# -*- coding: utf-8 -*-
# 產生「五上 L05 週五版」學習單：L05（找查核文章）＋ L06（整理成報告）合成一份，
# 全部寫在學習單裡（不開 Google 文件，所以沒有標題 1/2、超連結、貼格式這些排版步驟）。
#
# 流程：開始 → 選訊息 → 找查核文章 → 7 個填寫節點 → 預覽全部內容 → 繳交（共 12 步）
# 7 個節點（照老師指定順序）：查核網址、你使用的搜索工具、原始內容描述、
#                              查核結果、正確資訊、為什麼會流傳、相信的後果
# （2026-11-06 教師指定：拿掉「查核報告標題」整節；搜索工具只留「用的工具」與「我輸入的是」，後者只有選了關鍵字搜尋才出現）
# 2026-11-06 依國小課本編排重整：拿掉「老師示範」整步（示範改放在各欄）；每一欄＝本欄目標一句＋「看老師怎麼做」
#   （操作欄放一支完整影片、寫作欄放標出重點的範例）→ 按「看懂了，換我寫」才出現最多 3 步＋填寫＋檢查表；
#   每欄檢查表全部打勾就收集一顆 ★（頁面不用 emoji）。
# 新功能「斷點繳交」：每個節點都能先交一次（老師後台同樣顯示已繳交），並把進度存進 studentWork，
#                    下次輸入同樣的年級／班級／座號就能拿回。
# 骨架（CSS、靠椅子關卡、步驟卡）直接取自已發布的 pcclass/g5/L05/index.html，確保行為一致。
# 用法：python3 build_L05_fri.py   → 寫出兩份（lesson-prep 教材資料夾、pcclass 發布資料夾）
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # materials/五年級上學期
REPO = os.path.dirname(os.path.dirname(ROOT))      # lesson-prep
PCCLASS = os.path.join(os.path.dirname(REPO), 'pcclass')
SRC = os.path.join(PCCLASS, 'g5', 'L05', 'index.html')
src = io.open(SRC, encoding='utf8').read()

# ---------- 取用已發布 L05 的骨架 ----------
HEAD_CSS = src[:src.index('</head>')]
HEAD_CSS = re.sub(r'<title>.*?</title>', '<title>訊息查證小偵探｜五上 L05 週五版學習單</title>', HEAD_CSS)
FIREBASE_CFG = re.search(r'var firebaseConfig = \{.*?\n\};', src, re.S).group(0)
CHAIR = re.search(r'<!--CHAIR-GATE-START-->.*?<!--CHAIR-GATE-END-->', src, re.S).group(0)
STEPCARDS = re.search(r'<!--STEPCARDS-START-->.*?<!--STEPCARDS-END-->', src, re.S).group(0)
s3 = src[src.index('data-step="3"'):]
CARDS_HTML = re.search(r'<div class="grid md:grid-cols-2 gap-5">.*?\n    </div>\n    <div class="stepnav">', s3, re.S).group(0)
CARDS_HTML = CARDS_HTML.replace('\n    <div class="stepnav">', '').replace('src="assets/', 'src="@@A@@').replace('poster="assets/', 'poster="@@A@@')

