# -*- coding: utf-8 -*-
# 產生五上 L07「補完查證文件＋找主題」學習單。
# 骨架直接取自「目前的」L06 學習單（含識別列、教師列、進度列、點圖放大、Firebase、靠椅子關卡、步驟卡），
# 只換：標題、步驟內容、題目設定（C）、本節專屬的 JS（hooks）、評分設定。
# ⚠ 不要用同資料夾旁邊 _build_L05_L06/build.py：它切 L04 的行號已經過時，重建會壞掉。
# 生成後：python 引導規範/chair-gate/inject.py（已含就不會變）、python 引導規範/game-portal/check.py
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # materials/五年級上學期
SKEL = os.path.join(ROOT, 'L06_Docs查證文件二', '五上_L06_Docs查證文件二.html')
OUT = os.path.join(ROOT, 'L07_補排版與找主題', '五上_L07_補排版與找主題.html')
FMT = io.open(os.path.join(HERE, 'fmt_step.html'), encoding='utf8').read()   # 從 L06 原「格式檢查」步驟搬來

PORTAL = 'https://boyinslps.github.io/pcclass/games/'

# ---------- 示範影片（只放真的看過畫面、確認可內嵌的） ----------
DEMOS = [
    dict(id='1CTlLdkNNPw', kind='冷知識', tone='sky', vertical=True, sec='48 秒',
         title='動物也有慣用手？', src='維思維 WeisWay',
         look='黑底，最上面一條標題問問題，重點字用黃色；中間是簡單插畫，下面一句一句字幕。'),
    dict(id='iUkynDTlRn0', kind='冷知識', tone='amber', vertical=True, sec='34 秒',
         title='新發現恐龍「地獄雞」！特別愛吃水果？', src='志祺七七 Shorts',
         look='上面放真實的復原圖和論文裡的化石照片，角落寫出圖片出處，黃色字幕一句一句出現；下面有人講解。'),
]


def demo_card(d):
    ar = 'aspect-[9/16] max-h-[460px]' if d['vertical'] else 'aspect-video'
    return ('<div class="bg-white border-4 border-%(tone)s-300 rounded-3xl p-4 shadow-sm flex flex-col">'
            '<p class="cute text-xl font-extrabold text-%(tone)s-700 m-0">%(kind)s<span class="text-sm font-bold text-slate-500 ml-2">%(sec)s</span></p>'
            '<div class="%(ar)s mx-auto w-full mt-2 rounded-2xl overflow-hidden bg-slate-900">'
            '<iframe class="w-full h-full" src="https://www.youtube-nocookie.com/embed/%(id)s?rel=0" title="%(title)s" loading="lazy" '
            'allow="accelerometer; encrypted-media; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
            '<p class="font-bold text-slate-800 mt-3 text-base leading-snug">%(title)s</p>'
            '<p class="text-sm text-slate-500 mt-1">%(src)s</p>'
            '<p class="text-lg text-slate-700 mt-2"><b>看看：</b>%(look)s</p>'
            '<a href="https://www.youtube.com/watch?v=%(id)s" target="_blank" rel="noopener" class="text-sm font-bold text-indigo-600 underline mt-2">影片播不出來？在 YouTube 開啟 ↗</a>'
            '</div>') % dict(d, ar=ar)


def tone_card(tone, title, body):
    return ('<div class="bg-white border-4 border-%s-300 rounded-3xl p-5 shadow-sm"><p class="cute text-xl font-extrabold text-%s-700 m-0">%s</p>%s</div>') % (tone, tone, title, body)


STEP1 = '''
  <!-- ===== 步驟 1：看示範 ===== -->
  <section class="step" data-step="1">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">先看兩支「解說影片」</h2>
      <p class="text-slate-600 mt-2 text-lg">接下來幾堂課，你要做一支 <b>30～45 秒的解說影片</b>：用圖片、大字和旁白，把<b>一件事</b>說清楚。先看看別人怎麼做。</p>
    </div>
    <div class="grid lg:grid-cols-2 gap-5 mb-5 max-w-4xl mx-auto">
      @@DEMOS@@
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-sky-700 m-0">你發現這些影片都有什麼？<span class="text-sm font-bold text-slate-500 ml-2">可以選好幾個</span></p>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="demo"></span></div>
      <div id="demoOpts" class="flex flex-wrap gap-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''.replace('@@DEMOS@@', '\n      '.join(demo_card(d) for d in DEMOS))

_TIPS = [
    ('rose', '1　不說個資', '不打真實的姓名、學校、班級、電話、住址。只說「我是五年級學生」就夠了。'),
    ('sky', '2　說清楚要什麼', '一次問一件事。說你想做什麼、要幾個、什麼樣子，AI 才不會亂猜。'),
    ('amber', '3　AI 會說錯', '它給的資料和網址，都要自己點開來源看：網頁上真的有寫嗎？找不到來源的，就不要用。'),
    ('emerald', '4　點子自己決定', 'AI 給你幾個點子，你挑一個，再用自己的話改。決定的是你，不是 AI。'),
]
_TIP_HTML = ''.join(
    '<div class="bg-white border-4 border-%s-300 rounded-3xl p-5 shadow-sm"><p class="cute text-xl font-extrabold text-%s-700 m-0">%s</p><p class="text-lg text-slate-700 mt-2">%s</p></div>' % (t, t, h, b)
    for t, h, b in _TIPS)

STEP2 = '''
  <!-- ===== 步驟 2：跟 AI 怎麼聊 ===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-violet-700 m-0">跟 AI 聊天，先記住 4 件事</h2>
      <p class="text-slate-600 mt-2 text-lg">等一下找題目，可以請 AI 幫忙。先看這 4 個提醒，再做兩題。</p>
    </div>
    <div class="grid md:grid-cols-2 gap-4 mb-5">@@TIPS@@</div>
