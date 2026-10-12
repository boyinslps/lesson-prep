// 應用程式註冊表：要新增 Word / PPT / Google 搜尋這類 app，只要呼叫 registerApp()。
// 範例見 src/apps/index.js 與 AI說明.md「如何新增一個 App」。
//
// def = {
//   id: "notepad",            // 唯一代號（scene、API、工作列釘選都用它）
//   name: "記事本",            // 顯示名稱
//   icon: "notepad",           // Ico 名稱，或 "img:images/apps/edge.png"
//   component: Notepad,        // React 元件，用 useWin() 取得視窗資訊
//   defaultSize: {w, h},       // 預設視窗大小
//   minSize: {w, h},
//   singleton: false,          // true＝只開一個視窗
//   fileTypes: ["txt"],        // 雙擊這些副檔名時由這個 app 開啟
//   title: (args) => "…",      // 視窗標題（可選）
//   startMenu: true,           // 出現在開始功能表釘選區
//   newFile: {ext, label, content}  // 讓「新增」選單可建立這種檔案（可選）
//   hidden: false,             // true＝尚未開放（開始功能表不顯示）
// }
const registry = new Map();
const fileTypeMap = new Map(); // ext -> appId

export function registerApp(def) {
  registry.set(def.id, { defaultSize: { w: 800, h: 520 }, minSize: { w: 360, h: 240 }, startMenu: true, ...def });
  (def.fileTypes || []).forEach((e) => fileTypeMap.set(e.toLowerCase(), def.id));
  return def;
}
export const getApp = (id) => registry.get(id);
export const allApps = () => Array.from(registry.values());
export const appForExt = (ext) => fileTypeMap.get((ext || "").toLowerCase()) || null;
