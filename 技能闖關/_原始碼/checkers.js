/* ============================================================
   電腦急救站｜判定器（checker）
   ------------------------------------------------------------
   每個判定器：Checkers[名稱](el, params, ctx) → 回傳清除函式（可省略）
     el     ：放關卡畫面的容器
     params ：level.json 裡 practice／challenge 的 params
     ctx.mode     'practice'（有提示）或 'challenge'（沒有提示）
     ctx.pass()   全部完成
     ctx.miss(t)  做錯一次（會算進嘗試次數），t＝要給學生看的話
     ctx.hint(t)  單純提示，不算錯
   原則：一定要偵測「真的做了那個動作」，不能只按一個「我完成了」。
   ============================================================ */
(function(){
  var C = window.Checkers = {};
  var esc = function(s){return Quest.esc(s);};
  function norm(s){return String(s||'').replace(/\s+/g,'').replace(/[，。、！？：；「」（）,.!?:;()"']/g,'');}

  // 共用：任務清單（一次一個任務，做完打勾）
  function taskList(el,tasks){
    var box=document.createElement('div');
    box.innerHTML=tasks.map(function(t,k){return '<div class="task" data-k="'+k+'"><span class="dot">'+(k+1)+'</span><span>'+t+'</span></div>';}).join('');
    el.appendChild(box);
    var cur=0;
    function paint(){[].forEach.call(box.children,function(d,k){d.classList.toggle('done',k<cur);d.classList.toggle('now',k===cur);if(k<cur)d.querySelector('.dot').innerHTML=Quest.icon('check');});}
    paint();
    return {get cur(){return cur;}, next:function(){cur++;paint();return cur>=tasks.length;}};
  }

  /* ---------- selectText：選取文字（拖選、雙擊選詞、Ctrl+A 全選）----------
     params.passage：一段文字；params.tasks：[{kind:'range'|'word'|'all', target, say}]
       range：用滑鼠拖曳選到 target；word：雙擊選到 target（請用英文單字，中文雙擊斷詞不穩定）
       all  ：在下方的文字框裡按 Ctrl+A 全選 */
  C.selectText = function(el,p,ctx){
    var practice=ctx.mode==='practice';
    var html=esc(p.passage);
    if(practice)p.tasks.forEach(function(t){if(t.target&&t.kind!=='all')html=html.replace(esc(t.target),'<mark>'+esc(t.target)+'</mark>');});
    var tl=taskList(el,p.tasks.map(function(t){return t.say;}));
    var wrap=document.createElement('div');
    wrap.innerHTML='<div class="passage" data-ck="passage">'+html+'</div>'+
      (p.tasks.some(function(t){return t.kind==='all';})?'<label class="lbl">文字框</label><textarea class="field" data-ck="all" rows="4">'+esc(p.allText||p.passage)+'</textarea>':'');
    el.appendChild(wrap);
    var passage=wrap.querySelector('[data-ck=passage]'), ta=wrap.querySelector('[data-ck=all]');
    var lastDbl=0;
    passage.addEventListener('dblclick',function(){lastDbl=Date.now();setTimeout(check,30);});
    function check(){
      var t=p.tasks[tl.cur];if(!t)return;
      if(t.kind==='all'){
        if(ta&&document.activeElement===ta&&ta.selectionStart===0&&ta.selectionEnd===ta.value.length&&ta.value.length>0)ok();
        return;
      }
      var sel=window.getSelection();if(!sel||sel.isCollapsed)return;
      if(!passage.contains(sel.anchorNode))return;
      var got=sel.toString();
      if(norm(got)===norm(t.target)){
        if(t.kind==='word'&&Date.now()-lastDbl>800){ctx.hint('選對了！不過這一題要練「雙擊」：在單字上快速按兩下左鍵。');return;}
        ok();
      }else if(got.length>2&&t.kind==='range'){
        var g=norm(got),w=norm(t.target);
        ctx.miss(g.indexOf(w)>=0?'選太多了，再試一次：從第一個字按住，拖到最後一個字就放開。':
          w.indexOf(g)>=0?'還沒選完整，要從第一個字一路拖到最後一個字。':'選到別的字了，看清楚題目要選哪幾個字。');
      }
    }
    function ok(){ctx.hint('');if(tl.next())ctx.pass();}
    var onUp=function(){setTimeout(check,20);};
    passage.addEventListener('mouseup',onUp);
    if(ta){ta.addEventListener('keyup',onUp);ta.addEventListener('select',onUp);}
    if(practice)ctx.hint('看清楚有<b>點點底線</b>的地方，就是要選取的文字。');
  };

  /* ---------- copyPaste：複製 → 貼上 ----------
     params.passage：來源文字；params.tasks：[{target, label}]，每個任務一個文字框
     判定：要發生「複製」動作，而且文字框是用「貼上」放進去的，內容含 target */
  C.copyPaste = function(el,p,ctx){
    // params.cut：true＝剪下（來源變成可編輯的文字框，剪下後原處要消失）
    var practice=ctx.mode==='practice';
    var html=esc(p.passage);
    if(practice)p.tasks.forEach(function(t){html=html.replace(esc(t.target),'<mark>'+esc(t.target)+'</mark>');});
    var tl=taskList(el,p.tasks.map(function(t){return t.say||((p.cut?'剪下':'複製')+'「'+esc(t.target)+'」，貼到「'+esc(t.label)+'」');}));
    var wrap=document.createElement('div');
    wrap.innerHTML=(p.cut?'<label class="lbl">'+esc(p.srcLabel||'原本的文字')+'<textarea class="field" data-ck="src" rows="3" spellcheck="false" style="margin-top:6px"></textarea></label>':'<div class="passage">'+html+'</div>')+p.tasks.map(function(t,k){return '<label class="lbl">'+esc(t.label)+'<textarea class="field" data-ck="f'+k+'" rows="2" spellcheck="false" style="margin-top:6px"></textarea></label>';}).join('');
    el.appendChild(wrap);
    var copied=false, src=wrap.querySelector('[data-ck=src]'), cutDone=false;
    var onCopy=function(){copied=true;if(practice)ctx.hint('複製好了！現在點一下下面的框框，按 <kbd>Ctrl</kbd>＋<kbd>V</kbd> 貼上。');};
    if(src){
      src.value=p.passage;
      src.addEventListener('cut',function(){cutDone=true;if(practice)ctx.hint('剪下了！原本的字不見了，但電腦記住了。點下面的框框，按 <kbd>Ctrl</kbd>＋<kbd>V</kbd> 貼上。');});
      src.addEventListener('copy',function(e){e.stopPropagation();if(practice)ctx.hint('這是「複製」喔，原本的字還在。這一關要用 <kbd>Ctrl</kbd>＋<kbd>X</kbd> 剪下。');});
      if(practice)ctx.hint('把「'+esc(p.tasks[0].target)+'」選起來，按 <kbd>Ctrl</kbd>＋<kbd>X</kbd> 剪下。');
    }else document.addEventListener('copy',onCopy);
    p.tasks.forEach(function(t,k){
      var f=wrap.querySelector('[data-ck=f'+k+']'), pasted=false, tm=null;
      // 貼上會同時觸發 paste 和 input，合併成一次判定，避免錯一次算兩次
      function later(){clearTimeout(tm);tm=setTimeout(check,30);}
      f.addEventListener('paste',function(){pasted=true;later();});
      f.addEventListener('input',later);
      function check(){
        if(tl.cur!==k)return;
        var v=f.value;
        if(!v.trim())return;
        if(!pasted){ctx.miss('這一關要用「貼上」喔，不要自己打字。先清空框框，再用 <kbd>Ctrl</kbd>＋<kbd>V</kbd>。');f.value='';return;}
        if(norm(v).indexOf(norm(t.target))<0){ctx.miss('貼上的內容不對，檢查一下是不是複製到別的字了。清空框框後再試一次。');return;}
        if(src&&(!cutDone||norm(src.value).indexOf(norm(t.target))>=0)){ctx.miss('原本的地方還有這段字——這是「複製」不是「剪下」。清空下面的框框，按 <kbd>Ctrl</kbd>＋<kbd>Z</kbd> 或重來，改用 <kbd>Ctrl</kbd>＋<kbd>X</kbd>。');return;}
        ctx.hint('');f.readOnly=true;
        if(tl.next())ctx.pass();
        else{copied=false;var nx=wrap.querySelector('[data-ck=f'+(k+1)+']');if(nx)nx.scrollIntoView({block:'nearest'});}
      }
    });
    return function(){document.removeEventListener('copy',onCopy);};
  };

  /* ---------- plainPaste：純文字貼上（Ctrl+Shift+V）----------
     params.richHtml：有顏色粗體的來源；params.target：要貼的那段文字（純文字）
     params.docHtml ：文件原本的內容，用 <span class="slot">…</span> 標出要貼的位置
     判定：文件裡出現 target，而且沒有帶進任何格式（style、粗體、字型、顏色…） */
  C.plainPaste = function(el,p,ctx){
    var practice=ctx.mode==='practice';
    var tl=taskList(el,[p.say1||'把上面彩色那段文字選起來，按 <kbd>Ctrl</kbd>＋<kbd>C</kbd> 複製',p.say2||'點文件裡灰色的位置，用「純文字貼上」貼進去']);
    var wrap=document.createElement('div');
    wrap.innerHTML='<label class="lbl">網頁上的資料</label><div class="rich" data-ck="rich">'+p.richHtml+'</div>'+
      '<label class="lbl">我的文件</label><div class="docbar">文件　|　字型：預設　大小：16</div><div class="doc" data-ck="doc" contenteditable="true" spellcheck="false">'+p.docHtml+'</div>';
    el.appendChild(wrap);
    var doc=wrap.querySelector('[data-ck=doc]');
    [].forEach.call(doc.querySelectorAll('*'),function(n){n.setAttribute('data-keep','1');});
    var onCopy=function(){if(tl.cur===0){tl.next();if(practice)ctx.hint('現在點文件裡的灰色字，然後按 <kbd>Ctrl</kbd>＋<kbd>Shift</kbd>＋<kbd>V</kbd>（三個鍵一起按）。');}};
    document.addEventListener('copy',onCopy);
    // 點進文件時把灰色「貼在這裡」拿掉，游標放在那一段最後面（直接刪 span 的話，Chrome 會把灰色樣式留給接下來貼上的字）
    doc.addEventListener('focus',function(){
      var s=doc.querySelector('.slot');if(!s)return;
      var par=s.parentNode;par.removeChild(s);
      setTimeout(function(){var r=document.createRange();r.selectNodeContents(par);r.collapse(false);var sel=window.getSelection();sel.removeAllRanges();sel.addRange(r);},0);
    });
    doc.addEventListener('paste',function(){setTimeout(check,30);});
    function styled(){
      var bad=false;
      [].forEach.call(doc.querySelectorAll('*'),function(n){
        if(n.hasAttribute('data-keep'))return;
        if(n.hasAttribute('style')||/^(B|STRONG|I|EM|U|FONT|H\d|SPAN|A|TABLE|IMG)$/.test(n.tagName))bad=true;
      });
      return bad;
    }
    function check(){
      if(norm(doc.textContent).indexOf(norm(p.target))<0){
        if(styled())ctx.miss('格式（顏色、粗體）也跟著貼過來了！先按 <kbd>Ctrl</kbd>＋<kbd>Z</kbd> 復原，再改用 <kbd>Ctrl</kbd>＋<kbd>Shift</kbd>＋<kbd>V</kbd>。');
        else ctx.miss('貼進來的內容不完整，按 <kbd>Ctrl</kbd>＋<kbd>Z</kbd> 復原，再把整段複製一次。');
        return;
      }
      if(styled()){ctx.miss('格式（顏色、粗體）也跟著貼過來了！先按 <kbd>Ctrl</kbd>＋<kbd>Z</kbd> 復原，再改用 <kbd>Ctrl</kbd>＋<kbd>Shift</kbd>＋<kbd>V</kbd>。');return;}
      ctx.hint('');
      if(tl.cur===0)tl.next();
      if(tl.next()){doc.contentEditable='false';ctx.pass();}
    }
    return function(){document.removeEventListener('copy',onCopy);};
  };

  /* ---------- fileUpload：做完 → 把檔案上傳回來比對 ----------
     網頁看不到檔案總管，所以「下載、改名、另存」都用上傳回來的檔案判定。
     params.file：
       文字檔 {name, lines:[…]}：按鈕下載，內容自動加一行驗證碼（每次進關卡都不同，舊檔案過不了）
       圖片   {src, name, alt}：顯示圖片讓學生「另存圖片」，用 SHA-256 比對是不是同一張
     params.rename：要改成的檔名，可用 {grade}{class}{seat}（會比對時忽略前導 0、全形數字、空白）
     params.say：[第一步說明, 第二步說明]（可省略） */
  C.fileUpload = function(el,p,ctx){
    var practice=ctx.mode==='practice', F=p.file||{}, isImg=!!F.src;
    var code=Math.random().toString(36).slice(2,6).toUpperCase();
    var say=p.say||[
      isImg?'在圖片上按<b>右鍵</b> →「另存圖片」，存到電腦裡':'按「下載」，把 <b>'+esc(F.name)+'</b> 存到電腦',
      p.rename?'到檔案總管把檔名改成 <b>'+esc(fill(p.rename))+'</b>，再上傳':'按「選擇檔案」，找到剛剛的檔案上傳'];
    var tl=taskList(el,say);
    var wrap=document.createElement('div');
    wrap.innerHTML=(isImg?'<div class="rich" style="text-align:center"><img data-ck="img" src="'+esc(F.src)+'" alt="'+esc(F.alt||'')+'" style="margin:0 auto;max-height:320px"></div>':
        '<button class="go" data-ck="dl" type="button">下載 '+esc(F.name)+'</button>')+
      '<label class="drop" data-ck="drop"><input type="file" data-ck="file" hidden><b>選擇檔案</b>　或把檔案拖到這裡</label>';
    el.appendChild(wrap);
    var drop=wrap.querySelector('[data-ck=drop]'), inp=wrap.querySelector('[data-ck=file]');
    var origHash=null;
    if(isImg){
      fetch(F.src).then(function(r){return r.arrayBuffer();}).then(sha).then(function(h){origHash=h;});
      wrap.querySelector('[data-ck=img]').addEventListener('contextmenu',function(){
        if(tl.cur===0){tl.next();if(practice)ctx.hint('選「另存圖片」，記住存到哪個資料夾（通常是「下載」）。存好後按下面的「選擇檔案」把它找出來。');}
      });
    }else{
      wrap.querySelector('[data-ck=dl]').addEventListener('click',function(){
        var text='﻿'+(F.lines||[]).join('\r\n')+'\r\n驗證碼：'+code+'\r\n';
        var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:'text/plain'}));a.download=F.name;
        document.body.appendChild(a);a.click();a.remove();
        if(tl.cur===0)tl.next();
        if(practice)ctx.hint(p.rename?'下載好了！打開檔案總管 →「下載」資料夾，在檔案上按右鍵 →「重新命名」（或選取後按 <kbd>F2</kbd>）。':
          '下載好了！按下面的「選擇檔案」，在左邊點「下載」，選 <b>'+esc(F.name)+'</b> →「開啟」。');
      });
    }
    inp.addEventListener('change',function(){if(inp.files[0])check(inp.files[0]);inp.value='';});
    drop.addEventListener('dragover',function(e){e.preventDefault();drop.classList.add('on');});
    drop.addEventListener('dragleave',function(){drop.classList.remove('on');});
    drop.addEventListener('drop',function(e){e.preventDefault();drop.classList.remove('on');var f=e.dataTransfer.files[0];if(f)check(f);});

    function fill(s){var i=Quest.getId();return s.replace('{grade}',i.grade||'?').replace('{class}',i.className||'?').replace('{seat}',i.studentId||'?');}
    function nname(s){return String(s).replace(/[０-９]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-0xFEE0);}).replace(/\s+/g,'').replace(/\d+/g,function(d){return String(+d);}).toLowerCase();}
    function sha(buf){return crypto.subtle.digest('SHA-256',buf).then(function(h){return Array.prototype.map.call(new Uint8Array(h),function(b){return ('0'+b.toString(16)).slice(-2);}).join('');});}
    function base(n){return n.replace(/ ?\(\d+\)(?=\.[^.]+$)/,'');}   // 「任務卡 (1).txt」→「任務卡.txt」

    function check(f){
      if(p.rename&&!Quest.idValid()){ctx.hint('先在右上角填好年級、班級、座號，才知道檔名要改成什麼。');return;}
      if(isImg){
        if(!/^image\//.test(f.type)){ctx.miss('這不是圖片檔，要上傳剛剛另存的那張圖片。');return;}
        f.arrayBuffer().then(sha).then(function(h){
          if(origHash&&h!==origHash){ctx.miss('這張圖片和上面的不一樣。要用「另存圖片」存下來，不要用截圖。');return;}
          done();
        });
        return;
      }
      if(p.rename){
        var want=nname(fill(p.rename)), got=nname(f.name), ext=(want.match(/\.[^.]+$/)||[''])[0];
        if(got!==want){
          if(got===want+ext)return ctx.miss('檔名變成「'+esc(f.name)+'」，多了一個 '+ext+'。副檔名本來就有了，只要改前面的名字。');
          if(got===want.slice(0,-ext.length))return ctx.miss('副檔名 '+ext+' 不見了！改名時只改前面，後面的 '+ext+' 要留著。');
          if(nname(base(f.name))===nname(F.name))return ctx.miss('這個檔案還沒改名喔。到檔案總管把它改成 <b>'+esc(fill(p.rename))+'</b> 再上傳。');
          return ctx.miss('檔名是「'+esc(f.name)+'」，和題目要的 <b>'+esc(fill(p.rename))+'</b> 不一樣，仔細看每個字。');
        }
      }else if(nname(base(f.name))!==nname(F.name)){
        return ctx.miss('上傳的是「'+esc(f.name)+'」，要找的是剛剛下載的 <b>'+esc(F.name)+'</b>。');
      }
      f.text().then(function(t){
        if(t.indexOf('驗證碼：'+code)<0)return ctx.miss('這是之前下載的舊檔案。請上傳<b>剛剛</b>下載的那一個（檔名後面可能多了 (1)、(2)）。');
        done();
      });
    }
    function done(){ctx.hint('');while(tl.cur<say.length-1)tl.next();tl.next();drop.style.pointerEvents='none';ctx.pass();}
  };

  /* ---------- popup：處理彈出視窗（網頁內模擬）----------
     params.popups：依序出現的視窗種類 cookie／notify／ad／prize／subscribe
     params.shuffle：true＝打亂順序；params.adWait：廣告的 × 要等幾秒才出現（0＝馬上）
     params.page：{tab, url, html} 底下那個網頁的樣子
     按到陷阱按鈕＝miss（說明為什麼不能按），視窗留著；按對才關掉、換下一個 */
  var POPS={
    cookie:{name:'Cookie 同意視窗',hint:'這是 Cookie 同意視窗。網站想記錄你看了什麼。選<b>「只接受必要的」</b>最安全。',
      html:function(){return '<div class="pp pp-cookie"><b>這個網站使用 Cookie</b><p>我們和合作夥伴會使用 Cookie 來提供個人化廣告與分析。</p><div class="pp-row"><button data-bad="全部接受">全部接受</button><button data-ok class="pp-plain">只接受必要的</button></div></div>';},
      bad:{'全部接受':'「全部接受」會讓網站和廣告商記錄你看了什麼。選「只接受必要的」比較保護自己。'}},
    notify:{name:'通知權限',hint:'網址列下面跳出「想要顯示通知」。不認識的網站一律按<b>「封鎖」</b>。',
      html:function(o){return '<div class="pp pp-notify"><b>'+esc(o.host)+' 想要</b><p>顯示通知</p><div class="pp-row"><button data-bad="允許">允許</button><button data-ok class="pp-plain">封鎖</button></div></div>';},
      bad:{'允許':'按了「允許」，這個網站以後可以一直跳通知給你，很多是廣告或詐騙。不認識的網站按「封鎖」。'}},
    ad:{name:'廣告視窗',hint:'這是廣告。大大的按鈕是陷阱，要找<b>角落的小 ×</b>（有時要等幾秒才出現）。',
      html:function(o){var left=o.shuffle&&Math.random()<.5;return '<div class="pp-mask"><div class="pp pp-ad"><span class="pp-x'+(left?' l':'')+'" data-ok'+(o.adWait?' hidden':'')+' title="關閉">×</span>'+(o.adWait?'<span class="pp-wait">'+o.adWait+' 秒後可關閉</span>':'')+'<div class="pp-adart">超好玩手機遊戲<br><small>限時免費</small></div><button data-bad="下載" class="pp-big">立即免費下載</button><button data-bad="關閉廣告" class="pp-fake">關閉廣告</button></div></div>';},
      bad:{'下載':'這是廣告按鈕！按了會跑到別的網站，甚至下載奇怪的程式。要找角落的小 ×。','關閉廣告':'小心！這個「關閉廣告」是廣告的一部分，按了一樣會跳到廣告網站。真正的關閉是角落的小 ×。'}},
    prize:{name:'假中獎視窗',hint:'「恭喜中獎」幾乎都是詐騙。不要領獎，按<b>「關閉」</b>。',
      html:function(){return '<div class="pp-mask"><div class="pp pp-prize"><div class="pp-trophy">恭喜你！</div><p>你是今天第 <b>1,000,000</b> 位訪客，獲得最新平板電腦一台！</p><p class="pp-red">只剩 59 秒，快領取！</p><div class="pp-row"><button data-bad="領獎" class="pp-big">立即領獎</button><button data-ok class="pp-plain">關閉</button></div></div></div>';},
      bad:{'領獎':'天下沒有白吃的午餐！「中獎」視窗是詐騙，按了會要你填個資、手機號碼或付錢。'}},
    subscribe:{name:'訂閱視窗',hint:'不需要的東西<b>不要留 Email</b>。點小小的<b>「不用了，謝謝」</b>。',
      html:function(){return '<div class="pp-mask"><div class="pp pp-sub"><b>訂閱我們的電子報！</b><p>輸入 Email 就送你 100 元折價券</p><input data-bad-input placeholder="你的 Email" aria-label="Email"><div class="pp-row"><button data-bad="訂閱" class="pp-big">訂閱</button></div><a href="#" data-ok class="pp-no">不用了，謝謝</a></div></div>';},
      bad:{'訂閱':'不需要的東西不要留 Email 或個資，留了之後會收到一堆廣告信。點「不用了，謝謝」就好。'}}
  };
  C.popup = function(el,p,ctx){
    var practice=ctx.mode==='practice', list=(p.popups||[]).slice();
    if(p.shuffle)list.sort(function(){return Math.random()-.5;});
    var pg=p.page||{};
    var tl=taskList(el,list.map(function(k,n){return practice?'關掉「'+POPS[k].name+'」':'安全地處理第 '+(n+1)+' 個跳出來的視窗';}));
    var wrap=document.createElement('div');
    wrap.innerHTML='<div class="fb"><div class="fb-tabs"><span class="fb-tab">'+esc(pg.tab||'小學生線上字典')+'</span></div><div class="fb-url">'+esc(pg.url||'dict.example.tw')+'</div><div class="fb-page">'+(pg.html||'<h3>小學生線上字典</h3><p>搜尋：<b>電腦</b></p><p>英文：computer</p>')+'</div><div class="fb-layer"></div></div>';
    el.appendChild(wrap);
    var layer=wrap.querySelector('.fb-layer'), i=0, timer=null;
    function showNext(){
      layer.innerHTML='';
      if(i>=list.length){ctx.hint('');ctx.pass();return;}
      var k=list[i], P=POPS[k];
      layer.innerHTML=P.html({host:pg.url||'dict.example.tw',shuffle:p.shuffle,adWait:p.adWait||0});
      if(practice){ctx.hint(P.hint);var ok=layer.querySelector('[data-ok]');if(ok)ok.classList.add('pulse');}
      var x=layer.querySelector('.pp-x[hidden]');
      if(x){var n=p.adWait,w=layer.querySelector('.pp-wait');timer=setInterval(function(){n--;if(n>0){w.textContent=n+' 秒後可關閉';}else{clearInterval(timer);w.remove();x.hidden=false;}},1000);}
    }
    layer.addEventListener('click',function(e){
      var t=e.target.closest('[data-ok],[data-bad]');if(!t)return;
      e.preventDefault();
      if(t.hasAttribute('data-ok')){clearInterval(timer);i++;tl.next();ctx.hint('');setTimeout(showNext,500);layer.innerHTML='';return;}
      ctx.miss(POPS[list[i]].bad[t.getAttribute('data-bad')]||'這個按鈕不對喔。');
    });
    layer.addEventListener('focusin',function(e){if(e.target.hasAttribute('data-bad-input'))ctx.hint('先停一下！不需要的東西，不要在跳出來的視窗裡填 Email 或個資。');});
    setTimeout(showNext,600);
    return function(){clearInterval(timer);};
  };

  /* ---------- tabPair：開新分頁 → 切過去看密碼 → 切回來輸入 → 關掉多的分頁 ----------
     搭配 site/tab/（密碼小卡），用 BroadcastChannel 溝通。
     params.linkText：連結文字；params.closeTab：true＝最後要把密碼小卡分頁關掉 */
  C.tabPair = function(el,p,ctx){
    var practice=ctx.mode==='practice';
    var sid=ctx.mode+Math.random().toString(36).slice(2,8), code=String(1000+Math.floor(Math.random()*9000));
    var steps=['按住 <kbd>Ctrl</kbd> 點下面的連結，讓它在<b>新分頁</b>打開','切換到新分頁，看密碼是多少','切回這個分頁，把密碼打進框框'];
    if(p.closeTab)steps.push('把「密碼小卡」那個分頁關掉（<kbd>Ctrl</kbd>＋<kbd>W</kbd> 或分頁上的 ×）');
    var tl=taskList(el,steps);
    var wrap=document.createElement('div');
    wrap.innerHTML='<div class="passage"><a href="../tab/#'+sid+'" target="_blank" rel="opener" data-ck="link" style="font-weight:700;color:var(--ac)">'+esc(p.linkText||'打開密碼小卡')+'</a></div>'+
      '<label class="lbl">密碼<input class="field" data-ck="code" inputmode="numeric" maxlength="4" style="min-height:0;max-width:180px;margin-top:6px;font-size:22px;letter-spacing:6px" disabled></label>';
    el.appendChild(wrap);
    var link=wrap.querySelector('[data-ck=link]'), inp=wrap.querySelector('[data-ck=code]');
    link.addEventListener('click',function(e){
      if(e.ctrlKey||e.metaKey||e.shiftKey)return;
      e.preventDefault();
      ctx.miss('直接點會蓋掉這一頁！要<b>按住 <kbd>Ctrl</kbd> 不放</b>再點連結（或按右鍵 →「在新分頁中開啟連結」）。');
    });
    if(!window.BroadcastChannel){ctx.hint('這個瀏覽器太舊，請改用 Chrome。');return;}
    var ch=new BroadcastChannel('skillquest-tab'), seen=false, typed=false, lastPong=0, poll=null;
    // 分頁被關掉時 pagehide 的 bye 不一定送得出來，所以輸入密碼後改成每秒 ping，連續 2.5 秒沒回應就當作關掉了
    function closed(){clearInterval(poll);if(tl.cur===3){tl.next();ctx.hint('');ctx.pass();}}
    function startPoll(){lastPong=Date.now();poll=setInterval(function(){ch.postMessage({sid:sid,type:'ping'});if(Date.now()-lastPong>2500)closed();},1000);}
    ch.onmessage=function(e){
      var d=e.data||{};if(d.sid!==sid)return;
      if(d.type==='pong'){lastPong=Date.now();return;}
      if(d.type==='hello'){
        ch.postMessage({sid:sid,type:'code',code:code});
        if(tl.cur===0){tl.next();if(practice)ctx.hint('新分頁開好了，在最上面。點它，或按 <kbd>Ctrl</kbd>＋<kbd>Tab</kbd> 切過去。');}
      }else if(d.type==='seen'&&!seen){
        seen=true;while(tl.cur<2)tl.next();inp.disabled=false;
        if(practice)ctx.hint('看到密碼了吧？切回這個分頁（點分頁或 <kbd>Ctrl</kbd>＋<kbd>Tab</kbd>），把密碼打進框框。');
      }else if(d.type==='bye'&&p.closeTab){
        if(!typed){ctx.miss('密碼還沒輸入，就把密碼小卡關掉了。按住 <kbd>Ctrl</kbd> 再點一次連結重新打開。');seen=false;inp.disabled=true;return;}
        closed();
      }
    };
    inp.addEventListener('input',function(){
      var v=inp.value.replace(/\D/g,'');if(v!==inp.value)inp.value=v;
      if(v.length<4)return;
      if(v!==code){ctx.miss('密碼不對，再切過去看一次。');return;}
      typed=true;inp.disabled=true;tl.next();
      if(!p.closeTab){ctx.hint('');ctx.pass();}
      else{startPoll();if(practice)ctx.hint('答對了！最後把「密碼小卡」分頁關掉：切過去按 <kbd>Ctrl</kbd>＋<kbd>W</kbd>，或按分頁上的 ×。');}
    });
    return function(){clearInterval(poll);ch.close();};
  };

  /* ---------- keyTask：在文字框裡依序完成任務，可指定要用哪個快速鍵 ----------
     params.text：文字框一開始的內容；params.tasks：[{say, key, cond, hint}]
       key ：必須用這個快速鍵完成（例 'ctrl+z'；可用 | 分隔多個 'ctrl+y|ctrl+shift+z'）
       cond：{equals:'@original'|文字, contains, notContains, caps:true}——文字框內容要符合
     條件達成但沒按指定快速鍵（例如自己重打）→ miss */
  // 鍵盤事件 → 'ctrl+shift+z' 這種字串（單獨按 Shift 打字不算組合鍵）
  function comboOf(e){
    var mod=e.ctrlKey||e.metaKey, parts=[];
    if(mod)parts.push('ctrl');
    if(e.shiftKey&&(mod||e.altKey||e.key.length>1))parts.push('shift');
    if(e.altKey)parts.push('alt');
    parts.push(e.key.toLowerCase());
    return parts.join('+');
  }
  function keyLabel(c){return c.split('+').map(function(k){return '<kbd>'+(k.length===1?k.toUpperCase():k.charAt(0).toUpperCase()+k.slice(1))+'</kbd>';}).join('＋');}
  C.keyTask = function(el,p,ctx){
    var practice=ctx.mode==='practice', T=p.tasks;
    var tl=taskList(el,T.map(function(t){return t.say;}));
    var wrap=document.createElement('div');
    wrap.innerHTML='<textarea class="field" data-ck="ta" rows="4" spellcheck="false"></textarea>';
    el.appendChild(wrap);
    var ta=wrap.querySelector('[data-ck=ta]'); ta.value=p.text||'';
    var lastCombo='', lastAt=0, lastBad='';
    // bad：[{re, msg}]，打出不該出現的字（例如全形數字、全部大寫）就提示
    function bad(t){
      var hit=null;(t.bad||p.bad||[]).some(function(b){if(new RegExp(b.re).test(ta.value)){hit=b.msg;return true;}});
      if(hit&&hit!==lastBad)ctx.miss(hit);
      lastBad=hit||'';return !!hit;
    }
    function met(c){
      var v=ta.value;
      if(c.equals!=null&&v!==(c.equals==='@original'?p.text:c.equals))return false;
      if(c.contains!=null&&v.indexOf(c.contains)<0)return false;
      if(c.notContains!=null&&v.indexOf(c.notContains)>=0)return false;
      return true;
    }
    function check(){
      var t=T[tl.cur];if(!t)return;
      if(bad(t))return;
      if(!met(t.cond||{}))return;
      if(t.key){
        var ok=t.key.split('|').indexOf(lastCombo)>=0&&Date.now()-lastAt<1500;
        if(!ok){ctx.miss(t.miss||('這一步要用 '+keyLabel(t.key.split('|')[0])+' 完成，不要自己重打。'));return;}
      }
      ctx.hint('');
      if(tl.next()){ta.readOnly=true;ctx.pass();}
      else if(practice&&T[tl.cur].hint)ctx.hint(T[tl.cur].hint);
    }
    ta.addEventListener('keydown',function(e){if(e.ctrlKey||e.metaKey||e.altKey||e.key.length>1){lastCombo=comboOf(e);lastAt=Date.now();}});
    ta.addEventListener('input',function(){setTimeout(check,10);});
    ta.addEventListener('keyup',function(){setTimeout(check,10);});
    if(practice&&T[0].hint)ctx.hint(T[0].hint);
  };

  /* ---------- quiz：選擇題或分類題（不計分數，全部答對才過關）----------
     params.kind：'choice'——questions:[{q, options:[…], answer:索引, why}]
                  'bucket'——buckets:[名稱…]、items:[{t, b:桶子索引, why}]；拖曳或「先點項目再點桶子」 */
  C.quiz = function(el,p,ctx){
    var practice=ctx.mode==='practice';
    var wrap=document.createElement('div');el.appendChild(wrap);
    if(p.kind==='bucket'){
      var left=p.items.length;
      wrap.innerHTML='<div class="qz-pool" data-ck="pool">'+p.items.map(function(it,k){return '<span class="qz-item" draggable="true" data-k="'+k+'">'+esc(it.t)+'</span>';}).join('')+'</div>'+
        '<div class="qz-buckets">'+p.buckets.map(function(b,k){return '<div class="qz-bucket" data-b="'+k+'"><b>'+esc(b)+'</b><div class="qz-in"></div></div>';}).join('')+'</div>';
      var pick=null;
      function sel(it){[].forEach.call(wrap.querySelectorAll('.qz-item'),function(x){x.classList.toggle('on',x===it);});pick=it;}
      function put(it,bk){
        var I=p.items[+it.dataset.k];
        if(I.b!==+bk.dataset.b){ctx.miss('「'+esc(I.t)+'」不是放這裡喔。'+(practice&&I.why?esc(I.why):''));sel(null);return;}
        bk.querySelector('.qz-in').appendChild(it);it.draggable=false;it.classList.remove('on');it.classList.add('ok');pick=null;ctx.hint(practice&&I.why?'答對了！'+esc(I.why):'');
        if(--left===0)ctx.pass();
      }
      // dragOnly：練「拖曳」本身的關卡，不接受「點一下再點框框」
      wrap.addEventListener('click',function(e){
        var it=e.target.closest('.qz-item:not(.ok)');if(it){sel(it);if(p.dragOnly)ctx.hint('要用<b>拖曳</b>：在它上面按住左鍵不放，移到框框上再放開。');return;}
        var bk=e.target.closest('.qz-bucket');if(bk&&pick&&!p.dragOnly)put(pick,bk);
      });
      wrap.addEventListener('dragstart',function(e){var it=e.target.closest('.qz-item');if(it){sel(it);e.dataTransfer.setData('text/plain',it.dataset.k);}});
      wrap.addEventListener('dragover',function(e){if(e.target.closest('.qz-bucket'))e.preventDefault();});
      wrap.addEventListener('drop',function(e){var bk=e.target.closest('.qz-bucket');if(bk&&pick){e.preventDefault();put(pick,bk);}});
      if(practice)ctx.hint(p.dragOnly?'在上面的東西按住左鍵不放，拖到正確的框框上再放開。':'把上面的每一個拖到正確的框框裡（也可以先點一下，再點框框）。');
      return;
    }
    var Qs=p.questions, i=0;
    function show(){
      if(i>=Qs.length){ctx.hint('');ctx.pass();return;}
      var q=Qs[i];
      wrap.innerHTML='<div class="task now"><span class="dot">'+(i+1)+'</span><span>'+q.q+'</span></div><div class="qz-opts">'+q.options.map(function(o,k){return '<button class="qz-opt" data-k="'+k+'">'+o+'</button>';}).join('')+'</div>';
    }
    wrap.addEventListener('click',function(e){
      var b=e.target.closest('.qz-opt');if(!b)return;
      var q=Qs[i];
      if(+b.dataset.k!==q.answer){b.classList.add('no');ctx.miss(q.wrong||'再想想看。');return;}
      ctx.hint(practice&&q.why?'答對了！'+q.why:'');i++;setTimeout(show,practice&&q.why?1400:300);
    });
    show();
  };

  /* ---------- tabUrl：開新分頁 → 複製網址列的網址 → 切回來貼上 ----------
     搭配 site/tab/（mode:url）。網址裡有這次專用的 #代碼，所以只有複製那個分頁的網址才會對。 */
  C.tabUrl = function(el,p,ctx){
    var practice=ctx.mode==='practice', sid='u'+ctx.mode+Math.random().toString(36).slice(2,8);
    var tl=taskList(el,['按住 <kbd>Ctrl</kbd> 點下面的連結，在新分頁打開','到新分頁，點網址列，按 <kbd>Ctrl</kbd>＋<kbd>C</kbd> 複製網址','切回這裡，把網址貼到框框']);
    var wrap=document.createElement('div');
    wrap.innerHTML='<div class="passage"><a href="../tab/#'+sid+'" target="_blank" data-ck="link" style="font-weight:700;color:var(--ac)">'+esc(p.linkText||'打開要複製網址的網頁')+'</a></div>'+
      '<label class="lbl">網址<textarea class="field" data-ck="url" rows="2" spellcheck="false" style="margin-top:6px"></textarea></label>';
    el.appendChild(wrap);
    var link=wrap.querySelector('[data-ck=link]'), f=wrap.querySelector('[data-ck=url]'), pasted=false;
    link.addEventListener('click',function(e){if(e.ctrlKey||e.metaKey||e.shiftKey)return;e.preventDefault();ctx.miss('要<b>按住 <kbd>Ctrl</kbd></b> 再點連結，讓它在新分頁打開。');});
    if(!window.BroadcastChannel){ctx.hint('這個瀏覽器太舊，請改用 Chrome。');return;}
    var ch=new BroadcastChannel('skillquest-tab');
    ch.onmessage=function(e){var d=e.data||{};if(d.sid!==sid)return;
      if(d.type==='hello'){ch.postMessage({sid:sid,type:'code',mode:'url'});if(tl.cur===0){tl.next();if(practice)ctx.hint('打開了！切到新分頁，照上面的說明複製網址。');}}
      else if(d.type==='seen'&&tl.cur===1&&practice)ctx.hint('點一下網址列，網址會整個變藍，這時按 <kbd>Ctrl</kbd>＋<kbd>C</kbd>。');};
    var tm=null;function later(){clearTimeout(tm);tm=setTimeout(check,30);}
    f.addEventListener('paste',function(){pasted=true;later();});
    f.addEventListener('input',later);
    function clean(u){try{u=decodeURI(u);}catch(x){}return u.trim().replace(/^https?:\/\//,'').replace(/\/$/,'');}
    function check(){
      var v=f.value.trim();if(!v)return;
      if(!pasted){ctx.miss('網址要用複製貼上，不要自己打（很容易打錯）。清空框框再試一次。');f.value='';return;}
      if(clean(v)!==clean(link.href)){ctx.miss(v.indexOf('#'+sid)<0?'這不是那個分頁的網址。到新打開的分頁，點網址列再複製一次。':'網址不完整，點一下網址列讓它整個變藍，再複製。');pasted=false;return;}
      while(tl.cur<3)tl.next();f.readOnly=true;ctx.hint('');ctx.pass();
    }
    return function(){ch.close();};
  };

  /* ---------- tabReopen：開分頁 → 關掉 → 用 Ctrl+Shift+T 救回來 ---------- */
  C.tabReopen = function(el,p,ctx){
    var practice=ctx.mode==='practice', sid='r'+ctx.mode+Math.random().toString(36).slice(2,8);
    var tl=taskList(el,['按住 <kbd>Ctrl</kbd> 點下面的連結，在新分頁打開','切到那個分頁，把它關掉（<kbd>Ctrl</kbd>＋<kbd>W</kbd>）','糟糕關錯了！按 <kbd>Ctrl</kbd>＋<kbd>Shift</kbd>＋<kbd>T</kbd> 把它救回來']);
    var wrap=document.createElement('div');
    wrap.innerHTML='<div class="passage"><a href="../tab/#'+sid+'" target="_blank" data-ck="link" style="font-weight:700;color:var(--ac)">'+esc(p.linkText||'打開練習用的分頁')+'</a></div>';
    el.appendChild(wrap);
    wrap.querySelector('[data-ck=link]').addEventListener('click',function(e){if(e.ctrlKey||e.metaKey||e.shiftKey)return;e.preventDefault();ctx.miss('要<b>按住 <kbd>Ctrl</kbd></b> 再點連結。');});
    if(!window.BroadcastChannel){ctx.hint('這個瀏覽器太舊，請改用 Chrome。');return;}
    var ch=new BroadcastChannel('skillquest-tab'), lastPong=0, poll=null;
    function closed(){clearInterval(poll);poll=null;if(tl.cur===1){tl.next();if(practice)ctx.hint('關掉了。現在按 <kbd>Ctrl</kbd>＋<kbd>Shift</kbd>＋<kbd>T</kbd>（三個鍵一起按），剛剛關掉的分頁會回來。');}}
    ch.onmessage=function(e){var d=e.data||{};if(d.sid!==sid)return;
      if(d.type==='pong'){lastPong=Date.now();return;}
      if(d.type==='hello'){
        if(tl.cur===2){ch.postMessage({sid:sid,type:'code',mode:'back'});tl.next();ctx.hint('');ctx.pass();return;}
        ch.postMessage({sid:sid,type:'code',mode:'close'});
        lastPong=Date.now();
        if(!poll)poll=setInterval(function(){ch.postMessage({sid:sid,type:'ping'});if(Date.now()-lastPong>2500)closed();},1000);
        if(tl.cur===0){tl.next();if(practice)ctx.hint('打開了！切到那個分頁，按 <kbd>Ctrl</kbd>＋<kbd>W</kbd> 把它關掉。');}
      }else if(d.type==='bye')closed();
    };
    return function(){clearInterval(poll);ch.close();};
  };

  /* ---------- reload：網頁卡住了 → 按 F5（或重新整理鈕）----------
     進關卡時在 sessionStorage 記一筆；重新整理後同一個分頁回來、而且是 reload，就算過關。 */
  C.reload = function(el,p,ctx){
    var key='sq-reload-'+ctx.mode, t0=0;
    try{t0=+sessionStorage.getItem(key)||0;}catch(e){}
    var nav=(performance.getEntriesByType&&performance.getEntriesByType('navigation')[0])||{};
    var tl=taskList(el,[p.say||'這個網頁卡住了，一直轉圈圈。用<b>重新整理</b>讓它重新載入']);
    if(t0&&Date.now()-t0<10*60*1000&&nav.type==='reload'){
      try{sessionStorage.removeItem(key);}catch(e){}
      el.insertAdjacentHTML('beforeend','<div class="passage" style="text-align:center"><b style="color:var(--green)">重新整理成功，網頁正常了！</b></div>');
      tl.next();setTimeout(ctx.pass,400);return;
    }
    try{sessionStorage.setItem(key,String(Date.now()));}catch(e){}
    el.insertAdjacentHTML('beforeend','<div class="fb"><div class="fb-tabs"><span class="fb-tab">'+esc(p.tab||'載入中…')+'</span></div><div class="fb-url">'+esc(p.url||'school.example.tw')+'</div><div class="fb-page" style="display:grid;place-items:center;min-height:240px"><div class="spin"></div><p style="color:#888">載入中，請稍候……</p></div></div>');
    if(ctx.mode==='practice')ctx.hint('按鍵盤最上面一排的 <kbd>F5</kbd>，或按網址列左邊的「↻」重新整理按鈕。');
  };

  /* ---------- zoom：網頁縮放（Ctrl+滾輪／Ctrl+加減）再用 Ctrl+0 還原 ----------
     用 devicePixelRatio 判斷縮放比例；params.bigger：要放大到原本的幾倍（預設 1.2） */
  C.zoom = function(el,p,ctx){
    var practice=ctx.mode==='practice', base=window.devicePixelRatio, k0=false, big=false;
    var tl=taskList(el,['把網頁<b>放大</b>（按住 <kbd>Ctrl</kbd> 滾動滑鼠滾輪往上，或按 <kbd>Ctrl</kbd>＋<kbd>+</kbd>）','用 <kbd>Ctrl</kbd>＋<kbd>0</kbd>（數字零）一鍵恢復原本大小']);
    el.insertAdjacentHTML('beforeend','<div class="passage" style="font-size:13px">這段字很小很小，看不清楚的時候，可以把網頁放大。放大之後記得恢復，不然版面會跑掉。</div>');
    function check(){
      var r=window.devicePixelRatio/base;
      if(tl.cur===0&&r>=(p.bigger||1.2)){big=true;tl.next();if(practice)ctx.hint('放大了！字變大了吧？現在按 <kbd>Ctrl</kbd>＋<kbd>0</kbd> 恢復。');return;}
      if(tl.cur===1&&Math.abs(r-1)<0.02){
        if(!k0){ctx.miss('大小恢復了，不過這一關要練 <kbd>Ctrl</kbd>＋<kbd>0</kbd>：再放大一次，然後按 <kbd>Ctrl</kbd>＋<kbd>0</kbd>。');return;}
        tl.next();ctx.hint('');ctx.pass();
      }
    }
    function onKey(e){if((e.ctrlKey||e.metaKey)&&(e.key==='0'||e.code==='Digit0'||e.code==='Numpad0')){k0=true;setTimeout(function(){k0=false;},2500);setTimeout(check,300);}}
    window.addEventListener('resize',check);document.addEventListener('keydown',onKey);
    if(practice)ctx.hint('按住 <kbd>Ctrl</kbd> 不放，滑鼠滾輪往上滾兩下。');
    return function(){window.removeEventListener('resize',check);document.removeEventListener('keydown',onKey);};
  };

  /* ---------- findWord：用 Ctrl+F 在長文章裡找字，回答出現幾次 ----------
     params.passage（可用 \n 分段）、params.word；次數由程式自己數 */
  C.findWord = function(el,p,ctx){
    var practice=ctx.mode==='practice', usedF=false, n=p.passage.split(p.word).length-1;
    var tl=taskList(el,['按 <kbd>Ctrl</kbd>＋<kbd>F</kbd>，在右上角出現的搜尋框打「<b>'+esc(p.word)+'</b>」','看搜尋框右邊的數字（例如 1/5），回答下面的問題']);
    el.insertAdjacentHTML('beforeend','<div class="passage" style="max-height:260px;overflow:auto">'+p.passage.split('\n').map(function(t){return '<p style="margin:0 0 10px">'+esc(t)+'</p>';}).join('')+'</div>'+
      '<label class="lbl">「'+esc(p.word)+'」在文章裡出現幾次？<input class="field" data-ck="n" inputmode="numeric" maxlength="3" style="min-height:0;max-width:120px;margin-top:6px"></label>');
    var inp=el.querySelector('[data-ck=n]');
    function onKey(e){if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='f'){usedF=true;if(tl.cur===0){tl.next();if(practice)ctx.hint('打好字之後，搜尋框右邊會出現「1/'+'?'+'」，後面那個數字就是總共有幾個。');}}}
    document.addEventListener('keydown',onKey);
    inp.addEventListener('input',function(){
      var v=inp.value.replace(/\D/g,'');if(v!==inp.value)inp.value=v;if(!v)return;
      clearTimeout(inp._t);inp._t=setTimeout(function(){
        if(!usedF){ctx.miss('先按 <kbd>Ctrl</kbd>＋<kbd>F</kbd> 讓電腦幫你找，不要用眼睛一個一個數。');inp.value='';return;}
        if(+v!==n){ctx.miss('不對喔，再看一次搜尋框右邊的數字（斜線後面那個）。');return;}
        while(tl.cur<2)tl.next();inp.readOnly=true;ctx.hint('');ctx.pass();
      },500);
    });
    return function(){document.removeEventListener('keydown',onKey);};
  };
})();
