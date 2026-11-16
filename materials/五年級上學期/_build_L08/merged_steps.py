# -*- coding: utf-8 -*-
# L08 的「寫台詞」部分（確認主題以後、Canva 以前）。由 build_L08.py 匯入。
# 老師規則：關鍵字學生自己選，AI 不幫忙；只有寫台詞 AI 可以協助，而且用提問引導；要給台詞撰寫範例。
# 2026-11-16 晚：文件由老師幫學生開；台詞、關鍵字改回在學習單裡填，填完按「複製台詞表」貼進老師給的文件。
ROWS = 8
SEG = {1: ('①', '問題', 'rose'), 2: ('①', '問題', 'rose'), 3: ('②', '解釋', 'sky'), 4: ('②', '解釋', 'sky'),
       5: ('②', '解釋', 'sky'), 6: ('②', '解釋', 'sky'), 7: ('③', '結論', 'emerald'), 8: ('③', '結論', 'emerald')}


def badge(i):
    n, name, tone = SEG[i]
    return ('<span class="shrink-0 inline-block bg-%s-100 border-2 border-%s-300 text-%s-800 rounded-full px-2.5 py-0.5 text-sm font-bold">%s%s　第 %d 句</span>'
            % (tone, tone, tone, n, name, i))


# 範例：老師的示範影片「打雷時用手機」（事實來自台灣事實查核中心查核報告 #1804）
# 每列：段、老師找到的資料、AI 教練會問的問題、老師寫的台詞、關鍵字
EX = [
    ('①', '網傳：打雷時用手機，會引來雷擊', '你想用什麼問題，讓大家想聽下去？', '有人說：打雷時用手機，會引來雷擊？', '雷電　閃電'),
    ('①', '（要讓大家想知道答案）', '再用一句話，把問題丟給大家。', '這是真的嗎？', '問號　疑問'),
    ('②', '專家指出藍芽耳機不是吸引閃電的關鍵', '專家怎麼說？', '專家說：藍芽耳機不是關鍵。', '慢跑　耳機'),
    ('②', '人在空曠的地方，比較容易被雷擊', '那真正危險的是什麼？', '真正危險的，是站在空曠的地方。', '空曠　草原　河堤'),
    ('②', '手機電磁波會不會引雷，學者意見不一致', '還有什麼是大家還不確定的？', '手機會不會引雷，專家意見不一樣。', '科學家　討論'),
    ('③', '雷雨時，不要待在空曠的戶外', '所以大家應該怎麼做？', '所以打雷時，別待在空曠的戶外。', '烏雲　戶外'),
    ('③', '可以進入室內或車內', '再提醒一個安全的地方。', '先躲進室內或車裡。', '房子　汽車　下雨'),
]
_TONE = {'①': 'rose', '②': 'sky', '③': 'emerald'}
EX_Q_HTML = ''.join(
    '<tr class="border-t border-slate-200 align-top"><td class="py-2 pr-2 font-bold text-%s-700">%s</td><td class="py-2 pr-3 text-slate-700">%s</td><td class="py-2 pr-3 text-violet-700">%s</td><td class="py-2 font-bold text-slate-900">%s</td></tr>'
    % (_TONE[g], g, d, q, s) for g, d, q, s, k in EX)
EX_LINES_HTML = ''.join(
    '<tr class="border-t border-slate-200"><td class="py-1.5 pr-2 font-bold text-%s-700">%s</td><td class="py-1.5 text-slate-900">%s</td></tr>'
    % (_TONE[g], g, s) for g, d, q, s, k in EX)
EX_KW_HTML = ''.join(
    '<tr class="border-t border-slate-200"><td class="py-1.5 pr-2 font-bold text-%s-700">%s</td><td class="py-1.5 pr-3">%s</td><td class="py-1.5 text-slate-700">%s</td></tr>'
    % (_TONE[g], g, s, k) for g, d, q, s, k in EX)

