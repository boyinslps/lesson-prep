# -*- coding: utf-8 -*-
# 產生「五上 L05 週五版」學習單：L05（找查核文章）＋ L06（整理成報告）合成一份，
# 全部寫在學習單裡（不開 Google 文件，所以沒有標題 1/2、超連結、貼格式這些排版步驟）。
#
# 流程：開始 → 老師示範 → 選訊息 → 找查核文章 → 8 個填寫節點 → 檢查繳交
# 8 個節點（照老師指定順序）：查核報告標題、查核網址、你使用的搜索工具、原始內容描述、
#                              查核結果、正確資訊、為什麼會流傳、相信的後果
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
  @keyframes idp{0%,100%{box-shadow:0 0 0 0 rgba(244,63,94,.5)}50%{box-shadow:0 0 0 6px rgba(244,63,94,0)}}
</style>
'''

# ---------- 小零件 ----------
def media(name, cap=''):
    return ('<div class="sc sc-flat sc-nonum" data-sc><div class="sc-slide"><p class="sc-t">%s</p>'
            '<div class="sc-media" data-src="@@A@@%s.mp4" data-poster="@@A@@%s_封面.jpg"></div></div></div>') % (cap, name, name)


def clips(label, *items):
    """操作影片收在「看操作影片」裡（點開才載入）。items＝(檔名, 說明)"""
    return ('<details class="mt-4 bg-slate-50 border-2 border-slate-300 rounded-2xl p-3"><summary class="cursor-pointer font-extrabold text-slate-700 text-lg">%s</summary>'
            '<div class="mt-3">%s</div></details>') % (label, ''.join(media(n, c) for n, c in items))


def chips(key, items, multi=False, cls=''):
    return '<div class="flex flex-wrap gap-2 mt-2 %s" data-chips="%s"%s>%s</div>' % (
        cls, key, ' data-multi="1"' if multi else '',
        ''.join('<button type="button" class="chip" data-v="%s">%s%s</button>' % (v, '<span class="mk">☐</span>' if multi else '', v) for v in items))


def good_bad(good, bad):
    return ('<div class="grid sm:grid-cols-2 gap-3 mt-4 text-lg">'
            '<div class="bg-emerald-50 border-2 border-emerald-300 rounded-2xl p-3"><p class="font-extrabold text-emerald-700 m-0">這樣寫才對</p><div class="mt-1 text-slate-700">%s</div></div>'
            '<div class="bg-rose-50 border-2 border-rose-300 rounded-2xl p-3"><p class="font-extrabold text-rose-700 m-0">這樣寫不夠</p><div class="mt-1 text-slate-700">%s</div></div></div>') % (good, bad)


def example_box(ex, starter=''):
    h = ('<div class="bg-amber-50 border-2 border-amber-300 rounded-2xl p-4"><p class="font-extrabold text-amber-800 m-0">範例（老師的示範：幫陌生人操作手機）</p>'
         '<div class="mt-2 text-xl text-slate-800 leading-relaxed">%s</div></div>') % ex
    if starter:
        h += ('<div class="bg-sky-50 border-2 border-sky-300 rounded-2xl p-4 mt-3"><p class="font-extrabold text-sky-800 m-0">句型（照著填就好）</p>'
              '<div class="mt-2 text-lg text-slate-700">%s</div></div>') % starter
    return h


def node(n, k, tone, title, lead, qid, how, right, fill, extra=''):
    """一個填寫節點。how＝左欄（做什麼、怎麼做）；right＝右欄（範例、好壞對照）；fill＝填寫區。"""
    return '''
  <!-- ===== 步驟 %(n)d：%(title)s ===== -->
  <section class="step hidden" data-step="%(n)d">
    <div class="bg-white border-4 border-%(t)s-300 rounded-3xl p-5 mb-5 shadow-sm">
      <p class="text-sm font-bold text-slate-500 m-0">第 %(k)d 欄／共 8 欄　<span class="qtypeSlot" data-qid="%(q)s"></span></p>
      <h2 class="cute text-3xl font-extrabold text-%(t)s-700 m-0 mt-1">%(title)s</h2>
      <p class="text-xl text-slate-700 mt-2 mb-0">%(lead)s</p>
    </div>
    <div class="grid lg:grid-cols-2 gap-5">
      <div class="bg-white border-4 border-%(t)s-200 rounded-3xl p-5">
        <h3 class="cute text-2xl font-extrabold text-%(t)s-700 m-0">怎麼做（照順序）</h3>
        %(how)s
      </div>
      <div class="bg-white border-4 border-amber-200 rounded-3xl p-5">%(right)s</div>
    </div>
    <div class="fillbox bg-%(t)s-50 border-4 border-%(t)s-400 rounded-3xl p-5 mt-5">
      <h3 class="cute text-2xl font-extrabold text-%(t)s-700 m-0">換你寫：%(title)s</h3>
      %(fill)s
      <ul class="checks" data-checks="%(q)s"></ul>
    </div>%(extra)s
    <div class="ckptbar" data-ckpt></div>
    <div class="stepnav"></div>
  </section>
