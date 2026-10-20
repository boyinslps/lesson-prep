# -*- coding: utf-8 -*-
# 產生五上 L05、L06 兩份學習單（高年級：一個環節一步的步驟分頁）。
# 骨架（識別列、教師列、進度列、點圖放大、Firebase 登入）直接取自五上 L04，確保行為一致；
# 內容與題目寫在下面。生成後請執行 引導規範/chair-gate/inject.py 內嵌「靠椅子」關卡。
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l05_steps as L5S            # 第 6、7 步（回想、一欄一卡）
ROOT = os.path.dirname(HERE)            # materials/五年級上學期
L04 = os.path.join(ROOT, 'L04_認識農場文與業配文', '五上_L04_認識農場文與業配文.html')
lines = io.open(L04, encoding='utf8').read().split('\n')

def seg(a, b):   # 1-based, inclusive
    return '\n'.join(lines[a - 1:b])

CSS = seg(11, 49)                       # <style>…</style>
TOPBARS = seg(53, 93)                   # 檢視橫幅、教師列、識別列、進度列
LIGHTBOX = seg(502, 513)
SL_PH = seg(536, 570)                   # 圖片佔位＋點圖放大
SL_ID = seg(572, 599)                   # 識別列邏輯
SL_FB = seg(601, 618)                   # Firebase 載入與登入狀態
ENGINE = io.open(os.path.join(HERE, 'engine.js'), encoding='utf8').read()
ENGINE = (ENGINE.replace('/*L04SLICE:phimg_lightbox*/', SL_PH)
                .replace('/*L04SLICE:identity*/', SL_ID)
                .replace('/*L04SLICE:firebase*/', SL_FB))
FBCFG = seg(516, 525)                   # firebaseConfig（沿用 pcclass-94300）

DOC = 'https://docs.google.com/document/d/1e4-lD9lyZJgRPma8_7A3e3fn0y1M8M9Z1oqZF1gI0n4/edit'

REWARD = '''
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-5 shadow-sm text-center mt-6">
      <h2 class="cute text-xl font-extrabold text-indigo-700 mb-1">📮 繳交學習單</h2>
      <p class="text-sm text-slate-500 mb-3">確定都填好了嗎？按下面按鈕交給老師（可以重交，會覆蓋前一次）。</p>
      <button id="submitBtn" class="w-full bg-indigo-600 hover:bg-indigo-700 text-white cute text-xl font-extrabold rounded-2xl py-3">繳交學習單</button>
      <p id="submitStat" class="text-sm font-bold mt-3 min-h-[20px]"></p>
    </div>

    <div id="rewardBox" class="hidden text-center bg-gradient-to-b from-indigo-100 to-sky-100 border-4 border-indigo-300 rounded-3xl p-7 mt-6">
      <div class="text-6xl mb-2 pop">🎉</div>
      <h2 class="cute text-3xl font-extrabold text-indigo-700">恭喜你已經做完今日的作業，可以遊玩！</h2>
      <div class="flex flex-wrap gap-3 justify-center mt-4">
        <a href="https://boyinslps.github.io/typehero/index.html" target="_blank" rel="noopener" class="cute inline-block bg-indigo-600 hover:bg-indigo-700 text-white text-xl font-extrabold rounded-2xl px-8 py-3">🎮 打字英雄</a>
        <a href="https://gemini.google.com/share/0adbaeae6c16?skid=751ce4ac-860d-4160-8a1a-12a1ebcf6f1d" target="_blank" rel="noopener" class="cute inline-block bg-white border-4 border-indigo-300 hover:bg-indigo-50 text-indigo-700 text-xl font-extrabold rounded-2xl px-8 py-3">🕹️ 更多遊戲</a>
      </div>
    </div>'''

def page(title, h1, sub, body, cfg, hooks, spec, extra_css=''):
    return ('<!DOCTYPE html>\n<html lang="zh-Hant">\n<head>\n<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '<meta name="author" content="資訊老師黃博胤">\n'
            '<title>%s</title>\n<script src="https://cdn.tailwindcss.com"></script>\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">\n'
            '%s\n</head>\n<body class="text-slate-800">\n\n%s\n\n'
            '<div id="main" class="max-w-5xl mx-auto px-4 py-6">\n\n'
            '  <header class="text-center mb-6">\n'
            '    <h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">%s</h1>\n'
            '    <p class="text-sm text-slate-500 mt-2">%s</p>\n'
            '    <p id="syncBadge" class="hidden mt-2 text-xs text-emerald-600 font-bold">🔗 已連線：老師公布答案時，這台會自動同步</p>\n'
            '  </header>\n\n%s\n\n'
            '  <footer class="text-center text-xs text-slate-400 mt-8 pb-2">教師公布答案：在網址列加上 <code class="bg-slate-200 rounded px-1">#admin</code> 後重新整理。查核文章與網傳擷圖取自台灣事實查核中心、MyGoPen 查核報告。</footer>\n'
            '  <p class="text-right text-xs text-slate-400 pb-4">made by 資訊老師黃博胤</p>\n</div>\n\n%s\n\n'
            '<script>\n%s\n\n%s\n</script>\n\n'
            '<script type="application/json" id="grading-spec">\n%s\n</script>\n'
            '</body>\n</html>\n') % (
        title, CSS + EXTRA_CSS + extra_css, TOPBARS, h1, sub, body, LIGHTBOX, FBCFG,
        ENGINE.replace('/*CONFIG*/', json.dumps(cfg, ensure_ascii=False)).replace('/*HOOKS*/', hooks),
        json.dumps(spec, ensure_ascii=False, indent=2))

EXTRA_CSS = '''
<style>
  .pickcard{transition:.15s}
  .pickcard.on{border-color:#6366f1;background:#eef2ff;box-shadow:0 0 0 4px #c7d2fe}
  .bubble{background:#e8f0fe;border-radius:16px;padding:10px 14px;font-size:1.05rem;line-height:1.7}
  .playov{position:relative}
  .playov:after{content:'▶';position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:64px;height:64px;line-height:64px;text-align:center;border-radius:999px;background:rgba(0,0,0,.62);color:#fff;font-size:28px;pointer-events:none}
  .dur{position:absolute;right:8px;bottom:8px;background:rgba(0,0,0,.75);color:#fff;font-size:13px;font-weight:700;border-radius:6px;padding:1px 6px;z-index:2}
  .src{font-size:.9rem;margin-top:.5rem}
</style>'''

def vid(src, poster, cap=''):
    return ('<video class="w-full max-w-[560px] mx-auto rounded-2xl bg-slate-900" src="assets/%s" poster="assets/%s" controls playsinline preload="none"></video>'
            '<p class="text-[11px] text-slate-400 mt-1 text-center">%s</p>') % (src, poster, cap)

LINKS = '''<a href="https://tfc-taiwan.org.tw/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2"><img src="https://www.google.com/s2/favicons?domain=tfc-taiwan.org.tw&sz=64" class="w-5 h-5 bg-white rounded" alt="">台灣事實查核中心 ↗</a>
          <a href="https://www.mygopen.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2"><img src="https://www.google.com/s2/favicons?domain=mygopen.com&sz=64" class="w-5 h-5 bg-white rounded" alt="">MyGoPen 麥擱騙 ↗</a>'''

