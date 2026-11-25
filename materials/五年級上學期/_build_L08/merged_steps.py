# -*- coding: utf-8 -*-
# L08 的「寫台詞」部分（確認主題以後、Canva 以前）。由 build_L08.py 匯入。
# 老師規則：關鍵字學生自己選，AI 不幫忙；只有寫台詞 AI 可以協助，而且用提問引導；要給台詞撰寫範例。
# 2026-11-16 晚：文件由老師幫學生開；台詞改回在學習單裡填，填完按「複製台詞表」貼進老師給的文件。
# 2026-11-17：第 3 步＝直接對 Gem 說「開始寫台詞」（Gem 老師自己寫好，學習單不再收資料、不再給複製訊息）；
#             台詞表可用「新增問題／解釋／結論」加句子；關鍵字改到「貼進文件之後」在文件裡寫，學習單不再收關鍵字。
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '_build_shared'))
import ckpt                      # 先繳交（存檔）／讀取拿回：L07、L08 共用

MAXR = 12                       # 台詞最多幾句（欄位 s1..s12、段落 g1..g12）
DEFAULT_SEGS = 'qqeeeec'        # 一開始的 7 句：開頭 2、主體 4、CTA 1（q／e／c 只是內部代號：q=開頭、e=主體、c=CTA）

# 示範影片（老師自己想的題目，不用現成的查核報告，避免學生照抄）。每列：段、台詞、這句在做什麼、關鍵字（只有「冷知識」那支給關鍵字範例）
# 三段＝①開頭（Hook）②主體 ③CTA。2026-11-17 老師：冷知識沒有「問題」，所以不再用「問題／解釋／結論」。
DEMOS = {
    'rumor': {'label': '假資訊', 'type': '謠言', 'topic': '口香糖吞下去，會留在肚子裡 7 年？', 'rows': [
        ('①開頭（Hook）', '有人說：吞下口香糖，會卡在肚子 7 年？', '把網路上流傳的說法說出來，讓人想知道真假', ''),
        ('①開頭（Hook）', '這是真的嗎？', '把問題丟給大家，讓人想聽下去', ''),
        ('②主體（Body）', '口香糖裡的膠，人體確實消化不了。', '介紹背景：先說真的部分，是什麼東西', ''),
        ('②主體（Body）', '但它不會卡在肚子裡。', '說出重點：一句只講一件事', ''),
        ('②主體（Body）', '它會跟其他食物一起，慢慢排出去。', '證據：它後來去了哪裡', ''),
        ('②主體（Body）', '所以「留在肚子 7 年」是假的。', '說出查證的結果', ''),
        ('③行動呼籲（CTA）', '如果有人這樣說，記得提醒他。', 'CTA：只放一個，提醒身邊的人', ''),
    ]},
    'fact': {'label': '冷知識', 'type': '冷知識', 'topic': '章魚有三顆心臟', 'rows': [
        ('①開頭（Hook）', '你知道嗎？章魚有三顆心臟！', '震撼事實開頭：用想不到的事實讓人停下來', '章魚　心臟'),
        ('①開頭（Hook）', '而且牠的血是藍色的。', '再補一個驚人的事實，讓人想聽下去', '藍色　血'),
        ('②主體（Body）', '章魚是一種住在海裡的軟體動物。', '介紹背景：OOO是一種……', '海底　章魚'),
        ('②主體（Body）', '兩顆心臟，把血送去鰓。', '說明：一句只講一件事', '鰓　心臟'),
        ('②主體（Body）', '另一顆心臟，把血送到全身。', '接著講另一件事', '身體　血管'),
        ('②主體（Body）', '牠的血含銅，所以看起來是藍的。', '說明原因：為什麼是藍色', '銅　藍色'),
        ('③行動呼籲（CTA）', '下次看到章魚，記得跟朋友分享！', 'CTA：分享讓更多人知道', '朋友　分享'),
    ]},
    'clarify': {'label': '事實釐清', 'type': '事實澄清', 'topic': '蝙蝠是瞎子？', 'rows': [
        ('①開頭（Hook）', '很多人以為，蝙蝠是瞎子。', '說出大家常有的誤會', ''),
        ('①開頭（Hook）', '其實，牠們看得見！', '馬上說出真相，讓人想知道為什麼', ''),
        ('②主體（Body）', '蝙蝠是一種會飛的哺乳動物。', '介紹背景：OOO是一種……', ''),
        ('②主體（Body）', '所有的蝙蝠都有眼睛，也看得見。', '證據：直接回答誤會', ''),
        ('②主體（Body）', '有些蝙蝠還會發出聲音，聽回聲找路。', '再補充：牠們還有另一種本領', ''),
        ('②主體（Body）', '這叫「回聲定位」，晚上不容易撞到東西。', '說明這個本領叫什麼、有什麼用', ''),
        ('③行動呼籲（CTA）', '下次有人說蝙蝠是瞎子，告訴他真相！', 'CTA：下次遇到……，要……', ''),
    ]},
}
for _k, _d in DEMOS.items():
    for _r in _d['rows']:
        assert len(_r[1]) <= 20, (_k, _r[1], len(_r[1]))
