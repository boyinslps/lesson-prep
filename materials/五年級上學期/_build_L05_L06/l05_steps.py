# -*- coding: utf-8 -*-
# 五上 L05 的步驟卡頁面（2026-10-16 起；2026-10-19 依老師要求重排）。
# 頁面順序：1 看成品（含四欄示範）→ 2 選訊息 → 3 我來查 → 4 準備文件 → 5 回想 → 6 寫文件（一個欄位一個環節）→ 7 繳交
# 文件欄位順序：標題、年班座號＋名字、查核網址、我選的訊息、我怎麼找到查核文章的、查核結果、（L06）為什麼廣傳、正確資訊、後果
# 原則：一個畫面一小步、字少、動圖放在操作旁邊；句型、範例預設收起來；網址要先貼（在標題下面）。
DOC_URL = 'https://docs.google.com/document/d/1e4-lD9lyZJgRPma8_7A3e3fn0y1M8M9Z1oqZF1gI0n4/edit'

# 頁面步驟編號（改順序只改這裡和 build.py 的 steps 清單）
S_PREP, S_RECALL, S_WRITE, S_SUBMIT = 4, 5, 6, 7


def kbd(*ks):
    return '＋'.join('<kbd>%s</kbd>' % k for k in ks)


def slide(title, clip=None, extra=''):
    media = ''
    if clip:
        media = ('<div class="sc-media" data-src="assets/%s.mp4" data-poster="assets/%s_封面.jpg"></div>' % (clip, clip))
    return '<div class="sc-slide"><p class="sc-t">%s</p>%s%s</div>' % (title, media, extra)


def sc(slides, tone='amber'):
    return '<div class="sc" data-sc>%s</div>' % ''.join(slides)


def help_box(summary, body, tone='sky'):
    return ('<details class="mt-3 bg-%s-50 border-2 border-%s-200 rounded-2xl p-3"><summary class="cursor-pointer font-extrabold text-%s-800 text-lg">%s</summary>'
            '<div class="mt-2 text-lg text-slate-700">%s</div></details>') % (tone, tone, tone, summary, body)


def ex(text):
    return '<p class="bg-white border-2 border-amber-200 rounded-xl px-3 py-2">%s</p>' % text


def nextcol(label='✔ 這欄寫好了，下一欄 →', to=None):
    return ('<div class="mt-4 text-right"><button type="button" data-coldone="%s" class="cute bg-emerald-600 hover:bg-emerald-700 text-white text-xl font-extrabold rounded-2xl px-6 py-2">%s</button></div>'
            % (to or '', label))


# ---------- 第 1 步下半：四欄示範（原本第 2 步的示範合併進來）----------
DEMO_LINK = '<span class="text-indigo-700 underline">MyGoPen：幫陌生人操作手機會被盜取生物特徵去貸款？誇大AI技術！不符金融審核機制</span>'
DEMO_SC = sc([
    slide('示範　<b>① 查核網址</b>', None,
          '<p class="text-lg text-slate-500">查核文章的標題，做成<b>點得開</b>的連結：</p><p class="text-xl bg-amber-50 border-2 border-amber-200 rounded-2xl p-3 mt-1">' + DEMO_LINK + '</p>'
          '<p class="text-lg mt-2">要是<b>查核機構自己</b>的網站（tfc-taiwan、mygopen），不是轉載。</p>'),
    slide('示範　<b>② 我選的訊息</b>', None,
          '<div class="grid md:grid-cols-2 gap-4 items-start"><div><img class="shotimg" src="assets/M2_B示範_陌生人手機_網傳訊息.png" alt="示範訊息：兩則臉書貼文，標題寫「人工智能生物信息詐騙，要的不是你的錢而是你這個人」，帳號已遮蔽" loading="lazy"><p class="text-[11px] text-slate-400 mt-1">原始訊息的圖・點圖可放大</p></div>'
          '<p class="text-xl bg-amber-50 border-2 border-amber-200 rounded-2xl p-3">路上（地）有陌生人（人）請你幫忙操作手機（事、物），30 分鐘（時）就傾家蕩產。</p></div>'),
    slide('示範　<b>③ 我怎麼找到查核文章的</b>', None,
          '<p class="text-xl bg-amber-50 border-2 border-amber-200 rounded-2xl p-3">我圈出「陌生人」「操作手機」，搜「幫陌生人操作手機 查核」，點進 mygopen.com 的文章，它是專門查謠言的機構，不是轉載。</p>'),
    slide('示範　<b>④ 查核結果</b>', None,
          '<p class="text-xl bg-amber-50 border-2 border-amber-200 rounded-2xl p-3">MyGoPen 標為「誤導」；台灣事實查核中心標為「錯誤」。</p>'
          '<p class="text-lg text-slate-700 mt-2">💡 兩家查核機構<b>結論一致</b>，這樣更可信。</p>'),
])

