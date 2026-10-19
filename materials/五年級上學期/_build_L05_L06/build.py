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
    ('1', '查核網址', '查核文章的標題，做成可以點的連結（貼在標題下面）', True),
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
         ('2', '找到<b>查核文章</b>，記下<b>結果</b>和<b>網址</b>'),
         ('3', '打開<b>老師給的文件</b>，貼上<b>欄位</b>、設標題'),
         ('4', '由上往下寫<b>前四欄</b>')]
def tasks(active):
    rows = []
    for n, t in TASKS:
        on = n in active
        rows.append('<li class="%s">%s%s</li>' % ('text-slate-800' if on else 'text-slate-400', no(n, 'bg-orange-500' if on else 'bg-slate-300'), t))
    return ('<div class="bg-orange-50 border-4 border-orange-300 rounded-3xl p-4 mt-4">'
            '<p class="cute text-2xl font-extrabold text-orange-700 mb-2">🎯 今日任務：4 件事</p>'
            '<ol class="text-xl font-bold space-y-2">%s</ol></div>') % ''.join(rows)

L05_BODY = '''
  <!-- ===== 步驟 1：看成品 ===== -->
  <section class="step" data-step="1">
    <div id="resumeBox" class="hidden bg-teal-50 border-4 border-teal-300 rounded-3xl p-4 mb-5 shadow-sm flex items-center justify-between gap-3 flex-wrap">
      <p class="cute text-2xl font-extrabold text-teal-700 m-0">🔁 上週做到一半？前面的步驟不用再看。</p>
      <button id="resumeBtn" type="button" class="cute bg-teal-600 hover:bg-teal-700 text-white text-xl font-extrabold rounded-2xl px-6 py-2">直接去「回想」→</button>
    </div>
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-6 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">📄 這兩節，你要做出這樣一份查證文件</h2>
      <p class="text-slate-600 mt-2 text-lg">老師先帶大家看一份成品：把一則網傳訊息查清楚，整理成 Google 文件。文件有 <b>7 欄</b>，<b>這一節先做前 4 欄</b>，下一節做後 3 欄。</p>
      <a href="%(DOC)s" target="_blank" rel="noopener" class="flex items-center gap-3 bg-white border-4 border-dashed border-sky-300 rounded-2xl p-4 mt-4 hover:bg-sky-50">
        <div class="text-3xl">📄</div>
        <div class="flex-1"><div class="font-bold text-sky-700">成品範例：幫陌生人操作手機，會被盜走指紋嗎？</div><div class="text-xs text-slate-400">Google 文件・開新分頁</div></div>
        <div class="text-sky-600 font-bold text-sm">開啟 ↗</div>
      </a>
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-5 text-base">
        %(CHIPS)s
      </div>
      <p class="mt-4 text-sm text-slate-500"><span class="inline-block w-3 h-3 rounded bg-indigo-200 align-middle"></span> 今天（L05）　<span class="inline-block w-3 h-3 rounded bg-slate-200 align-middle ml-2"></span> 下一節（L06）</p>
    </div>
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-2xl font-extrabold text-amber-700 m-0">👩‍🏫 示範：一欄一欄看，成品怎麼寫</h2>
      <p class="text-slate-600 text-lg mt-1">示範訊息：<b>幫陌生人操作手機，會被盜走指紋？</b>　💡 不用從零查證：找到別人<b>已經查好的那一篇</b>，再讀懂它。</p>
    </div>
    %(DEMO)s
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 2：選訊息 ===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-rose-700">✋ 選一則你要查的訊息</h2>
      <p class="text-slate-600 mt-2 text-lg">下面 6 則都是真的在網路上流傳過的：有<b>圖片</b>、有<b>影片</b>。選<b>一則</b>，用今天學的方法查它。</p>
      <div class="mt-3 bg-amber-50 border-2 border-amber-200 rounded-2xl p-3 text-base text-slate-700">
        <p class="font-bold text-amber-800">查證難易度：星星越多越難查</p>
        <div class="grid sm:grid-cols-3 gap-2 mt-2">
          <p><span class="text-amber-500 font-extrabold tracking-wider">★☆☆</span> <b>簡單</b>：搜尋第一頁就找得到，結果很明確</p>
          <p><span class="text-amber-500 font-extrabold tracking-wider">★★☆</span> <b>中等</b>：要多讀一點，或多換幾個關鍵詞</p>
          <p><span class="text-amber-500 font-extrabold tracking-wider">★★★</span> <b>較難</b>：結果很細微，或要分辨轉載與原始查核機構</p>
        </div>
      </div>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="sel"></span></div>
      %(TASKS_S)s
    </div>
    <div class="grid md:grid-cols-2 gap-5">
%(CARDS)s
    </div>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 3：我來查（在搜尋頁與查核文章裡做完，答案記在學習單）===== -->
  <section class="step hidden" data-step="3">
    <div class="bg-white border-4 border-teal-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-teal-700">🔎 換你查：找到查核文章</h2>
      <div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-4 mt-3 text-lg">
        <p>你選的是：<b id="selName" class="text-teal-800">（還沒選，請回上一步）</b></p>
        <p id="hintBox" class="text-slate-600 mt-1"></p>
      </div>
      %(TASKS_A)s
    </div>

    <div class="bg-teal-50 border-4 border-teal-200 rounded-3xl p-5 mb-5">
      <p class="cute text-2xl font-extrabold text-teal-700 mb-3">%(N1)s搜尋：關鍵詞＋查核</p>
      <div class="grid md:grid-cols-5 gap-4 items-start">
        <div class="md:col-span-3">%(V1)s</div>
        <div class="md:col-span-2">
          <ol class="list-decimal pl-6 text-xl font-bold space-y-2">
            <li>圈 2～3 個<span class="text-teal-700">關鍵詞</span></li>
            <li>Google 打「關鍵詞＋<span class="text-teal-700">查核</span>」</li>
            <li>點網址是 <span class="text-teal-700">tfc-taiwan</span> 或 <span class="text-teal-700">mygopen</span> 的文章</li>
          </ol>
          <div class="flex flex-wrap gap-2 mt-3">
            <a href="https://www.google.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2">Google 搜尋 ↗</a>
            %(LINKS)s
          </div>
        </div>
      </div>

      <div class="bg-white border-2 border-sky-200 rounded-2xl p-4 mt-4">
        <p class="cute text-xl font-extrabold text-sky-700">🖼️ 搜不到？換以圖搜圖</p>
        <div class="grid md:grid-cols-2 gap-4 mt-2">
          <div><p class="font-bold text-slate-700 mb-2">圖片：智慧鏡頭，或相機圖示貼上圖片</p>%(V5)s</div>
          <div><p class="font-bold text-slate-700 mb-2">影片：<kbd>Win</kbd>＋<kbd>Shift</kbd>＋<kbd>S</kbd> 截圖，再搜</p>%(V6)s</div>
        </div>
      </div>
    </div>

    <div class="bg-emerald-50 border-4 border-emerald-200 rounded-3xl p-5 mb-5">
      <p class="cute text-2xl font-extrabold text-emerald-700 mb-3">%(N2)s讀懂查核文章，記下結果和網址</p>
      <div class="grid md:grid-cols-2 gap-4 items-start">
        <ol class="list-decimal pl-6 text-xl font-bold space-y-2">
          <li>看標題前的<span class="text-emerald-700">標籤</span>（錯誤、誤導…）</li>
          <li>讀最上面的「<span class="text-emerald-700">你可以先知道</span>」</li>
          <li>找到<span class="text-emerald-700">網址列</span>並複製，等下會用到</li>
        </ol>
        <div class="bg-white border-2 border-rose-200 rounded-2xl p-3 text-lg text-slate-700">⚠️ AI 摘要先跳過。新聞、貼文是<b>轉載</b>，要點到<b>原始的查核機構</b>。</div>
      </div>
      <p class="mt-4 text-lg font-bold text-rose-700">📌 查核文章的分頁<b>先不要關</b>：等一下要從它複製圖片、標題和網址。</p>
      <label class="block mt-3 text-lg font-bold text-slate-700">把查核文章的<b>網址</b>貼在這裡，下次就找得回來
        <input class="urlKeep mt-1 w-full border-2 border-slate-300 rounded-xl px-3 py-2 text-base bg-white" autocomplete="off"></label>
    </div>
    <div class="stepnav"></div>
  </section>

%(S4)s

%(S5)s
%(S6)s

  <!-- ===== 步驟 7：繳交 ===== -->
  <section class="step hidden" data-step="7">
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-indigo-700">✅ 繳交前自己檢查</h2>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="chk"></span></div>
      <div id="chkOpts" class="space-y-2 mt-3"></div>
      <div class="bg-amber-50 border-2 border-amber-300 rounded-2xl p-4 mt-4 text-lg">
        <p class="font-bold text-amber-800">⚠️ Classroom 的作業先<span class="text-rose-600">不要按「繳交」</span>，下一節還要繼續寫完。</p>
        <p class="mt-1">今天只要按下面的<span class="text-indigo-700 font-bold">「繳交學習單」</span>。</p>
      </div>
    </div>%(REWARD)s
    <div class="stepnav"></div>
  </section>
''' % {'TASKS_S': tasks('1'), 'TASKS_A': tasks('2'), 'TASKS_B': tasks('34'),
       'N1': no('2', 'bg-teal-600'), 'N2': '👉 接著：', 'N3': no('3', 'bg-blue-600'),
       'N4': no('4', 'bg-indigo-600'), 'N5': no('5', 'bg-amber-500'),
       'DOC': DOC, 'CHIPS': chips7('bg-indigo-100 border-2 border-indigo-200', 'bg-slate-100 border-2 border-slate-200'),
       'V7': vid('教學_複製傳言圖片貼入文件.mp4', '教學_複製傳言圖片貼入文件_封面.jpg', '操作影片：複製原始訊息的圖，貼進文件（約 15 秒）'),
       'V2': vid('教學_貼上欄位設標題.mp4', '教學_貼上欄位設標題_封面.jpg', '操作影片：貼上欄位、設定標題 1 與標題 2（約 40 秒）'),
       'CARDS': CARDS, 'S4': L5S.STEP_PREP, 'S5': L5S.STEP_RECALL, 'S6': L5S.STEP_WRITE, 'DEMO': L5S.DEMO_SC,
       'V1': vid('教學_找到查核文章.mp4', '教學_找到查核文章_封面.jpg', '操作影片：從訊息找到查核文章（約 1 分鐘）'),
       'V5': vid('教學_以圖搜圖兩種方法.mp4', '教學_以圖搜圖兩種方法_封面.jpg', '操作影片：以圖搜圖兩種方法（約 1 分 15 秒）'),
       'V6': vid('截圖google圖片搜尋_字卡.mp4', '截圖google圖片搜尋_字卡_封面.jpg', '操作影片：截圖再以圖搜圖（L04，約 22 秒）'),
       'LINKS': LINKS, 'REWARD': REWARD}