FIELDS7 = [
    ('1', '查核網址', '整條網址（貼在標題下面）', True),
    ('2', '我選的訊息', '用自己的話說：這則訊息在講什麼', True),
    ('3', '我怎麼找到查核文章的', '用了哪個關鍵詞、哪張圖', True),
    ('4', '查核結果', '查核機構標了什麼？是哪一家？', True),
    ('5', '為什麼這則訊息會被廣傳？', '它讓人怕？好奇？還是關心家人？', False),
    ('6', '正確資訊', '查核文章說的事實，用自己的話整理', False),
    ('7', '如果相信的話，會有什麼後果？', '誰會怎樣？', False),
]
def chips7(today_cls, later_cls):
    out = []
    for n, t, d, today in FIELDS7:
        cls = today_cls if today else later_cls
        out.append('<div class="%s rounded-2xl p-3"><p class="font-bold">%s ‧ %s</p><p class="text-sm text-slate-600 mt-0.5">%s</p></div>' % (cls, n, t, d))
    return '\n        '.join(out)

# =====================================================================
# L05 第 4 步：6 張選題卡（用函式組，方便統一版型）
# =====================================================================
L05_ASSETS = os.path.join(ROOT, 'L05_Docs查證文件一', 'assets')
YT_E = 'https://www.youtube.com/watch?v=P-tHhvtJFOw'   # 中視新聞：慢跑男遭雷擊亡
YT_H = 'https://www.youtube.com/watch?v=kTMSfHKNrq4'   # 手機充電時講電話喝水（短劇）

def stars(n, why=''):
    return ('<div class="mt-2"><span class="inline-block bg-amber-50 border-2 border-amber-300 text-amber-600 font-extrabold rounded-lg px-2 py-0.5 tracking-wider" title="查證難易度：星星越多越難">%s</span></div>') % ('★' * n + '☆' * (3 - n))

def srcbtn(url, label):
    return ('<a href="%s" target="_blank" rel="noopener" class="mt-3 flex items-center justify-center gap-2 w-full cute bg-sky-600 hover:bg-sky-700 text-white text-lg font-extrabold rounded-2xl py-2.5">%s ↗</a>'
            % (url, label))

def nosrc(text):
    return '<p class="src text-slate-500">🔗 原始來源：%s</p>' % text

def img(src, alt, cap):
    return ('<img class="shotimg mt-3" src="assets/%s" alt="%s" loading="lazy">'
            '<p class="text-[11px] text-slate-400 mt-1">%s・點圖可放大</p>') % (src, alt, cap)

def video(fname, poster, yturl, cap):
    """影片檔在 assets/ 就直接內嵌；還沒放進來就先顯示封面，點了連去 YouTube。"""
    if os.path.exists(os.path.join(L05_ASSETS, fname)):
        return ('<video class="w-full max-h-[440px] rounded-2xl bg-slate-900 mt-3" src="assets/%s" poster="assets/%s" controls playsinline preload="none"></video>'
                '<p class="text-[11px] text-slate-400 mt-1">%s</p>') % (fname, poster, cap)
    return ('<a href="%s" target="_blank" rel="noopener" class="playov block mt-3"><img class="w-full rounded-2xl border-3 border-slate-300" src="assets/%s" alt="影片封面" loading="lazy"></a>'
            '<p class="text-[11px] text-slate-400 mt-1">%s（影片檔還沒放進來，點封面到 YouTube 看）</p>') % (yturl, poster, cap)

def card(key, title, body, star):
    return ('      <div class="pickcard border-4 border-slate-200 bg-white rounded-3xl p-5 flex flex-col" data-card="%s">\n'
            '        <p class="cute text-xl font-extrabold text-indigo-700">%s</p>\n'
            '        %s\n        %s\n'
            '        <button type="button" data-pick="%s" class="mt-3 w-full cute bg-indigo-600 hover:bg-indigo-700 text-white text-lg font-extrabold rounded-2xl py-2">選這則</button>\n'
            '      </div>') % (key, title, star, body, key)

CARDS = '\n'.join([
    card('C', 'C ‧ 幫忙投票給繪畫比賽的小朋友',
         img('M2_C_繪畫比賽投票_LINE訊息重製.png', 'LINE 訊息：親戚家小孩繪畫比賽，麻煩幫我投下 7 號小朋友，謝謝，後面附一個網址和比賽縮圖卡', '依網傳訊息重製（網址已隱藏）'),
         stars(1)),
    card('D', 'D ‧ 微波爐加熱的食物有輻射',
         img('M2_D_微波爐輻射_網傳訊息.jpg', 'LINE 轉傳訊息：日本政府決定年底前處理所有微波爐，因為廣島大學研究發現微波爐加熱的食物含有輻射，韓國、中國也跟進', '網傳訊息擷圖'),
         stars(2)),
    card('E', 'E ‧ 打雷戴藍芽耳機會被雷擊',
         img('M2_E_打雷藍芽耳機_網傳訊息1.png', 'LINE 轉傳訊息：在戶外遇到打雷時，絕對不用手機接聽電話或上網，苗栗健身教練打雷時在慢跑，疑似使用藍芽耳機，不幸遭雷擊而亡', '網傳訊息擷圖')
         + video('M2_E_打雷藍芽耳機_新聞影片.mp4', 'M2_E_打雷藍芽耳機_新聞影片_封面.jpg', YT_E, '訊息提到的新聞影片（中視新聞）'),
         stars(3)),
    card('G', 'G ‧ 印度街頭小吃加了水溝水',
         (video('M2_G_印度街頭小吃_原始影片.mp4', 'M2_G_印度街頭小吃_原始影片_封面.jpg', 'https://x.com/sapnamadan/status/2095878992813568031', '網傳的影片（原始版本）')
          if os.path.exists(os.path.join(L05_ASSETS, 'M2_G_印度街頭小吃_原始影片.mp4')) else
          img('M2_G_印度街頭小吃_網傳貼文.png', '臉書貼文：高貴外國人系列，印度街頭小吃影片，一名婦人在水溝旁洗鍋碗，再把水溝的水加進煮好的食物裡', '網傳貼文擷圖（發文者已遮蔽）')),
         stars(2)),
    card('H', 'H ‧ 充電時講電話不能喝水',
         video('M2_H_充電講電話喝水_原始影片.mp4', 'M2_H_充電講電話喝水_原始影片_封面.jpg', YT_H, '網傳的影片（原始版本）。這支影片可以用「以圖搜圖」查'),
         stars(1)),
    card('K', 'K ‧ 地震要躲在「生命三角」',
         img('M2_K_地震逃生_網傳訊息1.jpg', '臉書貼文：我哥傳 Line 給我，如果遇到強地震，帶著手機、一瓶水，往大樓的電梯樓梯牆角下，抱頭蹲著，那處是住宅結構最強的金三角位置', '網傳貼文擷圖（發文者已遮蔽）'),
         stars(2)),
])