# 存起來／拿回我的台詞（兩節課、換電腦都能接著寫）
SAVE = '''<div class="bg-white border-4 border-emerald-200 rounded-3xl p-5 mb-5 shadow-sm">
      <p class="cute text-lg font-extrabold text-emerald-700 m-0">存起來，下次接著用</p>
      <p class="text-base text-slate-600 mt-1">先填好最上面的年級、班級、座號。換一台電腦、下一節課，都能拿回來。</p>
      <div class="flex gap-2 flex-wrap mt-2">
        <button type="button" data-script-save class="cute bg-emerald-600 hover:bg-emerald-700 text-white text-lg font-extrabold rounded-2xl px-5 py-2">存起來</button>
        <button type="button" data-script-load class="bg-white border-2 border-emerald-400 hover:bg-emerald-50 text-emerald-800 font-bold rounded-2xl px-5 py-2">拿回我存的台詞</button>
      </div>
      <p data-script-stat class="text-base font-bold mt-2 min-h-[24px]"></p>
    </div>'''

STEP_EXAMPLE = '''
  <!-- ===== 步驟 2：看台詞怎麼寫 ===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">看看台詞是怎麼寫出來的</h2>
      <p class="text-slate-600 mt-2 text-lg">台詞不是一次寫完，而是<b>一個問題、一句台詞</b>。下面是老師寫「打雷時用手機」的過程：先看<b>找到的資料</b>，回答一個<b>問題</b>，再把答案寫成<b>一句話</b>。</p>
      <div class="overflow-x-auto mt-4">
        <table class="w-full text-left text-lg">
          <thead><tr class="text-slate-500 text-base"><th class="pb-1 pr-2">段</th><th class="pb-1 pr-3">我找到的資料</th><th class="pb-1 pr-3">問題</th><th class="pb-1">我寫的台詞</th></tr></thead>
          <tbody>@@EXQ@@</tbody>
        </table>
      </div>
    </div>
    <div class="grid md:grid-cols-3 gap-4 mb-5">
      <div class="bg-rose-50 border-4 border-rose-200 rounded-3xl p-5 text-lg"><p class="cute text-xl font-extrabold text-rose-700 m-0">① 問題</p><p class="mt-1 text-slate-700">把問題或謠言說出來，讓人想聽下去。1～2 句。</p></div>
      <div class="bg-sky-50 border-4 border-sky-200 rounded-3xl p-5 text-lg"><p class="cute text-xl font-extrabold text-sky-700 m-0">② 解釋</p><p class="mt-1 text-slate-700">說資料怎麼說、原因和依據。3～4 句，一句只講一件事。</p></div>
      <div class="bg-emerald-50 border-4 border-emerald-200 rounded-3xl p-5 text-lg"><p class="cute text-xl font-extrabold text-emerald-700 m-0">③ 結論</p><p class="mt-1 text-slate-700">說正確的是什麼，我們該怎麼做。1～2 句。</p></div>
    </div>
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-amber-700 m-0">寫完先改短、改成說話</p>
      <div class="grid md:grid-cols-2 gap-3 mt-3 text-lg">
        <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-3"><b class="text-rose-700">太長、像課本</b><br>專家表示藍芽耳機並非吸引閃電之關鍵因素。（20 字以上）</div>
        <div class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-3"><b class="text-emerald-700">改成說話</b><br>專家說：藍芽耳機不是關鍵。（13 字）</div>
      </div>
      <p class="text-lg text-slate-700 mt-3">改的時候問自己：<b>哪個字可以拿掉？</b>　<b>講給同學聽，會怎麼說？</b></p>
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-sky-700 m-0">我看懂了</p><span class="qtypeSlot" data-qid="ex"></span></div>
      <div id="exOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''.replace('@@EXQ@@', EX_Q_HTML)

STEP_AI = '''
  <!-- ===== 步驟 3：寫下資料，請 AI 用問題帶你寫台詞 ===== -->
  <section class="step hidden" data-step="3">
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-violet-700 m-0">寫下資料，請 AI 用問題帶你寫台詞</h2>
      <p class="text-slate-600 mt-2 text-lg">AI 教練<b>不會直接寫給你</b>。它會<b>一次問你一個問題</b>，你回答，再自己把答案寫成一句台詞。就像剛剛老師的範例。</p>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <label for="mat3" class="cute text-xl font-extrabold text-violet-700">① 我從來源找到的資料（3～5 句，用自己的話寫）</label>
      <textarea id="mat3" data-k="mat3" rows="5" class="fld ans mt-2 text-lg"></textarea>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-violet-700 m-0">② 複製這段，貼給 AI 教練</p>
      <pre id="aiMsg" class="bg-slate-50 border-2 border-slate-200 rounded-2xl p-4 mt-3 text-base whitespace-pre-wrap"></pre>
      <div class="flex gap-2 flex-wrap mt-3 items-center">
        <button type="button" id="copyAI" class="cute bg-violet-600 hover:bg-violet-700 text-white text-lg font-extrabold rounded-2xl px-5 py-2">複製</button>
        <span data-set-show="scriptGemUrl" class="hidden"><a data-set-href="scriptGemUrl" target="_blank" rel="noopener" class="cute inline-block bg-white border-2 border-violet-400 text-violet-800 text-lg font-extrabold rounded-2xl px-5 py-2">開啟台詞小教練 ↗</a></span>
      </div>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-violet-700 m-0">AI 教練會怎麼幫你</p>
      <ul class="mt-2 space-y-1 text-lg text-slate-700 list-disc pl-6">
        <li>先問你要用什麼問題開頭，再一段一段問：資料怎麼說？原因是什麼？所以該怎麼做？</li>
        <li>你回答後，<b>自己</b>把答案寫成一句 20 字內的台詞。下一步把台詞填進來。</li>
        <li>太長、太難、不像說話，它會問你「哪個字可以拿掉？」「講給同學聽會怎麼說？」，由你來改。</li>
        <li>你卡住了，它會給你一個句型提示，還是由你寫完。</li>
        <li>資料裡沒有的數字、人名、日期，不要加。它會問你「資料裡有寫嗎？」</li>
        <li>關鍵字它不幫你選，之後你自己挑。</li>
      </ul>
    </div>
    <div class="bg-amber-50 border-4 border-amber-200 rounded-3xl p-6 mb-5 text-lg">
      <p class="cute text-xl font-extrabold text-amber-700 m-0">不用 AI，或 AI 打不開：用句型卡</p>
      <ul class="mt-2 space-y-1 text-slate-700">
        <li><b>① 問題：</b>最近有人說：＿＿＿＿＿？</li>
        <li><b>② 解釋：</b>但其實：＿＿＿＿＿。因為＿＿＿＿＿。</li>
        <li><b>③ 結論：</b>所以正確的是：＿＿＿＿＿。提醒大家：＿＿＿＿＿。</li>
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
    @@SAVE@@
    <div class="stepnav"></div>
  </section>
