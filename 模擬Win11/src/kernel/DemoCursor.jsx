import React from "react";
import { useSys } from "./store";

// 示範游標（假滑鼠）與錄影字卡。cursor.visible 為 true 時才顯示；不會攔截任何點擊。
export default function DemoCursor() {
  const c = useSys((s) => s.cursor);
  const cap = useSys((s) => s.caption);
  return (
    <>
      {c.visible && (
        <div className={"demo-cursor" + (c.pressed ? " pressed" : "")} style={{ transform: `translate(${c.x}px, ${c.y}px)`, transition: c.ms ? `transform ${c.ms}ms cubic-bezier(.4,0,.2,1)` : "none" }}>
          <svg width="26" height="30" viewBox="0 0 26 30"><path d="M3 2l17 16-7.5.8 4.2 8.4-3.4 1.7-4.2-8.4L3 26z" fill="#fff" stroke="#000" strokeWidth="1.6" strokeLinejoin="round" /></svg>
          <span className="demo-ring" />
        </div>
      )}
      {cap && (
        <div className="demo-caption" data-sim-id="caption"><div className="demo-caption-main">{cap.text}</div>{cap.sub && <div className="demo-caption-sub">{cap.sub}</div>}</div>
      )}
    </>
  );
}