# =====================================================================
# L05
# 步驟照「實際操作的順序」排（規範 §5.11）：示範 → 選訊息 → 在搜尋頁與查核文章裡查完、答案記在學習單
# → 開文件、貼欄位、設標題 → 由上往下寫前 4 欄。標題樣式等文件打開、欄位貼好才教；影片放在操作旁邊。
# =====================================================================
def no(n, bg='bg-indigo-600'):
    return '<span class="inline-flex items-center justify-center w-9 h-9 rounded-full %s text-white text-xl font-extrabold mr-2 align-middle">%s</span>' % (bg, n)

TASKS = [('1', '選一則<b>訊息</b>'),
         ('2', '找到<b>查核文章</b>，複製<b>網址</b>'),
         ('3', '打開<b>老師給的文件</b>，貼上<b>格式</b>和<b>網址</b>'),
         ('4', '由上往下寫<b>三欄</b>')]
def tasks(active):
    rows = []
    for n, t in TASKS:
        on = n in active
        rows.append('<li class="%s">%s%s</li>' % ('text-slate-800' if on else 'text-slate-400', no(n, 'bg-orange-500' if on else 'bg-slate-300'), t))
    return ('<div class="bg-orange-50 border-4 border-orange-300 rounded-3xl p-4 mt-4">'
            '<p class="cute text-2xl font-extrabold text-orange-700 mb-2">🎯 今日任務：4 件事</p>'
            '<ol class="text-xl font-bold space-y-2">%s</ol></div>') % ''.join(rows)

_SEL = '  <!-- ===== 步驟 3：找訊息 ===== -->\n  <section class="step hidden" data-step="3">\n    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">\n      <h2 class="cute text-3xl font-extrabold text-rose-700">✋ 選一則你要查的訊息</h2>\n      <p class="text-slate-600 mt-2 text-lg">下面 6 則都是真的在網路上流傳過的：有<b>圖片</b>、有<b>影片</b>。選<b>一則</b>，用今天學的方法查它。</p>\n      <div class="mt-3 bg-amber-50 border-2 border-amber-200 rounded-2xl p-3 text-base text-slate-700">\n        <p class="font-bold text-amber-800">查證難易度：星星越多越難查</p>\n        <div class="grid sm:grid-cols-3 gap-2 mt-2">\n          <p><span class="text-amber-500 font-extrabold tracking-wider">★☆☆</span> <b>簡單</b>：搜尋第一頁就找得到，結果很明確</p>\n          <p><span class="text-amber-500 font-extrabold tracking-wider">★★☆</span> <b>中等</b>：要多讀一點，或多換幾個關鍵詞</p>\n          <p><span class="text-amber-500 font-extrabold tracking-wider">★★★</span> <b>較難</b>：結果很細微，或要分辨轉載與原始查核機構</p>\n        </div>\n      </div>\n      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="sel"></span></div>\n      %(TASKS_S)s\n    </div>\n    <div class="grid md:grid-cols-2 gap-5">\n%(CARDS)s\n    </div>\n    <div class="stepnav"></div>\n  </section>\n\n'
_SEA = '  <!-- ===== 步驟 4：找網址（在搜尋頁與查核文章裡做完，答案記在學習單）===== -->\n  <section class="step hidden" data-step="4">\n    <div class="bg-white border-4 border-teal-300 rounded-3xl p-6 mb-5 shadow-sm">\n      <h2 class="cute text-3xl font-extrabold text-teal-700">🔎 換你查：找到查核文章</h2>\n      <div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-4 mt-3 text-lg">\n        <p>你選的是：<b id="selName" class="text-teal-800">（還沒選，請回上一步）</b></p>\n        <p id="hintBox" class="text-slate-600 mt-1"></p>\n      </div>\n      %(TASKS_A)s\n    </div>\n\n    <div class="bg-teal-50 border-4 border-teal-200 rounded-3xl p-5 mb-5">\n      <p class="cute text-2xl font-extrabold text-teal-700 mb-3">%(N1)s搜尋：關鍵詞＋查核</p>\n      <div class="grid md:grid-cols-5 gap-4 items-start">\n        <div class="md:col-span-3">%(V1)s</div>\n        <div class="md:col-span-2">\n          <ol class="list-decimal pl-6 text-xl font-bold space-y-2">\n            <li>圈 2～3 個<span class="text-teal-700">關鍵詞</span></li>\n            <li>Google 打「關鍵詞＋<span class="text-teal-700">查核</span>」</li>\n            <li>點網址是 <span class="text-teal-700">tfc-taiwan</span> 或 <span class="text-teal-700">mygopen</span> 的文章</li>\n          </ol>\n          <div class="flex flex-wrap gap-2 mt-3">\n            <a href="https://www.google.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2">Google 搜尋 ↗</a>\n            %(LINKS)s\n          </div>\n        </div>\n      </div>\n\n      <div class="bg-white border-2 border-sky-200 rounded-2xl p-4 mt-4">\n        <p class="cute text-xl font-extrabold text-sky-700">🖼️ 搜不到？換以圖搜圖</p>\n        <div class="grid md:grid-cols-2 gap-4 mt-2">\n          <div><p class="font-bold text-slate-700 mb-2">圖片：智慧鏡頭，或相機圖示貼上圖片</p>%(V5)s</div>\n          <div><p class="font-bold text-slate-700 mb-2">影片：<kbd>Win</kbd>＋<kbd>Shift</kbd>＋<kbd>S</kbd> 截圖，再搜</p>%(V6)s</div>\n        </div>\n      </div>\n    </div>\n\n    <div class="bg-emerald-50 border-4 border-emerald-200 rounded-3xl p-5 mb-5">\n      <p class="cute text-2xl font-extrabold text-emerald-700 mb-3">%(N2)s讀懂查核文章，記下結果和網址</p>\n      <div class="grid md:grid-cols-2 gap-4 items-start">\n        <ol class="list-decimal pl-6 text-xl font-bold space-y-2">\n          <li>看標題前的<span class="text-emerald-700">標籤</span>（錯誤、誤導…）</li>\n          <li>讀最上面的「<span class="text-emerald-700">你可以先知道</span>」</li>\n          <li>找到<span class="text-emerald-700">網址列</span>，等一下要複製它</li>\n        </ol>\n        <div class="bg-white border-2 border-rose-200 rounded-2xl p-3 text-lg text-slate-700">⚠️ AI 摘要先跳過。新聞、貼文是<b>轉載</b>，要點到<b>原始的查核機構</b>。</div>\n      </div>\n      <p class="mt-4 text-lg font-bold text-rose-700">📌 查核文章的分頁<b>先不要關</b>：等一下要從它複製網址和圖片。</p>\n      <label class="block mt-3 text-lg font-bold text-slate-700">把查核文章的<b>網址</b>貼在這裡，下次就找得回來\n        <input class="urlKeep mt-1 w-full border-2 border-slate-300 rounded-xl px-3 py-2 text-base bg-white" autocomplete="off"></label>\n    </div>\n    <div class="stepnav"></div>\n  </section>\n\n'
_STEP1 = '''
  <!-- ===== 步驟 1：看範例 ===== -->
  <section class="step" data-step="1">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-6 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">這兩節，你要做出這樣一份查證文件</h2>
      <p class="text-slate-600 mt-2 text-lg">先看成品：把一則網傳訊息查清楚，整理成 Google 文件。文件有 <b>7 欄</b>，<b>這一節先做前面 4 欄</b>，下一節做後面 3 欄。</p>
      <a href="%(DOC)s" target="_blank" rel="noopener" class="flex items-center gap-3 bg-white border-4 border-dashed border-sky-300 rounded-2xl p-4 mt-4 hover:bg-sky-50">
        <div class="flex-1"><div class="font-bold text-sky-700">成品範例：幫陌生人操作手機，會被盜走指紋嗎？</div><div class="text-xs text-slate-400">Google 文件・開新分頁</div></div>
        <div class="text-sky-600 font-bold text-sm">開啟 ↗</div>
      </a>
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-5 text-base">
        %(CHIPS)s
      </div>
      <p class="mt-4 text-sm text-slate-500"><span class="inline-block w-3 h-3 rounded bg-indigo-200 align-middle"></span> 這一節　<span class="inline-block w-3 h-3 rounded bg-slate-200 align-middle ml-2"></span> 下一節</p>
    </div>
    <div class="stepnav"></div>
  </section>
'''
_STEP11 = '''
  <!-- ===== 步驟 11：繳交 ===== -->
  <section class="step hidden" data-step="11">
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-indigo-700">繳交前自己檢查</h2>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="chk"></span></div>
      <div id="chkOpts" class="space-y-2 mt-3"></div>
      <div class="bg-amber-50 border-2 border-amber-300 rounded-2xl p-4 mt-4 text-lg">
        <p class="font-bold text-amber-800">Classroom 的作業先<span class="text-rose-600">不要按「繳交」</span>，下一節還要繼續寫完。</p>
        <p class="mt-1">今天只要按下面的<span class="text-indigo-700 font-bold">「繳交學習單」</span>。</p>
      </div>
    </div>%(REWARD)s
    <div class="stepnav"></div>
  </section>
'''
_FMT = {'TASKS_S': tasks('1'), 'TASKS_A': tasks('2'),
        'N1': no('2', 'bg-teal-600'), 'N2': '接著：',
        'DOC': DOC, 'CHIPS': chips7('bg-indigo-100 border-2 border-indigo-200', 'bg-slate-100 border-2 border-slate-200'),
        'CARDS': CARDS, 'LINKS': LINKS, 'REWARD': REWARD,
        'V1': vid('教學_找到查核文章.mp4', '教學_找到查核文章_封面.jpg', '操作影片：從訊息找到查核文章（約 1 分鐘）'),
        'V5': vid('教學_以圖搜圖兩種方法.mp4', '教學_以圖搜圖兩種方法_封面.jpg', '操作影片：以圖搜圖兩種方法（約 1 分 15 秒）'),
        'V6': vid('截圖google圖片搜尋_字卡.mp4', '截圖google圖片搜尋_字卡_封面.jpg', '操作影片：截圖再以圖搜圖（L04，約 22 秒）')}