@@GEMVID@@
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-violet-700 m-0">① 哪一種問法，比較容易得到你要的題目？</p><span class="qtypeSlot" data-qid="tip1"></span><span id="tip1Fb" class="text-sm font-bold"></span></div>
      <div id="tip1Opts" class="space-y-2 mt-3"></div>
      <div id="tip1Exp" class="hidden mt-3 bg-violet-50 border-2 border-violet-200 rounded-2xl p-3 text-lg text-slate-700">第二種說了<b>你是誰、要做什麼、要幾個、長什麼樣子、要附網址</b>，AI 比較不用猜。</div>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-violet-700 m-0">② 哪一句話，不應該打給 AI？</p><span class="qtypeSlot" data-qid="tip2"></span><span id="tip2Fb" class="text-sm font-bold"></span></div>
      <div id="tip2Opts" class="space-y-2 mt-3"></div>
      <div id="tip2Exp" class="hidden mt-3 bg-violet-50 border-2 border-violet-200 rounded-2xl p-3 text-lg text-slate-700">真實的<b>姓名、班級、住址</b>都不能給 AI。要說自己，只說「我是五年級學生」。</div>
    </div>
    <div class="stepnav"></div>
  </section>
'''.replace('@@TIPS@@', _TIP_HTML)

# 「怎麼在 Classroom 打開 Gem 開始聊天」操作影片：老師之後給影片；放進 assets/ 才會顯示（沒有檔案就不放這一塊，不留空框）
_GEM_MP4 = os.path.join(ROOT, 'L07_補排版與找主題', 'assets', '教學_開啟Gem.mp4')
_GEM_VID = ''
if os.path.exists(_GEM_MP4):
    _GEM_VID = ('\n    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">'
                '<p class="cute text-xl font-extrabold text-violet-700 m-0">怎麼在 Classroom 打開 Gem 開始聊天</p>'
                '<video class="w-full max-w-[560px] mx-auto rounded-2xl bg-slate-900 mt-3" src="assets/教學_開啟Gem.mp4" poster="assets/教學_開啟Gem_封面.jpg" controls playsinline preload="none"></video></div>')
STEP2 = STEP2.replace('@@GEMVID@@', _GEM_VID)
print('Gem 影片：', '已放入' if _GEM_VID else '尚未提供（不顯示）')

_KINDS = [
    ('sky', '冷知識', '你知道嗎？……',
     ['你知道嗎？章魚有三顆心臟。', '你知道嗎？165 可以幫你查可疑的電話和簡訊。'],
     '一件讓人「咦？真的嗎」的小知識。'),
    ('rose', '謠言', '有人說……，是真的嗎？',
     ['有人說：撿到提款機上的鑰匙，會被設局詐騙，是真的嗎？', '有人說：別買 10 種超商麵包，是真的嗎？'],
     '一個大家都在傳的說法，你來查它是真是假。'),
    ('emerald', '事實澄清', '很多人以為……，其實……',
     ['很多人以為中獎簡訊點連結就能領獎，其實那是詐騙。', '很多人以為有網址的就是真的網站，其實詐騙網站也有網址。'],
     '大家常搞錯的事，你把正確的說出來。'),
]


def kind_card(tone, name, opener, examples, what):
    ex = ''.join('<li class="bg-slate-50 border-2 border-slate-200 rounded-2xl px-3 py-2">%s</li>' % e for e in examples)
    return ('<div class="bg-white border-4 border-%s-300 rounded-3xl p-5 shadow-sm">'
            '<p class="cute text-2xl font-extrabold text-%s-700 m-0">%s</p>'
            '<p class="text-lg text-slate-600 mt-1">%s</p>'
            '<p class="text-sm font-bold text-slate-500 mt-3">開頭可以這樣說</p>'
            '<p class="cute text-xl font-extrabold text-slate-800 mt-1">%s</p>'
            '<p class="text-sm font-bold text-slate-500 mt-3">例子</p><ul class="space-y-2 mt-1 text-lg text-slate-700">%s</ul></div>') % (tone, tone, name, what, opener, ex)


STEP3 = '''
  <!-- ===== 步驟 3：題目範圍 ===== -->
  <section class="step hidden" data-step="3">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700 m-0">我們做的是「解說影片」</h2>
      <p class="text-slate-600 mt-2 text-lg">題目不限，只要是你想讓同學知道的事。下面<b>三種</b>都可以，開頭可以用這些句子。</p>
    </div>
    <div class="grid lg:grid-cols-3 gap-5 mb-5">@@KINDS@@</div>
    <div class="bg-amber-50 border-4 border-amber-200 rounded-3xl p-6 mb-5 text-lg text-slate-700">
      <p class="cute text-xl font-extrabold text-amber-700 m-0">自己喜歡的題目也可以</p>
      <p class="mt-2">動物、運動、遊戲、食物……都可以，找你真的有興趣的。只有一個條件：<b>要找得到可靠的來源</b>。</p>
      <p class="mt-2">冷知識也要查證：找到<b>兩個不同的可靠網站</b>，說法一樣，才算數。</p>
    </div>
    <div class="stepnav"></div>
  </section>
