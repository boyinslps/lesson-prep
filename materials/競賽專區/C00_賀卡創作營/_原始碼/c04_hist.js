/* ============================================================
   第 4 節｜我的對話紀錄（學生）＋ 老師管理（網址後面加 ?admin）＋ 歷程紀錄排版
   ------------------------------------------------------------
   資料：aiHistory/{年級-班級-座號}（見 firestore.rules）
     老師匯入：sessions（對話，整理對話紀錄.py 產生）、marks（老師標記）
     學生寫回：picks（挑的 4～5 輪）、picksAt
   一輪＝學生在第 4 步用手點選的一串訊息（不限一問一答，學生的話和 e度 的話都能選，可多則）。
     pick = {ids:[訊息 id，依對話順序], issNote:我發現的問題與怎麼追問修正, why:最終採用的理由, ts}
     第 4 步只負責選＋保存；第 5 步用對話畫面讀回那一串，下面只有兩格要自己寫的文字（沒有選項、沒有勾選）。
     舊格式 {q,a,f,...} 讀進來時自動轉成 ids［q,a,f］。
   ============================================================ */
(function(){
  if(!document.getElementById('hBody'))return;
  var AIH='aiHistory',MAXP=5,MINP=4,TEACHER='boyin0304@slps.tn.edu.tw';
  var LIM={issNote:140,why:140,q:160,f:120,a:110},MINE_MIN=6,ISS_MIN=6;
  var KIND={ask:'提問策略',check:'發現問題',fix:'追問修正'};
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
  // 一輪（pick）：ids 依對話順序排好；舊格式 {q,a,f} 轉成 ids。有 ix 時順便丟掉對話裡已經不存在的訊息。
  function cleanPick(p,ix){
    var ids=Array.isArray(p.ids)?p.ids:[p.q,p.a,p.f];
    ids=ids.filter(Boolean).map(String);
    if(ix){ids=ids.filter(function(id,k){return ix.by[id]&&ids.indexOf(id)===k;}).sort(function(x,y){return ix.by[x].i-ix.by[y].i;});}
    return {ids:ids,issNote:nb(p.issNote).slice(0,LIM.issNote),why:nb(typeof p.why==='string'?p.why:p.mine).slice(0,LIM.why),ts:Number(p.ts)||0};
  }
  function picksOf(doc,ix,raw){return (raw||doc.picks||[]).map(function(p){return cleanPick(p,ix);}).filter(function(p){return p.ids.length;});}
  function roleCount(ix,p,r){return p.ids.filter(function(id){var o=ix.by[id];return o&&!o.m.g&&o.m.r===r;}).length;}
  function chainOk(ix,p){return roleCount(ix,p,'u')>=1&&roleCount(ix,p,'a')>=1;}
  function isDone(p,ix){return chainOk(ix,p)&&(p.issNote||'').trim().length>=ISS_MIN&&(p.why||'').trim().length>=MINE_MIN;}
  function fmtT(t){return String(t||'').replace('-','/');}
  function sessHead(se){
    var d=se.date?new Date(se.date+'T00:00:00'):null,w=d&&!isNaN(d)?'（'+DAYS[d.getDay()]+'）':'';
    var md=se.date?Number(se.date.slice(5,7))+'/'+Number(se.date.slice(8,10)):'';
    return md+w+'<span class="md">'+esc(se.mode||'')+'</span>';
  }

  /* ---------- 對話畫面（學生與老師共用）---------- */
  // o: {admin, picks（已 cleanPick）, sel（正在選的訊息 id 陣列）, pickable（學生第 4 步：點訊息就選／取消）}
  function chatHTML(doc,ix,o){
    var role={},sel={};
    (o.picks||[]).forEach(function(p,k){p.ids.forEach(function(id){role[id]=k+1;});});
    (o.sel||[]).forEach(function(id){sel[id]=1;});
    var h='';
    (doc.sessions||[]).forEach(function(se){
      h+='<div class="sess">'+sessHead(se)+'</div>';
      (se.msgs||[]).forEach(function(m){
        var mk=ix.marks[m.id],rl=role[m.id],on=!!sel[m.id],pk=o.pickable&&!m.g;
        h+='<div class="msg '+m.r+(m.g?' g':'')+(rl?' pk':'')+(on?' sel':'')+(pk?' pickable':'')+'" data-mid="'+m.id+'">';
        h+='<div class="av">'+(m.r==='u'?'我':'e度')+'</div><div class="bw">';
        if(mk)h+='<div class="mk k-'+esc(mk.kind||'')+'"><b>★ '+esc(KIND[mk.kind]||'老師推薦')+'</b><span>'+esc(nb(mk.label))+'</span>'+(mk.note?'<span class="ex">'+esc(nb(mk.note))+'</span>':'')+'</div>';
        if(rl)h+='<span class="rb">已存入第 '+rl+' 輪</span>';
        h+='<div class="bub"'+(pk?' data-sel="'+m.id+'" role="button" tabindex="0" aria-pressed="'+on+'" title="點一下選取／取消"':'')+'>'+(pk?'<span class="ck" aria-hidden="true"><svg class="ico"><use href="#i-check"/></svg></span>':'')+'<div class="tx">'+esc(m.g?'e度 打招呼':nb(m.x))+'</div>'+(m.g?'':'<div class="tm">'+esc(fmtT(m.t))+'</div>')+'</div>';
        if(!m.g&&o.admin)h+='<div class="act"><button class="pbtn mkb" type="button" data-mk="'+m.id+'">'+(mk?'編輯標記':'★ 標記')+'</button></div>';
        h+='</div></div>';
      });
    });
    return h||'<div class="hempty">這位同學還沒有對話紀錄。</div>';
  }
  // 唯讀：把一輪的訊息用對話畫面讀回來（第 5 步）；中間沒選的地方用「⋯」隔開
  function chainHTML(doc,ix,p){
    var h='',last=-2,lastSi=-1;
    p.ids.forEach(function(id){
      var o=ix.by[id],m=o.m;
      if(o.si!==lastSi){h+='<div class="sess">'+sessHead(doc.sessions[o.si])+'</div>';lastSi=o.si;}
      else if(o.i-last>1)h+='<div class="gapm">⋯ 中間的話沒有選 ⋯</div>';
      last=o.i;
      h+='<div class="msg '+m.r+'"><div class="av">'+(m.r==='u'?'我':'e度')+'</div><div class="bw"><div class="bub"><div class="tx">'+esc(nb(m.x))+'</div><div class="tm">'+esc(fmtT(m.t))+'</div></div></div></div>';
    });
    return h;
  }
  function flash(root,id){
    var el=root.querySelector('[data-mid="'+id+'"]');if(!el)return;
    el.scrollIntoView({behavior:'smooth',block:'center'});
    el.classList.remove('flash');void el.offsetWidth;el.classList.add('flash');
    setTimeout(function(){el.classList.remove('flash');},1900);
  }

  /* ---------- 歷程紀錄的文字（學生編輯 → 排版）---------- */
  // 一輪排成比賽格式的四列：第一句學生的話＝原始提問、e度 的話＝回答摘要（每則縮短）、之後學生的話＝追問／修正；發現與理由是學生自己寫的
  function roundText(p,ix){
    var u=[],a=[];
    p.ids.forEach(function(id){var o=ix.by[id];if(!o||o.m.g)return;(o.m.r==='u'?u:a).push(o.m.x);});
    function cap(arr,lim){   // 訊息很多時只留第一則和最後一則，中間用省略號（2 頁放不下）
      if(arr.length<=2)return arr.map(function(x){return clip(x,lim);}).join('\n');
      return clip(arr[0],lim)+'\n⋯（中間還有 '+(arr.length-2)+' 則）\n'+clip(arr[arr.length-1],lim);
    }
    return {q:u.length?clip(u[0],LIM.q):'（這一輪沒有選到自己的話）',
      a:cap(a,LIM.a),fd:nb(p.issNote).trim(),fl:'我發現的問題與修正',
      f:cap(u.slice(1),LIM.f)||'（這一輪沒有追問）',why:nb(p.why).trim()};
  }
  function rowH(l,v,extra){return '<div class="rr"><div class="l">'+l+'</div><div class="v">'+v+(extra||'')+'</div></div>';}
  function sheetEl(items,o){
    // items: [{p, ix, mode}]
    var s=document.createElement('div');s.className='sheet'+(o&&o.brk?' brk':'');
    var h='<h1>教育型 AI 協作歷程紀錄</h1><div class="sub">摘錄與教育型 AI（e度）最具代表性的人機對話，共 '+items.length+' 輪，依重要程度排序</div>';
    items.forEach(function(it,k){
      var t=roundText(it.p,it.ix);
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
  var S={id:'',doc:null,ix:null,picks:[],items:[],view:0,cur:0,loadedFor:'',fb:null,saveT:null};
  var root=$('hBody'),lockEl=$('hLock'),statEl=$('hStat'),wroot=$('wBody'),wlock=$('wLock');
  function lock(msg,kind){
    S.doc=null;S.ix=null;S.picks=[];S.items=[];if(typeof renderGuide==='function')renderGuide();
    root.hidden=true;wroot.hidden=true;
    var h='<svg class="ico"><use href="#'+(kind==='bad'?'i-alert':'i-lock')+'"/></svg><span>'+esc(msg)+'</span>';
    [lockEl,wlock].forEach(function(e){e.hidden=false;e.innerHTML=h;});
  }
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
        S.picks=picksOf(S.doc,S.ix,use.picks).slice(0,MAXP);S.view=0;S.cur=firstUndone();
        lockEl.hidden=true;wlock.hidden=true;root.hidden=false;wroot.hidden=false;
        renderAll();
        statEl.textContent=loc.at>cloud.at?'用的是這台電腦上較新的存檔':'已讀取';
      });
    }).catch(function(e){console.warn('讀取對話紀錄失敗',e);if(S.loadedFor===id)lock('讀取失敗（'+(e.code||e.message||'網路')+'）。再按一次「讀取學習單」，還是不行就告訴老師。','bad');});
  }

  function renderAll(){buildItems();renderView();renderMyList();renderWrite();refreshMeta();renderGuide();}

  /* ---------- 第 4 步：老師預選的輪次，左右切換著看，勾「選這則」送去寫理由 ---------- */
  function candKey(ids){return ids.join('|');}
  // 要看的輪次 = 老師預選（doc.cands）＋學生之前自己挑、但不在預選裡的（保留，可取消）
  function buildItems(){
    var items=[],seen={};
    (S.doc.cands||[]).forEach(function(c){
      var p=cleanPick({ids:c.ids},S.ix);if(!chainOk(S.ix,p))return;
      var k=candKey(p.ids);if(seen[k])return;seen[k]=1;
      items.push({ids:p.ids,hint:nb(c.hint||''),extra:false});
    });
    S.picks.forEach(function(p){var k=candKey(p.ids);if(!seen[k]){seen[k]=1;items.push({ids:p.ids,hint:'',extra:true});}});
    S.items=items;
    if(S.view>=items.length)S.view=Math.max(0,items.length-1);
  }
  function pickIndex(it){var k=candKey(it.ids);for(var i=0;i<S.picks.length;i++)if(candKey(S.picks[i].ids)===k)return i;return -1;}
  function itemIndexOfPick(p){var k=candKey(p.ids);for(var i=0;i<S.items.length;i++)if(candKey(S.items[i].ids)===k)return i;return -1;}
  function modesOf(ids){var m=[];ids.forEach(function(id){var o=S.ix.by[id],md=o&&(S.doc.sessions[o.si]||{}).mode;if(md&&m.indexOf(md)<0)m.push(md);});return m;}
  function msgBlock(m,cls){return '<div class="msg '+m.r+(cls?' '+cls:'')+'" data-mid="'+m.id+'"><div class="av">'+(m.r==='u'?'我':'e度')+'</div><div class="bw"><div class="bub"><div class="tx">'+esc(nb(m.x))+'</div><div class="tm">'+esc(fmtT(m.t))+'</div></div></div></div>';}
  var WSJ='「文思精靈」會一直給整篇文章、帶你讀文章，所以 e度 沒有照你說的聊。想正常對話、寫賀卡，要切換到「一般模式」。';
  function renderView(){
    var host=$('hView'),pg=$('hPager'),n=S.items.length;
    if(!n){pg.innerHTML='';host.innerHTML='<div class="hempty">老師還沒有幫你挑好對話。先確認最上面的年級、班級、座號有沒有填對；都對的話，請告訴老師。</div>';return;}
    var it=S.items[S.view],pi=pickIndex(it),on=pi>=0,modes=modesOf(it.ids),o=S.ix.by[it.ids[0]],se=S.doc.sessions[o.si]||{};
    pg.innerHTML='<button class="btn ghost" type="button" data-vgo="-1"'+(S.view===0?' disabled':'')+'><svg class="ico"><use href="#i-prev"/></svg>上一輪</button>'+
      '<div class="pdots">'+S.items.map(function(x,k){var s=pickIndex(x)>=0;return '<button type="button" class="vdot'+(k===S.view?' on':'')+(s?' sel':'')+'" data-vdot="'+k+'" aria-label="第 '+(k+1)+' 輪'+(s?'（已選）':'')+'">'+(k+1)+(s?'<svg class="ico"><use href="#i-check"/></svg>':'')+'</button>';}).join('')+'</div>'+
      '<button class="btn ghost" type="button" data-vgo="1"'+(S.view===n-1?' disabled':'')+'>下一輪<svg class="ico"><use href="#i-next"/></svg></button>';
    var h='<div class="vcard'+(on?' chosen':'')+'">';
    h+='<div class="ph"><span class="pn">'+(S.view+1)+'</span><span class="pt">第 '+(S.view+1)+' 輪／共 '+n+' 輪<small>'+esc(modes.join('、'))+'　'+esc(sessHead(se).replace(/<[^>]+>/g,' '))+'　共 '+it.ids.length+' 則訊息</small></span><span class="tools"><button class="tbtn" type="button" data-ctx="'+it.ids[0]+'">看這一輪的前後文</button></span></div>';
    if(modes.indexOf('文思精靈')>=0)h+='<div class="vwarn"><b>這一輪是用「文思精靈」聊的。</b>'+WSJ+'老師盡量不挑這種輪次，真的沒有別的才用；要選的話，下一步可以寫「e度 沒有照我說的做」。</div>';
    if(it.hint)h+='<div class="vhint"><b>老師挑這一輪，可以查證、想想：</b>'+esc(it.hint)+'</div>';
    else if(it.extra)h+='<div class="vhint"><b>這是你之前自己挑的一輪。</b>不想用就把下面的勾拿掉。</div>';
    h+='<div class="chain big" aria-label="這一輪的對話">'+chainHTML(S.doc,S.ix,{ids:it.ids})+'</div>';
    h+='<label class="selbtn'+(on?' on':'')+'"><input type="checkbox" data-choose="1"'+(on?' checked':'')+'><span class="bx"><svg class="ico"><use href="#i-check"/></svg></span><span class="tt">選這則<small>勾起來，就會送到下一步「寫理由」的清單</small></span></label>';
    host.innerHTML=h+'</div>';
  }
  function toggleChoose(){
    var it=S.items[S.view];if(!it)return;
    var pi=pickIndex(it);
    if(pi>=0){
      var p=S.picks[pi];
      if(((p.issNote||'').trim()||(p.why||'').trim())&&!confirm('不選這一輪了？你在這一輪寫的內容會不見。')){renderView();return;}
      S.picks.splice(pi,1);S.cur=firstUndone();toast('已從「寫理由」清單拿掉');
    }else{
      if(S.picks.length>=MAXP){toast('最多選 '+MAXP+' 輪。先把別輪的勾拿掉。');renderView();return;}
      S.picks.push({ids:it.ids.slice(),issNote:'',why:'',ts:Date.now()});
      toast('已送到「寫理由」清單（第 '+S.picks.length+' 個）');
    }
    buildItems();renderView();renderMyList();renderWrite();refreshMeta();saveSoon();
  }
  function viewGo(k){S.view=Math.max(0,Math.min(S.items.length-1,k));renderView();var t=$('hPager');if(t)t.scrollIntoView({behavior:'smooth',block:'start'});}
  function firstText(p,n){for(var i=0;i<p.ids.length;i++){var o=S.ix.by[p.ids[i]];if(o&&o.m.r==='u'&&!o.m.g)return clip(o.m.x,n);}return '（沒有你的話）';}
  // 「我選的」：已勾的輪次，可用 ▲▼ 排優先順序（PDF 照這個順序，最能代表你的放第 1）
  function renderMyList(){
    var m=$('hMy'),n=S.picks.length;
    m.innerHTML=n?S.picks.map(function(p,k){
      var vi=itemIndexOfPick(p);
      return '<div class="svi"><button type="button" class="svn" data-vopen="'+vi+'"><span class="pn">'+(k+1)+'</span><span class="pt">'+esc(firstText(p,22))+'<small>第 '+(vi+1)+' 輪　'+p.ids.length+' 則訊息</small></span></button>'+
        '<span class="svt"><button type="button" class="tbtn" data-mv="'+k+':-1"'+(k===0?' disabled':'')+' title="排前面">▲ 往前</button><button type="button" class="tbtn" data-mv="'+k+':1"'+(k===n-1?' disabled':'')+' title="排後面">▼ 往後</button></span></div>';
    }).join(''):'<div class="none">還沒有勾任何一輪。看完上面的對話，在下面勾「選這則」。</div>';
  }
  function movePick(k,d){
    var j=k+d;if(j<0||j>=S.picks.length)return;
    var x=S.picks[k];S.picks[k]=S.picks[j];S.picks[j]=x;
    S.cur=firstUndone();
    renderMyList();renderWrite();refreshMeta();saveSoon();
  }
  // 看某一句的前後文（說明書提示「看那段對話」用）
  function openCtx(id){
    var o=S.ix&&S.ix.by[id];if(!o)return;
    var se=S.doc.sessions[o.si],ms=se.msgs.filter(function(m){return !m.g;}),k=ms.findIndex(function(m){return m.id===id;});
    var a=Math.max(0,k-3),b=Math.min(ms.length,k+4);
    var ov=$('ctxOv');
    if(!ov){ov=document.createElement('div');ov.id='ctxOv';ov.className='ctxov';document.body.appendChild(ov);
      ov.addEventListener('click',function(e){if(e.target===ov||e.target.closest('[data-ctxclose]'))ov.classList.remove('on');});
      document.addEventListener('keydown',function(e){if(e.key==='Escape')ov.classList.remove('on');});}
    var h='<div class="ctxbox"><div class="ctxh"><b>這句話前後的對話</b><button class="btn ghost" type="button" data-ctxclose="1">關閉</button></div><div class="ctxb"><div class="sess">'+sessHead(se)+'</div>';
    ms.slice(a,b).forEach(function(m){h+=msgBlock(m,m.id===id?'sel':'');});
    ov.innerHTML=h+'</div></div>';ov.classList.add('on');
    var t=ov.querySelector('.msg.sel');if(t)t.scrollIntoView({block:'center'});
  }

  /* ---------- 第 5 步：一次寫一輪，寫完才換下一輪 ---------- */
  function need(){return Math.min(MINP,S.items.length||MINP);}
  function unlocked(k){for(var i=0;i<k;i++)if(!isDone(S.picks[i],S.ix))return false;return true;}
  function firstUndone(){for(var i=0;i<S.picks.length;i++)if(!isDone(S.picks[i],S.ix))return i;return Math.max(0,S.picks.length-1);}
  function guideH(open,judge,asks){
    return '<details class="gd"'+(open?' open':'')+'><summary>評審看什麼？怎麼想？</summary><div class="gdb"><p class="gj"><b>評審看：</b>'+judge+'</p><ul>'+asks.map(function(x){return '<li>'+x+'</li>';}).join('')+'</ul></div></details>';
  }
  function needText(p){
    var a=(p.issNote||'').trim().length,b=(p.why||'').trim().length,r=[];
    if(a<ISS_MIN)r.push('「我發現的問題」至少 '+ISS_MIN+' 個字');
    if(b<MINE_MIN)r.push('「最終採用的理由」至少 '+MINE_MIN+' 個字');
    return r.length?'還差：'+r.join('、'):'';
  }
  function writeCardHTML(k){
    var p=S.picks[k],n=S.picks.length,o=S.ix.by[p.ids[0]],se=S.doc.sessions[o.si]||{};
    var h='<div class="pcard" data-i="'+k+'">';
    h+='<div class="ph"><span class="pn">'+(k+1)+'</span><span class="pt">第 '+(k+1)+' 輪<small>共 '+n+' 輪　'+esc(sessHead(se).replace(/<[^>]+>/g,' '))+'</small></span><span class="tools"><button class="tbtn" type="button" data-wback="'+k+'">回上一步看這一輪</button></span></div>';
    h+='<div class="chain" aria-label="你保存的這一輪對話">'+chainHTML(S.doc,S.ix,p)+'</div>';
    h+='<div class="pf"><div class="lb"><span>我發現的問題，和我怎麼追問或修正</span><span class="au me">我自己寫</span><span class="ct" data-ct="issNote"></span></div>'+
      '<textarea class="px" data-f="issNote" maxlength="'+LIM.issNote+'" rows="3">'+esc(p.issNote)+'</textarea>'+
      guideH(true,'批判檢視、提問策略與人工修正（佔 30%，同分時先比這項）。「查證」不一定要上網，下面這些都算；只寫「很好」「沒有錯」，評審看不出你的想法。',
        ['<b>e度 沒看懂你的意思（理解錯誤）</b>：你說的和它做的不一樣？例如你說「晚上」它畫成白天、你說是賀卡它當成作文、你貼自己的文章它當成別人的。','<b>顏色、人數、時間、地點、稱呼</b>：和你要的一樣嗎？把 e度 畫的圖、寫的字，和你說過的話一項一項對。','<b>事實、名稱、成語、修辭、數字</b>：e度 說得對嗎？用字典、網站或問家人確認，記下你查到什麼、哪裡不一樣。','<b>前後不一致</b>：e度 前面這樣說、後面又那樣說，或你前面說的和後面寫的不一樣，哪個才對？','<b>沒有照你的限制做</b>：你說「只給建議」「先問我問題」，它有做到嗎？還是直接幫你寫了？','<b>錯字、用詞怪怪的</b>：你覺得讀起來不對的地方，你怎麼確認？','<b>然後呢？</b>你追問了什麼、或自己改了哪裡？改之前和改之後差在哪？','都沒發現問題也要寫：你是怎麼檢查的、為什麼確定沒問題。'])+'</div>';
    h+='<div class="pf final"><div class="lb"><span>最終採用的理由</span><span class="au me">我自己寫</span><span class="ct" data-ct="why"></span></div>'+
      '<textarea class="px" data-f="why" maxlength="'+LIM.why+'" rows="3">'+esc(p.why)+'</textarea>'+
      guideH(true,'人工修正、創意與生活連結（各 30%）、數位倫理與權責揭露（20%）。',
        ['這一輪最後，你留下了哪一部分？哪一部分沒用或自己改掉？為什麼？','這一句為什麼「像我」「像我家」？連到哪一件真實發生過的事？','這一部分最後是誰做的：AI 給的、我改的，還是我自己想的？'])+'</div>';
    h+='<div class="wnav"><button class="btn ghost" type="button" data-wprev="1"'+(k===0?' disabled':'')+'>← 上一輪</button><span class="wneed" id="wNeed"></span>'+
      '<button class="btn" type="button" data-wnext="1" id="wNext"></button></div>';
    return h+'</div>';
  }
  function renderWrite(){
    var host=$('hPicks'),n=S.picks.length;
    if(!n){$('wTabs').innerHTML='';host.innerHTML='<div class="hempty">還沒有選任何一輪。回上一步，看老師幫你挑的對話，在想寫的那一輪勾「選這則」。<br><button class="btn" type="button" data-wback="-1" style="margin-top:8px">回上一步去選</button></div>';return;}
    if(S.cur>=n)S.cur=n-1;
    if(!unlocked(S.cur))S.cur=firstUndone();
    host.innerHTML=writeCardHTML(S.cur);
    updCounts();refreshWrite();
  }
  // 不重畫輸入框（會失去游標）：只更新分頁、提示、下一輪按鈕
  function refreshWrite(){
    var n=S.picks.length,tabs=$('wTabs');
    tabs.innerHTML=S.picks.map(function(p,k){
      var d=isDone(p,S.ix),ul=unlocked(k);
      return '<button type="button" class="wt'+(k===S.cur?' on':'')+(d?' done':'')+'" data-wgo="'+k+'"'+(ul?'':' disabled')+'><span class="pn">'+(k+1)+'</span>第 '+(k+1)+' 輪'+(d?'<svg class="ico ok"><use href="#i-check"/></svg>':(ul?'':'<svg class="ico"><use href="#i-lock"/></svg>'))+'</button>';
    }).join('');
    var nx=$('wNext');if(!nx||!S.picks[S.cur])return;
    var p=S.picks[S.cur],d=isDone(p,S.ix),last=S.cur===n-1;
    nx.disabled=!d;nx.innerHTML=last?'全部寫完了，預覽歷程紀錄<svg class="ico"><use href="#i-eye"/></svg>':'這一輪寫好了，換下一輪<svg class="ico"><use href="#i-next"/></svg>';
    $('wNeed').textContent=d?(last?'':'寫好了，可以換下一輪。'):needText(p);
    $('wNeed').className='wneed'+(d?' ok':'');
  }
  function updCounts(){
    var card=document.querySelector('#hPicks .pcard');if(!card)return;
    var p=S.picks[Number(card.dataset.i)];if(!p)return;
    Array.prototype.forEach.call(card.querySelectorAll('[data-ct]'),function(c){
      var f=c.dataset.ct,max=LIM[f],len=(p[f]||'').length;c.textContent=len+'／'+max;c.classList.toggle('over',len>=max);
    });
  }
  function refreshMeta(){
    var done=S.picks.filter(function(p){return isDone(p,S.ix);}).length,n=S.picks.length;
    var pr=$('hProg');
    pr.textContent='已選 '+n+' 輪，寫好 '+done+' 輪（至少要 '+need()+' 輪寫好）';
    pr.className='hprog'+(done>=need()?' good':'');
    clearTimeout(refreshMeta._t);refreshMeta._t=setTimeout(updPages,250);
    var ok=n>=need()&&done>=need();
    setHidden('hOk',ok?'1':'');
    setHidden('hCnt',n?(n+' 輪（寫好 '+done+' 輪）'):'');
    $('hSheetBtn').disabled=!done;
    var inf=$('hSaveInfo');inf.textContent='已選 '+n+' 輪（至少要 '+need()+' 輪，最多 '+MAXP+' 輪）';inf.className='hprog'+(n>=need()?' good':'');
    if(S.doc)refreshWrite();
  }
  function sheetItems(){return S.picks.filter(function(p){return isDone(p,S.ix);}).map(function(p){return {p:p,ix:S.ix,mode:(S.doc.sessions[S.ix.by[p.ids[0]].si]||{}).mode};});}
  function updPages(){
    var items=sheetItems(),el=$('hPages');
    if(!items.length){el.textContent='';return;}
    var tmp=document.createElement('div');tmp.style.cssText='position:absolute;left:-9999px;top:0;visibility:hidden';
    var sh=sheetEl(items,{});tmp.appendChild(sh);document.body.appendChild(tmp);
    var n=pagesOf(sh);document.body.removeChild(tmp);
    el.textContent='排版後約 '+n+' 頁（上限 2 頁）'+(n>2?'：太長了，請把文字縮短，或少保存一輪':'');
    el.className='hprog'+(n>2?'':' good');if(n>2)el.style.color='var(--red)';else el.style.color='';
  }
  function saveSoon(){
    clearTimeout(S.saveT);statEl.textContent='修改中…';
    S.saveT=setTimeout(saveNow,900);
  }
  function saveNow(){
    if(!S.id||!S.fb)return;
    var picks=S.picks.map(function(p){return cleanPick(p);}),at=Date.now(),id=S.id;
    writeLocal(id,{picks:picks,at:at});
    statEl.textContent='存檔中…';
    ensureAuth(S.fb).then(function(){return S.fb.db.collection(AIH).doc(id).update({picks:picks,picksAt:at});})
      .then(function(){var d=new Date();statEl.textContent='已存到雲端 '+d.getHours()+':'+('0'+d.getMinutes()).slice(-2);})
      .catch(function(e){console.warn('picks 存檔失敗',e);statEl.textContent='雲端沒存到，先存在這台電腦';});
  }

  // 事件：第 4 步（左右切換、勾「選這則」、排順序、看前後文）
  root.addEventListener('click',function(e){
    var t=e.target.closest('[data-vgo],[data-vdot],[data-ctx],[data-mv],[data-vopen]');if(!t||t.disabled)return;
    if(t.dataset.vgo){viewGo(S.view+Number(t.dataset.vgo));return;}
    if(t.dataset.vdot!=null){viewGo(Number(t.dataset.vdot));return;}
    if(t.dataset.ctx){openCtx(t.dataset.ctx);return;}
    if(t.dataset.vopen!=null){if(Number(t.dataset.vopen)>=0)viewGo(Number(t.dataset.vopen));return;}
    if(t.dataset.mv){var a=t.dataset.mv.split(':');movePick(Number(a[0]),Number(a[1]));return;}
  });
  root.addEventListener('change',function(e){if(e.target.dataset&&e.target.dataset.choose)toggleChoose();});
  document.addEventListener('keydown',function(e){   // 第 4 步用鍵盤 ← → 切換
    if((e.key!=='ArrowLeft'&&e.key!=='ArrowRight')||root.hidden||root.offsetParent===null)return;
    var tg=e.target&&e.target.tagName;if(tg==='TEXTAREA'||tg==='INPUT'||tg==='SELECT')return;
    viewGo(S.view+(e.key==='ArrowLeft'?-1:1));
  });
  // 事件：第 5 步（逐輪書寫）
  wroot.addEventListener('click',function(e){
    var t=e.target.closest('[data-wgo],[data-wprev],[data-wnext],[data-wback]');if(!t||t.disabled)return;
    function go(k){S.cur=k;renderWrite();var c=$('wTabs');if(c)c.scrollIntoView({behavior:'smooth',block:'start'});}
    if(t.dataset.wgo!=null){go(Number(t.dataset.wgo));return;}
    if(t.dataset.wprev){if(S.cur>0)go(S.cur-1);return;}
    if(t.dataset.wnext){
      if(!isDone(S.picks[S.cur],S.ix))return;
      if(S.cur<S.picks.length-1)go(S.cur+1);else $('hSheetBtn').click();
      return;
    }
    if(t.dataset.wback!=null){var k=Number(t.dataset.wback);if(k>=0&&S.picks[k]){var vi=itemIndexOfPick(S.picks[k]);if(vi>=0)S.view=vi;}window.cardShowStep(4);renderView();return;}
  });
  wroot.addEventListener('input',function(e){
    var f=e.target.dataset&&e.target.dataset.f,p=S.picks[S.cur];
    if(!f||!p)return;
    p[f]=e.target.value;
    updCounts();refreshMeta();saveSoon();
  });

  /* ---------- 第 6 步（作品說明書）：依對話給的提醒、手冊連結、自動儲存 ---------- */
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
    if(j){openCtx(j.dataset.gojump);}
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
    var items=sheetItems();
    if(!items.length){toast('先把至少一輪寫好，才排得出歷程紀錄');return;}
    var all=S.picks.length,skipped=all-items.length;
    showSheets([{items:items}],'AI協作歷程紀錄_'+S.id);
    if(skipped)toast('有 '+skipped+' 輪還沒寫好，預覽裡先不放');
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
    function dpicks(d,ix){return picksOf(d,ix);}
    function pageEst(d){
      var ix=indexDoc(d),items=dpicks(d,ix).filter(function(p){return isDone(p,ix);}).map(function(p){return {p:p,ix:ix};});
      if(!items.length)return '';
      var tmp=document.createElement('div');tmp.style.cssText='position:absolute;left:-9999px;top:0;visibility:hidden';
      var s=sheetEl(items,{});tmp.appendChild(s);document.body.appendChild(tmp);
      var n=pagesOf(s);document.body.removeChild(tmp);return n;
    }
    function aList(){
      var ids=Object.keys(A.docs).sort(function(a,b){var x=a.split('-'),y=b.split('-');return x[0]-y[0]||x[1]-y[1]||x[2]-y[2];});
      var h='<tr><th>年-班-座</th><th>對話</th><th>老師標記</th><th>學生挑了</th><th>理由寫好</th><th>預估頁數</th><th></th></tr>';
      ids.forEach(function(id){
        var d=A.docs[id],ix=indexDoc(d),n=ix.flat.filter(function(o){return o.m.r==='u'&&!o.m.g;}).length,pk=dpicks(d,ix),dn=pk.filter(function(p){return isDone(p,ix);}).length,pg=pageEst(d);
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
      var pk=dpicks(d,A.ix);
      var h='<div class="card"><h3><svg class="ico"><use href="#i-users"/></svg>'+id+'　學生保存了 '+pk.length+' 輪</h3>';
      h+='<p class="small muted">① 在下面的對話裡替老師認為「值得寫」的地方按「★ 標記」，學生會在右邊看到跳轉按鈕。② 學生挑好的對話在最下面，可預覽、列印成 PDF（每人最多 2 頁）。</p>';
      h+='<div class="adbox" id="hAdChat">'+chatHTML(d,A.ix,{admin:true,picks:pk,sel:[]})+'</div>';
      var cd=d.cands||[];
      if(cd.length){h+='<h3 style="margin-top:6px"><svg class="ico"><use href="#i-star"/></svg>老師預選的輪次（學生在第 4 步左右切換、勾「選這則」）</h3><div class="incl">'+cd.map(function(c,k){
        var ids=(c.ids||[]).filter(function(i){return A.ix.by[i];}),sel=pk.some(function(p){return p.ids.join('|')===ids.join('|');});
        return '<div class="candrow"><b>預選 '+(k+1)+'（'+ids.length+' 則）'+(sel?'　✓ 學生已選':'')+'</b><br><small>'+esc(c.hint||'')+'</small></div>';}).join('')+'</div>';}
      h+='<h3 style="margin-top:6px"><svg class="ico"><use href="#i-file"/></svg>學生挑的對話（依優先順序）</h3>';
      if(!pk.length)h+='<div class="hempty">這位同學還沒有挑。</div>';
      else{
        h+='<div class="incl" id="hAdIncl">'+pk.map(function(p,k){
          var t=roundText(p,A.ix),dn=isDone(p,A.ix);
          return '<label><input type="checkbox" data-inc="'+k+'"'+(dn?' checked':'')+'><span><b>優先 '+(k+1)+(dn?'':'（還沒寫好）')+'</b>　'+esc(clip(t.q,40))+'<br><small>理由：'+esc(clip(t.why,60)||'（空白）')+'</small></span></label>';
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
    function modeOf(d,ix,p){var o=ix.by[p.ids[0]];return o?((d.sessions[o.si]||{}).mode||''):'';}
    function aPreview(id){
      var d=A.docs[id],ix=indexDoc(d),chosen={},useId=false;
      Array.prototype.forEach.call(document.querySelectorAll('#hAdIncl input'),function(c){chosen[c.dataset.inc]=c.checked;});
      function draw(){
        var items=dpicks(d,ix).filter(function(p,k){return chosen[k];}).map(function(p){return {p:p,ix:ix,mode:modeOf(d,ix,p)};});
        var opt='<label><input type="checkbox" id="shId"'+(useId?' checked':'')+'> 角落加上編號（'+id+'，核對用；送件版不要勾）</label>';
        showSheets([{items:items,idLabel:useId?id:''}],'AI協作歷程紀錄_'+id,opt,function(){useId=$('shId').checked;draw();});
      }
      draw();
    }
    function aPreviewAll(){
      function doneOf(id){var d=A.docs[id],ix=indexDoc(d);return dpicks(d,ix).filter(function(p){return isDone(p,ix);});}
      var ids=Object.keys(A.docs).filter(function(id){return doneOf(id).length;}).sort();
      var sheets=ids.map(function(id){var d=A.docs[id],ix=indexDoc(d);return {items:doneOf(id).map(function(p){return {p:p,ix:ix,mode:modeOf(d,ix,p)};}),idLabel:''};});
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