# 找網址：搜尋整段收合（不會查來源才點開看影片）；認機構看名稱；加「貼到學習單欄位」動圖
_SEA = _SEA.replace('點網址是 <span class="text-teal-700">tfc-taiwan</span> 或 <span class="text-teal-700">mygopen</span> 的文章',
                    '點機構名稱是 <span class="text-teal-700">台灣事實查核中心</span> 或 <span class="text-teal-700">MyGoPen</span> 的文章')
_o1 = '搜尋：關鍵詞＋查核</p>\n      <div class="grid md:grid-cols-5'
assert _o1 in _SEA
_SEA = _SEA.replace(_o1, '搜尋：關鍵詞＋查核</p>\n      <details class="mt-1 bg-white border-2 border-teal-300 rounded-2xl p-3"><summary class="cursor-pointer font-extrabold text-teal-800 text-xl">不會查來源？點擊看影片</summary>\n      <div class="mt-3 grid md:grid-cols-5', 1)
_o2 = '      </div>\n    </div>\n\n    <div class="bg-emerald-50'
assert _o2 in _SEA
_SEA = _SEA.replace(_o2, '      </div>\n      </details>\n    </div>\n\n    <div class="bg-emerald-50', 1)
_o3 = 'autocomplete="off"></label>'
assert _o3 in _SEA
_SEA = _SEA.replace(_o3, _o3 + '\n      ' + L5S.sc([L5S.slide('找到網址，貼在學習單這個欄位', '步_網址0_貼到學習單')], numbered=False), 1)

L05_BODY = ((_STEP1 % _FMT) + L5S.STEP_DEMO + (_SEL % _FMT) + (_SEA % _FMT)
            + L5S.STEP_OPEN + L5S.STEP_FORMAT + L5S.STEP_URL + L5S.STEP_MSG + L5S.STEP_HOW + L5S.STEP_RES + (_STEP11 % _FMT))

L05_CFG = {
    'ws': 'g5-L05', 'lessonPath': 'g5/L05', 'title': 'Docs 查證文件（一）：找到查核文章', 'stateKey': 'g5L05flow',
    'steps': ['看範例', '老師示範', '找訊息', '找網址', '開文件', '貼格式', '貼網址', '我選的訊息', '怎麼找到的', '查核結果', '繳交'],
    'reveals': [], 'revealOf': {}, 'autoFb': [],
    'qtypes': {'sel': 'experience', 'chk': 'experience'},
    'choices': {
        'sel': {'opts': ['C', 'D', 'E', 'G', 'H', 'K'], 'card': True},
        'chk': {'opts': ['查核文章是查核機構自己的網站，不是轉載', '標題用「標題 1」、欄位名稱用「標題 2」', '文件最上面是查核報告的標題；「查核網址」下面是整條網址，點得開', '「我選的訊息」下面貼了原始訊息的圖片或影片截圖', '前面的欄位都寫好了'], 'multi': True, 'block': True},
    },
    'texts': [],
    'patterns': {},
    'openQtexts': {},
}

