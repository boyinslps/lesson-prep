// 對外控制介面 window.Win11Sim（AI、關卡網頁、錄影腳本都用這個）。完整說明見 AI說明.md。
import { sys } from "./store";
import * as events from "./events";
import * as vfs from "./vfs";
import * as wm from "./wm";
import * as power from "./power";
import * as demo from "./demo";
import * as fileops from "./fileops";
import { loadScene, fetchScene } from "./scene";
import { registerApp, allApps, getApp } from "./apps";
import { registerSite } from "./sites";
import { setClock, simNow } from "./clock";
import { appStateOf } from "./appstate";
import { toast } from "./ui";
import { getDocInfo, createDoc, patchDoc, docUrl } from "./docs";

export const VERSION = "1.0.0";

function windowsInfo() {
  const s = sys.get();
  return s.windows.map((w) => ({ id: w.id, app: w.app, title: w.title, state: w.state, rect: w.rect, focused: w.id === s.focusedId, args: w.args, state_app: appStateOf(w.id) }));
}

export function snapshot() {
  const s = sys.get();
  return {
    version: VERSION,
    phase: s.phase,
    scene: s.scene,
    user: s.user.name,
    clock: new Date(simNow()).toISOString(),
    settings: s.settings,
    windows: windowsInfo(),
    focusedId: s.focusedId,
    desktop: { selection: s.desktopSelection, systemIcons: s.desktopSystemIcons },
    taskbarPins: s.taskbarPins,
    startOpen: s.startOpen,
    clipboard: s.clipboard,
    dialogs: s.dialogs.map((d) => ({ id: d.id, kind: d.kind, title: d.title, ownerId: d.ownerId, text: d.data?.text })),
    contextMenu: s.contextMenu ? s.contextMenu.items.filter((i) => i.label).map((i) => i.label) : null,
    toasts: s.toasts.map((t) => ({ title: t.title, text: t.text })),
    recent: s.recent,
    fs: vfs.snapshot(),
  };
}

let current = null; // 最近一次載入的場景（reset 用）

const api = {
  version: VERSION,
  async loadScene(nameOrSpec, opts) { current = nameOrSpec; return loadScene(nameOrSpec, opts); },
  async reset() { if (current) return loadScene(current); },
  fetchScene,
  snapshot,
  describeUI: demo.describeUI,
  locate: (t, i) => { const r = demo.locate(t, i); return r && { x: r.x, y: r.y, w: r.w, h: r.h, cx: r.cx, cy: r.cy }; },
  fs: {
    exists: vfs.exists, isDir: vfs.isDir, list: (p) => vfs.list(p).map((n) => n.name), stat: vfs.stat, read: vfs.readFile,
    tree: vfs.snapshot, mkdir: vfs.mkdir, create: vfs.create, write: vfs.writeFile, save: vfs.saveFile,
    rename: vfs.rename, move: vfs.move, copy: vfs.copy, trash: vfs.trash, restore: vfs.restore, emptyBin: vfs.emptyBin,
    deleteForever: vfs.deleteForever, undo: vfs.undo, redo: vfs.redo,
    bin: () => vfs.binItems().map((b) => ({ id: b.id, name: b.node.name, origPath: b.origPath })),
    join: vfs.join, basename: vfs.basename, dirname: vfs.dirname,
  },
  wm: {
    openApp: wm.openApp, openPath: wm.openPath, close: wm.closeWindow, closeAll: wm.closeAll, focus: wm.focusWindow,
    minimize: wm.minimizeWindow, maximize: wm.toggleMaximize, restore: wm.restoreWindow, showDesktop: wm.showDesktop,
    list: windowsInfo,
  },
  apps: { list: () => allApps().map((a) => ({ id: a.id, name: a.name, fileTypes: a.fileTypes || [], hidden: !!a.hidden })), register: registerApp, get: getApp },
  events: { on: events.on, log: events.log, clear: events.clearLog, waitFor: events.waitFor, emit: events.emit },
  demo,
  sys: {
    setSetting(k, v) { sys.set((s) => ({ settings: { ...s.settings, [k]: v } })); },
    setClock, power, toast,
    fullscreen() { return document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); },
    state: () => sys.get(),
  },
  docs: { get: getDocInfo, create: createDoc, patch: patchDoc, url: docUrl, list: () => Object.keys(sys.get().docs) },
  ops: fileops,
  registerSite,
  registerApp,
};

export default api;

// ---- 給外層網頁用的 postMessage 橋 ----
// 外層：iframe.contentWindow.postMessage({sim:"win11", id:1, method:"fs.exists", args:["C:\\\\x"]}, "*")
// 回覆：{sim:"win11", id:1, ok:true, result}；模擬器的事件會以 {sim:"win11-event", type, data} 推給外層。
export function installBridge() {
  if (window.parent === window) return;
  window.addEventListener("message", async (ev) => {
    const d = ev.data;
    if (!d || d.sim !== "win11" || !d.method) return;
    try {
      const fn = d.method.split(".").reduce((o, k) => (o == null ? o : o[k]), api);
      if (typeof fn !== "function") throw new Error("沒有這個方法: " + d.method);
      const result = await fn(...(d.args || []));
      ev.source.postMessage({ sim: "win11", id: d.id, ok: true, result: JSON.parse(JSON.stringify(result ?? null, (k, v) => (typeof v === "function" ? undefined : v))) }, "*");
    } catch (e) {
      ev.source.postMessage({ sim: "win11", id: d.id, ok: false, error: String(e.message || e) }, "*");
    }
  });
  events.on("*", (e) => { try { window.parent.postMessage({ sim: "win11-event", type: e.type, data: JSON.parse(JSON.stringify(e.data)) }, "*"); } catch (err) { /* ignore */ } });
  window.parent.postMessage({ sim: "win11-event", type: "ready", data: { version: VERSION } }, "*");
}
