# -*- coding: utf-8 -*-
"""
把學生在 C04 第 5 步打好的「作品說明書」，填進主辦單位格式的 Word（作品說明書_範本.docx），每人一份 .docx。

用法（純標準庫，不需要 pip）：
    1. C04 網址後面加 ?admin → 老師登入 →「匯出說明書資料（給 Word 用）」→ 會下載 manual.json
    2. 把 manual.json 放進 學生對話紀錄\\ 資料夾（或 _輸出\\），然後：
       工作台\\runtime\\python\\python.exe materials\\競賽專區\\C04_檢查標記與排版\\_歷程工具\\產生說明書.py
       （也可以在後面加 manual.json 的路徑）
    3. 結果在 學生對話紀錄\\_輸出\\說明書\\，檔名「高年級組-姓名-作品名稱_作品說明書.docx」

只處理學生清單上的人（姓名對照規則同 整理對話紀錄.py，含 名單例外.json）。
空白欄位會列在畫面上，方便提醒學生補寫。輸出含姓名，已列入 .gitignore，不要 commit。
"""
import sys, os, re, io, json, zipfile, glob, html, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, '..', '學生對話紀錄'))
spec = importlib.util.spec_from_file_location('zl', os.path.join(HERE, '整理對話紀錄.py'))
zl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zl)

CHAPS = ['第一章', '第二章', '第三章', '第四章', '第五章', '第六章']
LABEL = [('idea', '創作理念'), ('chapDesc', '手冊對應章節的說明'), ('err', '教育型 AI 有沒有錯誤'), ('found', '怎麼發現跟修正的'),
         ('eUse', '哪些地方使用到 e度'), ('disclose', '查證揭露'), ('tools', '用到的工具'), ('learned', '學到了什麼')]


def tick(b):
    return '☑' if b else '□'


def val(m, k):
    v = m.get(k, '')
    if isinstance(v, list):
        return v
    return str(v or '').strip()


def fill(xml, mapping):
    def esc(t):
        return html.escape(t, quote=False)

    def repl(m):
        attrs, body = m.group(1) or '', m.group(2)
        if '{{' not in body:
            return m.group(0)
        for k, v in mapping.items():
            if '{{%s}}' % k in body:
                body = body.replace('{{%s}}' % k, '\0' + k + '\0')
        parts = re.split(r'\0(\w+)\0', body)
        out = []
        for i, p in enumerate(parts):
            out.append(p if i % 2 == 0 else esc(mapping[p]))
        text = ''.join(out)
        text = text.replace('\r', '').replace('\n', '</w:t><w:br/><w:t xml:space="preserve">')
        return '<w:t xml:space="preserve">' + text + '</w:t>'
    return re.sub(r'<w:t( [^>]*)?>([^<]*)</w:t>', repl, xml)


def safe(s):
    return re.sub(r'[\\/:*?"<>|\s]+', '', s) or '未命名'


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    cands = [arg] if arg else [os.path.join(DATA, 'manual.json'), os.path.join(DATA, '_輸出', 'manual.json')]
    mp = next((c for c in cands if c and os.path.exists(c)), None)
    if not mp:
        sys.exit('找不到 manual.json。請先在 C04 ?admin 頁面按「匯出說明書資料」，放進 學生對話紀錄\\ 再執行。')
    students = json.load(io.open(mp, encoding='utf-8'))['students']
    roster, _ = zl.load_roster(DATA)
    exc = {}
    ep = os.path.join(DATA, '名單例外.json')
    if os.path.exists(ep):
        exc = json.load(io.open(ep, encoding='utf-8'))
    tpl = os.path.join(HERE, '作品說明書_範本.docx')
    zin = zipfile.ZipFile(tpl)
    doc_xml = zin.read('word/document.xml').decode('utf-8')
    out_dir = os.path.join(DATA, '_輸出', '說明書')
    os.makedirs(out_dir, exist_ok=True)
    made = 0
    for nm, (g, c, s) in sorted(roster.items(), key=lambda kv: kv[1]):
        sid = '%d-%d-%d' % (g, c, s)
        real = exc.get(sid, nm)
        if sid not in students:
            print('✗ %s %s：雲端沒有這位的資料（還沒打開過學習單？）' % (sid, real))
            continue
        m = students[sid].get('manual', {})
        title = (students[sid].get('title') or '').strip()
        ch = val(m, 'chapters')
        tools = val(m, 'tools')
        mapping = {
            'idea': val(m, 'idea'), 'chapDesc': val(m, 'chapDesc'),
            'found': val(m, 'found'), 'eUse': val(m, 'eUse'), 'disclose': val(m, 'disclose'), 'learned': val(m, 'learned'),
            'ey': tick(m.get('err') == '有'), 'en': tick(m.get('err') == '沒有'),
            'te': tick('因材網 e度' in tools), 'tc': tick('Canva' in tools), 'tp': tick('PowerPoint' in tools), 'tw': tick('Word' in tools),
            'to': tick('其他' in tools), 'toolsOther': val(m, 'toolsOther'),
        }
        for i, k in enumerate(CHAPS):
            mapping['c%d' % (i + 1)] = tick(k in ch)
        xml = fill(doc_xml, mapping)
        group = '中年級組' if g <= 4 else '高年級組'
        fn = '%s-%s-%s_作品說明書.docx' % (group, safe(real), safe(title))
        path = os.path.join(out_dir, fn)
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zo:
            for it in zin.infolist():
                zo.writestr(it.filename, xml.encode('utf-8') if it.filename == 'word/document.xml' else zin.read(it.filename))
        miss = [lab for k, lab in LABEL if not (m.get(k) if k not in ('tools',) else tools)]
        if not title:
            miss.append('作品名稱（第 1 節）')
        print('✓ %s %s → %s%s' % (sid, real, fn, ('　⚠ 還是空白：' + '、'.join(miss)) if miss else ''))
        made += 1
    print('\n共產生 %d 份，在 %s' % (made, out_dir))


if __name__ == '__main__':
    main()