'''.replace('@@KINDS@@', ''.join(kind_card(*k) for k in _KINDS))

STEP4 = '''
  <!-- ===== 步驟 4：我的主題 ===== -->
  <section class="step hidden" data-step="4">
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-emerald-700 m-0">找到你想講的題目</h2>
      <p class="text-slate-600 mt-2 text-lg">先選一種，再找題目。下面三個辦法，挑你喜歡的。</p>
      <p class="font-bold text-slate-700 mt-3">我選的是：<span class="qtypeSlot" data-qid="cat"></span></p>
      <div id="catOpts" class="flex flex-wrap gap-2 mt-2"></div>
    </div>

    <div class="grid md:grid-cols-3 gap-4 mb-5">
      <div class="bg-white border-4 border-emerald-300 rounded-3xl p-5 shadow-sm"><p class="cute text-xl font-extrabold text-emerald-700 m-0">辦法 1　自己想</p><p class="text-lg text-slate-700 mt-2">從你知道、你好奇的事開始，最好玩。</p></div>
      <div class="bg-white border-4 border-violet-300 rounded-3xl p-5 shadow-sm"><p class="cute text-xl font-extrabold text-violet-700 m-0">辦法 2　請 AI 幫你想</p><p class="text-lg text-slate-700 mt-2">在 Classroom 打開 Gem，照 4 個提醒問。要選一個，自己改。</p>
        <div data-set-show="gemUrl" class="hidden mt-3"><a data-set-href="gemUrl" target="_blank" rel="noopener" class="cute inline-block bg-violet-600 hover:bg-violet-700 text-white text-lg font-extrabold rounded-2xl px-5 py-2">開啟找題目小幫手 ↗</a></div></div>
      <div class="bg-white border-4 border-teal-300 rounded-3xl p-5 shadow-sm"><p class="cute text-xl font-extrabold text-teal-700 m-0">辦法 3　去查核網站逛逛</p><p class="text-lg text-slate-700 mt-2">看看大家在傳什麼謠言。</p>
        <div class="flex flex-wrap gap-2 mt-3">
          <a href="https://tfc-taiwan.org.tw/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-3 py-1.5">台灣事實查核中心 ↗</a>
          <a href="https://www.mygopen.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-3 py-1.5">MyGoPen ↗</a>
          <a href="https://165.npa.gov.tw/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-3 py-1.5">165 全民防騙網 ↗</a>
        </div></div>
    </div>

    <div data-set-admin="gemUrl" class="hidden bg-slate-100 border-2 border-dashed border-slate-300 rounded-2xl p-4 mb-5">
      <p class="font-bold text-slate-600 text-sm">老師設定：找題目小幫手（Gem）的分享網址（貼上並儲存，學生就會看到按鈕；不貼就不顯示）</p>
      <div class="flex gap-2 flex-wrap mt-2 items-center">
        <input type="url" data-set-input="gemUrl" autocomplete="off" class="flex-1 min-w-[16rem] border-2 border-slate-300 rounded-xl px-3 py-2 text-base bg-white">
        <button type="button" data-set-save class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl px-4 py-2">儲存網址</button>
      </div>
      <p data-set-stat class="text-sm font-bold mt-2 min-h-[20px]"></p>
    </div>

    <div class="bg-white border-4 border-amber-200 rounded-3xl p-5 mb-5 text-lg">
      <p class="cute text-xl font-extrabold text-amber-700 m-0">範例（老師的示範）</p>
      <ul class="mt-2 space-y-1 text-slate-700">
        <li><b>開頭句：</b>有人說：撿到提款機上的鑰匙，會被設局詐騙，是真的嗎？</li>
        <li><b>來源：</b>台灣事實查核中心的查核報告，網址整條貼上。</li>
        <li><b>核心訊息：</b>這個說法查不到案例，不要被嚇到亂轉傳。</li>
      </ul>
    </div>

    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm space-y-5">
      <div><div class="flex items-center gap-2 flex-wrap"><label for="hook" class="cute text-xl font-extrabold text-emerald-700">① 我的開頭句</label><span class="qtypeSlot" data-qid="hook"></span></div>
        <textarea id="hook" data-k="hook" rows="2" class="fld ans mt-2 text-lg"></textarea></div>
      <div><div class="flex items-center gap-2 flex-wrap"><label for="src" class="cute text-xl font-extrabold text-emerald-700">② 我找到的來源（貼上網址）</label><span class="qtypeSlot" data-qid="src"></span></div>
        <input id="src" data-k="src" type="url" autocomplete="off" class="fld ans mt-2 text-lg">
        <div class="flex items-center gap-2 flex-wrap mt-2"><span class="qtypeSlot" data-qid="seen"></span><div id="seenOpts" class="flex flex-wrap gap-2"></div></div></div>
      <div><div class="flex items-center gap-2 flex-wrap"><label for="core" class="cute text-xl font-extrabold text-emerald-700">③ 我的核心訊息（一句話，20 字內）</label><span class="qtypeSlot" data-qid="core"></span></div>
        <textarea id="core" data-k="core" rows="2" class="fld ans mt-2 text-lg"></textarea></div>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-5 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-emerald-700 m-0">存起來，下次接著用</p>
      <p class="text-lg text-slate-700 mt-2">先填好最上面的年級、班級、座號。換一台電腦、下一節課，都能拿回來。</p>
      <div class="flex gap-2 flex-wrap mt-3">
        <button type="button" id="topicSave" class="cute bg-emerald-600 hover:bg-emerald-700 text-white text-lg font-extrabold rounded-2xl px-5 py-2">存起來</button>
        <button type="button" id="topicLoad" class="bg-white border-2 border-emerald-400 hover:bg-emerald-50 text-emerald-800 font-bold rounded-2xl px-5 py-2">拿回我存的主題</button>
      </div>
      <p id="topicStat" class="text-base font-bold mt-3 min-h-[24px]"></p>
    </div>
    <div class="stepnav"></div>
  </section>
