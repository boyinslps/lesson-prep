// 事件匯流排＋事件紀錄。關卡判定、AI 觀察操作都靠它。
// type 命名：fs:create / fs:rename / fs:move / fs:copy / fs:delete / fs:restore / fs:write / fs:emptyBin
//            win:open / win:close / win:focus / win:minimize / win:maximize / win:restore
//            app:<id>:<事件>（各 app 自訂）  ui:contextmenu / ui:key / ui:click …  sys:*（登入、關機等）
const listeners = new Map(); // type -> Set(fn)；'*' 代表全部
export const log = [];
let seq = 0;

export function emit(type, data = {}) {
  const entry = { seq: ++seq, t: Date.now(), type, data };
  log.push(entry);
  if (log.length > 2000) log.shift();
  [type, "*"].forEach((k) => listeners.get(k)?.forEach((f) => { try { f(entry); } catch (e) { console.error(e); } }));
  // 前綴訂閱：on('fs:*')
  const idx = type.indexOf(":");
  if (idx > 0) listeners.get(type.slice(0, idx) + ":*")?.forEach((f) => { try { f(entry); } catch (e) { console.error(e); } });
  return entry;
}

export function on(type, fn) {
  if (!listeners.has(type)) listeners.set(type, new Set());
  listeners.get(type).add(fn);
  return () => listeners.get(type)?.delete(fn);
}

export function clearLog() { log.length = 0; }

// 等到某事件出現（可附條件）。回傳 Promise<entry>，逾時 reject。
export function waitFor(type, pred = () => true, timeout = 10000) {
  const past = log.find((e) => (type === "*" || e.type === type || (type.endsWith(":*") && e.type.startsWith(type.slice(0, -1)))) && pred(e));
  if (past) return Promise.resolve(past);
  return new Promise((res, rej) => {
    const off = on(type, (e) => { if (pred(e)) { off(); clearTimeout(t); res(e); } });
    const t = setTimeout(() => { off(); rej(new Error("waitFor timeout: " + type)); }, timeout);
  });
}
