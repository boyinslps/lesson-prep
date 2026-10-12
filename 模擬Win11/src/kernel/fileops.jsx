// 檔案操作（含對話框）：複製／剪下／貼上／刪除／重新命名／新增／還原。桌面與檔案總管共用。
import React from "react";
import { sys } from "./store";
import { emit } from "./events";
import * as vfs from "./vfs";
import { messageBox, openDialog, errorBox } from "./ui";
import { setDropHandler } from "./dnd";
import { desktopDir } from "./paths";
import { allApps } from "./apps";
import { simNow } from "./clock";
import { Ico } from "../shell/icons";

export function setClipboardFiles(paths, mode) {
  sys.set({ clipboard: { ...sys.get().clipboard, files: { paths: paths.map(vfs.norm), mode } } });
  emit("clipboard:set", { paths, mode });
}
export const clipboardFiles = () => sys.get().clipboard.files;
export const cutPaths = () => (sys.get().clipboard.files?.mode === "cut" ? sys.get().clipboard.files.paths : []);

async function askConflict(ownerId, names, verb) {
  const one = names.length === 1;
  const v = await openDialog({
    ownerId, title: verb === "move" ? "移動檔案" : "複製檔案", width: 520, kind: "conflict", data: { names },
    render: (close) => (
      <div className="conflict">
        <div className="conflict-title">{verb === "move" ? "移動" : "複製"} {one ? "1 個項目" : `${names.length} 個項目`}</div>
        <div className="conflict-sub">目的地已經包含{one ? ` 名為「${names[0]}」的` : ` ${names.length} 個同名的`}檔案</div>
        <button className="conflict-opt" data-sim-id="dialog:btn:取代目的地中的檔案" onClick={() => close("replace")}><b>✓ 取代目的地中的檔案</b></button>
        <button className="conflict-opt" data-sim-id="dialog:btn:略過這個檔案" onClick={() => close("skip")}><b>↷ 略過這個檔案</b></button>
        <button className="conflict-opt" data-sim-id="dialog:btn:兩個檔案都保留" onClick={() => close("keep-both")}><b>⧉ 兩個檔案都保留</b><span>會在檔名後面加上編號</span></button>
        <div className="msgbox-btns"><button className="btn" data-sim-id="dialog:btn:取消" onClick={() => close("cancel")}>取消</button></div>
      </div>
    ),
  });
  return v === undefined ? "cancel" : v;
}

function fail(ownerId, e) {
  if (e instanceof vfs.VfsError) {
    const map = {
      "into-self": "無法將資料夾複製或移動到它自己的子資料夾。",
      "not-found": "找不到指定的位置或項目。",
      exists: "已有同名的項目存在。",
    };
    return errorBox(map[e.code] || e.message, { ownerId, title: "發生錯誤" });
  }
  throw e;
}

// 複製或移動 paths 到 destDir
export async function transfer(paths, destDir, mode, ownerId = null) {
  if (!paths.length || !vfs.isDir(destDir)) return [];
  let policy = "keep-both";
  const clash = vfs.conflicts(paths, destDir).filter((n) => !(mode === "move" && paths.some((p) => vfs.basename(p) === n && vfs.norm(vfs.dirname(p)).toLowerCase() === vfs.norm(destDir).toLowerCase())));
  if (clash.length && mode === "move") {
    const r = await askConflict(ownerId, clash, "move");
    if (r === "cancel") return [];
    policy = r;
  } else if (clash.length && mode === "copy") {
    // 複製到「別的」資料夾時會問；複製到「同一個」資料夾會自動加「 - 複製」
    const notSelfFolder = clash.filter((n) => !paths.some((p) => vfs.basename(p) === n && vfs.norm(vfs.dirname(p)).toLowerCase() === vfs.norm(destDir).toLowerCase()));
    if (notSelfFolder.length) {
      const r = await askConflict(ownerId, notSelfFolder, "copy");
      if (r === "cancel") return [];
      policy = r;
    }
  }
  try {
    return mode === "move" ? vfs.move(paths, destDir, { policy }) : vfs.copy(paths, destDir, { policy });
  } catch (e) { fail(ownerId, e); return []; }
}

export async function paste(destDir, ownerId = null) {
  const c = clipboardFiles();
  if (!c || !vfs.isDir(destDir)) return [];
  const live = c.paths.filter(vfs.exists);
  const out = await transfer(live, destDir, c.mode === "cut" ? "move" : "copy", ownerId);
  if (c.mode === "cut") sys.set({ clipboard: { ...sys.get().clipboard, files: null } });
  emit("clipboard:paste", { to: vfs.norm(destDir), count: out.length, mode: c.mode });
  return out;
}

export async function deleteItems(paths, { permanent = false, ownerId = null } = {}) {
  paths = paths.filter(vfs.exists);
  if (!paths.length) return;
  if (permanent) {
    const one = paths.length === 1;
    const kind = one ? (vfs.isDir(paths[0]) ? "此資料夾" : "這個檔案") : `這 ${paths.length} 個項目`;
    const r = await messageBox({ ownerId, title: one ? "刪除檔案" : "刪除多個項目", icon: "warn", text: `確定要永久刪除${kind}嗎?`, buttons: ["是", "否"], primary: 0, kind: "confirm-delete" });
    if (r !== 0) return;
    vfs.deleteForever(paths);
  } else {
    vfs.trash(paths);
  }
}