# ---------- 找回上次的網址（第 5、6 步各放一份；沒有網址的人先到這裡拿）----------
def rescue():
    opts = ''.join('<option value="%s">%s</option>' % (k, v) for k, v in [
        ('C', 'C ‧ 繪畫比賽投票'), ('D', 'D ‧ 微波爐有輻射'), ('E', 'E ‧ 打雷戴藍芽耳機'),
        ('G', 'G ‧ 印度街頭小吃'), ('H', 'H ‧ 充電時講電話喝水'), ('K', 'K ‧ 地震躲生命三角')])
    return (
        '<details class="urlfix mt-4 bg-violet-50 border-2 border-violet-300 rounded-2xl p-3">'
        '<summary class="cursor-pointer font-extrabold text-violet-800 text-xl">🔍 沒有網址？找回上次的網址</summary>'
        '<div class="mt-3 text-lg text-slate-700 space-y-3">'
        '<div data-ufpick class="hidden"><label class="block font-bold">上次你選的是哪一則？'
        '<select class="urlfixSel mt-1 w-full border-2 border-slate-300 rounded-xl px-3 py-2 text-lg"><option value="">請選</option>' + opts + '</select></label></div>'
        '<div data-ufbox class="hidden bg-white border-2 border-violet-200 rounded-xl p-3">'
        '<p class="font-bold" data-ufname></p>'
        '<p class="break-all font-mono text-base mt-1" data-ufurl></p>'
        '<div class="flex gap-2 flex-wrap mt-2">'
        '<a data-ufopen href="#" target="_blank" rel="noopener" class="bg-violet-600 hover:bg-violet-700 text-white font-bold rounded-xl px-4 py-2">開啟查核文章 ↗</a>'
        '<button type="button" data-copyurl class="bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-4 py-2">📋 複製網址</button></div></div>'
        '<p class="text-base text-slate-500">這是老師準備的那一篇，你上次找到別篇也可以。想自己找：瀏覽器按 <kbd>Ctrl</kbd>＋<kbd>H</kbd> 看「歷史記錄」，找 tfc-taiwan 或 mygopen 開頭的。</p>'
        '<label class="block font-bold">找到你的網址了？貼在這裡，下次就找得回來'
        '<input class="urlKeep mt-1 w-full border-2 border-slate-300 rounded-xl px-3 py-2 text-base" autocomplete="off"></label>'
        '</div></details>')


RESCUE = rescue()

