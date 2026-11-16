# -*- coding: utf-8 -*-
# 產生五上 L08「寫台詞、做字幕、挑關鍵字」學習單（找素材移到 L09，草稿在 L09_找素材步驟_草稿.html）。
# 2026-11-10 老師：台詞不要寫在學習單裡，學生自己開 Google 文件整理 → 學習單只放引導（步驟、範例、勾選、複製鈕），
# 台詞表在 Classroom 作業的文件裡，老師用「匯入 Classroom 文件」讀（規範 §3-d）。
# 骨架直接取自「目前的」L06 學習單（識別列、教師列、進度列、Firebase、靠椅子關卡、步驟卡），
# 只換：標題、步驟內容、題目設定（C）、本節專屬的 JS（hooks）、評分設定。
# ⚠ 不要用 _build_L05_L06/build.py（行號已過時，重建會把 L05、L06 弄壞）。
# 生成後：
#   python 引導規範/chair-gate/inject.py <本節 html>
#   python 引導規範/stepcards/inject.py <本節 html>
#   python 引導規範/game-portal/check.py <本節 html>
import io, json, os, re, shutil, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # materials/五年級上學期
SKEL = os.path.join(ROOT, 'L06_Docs查證文件二', '五上_L06_Docs查證文件二.html')
OUTDIR = os.path.join(ROOT, 'L08_寫台詞與挑關鍵字')
OUT = os.path.join(OUTDIR, '五上_L08_寫台詞與挑關鍵字.html')

PORTAL = 'https://boyinslps.github.io/pcclass/games/'
ROWS = 8                       # 台詞 8 句：① 2 句、② 4 句、③ 2 句（至少寫 7 句）
SEG = {1: ('①', '問題'), 2: ('①', '問題'), 3: ('②', '解釋'), 4: ('②', '解釋'), 5: ('②', '解釋'), 6: ('②', '解釋'),
       7: ('③', '結論'), 8: ('③', '結論')}

# 「繳交」操作影片沿用 L07/L06 的（Classroom 按繳交）
os.makedirs(os.path.join(OUTDIR, 'assets'), exist_ok=True)
for n in ('教學_繳交.mp4', '教學_繳交_封面.jpg'):
    src = os.path.join(ROOT, 'L07_補排版與找主題', 'assets', n)
    dst = os.path.join(OUTDIR, 'assets', n)
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy2(src, dst)

# ---------- 貼進文件的台詞表（純文字，跟 L06 的「複製欄位」同一種做法） ----------
TPL = ['我的台詞表', '我的主題：', '我找到的資料（3～5 句，用自己的話）：', '']
for i in range(1, ROWS + 1):
    TPL += ['第 %d 句（%s%s）：' % (i, SEG[i][0], SEG[i][1]), '關鍵字：', '']
TPL_TEXT = '\n'.join(TPL).rstrip('\n')

# ---------- 範例：老師的示範影片「打雷時用手機」 ----------
EX = [
    ('有人說：打雷時用手機，會引來雷擊？', '雷電　閃電', 'Canva 影片：雷電閃電'),
    ('這是真的嗎？', '問號　疑問', 'Canva 圖片：問號'),
    ('專家說：藍芽耳機不是關鍵。', '慢跑　耳機', 'Canva 影片：慢跑'),
    ('真正危險的，是站在空曠的地方。', '空曠　草原　河堤', 'Canva 影片：草原'),
    ('手機會不會引雷，專家意見不一樣。', '科學家　討論', 'Canva 圖片：科學家'),
    ('所以打雷時，別待在空曠的戶外。', '烏雲　戶外', 'Canva 影片：烏雲'),
    ('先躲進室內或車裡。', '房子　汽車　下雨', 'Canva 影片：汽車雨刷'),
]
EX_SEG = ['①', '①', '②', '②', '②', '③', '③']
EX_TONE = {'①': 'rose', '②': 'sky', '③': 'emerald'}
EX_HTML = ''.join(
    '<tr class="border-t border-slate-200"><td class="py-1.5 pr-2 font-bold text-%s-700">%s</td><td class="py-1.5 pr-3">%s</td><td class="py-1.5 text-slate-700">%s</td></tr>'
    % (EX_TONE[EX_SEG[i]], EX_SEG[i], s, k) for i, (s, k, m) in enumerate(EX))

