# -*- coding: utf-8 -*-
# 五上 L05（查證報告第一節）與 L06 共用的頁面零件。
# L05 流程（每一步都是固定的一頁：點進去內容就在那裡，不點開、不切換、不答題）：
#   1 看範例 → 2 老師示範 → 3 找訊息 → 4 找網址 → 5 開文件 → 6 貼格式 → 7 貼網址 → 8 我選的訊息 → 9 怎麼找到的 → 10 查核結果 → 11 繳交
# 文件欄位順序：標題、年班座號＋名字、查核網址、我選的訊息、我怎麼找到查核文章的、查核結果、（L06）為什麼廣傳、正確資訊、後果
# 原則：範例一律用老師的示範（幫陌生人操作手機），避免學生直接抄；字少；動圖放在操作旁邊；不使用 emoji；
#       這兩節不放互動答題（答案等老師口頭公布），句型與範例直接用文字攤開。
DOC_URL = 'https://docs.google.com/document/d/1e4-lD9lyZJgRPma8_7A3e3fn0y1M8M9Z1oqZF1gI0n4/edit'
DEMO_URL = 'https://www.mygopen.com/2026/02/ai-fraud.html'
LINK = '<span class="text-indigo-700 underline break-all">' + DEMO_URL + '</span>'


def kbd(*ks):
    return '＋'.join('<kbd>%s</kbd>' % k for k in ks)


def slide(title, clip=None, extra=''):
    media = ''
    if clip:
        media = ('<div class="sc-media" data-src="assets/%s.mp4" data-poster="assets/%s_封面.jpg"></div>' % (clip, clip))
    return '<div class="sc-slide"><p class="sc-t">%s</p>%s%s</div>' % (title, media, extra)


def sc(slides, numbered=True):
    """一組小步驟：全部攤開在同一頁（flat），不在頁面裡切換。"""
    return '<div class="sc sc-flat%s" data-sc>%s</div>' % ('' if numbered else ' sc-nonum', ''.join(slides))


def plain_box(title, body, tone='sky'):
    """句型、範例這類輔助資訊：直接攤開的文字方塊，不用點開。"""
    return ('<div class="mt-3 bg-%s-50 border-2 border-%s-200 rounded-2xl p-3"><p class="font-extrabold text-%s-800 text-base m-0">%s</p>'
            '<div class="mt-1 text-lg text-slate-700">%s</div></div>') % (tone, tone, tone, title, body)


def ex(text):
    return plain_box('範例（老師的示範）', '<span class="text-slate-800">%s</span>' % text, 'amber')


def step(n, title, color, lead, body):
    return ('\n  <!-- ===== 步驟 %d：%s ===== -->\n  <section class="step hidden" data-step="%d">\n'
            '    <div class="bg-white border-4 border-%s-300 rounded-3xl p-5 mb-5 shadow-sm">\n'
            '      <h2 class="cute text-3xl font-extrabold text-%s-700 m-0">%s</h2>\n%s    </div>\n    %s\n    <div class="stepnav"></div>\n  </section>\n') % (
        n, title, n, color, color, title, ('      <p class="text-lg text-slate-600 mt-1">%s</p>\n' % lead) if lead else '', body)


