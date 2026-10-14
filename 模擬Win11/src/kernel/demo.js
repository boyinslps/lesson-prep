// 示範游標引擎＋UI 定位。拿來：①錄教學影片（真的在畫面上操作）②關卡的示範游標 ③AI 用名稱找按鈕座標。
// 目標寫法 target：
//   "taskbar:start"                → data-sim-id 精確比對（可含 * 萬用字元，如 "desktop:icon:*作業*"）
//   "text:重新命名"                 → 畫面上可見、文字包含「重新命名」的最小元素
//   {x, y}                          → 螢幕座標
import { sys } from "./store";
import { emit } from "./events";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const visible = (el) => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none"; };

export function findAll(target) {
  if (typeof target === "object") return [];
  if (target.startsWith("text:")) {
    const t = target.slice(5);
    const all = Array.from(document.querySelectorAll(".sim-root *")).filter((el) => el.children.length === 0 || el.matches("button,a,span,div"));
    const hits = all.filter((el) => el.textContent.trim() === t && visible(el));
    return hits.length ? hits : all.filter((el) => el.textContent.includes(t) && visible(el) && Array.from(el.children).every((c) => !c.textContent.includes(t)));
  }
  if (target.includes("*")) {
    const re = new RegExp("^" + target.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*") + "$");
    return Array.from(document.querySelectorAll("[data-sim-id]")).filter((el) => re.test(el.getAttribute("data-sim-id")) && visible(el));
  }
  return Array.from(document.querySelectorAll(`[data-sim-id="${CSS.escape(target)}"]`)).filter(visible);
}

// 回傳 {x,y,w,h,cx,cy,el}；找不到回 null。index 用在多個符合時（預設取最上層可見者的最後一個）。
export function locate(target, index = 0) {
  if (target && typeof target === "object") return { x: target.x, y: target.y, w: 0, h: 0, cx: target.x, cy: target.y, el: document.elementFromPoint(target.x, target.y) };
  const list = findAll(target);
  const el = list[index];
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return { x: r.x, y: r.y, w: r.width, h: r.height, cx: r.x + r.width / 2, cy: r.y + r.height / 2, el };
}

// 目前畫面上所有帶 data-sim-id 的可見元素（AI 的「眼睛」，免截圖）
export function describeUI({ prefix = "" } = {}) {
  return Array.from(document.querySelectorAll("[data-sim-id]")).filter(visible).map((el) => {
    const r = el.getBoundingClientRect();
    return { id: el.getAttribute("data-sim-id"), x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), text: (el.innerText || "").trim().slice(0, 40) };
  }).filter((e) => e.id.startsWith(prefix));
}

const setCursor = (patch) => sys.set((s) => ({ cursor: { ...s.cursor, ...patch } }));
export const cursor = {
  show(x, y) { setCursor({ visible: true, ...(x != null ? { x, y, ms: 0 } : {}) }); },
  hide() { setCursor({ visible: false }); },
  async moveTo(target, { ms = 600 } = {}) {
    let p = typeof target === "object" && target.x != null && target.cx == null ? target : locate(target);
    if (!p) throw new Error("demo: 找不到目標 " + JSON.stringify(target));
    if (p.el && p.el.scrollIntoView && typeof target !== "object") { p.el.scrollIntoView({ block: "nearest", inline: "nearest" }); p = locate(target); } // 被捲動區域遮住時先捲到可見
    const x = p.cx ?? p.x, y = p.cy ?? p.y;
    setCursor({ visible: true, x, y, ms });
    await sleep(ms + 30);
    return p;
  },
};

const mouseInit = (x, y, extra = {}) => ({ bubbles: true, cancelable: true, composed: true, clientX: x, clientY: y, screenX: x, screenY: y, view: window, button: 0, buttons: 0, ...extra });
function fire(el, type, x, y, extra = {}) {
  const P = type.startsWith("pointer");
  const ev = P ? new PointerEvent(type, { ...mouseInit(x, y, extra), pointerId: 1, pointerType: "mouse", isPrimary: true }) : new MouseEvent(type, mouseInit(x, y, extra));
  return el.dispatchEvent(ev);
}
const at = (x, y) => document.elementFromPoint(x, y) || document.body;

