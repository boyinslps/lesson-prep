// 極簡全域 store（不依賴任何套件）。React 端用 useStore(selector)。
import { useSyncExternalStore, useRef } from "react";

export function createStore(initial) {
  let state = initial;
  const subs = new Set();
  return {
    get: () => state,
    set(patch) {
      const next = typeof patch === "function" ? patch(state) : patch;
      if (!next || next === state) return;
      state = { ...state, ...next };
      subs.forEach((f) => f());
    },
    subscribe(f) {
      subs.add(f);
      return () => subs.delete(f);
    },
  };
}

function shallowEq(a, b) {
  if (Object.is(a, b)) return true;
  if (typeof a !== "object" || typeof b !== "object" || !a || !b) return false;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  const ka = Object.keys(a), kb = Object.keys(b);
  if (ka.length !== kb.length) return false;
  return ka.every((k) => Object.is(a[k], b[k]));
}

// selector 回傳新陣列／物件也沒關係：內容淺比較相同就回傳上一次的結果（避免無限重繪）
export function useStoreOf(store, selector = (s) => s) {
  const sel = useRef(selector);
  const last = useRef(undefined);
  sel.current = selector;
  return useSyncExternalStore(store.subscribe, () => {
    const next = sel.current(store.get());
    if (last.current !== undefined && shallowEq(last.current, next)) return last.current;
    last.current = next;
    return next;
  });
}

// 系統狀態（視窗、剪貼簿、選單、對話框…）
export const sys = createStore({
  phase: "desktop", // off | sleep | restarting | lock | login | desktop
  user: { name: "學生", password: null, avatar: null },
  settings: {
    theme: "dark",
    showExtensions: false, // 真實 Windows 預設隱藏已知副檔名
    showHidden: false,
    wallpaper: "wallpapers/roki.jpg",
    sound: true,
    desktopIcons: true,
    desktopView: "medium",
  },
  clockBase: null, // null=真實時間；字串=固定時鐘起點（ISO）
  clockStart: 0,
  windows: [], // {id, app, title, args, rect:{x,y,w,h}, state:'normal'|'max'|'min', z}
  focusedId: null,
  zCounter: 10,
  clipboard: { files: null, text: "" }, // files: {paths:[], mode:'copy'|'cut'}
  startOpen: false,
  searchOpen: false,
  quickOpen: false,
  calendarOpen: false,
  userMenuOpen: false,
  contextMenu: null, // {x,y,items,owner}
  dialogs: [], // {id, ownerId, kind, ...}
  toasts: [],
  desktopSelection: [], // 桌面選取的項目（路徑或系統圖示 id）
  scene: null,
  taskbarPins: ["start", "explorer", "edge"],
  desktopSystemIcons: ["thisPC", "recycle"],
  fullscreen: false,
  cursorVisible: false,
  drag: null, // 拖放中：{paths,label,icon,x,y,over,copy}
  startPins: null, // 開始功能表釘選的 app id 陣列（null＝全部）
  recent: [], // 最近開啟的檔案 [{path,when}]
  snapPreview: null,
  volume: 60,
  fsButton: false,
  hideSig: false, // 網址 ?nosig=1 可隱藏右下角署名（外層網頁已有署名時）
  sites: {}, // 瀏覽器的模擬網站 {url: {title, html}}
  cursor: { x: 640, y: 360, visible: false, pressed: false, mode: "arrow", ms: 0 }, // 示範游標
  caption: null, // 錄影用字卡 {text, sub}
  rev: 0,
});

export const useSys = (selector) => useStoreOf(sys, selector);