L05_CFG = {
    'ws': 'g5-L05', 'lessonPath': 'g5/L05', 'title': 'Docs 查證文件（一）：找到查核文章', 'stateKey': 'g5L05flow',
    'steps': ['看成品', '選訊息', '我來查', '準備文件', '回想', '寫文件', '繳交'],
    'reveals': [], 'revealOf': {}, 'autoFb': ['c1'],
    'qtypes': {'sel': 'experience', 'c1': 'experience',
               'chk': 'experience'},
    'choices': {
        'sel': {'opts': ['C', 'D', 'E', 'G', 'H', 'K'], 'card': True},
        'c1': {'opts': ['會', '不會'], 'correct': '不會'},
        'chk': {'opts': ['查核文章是查核機構自己的網站，不是轉載', '標題用「標題 1」、欄位名稱用「標題 2」', '「我選的訊息」下面貼了原始訊息的圖片或影片截圖', '前 4 欄都寫好了', '「查核網址」的標題是連結，而且點得開'], 'multi': True, 'block': True},
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
    if(n===2)return !!state.sel;
    if(n===4)return answered('c1');
    if(n===5)return !!state.prog;
    if(n===6)return colCount()===4;
    return null;
  };
  H.report=function(){
    return ['選的訊息：'+(state.sel&&CARDS[state.sel]?CARDS[state.sel].name:'還沒選'),
      '前四欄自己標記完成：'+colCount()+'／4',
      '提醒：Classroom 的文件先不要按「繳交」，下一節還要繼續寫'];
  };
  H.showAnswers=function(){
    if(!state.sel)state.sel='C';
    state.c1='不會';
  };
  H.clear=function(){
    state.sel=null;state.c1=null;state.chk=[];state.prog=null;state.col=null;state.colDone={};
  };
  var STARS={C:1,D:2,E:3,G:2,H:1,K:2};
  H.changed=function(q){
    if(q==='c1')showC1();
  };
  function showC1(){var e=$('c1Expl');if(e)e.classList.toggle('hidden',!answered('c1'));}
  H.render=function(){
    showC1();renderL5b();
    document.querySelectorAll('[data-card]').forEach(function(c){
      var on=state.sel===c.dataset.card;c.classList.toggle('on',on);
      var b=c.querySelector('[data-pick]');b.textContent=on?'✔ 我選這則':'選這則';
    });
    var s=state.sel&&CARDS[state.sel];
    $('selName').textContent=s?s.name+'　難度 '+'★'.repeat(STARS[state.sel])+'☆'.repeat(3-STARS[state.sel]):'（還沒選，請回上一步）';
    $('hintBox').textContent=s?s.hint:'';
    if($('tplText'))$('tplText').textContent=buildTpl();
  };
  document.querySelectorAll('[data-pick]').forEach(function(b){
    b.onclick=function(){state.sel=b.dataset.pick;save();H.render();renderStepper();};
  });
'''

L05_HOOKS = L05_HOOKS + L5S.HOOKS + L5S.RESCUE_JS

L05_SPEC = {
    'summary': '用「關鍵詞＋查核」或以圖搜圖，從 6 則真實網傳訊息中選一則，找到台灣事實查核中心或 MyGoPen 已發布的查核文章，看懂結果標籤，並在 Google 文件寫好標題與前四欄（我選的訊息、我怎麼找到查核文章的、查核結果、查核網址）。',
    'questions': [
        {'qid': 'doc', 'prompt': '你的 Google 文件（老師從 Classroom 作業讀取文件內容）：標題與前四欄「我選的訊息（含原始訊息圖片）」「我怎麼找到查核文章的」「查核結果」「查核網址」。',
         'mode': 'checklist',
         'checks': [
             {'desc': '有標題，並用自己的話說明選的是哪一則訊息，有寫出人、事、時、地、物（沒寫的標「沒說」），下面貼了原始訊息的圖片或影片截圖', 'pts': 6},
             {'desc': '依序說出圈了哪些關鍵詞（或哪張圖）、在 Google 搜了什麼、點進哪個網站，並說明為什麼認定它是查核機構', 'pts': 6},
             {'desc': '寫出查核機構標的結果（例如錯誤、誤導）和是哪一家機構', 'pts': 4},
             {'desc': '「查核網址」放了查核文章的標題，並做成可以點的連結', 'pts': 4}]}],
    'scoring': {'base': 100, 'floor': 80, 'deduction': 1, 'itemPoints': {}},
}

# =====================================================================
# L06
# =====================================================================
OLD_S23 = '  <!-- ===== 步驟 5：抄與整理 ===== -->\n  <section class="step hidden" data-step="5">\n    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">\n      <h2 class="cute text-3xl font-extrabold text-amber-700">📝 「整理」不是「複製」</h2>\n      <p class="text-slate-700 mt-2 text-lg">把<b>整理</b>想成「向朋友轉述」：朋友沒看過那篇文章，你用一兩句話告訴他「這則訊息是真的嗎？為什麼？」。把整本書遞給他，他還是不知道重點。</p>\n    </div>\n    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">\n      <div class="flex items-center gap-2 flex-wrap">\n        <h3 class="cute text-2xl font-extrabold text-violet-700 m-0">✋ 先猜猜看</h3>\n        <button data-reveal-btn="r1" class="hidden shrink-0 bg-rose-500 hover:bg-rose-600 text-white text-sm font-bold rounded-lg px-3 py-1.5">🎉 公布</button>\n      </div>\n      <p class="text-slate-600 mt-2 text-lg">兩種寫法說的是同一件事：警方說，台灣沒有這種案件。哪一種是「<b>整理成自己的話</b>」？</p>\n      <div class="grid md:grid-cols-2 gap-4 mt-3 text-lg">\n        <div class="bg-slate-50 border-2 border-slate-200 rounded-2xl p-4"><p class="font-bold text-slate-700">A</p><p class="mt-1">經查，查核中心洽詢刑事警察局後，警方表示目前國內並無查獲與網傳手法相同之案件，且 165 反詐騙專線亦表示，台灣無此類案例。</p></div>\n        <div class="bg-slate-50 border-2 border-slate-200 rounded-2xl p-4"><p class="font-bold text-slate-700">B</p><p class="mt-1">警方和 165 反詐騙專線說，台灣目前查不到這種手法的案件。</p></div>\n      </div>\n      <div class="flex items-center gap-2 flex-wrap mt-3"><p class="font-bold text-violet-800">我覺得是</p><span class="qtypeSlot" data-qid="s1"></span><span id="s1Fb" class="text-sm font-bold"></span></div>\n      <div id="s1Opts" class="flex flex-wrap gap-2 mt-1"></div>\n      <p data-wait="r1" class="text-center text-slate-400 mt-4">🔒 答案等老師公布</p>\n      <div data-r="r1" class="hidden mt-4 flip bg-rose-50 border-2 border-rose-200 rounded-2xl p-4 text-lg text-slate-700 space-y-2">\n        <p>🎉 <b>B 是整理。</b>A 像是把文章整段貼來，句子長又難懂；B 一句話就把重點說完，而且是你自己說得出口的話。</p>\n        <p>💡 發現了嗎？整理＝<b>只留重點、用自己的話、標出是誰說的</b>。</p>\n      </div>\n    </div>\n    <div class="bg-white border-4 border-amber-200 rounded-3xl p-6">\n      <h3 class="cute text-2xl font-extrabold text-amber-700">👩\u200d🏫 示範：寫「正確資訊」</h3>\n      <p class="text-slate-600 mt-1">成品範例的「正確資訊」，每點一句、用自己的話：</p>\n      <ol class="list-decimal pl-6 mt-3 space-y-2 text-lg text-slate-700">\n        <li>只有指紋、臉或聲音，不能直接拿去貸款。銀行貸款還要看身分證、手機簡訊驗證碼等好幾道檢查。</li>\n        <li>警方和 165 反詐騙專線說，台灣目前查不到這種手法的案件。</li>\n        <li>不過，有人被騙去做「臉部認證」，結果存款被轉走。所以遇到陌生人要你做驗證，還是要小心。</li>\n      </ol>\n      <p class="mt-3 text-slate-600 text-lg">✍️ 句型：<b>「根據○○，……」「○○說，……」「不過，……」</b>。順序：先講<b>最重要的結論</b> → 再講<b>證據</b> → 最後講<b>還是要小心什麼</b>。</p>\n    </div>\n    <div class="stepnav"></div>\n  </section>\n\n  <!-- ===== 步驟 6：廣傳後果 ===== -->\n  <section class="step hidden" data-step="6">\n    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">\n      <h2 class="cute text-3xl font-extrabold text-rose-700">📣 為什麼會被廣傳？相信的話會怎樣？</h2>\n      <p class="text-slate-700 mt-2 text-lg">假訊息不只是「是假的」。要說得出：<b>大家為什麼會轉傳它</b>，和<b>相信它的後果</b>。</p>\n      <div class="grid md:grid-cols-2 gap-4 mt-4">\n        <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-4"><p class="cute text-xl font-extrabold text-rose-700">為什麼會轉傳（5 類）</p>\n          <ul class="mt-2 space-y-1 text-lg text-slate-700"><li>😨 <b>怕</b>：講得很可怕</li><li>🤩 <b>好奇／驚奇</b>：聽起來很厲害</li><li>👨\u200d👩\u200d👧 <b>關心家人</b>：「轉傳等於救人」</li><li>🎁 <b>好康</b>：免費、搶先</li><li>🤝 <b>親友傳來的</b>：因為信任</li></ul></div>\n        <div class="bg-amber-50 border-2 border-amber-200 rounded-2xl p-4"><p class="cute text-xl font-extrabold text-amber-700">相信的後果（4 類）</p>\n          <ul class="mt-2 space-y-1 text-lg text-slate-700"><li>🩺 <b>身體</b>：吃錯、做錯</li><li>💰 <b>錢</b>：被騙</li><li>🤝 <b>人際</b>：誤會、吵架</li><li>😱 <b>恐慌</b>：嚇到更多人、再轉傳</li></ul></div>\n      </div>\n    </div>\n\n    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">\n      <div class="flex items-center gap-2 flex-wrap">\n        <h3 class="cute text-2xl font-extrabold text-violet-700 m-0">✋ 先猜猜看：示範訊息為什麼會被轉傳？</h3>\n        <button data-reveal-btn="r2" class="hidden shrink-0 bg-rose-500 hover:bg-rose-600 text-white text-sm font-bold rounded-lg px-3 py-1.5">🎉 公布</button>\n      </div>\n      <p class="text-slate-600 mt-2 text-lg">「<b>幫陌生人操作手機，會被盜走指紋、聲音和臉，30 分鐘傾家蕩產。轉傳給家人朋友！</b>」大家轉傳它的原因有哪些？（可複選）</p>\n      <div class="flex items-center gap-2 flex-wrap mt-3"><span class="qtypeSlot" data-qid="s2"></span><span id="s2Fb" class="text-sm font-bold"></span></div>\n      <div id="s2Opts" class="flex flex-wrap gap-2 mt-1"></div>\n\n      <p class="font-bold text-violet-800 text-lg mt-6">下面哪一句「相信的後果」寫得最好？</p>\n      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="s3"></span><span id="s3Fb" class="text-sm font-bold"></span></div>\n      <div id="s3Opts" class="space-y-2 mt-1"></div>\n      <p data-wait="r2" class="text-center text-slate-400 mt-4">🔒 答案等老師公布</p>\n      <div data-r="r2" class="hidden mt-4 flip bg-rose-50 border-2 border-rose-200 rounded-2xl p-4 text-lg text-slate-700 space-y-2">\n        <p>🎉 <b>原因</b>：它說「30 分鐘傾家蕩產」，讓人<b>怕</b>；又寫「轉傳給家人朋友」，大家覺得轉出去是在<b>關心家人</b>；還提到 AI 和手機，聽起來很厲害，帶點<b>好奇</b>。</p>\n        <p>🎉 <b>後果寫得最好的是 C</b>：它說出<b>誰</b>會<b>怎樣</b>（不敢幫人、嚇到更多人）。「會被騙」沒說誰、也沒說怎麼被騙；「這則是假的」是結果，不是後果。</p>\n      </div>\n    </div>\n    <div class="stepnav"></div>\n  </section>\n\n'
OLD_S8 = '  <!-- ===== 步驟 8：繳交 ===== -->\n  <section class="step hidden" data-step="8">\n    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">\n      <h2 class="cute text-3xl font-extrabold text-indigo-700">✅ 繳交前自己檢查</h2>\n      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="chk"></span></div>\n      <div id="chkOpts" class="space-y-2 mt-3"></div>\n      <div class="bg-indigo-50 border-2 border-indigo-200 rounded-2xl p-4 mt-4 text-lg text-slate-700">\n        <p class="font-bold text-indigo-800">繳交兩個地方：</p>\n        <ol class="list-decimal pl-6 mt-1 space-y-1"><li>回 <b>Classroom 作業</b>，確認文件<b>附在作業裡</b>，按<b>「繳交」</b>。</li><li>回到這裡，按下面的<b>「繳交學習單」</b>。</li></ol>\n        <p class="text-sm text-slate-500 mt-2">還沒寫完也可以先交，下一節開頭還有時間補。</p>\n      </div>\n    </div>@@REWARD@@\n    <div class="stepnav"></div>\n  </section>\n'

def _tone_block(tone, title, hint, ex_html, why_html, guide_html, extra=''):
    return ('<div class="bg-white border-4 border-%(t)s-300 rounded-3xl p-5 mb-5 shadow-sm">'
            '<h3 class="cute text-2xl font-extrabold text-%(t)s-700 m-0">%(title)s<span class="text-base font-bold text-slate-500 ml-2">%(hint)s</span></h3>'
            '<div class="grid md:grid-cols-3 gap-3 mt-3 text-lg">'
            '<div class="bg-amber-50 border-2 border-amber-200 rounded-2xl p-3"><p class="font-extrabold text-amber-800">📝 範例（打雷戴藍芽耳機）</p><div class="mt-1 text-slate-800">%(ex)s</div></div>'
            '<div class="bg-sky-50 border-2 border-sky-200 rounded-2xl p-3"><p class="font-extrabold text-sky-800">💡 為什麼這樣寫</p><div class="mt-1 text-slate-700">%(why)s</div></div>'
            '<div class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-3"><p class="font-extrabold text-emerald-800">✅ 我檢查自己寫的</p><div class="mt-1 text-slate-700">%(guide)s</div></div>'
            '</div>%(extra)s</div>') % {'t': tone, 'title': title, 'hint': hint, 'ex': ex_html, 'why': why_html, 'guide': guide_html, 'extra': extra}


def _checks(*items):
    return '<ul class="space-y-1">' + ''.join('<li>☐ %s</li>' % i for i in items) + '</ul>'


def _chips(items, cls='bg-white border-2 border-slate-300 text-slate-700'):
    return '<div class="flex flex-wrap gap-1.5 mt-2">' + ''.join('<span class="%s rounded-full px-3 py-0.5 text-base font-bold">%s</span>' % (cls, t) for t in items) + '</div>'


def _clips(slides, opened=False, label="🎬 不會做？看動圖"):
    return ('<details%s class="mt-3 bg-white border-2 border-slate-300 rounded-2xl p-3"><summary class="cursor-pointer font-extrabold text-slate-700 text-lg">%s</summary>'
            '<div class="mt-2">' + L5S.sc(slides) + '</div></details>') % (' open' if opened else '', label)


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

_E_LINK = '<span class="text-indigo-700 underline">台灣事實查核中心：打雷時使用手機、藍牙耳機會被雷擊？</span>'
_BLK_TITLE = _tone_block('sky', '標題', '把「我的查證文件」換成你查的那一則',
    '<p class="text-slate-500">我的查證文件</p><p class="text-2xl">↓</p><p class="font-extrabold">打雷戴藍芽耳機會被雷擊？</p>',
    '<p>標題讓別人<b>一眼看出你查的是哪一則</b>，所以要換掉原本的字。</p><p class="mt-1">用疑問句或短句，10～20 個字。</p>',
    _checks('最上面不是「（文件標題）」或「我的查證文件」', '看標題就知道在查什麼', '已經設成「標題 1」'))
_BLK_URL = _tone_block('indigo', '① 查核網址', '放在標題下面、先貼',
    '<p>' + _E_LINK + '</p><p class="text-sm text-slate-500 mt-1">（示意；標題以你看到的那篇為準）</p>',
    '<p>讓讀的人<b>自己點進去驗證</b>。要放在<b>標題下面</b>。</p><p class="mt-1">要是<b>查核機構自己</b>的網站（tfc-taiwan、mygopen），轉載的不算。</p>',
    _checks('是查核機構自己的網站', '標題是藍色、有底線', '點一下真的開得起來', '沒有網址？回第 1 步找回'),
    _clips([
        L5S.slide('點一下<b>網址列</b>，複製網址', '步_網址1_複製網址列'),
        L5S.slide('回文件，<b>選取標題</b>', '步_網址2_選取標題'),
        L5S.slide('<b>Ctrl＋K</b>，貼上網址，按「套用」', '步_網址3_插入連結')], True, '🎬 複製網址、做成連結：看動圖'))
_BLK_MSG = _tone_block('amber', '② 我選的訊息', '人事時地物＋傳播，用自己的話',
    '<p>網傳訊息說：苗栗一位<b>健身教練</b>（人）<b>打雷時在戶外慢跑</b>（事、時、地），疑似戴著<b>藍芽耳機</b>（物）被雷擊身亡，所以呼籲大家打雷時絕對不要用手機接電話或上網。這則訊息在 <b>LINE 和臉書</b>流傳，還附了新聞影片（傳播）。</p>',
    '<p>讀的人沒看過原始訊息，要能<b>只看你這段</b>就知道訊息在說什麼、怎麼傳開的。</p><p class="mt-1">缺的就寫「沒說」，不要亂猜。</p>',
    '<div class="grid grid-cols-2 gap-1 text-base"><p>👤 <b>人</b>：誰說的？說誰會怎樣？</p><p>📌 <b>事</b>：發生什麼？要大家做什麼？</p><p>🕒 <b>時</b>：什麼時候？</p><p>📍 <b>地</b>：在哪裡？</p><p>🎒 <b>物</b>：提到什麼東西？</p><p>📣 <b>傳播</b>：在哪看到、怎麼傳？</p></div>'
    + _checks('是自己的話，不是整段貼', '六個都想過了', '下面貼了原始訊息的圖'),
    _clips([
        L5S.slide('找到<b>原始訊息的圖</b>', '步_圖1_找圖'),
        L5S.slide('在圖上按右鍵，<b>複製圖片</b>', '步_圖2_複製圖片'),
        L5S.slide('回文件，<b>貼在句子下面</b>', '步_圖3_貼上')]))
_BLK_HOW = _tone_block('teal', '③ 我怎麼找到查核文章的', '照順序寫 4 件事',
    '<p>我圈出「打雷」「藍芽耳機」「雷擊」，在 Google 搜「打雷 藍芽耳機 雷擊 查核」，第一個就是台灣事實查核中心的文章。tfc-taiwan.org.tw 是專門查謠言的機構，不是轉載，所以我點進去。</p>',
    '<p>讓別人<b>照你的步驟也找得到</b>，也說明你點的是<b>查核機構</b>，不是轉載或 AI 摘要。</p>',
    '<ol class="list-decimal pl-5"><li>圈了哪些<b>關鍵詞</b>（2～3 個）</li><li>Google 搜了<b>什麼字</b>（有加「查核」）</li><li>點進<b>哪個網站</b></li><li><b>為什麼</b>它是查核機構</li></ol>' + _checks('四件事都寫了'))
_BLK_RES = _tone_block('rose', '④ 查核結果', '哪一家、標了什麼、重點一句',
    '<p>台灣事實查核中心查核後，標為「<b>事實釐清</b>」：重點是<b>空曠處才是關鍵</b>，不是手機或藍芽耳機本身。</p>',
    '<p>只寫「是假的」不夠。要寫<b>哪一家</b>＋<b>標了什麼</b>＋<b>一句重點</b>（看「你可以先知道」）。</p>',
    '<p class="text-base">標籤有這些：</p>' + _chips(_LABELS, 'bg-amber-100 border-2 border-amber-300 text-amber-900') + _checks('寫了機構名', '標籤照查核文章寫', '加了一句重點', '⭐ 加分：另一家機構也一樣嗎？'))

STEP_L06_4 = '''
  <!-- ===== 步驟 4：檢查前四欄（含標題）===== -->
  <section class="step hidden" data-step="4">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700 m-0">🔎 檢查自己寫的：標題＋前四欄</h2>
      <p class="text-lg text-slate-600 mt-1">每一欄都有<b>範例、為什麼這樣寫、檢查方法</b>。範例用「打雷戴藍芽耳機」，你的內容要換成<b>你自己選的那一則</b>。慢慢來，一欄一欄對。</p>
    </div>
    @@BLOCKS@@
    <div class="stepnav"></div>
  </section>
'''.replace('@@BLOCKS@@', _BLK_TITLE + _BLK_URL + _BLK_MSG + _BLK_HOW + _BLK_RES)

_BLK_WHY = _tone_block('violet', '⑤ 為什麼這則訊息會被廣傳？', '至少一類，要有理由',
    '<p>因為<b>真的有人遭雷擊、新聞也報過</b>，很多人覺得可信（<b>親友傳來</b>）；又和人人都有的手機有關，家人看了會<b>怕</b>，覺得轉傳是<b>關心家人</b>。</p>',
    '<p>說得出<b>人們為什麼轉傳</b>，下次看到才知道先停一下。只寫「因為很多人信」不夠，要說<b>哪裡讓人這樣想</b>。</p>',
    '<p class="text-base">五類原因：</p>' + _chips(['😨 怕', '🤩 好奇／驚奇', '👨‍👩‍👧 關心家人', '🎁 好康', '🤝 親友傳來']) + _checks('選了至少一類', '寫了「哪裡讓人這樣想」'))
_BLK_FACT = _tone_block('emerald', '⑥ 正確資訊', '1～3 點，每點一句、自己的話、標機構',
    '<ol class="list-decimal pl-5 space-y-1"><li><b>根據台灣事實查核中心</b>，遭雷擊的關鍵是人在<b>空曠處</b>，不是手機或藍芽耳機。</li><li>所以打雷時，要先<b>離開空曠的地方</b>。</li><li><b>不過</b>，也不是「不碰手機就安全」，留在空曠處才是重點。</li></ol>',
    '<p>讀的人要知道<b>事實是什麼</b>。用自己的話、標出<b>是誰說的</b>，才不是把別人的文章搬過來。</p><p class="mt-1">先講最重要的結論，最後講「還要小心什麼」。</p>',
    '<p class="text-base">句型：<b>根據○○，……</b>／<b>○○說，……</b>／<b>不過，……</b></p>' + _checks('1～3 點，每點一句', '每點標了機構', '沒有整段複製', '最重要的結論放第一點'))
_BLK_RISK = _tone_block('rose', '⑦ 如果相信的話，會有什麼後果？', '寫「誰」會「怎樣」',
    '<p>有人會<b>嚇得連手機都不敢用</b>；也有人以為<b>只要不碰手機就安全</b>，反而留在空曠處慢跑或逗留，<b>更危險</b>。</p>',
    '<p>後果要寫<b>誰會怎樣</b>。「是假的」是查核結果，不是後果；「會被騙」沒說誰、怎麼被騙。</p>',
    '<p class="text-base">四類後果：</p>' + _chips(['🩺 身體', '💰 錢', '🤝 人際', '😱 恐慌']) + _checks('寫了「誰」', '寫了「會怎樣」', '是具體的事，不是「不好」'))

STEP_L06_7 = '''
  <!-- ===== 步驟 7：檢查後三欄 ===== -->
  <section class="step hidden" data-step="7">
    <div class="bg-white border-4 border-teal-300 rounded-3xl p-5 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-teal-700 m-0">🔎 檢查自己寫的：後 3 欄</h2>
      <p class="text-lg text-slate-600 mt-1">一樣用「打雷戴藍芽耳機」當範例。時間不夠時，照這個順序寫：<b>正確資訊 → 為什麼廣傳 → 後果</b>。</p>
    </div>
    @@BLOCKS@@
    <div class="stepnav"></div>
  </section>
'''.replace('@@BLOCKS@@', _BLK_WHY + _BLK_FACT + _BLK_RISK)

L06_BODY = ('\n' + STEP_L06_1 + '\n' + STEP_L06_2 + '\n' + L5S.step_prep(3, '上一節做過的，直接按「下一步」跳過；還沒做的，一步一步補。').replace('<!-- ===== 準備文件（步驟卡）===== -->', '<!-- ===== 步驟 3：準備文件 ===== -->')
            + '\n' + STEP_L06_4 + '\n' + OLD_S23 + '\n' + STEP_L06_7 + '\n' + OLD_S8 + '\n')
L06_BODY = (L06_BODY.replace('@@RESCUE@@', L5S.RESCUE.replace('<details class="urlfix', '<details open class="urlfix', 1))
            .replace('@@CARDS@@', CARDS).replace('@@DOC@@', DOC).replace('@@REWARD@@', REWARD)
            .replace('@@CHIPS@@', chips7('bg-slate-100 border-2 border-slate-200', 'bg-indigo-100 border-2 border-indigo-200')))

L06_CFG = {
    'ws': 'g5-L06', 'lessonPath': 'g5/L06', 'title': 'Docs 查證文件（二）：整理成報告', 'stateKey': 'g5L06flow',
    'steps': ['找回資料', '選訊息', '準備文件', '檢查前四欄', '抄與整理', '廣傳後果', '檢查後三欄', '繳交'],
    'reveals': ['r1', 'r2'], 'revealOf': {'s1': 'r1', 's2': 'r2', 's3': 'r2'}, 'autoFb': ['c1'],
    'qtypes': {'sel': 'experience', 'c1': 'experience', 's1': 'experience', 's2': 'experience', 's3': 'experience', 'chk': 'experience'},
    'choices': {
        'sel': {'opts': ['C', 'D', 'E', 'G', 'H', 'K'], 'card': True},
        'c1': {'opts': ['會', '不會'], 'correct': '不會'},
        's1': {'opts': ['A', 'B'], 'correct': 'B'},
        's2': {'opts': ['怕', '好奇／驚奇', '關心家人', '好康', '親友傳來的'], 'multi': True, 'correct': ['怕', '好奇／驚奇', '關心家人']},
        's3': {'opts': ['A．會被騙。', 'B．這則訊息是假的。', 'C．我們可能不敢幫真的需要幫忙的人，也會把嚇人的訊息再傳給更多人，讓大家一起害怕。'], 'block': True,
               'correct': 'C．我們可能不敢幫真的需要幫忙的人，也會把嚇人的訊息再傳給更多人，讓大家一起害怕。'},
        'chk': {'opts': ['標題和前四欄都對照檢查過了', '「正確資訊」有標出處，沒有整段複製', '「為什麼廣傳」和「後果」都寫了理由', '「查核網址」的連結點得開'], 'multi': True, 'block': True},
    },
    'texts': [], 'patterns': {}, 'openQtexts': {},
}

_a = L05_HOOKS.index("  // ===== 複製七個欄位")
_z = L05_HOOKS.index("  H.stepDone=function(n){")
L06_HOOKS = L05_HOOKS[_a:_z] + L5S.RESCUE_JS + r'''
  var STARS={C:1,D:2,E:3,G:2,H:1,K:2};
  function showC1(){var e=$('c1Expl');if(e)e.classList.toggle('hidden',!answered('c1'));}
  H.stepDone=function(n){
    if(n===2)return !!state.sel;
    if(n===3)return answered('c1');
    if(n===5)return answered('s1');
    if(n===6)return answered('s2')&&answered('s3');
    return null;
  };
  H.changed=function(q){if(q==='c1')showC1();};
  H.report=function(){
    return ['選的訊息：'+(state.sel&&CARDS[state.sel]?CARDS[state.sel].name:'還沒選'),
      '自查表：已勾 '+((state.chk||[]).length)+' 項（共 4 項）','提醒：文件要附在 Classroom 作業裡，並在那邊按「繳交」'];
  };
  H.showAnswers=function(){
    if(!state.sel)state.sel='E';
    state.c1='不會';state.s1='B';state.s2=['怕','好奇／驚奇','關心家人'];state.s3=C.choices.s3.correct;
  };
  H.clear=function(){state.sel=null;state.url='';state.c1=null;state.s1=null;state.s2=[];state.s3=null;state.chk=[];};
  H.render=function(){
    showC1();bindRescue();renderRescue();
    document.querySelectorAll('[data-card]').forEach(function(c){
      var on=state.sel===c.dataset.card;c.classList.toggle('on',on);
      var bt=c.querySelector('[data-pick]');bt.textContent=on?'✔ 我選這則':'選這則';
    });
    if($('tplText'))$('tplText').textContent=buildTpl();
  };
  document.querySelectorAll('[data-pick]').forEach(function(bt){
    bt.onclick=function(){state.sel=bt.dataset.pick;save();H.render();renderStepper();};
  });
'''

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

def write(name, folder, html):
    p = os.path.join(ROOT, folder, name)
    io.open(p, 'w', encoding='utf8', newline='\n').write(html)
    print('wrote', p, len(html) // 1024, 'KB')

write('五上_L05_Docs查證文件一.html', 'L05_Docs查證文件一',
      page('訊息查證小偵探｜五上 L05 教學活動', '🔎 訊息查證小偵探',
           '五年級上學期 · L05 Docs 查證文件（一）· 教學活動流程（40 分鐘）', L05_BODY, L05_CFG, L05_HOOKS, L05_SPEC, L5S.CSS))
write('五上_L06_Docs查證文件二.html', 'L06_Docs查證文件二',
      page('整理成查證文件｜五上 L06 教學活動', '📝 把查核文章整理成自己的報告',
           '五年級上學期 · L06 Docs 查證文件（二）· 教學活動流程（40 分鐘）', L06_BODY, L06_CFG, L06_HOOKS, L06_SPEC, L5S.CSS))