'''.replace('@@SAVE@@', SAVE)

_ROWS_WRITE = ''.join(
    '<div class="flex items-start gap-2 flex-wrap">%s<div class="flex-1 min-w-[14rem]">'
    '<input id="s%d" data-k="s%d" type="text" autocomplete="off" maxlength="40" class="fld ans text-lg">'
    '<p class="text-sm text-slate-500 mt-0.5"><span data-count="s%d">0</span> / 20 字</p></div></div>'
    % (badge(i), i, i, i) for i in range(1, ROWS + 1))

STEP_WRITE = '''
  <!-- ===== 步驟 4：寫下我的台詞 ===== -->
  <section class="step hidden" data-step="4">
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-emerald-700 m-0">寫下我的台詞</h2>
      <p class="text-slate-600 mt-2 text-lg">把你寫好的台詞，一句一句填進來。<b>寫 7～8 句，每句 20 字以內</b>，三段都要有。字數超過會變紅色。</p>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-emerald-700 m-0">老師的台詞（7 句，整支影片約 30 秒）</p>
      <div class="overflow-x-auto mt-3">
        <table class="w-full text-left text-lg">
          <thead><tr class="text-slate-500 text-base"><th class="pb-1 pr-2">段</th><th class="pb-1">台詞（字幕）</th></tr></thead>
          <tbody>@@EXL@@</tbody>
        </table>
      </div>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm space-y-4">
      <p class="cute text-xl font-extrabold text-emerald-700 m-0">我的台詞表</p>
      @@ROWS@@
      <p id="scriptCount" class="text-lg font-bold text-slate-700"></p>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-emerald-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="write"></span></div>
      <div id="writeOpts" class="space-y-2 mt-3"></div>
    </div>
    @@SAVE@@
    <div class="stepnav"></div>
  </section>