# ---------- 第 1 步下半：看範例（四欄範例，老師的示範）----------
DEMO_SC = sc([
    slide('查核網址', None,
          '<p class="text-lg text-slate-500">先貼查核報告的標題，下面一行是整條網址（藍色有底線的連結）：</p><div class="text-xl bg-amber-50 border-2 border-amber-200 rounded-2xl p-3 mt-1"><p class="m-0">【誤導】幫陌生人操作手機會被盜取生物特徵去貸款？誇大AI技術！不符金融審核機制</p><p class="m-0 mt-1">' + LINK + '</p></div>'
          '<p class="text-lg mt-2">要是<b>查核機構自己</b>的網站（台灣事實查核中心、MyGoPen），不是轉載。</p>'),
    slide('我選的訊息', None,
          '<div class="grid md:grid-cols-2 gap-4 items-start"><div><img class="shotimg" src="assets/M2_B示範_陌生人手機_網傳訊息.png" alt="示範訊息：兩則臉書貼文，標題寫「人工智能生物信息詐騙，要的不是你的錢而是你這個人」，帳號已遮蔽" loading="lazy"><p class="text-[11px] text-slate-400 mt-1">原始訊息的圖・點圖可放大</p></div>'
          '<p class="text-xl bg-amber-50 border-2 border-amber-200 rounded-2xl p-3">網傳訊息說：只要幫路上的陌生人操作手機、摸螢幕、對著鏡頭說話，指紋、聲音和臉就會被偷走，騙子拿去貸款，30 分鐘就傾家蕩產。這則訊息在臉書流傳。</p></div>'),
    slide('我怎麼找到查核文章的', None,
          '<p class="text-xl bg-amber-50 border-2 border-amber-200 rounded-2xl p-3">我圈出「陌生人」「操作手機」「生物特徵」，搜「陌生人 操作手機 生物特徵 查核」，點進 MyGoPen 的文章，它是專門查謠言的機構，不是轉載。</p>'),
    slide('查核結果', None,
          '<p class="text-xl bg-amber-50 border-2 border-amber-200 rounded-2xl p-3">MyGoPen 查核後標為「誤導」，重點是這個說法在技術和金融上都不合理。</p>'
          '<p class="text-lg text-slate-700 mt-2">台灣事實查核中心標為「錯誤」。兩家結論一致，更可信。</p>'),
], numbered=False)

# ---------- 第 2 步：老師示範 ----------
DEMO_FIND = sc([
    slide('圈出 2～3 個<b>關鍵詞</b>', None, '<p class="text-lg mt-2">不要整句貼去搜。例：<span class="bg-amber-50 border border-amber-300 rounded-lg px-2 font-bold">陌生人</span> <span class="bg-amber-50 border border-amber-300 rounded-lg px-2 font-bold">操作手機</span> <span class="bg-amber-50 border border-amber-300 rounded-lg px-2 font-bold">生物特徵</span></p>'),
    slide('Google 打「關鍵詞＋<b>查核</b>」', None, '<p class="text-lg mt-2 bg-amber-50 border-2 border-amber-200 rounded-xl px-3 py-2">陌生人 操作手機 生物特徵 查核</p>'),
    slide('認出<b>查核機構</b>', None, '<p class="text-lg mt-2">看<b>機構名稱</b>：<b>台灣事實查核中心</b>、<b>MyGoPen 麥擱騙</b>，才是專門查謠言的。新聞、貼文是轉載，要點到原始的查核機構。</p>'),
    slide('只讀<b>兩個地方</b>', None, '<p class="text-lg mt-2">標題前的<b>標籤</b>（錯誤、誤導…），和最上面的「<b>你可以先知道</b>」。</p>'),
    slide('結果', None, '<p class="text-lg mt-2">MyGoPen「誤導」、台灣事實查核中心「錯誤」，結論一致。</p>'
                         '<p class="text-lg mt-1 text-rose-700 font-bold">搜尋結果最上面的 AI 摘要先跳過，要讀的是查核機構寫的原始文章。</p>'),
], numbered=True)

# ---------- 第 5 步：開文件 ----------
SC_OPEN = sc([
    slide('從 Classroom 打開<b>老師給的文件</b>，改檔名', '步_文件1_打開文件',
          '<p class="text-xl font-bold mt-2">檔名：<b class="text-blue-700">年班座號＋名字</b>　<span class="text-base text-slate-500">例：51230 王小明</span></p>'
          '<p class="text-lg text-rose-700 font-bold mt-1">一定要從 Classroom 作業裡開，老師才讀得到。</p>'),
])

