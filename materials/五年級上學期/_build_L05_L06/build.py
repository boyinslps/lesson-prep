# -*- coding: utf-8 -*-
# 產生五上 L05、L06 兩份學習單（高年級：一個環節一步的步驟分頁）。
# 骨架（識別列、教師列、進度列、點圖放大、Firebase 登入）直接取自五上 L04，確保行為一致；
# 內容與題目寫在下面。生成後請執行 引導規範/chair-gate/inject.py 內嵌「靠椅子」關卡。
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
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

def page(title, h1, sub, body, cfg, hooks, spec):
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
        title, CSS + EXTRA_CSS, TOPBARS, h1, sub, body, LIGHTBOX, FBCFG,
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
    ('1', '我選的訊息', '用自己的話說：這則訊息在講什麼', True),
    ('2', '我怎麼找到查核文章的', '用了哪個關鍵詞、哪張圖', True),
    ('3', '查核結果', '查核機構標了什麼？是哪一家？', True),
    ('4', '查核網址', '查核文章的標題，做成可以點的連結', True),
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
# =====================================================================
L05_BODY = '''
  <!-- ===== 步驟 1：看成品 ===== -->
  <section class="step" data-step="1">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-6 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">📄 這兩節，你要做出這樣一份查證文件</h2>
      <p class="text-slate-600 mt-2 text-lg">老師先帶大家看一份成品：把一則網傳訊息查清楚，整理成 Google 文件。文件有 <b>7 欄</b>，<b>今天先做前 4 欄</b>，下一節做後 3 欄。</p>
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
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 shadow-sm">
      <h2 class="cute text-2xl font-extrabold text-rose-700">🤔 想一想</h2>
      <p class="text-slate-700 mt-2 text-lg">這份文件的 7 欄，你覺得<b>哪一欄最難寫</b>？為什麼？</p>
      <p class="text-slate-700 mt-3 text-lg">💡 不用從零查證：今天要學的是<b>找到別人已經查好的那一篇</b>，再讀懂它。</p>
    </div>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 2：標題設定 ===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-indigo-700">🧰 複習：用「標題 1」「標題 2」做出層次</h2>
      <p class="text-slate-600 mt-2 text-lg">Google 文件左上角那個「內文」按鈕裡，藏著各種<b>樣式</b>。這份文件用兩種：整份文件的題目用<b>標題 1</b>，每一欄的名字用<b>標題 2</b>。用樣式設定，左邊的「大綱」才找得到每一段。</p>
      <div class="mt-4">%(V2)s</div>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 shadow-sm">
      <h3 class="cute text-2xl font-extrabold text-violet-700 m-0">✋ 先猜猜看</h3>
      <div class="flex items-center gap-2 flex-wrap mt-3"><p class="font-bold text-violet-800 text-lg">如果我只把「我選的訊息」這幾個字改成 16 號大字，它會變成「標題 2」嗎？</p><span class="qtypeSlot" data-qid="c1"></span><span id="c1Fb" class="text-sm font-bold"></span></div>
      <div id="c1Opts" class="flex flex-wrap gap-2 mt-2"></div>
      <div id="c1Expl" class="hidden mt-4 flip bg-rose-50 border-2 border-rose-200 rounded-2xl p-4 text-lg text-slate-700">
        <p>🎉 答案是<b>不會</b>。只是字變大，左邊的「大綱」裡找不到它。<b>用「樣式」選了標題 2，才算標題 2</b>，文件才有層次。</p>
      </div>
    </div>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 3：示範 ===== -->
  <section class="step hidden" data-step="3">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700">👩‍🏫 老師示範：從訊息找到查核文章</h2>
      <p class="text-slate-600 mt-2 text-lg">還記得 L03 的<b>橫向閱讀</b>、L04 的<b>查證網站</b>和<b>以圖搜圖</b>嗎？把它們組合起來，就能找到別人<b>已經查好</b>的那一篇。看老師怎麼做：</p>
      <div class="grid md:grid-cols-2 gap-5 mt-4 items-start">
        <div>
          <img class="shotimg" src="assets/M2_B示範_陌生人手機_網傳訊息.png" alt="示範訊息：兩則臉書貼文，標題寫「人工智能生物信息詐騙，要的不是你的錢而是你這個人」，帳號已遮蔽" loading="lazy">
          <p class="text-[11px] text-slate-400 mt-1">網傳貼文擷圖（帳號已遮蔽）・點圖可放大</p>
        </div>
        <div class="text-lg text-slate-700">
          <p class="font-bold text-amber-700">示範訊息：幫陌生人操作手機，會被盜走指紋？</p>
          <p class="mt-2">訊息說：只要你摸螢幕、對著鏡頭說話，指紋、聲音和臉就會被偷走，騙子會拿去貸款，<b>30 分鐘傾家蕩產</b>。</p>
          <p class="mt-2 text-slate-500 text-base">你會信嗎？會轉傳嗎？先別急，我們來查。</p>
        </div>
      </div>
    </div>

    <div class="bg-white border-4 border-amber-200 rounded-3xl p-6 mb-5">
      <h3 class="cute text-2xl font-extrabold text-amber-700">① 圈出 2～3 個關鍵詞</h3>
      <p class="text-slate-700 text-lg mt-1">不要整句貼去搜。挑<b>人、事、物</b>最重要的幾個詞。換你選選看（<b>挑 2～3 個</b>）：</p>
      <div class="flex items-center gap-2 flex-wrap mt-2"><span class="qtypeSlot" data-qid="kwd"></span><span id="kwdFb" class="text-sm font-bold text-slate-500"></span></div>
      <div id="kwdOpts" class="flex flex-wrap gap-2 mt-2"></div>
    </div>

    <div class="grid md:grid-cols-3 gap-4 mb-5">
      <div class="bg-white border-4 border-amber-200 rounded-3xl p-5">
        <h3 class="cute text-xl font-extrabold text-amber-700">② 加上「查核」去搜</h3>
        <p class="text-slate-700 mt-1">關鍵詞＋<b>查核</b>。例：<span class="bg-amber-50 border border-amber-300 rounded-lg px-2 py-0.5 font-bold">陌生人 操作手機 生物特徵 查核</span></p>
      </div>
      <div class="bg-white border-4 border-amber-200 rounded-3xl p-5">
        <h3 class="cute text-xl font-extrabold text-amber-700">③ 認出查核機構</h3>
        <p class="text-slate-700 mt-1">網址是 <b>tfc-taiwan.org.tw</b>、<b>mygopen.com</b>，才是專門查謠言的。新聞、臉書貼文只是<b>轉載</b>。</p>
      </div>
      <div class="bg-white border-4 border-amber-200 rounded-3xl p-5">
        <h3 class="cute text-xl font-extrabold text-amber-700">④ 只讀兩個地方</h3>
        <p class="text-slate-700 mt-1">標題前的<b>標籤</b>（錯誤、誤導…），和文章最上面的「<b>你可以先知道</b>」。</p>
      </div>
    </div>

    <div class="bg-white border-4 border-teal-300 rounded-3xl p-6 mb-5">
      <h3 class="cute text-2xl font-extrabold text-teal-700">⚠️ 三條界線</h3>
      <ul class="list-disc pl-5 mt-2 space-y-2 text-lg text-slate-700">
        <li>搜尋結果最上面的 <b>AI 摘要先跳過</b>。它也會講結論，但你要讀的是<b>查核機構寫的原始文章</b>。</li>
        <li>點到<b>轉載站</b>（新聞網站、貼文）時，要再點到<b>原始的查核機構</b>。</li>
        <li>找不到時，<b>換關鍵詞</b>，或改用<b>以圖搜圖</b>，不要放棄，也不要自己亂猜結論。</li>
      </ul>
    </div>

    <div class="grid md:grid-cols-2 gap-5 mb-5">
      <div class="bg-white border-4 border-amber-200 rounded-3xl p-5">
        <h3 class="cute text-xl font-extrabold text-amber-700">🎬 找到查核文章（約 1 分鐘）</h3>
        <div class="mt-3">%(V1)s</div>
      </div>
      <div class="bg-white border-4 border-amber-200 rounded-3xl p-5">
        <h3 class="cute text-xl font-extrabold text-amber-700">🎬 以圖搜圖的兩種方法</h3>
        <div class="mt-3">%(V5)s</div>
      </div>
      <div class="bg-white border-4 border-amber-200 rounded-3xl p-5 md:col-span-2">
        <h3 class="cute text-xl font-extrabold text-amber-700">🎬 影片不能右鍵？用「截圖」再搜（L04 學過）</h3>
        <p class="text-slate-600 mt-1">影片、訊息裡的圖，用 <kbd>Win</kbd>＋<kbd>Shift</kbd>＋<kbd>S</kbd> 截圖，貼到 Google 圖片，再加關鍵字。</p>
        <div class="mt-3">%(V6)s</div>
      </div>
    </div>

    <details class="bg-white border-4 border-dashed border-amber-300 rounded-3xl p-5">
      <summary class="cute text-xl font-extrabold text-amber-700">👀 老師展開：示範的結果</summary>
      <div class="text-lg text-slate-700 mt-3 space-y-2">
        <p>🔎 MyGoPen：<b>【誤導】</b>幫陌生人操作手機會被盜取生物特徵去貸款？誇大 AI 技術！</p>
        <p>🔎 台灣事實查核中心：<b>錯誤</b>。刑事局與 165 都說，台灣查不到這種案件。</p>
        <p>💡 發現了嗎？<b>兩個查核機構的結論一致</b>，這樣更可信。</p>
      </div>
    </details>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 4：選訊息 ===== -->
  <section class="step hidden" data-step="4">
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
    </div>
    <div class="grid md:grid-cols-2 gap-5">
%(CARDS)s
    </div>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 5：我來查 ===== -->
  <section class="step hidden" data-step="5">
    <div class="bg-white border-4 border-teal-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-teal-700">🔎 換你查：找到查核文章</h2>
      <div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-4 mt-3 text-lg">
        <p>你選的是：<b id="selName" class="text-teal-800">（還沒選，請回上一步）</b></p>
        <p id="hintBox" class="text-slate-600 mt-1"></p>
      </div>
      <div class="flex flex-wrap items-center gap-3 mt-4">
        <span class="font-bold text-teal-800">🔎 去哪裡查：</span>
        <a href="https://www.google.com/" target="_blank" rel="noopener" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-2">Google 搜尋 ↗</a>
        %(LINKS)s
      </div>
      <details class="mt-4 bg-slate-50 border-2 border-slate-200 rounded-2xl p-4">
        <summary class="font-bold text-slate-700">🎬 卡住了？看影片</summary>
        <div class="grid md:grid-cols-2 gap-4 mt-3">
          <div>%(V1)s</div>
          <div>%(V5)s</div>
        </div>
      </details>
    </div>

    <div class="bg-white border-4 border-teal-200 rounded-3xl p-6 mb-5">
      <div class="space-y-5">
        <label class="block"><span class="font-bold text-teal-800 text-lg">1. 我圈的關鍵詞</span><span class="qtypeSlot ml-2" data-qid="kw"></span><input data-k="kw" class="fld ans mt-1"></label>
        <div>
          <div class="flex items-center gap-2 flex-wrap"><p class="font-bold text-teal-800 text-lg">2. 我是怎麼找到的？（可複選）</p><span class="qtypeSlot" data-qid="how"></span></div>
          <div id="howOpts" class="flex flex-wrap gap-2 mt-2"></div>
        </div>
        <div>
          <div class="flex items-center gap-2 flex-wrap"><p class="font-bold text-teal-800 text-lg">3. 查核機構標的結果是？</p><span class="qtypeSlot" data-qid="label"></span><span id="labelFb" class="text-sm font-bold"></span></div>
          <div id="labelOpts" class="flex flex-wrap gap-2 mt-2"></div>
        </div>
        <div>
          <div class="flex items-center gap-2 flex-wrap"><label for="url" class="font-bold text-teal-800 text-lg">4. 查核文章的網址（貼上，要是查核機構自己的網站）</label><span class="qtypeSlot" data-qid="url"></span><span id="urlFb" class="text-sm font-bold"></span></div>
          <input id="url" data-k="url" class="fld ans mt-1">
          <p class="text-sm text-slate-500 mt-1">在文章頁點網址列、Ctrl＋C，再回來 Ctrl＋V。</p>
        </div>
        <div>
          <div class="flex items-center gap-2 flex-wrap"><label for="url2" class="font-bold text-slate-600 text-lg">⭐ 加分：再找另一個機構的文章來比對</label><span class="qtypeSlot" data-qid="url2"></span></div>
          <input id="url2" data-k="url2" class="fld ans mt-1">
          <p class="text-sm text-slate-500 mt-1">兩個機構結論一致，更可信。</p>
        </div>
      </div>
    </div>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 6：寫文件 ===== -->
  <section class="step hidden" data-step="6">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700">✍️ 寫進你的 Google 文件</h2>
      <p class="text-slate-600 mt-1 text-lg">先把<b>格式排好</b>，再寫前 <b>3 欄</b>。</p>
    </div>

    <div class="bg-blue-50 border-4 border-blue-200 rounded-3xl p-5 mb-5">
      <p class="cute text-2xl font-extrabold text-blue-700 mb-2">① 打開老師給的文件</p>
      <div class="grid md:grid-cols-5 gap-4 items-center">
        <div class="md:col-span-3"><video class="w-full rounded-xl border-2 border-blue-200 bg-slate-900" src="assets/教學_打開文件.mp4" poster="assets/教學_打開文件_封面.jpg" controls playsinline preload="none"></video></div>
        <ol class="md:col-span-2 list-decimal pl-6 text-xl font-bold space-y-2">
          <li>作業裡點<span class="text-blue-700">老師給的文件</span></li>
          <li>改檔名：<span class="text-blue-700">年班座號＋名字</span><br><span class="text-lg text-slate-500">例：41230 王小明</span></li>
        </ol>
      </div>
      <p class="mt-3 text-lg text-rose-700 font-bold">⚠️ 一定要從 Classroom 作業裡開，老師才讀得到。</p>
    </div>

    <div class="bg-emerald-50 border-4 border-emerald-200 rounded-3xl p-5 mb-5">
      <p class="cute text-2xl font-extrabold text-emerald-700 mb-2">② 複製七個欄位 → 貼進文件</p>
      <div class="grid md:grid-cols-2 gap-4 items-start">
        <div>
          <button id="tplCopy" type="button" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white text-xl font-extrabold rounded-2xl px-4 py-3">📋 複製七個欄位</button>
          <p class="text-xl font-bold mt-3">文件第一行 → <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd></p>
          <p class="text-base text-slate-500">＝「貼上但不套用格式設定」</p>
          <p class="text-lg text-slate-600 mt-3">💡 不用按儲存　按錯了？<kbd>Ctrl</kbd> + <kbd>Z</kbd></p>
        </div>
        <pre id="tplText" class="text-lg leading-relaxed whitespace-pre-wrap font-[inherit] bg-white rounded-xl p-3 border-2 border-emerald-100"></pre>
      </div>
    </div>

    <div class="bg-indigo-50 border-4 border-indigo-200 rounded-3xl p-5 mb-5">
      <p class="cute text-2xl font-extrabold text-indigo-700 mb-2">③ 把標題和欄位名稱改好</p>
      <div class="grid md:grid-cols-2 gap-4 items-center">
        <div>%(V2)s</div>
        <ul class="list-disc pl-6 text-xl space-y-2">
          <li><b>第一行</b>（題目）→ <span class="text-indigo-700 font-bold">標題 1</span></li>
          <li><b>第二行</b>（年班座號＋名字）→ 改成<span class="text-indigo-700 font-bold">你自己的</span>，不用設樣式</li>
          <li><b>7 個欄位名稱</b> → 都改成 <span class="text-indigo-700 font-bold">標題 2</span></li>
          <li>快速鍵：選取後 <kbd>Ctrl</kbd>＋<kbd>Alt</kbd>＋<kbd>1</kbd> 或 <kbd>2</kbd></li>
        </ul>
      </div>
      <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-4 mt-4">
        <p class="cute text-2xl font-extrabold text-rose-600">多了空白、多一行？</p>
        <p class="text-xl font-bold text-slate-800 mb-2">👉 <kbd>Backspace</kbd> 刪前面　<kbd>Delete</kbd> 刪後面</p>
        <video class="w-full max-w-[560px] rounded-xl border-2 border-rose-200 bg-slate-900" src="assets/教學_排版刪除.mp4" poster="assets/教學_排版刪除_封面.jpg" controls playsinline preload="none"></video>
        <p class="text-[11px] text-slate-400 mt-1">複習影片（四上 L04）</p>
      </div>
    </div>

    <div class="bg-amber-50 border-4 border-amber-200 rounded-3xl p-5">
      <p class="cute text-2xl font-extrabold text-amber-700 mb-2">④ 完成前 4 欄</p>
      <div class="grid md:grid-cols-2 gap-4 text-lg text-slate-700">
        <div class="bg-white border-2 border-amber-200 rounded-2xl p-4"><p class="font-bold text-amber-800">我選的訊息</p><p class="mt-1">用<b>自己的話</b>說：這則訊息在講什麼？一兩句就好。</p></div>
        <div class="bg-white border-2 border-amber-200 rounded-2xl p-4"><p class="font-bold text-amber-800">我怎麼找到查核文章的</p><p class="mt-1">寫出你用的<b>關鍵詞</b>，或是哪一種以圖搜圖。</p></div>
        <div class="bg-white border-2 border-amber-200 rounded-2xl p-4"><p class="font-bold text-amber-800">查核結果</p><p class="mt-1">查核機構標了<b>什麼結果</b>？是<b>哪一家</b>？</p></div>
        <div class="bg-white border-2 border-amber-200 rounded-2xl p-4"><p class="font-bold text-amber-800">查核網址</p><p class="mt-1">放上<b>查核文章的標題</b>，做成<b>可以點的連結</b>：複製網址 → 選取標題 → <kbd>Ctrl</kbd>＋<kbd>K</kbd> → 貼上 → 套用。</p></div>
      </div>
      <p class="mt-4 text-slate-600 text-lg">〔例〕<span class="bg-white border border-amber-300 rounded-lg px-2 py-0.5">我圈出關鍵詞「陌生人」「操作手機」「生物特徵」，在 Google 搜尋「幫陌生人操作手機 生物特徵 查核」，找到 MyGoPen 和台灣事實查核中心兩篇文章。</span></p>
      <p class="mt-2 text-slate-600 text-lg">〔查核網址例〕<span class="bg-white border border-amber-300 rounded-lg px-2 py-0.5 text-indigo-700 underline">MyGoPen：幫陌生人操作手機會被盜取生物特徵去貸款？誇大AI技術！不符金融審核機制</span></p>
      <a href="%(DOC)s" target="_blank" rel="noopener" class="inline-block mt-3 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl px-5 py-2">📄 看成品範例怎麼寫 ↗</a>
    </div>
    <div class="stepnav"></div>
  </section>

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
''' % {'DOC': DOC, 'CHIPS': chips7('bg-indigo-100 border-2 border-indigo-200', 'bg-slate-100 border-2 border-slate-200'),
       'V2': vid('教學_貼上欄位設標題.mp4', '教學_貼上欄位設標題_封面.jpg', '操作影片：貼上欄位、設定標題 1 與標題 2（約 40 秒）'),
       'CARDS': CARDS,
       'V1': vid('教學_找到查核文章.mp4', '教學_找到查核文章_封面.jpg', '操作影片：從訊息找到查核文章（約 1 分鐘）'),
       'V5': vid('教學_以圖搜圖兩種方法.mp4', '教學_以圖搜圖兩種方法_封面.jpg', '操作影片：以圖搜圖兩種方法（約 1 分 15 秒）'),
       'V6': vid('截圖google圖片搜尋_字卡.mp4', '截圖google圖片搜尋_字卡_封面.jpg', '操作影片：截圖再以圖搜圖（L04，約 22 秒）'),
       'LINKS': LINKS, 'REWARD': REWARD}

