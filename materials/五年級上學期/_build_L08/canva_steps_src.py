# -*- coding: utf-8 -*-
# 產生五上 L09「Canva：建立影片、選比例、放文字、找素材」學習單。
# 2026-11-16 老師：先教建立影片，選比例（介紹影片比例概念，學生可選直式或橫式），再教文字放進影片
# （文字輸入、文字特效），然後照著文字找素材；繳交不需要回 Google（Classroom）。
# Canva 的影片像「會動的簡報」：一頁一個畫面，沒有時間軸的概念，學習單只說「頁面」。
# 骨架直接取自「目前的」L06 學習單（識別列、教師列、進度列、Firebase、靠椅子關卡、步驟卡），
# 只換：標題、步驟內容、題目設定（C）、本節專屬的 JS（hooks）、評分設定。
# ⚠ 不要用 _build_L05_L06/build.py（行號已過時，重建會把 L05、L06 弄壞）。
# 生成後：
#   python 引導規範/chair-gate/inject.py <本節 html>
#   python 引導規範/stepcards/inject.py <本節 html>
#   python 引導規範/game-portal/check.py <本節 html>
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # materials/五年級上學期
SKEL = os.path.join(ROOT, 'L06_Docs查證文件二', '五上_L06_Docs查證文件二.html')
OUTDIR = os.path.join(ROOT, 'L09_Canva建立影片與找素材')
OUT = os.path.join(OUTDIR, '五上_L09_Canva建立影片與找素材.html')

PORTAL = 'https://boyinslps.github.io/pcclass/games/'

STEP1 = '''
  <!-- ===== 步驟 1：建立影片、選比例 ===== -->
  <section class="step" data-step="1">
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-rose-700 m-0">建立影片，先選比例</h2>
      <p class="text-slate-600 mt-2 text-lg">Canva 的影片像<b>會動的簡報</b>：<b>一頁就是一個畫面</b>。開始之前，要先決定影片的<b>比例</b>。</p>
    </div>
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-rose-700 m-0">什麼是比例？</p>
      <p class="text-lg text-slate-700 mt-2">比例就是畫面的<b>寬</b>和<b>高</b>的比。兩種最常見：</p>
      <div class="flex flex-wrap items-end justify-center gap-10 mt-4">
        <div class="text-center">
          <div class="bg-sky-100 border-4 border-sky-400 rounded-xl flex items-center justify-center text-sky-800 font-extrabold text-xl" style="width:224px;height:126px">橫式　16：9</div>
          <p class="text-lg text-slate-700 mt-2">像電腦螢幕、電視。<br>在教室電腦上播最合適。</p>
        </div>
        <div class="text-center">
          <div class="bg-rose-100 border-4 border-rose-400 rounded-xl flex items-center justify-center text-rose-800 font-extrabold text-xl" style="width:126px;height:224px">直式<br>9：16</div>
          <p class="text-lg text-slate-700 mt-2">像手機拿直看。<br>前面看的兩支示範就是直式。</p>
        </div>
      </div>
      <p class="text-lg text-slate-700 mt-4">橫的、直的<b>都可以</b>，選你喜歡的。選好再開始做，因為字幕和素材的位置會跟著比例不同。</p>
    </div>
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-rose-700 m-0">我選的是<span class="text-sm font-bold text-slate-500 ml-2">選 1 個</span></p>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="ratio"></span></div>
      <div id="ratioOpts" class="flex flex-wrap gap-2 mt-3"></div>
      <p class="cute text-xl font-extrabold text-rose-700 mt-5 mb-0">在 Canva 建立影片</p>
      <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
        <li>打開 Canva，按「建立設計」。</li>
        <li>橫式：搜尋「影片」，選影片。<br>直式：搜尋「手機影片」，選手機影片。</li>
        <li>把名字改成「我的解說影片」。</li>
      </ol>
    </div>
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-rose-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="make"></span></div>
      <div id="makeOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP2 = '''
  <!-- ===== 步驟 2：把台詞放進影片（文字輸入） ===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">把台詞放進影片</h2>
      <p class="text-slate-600 mt-2 text-lg">先把字幕放好，再照著字幕找素材。<b>一句台詞一頁</b>。</p>
    </div>
    <div class="grid md:grid-cols-3 gap-4 mb-5">
      <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 shadow-sm">
        <p class="cute text-xl font-extrabold text-sky-700 m-0">① 一句一頁</p>
        <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
          <li>在畫面下方，按「新增頁面」。</li>
          <li><b>頁數和台詞句數一樣</b>，7～8 頁。</li>
          <li>想要開頭大字，就在最前面多加一頁放題目（選做）。</li>
        </ol>
      </div>
      <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 shadow-sm">
        <p class="cute text-xl font-extrabold text-sky-700 m-0">② 輸入文字</p>
        <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
          <li>另開一個分頁，打開上一節的<b>台詞表文件</b>。</li>
          <li>左邊選「文字」，新增一個文字方塊。</li>
          <li>回文件複製這一句，貼進文字方塊。</li>
          <li>第 2 頁貼第 2 句，一頁一頁做。</li>
        </ol>
      </div>
      <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 shadow-sm">
        <p class="cute text-xl font-extrabold text-sky-700 m-0">③ 字幕要好讀</p>
        <ul class="mt-2 space-y-1 text-lg text-slate-700 list-disc pl-6">
          <li>字要夠大，顏色和背景分得開。</li>
          <li>橫式：放在畫面下面。直式：放在中間偏下，不要太靠邊。</li>
          <li><b>每一頁</b>字型、大小、位置都一樣。</li>
        </ul>
      </div>
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-sky-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="text"></span></div>
      <div id="textOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP3 = '''
  <!-- ===== 步驟 3：文字特效 ===== -->
  <section class="step hidden" data-step="3">
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

