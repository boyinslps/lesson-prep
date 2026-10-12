import React, { useEffect, useRef, useState, useMemo } from "react";
import { sys, useSys } from "../kernel/store";
import * as vfs from "../kernel/vfs";
import { desktopDir, VIRTUAL } from "../kernel/paths";
import { openApp, openPath, TASKBAR_H } from "../kernel/wm";
import { getApp } from "../kernel/apps";
import { showContextMenu } from "../kernel/ui";
import { emit } from "../kernel/events";
import { startDrag } from "../kernel/dnd";
import * as ops from "../kernel/fileops";
import { Ico, FileIco, asset } from "./icons";
import { useVfs } from "./hooks";

const CELL_W = 80, CELL_H = 92, PAD = 4;

function sysIconInfo(id, binFull) {
  if (id === "thisPC") return { label: "本機", icon: "thisPC", open: () => openApp("explorer", { path: VIRTUAL.THISPC }) };
  if (id === "recycle") return { label: "資源回收筒", icon: binFull ? "recycle-full" : "recycle", open: () => openApp("explorer", { path: VIRTUAL.RECYCLE }), drop: "::recycle" };
  if (id === "home") return { label: sys.get().user.name, icon: "folder-user", open: () => openApp("explorer", { path: VIRTUAL.HOME }) };
  const app = getApp(id);
  if (app) return { label: app.name, icon: app.icon, shortcut: true, open: () => openApp(id) };
  return null;
}

