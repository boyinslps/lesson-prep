# -*- coding: utf-8 -*-
"""
老師端一鍵匯出：依學生在網頁填的內容，產生每人一個資料夾，放進本機（含姓名，只存在你的電腦，已列入 .gitignore）：

    {輸出資料夾}\{學生姓名}\
        {組別-姓名-作品名稱}_作品說明書.pdf        ← 主辦單位 Word 格式（作品說明書_範本.docx）填好，再用 Word 轉 PDF
        {組別-姓名-作品名稱}_AI協作歷程紀錄.pdf     ← 學生選好、寫好的輪次，排成 A4（最多 2 頁），用 Edge 轉 PDF
        {組別-姓名-作品名稱}_作品.pdf               ← 你把 Canva 下載的 PDF 放進 _作品PDF\\ 資料夾（檔名用 年-班-座.pdf，例如 5-9-11.pdf），這裡會自動收進來
        作品連結.txt                                ← 學生在 C05 貼的 Canva 分享連結
        參賽資料.txt                                ← 這位的參賽資料（組別、姓名、年級班級座號、作品名稱、檔名、檢查結果）
        原始檔\\作品說明書.docx
    {輸出資料夾}\\參賽資料總表.csv、檢查報告.txt、_作品PDF\\

用法（專案根目錄，或直接點兩下「匯出參賽資料.bat」）：
    工作台\\runtime\\python\\python.exe materials\\競賽專區\\C04_檢查標記與排版\\_歷程工具\\匯出參賽資料.py [輸出資料夾]
    預設輸出資料夾：materials\\競賽專區\\_繳交輸出\\
    加 --min-chars N：「我的發現」「最終採用的理由」各至少幾個字才算寫好（預設 6，和學生網頁一樣；字數偏少但學生有寫的，可以用 --min-chars 1 讓它進 PDF，報告會標出字數偏少的則）
    學生歷程超過 2 頁時，老師可以在 學生對話紀錄\\歷程挑選.json 指定只放哪幾則：{"5-11-7": [1], "5-11-16": [2]}（數字＝學生在第 3 步選的第幾則，1 起算）。只影響匯出的 PDF，學生雲端的選擇不動。
    加 --no-download 可以不重抓雲端資料，直接用上次下載的（_輸出\\雲端資料.json）。

需要：D:\\keys 的 worksheet-f47f3 服務帳號金鑰、本機的 Microsoft Word 和 Edge（或 Chrome）。
作品授權同意書（紙本家長簽名）不在系統裡，請另外掃描／拍照放進各人資料夾。
"""
import sys, os, re, io, json, subprocess, shutil, html, importlib.util, csv, zipfile, tempfile, glob

sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
DATA = os.path.abspath(os.path.join(HERE, '..', '學生對話紀錄'))
PY = os.path.join(ROOT, '工作台', 'runtime', 'python', 'python.exe')
NODE = os.path.join(ROOT, '工作台', 'runtime', 'node', 'node.exe')


def load(name):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


zl = load('整理對話紀錄')
ms = load('產生說明書')

LIM = dict(q=160, f=120, a=110)
ISS_MIN = MINE_MIN = 6
COLORS = {'0': '1F2A44', '1': 'D9534F', '2': '2F5AA8'}


# ---------- 歷程紀錄（和 c04_hist.js 的 roundText／sheetEl 同一套規則）----------
def nb(s):
    return re.sub(r'[〔〕]', '', str(s or ''))


def plain(s):
    s = nb(s).replace('**', '')
    s = re.sub(r'\s*\n+\s*', ' ', s)
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()


def clip(s, n):
    s = plain(s)
    return s[:n - 1] + '…' if len(s) > n else s


def cap(arr, lim):
    if len(arr) <= 2:
        return '\n'.join(clip(x, lim) for x in arr)
    return clip(arr[0], lim) + '\n⋯（中間還有 %d 則）\n' % (len(arr) - 2) + clip(arr[-1], lim)


def index_doc(doc):
    by, flat = {}, []
    for si, se in enumerate(doc.get('sessions') or []):
        for m in se.get('msgs') or []:
            o = dict(m=m, si=si, i=len(flat))
            flat.append(o)
            by[m['id']] = o
    return by, flat