EXTRA_CSS = r'''
<style>
  /* 週五版：填寫節點 */
  .chip{border:2px solid #cbd5e1;background:#fff;border-radius:999px;padding:6px 14px;font-weight:700;font-size:1.05rem;transition:.12s;cursor:pointer;text-align:left}
  .chip:hover{border-color:#818cf8}
  .chip.on{border-color:#6366f1;background:#eef2ff;color:#3730a3;box-shadow:0 0 0 3px #c7d2fe}
  .chip .mk{display:inline-block;width:1.2em}
  .fld{font-size:1.1rem;line-height:1.7}
  textarea.fld{resize:vertical;min-height:84px}
  .fillbox label.lb{display:block;font-weight:800;font-size:1.1rem;margin-top:14px;color:#334155}
  .fillbox label.lb small{font-weight:600;color:#64748b}
  .checks{list-style:none;margin:12px 0 0;padding:0}
  .checks li{display:flex;gap:8px;align-items:flex-start;padding:3px 0;font-size:1.02rem}
  .checks .ckm{flex:none;width:1.4em;text-align:center;font-weight:900}
  .checks .ck-ok{color:#047857}
  .checks .ck-todo{color:#64748b}
  .checks .ck-warn{color:#b45309}
  .howlist{counter-reset:h;list-style:none;margin:10px 0 0;padding:0}
  .howlist>li{counter-increment:h;position:relative;padding:6px 0 6px 2.4rem;font-size:1.15rem;line-height:1.65}
  .howlist>li:before{content:counter(h);position:absolute;left:0;top:6px;width:1.8rem;height:1.8rem;border-radius:999px;background:#6366f1;color:#fff;font-weight:900;text-align:center;line-height:1.8rem;font-size:1rem}
  .ckptbar{margin-top:18px;background:#fffbeb;border:3px dashed #fbbf24;border-radius:20px;padding:12px 14px}
  .ckptbar .ckBtn{background:#f59e0b;color:#fff;font-weight:900;border-radius:14px;padding:8px 16px}
  .ckptbar .ckBtn:hover{background:#d97706}
  .ckptbar .ckBtn:disabled{opacity:.5}
  .locked .chip,.locked [data-pick],.locked .ckptbar,.locked [data-insert]{pointer-events:none;opacity:.8}
  #toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:70;background:#065f46;color:#fff;font-weight:800;border-radius:16px;padding:10px 20px;box-shadow:0 8px 24px rgba(0,0,0,.3);max-width:92vw;text-align:center}
  #toast.hidden{display:none}
  .idwarn{animation:idp 1.2s ease-in-out infinite}
  /* 課本式編排：本欄目標 → 看老師怎麼做 → 換你寫 */
  .goal{font-size:1.3rem;font-weight:700;color:#334155;margin:.4rem 0 0;line-height:1.6}
  .parth{font-size:1.5rem;font-weight:900;margin:0 0 .6rem}
  .opennext{display:block;margin:18px auto 0;background:#4f46e5;color:#fff;font-weight:900;font-size:1.25rem;border-radius:16px;padding:10px 30px}
  .opennext:hover{background:#4338ca}
  .mhead{font-size:1.2rem;font-weight:900;color:#0f766e;margin:.9rem 0 .2rem}
  .parthrow{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
  .parthrow .parth{margin:0}
  .reviewbtn{background:#fff;border:2px solid #f59e0b;color:#b45309;font-weight:800;border-radius:12px;padding:4px 14px}
  .reviewbtn:hover{background:#fffbeb}
  [data-demo].flash{animation:demoflash 1.4s ease-out}
  @keyframes demoflash{0%,60%{box-shadow:0 0 0 6px rgba(245,158,11,.55)}100%{box-shadow:0 0 0 0 rgba(245,158,11,0)}}
  .opennext.hidden,.fillbox.hidden,[data-kwonly].hidden{display:none}   /* 自己寫的 display 會蓋過 Tailwind 的 hidden，這裡明確補上 */
  .exbox{background:#fffbeb;border:2px solid #fcd34d;border-radius:16px;padding:12px 16px;font-size:1.25rem;line-height:2}
  .exbox .exh{margin:0 0 2px;font-size:1rem;font-weight:900;color:#b45309}
  .exnote{margin:8px 0 0;font-size:1.05rem;color:#64748b}
  .tag{display:inline-block;font-size:.8rem;font-weight:900;color:#fff;background:#f59e0b;border-radius:999px;padding:0 8px;margin:0 3px;line-height:1.6;vertical-align:middle}
  .hl{background:#fef08a;border-radius:4px;padding:0 2px}
  .fieldcell{background:#eef2ff;border:2px solid #c7d2fe;border-radius:14px;padding:8px 10px;font-weight:800;font-size:1.05rem}
  .selline{font-size:1.15rem;margin:.6rem 0 0}
  .selbox{background:#fff;border:2px solid #fcd34d;border-radius:16px;padding:12px 14px;margin-bottom:6px}
  .selbox img,.selbox video{max-height:420px;width:auto;max-width:100%;border-radius:12px;display:block;margin:0 auto}
  [data-forkind].hidden{display:none}
  .insbtn{background:#0284c7;color:#fff;font-weight:700;border-radius:12px;padding:4px 12px}
  .insbtn:hover{background:#0369a1}
  /* 收集星星（用 ★ 字元，不用 emoji） */
  .starbadge{display:inline-block;margin-left:10px;font-weight:800;font-size:.95rem;color:#94a3b8;border:2px dashed #cbd5e1;border-radius:999px;padding:1px 10px}
  .starbadge.got{color:#92400e;background:#fef3c7;border:2px solid #f59e0b}
  .starmini{color:#cbd5e1;font-size:1.15em;margin-right:4px}
  .starmini.on{color:#f59e0b}
  #starPop{position:fixed;left:50%;top:110px;transform:translateX(-50%);z-index:80;pointer-events:none;background:#fffbeb;border:4px solid #f59e0b;border-radius:24px;padding:12px 26px;text-align:center;box-shadow:0 12px 32px rgba(0,0,0,.18);animation:starin .45s cubic-bezier(.2,1.4,.4,1)}
  #starPop .big{font-size:64px;line-height:1.1;display:block;color:#f59e0b;animation:starspin .8s ease-out}
  @keyframes starin{from{transform:translateX(-50%) scale(.4);opacity:0}to{transform:translateX(-50%) scale(1);opacity:1}}
  @keyframes starspin{from{transform:rotate(-180deg) scale(.3)}to{transform:rotate(0) scale(1)}}
  @media (prefers-reduced-motion:reduce){#starPop,#starPop .big{animation:none}}
  @keyframes idp{0%,100%{box-shadow:0 0 0 0 rgba(244,63,94,.5)}50%{box-shadow:0 0 0 6px rgba(244,63,94,0)}}
</style>
'''

LINKS = '''<div class="flex flex-wrap gap-2 mt-4">
        <a href="https://www.google.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2">Google 搜尋</a>
        <a href="https://tfc-taiwan.org.tw/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2"><img src="https://www.google.com/s2/favicons?domain=tfc-taiwan.org.tw&sz=64" class="w-5 h-5 bg-white rounded" alt="">台灣事實查核中心</a>
        <a href="https://www.mygopen.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2"><img src="https://www.google.com/s2/favicons?domain=mygopen.com&sz=64" class="w-5 h-5 bg-white rounded" alt="">MyGoPen 麥擱騙</a>
      </div>'''