''' % {'n': n, 'k': k, 't': tone, 'title': title, 'lead': lead, 'q': qid, 'how': how, 'right': right, 'fill': fill, 'extra': extra}


def how(*items):
    return '<ol class="howlist">%s</ol>' % ''.join('<li>%s</li>' % i for i in items)


def kb(*ks):
    return '＋'.join('<kbd>%s</kbd>' % k for k in ks)


SELNAME = '<div class="bg-teal-50 border-2 border-teal-200 rounded-2xl px-4 py-2 mt-3 text-lg">你選的是：<b data-selname class="text-teal-800">（還沒選，請回第 3 步）</b></div>'

# ---------- 步驟 1：開始 ----------
FIELD_LIST = [
    ('1', '查核報告標題', '查核機構那篇文章的標題'),
    ('2', '查核網址', '那篇文章的整條網址'),
    ('3', '你使用的搜索工具', '關鍵字、以圖搜圖、智慧鏡頭'),
    ('4', '原始內容描述', '只描述訊息說了什麼，不判斷真假'),
    ('5', '查核結果', '哪個機構、標了什麼'),
    ('6', '正確資訊', '真正的事實，用自己的話'),
    ('7', '為什麼會流傳', '為什麼大家想轉傳'),
    ('8', '相信的後果', '相信了，誰會怎樣'),
]
FIELD_GRID = ''.join('<div class="bg-indigo-50 border-2 border-indigo-200 rounded-2xl p-3"><p class="font-extrabold m-0">%s ‧ %s</p><p class="text-sm text-slate-600 mt-0.5 mb-0">%s</p></div>' % f for f in FIELD_LIST)

STEP1 = '''
  <!-- ===== 步驟 1：開始 ===== -->
  <section class="step" data-step="1">
    <div class="bg-rose-50 border-4 border-rose-400 rounded-3xl p-5 mb-5">
      <h2 class="cute text-3xl font-extrabold text-rose-700 m-0">第一件事：寫好年級、班級、座號</h2>
      <p class="text-xl text-slate-800 mt-2 mb-0">畫面最上面有「我是誰」三個框，<b>先填好</b>，再往下做。不用寫名字，三個數字就好。</p>
      <ul class="list-disc pl-6 mt-2 mb-0 text-lg text-slate-700 space-y-1"><li>老師靠這三個數字找到你的作業。</li><li>例：五年 3 班 12 號 → 年級 5、班級 3、座號 12。班級是 1～14。</li><li>上次存過進度？填好三個數字，按下面的<b>「拿回我上次存的進度」</b>，就能接著寫。</li></ul>
      <p class="mt-3 mb-0"><button type="button" data-loadwork class="bg-violet-600 hover:bg-violet-700 text-white font-extrabold rounded-xl px-4 py-2 text-lg">拿回我上次存的進度</button>
        <span data-resumemsg class="ml-2 text-base font-bold text-violet-700"></span></p>
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-6 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">今天要做的事</h2>
      <p class="text-xl text-slate-700 mt-2">把一則網路上流傳的訊息查清楚，寫成一份<b>查證報告</b>。報告有 <b>8 個欄位</b>，<b>全部直接寫在這張學習單裡</b>，不用開 Google 文件。每個欄位都有「怎麼做」「範例」「檢查表」。</p>
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 text-base">%s</div>
      <div class="bg-amber-50 border-4 border-dashed border-amber-300 rounded-2xl p-4 mt-5 text-lg text-slate-800">
        <p class="font-extrabold text-amber-800 m-0">一節寫不完怎麼辦？用「斷點繳交」</p>
        <ol class="list-decimal pl-6 mt-2 mb-0 space-y-1"><li>每一步下面都有黃色的<b>「先存檔交一次」</b>按鈕，寫到哪都能按。</li><li>按了以後，老師那邊會看到你<b>已經繳交</b>，你寫的內容也<b>存起來</b>了。</li><li>下一節打開學習單，輸入<b>同樣的年級、班級、座號</b>，就能<b>拿回</b>剛才的內容，接著寫。</li><li>全部寫完，到最後一步按「繳交學習單」，會覆蓋前面存的那一份。</li></ol>
      </div>
    </div>
    <div class="stepnav"></div>
  </section>