_TONE = {'①': 'rose', '②': 'sky', '③': 'emerald'}
_FACT = DEMOS['fact']['rows']
# 第 5 步「老師的台詞」、第 7 步「老師的關鍵字」都用「冷知識」那支當示範
EX_LINES_HTML = ''.join(
    '<tr class="border-t border-slate-200"><td class="py-1.5 pr-2 font-bold text-%s-700">%s</td><td class="py-1.5 text-slate-900">%s</td></tr>'
    % (_TONE[g[0]], g, s) for g, s, n, k in _FACT)
EX_KW_HTML = ''.join(
    '<tr class="border-t border-slate-200"><td class="py-1.5 pr-2 font-bold text-%s-700">%s</td><td class="py-1.5 pr-3">%s</td><td class="py-1.5 text-slate-700">%s</td></tr>'
    % (_TONE[g[0]], g, s, k) for g, s, n, k in _FACT)

# 先繳交（存檔）／讀取拿回（2026-11-17 老師：需要大量寫入的步驟都要有；繳交在評分平台視同已繳交）
SAVE = ckpt.CARD

STEP_PARTS = '''
  <!-- ===== 步驟 2：短影片分成三個部分 ===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">短影片分成三個部分</h2>
      <p class="text-slate-600 mt-2 text-lg">這是做短影片的小技巧：把影片分成<b>三個部分</b>，每個部分只做一件事。你的台詞也照這三個部分來寫。</p>
    </div>
    <div class="grid md:grid-cols-3 gap-4 mb-5">
      <div class="bg-rose-50 border-4 border-rose-200 rounded-3xl p-5 text-lg"><p class="cute text-xl font-extrabold text-rose-700 m-0">① 開頭（Hook）</p><p class="mt-1 text-slate-700">前 3 秒，1～2 句。<br>任務：<b>讓人停下來</b>，想聽下去。</p></div>
      <div class="bg-sky-50 border-4 border-sky-200 rounded-3xl p-5 text-lg"><p class="cute text-xl font-extrabold text-sky-700 m-0">② 主體（Body）</p><p class="mt-1 text-slate-700">3～4 句。<br>任務：把內容說清楚，<b>每一句只講一件事</b>。</p></div>
      <div class="bg-emerald-50 border-4 border-emerald-200 rounded-3xl p-5 text-lg"><p class="cute text-xl font-extrabold text-emerald-700 m-0">③ 行動呼籲（CTA）<span class="block text-xs font-bold text-emerald-600">Call To Action</span></p><p class="mt-1 text-slate-700">最後 1 句。<br>任務：告訴大家<b>看完可以做什麼</b>。</p></div>
    </div>

    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-2xl font-extrabold text-rose-700 m-0">① 開頭（Hook）：前 3 秒決定別人要不要看</p>
      <ul class="mt-3 space-y-1 text-lg text-slate-700 list-disc pl-6">
        <li>你滑短影片的時候也是這樣：開頭沒意思，馬上就滑走了。</li>
        <li>大部分的人，在影片開始的前幾秒，就決定要不要看下去。開頭沒讓人停下來，後面寫得再好，也沒有人看到。</li>
        <li>所以開頭的任務是：<b>讓人停下來，想聽下去</b>。</li>
      </ul>
      <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-4 mt-4 text-lg">
        <p class="font-extrabold text-rose-700 m-0">好用的招：震撼事實開頭</p>
        <p class="mt-1 text-slate-700">用<b>讓人驚訝、想不到的事實</b>開場。你說完，別人會想：「真的嗎？」就會停下來。</p>
      </div>
      <p class="font-bold text-slate-700 mt-4 mb-1 text-lg">三種影片，開頭可以這樣寫：</p>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-lg">
          <tbody>
            <tr class="border-t border-slate-200"><td class="py-2 pr-4 font-bold text-rose-700 whitespace-nowrap">冷知識</td><td class="py-2 text-slate-800">你知道嗎？＿＿＿＿＿！</td></tr>
            <tr class="border-t border-slate-200"><td class="py-2 pr-4 font-bold text-rose-700 whitespace-nowrap">假資訊（謠言）</td><td class="py-2 text-slate-800">有人說：＿＿＿＿＿？　這是真的嗎？</td></tr>
            <tr class="border-t border-slate-200"><td class="py-2 pr-4 font-bold text-rose-700 whitespace-nowrap">事實釐清</td><td class="py-2 text-slate-800">很多人以為＿＿＿＿＿，其實＿＿＿＿＿！</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-2xl font-extrabold text-sky-700 m-0">② 主體（Body）：每一句只講一件事</p>
      <ul class="mt-3 space-y-1 text-lg text-slate-700 list-disc pl-6">
        <li>開頭之後，就是影片的內容。30～45 秒很短，<b>一次講太多重點，大家最後什麼都記不住</b>。</li>
        <li>所以<b>一句台詞，只講一件事</b>。</li>
      </ul>
      <p class="font-bold text-slate-700 mt-4 mb-2 text-lg">主體可以說這些：</p>
      <div class="flex flex-wrap gap-2 text-lg">
        <span class="bg-sky-100 border-2 border-sky-300 text-sky-800 rounded-full px-3 py-0.5 font-bold">背景</span>
        <span class="bg-sky-100 border-2 border-sky-300 text-sky-800 rounded-full px-3 py-0.5 font-bold">由來</span>
        <span class="bg-sky-100 border-2 border-sky-300 text-sky-800 rounded-full px-3 py-0.5 font-bold">查證的詳細內容</span>
        <span class="bg-sky-100 border-2 border-sky-300 text-sky-800 rounded-full px-3 py-0.5 font-bold">證據和佐證資料</span>
        <span class="bg-sky-100 border-2 border-sky-300 text-sky-800 rounded-full px-3 py-0.5 font-bold">步驟</span>
      </div>
      <p class="font-bold text-slate-700 mt-4 mb-2 text-lg">不知道怎麼開始寫，可以用這些句型：</p>
      <ul class="space-y-1 text-lg text-slate-800 list-disc pl-6">
        <li>＿＿＿最早是由＿＿＿＿＿……</li>
        <li>＿＿＿是出現在＿＿＿＿＿……</li>
        <li>＿＿＿是一種＿＿＿＿＿……</li>
        <li>網路上流傳＿＿＿＿＿，說＿＿＿＿＿……</li>
        <li>根據＿＿＿（來源），＿＿＿＿＿……</li>
        <li>其實＿＿＿＿＿，因為＿＿＿＿＿。</li>
      </ul>
    </div>

    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-2xl font-extrabold text-emerald-700 m-0">③ 行動呼籲（CTA）：影片最後，告訴大家可以做什麼 <span class="text-sm font-bold text-emerald-600">Call To Action</span></p>
      <p class="text-lg text-slate-700 mt-3">行動呼籲（CTA）的意思是「請大家行動」。影片不要說完就停了，最後用<b>一句話</b>告訴大家，看完可以做什麼。<b>一支影片，只放一個。</b></p>
      <ul class="mt-3 space-y-1 text-lg text-slate-800 list-disc pl-6">
        <li>下次遇到＿＿＿＿＿，不要／要＿＿＿＿＿。</li>
        <li>如果有人說＿＿＿＿＿，記得提醒他＿＿＿＿＿。</li>
        <li>分享出去，讓更多人知道！</li>
      </ul>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP_DEMO = '''
  <!-- ===== 步驟 3：看示範（三種可切換）===== -->
  <section class="step hidden" data-step="3">
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-violet-700 m-0">看示範：三種影片的台詞</h2>
      <p class="text-slate-600 mt-2 text-lg">老師用<b>自己想的題目</b>，各寫了一支 7 句的台詞。按下面的按鈕，換著看。每一句旁邊，寫了「這一句在做什麼」。你要寫的是<b>你自己的主題</b>，用自己的話寫。</p>
      <div id="demoTabs" class="flex flex-wrap gap-2 mt-4">
        <button type="button" data-demo="rumor" class="cute border-4 border-violet-300 bg-white text-violet-800 text-xl font-extrabold rounded-2xl px-6 py-2">假資訊</button>
        <button type="button" data-demo="fact" class="cute border-4 border-violet-300 bg-white text-violet-800 text-xl font-extrabold rounded-2xl px-6 py-2">冷知識</button>
        <button type="button" data-demo="clarify" class="cute border-4 border-violet-300 bg-white text-violet-800 text-xl font-extrabold rounded-2xl px-6 py-2">事實釐清</button>
      </div>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p id="demoTitle" class="cute text-xl font-extrabold text-violet-700 m-0"></p>
      <div class="overflow-x-auto mt-3">
        <table class="w-full text-left text-lg">
          <thead><tr class="text-slate-500 text-base"><th class="pb-1 pr-2">部分</th><th class="pb-1 pr-3">台詞（字幕）</th><th class="pb-1">這一句在做什麼</th></tr></thead>
          <tbody id="demoRows"></tbody>
        </table>
      </div>
      <p class="text-lg text-slate-700 mt-4">每句不超過 30 字，7 句，唸起來約 30 秒。</p>
    </div>
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-amber-700 m-0">寫完檢查：有內容，不囉嗦</p>
      <p class="text-lg text-slate-700 mt-2">知識性的影片，句子可以比較正式、有知識，例如「章魚有三顆心臟，各自負責不同的血液循環。」這樣就很好。要避免的是<b>太長，又沒講到內容</b>。</p>
      <div class="grid md:grid-cols-2 gap-3 mt-3 text-lg">
        <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-3"><b class="text-rose-700">太長、沒內容</b><br>章魚這種動物，其實真的是非常非常特別，牠的身體裡也有很多很有趣的地方喔。</div>
        <div class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-3"><b class="text-emerald-700">有內容、說得短</b><br>章魚有三顆心臟，各管不同的地方。</div>
      </div>
      <p class="text-lg text-slate-700 mt-3">寫完問自己：<b>這一句，有沒有告訴大家一個資訊？</b>　<b>哪些字可以拿掉？</b></p>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP_AI = '''
  <!-- ===== 步驟 3：直接對 Gem 說「開始寫台詞」 ===== -->
  <section class="step hidden" data-step="3">
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-violet-700 m-0">請 AI 教練用問題帶你寫台詞</h2>
      <p class="text-slate-600 mt-2 text-lg">AI 教練<b>不會直接寫給你</b>。它會<b>一次問你一個問題</b>，你回答，再自己把答案寫成一句台詞。就像剛剛老師的範例。</p>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-violet-700 m-0">怎麼開始</p>
      <ol class="mt-2 space-y-2 text-lg text-slate-700 list-decimal pl-6">
        <li>按下面的「開啟台詞小教練」。</li>
        <li>對它說：<b class="bg-violet-100 border-2 border-violet-300 rounded-lg px-2 py-0.5">開始寫台詞</b></li>
        <li><b>把你自己找到的資料給它</b>：貼上來源網址，或貼上你整理的重點（3～5 句）。它會先讀一遍，再問你想講什麼。</li>
        <li>照它的問題一題一題回答，自己把答案說成一句短短的台詞。</li>
        <li>全部寫完，它會給你一張<b>完整的台詞表</b>。下一步照著填進學習單的「台詞表」。</li>
      </ol>
      <div class="flex gap-2 flex-wrap mt-4 items-center">
        <span data-set-show="scriptGemUrl" class="hidden"><a data-set-href="scriptGemUrl" target="_blank" rel="noopener" class="cute inline-block bg-violet-600 hover:bg-violet-700 text-white text-xl font-extrabold rounded-2xl px-6 py-3">開啟台詞小教練 ↗</a></span>
        <button type="button" id="copyGo" class="bg-white border-2 border-violet-400 hover:bg-violet-50 text-violet-800 font-bold rounded-2xl px-5 py-2.5">複製「開始寫台詞」</button>
      </div>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-violet-700 m-0">怎麼和 AI 討論台詞</p>
      <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
        <li>先告訴它你的主題，貼上你找到的資料（來源網址或重點），再說你想對大家說什麼。</li>
        <li>它問你問題，你<b>一題一題回答</b>。答案是你的想法，不是它的。</li>
        <li>想到一句，貼給它看，問：「這一句有內容嗎？哪裡可以更短？」</li>
        <li>卡住了，可以請它「給我一個句型提示」。不要叫它「幫我寫」。</li>
        <li>它說的資料，要回到<b>來源網址</b>確認。AI 也可能說錯。</li>
        <li>最後的台詞，用<b>自己的話</b>寫。不要整句複製它的句子。</li>
      </ol>
      <p class="font-bold text-slate-700 mt-4 mb-2 text-lg">你可以這樣說：</p>
      <div class="flex flex-wrap gap-2 text-lg">
        <span class="bg-violet-50 border-2 border-violet-200 text-violet-800 rounded-xl px-3 py-1">「開始寫台詞」</span>
        <span class="bg-violet-50 border-2 border-violet-200 text-violet-800 rounded-xl px-3 py-1">「我想講的是……」</span>
        <span class="bg-violet-50 border-2 border-violet-200 text-violet-800 rounded-xl px-3 py-1">「這句太長了，怎麼變短？」</span>
        <span class="bg-violet-50 border-2 border-violet-200 text-violet-800 rounded-xl px-3 py-1">「我卡住了，給我一個句型提示」</span>
        <span class="bg-violet-50 border-2 border-violet-200 text-violet-800 rounded-xl px-3 py-1">「這一句有講到重點嗎？」</span>
      </div>
    </div>
    <div class="bg-amber-50 border-4 border-amber-200 rounded-3xl p-6 mb-5 text-lg">
      <p class="cute text-xl font-extrabold text-amber-700 m-0">不用 AI，或 AI 打不開：用句型卡</p>
      <ul class="mt-2 space-y-1 text-slate-700">
        <li><b>① 開頭（Hook）：</b>你知道嗎？＿＿＿＿＿！／有人說：＿＿＿＿＿？／很多人以為＿＿＿，其實＿＿＿！</li>
        <li><b>② 主體（Body）：</b>＿＿＿是一種＿＿＿。／＿＿＿最早是由＿＿＿。／其實＿＿＿，因為＿＿＿。</li>
        <li><b>③ 行動呼籲（CTA）：</b>下次遇到＿＿＿，要＿＿＿。／如果有人說＿＿＿，記得提醒他。</li>
      </ul>
    </div>
    <div data-set-admin="scriptGemUrl" class="hidden bg-slate-100 border-2 border-dashed border-slate-300 rounded-2xl p-4 mb-5">
      <p class="font-bold text-slate-600 text-sm">老師設定：台詞小教練（Gem）的分享網址（貼上並儲存，學生就會看到按鈕；不貼就不顯示）</p>
      <div class="flex gap-2 flex-wrap mt-2 items-center">
        <input type="url" data-set-input="scriptGemUrl" autocomplete="off" class="flex-1 min-w-[16rem] border-2 border-slate-300 rounded-xl px-3 py-2 text-base bg-white">
        <button type="button" data-set-save class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl px-4 py-2">儲存網址</button>
      </div>
      <p data-set-stat class="text-sm font-bold mt-2 min-h-[20px]"></p>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-violet-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="gem"></span></div>
      <div id="gemOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

# 台詞表：一開始 7 句（問題 2、解釋 3、結論 2），按「新增問題／解釋／結論」可以加句子（最多 12 句）；欄位由 build_L08 的 JS 產生
STEP_WRITE = '''
  <!-- ===== 步驟 4：寫下我的台詞 ===== -->
  <section class="step hidden" data-step="4">
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-emerald-700 m-0">寫下我的台詞</h2>
      <p class="text-slate-600 mt-2 text-lg">把你寫好的台詞，一句一句填進來。<b>至少 7 句，每句 30 字以內</b>，開頭、主體、行動呼籲（CTA）三個部分都要有。最上面也寫一個<b>影片標題</b>，等一下會跟著台詞一起複製進文件。字數超過會變紅色。</p>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-emerald-700 m-0">老師的台詞（示範：冷知識，7 句，約 30 秒）</p>
      <div class="overflow-x-auto mt-3">
        <table class="w-full text-left text-lg">
          <thead><tr class="text-slate-500 text-base"><th class="pb-1 pr-2">段</th><th class="pb-1">台詞（字幕）</th></tr></thead>
          <tbody>@@EXL@@</tbody>
        </table>
      </div>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-emerald-700 m-0">我的台詞表</p>
      <div class="bg-amber-50 border-2 border-amber-300 rounded-2xl p-4 mt-3">
        <p class="cute text-xl font-extrabold text-amber-800 m-0">斷句小提示：寫好一句，自己小聲唸唸看</p>
        <ul class="mt-2 space-y-1 text-lg text-slate-800 list-disc pl-6">
          <li>唸到<b>中間要換氣</b>，就在那裡斷開，後面的字換到<b>下一句</b>。</li>
          <li>一句<b>太長、唸得很喘</b>，也換到下一句。</li>
          <li>一句最多 30 字，而且只講一件事。</li>
        </ul>
        <p class="text-lg text-slate-700 mt-2 mb-0">例：「企鵝為了保暖，會擠成一團，還會輪流站到外面來。」唸到一半要換氣 → 拆成兩句：「企鵝為了保暖，會擠成一團。」「牠們還會輪流站到外面來。」</p>
      </div>
      <div class="mt-4">
        <label for="vtitle" class="cute text-lg font-extrabold text-emerald-700 block">我的影片標題</label>
        <input id="vtitle" data-k="vtitle" type="text" autocomplete="off" maxlength="30" class="fld ans mt-1 text-lg">
      </div>
      <div id="scriptRows" class="space-y-4 mt-5"></div>
      <div class="flex flex-wrap gap-2 mt-5">
        <button type="button" data-addseg="q" class="cute bg-rose-100 hover:bg-rose-200 border-2 border-rose-300 text-rose-800 text-lg font-extrabold rounded-2xl px-5 py-2">＋ 新增開頭</button>
        <button type="button" data-addseg="e" class="cute bg-sky-100 hover:bg-sky-200 border-2 border-sky-300 text-sky-800 text-lg font-extrabold rounded-2xl px-5 py-2">＋ 新增主體</button>
        <button type="button" data-addseg="c" class="cute bg-emerald-100 hover:bg-emerald-200 border-2 border-emerald-300 text-emerald-800 text-lg font-extrabold rounded-2xl px-5 py-2">＋ 新增行動呼籲（CTA）</button>
      </div>
      <p id="scriptCount" class="text-lg font-bold text-slate-700 mt-4"></p>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-emerald-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="write"></span></div>
      <div id="writeOpts" class="space-y-2 mt-3"></div>
    </div>
    @@SAVE@@
    <div class="stepnav"></div>
  </section>
