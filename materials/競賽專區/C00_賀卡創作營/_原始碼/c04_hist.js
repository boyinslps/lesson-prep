/* ============================================================
   第 4 節｜我的對話紀錄（學生）＋ 老師管理（網址後面加 ?admin）＋ 歷程紀錄排版
   ------------------------------------------------------------
   資料：aiHistory/{年級-班級-座號}（見 firestore.rules）
     老師匯入：sessions（對話，整理對話紀錄.py 產生）、marks（老師標記）
     學生寫回：picks（挑的 4～5 輪）、picksAt
   一輪＝學生的一句提問（q）→ e度 的回答（a）→ 學生的下一句追問／修正（f）。
   ============================================================ */
(function(){
  if(!document.getElementById('hBody'))return;
  var AIH='aiHistory',MAXP=5,MINP=4,TEACHER='boyin0304@slps.tn.edu.tw';
  var LIM={qt:160,at:120,ft:120,issNote:90,mine:100},MINE_MIN=6,ISS_MIN=6;
  var KIND={ask:'提問策略',check:'發現問題',fix:'追問修正'};
  var FK=[['find','發現問題'],['fix','我修正了'],['ask','我追問了'],['add','我補充了']];
  var FKL={find:'發現問題',fix:'我的修正',ask:'我的追問',add:'我的補充'};
  var DEC=[['use','我採用 AI 的意見'],['edit','我改過之後才採用'],['no','我沒有採用']];
  var WHY=['很像我真實的經驗或感覺','我自己查過，確認是對的','我發現 AI 說錯了，所以追問修正','那天沒有發生，所以不用','太空泛，我換成只有我才有的細節','我沒看懂，請 AI 換個方式說','結果比原本更好'];
  var $=window.$,esc=window.esc,toast=window.toast;
  var DAYS='日一二三四五六';
  function nb(s){return String(s==null?'':s).replace(/[〔〕]/g,'');}  // 提問句型留下來的〔 〕一律拿掉

  /* ---------- 共用：資料索引與一輪的自動帶入 ---------- */
  function indexDoc(doc){
    var ix={flat:[],by:{},marks:{}};
    (doc.sessions||[]).forEach(function(se,si){
      (se.msgs||[]).forEach(function(m){var o={m:m,si:si,i:ix.flat.length};ix.flat.push(o);ix.by[m.id]=o;});
    });
    (doc.marks||[]).forEach(function(k){if(ix.by[k.id])ix.marks[k.id]=k;});
    return ix;
  }
  function plain(s){return nb(s).replace(/\*\*/g,'').replace(/\s*\n+\s*/g,' ').replace(/\s{2,}/g,' ').trim();}
  function clip(s,n){s=plain(s);return s.length>n?s.slice(0,n-1)+'…':s;}
  function nextA(ix,qid){var o=ix.by[qid];if(!o)return null;for(var j=o.i+1;j<ix.flat.length;j++){var x=ix.flat[j];if(x.si!==o.si)break;if(x.m.r==='u')break;if(x.m.r==='a'&&!x.m.g)return x;}return null;}
  function nextU(ix,aid){var o=ix.by[aid];if(!o)return null;for(var j=o.i+1;j<ix.flat.length;j++){var x=ix.flat[j];if(x.si!==o.si)break;if(x.m.r==='u')return x;}return null;}
  function roundIds(ix,qid){var a=nextA(ix,qid),f=a?nextU(ix,a.m.id):nextU(ix,qid);return {q:qid,a:a?a.m.id:'',f:f?f.m.id:''};}
  function autoFill(ix,p){
    var r=roundIds(ix,p.q);p.a=r.a;p.f=r.f;
    p.qt=clip(ix.by[p.q].m.x,LIM.qt);
    p.at=r.a?clip(ix.by[r.a].m.x,LIM.at):'';
    p.ft=r.f?clip(ix.by[r.f].m.x,LIM.ft):'';
    return p;
  }
  function newPick(ix,qid){return autoFill(ix,{q:qid,a:'',f:'',qt:'',at:'',ft:'',fk:'',issNote:'',dec:'',why:[],mine:'',ts:Date.now()});}
  function isDone(p){return !!(p.qt&&p.qt.trim()&&p.at&&p.at.trim()&&p.fk&&(p.issNote||'').trim().length>=ISS_MIN&&p.dec&&(p.mine||'').trim().length>=MINE_MIN);}
  // 評審會看的 4 個地方（簡章五）：只是提醒，不擋人
  function rubric(p){return [['批判檢視 30%',(p.issNote||'').trim().length>=12],['提問與修正 30%',(p.ft||'').trim().length>=4],['生活連結 30%',(p.mine||'').trim().length>=15],['權責揭露 20%',!!p.dec]];}
  function cleanPick(p){
    return {q:String(p.q),a:String(p.a||''),f:String(p.f||''),qt:nb(p.qt).slice(0,LIM.qt),at:nb(p.at).slice(0,LIM.at),ft:nb(p.ft).slice(0,LIM.ft),
      fk:FKL[p.fk]?p.fk:'',issNote:nb(p.issNote).slice(0,LIM.issNote),
      dec:p.dec==='use'||p.dec==='edit'||p.dec==='no'?p.dec:'',why:(p.why||[]).filter(function(x){return WHY.indexOf(x)>=0;}),mine:nb(p.mine).slice(0,LIM.mine),ts:Number(p.ts)||0};
  }
  function fmtT(t){return String(t||'').replace('-','/');}
  function sessHead(se){
    var d=se.date?new Date(se.date+'T00:00:00'):null,w=d&&!isNaN(d)?'（'+DAYS[d.getDay()]+'）':'';
    var md=se.date?Number(se.date.slice(5,7))+'/'+Number(se.date.slice(8,10)):'';
    return md+w+'<span class="md">'+esc(se.mode||'')+'</span>';
  }

  /* ---------- 對話畫面（學生與老師共用）---------- */
  // o: {admin, picks}
  function chatHTML(doc,ix,o){
    var role={};
    (o.picks||[]).forEach(function(p,k){
      if(ix.by[p.q])role[p.q]=[k+1,'原始提問'];
      if(p.a&&ix.by[p.a])role[p.a]=[k+1,'AI 回答'];
      if(p.f&&ix.by[p.f])role[p.f]=[k+1,'我的追問／修正'];
    });
    var pickIdx={};(o.picks||[]).forEach(function(p,k){pickIdx[p.q]=k+1;});
    var h='';
    (doc.sessions||[]).forEach(function(se){
      h+='<div class="sess">'+sessHead(se)+'</div>';
      (se.msgs||[]).forEach(function(m){
        var mk=ix.marks[m.id],rl=role[m.id];
        h+='<div class="msg '+m.r+(m.g?' g':'')+(rl?' pk':'')+'" data-mid="'+m.id+'">';
        h+='<div class="av">'+(m.r==='u'?'我':'e度')+'</div><div class="bw">';
        if(mk)h+='<div class="mk k-'+esc(mk.kind||'')+'"><b>★ '+esc(KIND[mk.kind]||'老師推薦')+'</b><span>'+esc(nb(mk.label))+'</span>'+(mk.note?'<span class="ex">'+esc(nb(mk.note))+'</span>':'')+'</div>';
        if(rl)h+='<span class="rb">第 '+rl[0]+' 輪・'+rl[1]+'</span>';
        h+='<div class="bub"><div class="tx">'+esc(m.g?'e度 打招呼':nb(m.x))+'</div>'+(m.g?'':'<div class="tm">'+esc(fmtT(m.t))+'</div>')+'</div>';
        if(!m.g){
          if(o.admin)h+='<div class="act"><button class="pbtn mkb" type="button" data-mk="'+m.id+'">'+(mk?'編輯標記':'★ 標記')+'</button></div>';
          else if(m.r==='u')h+='<div class="act"><button class="pbtn'+(pickIdx[m.id]?' on':'')+'" type="button" data-pick="'+m.id+'"><svg class="ico"><use href="#'+(pickIdx[m.id]?'i-check':'i-plus')+'"/></svg>'+(pickIdx[m.id]?'已挑為第 '+pickIdx[m.id]+' 輪（再按取消）':'挑這一輪')+'</button></div>';
        }
        h+='</div></div>';
      });
    });
    return h||'<div class="hempty">這位同學還沒有對話紀錄。</div>';
  }
  function flash(root,id){
    var el=root.querySelector('[data-mid="'+id+'"]');if(!el)return;
    el.scrollIntoView({behavior:'smooth',block:'center'});
    el.classList.remove('flash');void el.offsetWidth;el.classList.add('flash');
    setTimeout(function(){el.classList.remove('flash');},1900);
  }

  /* ---------- 歷程紀錄的文字（學生編輯 → 排版）---------- */
  function decLabel(d){for(var i=0;i<DEC.length;i++)if(DEC[i][0]===d)return DEC[i][1];return '';}
  function roundText(p){
    var a=nb(p.at).trim(),fd=nb(p.issNote).trim();
    var why=(p.dec?'【'+decLabel(p.dec)+'】':'')+(p.why||[]).join('；');
    if(nb(p.mine).trim())why+=(why&&!/】$/.test(why)?'。':'')+nb(p.mine).trim();
    return {q:nb(p.qt).trim(),a:a,fd:fd,fl:FKL[p.fk]||'發現與修正',f:nb(p.ft).trim()||'（這一輪沒有追問）',why:why};
  }
  function rowH(l,v,extra){return '<div class="rr"><div class="l">'+l+'</div><div class="v">'+v+(extra||'')+'</div></div>';}
  function sheetEl(items,o){
    // items: [{p, mode}]
    var s=document.createElement('div');s.className='sheet'+(o&&o.brk?' brk':'');
    var h='<h1>教育型 AI 協作歷程紀錄</h1><div class="sub">摘錄與教育型 AI（e度）最具代表性的人機對話，共 '+items.length+' 輪，依重要程度排序</div>';
    items.forEach(function(it,k){
      var t=roundText(it.p);
      h+='<div class="rd"><div class="rh">第 '+(k+1)+' 輪'+(it.mode?'　（'+esc(it.mode)+'）':'')+'</div>'+
        rowH('我的原始提問（Prompt）',esc(t.q))+
        rowH('教育型 AI 的回答摘要與問題發現',esc(t.a),t.fd?'<span class="fd"><b>'+esc(t.fl)+'：</b>'+esc(t.fd)+'</span>':'')+
        rowH('我的追問／修正指令',esc(t.f))+
        rowH('最終採用的理由',esc(t.why))+'</div>';
    });
    if(o&&o.idLabel)h+='<div class="idl">'+esc(o.idLabel)+'</div>';
    s.innerHTML=h;return s;
  }
  // 模擬分頁（A4，邊界 12mm，每一輪不拆開）→ 頁數
  function pagesOf(sheet){
    var H=273/25.4*96,y=0,pg=1,rds=sheet.querySelectorAll('.rd');
    var cs=getComputedStyle(sheet),top=parseFloat(cs.paddingTop)||0;
    var first=rds.length?rds[0].offsetTop-top:0;y=first;
    Array.prototype.forEach.call(rds,function(r){
      var h=r.offsetHeight+11;
      if(y+h>H+11&&y>0){pg++;y=0;}
      y+=h;
    });
    return pg;
  }
  var ov=null;
  function ensureOv(){
    if(ov)return ov;
    ov=document.createElement('div');ov.id='sheetPrint';ov.className='sheetov';
    ov.innerHTML='<div class="sbar"><b>AI 協作歷程紀錄（最多 2 頁）</b><span class="pg" id="shPg"></span><span class="adm-opt" id="shOpt"></span><button class="btn" type="button" id="shPrint"><svg class="ico"><use href="#i-download"/></svg>列印／存成 PDF</button><button class="btn ghost x" type="button" id="shClose"><svg class="ico"><use href="#i-x"/></svg>關閉</button></div><div class="sbody" id="shBody"></div>';
    document.body.appendChild(ov);
    $('shClose').onclick=function(){ov.classList.remove('on');document.body.style.overflow='';};
    $('shPrint').onclick=function(){
      var old=document.title;document.title=ov.dataset.title||'AI協作歷程紀錄';
      document.body.classList.add('printing');
      var done=function(){document.body.classList.remove('printing');document.title=old;window.removeEventListener('afterprint',done);};
      window.addEventListener('afterprint',done);
      setTimeout(function(){window.print();},50);
    };
    return ov;
  }
  // sheets: [{items, idLabel}]；opt: 額外控制項 HTML
  function showSheets(sheets,title,optHTML,onOpt){
    var o=ensureOv(),body=$('shBody');
    o.dataset.title=title;
    body.innerHTML='';
    $('shOpt').innerHTML=optHTML||'';
    var els=sheets.map(function(s,k){var e=sheetEl(s.items,{brk:k>0,idLabel:s.idLabel});body.appendChild(e);return e;});
    o.classList.add('on');document.body.style.overflow='hidden';
    var worst=Math.max.apply(null,els.map(pagesOf)),pg=$('shPg');
    pg.textContent='預估 '+worst+' 頁'+(worst>2?'（超過 2 頁，請減少輪數或縮短文字）':'（符合上限）');
    pg.className='pg '+(worst>2?'bad':'ok');
    if(onOpt)$('shOpt').querySelectorAll('input').forEach(function(i){i.onchange=onOpt;});
    return els;
  }

  /* ============================================================
     學生端
     ============================================================ */
  var S={id:'',doc:null,ix:null,picks:[],loadedFor:'',fb:null,saveT:null};
  var root=$('hBody'),lockEl=$('hLock'),statEl=$('hStat');
  function lock(msg,kind){S.doc=null;S.ix=null;if(typeof renderGuide==='function')renderGuide();root.hidden=true;lockEl.hidden=false;lockEl.innerHTML='<svg class="ico"><use href="#'+(kind==='bad'?'i-alert':'i-lock')+'"/></svg><span>'+esc(msg)+'</span>';}
  function ident(){return window.cardIdentity&&window.cardIdentity();}
  function ensureAuth(fb){return fb.auth.currentUser?Promise.resolve(fb.auth.currentUser):fb.auth.signInAnonymously();}
  function setHidden(id,val){var e=$(id);if(e&&e.value!==val){e.value=val;e.dispatchEvent(new Event('input',{bubbles:true}));}}
  function lkey(id){return 'aih_picks_'+id;}
  function readLocal(id){try{return JSON.parse(localStorage.getItem(lkey(id))||'null');}catch(e){return null;}}
  function writeLocal(id,o){try{localStorage.setItem(lkey(id),JSON.stringify(o));}catch(e){}}

  function loadStudent(force){
    var i=ident();
    if(!i){S.loadedFor='';lock('先在最上面填好年級、班級、座號，這一步才看得到你自己的對話紀錄。');return;}
    var id=i.grade+'-'+i.className+'-'+i.studentId;
    if(S.loadedFor===id&&!force)return;
    S.loadedFor=id;lock('讀取你的對話紀錄中…');
    window.cardFirebase().then(function(fb){
      if(!fb){lock('現在連不上雲端，看不到對話紀錄。請檢查網路，或告訴老師。','bad');return;}
      S.fb=fb;
      return ensureAuth(fb).then(function(){return fb.db.collection(AIH).doc(id).get();}).then(function(snap){
        if(S.loadedFor!==id)return;
        if(!snap.exists){lock('老師還沒有把你的對話紀錄放上來，或是年級、班級、座號填錯了。先檢查最上面的三個數字；沒錯的話，請告訴老師。');return;}
        S.id=id;S.doc=snap.data();S.ix=indexDoc(S.doc);
        var cloud={picks:S.doc.picks||[],at:S.doc.picksAt||0},loc=readLocal(id)||{picks:[],at:0};
        var use=(loc.at>cloud.at)?loc:cloud;
        S.picks=(use.picks||[]).filter(function(p){return p&&S.ix.by[p.q];}).map(cleanPick).slice(0,MAXP);
        lockEl.hidden=true;root.hidden=false;
        renderAll();
        statEl.textContent=loc.at>cloud.at?'用的是這台電腦上較新的存檔':'已讀取';
      });
    }).catch(function(e){console.warn('讀取對話紀錄失敗',e);if(S.loadedFor===id)lock('讀取失敗（'+(e.code||e.message||'網路')+'）。再按一次「讀取學習單」，還是不行就告訴老師。','bad');});
  }

  function renderAll(){renderSide();renderChat();renderPicks();refreshMeta();renderGuide();}
  function renderChat(){
    var c=$('hChat'),y=window.pageYOffset;
    c.innerHTML=chatHTML(S.doc,S.ix,{picks:S.picks});
    window.scrollTo(0,y);
  }
  function renderSide(){
    var jm=$('hJump'),marks=(S.doc.marks||[]).filter(function(k){return S.ix.by[k.id];}).sort(function(a,b){return S.ix.by[a.id].i-S.ix.by[b.id].i;});
    jm.innerHTML=marks.length?marks.map(function(k){
      return '<button type="button" class="k-'+esc(k.kind||'')+'" data-jump="'+k.id+'"><span class="kt">★ '+esc(KIND[k.kind]||'值得寫')+'</span>'+esc(k.label)+'<span class="tm">'+esc(fmtT(S.ix.by[k.id].m.t))+'</span></button>';
    }).join(''):'<div class="none">老師還沒有標記。自己從上往下看，找「我發現問題」「我追問」「我改了」的地方。</div>';
  }
  function renderMyPk(){
    var m=$('hMy');
    m.innerHTML=S.picks.length?S.picks.map(function(p,k){
      return '<button type="button" class="'+(isDone(p)?'':'todo')+'" data-gopick="'+k+'"><span class="pn">'+(k+1)+'</span><span class="pt">'+esc(clip(p.qt,18)||'（空白）')+'</span>'+(isDone(p)?'<svg class="ico ok"><use href="#i-check"/></svg>':'')+'</button>';
    }).join(''):'<div class="none">還沒挑。在左邊你說的話下面按「挑這一輪」。</div>';
  }
  function guideH(open,judge,asks,tip){
    return '<details class="gd"'+(open?' open':'')+'><summary>評審看什麼？怎麼寫？</summary><div class="gdb"><p class="gj"><b>評審看：</b>'+judge+'</p><ul>'+asks.map(function(x){return '<li>'+x+'</li>';}).join('')+'</ul>'+(tip?'<p class="gt">'+tip+'</p>':'')+'</div></details>';
  }
  function rubH(p){return rubric(p).map(function(r){return '<span class="rc'+(r[1]?' on':'')+'">'+(r[1]?'✓ ':'○ ')+r[0]+'</span>';}).join('');}
  function pickCardHTML(p,k){
    var n=S.picks.length,r=roundIds(S.ix,p.q),mode=(S.doc.sessions[S.ix.by[p.q].si]||{}).mode||'',op=k===0;
    var h='<div class="pcard'+(isDone(p)?' done':'')+'" data-i="'+k+'" id="pk'+k+'">';
    h+='<div class="ph"><span class="pn">'+(k+1)+'</span><span class="pt">優先 '+(k+1)+(k===0?'（最重要的放第 1）':'')+'<small>'+esc(fmtT(S.ix.by[p.q].m.t))+'　'+esc(mode)+'</small></span><span class="tools">'+
      '<button class="tbtn" type="button" data-act="view">看原文</button>'+
      '<button class="tbtn" type="button" data-act="up"'+(k===0?' disabled':'')+'>▲ 往前</button>'+
      '<button class="tbtn" type="button" data-act="down"'+(k===n-1?' disabled':'')+'>▼ 往後</button>'+
      '<button class="tbtn" type="button" data-act="reset" title="把三個自動帶入的欄位換回原文">重新帶入</button>'+
      '<button class="tbtn del" type="button" data-act="del">不挑了</button></span></div>';
    h+='<div class="rub" title="評審會看的四個地方，寫得具體就會打勾">'+rubH(p)+'</div>';
    h+=fieldH('qt','我的原始提問（Prompt）',true,p.qt,LIM.qt,'自動帶入你當時說的話。太長就留下重點，可以自己刪減。');
    h+='<div class="pf"><div class="lb"><span>教育型 AI 的回答摘要</span><span class="au">自動帶入</span><span class="ct" data-ct="at"></span></div>'+
      '<textarea class="px auto" data-f="at" maxlength="'+LIM.at+'" rows="3">'+esc(p.at)+'</textarea></div>';
    h+='<div class="pf"><div class="lb"><span>我的發現與修正</span><span class="au me">我自己寫</span><span class="ct" data-ct="issNote"></span></div>'+
      '<div class="mini">這一輪我主要是…（發現問題、修正、追問、補充，都可以得分）</div><div class="opts">'+FK.map(function(d){return '<label class="opt"><input type="radio" name="fk'+k+'" data-fk="'+d[0]+'"'+(p.fk===d[0]?' checked':'')+'>'+esc(d[1])+'</label>';}).join('')+'</div>'+
      '<textarea class="px" data-f="issNote" maxlength="'+LIM.issNote+'" rows="2" style="margin-top:6px" placeholder="是哪一句、哪個字或哪個想法？為什麼這樣做？我怎麼確認或決定的？（至少 '+ISS_MIN+' 個字）">'+esc(p.issNote)+'</textarea>'+
      guideH(op,'批判檢視、提問策略與人工修正（佔 30%，同分時先比這項）。不一定要「找到錯」，四種都算：',
        ['<b>發現問題</b>：哪一句、哪個字、哪個說法有問題？為什麼？你怎麼確認的（查課本或網站、問家人、重讀）？','<b>我修正了</b>：改了哪裡？改之前和改之後差在哪？為什麼這樣更像我？','<b>我追問了</b>：你想知道什麼？為什麼追問？追問之後 e度 的回答有什麼不一樣？','<b>我補充了</b>：補了哪個只有你才有的細節？為什麼要補？'],
        '都沒發現問題也要寫：我是怎麼檢查的、為什麼確定沒問題。只寫「很好」「沒有錯誤」，評審看不出你的想法。')+'</div>';
    h+=fieldH('ft','我的追問／修正指令',true,p.ft,LIM.ft,r.f?'自動帶入你接著說的那句話。':'');
    if(!r.f)h+='<div class="pnote">這一輪後面你沒有再問 e度。評審很看重追問和修正；可以換一輪挑，或在上面寫你後來怎麼改。</div>';
    h+=guideH(op,'提問策略與人工修正（各佔 30% 的一部分）：你有沒有根據自己的發現，繼續把結果問得更好、改得更像你。',
      ['有沒有說出<b>哪裡要改</b>、<b>要它怎麼做</b>？','有沒有<b>限制它</b>（只給建議、不要幫我寫、請說明理由）？','追問之後，結果有沒有變得更像我家？'],
      '追問只有「好」「謝謝」，評審看不到策略；可以換一輪挑，或自己補寫你後來怎麼改。');
    h+='<div class="pf final"><div class="lb"><span>最終採用的理由</span><span class="au me">我自己寫</span></div>'+
      '<div class="mini">① 這一輪的結果，我…</div><div class="opts">'+DEC.map(function(d){return '<label class="opt"><input type="radio" name="dec'+k+'" data-dec="'+d[0]+'"'+(p.dec===d[0]?' checked':'')+'>'+esc(d[1])+'</label>';}).join('')+'</div>'+
      '<div class="mini">② 原因（可複選）</div><div class="opts">'+WHY.map(function(x,j){return '<label class="opt"><input type="checkbox" data-why="'+j+'"'+(p.why.indexOf(x)>=0?' checked':'')+'>'+esc(x)+'</label>';}).join('')+'</div>'+
      '<div class="mini">③ 用你自己的話補一句：到底是哪個字、哪句話、為什麼？（至少 '+MINE_MIN+' 個字）<span class="ct" data-ct="mine" style="float:right;font-weight:500"></span></div>'+
      '<textarea class="px" data-f="mine" maxlength="'+LIM.mine+'" rows="2" placeholder="我把哪一句留下來或刪掉，因為……">'+esc(p.mine)+'</textarea>'+
      guideH(op,'人工修正、創意與生活連結（各 30%）、數位倫理與權責揭露（20%）。',
        ['<b>留下或不用哪一部分</b>，為什麼？','這一句為什麼<b>像我家</b>？連到哪一件真實的事？','這一部分最後是<b>誰做的</b>：AI 給的（紅）、我改的（藍）、我自己想的（黑）？'],
        '只寫「因為很好」「因為通順」，評審看不到你的判斷。')+'</div>';
    return h+'</div>';
  }
  function fieldH(f,label,auto,val,max,hint){
    return '<div class="pf"><div class="lb"><span>'+label+'</span>'+(auto?'<span class="au">自動帶入</span>':'')+'<span class="ct" data-ct="'+f+'"></span></div>'+
      '<textarea class="px'+(auto?' auto':'')+'" data-f="'+f+'" maxlength="'+max+'" rows="2">'+esc(val)+'</textarea>'+(hint?'<div class="hintx">'+esc(hint)+'</div>':'')+'</div>';
  }
  function renderPicks(){
    var h=$('hPicks');
    h.innerHTML=S.picks.length?S.picks.map(pickCardHTML).join(''):'<div class="hempty">還沒有挑任何一輪。回到上面的對話，在你說的話下面按「挑這一輪」，挑 4～5 輪最有代表性的。</div>';
    renderMyPk();updCounts();
  }
  function updCounts(){
    Array.prototype.forEach.call(document.querySelectorAll('#hPicks .pcard'),function(card){
      var p=S.picks[Number(card.dataset.i)];if(!p)return;
      Array.prototype.forEach.call(card.querySelectorAll('[data-ct]'),function(c){
        var f=c.dataset.ct,max=LIM[f],len=(p[f]||'').length;c.textContent=len+'／'+max;c.classList.toggle('over',len>=max);
      });
    });
  }
  function refreshMeta(){
    var done=S.picks.filter(isDone).length,n=S.picks.length;
    Array.prototype.forEach.call(document.querySelectorAll('#hPicks .pcard'),function(card){var pp=S.picks[Number(card.dataset.i)];card.classList.toggle('done',isDone(pp));var rb=card.querySelector('.rub');if(rb)rb.innerHTML=rubH(pp);});
    renderMyPk();
    var pr=$('hProg');
    pr.textContent='已挑 '+n+'／'+MAXP+' 輪，寫好理由 '+done+' 輪（至少要 '+MINP+' 輪寫好）';
    pr.className='hprog'+(done>=MINP?' good':'');
    clearTimeout(refreshMeta._t);refreshMeta._t=setTimeout(updPages,250);
    var ok=n>=MINP&&done>=MINP;
    setHidden('hOk',ok?'1':'');
    setHidden('hCnt',n?(n+' 輪（寫好理由 '+done+' 輪）'):'');
    $('hSheetBtn').disabled=!n;
  }
  function updPages(){
    var items=S.picks.filter(isDone).map(function(p){return {p:p};}),el=$('hPages');
    if(!items.length){el.textContent='';return;}
    var tmp=document.createElement('div');tmp.style.cssText='position:absolute;left:-9999px;top:0;visibility:hidden';
    var sh=sheetEl(items,{});tmp.appendChild(sh);document.body.appendChild(tmp);
    var n=pagesOf(sh);document.body.removeChild(tmp);
    el.textContent='排版後約 '+n+' 頁（上限 2 頁）'+(n>2?'：太長了，請把文字縮短或少挑一輪':'');
    el.className='hprog'+(n>2?'':' good');if(n>2)el.style.color='var(--red)';else el.style.color='';
  }
  function saveSoon(){
    clearTimeout(S.saveT);statEl.textContent='修改中…';
    S.saveT=setTimeout(saveNow,900);
  }
  function saveNow(){
    if(!S.id||!S.fb)return;
    var picks=S.picks.map(cleanPick),at=Date.now(),id=S.id;
    writeLocal(id,{picks:picks,at:at});
    statEl.textContent='存檔中…';
    ensureAuth(S.fb).then(function(){return S.fb.db.collection(AIH).doc(id).update({picks:picks,picksAt:at});})
      .then(function(){var d=new Date();statEl.textContent='已存到雲端 '+d.getHours()+':'+('0'+d.getMinutes()).slice(-2);})
      .catch(function(e){console.warn('picks 存檔失敗',e);statEl.textContent='雲端沒存到，先存在這台電腦';});
  }

  // 事件：整個步驟用委派
  root.addEventListener('click',function(e){
    var t=e.target.closest('[data-pick],[data-jump],[data-gopick],[data-act]');if(!t)return;
    if(t.dataset.jump){flash($('hChat'),t.dataset.jump);return;}
    if(t.dataset.gopick!=null){var c=$('pk'+t.dataset.gopick);if(c)c.scrollIntoView({behavior:'smooth',block:'start'});return;}
    if(t.dataset.pick){
      var id=t.dataset.pick,k=S.picks.findIndex(function(p){return p.q===id;});
      if(k>=0){S.picks.splice(k,1);toast('已取消這一輪');}
      else{
        if(S.picks.length>=MAXP){toast('最多挑 '+MAXP+' 輪。先在下面「不挑了」一輪再挑。');return;}
        S.picks.push(newPick(S.ix,id));toast('已挑為第 '+S.picks.length+' 輪，往下捲到「我挑的對話」寫理由');
      }
      renderChat();renderPicks();refreshMeta();saveSoon();return;
    }
    var card=t.closest('.pcard'),i=card?Number(card.dataset.i):-1,a=t.dataset.act;
    if(i<0)return;
    if(a==='view'){flash($('hChat'),S.picks[i].q);return;}
    if(a==='up'||a==='down'){var j=a==='up'?i-1:i+1;if(j<0||j>=S.picks.length)return;var x=S.picks[i];S.picks[i]=S.picks[j];S.picks[j]=x;renderChat();renderPicks();refreshMeta();saveSoon();
      var nc=$('pk'+j);if(nc)nc.scrollIntoView({block:'center'});return;}
    if(a==='reset'){if(confirm('把「原始提問、回答摘要、追問」換回自動帶入的原文？你改過的字會不見。')){autoFill(S.ix,S.picks[i]);renderPicks();refreshMeta();saveSoon();}return;}
    if(a==='del'){if(confirm('不挑這一輪了？你在這一輪寫的理由會不見。')){S.picks.splice(i,1);renderChat();renderPicks();refreshMeta();saveSoon();}return;}
  });
  root.addEventListener('input',function(e){
    var card=e.target.closest('.pcard');if(!card)return;
    var p=S.picks[Number(card.dataset.i)],f=e.target.dataset.f;
    if(!p)return;
    if(f){p[f]=e.target.value;}
    else if(e.target.dataset.dec){p.dec=e.target.dataset.dec;}
    else if(e.target.dataset.fk){p.fk=e.target.dataset.fk;}
    else if(e.target.dataset.why!=null){var w=WHY[Number(e.target.dataset.why)];p.why=p.why.filter(function(x){return x!==w;});if(e.target.checked)p.why.push(w);}
    else return;
    updCounts();refreshMeta();saveSoon();
  });

  /* ---------- 第 5 步：依對話給的提醒、手冊連結、自動儲存 ---------- */
  var HBIDX={};
  (function(){var pdf={'第一章':14,'第二章':22,'第三章':34,'第四章':47,'第五章':52,'第六章':65},list=(window.PAGE&&window.PAGE.hb)||[];
    Object.keys(pdf).forEach(function(k){for(var i=0;i<list.length;i++)if(list[i][0]===pdf[k])HBIDX[k]=i;});})();
  var CHN={'第一章':'壹 AI 是什麼？','第二章':'貳 怎麼和 AI 溝通？','第三章':'參 AI 小任務','第四章':'肆 AI 說的一定對嗎？','第五章':'伍 AI 幫助我學習','第六章':'陸 AI 時代的好公民'};
  var MODEUSE={'一般模式':'一般模式（問答、查事實）','文思精靈':'文思精靈（想細節、帶著寫）','寫作精靈':'寫作精靈（給修改建議）','繪圖精靈':'繪圖精靈（畫圖）'};
  function links(ids){return (ids||[]).slice(0,3).map(function(id){var o=S.ix&&S.ix.by[id];return o?'<button type="button" class="gl" data-gojump="'+id+'">看那段對話 '+esc(fmtT(o.m.t))+'</button>':'';}).join('');}
  function gitem(it){return '<div class="gi">'+esc(nb(it.why))+links(it.ids)+'</div>';}
  function renderGuide(){
    var g=(S.doc&&S.doc.guide)||{};
    Array.prototype.forEach.call(document.querySelectorAll('[data-guide]'),function(b){
      var k=b.dataset.guide,v=g[k],items=!v?[]:(Array.isArray(v)?v:[v]);
      b.hidden=!items.length;
      b.innerHTML=items.length?'<div class="gh">★ 老師根據你的對話提醒</div>'+items.map(gitem).join(''):'';
    });
    var rec={};(g.chapters||[]).forEach(function(c){rec[c.ch]=c;});
    Array.prototype.forEach.call(document.querySelectorAll('.chap'),function(el){
      var c=rec[el.dataset.ch],b=el.querySelector('[data-guide-ch]');
      el.classList.toggle('rec',!!c);b.hidden=!c;b.innerHTML=c?gitem(c):'';
    });
    var sum=$('gChapSum');
    if(!S.doc){sum.hidden=false;sum.innerHTML='<div class="gh">填好最上面的年級、班級、座號後，這裡會出現依你的對話整理的提醒。</div>';}
    else if(!(g.chapters||[]).length){sum.hidden=true;}
    else{sum.hidden=false;sum.innerHTML='<div class="gh">★ 老師看了你的對話，適合寫這幾章（下面有 ★ 標記）</div><div class="gi">'+g.chapters.map(function(c){return esc(CHN[c.ch]||c.ch);}).join('、')+'</div>';}
    var mo=$('gModes'),m=(S.doc&&S.doc.modes)||{},ks=Object.keys(m).sort(function(a,b){return m[b]-m[a];});
    if(ks.length){mo.hidden=false;mo.innerHTML='<div class="gh">★ 你的 e度 對話紀錄顯示，你用過這些模式（可寫進「你在哪些地方使用到 e度」）</div><div class="gi">'+ks.map(function(k){return esc(MODEUSE[k]||k)+' '+m[k]+' 次';}).join('、')+'</div>';}
    else mo.hidden=true;
  }
  document.addEventListener('click',function(e){
    var j=e.target.closest('[data-gojump]'),h=e.target.closest('[data-hb]');
    if(j){var id=j.dataset.gojump;window.cardShowStep(4);setTimeout(function(){flash($('hChat'),id);},350);}
    else if(h){var i=HBIDX[h.dataset.hb];if(i!=null&&window.openHandbook)window.openHandbook(i);}
  });
  // 每 8 秒自動儲存（打字後 1 秒多也會先存一次）
  (function(){
    var man=$('manual'),touched=false,st=$('autoStat');
    if(!man)return;
    function mark(){touched=true;}
    man.addEventListener('input',mark);man.addEventListener('change',mark);
    function tick(){
      if(!touched||!window.cardSave)return;
      touched=false;window.cardRefresh();
      window.cardSave().then(function(r){
        var d=new Date(),t=d.getHours()+':'+('0'+d.getMinutes()).slice(-2)+':'+('0'+d.getSeconds()).slice(-2);
        if(r==='cloud'){st.className='chip ok';st.textContent='已自動儲存 '+t;}
        else if(r==='local'){st.className='chip bad';st.textContent='只存在這台電腦，請檢查網路';}
        else{st.className='chip bad';st.textContent='儲存失敗，請填好年級、班級、座號';}
      });
    }
    setInterval(tick,8000);
    document.addEventListener('visibilitychange',function(){if(document.hidden)tick();});
  })();
  $('hReload').addEventListener('click',function(){loadStudent(true);});
  $('hSheetBtn').addEventListener('click',function(){
    var items=S.picks.filter(isDone).map(function(p){return {p:p,mode:(S.doc.sessions[S.ix.by[p.q].si]||{}).mode};});
    if(!items.length){toast('先把至少一輪的理由寫好，才排得出歷程紀錄');return;}
    var all=S.picks.length,skipped=all-items.length;
    showSheets([{items:items}],'AI協作歷程紀錄_'+S.id);
    if(skipped)toast('有 '+skipped+' 輪還沒寫好理由，預覽裡先不放');
  });
  ['idG','idC','idS'].forEach(function(id){var el=$(id);if(el)el.addEventListener('input',function(){clearTimeout(loadStudent._t);loadStudent._t=setTimeout(function(){loadStudent();},500);});});
  if($('loadBtn'))$('loadBtn').addEventListener('click',function(){setTimeout(function(){loadStudent(true);},50);});
  document.addEventListener('visibilitychange',function(){if(document.hidden&&S.saveT){clearTimeout(S.saveT);S.saveT=null;saveNow();}});
  window.addEventListener('pagehide',function(){if(S.saveT){clearTimeout(S.saveT);S.saveT=null;saveNow();}});
  setTimeout(function(){loadStudent();},400);

  /* ============================================================
     老師端（?admin）
     ============================================================ */
  if(/[?&]admin(=|&|$)/.test(location.search)){
    document.body.classList.add('adm');
    var A={fb:null,docs:{},cur:'',ix:null};
    var aStat=$('hAdStat'),aTable=$('hAdTable'),aDet=$('hAdDetail');
    function aMsg(t){aStat.textContent=t;}
    function pageEst(d){
      var items=(d.picks||[]).filter(isDone).map(function(p){return {p:p};});
      if(!items.length)return '';
      var tmp=document.createElement('div');tmp.style.cssText='position:absolute;left:-9999px;top:0;visibility:hidden';
      var s=sheetEl(items,{});tmp.appendChild(s);document.body.appendChild(tmp);
      var n=pagesOf(s);document.body.removeChild(tmp);return n;
    }
    function aList(){
      var ids=Object.keys(A.docs).sort(function(a,b){var x=a.split('-'),y=b.split('-');return x[0]-y[0]||x[1]-y[1]||x[2]-y[2];});
      var h='<tr><th>年-班-座</th><th>對話</th><th>老師標記</th><th>學生挑了</th><th>理由寫好</th><th>預估頁數</th><th></th></tr>';
      ids.forEach(function(id){
        var d=A.docs[id],ix=indexDoc(d),n=ix.flat.filter(function(o){return o.m.r==='u'&&!o.m.g;}).length,pk=d.picks||[],dn=pk.filter(isDone).length,pg=pageEst(d);
        h+='<tr><td>'+id+'</td><td>學生 '+n+' 則・'+(d.sessions||[]).length+' 場</td><td>'+(d.marks||[]).length+'</td><td>'+pk.length+'</td><td>'+dn+'</td><td'+(pg>2?' style="color:#c0392b;font-weight:900"':'')+'>'+(pg||'—')+'</td><td><button class="btn ghost" style="padding:2px 12px;font-size:13.5px" type="button" data-sel="'+id+'">檢視／標記／列印</button></td></tr>';
      });
      aTable.innerHTML=h;
      aMsg('共 '+ids.length+' 位學生');
    }
    function aLoad(){
      window.cardFirebase().then(function(fb){
        if(!fb){aMsg('還沒設定 Firebase（FB_CONFIG 是 null）。');return;}
        A.fb=fb;
        var u=fb.auth.currentUser;
        var p=(u&&u.email===TEACHER)?Promise.resolve(u):fb.auth.signInWithPopup(new firebase.auth.GoogleAuthProvider()).then(function(c){return c.user;});
        return p.then(function(user){
          if(user.email!==TEACHER){aMsg('這個帳號（'+user.email+'）不是老師帳號。');return;}
          aMsg('讀取中…');
          return fb.db.collection(AIH).get().then(function(snap){
            A.docs={};snap.docs.forEach(function(d){A.docs[d.id]=d.data();});
            aList();if(A.cur&&A.docs[A.cur])aDetail(A.cur);
          });
        });
      }).catch(function(e){console.warn(e);aMsg('讀取失敗：'+(e.code||e.message));});
    }
    function aDetail(id){
      A.cur=id;var d=A.docs[id];A.ix=indexDoc(d);
      var pk=d.picks||[];
      var h='<div class="card"><h3><svg class="ico"><use href="#i-users"/></svg>'+id+'　學生挑了 '+pk.length+' 輪</h3>';
      h+='<p class="small muted">① 在下面的對話裡替老師認為「值得寫」的地方按「★ 標記」，學生會在右邊看到跳轉按鈕。② 學生挑好的對話在最下面，可預覽、列印成 PDF（每人最多 2 頁）。</p>';
      h+='<div class="adbox" id="hAdChat">'+chatHTML(d,A.ix,{admin:true,picks:pk})+'</div>';
      h+='<h3 style="margin-top:6px"><svg class="ico"><use href="#i-file"/></svg>學生挑的對話（依優先順序）</h3>';
      if(!pk.length)h+='<div class="hempty">這位同學還沒有挑。</div>';
      else{
        h+='<div class="incl" id="hAdIncl">'+pk.map(function(p,k){
          var t=roundText(p);
          return '<label><input type="checkbox" data-inc="'+k+'"'+(isDone(p)?' checked':'')+'><span><b>優先 '+(k+1)+(isDone(p)?'':'（理由還沒寫好）')+'</b>　'+esc(clip(t.q,40))+'<br><small>理由：'+esc(clip(t.why,60)||'（空白）')+'</small></span></label>';
        }).join('')+'</div>';
        h+='<div class="hbar"><button class="btn" type="button" id="hAdPrev"><svg class="ico"><use href="#i-eye"/></svg>預覽／列印這位的歷程紀錄</button><button class="btn ghost" type="button" id="hAdAll">一次列印全部學生（每人另起一頁）</button></div>';
      }
      aDet.innerHTML=h+'</div>';
      aDet.scrollIntoView({behavior:'smooth',block:'start'});
      if(pk.length){
        $('hAdPrev').onclick=function(){aPreview(id);};
        $('hAdAll').onclick=function(){aPreviewAll();};
      }
    }
    function modeOf(d,ix,p){var o=ix.by[p.q];return o?((d.sessions[o.si]||{}).mode||''):'';}
    function aPreview(id){
      var d=A.docs[id],ix=indexDoc(d),chosen={},useId=false;
      Array.prototype.forEach.call(document.querySelectorAll('#hAdIncl input'),function(c){chosen[c.dataset.inc]=c.checked;});
      function draw(){
        var items=(d.picks||[]).filter(function(p,k){return chosen[k];}).map(function(p){return {p:p,mode:modeOf(d,ix,p)};});
        var opt='<label><input type="checkbox" id="shId"'+(useId?' checked':'')+'> 角落加上編號（'+id+'，核對用；送件版不要勾）</label>';
        showSheets([{items:items,idLabel:useId?id:''}],'AI協作歷程紀錄_'+id,opt,function(){useId=$('shId').checked;draw();});
      }
      draw();
    }
    function aPreviewAll(){
      var ids=Object.keys(A.docs).filter(function(id){return (A.docs[id].picks||[]).some(isDone);}).sort();
      var sheets=ids.map(function(id){var d=A.docs[id],ix=indexDoc(d);return {items:(d.picks||[]).filter(isDone).map(function(p){return {p:p,mode:modeOf(d,ix,p)};}),idLabel:''};});
      if(!sheets.length){toast('還沒有人寫好理由');return;}
      showSheets(sheets,'AI協作歷程紀錄_全部','<span>共 '+sheets.length+' 位：'+ids.join('、')+'（每位從新的一頁開始；列印時選頁碼範圍就能分開存）</span>');
    }
    // 標記
    aDet.addEventListener('click',function(e){
      var b=e.target.closest('[data-mk],[data-mksave],[data-mkdel],[data-mkcancel]');if(!b)return;
      var d=A.docs[A.cur];
      if(b.dataset.mk){
        var id=b.dataset.mk,old=A.ix.marks[id]||{},msgEl=aDet.querySelector('[data-mid="'+id+'"] .bw');
        var ex=aDet.querySelector('.mkform');if(ex)ex.remove();
        var f=document.createElement('div');f.className='mkform';f.dataset.for=id;
        f.innerHTML='<div class="row"><select id="mkK">'+Object.keys(KIND).map(function(k){return '<option value="'+k+'"'+(old.kind===k?' selected':'')+'>'+KIND[k]+'</option>';}).join('')+'</select><input class="l1" id="mkL" maxlength="30" placeholder="按鈕上的字（例如：AI 想畫白天，我更正成晚上）" value="'+esc(old.label||'')+'"></div><div class="row"><input class="l2" id="mkN" maxlength="80" placeholder="為什麼值得寫（一句話，學生看得到）" value="'+esc(old.note||'')+'"></div><div class="row"><button class="btn" type="button" data-mksave="'+id+'">存標記</button>'+(old.id?'<button class="btn ghost" type="button" data-mkdel="'+id+'">拿掉標記</button>':'')+'<button class="btn ghost" type="button" data-mkcancel="1">取消</button></div>';
        msgEl.appendChild(f);$('mkL').focus();return;
      }
      if(b.dataset.mkcancel){var x=aDet.querySelector('.mkform');if(x)x.remove();return;}
      var marks=(d.marks||[]).slice();
      if(b.dataset.mksave){
        var lab=$('mkL').value.trim();if(!lab){toast('按鈕上的字不能空白');return;}
        var mk={id:b.dataset.mksave,kind:$('mkK').value,label:lab,note:$('mkN').value.trim()};
        var k=marks.findIndex(function(m){return m.id===mk.id;});if(k>=0)marks[k]=mk;else marks.push(mk);
      }else if(b.dataset.mkdel){marks=marks.filter(function(m){return m.id!==b.dataset.mkdel;});}
      A.fb.db.collection(AIH).doc(A.cur).update({marks:marks,marksEdited:true}).then(function(){
        d.marks=marks;d.marksEdited=true;toast('標記已存好');aDetail(A.cur);aList();
      }).catch(function(er){console.warn(er);toast('存標記失敗：'+(er.code||er.message));});
    });
    aTable.addEventListener('click',function(e){var b=e.target.closest('[data-sel]');if(b)aDetail(b.dataset.sel);});
    $('hAdLogin').onclick=aLoad;$('hAdReload').onclick=aLoad;
    $('hAdManual').onclick=function(){
      if(!A.fb){aMsg('請先按「老師登入並讀取」。');return;}
      A.fb.db.collection('cardWork').get().then(function(snap){
        var out={};
        snap.docs.forEach(function(d){var x=d.data();out[d.id]={title:(x.L1&&x.L1.title)||'',manual:x.L4||{}};});
        var blob=new Blob([JSON.stringify({exportedAt:new Date().toISOString(),students:out})],{type:'application/json'});
        var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='manual.json';document.body.appendChild(a);a.click();a.remove();
        aMsg('已匯出 '+Object.keys(out).length+' 位的說明書資料（manual.json），拿去跑「產生說明書.py」。');
      }).catch(function(er){aMsg('匯出失敗：'+(er.code||er.message));});
    };
    // 匯入
    $('hAdFile').addEventListener('change',function(){
      var f=this.files[0];this.value='';if(!f)return;
      if(!A.fb){aMsg('請先按「老師登入並讀取」。');return;}
      var rd=new FileReader();
      rd.onload=function(){
        var j;try{j=JSON.parse(rd.result);}catch(er){aMsg('這不是正確的 aiHistory.json');return;}
        var ids=Object.keys(j.students||{});
        if(!ids.length){aMsg('檔案裡沒有學生');return;}
        var over=$('hAdOver').checked;
        if(!confirm('要把這 '+ids.length+' 位的對話寫進雲端嗎？\n'+ids.join('、')+'\n\n學生已經挑好的內容不會被動到。'+(over?'\n（網頁上改過的標記會被檔案裡的標記覆蓋）':'\n（網頁上改過的標記會保留）')))return;
        aMsg('寫入中…');
        var chain=Promise.resolve(),okN=0;
        ids.forEach(function(id){
          chain=chain.then(function(){
            var s=j.students[id],body={grade:s.grade,className:s.className,studentId:s.studentId,sessions:s.sessions,importedAt:Date.now()};
            var cur=A.docs[id];
            if(over||!(cur&&cur.marksEdited)){body.marks=s.marks||[];if(over)body.marksEdited=false;}
            return A.fb.db.collection(AIH).doc(id).set(body,{merge:true}).then(function(){okN++;aMsg('寫入中… '+okN+'／'+ids.length);});
          });
        });
        chain.then(function(){aMsg('已寫入 '+okN+' 位學生。');aLoad();}).catch(function(er){console.warn(er);aMsg('寫入失敗：'+(er.code||er.message)+'（已完成 '+okN+' 位）');});
      };
      rd.readAsText(f,'utf-8');
    });
  }
})();
