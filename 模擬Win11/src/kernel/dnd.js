// 以 pointer 事件實作的拖放（不用 HTML5 DnD，這樣示範游標／自動化腳本也能驅動）。
// 來源：在 pointerdown 呼叫 startDrag(e, paths)。目標：任何帶 data-drop-path 的元素（目錄路徑、"::recycle" 或 "::desktop"）。
import { sys } from "./store";
import { emit } from "./events";

let handler = null; // (paths, target, {copy, ownerId}) => void，由 fileops 設定
export const setDropHandler = (fn) => { handler = fn; };

export function startDrag(e, paths, { label = "", icon = "file", ownerId = null } = {}) {
  if (e.button !== 0) return;
  const sx = e.clientX, sy = e.clientY;
  let active = false;
  const move = (ev) => {
    if (!active && Math.hypot(ev.clientX - sx, ev.clientY - sy) < 5) return;
    active = true;
    const el = document.elementFromPoint(ev.clientX, ev.clientY);
    const t = el && el.closest("[data-drop-path]");
    sys.set({ drag: { paths, label, icon, x: ev.clientX, y: ev.clientY, over: t ? t.getAttribute("data-drop-path") : null, copy: ev.ctrlKey } });
  };
  const up = (ev) => {
    window.removeEventListener("pointermove", move, true);
    window.removeEventListener("pointerup", up, true);
    if (!active) return;
    const el = document.elementFromPoint(ev.clientX, ev.clientY);
    const t = el && el.closest("[data-drop-path]");
    sys.set({ drag: null });
    emit("ui:drop", { paths, target: t ? t.getAttribute("data-drop-path") : null });
    if (t && handler) handler(paths, t.getAttribute("data-drop-path"), { copy: ev.ctrlKey, ownerId });
  };
  window.addEventListener("pointermove", move, true);
  window.addEventListener("pointerup", up, true);
}
