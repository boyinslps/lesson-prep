// 記事本：比照 Windows 11（選單、狀態列、未存檔提示、另存新檔、Insert 覆寫模式、自己管理復原／剪貼簿以支援自動操作）
import React, { useEffect, useRef, useState } from "react";
import { sys } from "../kernel/store";
import * as vfs from "../kernel/vfs";
import { known } from "../kernel/paths";
import { openApp } from "../kernel/wm";
import { showContextMenu, hideContextMenu, messageBox } from "../kernel/ui";
import { emit } from "../kernel/events";
import { fileDialog } from "../shell/FileDialog";
import { useWin, useCloseGuard } from "../shell/WinContext";
import { useExposeState } from "../kernel/appstate";
import { simNow } from "../kernel/clock";

const FILTERS = [{ label: "文字文件 (*.txt)", exts: ["txt"] }, { label: "所有檔案 (*.*)", exts: ["*"] }];

export default function Notepad() {
  const w = useWin();
  const ta = useRef(null);
  const [text, setText] = useState("");
  const [path, setPath] = useState(null);
  const [dirty, setDirty] = useState(false);
  const [wrap, setWrap] = useState(true);
  const [overwrite, setOverwrite] = useState(false);
  const [menu, setMenu] = useState(null);
  const [caret, setCaret] = useState({ line: 1, col: 1 });
  const [zoom, setZoom] = useState(100);
  const undo = useRef({ stack: [""], i: 0, last: 0 });
  useExposeState(() => ({ text, path, dirty, overwrite, zoom }));

  // 開啟指定檔案
  const load = (p) => {
    try {
      const t = vfs.readFile(p);
      setText(t); setPath(vfs.norm(p)); setDirty(false);
      undo.current = { stack: [t], i: 0, last: 0 };
    } catch (e) { messageBox({ ownerId: w.id, title: "記事本", icon: "warn", text: "找不到檔案。" }); }
  };
  useEffect(() => { if (w.args.path) load(w.args.path); }, []); // eslint-disable-line
  useEffect(() => { w.setTitle(`${dirty ? "*" : ""}${path ? vfs.basename(path) : "無標題"} - 記事本`); }, [path, dirty]); // eslint-disable-line

  const record = (v) => {
    const u = undo.current, now = performance.now();
    if (now - u.last > 700 || u.stack.length === 0) { u.stack = u.stack.slice(0, u.i + 1); u.stack.push(v); u.i = u.stack.length - 1; }
    else u.stack[u.i] = v;
    u.last = now;
  };
  const change = (v) => { setText(v); setDirty(true); record(v); emit("app:notepad:edit", { id: w.id, length: v.length }); };
  const apply = (v, s, e = s) => { change(v); requestAnimationFrame(() => { if (ta.current) { ta.current.value = v; ta.current.setSelectionRange(s, e); updateCaret(); } }); };
  const sel = () => { const el = ta.current; return { s: el.selectionStart, e: el.selectionEnd, v: el.value }; };
  const updateCaret = () => {
    const el = ta.current; if (!el) return;
    const before = el.value.slice(0, el.selectionStart).split("\n");
    setCaret({ line: before.length, col: before[before.length - 1].length + 1 });
  };

  // ---- 編輯動作（真實與模擬事件共用）----
  const setClip = (t) => { sys.set((s) => ({ clipboard: { ...s.clipboard, text: t } })); try { navigator.clipboard && navigator.clipboard.writeText(t).catch(() => {}); } catch (e) { /* 忽略 */ } emit("clipboard:text", { length: t.length }); };
  const doCopy = () => { const { s, e, v } = sel(); if (e > s) setClip(v.slice(s, e)); };
  const doCut = () => { const { s, e, v } = sel(); if (e > s) { setClip(v.slice(s, e)); apply(v.slice(0, s) + v.slice(e), s); } };
  const doPaste = (t) => { const clip = t ?? sys.get().clipboard.text; if (!clip) return; const { s, e, v } = sel(); apply(v.slice(0, s) + clip + v.slice(e), s + clip.length); };
  const doDelete = () => { const { s, e, v } = sel(); if (e > s) apply(v.slice(0, s) + v.slice(e), s); };
  const doAll = () => { ta.current.focus(); ta.current.setSelectionRange(0, ta.current.value.length); updateCaret(); };
  const doUndo = () => { const u = undo.current; if (u.i > 0) { u.i--; const v = u.stack[u.i]; setText(v); setDirty(true); u.last = 0; requestAnimationFrame(() => ta.current && ta.current.setSelectionRange(v.length, v.length)); emit("app:notepad:undo", { id: w.id }); } };
  const doRedo = () => { const u = undo.current; if (u.i < u.stack.length - 1) { u.i++; const v = u.stack[u.i]; setText(v); setDirty(true); u.last = 0; emit("app:notepad:redo", { id: w.id }); } };
  const doDate = () => { const d = new Date(simNow()); const t = d.toLocaleTimeString("zh-TW", { hour: "numeric", minute: "2-digit", hour12: true }) + " " + d.toLocaleDateString("zh-TW"); const { s, e, v } = sel(); apply(v.slice(0, s) + t + v.slice(e), s + t.length); };

  // ---- 檔案動作 ----
  const saveTo = (p) => { vfs.saveFile(p, text); setPath(vfs.norm(p)); setDirty(false); emit("app:notepad:save", { id: w.id, path: vfs.norm(p) }); return true; };
  const saveAs = async () => {
    const p = await fileDialog({ ownerId: w.id, mode: "save", startDir: path ? vfs.dirname(path) : known("documents"), defaultName: path ? vfs.basename(path) : "", filters: FILTERS, defaultExt: "txt" });
    if (!p) return false;
    return saveTo(p);
  };
  const save = async () => (path && vfs.exists(path) ? saveTo(path) : saveAs());
  const askSave = async () => {
    if (!dirty) return true;
    const r = await w.messageBox({ title: "記事本", icon: null, text: `要儲存變更至 ${path ? vfs.basename(path) : "無標題"} 嗎?`, buttons: [{ label: "儲存", value: "save", primary: true }, { label: "不要儲存", value: "no" }, { label: "取消", value: "cancel" }], kind: "save-changes" });
    if (r === "save") return save();
    return r === "no";
  };
  useCloseGuard(askSave);
  const newDoc = async () => { if (!(await askSave())) return; setText(""); setPath(null); setDirty(false); undo.current = { stack: [""], i: 0, last: 0 }; };
  const openFile = async () => {
    if (!(await askSave())) return;
    const p = await fileDialog({ ownerId: w.id, mode: "open", startDir: known("documents"), filters: FILTERS });
    if (p) load(p);
  };

  const onKeyDown = (e) => {
    const k = e.key.toLowerCase();
    e.stopPropagation();
    if (e.ctrlKey && !e.altKey) {
      if (k === "s") { e.preventDefault(); e.shiftKey ? saveAs() : save(); return; }
      if (k === "o") { e.preventDefault(); openFile(); return; }
      if (k === "n") { e.preventDefault(); e.shiftKey ? openApp("notepad") : newDoc(); return; }
      if (k === "z") { e.preventDefault(); doUndo(); return; }
      if (k === "y") { e.preventDefault(); doRedo(); return; }
      if (k === "a") { e.preventDefault(); doAll(); return; }
      if (!e.isTrusted) { // 自動操作送來的按鍵：自己處理剪貼簿
        if (k === "c") { e.preventDefault(); doCopy(); return; }
        if (k === "x") { e.preventDefault(); doCut(); return; }
        if (k === "v") { e.preventDefault(); doPaste(); return; }
      }
      if (e.key === "+" || e.key === "=") { e.preventDefault(); setZoom((z) => Math.min(500, z + 10)); return; }
      if (e.key === "-") { e.preventDefault(); setZoom((z) => Math.max(10, z - 10)); return; }
      if (e.key === "0") { e.preventDefault(); setZoom(100); return; }
    }
    if (e.key === "F5") { e.preventDefault(); doDate(); return; }
    if (e.key === "Insert") { e.preventDefault(); setOverwrite((o) => !o); emit("app:notepad:overwrite", { on: !overwrite }); return; }
    if (overwrite && e.key.length === 1 && !e.ctrlKey && !e.altKey && !e.metaKey) {
      e.preventDefault();
      const { s, e: en, v } = sel();
      const end = en > s ? en : Math.min(v.length, s + (v[s] === "\n" ? 0 : 1));
      apply(v.slice(0, s) + e.key + v.slice(end), s + 1);
      return;
    }
    if (e.key === "Tab") { e.preventDefault(); const { s, e: en, v } = sel(); apply(v.slice(0, s) + "\t" + v.slice(en), s + 1); }
  };

  const ctx = (e) => {
    e.preventDefault();
    const { s, e: en } = sel(); const has = en > s;
    showContextMenu(e.clientX, e.clientY, [
      { label: "復原", shortcut: "Ctrl+Z", disabled: undo.current.i === 0, onClick: doUndo },
      { separator: true },
      { label: "剪下", shortcut: "Ctrl+X", disabled: !has, onClick: doCut },
      { label: "複製", shortcut: "Ctrl+C", disabled: !has, onClick: doCopy },
      { label: "貼上", shortcut: "Ctrl+V", disabled: !sys.get().clipboard.text, onClick: () => doPaste() },
      { label: "刪除", shortcut: "Del", disabled: !has, onClick: doDelete },
      { separator: true },
      { label: "全選", shortcut: "Ctrl+A", onClick: doAll },
    ], { ownerId: w.id });
  };

  const MENUS = {
    "檔案": [
      ["新增", "Ctrl+N", newDoc], ["新增視窗", "Ctrl+Shift+N", () => openApp("notepad")], ["開啟...", "Ctrl+O", openFile], ["儲存", "Ctrl+S", save], ["另存新檔...", "Ctrl+Shift+S", saveAs], null, ["結束", "", () => w.close()],
    ],
    "編輯": [
      ["復原", "Ctrl+Z", doUndo], null, ["剪下", "Ctrl+X", doCut], ["複製", "Ctrl+C", doCopy], ["貼上", "Ctrl+V", () => doPaste()], ["刪除", "Del", doDelete], null, ["時間/日期", "F5", doDate], null, ["全選", "Ctrl+A", doAll],
    ],
    "檢視": [
      ["放大", "Ctrl+加號", () => setZoom((z) => Math.min(500, z + 10))], ["縮小", "Ctrl+減號", () => setZoom((z) => Math.max(10, z - 10))], ["還原預設縮放", "Ctrl+0", () => setZoom(100)], null, [(wrap ? "✓ " : "　") + "自動換行", "", () => setWrap(!wrap)],
    ],
  };

  return (
    <div className="notepad" data-sim-id={`notepad:${w.id}`} onPointerDown={() => hideContextMenu()}>
      <div className="np-menubar">
        {Object.keys(MENUS).map((m) => (
          <div key={m} className="np-menu-wrap">
            <button className={"np-menu" + (menu === m ? " open" : "")} data-sim-id={`notepad:${w.id}:menu:${m}`} onClick={() => setMenu(menu === m ? null : m)} onMouseEnter={() => menu && setMenu(m)}>{m}</button>
            {menu === m && (
              <div className="np-drop" onMouseLeave={() => {}}>
                {MENUS[m].map((it, i) => it ? (
                  <div key={i} className="np-item" data-sim-id={`notepad:${w.id}:item:${it[0].replace(/^[✓　] /, "")}`} onClick={() => { setMenu(null); it[2](); }}>
                    <span>{it[0]}</span><em>{it[1]}</em>
                  </div>
                ) : <div key={i} className="ctx-sep" />)}
              </div>
            )}
          </div>
        ))}
      </div>
      {menu && <div className="np-backdrop" onPointerDown={() => setMenu(null)} />}
      <textarea
        ref={ta}
        className="np-text"
        data-sim-id={`notepad:${w.id}:text`}
        value={text}
        spellCheck={false}
        autoFocus
        wrap={wrap ? "soft" : "off"}
        style={{ fontSize: (14 * zoom) / 100, whiteSpace: wrap ? "pre-wrap" : "pre" }}
        onChange={(e) => change(e.target.value)}
        onKeyDown={onKeyDown}
        onKeyUp={updateCaret}
        onClick={updateCaret}
        onSelect={updateCaret}
        onCopy={() => { const { s, e, v } = sel(); if (e > s) sys.set((st) => ({ clipboard: { ...st.clipboard, text: v.slice(s, e) } })); }}
        onCut={() => { const { s, e, v } = sel(); if (e > s) sys.set((st) => ({ clipboard: { ...st.clipboard, text: v.slice(s, e) } })); }}
        onContextMenu={ctx}
      />
      <div className="np-status">
        <span>第 {caret.line} 行，第 {caret.col} 欄</span>
        <span>{text.length} 個字元</span>
        <span>{zoom}%</span>
        <span>Windows (CRLF)</span>
        <span>UTF-8</span>
        {overwrite && <span className="np-ovr">改寫</span>}
      </div>
    </div>
  );
}