'''.replace('@@EXL@@', EX_LINES_HTML).replace('@@SAVE@@', SAVE)

STEP_COPY = '''
  <!-- ===== 步驟 5：複製進老師給的文件 ===== -->
  <section class="step hidden" data-step="5">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">把台詞表放進文件</h2>
      <p class="text-slate-600 mt-2 text-lg">你填好的主題、影片標題和台詞，一次複製，貼進老師幫你開好的文件。每一句下面留了「關鍵字」，<b>下一步在文件裡寫</b>。</p>
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-sky-700 m-0">① 複製台詞表</p>
      <pre id="tplText" class="bg-slate-50 border-2 border-slate-200 rounded-2xl p-4 mt-3 text-base whitespace-pre-wrap max-h-72 overflow-y-auto"></pre>
      <button type="button" id="tplCopy" class="mt-3 w-full bg-sky-600 hover:bg-sky-700 text-white text-2xl font-extrabold rounded-2xl px-4 py-4">複製台詞表</button>
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-sky-700 m-0">② 貼進老師給你的文件</p>
      <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
        <li>打開老師給你的「台詞表」文件。</li>
        <li>在文件裡按 Ctrl+V，貼上。</li>
        <li>往下看一遍，每一句台詞都有貼進去。</li>
      </ol>
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-sky-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="doc"></span></div>
      <div id="docOpts" class="space-y-2 mt-3"></div>
    </div>
    @@SAVE@@
    <div class="stepnav"></div>
  </section>
