// 虛擬檔案系統：記憶體內的真實樹狀結構，行為比照 Windows 檔案總管。
// 路徑格式 C:\Users\學生\桌面\a.txt（大小寫不分，/ 或 \ 都接受）。所有變更都會 emit fs:* 事件。
import { emit } from "./events";
import { simNow } from "./clock";

export class VfsError extends Error {
  constructor(code, msg, extra = {}) {
    super(msg || code);
    this.code = code;
    Object.assign(this, extra);
  }
}
export const INVALID_CHARS = /[\\/:*?"<>|]/;

let idSeq = 1;
let root = { drives: {} }; // drives: {C: node}
let bin = []; // {id,node,origPath,deletedAt,par}
let rev = 0;
const subs = new Set();
const undoStack = [];
const redoStack = [];

const key = (s) => s.normalize("NFC").toLowerCase();
const mk = (name, type, o = {}) => ({
  id: idSeq++, name, type,
  children: type === "dir" ? [] : undefined,
  content: type === "file" ? "" : undefined,
  size: null, created: simNow(), modified: simNow(), hidden: false, src: null, meta: {}, ...o,
});

export function extOf(name) {
  const i = name.lastIndexOf(".");
  return i > 0 ? name.slice(i + 1).toLowerCase() : "";
}
export function baseOf(name) {
  const i = name.lastIndexOf(".");
  return i > 0 ? name.slice(0, i) : name;
}

export function parse(p) {
  const s = String(p).replace(/\//g, "\\").replace(/\\+$/, "");
  const m = /^([A-Za-z]):(.*)$/.exec(s);
  if (!m) return null;
  return { drive: m[1].toUpperCase(), parts: m[2].split("\\").filter(Boolean) };
}
export function join(...a) {
  const [h, ...r] = a;
  let s = h.replace(/[\\/]+$/, "");
  r.forEach((x) => { s += "\\" + x.replace(/^[\\/]+|[\\/]+$/g, ""); });
  return /^[A-Za-z]:$/.test(s) ? s + "\\" : s;
}
export function dirname(p) {
  const q = parse(p);
  if (!q || !q.parts.length) return null;
  return q.parts.length === 1 ? q.drive + ":\\" : q.drive + ":\\" + q.parts.slice(0, -1).join("\\");
}
export function basename(p) {
  const q = parse(p);
  return q && q.parts.length ? q.parts[q.parts.length - 1] : q ? q.drive + ":" : "";
}
export function norm(p) {
  const q = parse(p);
  if (!q) return p;
  return q.parts.length ? q.drive + ":\\" + q.parts.join("\\") : q.drive + ":\\";
}

function bump() { rev++; subs.forEach((f) => f()); }
export const subscribe = (f) => { subs.add(f); return () => subs.delete(f); };
export const getRev = () => rev;

export function reset(drives = ["C"]) {
  root = { drives: {} };
  drives.forEach((d) => { root.drives[d.toUpperCase()] = mk(d.toUpperCase() + ":", "dir"); });
  bin = [];
  undoStack.length = 0;
  redoStack.length = 0;
  bump();
}

export const drives = () => Object.keys(root.drives);

export function get(p) {
  const q = parse(p);
  if (!q) return null;
  let n = root.drives[q.drive];
  if (!n) return null;
  for (const part of q.parts) {
    if (n.type !== "dir") return null;
    n = n.children.find((c) => key(c.name) === key(part));
    if (!n) return null;
  }
  return n;
}
export const exists = (p) => !!get(p);
export const isDir = (p) => get(p)?.type === "dir";

export function list(p, { hidden = true } = {}) {
  const n = get(p);
  if (!n || n.type !== "dir") return [];
  return n.children.filter((c) => hidden || !c.hidden);
}

export function sizeOf(n) {
  if (n.type === "dir") return n.children.reduce((a, c) => a + sizeOf(c), 0);
  if (n.size != null) return n.size;
  return new TextEncoder().encode(n.content || "").length;
}

export function stat(p) {
  const n = get(p);
  if (!n) return null;
  return { name: n.name, type: n.type, ext: n.type === "file" ? extOf(n.name) : "", size: sizeOf(n), created: n.created, modified: n.modified, hidden: n.hidden, id: n.id, src: n.src };
}

export function readFile(p) {
  const n = get(p);
  if (!n || n.type !== "file") throw new VfsError("not-found", "找不到檔案");
  return n.content ?? "";
}

export function validateName(name) {
  const t = name.replace(/[ .]+$/, "").replace(/^ +/, "");
  if (!t) return { ok: false, code: "empty" };
  if (INVALID_CHARS.test(t)) return { ok: false, code: "invalid" };
  return { ok: true, name: t };
}

// 自動編號：新增資料夾、新增資料夾 (2)…；style:'copy' 則是「a - 複製.txt」
export function uniqueName(dir, name, style = "num") {
  const d = get(dir);
  if (!d) return name;
  const taken = (n) => d.children.some((c) => key(c.name) === key(n));
  if (!taken(name)) return name;
  const base = baseOf(name), ext = name.slice(base.length);
  if (style === "copy") {
    let n = `${base} - 複製${ext}`;
    if (!taken(n)) return n;
    for (let i = 2; ; i++) { n = `${base} - 複製 (${i})${ext}`; if (!taken(n)) return n; }
  }
  for (let i = 2; ; i++) { const n = `${base} (${i})${ext}`; if (!taken(n)) return n; }
}

function pushUndo(label, undoFn, redoFn) {
  undoStack.push({ label, undo: undoFn, redo: redoFn });
  redoStack.length = 0;
  if (undoStack.length > 100) undoStack.shift();
}
export function undo() {
  const e = undoStack.pop();
  if (!e) return false;
  e.undo(); redoStack.push(e); bump(); emit("fs:undo", { label: e.label });
  return true;
}
export function redo() {
  const e = redoStack.pop();
  if (!e) return false;
  e.redo(); undoStack.push(e); bump(); emit("fs:redo", { label: e.label });
  return true;
}
export const canUndo = () => undoStack.length > 0;

function detach(p) {
  const par = get(dirname(p));
  const n = get(p);
  par.children.splice(par.children.indexOf(n), 1);
  return { par, n };
}
function cloneNode(n, name) {
  const c = { ...n, id: idSeq++, name: name ?? n.name, created: simNow(), meta: { ...n.meta } };
  if (n.type === "dir") c.children = n.children.map((k) => cloneNode(k));
  return c;
}

export function mkdir(path, { silent = false, parents = false } = {}) {
  const q = parse(path);
  if (!q) throw new VfsError("invalid-path");
  let cur = root.drives[q.drive];
  if (!cur) throw new VfsError("not-found", "找不到磁碟機");
  let created = null;
  q.parts.forEach((part, i) => {
    let nx = cur.children.find((c) => key(c.name) === key(part));
    if (!nx) {
      if (i < q.parts.length - 1 && !parents) throw new VfsError("not-found", "找不到路徑");
      nx = mk(part, "dir");
      cur.children.push(nx);
      created = created || nx;
    } else if (nx.type !== "dir") throw new VfsError("exists", "已有同名檔案");
    cur = nx;
  });
  if (!silent && created) { bump(); emit("fs:create", { path: norm(path), kind: "dir" }); }
  return norm(path);
}

// 在 dir 底下新增檔案/資料夾；auto=true 時名稱重複會自動編號。回傳新路徑。
export function create(dir, name, type = "file", { content = "", size = null, src = null, silent = false, hidden = false, modified = null, auto = true } = {}) {
  const d = get(dir);
  if (!d || d.type !== "dir") throw new VfsError("not-found", "找不到資料夾");
  const v = validateName(name);
  if (!v.ok) throw new VfsError("invalid-name", "檔名無效", { reason: v.code });
  const nm = auto ? uniqueName(dir, v.name) : v.name;
  if (!auto && d.children.some((c) => key(c.name) === key(nm))) throw new VfsError("exists", "已存在", { name: nm });
  const n = mk(nm, type, { content: type === "file" ? content : undefined, size, src, hidden });
  if (modified) { n.modified = modified; n.created = modified; }
  d.children.push(n);
  const path = join(dir, nm);
  if (!silent) {
    pushUndo("新增", () => { detach(path); }, () => { get(dir).children.push(n); });
    bump();
    emit("fs:create", { path, kind: type, name: nm });
  }
  return path;
}

export function writeFile(path, content, { silent = false } = {}) {
  const n = get(path);
  if (!n || n.type !== "file") throw new VfsError("not-found");
  n.content = content;
  n.size = null;
  n.modified = simNow();
  if (!silent) { bump(); emit("fs:write", { path: norm(path), length: content.length }); }
}

// 另存新檔：存在就覆寫，不存在就建立
export function saveFile(path, content) {
  if (exists(path)) { writeFile(path, content); return norm(path); }
  create(dirname(path), basename(path), "file", { content, auto: false });
  return norm(path);
}

export function rename(path, newName) {
  const n = get(path);
  if (!n) throw new VfsError("not-found");
  const v = validateName(newName);
  if (!v.ok) throw new VfsError("invalid-name", "檔名無效", { reason: v.code });
  if (v.name === n.name) return norm(path);
  const dir = dirname(path), par = get(dir);
  if (par.children.some((c) => c !== n && key(c.name) === key(v.name))) throw new VfsError("exists", "名稱已存在", { name: v.name });
  const old = n.name;
  n.name = v.name;
  const np = join(dir, v.name);
  pushUndo("重新命名", () => { n.name = old; }, () => { n.name = v.name; });
  bump();
  emit("fs:rename", { from: norm(path), to: np, oldName: old, newName: v.name });
  return np;
}

// 目的地已有同名項目的名稱清單（用來決定要不要跳「取代或略過」）
export function conflicts(srcs, destDir) {
  const d = get(destDir);
  if (!d) return [];
  return srcs.filter((s) => {
    const b = basename(s);
    return d.children.some((c) => key(c.name) === key(b) && c !== get(s));
  }).map(basename);
}
function isInside(dir, candidate) {
  const a = key(norm(dir)) + "\\", b = key(norm(candidate)) + "\\";
  return b.startsWith(a);
}

// policy: 'keep-both' | 'replace' | 'skip'
export function copy(srcs, destDir, { policy = "keep-both", silent = false } = {}) {
  const d = get(destDir);
  if (!d || d.type !== "dir") throw new VfsError("not-found");
  const out = [], undos = [];
  srcs.forEach((s) => {
    const n = get(s);
    if (!n) return;
    if (n.type === "dir" && isInside(s, destDir)) throw new VfsError("into-self", "無法複製到自己的子資料夾");
    const b = basename(s);
    const clash = d.children.find((c) => key(c.name) === key(b));
    let name = b;
    if (clash) {
      if (policy === "skip") return;
      if (policy === "replace" && clash !== n) { d.children.splice(d.children.indexOf(clash), 1); undos.push(() => d.children.push(clash)); }
      else name = uniqueName(destDir, b, "copy");
    }
    const c = cloneNode(n, name);
    d.children.push(c);
    undos.push(() => d.children.splice(d.children.indexOf(c), 1));
    out.push(join(destDir, name));
  });
  if (!silent && out.length) {
    pushUndo("複製", () => undos.slice().reverse().forEach((f) => f()), () => {});
    bump();
    emit("fs:copy", { from: srcs.map(norm), to: out, destDir: norm(destDir) });
  }
  return out;
}

export function move(srcs, destDir, { policy = "keep-both", silent = false } = {}) {
  const d = get(destDir);
  if (!d || d.type !== "dir") throw new VfsError("not-found");
  const out = [], undos = [];
  srcs.forEach((s) => {
    const n = get(s);
    if (!n) return;
    if (n.type === "dir" && isInside(s, destDir)) throw new VfsError("into-self", "無法移動到自己的子資料夾");
    if (key(norm(dirname(s))) === key(norm(destDir))) { out.push(norm(s)); return; } // 同資料夾：不動
    const clash = d.children.find((c) => key(c.name) === key(n.name));
    let name = n.name;
    if (clash) {
      if (policy === "skip") return;
      if (policy === "replace") { d.children.splice(d.children.indexOf(clash), 1); undos.push(() => d.children.push(clash)); }
      else name = uniqueName(destDir, n.name);
    }
    const { par } = detach(s);
    const oldName = n.name;
    n.name = name;
    d.children.push(n);
    undos.push(() => { d.children.splice(d.children.indexOf(n), 1); n.name = oldName; par.children.push(n); });
    out.push(join(destDir, name));
  });
  if (!silent && out.length) {
    pushUndo("移動", () => undos.slice().reverse().forEach((f) => f()), () => {});
    bump();
    emit("fs:move", { from: srcs.map(norm), to: out, destDir: norm(destDir) });
  }
  return out;
}

// 刪除到資源回收筒
export function trash(paths, { silent = false } = {}) {
  const items = [];
  paths.forEach((p) => {
    const n = get(p);
    if (!n || !dirname(p)) return;
    const { par } = detach(p);
    items.push({ id: idSeq++, node: n, origPath: norm(p), deletedAt: simNow(), par });
    bin.push(items[items.length - 1]);
  });
  if (!silent && items.length) {
    pushUndo("刪除", () => items.forEach((it) => { bin.splice(bin.indexOf(it), 1); (get(dirname(it.origPath)) || it.par).children.push(it.node); }), () => {});
    bump();
    emit("fs:delete", { paths: items.map((i) => i.origPath), toBin: true });
  }
  return items.map((i) => i.id);
}
export function deleteForever(paths) {
  const done = [];
  paths.forEach((p) => {
    const n = get(p);
    if (n && dirname(p)) { detach(p); done.push(norm(p)); }
  });
  if (done.length) { bump(); emit("fs:delete", { paths: done, toBin: false }); }
}
export const binItems = () => bin.slice();
export const binCount = () => bin.length;

export function restore(ids) {
  const out = [];
  ids.forEach((id) => {
    const it = bin.find((b) => b.id === id);
    if (!it) return;
    const dir = dirname(it.origPath);
    if (!get(dir)) mkdir(dir, { parents: true, silent: true }); // 原資料夾不在了：重建
    const d = get(dir);
    let name = it.node.name;
    if (d.children.some((c) => key(c.name) === key(name))) name = uniqueName(dir, name);
    it.node.name = name;
    d.children.push(it.node);
    bin.splice(bin.indexOf(it), 1);
    out.push(join(dir, name));
  });
  if (out.length) { bump(); emit("fs:restore", { paths: out }); }
  return out;
}
export function deleteFromBin(ids) {
  const before = bin.length;
  bin = bin.filter((b) => !ids.includes(b.id));
  if (bin.length !== before) { bump(); emit("fs:delete", { binIds: ids, toBin: false, fromBin: true }); }
}
export function emptyBin() {
  const n = bin.length;
  bin = [];
  if (n) { bump(); emit("fs:emptyBin", { count: n }); }
}

// ---- 場景載入／匯出 ----
// spec: [{path, type?:'dir'|'file', content?, size?, src?, hidden?, modified?}]；上層資料夾自動建立。
export function loadSpec(list = []) {
  list.forEach((it) => {
    const type = it.type || (/\.[A-Za-z0-9]{1,6}$/.test(it.path) ? "file" : "dir");
    if (type === "dir") {
      mkdir(it.path, { silent: true, parents: true });
      if (it.hidden) get(it.path).hidden = true;
      return;
    }
    const dir = dirname(it.path);
    mkdir(dir, { silent: true, parents: true });
    create(dir, basename(it.path), "file", {
      content: it.content ?? "", size: it.size ?? null, src: it.src ?? null, silent: true,
      hidden: !!it.hidden, modified: it.modified ? new Date(it.modified).getTime() : null, auto: false,
    });
  });
  bump();
}

export function snapshot({ maxContent = 200 } = {}) {
  const out = [];
  const walk = (n, path) => {
    n.children.forEach((c) => {
      const p = path + "\\" + c.name;
      out.push({
        path: p, type: c.type, size: sizeOf(c), modified: new Date(c.modified).toISOString(),
        ...(c.hidden ? { hidden: true } : {}),
        ...(c.type === "file" && c.content ? { content: c.content.length > maxContent ? c.content.slice(0, maxContent) + "…" : c.content } : {}),
      });
      if (c.type === "dir") walk(c, p);
    });
  };
  Object.entries(root.drives).forEach(([d, n]) => walk(n, d + ":"));
  return { files: out, bin: bin.map((b) => ({ id: b.id, name: b.node.name, origPath: b.origPath })) };
}

const KIND = {
  txt: "文字文件", md: "Markdown 檔案", docx: "Microsoft Word 文件", doc: "Microsoft Word 97-2003 文件",
  xlsx: "Microsoft Excel 工作表", pptx: "Microsoft PowerPoint 簡報", pdf: "PDF 文件", png: "PNG 檔案",
  jpg: "JPG 檔案", jpeg: "JPEG 檔案", gif: "GIF 檔案", svg: "SVG 檔案", mp3: "MP3 檔案", mp4: "MP4 檔案",
  zip: "壓縮的 (zipped) 資料夾", html: "HTML 文件", csv: "Microsoft Excel 逗號分隔值檔案", lnk: "捷徑", exe: "應用程式",
};
export function kindOf(name, type) {
  if (type === "dir") return "檔案資料夾";
  const e = extOf(name);
  return KIND[e] || (e ? e.toUpperCase() + " 檔案" : "檔案");
}

// 副檔名是否為「已知類型」（Windows 只會隱藏已知類型的副檔名）
export const isKnownExt = (e) => !!KIND[e];
// 檔案在清單裡顯示的名稱：showExt=false 時，已知副檔名會被隱藏
export function displayName(name, type, showExt) {
  if (type === "dir" || showExt) return name;
  const e = extOf(name);
  return e && isKnownExt(e) ? baseOf(name) : name;
}