L05_HOOKS = r'''
  // ===== 複製七個欄位（先用剪貼簿 API，被拒絕就退回選取＋execCommand）=====
  // 貼進文件的文字：第 1 行（文件標題）、第 2 行帶入第 4 步記下的查核網址，每個欄位名稱下一行提示
  // 貼進文件的文字：乾淨的格式，不放引導（寫法在「每一欄怎麼寫」那步）
  function buildTpl(){
    return ['（文件標題）','（年班座號＋名字）','查核網址','我選的訊息','我怎麼找到查核文章的','查核結果',
      '為什麼這則訊息會被廣傳？','正確資訊','如果相信的話，會有什麼後果？'].join('\n');
  }
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
  $('tplText').textContent=buildTpl();
  $('tplCopy').onclick=function(){copyText(buildTpl(),this);};
  // ===== L05 專屬：6 則訊息、選題卡、提示 =====
  var CARDS={
    C:{name:'C ‧ 繪畫比賽投票（LINE 訊息）',label:'詐騙',url:'https://www.mygopen.com/2026/08/vote-scam.html',hint:'想想：這則訊息要你「做什麼」？連結要你「輸入什麼」？再加上「查核」。'},
    D:{name:'D ‧ 微波爐加熱食物有輻射（訊息）',label:'錯誤',url:'https://tfc-taiwan.org.tw/?p=109294',hint:'想想：哪一種家電？哪個國家要禁用？再加上「查核」。也可以點原始文章，看它是什麼樣的網站。'},
    E:{name:'E ‧ 打雷時用手機、藍芽耳機（訊息）',label:'事實釐清',url:'https://tfc-taiwan.org.tw/fact-check-reports/migration-7854',hint:'想想：什麼東西、遇到什麼天氣、會怎樣？再加上「查核」。'},
    G:{name:'G ‧ 印度街頭小吃影片（貼文）',label:'錯誤',url:'https://www.mygopen.com/2026/09/india-ai.html',hint:'想想：哪個國家？在做什麼食物？影片裡的人做了什麼事？再加上「查核」。'},
    H:{name:'H ‧ 手機充電時喝水（影片）',label:'錯誤',url:'https://www.mygopen.com/2022/01/Charging-Phone.html',hint:'想想：充電時做了什麼事？這支影片也可以用「以圖搜圖」找。'},
    K:{name:'K ‧ 地震時躲哪裡（訊息）',label:'錯誤',url:'https://tfc-taiwan.org.tw/fact-check-reports/migration-4806',hint:'想想：地震時要「去哪裡」躲？也試試找消防局、氣象署的官方說明。'}
  };
  H.stepDone=function(n){
    if(n===3)return !!state.sel;
    return null;
  };
  H.report=function(){
    return ['選的訊息：'+(state.sel&&CARDS[state.sel]?CARDS[state.sel].name:'還沒選'),
      '提醒：Classroom 的文件先不要按「繳交」，下一節還要繼續寫'];
  };
  H.showAnswers=function(){if(!state.sel)state.sel='C';};
  H.clear=function(){state.sel=null;state.url='';state.chk=[];};
  var STARS={C:1,D:2,E:3,G:2,H:1,K:2};
  H.render=function(){
    bindRescue();renderRescue();
    document.querySelectorAll('[data-card]').forEach(function(c){
      var on=state.sel===c.dataset.card;c.classList.toggle('on',on);
      var bt=c.querySelector('[data-pick]');bt.textContent=on?'✔ 我選這則':'選這則';
    });
    var s=state.sel&&CARDS[state.sel];
    if($('selName'))$('selName').textContent=s?s.name+'　難度 '+'★'.repeat(STARS[state.sel])+'☆'.repeat(3-STARS[state.sel]):'（還沒選，請回上一步）';
    if($('hintBox'))$('hintBox').textContent=s?s.hint:'';
    if($('tplText'))$('tplText').textContent=buildTpl();
  };
  document.querySelectorAll('[data-pick]').forEach(function(bt){
    bt.onclick=function(){state.sel=bt.dataset.pick;save();H.render();renderStepper();};
  });
'''

L05_HOOKS = L05_HOOKS + L5S.RESCUE_JS

L05_SPEC = {
    'summary': '用「關鍵詞＋查核」或以圖搜圖，從 6 則真實網傳訊息中選一則，找到台灣事實查核中心或 MyGoPen 已發布的查核文章，看懂結果標籤，並在 Google 文件寫好標題與前四欄（我選的訊息、我怎麼找到查核文章的、查核結果、查核網址）。',
    'questions': [
        {'qid': 'doc', 'prompt': '你的 Google 文件（老師從 Classroom 作業讀取文件內容）：標題與前四欄「我選的訊息（含原始訊息圖片）」「我怎麼找到查核文章的」「查核結果」「查核網址」。',
         'mode': 'checklist',
         'checks': [
             {'desc': '有標題，並用自己的話說明選的是哪一則訊息，有寫出人、事、時、地、物（沒寫的標「沒說」），下面貼了原始訊息的圖片或影片截圖', 'pts': 6},
             {'desc': '依序說出圈了哪些關鍵詞（或哪張圖）、在 Google 搜了什麼、點進哪個網站，並說明為什麼認定它是查核機構', 'pts': 6},
             {'desc': '寫出查核機構標的結果（例如錯誤、誤導）和是哪一家機構', 'pts': 4},
             {'desc': '文件標題是查核報告的標題；「查核網址」下面貼了整條網址（https:// 開頭，是查核機構自己的網站）', 'pts': 4}]}],
    'scoring': {'base': 100, 'floor': 80, 'deduction': 1, 'itemPoints': {}},
}