# ---------- 第 6 步：貼格式 ----------
SC_FORMAT = sc([
    slide('按<b>複製欄位</b>', None,
          '<button id="tplCopy" type="button" class="w-full bg-blue-600 hover:bg-blue-700 text-white text-2xl font-extrabold rounded-2xl px-4 py-4">複製欄位</button>'
          '<p class="text-lg font-bold mt-3">會貼上這些格式：</p>'
          '<pre id="tplText" class="text-lg leading-relaxed whitespace-pre-wrap font-[inherit] bg-white rounded-xl p-3 border-2 border-blue-100 mt-1"></pre>'),
    slide('文件第一行，按 <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd> 貼上', '步_文件2_貼上七欄位',
          '<p class="text-lg mt-3">第 2 行「（年班座號＋名字）」換成<b class="text-indigo-700">你的</b>。第 1 行的標題，下面兩步換。</p>'
          '<p class="text-base text-slate-500 mt-2">貼錯了？<kbd>Ctrl</kbd> + <kbd>Z</kbd>。多了空白？<kbd>Backspace</kbd> 刪前面、<kbd>Delete</kbd> 刪後面。</p>'),
    slide('到查核文章，選取<b>查核報告的標題</b>，複製', '步_標題A_複製標題',
          '<p class="text-lg mt-2 text-slate-600">是<b>查核報告</b>的標題，不是網傳訊息的標題。</p>'),
    slide('回文件，選取第 1 行「（文件標題）」，貼上', '步_標題B_貼上標題',
          '<p class="text-2xl font-bold mt-2">' + kbd('Ctrl', 'V') + '</p>'),
    slide('題目選起來，設成<b>標題 1</b>', '步_文件3_設標題1',
          '<p class="text-lg text-slate-500 mt-2">左上角「內文」按鈕 → 標題 1。快速鍵 <kbd>Ctrl</kbd>＋<kbd>Alt</kbd>＋<kbd>1</kbd>。</p>'),
    slide('<b>欄位名稱</b>，都設成<b>標題 2</b>', '步_文件4_設標題2',
          '<p class="text-lg text-slate-500 mt-2">要用左上角「內文」按鈕選「標題 2」，不是只把字放大，這樣左邊的「大綱」才找得到。快速鍵 <kbd>Ctrl</kbd>＋<kbd>Alt</kbd>＋<kbd>2</kbd>。</p>'),
])

# ---------- 第 7 步：貼網址 ----------
SC_URL = sc([
    slide('回到查核文章，點<b>網址列</b>，複製<b>網址</b>', '步_網址1_複製網址列',
          '<p class="text-xl mt-3 bg-rose-50 border-2 border-rose-200 rounded-2xl p-3">要是<b>查核機構自己</b>的網站（台灣事實查核中心、MyGoPen），不是轉載。</p>'),
    slide('回文件，貼在「查核網址」<b>下面</b>', '步_網址2_貼上網址',
          '<p class="text-2xl font-bold mt-2">' + kbd('Ctrl', 'V') + '</p>'),
    slide('圈選網址，點<b>鎖鏈符號</b>，按「套用」', '步_網址3_加超連結',
          '<p class="text-lg text-slate-500 mt-2">網址變藍色、有底線，點得開，就成功了。</p>'),
])

# ---------- 第 8 步：我選的訊息 ----------
CHIPS5 = ('<div class="grid grid-cols-3 sm:grid-cols-6 gap-2 mt-3 text-center text-base">'
          + ''.join('<div class="bg-amber-50 border border-amber-200 rounded-xl p-2"><b>%s</b></div>' % t for t in ['人：誰', '事：做什麼', '時：何時', '地：哪裡', '物：什麼東西', '傳播：在哪傳'])
          + '</div><p class="text-base text-slate-500 mt-2">沒寫的，就寫「沒說」。</p>')
