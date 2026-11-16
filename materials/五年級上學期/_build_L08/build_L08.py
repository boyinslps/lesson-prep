# -*- coding: utf-8 -*-
# 產生五上 L08「確認主題、寫台詞、做出你的影片」學習單。
# 2026-11-16 老師：L07 改回原本（找主題 7 步）；L08 = 原 L07 的後半（確認主題、寫台詞、關鍵字）＋新的 Canva 影片課
# （建立影片、選比例、文字輸入、文字特效、照字幕找素材）；要能「拿回 L07 的內容」；繳交不需要回 Google。
# 關鍵字學生自己選、AI 不幫忙；只有寫台詞 AI 可協助（用提問引導）；要有台詞撰寫範例。
# 晚：文件由老師幫學生開；台詞、關鍵字改成在學習單裡填，填完按「複製台詞表」貼進老師給的文件。
# Canva 的影片像「會動的簡報」：一頁一個畫面，沒有時間軸，學習單只說「頁面」。
#
# 步驟來源：
#   merged_steps.py   : 看範例、資料＋AI 提問、寫台詞、挑關鍵字、複製進文件（步驟 2～6）
#   canva_steps_src.py: Canva 建立影片、放文字、文字特效、找素材、素材來源頁、分享連結繳交（步驟 7～12）
# 骨架直接取自「目前的」L06 學習單；⚠ 不要用 _build_L05_L06/build.py（行號已過時，會把 L05、L06 弄壞）。
# 生成後：
#   python 引導規範/chair-gate/inject.py <本節 html>
#   python 引導規範/stepcards/inject.py <本節 html>
#   python 引導規範/game-portal/check.py <本節 html>
import io, json, os, re, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import merged_steps as M
ROOT = os.path.dirname(HERE)                       # materials/五年級上學期
SKEL = os.path.join(ROOT, 'L06_Docs查證文件二', '五上_L06_Docs查證文件二.html')
OUTDIR = os.path.join(ROOT, 'L08_寫台詞與Canva影片')
OUT = os.path.join(OUTDIR, '五上_L08_寫台詞與Canva影片.html')

# Canva 步驟（原獨立 L09）：只取 BODY 以前的 STEP1～STEP6 字串
_src = io.open(os.path.join(HERE, 'canva_steps_src.py'), encoding='utf8').read().split('\nBODY = ')[0]
NS = {'__file__': os.path.join(HERE, 'canva_steps_src.py')}
exec(compile(_src, 'canva_steps_src', 'exec'), NS)
PORTAL = NS['PORTAL']
NL = chr(10)


def must(s, a, b):
    assert s.count(a) == 1, a
    return s.replace(a, b)


C_MAKE, C_TEXT, C_FX, C_MAT, C_SRC, C_SUBMIT = (NS['STEP%d' % i] for i in range(1, 7))

# 步驟 8（放進文字）：台詞從學習單複製，不用再開文件
C_TEXT = must(C_TEXT, '<li>另開一個分頁，打開上一節的<b>台詞表文件</b>。</li>', '<li>到下面的「我的台詞」，每一句旁邊有「複製」。</li>')
C_TEXT = must(C_TEXT, '<li>回文件複製這一句，貼進文字方塊。</li>', '<li>按第 1 句的「複製」，回 Canva 貼進文字方塊（Ctrl+V）。</li>')
C_TEXT = must(C_TEXT, '<li>第 2 頁貼第 2 句，一頁一頁做。</li>', '<li>第 2 頁貼第 2 句，一頁一頁做。</li>')
_CAP_ANCH = '    <div class="bg-white border-4 border-sky-300 rounded-3xl p-5 mb-5 shadow-sm">' + NL + '      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-sky-700 m-0">我做到了</p><span class="qtypeSlot" data-qid="text"></span></div>'
CAP_CARD = '''    <div class="bg-white border-4 border-sky-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-sky-700 m-0">我的台詞</p>
      <div id="capList" class="space-y-2 mt-3"></div>
    </div>
'''
C_TEXT = must(C_TEXT, _CAP_ANCH, CAP_CARD + _CAP_ANCH)