L05_CFG = {
    'ws': 'g5-L05', 'lessonPath': 'g5/L05', 'title': 'Docs 查證文件（一）：找到查核文章', 'stateKey': 'g5L05flow',
    'steps': ['看成品', '標題設定', '示範', '選訊息', '我來查', '寫文件', '繳交'],
    'reveals': [], 'revealOf': {}, 'autoFb': ['c1'],
    'qtypes': {'sel': 'experience', 'c1': 'experience', 'kwd': 'experience', 'kw': 'experience', 'how': 'experience',
               'label': 'score', 'url': 'score', 'url2': 'experience', 'chk': 'experience'},
    'bonus': ['url2'],
    'choices': {
        'sel': {'opts': ['C', 'D', 'E', 'G', 'H', 'K'], 'card': True},
        'c1': {'opts': ['會', '不會'], 'correct': '不會'},
        'kwd': {'opts': ['人工智能', '陌生人', '操作手機', '指紋', '30 分鐘', '生物特徵', '傾家蕩產', '轉傳給家人'], 'multi': True},
        'how': {'opts': ['關鍵詞搜尋', '以圖搜圖：智慧鏡頭', '以圖搜圖：相機圖示', '直接上查核網站'], 'multi': True},
        'label': {'opts': ['錯誤', '誤導', '易誤解', '事實釐清', '詐騙', '部分錯誤', '正確']},
        'chk': {'opts': ['標題用「標題 1」、欄位名稱用「標題 2」', '前 4 欄都寫好了', '「查核網址」的標題是連結，而且點得開', '連結是查核機構自己的網站，不是轉載'], 'multi': True, 'block': True},
    },
    'texts': ['kw', 'url', 'url2'],
    'patterns': {'url': 'tfc-taiwan\\.org\\.tw|mygopen\\.com'},
    'openQtexts': {},
}

