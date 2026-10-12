import { sys } from "./store";

// 模擬時鐘：scene.clock 設固定起點時會從該時間開始走（錄影／截圖畫面才會每次一樣）
export function simNow() {
  const s = sys.get();
  if (!s.clockBase) return Date.now();
  return new Date(s.clockBase).getTime() + (performance.now() - s.clockStart);
}

export function setClock(iso) {
  sys.set({ clockBase: iso || null, clockStart: performance.now() });
}