# ---------- 小零件 ----------
def media(name, cap='', at='@@A@@'):
    """老師示範影片：靜音、循環、點一下暫停（stepcards 元件負責載入）。一個操作一支完整影片，不切碎。
    at＝素材資料夾代號：@@A@@＝L05 素材、@@A4@@＝L04 素材（智慧鏡頭）。"""
    return ('<div class="sc sc-flat sc-nonum" data-sc><div class="sc-slide"><p class="sc-t">%s</p>'
            '<div class="sc-media" data-src="%s%s.mp4" data-poster="%s%s_封面.jpg"></div></div></div>') % (cap, at, name, at, name)


def chips(key, items, multi=False, cls=''):
    return '<div class="flex flex-wrap gap-2 mt-2 %s" data-chips="%s"%s>%s</div>' % (
        cls, key, ' data-multi="1"' if multi else '',
        ''.join('<button type="button" class="chip" data-v="%s">%s%s</button>' % (v, '<span class="mk">☐</span>' if multi else '', v) for v in items))


def kb(*ks):
    return '＋'.join('<kbd>%s</kbd>' % k for k in ks)


def steps(*items):
    """換你寫的步驟：最多 3 步，每步一句短話、動詞開頭。"""
    assert len(items) <= 3
    return '<ol class="howlist">%s</ol>' % ''.join('<li>%s</li>' % i for i in items)


def ex(html, note=''):
    """老師的示範（寫作欄）：黃底範例，用 <span class="tag"> 標出每一部分在回答什麼。"""
    return ('<div class="exbox"><p class="exh">老師的示範</p><div>%s</div></div>' % html
            + ('<p class="exnote">%s</p>' % note if note else ''))


def tag(t):
    return '<span class="tag">%s</span>' % t


def node(n, k, tone, title, goal, qid, demo, todo, fill):
    """一欄一頁，照國小課本的順序分兩批出現：
       ① 本欄目標＋看老師怎麼做（影片或範例）→ 按「看懂了，換我寫」→ ② 換你寫（最多 3 步＋填寫＋檢查表）。
       已經寫過、拿到星星或老師檢視時，②直接展開（engine 的 renderParts）。"""
    return '''
  <!-- ===== 步驟 %(n)d：%(title)s ===== -->
  <section class="step hidden" data-step="%(n)d">
    <div class="bg-white border-4 border-%(t)s-300 rounded-3xl p-5 mb-4 shadow-sm">
      <p class="text-sm font-bold text-slate-500 m-0">第 %(k)d 欄／共 7 欄<span class="starbadge" data-star="%(q)s"></span><span class="qtypeSlot" data-qid="%(q)s"></span></p>
      <h2 class="cute text-3xl font-extrabold text-%(t)s-700 m-0 mt-1">%(title)s</h2>
      <p class="goal">%(goal)s</p>
    </div>
    <div class="bg-white border-4 border-amber-200 rounded-3xl p-5" data-demo="%(q)s">
      <h3 class="parth text-amber-700">看老師怎麼做</h3>
      %(demo)s
      <button type="button" class="opennext" data-open="%(q)s">看懂了，換我寫</button>
    </div>
    <div class="fillbox hidden bg-%(t)s-50 border-4 border-%(t)s-400 rounded-3xl p-5 mt-4" data-part="%(q)s">
      <div class="parthrow"><h3 class="parth text-%(t)s-700">換你寫</h3><button type="button" class="reviewbtn" data-review="%(q)s">再看一次示範</button></div>
      %(todo)s
      %(fill)s
      <ul class="checks" data-checks="%(q)s"></ul>
    </div>
    <div class="ckptbar" data-ckpt></div>
    <div class="stepnav"></div>
  </section>
''' % {'n': n, 'k': k, 't': tone, 'title': title, 'goal': goal, 'q': qid, 'demo': demo, 'todo': todo, 'fill': fill}


SELNAME = '<p class="selline">你選的是：<b data-selname></b></p>'

# 選訊息卡片上的難度原本是 ★☆☆，會跟「收集星星」搞混 → 改成文字
for s_, w_ in (('★☆☆', '簡單'), ('★★☆', '中等'), ('★★★', '較難')):
    CARDS_HTML = CARDS_HTML.replace('title="查證難易度：星星越多越難">%s</span>' % s_, 'title="查證難易度">難度：%s</span>' % w_)
assert '★' not in CARDS_HTML

# ---------- 步驟 1：開始 ----------
FIELD_LIST = ['查核網址', '搜尋工具', '原始內容', '查核結果', '正確資訊', '為什麼流傳', '相信的後果']
FIELD_QIDS = ['url', 'tool', 'desc', 'res', 'fact', 'why', 'risk']
FIELD_GRID = ''.join('<div class="fieldcell"><span class="starmini" data-star-mini="%s">☆</span>%d ‧ %s</div>' % (q, i + 1, t)
                     for i, (q, t) in enumerate(zip(FIELD_QIDS, FIELD_LIST)))