STEP4 = '''
  <!-- ===== 步驟 4：照字幕找素材 ===== -->
  <section class="step hidden" data-step="4">
    <div class="bg-white border-4 border-teal-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-teal-700 m-0">照著字幕找素材</h2>
      <p class="text-slate-600 mt-2 text-lg">看這一頁的字幕，用<b>關鍵字</b>找圖片或短影片，放進<b>同一頁</b>。<b>每一頁至少 1 個素材</b>，素材不要擋住字幕。下面四個地方都可以找，挑你好找的。</p>
      <p class="text-lg text-slate-700 mt-2">關鍵字寫在上一節的台詞表文件裡，沒有的話，從字幕裡挑看得到畫面的詞。搜不到，就換一個詞，或試試英文。</p>
    </div>
    <div class="grid md:grid-cols-2 gap-4 mb-5">
      <div class="bg-white border-4 border-teal-300 rounded-3xl p-5 shadow-sm">
        <p class="cute text-xl font-extrabold text-teal-700 m-0">辦法 1　Canva 素材庫</p>
        <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
          <li>左邊選「素材」，打上關鍵字搜尋。</li>
          <li>找圖片或影片，點一下放進這一頁。</li>
          <li>拖角落可以放大縮小，拖中間可以移動。</li>
        </ol>
      </div>
      <div class="bg-white border-4 border-pink-300 rounded-3xl p-5 shadow-sm">
        <p class="cute text-xl font-extrabold text-pink-700 m-0">辦法 2　可愛插圖：いらすとや</p>
        <p class="mt-2 text-lg text-slate-700">日本的免費插圖網站，圖很可愛，人物、動物、生活用品都有。</p>
        <ul class="mt-2 space-y-1 text-lg text-slate-700 list-disc pl-6">
          <li>用日文搜尋比較找得到：貓＝ねこ、車＝くるま、雷＝かみなり。不會打，就請 Google 翻譯變日文再貼上。</li>
          <li>圖片點開，按右鍵另存，再到 Canva「上傳」，拖進這一頁。</li>
          <li>使用前看一下他們的使用規定，素材不能拿去賣或再分享給別人。</li>
        </ul>
        <div class="flex flex-wrap gap-2 mt-3">
          <a href="https://www.irasutoya.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-pink-600 hover:bg-pink-700 text-white font-bold rounded-xl px-3 py-1.5">いらすとや ↗</a>
          <a href="https://www.irasutoya.com/p/terms.html" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-white border-2 border-pink-400 text-pink-800 font-bold rounded-xl px-3 py-1.5">使用規定 ↗</a>
        </div>
      </div>
      <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 shadow-sm">
        <p class="cute text-xl font-extrabold text-sky-700 m-0">辦法 3　免費圖庫：Pixabay、Pexels</p>
        <p class="mt-2 text-lg text-slate-700">兩個都有免費的照片和影片，Pixabay 還有插圖。可以用中文或英文搜尋。</p>
        <ul class="mt-2 space-y-1 text-lg text-slate-700 list-disc pl-6">
          <li>找到後按下載，再到 Canva「上傳」，拖進這一頁。</li>
          <li>有看得出品牌、商標的圖，或看得出是誰的人像，不要用。</li>
        </ul>
        <div class="flex flex-wrap gap-2 mt-3">
          <a href="https://pixabay.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-3 py-1.5">Pixabay ↗</a>
          <a href="https://www.pexels.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-3 py-1.5">Pexels ↗</a>
          <a href="https://pixabay.com/service/license-summary/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-white border-2 border-sky-400 text-sky-800 font-bold rounded-xl px-3 py-1.5">Pixabay 使用規定 ↗</a>
          <a href="https://www.pexels.com/license/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-white border-2 border-sky-400 text-sky-800 font-bold rounded-xl px-3 py-1.5">Pexels 使用規定 ↗</a>
        </div>
      </div>
      <div class="bg-white border-4 border-teal-300 rounded-3xl p-5 shadow-sm">
        <p class="cute text-xl font-extrabold text-teal-700 m-0">辦法 4　Google 圖片</p>
        <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
          <li>到 Google 搜尋，點「圖片」，打上關鍵字。</li>
          <li>按「工具」→「使用權」→ 選<b>創用 CC 授權</b>。</li>
          <li>點開圖片，看它從哪個網頁來，<b>記下網頁網址</b>。</li>
          <li>圖片按右鍵另存，再到 Canva「上傳」，拖進這一頁。</li>
        </ol>
      </div>
    </div>
    <div class="bg-white border-4 border-teal-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-teal-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="mat"></span></div>
      <div id="matOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP5 = '''
  <!-- ===== 步驟 5：素材來源頁 ===== -->
  <section class="step hidden" data-step="5">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700 m-0">在最後加一頁「素材來源」</h2>
      <p class="text-slate-600 mt-2 text-lg">用了別人的素材，要說清楚是從哪裡來的。影片最後多加一頁，把來源打上去。</p>
    </div>
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <ol class="space-y-2 text-lg text-slate-700 list-decimal pl-6">
        <li>按「新增頁面」，加在<b>最後面</b>。</li>
        <li>打上標題「素材來源」，再用文字方塊一行一行寫。</li>
        <li>用 Canva 素材庫的，寫「Canva 素材庫」。</li>
        <li>用其他網站的，寫網站名稱，例如「いらすとや」「Pixabay」「Pexels」，Google 圖片的寫圖片所在的網頁網址。</li>
        <li>同一個網站用了好幾張，寫一次就好。</li>
      </ol>
      <div class="bg-amber-50 border-2 border-amber-200 rounded-2xl p-4 mt-4 text-lg text-slate-700">
        <p class="font-bold text-amber-800 m-0">範例</p>
        <p class="mt-1">素材來源<br>Canva 素材庫<br>いらすとや　irasutoya.com<br>Pexels　pexels.com</p>
      </div>
    </div>
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-amber-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="srcpage"></span></div>
      <div id="srcpageOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP6 = '''
  <!-- ===== 步驟 6：繳交 ===== -->
  <section class="step hidden" data-step="6">
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-indigo-700">分享連結，再繳交</h2>
      <p class="text-slate-600 mt-2 text-lg">你的影片在 Canva 裡，不用回 Classroom。把影片的分享連結貼在下面，再按繳交，老師就看得到。</p>
    </div>
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-indigo-700 m-0">① 取得分享連結</p>
      <ol class="mt-2 space-y-1 text-lg text-slate-700 list-decimal pl-6">
        <li>在 Canva 按右上角的「分享」。</li>
        <li>把權限設成<b>知道連結的人都可以檢視</b>。</li>
        <li>按「複製連結」。</li>
      </ol>
      <p class="cute text-xl font-extrabold text-indigo-700 mt-5 mb-0">② 貼在這裡</p>
      <div class="flex items-center gap-2 flex-wrap mt-2"><span class="qtypeSlot" data-qid="canvaLink"></span></div>
      <input id="canvaLink" data-k="canvaLink" type="url" autocomplete="off" class="fld ans mt-2 text-lg">
      <p id="linkMsg" class="text-base font-bold mt-2 min-h-[24px]"></p>
    </div>
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h3 class="cute text-xl font-extrabold text-indigo-700 m-0">繳交前自己檢查</h3>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="chk"></span></div>
      <div id="chkOpts" class="space-y-2 mt-3"></div>
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