# ---------- 第 4 步：準備文件（開文件、複製貼上欄位、設標題）----------
STEP_PREP = """
  <!-- ===== 步驟 4：準備文件（步驟卡）===== -->
  <section class="step hidden" data-step="%(N)d">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700 m-0">📄 準備好你的 Google 文件</h2>
      <p class="text-lg text-slate-600 mt-1">一小步一小步來。上週<b>已經做完</b>的，直接按「下一步」跳過。</p>
    </div>
    %(SC)s
    <div class="stepnav"></div>
  </section>
"""
SC_PREP = sc([
    slide('從 Classroom 打開<b>老師給的文件</b>，改檔名', '步_文件1_打開文件',
          '<p class="text-xl font-bold mt-2">檔名：<b class="text-blue-700">年班座號＋名字</b>　<span class="text-base text-slate-500">例：51230 王小明</span></p>'
          '<p class="text-lg text-rose-700 font-bold mt-1">⚠️ 一定要從 Classroom 作業裡開，老師才讀得到。</p>'),
    slide('按 <b>📋 複製欄位</b>', None,
          '<button id="tplCopy" type="button" class="w-full bg-blue-600 hover:bg-blue-700 text-white text-2xl font-extrabold rounded-2xl px-4 py-4">📋 複製欄位</button>'
          '<details class="mt-3 bg-white border-2 border-blue-100 rounded-2xl p-3"><summary class="cursor-pointer font-bold text-blue-800 text-lg">看會貼上什麼</summary>'
          '<pre id="tplText" class="text-lg leading-relaxed whitespace-pre-wrap font-[inherit] mt-2"></pre></details>'),
    slide('文件第一行，按 <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd> 貼上', '步_文件2_貼上七欄位',
          '<ol class="text-xl font-bold mt-3 space-y-1"><li>第 1 行「（文件標題）」→ 改成<b class="text-indigo-700">你的標題</b></li>'
          '<li>第 2 行「（年班座號＋名字）」→ 改成<b class="text-indigo-700">你的</b></li></ol>'
          '<p class="text-base text-slate-500 mt-2">貼錯了？<kbd>Ctrl</kbd> + <kbd>Z</kbd>。多了空白？<kbd>Backspace</kbd> 刪前面、<kbd>Delete</kbd> 刪後面。不用按儲存。</p>'),
    slide('題目選起來，設成<b>標題 1</b>', '步_文件3_設標題1',
          '<p class="text-lg text-slate-500 mt-2">左上角「內文」按鈕 → 標題 1。快速鍵 <kbd>Ctrl</kbd>＋<kbd>Alt</kbd>＋<kbd>1</kbd>。</p>'),
    slide('✋ 先猜猜看', None,
          '<div class="bg-white border-2 border-violet-200 rounded-2xl p-4"><div class="flex items-center gap-2 flex-wrap"><p class="font-bold text-violet-800 text-xl">只把「我選的訊息」改成 16 號大字，它會變成「標題 2」嗎？</p><span class="qtypeSlot" data-qid="c1"></span><span id="c1Fb" class="text-sm font-bold"></span></div>'
          '<div id="c1Opts" class="flex flex-wrap gap-2 mt-3"></div>'
          '<div id="c1Expl" class="hidden mt-3 flip bg-rose-50 border-2 border-rose-200 rounded-2xl p-3 text-lg text-slate-700"><p>🎉 答案是<b>不會</b>。只是字變大，「大綱」裡找不到它。<b>用「樣式」選了標題 2，才算標題 2</b>。</p></div></div>'),
    slide('<b>欄位名稱</b>，都設成<b>標題 2</b>', '步_文件4_設標題2',
          '<p class="text-lg text-slate-500 mt-2">選取一行 → 「內文」→ 標題 2。快速鍵 <kbd>Ctrl</kbd>＋<kbd>Alt</kbd>＋<kbd>2</kbd>。</p>'),
])
STEP_PREP = STEP_PREP % {'N': S_PREP, 'SC': SC_PREP}

# ---------- 第 5 步：回想＋我的文件做到哪 ----------
RV = [
    ('我們要找的，是<b>誰寫的</b>文章？', '<b>查核機構</b>寫好的原始文章。<br><span class="text-base text-slate-500">不是轉載、不是 AI 摘要。</span>'),
    ('搜尋要怎麼打？搜不到怎麼辦？', '<b>2～3 個關鍵詞＋查核</b>。<br><span class="text-base text-slate-500">搜不到：換詞，或用以圖搜圖。</span>'),
    ('怎麼認出是查核機構？', '網址是 <b>tfc-taiwan.org.tw</b> 或 <b>mygopen.com</b>。<br><span class="text-base text-slate-500">看標題前的標籤（錯誤、誤導…）。</span>'),
    ('標題 1、標題 2 要怎麼設？', '用<b>「樣式」</b>（左上角「內文」按鈕）。<br><span class="text-base text-slate-500">只把字放大，大綱不會出現。</span>'),
]


def rv_cards():
    out = []
    for i, (q, a) in enumerate(RV, 1):
        out.append('<button type="button" data-rv class="rv text-left bg-sky-50 border-4 border-sky-200 hover:border-sky-400 rounded-3xl p-4 min-h-[120px]">'
                   '<span class="q block text-xl font-extrabold text-sky-800">%d　%s<br><span class="text-base font-bold text-sky-500">點一下，看答案</span></span>'
                   '<span class="a hidden text-xl text-slate-800">%s</span></button>' % (i, q, a))
    return '\n      '.join(out)