STEP1 = '''
  <!-- ===== 步驟 1：開始 ===== -->
  <section class="step" data-step="1">
    <div class="bg-rose-50 border-4 border-rose-400 rounded-3xl p-5 mb-5">
      <h2 class="cute text-3xl font-extrabold text-rose-700 m-0">先寫好你是誰</h2>
      <p class="goal">在最上面填年級、班級、座號。<span class="text-slate-500">例：五年 3 班 12 號 → 5、3、12</span></p>
      <p class="mt-3 mb-0 text-lg">上一節存過？<button type="button" data-loadwork class="bg-violet-600 hover:bg-violet-700 text-white font-extrabold rounded-xl px-4 py-2 text-lg">拿回我上次存的進度</button>
        <span data-resumemsg class="ml-2 text-base font-bold text-violet-700"></span></p>
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">今天的任務</h2>
      <p class="goal">查一則網路訊息，寫成 7 欄的查證報告。</p>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3">%s</div>
      <p class="goal mt-4">每寫好一欄，就收集一顆 <span class="starmini on">★</span>。</p>
      <p class="text-lg text-slate-600 mt-2 mb-0">寫不完？按黃色的「先存檔交一次」，下次拿回來接著寫。</p>
    </div>
    <div class="stepnav"></div>
  </section>
''' % FIELD_GRID

# ---------- 步驟 2：選訊息 ----------
STEP2 = '''
  <!-- ===== 步驟 2：選訊息 ===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-rose-700 m-0">選一則你要查的訊息</h2>
      <p class="goal">6 則都在網路上流傳過。選一則，按「選這則」。</p>
      <div class="flex items-center gap-2 flex-wrap mt-2"><span class="qtypeSlot" data-qid="sel"></span></div>
      <ul class="checks" data-checks="sel"></ul>
    </div>
''' + CARDS_HTML + '''
    <div class="ckptbar" data-ckpt></div>
    <div class="stepnav"></div>
  </section>
'''

# ---------- 步驟 3：找查核文章 ----------
STEP3 = '''
  <!-- ===== 步驟 3：找查核文章 ===== -->
  <section class="step hidden" data-step="3">
    <div class="bg-white border-4 border-teal-300 rounded-3xl p-5 mb-4 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-teal-700 m-0">找到查核文章</h2>
      <p class="goal">找到查核機構寫的那一篇。</p>
      %(sel)s
      <p data-hint class="text-lg text-slate-600 mt-1 mb-0"></p>
    </div>
    <div class="bg-white border-4 border-amber-200 rounded-3xl p-5" data-demo="find">
      <h3 class="parth text-amber-700">看老師怎麼做</h3>
      <p class="mhead">方法一：用關鍵字找</p>
      %(v1)s
      <p class="mhead">方法二：用智慧鏡頭找（訊息有圖片時）</p>
      %(v2)s
      <button type="button" class="opennext" data-open="find">看懂了，換我找</button>
    </div>
    <div class="fillbox hidden bg-teal-50 border-4 border-teal-400 rounded-3xl p-5 mt-4" data-part="find">
      <div class="parthrow"><h3 class="parth text-teal-700">換你找</h3><button type="button" class="reviewbtn" data-review="find">再看一次示範</button></div>
      <p class="mhead">用關鍵字</p>
      %(todo)s
      <p class="mhead">訊息有圖片：用智慧鏡頭</p>
      %(todo2)s
      %(links)s
      <p class="goal mt-4">找到了？<b class="text-rose-700">這個分頁不要關</b>，下一步要用。</p>
      <details class="mt-4 bg-white border-2 border-sky-200 rounded-2xl p-3">
        <summary class="cursor-pointer font-extrabold text-sky-700 text-lg">訊息是影片？先截一張圖，再用智慧鏡頭找</summary>
        %(v3)s
      </details>
    </div>
    <div class="ckptbar" data-ckpt></div>
    <div class="stepnav"></div>
  </section>
''' % {
    'sel': SELNAME,
    'v1': media('教學_找到查核文章', '用關鍵字找到查核文章'),
    'todo': steps('圈 2～3 個關鍵詞，最後加「<b>查核</b>」',
                  '用 Google 搜尋，<b>跳過</b>最上面的 AI 摘要',
                  '點<b>台灣事實查核中心</b>或 <b>MyGoPen</b> 的文章'),
    'todo2': steps('在圖片上按右鍵，選「用 Google <b>智慧鏡頭</b>搜尋」',
                   '看右邊的結果，點<b>查核機構</b>的文章'),
    'links': LINKS,
    'v2': media('智慧鏡頭', '圖片按右鍵 → 智慧鏡頭 → 看右邊的結果', '@@A4@@'),
    'v3': media('截圖google圖片搜尋_字卡', '影片：先按 Win＋Shift＋S 截一張圖再找'),
}

