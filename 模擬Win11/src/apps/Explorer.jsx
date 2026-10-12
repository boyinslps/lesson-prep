// 檔案總管：比照 Windows 11。路徑可以是真實路徑，或 ::thispc（本機）、::recycle（資源回收筒）、::home。
import React, { useEffect, useMemo, useRef, useState } from "react";
import { FiScissors, FiCopy, FiClipboard, FiTrash2, FiPlus, FiMoreHorizontal, FiArrowLeft, FiArrowRight, FiArrowUp, FiRefreshCw, FiSearch, FiGrid, FiList } from "react-icons/fi";
import { MdDriveFileRenameOutline, MdSort, MdOutlineRestore } from "react-icons/md";
import { sys, useSys } from "../kernel/store";
import * as vfs from "../kernel/vfs";
import { known, home, desktopDir, VIRTUAL, isVirtual } from "../kernel/paths";
import { openApp, openPath } from "../kernel/wm";
import { showContextMenu, messageBox } from "../kernel/ui";
import { startDrag } from "../kernel/dnd";
import * as ops from "../kernel/fileops";
import { emit } from "../kernel/events";
import { Ico, FileIco, asset } from "../shell/icons";
import { useVfs } from "../shell/hooks";
import { useWin } from "../shell/WinContext";
import { useExposeState } from "../kernel/appstate";
import { RenameBox } from "../shell/Desktop";

const IMG = /\.(png|jpe?g|gif|svg|webp|bmp)$/i;
const SPECIAL_ICON = { desktop: "folder-desktop", downloads: "folder-downloads", documents: "folder-documents", pictures: "folder-pictures", music: "folder-music", videos: "folder-videos" };
const QUICK = [["desktop", "桌面"], ["downloads", "下載"], ["documents", "文件"], ["pictures", "圖片"], ["music", "音樂"], ["videos", "影片"]];

function iconForPath(p, node) {
  const q = vfs.parse(p);
  if (q && q.parts.length === 0) return "drive";
  if (q && q.parts.length === 3 && q.parts[0].toLowerCase() === "users" && q.parts[1] === sys.get().user.name) {
    const k = QUICK.find(([, n]) => n === q.parts[2]);
    if (k) return SPECIAL_ICON[k[0]];
  }
  if (q && q.parts.length === 2 && q.parts[0].toLowerCase() === "users" && q.parts[1] === sys.get().user.name) return "folder-user";
  return node?.type === "file" ? null : "folder";
}

function locName(p) {
  if (p === VIRTUAL.THISPC) return "本機";
  if (p === VIRTUAL.RECYCLE) return "資源回收筒";
  const q = vfs.parse(p);
  if (!q) return p;
  if (!q.parts.length) return `本機磁碟 (${q.drive}:)`;
  return q.parts[q.parts.length - 1];
}

function Crumbs({ path, go, winId }) {
  const segs = [];
  if (path === VIRTUAL.THISPC) segs.push([VIRTUAL.THISPC, "本機"]);
  else if (path === VIRTUAL.RECYCLE) { segs.push([VIRTUAL.THISPC, "桌面"], [VIRTUAL.RECYCLE, "資源回收筒"]); }
  else {
    segs.push([VIRTUAL.THISPC, "本機"]);
    const q = vfs.parse(path);
    let acc = q.drive + ":\\";
    segs.push([acc, `本機磁碟 (${q.drive}:)`]);
    q.parts.forEach((p) => { acc = vfs.join(acc, p); segs.push([acc, p]); });
  }
  return segs.map(([p, t], i) => (
    <span key={i} className="crumb-wrap">
      {i > 0 && <span className="crumb-sep">›</span>}
      <span className="crumb" data-sim-id={`explorer:${winId}:crumb:${t}`} data-drop-path={isVirtual(p) ? undefined : p} onClick={(e) => { e.stopPropagation(); go(p); }}>{t}</span>
    </span>
  ));
}

function TreeNode({ path, label, icon, depth, cur, go, expanded, toggle, winId }) {
  useVfs();
  const kids = vfs.isDir(path) ? vfs.list(path, { hidden: false }).filter((n) => n.type === "dir") : [];
  const open = expanded.has(path);
  return (
    <>
      <div className={"tree-row" + (cur === path ? " sel" : "")} style={{ paddingLeft: 6 + depth * 14 }} data-sim-id={`explorer:${winId}:nav:${label}`} data-drop-path={path} onClick={() => go(path)}>
        <span className={"tree-arrow" + (kids.length ? "" : " none")} onClick={(e) => { e.stopPropagation(); toggle(path); }}>{open ? "⌄" : "›"}</span>
        <Ico name={icon} size={16} /><span className="tree-label">{label}</span>
      </div>
      {open && kids.map((k) => {
        const kp = vfs.join(path, k.name);
        return <TreeNode key={kp} path={kp} label={k.name} icon={iconForPath(kp, k) || "folder"} depth={depth + 1} cur={cur} go={go} expanded={expanded} toggle={toggle} winId={winId} />;
      })}
    </>
  );
}

