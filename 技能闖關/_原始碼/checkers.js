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
    var practice=ctx.mode==='practice';
    var html=esc(p.passage);
    if(practice)p.tasks.forEach(function(t){html=html.replace(esc(t.target),'<mark>'+esc(t.target)+'</mark>');});
    var tl=taskList(el,p.tasks.map(function(t){return t.say||('複製「'+esc(t.target)+'」，貼到「'+esc(t.label)+'」');}));
    var wrap=document.createElement('div');
    wrap.innerHTML='<div class="passage">'+html+'</div>'+p.tasks.map(function(t,k){return '<label class="lbl">'+esc(t.label)+'<textarea class="field" data-ck="f'+k+'" rows="2" spellcheck="false" style="margin-top:6px"></textarea></label>';}).join('');
    el.appendChild(wrap);
    var copied=false;
    var onCopy=function(){copied=true;if(practice)ctx.hint('複製好了！現在點一下下面的框框，按 <kbd>Ctrl</kbd>＋<kbd>V</kbd> 貼上。');};
    document.addEventListener('copy',onCopy);
    p.tasks.forEach(function(t,k){
      var f=wrap.querySelector('[data-ck=f'+k+']'), pasted=false;
      f.addEventListener('paste',function(){pasted=true;setTimeout(check,20);});
      f.addEventListener('input',function(){setTimeout(check,20);});
      function check(){
        if(tl.cur!==k)return;
        var v=f.value;
        if(!v.trim())return;
        if(!pasted){ctx.miss('這一關要用「貼上」喔，不要自己打字。先清空框框，再用 <kbd>Ctrl</kbd>＋<kbd>V</kbd>。');f.value='';return;}
        if(norm(v).indexOf(norm(t.target))<0){ctx.miss('貼上的內容不對，檢查一下是不是複製到別的字了。清空框框後再試一次。');return;}
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
})();