# ---------- 7 個填寫節點（一欄一頁）----------
N_URL = node(4, 1, 'indigo', '查核網址', '把查核文章的網址貼過來。', 'url',
    media('步_網址0_貼到學習單_v2', '複製網址列，回來貼上'),
    steps('回到查核文章，點上面的<b>網址列</b>',
          '按 ' + kb('Ctrl', 'C') + ' 複製',
          '點下面的框，按 ' + kb('Ctrl', 'V') + ' 貼上'),
    '<label class="lb" for="f_url">查核文章的網址</label>'
    '<input id="f_url" class="fld mt-1" data-k="url" autocomplete="off" inputmode="url">'
    '<p class="mt-2 mb-0"><a data-urltest href="#" target="_blank" rel="noopener" class="hidden inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl px-4 py-2">測試連結：開開看</a></p>')

N_TOOL = node(5, 2, 'teal', '你使用的搜索工具', '你是用什麼方法找到的？', 'tool',
    ex('工具：<b>關鍵字搜尋</b><br>我輸入的是：陌生人 操作手機 生物特徵 查核'),
    steps('選你剛剛用的工具（可以選兩個）',
          '選了關鍵字搜尋：把<b>搜尋框裡的字</b>抄下來'),
    '<p class="lb">① 我用的工具</p>' +
    chips('toolKinds', ['關鍵字搜尋', '以圖搜圖', '智慧鏡頭'], True) +
    '<div data-kwonly class="hidden">'
    '<label class="lb" for="f_toolB">② 我輸入的是</label>'
    '<input id="f_toolB" class="fld mt-1" data-k="toolB" autocomplete="off"></div>')

N_DESC = node(6, 3, 'amber', '原始內容描述', '<b>看到什麼寫什麼</b>：這則訊息說了什麼？不猜、不寫真的假的。', 'desc',
    ex('網傳訊息說：只要<span class="hl">幫路上的陌生人操作手機</span>' + tag('什麼事') +
       '，<span class="hl">指紋、聲音和臉就會被偷走，拿去貸款</span>' + tag('會怎樣') +
       '。這則訊息在<span class="hl">臉書</span>' + tag('在哪裡') + '流傳。',
       '老師只寫訊息上看得到的字，沒有加自己的想法。') +
    # 選的是影片：多一張「影片這樣寫」（句型，不是答案）
    '<div data-forkind="video" class="hidden exbox mt-3"><p class="exh">影片這樣寫</p><div>網傳影片中，<b>＿＿</b>' + tag('誰') +
    '在<b>＿＿</b>' + tag('做什麼') + '，影片說<b>＿＿</b>' + tag('字幕或說的話') +
    '。這支影片在<b>＿＿</b>' + tag('在哪裡') + '流傳。</div></div>',
    # 換你寫：先把選的訊息放出來，邊看邊寫
    '<div class="selbox"><p class="m-0 font-extrabold text-lg">你選的訊息：<span data-selname></span></p>'
    '<div data-selmedia class="mt-2"></div>'
    '<p data-forkind="img" class="hidden exnote">點圖可以放大。看上面的字，邊看邊寫。</p>'
    '<p data-forkind="video" class="hidden exnote">按播放，看完再寫。可以重看。</p></div>'
    '<div data-forkind="img" class="hidden">' + steps('看圖上的字：說了<b>什麼事</b>？',
          '它說<b>會怎樣</b>？要大家做什麼？',
          '在<b>哪裡流傳</b>？看不出來就寫「網路上」') + '</div>'
    '<div data-forkind="video" class="hidden">' + steps('看影片：<b>誰</b>在<b>做什麼</b>？',
          '字幕或說話，說了<b>什麼</b>？',
          '在<b>哪裡流傳</b>？看不出來就寫「網路上」') + '</div>'
    '<p data-forkind="none" class="exnote">還沒選訊息？先回到「選訊息」選一則。</p>',
    '<div class="mt-3" data-forkind="img"><button type="button" data-insert="desc" data-text="網傳訊息說：" class="insbtn">插入：網傳訊息說：</button> '
    '<button type="button" data-insert="desc" data-text="這則訊息在　　流傳。" class="insbtn">插入：這則訊息在　流傳。</button></div>'
    '<div class="mt-3 hidden" data-forkind="video"><button type="button" data-insert="desc" data-text="網傳影片中，" class="insbtn">插入：網傳影片中，</button> '
    '<button type="button" data-insert="desc" data-text="影片說：" class="insbtn">插入：影片說：</button> '
    '<button type="button" data-insert="desc" data-text="這支影片在　　流傳。" class="insbtn">插入：這支影片在　流傳。</button></div>'
    '<textarea id="f_desc" class="fld mt-2" rows="4" data-k="desc" aria-label="原始內容描述"></textarea>')

N_RES = node(7, 4, 'rose', '查核結果', '查核機構給了什麼結果？', 'res',
    media('步_結果_看標籤_v2', '看標題前的標籤，再看「你可以先知道」') +
    ex('MyGoPen' + tag('哪一家') + ' 查核後標為「誤導」' + tag('標籤') +
       '，重點是這個說法在技術和金融上都不合理' + tag('重點') + '。'),
    steps('選<b>哪一家</b>查的',
          '選<b>標籤</b>（照文章寫）',
          '用一句話寫<b>重點</b>'),
    '<p class="lb">① 哪一家查的</p>' + chips('resOrg', ['台灣事實查核中心', 'MyGoPen 麥擱騙', '其他查核機構']) +
    '<p class="lb">② 標籤</p>' + chips('resLabel', ['錯誤', '誤導', '易誤解', '事實釐清', '詐騙', '部分錯誤', '正確', '其他']) +
    '<label class="lb" for="f_resNote">③ 一句重點</label>'
    '<textarea id="f_resNote" class="fld mt-1" rows="3" data-k="resNote"></textarea>')

