import React, { useState } from "react";
import { useSys } from "../kernel/store";
import { closeDialog } from "../kernel/ui";
import { Ico } from "./icons";
import { desktopArea } from "../kernel/wm";

function DialogFrame({ d }) {
  const owner = useSys((s) => s.windows.find((w) => w.id === d.ownerId));
  const D = desktopArea();
  const base = owner && owner.state !== "max" ? owner.rect : { x: 0, y: 0, w: D.w, h: D.h };
  const [off, setOff] = useState({ x: 0, y: 0 });
  const z = (owner ? owner.z : 9000) + 5000;
  const close = (v) => closeDialog(d.id, v);
  const start = (e) => {
    if (e.target.closest("button")) return;
    const sx = e.clientX - off.x, sy = e.clientY - off.y;
    const mv = (ev) => setOff({ x: ev.clientX - sx, y: ev.clientY - sy });
    const up = () => { window.removeEventListener("pointermove", mv, true); window.removeEventListener("pointerup", up, true); };
    window.addEventListener("pointermove", mv, true);
    window.addEventListener("pointerup", up, true);
  };
  return (
    <div className="dlg-wrap" style={{ zIndex: z }}>
      {!owner && <div className="dlg-dim" />}
      <div className="dlg" role="dialog" data-sim-id={"dialog:" + d.kind} data-title={d.title}
        style={{ width: d.width, left: base.x + base.w / 2 - d.width / 2 + off.x, top: Math.max(8, base.y + base.h / 3 - 80 + off.y) }}>
        <div className="dlg-title" onPointerDown={start}>
          <span>{d.title}</span>
          <button className="win-ctl close" aria-label="關閉" data-sim-id="dialog:close" onClick={() => close(undefined)}>
            <svg width="10" height="10" viewBox="0 0 10 10"><path d="M0 0l10 10M10 0L0 10" stroke="currentColor" /></svg>
          </button>
        </div>
        <div className="dlg-body">{d.render(close)}</div>
      </div>
    </div>
  );
}

export default function DialogLayer() {
  const dialogs = useSys((s) => s.dialogs);
  return <>{dialogs.map((d) => <DialogFrame key={d.id} d={d} />)}</>;
}
