/* ============================================================
   stepcards.js — 步驟卡：一個畫面一小步（動圖循環播放、只載入目前那一張）
   規格：引導規範/HTML互動教材設計規範.md §5.12
   標記：
     <div class="sc" data-sc>
       <div class="sc-slide"><p class="sc-t">這一小步做什麼</p>
         <div class="sc-media" data-src="assets/步_xxx.mp4" data-poster="assets/步_xxx_封面.jpg"></div>  （可省略：純文字小步）
         …其他想放的 HTML…
       </div> …
     </div>
   導覽列（上一小步／下一小步／點點）由這支程式自己補。
   影片＝靜音、循環、自動播放的短片（等同 GIF，但檔案小十倍）；點一下可暫停。
   由 引導規範/stepcards/inject.py 用 STEPCARDS-START/END 兩個 HTML 註解標記包起來，內嵌進學習單。
   ============================================================ */
(function () {
  if (window.__stepCards) return;
  window.__stepCards = true;

  // 只有「看得到」的那一小步才載入影片（display:none 的不載入）；每半秒檢查一次，換步驟、換分頁都會跟上
  function visible(m) { return m.offsetParent !== null; }
  function sweep() { [].forEach.call(document.querySelectorAll('.sc-media'), function (m) { setMedia(m, visible(m)); }); }

  function setMedia(m, on) {
    var v = m.querySelector('video');
    if (on && !v) {
      v = document.createElement('video');
      v.src = m.dataset.src;
      if (m.dataset.poster) v.poster = m.dataset.poster;
      v.muted = true; v.loop = true; v.autoplay = true; v.playsInline = true; v.setAttribute('playsinline', '');
      v.addEventListener('click', function () {
        if (v.paused) { v.play(); m.classList.remove('paused'); } else { v.pause(); m.classList.add('paused'); }
      });
      m.appendChild(v);
      var h = document.createElement('span'); h.className = 'sc-hint'; h.textContent = '點一下暫停'; m.appendChild(h);
      var p = v.play(); if (p && p.catch) p.catch(function () { m.classList.add('paused'); });
    } else if (!on && v) {
      m.innerHTML = ''; m.classList.remove('paused');
    }
  }

  function init(sc) {
    if (sc.__scReady) return; sc.__scReady = true;
    var slides = [].slice.call(sc.querySelectorAll(':scope > .sc-slide')), cur = 0, seen = {};
    var nav = document.createElement('div'); nav.className = 'sc-nav';
    nav.innerHTML = '<button type="button" class="sc-prev">← 上一小步</button><div class="sc-dots"></div><button type="button" class="sc-next">下一小步 →</button>';
    sc.appendChild(nav);
    var prev = nav.querySelector('.sc-prev'), next = nav.querySelector('.sc-next'), dots = nav.querySelector('.sc-dots');
    slides.forEach(function (s, i) {
      var d = document.createElement('i'); d.title = '第 ' + (i + 1) + ' 小步';
      d.onclick = function () { go(i); }; dots.appendChild(d);
    });
    function go(i) {
      cur = Math.max(0, Math.min(slides.length - 1, i)); seen[cur] = true;
      slides.forEach(function (s, k) {
        s.classList.toggle('on', k === cur);
      });
      sweep();
      [].forEach.call(dots.children, function (d, k) { d.className = k === cur ? 'on' : (seen[k] ? 'seen' : ''); });
      prev.disabled = cur === 0; next.disabled = cur === slides.length - 1;
      next.style.visibility = slides.length > 1 ? 'visible' : 'hidden'; prev.style.visibility = next.style.visibility;
      sc.dispatchEvent(new CustomEvent('sc:change', { detail: { index: cur, total: slides.length }, bubbles: true }));
    }
    prev.onclick = function () { go(cur - 1); };
    next.onclick = function () { go(cur + 1); };
    sc.__scGo = go;
    go(0);
  }

  function boot() { [].forEach.call(document.querySelectorAll('[data-sc]'), init); sweep(); }
  setInterval(sweep, 500);
  window.StepCards = { init: boot, reset: function (sc) { if (sc && sc.__scGo) sc.__scGo(0); } };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
