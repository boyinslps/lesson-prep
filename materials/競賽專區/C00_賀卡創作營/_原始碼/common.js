/* ============================================================
   賀卡創作營｜共用程式（六個頁面都一樣）
   ------------------------------------------------------------
   ◆ Firebase：老師建好新專案後，把 firebaseConfig 整段貼到 FB_CONFIG（六個頁面都要換）。
     維持 null＝只存在這台電腦的瀏覽器（換電腦就看不到），頁面其他功能照常。
   ◆ 資料放在 cardWork/{年級-班級-座號}，每一節一個欄位 L1～L5（見 firestore.rules）。
   ============================================================ */
var FB_CONFIG = {
  apiKey: "AIzaSyDxAPNchjR37VsBPO4QltbuNIJ98F3mwtw",
  authDomain: "worksheet-f47f3.firebaseapp.com",
  projectId: "worksheet-f47f3",
  storageBucket: "worksheet-f47f3.firebasestorage.app",
  messagingSenderId: "42265052892",
  appId: "1:42265052892:web:415d41d37b96fd24e61619"
};
var COLL = 'cardWork';

(function(){
  var P = window.PAGE || {};
  var LESSON = P.lesson || '';
  function $(id){return document.getElementById(id);}
  function $$(sel,root){return Array.prototype.slice.call((root||document).querySelectorAll(sel));}
  window.$ = $; window.$$ = $$;

  /* ---------- 小工具 ---------- */
  var toastT;
  function toast(t){var e=$('toast');if(!e)return;e.textContent=t;e.classList.add('on');clearTimeout(toastT);toastT=setTimeout(function(){e.classList.remove('on');},2200);}
  window.toast = toast;
  function copyText(text,btn,doneLabel){
    function ok(){
      if(btn){var old=btn.innerHTML;btn.classList.add('done');btn.innerHTML='<svg class="ico"><use href="#i-check"/></svg>已複製';setTimeout(function(){btn.classList.remove('done');btn.innerHTML=old;},1800);}
      toast(doneLabel||'已複製！〔 〕換成你的內容，句子用你自己的話改一改');
    }
    function fb(){var ta=document.createElement('textarea');ta.value=text;ta.style.cssText='position:fixed;left:-9999px;top:0';document.body.appendChild(ta);ta.select();try{document.execCommand('copy');ok();}catch(e){toast('請按 Ctrl＋C 複製');}document.body.removeChild(ta);}
    try{navigator.clipboard.writeText(text).then(ok,fb);}catch(e){fb();}
  }
  window.copyText = copyText;
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  window.esc = esc;

  /* ---------- 我是誰：年級／班級／座號 ---------- */
  var ID_KEY='card_identity';
  function digits(s){return String(s||'').replace(/[^0-9]/g,'');}
  function getId(){
    var g=digits($('idG')&&$('idG').value),c=digits($('idC')&&$('idC').value),s=digits($('idS')&&$('idS').value);
    return {grade:g?Number(g):null,className:c?Number(c):null,studentId:s?Number(s):null};
  }
  function idValid(i){return i.grade>=3&&i.grade<=6&&i.className>=1&&i.className<=20&&i.studentId>=1&&i.studentId<=40;}
  function docId(i){return i.grade+'-'+i.className+'-'+i.studentId;}
  window.cardIdentity = function(){var i=getId();return idValid(i)?i:null;};

  /* ---------- 存檔狀態 ---------- */
  function stat(kind,text){var e=$('saveStat');if(!e)return;e.className='pill'+(kind?' '+kind:'');e.innerHTML='<svg class="ico"><use href="#i-cloud"/></svg>'+esc(text);}

  /* ---------- 讀寫頁面上的欄位（data-key） ---------- */
  function fieldEls(){return $$('[data-key]');}
  function collect(){
    var o={};
    fieldEls().forEach(function(el){
      var k=el.dataset.key;
      if(el.type==='checkbox'){if(!o[k])o[k]=[];if(el.checked)o[k].push(el.value);}
      else if(el.type==='radio'){if(el.checked)o[k]=el.value;else if(!(k in o))o[k]='';}
      else o[k]=(el.value||'').slice(0,3000);
    });
    return o;
  }
  function isEmptyVal(v){return v==null||v===''||(Array.isArray(v)&&!v.length);}
  function fill(obj,force){
    if(!obj)return;
    fieldEls().forEach(function(el){
      var k=el.dataset.key;if(!(k in obj))return;var v=obj[k];
      if(el.type==='checkbox'){var cur=el.checked;if(force||!$$('[data-key="'+k+'"]').some(function(x){return x.checked;}))el.checked=Array.isArray(v)&&v.indexOf(el.value)>=0;else el.checked=cur;}
      else if(el.type==='radio'){if(force||!$$('[data-key="'+k+'"]').some(function(x){return x.checked;}))el.checked=(v===el.value);}
      else if(force||!el.value.trim())el.value=v||'';
    });
  }

  /* ---------- 全部資料（五節）---------- */
  var ALL={};
  window.cardData = function(){return ALL;};
  function getPath(path){var p=path.split('.'),o=ALL[p[0]]||{};var v=o[p[1]];return Array.isArray(v)?v.join('、'):(v||'');}
  window.cardGet = getPath;
  function updSub(){var e=$('subStat'),b=$('subBtn');if(!e||!LESSON)return;var t=(ALL[LESSON]||{})._sub;if(t){var d=new Date(t);e.className='ss ok';e.textContent='已繳交（'+(d.getMonth()+1)+'/'+d.getDate()+' '+d.getHours()+':'+('0'+d.getMinutes()).slice(-2)+'）。之後再改內容會自動更新。';if(b)b.innerHTML='<svg class="ico"><use href="#i-upload"/></svg>重新繳交';}else{e.className='ss';e.textContent='還沒繳交。這一節做完，按右邊的按鈕交給老師。';if(b)b.innerHTML='<svg class="ico"><use href="#i-upload"/></svg>繳交這一節';}}
  function renderRefs(){
    $$('[data-ref]').forEach(function(el){
      var v=getPath(el.dataset.ref);
      el.textContent=v||(el.dataset.empty||'（還沒寫）');
      el.classList.toggle('empty',!v);
    });
    $$('[data-need]').forEach(function(el){el.hidden=!!getPath(el.dataset.need);});
    if(typeof P.onSub==='function'||true)updSub();
    if(typeof P.onData==='function')try{P.onData(ALL);}catch(e){console.warn(e);}
    if(window.__refreshSteps)window.__refreshSteps();
  }
  window.cardRefresh = function(){ if(LESSON)ALL[LESSON]=Object.assign({},ALL[LESSON]||{},collect());renderRefs(); };

  /* ---------- 本機暫存 ---------- */
  function lkey(i){return 'card_work_'+docId(i);}
  function readLocal(i){try{return JSON.parse(localStorage.getItem(lkey(i))||'{}')||{};}catch(e){return {};}}
  function writeLocal(i,o){try{localStorage.setItem(lkey(i),JSON.stringify(o));}catch(e){}}

  /* ---------- Firebase ---------- */
  var db=null,auth=null,fbReady=null;
  function loadScript(src){return new Promise(function(res,rej){var s=document.createElement('script');s.src=src;s.onload=res;s.onerror=rej;document.head.appendChild(s);});}
  fbReady=new Promise(function(resolve){
    if(!FB_CONFIG){resolve(false);return;}
    var base='https://www.gstatic.com/firebasejs/10.8.0/';
    loadScript(base+'firebase-app-compat.js')
      .then(function(){return loadScript(base+'firebase-auth-compat.js');})
      .then(function(){return loadScript(base+'firebase-firestore-compat.js');})
      .then(function(){if(!firebase.apps.length)firebase.initializeApp(FB_CONFIG);db=firebase.firestore();auth=firebase.auth();resolve(true);})
      .catch(function(e){console.warn('Firebase 載入失敗，改成只存在這台電腦',e);resolve(false);});
  });
  window.cardFirebase = function(){return fbReady.then(function(ok){return ok?{db:db,auth:auth}:null;});};
  function ensureAuth(){return (auth.currentUser)?Promise.resolve(auth.currentUser):auth.signInAnonymously().then(function(c){return c.user;});}

  /* ---------- 載入 ---------- */
  var loadedFor='',loadP=Promise.resolve(),dirty=false;
  function load(force){loadP=doLoad(force)||Promise.resolve();return loadP;}
  function doLoad(force){
    var i=getId();
    if(!idValid(i)){stat('warn','先填年級、班級、座號');return;}
    var id=docId(i);
    var changed=(loadedFor&&loadedFor!==id)||!!force;
    loadedFor=id;
    ALL=readLocal(i);
    fill(ALL[LESSON],changed);
    renderRefs();
    stat('', '讀取中…');
    return fbReady.then(function(ok){
      if(!ok){stat('warn','只存在這台電腦');return;}
      return ensureAuth().then(function(){return db.collection(COLL).doc(id).get();}).then(function(doc){
        if(loadedFor!==id)return;
        var cloud=doc.exists?doc.data():{};
        ['L1','L2','L3','L4','L5'].forEach(function(L){
          var c=cloud[L],l=ALL[L];
          if(c&&(!l||(c._ms||0)>=(l._ms||0)))ALL[L]=c;
        });
        writeLocal(i,ALL);
        fill(ALL[LESSON],changed);
        renderRefs();
        var got=['L1','L2','L3','L4','L5'].map(function(L,k){var d=ALL[L];return d&&Object.keys(d).some(function(x){return x!=='_ms'&&x!=='_sub';})?String(k+1):'';}).filter(Boolean);
        stat('ok',got.length?'已讀回第 '+got.join('、')+' 節的紀錄':(doc.exists?'已連線，還沒有紀錄':'已連線，還沒有紀錄'));
        if(force)toast(got.length?'已讀回你之前的紀錄（第 '+got.join('、')+' 節）':'雲端還沒有你的紀錄');
      });
    }).catch(function(e){console.warn('讀取失敗',e);stat('bad','雲端讀不到，先存在這台電腦');});
  }

  /* ---------- 存檔（打字後自動存）---------- */
  var saveT=null,subTime=0;
  function save(){return loadP.then(doSave);}
  function doSave(){
    var i=getId();
    if(!idValid(i)){stat('warn','先填年級、班級、座號');return Promise.resolve(false);}
    if(!LESSON)return Promise.resolve(false);
    var data=collect();data._ms=Date.now();
    if(subTime)data._sub=subTime;else if(ALL[LESSON]&&ALL[LESSON]._sub)data._sub=ALL[LESSON]._sub;
    ALL[LESSON]=data;
    writeLocal(i,ALL);
    renderRefs();
    return fbReady.then(function(ok){
      if(!ok){stat('warn','已存在這台電腦');return 'local';}
      stat('','存檔中…');
      var payload={grade:i.grade,className:i.className,studentId:i.studentId,updatedAt:firebase.firestore.FieldValue.serverTimestamp()};
      payload[LESSON]=data;
      return ensureAuth().then(function(){return db.collection(COLL).doc(docId(i)).set(payload,{merge:true});})
        .then(function(){var d=new Date();stat('ok','已存到雲端 '+d.getHours()+':'+('0'+d.getMinutes()).slice(-2));return 'cloud';})
        .catch(function(e){console.warn('雲端存檔失敗',e);stat('bad','雲端沒存到，先存在這台電腦');return false;});
    });
  }
  window.cardSave = save;
  function queueSave(){dirty=true;clearTimeout(saveT);saveT=setTimeout(save,1200);}

  /* ---------- 初始化識別列 ---------- */
  (function(){
    if(!$('idG'))return;
    var s={};try{s=JSON.parse(localStorage.getItem(ID_KEY)||'{}')||{};}catch(e){}
    if(s.grade)$('idG').value=s.grade;if(s.className)$('idC').value=s.className;if(s.studentId)$('idS').value=s.studentId;
    ['idG','idC','idS'].forEach(function(id){
      $(id).addEventListener('input',function(){
        var d=digits(this.value);if(d!==this.value)this.value=d;
        var i=getId();
        if(idValid(i)){try{localStorage.setItem(ID_KEY,JSON.stringify(i));}catch(e){}load();}
        else stat('warn','先填年級、班級、座號');
      });
    });
    load();
  })();
  window.cardReload=function(){
    var i=getId();
    if(!idValid(i)){toast('先填好年級、班級、座號');var g=$('idG');if(g)g.focus();return Promise.resolve();}
    var filled=fieldEls().some(function(el){return (el.type==='checkbox'||el.type==='radio')?el.checked:!!(el.value||'').trim();});
    if(filled&&!confirm('會用雲端上次存的內容，蓋掉這一頁現在填的內容，可以嗎？'))return Promise.resolve();
    return load(true);
  };
  if($('loadBtn'))$('loadBtn').addEventListener('click',function(){window.cardReload();});
  $$('[data-reload]').forEach(function(b){b.addEventListener('click',function(){window.cardReload();});});
  document.addEventListener('input',function(e){
    if(e.target.closest&&e.target.closest('[data-key]')){window.cardRefresh();queueSave();}
  });
  document.addEventListener('change',function(e){
    if(e.target.matches&&e.target.matches('[data-key]')){window.cardRefresh();queueSave();}
  });

  /* ---------- 字數 ---------- */
  $$('textarea[data-count]').forEach(function(t){
    var c=document.createElement('div');c.className='count';t.after(c);
    function u(){c.textContent=t.value.replace(/\s/g,'').length+' 字';}
    t.addEventListener('input',u);u();
    setTimeout(u,1500);
  });

  /* ---------- 提問框架：複製 ---------- */
  $$('.frame').forEach(function(f){
    $$('.fbox',f).forEach(function(box){
      var t=box.querySelector('.ftext'),b=box.querySelector('.copy');
      if(t&&b)b.addEventListener('click',function(){copyText(t.innerText.replace(/\s+\n/g,'\n').trim(),b);});
    });
  });
  $$('[data-copy]').forEach(function(b){
    b.addEventListener('click',function(){var src=$(b.dataset.copy);if(src)copyText((src.value!=null&&src.tagName!=='DIV'&&src.tagName!=='PRE')?src.value:src.innerText,b,b.dataset.done||'已複製！');});
  });

  /* ---------- 圖片縮放：滾輪多段放大、拖曳移動、雙擊還原（放大看圖與手冊閱讀器共用）---------- */
  function makeZoom(stage,img,label){
    var sc=1,tx=0,ty=0,drag=null,moved=false,MAX=8;
    img.style.transformOrigin='0 0';img.style.transition='none';img.draggable=false;
    function apply(){img.style.transform='translate('+tx+'px,'+ty+'px) scale('+sc+')';img.style.cursor=sc>1?(drag?'grabbing':'grab'):'zoom-in';if(label)label.textContent=Math.round(sc*100)+'%';}
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
    img.addEventListener('load',reset);
    apply();
    return {reset:reset,zoom:function(f){zoomAt(f);},get scale(){return sc;}};
  }
  window.makeZoom=makeZoom;
  function zoomBar(){return '<span class="zbar"><button type="button" class="zo" aria-label="縮小"><svg class="ico"><use href="#i-minus"/></svg></button><span class="zl">100%</span><button type="button" class="zi" aria-label="放大"><svg class="ico"><use href="#i-plus"/></svg></button><button type="button" class="zr">還原</button></span>';}
  window.cardZoomBar=zoomBar;
  function wireBar(root,z){root.querySelector('.zi').onclick=function(){z.zoom(1.25);};root.querySelector('.zo').onclick=function(){z.zoom(0.8);};root.querySelector('.zr').onclick=function(){z.reset();};}
  window.cardWireBar=wireBar;

  /* ---------- 放大看圖 ---------- */
  var lb=document.createElement('div');lb.id='lightbox';
  lb.innerHTML='<div class="lbtop"><span class="tip">滾輪放大縮小・拖曳移動・雙擊還原</span>'+zoomBar()+'<button class="x" type="button"><svg class="ico"><use href="#i-x"/></svg>關閉</button></div><div class="lbstage"><img alt=""></div>';
  document.body.appendChild(lb);
  var lbImg=lb.querySelector('img'),lbZ=makeZoom(lb.querySelector('.lbstage'),lbImg,lb.querySelector('.zl'));wireBar(lb,lbZ);
  function lbClose(){lb.classList.remove('on');document.body.style.overflow='';}
  lb.querySelector('.x').onclick=lbClose;
  lb.querySelector('.lbstage').addEventListener('click',function(e){if(e.target===this)lbClose();});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&lb.classList.contains('on'))lbClose();});
  document.addEventListener('click',function(e){
    if(lb.contains(e.target))return;
    var t=e.target.closest&&e.target.closest('[data-zoom],img.shot,img.thumb');
    if(!t)return;
    var src=t.dataset.zoom||t.getAttribute('src');if(!src)return;
    e.preventDefault();lbImg.src=src;lbZ.reset();lb.classList.add('on');document.body.style.overflow='hidden';
  });
  var tst=document.createElement('div');tst.id='toast';document.body.appendChild(tst);

  /* ---------- 步驟：一次看一步 ---------- */
  var steps=$$('section.step');
  if(steps.length){
    var bar=$('stepbar'),flow=$('flow'),cur=1,visited={1:true};
    function reqDone(sec){
      var req=$$('[data-req]',sec);
      if(!req.length)return null;
      return req.every(function(el){
        if(el.type==='checkbox'||el.type==='radio')return $$('[data-key="'+el.dataset.key+'"]',sec).some(function(x){return x.checked;});
        if(el.dataset.req==='all')return $$('[data-key="'+el.dataset.key+'"]',sec).every(function(x){return x.checked;});
        return !!(el.value||'').trim();
      });
    }
    function isDone(n){var sec=steps[n-1],r=reqDone(sec);if(r!==null)return r;return visited[n]&&n!==cur;}
    function render(){
      if(bar)bar.innerHTML='';
      steps.forEach(function(sec,idx){
        var n=idx+1,b=document.createElement('button');
        b.type='button';b.className=isDone(n)&&n!==cur?'done':'';
        b.innerHTML='<span class="d">'+(isDone(n)&&n!==cur?'<svg class="ico"><use href="#i-check"/></svg>':n)+'</span><span class="t">'+esc(sec.dataset.title)+'</span>';
        b.setAttribute('aria-label','第 '+n+' 步：'+sec.dataset.title);
        if(n===cur)b.setAttribute('aria-current','step');
        b.onclick=function(){show(n);};
        if(bar)bar.appendChild(b);
      });
    }
    window.__refreshSteps=render;
    function show(n,noScroll){
      cur=n;visited[n]=true;
      steps.forEach(function(s,i){s.hidden=(i+1)!==n;});
      render();
      if(!noScroll){var top=(bar?bar.parentNode.offsetTop:0);window.scrollTo({top:Math.max(0,top-2),behavior:'smooth'});}
      if(LESSON&&dirty)save();
      try{history.replaceState(null,'','#s'+n);}catch(e){}
    }
    window.cardShowStep=show;
    steps.forEach(function(sec,idx){
      var n=idx+1,nav=sec.querySelector('.stepnav');if(!nav)return;
      if(n>1){var p=document.createElement('button');p.type='button';p.className='btn ghost';p.innerHTML='<svg class="ico"><use href="#i-prev"/></svg>上一步';p.onclick=function(){show(n-1);};nav.appendChild(p);}else nav.appendChild(document.createElement('span'));
      if(n<steps.length){var x=document.createElement('button');x.type='button';x.className='btn';x.innerHTML='下一步：'+esc(steps[n].dataset.title)+'<svg class="ico"><use href="#i-next"/></svg>';x.onclick=function(){show(n+1);};nav.appendChild(x);}
    });
    if(flow)steps.forEach(function(sec,idx){
      var b=document.createElement('button');b.type='button';
      b.innerHTML='<span class="n">'+(idx+1)+'</span>'+esc(sec.dataset.title)+(sec.dataset.min?' <span class="m">'+sec.dataset.min+' 分鐘</span>':'');
      b.onclick=function(){show(idx+1);};flow.appendChild(b);
    });
    if(LESSON){
      var last=steps[steps.length-1],nv=last.querySelector('.stepnav'),box=document.createElement('div');
      box.className='submitbox';
      box.innerHTML='<div><b>繳交這一節的成果</b><span class="ss" id="subStat"></span></div><button type="button" class="btn" id="subBtn"></button>';
      last.insertBefore(box,nv);
      updSub();
      $('subBtn').onclick=function(){
        var i=getId();
        if(!idValid(i)){alert('請先在最上面填好年級、班級、座號。');var g=$('idG');if(g)g.focus();window.scrollTo({top:0,behavior:'smooth'});return;}
        window.cardRefresh();
        var miss=[];steps.forEach(function(sec){if(reqDone(sec)===false)miss.push(sec.dataset.title);});
        var msg='確定要繳交這一節的成果嗎？'+(miss.length?'\n\n還沒完成的步驟：'+miss.join('、')+'\n（可以先繳交，之後補完會自動更新）':'')+'\n\n繳交後老師會看到。';
        if(!confirm(msg))return;
        subTime=Date.now();var btn=this;btn.disabled=true;
        save().then(function(r){
          btn.disabled=false;
          if(r==='cloud'){updSub();toast('已繳交！');}
          else{subTime=0;var e=$('subStat');e.className='ss bad';e.textContent=r==='local'?'沒有連上雲端，還沒交出去。請檢查網路再按一次，或告訴老師。':'繳交失敗，請再按一次；還是不行就告訴老師。';}
        });
      };
    }
    var m=/^#s(\d)$/.exec(location.hash);
    show(m&&Number(m[1])<=steps.length?Number(m[1]):1,true);
  }
})();