'''

# 步驟 5：把 L06 原本的「格式檢查」搬過來（標題與說明改成補完文件）
_s5 = FMT.replace('<!-- ===== 步驟 9：格式檢查 ===== -->', '<!-- ===== 步驟 5：補完查證文件 ===== -->').replace('data-step="9"', 'data-step="5"')
_s5 = _s5.replace('<h2 class="cute text-3xl font-extrabold text-sky-700 m-0">格式檢查</h2>',
                  '<h2 class="cute text-3xl font-extrabold text-sky-700 m-0">補完你的查證文件：檢查格式</h2>')
_s5 = _s5.replace('<p class="text-lg text-slate-600 mt-1">內容寫完了，最後檢查<b>字型、字級、樣式、連結</b>。下面的字都是真的大小。</p>',
                  '<p class="text-lg text-slate-600 mt-1">上一節的查證文件，格式還沒排好的現在補；已經排好的，檢查一遍就好。要檢查<b>字型、字級、樣式、連結</b>，下面的字都是真的大小。</p>')
_s5 = _s5.replace('<p class="text-base text-slate-500 mt-1">點一下文件裡那一行，上面的工具列會顯示它的樣式、字型、字級。</p>',
                  '<p class="text-base text-slate-500 mt-1">點一下文件裡那一行，上面的工具列會顯示它的樣式、字型、字級。文件已經繳交、改不動的話，先到 Classroom 作業按「取消繳交」，改完再繳交一次。</p>')
assert '補完你的查證文件' in _s5 and '取消繳交' in _s5 and 'data-step="5"' in _s5
_FMT_CHECK = '''
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-sky-700 m-0">我檢查過了</p><span class="qtypeSlot" data-qid="fmt"></span></div>
      <div id="fmtOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h3 class="cute text-2xl font-extrabold text-indigo-700 m-0">改完了，回 Classroom 重新繳交</h3>
      <p class="text-lg text-slate-700 mt-2">回 <b>Classroom 作業</b>，確認文件<b>附在作業裡</b>，按<b>「繳交」</b>，再按一次確認。</p>
      <details class="mt-3 bg-slate-50 border-2 border-slate-300 rounded-2xl p-3"><summary class="cursor-pointer font-extrabold text-slate-700 text-lg">查看操作影片：怎麼在 Classroom 繳交</summary><div class="mt-3">
        <video class="w-full max-w-[560px] mx-auto rounded-2xl bg-slate-900" src="assets/教學_繳交.mp4" poster="assets/教學_繳交_封面.jpg" controls playsinline preload="none"></video></div></details>
    </div>
    <div class="stepnav"></div>'''
_s5 = _s5.replace('\n    <div class="stepnav"></div>', _FMT_CHECK, 1)
STEP5 = '\n' + _s5

# 步驟 5b：檢查欄位內容是否正確、說明是否正確（2026-11-10 老師：排版完下一步）
# 判準取自 L05、L06 的評分設定（doc、doc2 的 checks），例子用老師示範 G1（幫陌生人操作手機，L05/G1_成品範例_草稿.md），不用學生會選的訊息以免直接抄。
def _fcard(color, title, chips, good, weak):
    chip = ''.join('<span class="bg-{c}-100 border-2 border-{c}-300 text-{c}-900 rounded-full px-3 py-0.5 text-base font-bold">{t}</span>'.format(c=color, t=t) for t in chips)
    return ('<div class="bg-white border-4 border-{c}-300 rounded-3xl p-5 mb-5 shadow-sm"><h3 class="cute text-2xl font-extrabold text-{c}-700 m-0">{title}</h3>'
            '<div class="flex flex-wrap gap-2 mt-2">{chip}</div>'
            '<div class="docpage"><p class="text-sm font-bold text-emerald-700" style="font-size:14px">✓ 這樣寫</p><p>{good}</p></div>'
            '<div class="docpage mt-2" style="background:#fff7ed"><p class="text-sm font-bold text-rose-700" style="font-size:14px">✗ 還不夠</p><p>{weak}</p></div></div>').format(c=color, title=title, chip=chip, good=good, weak=weak)

STEPC = '''
  <!-- ===== 步驟 5b：檢查欄位內容 ===== -->
  <section class="step hidden" data-step="5">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">檢查欄位的內容對不對</h2>
      <p class="text-lg text-slate-600 mt-1">格式排好了，接著看<b>內容</b>。打開你的查證文件，一欄一欄對照下面的樣子；沒做到的，直接在文件裡補。</p>
      <p class="text-base text-slate-500 mt-1">例子是老師的示範「幫陌生人操作手機」。你的文件要寫你自己選的那一則，不用寫得比例子長。</p>
    </div>