''' % FIELD_GRID

# ---------- 步驟 2：老師示範 ----------
DEMO_ROWS = [
    ('1 ‧ 查核報告標題', '【誤導】幫陌生人操作手機會被盜取生物特徵去貸款？誇大AI技術！不符金融審核機制'),
    ('2 ‧ 查核網址', '<span class="text-indigo-700 underline break-all">https://www.mygopen.com/2026/02/ai-fraud.html</span>'),
    ('3 ‧ 你使用的搜索工具', '工具：關鍵字搜尋<br>圈出的關鍵詞：陌生人、操作手機、生物特徵<br>在 Google 輸入：陌生人 操作手機 生物特徵 查核<br>點進：MyGoPen 麥擱騙，它專門查謠言，不是轉載'),
    ('4 ‧ 原始內容描述', '網傳訊息說：只要幫路上的陌生人操作手機、摸螢幕、對著鏡頭說話，指紋、聲音和臉就會被偷走，騙子拿去貸款，30 分鐘就傾家蕩產。這則訊息在臉書流傳。'),
    ('5 ‧ 查核結果', 'MyGoPen 查核後標為「誤導」，重點是這個說法在技術和金融上都不合理。'),
    ('6 ‧ 正確資訊', '1. 根據 MyGoPen，只有指紋或臉，不能直接拿去貸款，銀行還要看很多檢查。<br>2. 警方和 165 說，台灣查不到這種案件。<br>3. 不過，陌生人要你做驗證時，還是要小心。'),
    ('7 ‧ 為什麼會流傳', '訊息說「30 分鐘傾家蕩產」，讓人怕；又寫「轉傳給家人朋友」，大家覺得轉傳是關心家人；還提到 AI 和手機，聽起來很厲害，帶點好奇。'),
    ('8 ‧ 相信的後果', '有人怕到不敢幫真的需要幫忙的人；也有人把嚇人的訊息再轉給更多人，讓大家一起害怕。'),
]
DEMO_TABLE = ''.join('<div class="grid sm:grid-cols-4 gap-2 border-t-2 border-amber-100 py-3"><p class="font-extrabold text-amber-800 m-0">%s</p><div class="sm:col-span-3 text-lg text-slate-800">%s</div></div>' % r for r in DEMO_ROWS)

STEP2 = '''
  <!-- ===== 步驟 2：老師示範 ===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700 m-0">老師示範：從訊息找到查核文章</h2>
      <p class="text-lg text-slate-600 mt-1">看老師怎麼做。示範訊息：幫陌生人操作手機，會被盜走指紋？</p>
    </div>
    <div class="bg-white border-4 border-amber-200 rounded-3xl p-5 mb-5"><div class="grid md:grid-cols-2 gap-4 items-start"><div><img class="shotimg" src="@@A@@M2_B示範_陌生人手機_網傳訊息.png" alt="示範訊息：兩則臉書貼文，標題寫「人工智能生物信息詐騙，要的不是你的錢而是你這個人」，帳號已遮蔽" loading="lazy"><p class="text-[11px] text-slate-400 mt-1">示範訊息（帳號已遮蔽）・點圖可放大</p></div><p class="text-xl text-slate-800 m-0">網傳訊息說：只要幫路上的陌生人操作手機、摸螢幕、對著鏡頭說話，指紋、聲音和臉就會被偷走，騙子拿去貸款，30 分鐘就傾家蕩產。</p></div></div>
    <div class="sc sc-flat" data-sc>
      <div class="sc-slide"><p class="sc-t">圈出 2～3 個<b>關鍵詞</b></p><p class="text-lg mt-2">不要整句貼去搜。例：<span class="bg-amber-50 border border-amber-300 rounded-lg px-2 font-bold">陌生人</span> <span class="bg-amber-50 border border-amber-300 rounded-lg px-2 font-bold">操作手機</span> <span class="bg-amber-50 border border-amber-300 rounded-lg px-2 font-bold">生物特徵</span></p></div>
      <div class="sc-slide"><p class="sc-t">Google 打「關鍵詞＋<b>查核</b>」</p><p class="text-lg mt-2 bg-amber-50 border-2 border-amber-200 rounded-xl px-3 py-2">陌生人 操作手機 生物特徵 查核</p></div>
      <div class="sc-slide"><p class="sc-t">認出<b>查核機構</b></p><p class="text-lg mt-2">看<b>機構名稱</b>：<b>台灣事實查核中心</b>、<b>MyGoPen 麥擱騙</b>，才是專門查謠言的。新聞、貼文是轉載，要點到原始的查核機構。</p></div>
      <div class="sc-slide"><p class="sc-t">只讀<b>兩個地方</b></p><p class="text-lg mt-2">標題前的<b>標籤</b>（錯誤、誤導…），和最上面的「<b>你可以先知道</b>」。</p></div>
      <div class="sc-slide"><p class="sc-t">結果</p><p class="text-lg mt-2">MyGoPen「誤導」、台灣事實查核中心「錯誤」，結論一致。</p><p class="text-lg mt-1 text-rose-700 font-bold">搜尋結果最上面的 AI 摘要先跳過，要讀的是查核機構寫的原始文章。</p></div>
    </div>
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h3 class="cute text-2xl font-extrabold text-amber-700 m-0">老師寫好的 8 欄長這樣</h3>
      <p class="text-base text-slate-500 mt-1">你的報告每一欄只要像這樣，1～3 句就夠，不用比這份長。你要換成<b>你自己選的那一則</b>，不能照抄。</p>
      %s
    </div>
    <div class="stepnav"></div>
  </section>
''' % DEMO_TABLE

# ---------- 步驟 3：選訊息 ----------
STEP3 = '''
  <!-- ===== 步驟 3：選訊息 ===== -->
  <section class="step hidden" data-step="3">
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-rose-700">選一則你要查的訊息</h2>
      <p class="text-slate-600 mt-2 text-lg">下面 6 則都是真的在網路上流傳過的：有<b>圖片</b>、有<b>影片</b>。選<b>一則</b>，用今天學的方法查它。選好會顯示「我選這則」。</p>
      <div class="mt-3 bg-amber-50 border-2 border-amber-200 rounded-2xl p-3 text-base text-slate-700">
        <p class="font-bold text-amber-800">查證難易度：星星越多越難查</p>
        <div class="grid sm:grid-cols-3 gap-2 mt-2">
          <p><span class="text-amber-500 font-extrabold tracking-wider">★☆☆</span> <b>簡單</b>：搜尋第一頁就找得到，結果很明確</p>
          <p><span class="text-amber-500 font-extrabold tracking-wider">★★☆</span> <b>中等</b>：要多讀一點，或多換幾個關鍵詞</p>
          <p><span class="text-amber-500 font-extrabold tracking-wider">★★★</span> <b>較難</b>：結果很細微，或要分辨轉載與原始查核機構</p>
        </div>
      </div>
      <div class="flex items-center gap-2 flex-wrap mt-2"><span class="qtypeSlot" data-qid="sel"></span></div>
      <ul class="checks" data-checks="sel"></ul>
    </div>
''' + CARDS_HTML + '''
    <div class="ckptbar" data-ckpt></div>
    <div class="stepnav"></div>
  </section>
