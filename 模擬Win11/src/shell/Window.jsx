import React, { useRef } from "react";
import { sys, useSys } from "../kernel/store";
import { getApp } from "../kernel/apps";
import { WinCtx } from "./WinContext";
import { Ico } from "./icons";
import { closeWindow, focusWindow, minimizeWindow, toggleMaximize, moveWindow, snapWindow, desktopArea } from "../kernel/wm";

const MIN = { w: 320, h: 200 };

function Frame({ win }) {
  const app = getApp(win.app);
  const focused = useSys((s) => s.focusedId === win.id);
  const hasDialog = useSys((s) => s.dialogs.some((d) => d.ownerId === win.id));
  const ref = useRef(null);
  if (!app) return null;
  const max = win.state === "max";
  const D = desktopArea();
  const r = max ? { x: 0, y: 0, w: D.w, h: D.h } : win.rect;
  const sid = (n) => `win:${win.id}:${n}`;

  const startMove = (e) => {
    if (e.button !== 0 || e.target.closest(".win-ctl")) return;
    focusWindow(win.id);
    const sx = e.clientX, sy = e.clientY;
    const base = max ? { x: sx - win.rect.w / 2, y: 0, w: (win.restoreRect || win.rect).w, h: (win.restoreRect || win.rect).h } : { ...win.rect };
    let moved = false, snap = null;
    const mv = (ev) => {
      const dx = ev.clientX - sx, dy = ev.clientY - sy;
      if (!moved && Math.hypot(dx, dy) < 4) return;
      if (!moved && max) { sys.set((s) => ({ windows: s.windows.map((w) => (w.id === win.id ? { ...w, state: "normal", rect: { ...base, x: ev.clientX - base.w * (sx / D.w), y: 0 }, restoreRect: null } : w)) })); base.x = ev.clientX - base.w * (sx / D.w); base.y = 0; }
      moved = true;
      const nx = base.x + (max ? ev.clientX - sx : dx), ny = Math.max(0, base.y + dy);
      moveWindow(win.id, { x: nx, y: Math.min(ny, D.h - 30) });
      snap = ev.clientY <= 2 ? "max" : ev.clientX <= 2 ? "left" : ev.clientX >= window.innerWidth - 3 ? "right" : null;
      sys.set({ snapPreview: snap });
    };
    const up = () => {
      window.removeEventListener("pointermove", mv, true);
      window.removeEventListener("pointerup", up, true);
      sys.set({ snapPreview: null });
      if (snap === "max") toggleMaximize(win.id);
      else if (snap) snapWindow(win.id, snap);
    };
    window.addEventListener("pointermove", mv, true);
    window.addEventListener("pointerup", up, true);
  };

  const startResize = (dir) => (e) => {
    if (e.button !== 0 || max) return;
    e.stopPropagation();
    focusWindow(win.id);
    const sx = e.clientX, sy = e.clientY, b = { ...win.rect };
    const mn = app.minSize || MIN;
    const mv = (ev) => {
      let { x, y, w, h } = b;
      const dx = ev.clientX - sx, dy = ev.clientY - sy;
      if (dir.includes("e")) w = Math.max(mn.w, b.w + dx);
      if (dir.includes("s")) h = Math.max(mn.h, b.h + dy);
      if (dir.includes("w")) { w = Math.max(mn.w, b.w - dx); x = b.x + (b.w - w); }
      if (dir.includes("n")) { h = Math.max(mn.h, b.h - dy); y = b.y + (b.h - h); }
      moveWindow(win.id, { x, y, w, h });
    };
    const up = () => { window.removeEventListener("pointermove", mv, true); window.removeEventListener("pointerup", up, true); };
    window.addEventListener("pointermove", mv, true);
    window.addEventListener("pointerup", up, true);
  };

  const Comp = app.component;
  return (
    <div
      ref={ref}
      className={"win" + (focused ? " focused" : "") + (max ? " max" : "") + (win.state === "min" ? " minimized" : "")}
      style={{ left: r.x, top: r.y, width: r.w, height: r.h, zIndex: win.z }}
      data-sim-id={`win:${win.id}`}
      data-app={win.app}
      onPointerDown={() => !focused && focusWindow(win.id)}
    >
      <div className="win-title" onPointerDown={startMove} onDoubleClick={(e) => !e.target.closest(".win-ctl") && app.maximizable !== false && toggleMaximize(win.id)} data-sim-id={sid("title")}>
        <Ico name={app.icon} size={16} className="win-ico" />
        <span className="win-title-text">{win.title}</span>
        <div className="win-ctl-wrap">
          <button className="win-ctl" aria-label="最小化" data-sim-id={sid("minimize")} onClick={() => minimizeWindow(win.id)}>
            <svg width="10" height="10" viewBox="0 0 10 10"><path d="M0 5h10" stroke="currentColor" /></svg>
          </button>
          {app.maximizable !== false && (
            <button className="win-ctl" aria-label={max ? "還原" : "最大化"} data-sim-id={sid("maximize")} onClick={() => toggleMaximize(win.id)}>
              {max ? <svg width="10" height="10" viewBox="0 0 10 10"><path d="M2.5 2.5v-2h7v7h-2M.5 2.5h7v7h-7z" stroke="currentColor" fill="none" /></svg> : <svg width="10" height="10" viewBox="0 0 10 10"><rect x=".5" y=".5" width="9" height="9" stroke="currentColor" fill="none" /></svg>}
            </button>
          )}
          <button className="win-ctl close" aria-label="關閉" data-sim-id={sid("close")} onClick={() => closeWindow(win.id)}>
            <svg width="10" height="10" viewBox="0 0 10 10"><path d="M0 0l10 10M10 0L0 10" stroke="currentColor" /></svg>
          </button>
        </div>
      </div>
      <div className="win-body">
        <WinCtx.Provider value={win}>
          <Comp win={win} args={win.args} />
        </WinCtx.Provider>
      </div>
      {hasDialog && <div className="win-blocker" />}
      {!max && ["n", "s", "e", "w", "ne", "nw", "se", "sw"].map((d) => <div key={d} className={"rz rz-" + d} onPointerDown={startResize(d)} />)}
    </div>
  );
}

export default function WindowLayer() {
  const wins = useSys((s) => s.windows);
  const snap = useSys((s) => s.snapPreview);
  const D = desktopArea();
  return (
    <>
      {wins.map((w) => <Frame key={w.id} win={w} />)}
      {snap && <div className="snap-preview" style={snap === "max" ? { left: 8, top: 8, width: D.w - 16, height: D.h - 16 } : { left: snap === "left" ? 8 : D.w / 2 + 4, top: 8, width: D.w / 2 - 12, height: D.h - 16 }} />}
    </>
  );
}
