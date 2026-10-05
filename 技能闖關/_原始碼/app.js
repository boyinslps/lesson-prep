/* ============================================================
   電腦急救站｜共用程式（地圖頁、關卡頁都用這一份）
   ------------------------------------------------------------
   window.SITE 由 build.py 注入：{config, levels:[...], base}
   紀錄：localStorage「skillQuest_年-班-座」＋ Firestore skillQuest/{年-班-座}
   ============================================================ */
(function(){
  var SITE = window.SITE, CFG = SITE.config, LEVELS = SITE.levels;
  var ID_KEY = 'wk_identity';
  function $(id){return document.getElementById(id);}
  function digits(s){return String(s||'').replace(/\D/g,'');}
  var Q = window.Quest = {levels: LEVELS, config: CFG};
  Q.byCode = {}; LEVELS.forEach(function(l){Q.byCode[l.code]=l;});

  /* ---------- 小工具 ---------- */
  var toastT;
  Q.toast = function(t){var e=$('toast');if(!e)return;e.textContent=t;e.classList.add('on');clearTimeout(toastT);toastT=setTimeout(function(){e.classList.remove('on');},2400);};
  Q.icon = function(name,cls){return '<svg class="ico'+(cls?' '+cls:'')+'"><use href="#i-'+name+'"/></svg>';};
  Q.esc = function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};

  /* ---------- 身分（年級／班級／座號）---------- */
  Q.getId = function(){
    var s={};try{s=JSON.parse(localStorage.getItem(ID_KEY)||'{}')||{};}catch(e){}
    return {grade:+s.grade||0, className:+s.className||0, studentId:+s.studentId||0};
  };
  Q.idValid = function(i){i=i||Q.getId();return i.grade>=3&&i.grade<=6&&i.className>=1&&i.className<=20&&i.studentId>=1&&i.studentId<=40;};
  Q.docId = function(i){i=i||Q.getId();return i.grade+'-'+i.className+'-'+i.studentId;};
  function setId(i){try{localStorage.setItem(ID_KEY,JSON.stringify(i));}catch(e){}}

  /* ---------- 紀錄 ---------- */
  var PROG = {levels:{}, certs:{}};
  function lkey(){return 'skillQuest_'+Q.docId();}
  function readLocal(){try{var o=JSON.parse(localStorage.getItem(lkey())||'{}')||{};return {levels:o.levels||{},certs:o.certs||{}};}catch(e){return {levels:{},certs:{}};}}
  function writeLocal(){try{localStorage.setItem(lkey(),JSON.stringify(PROG));}catch(e){}}
  Q.progress = function(){return PROG;};
  Q.passed = function(code){return !!PROG.levels[code];};
  Q.status = function(code){
    if(Q.passed(code))return 'passed';
    var l=Q.byCode[code];
    return (l.prereq||[]).every(Q.passed)?'open':'locked';
  };

  /* ---------- 證書條件 ---------- */
  Q.certOpen = function(c){return LEVELS.length>=((c.rule||{}).minLevels||0);};
  Q.certMet = function(c){
    var r=c.rule||{}, lv=LEVELS;
    if(!Q.certOpen(c))return false;
    if(r.all&&!lv.every(function(l){return Q.passed(l.code);}))return false;
    if(r.core&&!lv.filter(function(l){return l.core;}).every(function(l){return Q.passed(l.code);}))return false;
    if(r.perCategory){
      var ok=CFG.categories.every(function(cat){
        var inCat=lv.filter(function(l){return l.category===cat.id;});
        if(!inCat.length)return true;
        var need=Math.min(r.perCategory,inCat.length);
        return inCat.filter(function(l){return Q.passed(l.code);}).length>=need;
      });
      if(!ok)return false;
    }
    return true;
  };
  function certCode(cid){
    var s=Q.docId()+'|'+cid+'|'+Date.now(), h=0;
    for(var k=0;k<s.length;k++){h=(h*31+s.charCodeAt(k))>>>0;}
    return cid+'-'+h.toString(36).toUpperCase().slice(-6);
  }
  // 條件達成就頒發；頒發後永久保留（之後新增關卡也不會收回）
  Q.awardCerts = function(){
    var fresh=[];
    CFG.certs.forEach(function(c){
      if(!PROG.certs[c.id]&&Q.certMet(c)){
        PROG.certs[c.id]={awardedAt:Date.now(),code:certCode(c.id),levelSnapshot:LEVELS.map(function(l){return l.code;})};
        fresh.push(c);
      }
    });
    return fresh;
  };

  /* ---------- Firebase ---------- */
  var db=null,auth=null;
  function loadScript(src){return new Promise(function(res,rej){var s=document.createElement('script');s.src=src;s.onload=res;s.onerror=rej;document.head.appendChild(s);});}
  var fbReady=new Promise(function(resolve){
    if(!CFG.firebase||location.protocol==='file:'){resolve(false);return;}
    var base='https://www.gstatic.com/firebasejs/10.8.0/';
    loadScript(base+'firebase-app-compat.js')
      .then(function(){return loadScript(base+'firebase-auth-compat.js');})
      .then(function(){return loadScript(base+'firebase-firestore-compat.js');})
      .then(function(){if(!firebase.apps.length)firebase.initializeApp(CFG.firebase);db=firebase.firestore();auth=firebase.auth();resolve(true);})
      .catch(function(e){console.warn('Firebase 載入失敗，改成只存在這台電腦',e);resolve(false);});
  });
  function ensureAuth(){return auth.currentUser?Promise.resolve(auth.currentUser):auth.signInAnonymously().then(function(c){return c.user;});}
  function coll(){return db.collection(CFG.collection||'skillQuest');}

  function stat(cls,t){var e=$('saveStat');if(!e)return;e.className='pill'+(cls?' '+cls:'');e.textContent=t;}

  // 雲端與本機合併：關卡取「最早過關」那筆；證書取最早頒發那筆
  function merge(a,b){
    Object.keys(b||{}).forEach(function(k){if(!a[k]||(b[k].passedAt||b[k].awardedAt||0)<(a[k].passedAt||a[k].awardedAt||0))a[k]=b[k];});
    return a;
  }

  var listeners=[];
  Q.onChange = function(fn){listeners.push(fn);fn();};
  function emit(){listeners.forEach(function(fn){try{fn();}catch(e){console.error(e);}});}

  var loadedFor='';
  Q.load = function(){
    if(!Q.idValid()){PROG={levels:{},certs:{}};stat('warn','先填年級、班級、座號');emit();return Promise.resolve();}
    var id=Q.docId();loadedFor=id;
    PROG=readLocal();emit();
    stat('','讀取中…');
    return fbReady.then(function(ok){
      if(!ok){stat('warn','紀錄存在這台電腦');return;}
      return ensureAuth().then(function(){return coll().doc(id).get();}).then(function(doc){
        if(loadedFor!==id)return;
        var c=doc.exists?doc.data():{};
        merge(PROG.levels,c.levels);merge(PROG.certs,c.certs);
        writeLocal();emit();
        stat('ok','已連上雲端');
        // 本機有、雲端沒有的（例如之前離線過關）補上傳
        var needPush=Object.keys(PROG.levels).some(function(k){return !(c.levels||{})[k];})||Object.keys(PROG.certs).some(function(k){return !(c.certs||{})[k];});
        if(needPush)return push();
      });
    }).catch(function(e){console.warn('讀取失敗',e);stat('bad','雲端讀不到，先存在這台電腦');});
  };
  function push(){
    var i=Q.getId();
    return fbReady.then(function(ok){
      if(!ok){stat('warn','紀錄存在這台電腦');return false;}
      var payload={grade:i.grade,className:i.className,studentId:i.studentId,levels:PROG.levels,certs:PROG.certs,updatedAt:firebase.firestore.FieldValue.serverTimestamp()};
      return ensureAuth().then(function(){return coll().doc(Q.docId(i)).set(payload,{merge:true});})
        .then(function(){stat('ok','已存到雲端');return true;})
        .catch(function(e){console.warn('雲端存檔失敗',e);stat('bad','雲端沒存到，先存在這台電腦');return false;});
    });
  }

  // 過關：記錄＋檢查證書。回傳 {fresh:[新拿到的證書]}
  Q.recordPass = function(code,info){
    if(!Q.idValid())return Promise.resolve({fresh:[],noId:true});
    if(!PROG.levels[code])PROG.levels[code]={passedAt:Date.now(),tries:info.tries||1,seconds:Math.round(info.seconds||0)};
    var fresh=Q.awardCerts();
    writeLocal();emit();
    return push().then(function(){return {fresh:fresh};});
  };

  /* ---------- 身分欄位 ---------- */
  Q.initIdBar = function(){
    if(!$('idG'))return Q.load();
    var s=Q.getId();
    if(s.grade)$('idG').value=s.grade;if(s.className)$('idC').value=s.className;if(s.studentId)$('idS').value=s.studentId;
    var t;
    ['idG','idC','idS'].forEach(function(id){
      $(id).addEventListener('input',function(){
        var d=digits(this.value);if(d!==this.value)this.value=d;
        setId({grade:+$('idG').value||0,className:+$('idC').value||0,studentId:+$('idS').value||0});
        clearTimeout(t);t=setTimeout(Q.load,500);
      });
    });
    return Q.load();
  };
})();
