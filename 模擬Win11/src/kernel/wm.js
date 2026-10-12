// 視窗管理：開／關／焦點／最小化／最大化／貼齊。所有動作都 emit win:* 事件。
import { sys } from "./store";
import { emit } from "./events";
import { getApp, appForExt } from "./apps";
import * as vfs from "./vfs";

export const TASKBAR_H = 48;
let winSeq = 0;
const guards = new Map(); // windowId -> async () => boolean（回傳 false 取消關閉）

export const desktopArea = () => ({ w: window.innerWidth, h: window.innerHeight - TASKBAR_H });
export const registerGuard = (id, fn) => { guards.set(id, fn); return () => guards.delete(id); };

const update = (id, patch) => sys.set((s) => ({ windows: s.windows.map((w) => (w.id === id ? { ...w, ...(typeof patch === "function" ? patch(w) : patch) } : w)) }));
export const getWindow = (id) => sys.get().windows.find((w) => w.id === id);

export function openApp(appId, args = {}, opts = {}) {
  const app = getApp(appId);
  if (!app) { emit("sys:error", { msg: "找不到應用程式 " + appId }); return null; }
  const s = sys.get();
  if (app.singleton) {
    const ex = s.windows.find((w) => w.app === appId);
    if (ex) { if (args && Object.keys(args).length) update(ex.id, { args: { ...ex.args, ...args, _n: (ex.args._n || 0) + 1 } }); restoreWindow(ex.id); return ex.id; }
  }
  const id = "w" + ++winSeq;
  const D = desktopArea();
  const w = Math.min(opts.rect?.w || app.defaultSize.w, D.w), h = Math.min(opts.rect?.h || app.defaultSize.h, D.h);
  const n = s.windows.filter((x) => x.state !== "min").length % 6;
  const x = opts.rect?.x ?? Math.max(0, Math.round((D.w - w) / 2) - 60 + n * 30);
  const y = opts.rect?.y ?? Math.max(0, Math.round((D.h - h) / 2) - 30 + n * 30);
  const z = s.zCounter + 1;
  const win = { id, app: appId, title: app.title ? app.title(args) : app.name, args, rect: { x, y, w, h }, restoreRect: null, state: opts.state || "normal", z, icon: app.icon };
  if (win.state === "max") { win.restoreRect = { ...win.rect }; }
  sys.set({ windows: [...s.windows, win], zCounter: z, focusedId: id, startOpen: false, searchOpen: false, quickOpen: false, calendarOpen: false, userMenuOpen: false, contextMenu: null });
  emit("win:open", { id, app: appId, args });
  return id;
}

export function openPath(path, { ownerId } = {}) {
  const st = vfs.stat(path);
  if (!st) { emit("sys:error", { msg: "找不到 " + path }); return false; }
  if (st.type === "dir") { openApp("explorer", { path: vfs.norm(path) }); return true; }
  const appId = appForExt(st.ext);
  emit("file:open", { path: vfs.norm(path), app: appId });
  if (appId) { openApp(appId, { path: vfs.norm(path) }); return true; }
  return false;
}

export function focusWindow(id) {
  const s = sys.get();
  const w = s.windows.find((x) => x.id === id);
  if (!w) return;
  if (s.focusedId === id && w.state !== "min") return;
  const z = s.zCounter + 1;
  sys.set({ zCounter: z, focusedId: id, windows: s.windows.map((x) => (x.id === id ? { ...x, z, state: x.state === "min" ? (x.prev || "normal") : x.state } : x)) });
  emit("win:focus", { id, app: w.app });
}

export function restoreWindow(id) {
  const w = getWindow(id);
  if (!w) return;
  if (w.state === "min") { focusWindow(id); emit("win:restore", { id, app: w.app }); }
  else focusWindow(id);
  sys.set({ startOpen: false });
}

export function minimizeWindow(id) {
  const s = sys.get();
  const w = getWindow(id);
  if (!w || w.state === "min") return;
  update(id, { state: "min", prev: w.state });
  // 焦點移給下一個最上層、未最小化的視窗
  const next = sys.get().windows.filter((x) => x.state !== "min").sort((a, b) => b.z - a.z)[0];
  sys.set({ focusedId: next ? next.id : null });
  emit("win:minimize", { id, app: w.app });
}

export function toggleMaximize(id) {
  const w = getWindow(id);
  if (!w) return;
  if (w.state === "max") {
    update(id, { state: "normal", rect: w.restoreRect || w.rect, restoreRect: null });
    emit("win:restore", { id, app: w.app });
  } else {
    update(id, { state: "max", restoreRect: { ...w.rect } });
    emit("win:maximize", { id, app: w.app });
  }
  focusWindow(id);
}

export function snapWindow(id, side) {
  const w = getWindow(id);
  const D = desktopArea();
  if (!w) return;
  const base = w.restoreRect || w.rect;
  update(id, { state: "normal", restoreRect: base, rect: { x: side === "left" ? 0 : D.w / 2, y: 0, w: D.w / 2, h: D.h } });
  emit("win:snap", { id, app: w.app, side });
}

export function moveWindow(id, rect) { update(id, (w) => ({ rect: { ...w.rect, ...rect } })); }
export function setTitle(id, title) { update(id, { title }); }

export async function closeWindow(id, { force = false } = {}) {
  const w = getWindow(id);
  if (!w) return false;
  if (!force && guards.has(id)) {
    const ok = await guards.get(id)();
    if (!ok) return false;
  }
  guards.delete(id);
  const s = sys.get();
  const rest = s.windows.filter((x) => x.id !== id);
  const next = s.focusedId === id ? rest.filter((x) => x.state !== "min").sort((a, b) => b.z - a.z)[0] : null;
  sys.set({ windows: rest, focusedId: s.focusedId === id ? (next ? next.id : null) : s.focusedId, dialogs: s.dialogs.filter((d) => d.ownerId !== id) });
  emit("win:close", { id, app: w.app, args: w.args });
  return true;
}

export function closeAll() { sys.get().windows.forEach((w) => closeWindow(w.id, { force: true })); }

export function showDesktop() {
  const s = sys.get();
  const vis = s.windows.filter((w) => w.state !== "min");
  if (vis.length) {
    sys.set({ windows: s.windows.map((w) => (w.state === "min" ? w : { ...w, state: "min", prev: w.state })), focusedId: null });
    emit("win:showDesktop", {});
  } else {
    sys.set({ windows: s.windows.map((w) => ({ ...w, state: w.prev || "normal" })) });
  }
}