L05_HOOKS = r'''
  // ===== 複製七個欄位（先用剪貼簿 API，被拒絕就退回選取＋execCommand）=====
  var TPL=['我的查證文件','（年班座號＋名字）','我選的訊息','我怎麼找到查核文章的','查核結果','查核網址','為什麼這則訊息會被廣傳？','正確資訊','如果相信的話，會有什麼後果？'].join('\n');
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
  $('tplText').textContent=TPL;
  $('tplCopy').onclick=function(){copyText(TPL,this);};
  // ===== L05 專屬：6 則訊息、選題卡、提示 =====
  var CARDS={
    C:{name:'C ‧ 繪畫比賽投票（LINE 訊息）',label:'詐騙',url:'https://www.mygopen.com/2026/08/vote-scam.html',hint:'想想：這則訊息要你「做什麼」？連結要你「輸入什麼」？再加上「查核」。'},
    D:{name:'D ‧ 微波爐加熱食物有輻射（訊息）',label:'錯誤',url:'https://tfc-taiwan.org.tw/?p=109294',hint:'想想：哪一種家電？哪個國家要禁用？再加上「查核」。也可以點原始文章，看它是什麼樣的網站。'},
    E:{name:'E ‧ 打雷時用手機、藍芽耳機（訊息）',label:'事實釐清',url:'https://tfc-taiwan.org.tw/fact-check-reports/migration-7854',hint:'想想：什麼東西、遇到什麼天氣、會怎樣？再加上「查核」。'},
    G:{name:'G ‧ 印度街頭小吃影片（貼文）',label:'錯誤',url:'https://www.mygopen.com/2026/09/india-ai.html',hint:'想想：哪個國家？在做什麼食物？影片裡的人做了什麼事？再加上「查核」。'},
    H:{name:'H ‧ 手機充電時喝水（影片）',label:'錯誤',url:'https://www.mygopen.com/2022/01/Charging-Phone.html',hint:'想想：充電時做了什麼事？這支影片也可以用「以圖搜圖」找。'},
    K:{name:'K ‧ 地震時躲哪裡（訊息）',label:'錯誤',url:'https://tfc-taiwan.org.tw/fact-check-reports/migration-4806',hint:'想想：地震時要「去哪裡」躲？也試試找消防局、氣象署的官方說明。'}
  };
  H.corr=function(q){
    if(q==='label')return state.sel&&CARDS[state.sel]?CARDS[state.sel].label:'（還沒選訊息）';
  };
  H.stepDone=function(n){
    if(n===2)return answered('c1');
    if(n===3)return (state.kwd||[]).length>0;
    if(n===4)return !!state.sel;
    if(n===5)return filled(state.label)&&filled(state.url);
    return null;
  };
  H.report=function(){
    return ['選的訊息：'+(state.sel&&CARDS[state.sel]?CARDS[state.sel].name:'還沒選'),
      '查核結果：'+(filled(state.label)?'已選':'還沒選')+'；查核文章網址：'+(filled(state.url)?'已貼':'還沒貼'),
      '怎麼找到的：'+(((state.how||[]).length)?'已勾':'還沒勾')];
  };
  H.showAnswers=function(){
    if(!state.sel)state.sel='C';
    var c=CARDS[state.sel];
    state.c1='不會';state.kwd=['陌生人','操作手機','生物特徵'];state.kw='陌生人 操作手機 生物特徵 查核';
    state.how=['關鍵詞搜尋'];state.label=c.label;state.url=c.url;
  };
  H.clear=function(){
    state.sel=null;state.c1=null;state.kwd=[];state.how=[];state.label=null;state.chk=[];
    state.kw='';state.url='';state.url2='';
  };
  var STARS={C:1,D:2,E:3,G:2,H:1,K:2};
  H.changed=function(q){
    if(q==='c1')showC1();
    if(q==='kwd'){var n=(state.kwd||[]).length,e=$('kwdFb');
      e.textContent=n===0?'':(n>=2&&n<=3?'✔ '+n+' 個，剛剛好。老師選的是「陌生人・操作手機・生物特徵」':'挑 2～3 個最重要的就好');}
  };
  function showC1(){var e=$('c1Expl');if(e)e.classList.toggle('hidden',!answered('c1'));}
  H.render=function(){
    showC1();
    document.querySelectorAll('[data-card]').forEach(function(c){
      var on=state.sel===c.dataset.card;c.classList.toggle('on',on);
      var b=c.querySelector('[data-pick]');b.textContent=on?'✔ 我選這則':'選這則';
    });
    var s=state.sel&&CARDS[state.sel];
    $('selName').textContent=s?s.name+'　難度 '+'★'.repeat(STARS[state.sel])+'☆'.repeat(3-STARS[state.sel]):'（還沒選，請回上一步）';
    $('hintBox').textContent=s?s.hint:'';
    if($('kwdFb'))H.changed('kwd');
  };
  document.querySelectorAll('[data-pick]').forEach(function(b){
    b.onclick=function(){state.sel=b.dataset.pick;save();H.render();renderStepper();};
  });
'''

