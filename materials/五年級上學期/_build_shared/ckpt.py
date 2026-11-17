# -*- coding: utf-8 -*-
# 「先繳交（存檔）」＋「讀取拿回」：L07、L08 共用（規範 §3-f 斷點繳交的簡化版）。
# 用法（在 build_L07.py／build_L08.py 裡）：
#   import ckpt
#   步驟 HTML 裡放 ckpt.CARD；組好整頁 t 之後 t = ckpt.patch_submit(t)；HOOKS 裡定義 H.hasContent。
# 做法：
#   - 「先繳交（存檔）」＝走同一顆 #submitBtn（先設旗標 pendingCk 再 click()，靠椅子關卡照樣攔得到），
#     寫進 submissions/{ws}__{年-班-號}，內容和正式繳交一樣，多一個 checkpoint:{final:false,step,stepName}；
#     評分平台看到的就是一筆已繳交的紀錄；之後正式繳交會覆蓋同一份。
#   - 成功後另存 studentWork/{ws}__{年-班-號}__progress：data:{state,step,stepName,v}、text（摘要）。
#   - 「讀取拿回」＝讀這份 progress，灌回 state、回到存檔時的步驟；這台電腦已有內容時先 confirm()。
import re

CARD = '''<div class="bg-white border-4 border-emerald-300 rounded-3xl p-5 mb-5 shadow-sm">
      <p class="cute text-xl font-extrabold text-emerald-700 m-0">寫不完？先繳交（存檔）</p>
      <p class="text-base text-slate-600 mt-1">先填好最上面的年級、班級、座號。按「先繳交（存檔）」，老師看得到你已經交了，內容也存好了；下一節或換一台電腦，填好同樣的號碼，按「讀取拿回」就能接著寫。</p>
      <div class="flex gap-2 flex-wrap mt-3">
        <button type="button" data-ck-save class="cute bg-emerald-600 hover:bg-emerald-700 text-white text-lg font-extrabold rounded-2xl px-5 py-2">先繳交（存檔）</button>
        <button type="button" data-ck-load class="bg-white border-2 border-emerald-400 hover:bg-emerald-50 text-emerald-800 font-bold rounded-2xl px-5 py-2">讀取拿回</button>
      </div>
      <p class="ckStat text-base font-bold mt-3 min-h-[24px]"></p>
    </div>'''