BODY = '\n' + ''.join([STEP1, STEP2, STEP3, STEP4, STEP5, STEP6]) + '\n'

CFG = {
    'ws': 'g5-L09', 'lessonPath': 'g5/L09', 'title': 'Canva：建立影片、放文字、找素材', 'stateKey': 'g5L09flow',
    'steps': ['建立影片', '放進文字', '文字特效', '找素材', '素材來源', '分享繳交'],
    'reveals': [], 'revealOf': {}, 'autoFb': [], 'textSettings': [],
    'qtypes': {'ratio': 'experience', 'make': 'experience', 'text': 'experience', 'fx': 'experience', 'mat': 'experience',
               'srcpage': 'experience', 'canvaLink': 'open', 'chk': 'experience'},
    'choices': {
        'ratio': {'opts': ['橫式（16：9）', '直式（9：16）']},
        'make': {'opts': ['我建立了影片設計，比例是我選的那一種', '名字改成「我的解說影片」了'], 'multi': True, 'block': True},
        'text': {'opts': ['頁數和台詞句數一樣，每頁一句', '每頁字幕都貼好了，看得清楚', '每頁字幕的字型、大小、位置一樣'], 'multi': True, 'block': True},
        'fx': {'opts': ['每一頁字幕都有文字特效，而且是同一種', '我按播放從頭看過，字幕讀得完'], 'multi': True, 'block': True},
        'mat': {'opts': ['每一頁至少有 1 個素材', '素材跟那一頁的字幕有關', '素材沒有擋住字幕'], 'multi': True, 'block': True},
        'srcpage': {'opts': ['最後多了一頁「素材來源」', '每個用到的網站或 Canva 素材庫都寫了'], 'multi': True, 'block': True},
        'chk': {'opts': ['影片每一頁都有字幕和文字特效', '每一頁都有素材', '最後有素材來源頁', '分享連結貼好了，我自己點開看得到影片'], 'multi': True, 'block': True},
    },
    'texts': ['canvaLink'],
    'patterns': {'canvaLink': r'^https?://(www\.)?canva\.(com|link)/\S+'},
    'openQtexts': {'canvaLink': '我的 Canva 影片分享連結。'},
}