SC_MSG = sc([
    slide('用自己的話寫一兩句：這則訊息<b>在講什麼</b>', None,
          CHIPS5 + ex('網傳訊息說：只要幫路上的陌生人操作手機、摸螢幕、對著鏡頭說話，指紋、聲音和臉就會被偷走，騙子拿去貸款，30 分鐘就傾家蕩產。這則訊息在臉書流傳。')
          + plain_box('句型', '網傳訊息說：<b>＿＿</b>（人）在<b>＿＿</b>（地），<b>＿＿</b>（事）……這則訊息在<b>＿＿</b>流傳。')),
    slide('到查核文章，找到<b>原始訊息的圖</b>，右鍵<b>複製圖片</b>', '步_圖A_找圖複製',
          '<p class="text-base text-slate-500 mt-2">選的是影片？按 <kbd>Win</kbd>＋<kbd>Shift</kbd>＋<kbd>S</kbd> 截一張畫面。</p>'),
    slide('回文件，<b>貼在句子下面</b>', '步_圖3_貼上', '<p class="text-2xl font-bold mt-2">' + kbd('Ctrl', 'V') + '</p>'),
])

# ---------- 第 9 步：我怎麼找到查核文章的 ----------
STRIP9 = ('<div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center mt-2">'
          + ''.join('<div class="bg-teal-50 border-2 border-teal-200 rounded-2xl p-3"><div class="text-3xl font-extrabold text-teal-600">%d</div><b>%s</b></div>' % (i, t)
                    for i, t in enumerate(['圈了哪些<br>關鍵詞？', 'Google<br>搜了什麼？', '點進<br>哪個網站？', '為什麼是<br>查核機構？'], 1)) + '</div>')
SC_HOW = sc([
    slide('照順序寫這 4 件事', None,
          STRIP9 + ex('我圈出「陌生人」「操作手機」「生物特徵」，搜「陌生人 操作手機 生物特徵 查核」，點進 MyGoPen 的文章，它是專門查謠言的機構，不是轉載。')
          + plain_box('句型', '我圈出「<b>＿＿</b>」當關鍵詞，在 Google 搜「<b>＿＿ 查核</b>」，點進 <b>＿＿</b> 的文章。它是專門查謠言的查核機構，不是轉載。')),
])

# ---------- 第 10 步：查核結果 ----------
LABELS = ['錯誤', '誤導', '易誤解', '事實釐清', '詐騙', '部分錯誤', '正確']
LABEL_CHIPS = ('<div class="flex flex-wrap gap-2 mt-2">' + ''.join(
    '<span class="bg-amber-100 border-2 border-amber-300 text-amber-900 font-extrabold rounded-full px-4 py-1 text-xl">%s</span>' % t for t in LABELS) + '</div>')
SC_RES = sc([
    slide('看<b>標題前的標籤</b>，和「你可以先知道」', '步_結果_看標籤'),
    slide('查核機構標的結果是？', None,
          LABEL_CHIPS + '<p class="text-lg mt-2">寫：<b>哪一家</b>、<b>標了什麼</b>、<b>一句重點</b>。</p>'
          + ex('MyGoPen 查核後標為「誤導」，重點是這個說法在技術和金融上都不合理。')
          + plain_box('句型', '<b>＿＿</b>（機構）查核後標為「<b>＿＿</b>」，重點是……')
          + '<p class="text-lg mt-3 font-bold text-amber-800">加分：再找另一個機構的文章來比對，多寫一句。</p>'),
])

STEP_OPEN = step(5, '開文件', 'blue', '先把文件準備好。', SC_OPEN)
STEP_FORMAT = step(6, '貼格式', 'indigo', '貼上欄位，設標題。', SC_FORMAT)
STEP_URL = step(7, '貼網址', 'rose', '查核網址要先貼，放在標題下面。', SC_URL)
STEP_MSG = step(8, '我選的訊息', 'amber', '往下寫第一欄。', SC_MSG)
STEP_HOW = step(9, '我怎麼找到查核文章的', 'teal', '往下寫第二欄。', SC_HOW)
STEP_RES = step(10, '查核結果', 'rose', '往下寫第三欄。', SC_RES)
DEMO_MSG = ('<div class="bg-white border-4 border-amber-200 rounded-3xl p-5 mb-5"><div class="grid md:grid-cols-2 gap-4 items-start">'
            '<div><img class="shotimg" src="assets/M2_B示範_陌生人手機_網傳訊息.png" alt="示範訊息：兩則臉書貼文，標題寫「人工智能生物信息詐騙，要的不是你的錢而是你這個人」，帳號已遮蔽" loading="lazy"><p class="text-[11px] text-slate-400 mt-1">示範訊息（帳號已遮蔽）・點圖可放大</p></div>'
            '<p class="text-xl text-slate-800 m-0">網傳訊息說：只要幫路上的陌生人操作手機、摸螢幕、對著鏡頭說話，指紋、聲音和臉就會被偷走，騙子拿去貸款，30 分鐘就傾家蕩產。</p></div></div>')