export default function Explorer() {
  const w = useWin();
  const rev = useVfs();
  const settings = useSys((s) => s.settings);
  const drag = useSys((s) => s.drag);
  const clip = useSys((s) => s.clipboard.files);
  const user = useSys((s) => s.user.name);
  const start = w.args.path ? (w.args.path === VIRTUAL.HOME ? home() : w.args.path) : known("documents");
  const [hist, setHist] = useState({ stack: [start], i: 0 });
  const path = hist.stack[hist.i];
  const [sel, setSel] = useState([]);
  const [view, setView] = useState("details");
  const [sort, setSort] = useState({ key: "name", dir: 1 });
  const [renaming, setRenaming] = useState(null);
  const [addrEdit, setAddrEdit] = useState(null);
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState(new Set());
  const [band, setBand] = useState(null);
  const root = useRef(null);
  const contentRef = useRef(null);
  const lastIdx = useRef(null);
  const slow = useRef({ key: null, timer: null });
  const id = w.id;
  const sid = (n) => `explorer:${id}:${n}`;

  const isBin = path === VIRTUAL.RECYCLE;
  useExposeState(() => ({ path, selection: sel, view, sort, renaming, query }));
  const isPC = path === VIRTUAL.THISPC;

  // ---- 導覽 ----
  const go = (p, { push = true } = {}) => {
    if (p === VIRTUAL.HOME) p = home();
    if (!isVirtual(p) && !vfs.isDir(p)) {
      messageBox({ ownerId: id, title: "檔案總管", icon: "warn", text: `Windows 找不到「${p}」。請確認名稱是否正確，然後再試一次。` });
      return;
    }
    setSel([]); setRenaming(null); setQuery(""); setAddrEdit(null);
    if (push) setHist((h) => ({ stack: [...h.stack.slice(0, h.i + 1), p], i: h.i + 1 }));
    emit("app:explorer:navigate", { id, path: p });
  };
  const back = () => hist.i > 0 && (setHist({ ...hist, i: hist.i - 1 }), setSel([]), setQuery(""));
  const fwd = () => hist.i < hist.stack.length - 1 && (setHist({ ...hist, i: hist.i + 1 }), setSel([]), setQuery(""));
  const up = () => { if (isVirtual(path)) return; const d = vfs.dirname(path); go(d || VIRTUAL.THISPC); };

  // 路徑不存在了（被刪除）→ 退回上層
  useEffect(() => {
    if (!isVirtual(path) && !vfs.isDir(path)) {
      let d = vfs.dirname(path);
      while (d && !vfs.isDir(d)) d = vfs.dirname(d);
      go(d || VIRTUAL.THISPC);
    }
    // eslint-disable-next-line
  }, [rev]);

  useEffect(() => { w.setTitle(locName(path)); }, [path]); // eslint-disable-line
  useEffect(() => { if (w.args._n) { const p = w.args.path === VIRTUAL.HOME ? home() : w.args.path; if (p) go(p); } }, [w.args._n]); // eslint-disable-line

  // ---- 項目資料 ----
  const showExt = settings.showExtensions;
  const entries = useMemo(() => {
    if (isPC) return [];
    if (isBin) {
      return vfs.binItems().map((b) => ({ key: "bin:" + b.id, binId: b.id, name: b.node.name, type: b.node.type, size: vfs.sizeOf(b.node), modified: b.node.modified, deletedAt: b.deletedAt, orig: vfs.dirname(b.origPath), path: null }));
    }
    let list;
    if (query.trim()) {
      const q = query.trim().toLowerCase(); list = [];
      const walk = (d) => vfs.list(d, { hidden: settings.showHidden }).forEach((n) => { const p = vfs.join(d, n.name); if (n.name.toLowerCase().includes(q)) list.push({ n, p, d }); if (n.type === "dir") walk(p); });
      walk(path);
      return list.map(({ n, p, d }) => ({ key: p, path: p, name: n.name, type: n.type, size: vfs.sizeOf(n), modified: n.modified, src: n.src, orig: d }));
    }
    list = vfs.list(path, { hidden: settings.showHidden });
    return list.map((n) => ({ key: vfs.join(path, n.name), path: vfs.join(path, n.name), name: n.name, type: n.type, size: vfs.sizeOf(n), modified: n.modified, src: n.src, hiddenItem: n.hidden }));
    // eslint-disable-next-line
  }, [path, rev, query, settings.showHidden, isBin, isPC]);

  const sorted = useMemo(() => {
    const k = sort.key, d = sort.dir;
    const arr = entries.slice();
    arr.sort((a, b) => {
      if (a.type !== b.type) return a.type === "dir" ? -1 : 1;
      let r;
      if (k === "name") r = a.name.localeCompare(b.name, "zh-TW", { numeric: true });
      else if (k === "modified") r = a.modified - b.modified;
      else if (k === "size") r = a.size - b.size;
      else if (k === "type") r = vfs.kindOf(a.name, a.type).localeCompare(vfs.kindOf(b.name, b.type));
      else if (k === "deleted") r = a.deletedAt - b.deletedAt;
      else if (k === "orig") r = (a.orig || "").localeCompare(b.orig || "");
      else r = 0;
      return r * d || a.name.localeCompare(b.name, "zh-TW");
    });
    return arr;
  }, [entries, sort]);

  const cut = new Set(ops.cutPaths().map((p) => p.toLowerCase()));
  const selEntries = sorted.filter((e) => sel.includes(e.key));
  const selPaths = selEntries.map((e) => e.path).filter(Boolean);
  const dispName = (e) => vfs.displayName(e.name, e.type, showExt);

  // ---- 動作 ----
  const openEntry = (e) => {
    if (isBin) { messageBox({ ownerId: id, title: "資源回收筒", icon: "warn", text: "無法開啟資源回收筒內的項目。\n請先還原它，才能開啟。" }); return; }
    if (e.type === "dir") go(e.path); else openPath(e.path);
  };
  const doDelete = (permanent) => {
    if (isBin) { if (selEntries.length) ops_binDelete(selEntries); return; }
    ops.deleteItems(selPaths, { permanent, ownerId: id });
    setSel([]);
  };
  const ops_binDelete = async (es) => {
    const n = es.length;
    const r = await messageBox({ ownerId: id, title: n > 1 ? "刪除多個項目" : "刪除檔案", icon: "warn", text: n > 1 ? `確定要永久刪除這 ${n} 個項目嗎?` : "確定要永久刪除這個檔案嗎?", buttons: ["是", "否"], kind: "confirm-delete" });
    if (r === 0) { vfs.deleteFromBin(es.map((e) => e.binId)); setSel([]); }
  };
  const doRestore = (all) => { const es = all ? sorted : selEntries; const p = vfs.restore(es.map((e) => e.binId)); setSel(p); };
  const startRename = (key) => { setRenaming(key); setSel([key]); };
  const doNew = (kind) => { if (isBin || isPC) return; const p = ops.createNew(path, kind); setSel([p]); setRenaming(p); emit("app:explorer:new", { id, path: p }); };
  const commitRename = async (e, val) => {
    setRenaming(null);
    const np = await ops.renameItem(e.path, val, { ownerId: id });
    if (np) setSel([np]);
  };
  const copySel = (mode) => selPaths.length && ops.setClipboardFiles(selPaths, mode);
  const pasteHere = () => !isBin && !isPC && ops.paste(path, id);

  const sortMenu = (x, y) => showContextMenu(x, y, [
    ["name", "名稱"], ["modified", "修改日期"], ["type", "類型"], ["size", "大小"],
  ].map(([k, t]) => ({ label: t, checked: sort.key === k, onClick: () => setSort({ key: k, dir: 1 }) })).concat([{ separator: true }, { label: "遞增", checked: sort.dir === 1, onClick: () => setSort({ ...sort, dir: 1 }) }, { label: "遞減", checked: sort.dir === -1, onClick: () => setSort({ ...sort, dir: -1 }) }]), { ownerId: id });
  const viewMenu = (x, y) => showContextMenu(x, y, [
    { label: "大圖示", checked: view === "large", onClick: () => setView("large") },
    { label: "中圖示", checked: view === "medium", onClick: () => setView("medium") },
    { label: "清單", checked: view === "list", onClick: () => setView("list") },
    { label: "詳細資料", checked: view === "details", onClick: () => setView("details") },
    { separator: true },
    { label: "顯示", items: [{ label: "檔案名稱副檔名", checked: showExt, onClick: () => { sys.set({ settings: { ...sys.get().settings, showExtensions: !showExt } }); emit("sys:setting", { key: "showExtensions", value: !showExt }); } }, { label: "隱藏的項目", checked: settings.showHidden, onClick: () => sys.set({ settings: { ...sys.get().settings, showHidden: !settings.showHidden } }) }] },
  ], { ownerId: id });
  const newMenu = (x, y) => showContextMenu(x, y, ops.newMenuKinds().map((k) => ({ label: k.label, icon: k.icon, onClick: () => doNew(k) })), { ownerId: id });
  const moreMenu = (x, y) => showContextMenu(x, y, [{ label: "全選", shortcut: "Ctrl+A", onClick: () => setSel(sorted.map((e) => e.key)) }, { label: "全部不選", onClick: () => setSel([]) }, { label: "反向選擇", onClick: () => setSel(sorted.filter((e) => !sel.includes(e.key)).map((e) => e.key)) }, { separator: true }, { label: "內容", disabled: !selPaths.length, onClick: () => ops.showProperties(selPaths, id) }], { ownerId: id });

  const itemMenu = (ev, e) => {
    ev.preventDefault(); ev.stopPropagation();
    let keys = sel.includes(e.key) ? sel : [e.key];
    if (!sel.includes(e.key)) setSel([e.key]);
    const es = sorted.filter((x) => keys.includes(x.key));
    const ps = es.map((x) => x.path).filter(Boolean);
    const single = es.length === 1;
    let menu;
    if (isBin) {
      menu = [{ label: "還原", onClick: () => { const r = vfs.restore(es.map((x) => x.binId)); setSel(r); } }, { separator: true }, { label: "剪下", disabled: true }, { separator: true }, { label: "刪除", onClick: () => ops_binDelete(es) }, { label: "內容", disabled: true }];
    } else {
      menu = [
        { iconRow: [
          { icon: "file", label: "剪下", onClick: () => ops.setClipboardFiles(ps, "cut") },
          { icon: "file", label: "複製", onClick: () => ops.setClipboardFiles(ps, "copy") },
          { icon: "file", label: "重新命名", disabled: !single, onClick: () => startRename(e.key) },
          { icon: "file", label: "刪除", onClick: () => ops.deleteItems(ps, { ownerId: id }) },
        ] },
        { label: "開啟", shortcut: "Enter", onClick: () => es.forEach(openEntry) },
        ...(single && e.type === "dir" ? [{ label: "在新視窗中開啟", onClick: () => openApp("explorer", { path: e.path }) }] : []),
        { separator: true },
        { label: "剪下", shortcut: "Ctrl+X", onClick: () => ops.setClipboardFiles(ps, "cut") },
        { label: "複製", shortcut: "Ctrl+C", onClick: () => ops.setClipboardFiles(ps, "copy") },
        { label: "重新命名", shortcut: "F2", disabled: !single, onClick: () => startRename(e.key) },
        { label: "刪除", shortcut: "Del", onClick: () => ops.deleteItems(ps, { ownerId: id }) },
        { separator: true },
        { label: "內容", shortcut: "Alt+Enter", onClick: () => ops.showProperties(ps, id) },
      ];
    }
    showContextMenu(ev.clientX, ev.clientY, menu, { ownerId: id });
  };
  const bgMenu = (ev) => {
    ev.preventDefault();
    if (ev.target.closest(".ex-item")) return;
    if (isPC) return;
    if (isBin) { showContextMenu(ev.clientX, ev.clientY, [{ label: "清空資源回收筒", disabled: !sorted.length, onClick: () => ops.emptyRecycleBin(id) }, { label: "重新整理" }], { ownerId: id }); return; }
    showContextMenu(ev.clientX, ev.clientY, [
      { label: "檢視", items: [{ label: "大圖示", onClick: () => setView("large") }, { label: "中圖示", onClick: () => setView("medium") }, { label: "清單", onClick: () => setView("list") }, { label: "詳細資料", onClick: () => setView("details") }] },
      { label: "排序方式", items: [{ label: "名稱", onClick: () => setSort({ key: "name", dir: 1 }) }, { label: "修改日期", onClick: () => setSort({ key: "modified", dir: 1 }) }, { label: "類型", onClick: () => setSort({ key: "type", dir: 1 }) }, { label: "大小", onClick: () => setSort({ key: "size", dir: 1 }) }] },
      { label: "重新整理", onClick: () => emit("app:explorer:refresh", { id }) },
      { separator: true },
      { label: "貼上", shortcut: "Ctrl+V", disabled: !clip, onClick: pasteHere },
      { label: "復原", shortcut: "Ctrl+Z", disabled: !vfs.canUndo(), onClick: () => vfs.undo() },
      { separator: true },
      { label: "新增", items: ops.newMenuKinds().map((k) => ({ label: k.label, icon: k.icon, onClick: () => doNew(k) })) },
      { separator: true },
      { label: "內容", onClick: () => ops.showProperties([path], id) },
    ], { ownerId: id });
  };

  // ---- 選取 ----
  const itemDown = (ev, e, idx) => {
    if (ev.button !== 0) return;
    ev.stopPropagation();
    root.current && root.current.focus();
    let keys;
    const wasOnly = sel.length === 1 && sel[0] === e.key;
    if (ev.ctrlKey) keys = sel.includes(e.key) ? sel.filter((k) => k !== e.key) : [...sel, e.key];
    else if (ev.shiftKey && lastIdx.current != null) { const [a, b] = [lastIdx.current, idx].sort((x, y) => x - y); keys = sorted.slice(a, b + 1).map((x) => x.key); }
    else keys = sel.includes(e.key) && sel.length > 1 ? sel : [e.key];
    if (!ev.shiftKey) lastIdx.current = idx;
    setSel(keys);
    slow.current.key = wasOnly && !ev.ctrlKey && !ev.shiftKey && !isBin ? e.key : null;
    const ps = sorted.filter((x) => keys.includes(x.key)).map((x) => x.path).filter(Boolean);
    if (ps.length && !isBin) startDrag(ev, ps, { label: ps.length > 1 ? String(ps.length) : e.name, icon: e.type, ownerId: id });
  };
  const bgDown = (ev) => {
    if (ev.button !== 0 || ev.target.closest(".ex-item") || ev.target.closest(".ex-head")) return;
    root.current && root.current.focus();
    const host = contentRef.current;
    const r = host.getBoundingClientRect();
    const sx = ev.clientX - r.left + host.scrollLeft, sy = ev.clientY - r.top + host.scrollTop;
    const base = ev.ctrlKey ? sel : [];
    if (!ev.ctrlKey) setSel([]);
    setRenaming(null);
    const mv = (m) => {
      const x = m.clientX - r.left + host.scrollLeft, y = m.clientY - r.top + host.scrollTop;
      const b = { x: Math.min(sx, x), y: Math.min(sy, y), w: Math.abs(x - sx), h: Math.abs(y - sy) };
      if (b.w < 4 && b.h < 4) return;
      setBand(b);
      const hit = Array.from(host.querySelectorAll(".ex-item")).filter((el) => {
        const q = el.getBoundingClientRect();
        const ex = q.left - r.left + host.scrollLeft, ey = q.top - r.top + host.scrollTop;
        return ex < b.x + b.w && ex + q.width > b.x && ey < b.y + b.h && ey + q.height > b.y;
      }).map((el) => el.getAttribute("data-key"));
      setSel([...new Set([...base, ...hit])]);
    };
    const up = () => { setBand(null); window.removeEventListener("pointermove", mv, true); window.removeEventListener("pointerup", up, true); };
    window.addEventListener("pointermove", mv, true);
    window.addEventListener("pointerup", up, true);
  };

  const onKey = (ev) => {
    if (renaming || ev.target.tagName === "INPUT" || ev.target.tagName === "TEXTAREA") return;
    const k = ev.key.toLowerCase();
    if (ev.altKey && ev.key === "ArrowLeft") back();
    else if (ev.altKey && ev.key === "ArrowRight") fwd();
    else if (ev.altKey && ev.key === "ArrowUp") up();
    else if (ev.key === "Backspace") back();
    else if (ev.key === "F5") emit("app:explorer:refresh", { id });
    else if (ev.key === "F2" && sel.length === 1 && !isBin) { ev.preventDefault(); startRename(sel[0]); }
    else if (ev.key === "Delete" && sel.length) doDelete(ev.shiftKey);
    else if (ev.ctrlKey && k === "a") { ev.preventDefault(); setSel(sorted.map((e) => e.key)); }
    else if (ev.ctrlKey && k === "c") copySel("copy");
    else if (ev.ctrlKey && k === "x") copySel("cut");
    else if (ev.ctrlKey && k === "v") pasteHere();
    else if (ev.ctrlKey && k === "z") vfs.undo();
    else if (ev.ctrlKey && k === "y") vfs.redo();
    else if (ev.ctrlKey && ev.shiftKey && k === "n") { ev.preventDefault(); doNew("folder"); }
    else if (ev.key === "Enter" && selEntries.length) selEntries.forEach(openEntry);
    else if (ev.altKey && ev.key === "Enter") ops.showProperties(selPaths, id);
    else if (["ArrowDown", "ArrowUp", "ArrowRight", "ArrowLeft"].includes(ev.key) && sorted.length) {
      ev.preventDefault();
      const cur = sorted.findIndex((e) => e.key === sel[sel.length - 1]);
      const step = ev.key === "ArrowDown" || ev.key === "ArrowRight" ? 1 : -1;
      const ni = Math.min(sorted.length - 1, Math.max(0, cur < 0 ? 0 : cur + step));
      setSel([sorted[ni].key]); lastIdx.current = ni;
    }
  };

  // ---- 渲染 ----
  const drives = vfs.drives();
  const cmdBtn = (icon, label, onClick, disabled, simid) => (
    <button className={"ex-cmd" + (disabled ? " disabled" : "")} data-sim-id={sid("cmd:" + (simid || label))} title={label} onClick={(e) => !disabled && onClick(e)}>{icon}</button>
  );

  const renderItem = (e, idx) => {
    const selected = sel.includes(e.key);
    const isRen = renaming === e.key;
    const dropTarget = e.type === "dir" && !isBin ? e.path : undefined;
    const over = drag && dropTarget && drag.over === dropTarget;
    const thumb = e.src && IMG.test(e.name) ? asset(e.src) : null;
    const spec = e.type === "dir" && e.path ? iconForPath(e.path, { type: "dir" }) : null;
    const icon = spec ? <Ico name={spec} size={view === "large" ? 56 : view === "medium" ? 40 : 18} /> : <FileIco name={e.name} type={e.type} size={view === "large" ? 56 : view === "medium" ? 40 : 18} thumb={thumb && view !== "details" && view !== "list" ? thumb : null} />;
    const nameEl = isRen ? (
      <RenameBox initial={dispName(e)} multiline={view === "large" || view === "medium"} className={view === "details" || view === "list" ? "rename inline" : "rename"} onDone={(v) => commitRename(e, v)} />
    ) : <span className="ex-name" title={e.name}>{dispName(e)}</span>;
    const common = {
      "data-key": e.key, "data-sim-id": sid("item:" + e.name), "data-drop-path": dropTarget,
      className: "ex-item" + (selected ? " sel" : "") + (over ? " dropover" : "") + (e.path && cut.has(e.path.toLowerCase()) ? " cut" : "") + (e.hiddenItem ? " ghost" : ""),
      onPointerDown: (ev) => itemDown(ev, e, idx),
      onPointerUp: (ev) => { if (ev.button === 0 && slow.current.key === e.key && !sys.get().drag && !isRen) { slow.current.key = null; clearTimeout(slow.current.timer); slow.current.timer = setTimeout(() => startRename(e.key), 700); } },
      onDoubleClick: () => { clearTimeout(slow.current.timer); openEntry(e); },
      onContextMenu: (ev) => itemMenu(ev, e),
    };
    if (view === "details") {
      return (
        <div {...common} key={e.key} role="row">
          <div className="col-name">{icon}{nameEl}</div>
          {isBin ? <><div className="col orig">{e.orig}</div><div className="col date">{ops.fileTime(e.deletedAt)}</div><div className="col size">{e.type === "dir" ? "" : ops.formatSize(e.size)}</div><div className="col kind">{vfs.kindOf(e.name, e.type)}</div><div className="col date">{ops.fileTime(e.modified)}</div></>
            : <><div className="col date">{ops.fileTime(e.modified)}</div><div className="col kind">{vfs.kindOf(e.name, e.type)}</div><div className="col size">{e.type === "dir" ? "" : ops.formatSize(e.size)}</div>{query && <div className="col orig">{e.orig}</div>}</>}
        </div>
      );
    }
    return (
      <div {...common} key={e.key} role="gridcell" style={view === "list" ? {} : {}}>
        {icon}{nameEl}
      </div>
    );
  };

  const head = (key, label, cls) => (
    <div className={"col-h " + cls} data-sim-id={sid("sort:" + label)} onClick={() => setSort({ key, dir: sort.key === key ? -sort.dir : 1 })}>{label}{sort.key === key && <i>{sort.dir === 1 ? "︿" : "﹀"}</i>}</div>
  );

  const total = sorted.length;
  const selSize = selEntries.reduce((a, e) => a + (e.type === "dir" ? 0 : e.size), 0);

  return (
    <div className="explorer" ref={root} tabIndex={0} onKeyDown={onKey} data-sim-id={sid("root")} data-path={path}>
      {/* 工具列 */}
      <div className="ex-toolbar">
        <button className="ex-cmd text" data-sim-id={sid("cmd:新增")} disabled={isBin || isPC} onClick={(e) => { const r = e.currentTarget.getBoundingClientRect(); newMenu(r.left, r.bottom + 2); }}><FiPlus /> 新增 <span className="caret">⌄</span></button>
        <span className="ex-sep" />
        {isBin ? (
          <>
            <button className="ex-cmd text" disabled={!total} data-sim-id={sid("cmd:清空資源回收筒")} onClick={() => ops.emptyRecycleBin(id)}><FiTrash2 /> 清空資源回收筒</button>
            <button className="ex-cmd text" disabled={!total} data-sim-id={sid("cmd:還原")} onClick={() => doRestore(!sel.length)}><MdOutlineRestore /> {sel.length ? "還原選取的項目" : "還原所有項目"}</button>
          </>
        ) : (
          <>
            {cmdBtn(<FiScissors />, "剪下", () => copySel("cut"), !selPaths.length)}
            {cmdBtn(<FiCopy />, "複製", () => copySel("copy"), !selPaths.length)}
            {cmdBtn(<FiClipboard />, "貼上", pasteHere, !clip || isPC)}
            {cmdBtn(<MdDriveFileRenameOutline />, "重新命名", () => startRename(sel[0]), sel.length !== 1)}
            {cmdBtn(<FiTrash2 />, "刪除", () => doDelete(false), !selPaths.length)}
            <span className="ex-sep" />
            <button className="ex-cmd text" data-sim-id={sid("cmd:排序")} onClick={(e) => { const r = e.currentTarget.getBoundingClientRect(); sortMenu(r.left, r.bottom + 2); }}><MdSort /> 排序 <span className="caret">⌄</span></button>
            <button className="ex-cmd text" data-sim-id={sid("cmd:檢視")} onClick={(e) => { const r = e.currentTarget.getBoundingClientRect(); viewMenu(r.left, r.bottom + 2); }}><FiGrid /> 檢視 <span className="caret">⌄</span></button>
            <button className="ex-cmd" data-sim-id={sid("cmd:更多")} title="查看更多" onClick={(e) => { const r = e.currentTarget.getBoundingClientRect(); moreMenu(r.left, r.bottom + 2); }}><FiMoreHorizontal /></button>
          </>
        )}
      </div>
      {/* 位址列 */}
      <div className="ex-addrbar">
        <button className="ex-nav" disabled={hist.i === 0} data-sim-id={sid("back")} title="上一頁" onClick={back}><FiArrowLeft /></button>
        <button className="ex-nav" disabled={hist.i >= hist.stack.length - 1} data-sim-id={sid("forward")} title="下一頁" onClick={fwd}><FiArrowRight /></button>
        <button className="ex-nav" disabled={isPC} data-sim-id={sid("up")} title="上移一層" onClick={up}><FiArrowUp /></button>
        <div className="ex-addr" data-sim-id={sid("address")} onClick={() => !isVirtual(path) && setAddrEdit(path)}>
          {addrEdit != null ? (
            <input autoFocus className="ex-addr-input" data-sim-id={sid("address:input")} value={addrEdit} onChange={(e) => setAddrEdit(e.target.value)} onBlur={() => setAddrEdit(null)}
              onKeyDown={(e) => { e.stopPropagation(); if (e.key === "Enter") go(vfs.norm(addrEdit)); else if (e.key === "Escape") setAddrEdit(null); }} onFocus={(e) => e.target.select()} />
          ) : <div className="ex-crumbs"><Ico name={isBin ? "recycle" : isPC ? "thisPC" : iconForPath(path) || "folder"} size={16} /><Crumbs path={path} go={go} winId={id} /></div>}
        </div>
        <button className="ex-nav" title="重新整理" onClick={() => emit("app:explorer:refresh", { id })}><FiRefreshCw /></button>
        <div className="ex-search"><FiSearch /><input data-sim-id={sid("search")} placeholder={`搜尋 ${locName(path)}`} value={query} disabled={isPC || isBin} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.stopPropagation()} /></div>
      </div>
      <div className="ex-main">
        {/* 導覽窗格 */}
        <div className="ex-nav-pane" data-sim-id={sid("navpane")}>
          <div className="nav-sec">
            {QUICK.map(([k, t]) => (
              <div key={k} className={"tree-row" + (path === known(k) ? " sel" : "")} data-sim-id={sid("nav:" + t)} data-drop-path={known(k)} onClick={() => go(known(k))} style={{ paddingLeft: 6 }}>
                <span className="tree-arrow none" /><Ico name={SPECIAL_ICON[k]} size={16} /><span className="tree-label">{t}</span>
              </div>
            ))}
          </div>
          <div className="nav-div" />
          <div className={"tree-row" + (path === VIRTUAL.RECYCLE ? " sel" : "")} style={{ paddingLeft: 6 }} data-sim-id={sid("nav:資源回收筒")} data-drop-path="::recycle" onClick={() => go(VIRTUAL.RECYCLE)}>
            <span className="tree-arrow none" /><Ico name={vfs.binCount() ? "recycle-full" : "recycle"} size={16} /><span className="tree-label">資源回收筒</span>
          </div>
          <div className={"tree-row" + (path === VIRTUAL.THISPC ? " sel" : "")} style={{ paddingLeft: 6 }} data-sim-id={sid("nav:本機")} onClick={() => go(VIRTUAL.THISPC)}>
            <span className="tree-arrow" onClick={(e) => { e.stopPropagation(); setExpanded((s) => { const n = new Set(s); n.has("::thispc") ? n.delete("::thispc") : n.add("::thispc"); return n; }); }}>{expanded.has("::thispc") ? "⌄" : "›"}</span>
            <Ico name="thisPC" size={16} /><span className="tree-label">本機</span>
          </div>
          {expanded.has("::thispc") && (
            <>
              {QUICK.map(([k, t]) => <TreeNode key={"t" + k} path={known(k)} label={t + " "} icon={SPECIAL_ICON[k]} depth={1} cur={path} go={go} winId={id} expanded={expanded} toggle={(p) => setExpanded((s) => { const n = new Set(s); n.has(p) ? n.delete(p) : n.add(p); return n; })} />)}
              {drives.map((d) => <TreeNode key={d} path={d + ":\\"} label={`本機磁碟 (${d}:)`} icon="drive" depth={1} cur={path} go={go} winId={id} expanded={expanded} toggle={(p) => setExpanded((s) => { const n = new Set(s); n.has(p) ? n.delete(p) : n.add(p); return n; })} />)}
            </>
          )}
        </div>
        {/* 內容 */}
        <div className="ex-content-wrap">
          {isPC ? (
            <div className="ex-pc" data-sim-id={sid("content")}>
              <div className="pc-h">資料夾 ({QUICK.length})</div>
              <div className="pc-folders">
                {QUICK.map(([k, t]) => (
                  <div key={k} className="pc-folder" data-sim-id={sid("item:" + t)} data-drop-path={known(k)} onDoubleClick={() => go(known(k))} onClick={() => root.current.focus()}>
                    <Ico name={SPECIAL_ICON[k]} size={40} /><div><div>{t}</div><small>{vfs.list(known(k)).length} 個項目</small></div>
                  </div>
                ))}
              </div>
              <div className="pc-h">裝置和磁碟機 ({drives.length})</div>
              <div className="pc-folders">
                {drives.map((d) => {
                  const used = vfs.sizeOf(vfs.get(d + ":\\")) + 31.9 * 1073741824, tot = 119 * 1073741824;
                  return (
                    <div key={d} className="pc-drive" data-sim-id={sid("item:本機磁碟 (" + d + ":)")} data-drop-path={d + ":\\"} onDoubleClick={() => go(d + ":\\")}>
                      <Ico name="drive" size={44} />
                      <div style={{ flex: 1 }}><div>本機磁碟 ({d}:)</div><div className="drive-bar"><i style={{ width: (used / tot) * 100 + "%" }} /></div><small>{((tot - used) / 1073741824).toFixed(1)} GB 可用，共 {(tot / 1073741824).toFixed(0)} GB</small></div>
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            <div ref={contentRef} className={"ex-content view-" + view} data-sim-id={sid("content")} data-drop-path={isBin ? undefined : path} onPointerDown={bgDown} onContextMenu={bgMenu}>
              {view === "details" && (
                <div className="ex-head" role="row">
                  {head("name", "名稱", "col-name-h")}
                  {isBin ? <>{head("orig", "原始位置", "orig")}{head("deleted", "刪除日期", "date")}{head("size", "大小", "size")}{head("type", "項目類型", "kind")}{head("modified", "修改日期", "date")}</>
                    : <>{head("modified", "修改日期", "date")}{head("type", "類型", "kind")}{head("size", "大小", "size")}{query && <div className="col-h orig">位置</div>}</>}
                </div>
              )}
              {sorted.map(renderItem)}
              {!sorted.length && <div className="ex-empty" data-sim-id={sid("empty")}>{query ? "沒有符合搜尋條件的項目。" : isBin ? "資源回收筒是空的" : "這個資料夾是空的。"}</div>}
              {band && <div className="band" style={{ left: band.x, top: band.y, width: band.w, height: band.h }} />}
            </div>
          )}
        </div>
      </div>
      <div className="ex-status" data-sim-id={sid("status")}>
        <span>{isPC ? `${QUICK.length + drives.length} 個項目` : `${total} 個項目`}{sel.length > 0 && `　|　已選取 ${sel.length} 個項目${selSize ? "　" + ops.formatSize(selSize) : ""}`}</span>
        <span className="ex-views">
          <button className={view === "details" ? "on" : ""} title="詳細資料" onClick={() => setView("details")}><FiList /></button>
          <button className={view === "large" ? "on" : ""} title="大圖示" onClick={() => setView("large")}><FiGrid /></button>
        </span>
      </div>
    </div>
  );
}