L05_SPEC = {
    'summary': '用「關鍵詞＋查核」或以圖搜圖，從 6 則真實網傳訊息中選一則，找到台灣事實查核中心或 MyGoPen 已發布的查核文章，看懂結果標籤，並在 Google 文件寫好標題與前四欄（我選的訊息、我怎麼找到查核文章的、查核結果、查核網址）。',
    'questions': [
        {'qid': 'doc', 'prompt': '你的 Google 文件（老師從 Classroom 作業讀取文件內容）：標題與前四欄「我選的訊息」「我怎麼找到查核文章的」「查核結果」「查核網址」。',
         'mode': 'checklist',
         'checks': [
             {'desc': '有標題，並用自己的話說明選的是哪一則訊息、在講什麼', 'pts': 3},
             {'desc': '說出自己用了哪個關鍵詞，或用了哪一種以圖搜圖找到查核文章', 'pts': 3},
             {'desc': '寫出查核機構標的結果（例如錯誤、誤導）和是哪一家機構', 'pts': 2},
             {'desc': '「查核網址」放了查核文章的標題，並做成可以點的連結', 'pts': 2}]}],
    'scoring': {'base': 100, 'floor': 80, 'deduction': 1, 'itemPoints': {'label': 5, 'url': 5}},
}

# =====================================================================
# L06
# =====================================================================
L06_BODY = '''
  <!-- ===== 步驟 1：回顧 ===== -->
  <section class="step" data-step="1">
    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-6 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-sky-700 m-0">📂 先打開上一節的文件</h2>
      <p class="text-slate-600 mt-2 text-lg">上一節你找到了一則訊息的查核文章，也寫好了前 4 欄（含查核網址）。今天要完成<b>後 3 欄</b>，把它變成一份完整的查證文件。</p>
      <ol class="list-decimal pl-6 mt-3 space-y-1 text-lg text-slate-700"><li>回 <b>Classroom 作業</b>，打開<b>同一份文件</b>（從作業裡開）。</li><li>確認有：標題、我選的訊息、我怎麼找到查核文章的、查核結果、查核網址（標題是連結）。</li><li>還沒寫完的，先補完。</li></ol>
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-5 text-base">
        %(CHIPS)s
      </div>
      <p class="mt-4 text-sm text-slate-500"><span class="inline-block w-3 h-3 rounded bg-slate-200 align-middle"></span> 上一節（L05）　<span class="inline-block w-3 h-3 rounded bg-indigo-200 align-middle ml-2"></span> 今天（L06）</p>
      <a href="%(DOC)s" target="_blank" rel="noopener" class="inline-block mt-3 bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl px-5 py-2">📄 成品範例：看 7 欄寫好的樣子 ↗</a>
    </div>
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 shadow-sm">
      <h2 class="cute text-2xl font-extrabold text-rose-700">🤔 想一想</h2>
      <p class="text-slate-700 mt-2 text-lg">你找到的那一篇查核文章，如果<b>整篇貼進文件</b>，算不算你查證完成？為什麼？</p>
    </div>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 2：抄與整理 ===== -->
  <section class="step hidden" data-step="2">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700">📝 「整理」不是「複製」</h2>
      <p class="text-slate-700 mt-2 text-lg">把<b>整理</b>想成「向朋友轉述」：朋友沒看過那篇文章，你用一兩句話告訴他「這則訊息是真的嗎？為什麼？」。把整本書遞給他，他還是不知道重點。</p>
    </div>
    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap">
        <h3 class="cute text-2xl font-extrabold text-violet-700 m-0">✋ 先猜猜看</h3>
        <button data-reveal-btn="r1" class="hidden shrink-0 bg-rose-500 hover:bg-rose-600 text-white text-sm font-bold rounded-lg px-3 py-1.5">🎉 公布</button>
      </div>
      <p class="text-slate-600 mt-2 text-lg">兩種寫法說的是同一件事：警方說，台灣沒有這種案件。哪一種是「<b>整理成自己的話</b>」？</p>
      <div class="grid md:grid-cols-2 gap-4 mt-3 text-lg">
        <div class="bg-slate-50 border-2 border-slate-200 rounded-2xl p-4"><p class="font-bold text-slate-700">A</p><p class="mt-1">經查，查核中心洽詢刑事警察局後，警方表示目前國內並無查獲與網傳手法相同之案件，且 165 反詐騙專線亦表示，台灣無此類案例。</p></div>
        <div class="bg-slate-50 border-2 border-slate-200 rounded-2xl p-4"><p class="font-bold text-slate-700">B</p><p class="mt-1">警方和 165 反詐騙專線說，台灣目前查不到這種手法的案件。</p></div>
      </div>
      <div class="flex items-center gap-2 flex-wrap mt-3"><p class="font-bold text-violet-800">我覺得是</p><span class="qtypeSlot" data-qid="s1"></span><span id="s1Fb" class="text-sm font-bold"></span></div>
      <div id="s1Opts" class="flex flex-wrap gap-2 mt-1"></div>
      <p data-wait="r1" class="text-center text-slate-400 mt-4">🔒 答案等老師公布</p>
      <div data-r="r1" class="hidden mt-4 flip bg-rose-50 border-2 border-rose-200 rounded-2xl p-4 text-lg text-slate-700 space-y-2">
        <p>🎉 <b>B 是整理。</b>A 像是把文章整段貼來，句子長又難懂；B 一句話就把重點說完，而且是你自己說得出口的話。</p>
        <p>💡 發現了嗎？整理＝<b>只留重點、用自己的話、標出是誰說的</b>。</p>
      </div>
    </div>
    <div class="bg-white border-4 border-teal-300 rounded-3xl p-6 mb-5">
      <h3 class="cute text-2xl font-extrabold text-teal-700">⚠️ 引用的三條界線</h3>
      <ul class="list-disc pl-5 mt-2 space-y-1 text-lg text-slate-700">
        <li>可以<b>引用一小句</b>，一定要加<b>引號</b>，並寫出<b>出處</b>（哪個機構）。</li>
        <li>只放<b>最重要的一句</b>，不能整段貼。</li>
        <li>其他都用<b>自己的話</b>，每一點後面標出是誰說的。</li>
      </ul>
    </div>
    <div class="bg-white border-4 border-amber-200 rounded-3xl p-6">
      <h3 class="cute text-2xl font-extrabold text-amber-700">👩‍🏫 示範：寫「正確資訊」</h3>
      <p class="text-slate-600 mt-1">成品範例的「正確資訊」，每點一句、用自己的話：</p>
      <ol class="list-decimal pl-6 mt-3 space-y-2 text-lg text-slate-700">
        <li>只有指紋、臉或聲音，不能直接拿去貸款。銀行貸款還要看身分證、手機簡訊驗證碼等好幾道檢查。</li>
        <li>警方和 165 反詐騙專線說，台灣目前查不到這種手法的案件。</li>
        <li>不過，有人被騙去做「臉部認證」，結果存款被轉走。所以遇到陌生人要你做驗證，還是要小心。</li>
      </ol>
      <p class="mt-3 text-slate-600 text-lg">✍️ 句型：<b>「根據○○，……」「○○說，……」「不過，……」</b>。順序：先講<b>最重要的結論</b> → 再講<b>證據</b> → 最後講<b>還是要小心什麼</b>。</p>
    </div>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 3：廣傳後果 ===== -->
  <section class="step hidden" data-step="3">
    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-rose-700">📣 為什麼會被廣傳？相信的話會怎樣？</h2>
      <p class="text-slate-700 mt-2 text-lg">假訊息不只是「是假的」。要說得出：<b>大家為什麼會轉傳它</b>，和<b>相信它的後果</b>。</p>
      <div class="grid md:grid-cols-2 gap-4 mt-4">
        <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-4"><p class="cute text-xl font-extrabold text-rose-700">為什麼會轉傳（5 類）</p>
          <ul class="mt-2 space-y-1 text-lg text-slate-700"><li>😨 <b>怕</b>：講得很可怕</li><li>🤩 <b>好奇／驚奇</b>：聽起來很厲害</li><li>👨‍👩‍👧 <b>關心家人</b>：「轉傳等於救人」</li><li>🎁 <b>好康</b>：免費、搶先</li><li>🤝 <b>親友傳來的</b>：因為信任</li></ul></div>
        <div class="bg-amber-50 border-2 border-amber-200 rounded-2xl p-4"><p class="cute text-xl font-extrabold text-amber-700">相信的後果（4 類）</p>
          <ul class="mt-2 space-y-1 text-lg text-slate-700"><li>🩺 <b>身體</b>：吃錯、做錯</li><li>💰 <b>錢</b>：被騙</li><li>🤝 <b>人際</b>：誤會、吵架</li><li>😱 <b>恐慌</b>：嚇到更多人、再轉傳</li></ul></div>
      </div>
    </div>

    <div class="bg-white border-4 border-violet-300 rounded-3xl p-6 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap">
        <h3 class="cute text-2xl font-extrabold text-violet-700 m-0">✋ 先猜猜看：示範訊息為什麼會被轉傳？</h3>
        <button data-reveal-btn="r2" class="hidden shrink-0 bg-rose-500 hover:bg-rose-600 text-white text-sm font-bold rounded-lg px-3 py-1.5">🎉 公布</button>
      </div>
      <p class="text-slate-600 mt-2 text-lg">「<b>幫陌生人操作手機，會被盜走指紋、聲音和臉，30 分鐘傾家蕩產。轉傳給家人朋友！</b>」大家轉傳它的原因有哪些？（可複選）</p>
      <div class="flex items-center gap-2 flex-wrap mt-3"><span class="qtypeSlot" data-qid="s2"></span><span id="s2Fb" class="text-sm font-bold"></span></div>
      <div id="s2Opts" class="flex flex-wrap gap-2 mt-1"></div>

      <p class="font-bold text-violet-800 text-lg mt-6">下面哪一句「相信的後果」寫得最好？</p>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="s3"></span><span id="s3Fb" class="text-sm font-bold"></span></div>
      <div id="s3Opts" class="space-y-2 mt-1"></div>
      <p data-wait="r2" class="text-center text-slate-400 mt-4">🔒 答案等老師公布</p>
      <div data-r="r2" class="hidden mt-4 flip bg-rose-50 border-2 border-rose-200 rounded-2xl p-4 text-lg text-slate-700 space-y-2">
        <p>🎉 <b>原因</b>：它說「30 分鐘傾家蕩產」，讓人<b>怕</b>；又寫「轉傳給家人朋友」，大家覺得轉出去是在<b>關心家人</b>；還提到 AI 和手機，聽起來很厲害，帶點<b>好奇</b>。</p>
        <p>🎉 <b>後果寫得最好的是 C</b>：它說出<b>誰</b>會<b>怎樣</b>（不敢幫人、嚇到更多人）。「會被騙」沒說誰、也沒說怎麼被騙；「這則是假的」是結果，不是後果。</p>
      </div>
    </div>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 4：貼圖 ===== -->
  <section class="step hidden" data-step="4">
    <div class="bg-white border-4 border-amber-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-amber-700">🖼️ 貼網傳訊息的圖，寫圖說</h2>
      <p class="text-slate-700 mt-2 text-lg">查證文件要有<b>網傳訊息的圖</b>，貼在<b>「我選的訊息」</b>下面，圖下面要有<b>說明</b>。看老師示範，不會的回來看影片。</p>
    </div>
    <div class="bg-white border-4 border-amber-200 rounded-3xl p-5">
      <h3 class="cute text-xl font-extrabold text-amber-700">貼網傳訊息的截圖</h3>
      <div class="grid md:grid-cols-2 gap-5 items-center mt-2">
        <ul class="list-disc pl-5 text-lg text-slate-700 space-y-1"><li><kbd>Win</kbd>＋<kbd>Shift</kbd>＋<kbd>S</kbd> 框住訊息</li><li>回文件，點「我選的訊息」下面一行，<kbd>Ctrl</kbd>＋<kbd>V</kbd> 貼上</li><li>拖角落縮小，圖下面寫圖說（例：圖：網傳訊息（來源：臉書））</li></ul>
        <div>%(V3)s</div>
      </div>
    </div>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 5：寫文件 ===== -->
  <section class="step hidden" data-step="5">
    <div class="bg-white border-4 border-teal-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-teal-700">✍️ 完成後 3 欄，變成完整的查證文件</h2>
      <div class="bg-rose-50 border-2 border-rose-300 rounded-2xl p-4 mt-3 text-lg text-rose-800">
        <b>⚠️ 用 Classroom 作業裡的同一份文件。</b>不要另外開新的，老師才讀得到。
      </div>
      <p class="mt-4 text-lg text-slate-700"><b>這節的完成標準（全班一樣）</b>：文件 <b>7 欄</b>都有，<b>圖下面有圖說</b>。</p>
    </div>
    <div class="grid md:grid-cols-3 gap-4 mb-5">
      <div class="bg-white border-4 border-teal-200 rounded-3xl p-5">
        <p class="cute text-xl font-extrabold text-teal-700">① 為什麼這則訊息會被廣傳？</p>
        <p class="text-lg text-slate-700 mt-1">從 5 類挑，寫 <b>1～2 句，要有理由</b>。</p>
      </div>
      <div class="bg-white border-4 border-teal-200 rounded-3xl p-5">
        <p class="cute text-xl font-extrabold text-teal-700">② 正確資訊</p>
        <p class="text-lg text-slate-700 mt-1">1～3 點，每點<b>一句、自己的話、標機構</b>。可以引用一小句（加引號）。</p>
      </div>
      <div class="bg-white border-4 border-teal-200 rounded-3xl p-5">
        <p class="cute text-xl font-extrabold text-teal-700">③ 如果相信的話，會有什麼後果？</p>
        <p class="text-lg text-slate-700 mt-1">從 4 類挑，寫<b>誰會怎樣</b>，1～2 句。</p>
      </div>
    </div>
    <div class="bg-white border-4 border-amber-200 rounded-3xl p-5">
      <p class="font-bold text-amber-700 text-lg">時間不夠？照這個順序做：</p>
      <p class="text-lg text-slate-700 mt-1"><b>正確資訊 → 為什麼這則訊息會被廣傳 → 如果相信的話會有什麼後果 → 圖</b></p>
      <a href="%(DOC)s" target="_blank" rel="noopener" class="inline-block mt-3 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl px-5 py-2">📄 看成品範例怎麼寫 ↗</a>
    </div>
    <div class="stepnav"></div>
  </section>

  <!-- ===== 步驟 6：繳交 ===== -->
  <section class="step hidden" data-step="6">
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-indigo-700">✅ 繳交前自己檢查</h2>
      <div class="flex items-center gap-2 flex-wrap mt-1"><span class="qtypeSlot" data-qid="chk"></span></div>
      <div id="chkOpts" class="space-y-2 mt-3"></div>
      <div class="bg-indigo-50 border-2 border-indigo-200 rounded-2xl p-4 mt-4 text-lg text-slate-700">
        <p class="font-bold text-indigo-800">繳交兩個地方：</p>
        <ol class="list-decimal pl-6 mt-1 space-y-1"><li>回 <b>Classroom 作業</b>，確認文件<b>附在作業裡</b>，按<b>「繳交」</b>。</li><li>回到這裡，按下面的<b>「繳交學習單」</b>。</li></ol>
        <p class="text-sm text-slate-500 mt-2">還沒寫完也可以先交，下一節開頭還有時間補。</p>
      </div>
    </div>%(REWARD)s
    <div class="stepnav"></div>
  </section>
''' % {'DOC': DOC, 'REWARD': REWARD,
       'CHIPS': chips7('bg-slate-100 border-2 border-slate-200', 'bg-indigo-100 border-2 border-indigo-200'),
       'V3': vid('教學_貼網傳截圖.mp4', '教學_貼網傳截圖_封面.jpg', '操作影片：貼網傳截圖（約 40 秒）')}