export async function emptyRecycleBin(ownerId = null) {
  const n = vfs.binCount();
  if (!n) return;
  const r = await messageBox({ ownerId, title: "刪除多個項目", icon: "warn", text: `確定要永久刪除這 ${n} 個項目嗎?`, buttons: ["是", "否"], kind: "confirm-delete" });
  if (r === 0) vfs.emptyBin();
}

// 重新命名；回傳新路徑或 null。showExt=true 且副檔名被改時會跳確認。
export async function renameItem(path, newName, { ownerId = null, visibleName = null } = {}) {
  const n = vfs.stat(path);
  if (!n) return null;
  const typed = newName;
  let full = typed;
  const hideExt = !sys.get().settings.showExtensions && n.type === "file" && n.ext && vfs.isKnownExt(n.ext);
  if (hideExt) full = typed.replace(/[ .]+$/, "") ? typed.replace(/[ .]+$/, "") + n.name.slice(vfs.baseOf(n.name).length) : ""; // 副檔名隱藏時，改名只改主檔名
  const v = vfs.validateName(full);
  if (!v.ok) {
    if (v.code === "invalid") await errorBox("檔案名稱不可包含下列任何字元:\n\\ / : * ? \" < > |", { ownerId, title: "重新命名" });
    return null; // 空白＝取消
  }
  if (v.name === n.name) return vfs.norm(path);
  if (n.type === "file" && vfs.extOf(v.name) !== n.ext) {
    const r = await messageBox({ ownerId, title: "重新命名", icon: "warn", text: "如果變更副檔名，檔案可能會無法使用。\n確定要變更嗎?", buttons: ["是", "否"], primary: 1, kind: "confirm-ext" });
    if (r !== 0) return null;
  }
  try {
    return vfs.rename(path, v.name);
  } catch (e) {
    if (e instanceof vfs.VfsError && e.code === "exists") {
      await messageBox({ ownerId, title: "重新命名", icon: "warn", text: "已有名為「" + v.name + "」的檔案或資料夾存在。請指定其他名稱。", kind: "rename-exists" });
      return null;
    }
    fail(ownerId, e);
    return null;
  }
}

// 「新增」選單的項目：資料夾＋各 app 註冊的 newFile
export function newMenuKinds() {
  const kinds = [{ id: "folder", label: "資料夾", icon: "folder" }];
  allApps().forEach((a) => { if (a.newFile) kinds.push({ id: a.id, label: a.newFile.label, icon: a.icon, ext: a.newFile.ext, content: a.newFile.content || "" }); });
  return kinds;
}
export function createNew(dir, kind) {
  if (kind === "folder" || kind.id === "folder") return vfs.create(dir, "新增資料夾", "dir");
  const k = typeof kind === "string" ? newMenuKinds().find((x) => x.id === kind) : kind;
  if (!k) return null;
  return vfs.create(dir, `${k.label}.${k.ext}`.replace(/^新增 /, "新增"), "file", { content: k.content });
}

export function showProperties(paths, ownerId = null) {
  const p = paths[0];
  const st = vfs.stat(p);
  if (!st) return;
  const multi = paths.length > 1;
  const fmt = (t) => new Date(t).toLocaleString("zh-TW", { year: "numeric", month: "long", day: "numeric", hour: "numeric", minute: "2-digit", second: "2-digit" });
  const size = (b) => (b < 1024 ? `${b} 位元組` : b < 1048576 ? `${(b / 1024).toFixed(1)} KB (${b.toLocaleString()} 位元組)` : `${(b / 1048576).toFixed(1)} MB (${b.toLocaleString()} 位元組)`);
  openDialog({
    ownerId, title: `${multi ? "多個項目" : st.name} 內容`, width: 400, kind: "properties",
    render: (close) => (
      <div className="props">
        <div className="props-head"><Ico name={st.type === "dir" ? "folder" : "file"} size={36} /><div className="props-name">{multi ? `${paths.length} 個項目` : st.name}</div></div>
        <table className="props-table"><tbody>
          <tr><td>類型:</td><td>{multi ? "多個類型" : vfs.kindOf(st.name, st.type)}</td></tr>
          <tr><td>位置:</td><td>{vfs.dirname(p)}</td></tr>
          <tr><td>大小:</td><td>{size(paths.reduce((a, x) => a + (vfs.stat(x)?.size || 0), 0))}</td></tr>
          {!multi && <><tr><td>建立日期:</td><td>{fmt(st.created)}</td></tr><tr><td>修改日期:</td><td>{fmt(st.modified)}</td></tr></>}
        </tbody></table>
        <div className="msgbox-btns"><button className="btn primary" data-sim-id="dialog:btn:確定" onClick={() => close(true)}>確定</button><button className="btn" data-sim-id="dialog:btn:取消" onClick={() => close(false)}>取消</button></div>
      </div>
    ),
  });
}

// 拖放處理：目標可以是資料夾路徑、::recycle、::desktop
export function dropFiles(paths, target, { copy = false, ownerId = null } = {}) {
  if (target === "::recycle") return deleteItems(paths, { ownerId });
  const dest = target === "::desktop" ? desktopDir() : target;
  if (!vfs.isDir(dest)) return;
  // 同磁碟預設移動；按住 Ctrl 為複製
  return transfer(paths, dest, copy ? "copy" : "move", ownerId);
}
setDropHandler(dropFiles);

export const fileTime = (t) => new Date(t).toLocaleString("zh-TW", { year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "2-digit", hour12: true });
export const formatSize = (b) => (b < 1024 ? Math.max(1, Math.ceil(b / 1024)) + " KB" : b < 1048576 ? Math.ceil(b / 1024).toLocaleString() + " KB" : (b / 1048576).toFixed(1) + " MB");
export { simNow };