def clean_pick(p, by):
    ids = p.get('ids') if isinstance(p.get('ids'), list) else [p.get('q'), p.get('a'), p.get('f')]
    ids = [str(i) for i in ids if i]
    seen, out = set(), []
    for i in ids:
        if i in by and i not in seen:
            seen.add(i)
            out.append(i)
    out.sort(key=lambda i: by[i]['i'])
    why = p.get('why') if isinstance(p.get('why'), str) else p.get('mine', '')
    return dict(ids=out, issNote=nb(p.get('issNote'))[:140], why=nb(why)[:140])


def is_done(p, by):
    u = sum(1 for i in p['ids'] if by[i]['m'].get('r') == 'u' and not by[i]['m'].get('g'))
    a = sum(1 for i in p['ids'] if by[i]['m'].get('r') == 'a' and not by[i]['m'].get('g'))
    return u >= 1 and a >= 1 and len(p['issNote'].strip()) >= ISS_MIN and len(p['why'].strip()) >= MINE_MIN


def rounds_of(p, by):
    """一問一答算 1 輪；一個「選這則」常常包含好幾輪。"""
    n, wait = 0, False
    for i in p['ids']:
        m = by[i]['m']
        if m.get('g'):
            continue
        if m.get('r') == 'u':
            wait = True
        elif wait:
            n += 1
            wait = False
    return n


def ts_of(i):
    m = re.match(r'(\d{4})(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)', i)
    return '%s-%s-%s %s:%s:%s' % m.groups() if m else ''


# 照 e度 匯出的 Excel 排版（對話模式／對話時間／角色／對話內容），完整呈現不省略；純黑白表格。
SHEET_CSS = """
@page{size:A4;margin:12mm}
*{box-sizing:border-box}
body{margin:0;color:#000;font-family:'Microsoft JhengHei','Noto Sans TC',sans-serif;font-size:9.5pt;line-height:1.5}
h1{font-size:15pt;margin:0 0 3mm;font-weight:700;text-align:center}
h2{font-size:10.5pt;margin:4mm 0 1.2mm;font-weight:700;break-after:avoid;page-break-after:avoid}
table{width:100%;border-collapse:collapse;table-layout:fixed;margin:0 0 1mm}
th,td{border:.6pt solid #000;padding:.9mm 1.6mm;vertical-align:top}
th{font-weight:700;text-align:center}
table.fd th{text-align:left}
td.c{text-align:center;white-space:nowrap;font-size:8.5pt}
td.tx,table.fd td{white-space:pre-wrap;word-break:break-word}
tr{break-inside:avoid;page-break-inside:avoid}
"""


def sheet_html(picks, by, doc):
    e = html.escape
    h = ['<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><title>AI協作歷程紀錄</title><style>', SHEET_CSS, '</style></head><body>',
         '<h1>教育型 AI 協作歷程紀錄</h1>']
    modes = [(se or {}).get('mode', '') for se in (doc.get('sessions') or [])]
    for k, p in enumerate(picks, 1):
        rows = ''
        for i in p['ids']:
            o = by[i]
            if o['m'].get('g'):
                continue
            rows += '<tr><td class="c">%s</td><td class="c">%s</td><td class="c">%s</td><td class="tx">%s</td></tr>' % (
                e(modes[o['si']] if o['si'] < len(modes) else ''), e(ts_of(i)), '使用者' if o['m'].get('r') == 'u' else 'e度', e(nb(o['m'].get('x')).strip()))
        h.append('<h2>第 %d 則　對話紀錄（共 %d 輪）</h2>' % (k, rounds_of(p, by)))
        h.append('<table><colgroup><col style="width:17mm"><col style="width:30mm"><col style="width:14mm"><col></colgroup>'
                 '<thead><tr><th>對話模式</th><th>對話時間</th><th>角色</th><th>對話內容</th></tr></thead><tbody>%s</tbody></table>' % rows)
        h.append('<h2>第 %d 則　我的發現與理由</h2>' % k)
        h.append('<table class="fd"><colgroup><col style="width:34mm"><col></colgroup><tbody>'
                 '<tr><th>我的發現（問題，或 e度 怎麼幫我）</th><td>%s</td></tr><tr><th>最終採用的理由</th><td>%s</td></tr></tbody></table>' % (e(nb(p['issNote']).strip()), e(nb(p['why']).strip())))
    h.append('</body></html>')
    return ''.join(h)