async function press(x, y, button = 0, mods = {}) {
  setCursor({ pressed: true });
  const el = at(x, y);
  const b = { button, buttons: button === 0 ? 1 : 2, ...mods };
  fire(el, "pointerdown", x, y, b);
  const proceed = fire(el, "mousedown", x, y, b); // 網頁對 mousedown 呼叫 preventDefault（例如工具列按鈕）→ 不改變焦點，跟真滑鼠一樣
  if (button === 0 && proceed) { // 假事件不會自動移動焦點：自己模擬「按下滑鼠時，焦點移到最近的可聚焦元素」
    const f = el.closest && el.closest("input,textarea,select,[tabindex],[contenteditable]");
    if (f) { const was = document.activeElement === f; f.focus(); if (!was && "value" in f && f.setSelectionRange && f.type !== "range" && f.type !== "checkbox") { try { f.setSelectionRange(f.value.length, f.value.length); } catch (e) { /* ignore */ } } }
    else if (document.activeElement && document.activeElement !== document.body) document.activeElement.blur();
  }
  return el;
}
async function release(x, y, button = 0, mods = {}) {
  const el = at(x, y);
  const b = { button, buttons: 0, ...mods };
  fire(el, "pointerup", x, y, b); fire(el, "mouseup", x, y, b);
  setCursor({ pressed: false });
  return el;
}

export async function click(target, o = {}) {
  const p = await cursor.moveTo(target, o);
  const x = p.cx ?? p.x, y = p.cy ?? p.y;
  const m = o.mods || {};
  await press(x, y, 0, m); await sleep(70); const el = await release(x, y, 0, m);
  fire(el, "click", x, y, { button: 0, detail: 1, ...m });
  await sleep(o.after ?? 250);
  return p;
}
export async function dblclick(target, o = {}) {
  const p = await cursor.moveTo(target, o);
  const x = p.cx, y = p.cy;
  for (let i = 1; i <= 2; i++) {
    await press(x, y); await sleep(50); const el = await release(x, y);
    fire(el, "click", x, y, { detail: i });
    if (i === 2) fire(el, "dblclick", x, y, { detail: 2 });
    await sleep(80);
  }
  await sleep(o.after ?? 350);
  return p;
}
export async function rightclick(target, o = {}) {
  const p = await cursor.moveTo(target, o);
  const x = p.cx ?? p.x, y = p.cy ?? p.y;
  await press(x, y, 2); await sleep(60);
  const el = await release(x, y, 2);
  fire(el, "contextmenu", x, y, { button: 2, buttons: 2 });
  await sleep(o.after ?? 350);
  return p;
}
export async function drag(from, to, o = {}) {
  const a = await cursor.moveTo(from, o);
  const ax = a.cx ?? a.x, ay = a.cy ?? a.y;
  await press(ax, ay, 0, o.mods || {});
  await sleep(120);
  const b = locate(to);
  if (!b) throw new Error("demo: 找不到拖放目標 " + JSON.stringify(to));
  const bx = b.cx ?? b.x, by = b.cy ?? b.y, steps = 14, ms = o.ms ?? 800;
  setCursor({ ms: ms / steps });
  for (let i = 1; i <= steps; i++) {
    const x = ax + ((bx - ax) * i) / steps, y = ay + ((by - ay) * i) / steps;
    setCursor({ x, y });
    const el = at(x, y);
    fire(el, "pointermove", x, y, { buttons: 1, ...(o.mods || {}) }); fire(el, "mousemove", x, y, { buttons: 1 });
    await sleep(ms / steps);
  }
  await sleep(150);
  await release(bx, by, 0, o.mods || {});
  await sleep(o.after ?? 400);
}

const KEYMAP = { ctrl: "Control", shift: "Shift", alt: "Alt", win: "Meta", meta: "Meta", del: "Delete", esc: "Escape", enter: "Enter", return: "Enter", backspace: "Backspace", tab: "Tab", space: " ", up: "ArrowUp", down: "ArrowDown", left: "ArrowLeft", right: "ArrowRight", insert: "Insert", home: "Home", end: "End" };
// 按鍵：key("Ctrl+C")、key("F2")、key("Delete")、key("Alt+F4")
export async function key(combo, o = {}) {
  // "Ctrl+C"、"F2"；按加號本身寫成 "Ctrl++"
  const plus = combo === "+" || combo.endsWith("++");
  const parts = (plus ? combo.slice(0, -1) : combo).split("+").map((s) => s.trim()).filter((s, i, a) => s || i < a.length - 1);
  const main = plus ? "+" : parts.pop();
  if (plus && parts[parts.length - 1] === "") parts.pop();
  const mods = { ctrlKey: false, shiftKey: false, altKey: false, metaKey: false };
  parts.forEach((p) => { const k = p.toLowerCase(); if (k === "ctrl") mods.ctrlKey = true; else if (k === "shift") mods.shiftKey = true; else if (k === "alt") mods.altKey = true; else mods.metaKey = true; });
  const k = KEYMAP[main.toLowerCase()] || (main.length === 1 ? (mods.shiftKey ? main.toUpperCase() : main) : main);
  const target = document.activeElement && document.activeElement !== document.body ? document.activeElement : document.body;
  const init = { bubbles: true, cancelable: true, key: k, code: /^[a-z]$/i.test(main) ? "Key" + main.toUpperCase() : k, ...mods };
  sys.set((s) => ({ lastKey: combo }));
  const notPrevented = target.dispatchEvent(new KeyboardEvent("keydown", init));
  await sleep(80);
  target.dispatchEvent(new KeyboardEvent("keyup", init));
  emit("demo:key", { combo });
  await sleep(o.after ?? 250);
  return notPrevented;
}

