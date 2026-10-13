/* ===== 共用引擎：識別列／Firebase／作答狀態／繳交／教師模式／檢視／步驟分頁（依《學習單資料與提交規範》） ===== */
(function(){
  var C=/*CONFIG*/;
  var WS=C.ws,QUIZ_ID=C.ws,LESSON_PATH=C.lessonPath,TITLE=C.title;
  var TEACHER_EMAIL='boyin0304@slps.tn.edu.tw';
  var IS_ADMIN=location.hash==='#admin';
  var REVIEW_ID=IS_ADMIN?new URLSearchParams(location.search).get('review'):null;   // 沒有 #admin 不給看別人的作答
  function $(id){return document.getElementById(id);}
  function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function filled(v){return !!String(v==null?'':v).trim();}
  var state={},REV={},H={};
  /*L04SLICE:phimg_lightbox*/
  /*L04SLICE:identity*/
  /*L04SLICE:firebase*/

  // ===== 題目資料（唯一來源＝這份學習單；文字題的標準答案用正則，§2-d）=====
  var PATTERNS=Object.assign({},C.patterns||{});
  function testPattern(qid,val){
    val=String(val||'').trim();if(!val)return false;
    var p=PATTERNS[qid];if(!p)return true;
    try{return new RegExp(p,'i').test(val);}catch(e){console.warn('答案格式有誤，改成有填就算',qid,e);return true;}
  }
  /*HOOKS*/

  // ===== 作答狀態（localStorage 暫存）=====
  var STATE_KEY=C.stateKey;
  Object.keys(C.choices).forEach(function(q){state[q]=C.choices[q].multi?[]:null;});
  (C.texts||[]).forEach(function(k){state[k]='';});
  (C.reveals||[]).forEach(function(r){REV[r]=false;});
  if(!REVIEW_ID){try{var sv=localStorage.getItem(STATE_KEY);if(sv)state=Object.assign(state,JSON.parse(sv));}catch(e){}}
  function save(){if(REVIEW_ID)return;try{localStorage.setItem(STATE_KEY,JSON.stringify(state));}catch(e){}}

  // ===== 題型（預設＋老師即時切換，§5-6）=====
  var DEFAULT_QTYPE=C.qtypes,QTYPE_OVERRIDES={};
  function qtypeOf(qid){return QTYPE_OVERRIDES[qid]||DEFAULT_QTYPE[qid]||'experience';}

  // ===== 畫面 =====
  var chipCls='opt ans border-2 border-slate-200 bg-white rounded-full px-4 py-1.5 font-bold hover:border-indigo-400';
  var chipOn='opt ans border-2 border-indigo-500 bg-indigo-50 text-indigo-800 rounded-full px-4 py-1.5 font-bold';
  var blkCls='opt ans text-left w-full border-2 border-slate-200 bg-white rounded-2xl px-4 py-2 hover:border-indigo-400';
  var blkOn='opt ans text-left w-full border-2 border-indigo-500 bg-indigo-50 text-indigo-900 rounded-2xl px-4 py-2 font-bold';
  function renderChoice(q){
    var cfg=C.choices[q];if(cfg.card)return;
    var host=$(q+'Opts');if(!host)return;host.innerHTML='';
    cfg.opts.forEach(function(o){
      var on=cfg.multi?(state[q]||[]).indexOf(o)>=0:state[q]===o;
      var b=el('button',cfg.block?(on?blkOn:blkCls):(on?chipOn:chipCls),(cfg.block&&cfg.multi?'<span class="inline-block w-6 text-xl align-middle">'+(on?'☑':'☐')+'</span> ':(cfg.multi&&on?'✔ ':''))+esc(o));b.type='button';
      b.onclick=function(){
        if(cfg.multi){var i=state[q].indexOf(o);if(i>=0)state[q].splice(i,1);else state[q].push(o);}
        else state[q]=o;
        save();renderChoice(q);renderFeedback();if(H.changed)H.changed(q);
      };
      host.appendChild(b);
    });
  }
  function bindFields(){
    document.querySelectorAll('[data-k]').forEach(function(f){
      f.value=state[f.dataset.k]||'';
      f.addEventListener('input',function(){state[f.dataset.k]=f.value;save();renderFeedback();if(H.changed)H.changed(f.dataset.k);});
    });
  }
  function fillFields(){document.querySelectorAll('[data-k]').forEach(function(f){f.value=state[f.dataset.k]||'';});}
  function corrOf(q){var cfg=C.choices[q];if(!cfg)return null;var h=H.corr?H.corr(q):undefined;if(h!==undefined)return h;return cfg.correct==null?null:cfg.correct;}
  function answered(q){var v=state[q];return Array.isArray(v)?v.length>0:filled(v);}
  function isRight(q){
    var cfg=C.choices[q];
    if(cfg){
      var c=corrOf(q);
      if(c==null)return answered(q);
      if(cfg.multi){return (state[q]||[]).slice().sort().join('|')===c.slice().sort().join('|');}
      return state[q]===c;
    }
    return testPattern(q,state[q]);
  }
  function renderFeedback(){
    var auto=C.autoFb||[];   // autoFb：不用等老師公布，選完立刻顯示對錯
    Object.keys(C.revealOf||{}).concat(auto).forEach(function(q){
      var e=$(q+'Fb');if(!e)return;
      var hasKey=C.choices[q]?corrOf(q)!=null:!!PATTERNS[q];
      var show=hasKey&&(auto.indexOf(q)>=0||REV[C.revealOf[q]])&&answered(q);
      if(!show){e.textContent='';return;}
      var ok=isRight(q);e.className='text-sm font-bold '+(ok?'text-emerald-600':'text-rose-600');e.textContent=ok?'✔ 正確':'✘ 再想想看';
    });
  }
  function applyReveal(){
    document.querySelectorAll('[data-r]').forEach(function(e){e.classList.toggle('hidden',!REV[e.dataset.r]);});
    document.querySelectorAll('[data-wait]').forEach(function(e){e.classList.toggle('hidden',!!REV[e.dataset.wait]);});
    renderFeedback();
  }
  function renderAll(){Object.keys(C.choices).forEach(renderChoice);fillFields();renderFeedback();if(H.render)H.render();}
  bindFields();renderAll();

  // ===== 每題判斷（繳交與檢視共用）=====
  function judge(){
    var r={};
    Object.keys(C.qtypes).forEach(function(q){
      var cfg=C.choices[q];
      if(cfg){
        var c=corrOf(q),v=state[q];
        r[q]={given:cfg.multi?((v&&v.length)?v.join('、'):null):(v||null),correct:c==null?null:(cfg.multi?c.join('、'):c),isCorrect:isRight(q)};
      }else{
        r[q]={given:String(state[q]||'').trim()||null,correct:PATTERNS[q]||null,isCorrect:isRight(q)};
      }
    });
    return r;
  }

  // ===== 繳交（§2-b、§3、§3-b）=====
  function buildPayload(idn){
    var j=judge(),answers={},qtypes={},scoreAnswers={},experienceAnswers={},openAnswers={},bonusAnswers={};
    var sT=0,sC=0,eT=0,eA=0,bonus=C.bonus||[];
    Object.keys(C.qtypes).forEach(function(qid){
      var t=qtypeOf(qid),item=j[qid];
      qtypes[qid]=t;answers[qid]=item.given;
      if(bonus.indexOf(qid)>=0){bonusAnswers[qid]={given:item.given,completed:filled(item.given)};}
      if(t==='open'){openAnswers[qid]=String(item.given||'');}
      else if(t==='experience'){experienceAnswers[qid]=item;if(bonus.indexOf(qid)<0){eT++;if(filled(item.given))eA++;}}
      else{scoreAnswers[qid]=item;sT++;if(item.isCorrect)sC++;}
    });
    var p={worksheetId:WS,worksheetTitle:TITLE,lessonPath:LESSON_PATH,
      grade:idn.grade,className:idn.className,studentId:idn.studentId,
      answers:answers,qtypes:qtypes,qtexts:C.openQtexts||{},
      scoreAnswers:scoreAnswers,experienceAnswers:experienceAnswers,openAnswers:openAnswers,
      accuracyRate:sT?Math.round(sC/sT*100):null,experienceCompletion:eT?Math.round(eA/eT*100):null,
      parts:JSON.parse(JSON.stringify(state)),status:'submitted'};
    if(bonus.length){p.bonusQids=bonus.slice();p.bonusAnswers=bonusAnswers;}
    return p;
  }
  var submittedOnce=false;
  $('submitBtn').onclick=function(){
    var idn=getIdentity(),stat=$('submitStat');
    if(!identityValid(idn)){   // 不捲到頂端，只在按鈕下提示、把空格標紅
      markIdentity(true);
      stat.className='text-sm font-bold mt-3 min-h-[20px] text-rose-600';stat.textContent='⚠️ 還沒填好身分：請到頁面最上面填年級、班級（1-14）、座號，再按一次繳交。';
      return;
    }
    markIdentity(false);
    if(!db){alert('現在連不上，請稍後再試或重新整理頁面。');return;}
    if(!confirm('確定要繳交嗎？\n\n'+H.report().join('\n')+'\n\n送出後老師會看到，確定要交嗎？'))return;
    var payload=buildPayload(idn);payload.submittedAt=firebase.firestore.FieldValue.serverTimestamp();
    var btn=this;
    btn.disabled=true;stat.className='text-sm font-bold mt-3 min-h-[20px] text-indigo-600';stat.textContent='繳交中…';
    authResolved.then(function(){return ensureAuth();})
      .then(function(){return db.collection('submissions').doc(WS+'__'+idn.grade+'-'+idn.className+'-'+idn.studentId).set(payload,{merge:true});})
      .then(function(){
        btn.disabled=false;btn.textContent='重新繳交（覆蓋）';submittedOnce=true;renderStepper();
        stat.className='text-sm font-bold mt-3 min-h-[20px] text-emerald-600';stat.textContent='✓ 已繳交。可再按一次覆蓋更新。';
        var rb=$('rewardBox');rb.classList.remove('hidden');rb.scrollIntoView({behavior:'smooth'});
      }).catch(function(e){
        console.warn('繳交失敗',e);btn.disabled=false;
        stat.className='text-sm font-bold mt-3 min-h-[20px] text-amber-600';stat.textContent='繳交失敗，請檢查網路後再按一次；還是不行就告訴老師。';
      });
  };

  // ===== 教師模式（§5）=====
  var PREVIEW_KEY='wk_previewMode',teacherAuthed=false;
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
  var QTYPE_CYCLE=['experience','score','open'];
  var QTYPE_LABEL={score:'檢測',experience:'體驗',open:'開放'};
  var QTYPE_STYLE={score:'bg-rose-100 text-rose-700 border-rose-300',experience:'bg-sky-100 text-sky-700 border-sky-300',open:'bg-emerald-100 text-emerald-700 border-emerald-300'};
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
  function resetReveals(){var o={};(C.reveals||[]).forEach(function(r){o[r]=false;REV[r]=false;});return o;}
  function wireTeacher(label){
    $('teacherbar').classList.remove('hidden');$('tStatus').textContent=label;teacherAuthed=true;renderQtypeSlots();
    if(REVIEW_ID){loadReview();return;}
    ['showAnsBtn','lockBtn'].forEach(function(id){$(id).classList.remove('hidden');});
    document.querySelectorAll('[data-reveal-btn]').forEach(function(b){
      b.classList.remove('hidden');
      b.onclick=function(){
        var r=b.dataset.revealBtn,o={};o[r]=true;
        if(quizRef)quizRef.set(o,{merge:true}).catch(function(e){alert('公布失敗：'+e.message);});
        else{REV[r]=true;applyReveal();}
      };
    });
    $('showAnsBtn').onclick=function(){if(H.showAnswers)H.showAnswers();renderAll();};
    $('lockBtn').onclick=function(){
      if(!confirm('確定要還原嗎？\n全班畫面會收回所有公布，「檢視答案」填進去的內容也會清掉。\n學生已經繳交的學習單不受影響。'))return;
      if(H.clear)H.clear();save();renderAll();
      var o=resetReveals();
      if(quizRef)quizRef.set(o,{merge:true}).catch(function(e){alert('還原失敗：'+e.message);});
      else applyReveal();
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
    wireTeacher('單機模式（公布、題型只影響這台）');
  }
  // 檢視學生繳交（唯讀重現，§5-7）
  function loadReview(){
    $('reviewBanner').classList.remove('hidden');$('reviewExit').href=location.pathname+'#admin';
    $('submitBtn').classList.add('hidden');$('rewardBox').remove();
    (C.reveals||[]).forEach(function(r){REV[r]=true;});
    if(!db){$('reviewText').textContent='🔍 檢視模式：現在連不上資料庫';return;}
    db.collection('submissions').doc(REVIEW_ID).get().then(function(doc){
      if(!doc.exists){$('reviewText').textContent='🔍 檢視模式：找不到這份繳交';return;}
      var d=doc.data()||{};
      $('reviewText').textContent='🔍 檢視模式（唯讀）：'+d.grade+'年'+d.className+'班'+d.studentId+'號 的作答';
      $('idGrade').value=d.grade||'';$('idClass').value=d.className||'';$('idStudent').value=d.studentId||'';
      if(d.qtypes)QTYPE_OVERRIDES=d.qtypes;
      Object.assign(state,d.parts||{});
      applyReveal();renderAll();
      $('main').classList.add('locked');
      document.querySelectorAll('#main input,#main textarea,#idGrade,#idClass,#idStudent').forEach(function(f){f.disabled=true;});
    }).catch(function(e){console.warn('讀取繳交失敗',e);$('reviewText').textContent='🔍 檢視模式：讀取失敗';});
  }

  // ===== 學習路徑：一次只顯示一步，頂端進度列可以跳步（《HTML互動教材設計規範》§5.8）=====
  var STEP_NAMES=C.steps;
  var stepEls=[].slice.call(document.querySelectorAll('.step'));
  var curStep=1,visited={1:true};
  function stepDone(n){
    var h=H.stepDone?H.stepDone(n):null;
    if(h!=null)return h;
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
      cell.appendChild(el('span','hidden sm:block text-xs font-bold mt-0.5 '+(cur?'text-indigo-700':'text-slate-400'),name));
      host.appendChild(cell);
      if(n<STEP_NAMES.length)host.appendChild(el('div','flex-1 h-0.5 mt-3.5 sm:mt-4 mx-0.5 sm:mx-1 rounded '+(done&&!cur?'bg-emerald-300':'bg-slate-200')));
    });
    $('stepLabel').textContent='第 '+curStep+' 步／共 '+STEP_NAMES.length+' 步 · '+STEP_NAMES[curStep-1];
  }
  function showStep(n){
    curStep=n;visited[n]=true;
    stepEls.forEach(function(s){s.classList.toggle('hidden',Number(s.dataset.step)!==n);});
    renderStepper();if(H.render)H.render();
    window.scrollTo({top:0,behavior:'smooth'});
  }
  stepEls.forEach(function(s){
    var n=Number(s.dataset.step),nav=s.querySelector('.stepnav');
    if(n>1){var p=el('button','bg-white border-2 border-slate-300 hover:border-indigo-400 text-slate-600 font-bold rounded-2xl px-5 py-2','← 上一步');p.type='button';p.onclick=function(){showStep(n-1);};nav.appendChild(p);}
    else nav.appendChild(el('span',''));
    if(n<STEP_NAMES.length){var x=el('button','cute bg-indigo-600 hover:bg-indigo-700 text-white text-lg font-extrabold rounded-2xl px-6 py-2','下一步：'+STEP_NAMES[n]+' →');x.type='button';x.onclick=function(){showStep(n+1);};nav.appendChild(x);}
  });
  document.addEventListener('click',function(){setTimeout(renderStepper,0);});
  document.addEventListener('input',function(){setTimeout(renderStepper,0);});
  renderStepper();

  fbReady.then(function(){
    if(!quizRef){if(IS_ADMIN)teacherOffline();return;}
    var first=true;
    quizRef.onSnapshot(function(doc){
      var d=(doc&&doc.data())||{};
      if(d.qtypeOverrides&&!REVIEW_ID){QTYPE_OVERRIDES=d.qtypeOverrides;renderQtypeSlots();}
      if(REVIEW_ID)return;
      var next={};(C.reveals||[]).forEach(function(r){next[r]=!!d[r];});
      var undone=Object.keys(next).some(function(k){return REV[k]&&!next[k];});
      if(undone&&!first&&!IS_ADMIN){location.reload();return;}   // 老師按還原：全部收回
      REV=next;first=false;applyReveal();
    },function(e){console.warn('讀取公布狀態失敗',e);});
    if(IS_ADMIN)teacherOnline();
  });
})();