# =====================================================================
# L06
# =====================================================================
OLD_S23 = '\n  <!-- ===== 步驟 5：抄與整理 ===== -->\n  <section class="step hidden" data-step="5">\n    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">\n      <h2 class="cute text-3xl font-extrabold text-amber-700 m-0">整理不是複製</h2>\n      <p class="text-slate-700 mt-2 text-lg">整理像是<b>向朋友轉述</b>：朋友沒看過那篇文章，你用一兩句話告訴他「這則訊息是真的嗎？為什麼？」。</p>\n    </div>\n    <div class="grid md:grid-cols-2 gap-4 mb-5 text-lg">\n      <div class="bg-slate-50 border-4 border-slate-200 rounded-3xl p-4"><p class="cute text-xl font-extrabold text-slate-600 m-0">整段複製（不要這樣）</p><p class="mt-2">經查，查核中心洽詢刑事警察局後，警方表示目前國內並無查獲與網傳手法相同之案件，且 165 反詐騙專線亦表示，台灣無此類案例。</p></div>\n      <div class="bg-emerald-50 border-4 border-emerald-200 rounded-3xl p-4"><p class="cute text-xl font-extrabold text-emerald-700 m-0">整理成自己的話（要這樣）</p><p class="mt-2">警方和 165 反詐騙專線說，台灣目前查不到這種手法的案件。</p></div>\n    </div>\n    <div class="bg-white border-4 border-teal-200 rounded-3xl p-5 mb-5 text-lg">\n      <p class="m-0"><b>整理</b>＝只留重點、用自己的話、標出是誰說的。</p>\n    </div>\n    <div class="bg-white border-4 border-amber-200 rounded-3xl p-5">\n      <h3 class="cute text-2xl font-extrabold text-amber-700 m-0">範例（老師的示範）：正確資訊</h3>\n      <ol class="list-decimal pl-6 mt-3 space-y-2 text-lg text-slate-700">\n        <li><b>根據 MyGoPen</b>，只有指紋或臉，不能直接拿去貸款，銀行還要看很多檢查。</li>\n        <li><b>警方和 165 說</b>，台灣查不到這種案件。</li>\n        <li><b>不過</b>，陌生人要你做驗證時，還是要小心。</li>\n      </ol>\n      <p class="mt-3 text-slate-600 text-lg">句型：根據○○，……／○○說，……／不過，……。先講最重要的結論，最後講還要小心什麼。</p>\n    </div>\n    <div class="stepnav"></div>\n  </section>\n\n  <!-- ===== 步驟 6：廣傳後果 ===== -->\n  <section class="step hidden" data-step="6">\n    <div class="bg-white border-4 border-rose-300 rounded-3xl p-5 mb-5 shadow-sm">\n      <h2 class="cute text-3xl font-extrabold text-rose-700 m-0">為什麼會被廣傳？相信的話會怎樣？</h2>\n      <div class="grid md:grid-cols-2 gap-4 mt-4">\n        <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-4"><p class="cute text-xl font-extrabold text-rose-700 m-0">為什麼會轉傳（5 類）</p>\n          <ul class="mt-2 space-y-1 text-lg text-slate-700"><li><b>怕</b>：講得很可怕</li><li><b>好奇／驚奇</b>：聽起來很厲害</li><li><b>關心家人</b>：「轉傳等於救人」</li><li><b>好康</b>：免費、搶先</li><li><b>親友傳來的</b>：因為信任</li></ul></div>\n        <div class="bg-amber-50 border-2 border-amber-200 rounded-2xl p-4"><p class="cute text-xl font-extrabold text-amber-700 m-0">相信的後果（4 類）</p>\n          <ul class="mt-2 space-y-1 text-lg text-slate-700"><li><b>身體</b>：吃錯、做錯</li><li><b>錢</b>：被騙</li><li><b>人際</b>：誤會、吵架</li><li><b>恐慌</b>：嚇到更多人、再轉傳</li></ul></div>\n      </div>\n    </div>\n    <div class="bg-white border-4 border-amber-200 rounded-3xl p-5 mb-5 text-lg">\n      <h3 class="cute text-2xl font-extrabold text-amber-700 m-0">範例（老師的示範）</h3>\n      <p class="mt-2"><b>為什麼廣傳：</b>訊息說「30 分鐘傾家蕩產」，讓人怕；又寫「轉傳給家人朋友」，大家覺得轉傳是關心家人；還提到 AI 和手機，聽起來很厲害，帶點好奇。</p>\n      <p class="mt-2"><b>後果：</b>有人怕到不敢幫真的需要幫忙的人；也有人把嚇人的訊息再轉給更多人，讓大家一起害怕。</p>\n    </div>\n    <div class="grid md:grid-cols-2 gap-4 text-lg">\n      <div class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-4"><p class="font-extrabold text-emerald-700 m-0">後果這樣寫才好</p><p class="mt-1">寫出<b>誰</b>會<b>怎樣</b>。</p></div>\n      <div class="bg-slate-50 border-2 border-slate-200 rounded-2xl p-4"><p class="font-extrabold text-slate-600 m-0">這樣寫不夠</p><p class="mt-1">「會被騙」沒說誰、怎麼被騙；「這則訊息是假的」是查核結果，不是後果。</p></div>\n    </div>\n    <div class="stepnav"></div>\n  </section>\n\n'
OLD_S8 = '  <!-- ===== 步驟 7：繳交 ===== -->\n  <section class="step hidden" data-step="7">\n    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">\n      <h2 class="cute text-3xl font-extrabold text-indigo-700">✅ 繳交前自己檢查</h2>\n      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="chk"></span></div>\n      <div id="chkOpts" class="space-y-2 mt-3"></div>\n      <div class="bg-indigo-50 border-2 border-indigo-200 rounded-2xl p-4 mt-4 text-lg text-slate-700">\n        <p class="font-bold text-indigo-800">繳交兩個地方：</p>\n        <ol class="list-decimal pl-6 mt-1 space-y-1"><li>回 <b>Classroom 作業</b>，確認文件<b>附在作業裡</b>，按<b>「繳交」</b>。</li><li>回到這裡，按下面的<b>「繳交學習單」</b>。</li></ol>\n        <p class="text-sm text-slate-500 mt-2">還沒寫完也可以先交，下一節開頭還有時間補。</p>\n      </div>\n    </div>@@REWARD@@\n    <div class="stepnav"></div>\n  </section>\n'

def _tone_block(tone, title, hint, ex_html, why_html, guide_html, extra=''):
    return ('<div class="bg-white border-4 border-%(t)s-300 rounded-3xl p-5 mb-5 shadow-sm">'
            '<h3 class="cute text-2xl font-extrabold text-%(t)s-700 m-0">%(title)s<span class="text-base font-bold text-slate-500 ml-2">%(hint)s</span></h3>'
            '<div class="grid md:grid-cols-3 gap-3 mt-3 text-lg">'
            '<div class="bg-amber-50 border-2 border-amber-200 rounded-2xl p-3"><p class="font-extrabold text-amber-800">範例（老師的示範）</p><div class="mt-1 text-slate-800">%(ex)s</div></div>'
            '<div class="bg-sky-50 border-2 border-sky-200 rounded-2xl p-3"><p class="font-extrabold text-sky-800">為什麼這樣寫</p><div class="mt-1 text-slate-700">%(why)s</div></div>'
            '<div class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-3"><p class="font-extrabold text-emerald-800">我檢查</p><div class="mt-1 text-slate-700">%(guide)s</div></div>'
            '</div>%(extra)s</div>') % {'t': tone, 'title': title, 'hint': hint, 'ex': ex_html, 'why': why_html, 'guide': guide_html, 'extra': extra}


def _checks(*items):
    return '<ul class="space-y-1">' + ''.join('<li>☐ %s</li>' % i for i in items) + '</ul>'


def _chips(items, cls='bg-white border-2 border-slate-300 text-slate-700'):
    return '<div class="flex flex-wrap gap-1.5 mt-2">' + ''.join('<span class="%s rounded-full px-3 py-0.5 text-base font-bold">%s</span>' % (cls, t) for t in items) + '</div>'


def _clips(slides, opened=False, label='查看操作影片'):
    return ('<details class="mt-3 bg-slate-50 border-2 border-slate-300 rounded-2xl p-3"><summary class="cursor-pointer font-extrabold text-slate-700 text-lg">%s</summary>'
            '<div class="mt-3">' % label) + L5S.sc(slides) + '</div></details>'


_LABELS = ['錯誤', '誤導', '易誤解', '事實釐清', '詐騙', '部分錯誤', '正確']

STEP_L06_1 = '''
  <!-- ===== 步驟 1：回顧、找回上次的資料 ===== -->
  <section class="step" data-step="1">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-6 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">📂 先找回你上次的資料</h2>
      <p class="text-slate-600 mt-2 text-lg">上一節選了一則訊息、找到查核文章。<b>沒做完也沒關係</b>，這一節會一步一步補，再做後 3 欄。先把<b>查核網址</b>找回來。</p>
      @@RESCUE@@
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-5 text-base">
        @@CHIPS@@
      </div>
      <p class="mt-4 text-sm text-slate-500"><span class="inline-block w-3 h-3 rounded bg-slate-200 align-middle"></span> 前面的欄位（上一節）　<span class="inline-block w-3 h-3 rounded bg-indigo-200 align-middle ml-2"></span> 今天要做的後 3 欄</p>
      <a href="@@DOC@@" target="_blank" rel="noopener" class="inline-block mt-3 bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl px-5 py-2">📄 成品範例：看 7 欄寫好的樣子 ↗</a>
    </div>
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 shadow-sm">
      <h2 class="cute text-2xl font-extrabold text-rose-700">🤔 想一想</h2>
      <p class="text-slate-700 mt-2 text-lg">你找到的那一篇查核文章，如果<b>整篇貼進文件</b>，算不算你查證完成？為什麼？</p>
    </div>
    <div class="stepnav"></div>
  </section>
'''