STEP_RECALL = '''
  <!-- ===== 步驟 5：回想＋我的文件做到哪（接續上課用）===== -->
  <section class="step hidden" data-step="%(N)d">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">🧠 先回想：上週學了什麼？</h2>
      <p class="text-lg text-slate-600 mt-1">先自己想一想，再點開看答案。</p>
      <div class="grid sm:grid-cols-2 gap-3 mt-4">
      %(RV)s
      </div>
    </div>

    <div class="bg-white border-4 border-teal-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-teal-700 m-0">📍 你的文件現在做到哪？</h2>
      <p class="text-lg text-slate-600 mt-1">打開 Classroom 的文件，看一看，選一個。</p>
      <div class="grid sm:grid-cols-3 gap-3 mt-4">
        <button type="button" data-prog="A" class="prog text-left bg-white border-4 border-slate-200 hover:border-teal-400 rounded-3xl p-4"><span class="cute block text-2xl font-extrabold text-rose-600">A</span><span class="text-xl font-bold">文件的格式還沒弄好<br><span class="text-base text-slate-500">欄位、標題</span></span></button>
        <button type="button" data-prog="B" class="prog text-left bg-white border-4 border-slate-200 hover:border-teal-400 rounded-3xl p-4"><span class="cute block text-2xl font-extrabold text-amber-600">B</span><span class="text-xl font-bold">格式好了，欄位還沒寫完</span></button>
        <button type="button" data-prog="C" class="prog text-left bg-white border-4 border-slate-200 hover:border-teal-400 rounded-3xl p-4"><span class="cute block text-2xl font-extrabold text-emerald-600">C</span><span class="text-xl font-bold">前面的欄位都寫好了</span></button>
      </div>
      <div id="progBox" class="hidden mt-4 bg-teal-50 border-2 border-teal-200 rounded-2xl p-4 text-xl"></div>
      %(RESCUE)s
    </div>
    <div class="stepnav"></div>
  </section>
'''

# ---------- 第 6 步：寫文件，一個欄位一個環節（順序＝文件裡由上往下）----------
# ① 查核網址（標題下面，要先貼）
COL1 = sc([
    slide('複製查核文章的<b>標題</b>，貼在「查核網址」下面', None,
          '<p class="text-2xl font-bold mt-1">' + kbd('Ctrl', 'C') + ' → 回文件 → ' + kbd('Ctrl', 'V') + '</p>'
          '<p class="text-xl mt-3 bg-rose-50 border-2 border-rose-200 rounded-2xl p-3">✏️ 要是<b>查核機構自己</b>的網站（tfc-taiwan、mygopen…），不是轉載。</p>'),
    slide('點一下<b>網址列</b>，複製網址', '步_網址1_複製網址列'),
    slide('回文件，<b>選取標題</b>', '步_網址2_選取標題'),
    slide('<b>Ctrl＋K</b>，貼上網址，按「套用」', '步_網址3_插入連結'),
])
COL1_HELP = (help_box('⭐ 看範例', '<p class="bg-white border-2 border-amber-200 rounded-xl px-3 py-2 text-indigo-700 underline">MyGoPen：幫陌生人操作手機會被盜取生物特徵去貸款？誇大AI技術！不符金融審核機制</p>'
                      '<p class="text-base text-slate-500 mt-2">藍色有底線，點一下能開啟＝成功了。</p>', 'amber')
             + RESCUE)

# ② 我選的訊息
CHIPS5 = ('<div class="grid grid-cols-5 gap-2 mt-3 text-center text-base">'
          '<div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>👤 人</b></div>'
          '<div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>📌 事</b></div>'
          '<div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>🕒 時</b></div>'
          '<div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>📍 地</b></div>'
          '<div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>🎒 物</b></div></div>'
          '<p class="text-base text-slate-500 mt-2">沒寫的，就寫「沒說」。</p>')
COL2 = sc([
    slide('先寫一兩句：這則訊息<b>在講什麼</b>', None, CHIPS5),
    slide('找到<b>原始訊息的圖</b>', '步_圖1_找圖', '<p class="text-base text-slate-500 mt-2">選的是影片？按 <kbd>Win</kbd>＋<kbd>Shift</kbd>＋<kbd>S</kbd> 截一張畫面。</p>'),
    slide('在圖上按右鍵，<b>複製圖片</b>', '步_圖2_複製圖片'),
    slide('回文件，<b>貼在句子下面</b>', '步_圖3_貼上'),
])
COL2_HELP = (help_box('🧩 給我句型', '<p>網傳訊息說：<b>＿＿</b>（人）在<b>＿＿</b>（地），<b>＿＿</b>（事）……</p>')
             + help_box('⭐ 看範例', ex('路上（地）有陌生人（人）請你幫忙操作手機（事、物），30 分鐘（時）就傾家蕩產。'), 'amber'))