L06_CFG = {
    'ws': 'g5-L06', 'lessonPath': 'g5/L06', 'title': 'Docs 查證文件（二）：整理成報告', 'stateKey': 'g5L06flow',
    'steps': ['回顧', '抄與整理', '廣傳後果', '貼圖', '寫文件', '繳交'],
    'reveals': ['r1', 'r2'], 'revealOf': {'s1': 'r1', 's2': 'r2', 's3': 'r2'},
    'qtypes': {'s1': 'experience', 's2': 'experience', 's3': 'experience', 'chk': 'experience'},
    'choices': {
        's1': {'opts': ['A', 'B'], 'correct': 'B'},
        's2': {'opts': ['怕', '好奇／驚奇', '關心家人', '好康', '親友傳來的'], 'multi': True, 'correct': ['怕', '好奇／驚奇', '關心家人']},
        's3': {'opts': ['A．會被騙。', 'B．這則訊息是假的。', 'C．我們可能不敢幫真的需要幫忙的人，也會把嚇人的訊息再傳給更多人，讓大家一起害怕。'], 'block': True,
               'correct': 'C．我們可能不敢幫真的需要幫忙的人，也會把嚇人的訊息再傳給更多人，讓大家一起害怕。'},
        'chk': {'opts': ['「正確資訊」有標出處，沒有整段複製', '「為什麼這則訊息會被廣傳」和「後果」都寫了理由', '圖下面有說明', '「查核網址」的連結點得開'], 'multi': True, 'block': True},
    },
    'texts': [], 'patterns': {}, 'openQtexts': {},
}