STEP_L06_2 = '''
  <!-- ===== 步驟 2：選訊息（上一節選過的，這裡會顯示 ✔）===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-rose-700 m-0">✋ 你查的是哪一則訊息？</h2>
      <p class="text-slate-600 mt-2 text-lg">上一節選過的，這裡已經打勾。還沒選的，現在選<b>一則</b>。圖片、影片都在卡片裡。</p>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="sel"></span></div>
    </div>
    <div class="grid md:grid-cols-2 gap-5">
@@CARDS@@
    </div>
    <div class="stepnav"></div>
  </section>
'''

_LINK = '<span class="text-indigo-700 underline break-all">https://www.mygopen.com/2026/02/ai-fraud.html</span>'
_BLK_TITLE = _tone_block('sky', '標題', '換成查核報告的標題',
    '<p class="text-slate-500">（文件標題）</p><p class="text-2xl">↓</p><p class="font-extrabold">【誤導】幫陌生人操作手機會被盜取生物特徵去貸款？誇大AI技術！不符金融審核機制</p>',
    '<p>標題要是<b>查核報告的標題</b>，一看就知道你查的是哪一則。</p>',
    _checks('不是「（文件標題）」', '是查核文章上的標題', '已設成「標題 1」'),
    _clips([
        L5S.slide('到查核文章，選取<b>查核報告的標題</b>，複製', '步_標題A_複製標題'),
        L5S.slide('回文件，選取第 1 行「（文件標題）」，貼上', '步_標題B_貼上標題')], False, '查看操作影片：標題'))
_BLK_URL = _tone_block('indigo', '① 查核網址', '標題下面，整條網址',
    '<p>' + _LINK + '</p>',
    '<p>讓人點進去驗證。貼<b>整條網址</b>，不要放標題。</p>',
    _checks('查核機構自己的網站', 'https:// 開頭、藍色有底線', '點得開', '「查核網址」下面只有網址', '沒有網址？回第 1 步找回'),
    _clips([
        L5S.slide('到查核文章，點<b>網址列</b>，複製<b>網址</b>', '步_網址1_複製網址列'),
        L5S.slide('回文件，貼在「查核網址」<b>下面</b>', '步_網址2_貼上網址'),
        L5S.slide('圈選網址，點<b>鎖鏈符號</b>，按「套用」', '步_網址3_加超連結')], False, '查看操作影片：查核網址'))
_BLK_MSG = _tone_block('amber', '② 我選的訊息', '人事時地物＋傳播',
    '<p>網傳訊息說：只要幫路上的陌生人操作手機、摸螢幕、對著鏡頭說話，指紋、聲音和臉就會被偷走，騙子拿去貸款，30 分鐘就傾家蕩產。這則訊息在臉書流傳。</p>',
    '<p>沒看過的人，只看這段就懂。缺的寫「沒說」。</p>',
    '<p class="text-base">人：誰　事：做什麼　時：何時　地：哪裡　物：什麼東西　傳播：在哪傳</p>' + _checks('是自己的話', '貼了原始訊息的圖'),
    _clips([
        L5S.slide('找到<b>原始訊息的圖</b>，右鍵<b>複製圖片</b>', '步_圖A_找圖複製'),
        L5S.slide('回文件，<b>貼在句子下面</b>', '步_圖3_貼上')], False, '查看操作影片：我選的訊息'))
_BLK_HOW = _tone_block('teal', '③ 我怎麼找到查核文章的', '照順序寫',
    '<p>我圈出「陌生人」「操作手機」「生物特徵」，搜「陌生人 操作手機 生物特徵 查核」，點進 MyGoPen 的文章，它是專門查謠言的機構，不是轉載。</p>',
    '<p>別人照著做也找得到。</p>',
    '<p class="text-base">關鍵詞、搜什麼字、點哪個網站、為什麼是查核機構</p>' + _checks('四件事都寫了'))
_BLK_RES = _tone_block('rose', '④ 查核結果', '哪一家、標什麼、一句重點',
    '<p>MyGoPen 查核後標為「誤導」，重點是這個說法在技術和金融上都不合理。</p>',
    '<p>不能只寫「是假的」。</p>',
    _chips(_LABELS, 'bg-amber-100 border-2 border-amber-300 text-amber-900') + _checks('寫了機構名', '標籤照文章寫', '有一句重點'))

STEP_L06_4 = """
  <!-- ===== 步驟 4：檢查前四欄（含標題）===== -->
  <section class="step hidden" data-step="4">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700 m-0">檢查自己寫的：標題＋前四欄</h2>
      <p class="text-lg text-slate-600 mt-1">對照範例，換成<b>你自己選的那一則</b>。</p>
    </div>
    @@BLOCKS@@
    <div class="stepnav"></div>
  </section>
""".replace('@@BLOCKS@@', _BLK_TITLE + _BLK_URL + _BLK_MSG + _BLK_HOW + _BLK_RES)

_BLK_WHY = _tone_block('violet', '⑤ 為什麼這則訊息會被廣傳？', '至少一類，要有理由',
    '<p>訊息說「30 分鐘傾家蕩產」，讓人<b>怕</b>；又說「轉傳給家人朋友」，大家覺得轉傳是<b>關心家人</b>。</p>',
    '<p>說出哪裡讓人想轉傳。</p>',
    _chips(['怕', '好奇', '關心家人', '好康', '親友傳來']) + _checks('選一類', '寫了理由'))
_BLK_FACT = _tone_block('emerald', '⑥ 正確資訊', '1～3 點，標機構',
    '<ol class="list-decimal pl-5 space-y-1"><li><b>根據 MyGoPen</b>，只有指紋或臉，不能直接拿去貸款，銀行還要看很多檢查。</li><li><b>警方和 165 說</b>，台灣查不到這種案件。</li><li><b>不過</b>，陌生人要你做驗證時，還是要小心。</li></ol>',
    '<p>讓人知道事實，並標出是誰說的。</p>',
    '<p class="text-base">句型：根據○○，……／○○說，……／不過，……</p>' + _checks('每點一句', '標了機構', '不整段複製'))
_BLK_RISK = _tone_block('rose', '⑦ 如果相信的話，會有什麼後果？', '誰會怎樣',
    '<p>有人怕到不敢幫真的需要幫忙的人；也有人把嚇人的訊息再轉給更多人。</p>',
    '<p>要寫誰會怎樣，不是「是假的」。</p>',
    _chips(['身體', '錢', '人際', '恐慌']) + _checks('寫了誰', '寫了怎樣'))

