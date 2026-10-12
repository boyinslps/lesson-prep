import { sys } from "./store";
import { join } from "./vfs";

// 使用者資料夾（名稱比照繁體中文 Windows 11）
export const FOLDER_NAMES = { desktop: "桌面", downloads: "下載", documents: "文件", pictures: "圖片", music: "音樂", videos: "影片" };
export const home = () => `C:\\Users\\${sys.get().user.name}`;
export const known = (k) => join(home(), FOLDER_NAMES[k]);
export const desktopDir = () => known("desktop");

// 「此電腦」「桌面」這類虛擬位置的代號（Explorer 的 path 可以是真實路徑或這些代號）
export const VIRTUAL = { THISPC: "::thispc", RECYCLE: "::recycle", HOME: "::home" };
export const isVirtual = (p) => typeof p === "string" && p.startsWith("::");
