import React, { useEffect } from "react";
import { sys, useSys } from "../kernel/store";
import { closeWindow, openApp, showDesktop } from "../kernel/wm";
import { hideContextMenu } from "../kernel/ui";
import { on, emit } from "../kernel/events";
import * as vfs from "../kernel/vfs";
import Desktop from "./Desktop";
import WindowLayer from "./Window";
import Taskbar from "./Taskbar";
import StartMenu from "./StartMenu";
import ContextMenuLayer from "./ContextMenu";
import DialogLayer from "./Dialogs";
import Boot from "./Boot";
import { Calendar, QuickSettings } from "./Flyouts";
import { Ico } from "./icons";
import DemoCursor from "../kernel/DemoCursor";

function Toasts() {
  const toasts = useSys((s) => s.toasts);
  return (
    <div className="toasts">
      {toasts.map((t) => (
        <div key={t.id} className="toast" data-sim-id="toast">
          <Ico name={t.icon} size={22} />
          <div><b>{t.title}</b><div>{t.text}</div></div>
        </div>
      ))}
    </div>
  );
}

function DragGhost() {
  const d = useSys((s) => s.drag);
  if (!d) return null;
  return (
    <div className="drag-ghost" style={{ left: d.x + 12, top: d.y + 12 }}>
      <Ico name={d.icon === "dir" ? "folder" : "file"} size={28} />
      <div className="drag-tip">{d.over ? (d.over === "::recycle" ? "移至 資源回收筒" : (d.copy ? "複製到 " : "移動到 ") + (d.over === "::desktop" ? "桌面" : vfs.basename(d.over))) : d.label}</div>
    </div>
  );
}

export default function Shell() {
  const phase = useSys((s) => s.phase);
  const fsBtn = useSys((s) => s.fsButton);
  const theme = useSys((s) => s.settings.theme);
  const hideSig = useSys((s) => s.hideSig);
  const sig = hideSig ? null : <div className="sim-sig">made by 資訊老師黃博胤</div>;

  useEffect(() => {
    // 最近使用的檔案（開始功能表「建議的項目」）
    const off = on("file:open", (e) => {
      sys.set((s) => ({ recent: [{ path: e.data.path, when: "剛剛" }, ...(s.recent || []).filter((r) => r.path.toLowerCase() !== e.data.path.toLowerCase())].slice(0, 12) }));
    });
    const key = (e) => {
      if (sys.get().phase !== "desktop") return;
      if (e.altKey && e.key === "F4") { e.preventDefault(); const id = sys.get().focusedId; if (id) closeWindow(id); }
      else if (e.key === "Meta" && !e.ctrlKey) { sys.set((s) => ({ startOpen: !s.startOpen, contextMenu: null })); }
      else if (e.key === "Escape") { if (sys.get().contextMenu) hideContextMenu(); else sys.set({ startOpen: false, quickOpen: false, calendarOpen: false, userMenuOpen: false }); }
      else if (e.metaKey && e.key.toLowerCase() === "d") { e.preventDefault(); showDesktop(); }
      else if (e.metaKey && e.key.toLowerCase() === "e") { e.preventDefault(); openApp("explorer"); }
    };
    const down = (e) => {
      if (!e.target.closest) return;
      const s = sys.get();
      if (!e.target.closest(".start,.taskbar,.flyout")) {
        if (s.startOpen || s.quickOpen || s.calendarOpen || s.userMenuOpen) sys.set({ startOpen: false, quickOpen: false, calendarOpen: false, userMenuOpen: false });
      }
    };
    const ctx = (e) => e.preventDefault();
    window.addEventListener("keydown", key);
    window.addEventListener("pointerdown", down, true);
    window.addEventListener("contextmenu", ctx);
    return () => { off(); window.removeEventListener("keydown", key); window.removeEventListener("pointerdown", down, true); window.removeEventListener("contextmenu", ctx); };
  }, []);

  if (phase !== "desktop") {
    return (<div className="sim-root" data-theme={theme}><Boot /><DemoCursor />{sig}</div>);
  }
  return (
    <div className="sim-root" data-sim-id="root" data-theme={theme}>
      <Desktop />
      <WindowLayer />
      <Taskbar />
      <StartMenu />
      <Calendar />
      <QuickSettings />
      <ContextMenuLayer />
      <DialogLayer />
      <Toasts />
      <DragGhost />
      <DemoCursor />
      {sig}
      {fsBtn && <button className="fs-btn" title="全螢幕" onClick={() => (document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen())}>⛶</button>}
    </div>
  );
}
