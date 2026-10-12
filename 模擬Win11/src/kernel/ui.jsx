// 共用 UI 服務：對話框、右鍵選單、通知。任何 app 都可以呼叫。
import React from "react";
import { sys } from "./store";
import { emit } from "./events";
import { Ico } from "../shell/icons";

let seq = 0;
const resolvers = new Map();

// 開一個對話框（掛在 ownerId 視窗上，會擋住該視窗）。render(close) 回傳內容；close(value) 結束並回傳 Promise 值。
export function openDialog({ ownerId = null, title = "", width = 420, icon = null, render, kind = "custom", data = {} }) {
  const id = "d" + ++seq;
  const p = new Promise((res) => resolvers.set(id, res));
  sys.set((s) => ({ dialogs: [...s.dialogs, { id, ownerId, title, width, icon, render, kind, data }] }));
  emit("dialog:open", { id, title, kind, ownerId });
  return p;
}
export function closeDialog(id, value) {
  const s = sys.get();
  const d = s.dialogs.find((x) => x.id === id);
  if (!d) return;
  sys.set({ dialogs: s.dialogs.filter((x) => x.id !== id) });
  emit("dialog:close", { id, title: d.title, kind: d.kind, value: typeof value === "object" ? undefined : value });
  const r = resolvers.get(id);
  resolvers.delete(id);
  r && r(value);
}

// 訊息方塊：buttons 為文字陣列（回傳被按的索引）或 [{label,value,primary}]
export function messageBox({ ownerId = null, title = "", text = "", detail = "", icon = "info", buttons = ["確定"], primary = 0, width = 440, kind = "message" }) {
  return openDialog({
    ownerId, title, width, kind, data: { text },
    render: (close) => (
      <div className="msgbox">
        <div className="msgbox-body">
          {icon && <Ico name={icon} size={32} />}
          <div className="msgbox-text">
            <div className="msgbox-main">{text}</div>
            {detail && <div className="msgbox-detail">{detail}</div>}
          </div>
        </div>
        <div className="msgbox-btns">
          {buttons.map((b, i) => {
            const label = typeof b === "string" ? b : b.label;
            const value = typeof b === "string" ? i : b.value ?? i;
            const isPrimary = typeof b === "object" && b.primary !== undefined ? b.primary : i === primary;
            return (
              <button key={i} className={"btn" + (isPrimary ? " primary" : "")} data-sim-id={"dialog:btn:" + label} autoFocus={isPrimary} onClick={() => close(value)}>
                {label}
              </button>
            );
          })}
        </div>
      </div>
    ),
  });
}

export function errorBox(text, opts = {}) { return messageBox({ icon: "error", title: opts.title || "錯誤", text, ...opts }); }

// 右鍵選單。items: [{label, icon, shortcut, onClick, disabled, checked, items:[…子選單], separator:true, iconRow:[{icon,label,onClick,disabled}]}]
export function showContextMenu(x, y, items, { ownerId = null } = {}) {
  sys.set({ contextMenu: { x, y, items, ownerId }, startOpen: false, quickOpen: false, calendarOpen: false, userMenuOpen: false });
  emit("ui:contextmenu", { x, y, labels: items.filter((i) => i.label).map((i) => i.label) });
}
export const hideContextMenu = () => { if (sys.get().contextMenu) sys.set({ contextMenu: null }); };

export function toast({ title = "", text = "", icon = "info", ms = 5000 }) {
  const id = "t" + ++seq;
  sys.set((s) => ({ toasts: [...s.toasts, { id, title, text, icon }] }));
  emit("ui:toast", { title, text });
  setTimeout(() => sys.set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })), ms);
}
