// 通用「開啟舊檔／另存新檔」對話框。Notepad、未來的 Word／PPT 都用它。
// 用法：const path = await fileDialog({ ownerId, mode:"save", defaultName:"未命名.txt", filters:[{label:"文字文件 (*.txt)", exts:["txt"]},{label:"所有檔案", exts:["*"]}], startDir })
import React, { useState } from "react";
import * as vfs from "../kernel/vfs";
import { openDialog, messageBox, errorBox } from "../kernel/ui";
import { known, home } from "../kernel/paths";
import { FileIco, Ico } from "./icons";
import { sys } from "../kernel/store";

const QUICK = [["desktop", "桌面", "folder-desktop"], ["downloads", "下載", "folder-downloads"], ["documents", "文件", "folder-documents"], ["pictures", "圖片", "folder-pictures"], ["music", "音樂", "folder-music"], ["videos", "影片", "folder-videos"]];

function Body({ mode, close, ownerId, startDir, defaultName, filters, defaultExt }) {
  const [dir, setDir] = useState(startDir);
  const [name, setName] = useState(defaultName || "");
  const [filterIdx, setFilterIdx] = useState(0);
  const [sel, setSel] = useState(null);
  vfs.getRev();
  const f = filters[filterIdx];
  const showExt = sys.get().settings.showExtensions;
  const items = vfs.list(dir, { hidden: sys.get().settings.showHidden }).filter((n) => n.type === "dir" || f.exts.includes("*") || f.exts.includes(vfs.extOf(n.name)));
  items.sort((a, b) => (a.type === b.type ? a.name.localeCompare(b.name, "zh-TW") : a.type === "dir" ? -1 : 1));
  const crumbs = [];
  const q = vfs.parse(dir);
  let acc = q.drive + ":\\";
  crumbs.push([acc, "本機磁碟 (" + q.drive + ":)"]);
  q.parts.forEach((p) => { acc = vfs.join(acc, p); crumbs.push([acc, p]); });

  const submit = async () => {
    let n = name.trim();
    if (!n) return;
    if (n.includes("\\") || /^[A-Za-z]:/.test(n)) {
      const full = vfs.norm(n);
      if (vfs.isDir(full)) { setDir(full); setName(""); return; }
      n = vfs.basename(full);
      return finish(vfs.dirname(full) || dir, n);
    }
    return finish(dir, n);
  };
  const finish = async (d, n) => {
    const v = vfs.validateName(n);
    if (!v.ok) { await errorBox("檔案名稱不可包含下列任何字元:\n\\ / : * ? \" < > |", { ownerId, title: mode === "save" ? "另存新檔" : "開啟舊檔" }); return; }
    n = v.name;
    if (mode === "save" && !vfs.extOf(n) && defaultExt && f.exts[0] !== "*") n += "." + (f.exts.includes(defaultExt) ? defaultExt : f.exts[0]);
    else if (mode === "save" && !vfs.extOf(n) && defaultExt) n += "." + defaultExt;
    const p = vfs.join(d, n);
    if (vfs.isDir(p)) { setDir(p); setName(""); return; }
    if (mode === "open" && !vfs.exists(p)) { await messageBox({ ownerId, title: "開啟舊檔", icon: "warn", text: `找不到 ${n}。\n請確認檔名是否正確。` }); return; }
    if (mode === "save" && vfs.exists(p)) {
      const r = await messageBox({ ownerId, title: "確認另存新檔", icon: "warn", text: `${n} 已經存在。\n要取代它嗎?`, buttons: ["是", "否"], primary: 1, kind: "confirm-overwrite" });
      if (r !== 0) return;
    }
    close(p);
  };

  return (
    <div className="fdlg">
      <div className="fdlg-bar">
        <button className="fdlg-btn" title="上一層" data-sim-id="fdlg:up" onClick={() => vfs.dirname(dir) && setDir(vfs.dirname(dir))}>↑</button>
        <div className="fdlg-path" data-sim-id="fdlg:path">{crumbs.map(([p, t], i) => <span key={p}>{i > 0 && <i> › </i>}<a onClick={() => setDir(p)}>{t}</a></span>)}</div>
      </div>
      <div className="fdlg-main">
        <div className="fdlg-nav">
          {QUICK.map(([k, t, ic]) => <div key={k} className="fdlg-navitem" data-sim-id={"fdlg:nav:" + t} onClick={() => setDir(known(k))}><Ico name={ic} size={16} />{t}</div>)}
          <div className="fdlg-navitem" data-sim-id="fdlg:nav:本機磁碟 (C:)" onClick={() => setDir("C:\\")}><Ico name="drive" size={16} />本機磁碟 (C:)</div>
        </div>
        <div className="fdlg-list" data-sim-id="fdlg:list">
          {items.length === 0 && <div className="fdlg-empty">沒有符合搜尋條件的項目。</div>}
          {items.map((n) => (
            <div key={n.id} className={"fdlg-item" + (sel === n.id ? " sel" : "")} data-sim-id={"fdlg:item:" + n.name}
              onClick={() => { setSel(n.id); if (n.type === "file") setName(n.name); }}
              onDoubleClick={() => (n.type === "dir" ? (setDir(vfs.join(dir, n.name)), setSel(null)) : finish(dir, n.name))}>
              <FileIco name={n.name} type={n.type} size={16} />
              <span className="fdlg-name">{vfs.displayName(n.name, n.type, showExt)}</span>
              <span className="fdlg-kind">{vfs.kindOf(n.name, n.type)}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="fdlg-foot">
        <label>檔案名稱(N):</label>
        <input className="fdlg-input" data-sim-id="fdlg:filename" value={name} autoFocus onChange={(e) => setName(e.target.value)} onKeyDown={(e) => e.key === "Enter" && submit()} />
        <select className="fdlg-select" data-sim-id="fdlg:type" value={filterIdx} onChange={(e) => setFilterIdx(+e.target.value)}>{filters.map((x, i) => <option key={i} value={i}>{x.label}</option>)}</select>
        <button className="btn primary" data-sim-id={"dialog:btn:" + (mode === "save" ? "儲存" : "開啟")} onClick={submit}>{mode === "save" ? "儲存(S)" : "開啟(O)"}</button>
        <button className="btn" data-sim-id="dialog:btn:取消" onClick={() => close(null)}>取消</button>
      </div>
    </div>
  );
}

export async function fileDialog({ ownerId = null, mode = "save", startDir, defaultName = "", filters = [{ label: "所有檔案 (*.*)", exts: ["*"] }], defaultExt = "" } = {}) {
  const r = await openDialog({
    ownerId, kind: mode === "save" ? "save-as" : "open-file", title: mode === "save" ? "另存新檔" : "開啟舊檔", width: 640,
    render: (close) => <Body mode={mode} close={close} ownerId={ownerId} startDir={startDir || known("documents")} defaultName={defaultName} filters={filters} defaultExt={defaultExt} />,
  });
  return r || null;
}
export { home };