STEP1 = '''
  <!-- ===== 步驟 1：拿回主題 ===== -->
  <section class="step" data-step="1">
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-emerald-700 m-0">先拿回你的主題</h2>
      <p class="text-slate-600 mt-2 text-lg">上一節你選好了題目。先填好最上面的年級、班級、座號，再按「拿回我的主題」。接下來要寫的東西，都寫在你自己的 Google 文件裡。</p>
      <div class="flex gap-2 flex-wrap mt-3">
        <button type="button" id="topicLoad" class="cute bg-emerald-600 hover:bg-emerald-700 text-white text-lg font-extrabold rounded-2xl px-5 py-2">拿回我的主題</button>
      </div>
      <p id="topicStat" class="text-base font-bold mt-3 min-h-[24px]"></p>
    </div>
    <div id="topicCard" class="hidden bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm space-y-3 text-lg">
      <p><b class="text-emerald-700">類型：</b><span id="tCat"></span></p>
      <p><b class="text-emerald-700">開頭句：</b><span id="tHook"></span></p>
      <p><b class="text-emerald-700">來源網址：</b><span id="tSrc" class="break-all"></span></p>
      <p><b class="text-emerald-700">核心訊息：</b><span id="tCore"></span></p>
      <div class="flex gap-2 flex-wrap pt-1">
        <button type="button" id="topicCopy" class="cute bg-emerald-600 hover:bg-emerald-700 text-white text-lg font-extrabold rounded-2xl px-5 py-2">複製我的主題</button>
        <a id="srcLink" target="_blank" rel="noopener" class="hidden inline-block bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2">點開來源，再看一遍 ↗</a>
      </div>
    </div>
    <div class="bg-amber-50 border-4 border-amber-200 rounded-3xl p-5 mb-5 text-lg">
      <p class="cute text-xl font-extrabold text-amber-700 m-0">上一節沒存到？</p>
      <p class="mt-1 text-slate-700">沒關係，打開你的查證文件，把「查核網址」「我選的訊息」找出來，下一步在新文件裡重寫一次。</p>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP2 = '''
  <!-- ===== 步驟 2：開文件 ===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">打開你的台詞表文件</h2>
      <div class="bg-rose-50 border-4 border-rose-300 rounded-2xl p-4 mt-3 text-lg">
        <p class="font-extrabold text-rose-700 m-0">一定要從 Classroom 作業裡開文件</p>
        <p class="mt-1 text-slate-700">到 Classroom，打開這一節的作業，點作業裡的「台詞表」文件。自己另外開的新文件，老師看不到。</p>
      </div>
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-sky-700 m-0">把台詞表貼進文件</p>
      <p class="text-lg text-slate-700 mt-2">按「複製台詞表」，到文件按 Ctrl+V 貼上。貼上後，再把剛剛複製的「我的主題」貼在「我的主題：」下面。</p>
      <pre id="tplText" class="bg-slate-50 border-2 border-slate-200 rounded-2xl p-4 mt-3 text-base whitespace-pre-wrap max-h-72 overflow-y-auto"></pre>
      <button type="button" id="tplCopy" class="mt-3 w-full bg-sky-600 hover:bg-sky-700 text-white text-2xl font-extrabold rounded-2xl px-4 py-4">複製台詞表</button>
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-sky-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="doc"></span></div>
      <div id="docOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP3 = '''
  <!-- ===== 步驟 3：請 AI 幫忙想台詞 ===== -->
  <section class="step hidden" data-step="3">
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-violet-700 m-0">請 AI 幫你想台詞</h2>
      <p class="text-slate-600 mt-2 text-lg">AI 只能用<b>你給它的資料</b>。先在文件的「我找到的資料」寫 3～5 句重點，用自己的話寫。</p>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-violet-700 m-0">複製這段，貼給 AI</p>
      <p class="text-lg text-slate-700 mt-2">貼上後，把「（把你在文件寫的資料貼在這裡）」換成你寫的資料。</p>
      <pre id="aiMsg" class="bg-slate-50 border-2 border-slate-200 rounded-2xl p-4 mt-3 text-base whitespace-pre-wrap"></pre>
      <div class="flex gap-2 flex-wrap mt-3 items-center">
        <button type="button" id="copyAI" class="cute bg-violet-600 hover:bg-violet-700 text-white text-lg font-extrabold rounded-2xl px-5 py-2">複製</button>
        <span data-set-show="scriptGemUrl" class="hidden"><a data-set-href="scriptGemUrl" target="_blank" rel="noopener" class="cute inline-block bg-white border-2 border-violet-400 text-violet-800 text-lg font-extrabold rounded-2xl px-5 py-2">開啟寫台詞小幫手 ↗</a></span>
      </div>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-violet-700 m-0">AI 會給 3 個版本</p>
      <ul class="mt-2 space-y-1 text-lg text-slate-700 list-disc pl-6">
        <li>挑 1 個你最喜歡的，貼進文件的台詞表。</li>
        <li><b>至少自己改一個地方</b>，用你自己的話。</li>
        <li>每句 20 字以內，說不完就請 AI「更短」。</li>
        <li>AI 寫了你沒給的數字、人名、日期，就刪掉，或回去查來源。</li>
        <li>AI 給的句子設成<b class="text-rose-600">紅字</b>，你改過或自己寫的設成<b class="text-sky-700">藍字</b>。</li>
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
      <p class="font-bold text-slate-600 text-sm">老師設定：寫台詞小幫手（Gem）的分享網址（貼上並儲存，學生就會看到按鈕；不貼就不顯示）</p>
      <div class="flex gap-2 flex-wrap mt-2 items-center">
        <input type="url" data-set-input="scriptGemUrl" autocomplete="off" class="flex-1 min-w-[16rem] border-2 border-slate-300 rounded-xl px-3 py-2 text-base bg-white">
        <button type="button" data-set-save class="bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl px-4 py-2">儲存網址</button>
      </div>
      <p data-set-stat class="text-sm font-bold mt-2 min-h-[20px]"></p>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP4 = '''
  <!-- ===== 步驟 4：整理台詞 ===== -->
  <section class="step hidden" data-step="4">
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-emerald-700 m-0">在文件裡整理台詞</h2>
      <p class="text-slate-600 mt-2 text-lg">把挑好的台詞，一句一句填進文件的「第 1 句」到「第 8 句」。<b>寫 7～8 句，每句 20 字以內</b>。先看老師的台詞表。下一步要把它們放進 Canva。</p>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-emerald-700 m-0">老師的「打雷時用手機」台詞表</p>
      <div class="overflow-x-auto mt-3">
        <table class="w-full text-left text-lg">
          <thead><tr class="text-slate-500 text-base"><th class="pb-1 pr-2">段</th><th class="pb-1 pr-3">台詞（字幕）</th><th class="pb-1">關鍵字</th></tr></thead>
          <tbody>@@EX@@</tbody>
        </table>
      </div>
      <div class="grid md:grid-cols-3 gap-3 mt-4 text-lg">
        <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-3"><b class="text-rose-700">① 問題</b><br>把問題或謠言說出來。</div>
        <div class="bg-sky-50 border-2 border-sky-200 rounded-2xl p-3"><b class="text-sky-700">② 解釋</b><br>說原因和依據。</div>
        <div class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-3"><b class="text-emerald-700">③ 結論</b><br>說正確的是什麼，我們該怎麼做。</div>
      </div>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-emerald-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="write"></span></div>
      <div id="writeOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''.replace('@@EX@@', EX_HTML)

STEP5 = '''
  <!-- ===== 步驟 5：把台詞放進 Canva 影片 ===== -->
  <section class="step hidden" data-step="5">
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-rose-700 m-0">把台詞放進 Canva 影片</h2>
      <p class="text-slate-600 mt-2 text-lg">Canva 的影片像<b>會動的簡報</b>：<b>一頁就是一個畫面</b>。我們讓<b>每一句台詞一頁</b>，先把字幕放好，再照著字幕找素材。</p>
    </div>
    <div class="grid md:grid-cols-3 gap-4 mb-5">
      <div class="bg-white border-4 border-rose-300 rounded-3xl p-5 shadow-sm">
        <p class="cute text-xl font-extrabold text-rose-700 m-0">① 建立影片</p>
        <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
          <li>打開 Canva，按「建立設計」。</li>
          <li>搜尋「影片」，選影片。</li>
          <li>把名字改成「我的解說影片」。</li>
        </ol>
      </div>
      <div class="bg-white border-4 border-rose-300 rounded-3xl p-5 shadow-sm">
        <p class="cute text-xl font-extrabold text-rose-700 m-0">② 一句一頁</p>
        <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
          <li>頁面下方按「新增頁面」。</li>
          <li><b>頁數和台詞句數一樣</b>，7～8 頁。</li>
          <li>想要開頭大字，就在最前面多加一頁放題目（選做）。</li>
        </ol>
      </div>
      <div class="bg-white border-4 border-rose-300 rounded-3xl p-5 shadow-sm">
        <p class="cute text-xl font-extrabold text-rose-700 m-0">③ 打字幕</p>
        <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
          <li>左邊選「文字」，新增一個文字方塊。</li>
          <li>回文件複製這一句，貼進文字方塊。</li>
          <li>字要夠大、顏色和背景分得開，放在畫面下面。</li>
          <li><b>每一頁</b>字型、大小、位置都一樣。</li>
        </ol>
      </div>
    </div>
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-rose-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="canva"></span></div>
      <div id="canvaOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP6 = '''
  <!-- ===== 步驟 6：文字特效 ===== -->
  <section class="step hidden" data-step="6">
    <div class="bg-white border-4 border-fuchsia-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-fuchsia-700 m-0">讓字幕動起來</h2>
      <p class="text-slate-600 mt-2 text-lg">文字特效就是字出現的方式。挑<b>一種</b>，每一頁的字幕都用它，影片才會整齊。</p>
    </div>
    <div class="bg-white border-4 border-fuchsia-300 rounded-3xl p-6 mb-5 shadow-sm">
      <ol class="space-y-2 text-lg text-slate-700 list-decimal pl-6">
        <li>點一下第 1 頁的字幕，選取它。</li>
        <li>按上方的「動畫」。</li>
        <li>選「文字」那一區，滑鼠移過去可以先看效果。</li>
        <li>點一下喜歡的，就套用了。可以試：<b>淡入</b>、<b>彈出</b>、<b>打字機</b>。</li>
        <li>速度選「中」，字幕才讀得完。</li>
        <li>第 2 頁到最後一頁，一頁一頁照做，<b>用同一種</b>。</li>
        <li>按「播放」，從頭看一遍。</li>
      </ol>
      <p class="text-lg text-slate-700 mt-3">不要每一句換不同的特效，也不要選太花、太慢的，看字幕比炫比較重要。</p>
    </div>
    <div class="bg-white border-4 border-fuchsia-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-fuchsia-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="fx"></span></div>
      <div id="fxOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP7 = '''
  <!-- ===== 步驟 7：挑關鍵字 ===== -->
  <section class="step hidden" data-step="7">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700 m-0">每句挑 1～2 個關鍵字</h2>
      <p class="text-slate-600 mt-2 text-lg">字幕放好了，接著想每一句要配什麼畫面。關鍵字是<b>搜尋圖片、影片要打的字</b>，下一節就用它找素材。挑「看得到畫面」的名詞或動作，寫在文件每一句下面的「關鍵字：」。</p>
      <div class="grid md:grid-cols-2 gap-3 mt-4 text-lg">
        <div class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-3"><b class="text-emerald-700">好找的</b><br>閃電、慢跑、草原、汽車、科學家</div>
        <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-3"><b class="text-rose-700">不好找的</b><br>意見不一樣、真正、關鍵（看不到畫面，換成能看到的東西）</div>
      </div>
      <p class="text-lg text-slate-700 mt-3">例：「專家說：藍芽耳機不是關鍵。」→ 關鍵字：<b>慢跑　耳機</b>。搜不到，就試試英文，例如 jogging、lightning。</p>
    </div>
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-amber-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="kw"></span></div>
      <div id="kwOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP8 = '''
  <!-- ===== 步驟 8：繳交 ===== -->
  <section class="step hidden" data-step="8">
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-indigo-700">繳交前自己檢查</h2>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="chk"></span></div>
      <div id="chkOpts" class="space-y-2 mt-3"></div>
      <div class="bg-indigo-50 border-2 border-indigo-200 rounded-2xl p-4 mt-4 text-lg text-slate-700">
        <p class="font-bold text-indigo-800">台詞表文件寫好了：</p>
        <p class="mt-1">回 <b>Classroom 作業</b>，確認文件<b>附在作業裡</b>，按<b>「繳交」</b>。</p>
      </div>
      <p class="font-bold text-indigo-800 mt-5 mb-2">看影片：怎麼在 Classroom 繳交</p>
      <video class="w-full max-w-[560px] mx-auto rounded-2xl bg-slate-900" src="assets/教學_繳交.mp4" poster="assets/教學_繳交_封面.jpg" controls playsinline preload="none"></video><p class="text-[11px] text-slate-400 mt-1 text-center">回 Classroom 分頁，按「繳交」，再按一次確認</p>
    </div>
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-5 shadow-sm text-center mt-6">
      <h2 class="cute text-xl font-extrabold text-indigo-700 mb-1">繳交學習單</h2>
      <p class="text-sm text-slate-500 mb-3">確定都填好了嗎？按下面按鈕交給老師（可以重交，會覆蓋前一次）。</p>
      <button id="submitBtn" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white cute text-xl font-extrabold rounded-2xl py-3">繳交學習單</button>
      <p id="submitStat" class="text-sm font-bold mt-3 min-h-[20px]"></p>
    </div>

    <div id="rewardBox" class="hidden text-center bg-gradient-to-b from-indigo-100 to-sky-100 border-4 border-indigo-300 rounded-3xl p-7 mt-6">
      <div class="text-6xl mb-2 pop"></div>
      <h2 class="cute text-3xl font-extrabold text-indigo-700">恭喜你已經做完今日的作業，可以遊玩！</h2>
      <div class="flex flex-wrap gap-3 justify-center mt-4">
        <a href="@@PORTAL@@" target="_blank" rel="noopener" class="cute inline-block bg-indigo-600 hover:bg-indigo-700 text-white text-2xl font-extrabold rounded-2xl px-10 py-4">電腦教室遊戲網站</a>
      </div>
    </div>
    <div class="stepnav"></div>
  </section>