N_FACT = node(8, 5, 'emerald', '正確資訊', '真正的事實是什麼？<b>先寫 1 點</b>就可以。', 'fact',
    ex('1. <span class="hl">根據 MyGoPen</span>，只有指紋或臉，不能直接拿去貸款。<br>'
       '2. <span class="hl">警方和 165 說</span>，台灣查不到這種案件。',
       '黃色＝是誰說的。用自己的話寫，不要整段貼上。'),
    steps('找出<b>最重要</b>的一件事實',
          '用自己的話寫成<b>一句</b>',
          '寫出是<b>誰說的</b>（根據○○）'),
    '<div class="mt-3"><button type="button" data-insert="fact" data-text="根據　　，" class="insbtn">插入：根據……</button> '
    '<button type="button" data-insert="fact" data-text="　　說，" class="insbtn">插入：○○說……</button></div>'
    '<textarea id="f_fact" class="fld mt-2" rows="5" data-k="fact" aria-label="正確資訊"></textarea>')

N_WHY = node(9, 6, 'violet', '為什麼會流傳', '這則訊息為什麼讓人想轉傳？', 'why',
    ex('訊息說「<span class="hl">30 分鐘傾家蕩產</span>」，讓人' + tag('怕') + '；'
       '又寫「<span class="hl">轉傳給家人朋友</span>」，大家覺得轉傳是' + tag('關心家人') + '。',
       '黃色＝訊息裡的原句。'),
    steps('找出訊息裡<b>讓人想轉傳</b>的那一句',
          '寫出這句話讓人有什麼<b>感覺</b>（怕？好奇？想幫忙？）'),
    '<label class="lb" for="f_whyText">為什麼大家想轉傳？</label>'
    '<textarea id="f_whyText" class="fld mt-1" rows="4" data-k="whyText"></textarea>')

N_RISK = node(10, 7, 'rose', '相信的後果', '如果有人相信了，會怎樣？', 'risk',
    ex('<span class="hl">有人</span>' + tag('誰') + '怕到不敢幫真的需要幫忙的人' + tag('會怎樣') + '。'),
    steps('想一想：<b>誰</b>會相信這則訊息？',
          '寫出他相信以後，<b>會怎樣</b>'),
    '<label class="lb" for="f_riskText">誰會怎樣？</label>'
    '<textarea id="f_riskText" class="fld mt-1" rows="4" data-k="riskText"></textarea>')

# ---------- 步驟 11：預覽全部內容（內容由 engine 的 renderPreview 依作答填入）----------
STEP_PREVIEW = '''
  <!-- ===== 步驟 11：預覽全部內容 ===== -->
  <section class="step hidden" data-step="11">
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-5 mb-4 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-emerald-700 m-0">預覽全部內容</h2>
      <p class="goal">從頭看一遍。要改的，按「去改」。</p>
    </div>
    <div id="previewBox" class="bg-white border-4 border-emerald-200 rounded-3xl p-5 sm:p-7 space-y-4"></div>
    <div class="ckptbar" data-ckpt></div>
    <div class="stepnav"></div>
  </section>
'''

# ---------- 步驟 12：繳交 ----------
STEP_SUBMIT = '''
  <!-- ===== 步驟 12：繳交 ===== -->
  <section class="step hidden" data-step="12">
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-indigo-700 m-0">繳交</h2>
      <p class="goal">還沒寫完的，按「去寫」。</p>
      <div id="sumList" class="mt-3 space-y-2"></div>
    </div>
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-5 shadow-sm text-center">
      <p class="text-lg text-slate-600 mt-0 mb-3">確定好了，按下面的按鈕交給老師。可以重交。</p>
      <button id="submitBtn" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white cute text-xl font-extrabold rounded-2xl py-3">繳交學習單</button>
      <p id="submitStat" class="text-sm font-bold mt-3 min-h-[20px]"></p>
    </div>
    <div id="rewardBox" class="hidden text-center bg-gradient-to-b from-indigo-100 to-sky-100 border-4 border-indigo-300 rounded-3xl p-7 mt-6">
      <div class="pop" style="font-size:64px;line-height:1;color:#f59e0b">★</div>
      <h2 class="cute text-3xl font-extrabold text-indigo-700">恭喜你已經做完今日的作業，可以遊玩！</h2>
      <p id="starFinal" class="text-xl font-extrabold text-amber-700 mt-2 mb-0"></p>
      <div class="flex flex-wrap gap-3 justify-center mt-4">
        <a href="https://boyinslps.github.io/typehero/index.html" target="_blank" rel="noopener" class="cute inline-block bg-indigo-600 hover:bg-indigo-700 text-white text-xl font-extrabold rounded-2xl px-8 py-3">打字英雄</a>
        <a href="https://boyinslps.github.io/pcclass/games/" target="_blank" rel="noopener" class="cute inline-block bg-white border-4 border-indigo-300 hover:bg-indigo-50 text-indigo-700 text-xl font-extrabold rounded-2xl px-8 py-3">更多遊戲</a>
      </div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

TOP = '''<body class="text-slate-800">

