/* ============================================================
   chair-gate.js — 繳交前「靠椅子」提醒＋等待關卡（學習單通用，無相依、不改學習單原本的繳交程式）
   規格權威來源：引導規範/學習單資料與提交規範.md §3-e

   原理：在 document 捕獲階段攔截 #submitBtn 的點擊。
     1. 沒填好身分（localStorage wk_identity）→ 直接放行，讓學習單自己提醒。
     2. 查 Firestore：chairSettings/main（總開關、等待秒數階梯、下課前免罰分鐘、節次時間）與 chairLog/{年級-班級-座號}。
     3. 該生有待處理紀錄（pending）且總開關開著 → 蓋一層全螢幕提醒（😠 ＋ 累計次數 ＋ 倒數），倒數完才放行。
        下課前 graceMin 分鐘內：不用等，但紀錄照樣累計（次數不變）；處理後 pending 清掉。
     4. 任何一步失敗／逾時 → 放行。這個關卡絕不可以擋住學生交作業。
   放行＝把 passed 設 true 後再 btn.click() 一次，原本學習單的 onclick 完全不知道被攔過。

   由 引導規範/chair-gate/inject.py 用 CHAIR-GATE-START/END 兩個 HTML 註解標記包起來，內嵌進每份學習單；
   要改邏輯就改這個檔再重跑 inject.py（idempotent，會整段取代）。
   ============================================================ */
