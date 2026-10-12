import React, { useState, useLayoutEffect, useRef } from "react";
import { useSys } from "../kernel/store";
import { hideContextMenu } from "../kernel/ui";
import { Ico } from "./icons";

function Menu({ items, x, y, depth = 0 }) {
  const ref = useRef(null);
  const [pos, setPos] = useState({ x, y });
  const [flip, setFlip] = useState({ left: false, dy: 0 });
  const [open, setOpen] = useState(null);
  useLayoutEffect(() => {
    const r = ref.current.getBoundingClientRect();
    if (depth) { // 子選單：用絕對定位貼在父項目右側，放不下就翻到左側、超出底部就往上移
      const parent = ref.current.parentElement.getBoundingClientRect();
      setFlip({ left: parent.right - 4 + r.width > window.innerWidth - 4, dy: Math.min(0, window.innerHeight - 52 - (parent.top - 5 + r.height)) });
      return;
    }
    let nx = x, ny = y;
    if (nx + r.width > window.innerWidth - 4) nx = window.innerWidth - r.width - 4;
    if (ny + r.height > window.innerHeight - 52) ny = Math.max(4, window.innerHeight - 52 - r.height);
    setPos({ x: nx, y: ny });
  }, [x, y, depth, items]);

  return (
    <div ref={ref} className={"ctx" + (depth ? " nested" : "")} style={depth ? (flip.left ? { right: "calc(100% - 4px)", top: -5 + flip.dy } : { left: "calc(100% - 4px)", top: -5 + flip.dy }) : { left: pos.x, top: pos.y }} role="menu" data-sim-id={depth ? "ctx:submenu" : "ctx:menu"} onContextMenu={(e) => e.preventDefault()} onPointerDown={(e) => e.stopPropagation()}>
      {items.map((it, i) => {
        if (it.separator) return <div key={i} className="ctx-sep" />;
        if (it.iconRow) {
          return (
            <div key={i} className="ctx-iconrow">
              {it.iconRow.map((b, j) => (
                <button key={j} className="ctx-iconbtn" disabled={b.disabled} title={b.label} data-sim-id={"ctx:" + b.label} onClick={() => { if (b.disabled) return; hideContextMenu(); b.onClick && b.onClick(); }}>
                  <Ico name={b.icon} size={18} />
                </button>
              ))}
            </div>
          );
        }
        const has = !!it.items;
        return (
          <div
            key={i}
            className={"ctx-item" + (it.disabled ? " disabled" : "") + (open === i ? " open" : "")}
            data-sim-id={"ctx:" + it.label}
            onMouseEnter={(e) => setOpen(has ? i : null)}
            onClick={(e) => {
              if (it.disabled) return;
              if (has) { setOpen(i); return; }
              hideContextMenu();
              it.onClick && it.onClick();
            }}
          >
            <span className="ctx-ico">{it.checked ? "✓" : it.icon ? <Ico name={it.icon} size={16} /> : null}</span>
            <span className="ctx-label">{it.label}</span>
            {it.shortcut && <span className="ctx-short">{it.shortcut}</span>}
            {has && <span className="ctx-arrow">›</span>}
            {has && open === i && <Menu items={it.items} depth={1} />}
          </div>
        );
      })}
    </div>
  );
}

export default function ContextMenuLayer() {
  const cm = useSys((s) => s.contextMenu);
  if (!cm) return null;
  return (
    <>
      <div className="ctx-backdrop" onPointerDown={hideContextMenu} onContextMenu={(e) => { e.preventDefault(); hideContextMenu(); }} />
      <Menu items={cm.items} x={cm.x} y={cm.y} />
    </>
  );
}