'''.replace('@@SAVE@@', SAVE)

STEP_KW = '''
  <!-- ===== 步驟 6：在文件裡自己挑關鍵字 ===== -->
  <section class="step hidden" data-step="6">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700 m-0">在文件裡，自己挑每一句的關鍵字</h2>
      <p class="text-slate-600 mt-2 text-lg">台詞已經在文件裡了。回到文件，在每一句下面的「<b>關鍵字：</b>」後面，寫 1～2 個關鍵字。關鍵字是<b>搜尋圖片、影片要打的字</b>，下週找素材要用。畫面是你想的，所以<b>關鍵字自己挑</b>。</p>
      <div class="grid md:grid-cols-2 gap-3 mt-4 text-lg">
        <div class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-3"><b class="text-emerald-700">好找的</b><br>閃電、慢跑、草原、汽車、科學家</div>
        <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-3"><b class="text-rose-700">不好找的</b><br>意見不一樣、真正、關鍵（看不到畫面，換成能看到的東西）</div>
      </div>
      <p class="text-lg text-slate-700 mt-3">挑的時候問自己：<b>這一句，我想看到什麼畫面？</b></p>
    </div>
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-amber-700 m-0">老師的關鍵字</p>
      <div class="overflow-x-auto mt-3">
        <table class="w-full text-left text-lg">
          <thead><tr class="text-slate-500 text-base"><th class="pb-1 pr-2">段</th><th class="pb-1 pr-3">台詞（字幕）</th><th class="pb-1">關鍵字</th></tr></thead>
          <tbody>@@EXK@@</tbody>
        </table>
      </div>
    </div>
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-amber-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="kw"></span></div>
      <div id="kwOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''.replace('@@EXK@@', EX_KW_HTML)