STEP_L06_7 = """
  <!-- ===== 步驟 6：檢查後三欄 ===== -->
  <section class="step hidden" data-step="6">
    <div class="bg-white border-4 border-teal-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-teal-700 m-0">檢查自己寫的：後 3 欄</h2>
      <p class="text-lg text-slate-600 mt-1">時間不夠，先寫：正確資訊、廣傳、後果。</p>
    </div>
    @@BLOCKS@@
    <div class="stepnav"></div>
  </section>
""".replace('@@BLOCKS@@', _BLK_WHY + _BLK_FACT + _BLK_RISK)

# L06 不再有「抄與整理」（搬到 L05 第 8 步開頭）：只留「廣傳後果」，編號往前補
_i = OLD_S23.index('  <!-- ===== 步驟 6：廣傳後果 ===== -->')
OLD_S23 = OLD_S23[_i:].replace('data-step="6"', 'data-step="5"').replace('步驟 6：廣傳後果', '步驟 5：廣傳後果')
L06_BODY = ('\n' + STEP_L06_1 + '\n' + STEP_L06_2 + '\n' + L5S.step_prep(3, '上一節做過的，直接按「下一步」跳過；還沒做的，一步一步補。').replace('<!-- ===== 準備文件（步驟卡）===== -->', '<!-- ===== 步驟 3：準備文件 ===== -->')
            + '\n' + STEP_L06_4 + '\n' + OLD_S23 + '\n' + STEP_L06_7 + '\n' + OLD_S8 + '\n')
L06_BODY = (L06_BODY.replace('@@RESCUE@@', L5S.RESCUE.replace('<details class="urlfix', '<details open class="urlfix', 1))
            .replace('@@CARDS@@', CARDS).replace('@@DOC@@', DOC).replace('@@REWARD@@', REWARD)
            .replace('@@CHIPS@@', chips7('bg-slate-100 border-2 border-slate-200', 'bg-indigo-100 border-2 border-indigo-200')))

L06_CFG = {
    'ws': 'g5-L06', 'lessonPath': 'g5/L06', 'title': 'Docs 查證文件（二）：整理成報告', 'stateKey': 'g5L06flow',
    'steps': ['找回資料', '選訊息', '準備文件', '檢查前四欄', '廣傳後果', '檢查後三欄', '繳交'],
    'reveals': [], 'revealOf': {}, 'autoFb': [],
    'qtypes': {'sel': 'experience', 'chk': 'experience'},
    'choices': {
        'sel': {'opts': ['C', 'D', 'E', 'G', 'H', 'K'], 'card': True},
        'chk': {'opts': ['標題和前四欄都對照檢查過了', '「正確資訊」有標出處，沒有整段複製', '「為什麼廣傳」和「後果」都寫了理由', '標題是查核報告的標題，「查核網址」是整條網址、點得開'], 'multi': True, 'block': True},
    },
    'texts': [], 'patterns': {}, 'openQtexts': {},
}

_a = L05_HOOKS.index("  // ===== 複製七個欄位")
_z = L05_HOOKS.index("  H.stepDone=function(n){")
L06_HOOKS = L05_HOOKS[_a:_z] + r'''
  var STARS={C:1,D:2,E:3,G:2,H:1,K:2};
  H.stepDone=function(n){
    if(n===2)return !!state.sel;
    return null;
  };
  H.report=function(){
    return ['選的訊息：'+(state.sel&&CARDS[state.sel]?CARDS[state.sel].name:'還沒選'),
      '自查表：已勾 '+((state.chk||[]).length)+' 項（共 4 項）','提醒：文件要附在 Classroom 作業裡，並在那邊按「繳交」'];
  };
  H.showAnswers=function(){if(!state.sel)state.sel='E';};
  H.clear=function(){state.sel=null;state.url='';state.chk=[];};
  H.render=function(){
    bindRescue();renderRescue();
    document.querySelectorAll('[data-card]').forEach(function(c){
      var on=state.sel===c.dataset.card;c.classList.toggle('on',on);
      var bt=c.querySelector('[data-pick]');bt.textContent=on?'✔ 我選這則':'選這則';
    });
    if($('tplText'))$('tplText').textContent=buildTpl();
  };
  document.querySelectorAll('[data-pick]').forEach(function(bt){
    bt.onclick=function(){state.sel=bt.dataset.pick;save();H.render();renderStepper();};
  });
''' + L5S.RESCUE_JS

L06_SPEC = {
    'summary': '把上一節找到的查核文章整理成完整的查證文件：用自己的話寫正確資訊並標出處、說明訊息為什麼被廣傳與相信的後果。',
    'questions': [
        {'qid': 'doc2', 'prompt': '你的 Google 文件（老師從 Classroom 作業讀取文件內容）：「正確資訊」「為什麼這則訊息會被廣傳」「如果相信的話會有什麼後果」。',
         'mode': 'checklist',
         'checks': [
             {'desc': '「正確資訊」用自己的話寫 1～3 點，沒有整段複製查核文章', 'pts': 7},
             {'desc': '「正確資訊」有標出是哪個機構（警方、165、查核機構、專家等）說的', 'pts': 3},
             {'desc': '「為什麼這則訊息會被廣傳」說出至少一個原因（怕、好奇、關心家人、好康、親友傳來）並說明理由', 'pts': 5},
             {'desc': '「相信的後果」說出誰會怎樣，不只是寫「是假的」或「會被騙」', 'pts': 5}]}],
    'scoring': {'base': 100, 'floor': 80, 'deduction': 1, 'itemPoints': {}},
}

_EMOJI = re.compile('[\U0001F000-\U0001FAFF\u2600-\u26FF\u2700-\u27BF\u2B00-\u2BFF\uFE0F\u200D]')
_KEEP = '✓✔☐☑★☆✏'.replace('✏', '')


def strip_emoji(html):
    out = []
    for ch in html:
        if _EMOJI.match(ch) and ch not in _KEEP:
            continue
        out.append(ch)
    return ''.join(out)


def write(name, folder, html):
    html = strip_emoji(html)
    p = os.path.join(ROOT, folder, name)
    io.open(p, 'w', encoding='utf8', newline='\n').write(html)
    print('wrote', p, len(html) // 1024, 'KB')

write('五上_L05_Docs查證文件一.html', 'L05_Docs查證文件一',
      page('訊息查證小偵探｜五上 L05 教學活動', '🔎 訊息查證小偵探',
           '五年級上學期 · L05 Docs 查證文件（一）· 教學活動流程（40 分鐘）', L05_BODY, L05_CFG, L05_HOOKS, L05_SPEC, L5S.CSS))
write('五上_L06_Docs查證文件二.html', 'L06_Docs查證文件二',
      page('整理成查證文件｜五上 L06 教學活動', '📝 把查核文章整理成自己的報告',
           '五年級上學期 · L06 Docs 查證文件（二）· 教學活動流程（40 分鐘）', L06_BODY, L06_CFG, L06_HOOKS, L06_SPEC, L5S.CSS))
