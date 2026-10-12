import { createContext, useContext, useEffect, useRef } from "react";
import { registerGuard, closeWindow, setTitle, openApp, focusWindow } from "../kernel/wm";
import { openDialog, messageBox } from "../kernel/ui";

export const WinCtx = createContext(null);

// App 元件內用：const win = useWin(); win.args / win.setTitle("…") / win.close() / win.guard(async()=>true) / win.messageBox({…})
export function useWin() {
  const w = useContext(WinCtx);
  return {
    id: w.id,
    args: w.args,
    win: w,
    setTitle: (t) => setTitle(w.id, t),
    close: (force) => closeWindow(w.id, { force }),
    focus: () => focusWindow(w.id),
    openApp,
    openDialog: (o) => openDialog({ ownerId: w.id, ...o }),
    messageBox: (o) => messageBox({ ownerId: w.id, ...o }),
  };
}

// 關閉前攔截（例如記事本未存檔）：useCloseGuard(async () => 是否允許關閉)
export function useCloseGuard(fn) {
  const w = useContext(WinCtx);
  const ref = useRef(fn);
  ref.current = fn;
  useEffect(() => registerGuard(w.id, () => ref.current()), [w.id]);
}