# 步驟 10（找素材）：把學生自己的關鍵字列在最上面
C_MAT = must(C_MAT, '關鍵字寫在上一節的台詞表文件裡，沒有的話，從字幕裡挑看得到畫面的詞。搜不到，就換一個詞，或試試英文。', '關鍵字就在下面「我的關鍵字」。搜不到，就換一個詞，或試試英文。')
_KW_ANCH = '    <div class="grid md:grid-cols-2 gap-4 mb-5">'
KW_CARD = '''    <div class="bg-white border-4 border-teal-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-teal-700 m-0">我的關鍵字</p>
      <div id="kwList" class="space-y-2 mt-3 text-lg"></div>
    </div>
'''
C_MAT = must(C_MAT, _KW_ANCH, KW_CARD + _KW_ANCH)

C_SUBMIT = must(C_SUBMIT, '你的影片在 Canva 裡，不用回 Classroom。', '你的影片在 Canva 裡，不用再回 Classroom 按繳交。')

STEP_TOPIC = '''
  <!-- ===== 步驟 1：拿回主題、確認 ===== -->
  <section class="step" data-step="1">
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-emerald-700 m-0">拿回你的主題，確認一下</h2>
      <p class="text-slate-600 mt-2 text-lg">上一節你選好了題目。先填好最上面的年級、班級、座號，再按「拿回我的主題」。上一節沒存到的話，直接在下面寫。</p>
      <div class="flex gap-2 flex-wrap mt-3">
        <button type="button" id="topicLoad" class="cute bg-emerald-600 hover:bg-emerald-700 text-white text-lg font-extrabold rounded-2xl px-5 py-2">拿回我的主題</button>
      </div>
      <p id="topicStat" class="text-base font-bold mt-3 min-h-[24px]"></p>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm space-y-5">
      <div><label for="cat" class="cute text-xl font-extrabold text-emerald-700">我選的類型</label>
        <select id="cat" data-k="cat" class="fld ans mt-2 text-lg"><option value="">選一個</option><option>冷知識</option><option>謠言</option><option>事實澄清</option></select></div>
      <div><label for="hook" class="cute text-xl font-extrabold text-emerald-700">我的開頭句</label>
        <textarea id="hook" data-k="hook" rows="2" class="fld ans mt-2 text-lg"></textarea></div>
      <div><label for="src" class="cute text-xl font-extrabold text-emerald-700">我的來源網址</label>
        <input id="src" data-k="src" type="url" autocomplete="off" class="fld ans mt-2 text-lg">
        <a id="srcLink" target="_blank" rel="noopener" class="hidden inline-block mt-2 bg-teal-600 hover:bg-teal-700 text-white font-bold rounded-xl px-4 py-1.5">點開來源，再看一遍 ↗</a></div>
      <div><label for="core" class="cute text-xl font-extrabold text-emerald-700">我的核心訊息（一句話，20 字內）</label>
        <textarea id="core" data-k="core" rows="2" class="fld ans mt-2 text-lg"></textarea></div>
    </div>
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-5 mb-5 shadow-sm">
      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-emerald-700 m-0">我確認了</p><span class="qtypeSlot" data-qid="tconf"></span></div>
      <div id="tconfOpts" class="space-y-2 mt-3"></div>
    </div>
    <div class="stepnav"></div>
  </section>
'''


def renum(s, n):
    s = re.sub(r'data-step="\d+"', 'data-step="%d"' % n, s, count=1)
    return re.sub(r'<section class="step( hidden)?"', '<section class="step' + (' hidden' if n > 1 else '') + '"', s, count=1)


ORDER = [STEP_TOPIC, M.STEP_EXAMPLE, M.STEP_AI, M.STEP_WRITE, M.STEP_KW, M.STEP_COPY, C_MAKE, C_TEXT, C_FX, C_MAT, C_SRC, C_SUBMIT]
BODY = NL + ''.join(renum(s, i + 1) for i, s in enumerate(ORDER)) + NL