def find_browser():
    for p in [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe']:
        if os.path.exists(p):
            return p
    return None


def html_to_pdf(browser, html_path, pdf_path):
    prof = tempfile.mkdtemp(prefix='edge_')
    try:
        subprocess.run([browser, '--headless=new', '--disable-gpu', '--no-first-run', '--user-data-dir=' + prof, '--no-pdf-header-footer',
                        '--print-to-pdf=' + pdf_path, 'file:///' + html_path.replace('\\', '/')], timeout=120, capture_output=True)
    finally:
        shutil.rmtree(prof, ignore_errors=True)
    return os.path.exists(pdf_path)


def pdf_pages(path):
    try:
        data = open(path, 'rb').read()
        return len(re.findall(rb'/Type\s*/Page[^s]', data))
    except Exception:
        return 0


# ---------- 作品說明書（Word 格式）----------
def mark_runs(text, codes):
    codes = (re.sub(r'[^012]', '', codes or '') + '0' * len(text))[:len(text)]
    runs, cur, cc = [], '', None
    def flush():
        if cur:
            col = COLORS[cc]
            bold = '<w:b/>' if cc != '0' else ''
            parts = cur.split('\n')
            inner = '<w:br/>'.join('<w:t xml:space="preserve">%s</w:t>' % html.escape(x, quote=False) for x in parts)
            runs.append('<w:r><w:rPr>%s<w:color w:val="%s"/></w:rPr>%s</w:r>' % (bold, col, inner))
    for ch, c in zip(text, codes):
        if c != cc and cur:
            flush()
            cur = ''
        cc = c
        cur += ch
    flush()
    return ''.join(runs)


def make_docx(tpl_xml, zin, m, mark_text, mark_codes, path):
    ch, tools = ms.val(m, 'chapters'), ms.val(m, 'tools')
    mapping = {
        'idea': ms.val(m, 'idea'), 'chapDesc': ms.val(m, 'chapDesc'), 'found': ms.val(m, 'found'), 'eUse': ms.val(m, 'eUse'),
        'disclose': ms.val(m, 'disclose'), 'learned': ms.val(m, 'learned'),
        'ey': ms.tick(m.get('err') == '有'), 'en': ms.tick(m.get('err') == '沒有'),
        'te': ms.tick('因材網 e度' in tools), 'tc': ms.tick('Canva' in tools), 'tp': ms.tick('PowerPoint' in tools), 'tw': ms.tick('Word' in tools),
        'to': ms.tick('其他' in tools), 'toolsOther': ms.val(m, 'toolsOther'),
    }
    for i, k in enumerate(ms.CHAPS):
        mapping['c%d' % (i + 1)] = ms.tick(k in ch)
    xml = tpl_xml
    if mark_text.strip():   # 查證揭露的格子裡，放上學生標好顏色的卡片文字（在學生說明的上方）
        mm = re.search(r'<w:p[ >](?:(?!</w:p>).)*\{\{disclose\}\}(?:(?!</w:p>).)*</w:p>', xml, re.S)
        if mm:   # 同一格：標記後的文章在上，學生的簡單說明（{{disclose}}）在下
            head = '<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">【卡片文字標記：黑色＝自己想的　紅色＝AI 幫忙的　藍色＝自己修改的】</w:t></w:r><w:r><w:br/></w:r>'
            para = '<w:p><w:pPr><w:spacing w:after="120"/></w:pPr>%s%s</w:p>' % (head, mark_runs(mark_text, mark_codes))
            xml = xml[:mm.start()] + para + xml[mm.start():]
    xml = ms.fill(xml, mapping)
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zo:
        for it in zin.infolist():
            zo.writestr(it.filename, xml.encode('utf-8') if it.filename == 'word/document.xml' else zin.read(it.filename))


def docx_to_pdf(pairs):
    """用本機 Microsoft Word 把一批 .docx 轉成 .pdf。pairs: [(docx, pdf)]"""
    if not pairs:
        return
    ps = ["$ErrorActionPreference='Stop'", "$w=New-Object -ComObject Word.Application", "$w.Visible=$false", "$w.DisplayAlerts=0"]
    for a, b in pairs:
        ps.append("try{$d=$w.Documents.Open('%s',$false,$true);$d.SaveAs2('%s',17);$d.Close($false)}catch{Write-Host ('轉檔失敗：'+$_.Exception.Message)}" % (a.replace("'", "''"), b.replace("'", "''")))
    ps.append("$w.Quit()")
    f = os.path.join(tempfile.gettempdir(), 'docx2pdf_%d.ps1' % os.getpid())
    io.open(f, 'w', encoding='utf-8-sig').write('\n'.join(ps))
    r = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', f], capture_output=True, timeout=600)
    os.remove(f)
    msg = (r.stdout or b'').decode('utf-8', 'ignore') + (r.stderr or b'').decode('utf-8', 'ignore')
    if msg.strip():
        print(msg.strip())


def main():
    global ISS_MIN, MINE_MIN
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a.startswith('--min-chars'):
            v = a.split('=', 1)[1] if '=' in a else (argv[i + 1] if i + 1 < len(argv) else '6')
            ISS_MIN = MINE_MIN = max(1, int(v))
    args = [a for k, a in enumerate(argv) if not a.startswith('--') and not (k > 0 and argv[k - 1] == '--min-chars')]
    out_root = os.path.abspath(args[0]) if args else os.path.join(ROOT, 'materials', '競賽專區', '_繳交輸出')
    cloud_path = os.path.join(DATA, '_輸出', '雲端資料.json')
    if '--no-download' not in sys.argv:
        print('下載雲端資料…')
        r = subprocess.run([NODE, os.path.join(HERE, '下載雲端資料.js'), cloud_path], capture_output=True, timeout=300)
        print((r.stdout or b'').decode('utf-8', 'ignore').strip() or (r.stderr or b'').decode('utf-8', 'ignore').strip())
        if r.returncode:
            sys.exit(1)
    cloud = json.load(io.open(cloud_path, encoding='utf-8'))
    work, hist = cloud['cardWork'], cloud['aiHistory']
    try:
        roster, _ = zl.load_roster(DATA)       # {姓名: (年, 班, 座)}
    except Exception:
        roster = {}
    seat_name = {'%d-%d-%d' % v: k for k, v in roster.items()}
    # 名單例外.json：名單上的姓名不對（舊資料）時，老師確認過的正確姓名（座號 → 姓名），優先於名單
    exc_p = os.path.join(DATA, '名單例外.json')
    if os.path.exists(exc_p):
        for k, v in json.load(io.open(exc_p, encoding='utf-8')).items():
            if not k.startswith('_'):
                seat_name[k] = v
    browser = find_browser()
    if not browser:
        sys.exit('找不到 Edge 或 Chrome，無法產生歷程紀錄 PDF。')
    os.makedirs(out_root, exist_ok=True)
    works_dir = os.path.join(out_root, '_作品PDF')
    os.makedirs(works_dir, exist_ok=True)
    io.open(os.path.join(works_dir, '放這裡.txt'), 'w', encoding='utf-8').write(
        '把學生從 Canva 下載的賀卡 PDF 放在這個資料夾，檔名用「年級-班級-座號.pdf」（例如 5-9-11.pdf），重新執行匯出就會自動收進各人的資料夾。\n')

    pick_sel = {}
    sp_ = os.path.join(DATA, '歷程挑選.json')
    if os.path.exists(sp_):
        pick_sel = {k: v for k, v in json.load(io.open(sp_, encoding='utf-8')).items() if not k.startswith('_')}
    tpl = os.path.join(HERE, '作品說明書_範本.docx')
    zin = zipfile.ZipFile(tpl)
    doc_xml = zin.read('word/document.xml').decode('utf-8')
    ids = sorted(set(work) | set(hist) | set(seat_name), key=lambda s: [int(x) for x in s.split('-')])
    extra_ids = [i for i in ids if i not in seat_name and work.get(i, {}).get('L4')]   # 名單外的資料（誤填座號、測試）不匯出，只在報告提醒
    ids = [i for i in ids if i in seat_name]
    used_folders = {}
    rows, report, pdf_jobs, tmp = [], [], [], tempfile.mkdtemp(prefix='sheet_')
    for sid in ids:
        g = int(sid.split('-')[0])
        w = work.get(sid, {})
        l4, l1, l5 = w.get('L4', {}) or {}, w.get('L1', {}) or {}, w.get('L5', {}) or {}
        name = (l4.get('mName') or '').strip() or seat_name.get(sid, '') or '未填姓名'
        title = (l4.get('mTitle') or '').strip() or (l1.get('title') or '').strip() or '未取名'
        group = '中年級組' if g <= 4 else '高年級組'
        base = '%s-%s-%s' % (group, ms.safe(name), ms.safe(title))
        miss = []
        fname = ms.safe(name)
        if fname in used_folders:   # 兩位同名（或姓名沒填）時加上座號，避免資料夾撞在一起
            fname = '%s_%s' % (fname, sid)
        used_folders[fname] = sid
        folder = os.path.join(out_root, fname)   # 資料夾用學生姓名；裡面的檔名照簡章【組別-姓名-作品名稱】
        os.makedirs(os.path.join(folder, '原始檔'), exist_ok=True)
        roster_name = seat_name.get(sid, '')
        if roster_name and (l4.get('mName') or '').strip() and (l4.get('mName') or '').strip() != roster_name:
            miss.append('學生自己填的姓名（%s）和名單上的姓名（%s）不一樣，報名前請確認' % ((l4.get('mName') or '').strip(), roster_name))

        # 作品說明書
        docx = os.path.join(folder, '原始檔', '作品說明書.docx')
        if l4:
            make_docx(doc_xml, zin, l4, l4.get('markText') or '', l4.get('markCodes') or '', docx)
            pdf_jobs.append((docx, os.path.join(folder, base + '_作品說明書.pdf')))
            emp = [lab for k, lab in ms.LABEL if k != 'disclose' and not (l4.get(k) if k != 'tools' else ms.val(l4, 'tools'))]
            if not (l4.get('idea') or '').strip():
                pass
            if emp:
                miss.append('說明書空白欄位：' + '、'.join(emp))
            if not (l4.get('markText') or '').strip():
                miss.append('沒有標記賀卡文字（說明書的「查證揭露」會是空的，請學生到第 1 步標記）')
        else:
            miss.append('還沒有作品說明書（學生沒打開過第 4 節）')

        # 歷程紀錄
        npages, ndone = 0, 0
        d = hist.get(sid)
        if d:
            by, _ = index_doc(d)
            picks = [clean_pick(p, by) for p in (d.get('picks') or [])]
            picks = [p for p in picks if p['ids']]
            if sid in pick_sel:   # 老師挑選：只放指定的幾則（PDF 在 2 頁內）；學生雲端的選擇不動
                keep = [picks[i - 1] for i in pick_sel[sid] if 1 <= i <= len(picks)]
                dropped = [k for k in range(1, len(picks) + 1) if k not in pick_sel[sid]]
                picks = keep
                if dropped:
                    miss.append('歷程只放學生選的第 %s 則（老師挑選；第 %s 則沒放，是為了 PDF 在 2 頁內）' % ('、'.join(map(str, pick_sel[sid])), '、'.join(map(str, dropped))))
            good = [p for p in picks if is_done(p, by)]
            ndone = sum(rounds_of(p, by) for p in good)      # 寫好的輪數（一問一答算 1 輪）
            for k, p in enumerate(good, 1):
                a, b = len(p['issNote'].strip()), len(p['why'].strip())
                if a < 6 or b < 6:
                    miss.append('第 %d 則的發現／理由字數偏少（發現 %d 字、理由 %d 字），建議請學生補充' % (k, a, b))
            skipped = [k for k, p in enumerate(picks, 1) if p not in good and (p['issNote'].strip() or p['why'].strip())]
            if skipped:
                miss.append('第 %s 則有寫但字數不到門檻，沒放進 PDF（可用 --min-chars 1 放進去）' % '、'.join(map(str, skipped)))
            if good:
                hp = os.path.join(tmp, sid + '.html')
                io.open(hp, 'w', encoding='utf-8').write(sheet_html(good, by, d))
                pdf = os.path.join(folder, base + '_AI協作歷程紀錄.pdf')
                if html_to_pdf(browser, hp, pdf):
                    npages = pdf_pages(pdf)
                    if npages > 2:
                        miss.append('歷程紀錄完整呈現共 %d 頁，超過簡章的 2 頁上限（請學生少選幾則、或選短一點的）' % npages)
                else:
                    miss.append('歷程紀錄 PDF 產生失敗')
            if ndone < 4:
                miss.append('歷程紀錄寫好 %d 輪（一問一答算 1 輪，建議至少 4 輪）' % ndone)
        else:
            miss.append('沒有對話紀錄資料（aiHistory）')

        # 作品：Canva 連結 + 你放進 _作品PDF 的 PDF
        link = (l5.get('workLink') or '').strip()
        if link:
            io.open(os.path.join(folder, '作品連結.txt'), 'w', encoding='utf-8').write(link + '\n')
        else:
            miss.append('學生還沒貼 Canva 作品連結（C05）')
        src = next(iter(glob.glob(os.path.join(works_dir, sid + '*.pdf'))), None)
        has_work = False
        if src:
            shutil.copy2(src, os.path.join(folder, base + '_作品.pdf'))
            has_work = True
        else:
            miss.append('還沒有作品 PDF（請放進 _作品PDF\\%s.pdf）' % sid)

        info = ['參賽資料', '=' * 20, '組別：' + group, '參賽者姓名：' + name, '年級：' + str(l4.get('mGrade') or g), '班級／座號：%s／%s' % (sid.split('-')[1], sid.split('-')[2]),
                '作品名稱：' + title, '作品連結：' + (link or '（未填）'), '', '檔名（簡章規定【參賽組別-參賽者姓名-作品名稱】）：', '  ' + base,
                '', '檢查：', *(['  ✓ 都齊了（作品授權同意書為紙本，請另外掃描）'] if not miss else ['  ✗ ' + x for x in miss])]
        io.open(os.path.join(folder, '參賽資料.txt'), 'w', encoding='utf-8').write('\n'.join(info) + '\n')
        rows.append([group, g, sid.split('-')[1], sid.split('-')[2], name, title, base, link, '有' if has_work else '無', ndone, npages, '；'.join(miss)])
        report.append('%s %s：%s' % (sid, name, '✓ 齊全' if not miss else '；'.join(miss)))

    print('用 Word 轉作品說明書 PDF（%d 份）…' % len(pdf_jobs))
    docx_to_pdf(pdf_jobs)
    for a, b in pdf_jobs:
        if not os.path.exists(b):
            report.append('⚠ %s 的說明書 PDF 沒轉成功（原始檔在 原始檔\\作品說明書.docx，可以手動用 Word 另存 PDF）' % os.path.basename(os.path.dirname(os.path.dirname(a))))
    shutil.rmtree(tmp, ignore_errors=True)

    with io.open(os.path.join(out_root, '參賽資料總表.csv'), 'w', encoding='utf-8-sig', newline='') as fh:
        wr = csv.writer(fh)
        wr.writerow(['組別', '年級', '班級', '座號', '參賽者姓名（學生填的，沒填用名單）', '作品名稱', '檔名', 'Canva 作品連結', '作品PDF', '歷程寫好輪數（一問一答算1輪）', '歷程頁數', '待補'])
        wr.writerows(rows)
    for i in extra_ids:
        report.append('⚠ 名單外的資料 %s（姓名：%s）沒有匯出：可能是學生填錯座號自動存下的重複資料，或是測試資料' % (i, (work[i].get('L4') or {}).get('mName') or '未填'))
    io.open(os.path.join(out_root, '檢查報告.txt'), 'w', encoding='utf-8').write('\n'.join(report) + '\n')
    print('\n'.join(report))
    print('\n已匯出 %d 位到：%s' % (len(rows), out_root))
    print('提醒：作品授權同意書（紙本）請另外掃描放進各人資料夾；作品 PDF 請放進 _作品PDF\\ 再重跑一次。')


if __name__ == '__main__':
    main()