<!-- 教師檢視模式橫幅（?review= 時顯示） -->
<div id="reviewBanner" class="hidden bg-amber-400 text-amber-950 text-sm font-bold">
  <div class="max-w-5xl mx-auto px-4 py-2 flex items-center gap-3 flex-wrap">
    <span id="reviewText">檢視模式（唯讀）</span>
    <a id="reviewExit" href="#" class="ml-auto underline">離開檢視</a>
  </div>
</div>

<!-- 老師工具列（僅 #admin 時顯示） -->
<div id="teacherbar" class="hidden bg-slate-900 text-white text-sm">
  <div class="max-w-5xl mx-auto px-4 py-2 flex items-center gap-2 flex-wrap">
    <span class="cute font-bold text-amber-300">教師模式</span>
    <span id="tStatus" class="text-slate-300 text-xs"></span>
    <div class="ml-auto flex gap-2 flex-wrap">
      <button id="showAnsBtn" class="hidden bg-emerald-600 hover:bg-emerald-700 rounded-lg px-3 py-1" title="把老師的示範答案填進學習單的作答欄">檢視答案</button>
      <button id="lockBtn" class="hidden bg-slate-700 hover:bg-slate-600 rounded-lg px-3 py-1" title="清掉「檢視答案」填進去的內容">↩ 還原</button>
      <button id="previewModeBtn" class="bg-indigo-600 hover:bg-indigo-700 font-bold rounded-lg px-3 py-1">預覽學生模式</button>
    </div>
  </div>
</div>
<button id="backToTeacher" class="hidden fixed bottom-4 right-4 z-30 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold rounded-full px-4 py-2 shadow-lg">↩ 返回教師模式</button>

<!-- 固定在上方：我是誰＋學習路徑＋進度 -->
<div class="sticky top-0 z-30 bg-white/95 backdrop-blur border-b-2 border-indigo-200">
  <div class="max-w-5xl mx-auto px-4 pt-2 flex items-center gap-3 flex-wrap text-sm">
    <span class="cute font-bold text-indigo-700">我是誰</span>
    <label class="flex items-center gap-1 text-slate-500">年級<input id="idGrade" class="idnum border-2 border-slate-200 rounded-lg px-2 py-1 font-bold text-slate-700 focus:border-indigo-400 outline-none" inputmode="numeric" maxlength="2"></label>
    <label class="flex items-center gap-1 text-slate-500">班級<input id="idClass" class="idnum border-2 border-slate-200 rounded-lg px-2 py-1 font-bold text-slate-700 focus:border-indigo-400 outline-none" inputmode="numeric" maxlength="2"></label>
    <label class="flex items-center gap-1 text-slate-500">座號<input id="idStudent" class="idnum border-2 border-slate-200 rounded-lg px-2 py-1 font-bold text-slate-700 focus:border-indigo-400 outline-none" inputmode="numeric" maxlength="2"></label>
    <span id="idOk" class="hidden text-emerald-600 font-bold text-xs">✓ 已記住</span>
    <span id="idNeed" class="hidden text-rose-600 font-extrabold text-sm">← 先填年級、班級、座號</span>
    <span class="ml-auto flex items-center gap-2 text-xs font-bold text-slate-500"><span id="progTxt">★ 0／7</span><span class="inline-block w-24 h-2 bg-slate-200 rounded-full overflow-hidden align-middle"><span id="progBar" class="block h-full bg-emerald-500" style="width:0%"></span></span></span>
  </div>
  <div class="max-w-5xl mx-auto px-4 py-2">
    <div id="stepper" class="flex items-start"></div>
    <p id="stepLabel" class="sm:hidden text-xs font-bold text-indigo-700 text-center mt-1"></p>
  </div>
</div>

<div id="main" class="max-w-5xl mx-auto px-4 py-6">

  <header class="text-center mb-6">
    <h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">訊息查證小偵探</h1>
    <p class="text-sm text-slate-500 mt-2">五年級上學期 · L05 查證報告（週五版）· 全部寫在學習單，可分節完成</p>
    <p id="syncBadge" class="hidden mt-2 text-xs text-emerald-600 font-bold">已連線</p>
  </header>
'''

BOTTOM = '''
  <footer class="text-center text-xs text-slate-400 mt-8 pb-2">教師預覽：在網址列加上 <code class="bg-slate-200 rounded px-1">#admin</code> 後重新整理。查核文章與網傳擷圖取自台灣事實查核中心、MyGoPen 查核報告。</footer>
  <p class="text-right text-xs text-slate-400 pb-4">made by 資訊老師黃博胤</p>
</div>

<div id="toast" class="hidden" role="status"></div>