_TEXTS = ['cat', 'hook', 'src', 'core', 'mat3'] + ['%s%d' % (p, i) for p in 'sk' for i in range(1, M.ROWS + 1)] + ['canvaLink']
CFG = {
    'ws': 'g5-L08', 'lessonPath': 'g5/L08', 'title': '確認主題、寫台詞、做出你的影片', 'stateKey': 'g5L08flow',
    'steps': ['拿回主題', '看範例', '資料與 AI', '寫台詞', '挑關鍵字', '複製進文件', '建立影片', '放進文字', '文字特效', '找素材', '素材來源', '分享繳交'],
    'reveals': [], 'revealOf': {}, 'autoFb': [], 'textSettings': ['scriptGemUrl'],
    'qtypes': dict(M.QTYPES, **{'ratio': 'experience', 'make': 'experience', 'text': 'experience', 'fx': 'experience',
                                'mat': 'experience', 'srcpage': 'experience', 'canvaLink': 'open', 'chk': 'experience'}),
    'choices': dict(M.CHOICES, **{
        'ratio': {'opts': ['橫式（16：9）', '直式（9：16）']},
        'make': {'opts': ['我建立了影片設計，比例是我選的那一種', '名字改成「我的解說影片」了'], 'multi': True, 'block': True},
        'text': {'opts': ['頁數和台詞句數一樣，每頁一句', '每頁字幕都貼好了，看得清楚', '每頁字幕的字型、大小、位置一樣'], 'multi': True, 'block': True},
        'fx': {'opts': ['每一頁字幕都有文字特效，而且是同一種', '我按播放從頭看過，字幕讀得完'], 'multi': True, 'block': True},
        'mat': {'opts': ['每一頁至少有 1 個素材', '素材跟那一頁的字幕有關', '素材沒有擋住字幕'], 'multi': True, 'block': True},
        'srcpage': {'opts': ['最後多了一頁「素材來源」', '每個用到的網站或 Canva 素材庫都寫了'], 'multi': True, 'block': True},
        'chk': {'opts': ['台詞寫了 7 句以上，每句都有關鍵字', 'Canva 影片每一頁都有字幕和文字特效', '每一頁都有素材，最後有素材來源頁', '分享連結貼好了，我自己點開看得到影片'], 'multi': True, 'block': True},
    }),
    'texts': _TEXTS,
    'patterns': {'canvaLink': r'^https?://(www\.)?canva\.(com|link)/\S+'},
    'openQtexts': {'scriptAll': '我的台詞表（每句台詞和它的關鍵字）。', 'canvaLink': '我的 Canva 影片分享連結。'},
}