# ③ 我怎麼找到查核文章的
COL3_STRIP = ('<div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">'
              '<div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-3"><div class="text-3xl">🔤</div><b>圈了哪些<br>關鍵詞？</b></div>'
              '<div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-3"><div class="text-3xl">🔎</div><b>Google<br>搜了什麼？</b></div>'
              '<div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-3"><div class="text-3xl">🌐</div><b>點進<br>哪個網站？</b></div>'
              '<div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-3"><div class="text-3xl">✅</div><b>為什麼是<br>查核機構？</b></div></div>')
BUILD3 = '''
<div class="grid sm:grid-cols-3 gap-3">
  <label class="block font-bold">我怎麼找的？
    <select id="b2how" class="mt-1 w-full border-2 border-slate-300 rounded-xl px-3 py-2 text-lg"><option value="字">用文字搜尋</option><option value="圖">用圖片搜尋</option></select></label>
  <label class="block font-bold" id="b2kwWrap">關鍵詞（用空白隔開）
    <input id="b2kw" class="mt-1 w-full border-2 border-slate-300 rounded-xl px-3 py-2 text-lg" autocomplete="off"></label>
  <label class="block font-bold">我點進的網站
    <select id="b2site" class="mt-1 w-full border-2 border-slate-300 rounded-xl px-3 py-2 text-lg"><option value="">請選</option><option>MyGoPen</option><option>台灣事實查核中心</option><option>其他查核機構</option></select></label>
</div>
<p id="sent2" class="mt-3 bg-white border-2 border-sky-300 rounded-xl px-3 py-2"></p>
<button type="button" data-copy="sent2" class="mt-2 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-4 py-2">📋 複製這句，貼到文件</button>
<p class="text-base text-slate-500 mt-2">貼上後，改成你自己的說法更好。</p>
'''
COL3_HELP = (help_box('🧩 給我句型', BUILD3)
             + help_box('⭐ 看範例', ex('我圈出「陌生人」「操作手機」，搜「幫陌生人操作手機 查核」，點進 mygopen.com 的文章，它是專門查謠言的機構，不是轉載。'), 'amber'))

# ④ 查核結果（標籤清單從舊的「我來查」搬來）
LABELS = ['錯誤', '誤導', '易誤解', '事實釐清', '詐騙', '部分錯誤', '正確']
LABEL_CHIPS = ('<div class="flex flex-wrap gap-2 mt-2">' + ''.join(
    '<span class="bg-amber-100 border-2 border-amber-300 text-amber-900 font-extrabold rounded-full px-4 py-1 text-xl">%s</span>' % t for t in LABELS) + '</div>')
COL4 = sc([
    slide('看<b>標題前的標籤</b>，和「你可以先知道」', '步_結果_看標籤'),
    slide('✏️ 查核機構標的結果是？', None,
          LABEL_CHIPS +
          '<p class="text-2xl font-extrabold bg-amber-50 border-2 border-amber-200 rounded-2xl p-4 mt-4">（機構名）查核後，標為「（標籤）」。</p>'
          '<p class="text-base text-slate-500 mt-2">看你找到的那一篇，標籤不一定在上面這幾個裡面時，照它寫的抄。</p>'),
])
BUILD4 = '''
<div class="grid sm:grid-cols-2 gap-3">
  <label class="block font-bold">哪一家？
    <select id="b3org" class="mt-1 w-full border-2 border-slate-300 rounded-xl px-3 py-2 text-lg"><option value="">請選</option><option>MyGoPen</option><option>台灣事實查核中心</option><option>其他查核機構</option></select></label>
  <label class="block font-bold">標了什麼？
    <select id="b3label" class="mt-1 w-full border-2 border-slate-300 rounded-xl px-3 py-2 text-lg"><option value="">請選</option>''' + ''.join('<option>%s</option>' % t for t in LABELS) + '''<option>其他</option></select></label>
</div>
<p id="sent3" class="mt-3 bg-white border-2 border-sky-300 rounded-xl px-3 py-2"></p>
<button type="button" data-copy="sent3" class="mt-2 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-4 py-2">📋 複製這句，貼到文件</button>
'''
COL4_HELP = (help_box('🧩 給我句型', BUILD4)
             + help_box('⭐ 看範例', ex('MyGoPen 查核後，標為「誤導」。台灣事實查核中心標為「錯誤」。'), 'amber')
             + help_box('⭐ 加分：再找另一個機構的文章來比對', '<p>在「查核結果」多寫一句：另一家機構也說……，兩家<b>一樣</b>還是<b>不一樣</b>？</p>', 'amber'))


