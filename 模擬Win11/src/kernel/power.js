// 電源與登入狀態：睡眠／關機／重新啟動／登出／鎖定。phase 轉換都會 emit sys:* 事件。
// phase: off | booting | restarting | sleep | lock | login | desktop
import { sys } from "./store";
import { emit } from "./events";
import { closeAll } from "./wm";

const bootDelay = () => (sys.get().settings.fastBoot ? 50 : 1800);

export function sleep() {
  sys.set({ phase: "sleep", startOpen: false, userMenuOpen: false, contextMenu: null });
  emit("sys:sleep");
}
export function wake() {
  if (sys.get().phase !== "sleep") return;
  sys.set({ phase: "lock" });
  emit("sys:wake");
}
export function shutdown() {
  closeAll();
  sys.set({ phase: "off", startOpen: false, userMenuOpen: false, contextMenu: null });
  emit("sys:shutdown");
}
export function powerOn() {
  if (sys.get().phase !== "off") return;
  sys.set({ phase: "booting" });
  emit("sys:boot");
  setTimeout(() => { sys.set({ phase: "lock" }); }, bootDelay());
}
export function restart() {
  closeAll();
  sys.set({ phase: "restarting", startOpen: false, userMenuOpen: false, contextMenu: null });
  emit("sys:restart");
  setTimeout(() => { sys.set({ phase: "booting" }); setTimeout(() => sys.set({ phase: "lock" }), bootDelay()); }, bootDelay() + 600);
}
export function lock() {
  sys.set({ phase: "lock", startOpen: false, userMenuOpen: false, contextMenu: null });
  emit("sys:lock");
}
export function signOut() {
  closeAll();
  sys.set({ phase: "login", startOpen: false, userMenuOpen: false, contextMenu: null });
  emit("sys:signout");
}
export function unlockToLogin() { sys.set({ phase: "login" }); }
export function login(password = "") {
  const u = sys.get().user;
  if (u.password && password !== u.password) { emit("sys:loginFailed"); return false; }
  sys.set({ phase: "desktop" });
  emit("sys:login", { user: u.name });
  return true;
}
