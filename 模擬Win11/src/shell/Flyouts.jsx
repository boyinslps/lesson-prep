import React, { useState } from "react";
import { sys, useSys } from "../kernel/store";
import { useClock } from "./hooks";

export function Calendar() {
  const open = useSys((s) => s.calendarOpen);
  const t = useClock();
  if (!open) return null;
  const y = t.getFullYear(), m = t.getMonth(), today = t.getDate();
  const first = new Date(y, m, 1).getDay();
  const days = new Date(y, m + 1, 0).getDate();
  const cells = [...Array(first).fill(null), ...Array.from({ length: days }, (_, i) => i + 1)];
  return (
    <div className="flyout cal" data-sim-id="flyout:calendar" onPointerDown={(e) => e.stopPropagation()}>
      <div className="cal-head"><div className="cal-time">{t.toLocaleTimeString("zh-TW", { hour: "numeric", minute: "2-digit", second: "2-digit", hour12: true })}</div><div className="cal-date">{t.toLocaleDateString("zh-TW", { year: "numeric", month: "long", day: "numeric", weekday: "long" })}</div></div>
      <div className="cal-month">{y} 年 {m + 1} 月</div>
      <div className="cal-grid">
        {["日", "一", "二", "三", "四", "五", "六"].map((d) => <div key={d} className="cal-dow">{d}</div>)}
        {cells.map((d, i) => <div key={i} className={"cal-day" + (d === today ? " today" : "")}>{d}</div>)}
      </div>
    </div>
  );
}

export function QuickSettings() {
  const open = useSys((s) => s.quickOpen);
  const vol = useSys((s) => s.volume ?? 60);
  const [tiles, setTiles] = useState({ wifi: true, bt: false, plane: false, saver: false, night: false, access: false });
  if (!open) return null;
  const T = ({ id, label }) => (
    <button className={"qs-tile" + (tiles[id] ? " on" : "")} data-sim-id={"quick:" + label} onClick={() => setTiles({ ...tiles, [id]: !tiles[id] })}>
      <span className="qs-dot" /> {label}
    </button>
  );
  return (
    <div className="flyout qs" data-sim-id="flyout:quick" onPointerDown={(e) => e.stopPropagation()}>
      <div className="qs-grid">
        <T id="wifi" label="Wi-Fi" /><T id="bt" label="藍牙" /><T id="plane" label="飛航模式" />
        <T id="saver" label="省電模式" /><T id="night" label="夜間模式" /><T id="access" label="協助工具" />
      </div>
      <div className="qs-slider"><span>🔊</span><input type="range" min="0" max="100" value={vol} data-sim-id="quick:volume" onChange={(e) => sys.set({ volume: +e.target.value })} /><span>{vol}</span></div>
      <div className="qs-foot"><span>🔋 100%</span></div>
    </div>
  );
}