// 輸入文字到目前焦點的輸入框／textarea（逐字，模擬打字）
export async function type(text, { delay = 60, after = 250 } = {}) {
  const el = document.activeElement;
  if (el && el.isContentEditable) { // 文件編輯區：用 execCommand 逐字插入（產生真的 input 事件）
    for (const ch of text) {
      const nl = ch === String.fromCharCode(10);
      el.dispatchEvent(new KeyboardEvent("keydown", { bubbles: true, cancelable: true, key: nl ? "Enter" : ch }));
      document.execCommand(nl ? "insertParagraph" : "insertText", false, ch);
      el.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true, key: ch }));
      await sleep(delay);
    }
    await sleep(after);
    return;
  }
  if (!el || !("value" in el)) throw new Error("demo.type: 目前焦點不在輸入框");
  const proto = el.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  const setter = Object.getOwnPropertyDescriptor(proto, "value").set;
  for (const ch of text) {
    el.dispatchEvent(new KeyboardEvent("keydown", { bubbles: true, cancelable: true, key: ch }));
    const s = el.selectionStart ?? el.value.length, e = el.selectionEnd ?? el.value.length;
    const v = el.value.slice(0, s) + (ch === "\n" ? "\n" : ch) + el.value.slice(e);
    setter.call(el, v);
    el.setSelectionRange(s + 1, s + 1);
    el.dispatchEvent(new InputEvent("input", { bubbles: true, data: ch, inputType: "insertText" }));
    el.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true, key: ch }));
    await sleep(delay);
  }
  await sleep(after);
}

// 選取文字（假事件選不到字，所以直接設定選取範圍；游標會從頭拖到尾做給人看）
// select("gdoc:page", {text:"自我介紹"})：選取該元素內第一個符合的文字；select("gdoc:page", {all:true})：全選；{caret:"end"}：只放游標
export async function select(target, { text, all, caret, ms = 500, after = 300 } = {}) {
  const p = locate(target);
  if (!p) throw new Error("demo.select: 找不到目標 " + target);
  const root = p.el;
  const editable = root.closest("[contenteditable]") || root;
  editable.focus && editable.focus();
  const sel = window.getSelection();
  const range = document.createRange();
  let startRect = null, endRect = null;
  if (all) range.selectNodeContents(root);
  else if (caret) { range.selectNodeContents(root); range.collapse(caret !== "start"); }
  else {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let n, found = false;
    while ((n = walker.nextNode())) { const i = n.nodeValue.indexOf(text); if (i >= 0) { range.setStart(n, i); range.setEnd(n, i + text.length); found = true; break; } }
    if (!found) throw new Error("demo.select: 找不到文字 " + text);
  }
  const rects = range.getClientRects();
  if (rects.length) { startRect = rects[0]; endRect = rects[rects.length - 1]; }
  if (startRect) {
    await cursor.moveTo({ x: startRect.left + 1, y: startRect.top + startRect.height / 2 }, { ms });
    if (!caret) { setCursor({ pressed: true }); await cursor.moveTo({ x: endRect.right, y: endRect.top + endRect.height / 2 }, { ms: Math.min(700, 250 + (text ? text.length * 40 : 300)) }); setCursor({ pressed: false }); }
  }
  sel.removeAllRanges(); sel.addRange(range);
  emit("demo:select", { text: text || (all ? "(all)" : "(caret)") });
  await sleep(after);
}

export const wait = sleep;
export function caption(text, sub = "") { sys.set({ caption: text ? { text, sub } : null }); }

// 劇本：steps = [{do:"click", target:"…"}, {do:"type", text:"…"}, {do:"key", key:"F2"}, {do:"drag", from, to}, {do:"wait", ms}, {do:"caption", text}, …]
export async function run(steps, { cursorVisible = true } = {}) {
  if (cursorVisible) cursor.show();
  emit("demo:start", { steps: steps.length });
  for (const s of steps) {
    const t = s.do;
    if (t === "click") await click(s.target, s);
    else if (t === "dblclick") await dblclick(s.target, s);
    else if (t === "rightclick") await rightclick(s.target, s);
    else if (t === "move") await cursor.moveTo(s.target, s);
    else if (t === "drag") await drag(s.from, s.to, s);
    else if (t === "select") await select(s.target, s);
    else if (t === "key") await key(s.key, s);
    else if (t === "type") await type(s.text, s);
    else if (t === "wait") await sleep(s.ms ?? 500);
    else if (t === "caption") caption(s.text, s.sub);
    else if (t === "scene") { const { loadScene } = await import("./scene"); await loadScene(s.name || s.scene); }
    else throw new Error("demo: 不認得的步驟 " + t);
  }
  emit("demo:end", {});
}