/* ---------- 頁面之間的連結：本機（materials 資料夾）和發布後（pcclass/contest/）路徑不同 ---------- */
(function(){
  var F={C00:'C00_賀卡創作營',C01:'C01_認識e度與主題',C02:'C02_文字創作與提問',C03:'C03_AI繪圖',C04:'C04_檢查標記與排版',C05:'C05_說明書與交件'};
  var here=(window.PAGE&&window.PAGE.code)||'C00';
  var local=/\/materials\//.test(decodeURIComponent(location.pathname));
  function href(to){
    if(local)return (here==='C00'?'../':'../')+F[to]+'/競賽_'+F[to]+'.html';
    if(to==='C00')return here==='C00'?'./':'../';
    return here==='C00'?to+'/':'../'+to+'/';
  }
  window.cardHref=href;
  Array.prototype.forEach.call(document.querySelectorAll('[data-go]'),function(a){a.setAttribute('href',href(a.dataset.go));});
})();

/* ---------- 單元手冊閱讀器：PAGE.hb＝[[PDF頁碼,'章 p.頁','說明'],…]；圖在 assets/hb/pdf{N}.jpg（縮圖 _s）---------- */
(function(){
  var P=window.PAGE||{},list=P.hb,host=document.getElementById('hbBook');
  if(!list||!list.length||!host)return;
  function big(i){return 'assets/hb/pdf'+list[i][0]+'.jpg';}
  function sm(i){return 'assets/hb/pdf'+list[i][0]+'_s.jpg';}
  var pick=[Math.min(2,list.length-1),Math.min(1,list.length-1),0];
  host.innerHTML=pick.map(function(i){return '<img src="'+sm(i)+'" alt="">';}).join('')+'<span class="lb"><svg class="ico"><use href="#i-book"/></svg>手冊 '+list.length+' 頁</span>';
  host.title='打開這一節要讀的手冊頁面';
  var ov=document.createElement('div');ov.id='hbr';ov.setAttribute('role','dialog');ov.setAttribute('aria-label','手冊頁面');
  ov.innerHTML='<div class="top"><svg class="ico"><use href="#i-book"/></svg><b>'+esc(P.hbTitle||'這一節要讀的手冊頁面')+'</b><span class="cap"></span><span class="cnt"></span>'+
    '<button class="x" type="button"><svg class="ico"><use href="#i-x"/></svg>關閉</button></div>'+
    '<div class="stage"><button class="nav p" type="button" aria-label="上一頁"><svg class="ico"><use href="#i-prev"/></svg></button><img alt=""><button class="nav n" type="button" aria-label="下一頁"><svg class="ico"><use href="#i-next"/></svg></button></div>'+
    '<div class="strip"></div>';
  ov.querySelector('.top .x').insertAdjacentHTML('beforebegin',window.cardZoomBar());
  document.body.appendChild(ov);
  var img=ov.querySelector('.stage img'),strip=ov.querySelector('.strip'),cur=0;
  var z=window.makeZoom(ov.querySelector('.stage'),img,ov.querySelector('.zl'));window.cardWireBar(ov,z);
  list.forEach(function(p,i){var b=document.createElement('button');b.type='button';b.innerHTML='<img src="'+sm(i)+'" alt="" loading="lazy">'+esc(p[1]);b.onclick=function(){go(i);};strip.appendChild(b);});
  function go(i){
    cur=Math.max(0,Math.min(list.length-1,i));
    img.src=big(cur);img.alt='手冊 '+list[cur][1];
    ov.querySelector('.cap').textContent=list[cur][1]+'　'+(list[cur][2]||'');
    ov.querySelector('.cnt').textContent=(cur+1)+'／'+list.length;
    ov.querySelector('.nav.p').disabled=cur===0;ov.querySelector('.nav.n').disabled=cur===list.length-1;
    Array.prototype.forEach.call(strip.children,function(b,k){b.classList.toggle('on',k===cur);if(k===cur)b.scrollIntoView({block:'nearest',inline:'center'});});
    if(cur+1<list.length){var pre=new Image();pre.src=big(cur+1);}
  }
  function open(i){ov.classList.add('on');document.body.style.overflow='hidden';go(i||0);}
  function close(){ov.classList.remove('on');document.body.style.overflow='';}
  window.openHandbook=open;
  host.addEventListener('click',function(){open(0);});
  ov.querySelector('.x').onclick=close;
  ov.querySelector('.nav.p').onclick=function(){go(cur-1);};
  ov.querySelector('.nav.n').onclick=function(){go(cur+1);};
  ov.addEventListener('click',function(e){if(e.target===ov||e.target.classList.contains('stage'))close();});
  img.addEventListener('touchstart',function(){},{passive:true});
  document.addEventListener('keydown',function(e){if(!ov.classList.contains('on'))return;if(e.key==='Escape')close();else if(e.key==='ArrowRight')go(cur+1);else if(e.key==='ArrowLeft')go(cur-1);});
  var sx=null;img.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;},{passive:true});
  img.addEventListener('touchend',function(e){if(sx==null||z.scale>1){sx=null;return;}var dx=e.changedTouches[0].clientX-sx;if(Math.abs(dx)>40)go(cur+(dx<0?1:-1));sx=null;});
})();
