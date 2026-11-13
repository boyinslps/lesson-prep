/*FIREBASE_CONFIG*/

/* ===== 週五版引擎：識別列／開場提醒／作答狀態／斷點繳交／取回進度／教師模式／檢視／步驟分頁 =====
   資料契約依《學習單資料與提交規範》：submissions（教師看）＋ studentWork（學生取回自己的進度）。 */
(function(){
  var WS='g5-L05-fri',LESSON_PATH='g5/L05-fri',TITLE='Docs 查證報告（週五版）：全部寫在學習單';
  var STATE_KEY='g5L05friflow',WORK_KIND='progress';
  var TEACHER_EMAIL='boyin0304@slps.tn.edu.tw';
  var IS_ADMIN=location.hash==='#admin';
  var REVIEW_ID=IS_ADMIN?new URLSearchParams(location.search).get('review'):null;   // 沒有 #admin 不給看別人的作答
  function $(id){return document.getElementById(id);}
  function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function filled(v){return !!String(v==null?'':v).trim();}
  function tr(v){return String(v==null?'':v).trim();}
  function withTimeout(p,ms){return new Promise(function(res,rej){var t=setTimeout(function(){rej(new Error('timeout'));},ms);p.then(function(v){clearTimeout(t);res(v);},function(e){clearTimeout(t);rej(e);});});}

  // ===== 題目：qid 對應步驟、題型、題幹 =====
  var STEP_NAMES=['開始','選訊息','找文章','網址','搜尋工具','原始內容','查核結果','正確資訊','為何流傳','相信後果','預覽','繳交'];
  var Q=[
    {qid:'sel',step:2,type:'experience',name:'選一則訊息'},
    {qid:'url',step:4,type:'experience',report:1,name:'查核網址'},
    {qid:'tool',step:5,type:'open',report:1,name:'你使用的搜索工具',text:'你使用的搜索工具（關鍵字、以圖搜圖、智慧鏡頭）：用了什麼工具；用關鍵字搜尋的，輸入了什麼'},
    {qid:'desc',step:6,type:'open',report:1,name:'原始內容描述',text:'原始內容描述：只描述網傳訊息或影片說了什麼，不做查證判斷'},
    {qid:'res',step:7,type:'open',report:1,name:'查核結果',text:'查核結果：哪個查核機構、標了什麼結果、一句重點'},
    {qid:'fact',step:8,type:'open',report:1,name:'正確資訊',text:'正確資訊：用自己的話整理查核文章說的事實，1～3 點，並標出是誰說的'},
    {qid:'why',step:9,type:'open',report:1,name:'為什麼會流傳',text:'為什麼這則訊息會被廣傳？'},
    {qid:'risk',step:10,type:'open',report:1,name:'相信的後果',text:'如果相信這則訊息，會有什麼後果？（誰會怎樣）'}
  ];
  // 舊版的步驟清單（拿回舊進度時用名稱對到新的步驟）。v1：有標題；v2：拿掉標題；v3：加預覽；v4（現在）：拿掉老師示範
  var OLD_STEPS={1:['開始','老師示範','選訊息','找文章','標題','網址','搜尋工具','原始內容','查核結果','正確資訊','為何流傳','相信後果','繳交'],
    2:['開始','老師示範','選訊息','找文章','網址','搜尋工具','原始內容','查核結果','正確資訊','為何流傳','相信後果','繳交'],
    3:['開始','老師示範','選訊息','找文章','網址','搜尋工具','原始內容','查核結果','正確資訊','為何流傳','相信後果','預覽','繳交']};
  var STEP_ALIAS={'標題':'網址','老師示範':'選訊息'};
  var QMAP={};Q.forEach(function(q){QMAP[q.qid]=q;});
  var STEP_Q={};Q.forEach(function(q){STEP_Q[q.step]=q.qid;});
  var REPORT=Q.filter(function(q){return q.report;});
  var URL_RE=/^https?:\/\/[^\s]+$/i;
  var OK_HOST=/(^|\.)(tfc-taiwan\.org\.tw|mygopen\.com)$/i;

  var CARDS={
    C:{name:'C ‧ 繪畫比賽投票（LINE 訊息）',stars:1,hint:'想想：這則訊息要你「做什麼」？連結要你「輸入什麼」？再加上「查核」。'},
    D:{name:'D ‧ 微波爐加熱食物有輻射（訊息）',stars:2,hint:'想想：哪一種家電？哪個國家要禁用？再加上「查核」。也可以點原始文章，看它是什麼樣的網站。'},
    E:{name:'E ‧ 打雷時用手機、藍芽耳機（訊息）',stars:3,hint:'想想：什麼東西、遇到什麼天氣、會怎樣？再加上「查核」。'},
    G:{name:'G ‧ 印度街頭小吃影片（貼文）',stars:2,hint:'想想：哪個國家？在做什麼食物？影片裡的人做了什麼事？再加上「查核」。'},
    H:{name:'H ‧ 手機充電時喝水（影片）',stars:1,hint:'想想：充電時做了什麼事？這支影片也可以用「以圖搜圖」找。'},
    K:{name:'K ‧ 地震時躲哪裡（訊息）',stars:2,hint:'想想：地震時要「去哪裡」躲？也試試找消防局、氣象署的官方說明。'}
  };

  // ===== 作答狀態（localStorage）。_owner＝這份作答屬於誰（共用電腦換人時用）=====
  function freshState(){return {sel:null,url:'',toolKinds:[],toolB:'',desc:'',resOrg:'',resLabel:'',resNote:'',fact:'',whyKinds:[],whyText:'',riskKinds:[],riskText:'',chk:[],open:{},_owner:'',_step:1};}
  var state=freshState();
  if(!REVIEW_ID){try{var sv=localStorage.getItem(STATE_KEY);if(sv)state=Object.assign(freshState(),JSON.parse(sv));}catch(e){}}
  function save(){
    if(REVIEW_ID)return;
    var idn=getIdentity();if(!state._owner&&identityValid(idn))state._owner=idKey(idn);   // 換人由 checkOwner 處理
    state._step=curStep;
    try{localStorage.setItem(STATE_KEY,JSON.stringify(state));}catch(e){}
  }
  function hasContent(){
    return ['sel','url','toolB','desc','resOrg','resLabel','resNote','fact','whyText','riskText'].some(function(k){return filled(state[k]);})
      ||['toolKinds','whyKinds','riskKinds'].some(function(k){return (state[k]||[]).length>0;});
  }

  // ===== 每題「寫好了嗎」＋「交出去的文字」=====
  function hasKw(){return (state.toolKinds||[]).indexOf('關鍵字搜尋')>=0;}
  var DONE={
    sel:function(){return !!state.sel;},
    url:function(){return URL_RE.test(tr(state.url));},
    // 只有選了「關鍵字搜尋」才需要寫「我輸入的是」；以圖搜圖、智慧鏡頭沒有這一欄
    tool:function(){return state.toolKinds.length>0&&(!hasKw()||filled(state.toolB));},
    desc:function(){return filled(state.desc);},
    res:function(){return filled(state.resOrg)&&filled(state.resLabel)&&filled(state.resNote);},
    fact:function(){return filled(state.fact);},
    why:function(){return filled(state.whyText);},
    risk:function(){return filled(state.riskText);}
  };
  function given(qid){
    var s=state,p=[];
    switch(qid){
      case 'sel':return s.sel?(CARDS[s.sel]?CARDS[s.sel].name:s.sel):'';
      case 'url':return tr(s.url);
      case 'tool':
        if(s.toolKinds.length)p.push('使用的工具：'+s.toolKinds.join('、'));
        if(hasKw()&&filled(s.toolB))p.push('在 Google 輸入：'+tr(s.toolB));
        return p.join('\n');
      case 'desc':return tr(s.desc);
      case 'res':
        if(filled(s.resOrg))p.push('機構：'+s.resOrg);
        if(filled(s.resLabel))p.push('標籤：'+s.resLabel);
        if(filled(s.resNote))p.push('重點：'+tr(s.resNote));
        return p.join('\n');
      case 'fact':return tr(s.fact);
      case 'why':
        if(s.whyKinds.length)p.push('原因類型：'+s.whyKinds.join('、'));
        if(filled(s.whyText))p.push((s.whyKinds.length?'理由：':'')+tr(s.whyText));
        return p.join('\n');
      case 'risk':
        if(s.riskKinds.length)p.push('後果類型：'+s.riskKinds.join('、'));
        if(filled(s.riskText))p.push((s.riskKinds.length?'誰會怎樣：':'')+tr(s.riskText));
        return p.join('\n');
    }
    return '';
  }
  function doneCount(){return REPORT.filter(function(q){return DONE[q.qid]();}).length;}

  // ===== 圖片載不到 → 佔位框；點圖放大 =====
  function phImg(img){var d=el('div','imgph',esc(img.getAttribute('src')));img.replaceWith(d);}
  document.querySelectorAll('img.shotimg').forEach(function(img){if(img.complete&&img.naturalWidth===0)phImg(img);else img.addEventListener('error',function(){phImg(img);});});
  (function(){
    var lb=$('lightbox'),stage=$('lbStage'),img=$('lbImg'),pct=$('lbPct');
    var sc=1,tx=0,ty=0,drag=null,moved=false,MAX=8;
    img.style.transformOrigin='0 0';img.draggable=false;
    function apply(){img.style.transform='translate('+tx+'px,'+ty+'px) scale('+sc+')';img.style.cursor=sc>1?(drag?'grabbing':'grab'):'zoom-in';pct.textContent=Math.round(sc*100)+'%';}
    function zoomAt(f,cx,cy){
      var r=img.getBoundingClientRect(),bl=r.left-tx,bt=r.top-ty;
      if(cx==null){cx=r.left+r.width/2;cy=r.top+r.height/2;}
      var x=(cx-bl-tx)/sc,y=(cy-bt-ty)/sc,s2=Math.max(1,Math.min(MAX,sc*f));
      if(s2===1){tx=ty=0;}else{tx=cx-bl-x*s2;ty=cy-bt-y*s2;}
      sc=s2;apply();
    }
    function reset(){sc=1;tx=ty=0;apply();}
    stage.addEventListener('wheel',function(e){e.preventDefault();zoomAt(e.deltaY<0?1.25:0.8,e.clientX,e.clientY);},{passive:false});
    img.addEventListener('dblclick',function(e){e.preventDefault();if(sc>1)reset();else zoomAt(2.5,e.clientX,e.clientY);});
    img.addEventListener('pointerdown',function(e){if(sc<=1)return;e.preventDefault();drag={x:e.clientX-tx,y:e.clientY-ty};moved=false;img.setPointerCapture(e.pointerId);apply();});
    img.addEventListener('pointermove',function(e){if(!drag)return;tx=e.clientX-drag.x;ty=e.clientY-drag.y;moved=true;apply();});
    img.addEventListener('pointerup',function(){drag=null;apply();});
    img.addEventListener('click',function(e){e.stopPropagation();if(!moved&&sc===1)zoomAt(2,e.clientX,e.clientY);moved=false;});
    $('lbIn').onclick=function(){zoomAt(1.25);};$('lbOut').onclick=function(){zoomAt(0.8);};$('lbReset').onclick=reset;
    function close(){lb.classList.remove('on');document.body.style.overflow='';}
    $('lbClose').onclick=close;
    stage.addEventListener('click',function(e){if(e.target===stage)close();});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&lb.classList.contains('on'))close();});
    document.addEventListener('click',function(e){
      var t=e.target.closest&&e.target.closest('img.shotimg');
      if(!t||lb.contains(t))return;
      e.preventDefault();img.src=t.getAttribute('src');img.alt=t.alt||'';reset();lb.classList.add('on');document.body.style.overflow='hidden';
    });
  })();

  // ===== 識別列（頁面上方黏頂）=====
  var ID_KEY='wk_identity',BAR=['idGrade','idClass','idStudent'];
  function digits(s){return String(s||'').replace(/[^0-9]/g,'');}
  function loadIdentity(){try{return JSON.parse(localStorage.getItem(ID_KEY)||'{}');}catch(e){return {};}}
  function saveIdentity(o){try{localStorage.setItem(ID_KEY,JSON.stringify(o));}catch(e){}}
  function getIdentity(){
    var g=digits($('idGrade').value),c=digits($('idClass').value),s=digits($('idStudent').value);
    return {grade:g?Number(g):null,className:c?Number(c):null,studentId:s?Number(s):null};
  }
  function identityValid(id){return id.grade!=null&&id.className!=null&&id.className>=1&&id.className<=14&&id.studentId!=null;}
  function idKey(id){return id.grade+'-'+id.className+'-'+id.studentId;}
  function idLabel(k){var a=String(k).split('-');return a[0]+'年'+a[1]+'班'+a[2]+'號';}
  function clampClass(v){while(v!==''&&Number(v)>14)v=v.slice(0,-1);return v;}
  function markIdentity(on){
    BAR.forEach(function(id){var e=$(id),bad=on&&!digits(e.value);
      e.classList.toggle('border-rose-400',bad);e.classList.toggle('bg-rose-50',bad);e.classList.toggle('border-slate-200',!bad);});
  }
  function focusFirstEmptyId(){
    var f=BAR.filter(function(id){return !digits($(id).value);})[0];
    if(f)$(f).focus();
  }
  function afterIdChange(){
    var idn=getIdentity(),ok=identityValid(idn);
    if(ok){saveIdentity(idn);}
    $('idOk').classList.toggle('hidden',!ok);
    $('idNeed').classList.toggle('hidden',ok);
    $('idGrade').parentElement.parentElement.classList.toggle('idwarn',!ok&&!REVIEW_ID);
  }
  // 共用電腦：三個框填好離開時，若這台電腦上的作答是別人的，先問再清空（不同意就換回原本的身分）
  function checkOwner(){
    if(REVIEW_ID)return;
    var idn=getIdentity();if(!identityValid(idn))return;
    var key=idKey(idn);
    if(state._owner&&state._owner!==key&&hasContent()){
      if(!confirm('這台電腦上現在的作答是 '+idLabel(state._owner)+' 的，你填的是 '+idLabel(key)+'。\n\n要清掉換成你的嗎？\n（對方如果按過「先存檔交一次」，之後還是拿得回來。）')){
        var o=state._owner.split('-');BAR.forEach(function(id,i){$(id).value=o[i];});afterIdChange();return;
      }
      state=freshState();state._owner=key;save();renderAll();return;
    }
    state._owner=key;save();   // 沒換人就不重畫，避免吃掉使用者正要點的按鈕
  }
  (function(){
    var saved=loadIdentity();
    if(saved.grade)$('idGrade').value=saved.grade;
    if(saved.className)$('idClass').value=saved.className;
    if(saved.studentId)$('idStudent').value=saved.studentId;
    BAR.forEach(function(id,i){
      var e=$(id);
      e.addEventListener('input',function(){
        var d=digits(e.value);if(i===1)d=clampClass(d);if(d!==e.value)e.value=d;
        if(d){e.classList.remove('border-rose-400','bg-rose-50');e.classList.add('border-slate-200');}
        afterIdChange();
      });
      e.addEventListener('change',checkOwner);
    });
    afterIdChange();
  })();

  // ===== Firebase =====
  var db=null,auth=null,quizRef=null;
  function loadScript(src){return new Promise(function(res,rej){var s=document.createElement('script');s.src=src;s.onload=res;s.onerror=rej;document.head.appendChild(s);});}
  var fbReady=(function(){
    if(!firebaseConfig)return Promise.resolve();
    var base='https://www.gstatic.com/firebasejs/10.8.0/';
    return loadScript(base+'firebase-app-compat.js')
      .then(function(){return loadScript(base+'firebase-auth-compat.js');})
      .then(function(){return loadScript(base+'firebase-firestore-compat.js');})
      .then(function(){firebase.initializeApp(firebaseConfig);db=firebase.firestore();auth=firebase.auth();quizRef=db.collection('quizzes').doc(WS);$('syncBadge').classList.remove('hidden');})
      .catch(function(e){console.warn('Firebase 啟用失敗，改用單機模式',e);});
  })();
  // 等 Firebase 還原持久化登入狀態；學生分支確認沒人登入才匿名登入（避免洗掉老師的 session）
  var authResolved=fbReady.then(function(){
    if(!auth)return null;
    return new Promise(function(resolve){var unsub=auth.onAuthStateChanged(function(u){if(unsub){unsub();unsub=null;}resolve(u);});});
  });
  function ensureAuth(){return (auth&&auth.currentUser)?Promise.resolve(auth.currentUser):auth.signInAnonymously().then(function(c){return c.user;});}

  // ===== 小提示、紅框提醒視窗 =====
  var toastT=null;
  function toast(t){var e=$('toast');e.textContent=t;e.classList.remove('hidden');clearTimeout(toastT);toastT=setTimeout(function(){e.classList.add('hidden');},4200);}
  function failModal(title,msgHtml,focusId){
    var old=$('failModal');if(old)old.remove();
    var m=el('div','');m.id='failModal';
    m.style.cssText='position:fixed;inset:0;z-index:9999;background:rgba(15,23,42,.6);display:flex;align-items:center;justify-content:center;padding:20px';
    m.innerHTML='<div style="background:#fff;border:6px solid #f43f5e;border-radius:24px;max-width:460px;width:100%;padding:24px;text-align:center"><div style="font-size:56px;line-height:1">⚠️</div><h2 style="color:#e11d48;font-size:28px;font-weight:900;margin:8px 0">'+esc(title)+'</h2><p style="font-size:19px;font-weight:700;line-height:1.7;color:#334155;margin:0 0 16px">'+msgHtml+'</p><button type="button" id="failOk" style="background:#e11d48;color:#fff;font-weight:900;font-size:18px;border:0;border-radius:14px;padding:10px 28px;cursor:pointer">我知道了</button></div>';
    document.body.appendChild(m);
    $('failOk').onclick=function(){m.remove();if(focusId)focusFirstEmptyId();};
  }
  var ID_MSG='請先填好 <b style="color:#e11d48">年級、班級、座號</b>（班級是 1～14），再按一次。';

  // ===== 學生暫存區 studentWork：斷點進度（id 尾巴帶 __progress，見規範 §3-c）=====
  function workId(idn){return WS+'__'+idKey(idn)+'__'+WORK_KIND;}
  function saveProgress(idn){
    if(!db)return;
    var snap=JSON.parse(JSON.stringify(state));delete snap._owner;delete snap._step;
    var text='第 '+curStep+' 步・已完成 '+doneCount()+'／'+REPORT.length+' 欄\n'+tr(state.url).slice(0,300);
    db.collection('studentWork').doc(workId(idn)).set({
      worksheetId:WS,kind:WORK_KIND,grade:idn.grade,className:idn.className,studentId:idn.studentId,
      data:{state:snap,step:curStep,done:doneCount(),v:4},text:text.slice(0,1900),updatedAt:firebase.firestore.FieldValue.serverTimestamp()})
      .catch(function(e){console.warn('進度暫存失敗',e);});
  }
  // 回傳 Promise<null | {state,step,done,at}>；讀取失敗會 reject
  function fetchProgress(idn){
    if(!db||!auth)return Promise.reject(new Error('offline'));
    var p=authResolved.then(function(){return ensureAuth();})
      .then(function(){return db.collection('studentWork').doc(workId(idn)).get();})
      .then(function(doc){
        if(!doc.exists)return null;
        var d=doc.data()||{},dd=d.data||{};if(!dd.state)return null;
        var at=null;try{at=d.updatedAt&&d.updatedAt.toDate();}catch(e){}
        var step=dd.step||0,done=dd.done||0,v=dd.v||1;
        if(v<4){
          var oldNames=OLD_STEPS[v]||OLD_STEPS[1],nm=oldNames[step-1];nm=STEP_ALIAS[nm]||nm;
          var idx=STEP_NAMES.indexOf(nm);step=idx>=0?idx+1:0;
          if(v<2&&filled(dd.state.title)&&done>0)done-=1;   // v1 的完成數含「標題」
        }
        return {state:dd.state,step:step,done:done,at:at};
      });
    return withTimeout(p,6000);
  }
  function fmtAt(d){return d?((d.getMonth()+1)+'/'+d.getDate()+' '+('0'+d.getHours()).slice(-2)+':'+('0'+d.getMinutes()).slice(-2)):'';}
  function resumeLine(r){return '找到了！你上次存的進度：寫到第 '+(r.step||'?')+' 步，已完成 '+r.done+'／'+REPORT.length+' 欄'+(r.at?'（'+fmtAt(r.at)+'）':'')+'。';}
  function applyProgress(r,idn){
    state=Object.assign(freshState(),r.state);state._owner=idKey(idn);
    var want=r.step&&r.step<=STEP_NAMES.length?r.step:suggestStep();
    starLive=false;save();renderAll();showStep(want);starLive=true;
    toast('已拿回你的進度，接著寫吧！');
  }
  function suggestStep(){
    for(var i=0;i<Q.length;i++){if(!DONE[Q[i].qid]())return Q[i].step;}
    return STEP_NAMES.length;
  }
  function resumeMsg(t,kind){
    document.querySelectorAll('[data-resumemsg]').forEach(function(p){p.textContent=t;p.className='ml-2 text-base font-bold '+(kind==='ok'?'text-emerald-700':kind==='warn'?'text-amber-700':'text-violet-700');});
  }
  function manualResume(){
    var idn=getIdentity();
    if(!identityValid(idn)){markIdentity(true);focusFirstEmptyId();resumeMsg('先在最上面填好年級、班級、座號。','warn');return;}
    resumeMsg('找找看…');
    fetchProgress(idn).then(function(r){
      if(!r){resumeMsg('還沒有找到你存過的進度。寫完按「先存檔交一次」，下次就能拿回來。','warn');return;}
      if(hasContent()&&!confirm(resumeLine(r)+'\n\n要用它換掉這台電腦上現在寫的內容嗎？'))return;
      applyProgress(r,idn);resumeMsg('');
    }).catch(function(e){console.warn('讀取進度失敗',e);resumeMsg('現在拿不到，晚點再試試看。','warn');});
  }
  document.addEventListener('click',function(ev){
    var t=ev.target.closest&&ev.target.closest('[data-loadwork]');if(t)manualResume();
  });

  // ===== 填寫畫面：欄位、選項、檢查表、進度 =====
  function bindFields(){
    document.querySelectorAll('[data-k]').forEach(function(f){
      f.value=state[f.dataset.k]||'';
      f.addEventListener('input',function(){state[f.dataset.k]=f.value;save();refresh();});
    });
  }
  function fillFields(){document.querySelectorAll('[data-k]').forEach(function(f){f.value=state[f.dataset.k]||'';});}
  document.addEventListener('click',function(ev){
    var b=ev.target.closest&&ev.target.closest('[data-chips] [data-v]');
    if(b){
      var host=b.closest('[data-chips]'),k=host.dataset.chips,v=b.dataset.v;
      if(host.hasAttribute('data-multi')){var a=state[k]||[],i=a.indexOf(v);if(i>=0)a.splice(i,1);else a.push(v);state[k]=a;}
      else state[k]=(state[k]===v)?'':v;
      save();refresh();return;
    }
    var ins=ev.target.closest&&ev.target.closest('[data-insert]');
    if(ins){
      var f=document.querySelector('[data-k="'+ins.dataset.insert+'"]'),t=ins.dataset.text;
      f.value=f.value&&!/\n$/.test(f.value)?f.value+(ins.dataset.insert==='fact'?'\n':''):f.value;
      f.value+=t;state[f.dataset.k]=f.value;save();refresh();f.focus();
    }
  });
  function renderChips(){
    document.querySelectorAll('[data-chips]').forEach(function(host){
      var k=host.dataset.chips,multi=host.hasAttribute('data-multi');
      host.querySelectorAll('[data-v]').forEach(function(b){
        var v=b.dataset.v,on=multi?(state[k]||[]).indexOf(v)>=0:state[k]===v;
        b.classList.toggle('on',on);b.setAttribute('aria-pressed',on?'true':'false');
        var mk=b.querySelector('.mk');if(mk)mk.textContent=on?'✓':'☐';
      });
    });
  }
  // 選訊息
  document.querySelectorAll('[data-pick]').forEach(function(bt){bt.onclick=function(){state.sel=bt.dataset.pick;save();refresh();};});
  function renderCards(){
    document.querySelectorAll('[data-card]').forEach(function(c){
      var on=state.sel===c.dataset.card;c.classList.toggle('on',on);
      var bt=c.querySelector('[data-pick]');bt.textContent=on?'✓ 我選這則':'選這則';
    });
    var s=state.sel&&CARDS[state.sel];
    document.querySelectorAll('[data-selname]').forEach(function(e){e.textContent=s?s.name+'（難度：'+['','簡單','中等','較難'][s.stars]+'）':'還沒選，回到「選訊息」選一則';});
    document.querySelectorAll('[data-hint]').forEach(function(e){e.textContent=s?s.hint:'';});
  }
  // 網址測試連結
  function renderUrlTest(){
    var a=document.querySelector('[data-urltest]');if(!a)return;
    var ok=URL_RE.test(tr(state.url));a.classList.toggle('hidden',!ok);if(ok)a.href=tr(state.url);
  }
  // 檢查表（只是提醒，不是評分）
  function C(ok,t,warn){return {t:t,s:ok?'ok':(warn?'warn':'todo')};}
  var JUDGE=/假的|不是真|謠言|不實|造謠|錯誤|誤導|詐騙|騙人|不可信|不要相信|別相信/;
  var CHECKS={
    sel:function(){return [C(!!state.sel,'選了一則訊息')];},
    url:function(){
      var t=tr(state.url),isUrl=URL_RE.test(t),host='';
      if(isUrl){try{host=new URL(t).hostname;}catch(e){}}
      return [C(/^https:\/\//i.test(t),'開頭是 https://'),
        C(isUrl,'只有網址，沒有別的字'),
        C(isUrl&&OK_HOST.test(host),'網址裡有 mygopen 或 tfc-taiwan',isUrl),
        C(isUrl,'按「測試連結」開得到')];
    },
    tool:function(){
      var l=[C(state.toolKinds.length>0,'選了工具')];
      if(hasKw()){
        l.push(C(filled(state.toolB),'寫了輸入的字'));
        if(filled(state.toolB))l.push(C(/查核/.test(state.toolB),'最後要加「查核」',true));
      }
      return l;
    },
    desc:function(){
      var t=tr(state.desc),m=t.match(JUDGE);
      var l=[C(t.length>=30,'寫了一兩句（30 字以上）'),
        C(/流傳|LINE|Line|臉書|FB|IG|Threads|YouTube|TikTok|抖音|網路|群組|轉傳|社群|傳/.test(t),'說了在哪裡流傳')];
      if(m)l.push(C(false,'有「'+m[0]+'」：是你的判斷就刪掉',true));
      else l.push(C(t.length>0,'沒有寫真的假的'));
      return l;
    },
    res:function(){
      return [C(filled(state.resOrg),'選了哪一家'),C(filled(state.resLabel),'選了標籤'),
        C(tr(state.resNote).length>=10,'寫了一句重點')];
    },
    fact:function(){
      var t=tr(state.fact),lines=t.split(/\n+/).filter(filled),long=lines.some(function(x){return x.length>110;});
      return [C(t.length>=20,'寫了一點事實'),
        C(/根據|說|表示|指出|MyGoPen|查核中心|警方|165|衛福|專家|機構|官方|消防|氣象/.test(t),'寫了是誰說的'),
        long?C(false,'有一句太長，改成自己的話',true):C(t.length>0,'用自己的話，一點一句')];
    },
    why:function(){
      var t=tr(state.whyText);
      return [C(t.length>=15,'寫了為什麼想轉傳'),
        C(/怕|擔心|緊張|恐慌|好奇|驚奇|厲害|神奇|想幫|幫忙|關心|家人|救人|好康|免費|便宜|搶|相信|信任|朋友|親友|感動|生氣|有趣/.test(t),'說了讓人有什麼感覺',t.length>0)];
    },
    risk:function(){
      var t=tr(state.riskText);
      return [C(/有人|我|大家|家人|別人|老人|長輩|學生|小孩|同學|朋友|民眾|他們|人們|陌生人|消費者|媽媽|爸爸|阿公|阿嬤/.test(t),'寫了「誰」'),
        C(t.length>=15,'寫了「會怎樣」')];
    }
  };
  function renderChecks(){
    document.querySelectorAll('[data-checks]').forEach(function(ul){
      var f=CHECKS[ul.dataset.checks];if(!f)return;
      ul.innerHTML=f().map(function(c){return '<li class="ck-'+c.s+'"><span class="ckm">'+(c.s==='ok'?'✓':c.s==='warn'?'!':'☐')+'</span><span>'+esc(c.t)+'</span></li>';}).join('');
    });
  }
  function renderProgress(){
    var n=starCount(),t=REPORT.length;
    $('progTxt').innerHTML='<b style="color:#f59e0b">★</b> '+n+'／'+t;$('progBar').style.width=Math.round(n/t*100)+'%';
  }
  // ===== 收集星星：一欄寫好且文字超過 5 個字就拿到一顆 ★ =====
  // 星星門檻（老師口頭提醒內容品質）：該欄必填的都有寫，而且要寫的字「超過 5 個字」（空白不算）就給星星。
  // 檢查表照樣顯示當提醒，但不再擋星星。選項類的欄（只選工具）不需要字數。
  var STAR_MIN=5;
  function starText(qid){
    var s=state;
    switch(qid){
      case 'url':return s.url;
      case 'tool':return hasKw()?s.toolB:null;
      case 'desc':return s.desc;
      case 'res':return s.resNote;
      case 'fact':return s.fact;
      case 'why':return s.whyText;
      case 'risk':return s.riskText;
    }
    return null;
  }
  function starOf(qid){
    if(!DONE[qid]())return false;
    var t=starText(qid);
    return t==null||tr(t).replace(/\s/g,'').length>STAR_MIN;
  }
  function starCount(){return REPORT.filter(function(q){return starOf(q.qid);}).length;}
  var STAR_SEEN={},starLive=false,starT;   // starLive=false 時（載入、拿回進度）只記錄不慶祝
  function renderStars(){
    var n=starCount(),t=REPORT.length,fresh=null;
    document.querySelectorAll('[data-star]').forEach(function(x){var ok=starOf(x.dataset.star);x.className='starbadge'+(ok?' got':'');x.textContent=ok?'★ 拿到這顆星了':'☆ 寫超過 5 個字，就拿到 ★';});
    document.querySelectorAll('[data-star-mini]').forEach(function(x){var ok=starOf(x.dataset.starMini);x.textContent=ok?'★':'☆';x.classList.toggle('on',ok);});
    var f=$('starFinal');if(f)f.textContent='你收集了 '+n+'／'+t+' 顆 ★'+(n===t?'，全部收集完成！':'。');
    REPORT.forEach(function(q){if(starOf(q.qid)&&!STAR_SEEN[q.qid]){STAR_SEEN[q.qid]=true;fresh=q;}});
    if(fresh&&starLive&&!REVIEW_ID)starPop(fresh,n,t);
  }
  function starPop(q,n,t){
    var old=$('starPop');if(old)old.remove();
    var p=el('div','');p.id='starPop';p.setAttribute('role','status');
    p.innerHTML='<span class="big">★</span><b class="cute" style="font-size:1.5rem;color:#b45309">拿到第 '+n+' 顆星！</b>'
      +'<div style="font-weight:700;color:#78350f">'+esc(q.name)+' 完成'+(n===t?'<br>7 顆全收集！去「預覽」看看你的報告':'・還差 '+(t-n)+' 顆')+'</div>';
    document.body.appendChild(p);clearTimeout(starT);starT=setTimeout(function(){p.remove();},n===t?3500:2200);
  }
  function renderSummary(){
    var host=$('sumList');if(!host)return;host.innerHTML='';
    REPORT.forEach(function(q,i){
      var ok=DONE[q.qid](),row=el('div','flex items-center gap-3 flex-wrap bg-'+(ok?'emerald':'slate')+'-50 border-2 border-'+(ok?'emerald':'slate')+'-200 rounded-2xl px-4 py-2');
      row.innerHTML='<span class="font-extrabold text-lg flex-1">'+(i+1)+' ‧ '+esc(q.name)+'</span><span class="font-bold '+(ok?'text-emerald-700':'text-amber-700')+'">'+(ok?'✓ 寫好了':'還沒寫完')+'</span><span class="starmini'+(starOf(q.qid)?' on':'')+'" style="font-size:1.4rem">'+(starOf(q.qid)?'★':'☆')+'</span>';
      var b=el('button','bg-white border-2 border-slate-300 hover:border-indigo-400 text-slate-600 font-bold rounded-xl px-3 py-1',ok?'再看看':'去寫');b.type='button';b.onclick=function(){showStep(q.step);};
      row.appendChild(b);host.appendChild(row);
    });
  }
  function partOpen(k){
    if(REVIEW_ID||(state.open&&state.open[k]))return true;
    if(k==='find')return filled(state.url);
    return !!(DONE[k]&&given(k));
  }
  function renderParts(){
    document.querySelectorAll('[data-part]').forEach(function(p){p.classList.toggle('hidden',!partOpen(p.dataset.part));});
    document.querySelectorAll('[data-open]').forEach(function(b){b.classList.toggle('hidden',partOpen(b.dataset.open));});
  }
  document.addEventListener('click',function(ev){
    var b=ev.target.closest&&ev.target.closest('[data-open]');if(!b)return;
    var k=b.dataset.open;state.open=state.open||{};state.open[k]=true;save();refresh();
    scrollToEl(document.querySelector('[data-part="'+k+'"]'));
  });
  function scrollToEl(el){
    if(!el)return;var bar=document.querySelector('.sticky');var off=(bar?bar.offsetHeight:0)+16;
    window.scrollTo({top:el.getBoundingClientRect().top+window.pageYOffset-off,behavior:'smooth'});
  }
  document.addEventListener('click',function(ev){
    var b=ev.target.closest&&ev.target.closest('[data-review]');if(!b)return;
    var d=document.querySelector('[data-demo="'+b.dataset.review+'"]');if(!d)return;
    scrollToEl(d);
    d.querySelectorAll('video').forEach(function(v){try{v.currentTime=0;var p=v.play();if(p&&p.catch)p.catch(function(){});}catch(x){}});
    d.classList.remove('flash');void d.offsetWidth;d.classList.add('flash');
  });
  // 原始內容描述：把選的訊息（圖或影片）放到寫的地方，依種類換引導與句型
  var lastSelMedia='?';
  function selKind(){
    if(!state.sel)return 'none';
    var c=document.querySelector('[data-card="'+state.sel+'"]');
    return c&&!c.querySelector('img.shotimg')&&c.querySelector('video')?'video':'img';
  }
  function renderSelMedia(){
    var k=selKind();
    document.querySelectorAll('[data-forkind]').forEach(function(x){x.classList.toggle('hidden',x.dataset.forkind!==k);});
    if(lastSelMedia===state.sel)return;lastSelMedia=state.sel;
    document.querySelectorAll('[data-selmedia]').forEach(function(box){
      box.innerHTML='';var c=state.sel&&document.querySelector('[data-card="'+state.sel+'"]');if(!c)return;
      var m=c.querySelector('img.shotimg')||c.querySelector('video');if(!m)return;
      var n=m.cloneNode(true);n.removeAttribute('loading');n.classList.remove('mt-3');if(n.tagName==='VIDEO')n.setAttribute('preload','metadata');
      box.appendChild(n);
    });
  }
  function renderToolFields(){document.querySelectorAll('[data-kwonly]').forEach(function(n){n.classList.toggle('hidden',!hasKw());});}
  // ===== 預覽全部內容：7 欄排成一份報告（只讀，內容全部經 esc 跳脫）=====
  function renderPreview(){
    var host=$('previewBox');if(!host)return;
    var s=state,none='<p class="m-0 text-amber-700 font-bold">（還沒寫）</p>';
    function pv(label,val){return filled(val)?'<p class="m-0 mt-1"><b class="text-slate-500">'+label+'</b><span style="white-space:pre-wrap">'+esc(tr(val))+'</span></p>':'';}
    function body(qid){
      switch(qid){
        case 'url':return filled(s.url)?(URL_RE.test(tr(s.url))?'<p class="m-0"><a href="'+esc(tr(s.url))+'" target="_blank" rel="noopener" class="underline break-all text-indigo-700">'+esc(tr(s.url))+'</a></p>':pv('',s.url)):'';
        case 'tool':return pv('工具：',s.toolKinds.join('、'))+(hasKw()?pv('我輸入的是：',s.toolB):'');
        case 'desc':return pv('',s.desc);
        case 'res':return pv('機構：',s.resOrg)+pv('標籤：',s.resLabel)+pv('重點：',s.resNote);
        case 'fact':return pv('',s.fact);
        case 'why':return pv('原因類型：',s.whyKinds.join('、'))+pv(s.whyKinds.length?'理由：':'',s.whyText);
        case 'risk':return pv('後果類型：',s.riskKinds.join('、'))+pv(s.riskKinds.length?'誰會怎樣：':'',s.riskText);
      }
      return '';
    }
    host.innerHTML='';
    var selName=s.sel&&CARDS[s.sel]?CARDS[s.sel].name:'';
    var head=el('div','pb-3 border-b-2 border-dashed border-emerald-200 flex items-center gap-2 flex-wrap');
    head.innerHTML='<div class="flex-1 min-w-0"><p class="cute text-2xl font-extrabold text-emerald-700 m-0">查證報告</p><p class="m-0 text-lg">我查的訊息：'+(selName?'<b>'+esc(selName)+'</b>':'<span class="text-amber-700 font-bold">（還沒選）</span>')+'</p><p class="m-0 text-lg font-extrabold text-amber-700">我收集到 <span style="color:#f59e0b">★</span> '+starCount()+'／'+REPORT.length+'</p></div>';
    var hb=el('button','bg-white border-2 border-slate-300 hover:border-indigo-400 text-slate-600 font-bold rounded-xl px-3 py-1',selName?'換一則':'去選');hb.type='button';hb.onclick=function(){showStep(QMAP.sel.step);};head.appendChild(hb);
    host.appendChild(head);
    REPORT.forEach(function(q,i){
      var ok=DONE[q.qid](),html=body(q.qid),box=el('div','border-2 rounded-2xl p-4 '+(ok?'border-emerald-200 bg-emerald-50':'border-amber-300 bg-amber-50'));
      box.innerHTML='<div class="flex items-center gap-2 flex-wrap"><p class="cute text-xl font-extrabold m-0 flex-1">'+(i+1)+' ‧ '+esc(q.name)+'</p>'
        +'<span class="font-bold text-sm '+(ok?'text-emerald-700':'text-amber-700')+'">'+(ok?'✓ 寫好了':'還沒寫完')+'</span><span class="starmini'+(starOf(q.qid)?' on':'')+'" style="font-size:1.4rem">'+(starOf(q.qid)?'★':'☆')+'</span></div>'
        +'<div class="text-lg text-slate-800 mt-1">'+(html||none)+'</div>';
      var b=el('button','mt-2 bg-white border-2 border-slate-300 hover:border-indigo-400 text-slate-600 font-bold rounded-xl px-3 py-1',html?'去改':'去寫');b.type='button';b.onclick=function(){showStep(q.step);};
      box.appendChild(b);host.appendChild(box);
    });
  }
  function refresh(){renderChips();renderParts();renderToolFields();renderSelMedia();renderPreview();renderCards();renderUrlTest();renderChecks();renderProgress();renderSummary();renderStepper();renderStars();}
  function renderAll(){fillFields();refresh();}

  // ===== 題型（預設＋老師即時切換，§5-6）=====
  var QTYPE_OVERRIDES={},QTYPE_CYCLE=['experience','score','open'];
  var QTYPE_LABEL={score:'檢測',experience:'體驗',open:'開放'};
  var QTYPE_STYLE={score:'bg-rose-100 text-rose-700 border-rose-300',experience:'bg-sky-100 text-sky-700 border-sky-300',open:'bg-emerald-100 text-emerald-700 border-emerald-300'};
  function qtypeOf(qid){return QTYPE_OVERRIDES[qid]||QMAP[qid].type;}
  var teacherAuthed=false;
  function renderQtypeSlots(){
    document.querySelectorAll('.qtypeSlot').forEach(function(slot){
      var qid=slot.dataset.qid,t=qtypeOf(qid);
      if(!IS_ADMIN||!teacherAuthed||REVIEW_ID){slot.innerHTML='';return;}
      slot.innerHTML='<button type="button" class="border rounded-full px-2 py-0.5 text-xs font-bold '+QTYPE_STYLE[t]+'" title="點一下切換題型">'+QTYPE_LABEL[t]+'</button>';
      slot.firstChild.onclick=function(){
        QTYPE_OVERRIDES[qid]=QTYPE_CYCLE[(QTYPE_CYCLE.indexOf(qtypeOf(qid))+1)%QTYPE_CYCLE.length];renderQtypeSlots();
        if(quizRef)quizRef.set({qtypeOverrides:QTYPE_OVERRIDES},{merge:true}).catch(function(e){alert('題型存不進去：'+e.message);});
      };
    });
  }

  // ===== 繳交（正式繳交＋斷點繳交共用同一條路，§2-b、§3、§3-b）=====
  function buildPayload(idn,mode){
    var answers={},qtypes={},scoreAnswers={},experienceAnswers={},openAnswers={},qtexts={};
    var sT=0,sC=0,eT=0,eA=0;
    Q.forEach(function(q){
      var t=qtypeOf(q.qid),g=given(q.qid),item={given:g||null,correct:null,isCorrect:DONE[q.qid]()};
      qtypes[q.qid]=t;answers[q.qid]=g||null;
      if(q.text)qtexts[q.qid]=q.text;
      if(t==='open'){openAnswers[q.qid]=g;}
      else if(t==='experience'){experienceAnswers[q.qid]=item;eT++;if(filled(g))eA++;}
      else{scoreAnswers[q.qid]=item;sT++;if(item.isCorrect)sC++;}
    });
    var parts=JSON.parse(JSON.stringify(state));
    return {worksheetId:WS,worksheetTitle:TITLE,lessonPath:LESSON_PATH,
      grade:idn.grade,className:idn.className,studentId:idn.studentId,
      answers:answers,qtypes:qtypes,qtexts:qtexts,
      scoreAnswers:scoreAnswers,experienceAnswers:experienceAnswers,openAnswers:openAnswers,
      accuracyRate:sT?Math.round(sC/sT*100):null,experienceCompletion:eT?Math.round(eA/eT*100):null,
      checkpoint:{final:!!mode.final,step:mode.final?STEP_NAMES.length:curStep,stepName:STEP_NAMES[(mode.final?STEP_NAMES.length:curStep)-1],done:doneCount(),total:REPORT.length},
      parts:parts,status:'submitted'};
  }
  var submittedOnce=false,pendingCk=null;
  // 每個節點的「先存檔交一次」：走同一顆 #submitBtn（靠椅子關卡才攔得到），用 pendingCk 標記是斷點
  document.querySelectorAll('[data-ckpt]').forEach(function(box){
    box.innerHTML='<div class="flex items-center gap-3 flex-wrap"><button type="button" class="ckBtn">先存檔交一次</button><span class="ckStat text-sm font-bold"></span></div>'
      +'<p class="text-sm text-slate-600 mt-2 mb-0">寫不完先按，下次用同樣的年級、班級、座號拿回來。</p>';
    box.querySelector('.ckBtn').onclick=function(){pendingCk={final:false};$('submitBtn').click();};
  });
  $('submitBtn').addEventListener('pointerdown',function(){pendingCk=null;},true);   // 真的用滑鼠按最後一步的鈕＝正式繳交
  $('submitBtn').addEventListener('keydown',function(){pendingCk=null;},true);
  function setStat(t,cls){
    document.querySelectorAll('.ckStat').forEach(function(e){e.textContent=t;e.className='ckStat text-sm font-bold '+cls;});
    var s=$('submitStat');s.className='text-sm font-bold mt-3 min-h-[20px] '+cls;s.textContent=t;
  }
  function setBusy(b){document.querySelectorAll('.ckBtn').forEach(function(x){x.disabled=b;});$('submitBtn').disabled=b;}
  $('submitBtn').onclick=function(){
    var mode=pendingCk||{final:true};pendingCk=null;
    var idn=getIdentity();
    if(!identityValid(idn)){markIdentity(true);failModal('還不能繳交！',ID_MSG,true);return;}
    markIdentity(false);
    if(!db){failModal('繳交失敗！','現在連不上網路。請檢查網路後再按一次；還是不行就舉手告訴老師。');return;}
    var n=doneCount(),head=mode.final?'確定要繳交整份學習單嗎？':'要先存檔交一次嗎？';
    var lines=['選的訊息：'+(state.sel&&CARDS[state.sel]?CARDS[state.sel].name:'還沒選'),'報告已完成：'+n+'／'+REPORT.length+' 欄'];
    if(!mode.final)lines.push('目前在第 '+curStep+' 步。下次輸入同樣的年級、班級、座號，就能拿回來接著寫。');
    if(!confirm(head+'\n\n'+lines.join('\n')+'\n\n送出後老師會看到，確定要交嗎？'))return;
    var payload=buildPayload(idn,mode);payload.submittedAt=firebase.firestore.FieldValue.serverTimestamp();
    save();setBusy(true);setStat('繳交中…','text-indigo-600');
    authResolved.then(function(){return ensureAuth();})
      .then(function(){return db.collection('submissions').doc(WS+'__'+idKey(idn)).set(payload,{merge:true});})
      .then(function(){
        setBusy(false);
        saveProgress(idn);
        if(mode.final){
          submittedOnce=true;$('submitBtn').textContent='重新繳交（覆蓋）';renderStepper();
          setStat('✓ 已繳交。可再按一次覆蓋更新。','text-emerald-600');
          var rb=$('rewardBox');rb.classList.remove('hidden');rb.scrollIntoView({behavior:'smooth'});
        }else{
          setStat('✓ 已存檔繳交（第 '+curStep+' 步，'+n+'／'+REPORT.length+' 欄）。','text-emerald-600');
          toast('已存檔繳交 ✓ 下次輸入年級、班級、座號就能拿回來');
        }
      }).catch(function(e){
        console.warn('繳交失敗',e);setBusy(false);setStat('','');
        failModal('繳交失敗！','請檢查 <b style="color:#e11d48">年級、班級、座號</b> 有沒有寫好，網路是否正常，再按一次；還是不行就舉手告訴老師。',true);
      });
  };

  // ===== 教師模式（§5）=====
  var PREVIEW_KEY='wk_previewMode';
  var SAMPLE={sel:'C',url:'https://www.mygopen.com/2026/02/ai-fraud.html',
    toolKinds:['關鍵字搜尋'],toolB:'陌生人 操作手機 生物特徵 查核',
    desc:'網傳訊息說：只要幫路上的陌生人操作手機、摸螢幕、對著鏡頭說話，指紋、聲音和臉就會被偷走，騙子拿去貸款，30 分鐘就傾家蕩產。這則訊息在臉書流傳。',
    resOrg:'MyGoPen 麥擱騙',resLabel:'誤導',resNote:'MyGoPen 查核後標為「誤導」，重點是這個說法在技術和金融上都不合理。',
    fact:'1. 根據 MyGoPen，只有指紋或臉，不能直接拿去貸款，銀行還要看很多檢查。\n2. 警方和 165 說，台灣查不到這種案件。\n3. 不過，陌生人要你做驗證時，還是要小心。',
    whyText:'訊息說「30 分鐘傾家蕩產」，讓人怕；又寫「轉傳給家人朋友」，大家覺得轉傳是關心家人。',
    riskText:'有人怕到不敢幫真的需要幫忙的人；也有人把嚇人的訊息再轉給更多人，讓大家一起害怕。'};
  if(!IS_ADMIN){try{if(sessionStorage.getItem(PREVIEW_KEY)==='1')$('backToTeacher').classList.remove('hidden');}catch(e){}}
  $('previewModeBtn').onclick=function(){
    if(!confirm('會清空這台裝置上的身分（年級/班級/座號）與作答，變回全新學生的畫面，確定要預覽嗎？'))return;
    try{localStorage.removeItem(ID_KEY);localStorage.removeItem(STATE_KEY);sessionStorage.setItem(PREVIEW_KEY,'1');}catch(e){}
    location.href=location.pathname;
  };
  $('backToTeacher').onclick=function(){
    try{sessionStorage.removeItem(PREVIEW_KEY);}catch(e){}
    location.href=location.pathname+location.search+'#admin';location.reload();
  };
  function wireTeacher(label){
    $('teacherbar').classList.remove('hidden');$('tStatus').textContent=label;teacherAuthed=true;renderQtypeSlots();
    if(REVIEW_ID){loadReview();return;}
    ['showAnsBtn','lockBtn'].forEach(function(id){$(id).classList.remove('hidden');});
    $('showAnsBtn').onclick=function(){state=Object.assign(freshState(),JSON.parse(JSON.stringify(SAMPLE)));starLive=false;save();renderAll();starLive=true;};
    $('lockBtn').onclick=function(){
      if(!confirm('確定要還原嗎？\n會清掉「檢視答案」填進去的內容。\n學生已經繳交的學習單不受影響。'))return;
      state=freshState();save();renderAll();
    };
  }
  function teacherOnline(){
    authResolved.then(function(u){
      if(u&&!u.isAnonymous&&u.email){wireTeacher('已登入 '+u.email);return;}
      var email=prompt('教師 Email：',TEACHER_EMAIL);if(email===null)return;
      var pw=prompt('密碼：');if(pw===null)return;
      auth.signInWithEmailAndPassword(email,pw).then(function(c){wireTeacher('已登入 '+c.user.email);})
        .catch(function(e){alert('登入失敗：'+e.message);});
    });
  }
  function teacherOffline(){
    var pw=prompt('教師密碼：');if(pw!=='1234'){if(pw!==null)alert('密碼錯誤');return;}
    wireTeacher('單機模式（題型只影響這台）');
  }
  // 檢視學生繳交（唯讀重現，§5-7）
  function loadReview(){
    $('reviewBanner').classList.remove('hidden');$('reviewExit').href=location.pathname+'#admin';
    $('submitBtn').classList.add('hidden');$('rewardBox').remove();
    document.querySelectorAll('[data-ckpt]').forEach(function(b){b.remove();});
    if(!db){$('reviewText').textContent='檢視模式：現在連不上資料庫';return;}
    db.collection('submissions').doc(REVIEW_ID).get().then(function(doc){
      if(!doc.exists){$('reviewText').textContent='檢視模式：找不到這份繳交';return;}
      var d=doc.data()||{},ck=d.checkpoint||{};
      $('reviewText').textContent='檢視模式（唯讀）：'+d.grade+'年'+d.className+'班'+d.studentId+'號 的作答'+(ck.final===false?'（斷點繳交：存在第 '+ck.step+' 步，'+ck.done+'／'+ck.total+' 欄）':'');
      $('idGrade').value=d.grade||'';$('idClass').value=d.className||'';$('idStudent').value=d.studentId||'';
      if(d.qtypes)QTYPE_OVERRIDES=d.qtypes;
      state=Object.assign(freshState(),d.parts||{});
      renderAll();
      $('main').classList.add('locked');
      document.querySelectorAll('#main input,#main textarea,#idGrade,#idClass,#idStudent').forEach(function(f){f.disabled=true;});
    }).catch(function(e){console.warn('讀取繳交失敗',e);$('reviewText').textContent='檢視模式：讀取失敗';});
  }

  // ===== 學習路徑：一次只顯示一步，頂端進度列可以跳步 =====
  var stepEls=[].slice.call(document.querySelectorAll('.step'));
  var curStep=1,visited={1:true};
  function stepDone(n){
    var q=STEP_Q[n];if(q)return DONE[q]();
    if(n===STEP_NAMES.length)return submittedOnce;
    return !!visited[n]&&n!==curStep;
  }
  function renderStepper(){
    var host=$('stepper');host.innerHTML='';
    STEP_NAMES.forEach(function(name,idx){
      var n=idx+1,cur=n===curStep,done=stepDone(n);
      var cell=el('div','flex flex-col items-center');
      var b=el('button','stepdot cute rounded-full border-2 font-extrabold text-sm flex items-center justify-center transition '+
        (cur?'bg-indigo-600 border-indigo-600 text-white':(done?'bg-emerald-500 border-emerald-500 text-white':'bg-white border-slate-300 text-slate-400 hover:border-indigo-300')));
      b.type='button';b.textContent=done&&!cur?'✓':String(n);
      b.setAttribute('aria-label','第 '+n+' 步：'+name);
      if(cur)b.setAttribute('aria-current','step');
      b.onclick=function(){showStep(n);};
      cell.appendChild(b);
      cell.appendChild(el('span','hidden lg:block text-xs font-bold mt-0.5 '+(cur?'text-indigo-700':'text-slate-400'),name));
      host.appendChild(cell);
      if(n<STEP_NAMES.length)host.appendChild(el('div','flex-1 h-0.5 mt-3.5 sm:mt-4 mx-0.5 sm:mx-1 rounded '+(done&&!cur?'bg-emerald-300':'bg-slate-200')));
    });
    $('stepLabel').textContent='第 '+curStep+' 步／共 '+STEP_NAMES.length+' 步 · '+STEP_NAMES[curStep-1];
  }
  function showStep(n){
    curStep=n;visited[n]=true;pendingCk=null;
    stepEls.forEach(function(s){s.classList.toggle('hidden',Number(s.dataset.step)!==n);});
    save();refresh();
    window.scrollTo({top:0,behavior:'smooth'});
  }
  stepEls.forEach(function(s){
    var n=Number(s.dataset.step),nav=s.querySelector('.stepnav');
    if(n>1){var p=el('button','bg-white border-2 border-slate-300 hover:border-indigo-400 text-slate-600 font-bold rounded-2xl px-5 py-2','← 上一步');p.type='button';p.onclick=function(){showStep(n-1);};nav.appendChild(p);}
    else nav.appendChild(el('span',''));
    if(n<STEP_NAMES.length){var x=el('button','cute bg-indigo-600 hover:bg-indigo-700 text-white text-lg font-extrabold rounded-2xl px-6 py-2','下一步：'+STEP_NAMES[n]+' →');x.type='button';x.onclick=function(){showStep(n+1);};nav.appendChild(x);}
  });

  bindFields();renderAll();starLive=true;
  curStep=1;stepEls.forEach(function(s){s.classList.toggle('hidden',Number(s.dataset.step)!==1);});renderStepper();

  fbReady.then(function(){
    if(!quizRef){if(IS_ADMIN)teacherOffline();return;}
    quizRef.onSnapshot(function(doc){
      var d=(doc&&doc.data())||{};
      if(d.qtypeOverrides&&!REVIEW_ID){QTYPE_OVERRIDES=d.qtypeOverrides;renderQtypeSlots();}
    },function(e){console.warn('讀取題型設定失敗',e);});
    if(IS_ADMIN)teacherOnline();
  });

})();
