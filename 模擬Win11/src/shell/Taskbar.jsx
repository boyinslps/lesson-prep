import React, { useState } from "react";
import { sys, useSys } from "../kernel/store";
import { allApps, getApp } from "../kernel/apps";
import { openApp, restoreWindow, minimizeWindow, closeWindow, showDesktop } from "../kernel/wm";
import { showContextMenu } from "../kernel/ui";
import * as vfs from "../kernel/vfs";
import { Ico } from "./icons";
import { useClock, useVfs } from "./hooks";

const closeFlyouts = { startOpen: false, searchOpen: false, quickOpen: false, calendarOpen: false, userMenuOpen: false };

function AppBtn({ appId }) {
  const app = getApp(appId);
  const wins = useSys((s) => s.windows.filter((w) => w.app === appId));
  const focusedId = useSys((s) => s.focusedId);
  const pinned = useSys((s) => s.taskbarPins.includes(appId));
  const [list, setList] = useState(false);
  if (!app) return null;
  const active = wins.some((w) => w.id === focusedId && w.state !== "min");
  const click = () => {
    sys.set(closeFlyouts);
    if (!wins.length) return openApp(appId);
    if (wins.length === 1) {
      const w = wins[0];
      if (w.id === focusedId && w.state !== "min") minimizeWindow(w.id);
      else restoreWindow(w.id);
    } else setList((v) => !v);
  };
  return (
    <div className="tb-wrap">
      <button
        className={"tb-btn" + (wins.length ? " running" : "") + (active ? " active" : "")}
        data-sim-id={"taskbar:app:" + appId}
        title={app.name}
        onClick={click}
        onContextMenu={(e) => {
          e.preventDefault();
          showContextMenu(e.clientX, Math.max(8, e.clientY - 120), [
            { label: app.name, icon: app.icon, onClick: () => openApp(appId) },
            { separator: true },
            { label: pinned ? "從工作列取消釘選" : "釘選到工作列", icon: "windows", onClick: () => sys.set((s) => ({ taskbarPins: pinned ? s.taskbarPins.filter((x) => x !== appId) : [...s.taskbarPins, appId] })) },
            ...(wins.length ? [{ label: wins.length > 1 ? "關閉所有視窗" : "關閉視窗", icon: "error", onClick: () => wins.forEach((w) => closeWindow(w.id)) }] : []),
          ]);
        }}
      >
        <Ico name={app.icon} size={26} />
        {wins.length > 1 && <span className="tb-count">{wins.length}</span>}
      </button>
      {list && (
        <div className="tb-list" onMouseLeave={() => setList(false)}>
          {wins.map((w) => (
            <div key={w.id} className="tb-list-item" data-sim-id={"taskbar:win:" + w.id} onClick={() => { restoreWindow(w.id); setList(false); }}>
              <Ico name={app.icon} size={16} /><span>{w.title}</span>
              <button className="tb-x" onClick={(e) => { e.stopPropagation(); closeWindow(w.id); }}>✕</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Taskbar() {
  const pins = useSys((s) => s.taskbarPins);
  const startOpen = useSys((s) => s.startOpen);
  const running = useSys((s) => Array.from(new Set(s.windows.map((w) => w.app))));
  const quickOpen = useSys((s) => s.quickOpen);
  const calOpen = useSys((s) => s.calendarOpen);
  const t = useClock();
  useVfs();
  const apps = [...pins.filter((p) => p !== "start" && p !== "search"), ...running.filter((r) => !pins.includes(r))];
  const time = t.toLocaleTimeString("zh-TW", { hour: "numeric", minute: "2-digit", hour12: true });
  const date = t.toLocaleDateString("zh-TW", { year: "numeric", month: "numeric", day: "numeric" });

  return (
    <div className="taskbar" data-sim-id="taskbar" onContextMenu={(e) => { e.preventDefault(); showContextMenu(e.clientX, e.clientY - 80, [{ label: "工作列設定", icon: "settings" }]); }}>
      <div className="tb-center">
        <button className={"tb-btn" + (startOpen ? " active" : "")} data-sim-id="taskbar:start" title="開始" onClick={() => sys.set({ ...closeFlyouts, startOpen: !startOpen, contextMenu: null })}>
          <Ico name="windows" size={24} />
        </button>
        {pins.includes("search") && (
          <button className="tb-btn" data-sim-id="taskbar:search" title="搜尋" onClick={() => sys.set({ ...closeFlyouts, startOpen: true })}><Ico name="search" size={22} /></button>
        )}
        {apps.map((id) => <AppBtn key={id} appId={id} />)}
      </div>
      <div className="tb-right">
        <button className="tb-tray" title="顯示隱藏的圖示" data-sim-id="taskbar:chevron">
          <svg width="12" height="12" viewBox="0 0 12 12"><path d="M2 8l4-4 4 4" stroke="currentColor" fill="none" /></svg>
        </button>
        <button className={"tb-tray sys" + (quickOpen ? " active" : "")} data-sim-id="taskbar:quick" title="網路、音量、電池" onClick={() => sys.set({ ...closeFlyouts, quickOpen: !quickOpen })}>
          <svg width="16" height="16" viewBox="0 0 16 16"><path d="M1 6a10 10 0 0 1 14 0M3.3 8.6a6.6 6.6 0 0 1 9.4 0M5.7 11a3.3 3.3 0 0 1 4.6 0" stroke="currentColor" fill="none" strokeLinecap="round" /><circle cx="8" cy="13" r="1" fill="currentColor" /></svg>
          <svg width="16" height="16" viewBox="0 0 16 16"><path d="M2 6h3l4-3v10l-4-3H2zM11 5.5a3.5 3.5 0 0 1 0 5" stroke="currentColor" fill="none" strokeLinecap="round" /></svg>
          <svg width="18" height="16" viewBox="0 0 18 16"><rect x="1" y="4" width="13" height="8" rx="1.5" stroke="currentColor" fill="none" /><rect x="2.5" y="5.5" width="10" height="5" fill="currentColor" /><rect x="15" y="6.5" width="1.6" height="3" fill="currentColor" /></svg>
        </button>
        <button className={"tb-tray clock" + (calOpen ? " active" : "")} data-sim-id="taskbar:clock" onClick={() => sys.set({ ...closeFlyouts, calendarOpen: !calOpen })}>
          <span>{time}</span><span>{date}</span>
        </button>
        <button className="tb-tray bell" data-sim-id="taskbar:notifications" title="通知">
          <svg width="16" height="16" viewBox="0 0 16 16"><path d="M8 2a4 4 0 0 0-4 4v3L2.5 11.5h11L12 9V6a4 4 0 0 0-4-4zM6.5 13a1.5 1.5 0 0 0 3 0" stroke="currentColor" fill="none" /></svg>
        </button>
        <div className="tb-showdesktop" data-sim-id="taskbar:showdesktop" title="顯示桌面" onClick={showDesktop} />
      </div>
    </div>
  );
}

export { allApps, vfs };