STEP_DEMO = step(2, '老師示範：從訊息找到查核文章', 'amber', '看老師怎麼做。示範訊息：幫陌生人操作手機，會被盜走指紋？', DEMO_MSG + DEMO_FIND)


# ---------- L06 用：準備文件（開文件、貼格式；一頁固定）----------
def step_prep(n, lead='做過的，直接按「下一步」跳過。'):
    return step(n, '準備好你的 Google 文件', 'amber', lead, SC_OPEN + SC_FORMAT)


# ---------- 找回上次的網址（只放在 L06；直接攤開，不用點開）----------
def rescue():
    opts = ''.join('<option value="%s">%s</option>' % (k, v) for k, v in [
        ('C', 'C ‧ 繪畫比賽投票'), ('D', 'D ‧ 微波爐有輻射'), ('E', 'E ‧ 打雷戴藍芽耳機'),
        ('G', 'G ‧ 印度街頭小吃'), ('H', 'H ‧ 充電時講電話喝水'), ('K', 'K ‧ 地震躲生命三角')])
    return (
        '<div class="urlfix mt-4 bg-violet-50 border-2 border-violet-300 rounded-2xl p-4">'
        '<p class="font-extrabold text-violet-800 text-xl m-0">找回上次的查核網址</p>'
        '<div class="mt-3 text-lg text-slate-700 space-y-3">'
        '<div class="bg-white border-2 border-violet-200 rounded-xl p-3"><button type="button" data-loadwork class="bg-violet-600 hover:bg-violet-700 text-white font-extrabold rounded-xl px-4 py-2">用我的班級座號，拿回上次的網址</button>'
        '<p class="text-base text-slate-500 mt-1">先在最上面填好年級、班級、座號。</p><p data-ufmsg class="text-base font-bold mt-1 min-h-[22px]"></p></div>'
        '<div data-ufpick class="hidden"><label class="block font-bold">上次你選的是哪一則？'
        '<select class="urlfixSel mt-1 w-full border-2 border-slate-300 rounded-xl px-3 py-2 text-lg"><option value="">請選</option>' + opts + '</select></label></div>'
        '<div data-ufbox class="hidden bg-white border-2 border-violet-200 rounded-xl p-3">'
        '<p class="font-bold" data-ufname></p>'
        '<p class="break-all font-mono text-base mt-1" data-ufurl></p>'
        '<div class="flex gap-2 flex-wrap mt-2">'
        '<a data-ufopen href="#" target="_blank" rel="noopener" class="bg-violet-600 hover:bg-violet-700 text-white font-bold rounded-xl px-4 py-2">開啟查核文章 ↗</a>'
        '<button type="button" data-copyurl class="bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-4 py-2">複製網址</button></div></div>'
        '<p class="text-base text-slate-500">這是老師準備的那一篇，你上次找到別篇也可以。想自己找：瀏覽器按 <kbd>Ctrl</kbd>＋<kbd>H</kbd> 看「歷史記錄」，找 tfc-taiwan 或 mygopen 開頭的。</p>'
        '</div></div>')


RESCUE = rescue()

CSS = ''