export default function Desktop() {
  const rev = useVfs();
  const settings = useSys((s) => s.settings);
  const sysIcons = useSys((s) => s.desktopSystemIcons);
  const selection = useSys((s) => s.desktopSelection);
  const drag = useSys((s) => s.drag);
  const hasWin = useSys((s) => s.focusedId);
  const hasDlg = useSys((s) => s.dialogs.length > 0);
  const user = useSys((s) => s.user.name);
  const [renaming, setRenaming] = useState(null);
  const [band, setBand] = useState(null);
  const ref = useRef(null);
  const slow = useRef({ key: null, timer: null });
  const rows = Math.max(1, Math.floor((window.innerHeight - TASKBAR_H - PAD * 2) / CELL_H));

  const dd = desktopDir();
  const files = settings.desktopIcons ? vfs.list(dd, { hidden: settings.showHidden }).slice().sort((a, b) => (a.type === b.type ? a.name.localeCompare(b.name, "zh-TW") : a.type === "dir" ? -1 : 1)) : [];
  const binFull = vfs.binCount() > 0;
  const items = useMemo(() => {
    if (!settings.desktopIcons) return [];
    const list = [];
    sysIcons.forEach((id) => { const info = sysIconInfo(id, binFull); if (info) list.push({ key: "sys:" + id, sys: id, ...info }); });
    files.forEach((n) => list.push({ key: vfs.join(dd, n.name), path: vfs.join(dd, n.name), label: n.name, file: n }));
    return list;
    // eslint-disable-next-line
  }, [rev, sysIcons, binFull, settings.desktopIcons, settings.showHidden, user]);

  const setSel = (arr) => sys.set({ desktopSelection: arr });
  const pos = (i) => ({ left: PAD + Math.floor(i / rows) * CELL_W, top: PAD + (i % rows) * CELL_H });
  const selFiles = () => selection.filter((k) => !k.startsWith("sys:"));

  const display = (it) => {
    if (it.sys) return it.label;
    return vfs.displayName(it.label, it.file.type, settings.showExtensions);
  };

  const open = (it) => {
    if (it.sys) { emit("desktop:open", { id: it.sys }); it.open(); }
    else openPath(it.path);
  };

  // 鍵盤：沒有視窗取得焦點時才處理
  useEffect(() => {
    const h = (e) => {
      if (sys.get().phase !== "desktop" || sys.get().focusedId || sys.get().dialogs.length || renaming) return;
      if (e.target.closest && e.target.closest("input,textarea,[contenteditable]")) return;
      const fs = selection.filter((k) => !k.startsWith("sys:"));
      if (e.key === "F2" && selection.length === 1) { setRenaming(selection[0]); e.preventDefault(); }
      else if (e.key === "Delete" && fs.length) { ops.deleteItems(fs, { permanent: e.shiftKey }); }
      else if (e.ctrlKey && e.key.toLowerCase() === "c" && fs.length) ops.setClipboardFiles(fs, "copy");
      else if (e.ctrlKey && e.key.toLowerCase() === "x" && fs.length) ops.setClipboardFiles(fs, "cut");
      else if (e.ctrlKey && e.key.toLowerCase() === "v") ops.paste(dd);
      else if (e.ctrlKey && e.key.toLowerCase() === "a") setSel(items.map((i) => i.key));
      else if (e.ctrlKey && e.key.toLowerCase() === "z") vfs.undo();
      else if (e.key === "Enter" && selection.length) items.filter((i) => selection.includes(i.key)).forEach(open);
      else if (e.key === "F5") emit("desktop:refresh", {});
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
    // eslint-disable-next-line
  }, [selection, items, renaming]);

  const itemMenu = (e, it) => {
    e.preventDefault(); e.stopPropagation();
    let selKeys = selection.includes(it.key) ? selection : [it.key];
    if (!selection.includes(it.key)) setSel([it.key]);
    const fs = selKeys.filter((k) => !k.startsWith("sys:"));
    const single = selKeys.length === 1;
    const menu = [];
    if (it.sys === "recycle") {
      menu.push({ label: "開啟", onClick: () => open(it) }, { label: "清空資源回收筒", disabled: !binFull, onClick: () => ops.emptyRecycleBin() });
    } else if (fs.length) {
      menu.push({ iconRow: [
        { icon: "file", label: "剪下", onClick: () => ops.setClipboardFiles(fs, "cut") },
        { icon: "file", label: "複製", onClick: () => ops.setClipboardFiles(fs, "copy") },
        { icon: "file", label: "重新命名", disabled: !single, onClick: () => setRenaming(selKeys[0]) },
        { icon: "file", label: "刪除", onClick: () => ops.deleteItems(fs) },
      ] });
      menu.push({ label: "開啟", onClick: () => items.filter((i) => selKeys.includes(i.key)).forEach(open) });
      menu.push({ separator: true }, { label: "剪下", shortcut: "Ctrl+X", onClick: () => ops.setClipboardFiles(fs, "cut") }, { label: "複製", shortcut: "Ctrl+C", onClick: () => ops.setClipboardFiles(fs, "copy") }, { label: "重新命名", shortcut: "F2", disabled: !single, onClick: () => setRenaming(selKeys[0]) }, { label: "刪除", shortcut: "Del", onClick: () => ops.deleteItems(fs) }, { separator: true }, { label: "內容", shortcut: "Alt+Enter", onClick: () => ops.showProperties(fs) });
    } else {
      menu.push({ label: "開啟", onClick: () => open(it) });
    }
    showContextMenu(e.clientX, e.clientY, menu);
  };

  const bgMenu = (e) => {
    e.preventDefault();
    if (e.target.closest(".dicon")) return;
    const c = ops.clipboardFiles();
    showContextMenu(e.clientX, e.clientY, [
      { label: "檢視", items: [{ label: "大圖示" }, { label: "中圖示", checked: true }, { label: "小圖示" }, { separator: true }, { label: "顯示桌面圖示", checked: settings.desktopIcons, onClick: () => sys.set({ settings: { ...settings, desktopIcons: !settings.desktopIcons } }) }] },
      { label: "排序方式", items: [{ label: "名稱" }, { label: "大小" }, { label: "項目類型" }, { label: "修改日期" }] },
      { label: "重新整理", onClick: () => emit("desktop:refresh", {}) },
      { separator: true },
      { label: "貼上", shortcut: "Ctrl+V", disabled: !c, onClick: () => ops.paste(dd) },
      { label: "復原", shortcut: "Ctrl+Z", disabled: !vfs.canUndo(), onClick: () => vfs.undo() },
      { separator: true },
      { label: "新增", items: ops.newMenuKinds().map((k) => ({ label: k.label, icon: k.icon, onClick: () => { const p = ops.createNew(dd, k); setSel([p]); setRenaming(p); } })) },
      { separator: true },
      { label: "顯示設定", icon: "settings" },
      { label: "個人化", icon: "settings" },
    ]);
  };

  const bgDown = (e) => {
    if (e.button !== 0 || e.target.closest(".dicon")) return;
    sys.set({ startOpen: false, searchOpen: false, quickOpen: false, calendarOpen: false, userMenuOpen: false, focusedId: null });
    const r = ref.current.getBoundingClientRect();
    const sx = e.clientX - r.left, sy = e.clientY - r.top;
    const base = e.ctrlKey ? selection : [];
    if (!e.ctrlKey) setSel([]);
    const mv = (ev) => {
      const x = ev.clientX - r.left, y = ev.clientY - r.top;
      const b = { x: Math.min(sx, x), y: Math.min(sy, y), w: Math.abs(x - sx), h: Math.abs(y - sy) };
      if (b.w < 4 && b.h < 4) return;
      setBand(b);
      const hit = items.filter((it, i) => { const p = pos(i); return p.left < b.x + b.w && p.left + CELL_W > b.x && p.top < b.y + b.h && p.top + CELL_H > b.y; }).map((i) => i.key);
      setSel([...new Set([...base, ...hit])]);
    };
    const up = () => { setBand(null); window.removeEventListener("pointermove", mv, true); window.removeEventListener("pointerup", up, true); };
    window.addEventListener("pointermove", mv, true);
    window.addEventListener("pointerup", up, true);
  };

  const itemDown = (e, it) => {
    if (e.button !== 0) return;
    e.stopPropagation();
    sys.set({ startOpen: false, searchOpen: false, quickOpen: false, calendarOpen: false, userMenuOpen: false, focusedId: null, contextMenu: null });
    let keys;
    if (e.ctrlKey) keys = selection.includes(it.key) ? selection.filter((k) => k !== it.key) : [...selection, it.key];
    else if (e.shiftKey && selection.length) { const a = items.findIndex((i) => i.key === selection[selection.length - 1]), b = items.findIndex((i) => i.key === it.key); keys = items.slice(Math.min(a, b), Math.max(a, b) + 1).map((i) => i.key); }
    else keys = selection.includes(it.key) && selection.length > 1 ? selection : [it.key];
    const wasSelected = selection.length === 1 && selection[0] === it.key && !e.ctrlKey && !e.shiftKey;
    setSel(keys);
    slow.current.key = wasSelected && !it.sys ? it.key : null;
    const fs = keys.filter((k) => !k.startsWith("sys:"));
    if (fs.length) startDrag(e, fs, { label: fs.length > 1 ? `${fs.length}` : it.label, icon: it.file ? it.file.type : "file" });
    else if (it.sys === "recycle") { /* 資源回收筒本身不可拖 */ }
  };

  const commitRename = async (it, val) => {
    setRenaming(null);
    if (it.sys) return;
    const np = await ops.renameItem(it.path, val);
    if (np) setSel([np]);
  };

  const cutSet = new Set((ops.cutPaths() || []).map((p) => p.toLowerCase()));

  return (
    <div ref={ref} className="desktop" onPointerDown={bgDown} onContextMenu={bgMenu} data-sim-id="desktop" data-drop-path="::desktop">
      <div className="wallpaper" style={settings.wallpaper.startsWith("#") || settings.wallpaper.startsWith("linear") ? { background: settings.wallpaper } : { backgroundImage: `url(${asset(settings.wallpaper)})` }} />
      {items.map((it, i) => {
        const sel = selection.includes(it.key);
        const isRen = renaming === it.key;
        const dropTarget = it.sys === "recycle" ? "::recycle" : it.file?.type === "dir" ? it.path : undefined;
        const over = drag && dropTarget && drag.over === dropTarget;
        return (
          <div
            key={it.key}
            className={"dicon" + (sel ? " sel" : "") + (over ? " dropover" : "") + (cutSet.has((it.path || "").toLowerCase()) ? " cut" : "")}
            style={{ ...pos(i), width: CELL_W, height: CELL_H }}
            data-sim-id={"desktop:icon:" + (it.sys ? it.label : it.label)}
            data-drop-path={dropTarget}
            onPointerDown={(e) => itemDown(e, it)}
            onPointerUp={(e) => { if (e.button === 0 && slow.current.key === it.key && !sys.get().drag && !isRen) { slow.current.key = null; clearTimeout(slow.current.timer); slow.current.timer = setTimeout(() => setRenaming(it.key), 700); } }}
            onDoubleClick={() => { clearTimeout(slow.current.timer); open(it); }}
            onContextMenu={(e) => itemMenu(e, it)}
          >
            <div className="dicon-img">
              {it.sys ? <Ico name={it.icon} size={40} /> : <FileIco name={it.label} type={it.file.type} size={40} thumb={it.file.src && /\.(png|jpe?g|gif|svg|webp)$/i.test(it.label) ? asset(it.file.src) : null} />}
              {it.shortcut && <span className="shortcut-arrow">↗</span>}
            </div>
            {isRen ? (
              <RenameBox it={it} initial={display(it)} onDone={(v) => commitRename(it, v)} />
            ) : (
              <div className="dicon-label" title={it.label}>{display(it)}</div>
            )}
          </div>
        );
      })}
      {band && <div className="band" style={{ left: band.x, top: band.y, width: band.w, height: band.h }} />}
    </div>
  );
}

export function RenameBox({ initial, onDone, multiline = true, className = "rename" }) {
  const ref = useRef(null);
  const [v, setV] = useState(initial);
  const done = useRef(false);
  useEffect(() => {
    const el = ref.current;
    el.focus();
    const dot = initial.lastIndexOf(".");
    el.setSelectionRange(0, dot > 0 ? dot : initial.length);
  }, []);
  const finish = (val) => { if (done.current) return; done.current = true; onDone(val); };
  return (
    <textarea
      ref={ref}
      className={className}
      data-sim-id="rename:input"
      rows={multiline ? 2 : 1}
      value={v}
      onChange={(e) => setV(e.target.value)}
      onPointerDown={(e) => e.stopPropagation()}
      onDoubleClick={(e) => e.stopPropagation()}
      onKeyDown={(e) => {
        e.stopPropagation();
        if (e.key === "Enter") { e.preventDefault(); finish(v); }
        else if (e.key === "Escape") { e.preventDefault(); finish(initial); }
      }}
      onBlur={() => finish(v)}
    />
  );
}