L06_HOOKS = r'''
  H.stepDone=function(n){
    if(n===2)return answered('s1');
    if(n===3)return answered('s2')&&answered('s3');
    return null;
  };
  H.report=function(){
    return ['自查表：已勾 '+((state.chk||[]).length)+' 項（共 4 項）','提醒：文件要附在 Classroom 作業裡，並在那邊按「繳交」'];
  };
  H.showAnswers=function(){
    state.s1='B';state.s2=['怕','好奇／驚奇','關心家人'];state.s3=C.choices.s3.correct;
  };
  H.clear=function(){state.s1=null;state.s2=[];state.s3=null;state.chk=[];};
'''

L06_SPEC = {
    'summary': '把上一節找到的查核文章整理成完整的查證文件：用自己的話寫正確資訊並標出處、說明訊息為什麼被廣傳與相信的後果、貼網傳截圖加圖說。',
    'questions': [
        {'qid': 'doc2', 'prompt': '你的 Google 文件（老師從 Classroom 作業讀取文件內容）：「正確資訊」「為什麼這則訊息會被廣傳」「如果相信的話會有什麼後果」「圖與圖說」。',
         'mode': 'checklist',
         'checks': [
             {'desc': '「正確資訊」用自己的話寫 1～3 點，沒有整段複製查核文章', 'pts': 6},
             {'desc': '「正確資訊」有標出是哪個機構（警方、165、查核機構、專家等）說的，引用的話有加引號', 'pts': 2},
             {'desc': '「為什麼這則訊息會被廣傳」說出至少一個原因（怕、好奇、關心家人、好康、親友傳來）並說明理由', 'pts': 4},
             {'desc': '「相信的後果」說出誰會怎樣，不只是寫「是假的」或「會被騙」', 'pts': 4},
             {'desc': '有貼圖並在圖下面寫了圖說', 'pts': 4}]}],
    'scoring': {'base': 100, 'floor': 80, 'deduction': 1, 'itemPoints': {}},
}

def write(name, folder, html):
    p = os.path.join(ROOT, folder, name)
    io.open(p, 'w', encoding='utf8', newline='\n').write(html)
    print('wrote', p, len(html) // 1024, 'KB')

write('五上_L05_Docs查證文件一.html', 'L05_Docs查證文件一',
      page('訊息查證小偵探｜五上 L05 教學活動', '🔎 訊息查證小偵探',
           '五年級上學期 · L05 Docs 查證文件（一）· 教學活動流程（40 分鐘）', L05_BODY, L05_CFG, L05_HOOKS, L05_SPEC))
write('五上_L06_Docs查證文件二.html', 'L06_Docs查證文件二',
      page('整理成查證文件｜五上 L06 教學活動', '📝 把查核文章整理成自己的報告',
           '五年級上學期 · L06 Docs 查證文件（二）· 教學活動流程（40 分鐘）', L06_BODY, L06_CFG, L06_HOOKS, L06_SPEC))
