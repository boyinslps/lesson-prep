/* ============================================================
   第 1 步｜標記：貼上自己賀卡上的文字 → 用滑鼠選取，按顏色劃記（黑＝自己想的、紅＝AI 幫忙的、藍＝自己修改的）
   → 標記後的文章獨立顯示在第 5 步「作品說明書」的「查證揭露」上方，匯出時合併。
   存檔欄位（L4）：markText（貼上的文字）、markCodes（每個字一碼：0 黑、1 紅、2 藍）、markOk（按過「標好了」）。
   ============================================================ */
(function(){
  var ta=document.getElementById('mkText');if(!ta)return;
  function $(i){return document.getElementById(i);}
  var hid=$('mkCodes'),ok=$('mkOk'),box=$('mkBox'),paste=$('mkPaste'),view=$('mkView'),sum=$('mkSum'),show=$('mkShow'),showView=$('mkShowView');
  var COLS=['k','r','b'],LINE=['我自己想的（黑色）','AI 幫忙的（紅色）','我自己修改的（藍色）'];
  var cur={text:'',codes:'x'};
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function norm(t,c){c=String(c||'').replace(/[^012]/g,'');while(c.length<t.length)c+='0';return c.slice(0,t.length);}
  function paint(el,t,c){
    var h='';
    for(var i=0;i<t.length;i++){var ch=t.charAt(i);h+=ch==='\n'?'<br>':'<span class="mc '+COLS[+c.charAt(i)]+'" data-i="'+i+'">'+esc(ch)+'</span>';}
    el.innerHTML=h;
  }
  function setVal(el,v){if(el.value!==v){el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}));}}
  function counts(t,c){var n=[0,0,0];for(var i=0;i<t.length;i++)if(/\S/.test(t.charAt(i)))n[+c.charAt(i)]++;return n;}
  // 連續同色的片段（只留有字的，丟掉只剩標點的）
  function frags(t,c,code){
    var out=[],run='';
    function push(){var x=run.trim();run='';if(/[一-鿿A-Za-z0-9]/.test(x))out.push(x.length>36?x.slice(0,35)+'…':x);}
    for(var i=0;i<t.length;i++){if(t.charAt(i)!=='\n'&&+c.charAt(i)===code)run+=t.charAt(i);else push();}
    push();return out;
  }
  function disclosure(t,c){
    var lines=['我在賀卡的文字上，用顏色標出哪些部分是誰完成的：'];
    [0,1,2].forEach(function(code){
      var f=frags(t,c,code);
      if(f.length)lines.push(LINE[code]+'：'+f.map(function(x){return '「'+x+'」';}).join('、')+'。');
      else lines.push(LINE[code]+'：沒有。');
    });
    return lines.join('\n');
  }
  function started(){return !!ta.value.trim()&&!!hid.value;}
  function render(){
    var t=ta.value.replace(/\r/g,''),c=norm(t,hid.value),on=started();
    paste.hidden=on;box.hidden=!on;
    if(on&&(t!==cur.text||c!==cur.codes)){paint(view,t,c);cur={text:t,codes:c};}
    if(on){var n=counts(t,c);sum.innerHTML='<span class="k">黑 '+n[0]+' 字</span><span class="r">紅 '+n[1]+' 字</span><span class="b">藍 '+n[2]+' 字</span>';}
    // 作品說明書「查證揭露」旁邊的顏色預覽
    if(show){show.hidden=!on;if(on)paint(showView,t,c);}
  }
  function save(c){setVal(hid,c);if(window.cardRefresh)window.cardRefresh();render();}

  $('mkStart').addEventListener('click',function(){
    var t=ta.value.replace(/\r/g,'').replace(/[ \t]+\n/g,'\n').trim();
    if(t.length<4){$('mkTip').textContent='先貼上賀卡的字（至少 4 個字）。';return;}
    ta.value=t.slice(0,800);ta.dispatchEvent(new Event('input',{bubbles:true}));
    cur={text:'',codes:'x'};setVal(ok,'');save(new Array(ta.value.length+1).join('0'));
  });
  $('mkRedo').addEventListener('click',function(){
    if(!confirm('重貼會清掉顏色，確定嗎？'))return;
    setVal(ok,'');cur={text:'',codes:'x'};setVal(hid,'');if(window.cardRefresh)window.cardRefresh();render();
  });
  // 選取 → 按顏色
  box.addEventListener('mousedown',function(e){if(e.target.closest('[data-mkc]'))e.preventDefault();});   // 不要讓按鈕把選取弄掉
  box.addEventListener('click',function(e){
    var b=e.target.closest('[data-mkc]');if(!b)return;
    var sel=window.getSelection(),code=b.dataset.mkc;
    if(!sel||!sel.rangeCount||sel.isCollapsed||!view.contains(sel.getRangeAt(0).commonAncestorContainer)){window.toast('先選字，再按顏色。');return;}
    var r=sel.getRangeAt(0),c=norm(ta.value.replace(/\r/g,''),hid.value).split(''),n=0;
    Array.prototype.forEach.call(view.querySelectorAll('.mc'),function(sp){
      if(!r.intersectsNode(sp))return;
      var tn=sp.firstChild;   // 邊界上的字（選取剛好停在它前面／後面）不算
      if(r.endContainer===tn&&r.endOffset===0)return;
      if(r.startContainer===tn&&r.startOffset>=tn.length)return;
      c[+sp.dataset.i]=code;n++;
    });
    sel.removeAllRanges();
    if(!n){window.toast('先選字，再按顏色。');return;}
    setVal(ok,'');save(c.join(''));
  });
  // 標好了：只記下「已完成」。標記後的文章獨立顯示在說明書「查證揭露」上方，交件匯出時才合併進去（不寫進文字格）
  $('mkDone').addEventListener('click',function(){
    if(!started())return;
    setVal(ok,'1');if(window.cardRefresh)window.cardRefresh();
    window.toast('標好了。會放在說明書的「查證揭露」上面。');
  });

  // 雲端資料讀回來、或每次存檔後同步畫面；基本資料預設帶入（作品名稱、年級），學生可以改
  function prefill(){
    var all=(window.cardData&&window.cardData())||{},id=(window.cardIdentity&&window.cardIdentity())||{};
    var t=$('m_title'),g=$('m_grade');
    if(t&&!t.value.trim()&&all.L1&&all.L1.title)setVal(t,all.L1.title);
    if(g&&!g.value.trim()&&id.grade)setVal(g,String(id.grade));
    var idea=$('m_idea');
    if(idea&&!idea.value.trim()&&all.L1&&all.L1.reason)setVal(idea,all.L1.reason);   // 第 1 節「為什麼想寫這個回憶」先帶進來，可以改
  }
  var P=window.PAGE=window.PAGE||{},old=P.onData;
  P.onData=function(a){if(old)try{old(a);}catch(e){}render();prefill();};
  render();
})();
