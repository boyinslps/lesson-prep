# -*- coding: utf-8 -*-
"""把 整理對話紀錄.py 的輸出（_輸出/aiHistory.json）再清一次，產生可以進版控的「去姓名版」。

用法：工作台\\runtime\\python\\python.exe materials\\競賽專區\\C04_檢查標記與排版\\_歷程工具\\去識別輸出.py
輸出：學生對話紀錄\\aiHistory_去姓名.json（只用 年級-班級-座號 識別，沒有姓名）

做的事：
1. 疑似帳號密碼的整則輸入（只有英數字、8 字以上、沒有空白）改成「（疑似帳號密碼，已遮蔽）」。
2. 從學生清單、名單例外.json、額外遮蔽.json 收集所有姓名／暱稱，逐字檢查輸出，只要還找得到就中止、不寫檔。
學生清單、原始 report_*.xlsx 含真名，不要 commit（.gitignore 已擋 *.xlsx；公開儲存庫）。
"""
import io, json, os, re, sys, zipfile
sys.stdout.reconfigure(encoding='utf8')

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', '學生對話紀錄')
SRC = os.path.join(DATA, '_輸出', 'aiHistory.json')
OUT = os.path.join(DATA, 'aiHistory_去姓名.json')
HEADER = {'姓名', '帳號', '年級', '班級', '座號', '縣市', '學校', '性別', '備註'}   # 學生清單的表頭，不是人名
CRED = re.compile(r'^[A-Za-z0-9_@.\-]{8,}$')


def roster_names():
    names = set()
    for n in os.listdir(DATA):
        if '學生清單' in n and n.endswith('.xlsx'):
            z = zipfile.ZipFile(os.path.join(DATA, n))
            for part in z.namelist():
                if part.endswith('sharedStrings.xml'):
                    for t in re.findall(r'<t[^>]*>([^<]*)</t>', z.read(part).decode('utf8')):
                        if re.fullmatch(r'[一-鿿·]{2,5}', t):
                            names.add(t)
    for fn in ('名單例外.json', '額外遮蔽.json'):
        p = os.path.join(DATA, fn)
        if os.path.exists(p):
            v = json.load(io.open(p, encoding='utf8'))
            names.update(v.values() if isinstance(v, dict) else v)
    return {n for n in names if len(n) >= 2 and n not in HEADER}


def main():
    d = json.load(io.open(SRC, encoding='utf8'))
    cut = 0
    for s in d['students'].values():
        for se in s['sessions']:
            for m in se['msgs']:
                if m['r'] == 'u' and CRED.match(m['x'].strip()):
                    m['x'] = '（疑似帳號密碼，已遮蔽）'
                    cut += 1
    text = json.dumps(d, ensure_ascii=False, indent=1)
    names = roster_names()
    bad = sorted(n for n in names if n in text)
    if bad:
        sys.exit('還找得到姓名，中止（沒寫檔）：' + '、'.join(bad))
    io.open(OUT, 'w', encoding='utf8', newline='\n').write(text + '\n')
    print('已檢查 %d 個姓名／暱稱，輸出裡都沒有；遮蔽疑似密碼 %d 則' % (len(names), cut))
    print('輸出：', os.path.abspath(OUT), '（%d 位學生）' % len(d['students']))


if __name__ == '__main__':
    main()