'''

# ---------- 步驟 4：找查核文章 ----------
STEP4 = '''
  <!-- ===== 步驟 4：找查核文章 ===== -->
  <section class="step hidden" data-step="4">
    <div class="bg-white border-4 border-teal-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-teal-700">換你查：找到查核文章</h2>
      <div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-4 mt-3 text-lg">
        <p class="m-0">你選的是：<b data-selname class="text-teal-800">（還沒選，請回第 3 步）</b></p>
        <p data-hint class="text-slate-600 mt-1 mb-0"></p>
      </div>
    </div>
    <div class="bg-teal-50 border-4 border-teal-200 rounded-3xl p-5 mb-5">
      <p class="cute text-2xl font-extrabold text-teal-700 mb-2">在新分頁，把查核文章找出來</p>
      <ol class="howlist">
        <li>圈 2～3 個<b class="text-teal-700">關鍵詞</b>（訊息有圖，也可以直接用圖片搜）。</li>
        <li>打開 Google，輸入「關鍵詞＋<b class="text-teal-700">查核</b>」，按 Enter。</li>
        <li>在結果裡，點機構名稱是 <b class="text-teal-700">台灣事實查核中心</b> 或 <b class="text-teal-700">MyGoPen 麥擱騙</b> 的那一篇。</li>
        <li>讀懂它：看標題前的<b class="text-teal-700">標籤</b>（錯誤、誤導…），再讀最上面的「<b class="text-teal-700">你可以先知道</b>」。</li>
        <li><b class="text-rose-700">這個分頁先不要關</b>：接下來 8 欄都要回來這一篇複製或查看。</li>
      </ol>
      <div class="flex flex-wrap gap-2 mt-4">
        <a href="https://www.google.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2">Google 搜尋 ↗</a>
        <a href="https://tfc-taiwan.org.tw/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2"><img src="https://www.google.com/s2/favicons?domain=tfc-taiwan.org.tw&sz=64" class="w-5 h-5 bg-white rounded" alt="">台灣事實查核中心 ↗</a>
        <a href="https://www.mygopen.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2"><img src="https://www.google.com/s2/favicons?domain=mygopen.com&sz=64" class="w-5 h-5 bg-white rounded" alt="">MyGoPen 麥擱騙 ↗</a>
      </div>
      <div class="mt-4 bg-white border-2 border-rose-200 rounded-2xl p-3 text-lg text-slate-700">搜尋結果最上面的 <b>AI 摘要先跳過</b>。新聞、臉書貼文只是<b>轉載</b>，要點到<b>原始的查核機構</b>。</div>
      %s
      <div class="bg-white border-2 border-sky-200 rounded-2xl p-4 mt-4">
        <p class="cute text-xl font-extrabold text-sky-700 m-0">搜不到？換「以圖搜圖」或「智慧鏡頭」</p>
        <p class="text-lg text-slate-700 mt-1 mb-0">第 7 欄會請你寫用了哪個工具，所以先記得自己用了什麼。</p>
        %s
      </div>
    </div>
    <div class="ckptbar" data-ckpt></div>
    <div class="stepnav"></div>
  </section>
