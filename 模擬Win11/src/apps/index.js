// 在這裡註冊所有 App。新增 App：寫一個元件，然後 registerApp({...})（欄位說明在 kernel/apps.js）。
import { registerApp } from "../kernel/apps";
import Explorer from "./Explorer";
import Notepad from "./Notepad";
import Browser from "./Browser";
import Photos from "./Photos";
import Placeholder from "./Placeholder";

registerApp({ id: "explorer", name: "檔案總管", icon: "img:images/apps/explorer.png", component: Explorer, defaultSize: { w: 900, h: 560 }, minSize: { w: 520, h: 320 } });

registerApp({
  id: "notepad", name: "記事本", icon: "notepad", component: Notepad, defaultSize: { w: 720, h: 480 }, minSize: { w: 360, h: 220 },
  fileTypes: ["txt", "log", "md", "csv", "ini"],
  newFile: { ext: "txt", label: "新增文字文件", content: "" },
});

registerApp({ id: "edge", name: "Microsoft Edge", icon: "img:images/apps/edge.png", component: Browser, defaultSize: { w: 1040, h: 620 }, minSize: { w: 520, h: 320 }, fileTypes: ["html", "htm"] });
registerApp({ id: "photos", name: "相片", icon: "photos", component: Photos, defaultSize: { w: 860, h: 560 }, fileTypes: ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"] });

// ---- 尚未開發（hidden＝不顯示在開始功能表；已先註冊副檔名關聯，之後換成真元件即可）----
registerApp({ id: "word", name: "Word", icon: "word", component: Placeholder, hidden: true, fileTypes: ["docx", "doc"], defaultSize: { w: 1000, h: 640 } });
registerApp({ id: "excel", name: "Excel", icon: "excel", component: Placeholder, hidden: true, fileTypes: ["xlsx", "xls"], defaultSize: { w: 1000, h: 640 } });
registerApp({ id: "powerpoint", name: "PowerPoint", icon: "powerpoint", component: Placeholder, hidden: true, fileTypes: ["pptx", "ppt"], defaultSize: { w: 1000, h: 640 } });