<!-- 點圖放大 -->
<div id="lightbox" role="dialog" aria-modal="true" aria-label="放大看圖">
  <div class="lbtop">
    <span>滾輪放大縮小・放大後拖曳移動・雙擊還原</span>
    <button type="button" class="zbtn" id="lbOut" aria-label="縮小">－</button>
    <span id="lbPct" class="font-bold text-white w-12 text-center">100%</span>
    <button type="button" class="zbtn" id="lbIn" aria-label="放大">＋</button>
    <button type="button" class="zbtn" id="lbReset">還原</button>
    <button type="button" class="zbtn ml-auto" id="lbClose">關閉</button>
  </div>
  <div class="lbstage" id="lbStage"><img id="lbImg" alt=""></div>
</div>
'''

GRADING = '''<script type="application/json" id="grading-spec">
{
  "summary": "從 6 則真實網傳訊息中選一則，用關鍵字搜尋、以圖搜圖或智慧鏡頭找到查核機構（台灣事實查核中心或 MyGoPen）已發布的查核文章，把它整理成 7 欄查證報告：查核網址、使用的搜索工具、原始內容描述、查核結果、正確資訊、為什麼會流傳、相信的後果。全部寫在學習單裡，可用「斷點繳交」分節完成。",
  "questions": [
    { "qid": "tool", "prompt": "你使用的搜索工具（關鍵字、以圖搜圖、智慧鏡頭）：用了什麼工具；用關鍵字搜尋的，輸入了什麼", "mode": "checklist",
      "checks": [
        { "desc": "說出使用的工具（關鍵字搜尋、以圖搜圖、智慧鏡頭至少一種）", "pts": 1 },
        { "desc": "選了關鍵字搜尋的，寫出在 Google 輸入的字，且最後有加「查核」（沒選關鍵字搜尋的此項直接給分）", "pts": 1 } ] },
    { "qid": "desc", "prompt": "原始內容描述：只描述網傳訊息或影片說了什麼，不做查證判斷", "mode": "checklist",
      "checks": [
        { "desc": "用自己的話說出訊息講了什麼事、說會怎樣，並說明在哪裡流傳", "pts": 2 },
        { "desc": "只描述，沒有加入「是假的」「不要相信」這類真假判斷", "pts": 1 } ] },
    { "qid": "res", "prompt": "查核結果：哪個查核機構、標了什麼結果、一句重點", "mode": "checklist",
      "checks": [
        { "desc": "寫出查核機構名稱", "pts": 1 },
        { "desc": "標籤照查核文章寫（例如錯誤、誤導）", "pts": 1 },
        { "desc": "有一句重點，說明為什麼是這個結果", "pts": 1 } ] },
    { "qid": "fact", "prompt": "正確資訊：用自己的話整理查核文章說的事實，1～3 點，並標出是誰說的", "mode": "checklist",
      "checks": [
        { "desc": "用自己的話寫 1～3 點，沒有整段複製查核文章", "pts": 2 },
        { "desc": "有標出是哪個機構或人（警方、165、查核機構、專家等）說的", "pts": 1 } ] },
    { "qid": "why", "prompt": "為什麼這則訊息會被廣傳？", "mode": "checklist",
      "checks": [
        { "desc": "說出這則訊息讓人有什麼感覺或想法（例如怕、好奇、想幫忙）", "pts": 1 },
        { "desc": "說明理由，最好指出訊息裡的哪句話造成的", "pts": 1 } ] },
    { "qid": "risk", "prompt": "如果相信這則訊息，會有什麼後果？（誰會怎樣）", "mode": "levels", "points": 2,
      "standard": "說出誰會怎樣；只寫「是假的」或「會被騙」不給分" }
  ],
  "scoring": { "base": 100, "floor": 80, "deduction": 1,
    "itemPoints": { "sel": 1, "url": 2 } }
}
</script>'''


def build(assets, assets4=None):
    # L04 素材：教材資料夾 ../L04_認識農場文與業配文/assets/、發布資料夾 ../L04/assets/
    if assets4 is None:
        assets4 = assets.replace('L05_Docs查證文件一', 'L04_認識農場文與業配文') if 'L05_Docs' in assets else assets.replace('/L05/', '/L04/')
    body = (TOP + STEP1 + STEP2 + STEP3 + N_URL + N_TOOL + N_DESC + N_RES + N_FACT + N_WHY + N_RISK + STEP_PREVIEW + STEP_SUBMIT + BOTTOM)
    engine = io.open(os.path.join(HERE, 'engine_L05_fri.js'), encoding='utf8').read().replace('/*FIREBASE_CONFIG*/', FIREBASE_CFG)
    html = (HEAD_CSS + EXTRA_CSS + '</head>\n' + body + '\n<script>\n' + engine + '\n</script>\n\n' + GRADING + '\n' + CHAIR + '\n' + STEPCARDS + '\n</body>\n</html>\n')
    return html.replace('@@A4@@', assets4).replace('@@A@@', assets)


def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, 'w', encoding='utf8', newline='\n').write(html)
    print('寫出', path, len(html))


if __name__ == '__main__':
    # lesson-prep 教材資料夾：素材沿用 L05 的 assets；pcclass 發布資料夾：g5/L05-fri 與 g5/L05 同層
    write(os.path.join(ROOT, 'L05_週五版', '五上_L05_週五版.html'), build('../L05_Docs查證文件一/assets/'))
    write(os.path.join(PCCLASS, 'g5', 'L05-fri', 'index.html'), build('../L05/assets/'))
