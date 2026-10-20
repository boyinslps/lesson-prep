# -*- coding: utf-8 -*-
"""
整理 e度 對話紀錄（Excel）→ 每位學生一份 aiHistory 資料，給 C04「我的對話紀錄」網頁用。

用法（純標準庫，不需要 pip；跟 build.py 一樣用工作台的可攜式 Python）：
    工作台\\runtime\\python\\python.exe materials\\競賽專區\\C04_檢查標記與排版\\_歷程工具\\整理對話紀錄.py
    （可加參數：資料夾路徑。預設是 ..\\學生對話紀錄）

資料夾內要有：
    report_{年級}_{班級}_{座號}_{時間}.xlsx   e度 匯出的紀錄（同一個人可以有很多份，會自動合併、去掉重複）
    *學生清單*.xlsx                           欄位：年級、班級、座號、姓名（其他欄位忽略）
    老師標記.json（選用）                     {"5-9-11": [{"id": "20261015130022u", "label": "…", "note": "…"}]}
    額外遮蔽.json（選用）                     ["蓁蓁", "潔潔"]  名單全名以外也要遮掉的字（暱稱、署名），內文出現就改成 ○
    說明書提示.json（選用）                   {"5-9-11": {"idea":{...}, "chapters":[...], "found":[...], "disclose":[...]}}  第 5 步依對話給學生的提醒
    名單例外.json（選用）                     {"5-11-14": "劉宜蓁"}  名單上的座號 → 紀錄裡實際的姓名（姓名對不上、但老師確認是同一人時用）

輸出（在資料夾的 _輸出\\ ，含學生姓名與對話，已列入 .gitignore，不要 commit）：
    aiHistory.json   到 C04 網頁 #admin →「匯入對話紀錄」上傳
    核對報告.txt     誰對上了、誰沒對上、哪些姓名被遮掉

比對規則：以「紀錄裡的姓名」對學生清單的姓名為準（名單有、紀錄有、名字一樣才收）。
座號與清單不同會提醒但照收，以清單的年班座號為學生登入用的編號。名單上沒有的人不會被收進去。
"""
import sys, os, re, io, json, glob, html, zipfile, hashlib, collections
import xml.etree.ElementTree as ET
from datetime import datetime

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
GAP_MIN = 25  # 兩句話相隔超過幾分鐘，就算新的一場對話