''' + ''.join([
    _fcard('sky', '① 我選的訊息', ['用自己的話', '人、事、時、地、物', '沒寫的標「沒說」', '有貼原始訊息圖片或截圖'],
           '網傳訊息說：路上有陌生人假裝不會用手機，請你幫忙操作；只要摸螢幕、對著鏡頭說話，指紋、聲音和臉就會被偷走，拿去貸款。人：陌生人和幫忙的人；事：指紋、聲音、臉被偷；時：沒說；地：路上；物：手機。（下面貼訊息截圖）',
           '一則網傳訊息。（沒說是哪一則、什麼事，也沒有截圖）'),
    _fcard('indigo', '② 我怎麼找到查核文章的', ['寫「以圖搜圖」就可以', '或寫「用……關鍵字查到的」', '關鍵字要寫出來'],
           '我用以圖搜圖找到的。　或　我用「陌生人　操作手機　生物特徵　查核」這幾個關鍵字查到的。',
           '我找到的。（沒說用什麼方法；用關鍵字卻沒寫是哪幾個字）'),
    _fcard('teal', '③ 查核結果和查核網址', ['寫出結果（錯誤、誤導…）', '寫出是哪一家機構', '網址是整條 https:// 開頭', '網址是查核機構自己的網站'],
           'MyGoPen 標示【誤導】，台灣事實查核中心標示「錯誤」。網址：https://tfc-taiwan.org.tw/fact-check-reports/…（整條，點得開）。',
           '查核結果：假的。（沒寫哪一家機構；網址只寫了網站名稱）'),
    _fcard('amber', '④ 正確資訊', ['用自己的話寫 1～3 點', '不是整段複製查核文章', '標出是哪個機構或專家說的'],
           '1. 只有指紋、臉或聲音，不能直接拿去貸款，銀行還要看好幾道檢查。2. 警方和 165 說，台灣查不到這種手法的案件。（MyGoPen）',
           '（把查核文章「查核點」整段複製貼上）'),
    _fcard('rose', '⑤ 為什麼這則訊息會被廣傳？', ['至少一個原因', '原因要說明理由'],
           '因為它說「30 分鐘傾家蕩產」，讓人很害怕；最後又寫「轉傳給家人朋友」，大家覺得轉出去就是在保護家人。',
           '因為很多人相信。'),
    _fcard('violet', '⑥ 如果相信的話，會有什麼後果？', ['說出「誰」會怎樣', '不只寫「是假的」「會被騙」'],
           '我們可能不敢幫真的需要幫忙的人，也會把嚇人的訊息再傳給更多人，讓大家一起害怕。',
           '會被騙。／這則訊息是假的。'),
]) + '''
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-sky-700 m-0">我檢查過了</p><span class="qtypeSlot" data-qid="cont"></span></div>
      <div id="contOpts" class="space-y-2 mt-3"></div>
      <p class="text-base text-slate-600 mt-3">文件有修改的話，回 <b>Classroom 作業</b>按「取消繳交」，改好再按「繳交」。</p>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP6 = '''
  <!-- ===== 步驟 6：繳交 ===== -->
  <section class="step hidden" data-step="6">
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-indigo-700">繳交前自己檢查</h2>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="chk"></span></div>
      <div id="chkOpts" class="space-y-2 mt-3"></div>
      <div class="bg-indigo-50 border-2 border-indigo-200 rounded-2xl p-4 mt-4 text-lg text-slate-700">
        <p class="font-bold text-indigo-800">查證文件有修改的話：</p>
        <p class="mt-1">回 <b>Classroom 作業</b>，確認文件<b>附在作業裡</b>，按<b>「繳交」</b>。</p>
      </div>
      <p class="font-bold text-indigo-800 mt-5 mb-2">看影片：怎麼在 Classroom 繳交</p>
      <video class="w-full max-w-[560px] mx-auto rounded-2xl bg-slate-900" src="assets/教學_繳交.mp4" poster="assets/教學_繳交_封面.jpg" controls playsinline preload="none"></video><p class="text-[11px] text-slate-400 mt-1 text-center">回 Classroom 分頁，按「繳交」，再按一次確認</p>
    </div>
    <div data-set-admin="gameUrl" class="hidden bg-slate-100 border-2 border-dashed border-slate-300 rounded-2xl p-4 mt-6">
      <p class="font-bold text-slate-600 text-sm">老師設定：真假對決的網址（不填就沿用 L06 設定的；開好伺服器後貼上並儲存，學生繳交後就會看到按鈕）</p>
      <div class="flex gap-2 flex-wrap mt-2 items-center">
        <input type="url" data-set-input="gameUrl" autocomplete="off" class="flex-1 min-w-[16rem] border-2 border-slate-300 rounded-xl px-3 py-2 text-base bg-white">
        <button type="button" data-set-save class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl px-4 py-2">儲存網址</button>
      </div>
      <p data-set-stat class="text-sm font-bold mt-2 min-h-[20px]"></p>
    </div>
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-5 shadow-sm text-center mt-6">
      <h2 class="cute text-xl font-extrabold text-indigo-700 mb-1">繳交學習單</h2>
      <p class="text-sm text-slate-500 mb-3">確定都填好了嗎？按下面按鈕交給老師（可以重交，會覆蓋前一次）。</p>
      <button id="submitBtn" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white cute text-xl font-extrabold rounded-2xl py-3">繳交學習單</button>
      <p id="submitStat" class="text-sm font-bold mt-3 min-h-[20px]"></p>
    </div>

    <div id="rewardBox" class="hidden text-center bg-gradient-to-b from-indigo-100 to-sky-100 border-4 border-indigo-300 rounded-3xl p-7 mt-6">
      <div class="text-6xl mb-2 pop">🎉</div>
      <h2 class="cute text-3xl font-extrabold text-indigo-700">恭喜你已經做完今日的作業，可以遊玩！</h2>
      <div data-set-show="gameUrl" class="hidden mt-5">
        <p class="text-xl font-bold text-slate-700">接下來，來挑戰「真假對決」</p>
        <p class="text-lg text-slate-600 mt-1">玩一段時間後，老師會看排名，名次在前面的同學可以先自由活動。</p>
        <a data-set-href="gameUrl" target="_blank" rel="noopener" class="cute inline-block bg-indigo-600 hover:bg-indigo-700 text-white text-2xl font-extrabold rounded-2xl px-10 py-4 mt-4">開始玩　真假對決</a>
      </div>
      <div class="flex flex-wrap gap-3 justify-center mt-4">
        <a href="@@PORTAL@@" target="_blank" rel="noopener" class="cute inline-block bg-white border-4 border-indigo-400 hover:bg-indigo-50 text-indigo-700 text-2xl font-extrabold rounded-2xl px-10 py-4">電腦教室遊戲網站</a>
      </div>
    </div>
    <div class="stepnav"></div>
  </section>
'''.replace('@@PORTAL@@', PORTAL)

