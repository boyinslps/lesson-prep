import io,re,os,sys
SRC=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(SRC,'..','..'))
rd=lambda n:io.open(os.path.join(SRC,n),encoding='utf-8').read()
css,sprite,common=rd('common.css'),rd('sprite.svg'),rd('common.js')
FOLD={'C00':'C00_賀卡創作營','C01':'C01_認識e度與主題','C02':'C02_文字創作與提問','C03':'C03_AI繪圖','C04':'C04_檢查標記與排版','C05':'C05_說明書與交件'}
def part(s,name):
    m=re.search(r'<!--@'+name+r'-->(.*?)(?=<!--@|\Z)',s,re.S); return m.group(1).strip() if m else ''
for code in (sys.argv[1:] or FOLD):
    fn=os.path.join(SRC,code.lower()+'.html')
    if not os.path.exists(fn): continue
    s=rd(code.lower()+'.html')
    title=part(s,'title'); ac=part(s,'accent').split()
    top='' if code=='C00' else f'''<header class="topbar"><div class="wrap">
  <a class="back" data-go="C00" href="#"><svg class="ico"><use href="#i-back"/></svg>目錄</a>
  <span style="font-weight:700;font-size:15px">{part(s,'label')}</span>
  <div class="who"><label>年級<input id="idG" inputmode="numeric" maxlength="1" aria-label="年級"></label><label>班級<input id="idC" inputmode="numeric" maxlength="2" aria-label="班級"></label><label>座號<input id="idS" inputmode="numeric" maxlength="2" aria-label="座號"></label><button id="loadBtn" class="loadbtn" type="button" title="把之前存在雲端的紀錄讀回來"><svg class="ico"><use href="#i-download"/></svg>讀取學習單</button><span id="saveStat" class="pill">…</span></div>
</div></header>'''
    html=f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
{css}
:root{{--ac:{ac[0]};--ac-soft:{ac[1]};--ac-ink:{ac[2]}}}
{part(s,'css')}
</style>
</head>
<body>
{sprite}
{top}
{part(s,'body')}
<footer><div class="wrap">{part(s,'foot') or '本頁引用《中小學 AI 之學習應用手冊—國小生聰明用 AI》（教育部，2026）的內容與頁面，僅供本校競賽指導使用；頁碼為手冊印刷頁碼。競賽規定以「115 年度小學生教育型 AI 學習夥伴應用競賽」簡章為準。'}</div></footer>
<script>
{part(s,'pre')}
</script>
<script>
{common}
</script>
<script>
{part(s,'post')}
</script>
</body>
</html>
'''
    out=os.path.join(OUT,FOLD[code],'競賽_'+FOLD[code]+'.html')
    io.open(out,'w',encoding='utf-8',newline='\n').write(html)
    print('built',out,len(html)//1024,'KB')