HOOKS = r'''
  var ROWS=@@ROWS@@;
  var SEGN=['①問題','①問題','②解釋','②解釋','②解釋','②解釋','③結論','③結論'];
  function rowsOf(p){var a=[];for(var i=1;i<=ROWS;i++)a.push(String(state[p+i]||'').trim());return a;}
  function nS(){return rowsOf('s').filter(Boolean).length;}
  function allKw(){var s=rowsOf('s'),k=rowsOf('k'),ok=s.some(Boolean);s.forEach(function(x,i){if(x&&!k[i])ok=false;});return ok;}
  function agg(){
    var out=[];rowsOf('s').forEach(function(v,i){if(v){var k=String(state['k'+(i+1)]||'').trim();out.push((i+1)+'. '+v+'（關鍵字：'+(k||'還沒寫')+'）');}});
    state.scriptAll=out.join(String.fromCharCode(10));
  }
  H.stepDone=function(n){
    var a=function(k){return state[k]!=null&&(Array.isArray(state[k])?state[k].length>0:filled(state[k]));};
    if(n===1)return a('tconf')&&n!==curStep;
    if(n===2)return a('ex')&&n!==curStep;
    if(n===3)return a('mat3')&&n!==curStep;
    if(n===4)return nS()>=7&&a('write')&&n!==curStep;
    if(n===5)return allKw()&&a('kw')&&n!==curStep;
    if(n===6)return a('doc')&&n!==curStep;
    if(n===7)return a('ratio')&&a('make')&&n!==curStep;
    if(n===8)return a('text')&&n!==curStep;
    if(n===9)return a('fx')&&n!==curStep;
    if(n===10)return a('mat')&&n!==curStep;
    if(n===11)return a('srcpage')&&n!==curStep;
    return null;
  };
  H.report=function(){
    var over=rowsOf('s').filter(function(x){return x.length>20;}).length;
    return ['台詞：寫了 '+nS()+' 句'+(over?'（有 '+over+' 句超過 20 字）':''),
      '關鍵字：'+(allKw()?'每句都有':'還有句子沒寫'),
      '影片比例：'+(state.ratio||'還沒選'),
      'Canva 分享連結：'+(filled(state.canvaLink)?'已貼':'還沒貼'),
      '自查表：已勾 '+((state.chk||[]).length)+' 項（共 4 項）'];
  };
  H.showAnswers=function(){};
  H.clear=function(){['tconf','ex','write','kw','doc','make','text','fx','mat','srcpage','chk'].forEach(function(k){state[k]=[];});state.ratio=null;C.texts.forEach(function(k){state[k]='';});agg();};

  function topicLines(){return '類型：'+(state.cat||'')+'\n開頭句：'+(state.hook||'')+'\n來源網址：'+(state.src||'')+'\n核心訊息：'+(state.core||'');}
  function tplText(){
    var t='我的台詞表\n我的主題：\n'+topicLines()+'\n\n我找到的資料（3～5 句，用自己的話）：\n'+(state.mat3||'')+'\n';
    for(var i=1;i<=ROWS;i++){t+='\n第 '+i+' 句（'+SEGN[i-1]+'）：'+(state['s'+i]||'')+'\n關鍵字：'+(state['k'+i]||'');}
    return t;
  }
  function aiText(){
    return '我是五年級學生，想做 30～45 秒的解說影片。\n類型：'+(state.cat||'（還沒選）')+'\n我找到的資料：'+(String(state.mat3||'').trim()||'（把你寫的資料貼在這裡）')+'\n核心訊息：'+(String(state.core||'').trim()||'（還沒寫）')+'\n請你用問題一步一步帶我自己寫台詞，一次只問一個問題，不要直接幫我寫。';
  }
  function topicHas(){return !!state.cat||filled(state.hook)||filled(state.src)||filled(state.core);}
  function workHas(){return filled(state.mat3)||nS()>0||rowsOf('k').some(Boolean);}
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
  function esc(s){return String(s).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
  H.render=function(){
    agg();
    var l=$('srcLink'),u=String(state.src||'').trim();
    if(l){if(/^https?:\/\/\S+/.test(u)){l.href=u;l.classList.remove('hidden');}else{l.removeAttribute('href');l.classList.add('hidden');}}
    var t=$('tplText');if(t)t.textContent=tplText();
    var m=$('aiMsg');if(m)m.textContent=aiText();
    document.querySelectorAll('[data-count]').forEach(function(e){var n=String(state[e.dataset.count]||'').length;e.textContent=n;e.parentNode.className='text-sm mt-0.5 '+(n>20?'text-rose-600 font-bold':'text-slate-500');});
    document.querySelectorAll('[data-echo]').forEach(function(e){e.textContent=String(state[e.dataset.echo]||'').trim()||'（這句還沒寫）';});
    var sc=$('scriptCount');if(sc){var n=nS();sc.textContent='目前寫了 '+n+' 句'+(n>=7?'，夠了。':'，至少要 7 句。');}
    var cl=$('capList');
    if(cl){
      var h='';
      for(var i=1;i<=ROWS;i++){var v=String(state['s'+i]||'').trim();if(v)h+='<div class="flex items-center gap-2 flex-wrap"><span class="shrink-0 text-sm font-bold text-slate-500">第 '+i+' 頁</span><span class="flex-1 min-w-[10rem] text-lg text-slate-800 font-bold">'+esc(v)+'</span><button type="button" data-cap="'+i+'" class="shrink-0 bg-sky-600 hover:bg-sky-700 text-white font-bold rounded-xl px-4 py-1.5">複製</button></div>';}
      cl.innerHTML=h||'<p class="text-lg text-rose-600 font-bold">還沒有台詞，回「寫台詞」那一步填好。</p>';
    }
    var kl=$('kwList');
    if(kl){
      var h2='';
      for(var j=1;j<=ROWS;j++){var sv=String(state['s'+j]||'').trim();if(sv)h2+='<p><b class="text-slate-500">第 '+j+' 頁</b>　'+esc(sv)+'　<b class="text-teal-700">'+esc(state['k'+j]||'（沒有關鍵字）')+'</b></p>';}
      kl.innerHTML=h2||'<p class="text-rose-600 font-bold">還沒有台詞和關鍵字，回前面填好。</p>';
    }
    var lm=$('linkMsg'),v=String(state.canvaLink||'').trim();
    if(lm){
      if(!v){lm.textContent='';}
      else{var ok=/^https?:\/\/(www\.)?canva\.(com|link)\/\S+/.test(v);
        lm.className='text-base font-bold mt-2 min-h-[24px] '+(ok?'text-emerald-600':'text-amber-600');
        lm.textContent=ok?'連結看起來可以。貼好後，自己點開確認看得到影片。':'這看起來不是 Canva 的連結，回 Canva 按「分享」→「複製連結」再貼一次。';}
    }
  };
  H.changed=function(){H.render();};
  document.addEventListener('click',function(e){var b=e.target.closest&&e.target.closest('[data-cap]');if(b)copyText(String(state['s'+b.dataset.cap]||''),b);});

  // ===== 拿回 L07 的內容（L07 存的主題：studentWork g5-L07__年-班-號__topic）與這節存的台詞（__script）=====
  function wid(i,ws,kind){return ws+'__'+i.grade+'-'+i.className+'-'+i.studentId+'__'+kind;}
  function idn(){var i=getIdentity();if(!identityValid(i)){markIdentity(true);return null;}markIdentity(false);return i;}
  var NEEDID='先到頁面最上面填年級、班級、座號，再按一次。';
  function loadTopic(i,st,silent,done){
    authResolved.then(function(){return ensureAuth();}).then(function(){return db.collection('studentWork').doc(wid(i,'g5-L07','topic')).get();}).then(function(doc){
      if(!doc.exists){if(!silent)say(st,'沒有找到你在上一節存的主題。直接在下面寫，或問老師。','amber');return;}
      if(!silent&&topicHas()&&!confirm('這會換掉你現在寫的主題，確定要拿回之前存的嗎？'))return;
      var d=(doc.data()||{}).data||{};
      state.cat=d.cat||'';state.hook=d.hook||'';state.src=d.src||'';state.core=d.core||'';
      save();renderAll();say(st,'已拿回你在上一節存的主題。','emerald');
    }).catch(function(e){console.warn('拿回主題失敗',e);if(!silent)say(st,'現在拿不到，晚點再試試看。','amber');});
  }
  function scriptData(){var d={cat:state.cat||'',hook:state.hook||'',src:state.src||'',core:state.core||'',mat3:state.mat3||'',rows:[]};
    for(var i=1;i<=ROWS;i++)d.rows.push({s:state['s'+i]||'',k:state['k'+i]||''});return d;}
  function saveWork(i){
    return authResolved.then(function(){return ensureAuth();}).then(function(){
      return db.collection('studentWork').doc(wid(i,WS,'script')).set({worksheetId:WS,kind:'script',grade:i.grade,className:i.className,studentId:i.studentId,data:scriptData(),text:String(state.scriptAll||'').slice(0,1500),updatedAt:firebase.firestore.FieldValue.serverTimestamp()});
    });
  }
  function loadWork(i,st,silent){
    authResolved.then(function(){return ensureAuth();}).then(function(){return db.collection('studentWork').doc(wid(i,WS,'script')).get();}).then(function(doc){
      if(!doc.exists){if(!silent)say(st,'還沒有找到你存過的台詞。寫好之後按「存起來」，下次就能拿回來。','amber');if(silent&&!topicHas())loadTopic(i,$('topicStat'),true);return;}
      if(!silent&&workHas()&&!confirm('這會換掉你現在寫的台詞，確定要拿回之前存的嗎？'))return;
      var d=(doc.data()||{}).data||{};
      ['cat','hook','src','core','mat3'].forEach(function(k){if(d[k]!=null)state[k]=d[k];});
      (d.rows||[]).forEach(function(r,n){var x=n+1;if(x>ROWS)return;state['s'+x]=r.s||'';state['k'+x]=r.k||'';});
      save();renderAll();say(st,'已拿回你存的台詞。','emerald');
    }).catch(function(e){console.warn('拿回台詞失敗',e);if(!silent)say(st,'現在拿不到，晚點再試試看。','amber');});
  }
  H.afterSubmit=function(i){if(workHas())saveWork(i).catch(function(e){console.warn('存台詞失敗',e);});};
  $('topicLoad').onclick=function(){
    var i=idn(),st=$('topicStat');
    if(!i){say(st,NEEDID,'rose');return;}
    if(!db){say(st,'現在連不上，晚點再試試看。','amber');return;}
    loadTopic(i,st,false);
  };
  document.querySelectorAll('[data-script-save]').forEach(function(b){b.onclick=function(){
    var i=idn(),st=b.closest('div.bg-white').querySelector('[data-script-stat]');
    if(!i){say(st,NEEDID,'rose');return;}
    if(!workHas()){say(st,'先寫一點再存。','amber');return;}
    if(!db){say(st,'現在連不上，晚點再試試看。','amber');return;}
    say(st,'存檔中…','indigo');
    saveWork(i).then(function(){say(st,'已存起來。下次按「拿回我存的台詞」就有了。','emerald');}).catch(function(e){console.warn('存台詞失敗',e);say(st,'現在存不了，晚點再試試看。','amber');});
  };});
  document.querySelectorAll('[data-script-load]').forEach(function(b){b.onclick=function(){
    var i=idn(),st=b.closest('div.bg-white').querySelector('[data-script-stat]');
    if(!i){say(st,NEEDID,'rose');return;}
    if(!db){say(st,'現在連不上，晚點再試試看。','amber');return;}
    loadWork(i,st,false);
  };});
  // 身分填好、而且這節的內容還是空的，就自動拿一次（先拿這節存的台詞，沒有再拿 L07 的主題；不會蓋掉學生已經寫的）
  function autoLoad(){var i=getIdentity();if(!identityValid(i)||!db||workHas())return;loadWork(i,$('topicStat'),true);}
  document.addEventListener('change',function(e){if(e.target&&/^id(Grade|Class|Student)$/.test(e.target.id))autoLoad();});
  fbReady.then(function(){return authResolved;}).then(autoLoad).catch(function(){});

  $('tplCopy').onclick=function(){copyText(tplText(),this);};
  $('copyAI').onclick=function(){copyText(aiText(),this);};
  H.render();
'''.replace('@@ROWS@@', str(M.ROWS))

SPEC = {
    'summary': '拿回 L07 存的主題並確認；看老師「資料→問題→台詞」的範例；寫下資料，用 AI 教練的提問（或句型卡）引導自己寫出 7～8 句台詞（每句 20 字內，用自己的話），自己挑每句 1～2 個可搜尋的關鍵字（AI 不幫忙），複製進老師給的文件；在 Canva 選好影片比例（橫式或直式）、建立影片，一句一頁把台詞放成字幕並套用同一種文字特效；照字幕找素材，每頁至少 1 個放進該頁；最後加素材來源頁；貼 Canva 分享連結繳交。',
    'questions': [
        M.SPEC_SCRIPT,
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


t = sub1(r'<title>.*?</title>', '<title>寫台詞、做出你的影片｜L08 教學活動</title>', t)
t = sub1(r'<h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">.*?</h1>',
         '<h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">寫台詞、做出你的影片</h1>', t)
t = sub1(r'<p class="text-sm text-slate-500 mt-2">L06 Docs[^<]*</p>',
         '<p class="text-sm text-slate-500 mt-2">L08 確認主題・寫台詞・Canva 影片 · 教學活動流程（2 節課）</p>', t)
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