_NEW_SUBMIT = r'''  var submittedOnce=false,pendingCk=null;
  // ===== 先繳交（存檔）／讀取拿回（§3-f）：存到 submissions（老師看得到）＋ studentWork __progress（學生拿回）=====
  function progDocId(i){return WS+'__'+i.grade+'-'+i.className+'-'+i.studentId+'__progress';}
  function ckSay(msg,tone){document.querySelectorAll('.ckStat').forEach(function(e){e.className='ckStat text-base font-bold mt-3 min-h-[24px] text-'+tone+'-600';e.textContent=msg;});}
  function submitSay(msg,tone){var s=$('submitStat');s.className='text-sm font-bold mt-3 min-h-[20px] text-'+tone+'-600';s.textContent=msg;}
  function sayBy(ck,msg,tone){if(ck)ckSay(msg,tone);else submitSay(msg,tone);}
  function setBusy(b){document.querySelectorAll('[data-ck-save]').forEach(function(x){x.disabled=b;});$('submitBtn').disabled=b;}
  function saveProgress(i){   // 回傳 Promise<boolean>：存成功與否
    var snap=JSON.parse(JSON.stringify(state)),step=curStep,nm=STEP_NAMES[step-1]||'';
    return authResolved.then(function(){return ensureAuth();}).then(function(){
      return db.collection('studentWork').doc(progDocId(i)).set({worksheetId:WS,kind:'progress',grade:i.grade,className:i.className,studentId:i.studentId,
        data:{state:snap,step:step,stepName:nm,v:1},text:('寫到第 '+step+' 步：'+nm).slice(0,1900),updatedAt:firebase.firestore.FieldValue.serverTimestamp()});
    }).then(function(){return true;},function(e){console.warn('存進度失敗',e);return false;});
  }
  function applyProgress(dd){
    if(H.clear)H.clear();
    var s=dd.state||{};Object.keys(s).forEach(function(k){state[k]=s[k];});
    var want=STEP_NAMES.indexOf(dd.stepName);want=want>=0?want+1:(dd.step||1);
    if(want<1||want>STEP_NAMES.length)want=1;
    for(var k=1;k<want;k++)visited[k]=true;
    save();renderAll();showStep(want);
  }
  function loadProgress(){
    var i=getIdentity();
    if(!identityValid(i)){markIdentity(true);ckSay('先到頁面最上面填年級、班級、座號，再按一次。','rose');return;}
    markIdentity(false);
    if(!db){ckSay('現在連不上，晚點再試試看。','amber');return;}
    ckSay('找找看…','indigo');
    authResolved.then(function(){return ensureAuth();}).then(function(){return db.collection('studentWork').doc(progDocId(i)).get();}).then(function(doc){
      var dd=doc.exists?((doc.data()||{}).data||{}):{};
      if(!dd.state){ckSay('還沒有找到你存過的進度。寫到一半先按「先繳交（存檔）」，下次就能拿回來。','amber');return;}
      var at='';try{var d=doc.data().updatedAt.toDate(),p=function(x){return ('0'+x).slice(-2);};at='（'+(d.getMonth()+1)+'/'+d.getDate()+' '+p(d.getHours())+':'+p(d.getMinutes())+'）';}catch(e){}
      if((H.hasContent?H.hasContent():true)&&!confirm('找到了！這是你上次存的進度'+at+'。\n\n要用它換掉現在寫的內容嗎？'))return;
      applyProgress(dd);
      ckSay('✓ 已拿回你的進度，接著寫吧！','emerald');
    }).catch(function(e){console.warn('讀取進度失敗',e);ckSay('現在拿不到，晚點再試試看。','amber');});
  }
  document.querySelectorAll('[data-ck-save]').forEach(function(b){b.onclick=function(){pendingCk={final:false};$('submitBtn').click();};});
  document.querySelectorAll('[data-ck-load]').forEach(function(b){b.onclick=loadProgress;});
  $('submitBtn').addEventListener('pointerdown',function(){pendingCk=null;},true);   // 真的用滑鼠按最後一步的鈕＝正式繳交
  $('submitBtn').addEventListener('keydown',function(){pendingCk=null;},true);
  $('submitBtn').onclick=function(){
    var mode=pendingCk||{final:true},ck=!mode.final;pendingCk=null;
    var idn=getIdentity();
    if(!identityValid(idn)){   // 不捲到頂端，只在按鈕下提示、把空格標紅
      markIdentity(true);
      sayBy(ck,ck?'先到頁面最上面填年級、班級（1-14）、座號，再按一次「先繳交（存檔）」。':' 還沒填好身分：請到頁面最上面填年級、班級（1-14）、座號，再按一次繳交。','rose');
      return;
    }
    markIdentity(false);
    if(!db){alert('現在連不上，請稍後再試或重新整理頁面。');return;}
    var head=ck?'要先繳交（存檔）嗎？':'確定要繳交嗎？';
    var tail=ck?'\n\n老師會看到你已經交了；下次填同樣的年級、班級、座號，按「讀取拿回」就能接著寫。確定要交嗎？':'\n\n送出後老師會看到，確定要交嗎？';
    if(!confirm(head+'\n\n'+H.report().join('\n')+tail))return;
    var payload=buildPayload(idn);payload.submittedAt=firebase.firestore.FieldValue.serverTimestamp();
    var cs=ck?curStep:STEP_NAMES.length;
    payload.checkpoint={final:!ck,step:cs,stepName:STEP_NAMES[cs-1]||''};
    var btn=$('submitBtn');
    setBusy(true);sayBy(ck,'繳交中…','indigo');
    authResolved.then(function(){return ensureAuth();})
      .then(function(){return db.collection('submissions').doc(WS+'__'+idn.grade+'-'+idn.className+'-'+idn.studentId).set(payload,{merge:true});})
      .then(function(){
        if(H.afterSubmit){try{H.afterSubmit(idn);}catch(err){console.warn('繳交後動作失敗',err);}}
        var sp=saveProgress(idn);
        if(!ck){
          setBusy(false);btn.textContent='重新繳交（覆蓋）';submittedOnce=true;renderStepper();
          submitSay('✓ 已繳交。可再按一次覆蓋更新。','emerald');
          var rb=$('rewardBox');rb.classList.remove('hidden');rb.scrollIntoView({behavior:'smooth'});
        }else{
          sp.then(function(ok){
            setBusy(false);
            if(ok)ckSay('✓ 已先繳交（存檔）。下次填同樣的年級、班級、座號，按「讀取拿回」就能接著寫。','emerald');
            else ckSay('老師那邊已經收到了，但「讀取拿回」用的存檔沒成功，晚點再按一次。','amber');
          });
        }
      }).catch(function(e){
        console.warn('繳交失敗',e);setBusy(false);
        sayBy(ck,ck?'先繳交失敗，請檢查網路後再按一次；還是不行就告訴老師。':'繳交失敗，請檢查網路後再按一次；還是不行就告訴老師。','amber');
      });
  };

'''


def patch_submit(t):
    """把骨架（L06）的繳交區塊換成支援「先繳交」的版本。t 是已換行為 LF 的整頁文字。"""
    a = t.index("  var submittedOnce=false;\n  $('submitBtn').onclick=function(){")
    b = t.index('  // ===== 教師模式（§5）=====')
    assert a < b
    return t[:a] + _NEW_SUBMIT + t[b:]
