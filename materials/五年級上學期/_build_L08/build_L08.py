# -*- coding: utf-8 -*-
# 產生五上 L08「確認主題、寫台詞、做出你的影片」學習單。
# 2026-11-16 老師：L07 改回原本（找主題 7 步）；L08 = 原 L07 的後半（確認主題、寫台詞、關鍵字）＋新的 Canva 影片課
# （建立影片、選比例、文字輸入、文字特效、照字幕找素材）；要能「拿回 L07 的內容」；繳交不需要回 Google。
# 關鍵字學生自己選、AI 不幫忙；只有寫台詞 AI 可協助（用提問引導）；要有台詞撰寫範例。
# 晚：文件由老師幫學生開；台詞、關鍵字改成在學習單裡填，填完按「複製台詞表」貼進老師給的文件。
# Canva 的影片像「會動的簡報」：一頁一個畫面，沒有時間軸，學習單只說「頁面」。
#
# 2026-11-17：只做到「建立影片」共 8 步（第 3 步對 Gem 說「開始寫台詞」；台詞表可新增問題／解釋／結論；
#   關鍵字在文件裡寫；專案命名「班級座號 影片標題」；繳交前自己檢查）。放進文字、文字特效、找素材移到下週，
#   素材來源、分享連結不做；canva_steps_src.py 只用 STEP1，STEP2～STEP6 留給下週的 L09。
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


C_MAKE = NS['STEP1']

# 步驟 7（建立影片）：專案名稱改成「班級座號 影片標題」，並幫學生組好名字
C_MAKE = must(C_MAKE, '<li>把名字改成「我的解說影片」。</li>', '<li>把專案名稱改成下面的「專案名稱」（點最上面的名稱就能改）。</li>')
_MK_ANCH = '    <div class="bg-white border-4 border-rose-300 rounded-3xl p-5 mb-5 shadow-sm">' + NL + '      <div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold text-rose-700 m-0">我做到了'
NAME_CARD = '''    <div class="bg-white border-4 border-rose-300 rounded-3xl p-6 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-rose-700 m-0">專案名稱要取好</p>
      <p class="text-lg text-slate-700 mt-2">名字的格式是<b>班級座號　影片標題</b>，中間空一格。影片標題，就是你在「寫台詞表」那一步寫的標題。班級和座號各用 2 位數，例如 11 班 22 號，寫成 <b>1122</b>。</p>
      <p class="text-lg text-slate-700 mt-4">你的專案名稱：</p>
      <div class="flex gap-2 flex-wrap items-center mt-1">
        <b id="projName" class="text-2xl text-rose-700 bg-rose-50 border-2 border-rose-200 rounded-2xl px-4 py-2"></b>
        <button type="button" id="projCopy" class="bg-rose-600 hover:bg-rose-700 text-white font-bold rounded-xl px-4 py-2">複製名稱</button>
      </div>
    </div>
'''
C_MAKE = must(C_MAKE, _MK_ANCH, NAME_CARD + _MK_ANCH)

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

