// 線上文件（仿 Google 文件）的資料：sys.docs[id] = {title, html, share:{people:[], access}}
// 場景用 scene.docs 預先放文件；網址 https://docs.google.com/document/d/<id>/edit 會開啟它。
import { sys } from "./store";
import { emit } from "./events";

let seq = 0;
export const docUrl = (id) => `https://docs.google.com/document/d/${id}/edit`;
export const docIdOf = (url) => (/^https:\/\/docs\.google\.com\/document\/d\/([^/?#]+)/.exec(url) || [])[1] || null;
export const getDoc = (id) => sys.get().docs[id] || null;

export function setDocs(map) {
  const docs = {};
  Object.entries(map || {}).forEach(([id, d]) => { docs[id] = { title: d.title || "未命名文件", html: d.html || "<p><br></p>", share: { people: [], access: "restricted", ...(d.share || {}) } }; });
  sys.set({ docs });
}
export function ensureDoc(id) {
  if (!getDoc(id)) sys.set((s) => ({ docs: { ...s.docs, [id]: { title: "未命名文件", html: "<p><br></p>", share: { people: [], access: "restricted" } } } }));
  return getDoc(id);
}
export function createDoc(init = {}) {
  const id = "doc" + Date.now().toString(36) + ++seq;
  sys.set((s) => ({ docs: { ...s.docs, [id]: { title: "未命名文件", html: "<p><br></p>", share: { people: [], access: "restricted" }, ...init } } }));
  emit("app:gdocs:create", { id });
  return id;
}
export function patchDoc(id, patch) {
  sys.set((s) => (s.docs[id] ? { docs: { ...s.docs, [id]: { ...s.docs[id], ...patch } } } : null));
}

// 把文件 HTML 分析成容易判定的資料（關卡用）
export function analyze(html) {
  const doc = new DOMParser().parseFromString("<body>" + html + "</body>", "text/html");
  const b = doc.body;
  const q = (sel) => Array.from(b.querySelectorAll(sel));
  const styleOf = (el, prop) => el.style && el.style[prop];
  const colors = new Set(), fonts = new Set(), sizes = new Set();
  q("font[color]").forEach((e) => colors.add(e.getAttribute("color").toLowerCase()));
  q("[style*='color']").forEach((e) => { const c = styleOf(e, "color"); if (c) colors.add(c.toLowerCase()); });
  q("font[face]").forEach((e) => fonts.add(e.getAttribute("face")));
  q("[style*='font-family']").forEach((e) => fonts.add(styleOf(e, "fontFamily").replace(/["']/g, "")));
  q("[style*='font-size']").forEach((e) => sizes.add(parseFloat(styleOf(e, "fontSize"))));
  const align = new Set();
  q("[style*='text-align'],[align]").forEach((e) => align.add(styleOf(e, "textAlign") || e.getAttribute("align")));
  return {
    text: b.innerText || b.textContent || "",
    bold: q("b,strong,[style*='font-weight']").length > 0,
    italic: q("i,em").length > 0,
    underline: q("u").length > 0,
    colors: [...colors], fonts: [...fonts], sizes: [...sizes], align: [...align],
    headings: q("h1,h2,h3").map((e) => ({ level: +e.tagName[1], text: e.textContent })),
    links: q("a[href]").map((e) => ({ href: e.getAttribute("href"), text: e.textContent })),
    bullets: q("ul li").length, numbered: q("ol li").length,
  };
}
export function getDocInfo(id) {
  const d = getDoc(id);
  return d && { id, title: d.title, html: d.html, share: d.share, ...analyze(d.html) };
}