# ---------- 找回上次的查核網址（L06）／繳交後存暫存區（L05）----------
RESCUE_JS = r"""
  // ===== 找回上次的查核網址 =====
  // 順序：自己記下的網址 → 上次繳交時存進「學生暫存區 studentWork」的（輸入年級班級座號拿回）→ 上次選的那一則訊息對應的查核文章
  var WORKWS='g5-L05',WORKKIND='factcheck';
  function workId(idn){return WORKWS+'__'+idn.grade+'-'+idn.className+'-'+idn.studentId+'__'+WORKKIND;}
  function rescueUrl(){
    if(filled(state.url))return String(state.url).trim();
    return state.sel&&CARDS[state.sel]?CARDS[state.sel].url:'';
  }
  function ufMsg(t,kind){
    document.querySelectorAll('[data-ufmsg]').forEach(function(p){p.textContent=t;p.className='text-base font-bold mt-1 min-h-[22px] '+(kind==='ok'?'text-emerald-700':kind==='warn'?'text-amber-600':'text-violet-700');});
  }
  function renderRescue(){
    var u=rescueUrl(),own=filled(state.url);
    document.querySelectorAll('.urlfix').forEach(function(box){
      box.querySelector('[data-ufpick]').classList.toggle('hidden',!!state.sel||own);
      var b=box.querySelector('[data-ufbox]');b.classList.toggle('hidden',!u);
      if(u){
        box.querySelector('[data-ufname]').textContent=own?'你記下的網址':'你上次選的是：'+CARDS[state.sel].name;
        box.querySelector('[data-ufurl]').textContent=u;
        box.querySelector('[data-ufopen]').href=u;
      }
      var sel=box.querySelector('.urlfixSel');if(sel&&state.sel)sel.value=state.sel;
    });
    document.querySelectorAll('.urlKeep').forEach(function(k){if(document.activeElement!==k)k.value=state.url||'';});
  }
  function loadWork(){
    var idn=getIdentity();
    if(!identityValid(idn)){ufMsg('先在最上面填好年級、班級、座號。','warn');return;}
    if(!db||!auth){ufMsg('現在拿不到，用下面的方法找。','warn');return;}
    ufMsg('找找看…');
    authResolved.then(function(){return ensureAuth();})
      .then(function(){return db.collection('studentWork').doc(workId(idn)).get();})
      .then(function(doc){
        if(!doc.exists){ufMsg('還沒找到你上次存的網址。用下面的方法找。','warn');return;}
        var d=(doc.data()||{}).data||{};
        if(d.sel&&CARDS[d.sel])state.sel=d.sel;
        if(d.own&&d.url)state.url=d.url;
        save();if(H.render)H.render();renderStepper();
        ufMsg('找到了！下面是你上次的查核文章網址，可以開啟、複製。','ok');
      })
      .catch(function(e){console.warn('讀取暫存失敗',e);ufMsg('現在拿不到，用下面的方法找。','warn');});
  }
  // L05 繳交成功後，把選的訊息與網址存進暫存區，之後（L06）填班級座號就能拿回
  function saveWork(idn){
    if(!db||!(state.sel||filled(state.url)))return;
    var u=rescueUrl();
    db.collection('studentWork').doc(workId(idn)).set({
      worksheetId:WORKWS,kind:WORKKIND,grade:idn.grade,className:idn.className,studentId:idn.studentId,
      data:{sel:state.sel||'',url:filled(state.url)?String(state.url).trim():'',own:filled(state.url)},
      text:String(u||'').slice(0,1900),updatedAt:firebase.firestore.FieldValue.serverTimestamp()},{merge:true})
      .catch(function(e){console.warn('暫存失敗',e);});
  }
  if(C.ws===WORKWS)H.afterSubmit=saveWork;
  var rescueBound=false;
  function bindRescue(){
    if(rescueBound)return;rescueBound=true;
    document.querySelectorAll('.urlfixSel').forEach(function(e){e.addEventListener('change',function(){if(e.value){state.sel=e.value;save();if(H.render)H.render();renderStepper();}});});
    document.querySelectorAll('.urlKeep').forEach(function(e){e.addEventListener('input',function(){state.url=e.value;save();renderRescue();});});
  }
  document.addEventListener('click',function(ev){
    var t=ev.target.closest&&ev.target.closest('[data-copyurl],[data-loadwork]');if(!t)return;
    if(t.hasAttribute('data-loadwork')){loadWork();return;}
    var u=rescueUrl();if(u)copyText(u,t);
  });
"""