def col_panel(n, title, hint, body, helps, tone):
    return ('<div class="colp hidden bg-white border-4 border-%s-300 rounded-3xl p-5 mb-5 shadow-sm" data-col="%d">'
            '<h2 class="cute text-3xl font-extrabold text-%s-700 m-0">%s<span class="text-lg font-bold text-slate-500 ml-2">%s</span></h2>'
            '<div class="mt-3">%s</div>%s%s</div>') % (tone, n, tone, title, hint, body, helps, nextcol('✔ 這欄寫好了，下一欄 →' if n < 4 else '✔ 這欄寫好了，完成 →'))


STEP_WRITE = '''
  <!-- ===== 步驟 6：寫文件（一個欄位一個環節，順序＝文件由上往下）===== -->
  <section class="step hidden" data-step="%(N)d">
    <div id="colPills" class="grid grid-cols-2 sm:grid-cols-4 gap-2 mb-4">
      <button type="button" data-colbtn="1" class="colbtn cute text-lg font-extrabold rounded-2xl border-4 px-2 py-2">① 查核網址</button>
      <button type="button" data-colbtn="2" class="colbtn cute text-lg font-extrabold rounded-2xl border-4 px-2 py-2">② 我選的訊息</button>
      <button type="button" data-colbtn="3" class="colbtn cute text-lg font-extrabold rounded-2xl border-4 px-2 py-2">③ 怎麼找到的</button>
      <button type="button" data-colbtn="4" class="colbtn cute text-lg font-extrabold rounded-2xl border-4 px-2 py-2">④ 查核結果</button>
    </div>
    <p class="text-slate-600 text-lg mb-3">在 Google 文件裡，<b>由上往下</b>一欄一欄寫。需要句型的，打開「🧩 給我句型」。<button type="button" data-goto="%(PREP)d" class="ml-2 text-base font-bold text-sky-700 underline">格式還沒貼好？回第 %(PREP)d 步</button></p>

    %(P1)s
    %(P2)s
    %(P3)s
    %(P4)s

    <div class="colp hidden bg-white border-4 border-emerald-300 rounded-3xl p-5 mb-5 shadow-sm" data-col="5">
      <h2 class="cute text-3xl font-extrabold text-emerald-700 m-0">🎉 前面的欄位寫好了！</h2>
      <p class="text-xl text-slate-700 mt-2">接著到下一步，<b>檢查</b>文件，再交出去。</p>
      <div class="mt-4 text-right"><button type="button" data-goto="%(SUBMIT)d" class="cute bg-indigo-600 hover:bg-indigo-700 text-white text-xl font-extrabold rounded-2xl px-6 py-2">去檢查、繳交 →</button></div>
      <div class="mt-5 bg-amber-50 border-2 border-amber-300 rounded-2xl p-4">
        <p class="cute text-2xl font-extrabold text-amber-700">⭐ 還有時間？挑戰一下</p>
        <ul class="list-disc pl-6 mt-2 text-xl space-y-1">
          <li>再找<b>另一個機構</b>的文章來比對，在「查核結果」加一句：「另一家也說……」</li>
          <li>幫旁邊的同學，用<b>檢查表</b>看他的文件</li>
        </ul>
      </div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

P1 = col_panel(1, '① 查核網址', '標題下面，先貼', COL1, COL1_HELP, 'indigo')
P2 = col_panel(2, '② 我選的訊息', '一兩句＋原始訊息的圖', COL2, COL2_HELP, 'amber')
P3 = col_panel(3, '③ 我怎麼找到查核文章的', '照順序寫 4 件事', COL3_STRIP, COL3_HELP, 'teal')
P4 = col_panel(4, '④ 查核結果', '哪一家、標了什麼', COL4, COL4_HELP, 'rose')
STEP_WRITE = STEP_WRITE % {'N': S_WRITE, 'PREP': S_PREP, 'SUBMIT': S_SUBMIT, 'P1': P1, 'P2': P2, 'P3': P3, 'P4': P4}
STEP_RECALL = STEP_RECALL % {'N': S_RECALL, 'RV': rv_cards(), 'RESCUE': RESCUE}

# ---------- 這幾步用的 CSS（併進 EXTRA_CSS）----------
CSS = '''
<style>
  .rv.open{background:#fffbeb;border-color:#f59e0b}
  .rv.open .q{display:none}.rv.open .a{display:block}
  .prog.on{border-color:#0d9488;background:#f0fdfa;box-shadow:0 0 0 4px #99f6e4}
  .colbtn{background:#fff;border-color:#e2e8f0;color:#64748b}
  .colbtn.on{background:#fef3c7;border-color:#f59e0b;color:#92400e}
  .colbtn.done{background:#ecfdf5;border-color:#34d399;color:#047857}
  .colbtn.on.done{box-shadow:0 0 0 3px #fde68a}
  details>summary{list-style:none}
  details>summary::-webkit-details-marker{display:none}
</style>'''

# ---------- 互動（併進 L05_HOOKS，執行在引擎裡，可用 $、state、save、showStep、renderStepper）----------
HOOKS = r'''
  // ===== 回想、進度分流、一欄一環節、句型、找回網址 =====
  var S_PREP=__PREP__,S_RECALL=__RECALL__,S_WRITE=__WRITE__,S_SUBMIT=__SUBMIT__;
  var COL_NAMES=['','① 查核網址','② 我選的訊息','③ 怎麼找到的','④ 查核結果'];
  var PROG_MSG={
    A:'👉 先到<b>第 '+S_PREP+' 步</b>，把文件的格式弄好（欄位、標題）。',
    B:'👉 用上面的 <b>①②③④</b> 找出還沒寫的那一欄，補上就好。',
    C:'👉 去檢查，檢查完還有 <b>⭐ 挑戰</b>。'};
  var PROG_GO={A:S_PREP,B:S_WRITE,C:S_WRITE};
  state.colDone=state.colDone||{};
  function colCount(){return [1,2,3,4].filter(function(n){return state.colDone[n];}).length;}
  function renderCols(){
    var cur=state.col||1;
    document.querySelectorAll('.colp').forEach(function(p){p.classList.toggle('hidden',Number(p.dataset.col)!==cur);});
    document.querySelectorAll('[data-colbtn]').forEach(function(b){
      var n=Number(b.dataset.colbtn);
      b.classList.toggle('on',n===cur);b.classList.toggle('done',!!state.colDone[n]);
      b.textContent=(state.colDone[n]?'✓ ':'')+COL_NAMES[n];
    });
    document.querySelectorAll('[data-prog]').forEach(function(b){b.classList.toggle('on',state.prog===b.dataset.prog);});
    var pb=$('progBox');
    if(pb){pb.classList.toggle('hidden',!state.prog);if(state.prog)pb.innerHTML=PROG_MSG[state.prog]+
      '<div class="mt-3 text-right"><button type="button" data-goto="'+PROG_GO[state.prog]+'" class="cute bg-teal-600 hover:bg-teal-700 text-white text-xl font-extrabold rounded-2xl px-6 py-2">'+(state.prog==='A'?'去第 '+S_PREP+' 步 →':state.prog==='C'?'去檢查 →':'去寫文件 →')+'</button></div>';}
  }
  function sent2(){
    var kw=(state.b2kw||'').trim()||'＿＿',site=state.b2site||'＿＿';
    if(state.b2how==='圖')return '我把訊息的圖片拿去以圖搜圖，點進 '+site+' 的文章。它是專門查謠言的查核機構，不是轉載。';
    return '我圈出「'+kw+'」當關鍵詞，在 Google 搜尋「'+kw+' 查核」，點進 '+site+' 的文章。它是專門查謠言的查核機構，不是轉載。';
  }
  function sent3(){
    return (state.b3org||'＿＿')+' 查核後，標為「'+(state.b3label||'＿＿')+'」。';
  }
  function renderSent(){
    var a=$('sent2'),b=$('sent3');if(a)a.textContent=sent2();if(b)b.textContent=sent3();
    var w=$('b2kwWrap');if(w)w.style.display=state.b2how==='圖'?'none':'';
  }
  // 引擎載入暫存作答之後（第一次 H.render）才綁定欄位、顯示「接續」提示
  var l5bReady=false;
  function initL5b(){
    if(l5bReady)return;l5bReady=true;
    state.colDone=state.colDone||{};
    ['b2kw','b2how','b2site','b3org','b3label'].forEach(function(k){
      var e=$(k);if(!e)return;e.value=state[k]||(k==='b2how'?'字':'');
      e.addEventListener('input',function(){state[k]=e.value;save();renderSent();});
    });
    document.querySelectorAll('.urlfixSel').forEach(function(e){e.addEventListener('change',function(){if(e.value){state.sel=e.value;save();if(H.render)H.render();renderStepper();}});});
    document.querySelectorAll('.urlKeep').forEach(function(e){e.addEventListener('input',function(){state.url=e.value;save();renderRescue();});});
    var jb=$('resumeBtn');
    if(jb){jb.onclick=function(){showStep(S_RECALL);};if(state.sel)$('resumeBox').classList.remove('hidden');}
  }
  // ===== 找回上次的網址：優先用自己記下的，沒有就用上次選的那一則的查核文章 =====
  function rescueUrl(){
    if(filled(state.url))return String(state.url).trim();
    return state.sel&&CARDS[state.sel]?CARDS[state.sel].url:'';
  }
  function renderRescue(){
    var u=rescueUrl(),own=filled(state.url);
    document.querySelectorAll('.urlfix').forEach(function(box){
      box.querySelector('[data-ufpick]').classList.toggle('hidden',!!state.sel||own);
      var b=box.querySelector('[data-ufbox]');b.classList.toggle('hidden',!u);
      if(u){
        box.querySelector('[data-ufname]').textContent=own?'你上次記下的網址':'你上次選的是：'+CARDS[state.sel].name;
        box.querySelector('[data-ufurl]').textContent=u;
        box.querySelector('[data-ufopen]').href=u;
      }
      var sel=box.querySelector('.urlfixSel');if(sel&&state.sel)sel.value=state.sel;
    });
    document.querySelectorAll('.urlKeep').forEach(function(k){if(document.activeElement!==k)k.value=state.url||'';});
  }
  function renderL5b(){initL5b();renderCols();renderSent();renderRescue();}
  document.addEventListener('click',function(ev){
    var t=ev.target.closest&&ev.target.closest('[data-rv],[data-prog],[data-colbtn],[data-coldone],[data-goto],[data-copy],[data-copyurl]');
    if(!t)return;
    if(t.hasAttribute('data-rv')){t.classList.toggle('open');return;}
    if(t.hasAttribute('data-prog')){state.prog=t.dataset.prog;if(t.dataset.prog==='C')state.col=5;else if(!state.col||state.col===5)state.col=1;save();renderCols();renderStepper();return;}
    if(t.hasAttribute('data-colbtn')){state.col=Number(t.dataset.colbtn);save();renderCols();window.scrollTo({top:0,behavior:'smooth'});return;}
    if(t.hasAttribute('data-coldone')){var n=state.col||1;state.colDone[n]=true;state.col=n+1;save();renderCols();renderStepper();window.scrollTo({top:0,behavior:'smooth'});return;}
    if(t.hasAttribute('data-goto')){var g=Number(t.dataset.goto);if(g===S_WRITE&&state.prog==='C')state.col=5;else if(g===S_WRITE&&(!state.col||state.col===5)&&colCount()<4)state.col=1;save();renderCols();showStep(g);return;}
    if(t.hasAttribute('data-copyurl')){var u=rescueUrl();if(u)copyText(u,t);return;}
    if(t.hasAttribute('data-copy')){var s=$(t.dataset.copy);if(s)copyText(s.textContent,t);return;}
  });
'''.replace('__PREP__', str(S_PREP)).replace('__RECALL__', str(S_RECALL)).replace('__WRITE__', str(S_WRITE)).replace('__SUBMIT__', str(S_SUBMIT))