HOOKS = r'''
  H.stepDone=function(n){
    var a=function(k){return state[k]!=null&&(Array.isArray(state[k])?state[k].length>0:filled(state[k]));};
    if(n===1)return a('ratio')&&a('make')&&n!==curStep;
    if(n===2)return a('text')&&n!==curStep;
    if(n===3)return a('fx')&&n!==curStep;
    if(n===4)return a('mat')&&n!==curStep;
    if(n===5)return a('srcpage')&&n!==curStep;
    return null;
  };
  H.report=function(){
    return ['影片比例：'+(state.ratio||'還沒選'),
      'Canva 分享連結：'+(filled(state.canvaLink)?'已貼':'還沒貼'),
      '自查表：已勾 '+((state.chk||[]).length)+' 項（共 4 項）'];
  };
  H.showAnswers=function(){};
  H.clear=function(){['make','text','fx','mat','srcpage','chk'].forEach(function(k){state[k]=[];});state.ratio=null;state.canvaLink='';};
  H.render=function(){
    var m=$('linkMsg'),v=String(state.canvaLink||'').trim();
    if(!m)return;
    if(!v){m.textContent='';return;}
    var ok=/^https?:\/\/(www\.)?canva\.(com|link)\/\S+/.test(v);
    m.className='text-base font-bold mt-2 min-h-[24px] '+(ok?'text-emerald-600':'text-amber-600');
    m.textContent=ok?'連結看起來可以。貼好後，自己點開確認看得到影片。':'這看起來不是 Canva 的連結，回 Canva 按「分享」→「複製連結」再貼一次。';
  };
  H.changed=function(){H.render();};
  H.render();
'''

SPEC = {
    'summary': '在 Canva 選好影片比例（橫式或直式）、建立影片；把台詞一句一頁放進影片，字幕版面一致，套用同一種文字特效；照字幕與關鍵字找素材，每頁至少 1 個放進該頁；最後加素材來源頁；貼上 Canva 分享連結繳交。',
    'questions': [
        {'qid': 'canvaLink', 'prompt': '我的 Canva 影片分享連結（老師點開連結看作品）。', 'mode': 'checklist',
         'checks': [{'desc': '連結點得開、看得到影片；每一頁一句字幕，頁數和台詞句數相近，字幕看得清楚、字型大小位置一致', 'pts': 4},
                    {'desc': '每一頁字幕都有文字特效，而且是同一種', 'pts': 2},
                    {'desc': '每一頁至少有 1 個素材，和字幕有關，沒有擋住字幕', 'pts': 4},
                    {'desc': '最後有「素材來源」頁，有寫 Canva 素材庫或其他網站', 'pts': 3}]},
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


t = sub1(r'<title>.*?</title>', '<title>Canva：建立影片、放文字、找素材｜L09 教學活動</title>', t)
t = sub1(r'<h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">.*?</h1>',
         '<h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">在 Canva 做你的影片</h1>', t)
t = sub1(r'<p class="text-sm text-slate-500 mt-2">L06 Docs[^<]*</p>',
         '<p class="text-sm text-slate-500 mt-2">L09 建立影片・文字・素材 · 教學活動流程（40 分鐘）</p>', t)
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

os.makedirs(OUTDIR, exist_ok=True)
io.open(OUT, 'w', encoding='utf8', newline='\r\n').write(t)
print('wrote', OUT, len(t) // 1024, 'KB')