# 步驟 8（檢查、繳交）：不交 Canva 連結；自己檢查台詞和關鍵字、Canva 專案
STEP_SUBMIT = '''
  <!-- ===== 步驟 8：自己檢查，再繳交 ===== -->
  <section class="step hidden" data-step="8">
    <div class="bg-white border-4 border-indigo-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h2 class="cute text-3xl font-extrabold text-indigo-700 m-0">自己檢查，再繳交</h2>
      <p class="text-slate-600 mt-2 text-lg">影片還在 Canva 裡，這節不用交連結。先自己檢查一遍，再按繳交。下週繼續做字幕和素材。</p>
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


def renum(s, n):
    s = re.sub(r'data-step="\d+"', 'data-step="%d"' % n, s, count=1)
    return re.sub(r'<section class="step( hidden)?"', '<section class="step' + (' hidden' if n > 1 else '') + '"', s, count=1)


ORDER = [STEP_TOPIC, M.STEP_PARTS, M.STEP_DEMO, M.STEP_AI, M.STEP_WRITE, M.STEP_COPY, M.STEP_KW, C_MAKE, STEP_SUBMIT]
BODY = NL + ''.join(renum(s, i + 1) for i, s in enumerate(ORDER)) + NL

_TEXTS = ['cat', 'hook', 'src', 'core', 'vtitle'] + ['%s%d' % (p, i) for p in 'sg' for i in range(1, M.MAXR + 1)]
CFG = {
    'ws': 'g5-L08', 'lessonPath': 'g5/L08', 'title': '寫台詞、建立你的影片', 'stateKey': 'g5L08flow',
    'steps': ['拿回主題', '影片三部分', '看示範', '問 AI 教練', '寫台詞表', '複製進文件', '挑關鍵字', '建立影片', '檢查繳交'],
    'reveals': [], 'revealOf': {}, 'autoFb': [], 'textSettings': ['scriptGemUrl'],
    'qtypes': dict(M.QTYPES, **{'ratio': 'experience', 'make': 'experience', 'chk': 'experience'}),
    'choices': dict(M.CHOICES, **{
        'ratio': {'opts': ['橫式（16：9）', '直式（9：16）']},
        'make': {'opts': ['我建立了影片設計，比例是我選的那一種', '專案名稱改成「班級座號　影片標題」了'], 'multi': True, 'block': True},
        'chk': {'opts': ['台詞表文件裡，每一句都有台詞和關鍵字', 'Canva 已經建立好影片專案，比例也選好了', 'Canva 專案名稱是「班級座號　影片標題」'], 'multi': True, 'block': True},
    }),
    'texts': _TEXTS,
    'patterns': {},
    'openQtexts': {'scriptAll': '我的台詞表（每句台詞，依開頭、主體、CTA 排列）。'},
}

HOOKS = r'''
  var MAXR=@@MAXR@@,DEFSEG='@@DEFSEG@@',OLDSEG='qqeeeecc';
  var SEGI={q:['①','開頭（Hook）','rose','開頭'],e:['②','主體（Body）','sky','主體'],c:['③','行動呼籲（CTA）','emerald','行動呼籲']},SEGO=['q','e','c'];
  var fullMsg=false;
  var DEMOS=@@DEMOS@@;
  var CATDEMO={'謠言':'rumor','冷知識':'fact','事實澄清':'clarify'};
  var demoPick=null,lastDemo='';
  function demoKey(){return demoPick||CATDEMO[state.cat]||'rumor';}
  function renderDemo(){
    var host=$('demoRows');if(!host)return;
    var key=demoKey();
    document.querySelectorAll('[data-demo]').forEach(function(b){
      var on=b.dataset.demo===key;
      b.className='cute border-4 text-xl font-extrabold rounded-2xl px-6 py-2 '+(on?'border-violet-600 bg-violet-600 text-white':'border-violet-300 bg-white text-violet-800 hover:bg-violet-50');
    });
    if(key===lastDemo)return;lastDemo=key;
    var d=DEMOS[key],tone={'①':'rose','②':'sky','③':'emerald'};
    $('demoTitle').textContent='示範：'+d.label+'　題目「'+d.topic+'」';
    host.innerHTML=d.rows.map(function(r){var t=tone[r[0].charAt(0)];return '<tr class="border-t border-slate-200 align-top"><td class="py-2 pr-3 font-bold text-'+t+'-700 whitespace-nowrap">'+esc(r[0])+'</td><td class="py-2 pr-3 font-bold text-slate-900">'+esc(r[1])+'</td><td class="py-2 text-slate-600">'+esc(r[2])+'</td></tr>';}).join('');
  }
  document.querySelectorAll('[data-demo]').forEach(function(b){b.onclick=function(){demoPick=b.dataset.demo;renderDemo();};});
  // 每一句是一個「欄位」s1..s12，屬於哪一段記在 g1..g12（q 開頭／e 主體／c CTA），o 是排序用的序號（新增的排在同一段最後）
  function ensureSegs(){
    var any=false,i;
    for(i=1;i<=MAXR;i++)if(state['g'+i])any=true;
    if(!any)for(i=1;i<=DEFSEG.length;i++)state['g'+i]=DEFSEG.charAt(i-1);
    for(i=1;i<=MAXR;i++)if(!state['g'+i]&&String(state['s'+i]||'').trim())state['g'+i]=OLDSEG.charAt(i-1)||'e';
  }
  function slots(){
    var out=[];
    SEGO.forEach(function(sg){
      var a=[];for(var i=1;i<=MAXR;i++)if(state['g'+i]===sg)a.push(i);
      a.sort(function(x,y){return ((+state['o'+x]||x)-(+state['o'+y]||y))||(x-y);});
      out=out.concat(a);
    });
    return out;
  }
  function textOf(i){return String(state['s'+i]||'').trim();}
  function nS(){return slots().filter(function(i){return textOf(i);}).length;}
  function segCount(sg){return slots().filter(function(i){return state['g'+i]===sg&&textOf(i);}).length;}
  function segsOk(){return segCount('q')>0&&segCount('e')>0&&segCount('c')>0;}
  function agg(){
    var out=[],n=0;
    slots().forEach(function(i){var v=textOf(i);if(v){n++;out.push(n+'.（'+SEGI[state['g'+i]][3]+'）'+v);}});
    state.scriptAll=out.join(String.fromCharCode(10));
  }
  H.stepDone=function(n){
    var a=function(k){return state[k]!=null&&(Array.isArray(state[k])?state[k].length>0:filled(state[k]));};
    if(n===1)return a('tconf')&&n!==curStep;
    if(n===4)return a('gem')&&n!==curStep;
    if(n===5)return nS()>=7&&segsOk()&&filled(state.vtitle)&&a('write')&&n!==curStep;
    if(n===6)return a('doc')&&n!==curStep;
    if(n===7)return a('kw')&&n!==curStep;
    if(n===8)return a('ratio')&&a('make')&&n!==curStep;
    return null;   // 第 2、3 步只閱讀、第 9 步是繳交：看過就算完成
  };
  H.report=function(){
    var over=slots().filter(function(i){return textOf(i).length>20;}).length;
    return ['台詞：寫了 '+nS()+' 句（開頭 '+segCount('q')+'、主體 '+segCount('e')+'、CTA '+segCount('c')+'）'+(over?'，有 '+over+' 句超過 20 字':''),
      '影片比例：'+(state.ratio||'還沒選'),
      '影片標題：'+(String(state.vtitle||'').trim()||'還沒寫'),
      '自查表：已勾 '+((state.chk||[]).length)+' 項（共 3 項）'];
  };
  H.showAnswers=function(){};
  H.clear=function(){
    ['tconf','gem','write','kw','doc','make','chk'].forEach(function(k){state[k]=[];});state.ratio=null;
    C.texts.forEach(function(k){state[k]='';});
    for(var i=1;i<=MAXR;i++)delete state['o'+i];
    ensureSegs();agg();
  };

  function topicLines(){return '類型：'+(state.cat||'')+'\n開頭句：'+(state.hook||'')+'\n來源網址：'+(state.src||'')+'\n核心訊息：'+(state.core||'');}
  function tplText(){
    var t='我的台詞表\n我的主題：\n'+topicLines()+'\n影片標題：'+(state.vtitle||'')+'\n\n台詞（關鍵字等一下在文件裡寫）：',n=0;
    slots().forEach(function(i){n++;var g=SEGI[state['g'+i]];t+='\n\n第 '+n+' 句（'+g[0]+g[3]+'）：'+(state['s'+i]||'')+'\n關鍵字：';});
    return t;
  }
  function projName(){
    var i;try{i=getIdentity();}catch(e){return '';}
    if(!identityValid(i))return '';
    var p2=function(x){x=String(x).trim();return x.length<2?('0'+x):x;};
    return p2(i.className)+p2(i.studentId)+' '+(String(state.vtitle||'').trim()||'影片標題');
  }
  function esc(x){return String(x).replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
  function topicHas(){return !!state.cat||filled(state.hook)||filled(state.src)||filled(state.core);}
  function workHas(){return nS()>0||filled(state.vtitle);}
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

  // ===== 台詞表：欄位會依「新增開頭／主體／CTA」增減；只有欄位的組成改變時才重建，打字時不會被打斷 =====
  var lastSig='';
  function buildRows(){
    var host=$('scriptRows');if(!host)return;
    var sl=slots(),sig=sl.map(function(i){return i+state['g'+i];}).join(',');
    if(sig===lastSig&&host.children.length===sl.length)return;
    lastSig=sig;host.innerHTML='';
    sl.forEach(function(i,n){
      var g=SEGI[state['g'+i]],row=document.createElement('div');
      row.className='flex items-start gap-2 flex-wrap';
      row.innerHTML='<span class="shrink-0 inline-block bg-'+g[2]+'-100 border-2 border-'+g[2]+'-300 text-'+g[2]+'-800 rounded-full px-2.5 py-0.5 text-sm font-bold">'+g[0]+g[1]+'　第 '+(n+1)+' 句</span>'
        +'<div class="flex-1 min-w-[14rem]"><input id="s'+i+'" data-k="s'+i+'" type="text" autocomplete="off" maxlength="40" class="fld ans text-lg"><p class="text-sm text-slate-500 mt-0.5"><span data-count="s'+i+'">0</span> / 20 字</p></div>'
        +'<button type="button" data-delrow="'+i+'" class="ans shrink-0 text-slate-500 hover:text-rose-600 font-bold px-2 py-1" title="刪掉這一句">刪除</button>';
      var inp=row.querySelector('input');inp.value=state['s'+i]||'';
      inp.addEventListener('input',function(){state['s'+i]=inp.value;save();renderFeedback();if(H.changed)H.changed('s'+i);});
      host.appendChild(row);
    });
  }
  function addRow(sg){
    var free=0,i,m=MAXR;
    for(i=1;i<=MAXR;i++){if(state['g'+i])m=Math.max(m,+state['o'+i]||i);else if(!free)free=i;}
    if(!free){fullMsg=true;H.render();return;}
    fullMsg=false;state['g'+free]=sg;state['s'+free]='';state['o'+free]=m+1;
    save();buildRows();H.render();
    var inp=$('s'+free);if(inp)inp.focus();
  }
  function delRow(i){
    if(textOf(i)&&!confirm('這一句已經寫了字，確定要刪掉嗎？'))return;
    fullMsg=false;state['g'+i]='';state['s'+i]='';delete state['o'+i];
    save();buildRows();H.render();
  }
  H.render=function(){
    ensureSegs();agg();buildRows();renderDemo();
    var l=$('srcLink'),u=String(state.src||'').trim();
    if(l){if(/^https?:\/\/\S+/.test(u)){l.href=u;l.classList.remove('hidden');}else{l.removeAttribute('href');l.classList.add('hidden');}}
    var t=$('tplText');if(t)t.textContent=tplText();
    document.querySelectorAll('[data-count]').forEach(function(e){var n=String(state[e.dataset.count]||'').length;e.textContent=n;e.parentNode.className='text-sm mt-0.5 '+(n>20?'text-rose-600 font-bold':'text-slate-500');});
    var sc=$('scriptCount');
    if(sc){var n=nS();sc.textContent='目前寫了 '+n+' 句（開頭 '+segCount('q')+'、主體 '+segCount('e')+'、行動呼籲 '+segCount('c')+'）'+(n>=7?'，夠了。':'，至少要 7 句。')+(filled(state.vtitle)?'':'　影片標題還沒寫。')+(fullMsg?'　最多 '+MAXR+' 句，不能再新增了。':'');}
    var pn=$('projName');if(pn)pn.textContent=projName()||'（先填好最上面的班級、座號）';
  };
  H.changed=function(){H.render();};
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('[data-addseg]');if(a){addRow(a.dataset.addseg);return;}
    var d=e.target.closest&&e.target.closest('[data-delrow]');if(d)delRow(+d.dataset.delrow);
  });
  document.querySelectorAll('[data-addseg]').forEach(function(b){b.classList.add('ans');});
  ['idGrade','idClass','idStudent'].forEach(function(id){var e=$(id);if(e)e.addEventListener('input',function(){H.render();});});

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
  function scriptData(){
    var d={cat:state.cat||'',hook:state.hook||'',src:state.src||'',core:state.core||'',vtitle:state.vtitle||'',slots:[]};
    for(var i=1;i<=MAXR;i++){var r={g:state['g'+i]||'',s:state['s'+i]||''};if(state['o'+i])r.o=+state['o'+i];d.slots.push(r);}
    return d;
  }
  function saveWork(i){
    return authResolved.then(function(){return ensureAuth();}).then(function(){
      return db.collection('studentWork').doc(wid(i,WS,'script')).set({worksheetId:WS,kind:'script',grade:i.grade,className:i.className,studentId:i.studentId,data:scriptData(),text:String(state.scriptAll||'').slice(0,1500),updatedAt:firebase.firestore.FieldValue.serverTimestamp()});
    });
  }
  function loadWork(i,st,silent){
    authResolved.then(function(){return ensureAuth();}).then(function(){return db.collection('studentWork').doc(wid(i,WS,'script')).get();}).then(function(doc){
      if(!doc.exists){if(!silent)say(st,'還沒有找到你存過的台詞。寫好之後按「存起來」，下次就能拿回來。','amber');if(silent&&!topicHas())loadTopic(i,$('topicStat'),true);return;}
      if(!silent&&workHas()&&!confirm('這會換掉你現在寫的台詞，確定要拿回之前存的嗎？'))return;
      var d=(doc.data()||{}).data||{},x;
      ['cat','hook','src','core','vtitle'].forEach(function(k){if(d[k]!=null)state[k]=d[k];});
      for(x=1;x<=MAXR;x++){state['g'+x]='';state['s'+x]='';delete state['o'+x];}
      if(d.slots){d.slots.forEach(function(r,n){x=n+1;if(x>MAXR)return;state['g'+x]=r.g||'';state['s'+x]=r.s||'';if(r.o)state['o'+x]=r.o;});}
      else{(d.rows||[]).forEach(function(r,n){x=n+1;if(x>MAXR)return;state['g'+x]=OLDSEG.charAt(n)||'e';state['s'+x]=r.s||'';});}
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
  $('copyGo').onclick=function(){copyText('開始寫台詞',this);};
  $('projCopy').onclick=function(){var p=projName();if(p)copyText(p,this);};
  H.render();
'''.replace('@@MAXR@@', str(M.MAXR)).replace('@@DEFSEG@@', M.DEFAULT_SEGS).replace('@@DEMOS@@', json.dumps(M.DEMOS, ensure_ascii=False))

SPEC = {
    'summary': '拿回 L07 存的主題並確認；學短影片的三個部分（開頭 Hook、主體、CTA），看冷知識、假資訊、事實釐清三種示範；對 AI 教練（Gem）說「開始寫台詞」，用它的提問引導自己想出台詞；在台詞表寫下至少 7 句（開頭、主體、CTA 三個部分，可新增，每句 20 字內，用自己的話）；複製台詞表貼進老師給的文件，並在文件裡自己挑每句 1～2 個可搜尋的關鍵字（AI 不幫忙）；在 Canva 選好影片比例、建立影片專案，專案名稱是「班級座號 影片標題」。這節不交 Canva 連結；字幕、文字特效、找素材在下週。',
    'questions': [
        M.SPEC_SCRIPT,
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


t = sub1(r'<title>.*?</title>', '<title>寫台詞、建立你的影片｜L08 教學活動</title>', t)
t = sub1(r'<h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">.*?</h1>',
         '<h1 class="cute text-3xl md:text-5xl font-extrabold text-indigo-600">寫台詞、建立你的影片</h1>', t)
t = sub1(r'<p class="text-sm text-slate-500 mt-2">L06 Docs[^<]*</p>',
         '<p class="text-sm text-slate-500 mt-2">L08 確認主題・寫台詞・建立 Canva 影片 · 教學活動流程（2 節課）</p>', t)
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