# 步驟順序（2026-11-05 老師：補完查證文件是第一步；11-10 排版後接檢查內容）：檢查格式／檢查內容／看示範／跟 AI 聊天／題目範圍／我的主題／繳交
def renum(s, n):
    s = re.sub(r'data-step="\d"', 'data-step="%d"' % n, s, count=1)
    s = re.sub(r'<section class="step( hidden)?"', '<section class="step' + (' hidden' if n > 1 else '') + '"', s, count=1)
    return re.sub(r'步驟 \d：', '步驟 %d：' % n, s, count=1)


BODY = '\n' + ''.join(renum(s, i + 1) for i, s in enumerate([STEP5, STEPC, STEP1, STEP2, STEP3, STEP4, STEP6])) + '\n'

CFG = {
    'ws': 'g5-L07', 'lessonPath': 'g5/L07', 'title': '找主題：解說影片的題目', 'stateKey': 'g5L07flow',
    'steps': ['檢查格式', '檢查內容', '看示範', '跟 AI 聊天', '題目範圍', '我的主題', '繳交'],
    'reveals': [], 'revealOf': {}, 'autoFb': ['tip1', 'tip2'], 'textSettings': ['gemUrl', 'gameUrl'],
    'qtypes': {'demo': 'experience', 'tip1': 'score', 'tip2': 'score', 'cat': 'experience', 'hook': 'open', 'src': 'open',
               'seen': 'experience', 'core': 'open', 'fmt': 'experience', 'cont': 'experience', 'chk': 'experience'},
    'choices': {
        'demo': {'opts': ['一開始就問一個問題', '用插畫、照片或影片當畫面', '重點用大字或顏色標出來', '下面有字幕', '有人在旁白說明', '最後有結論或提醒'], 'multi': True},
        'tip1': {'opts': ['幫我想一個影片題目', '我是五年級學生，想做 30 秒的解說影片。請給我 3 個「有人說……，是真的嗎？」的題目，每個都附上查核網站的網址。'],
                 'block': True, 'correct': '我是五年級學生，想做 30 秒的解說影片。請給我 3 個「有人說……，是真的嗎？」的題目，每個都附上查核網站的網址。'},
        'tip2': {'opts': ['我是五年級學生，想找冷知識的題目。', '我叫王小明，讀 5 年 3 班，住在……', '請給我 3 個題目，每個都附上來源網址。'],
                 'block': True, 'correct': '我叫王小明，讀 5 年 3 班，住在……'},
        'cat': {'opts': ['冷知識', '謠言', '事實澄清']},
        'seen': {'opts': ['我點開來源看過了，網頁上真的有寫'], 'multi': True},
        'fmt': {'opts': ['文件標題：標題 1、標楷體、26', '7 個欄位名稱：標題 2、標楷體、16', '查核網址：整條網址、超連結、點得開', '其餘內容：一般文字'], 'multi': True, 'block': True},
        'cont': {'opts': ['我選的訊息：用自己的話，有人事時地物，有貼圖', '我怎麼找到查核文章的：寫了是用以圖搜圖，或用哪些關鍵字查到的', '查核結果和查核網址：有結果、有機構、網址是整條', '正確資訊：用自己的話 1～3 點，有標出處', '為什麼會被廣傳：至少一個原因，說明了理由', '如果相信的後果：說出誰會怎樣'], 'multi': True, 'block': True},
        'chk': {'opts': ['我選好類型，也寫了開頭句', '我貼了來源網址，而且點開看過', '我寫了一句核心訊息', '查證文件的格式和內容檢查過了'], 'multi': True, 'block': True},
    },
    'texts': ['hook', 'src', 'core'],
    'patterns': {'src': r'^https?://\S+'},
    'openQtexts': {
        'hook': '我的解說影片開頭句（例如「你知道嗎？……」「有人說……，是真的嗎？」）。',
        'src': '我找到的來源網址。',
        'core': '我的核心訊息：一句話，20 字內。',
    },
}