''' % (
    clips('不會找？看操作影片：從訊息找到查核文章（約 1 分鐘）', ('教學_找到查核文章', '關鍵字搜尋：從訊息找到查核文章')),
    clips('看操作影片：以圖搜圖、智慧鏡頭', ('教學_以圖搜圖兩種方法', '圖片：智慧鏡頭，或相機圖示貼上圖片'), ('截圖google圖片搜尋_字卡', '影片：按 Win＋Shift＋S 截圖，再搜')))

# ---------- 8 個填寫節點 ----------
N_TITLE = node(5, 1, 'sky', '查核報告標題',
    '把查核機構那篇文章的<b>標題整句複製</b>過來。是<b>查核報告</b>的標題，<u>不是</u>網傳訊息的標題。', 'title',
    how('回到剛剛找到的<b>查核文章分頁</b>（瀏覽器上方的分頁，沒有關就還在）。',
        '找到文章最上面<b>最大的標題</b>（前面常有【誤導】【錯誤】這種標籤，也要一起複製）。',
        '用滑鼠從標題第一個字<b>拖曳到最後一個字</b>，按 ' + kb('Ctrl', 'C') + ' 複製。',
        '回到這裡，點下面的框，按 ' + kb('Ctrl', 'V') + ' 貼上。') +
        clips('看操作影片：複製標題', ('步_標題A_複製標題', '到查核文章，選取查核報告的標題，複製')),
    example_box('【誤導】幫陌生人操作手機會被盜取生物特徵去貸款？誇大AI技術！不符金融審核機制') +
        good_bad('和查核文章上的標題<b>一模一樣</b>，連【誤導】都有。', '自己改寫的標題；網傳訊息的標題；只寫「查核報告」。'),
    '<label class="lb" for="f_title">貼上查核報告的標題</label>'
    '<textarea id="f_title" class="fld mt-1" rows="2" data-k="title" placeholder="例：【誤導】幫陌生人操作手機會被盜取生物特徵去貸款？…"></textarea>')

N_URL = node(6, 2, 'indigo', '查核網址',
    '貼上那篇查核文章的<b>整條網址</b>，讓老師和別人能點進去驗證。', 'url',
    how('回到<b>查核文章分頁</b>，點一下最上面的<b>網址列</b>（整條網址會變成藍色反白）。',
        '按 ' + kb('Ctrl', 'C') + ' 複製。',
        '回到這裡，點下面的框，按 ' + kb('Ctrl', 'V') + ' 貼上。',
        '檢查：開頭是 <b>https://</b>，網址前後沒有多餘的字。按旁邊的「測試連結」，能開到同一篇才對。') +
        '<div class="mt-3 bg-rose-50 border-2 border-rose-200 rounded-2xl p-3 text-lg">網址要是<b>查核機構自己</b>的網站：<b>tfc-taiwan.org.tw</b>（台灣事實查核中心）或 <b>mygopen.com</b>（MyGoPen）。新聞、臉書貼文轉載的不算。</div>' +
        clips('看操作影片：複製網址', ('步_網址1_複製網址列', '回到查核文章，點網址列，複製網址')),
    example_box('<span class="text-indigo-700 underline break-all">https://www.mygopen.com/2026/02/ai-fraud.html</span>') +
        good_bad('整條網址，只有網址。', '只寫「MyGoPen」；把標題和網址混在一起；網址被截掉一半。'),
    '<label class="lb" for="f_url">貼上查核文章的網址</label>'
    '<input id="f_url" class="fld mt-1" data-k="url" autocomplete="off" placeholder="https://" inputmode="url">'
    '<p class="mt-2 mb-0"><a data-urltest href="#" target="_blank" rel="noopener" class="hidden inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl px-4 py-2">測試連結：開開看 ↗</a></p>')

N_TOOL = node(7, 3, 'teal', '你使用的搜索工具',
    '寫出你是<b>怎麼找到</b>查核文章的：用了哪個工具、搜了什麼、點進哪個網站。讓別人照著做也找得到。', 'tool',
    '<p class="text-lg text-slate-700 mt-2 mb-0">三種工具，用了哪個就選哪個（可以選不只一個）：</p>'
    '<div class="space-y-2 mt-2 text-lg">'
    '<div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-3"><b class="text-teal-800">關鍵字搜尋</b>：訊息是文字。圈 2～3 個關鍵詞，加上「查核」，打在 Google。</div>'
    '<div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-3"><b class="text-teal-800">以圖搜圖</b>：訊息有圖。到 Google 圖片搜尋，按<b>相機圖示</b>，貼上圖片或上傳。</div>'
    '<div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-3"><b class="text-teal-800">智慧鏡頭</b>：在圖片上按右鍵，選有「Google 智慧鏡頭」字樣的那一項；影片先按 ' + kb('Win', 'Shift', 'S') + ' 截一張圖再搜。</div></div>' +
        clips('看操作影片：三種搜尋工具', ('教學_找到查核文章', '關鍵字搜尋'), ('教學_以圖搜圖兩種方法', '以圖搜圖／智慧鏡頭'), ('截圖google圖片搜尋_字卡', '影片先截圖再搜')),
    example_box('<b>工具：</b>關鍵字搜尋<br><b>圈出的關鍵詞：</b>陌生人、操作手機、生物特徵<br><b>我在 Google 輸入：</b>陌生人 操作手機 生物特徵 查核<br><b>我點進：</b>MyGoPen 麥擱騙，它專門查謠言，不是轉載') +
        good_bad('三件事都寫：關鍵詞（或圖）、搜了什麼、點進哪個網站為什麼可信。', '只寫「我用 Google 找的」；只寫「查核網站」沒說哪一個。'),
    '<p class="lb">① 我用的工具（可複選）</p>' +
    chips('toolKinds', ['關鍵字搜尋', '以圖搜圖', '智慧鏡頭'], True) +
    '<label class="lb" for="f_toolA">② 我圈出的關鍵詞（或我用的是哪張圖／哪段影片截圖）</label>'
    '<input id="f_toolA" class="fld mt-1" data-k="toolA" autocomplete="off" placeholder="例：陌生人、操作手機、生物特徵">'
    '<label class="lb" for="f_toolB">③ 我在 Google 輸入（或上傳）的是 <small>用了關鍵字的話，後面要加「查核」</small></label>'
    '<input id="f_toolB" class="fld mt-1" data-k="toolB" autocomplete="off" placeholder="例：陌生人 操作手機 生物特徵 查核">'
    '<label class="lb" for="f_toolC">④ 我點進哪個網站？為什麼它是查核機構？</label>'
    '<textarea id="f_toolC" class="fld mt-1" rows="2" data-k="toolC" placeholder="例：點進 MyGoPen 麥擱騙，它專門查謠言，不是轉載。"></textarea>')

N_DESC = node(8, 4, 'amber', '原始內容描述',
    '只說這則訊息或影片<b>說了什麼</b>，像向沒看過的朋友轉述。<b>不要寫它是真的還是假的</b>，那是下一欄的事。', 'desc',
    how('重新看一次你選的訊息（圖片或影片）。',
        '想這 6 件事，訊息裡<b>沒有說</b>的就寫「沒說」：<div class="grid grid-cols-3 gap-2 mt-2 text-center text-base"><div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>人：誰</b></div><div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>事：做什麼</b></div><div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>時：何時</b></div><div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>地：哪裡</b></div><div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>物：什麼東西</b></div><div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>傳播：在哪傳</b></div></div>',
        '用 1～3 句話連起來，<b>用自己的話</b>，不要整段抄訊息。按下面「插入句型」可以先得到開頭。',
        '檢查：有沒有不小心寫了「這是假的」「不要相信」？有的話<b>刪掉</b>，留到「查核結果」再寫。') + SELNAME,
    example_box('網傳訊息說：只要幫路上的陌生人操作手機、摸螢幕、對著鏡頭說話，指紋、聲音和臉就會被偷走，騙子拿去貸款，30 分鐘就傾家蕩產。這則訊息在臉書流傳。',
                '網傳訊息說：<b>＿＿</b>（人）在<b>＿＿</b>（地），<b>＿＿</b>（事）……這則訊息在<b>＿＿</b>流傳。') +
        good_bad('只講訊息<b>本身說了什麼</b>，也說了在哪裡流傳。', '「這是假訊息，不要相信」（這是判斷，不是描述）；「一則很可怕的訊息」（沒說內容）。'),
    '<label class="lb" for="f_desc">用自己的話描述這則訊息或影片 <small>只描述，不判斷真假</small></label>'
    '<div class="mt-1"><button type="button" data-insert="desc" data-text="網傳訊息說：" class="bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-3 py-1">插入句型：網傳訊息說：</button> '
    '<button type="button" data-insert="desc" data-text="這則訊息在　　流傳。" class="bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-3 py-1">插入句型：這則訊息在　流傳</button></div>'
    '<textarea id="f_desc" class="fld mt-2" rows="4" data-k="desc" placeholder="網傳訊息說：……這則訊息在＿＿流傳。"></textarea>')

N_RES = node(9, 5, 'rose', '查核結果',
    '查核機構看完以後，<b>標了什麼結果</b>？寫出<b>哪一家</b>、<b>標什麼</b>、<b>一句重點</b>。', 'res',
    how('回到<b>查核文章分頁</b>，看標題前面的<b>標籤</b>（錯誤、誤導…）。',
        '讀文章最上面的「<b>你可以先知道</b>」，找出一句最重要的重點。',
        '在下面選<b>哪一家</b>機構、選<b>標籤</b>（照文章寫，不要自己換字）。',
        '用一句話寫<b>重點</b>。想挑戰：再找另一家機構的文章比對，多寫一句。') +
        clips('看操作影片：看標籤', ('步_結果_看標籤', '看標題前的標籤，和「你可以先知道」')),
    example_box('MyGoPen 查核後標為「誤導」，重點是這個說法在技術和金融上都不合理。',
                '<b>＿＿</b>（機構）查核後標為「<b>＿＿</b>」，重點是……') +
        good_bad('機構名稱、標籤、一句重點，三樣都有。', '只寫「是假的」；標籤自己亂換；沒說是哪一家查的。'),
    '<p class="lb">① 哪一家機構查的？</p>' + chips('resOrg', ['台灣事實查核中心', 'MyGoPen 麥擱騙', '其他查核機構']) +
    '<p class="lb">② 標的結果（照文章寫）</p>' + chips('resLabel', ['錯誤', '誤導', '易誤解', '事實釐清', '詐騙', '部分錯誤', '正確', '其他']) +
    '<label class="lb" for="f_resNote">③ 一句重點 <small>句型：＿＿（機構）查核後標為「＿＿」，重點是……</small></label>'
    '<textarea id="f_resNote" class="fld mt-1" rows="3" data-k="resNote" placeholder="例：MyGoPen 查核後標為「誤導」，重點是……"></textarea>')

N_FACT = node(10, 6, 'emerald', '正確資訊',
    '查核文章告訴我們<b>真正的事實</b>是什麼？用<b>自己的話</b>整理 1～3 點，每點說是<b>誰說的</b>。', 'fact',
    '<div class="grid sm:grid-cols-2 gap-3 mt-3 text-lg"><div class="bg-slate-50 border-2 border-slate-300 rounded-2xl p-3"><p class="font-extrabold text-slate-600 m-0">整段複製（不要這樣）</p><p class="mt-1 mb-0">經查，查核中心洽詢刑事警察局後，警方表示目前國內並無查獲與網傳手法相同之案件，且 165 反詐騙專線亦表示，台灣無此類案例。</p></div><div class="bg-emerald-50 border-2 border-emerald-300 rounded-2xl p-3"><p class="font-extrabold text-emerald-700 m-0">整理成自己的話（要這樣）</p><p class="mt-1 mb-0">警方和 165 反詐騙專線說，台灣目前查不到這種手法的案件。</p></div></div>'
    + how('回到<b>查核文章分頁</b>，讀「你可以先知道」和後面的說明。',
          '找出<b>最重要的 1～3 個事實</b>：是誰（警方、專家、機構）說了什麼。',
          '每一點寫<b>一句</b>，用句型：「根據○○，……」「○○說，……」「不過，……」。',
          '不要整段貼上。整理＝只留重點、用自己的話、標出是誰說的。'),
    example_box('1. 根據 MyGoPen，只有指紋或臉，不能直接拿去貸款，銀行還要看很多檢查。<br>2. 警方和 165 說，台灣查不到這種案件。<br>3. 不過，陌生人要你做驗證時，還是要小心。',
                '根據<b>＿＿</b>，……／<b>＿＿</b>說，……／不過，……') +
        good_bad('每點一句、標出是誰說的、先講最重要的結論。', '整段複製貼上；沒有說是誰說的；只寫「這是假的」。'),
    '<label class="lb" for="f_fact">正確資訊（1～3 點，每點一句） <small>每點標出是誰說的</small></label>'
    '<div class="mt-1"><button type="button" data-insert="fact" data-text="1. 根據　　，" class="bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-3 py-1">插入：根據……</button> '
    '<button type="button" data-insert="fact" data-text="2.　　說，" class="bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-3 py-1">插入：○○說……</button> '
    '<button type="button" data-insert="fact" data-text="3. 不過，" class="bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-3 py-1">插入：不過……</button></div>'
    '<textarea id="f_fact" class="fld mt-2" rows="6" data-k="fact" placeholder="1. 根據＿＿，……&#10;2. ＿＿說，……&#10;3. 不過，……"></textarea>')

N_WHY = node(11, 7, 'violet', '為什麼會流傳',
    '這則訊息有什麼地方，讓大家<b>想轉傳</b>？先選原因的<b>類型</b>，再用一兩句<b>說出理由</b>。', 'why',
    '<p class="text-lg text-slate-700 mt-2 mb-0">常見的 5 類原因：</p><ul class="mt-2 space-y-1 text-lg text-slate-700"><li><b>怕</b>：講得很可怕</li><li><b>好奇／驚奇</b>：聽起來很厲害</li><li><b>關心家人</b>：「轉傳等於救人」</li><li><b>好康</b>：免費、搶先</li><li><b>親友傳來的</b>：因為信任</li></ul>'
    + how('再看一次你的訊息，找出<b>哪一句話</b>讓你覺得「想轉傳」或「好可怕」。',
          '在下面選一類（或兩類）原因。',
          '用一兩句寫理由，最好<b>引用訊息裡的那句話</b>。'),
    example_box('訊息說「30 分鐘傾家蕩產」，讓人<b>怕</b>；又寫「轉傳給家人朋友」，大家覺得轉傳是<b>關心家人</b>；還提到 AI 和手機，聽起來很厲害，帶點<b>好奇</b>。',
                '這則訊息讓人<b>＿＿</b>（怕／好奇…），因為它說「<b>＿＿</b>」。') +
        good_bad('選了類型，還說出訊息裡<b>哪一句</b>造成的。', '「因為很多人相信」（沒說為什麼相信）；只勾類型沒寫理由。'),
    '<p class="lb">① 原因類型（可複選）</p>' + chips('whyKinds', ['怕', '好奇／驚奇', '關心家人', '好康', '親友傳來的'], True) +
    '<label class="lb" for="f_whyText">② 說出理由 <small>句型：這則訊息讓人＿＿，因為它說「＿＿」</small></label>'
    '<textarea id="f_whyText" class="fld mt-1" rows="4" data-k="whyText" placeholder="例：這則訊息讓人怕，因為它說「……」"></textarea>')

N_RISK = node(12, 8, 'rose', '相信的後果',
    '如果有人<b>相信並照做、轉傳</b>，會發生什麼事？要寫出<b>誰</b>會<b>怎樣</b>。', 'risk',
    '<p class="text-lg text-slate-700 mt-2 mb-0">常見的 4 類後果：</p><ul class="mt-2 space-y-1 text-lg text-slate-700"><li><b>身體</b>：吃錯、做錯</li><li><b>錢</b>：被騙</li><li><b>人際</b>：誤會、吵架</li><li><b>恐慌</b>：嚇到更多人、再轉傳</li></ul>'
    + how('想一想：誰會相信這則訊息？（家人、同學、陌生人…）',
          '他相信以後，會<b>做什麼</b>？會<b>發生什麼事</b>？',
          '在下面選類型，再寫成「<b>誰</b>會<b>怎樣</b>」。'),
    example_box('有人怕到不敢幫真的需要幫忙的人；也有人把嚇人的訊息再轉給更多人，讓大家一起害怕。',
                '<b>＿＿</b>（誰）相信以後，會<b>＿＿</b>（怎樣）。') +
        good_bad('寫出<b>誰</b>會<b>怎樣</b>。', '「會被騙」（沒說誰、怎麼被騙）；「這則訊息是假的」（那是查核結果，不是後果）。'),
    '<p class="lb">① 後果類型（可複選）</p>' + chips('riskKinds', ['身體', '錢', '人際', '恐慌'], True) +
    '<label class="lb" for="f_riskText">② 誰會怎樣？ <small>句型：＿＿（誰）相信以後，會＿＿</small></label>'
    '<textarea id="f_riskText" class="fld mt-1" rows="4" data-k="riskText" placeholder="例：有人相信以後，會……"></textarea>')

# ---------- 步驟 13：檢查繳交 ----------
STEP13 = '''
  <!-- ===== 步驟 13：檢查繳交 ===== -->
  <section class="step hidden" data-step="13">
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-indigo-700">繳交前自己檢查</h2>
      <p class="text-lg text-slate-600 mt-1">下面是 8 欄的狀態。還沒寫完的，按「去寫」跳過去。</p>
      <div id="sumList" class="mt-3 space-y-2"></div>
      <h3 class="cute text-xl font-extrabold text-indigo-700 mt-5 mb-1">最後再看一次（打勾，只是提醒自己）</h3>
      <div data-chips="chk" data-multi="1" class="space-y-2 mt-2">
        <button type="button" class="chip block w-full" data-v="標題是查核報告的標題，不是網傳訊息的標題"><span class="mk">☐</span>標題是查核報告的標題，不是網傳訊息的標題</button>
        <button type="button" class="chip block w-full" data-v="網址是查核機構自己的網站，點得開"><span class="mk">☐</span>網址是查核機構自己的網站，點得開</button>
        <button type="button" class="chip block w-full" data-v="原始內容描述只講訊息說什麼，沒有判斷真假"><span class="mk">☐</span>原始內容描述只講訊息說什麼，沒有判斷真假</button>
        <button type="button" class="chip block w-full" data-v="正確資訊用自己的話，有標出是誰說的"><span class="mk">☐</span>正確資訊用自己的話，有標出是誰說的</button>
        <button type="button" class="chip block w-full" data-v="為什麼流傳、相信的後果都有寫理由"><span class="mk">☐</span>為什麼流傳、相信的後果都有寫理由</button>
      </div>
    </div>
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-5 shadow-sm text-center mt-6">
      <h2 class="cute text-xl font-extrabold text-indigo-700 mb-1">繳交學習單</h2>
      <p class="text-sm text-slate-500 mb-3">確定都填好了嗎？按下面按鈕交給老師（可以重交，會覆蓋前一次，也會蓋掉之前「先存檔交一次」的那份）。</p>
      <button id="submitBtn" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white cute text-xl font-extrabold rounded-2xl py-3">繳交學習單</button>
      <p id="submitStat" class="text-sm font-bold mt-3 min-h-[20px]"></p>
    </div>
    <div id="rewardBox" class="hidden text-center bg-gradient-to-b from-indigo-100 to-sky-100 border-4 border-indigo-300 rounded-3xl p-7 mt-6">
      <div class="text-6xl mb-2 pop">🎉</div>
      <h2 class="cute text-3xl font-extrabold text-indigo-700">恭喜你已經做完今日的作業，可以遊玩！</h2>
      <div class="flex flex-wrap gap-3 justify-center mt-4">
        <a href="https://boyinslps.github.io/typehero/index.html" target="_blank" rel="noopener" class="cute inline-block bg-indigo-600 hover:bg-indigo-700 text-white text-xl font-extrabold rounded-2xl px-8 py-3">打字英雄</a>
        <a href="https://gemini.google.com/share/0adbaeae6c16?skid=751ce4ac-860d-4160-8a1a-12a1ebcf6f1d" target="_blank" rel="noopener" class="cute inline-block bg-white border-4 border-indigo-300 hover:bg-indigo-50 text-indigo-700 text-xl font-extrabold rounded-2xl px-8 py-3">更多遊戲</a>
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
    <span class="ml-auto flex items-center gap-2 text-xs font-bold text-slate-500"><span id="progTxt">報告 0／8 欄</span><span class="inline-block w-24 h-2 bg-slate-200 rounded-full overflow-hidden align-middle"><span id="progBar" class="block h-full bg-emerald-500" style="width:0%"></span></span></span>
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
  "summary": "從 6 則真實網傳訊息中選一則，用關鍵字搜尋、以圖搜圖或智慧鏡頭找到查核機構（台灣事實查核中心或 MyGoPen）已發布的查核文章，把它整理成 8 欄查證報告：查核報告標題、查核網址、使用的搜索工具、原始內容描述、查核結果、正確資訊、為什麼會流傳、相信的後果。全部寫在學習單裡，可用「斷點繳交」分節完成。",
  "questions": [
    { "qid": "tool", "prompt": "你使用的搜索工具（關鍵字、以圖搜圖、智慧鏡頭）：用了什麼工具、搜了什麼、點進哪個網站、為什麼認定它是查核機構", "mode": "checklist",
      "checks": [
        { "desc": "說出使用的工具，並寫出搜尋用的關鍵詞或圖片（關鍵字搜尋要加「查核」）", "pts": 1 },
        { "desc": "說明點進哪個網站，並說明為什麼認定它是查核機構（不是轉載）", "pts": 1 } ] },
    { "qid": "desc", "prompt": "原始內容描述：只描述網傳訊息或影片說了什麼，不做查證判斷", "mode": "checklist",
      "checks": [
        { "desc": "用自己的話概述訊息或影片的內容（人事時地物，沒說的標「沒說」），並說明在哪裡流傳", "pts": 2 },
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
        { "desc": "說出至少一個原因類型（怕、好奇、關心家人、好康、親友傳來）", "pts": 1 },
        { "desc": "說明理由，最好指出訊息裡的哪句話造成的", "pts": 1 } ] },
    { "qid": "risk", "prompt": "如果相信這則訊息，會有什麼後果？（誰會怎樣）", "mode": "levels", "points": 2,
      "standard": "說出誰會怎樣；只寫「是假的」或「會被騙」不給分" }
  ],
  "scoring": { "base": 100, "floor": 80, "deduction": 1,
    "itemPoints": { "sel": 1, "title": 2, "url": 2 } }
}
</script>'''


def build(assets):
    body = (TOP + STEP1 + STEP2 + STEP3 + STEP4 + N_TITLE + N_URL + N_TOOL + N_DESC + N_RES + N_FACT + N_WHY + N_RISK + STEP13 + BOTTOM)
    engine = io.open(os.path.join(HERE, 'engine_L05_fri.js'), encoding='utf8').read().replace('/*FIREBASE_CONFIG*/', FIREBASE_CFG)
    html = (HEAD_CSS + EXTRA_CSS + '</head>\n' + body + '\n<script>\n' + engine + '\n</script>\n\n' + GRADING + '\n' + CHAIR + '\n' + STEPCARDS + '\n</body>\n</html>\n')
    return html.replace('@@A@@', assets)


def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, 'w', encoding='utf8', newline='\n').write(html)
    print('寫出', path, len(html))


if __name__ == '__main__':
    # lesson-prep 教材資料夾：素材沿用 L05 的 assets；pcclass 發布資料夾：g5/L05-fri 與 g5/L05 同層
    write(os.path.join(ROOT, 'L05_週五版', '五上_L05_週五版.html'), build('../L05_Docs查證文件一/assets/'))
    write(os.path.join(PCCLASS, 'g5', 'L05-fri', 'index.html'), build('../L05/assets/'))