def col_idx(ref):
    n = 0
    for ch in re.match(r'[A-Z]+', ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_xlsx(path):
    """回傳第一張工作表的所有列（list of list of str|None）。"""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        shared = []
        if 'xl/sharedStrings.xml' in names:
            root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in root.findall('m:si', NS):
                shared.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
        wbx = ET.fromstring(z.read('xl/workbook.xml'))
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rid = wbx.find('m:sheets', NS)[0].get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        target = next(r.get('Target') for r in rels if r.get('Id') == rid)
        target = target.lstrip('/')
        if not target.startswith('xl/'):
            target = 'xl/' + target
        sheet = ET.fromstring(z.read(target))
    rows = []
    for row in sheet.iter('{%s}row' % NS['m']):
        cells = {}
        for c in row.findall('m:c', NS):
            t = c.get('t')
            v = c.find('m:v', NS)
            if t == 'inlineStr':
                val = ''.join(x.text or '' for x in c.iter('{%s}t' % NS['m']))
            elif v is None or v.text is None:
                val = None
            elif t == 's':
                val = shared[int(v.text)]
            else:
                val = v.text
            if val is not None:
                cells[col_idx(c.get('r'))] = val
        if cells:
            rows.append([cells.get(i) for i in range(max(cells) + 1)])
    return rows


def clean_text(s):
    s = html.unescape(s or '')
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'</?(b|strong|i|em|u|span|p|div)[^>]*>', '', s, flags=re.I)
    s = re.sub(r'\r\n?', '\n', s)
    s = re.sub(r'[ \t]+\n', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()


def to_int(x):
    try:
        return int(str(x).strip())
    except Exception:
        return None


def load_roster(folder):
    cands = [f for f in glob.glob(os.path.join(folder, '*學生清單*.xlsx')) if not os.path.basename(f).startswith('~$')]
    if not cands:
        sys.exit('找不到學生清單（檔名要有「學生清單」的 xlsx）：' + folder)
    rows = read_xlsx(cands[0])
    head = [str(h or '').strip() for h in rows[0]]

    def ix(*keys):
        for k in keys:
            if k in head:
                return head.index(k)
        sys.exit('學生清單缺少欄位：' + '/'.join(keys))
    ig, ic, is_, inm = ix('年級'), ix('班級'), ix('座號'), ix('姓名')
    roster = {}
    for r in rows[1:]:
        r = r + [None] * (len(head) - len(r))
        g, c, s, n = to_int(r[ig]), to_int(r[ic]), to_int(r[is_]), (r[inm] or '').strip()
        if g and c and s and n:
            roster[n] = (g, c, s)
    return roster, os.path.basename(cands[0])


def main():
    folder = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '學生對話紀錄'))
    roster, roster_file = load_roster(folder)
    out_dir = os.path.join(folder, '_輸出')
    os.makedirs(out_dir, exist_ok=True)
    rep = []
    P = rep.append
    P('名單：%s（%d 人）' % (roster_file, len(roster)))

    by_name = collections.defaultdict(list)   # 姓名 → [(來自檔案, 列)]
    seat_of_file = {}
    files = sorted(f for f in glob.glob(os.path.join(folder, 'report_*.xlsx')) if not os.path.basename(f).startswith('~$'))
    P('對話紀錄：%d 份 xlsx' % len(files))
    for f in files:
        base = os.path.basename(f)
        m = re.match(r'report_(\d+)_(\d+)_(\d+)_', base)
        fkey = tuple(int(x) for x in m.groups()) if m else None
        rows = read_xlsx(f)
        head = [str(h or '').strip() for h in rows[0]]
        need = ['學生姓名', '對話模式', '對話次數', '對話時間', '角色', '對話內容']
        miss = [h for h in need if h not in head]
        if miss:
            P('  ✗ %s 缺少欄位 %s，跳過' % (base, miss))
            continue
        H = {h: head.index(h) for h in head}
        for r in rows[1:]:
            r = r + [None] * (len(head) - len(r))
            if not r[H['對話時間']] or not r[H['角色']]:
                continue
            name = (r[H['學生姓名']] or '').strip()
            by_name[name].append(dict(file=base, fkey=fkey, mode=(r[H['對話模式']] or '').strip(),
                                      n=to_int(r[H['對話次數']]), t=r[H['對話時間']].strip(),
                                      role='u' if r[H['角色']].strip() == '使用者' else 'a',
                                      text=r[H['對話內容']] or ''))

    exc = {}
    ep = os.path.join(folder, '名單例外.json')
    if os.path.exists(ep):
        exc = json.load(io.open(ep, encoding='utf-8'))
        P('讀到 名單例外.json：%s' % '、'.join('%s→紀錄裡的「%s」' % kv for kv in exc.items()))

    extra_mask = []
    xp = os.path.join(folder, '額外遮蔽.json')
    if os.path.exists(xp):
        extra_mask = json.load(io.open(xp, encoding='utf-8'))
        P('讀到 額外遮蔽.json：%d 個詞' % len(extra_mask))
    guide_seed = {}
    gp = os.path.join(folder, '說明書提示.json')
    if os.path.exists(gp):
        guide_seed = {k: v for k, v in json.load(io.open(gp, encoding='utf-8')).items() if not k.startswith('_')}
        P('讀到 說明書提示.json（%d 位學生）' % len(guide_seed))

    names_all = sorted(set(roster) | set(exc.values()) | set(extra_mask), key=len, reverse=True)
    red_count = collections.Counter()

    def redact(txt, who):
        # 遮掉清單上所有人的全名（簡章：不可出現個人資訊）
        for nm in names_all:
            if nm in txt:
                red_count[(who, nm)] += txt.count(nm)
                txt = txt.replace(nm, '○' * len(nm))
        return txt

    marks_seed = {}
    mp = os.path.join(folder, '老師標記.json')
    if os.path.exists(mp):
        marks_seed = json.load(io.open(mp, encoding='utf-8'))
        P('讀到 老師標記.json（%d 位學生有標記）' % len(marks_seed))

    students = {}
    P('')
    P('── 比對結果 ──')
    for nm, (g, c, s) in sorted(roster.items(), key=lambda kv: kv[1]):
        sid = '%d-%d-%d' % (g, c, s)
        recs = by_name.get(exc.get(sid, nm), [])
        if not recs:
            others = sorted({r['fkey'] for rr in by_name.values() for r in rr if r['fkey'] == (g, c, s)})
            hint = ''
            if others:
                who = sorted({k for k, rr in by_name.items() if any(r['fkey'] == (g, c, s) for r in rr)})
                hint = '　⚠ 紀錄裡同一個座號（%s）的姓名是：%s，請老師確認是不是同一人' % (sid, '、'.join(who))
            P('✗ %s %s：紀錄裡找不到這個姓名%s' % (sid, nm, hint))
            continue
        seats = {r['fkey'] for r in recs}
        note = ''
        if seats != {(g, c, s)}:
            note = '　⚠ 紀錄檔名的座號 %s 和名單 %s 不同，以名單為準' % ('、'.join('%d-%d-%d' % k for k in sorted(k for k in seats if k)), sid)
        seen, uniq = set(), []
        for r in sorted(recs, key=lambda r: (r['t'], 0 if r['role'] == 'u' else 1)):
            k = (r['t'], r['role'], r['text'])
            if k in seen:
                continue
            seen.add(k)
            uniq.append(r)
        # 分場次
        sessions, cur, prev = [], None, None
        for r in uniq:
            dt = datetime.strptime(r['t'], '%Y-%m-%d %H:%M:%S')
            newsess = (cur is None or r['mode'] != cur['mode'] or
                       (dt - prev).total_seconds() > GAP_MIN * 60 or
                       (r['n'] is not None and cur.get('_n') is not None and r['n'] != cur['_n'] and r['file'] == cur['_f']))
            if newsess:
                cur = dict(mode=r['mode'], date=r['t'][:10], msgs=[], _n=r['n'], _f=r['file'])
                sessions.append(cur)
            prev = dt
            cur['_n'], cur['_f'] = r['n'], r['file']
            msg = dict(id=re.sub(r'\D', '', r['t']) + r['role'], t=r['t'][5:16], r=r['role'], x=redact(clean_text(r['text']), sid))
            if r['role'] == 'a' and (not any(m['r'] == 'u' for m in cur['msgs']) or msg['x'].startswith('嗨～我是您的AI教學夥伴')):
                msg['g'] = 1   # 開場問候（含切換精靈時的問候）
            cur['msgs'].append(msg)
        for se in sessions:
            se.pop('_n', None)
            se.pop('_f', None)
        ids = {m['id'] for se in sessions for m in se['msgs']}
        marks = []
        for mk in marks_seed.get(sid, []):
            mid = mk.get('id') or (re.sub(r'\D', '', mk.get('t', '')) + mk.get('who', 'u'))
            if mid in ids:
                marks.append(dict(id=mid, kind=mk.get('kind', ''), label=mk['label'], note=mk.get('note', '')))
            else:
                P('  ⚠ %s 的標記 %s 找不到對應的訊息，略過' % (sid, mid))
        def okids(items):
            out = []
            for it in items or []:
                ids_ok = [i for i in it.get('ids', []) if i in ids]
                bad = [i for i in it.get('ids', []) if i not in ids]
                for b in bad:
                    P('  ⚠ %s 的說明書提示 id %s 找不到對應的訊息，略過' % (sid, b))
                out.append(dict(it, ids=ids_ok))
            return out
        gs = guide_seed.get(sid, {})
        guide = {}
        if gs.get('idea'):
            guide['idea'] = okids([gs['idea']])[0]
        for k in ('chapters', 'found', 'disclose'):
            if gs.get(k):
                guide[k] = okids(gs[k])
        modes = collections.Counter()
        for se in sessions:
            modes[se['mode']] += sum(1 for m in se['msgs'] if m['r'] == 'u')
        nmsg = sum(len(se['msgs']) for se in sessions)
        nu = sum(1 for se in sessions for m in se['msgs'] if m['r'] == 'u')
        P('✓ %s %s：%d 份檔、%d 則訊息（學生 %d 則）、%d 場對話、%d 個老師標記%s' % (sid, nm, len({r['file'] for r in recs}), nmsg, nu, len(sessions), len(marks), note))
        students[sid] = dict(grade=g, className=c, studentId=s, sessions=sessions, marks=marks, guide=guide, modes=dict(modes))

    extra = [n for n in by_name if n not in roster and n not in exc.values()]
    if extra:
        P('')
        P('── 紀錄裡有、但名單上沒有的人（不會收進網頁）──')
        for n in extra:
            ks = sorted({'%d-%d-%d' % r['fkey'] for r in by_name[n] if r['fkey']})
            P('  - %s（檔名座號 %s，%d 則）' % (n or '（空白姓名）', '、'.join(ks), len(by_name[n])))
    if red_count:
        P('')
        P('── 內文出現名單上的姓名，已改成 ○ ──')
        for (who, nm), k in sorted(red_count.items()):
            P('  - %s 的紀錄裡出現「%s」%d 次' % (who, nm, k))

    pii = []
    pats = [('疑似帳號密碼／亂碼', re.compile(r'^(?=[A-Za-z0-9]*\d)(?=[A-Za-z0-9]*[A-Za-z])[A-Za-z0-9]{8,}$')),
            ('署名（可能是姓名或暱稱）', re.compile(r'[^\s，。：:、]{1,8}敬上')), ('電話', re.compile(r'09\d{2}-?\d{3}-?\d{3}')), ('Email', re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+')),
            ('身分證字號', re.compile(r'\b[A-Z][12]\d{8}\b'))]
    for sid, st in students.items():
        for se in st['sessions']:
            for m in se['msgs']:
                if m['r'] != 'u':
                    continue
                for lab, rx in pats:
                    if rx.search(m['x'].strip()) or (lab != '疑似帳號密碼／亂碼' and rx.search(m['x'])):
                        pii.append('  - %s %s（%s）：「%s」' % (sid, m['id'], lab, m['x'][:30].replace('\n', ' ')))
    if pii:
        P('')
        P('── 學生輸入的內容疑似個資（請老師看一下；挑進歷程紀錄前建議避開）──')
        rep.extend(pii)

    out = os.path.join(out_dir, 'aiHistory.json')
    json.dump(dict(generatedAt=datetime.now().isoformat(timespec='seconds'), students=students),
              io.open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    P('')
    P('輸出：%s（%d 位學生，%d KB）' % (out, len(students), os.path.getsize(out) // 1024))
    mapping = ['%s\t%s' % ('%d-%d-%d' % v, k) for k, v in sorted(roster.items(), key=lambda kv: kv[1]) if '%d-%d-%d' % v in students]
    io.open(os.path.join(out_dir, '編號對姓名.txt'), 'w', encoding='utf-8').write('\n'.join(mapping) + '\n')
    io.open(os.path.join(out_dir, '核對報告.txt'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
    print('\n'.join(rep))


if __name__ == '__main__':
    main()