HOOKS = r'''
  H.stepDone=function(n){
    var a=function(k){return state[k]!=null&&(Array.isArray(state[k])?state[k].length>0:filled(state[k]));};
    if(n===1)return a('fmt')&&n!==curStep;
    if(n===2)return a('cont')&&n!==curStep;
    if(n===3)return a('demo')&&n!==curStep;
    if(n===4)return a('tip1')&&a('tip2')&&n!==curStep;
    if(n===6)return a('cat')&&a('hook')&&a('src')&&a('core')&&n!==curStep;
    return null;
  };
  H.report=function(){
    return ['類型：'+(state.cat||'還沒選'),
      '開頭句：'+(filled(state.hook)?'已寫':'還沒寫'),
      '來源網址：'+(filled(state.src)?'已貼':'還沒貼'),
      '核心訊息：'+(filled(state.core)?'已寫':'還沒寫'),
      '自查表：已勾 '+((state.chk||[]).length)+' 項（共 4 項）','提醒：查證文件有修改的話，要在 Classroom 作業按「繳交」'];
  };
  H.showAnswers=function(){state.tip1=C.choices.tip1.correct;state.tip2=C.choices.tip2.correct;};
  H.clear=function(){['demo','fmt','cont','chk','seen'].forEach(function(k){state[k]=[];});['tip1','tip2','cat'].forEach(function(k){state[k]=null;});['hook','src','core'].forEach(function(k){state[k]='';});};
  H.render=function(){
    ['tip1','tip2'].forEach(function(q){var e=$(q+'Exp');if(e)e.classList.toggle('hidden',!state[q]);});
  };
  H.changed=function(){H.render();};

  // ===== 我的主題：存到學生暫存區 studentWork（id：g5-L07__年-班-號__topic），下一節讀回來用 =====
  function topicDocId(i){return WS+'__'+i.grade+'-'+i.className+'-'+i.studentId+'__topic';}
  function topicHasData(){return !!state.cat||filled(state.hook)||filled(state.src)||filled(state.core);}
  function topicStat(msg,tone){var e=$('topicStat');if(!e)return;e.className='text-base font-bold mt-3 min-h-[24px] text-'+tone+'-600';e.textContent=msg;}
  function saveTopic(i){
    var d={cat:state.cat||'',hook:String(state.hook||''),src:String(state.src||''),core:String(state.core||'')};
    var txt=('類型：'+d.cat+'\n開頭句：'+d.hook+'\n來源：'+d.src+'\n核心訊息：'+d.core).slice(0,1500);
    return authResolved.then(function(){return ensureAuth();}).then(function(){
      return db.collection('studentWork').doc(topicDocId(i)).set({worksheetId:WS,kind:'topic',grade:i.grade,className:i.className,studentId:i.studentId,data:d,text:txt,updatedAt:firebase.firestore.FieldValue.serverTimestamp()});
    });
  }
  H.afterSubmit=function(i){if(topicHasData())saveTopic(i).catch(function(e){console.warn('存主題失敗',e);});};
  $('topicSave').onclick=function(){
    var i=getIdentity();
    if(!identityValid(i)){markIdentity(true);topicStat('先到頁面最上面填年級、班級、座號，再按一次。','rose');return;}
    markIdentity(false);
    if(!topicHasData()){topicStat('先寫一點再存。','amber');return;}
    if(!db){topicStat('現在連不上，晚點再試試看。','amber');return;}
    topicStat('存檔中…','indigo');
    saveTopic(i).then(function(){topicStat('✓ 已存起來。下次按「拿回我存的主題」就有了。','emerald');})
      .catch(function(e){console.warn('存主題失敗',e);topicStat('現在存不了，晚點再試試看。','amber');});
  };
  $('topicLoad').onclick=function(){
    var i=getIdentity();
    if(!identityValid(i)){markIdentity(true);topicStat('先到頁面最上面填年級、班級、座號，再按一次。','rose');return;}
    markIdentity(false);
    if(!db){topicStat('現在連不上，晚點再試試看。','amber');return;}
    authResolved.then(function(){return ensureAuth();}).then(function(){return db.collection('studentWork').doc(topicDocId(i)).get();}).then(function(doc){
      if(!doc.exists){topicStat('還沒有找到你存過的主題。填好之後按「存起來」，下次就能拿回來。','amber');return;}
      if(topicHasData()&&!confirm('這會換掉你現在寫的內容，確定要拿回之前存的嗎？'))return;
      var d=(doc.data()||{}).data||{};
      state.cat=d.cat||null;state.hook=d.hook||'';state.src=d.src||'';state.core=d.core||'';
      save();renderAll();topicStat('✓ 已拿回你存的主題。','emerald');
    }).catch(function(e){console.warn('拿回主題失敗',e);topicStat('現在拿不到，晚點再試試看。','amber');});
  };
'''