'''.replace('@@PORTAL@@', PORTAL)

BODY = '\n' + ''.join([STEP1, STEP2, STEP3, STEP4, STEP5, STEP6, STEP7, STEP8]) + '\n'

CFG = {
    'ws': 'g5-L08', 'lessonPath': 'g5/L08', 'title': '寫台詞、做字幕、挑關鍵字', 'stateKey': 'g5L08flow',
    'steps': ['拿回主題', '開文件', '請 AI 想', '整理台詞', '輸入字幕', '文字特效', '挑關鍵字', '繳交'],
    'reveals': [], 'revealOf': {}, 'autoFb': [], 'textSettings': ['scriptGemUrl'],
    'qtypes': {'doc': 'experience', 'write': 'experience', 'canva': 'experience', 'fx': 'experience', 'kw': 'experience', 'chk': 'experience'},
    'choices': {
        'doc': {'opts': ['我是從 Classroom 作業打開文件的', '我把台詞表貼進文件了', '我把我的主題貼進文件了'], 'multi': True, 'block': True},
        'write': {'opts': ['台詞寫了 7 句以上，每句 20 字內', '三段都有：問題、解釋、結論', '至少有一句是我改過或自己寫的', 'AI 給的句子是紅字，我改的是藍字'], 'multi': True, 'block': True},
        'kw': {'opts': ['每一句都寫了 1～2 個關鍵字', '關鍵字是看得到畫面的詞'], 'multi': True, 'block': True},
        'canva': {'opts': ['我建立了影片設計，名字是「我的解說影片」', '頁數和台詞句數一樣，每頁一句', '每頁字幕都貼好了，看得清楚', '每頁字幕的字型、大小、位置一樣'], 'multi': True, 'block': True},
        'fx': {'opts': ['每一頁字幕都有文字特效，而且是同一種', '我按播放從頭看過，字幕讀得完'], 'multi': True, 'block': True},
        'chk': {'opts': ['台詞寫了 7 句以上，每句 20 字內', '每一句都有關鍵字', 'Canva 影片每句一頁，字幕和文字特效都做好了', '文件附在 Classroom 作業裡，我按了「繳交」'], 'multi': True, 'block': True},
    },
    'texts': [],
    'patterns': {},
    'openQtexts': {},
}

HOOKS = r'''
  H.stepDone=function(n){
    var a=function(k){return state[k]!=null&&(Array.isArray(state[k])?state[k].length>0:filled(state[k]));};
    if(n===1)return filled(state.core)&&n!==curStep;
    if(n===2)return a('doc')&&n!==curStep;
    if(n===4)return a('write')&&n!==curStep;
    if(n===5)return a('canva')&&n!==curStep;
    if(n===6)return a('fx')&&n!==curStep;
    if(n===7)return a('kw')&&n!==curStep;
    return null;
  };
  H.report=function(){
    return ['台詞表文件：'+((state.doc||[]).length?'已開好':'還沒開'),
      '自查表：已勾 '+((state.chk||[]).length)+' 項（共 4 項）','提醒：台詞表在 Classroom 作業的文件裡，要按「繳交」'];
  };
  H.showAnswers=function(){};
  H.clear=function(){['doc','write','canva','fx','kw','chk'].forEach(function(k){state[k]=[];});['cat','hook','src','core'].forEach(function(k){state[k]='';});};
  var TPL_TEXT=@@TPL@@;
  function topicText(){
    return '類型：'+(state.cat||'')+'\n開頭句：'+(state.hook||'')+'\n來源網址：'+(state.src||'')+'\n核心訊息：'+(state.core||'');
  }
  function aiText(){
    return '我是五年級學生，想做 30～45 秒的解說影片。\n類型：'+(state.cat||'（還沒選）')+'\n我找到的資料：（把你在文件寫的資料貼在這裡）\n核心訊息：'+(String(state.core||'').trim()||'（還沒寫）')+'\n請幫我寫成三段台詞。';
  }
  H.render=function(){
    var has=filled(state.hook)||filled(state.src)||filled(state.core)||filled(state.cat);
    var card=$('topicCard');if(card)card.classList.toggle('hidden',!has);
    if(has){$('tCat').textContent=state.cat||'（沒有）';$('tHook').textContent=state.hook||'（沒有）';$('tSrc').textContent=state.src||'（沒有）';$('tCore').textContent=state.core||'（沒有）';}
    var l=$('srcLink');if(l){var u=String(state.src||'').trim();if(/^https?:\/\/\S+/.test(u)){l.href=u;l.classList.remove('hidden');}else{l.removeAttribute('href');l.classList.add('hidden');}}
    var m=$('aiMsg');if(m)m.textContent=aiText();
    var t=$('tplText');if(t)t.textContent=TPL_TEXT;
  };
  H.changed=function(){H.render();};

  // ===== 拿回 L07 存的主題（studentWork：g5-L07__年-班-號__topic）=====
  function say(el,msg,tone){if(!el)return;el.className=el.className.replace(/ ?text-(rose|amber|emerald|indigo)-600/g,'')+' text-'+tone+'-600';el.textContent=msg;}
  function copyText(text,btn){
    var old=btn.textContent;
    function done(){btn.textContent='已複製';setTimeout(function(){btn.textContent=old;},2000);}
    function fallback(){
      var ta=document.createElement('textarea');ta.value=text;ta.style.cssText='position:fixed;left:-9999px;top:0';
      document.body.appendChild(ta);ta.select();
      try{document.execCommand('copy');done();}catch(e){btn.textContent='請按 Ctrl+C 複製';}
      document.body.removeChild(ta);
    }
    try{navigator.clipboard.writeText(text).then(done,fallback);}catch(e){fallback();}
  }
  $('topicLoad').onclick=function(){
    var i=getIdentity(),st=$('topicStat');
    if(!identityValid(i)){markIdentity(true);say(st,'先到頁面最上面填年級、班級、座號，再按一次。','rose');return;}
    markIdentity(false);
    if(!db){say(st,'現在連不上，晚點再試試看。','amber');return;}
    authResolved.then(function(){return ensureAuth();}).then(function(){return db.collection('studentWork').doc('g5-L07__'+i.grade+'-'+i.className+'-'+i.studentId+'__topic').get();}).then(function(doc){
      if(!doc.exists){say(st,'上一節沒有存到你的主題。看下面的說明，或問老師。','amber');return;}
      var d=(doc.data()||{}).data||{};
      state.cat=d.cat||'';state.hook=d.hook||'';state.src=d.src||'';state.core=d.core||'';
      save();H.render();renderStepper();say(st,'已拿回你的主題。','emerald');
    }).catch(function(e){console.warn('拿回主題失敗',e);say(st,'現在拿不到，晚點再試試看。','amber');});
  };
  $('topicCopy').onclick=function(){copyText(topicText(),this);};
  $('tplCopy').onclick=function(){copyText(TPL_TEXT,this);};
  $('copyAI').onclick=function(){copyText(aiText(),this);};