(function () {
  if (window.__chairGate) return;
  window.__chairGate = true;

  var BTN_ID = 'submitBtn';
  var TIMEOUT_MS = 4500;            // 查資料超過這麼久就放行
  var DEFAULT_STEPS = [3, 10, 20, 30, 60];
  var passed = false, busy = false;

  function digits(v) { return String(v == null ? '' : v).replace(/[^0-9]/g, ''); }
  function identity() {
    try {
      var o = JSON.parse(localStorage.getItem('wk_identity') || '{}');
      var g = digits(o.grade), c = digits(o.className), s = digits(o.studentId);
      if (!g || !c || !s) return null;
      return { grade: Number(g), className: Number(c), studentId: Number(s) };
    } catch (e) { return null; }
  }

  function withTimeout(p, ms) {
    return new Promise(function (resolve, reject) {
      var t = setTimeout(function () { reject(new Error('timeout')); }, ms);
      p.then(function (v) { clearTimeout(t); resolve(v); }, function (e) { clearTimeout(t); reject(e); });
    });
  }

  // 有登入就沿用；確定沒有任何登入狀態才匿名登入（不能蓋掉老師的 session，見規範 §5-2）
  function ensureUser(auth) {
    return new Promise(function (resolve, reject) {
      var unsub = auth.onAuthStateChanged(function (u) {
        if (unsub) { unsub(); unsub = null; }
        if (u) resolve(u);
        else auth.signInAnonymously().then(function (c) { resolve(c.user); }, reject);
      });
    });
  }

  function steps(cfg) {
    var a = (cfg && cfg.steps || []).map(Number).filter(function (n) { return n > 0 && isFinite(n); });
    return a.length ? a : DEFAULT_STEPS;
  }
  function waitSeconds(cfg, count) {
    var a = steps(cfg);
    return a[Math.min(Math.max(count, 1), a.length) - 1];
  }
  // 現在是不是某一節「下課前 graceMin 分鐘」以內
  function inGrace(cfg) {
    var g = Number(cfg && cfg.graceMin);
    if (!isFinite(g) || g < 0) g = 2;      // 沒設才用預設 2 分鐘；老師設 0＝不免罰
    var now = new Date(), nowSec = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
    return (cfg && cfg.periods || []).some(function (p) {
      var m = /^(\d{1,2}):(\d{2})$/.exec(String(p && p.end || ''));
      if (!m) return false;
      var endSec = (+m[1]) * 3600 + (+m[2]) * 60, left = endSec - nowSec;
      return left > 0 && left <= g * 60;
    });
  }

  function overlay(count, waitSec, waived) {
    return new Promise(function (resolve) {
      var css = document.createElement('style');
      css.textContent =
        '#chairGate{position:fixed;inset:0;z-index:2147483000;background:rgba(15,23,42,.72);display:grid;place-items:center;padding:20px;font-family:inherit}' +
        '#chairGate .cg{background:#fff;border-radius:22px;max-width:420px;width:100%;padding:26px 22px 22px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.4);border:4px solid #f87171}' +
        '#chairGate .em{font-size:78px;line-height:1;animation:cgShake .5s ease-in-out 2}' +
        '#chairGate h2{margin:10px 0 6px;font-size:24px;color:#b91c1c;font-weight:900}' +
        '#chairGate .cnt{display:inline-block;margin:6px 0 10px;padding:4px 14px;border-radius:999px;background:#fee2e2;color:#991b1b;font-weight:800;font-size:16px}' +
        '#chairGate .msg{font-size:17px;font-weight:700;color:#334155;margin:6px 0 14px;min-height:26px}' +
        '#chairGate .msg b{font-size:30px;color:#dc2626}' +
        '#chairGate button{font:inherit;font-weight:800;font-size:17px;width:100%;padding:12px;border:0;border-radius:12px;cursor:pointer}' +
        '#chairGate .go{background:#dc2626;color:#fff}#chairGate .go:disabled{background:#e2e8f0;color:#94a3b8;cursor:not-allowed}' +
        '#chairGate .back{margin-top:8px;background:transparent;color:#64748b;font-size:14px;font-weight:600}' +
        '@keyframes cgShake{0%,100%{transform:rotate(0)}25%{transform:rotate(-12deg)}75%{transform:rotate(12deg)}}';
      document.head.appendChild(css);
      var box = document.createElement('div');
      box.id = 'chairGate';
      box.innerHTML =
        '<div class="cg" role="alertdialog" aria-live="polite">' +
        '<div class="em">😠</div>' +
        '<h2>上次下課四步驟沒有做確實</h2>' +
        '<div class="cnt">已累計 ' + count + ' 次紀錄</div>' +
        '<div class="msg" id="cgMsg"></div>' +
        '<button class="go" id="cgGo" disabled></button>' +
        '<button class="back" id="cgBack">先回去檢查，等一下再交</button>' +
        '</div>';
      document.body.appendChild(box);
      var msg = box.querySelector('#cgMsg'), go = box.querySelector('#cgGo');
      function close(ok) {
        clearInterval(timer);
        box.remove(); css.remove();
        resolve(ok);
      }
      var endAt = Date.now() + waitSec * 1000, timer = null;
      function tick() {
        var left = Math.ceil((endAt - Date.now()) / 1000);
        if (left > 0) {
          msg.innerHTML = '請等待 <b>' + left + '</b> 秒才可以繳交';
          go.disabled = true; go.textContent = '等待中…';
        } else {
          clearInterval(timer);
          msg.textContent = '時間到了，下次記得做確實喔！';
          go.disabled = false; go.textContent = '我知道了，繳交';
        }
      }
      if (waived) {
        msg.textContent = '快下課了，這次不用等待；但這筆紀錄還是會累計。';
        go.disabled = false; go.textContent = '我知道了，繳交';
      } else {
        tick(); timer = setInterval(tick, 250);
      }
      go.onclick = function () { if (!go.disabled) close(true); };
      box.querySelector('#cgBack').onclick = function () { close(false); };
    });
  }

  // 回傳 Promise<boolean>：true＝放行繳交
  function check(idn) {
    if (!window.firebase || !firebase.apps || !firebase.apps.length) return Promise.resolve(true);
    var id = idn.grade + '-' + idn.className + '-' + idn.studentId;
    var db = firebase.firestore();
    return withTimeout(ensureUser(firebase.auth()).then(function () {
      return Promise.all([
        db.collection('chairSettings').doc('main').get(),
        db.collection('chairLog').doc(id).get()
      ]);
    }), TIMEOUT_MS).then(function (r) {
      var cfg = r[0].exists ? r[0].data() : null, log = r[1].exists ? r[1].data() : null;
      if (!cfg || !cfg.enabled || !log || !log.pending) return true;
      var count = Number(log.count) || 1, waived = inGrace(cfg);
      return overlay(count, waitSeconds(cfg, count), waived).then(function (ok) {
        if (ok) {   // 處理完（等完或免罰）就把待處理清掉；累計次數不動。失敗不影響繳交。
          db.collection('chairLog').doc(id)
            .update({ pending: false, servedAt: firebase.firestore.FieldValue.serverTimestamp() })
            .catch(function (e) { console.warn('chairGate 更新狀態失敗', e); });
        }
        return ok;
      });
    }).catch(function (e) {
      console.warn('chairGate 檢查失敗，直接放行', e);
      return true;
    });
  }

  document.addEventListener('click', function (e) {
    var btn = e.target && e.target.closest && e.target.closest('#' + BTN_ID);
    if (!btn || passed) return;
    var idn = identity();
    if (!idn) return;                       // 沒填身分：交給學習單自己提醒
    e.stopImmediatePropagation();
    e.preventDefault();
    if (busy) return;
    busy = true;
    check(idn).then(function (ok) {
      busy = false;
      if (!ok) return;
      passed = true;
      try { btn.click(); } finally { passed = false; }
    });
  }, true);
})();