SPEC = {
    'summary': '看兩支解說影片（冷知識）認識這類影片的樣子；學 4 個跟 AI 聊天的提醒（不給個資、說清楚、AI 會說錯、點子自己決定）；從冷知識、謠言、事實澄清三種裡選一種，找到自己想講的題目，寫開頭句、貼可靠來源並點開確認、寫一句核心訊息；並補完 L06 查證文件的格式與內容檢查。',
    'questions': [
        {'qid': 'hook', 'prompt': '我的解說影片開頭句（例如「你知道嗎？……」「有人說……，是真的嗎？」）。', 'mode': 'checklist',
         'checks': [{'desc': '是一個完整的開頭句，用「你知道嗎」「有人說…是真的嗎」「很多人以為…其實…」這類句型，或同樣能引起好奇的問句', 'pts': 2},
                    {'desc': '題目具體，看得出要講哪一件事，不是「一個冷知識」這種空話', 'pts': 2}]},
        {'qid': 'src', 'prompt': '我找到的來源網址。', 'mode': 'checklist',
         'checks': [{'desc': '貼的是 http(s):// 開頭的整條網址（不是只寫網站名稱）', 'pts': 2},
                    {'desc': '網址看得出是可靠的來源（查核機構、政府、學校、新聞媒體或專業機構），不是匿名貼文或內容農場', 'pts': 2}]},
        {'qid': 'core', 'prompt': '我的核心訊息：一句話，20 字內。', 'mode': 'checklist',
         'checks': [{'desc': '只有一句話，大約 20 字內', 'pts': 3},
                    {'desc': '說的是結論或提醒（例如「查不到案例，不要亂轉傳」），不只是重複題目', 'pts': 3}]},
    ],
    'scoring': {'base': 100, 'floor': 80, 'deduction': 1, 'itemPoints': {'tip1': 3, 'tip2': 3}},
}

_EMOJI = re.compile('[\U0001F000-\U0001FAFF☀-⛿✀-➿⬀-⯿️‍]')
_KEEP = '✓✔☐☑★☆'


def strip_emoji(html):
    return ''.join(ch for ch in html if not (_EMOJI.match(ch) and ch not in _KEEP))


raw = io.open(SKEL, encoding='utf8', newline='').read()
t = raw.replace('\r\n', '\n')

def sub1(pat, repl, s, flags=re.S):
    new, n = re.subn(pat, lambda m: repl, s, count=1, flags=flags)
    assert n == 1, pat
    return new

t = sub1(r'<title>.*?</title>', '<title>找一個想講的題目｜L07 教學活動</title>', t)
t = sub1(r'<h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">.*?</h1>',
         '<h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">找一個想講的題目</h1>', t)
t = sub1(r'<p class="text-sm text-slate-500 mt-2">L06 Docs[^<]*</p>',
         '<p class="text-sm text-slate-500 mt-2">L07 補完查證文件・找主題 · 教學活動流程（40 分鐘）</p>', t)
# 內容：<header>…</header> 到 <footer> 之間
i = t.index('  </header>\n') + len('  </header>\n')
j = t.index('  <footer')
t = t[:i] + strip_emoji(BODY.replace('<div class="text-6xl mb-2 pop">🎉</div>', '<div class="text-6xl mb-2 pop"></div>')) + '\n' + t[j:]
t = sub1(r'<footer class="text-center text-xs text-slate-400 mt-8 pb-2">.*?</footer>',
         '<footer class="text-center text-xs text-slate-400 mt-8 pb-2">老師設定與檢視：在網址列加上 <code class="bg-slate-200 rounded px-1">#admin</code> 後重新整理。示範影片來自 YouTube（維思維 WeisWay、志祺七七）。</footer>', t)
# 設定 C
t = sub1(r'  var C=\{.*?\};\n', '  var C=' + json.dumps(CFG, ensure_ascii=False) + ';\n', t)
# 本節專屬 JS：從「複製七個欄位」到「作答狀態」之前
a = t.index('// ===== 複製七個欄位')
a = t.rfind('\n', 0, a) + 1
b = t.index('// ===== 作答狀態（localStorage 暫存）')
b = t.rfind('\n', 0, b) + 1
t = t[:a] + HOOKS + '\n' + t[b:]
t = t.replace("已儲存，學生繳交後就會看到按鈕", "已儲存，學生馬上就會看到按鈕")
# 找題目 Gem 的預設網址（老師 2026-11-10 提供）：老師沒在 #admin 另填時用這個
GEM_URL = 'https://gemini.google.com/gem/1hC9bs9aBqIvNCe3GKbjujuU86tN7M21R?usp=sharing'
assert t.count("var SET={};") == 1 and t.count("SET[k]=String(d[k]||'');") == 1
t = t.replace("var SET={};", "var DEFAULT_SET={gemUrl:'" + GEM_URL + "'};var OWN={};var SET={gemUrl:DEFAULT_SET.gemUrl};")
t = t.replace("SET[k]=String(d[k]||'');", "OWN[k]=String(d[k]||'');SET[k]=OWN[k]||DEFAULT_SET[k]||'';")
# 真假對決：L07 自己沒設定網址，就沿用老師在 L06 設定的（quizzes/g5-L06.gameUrl，公開可讀）
_snap = "    var first=true;\n    quizRef.onSnapshot("
assert t.count(_snap) == 1
t = t.replace(_snap, "    db.collection('quizzes').doc('g5-L06').get().then(function(x){var u=x.exists&&x.data()&&x.data().gameUrl;if(u){DEFAULT_SET.gameUrl=String(u);if(!OWN.gameUrl){SET.gameUrl=String(u);applySettings();}}}).catch(function(){});\n" + _snap)
# 評分設定
t = sub1(r'<script type="application/json" id="grading-spec">\n.*?\n</script>',
         '<script type="application/json" id="grading-spec">\n' + json.dumps(SPEC, ensure_ascii=False, indent=2) + '\n</script>', t)

io.open(OUT, 'w', encoding='utf8', newline='\r\n').write(t)
print('wrote', OUT, len(t) // 1024, 'KB')
