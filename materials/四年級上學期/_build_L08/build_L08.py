# -*- coding: utf-8 -*-
# 產生四上 L08「Canva：開 B5 文件、認識介面、手冊結構、做封面與目錄」學習單（6 步）。
# 2026-11-17 老師指示：不用老師範本；明天只教「開文件選 A4、介紹 Canva 編輯介面、完整手冊結構」，只做封面與目錄頁。
# 骨架沿用四上 L07：識別列、進度列、步驟卡、Firebase 繳交、靠椅子關卡。
# 生成後依序執行（這台電腦用 工作台/runtime/python/python.exe）：
#   python 引導規範/chair-gate/inject.py <本節 html>
#   python 引導規範/stepcards/inject.py <本節 html>
#   python 引導規範/game-portal/check.py <本節 html>
# 改內容請改這支檔案再重新產生，不要直接改 HTML。
import io, os, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, 'L08_Canva導覽手冊_封面與目錄')
OUT = os.path.join(OUTDIR, '四上_L08_Canva導覽手冊_封面與目錄.html')

PORTAL = 'https://boyinslps.github.io/pcclass/games/'
CANVA_HOME = 'https://www.canva.com/'
TWTAINAN = 'https://www.twtainan.net/'

HEAD = r'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="author" content="資訊老師黃博胤">
<title>台南小導遊養成記｜L08</title>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Noto+Sans+TC:wght@500;700;900&display=swap" rel="stylesheet">
<style>
  body{font-family:'Noto Sans TC',sans-serif;background:#FFFBF3;color:#243b53;font-size:18px;line-height:1.7}
  .cute{font-family:'Baloo 2','Noto Sans TC',cursive}
  .idnum{width:52px;text-align:center}
  .stepnav{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:20px;padding-top:14px;border-top:2px solid #f1f5f9}
  .stepdot{width:32px;height:32px}
  @media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
  .stepno{display:inline-flex;align-items:center;justify-content:center;width:1.7em;height:1.7em;margin-right:.5em;border-radius:9999px;background:#0ea5e9;color:#fff;font-size:.8em}
  .stepno.bg-orange{background:#ea580c}.stepno.bg-violet{background:#7c3aed}.stepno.bg-teal{background:#0d9488}.stepno.bg-rose{background:#e11d48}
  kbd{background:#f1f5f9;border:1px solid #cbd5e1;border-bottom-width:3px;border-radius:6px;padding:0 6px;font-family:inherit;font-weight:700}
  .shot{border-radius:14px;border:3px solid #fff;box-shadow:0 6px 20px rgba(0,0,0,.14);width:100%;display:block}
  .hidden.hidden,.sc-flat .sc-slide.hidden{display:none !important}
  .ptype{border:4px solid #bae6fd;background:#fff;border-radius:18px;padding:4px 16px;font-weight:800;font-size:1.2rem;color:#0369a1}
  .ptype.on{background:#0ea5e9;border-color:#0ea5e9;color:#fff}
  .hs{position:absolute;width:34px;height:34px;border-radius:9999px;background:#ea580c;color:#fff;font-weight:800;font-size:18px;display:flex;align-items:center;justify-content:center;border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.35);transform:translate(-50%,-50%)}
  .zoomable{cursor:zoom-in}
  .pgcap{font-size:1.05rem;font-weight:800;line-height:1.25}
</style>
</head>
<body>

<!-- 識別列 -->
<div class="bg-white border-b-2 border-orange-200">
  <div class="max-w-5xl mx-auto px-4 py-2 flex items-center gap-3 flex-wrap text-sm">
    <span class="cute font-bold text-orange-700">我是誰</span>
    <label class="flex items-center gap-1 text-slate-500">年級<input id="idGrade" class="idnum border-2 border-slate-200 rounded-lg px-2 py-1 font-bold text-slate-700 focus:border-orange-400 outline-none" inputmode="numeric" maxlength="2"></label>
    <label class="flex items-center gap-1 text-slate-500">班級<input id="idClass" class="idnum border-2 border-slate-200 rounded-lg px-2 py-1 font-bold text-slate-700 focus:border-orange-400 outline-none" inputmode="numeric" maxlength="2"></label>
    <label class="flex items-center gap-1 text-slate-500">座號<input id="idStudent" class="idnum border-2 border-slate-200 rounded-lg px-2 py-1 font-bold text-slate-700 focus:border-orange-400 outline-none" inputmode="numeric" maxlength="2"></label>
    <span id="idOk" class="hidden text-emerald-600 font-bold text-xs">✓ 已記住</span>
  </div>
</div>

<!-- 學習路徑進度列 -->
<div class="sticky top-0 z-20 bg-white/95 backdrop-blur border-b-2 border-orange-100">
  <div class="max-w-5xl mx-auto px-4 py-2">
    <div id="stepper" class="flex items-start"></div>
    <p id="stepLabel" class="sm:hidden text-xs font-bold text-orange-700 text-center mt-1"></p>
  </div>
</div>

<div class="max-w-5xl mx-auto px-4 py-5">

  <header class="text-center mb-4">
    <h1 class="cute text-3xl md:text-4xl font-extrabold text-orange-600 leading-tight">台南小導遊養成記</h1>
    <p class="text-sm text-slate-500">第 8 課：用 Canva 做導覽手冊</p>
  </header>
'''

# 手冊 9 頁（縮圖 + 頁名 + 一句說明）
PAGES = [
    ('手冊_p1.jpg', '1', '封面', '書名、景點、照片', 'sky'),
    ('手冊_p2.jpg', '2', '目錄', '章節和頁碼', 'sky'),
    ('手冊_p3.jpg', '3', '行程規劃', '時間表、交通', 'orange'),
    ('手冊_p4.jpg', '4', '路線圖', 'Google 地圖', 'orange'),
    ('手冊_p5.jpg', '5', '景點頁', '第 1 站', 'orange'),
    ('手冊_p6.jpg', '6', '景點頁', '第 2 站', 'orange'),
    ('手冊_p7.jpg', '7', '午餐', '第 3 站', 'orange'),
    ('手冊_p8.jpg', '8', '景點頁', '第 4 站', 'orange'),
    ('手冊_p9.jpg', '9', '小吃', '第 5 站', 'orange'),
    ('手冊_p10.jpg', '10', '小提醒', '注意事項', 'orange'),
    ('手冊_p11.jpg', '11', '封底', '謝謝、署名', 'sky'),
]


def pages_grid():
    h = []
    for f, n, name, sub, col in PAGES:
        tc = 'text-sky-700' if col == 'sky' else 'text-orange-700'
        h.append('<div class="text-center"><img src="assets/%s" alt="第 %s 頁：%s" class="shot zoomable" loading="lazy">'
                 '<p class="pgcap %s mt-1">第 %s 頁<br>%s</p><p class="text-sm text-slate-500">%s</p></div>' % (f, n, name, tc, n, name, sub))
    return '\n        '.join(h)


STEP1 = r'''
  <!-- 步驟 1：完整手冊結構 -->
  <section class="step bg-white border-4 border-sky-300 rounded-3xl p-5 shadow-sm" data-step="1">
    <h2 class="cute text-3xl font-extrabold text-sky-700 mb-3">先看：完整的手冊</h2>

    <div class="bg-orange-50 border-4 border-orange-300 rounded-3xl p-4 mb-4">
      <p class="cute text-2xl font-extrabold text-orange-700 mb-2">今天的任務</p>
      <ol class="text-2xl font-extrabold space-y-2">
        <li><span class="stepno bg-orange">1</span>開一份 <span class="text-orange-700">B5</span> 新文件</li>
        <li><span class="stepno bg-orange">2</span>認識 Canva 的<span class="text-orange-700">編輯畫面</span></li>
        <li><span class="stepno bg-orange">3</span>做<span class="text-orange-700">封面</span>和<span class="text-orange-700">目錄</span></li>
      </ol>
      <p class="text-xl font-bold text-slate-600 mt-2">其他頁，之後的課再做。</p>
    </div>

    <div class="bg-sky-50 border-4 border-sky-200 rounded-3xl p-4 mb-4">
      <p class="cute text-2xl font-extrabold text-sky-700 mb-1">一本完整的手冊，有 11 頁</p>
      <p class="text-lg text-slate-500 mb-3">點圖放大。橘色字是會用到「文件裡的資料」的頁。</p>
      <div class="grid grid-cols-3 sm:grid-cols-6 gap-3">
        __PAGES__
      </div>
    </div>

    <div class="bg-amber-50 border-4 border-amber-200 rounded-3xl p-4 mb-4">
      <p class="cute text-2xl font-extrabold text-amber-700 mb-2">你文件裡的資料，放在哪一頁？</p>
      <ul class="text-xl font-bold space-y-1">
        <li><b class="text-orange-700">行程規劃</b>：幾點到哪裡的<b>時間表</b>（如 9:00 赤崁樓　10:00 …），交通格子</li>
        <li><b class="text-orange-700">路線圖</b>：用 Google 地圖把每一站連起來，截圖放進來</li>
        <li><b class="text-orange-700">景點頁</b>：地址、開放時間、門票、<b>照片（1～4 張）</b>，還有景點介紹（歷史、看點、特色）</li>
        <li><b class="text-orange-700">美食也是一站</b>：午餐、小吃，寫成「第 3 站　午餐」「第 5 站　小吃」，一樣一站一頁</li>
      </ul>
    </div>

    <div class="bg-white border-4 border-teal-200 rounded-3xl p-4 mb-4">
      <p class="cute text-2xl font-extrabold text-teal-700 mb-2">配一配：這些字放哪一頁？</p>
      <div id="quiz" class="space-y-3"></div>
      <p id="quizMsg" class="text-xl font-extrabold mt-3 min-h-[32px]"></p>
    </div>

    <div class="hidden"><input type="checkbox" class="chk" id="quizOk" disabled></div>
    <div class="stepnav"></div>
  </section>
'''

STEP2 = r'''
  <!-- 步驟 2：開 B5 新文件 -->
  <section class="step hidden bg-white border-4 border-teal-300 rounded-3xl p-5 shadow-sm" data-step="2">
    <h2 class="cute text-3xl font-extrabold text-teal-700 mb-3">開一份 B5 新文件</h2>

    <div class="sc sc-flat" data-sc>
      <div class="sc-slide">
        <p class="sc-t">打開 <b>Canva</b>，用學校帳號登入</p>
        <a href="__CANVA_HOME__" target="_blank" rel="noopener" class="cute inline-block bg-teal-600 hover:bg-teal-700 text-white text-xl font-extrabold rounded-2xl px-6 py-2">開 Canva ↗</a>
        <p class="text-lg text-slate-500 mt-2">登不進去，<b>舉手</b>。</p>
      </div>
      <div class="sc-slide sc-split">
        <div class="sc-txt">
          <p class="sc-t">按「<b>建立</b>」→「<b>自訂尺寸</b>」</p>
          <p class="text-xl font-extrabold mt-2">單位選「<b>公釐</b>」，寬打 <b class="text-orange-700">176</b>，高打 <b class="text-orange-700">250</b>，按「建立新設計」。</p>
          <p class="text-xl font-extrabold text-rose-700 mt-2">不要選 Docs，也不要選現成的「文件」。</p>
          <p class="text-lg text-slate-500">B5＝小冊子常用的紙，比 A4 小一點。</p>
        </div>
        <div class="sc-media" data-src="assets/步_canva_開B5文件.mp4" data-poster="assets/步_canva_開B5文件_封面.jpg"></div>
      </div>
      <div class="sc-slide sc-split">
        <div class="sc-txt">
          <p class="sc-t">右上角，把<b>作品名字</b>改成：</p>
          <p class="cute text-3xl font-extrabold text-teal-700"><span id="projName">先填上面的年級、班級、座號</span></p>
          <button type="button" id="projCopy" class="mt-2 bg-white border-2 border-teal-300 hover:bg-teal-50 text-teal-700 font-bold rounded-xl px-4 py-1">複製名字</button>
        </div>
        <div class="sc-media" data-src="assets/步_canva_改檔名.mp4" data-poster="assets/步_canva_改檔名_封面.jpg"></div>
      </div>
    </div>

    <div class="bg-white border-4 border-teal-200 rounded-3xl p-4 mt-4 text-xl">
      <p class="cute text-2xl font-extrabold text-teal-700 mb-2">這一步檢查</p>
      <label class="flex items-center gap-3 mb-2"><input type="checkbox" class="chk w-6 h-6"> 開好一張<b>空白</b>的 B5 紙（名字上寫 176 公釐 × 250 公釐）</label>
      <label class="flex items-center gap-3"><input type="checkbox" class="chk w-6 h-6"> <b>作品名字</b>改好了</label>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP3 = r'''
  <!-- 步驟 3：認識編輯畫面 -->
  <section class="step hidden bg-white border-4 border-violet-300 rounded-3xl p-5 shadow-sm" data-step="3">
    <h2 class="cute text-3xl font-extrabold text-violet-700 mb-3">認識 Canva 的編輯畫面</h2>

    <div class="grid gap-4 mb-4">
      <div class="relative">
        <img src="assets/介面_標記.jpg" alt="Canva 編輯畫面，已標上 1～6 號：上面有作品名字和分享，左邊是工具列，中間是白色的紙，下面是小頁面圖和新增頁面" class="shot zoomable" title="點一下放大">
      </div>
      <div class="bg-violet-50 border-4 border-violet-200 rounded-3xl p-4">
        <ol class="text-xl font-bold space-y-2">
          <li><span class="stepno bg-violet">1</span><b>作品名字</b>，點一下可以改</li>
          <li><span class="stepno bg-violet">2</span><b>左邊工具列</b>：文字、上傳、元素…要加東西，來這裡</li>
          <li><span class="stepno bg-violet">3</span><b>白色的紙</b>：做的東西放在這裡</li>
          <li><span class="stepno bg-violet">4</span><b>小頁面圖</b>：點一下，換到那一頁</li>
          <li><span class="stepno bg-violet">5</span><b>＋</b>：多一張新的紙</li>
          <li><span class="stepno bg-violet">6</span><b>分享</b>：做好了，從這裡拿連結</li>
        </ol>
      </div>
    </div>

    <div class="bg-rose-50 border-4 border-rose-300 rounded-2xl p-3 mb-4 text-xl font-extrabold text-rose-700">
      弄亂了？按 <kbd>Ctrl</kbd> + <kbd>Z</kbd> 復原。不要按 Delete。還是亂，就舉手。
    </div>

    <div class="bg-amber-50 border-4 border-amber-300 rounded-3xl p-4 mb-4">
      <p class="cute text-2xl font-extrabold text-amber-700 mb-1">小測驗：這一區是做什麼的？</p>
      <p class="text-lg text-slate-500 mb-3">看圖，選一個答案。選對才會顯示 ✓。</p>
      <div id="faceQuiz" class="space-y-3"></div>
      <p id="faceMsg" class="text-xl font-extrabold mt-3 min-h-[32px]"></p>
    </div>
    <div class="hidden"><input type="checkbox" class="chk" id="faceOk" disabled></div>

    <div class="bg-white border-4 border-teal-200 rounded-3xl p-4 text-xl">
      <p class="cute text-2xl font-extrabold text-teal-700 mb-2">這一步檢查</p>
      <label class="flex items-center gap-3"><input type="checkbox" class="chk w-6 h-6"> 我在<b>自己的畫面</b>找到了：文字、上傳、＋、分享</label>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP4 = r'''
  <!-- 步驟 4：做封面（選範本＋改文字） -->
  <section class="step hidden bg-white border-4 border-orange-300 rounded-3xl p-5 shadow-sm" data-step="4">
    <h2 class="cute text-3xl font-extrabold text-orange-700 mb-3">做封面（第 1 頁）：選範本，改文字</h2>

    <div class="grid sm:grid-cols-5 gap-4 items-center mb-4">
      <div class="sm:col-span-2"><img src="assets/手冊_p1.jpg" alt="範例封面：書名、三個景點" class="shot zoomable" loading="lazy"></div>
      <div class="sm:col-span-3 bg-orange-50 border-4 border-orange-200 rounded-3xl p-4">
        <p class="cute text-2xl font-extrabold text-orange-700 mb-2">封面 3 件事</p>
        <ol class="text-2xl font-extrabold space-y-1">
          <li><span class="stepno bg-orange">1</span><b>選一個範本</b>（自己喜歡的）</li>
          <li><span class="stepno bg-orange">2</span>把<b>書名</b>改成自己的</li>
          <li><span class="stepno bg-orange">3</span>把<b>三個景點</b>改上去</li>
        </ol>
        <p class="text-lg text-slate-500 mt-2">左邊是老師自己排的範例，你用範本，樣子會不一樣。照片之後的課再換，今天只處理文字。</p>
      </div>
    </div>

    <div class="bg-rose-50 border-4 border-rose-300 rounded-2xl p-3 mb-4 text-xl font-extrabold text-rose-700">
      弄亂了？按 <kbd>Ctrl</kbd> + <kbd>Z</kbd> 復原。不要按 Delete。還是亂，就舉手。
    </div>

    <div class="sc sc-flat" data-sc>
      <div class="sc-slide">
        <p class="sc-t"><b>選範本</b>：左邊按「<b>範本</b>」，在搜尋框打關鍵字</p>
        <img src="assets/封面_範本搜尋.jpg" alt="Canva 左邊範本面板：1 範本按鈕、2 搜尋框、3 搜尋結果" class="shot zoomable mb-2" loading="lazy">
        <ol class="text-xl font-bold space-y-1">
          <li><span class="stepno bg-orange">1</span>按左邊的「<b>範本</b>」</li>
          <li><span class="stepno bg-orange">2</span>在<b>搜尋框</b>打字，按 <kbd>Enter</kbd></li>
          <li><span class="stepno bg-orange">3</span>下面就是<b>搜尋結果</b>，往下滑可以看更多</li>
        </ol>
        <div class="bg-amber-50 border-4 border-amber-300 rounded-2xl p-3 mt-3 text-xl">
          <p class="font-extrabold text-amber-700">不喜歡？換一個關鍵字再搜</p>
          <p class="mt-1">試試看：<b>台南</b>、<b>旅行</b>、<b>旅遊</b>、<b>手冊</b>、<b>封面</b>、<b>景點</b>、<b>美食</b>、<b>小書</b>。也可以兩個字一起打，中間空一格，例如「<b>台南 旅行 封面</b>」。</p>
        </div>
      </div>
      <div class="sc-slide">
        <p class="sc-t">點一下喜歡的範本，再點<b>封面那一頁</b></p>
        <img src="assets/封面_範本選頁.jpg" alt="範本詳細頁：點第一張縮圖（封面）" class="shot zoomable mb-2" loading="lazy">
        <ul class="text-xl font-bold space-y-1 list-disc pl-6">
          <li>有的範本有好幾頁，只點<b>第一張（封面）</b>就好</li>
          <li>不要按「套用全部 ○ 個頁面」，不然會多出好多頁</li>
          <li>點了會放到你的紙上，不喜歡就 <kbd>Ctrl</kbd> + <kbd>Z</kbd>，再選別的</li>
          <li class="text-slate-500 font-normal">範本的大小和你的紙不一樣，上下可能有白邊，今天不管它</li>
        </ul>
      </div>
      <div class="sc-slide">
        <p class="sc-t"><b>改文字</b>：連按兩下 → <kbd>Ctrl</kbd> + <kbd>A</kbd> → 直接打自己的字</p>
        <ul class="text-xl font-bold space-y-1 list-disc pl-6">
          <li><b>書名</b>：最大的那行字，改成「我的台南一日小旅行」這類自己的書名</li>
          <li><b>三個景點</b>：小一點的字，改成你的三個景點，中間用「＋」隔開</li>
          <li>範本上用不到的字（作者、日期…），改成自己的，或選起來按 <kbd>Delete</kbd></li>
        </ul>
        <p class="text-lg text-slate-500 mt-2">連按兩下有時只選到一個詞，再按一次 <kbd>Ctrl</kbd> + <kbd>A</kbd> 就全選了。</p>
      </div>
      <div class="sc-slide">
        <p class="sc-t"><b>點一下文字</b>，上面會出現「文字工具列」</p>
        <img src="assets/封面_文字工具列.jpg" alt="選到文字後，上方工具列：1 字型、2 字大小、3 顏色，4 是文字框" class="shot zoomable mb-2" loading="lazy">
        <ol class="text-xl font-bold space-y-1">
          <li><span class="stepno bg-orange">1</span><b>字型</b>：字的樣子（圓圓的、粗粗的…），按一下可以換，下一張圖教你</li>
          <li><span class="stepno bg-orange">2</span><b>字大小</b>：按 <b>＋</b> 變大、<b>－</b> 變小，也可以點數字，直接打新的數字</li>
          <li><span class="stepno bg-orange">3</span><b>顏色</b>：按字母 <b>A</b> 底下的色條，選一個顏色</li>
          <li><span class="stepno bg-orange">4</span><b>文字框</b>：字外面的紫色框，用來移動和調整大小（下面教）</li>
        </ol>
        <p class="text-lg text-slate-500 mt-2">旁邊還有 <b>B</b>（粗體）、<b>I</b>（斜體）、<b>U</b>（底線）、對齊（靠左／置中）。</p>
      </div>
      <div class="sc-slide">
        <p class="sc-t"><b>換字型</b>：按工具列最左邊的字型名字</p>
        <img src="assets/封面_文字字型.jpg" alt="左邊跳出字型清單：1 搜尋字型、2 字型清單" class="shot zoomable mb-2" loading="lazy">
        <ol class="text-xl font-bold space-y-1">
          <li><span class="stepno bg-orange">1</span>左邊跳出「字型」清單，上面的<b>搜尋框</b>可以打字找（例如「書法」）</li>
          <li><span class="stepno bg-orange">2</span>往下滑，<b>點一個字型</b>，選到的字馬上就換</li>
        </ol>
        <p class="text-lg text-slate-500 mt-2">不好看就 <kbd>Ctrl</kbd> + <kbd>Z</kbd>，再換一個。封面的字型不要超過 2 種，才不會亂。</p>
      </div>
      <div class="sc-slide">
        <p class="sc-t"><b>移動文字</b>：按住文字，拖到想放的地方</p>
        <img src="assets/封面_文字移動.jpg" alt="把書名那個紫色文字框往下拖，書名跟著移動" class="shot zoomable mb-2" loading="lazy">
        <ul class="text-xl font-bold space-y-1 list-disc pl-6">
          <li>滑鼠放在字上，<b>按住左鍵</b>不放，拖到新位置再放開</li>
          <li>拖的時候會出現<b>紫色的對齊線</b>，靠近中間或邊邊會自動吸住</li>
          <li>也可以先點文字，再用鍵盤的<b>方向鍵</b>一格一格微調</li>
        </ul>
      </div>
      <div class="sc-slide">
        <p class="sc-t"><b>調整文字框大小</b>：拉紫色框上的小白點</p>
        <ul class="text-xl font-bold space-y-2 list-disc pl-6">
          <li><b>四個角的白點</b>：拉它，<b>字會跟著變大或變小</b>（和用 ＋／－ 一樣）</li>
          <li><b>左右兩邊中間的小白點</b>：只改文字框的<b>寬度</b>，字不變大小，太長的字會自己<b>換行</b></li>
          <li>框太窄，字會擠成好幾行；框太寬，字會跑到紙外面，拉回來就好</li>
        </ul>
        <p class="text-lg text-slate-500 mt-2">上一張圖的紫色框，就是你要拉的文字框。</p>
      </div>
    </div>

    <div class="bg-white border-4 border-teal-200 rounded-3xl p-4 mt-4 text-xl">
      <p class="cute text-2xl font-extrabold text-teal-700 mb-2">這一步檢查</p>
      <label class="flex items-center gap-3 mb-2"><input type="checkbox" class="chk w-6 h-6"> 第 1 頁用了一個<b>範本</b></label>
      <label class="flex items-center gap-3 mb-2"><input type="checkbox" class="chk w-6 h-6"> <b>書名</b>改成我自己的</label>
      <label class="flex items-center gap-3 mb-2"><input type="checkbox" class="chk w-6 h-6"> 有我的<b>三個景點</b></label>
      <label class="flex items-center gap-3"><input type="checkbox" class="chk w-6 h-6"> <b>字型、字大小、位置</b>至少調整過一樣</label>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP5 = r'''
  <!-- 步驟 5：做目錄 -->
  <section class="step hidden bg-white border-4 border-emerald-300 rounded-3xl p-5 shadow-sm" data-step="5">
    <h2 class="cute text-3xl font-extrabold text-emerald-700 mb-3">做目錄（第 2 頁）</h2>

    <div class="grid sm:grid-cols-5 gap-4 items-center mb-4">
      <div class="sm:col-span-2"><img src="assets/手冊_p2.jpg" alt="範例目錄：靠左、每行前面有圓點，行程規劃 3、路線圖 4、第 1 站 5…旅行小提醒 10" class="shot zoomable" loading="lazy"></div>
      <div class="sm:col-span-3 bg-emerald-50 border-4 border-emerald-200 rounded-3xl p-4">
        <p class="cute text-2xl font-extrabold text-emerald-700 mb-2">目錄：靠左，一行一個章節</p>
        <ul class="text-2xl font-extrabold space-y-0.5 list-disc pl-8">
          <li>行程規劃　<span class="text-emerald-700">3</span></li>
          <li>路線圖　<span class="text-emerald-700">4</span></li>
          <li>第 1 站　景點名　<span class="text-emerald-700">5</span></li>
          <li>第 2 站　景點名　<span class="text-emerald-700">6</span></li>
          <li>第 3 站　午餐　<span class="text-emerald-700">7</span></li>
          <li>…（你有幾站，就寫幾行）</li>
          <li>旅行小提醒　<span class="text-emerald-700">最後一頁前</span></li>
        </ul>
        <p class="text-lg text-slate-500 mt-2">美食也是一站。後面的數字是<b>頁碼</b>（對照第 1 步的頁）。</p>
      </div>
    </div>

    <div class="sc sc-flat" data-sc>
      <div class="sc-slide sc-split">
        <div class="sc-txt">
          <p class="sc-t">畫面下面按「<b>＋</b>」，多一張新的紙</p>
          <p class="text-lg text-slate-500 mt-2">再用「文字」加<b>標題</b>「目錄」。</p>
        </div>
        <div class="sc-media" data-src="assets/步_canva_新增頁面.mp4" data-poster="assets/步_canva_新增頁面_封面.jpg"></div>
      </div>
      <div class="sc-slide">
        <p class="sc-t">文字 →「新增少量內文文字」，一行一個章節</p>
        <p class="text-lg text-slate-500">一行打完按 <kbd>Enter</kbd> 換行。景點名和頁碼用你自己的。</p>
        <p class="text-lg text-slate-500 mt-1">頁碼怎麼算：封面 1、目錄 2、行程規劃 3、路線圖 4，之後<b>一站一頁</b>往後數。</p>
      </div>
      <div class="sc-slide sc-split">
        <div class="sc-txt">
          <p class="sc-t">目錄要<b>靠左</b>，前面加<b>圓點</b></p>
          <p class="text-lg text-slate-500 mt-2">連按兩下 → <kbd>Ctrl</kbd> + <kbd>A</kbd> →「對齊」按到靠左 →「項目符號」。</p>
        </div>
        <div class="sc-media" data-src="assets/步_canva_目錄靠左列點.mp4" data-poster="assets/步_canva_目錄靠左列點_封面.jpg"></div>
      </div>
    </div>

    <div class="bg-white border-4 border-teal-200 rounded-3xl p-4 mt-4 text-xl">
      <p class="cute text-2xl font-extrabold text-teal-700 mb-2">這一步檢查</p>
      <label class="flex items-center gap-3 mb-2"><input type="checkbox" class="chk w-6 h-6"> 第 2 頁有「<b>目錄</b>」標題</label>
      <label class="flex items-center gap-3 mb-2"><input type="checkbox" class="chk w-6 h-6"> 每一行都有<b>章節名</b>和<b>頁碼</b>，景點名是我的</label>
      <label class="flex items-center gap-3"><input type="checkbox" class="chk w-6 h-6"> 目錄<b>靠左</b>，每行前面有<b>圓點</b></label>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP6 = r'''
  <!-- 步驟 6：交作業 -->
  <section class="step hidden bg-white border-4 border-rose-300 rounded-3xl p-5 shadow-sm" data-step="6">
    <h2 class="cute text-3xl font-extrabold text-rose-700 mb-3">貼連結，交作業</h2>

    <div class="sc sc-flat" data-sc>
      <div class="sc-slide sc-split">
        <div class="sc-txt">
          <p class="sc-t">按 <b>分享</b> → <b>存取等級</b>（誰可以看）→ 選<b>任何具有此連結者</b></p>
          <p class="text-xl font-extrabold text-rose-700 mt-2">右邊要改成<b>可供檢視</b>（只能看）！</p>
          <p class="text-lg text-slate-500">預設是「可供編輯」，別人會改到你的作品。</p>
          <p class="text-lg font-bold text-slate-700 mt-1">最後按<b>複製連結</b>。</p>
        </div>
        <div class="sc-media" data-src="assets/步_canva_分享連結.mp4" data-poster="assets/步_canva_分享連結_封面.jpg"></div>
      </div>
      <div class="sc-slide">
        <p class="sc-t">回這裡，把連結<b>貼上</b></p>
        <label class="block text-xl font-extrabold mb-1" for="canvaLink">Canva 連結</label>
        <input id="canvaLink" type="text" autocomplete="off" class="w-full border-4 border-slate-300 rounded-2xl px-4 py-2 text-lg font-bold focus:border-rose-400 outline-none">
        <p id="linkMsg" class="text-lg font-bold mt-1 min-h-[28px]"></p>
        <p class="text-base text-slate-500"><kbd>Ctrl</kbd> + <kbd>V</kbd> 貼上。</p>
      </div>
    </div>
    <p class="text-lg font-bold text-slate-600 mt-3">來不及做完？貼目前的連結先交，之後還能再交一次。</p>

    <div class="bg-white border-4 border-teal-200 rounded-3xl p-4 mt-4 text-xl">
      <p class="cute text-2xl font-extrabold text-teal-700 mb-2">交之前檢查</p>
      <label class="flex items-center gap-3 mb-2"><input type="checkbox" class="chk w-6 h-6"> 連結<b>貼好</b>了（顯示 ✓）</label>
      <label class="flex items-center gap-3 mb-2"><input type="checkbox" class="chk w-6 h-6"> 權限是<b>可供檢視</b>（不是可供編輯）</label>
      <label class="flex items-center gap-3"><input type="checkbox" class="chk w-6 h-6"> 我開<b>新標籤</b>貼上連結，打得開</label>
    </div>

    <div class="bg-orange-50 border-4 border-orange-300 rounded-3xl p-4 mt-4">
      <p class="cute text-2xl font-extrabold text-orange-700 mb-2">交出去</p>
      <p class="text-xl font-bold">最後，按下面的「<span class="text-orange-700">繳交學習單</span>」</p>
      <button id="submitBtn" class="mt-4 w-full bg-orange-600 hover:bg-orange-700 text-white cute text-2xl font-extrabold rounded-2xl py-3">繳交學習單</button>
      <p id="submitStat" class="text-sm font-bold mt-2 min-h-[20px] text-center"></p>
    </div>

    <div id="rewardBox" class="hidden text-center bg-gradient-to-b from-amber-100 to-orange-100 border-4 border-amber-300 rounded-3xl p-6 mt-4">
      <h3 class="cute text-2xl font-extrabold text-orange-700">恭喜你已經做完今日的作業，可以遊玩！</h3>
      <div class="flex flex-wrap gap-3 justify-center mt-3">
        <a href="__PORTAL__" target="_blank" rel="noopener"
           class="cute inline-block bg-orange-600 hover:bg-orange-700 text-white text-lg font-extrabold rounded-2xl px-6 py-2">電腦教室遊戲網站</a>
      </div>
    </div>

    <div class="mt-6 bg-amber-50 border-4 border-amber-200 rounded-3xl p-4">
      <p class="cute text-xl font-extrabold text-amber-700 mb-2">文件資料還沒做完？回去補</p>
      <div class="flex flex-wrap gap-3">
        <a href="https://boyinslps.github.io/pcclass/g4/L07/" target="_blank" rel="noopener" class="inline-block bg-white border-4 border-amber-300 hover:bg-amber-50 text-amber-700 text-lg font-extrabold rounded-2xl px-5 py-2">L07 學習單（文件檢查）↗</a>
        <a href="https://boyinslps.github.io/pcclass/g4/L04/" target="_blank" rel="noopener" class="inline-block bg-white border-4 border-amber-300 hover:bg-amber-50 text-amber-700 text-lg font-extrabold rounded-2xl px-5 py-2">L04 學習單（選景點）↗</a>
      </div>
    </div>
    <div class="stepnav"></div>
  </section>

</div>

<footer class="max-w-5xl mx-auto px-4 pb-6 text-right text-xs text-slate-400">made by 資訊老師黃博胤</footer>
'''

SCRIPT = r'''
<script>
var firebaseConfig = {
  apiKey:"AIzaSyAaodBvsP-BSovON14izt22DOXeH40TTGM",
  authDomain:"pcclass-94300.firebaseapp.com",
  projectId:"pcclass-94300",
  storageBucket:"pcclass-94300.firebasestorage.app",
  messagingSenderId:"1034787516465",
  appId:"1:1034787516465:web:73c334b2ddad152c472510",
  measurementId:"G-37P75R7TZ7"
};

(function(){
  function $(id){return document.getElementById(id);}
  function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
  var WS='g4-L08';

  // ===== 識別列 =====
  var ID_KEY='wk_identity';
  function digits(s){return String(s||'').replace(/[^0-9]/g,'');}
  function loadIdentity(){try{return JSON.parse(localStorage.getItem(ID_KEY)||'{}')}catch(e){return {}}}
  function saveIdentity(o){try{localStorage.setItem(ID_KEY,JSON.stringify(o))}catch(e){}}
  function getIdentity(){
    var g=digits($('idGrade').value),c=digits($('idClass').value),s=digits($('idStudent').value);
    return {grade:g?Number(g):null,className:c?Number(c):null,studentId:s?Number(s):null};
  }
  function identityValid(id){return id.grade!=null&&id.className!=null&&id.className>=1&&id.className<=14&&id.studentId!=null;}
  function pad2(n){return (n<10?'0':'')+n;}
  // 作品名字：年級 1 位＋班級 2 位＋座號 2 位＋空格＋我的台南手冊（例：40205 我的台南手冊）
  function projName(){var i=getIdentity();return identityValid(i)?(i.grade+pad2(i.className)+pad2(i.studentId)+' 我的台南手冊'):'';}
  function showProj(){var n=projName();$('projName').textContent=n||'先填上面的年級、班級、座號';}
  (function initIdentity(){
    var saved=loadIdentity();
    if(saved.grade)$('idGrade').value=saved.grade;
    if(saved.className)$('idClass').value=saved.className;
    if(saved.studentId)$('idStudent').value=saved.studentId;
    if(identityValid(saved))$('idOk').classList.remove('hidden');
    ['idGrade','idClass','idStudent'].forEach(function(id){
      var e=$(id);
      e.addEventListener('input',function(){
        var d=digits(e.value);if(d!==e.value)e.value=d;
        var idn=getIdentity();
        if(identityValid(idn)){saveIdentity(idn);$('idOk').classList.remove('hidden');}
        else $('idOk').classList.add('hidden');
        showProj();
      });
    });
    showProj();
  })();

  // ===== Firebase：只用來寫入繳交 =====
  var db=null,auth=null;
  function loadScript(src){return new Promise(function(res,rej){var s=document.createElement('script');s.src=src;s.onload=res;s.onerror=rej;document.head.appendChild(s)})}
  function ensureAuth(){return (auth&&auth.currentUser)?Promise.resolve(auth.currentUser):auth.signInAnonymously().then(function(c){return c.user});}
  (function boot(){
    var base='https://www.gstatic.com/firebasejs/10.8.0/';
    loadScript(base+'firebase-app-compat.js')
      .then(function(){return loadScript(base+'firebase-auth-compat.js')})
      .then(function(){return loadScript(base+'firebase-firestore-compat.js')})
      .then(function(){firebase.initializeApp(firebaseConfig);db=firebase.firestore();auth=firebase.auth();})
      .catch(function(e){console.warn('Firebase 啟用失敗，改用單機模式',e);});
  })();

  function copyText(text,btn){
    var old=btn.textContent;
    function done(){btn.textContent='✓ 已複製';setTimeout(function(){btn.textContent=old;},2000);}
    function fallback(){
      var ta=document.createElement('textarea');ta.value=text;ta.style.cssText='position:fixed;left:-9999px;top:0';
      document.body.appendChild(ta);ta.select();
      try{document.execCommand('copy');done();}catch(e){btn.textContent='請按 Ctrl+C 複製';}
      document.body.removeChild(ta);
    }
    try{navigator.clipboard.writeText(text).then(done,fallback);}catch(e){fallback();}
  }
  $('projCopy').onclick=function(){var n=projName();if(!n){alert('先在最上方填好年級、班級、座號。');window.scrollTo({top:0,behavior:'smooth'});return;}copyText(n,this);};

  // ===== 步驟 1：這些字放哪一頁？（配對，立即回饋；全對才算完成）=====
  var QUIZ=[
    {t:'書名「我的台南一日小旅行」',a:'封面',why:'書名放在封面'},
    {t:'第 1 站　赤崁樓　5',a:'目錄',why:'章節和頁碼，是目錄'},
    {t:'09:00 赤崁樓　10:30 安平古堡',a:'行程規劃',why:'幾點到哪裡，放行程規劃'},
    {t:'Google 地圖畫的路線截圖',a:'路線圖',why:'地圖路線，放路線圖'},
    {t:'歷史、看點、特色、地址、照片',a:'景點頁',why:'每一站的介紹和資料，放景點頁'},
    {t:'謝謝你和我一起去玩！',a:'封底',why:'最後一頁是封底'}
  ];
  var QOPTS=['封面','目錄','行程規劃','路線圖','景點頁','封底'],quizDone={};
  (function buildQuiz(){
    var host=$('quiz');
    QUIZ.forEach(function(q,qi){
      var row=el('div','bg-white border-2 border-amber-200 rounded-2xl p-3');
      row.appendChild(el('p','text-xl font-extrabold mb-2',q.t));
      var btns=el('div','flex flex-wrap items-center gap-2');
      var fb=el('span','text-lg font-extrabold ml-2');
      QOPTS.forEach(function(o){
        var b=el('button','ptype',o);b.type='button';
        b.onclick=function(){
          if(o===q.a){
            quizDone[qi]=true;fb.className='text-lg font-extrabold ml-2 text-emerald-700';fb.textContent='✓ '+q.why;
            [].forEach.call(btns.querySelectorAll('button'),function(x){x.classList.toggle('on',x===b);});
          }else{fb.className='text-lg font-extrabold ml-2 text-amber-700';fb.textContent='再想想';}
          var n=Object.keys(quizDone).length,ok=n===QUIZ.length;
          $('quizMsg').textContent=ok?'全對了！手冊的頁都認得了。':'';
          $('quizMsg').className='text-xl font-extrabold mt-3 min-h-[32px] '+(ok?'text-emerald-700':'');
          var c=$('quizOk');if(c.checked!==ok){c.checked=ok;}
          renderStepper();
        };
        btns.appendChild(b);
      });
      btns.appendChild(fb);row.appendChild(btns);host.appendChild(row);
    });
  })();

  // ===== 介面小測驗（看截圖選功能）=====
  var FQ=[
    {img:'assets/介面題_左邊.jpg',q:'橘色框起來的左邊這一排，是做什麼的？',o:['要加文字、照片、圖形，來這裡','看這份作品有幾頁','把作品分享給老師','改作品的名字'],a:0,why:'左邊工具列：要加東西，來這裡'},
    {img:'assets/介面題_右上.jpg',q:'橘色框起來的「分享」，是做什麼的？',o:['把字變大','做好了，從這裡拿連結','多一張新的紙','換顏色'],a:1,why:'分享：做好了，從這裡拿連結'},
    {img:'assets/介面題_下方.jpg',q:'橘色框起來的「＋」，按了會怎樣？',o:['刪掉這份作品','把照片放大','多一張新的紙','存到電腦'],a:2,why:'＋：多一張新的紙'},
    {img:'assets/介面題_名字.jpg',q:'點一下橘色框起來的名字，可以做什麼？',o:['換下一頁','加照片','拿分享連結','改作品的名字'],a:3,why:'點作品名字，可以改名'}
  ],fqDone={};
  (function buildFaceQuiz(){
    var host=$('faceQuiz');if(!host)return;
    FQ.forEach(function(q,qi){
      var row=el('div','bg-white border-2 border-amber-200 rounded-2xl p-3');
      var im=el('img','');im.src=q.img;im.alt='Canva 畫面的一小塊';im.style.cssText='max-width:100%;max-height:340px;border-radius:10px;border:2px solid #e2e8f0;margin-bottom:8px;display:block';
      row.appendChild(im);
      row.appendChild(el('p','text-xl font-extrabold mb-2',(qi+1)+'. '+q.q));
      var btns=el('div','flex flex-wrap items-center gap-2');
      var fb=el('span','text-lg font-extrabold ml-2');
      q.o.forEach(function(o,oi){
        var b=el('button','ptype',o);b.type='button';
        b.onclick=function(){
          if(oi===q.a){
            fqDone[qi]=true;fb.className='text-lg font-extrabold ml-2 text-emerald-700';fb.textContent='✓ '+q.why;
            [].forEach.call(btns.querySelectorAll('button'),function(x){x.classList.toggle('on',x===b);});
          }else{fb.className='text-lg font-extrabold ml-2 text-amber-700';fb.textContent='再想想';}
          var ok=Object.keys(fqDone).length===FQ.length;
          $('faceMsg').textContent=ok?'全對了！每個區都認得了。':'';
          $('faceMsg').className='text-xl font-extrabold mt-3 min-h-[32px] '+(ok?'text-emerald-700':'');
          var c=$('faceOk');if(c.checked!==ok){c.checked=ok;}
          renderStepper();
        };
        btns.appendChild(b);
      });
      btns.appendChild(fb);row.appendChild(btns);host.appendChild(row);
    });
  })();

  // ===== 點小圖放大（留在這一頁，不開新分頁）=====
  (function zoom(){
    var ov=el('div','hidden fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4');
    ov.style.cursor='zoom-out';
    var im=el('img','');im.style.cssText='max-width:100%;max-height:100%;border-radius:12px;background:#fff';
    ov.appendChild(im);document.body.appendChild(ov);
    function close(){ov.classList.add('hidden');}
    ov.onclick=close;document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
    document.addEventListener('click',function(e){
      var t=e.target;if(t&&t.classList&&t.classList.contains('zoomable')){im.src=t.getAttribute('src');ov.classList.remove('hidden');}
    });
  })();

  // ===== 交作業：Canva 連結 =====
  // 接受：https://www.canva.com/design/<id>/<token>/view（分享連結）、https://canva.link/…；編輯連結（…/edit）提醒改成可供檢視。
  function linkKind(v){
    v=String(v||'').trim();
    if(/^https:\/\/(www\.)?canva\.com\/design\/[A-Za-z0-9_-]{8,}\/[A-Za-z0-9_-]+\/edit/.test(v))return 'edit';
    if(/^https:\/\/(www\.)?canva\.com\/design\/[A-Za-z0-9_-]{8,}/.test(v)||/^https:\/\/canva\.link\/[A-Za-z0-9]+/.test(v))return 'ok';
    return 'bad';
  }
  function linkOk(v){return linkKind(v)==='ok';}
  function showLink(){
    var v=($('canvaLink').value||'').trim(),m=$('linkMsg'),k=linkKind(v);
    if(!v){m.textContent='';m.className='text-lg font-bold mt-1 min-h-[28px]';}
    else if(k==='ok'){m.textContent='✓ 連結對了';m.className='text-lg font-bold mt-1 min-h-[28px] text-emerald-700';}
    else if(k==='edit'){m.textContent='這是「可供編輯」的連結。回 Canva 改成「可供檢視」再複製';m.className='text-lg font-bold mt-1 min-h-[28px] text-amber-700';}
    else{m.textContent='要貼 canva.com 開頭的連結';m.className='text-lg font-bold mt-1 min-h-[28px] text-amber-700';}
    renderStepper();
  }
  $('canvaLink').addEventListener('input',showLink);
  $('canvaLink').addEventListener('paste',function(){setTimeout(showLink,0);});

  // ===== 繳交學習單 =====
  // 定位：全部是體驗題（不計分）。老師從 q1 的 Canva 連結開手冊看；q2＝開 B5 與認識介面自查、q3＝封面自查、q4＝目錄自查、q5＝手冊頁配對全對。
  function workDocId(idn){return WS+'__'+idn.grade+'-'+idn.className+'-'+idn.studentId;}
  function stepChecksDone(n){
    var cs=document.querySelectorAll('.step[data-step="'+n+'"] input.chk');
    if(!cs.length)return false;
    for(var i=0;i<cs.length;i++)if(!cs[i].checked)return false;
    return true;
  }
  $('submitBtn').onclick=function(){
    var idn=getIdentity();
    if(!identityValid(idn)){alert('請先在最上方填好年級、班級、座號（都是數字，班級是 1 到 14）。');window.scrollTo({top:0,behavior:'smooth'});return;}
    var url=($('canvaLink').value||'').trim();
    if(!linkOk(url)){alert('先把 Canva 的分享連結貼在「Canva 連結」格子裡。');$('canvaLink').focus();return;}
    if(!db){alert('系統尚未連線，請稍後再試或重新整理頁面。');return;}
    var quizOk=!!$('quizOk').checked,openDone=stepChecksDone(2)&&stepChecksDone(3),coverDone=stepChecksDone(4),tocDone=stepChecksDone(5);
    var experienceAnswers={
      q1:{given:{url:url},correct:null,isCorrect:true},
      q2:{given:openDone,correct:null,isCorrect:openDone},
      q3:{given:coverDone,correct:null,isCorrect:coverDone},
      q4:{given:tocDone,correct:null,isCorrect:tocDone},
      q5:{given:quizOk,correct:null,isCorrect:quizOk}};
    var answers={q1:{url:url},q2:openDone,q3:coverDone,q4:tocDone,q5:quizOk},qtypes={q1:'experience',q2:'experience',q3:'experience',q4:'experience',q5:'experience'};
    var experienceCompletion=Math.round((1+(openDone?1:0)+(coverDone?1:0)+(tocDone?1:0)+(quizOk?1:0))/5*100);
    var msg='確定要繳交學習單嗎？\nCanva 連結：已貼\n封面檢查：'+(coverDone?'都勾了':'還沒全勾')+'\n目錄檢查：'+(tocDone?'都勾了':'還沒全勾')+'\n各頁用途配對：'+(quizOk?'全對':'還沒全對');
    if(!confirm(msg))return;
    var payload={worksheetId:WS,worksheetTitle:'台南小導遊養成記：Canva 導覽手冊（開 B5、認識介面、封面與目錄）',lessonPath:'g4/L08',
      grade:idn.grade,className:idn.className,studentId:idn.studentId,
      answers:answers,qtypes:qtypes,
      qtexts:{
        q1:'學生貼上的 Canva 分享連結（老師開連結看手冊：封面與目錄）。',
        q2:'開 B5 空白文件、改作品名字、認識編輯畫面的自我檢查是否都勾選。',
        q3:'封面自我檢查（選範本、書名、三個景點、調整字型大小位置；照片之後再放）是否都勾選。',
        q4:'目錄自我檢查（標題、章節與頁碼、景點名、靠左與圓點）是否都勾選。',
        q5:'手冊各頁用途配對（封面、目錄、行程規劃、路線圖、景點頁、封底）是否全對。'
      },
      bonusQids:[],
      scoreAnswers:{},experienceAnswers:experienceAnswers,openAnswers:{},bonusAnswers:{},
      accuracyRate:null,experienceCompletion:experienceCompletion,
      status:'submitted',submittedAt:firebase.firestore.FieldValue.serverTimestamp()};
    var btn=this,stat=$('submitStat');
    btn.disabled=true;stat.className='text-sm font-bold mt-2 min-h-[20px] text-center text-orange-600';stat.textContent='繳交中…';
    ensureAuth().then(function(){return db.collection('submissions').doc(workDocId(idn)).set(payload,{merge:true});})
      .then(function(){
        btn.disabled=false;btn.textContent='重新繳交（覆蓋）';
        stat.className='text-sm font-bold mt-2 min-h-[20px] text-center text-emerald-600';
        stat.textContent='✓ 已繳交！';submittedOnce=true;renderStepper();
        var rb=$('rewardBox');rb.classList.remove('hidden');rb.scrollIntoView({behavior:'smooth'});
      }).catch(function(e){
        console.warn('繳交失敗',e);btn.disabled=false;
        stat.className='text-sm font-bold mt-2 min-h-[20px] text-center text-amber-600';
        stat.textContent='繳交失敗，請檢查網路後再按一次；還是不行就告訴老師。';
      });
  };

  // ===== 學習路徑 =====
  var STEP_NAMES=['看手冊','開B5','認識介面','封面','目錄','交作業'];
  var stepEls=[].slice.call(document.querySelectorAll('.step'));
  var curStep=1,visited={1:true},submittedOnce=false;
  function stepDone(n){
    if(n===STEP_NAMES.length)return submittedOnce;
    var cs=stepEls[n-1].querySelectorAll('input.chk');
    if(!cs.length)return !!visited[n]&&n!==curStep;
    for(var i=0;i<cs.length;i++)if(!cs[i].checked)return false;
    return true;
  }
  function renderStepper(){
    var host=$('stepper');host.innerHTML='';
    STEP_NAMES.forEach(function(name,idx){
      var n=idx+1,cur=n===curStep,done=stepDone(n);
      var cell=el('div','flex flex-col items-center');
      var b=el('button','stepdot cute rounded-full border-2 font-extrabold text-sm flex items-center justify-center transition '+
        (cur?'bg-orange-500 border-orange-500 text-white':(done?'bg-emerald-500 border-emerald-500 text-white':'bg-white border-slate-300 text-slate-400 hover:border-orange-300')));
      b.type='button';
      b.textContent=done&&!cur?'✓':String(n);
      b.setAttribute('aria-label','第 '+n+' 步：'+name);
      if(cur)b.setAttribute('aria-current','step');
      b.onclick=function(){showStep(n);};
      cell.appendChild(b);
      cell.appendChild(el('span','hidden sm:block text-xs font-bold mt-0.5 '+(cur?'text-orange-600':'text-slate-400'),name));
      host.appendChild(cell);
      if(n<STEP_NAMES.length)host.appendChild(el('div','flex-1 h-0.5 mt-3.5 sm:mt-4 mx-0.5 sm:mx-1 rounded '+(done&&!cur?'bg-emerald-300':'bg-slate-200')));
    });
    $('stepLabel').textContent='第 '+curStep+' 步／共 '+STEP_NAMES.length+' 步 · '+STEP_NAMES[curStep-1];
  }
  function showStep(n){
    curStep=n;visited[n]=true;
    stepEls.forEach(function(s){s.classList.toggle('hidden',Number(s.dataset.step)!==n);});
    renderStepper();
    window.scrollTo({top:0,behavior:'smooth'});
  }
  stepEls.forEach(function(s){
    var n=Number(s.dataset.step),nav=s.querySelector('.stepnav');
    if(n>1){var p=el('button','bg-white border-2 border-slate-300 hover:border-orange-400 text-slate-600 font-bold rounded-2xl px-5 py-2','← 上一步');p.type='button';p.onclick=function(){showStep(n-1);};nav.appendChild(p);}
    else nav.appendChild(el('span',''));
    if(n<STEP_NAMES.length){var x=el('button','cute bg-orange-500 hover:bg-orange-600 text-white text-lg font-extrabold rounded-2xl px-6 py-2','下一步：'+STEP_NAMES[n]+' →');x.type='button';x.onclick=function(){showStep(n+1);};nav.appendChild(x);}
  });
  document.addEventListener('change',function(e){if(e.target&&e.target.classList&&e.target.classList.contains('chk'))renderStepper();});
  renderStepper();
})();
</script>
'''


def build():
    html = (HEAD + STEP1 + STEP2 + STEP3 + STEP4 + STEP5 + STEP6 + SCRIPT + '\n</body>\n</html>\n')
    html = (html.replace('__PAGES__', pages_grid()).replace('__PORTAL__', PORTAL)
            .replace('__CANVA_HOME__', CANVA_HOME).replace('__TWTAINAN__', TWTAINAN))
    os.makedirs(OUTDIR, exist_ok=True)
    with io.open(OUT, 'w', encoding='utf-8', newline='') as f:
        f.write(html)
    print('寫出', OUT, len(html), '字元')


if __name__ == '__main__':
    build()