'''.replace('@@EXL@@', EX_LINES_HTML).replace('@@ROWS@@', _ROWS_WRITE).replace('@@SAVE@@', SAVE)

_ROWS_KW = ''.join(
    '<div class="flex items-start gap-2 flex-wrap">%s<div class="flex-1 min-w-[14rem]"><p class="text-lg text-slate-800 font-bold" data-echo="s%d"></p>'
    '<input id="k%d" data-k="k%d" type="text" autocomplete="off" maxlength="40" class="fld ans mt-1 text-lg"></div></div>'
    % (badge(i), i, i, i) for i in range(1, ROWS + 1))

STEP_KW = '''
  <!-- ===== 步驟 5：自己挑關鍵字 ===== -->
  <section class="step hidden" data-step="5">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700 m-0">自己挑每一句的關鍵字</h2>
      <p class="text-slate-600 mt-2 text-lg">關鍵字是<b>搜尋圖片、影片要打的字</b>，等一下要用它找素材。畫面是你想的，所以<b>關鍵字自己挑</b>。每句 1～2 個。</p>
      <div class="grid md:grid-cols-2 gap-3 mt-4 text-lg">
        <div class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-3"><b class="text-emerald-700">好找的</b><br>閃電、慢跑、草原、汽車、科學家</div>
        <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-3"><b class="text-rose-700">不好找的</b><br>意見不一樣、真正、關鍵（看不到畫面，換成能看到的東西）</div>
      </div>
      <p class="text-lg text-slate-700 mt-3">挑的時候問自己：<b>這一句，我想看到什麼畫面？</b>　搜不到，就換一個詞，或試試英文，例如 jogging、lightning。</p>
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
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm space-y-4">
      <p class="cute text-xl font-extrabold text-amber-700 m-0">我的關鍵字</p>
      @@ROWS@@
    </div>
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-amber-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="kw"></span></div>
      <div id="kwOpts" class="space-y-2 mt-3"></div>
    </div>
    @@SAVE@@
    <div class="stepnav"></div>
  </section>
'''.replace('@@EXK@@', EX_KW_HTML).replace('@@ROWS@@', _ROWS_KW).replace('@@SAVE@@', SAVE)

STEP_COPY = '''
  <!-- ===== 步驟 6：複製進老師給的文件 ===== -->
  <section class="step hidden" data-step="6">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">把台詞表放進文件</h2>
      <p class="text-slate-600 mt-2 text-lg">你填好的主題、資料、台詞、關鍵字，一次複製，貼進老師幫你開好的文件。</p>
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
        <li>往下看一遍，每一句和關鍵字都有貼進去。</li>
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

CHOICES = {
    'tconf': {'opts': ['來源網址我點開看過，網頁上真的有寫', '開頭句是一個完整的句子', '核心訊息只有一句話、20 字內', '這個題目 30～45 秒說得完'], 'multi': True, 'block': True},
    'ex': {'opts': ['台詞是「先回答一個問題，再寫成一句話」', '每句 20 字內，像在說話', '寫完要改短、改成自己會說的話'], 'multi': True},
    'write': {'opts': ['台詞寫了 7 句以上，每句 20 字內', '三段都有：問題、解釋、結論', '台詞都是我自己用自己的話寫的', '我全部唸過一遍，像在說話'], 'multi': True, 'block': True},
    'kw': {'opts': ['每一句都有 1～2 個關鍵字', '關鍵字是我自己挑的，看得到畫面', '搜不到的關鍵字我會自己換'], 'multi': True, 'block': True},
    'doc': {'opts': ['我按了「複製台詞表」', '我打開老師給的台詞表文件，貼上了', '我看過了，每一句和關鍵字都在文件裡'], 'multi': True, 'block': True},
}
QTYPES = {'tconf': 'experience', 'ex': 'experience', 'write': 'experience', 'kw': 'experience', 'doc': 'experience',
          'scriptAll': 'open'}

SPEC_SCRIPT = {'qid': 'scriptAll', 'prompt': '我的台詞表（每句台詞和它的關鍵字）。', 'mode': 'checklist',
               'checks': [{'desc': '寫了 7 句以上，順序上有「問題或謠言、解釋、結論」三段', 'pts': 3},
                          {'desc': '每句大約 20 字內，一句只講一件事，是說話的口氣，不是整段複製來源或課本式的句子', 'pts': 4},
                          {'desc': '內容跟他的主題與來源有關，沒有加入來源裡沒有的數字、人名或日期', 'pts': 3},
                          {'desc': '每句都有 1～2 個關鍵字，是搜得到畫面的具體詞，不是「真正」「意見不一樣」這類看不到的詞', 'pts': 5}]}
