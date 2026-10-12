// 場景（scene）：一份 JSON 描述「這個 Windows 一開始長什麼樣子」。關卡與錄影都靠它重現固定畫面。
// 欄位說明見 AI說明.md「Scene JSON」。路徑裡的 ~ 代表使用者資料夾 C:\Users\<name>。
import { sys } from "./store";
import { emit, clearLog } from "./events";
import * as vfs from "./vfs";
import { setClock } from "./clock";
import { closeAll, openApp } from "./wm";
import { FOLDER_NAMES } from "./paths";
import { asset } from "../shell/icons";

const DEFAULT_SETTINGS = { theme: "dark", showExtensions: false, showHidden: false, wallpaper: "wallpapers/roki.jpg", sound: true, desktopIcons: true, fastBoot: false };

export async function fetchScene(name) {
  const r = await fetch(asset(`scenes/${name}.json`), { cache: "no-store" });
  if (!r.ok) throw new Error("找不到場景 " + name);
  return r.json();
}

export async function loadScene(input, { keepLog = false } = {}) {
  const spec = typeof input === "string" ? await fetchScene(input) : input;
  closeAll();
  sys.set({ dialogs: [], contextMenu: null, toasts: [], desktopSelection: [], startOpen: false, quickOpen: false, calendarOpen: false, userMenuOpen: false, drag: null, clipboard: { files: null, text: "" }, recent: [], caption: null });
  if (!keepLog) clearLog();

  const user = { name: "學生", password: null, ...(spec.user || {}) };
  const settings = { ...DEFAULT_SETTINGS, ...(spec.settings || {}) };
  if (spec.wallpaper) settings.wallpaper = spec.wallpaper;
  setClock(spec.clock || null);
  sys.set({
    user, settings,
    taskbarPins: spec.taskbarPins || ["start", "explorer", "edge"],
    desktopSystemIcons: spec.desktopSystemIcons || ["recycle"],
    startPins: spec.startPins || null,
    sites: spec.sites || {},
    fsButton: !!spec.fsButton,
    scene: { id: spec.id || (typeof input === "string" ? input : "custom"), title: spec.title || "" },
  });

  // ---- 檔案系統 ----
  vfs.reset(spec.drives || ["C"]);
  const home = `C:\\Users\\${user.name}`;
  Object.values(FOLDER_NAMES).forEach((n) => vfs.mkdir(`${home}\\${n}`, { silent: true, parents: true }));
  const ex = (p) => (p.startsWith("~") ? home + p.slice(1) : p);
  vfs.mkdir("C:\\Windows", { silent: true });
  vfs.mkdir("C:\\Program Files", { silent: true });
  vfs.loadSpec((spec.files || []).map((f) => ({ ...f, path: ex(f.path) })));

  // 資源回收筒內的初始項目：{name, from?:"~\\文件", content?, size?}
  (spec.recycleBin || []).forEach((b) => {
    const dir = ex(b.from || "~\\桌面");
    vfs.mkdir(dir, { silent: true, parents: true });
    const type = b.type || (/\.[A-Za-z0-9]{1,6}$/.test(b.name) ? "file" : "dir");
    const p = vfs.create(dir, b.name, type, { content: b.content || "", size: b.size ?? null, silent: true });
    vfs.trash([p], { silent: true });
  });
  vfs.loadSpec([]); // 通知畫面更新
  emit("scene:loaded", { id: spec.id });

  // ---- 階段與視窗 ----
  sys.set({ phase: spec.start || "desktop" });
  (spec.windows || []).forEach((w) => {
    openApp(w.app, w.args ? { ...w.args, ...(w.args.path ? { path: ex(w.args.path) } : {}) } : {}, { rect: w.rect ? { x: w.rect[0], y: w.rect[1], w: w.rect[2], h: w.rect[3] } : undefined, state: w.state });
  });
  return sys.get().scene;
}