'''.replace('@@TPL@@', json.dumps(TPL_TEXT, ensure_ascii=False))

SPEC = {
    'summary': '拿回上一節的主題；看老師的台詞表，認識三段式與關鍵字；用 AI（Gem）或句型卡在自己的 Google 文件寫出 7～8 句台詞，每句 20 字內，至少改一處；在 Canva 建立影片，每句一頁、把台詞打成字幕，套用一種文字特效；每句挑 1～2 個可搜尋的關鍵字（下一節用來找素材）。',
    'questions': [
        {'qid': 'doc', 'prompt': '你的 Google 文件（老師從 Classroom 作業讀取文件內容）：台詞表，每句有台詞和關鍵字。', 'mode': 'checklist',
         'checks': [{'desc': '寫了 7 句以上，順序上有「問題或謠言、解釋、結論」三段', 'pts': 3},
                    {'desc': '每句大約 20 字內，一句只講一件事，是說話的口氣；有標出 AI 給的（紅字）和自己改的（藍字）', 'pts': 3},
                    {'desc': '內容跟他的主題與來源有關，沒有加入來源裡沒有的數字、人名或日期', 'pts': 3},
                    {'desc': '每句都有 1～2 個關鍵字，是搜得到畫面的具體詞，不是「真正」「意見不一樣」這類看不到的詞', 'pts': 5}]},
    ],
    'scoring': {'base': 100, 'floor': 80, 'deduction': 1, 'itemPoints': {}},
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


t = sub1(r'<title>.*?</title>', '<title>寫台詞、做字幕、挑關鍵字｜L08 教學活動</title>', t)
t = sub1(r'<h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">.*?</h1>',
         '<h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">寫台詞、做字幕、挑關鍵字</h1>', t)
t = sub1(r'<p class="text-sm text-slate-500 mt-2">L06 Docs[^<]*</p>',
         '<p class="text-sm text-slate-500 mt-2">L08 台詞・字幕・關鍵字 · 教學活動流程（40 分鐘）</p>', t)
i = t.index('  </header>\n') + len('  </header>\n')
j = t.index('  <footer')
t = t[:i] + strip_emoji(BODY) + '\n' + t[j:]
t = sub1(r'<footer class="text-center text-xs text-slate-400 mt-8 pb-2">.*?</footer>',
         '<footer class="text-center text-xs text-slate-400 mt-8 pb-2">老師設定與檢視：在網址列加上 <code class="bg-slate-200 rounded px-1">#admin</code> 後重新整理。</footer>', t)
t = sub1(r'  var C=\{.*?\};\n', '  var C=' + json.dumps(CFG, ensure_ascii=False) + ';\n', t)
a = t.index('// ===== 複製七個欄位')
a = t.rfind('\n', 0, a) + 1
b = t.index('// ===== 作答狀態（localStorage 暫存）')
b = t.rfind('\n', 0, b) + 1
t = t[:a] + HOOKS + '\n' + t[b:]
t = t.replace("已儲存，學生繳交後就會看到按鈕", "已儲存，學生馬上就會看到按鈕")
t = sub1(r'<script type="application/json" id="grading-spec">\n.*?\n</script>',
         '<script type="application/json" id="grading-spec">\n' + json.dumps(SPEC, ensure_ascii=False, indent=2) + '\n</script>', t)

io.open(OUT, 'w', encoding='utf8', newline='\r\n').write(t)
print('wrote', OUT, len(t) // 1024, 'KB')
