import { useSyncExternalStore } from "react";
import * as vfs from "../kernel/vfs";
import { sys } from "../kernel/store";
import { simNow } from "../kernel/clock";
import { useEffect, useState } from "react";

// 檔案系統有變動就重新渲染；回傳版本號
export const useVfs = () => useSyncExternalStore(vfs.subscribe, vfs.getRev);

// 模擬時鐘（每秒更新）
export function useClock() {
  const [t, setT] = useState(simNow());
  useEffect(() => { const id = setInterval(() => setT(simNow()), 1000); return () => clearInterval(id); }, []);
  return new Date(t);
}
export { sys };
