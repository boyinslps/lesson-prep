// 讓 App 把「目前的內部狀態」交給 Win11Sim.snapshot()（AI 與關卡判定用）。
// App 內：useExposeState(() => ({ path, selection }))
import { useContext, useEffect, useRef } from "react";
import { WinCtx } from "../shell/WinContext";

const getters = new Map(); // windowId -> () => object
export const appStateOf = (id) => { try { return getters.get(id)?.() ?? null; } catch (e) { return null; } };

export function useExposeState(fn) {
  const w = useContext(WinCtx);
  const ref = useRef(fn);
  ref.current = fn;
  useEffect(() => { getters.set(w.id, () => ref.current()); return () => getters.delete(w.id); }, [w.id]);
}