CHOICES = {
    'tconf': {'opts': ['來源網址我點開看過，網頁上真的有寫', '開頭句是一個完整的句子', '核心訊息只有一句話、20 字內', '這個題目 30～45 秒說得完'], 'multi': True, 'block': True},
    'gem': {'opts': ['我打開台詞小教練，對它說了「開始寫台詞」', '我把來源網址或我找到的資料貼給它了', '我照它的問題一題一題回答', '每一句台詞，我自己用自己的話說出來'], 'multi': True, 'block': True},
    'write': {'opts': ['台詞寫了 7 句以上，每句 30 字內', '開頭、主體、行動呼籲（CTA）三個部分都有', '台詞都是我自己用自己的話寫的', '我全部唸過一遍，要換氣的地方都換到下一句了'], 'multi': True, 'block': True},
    'doc': {'opts': ['我按了「複製台詞表」', '我打開老師給的台詞表文件，貼上了', '我看過了，每一句台詞都在文件裡'], 'multi': True, 'block': True},
    'kw': {'opts': ['每一句下面都寫了 1～2 個關鍵字', '關鍵字是我自己挑的，看得到畫面', '關鍵字可以拿去搜尋圖片、影片'], 'multi': True, 'block': True},
}
QTYPES = {'tconf': 'experience', 'gem': 'experience', 'write': 'experience', 'doc': 'experience',
          'kw': 'experience', 'scriptAll': 'open'}

SPEC_SCRIPT = {'qid': 'scriptAll', 'prompt': '我的台詞表（每句台詞，依開頭、主體、CTA 排列）。', 'mode': 'checklist',
               'checks': [{'desc': '寫了 7 句以上，順序上有「開頭、主體、CTA」三個部分', 'pts': 4},
                          {'desc': '每句大約 30 字內（唸到要換氣或太長的地方有換到下一句），一句只講一件事，是說話的口氣，不是整段複製來源或課本式的句子', 'pts': 5},
                          {'desc': '內容跟他的主題與來源有關，沒有加入來源裡沒有的數字、人名或日期', 'pts': 4}]}
