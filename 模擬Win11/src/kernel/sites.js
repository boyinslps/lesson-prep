// 瀏覽器的「網站」來源。三種：
//  1) scene.sites 裡的靜態網頁 {"https://x.com/a": {title, html}}（最簡單，AI 寫關卡時用這個）
//  2) registerSite() 註冊的動態網站（例如未來的 Google 搜尋模擬、Google 文件模擬）
//  3) 內建頁面：edge://newtab、about:blank、搜尋結果、找不到網頁
import { sys } from "./store";

const handlers = []; // {id, match(url)->bool, resolve(url)->{title, html?, component?}}

// 註冊動態網站。resolve 回傳 {title, html} 或 {title, component: ReactComponent}（component 會收到 {url, nav}）
export function registerSite(def) { handlers.push(def); return def; }

export function normalizeUrl(input) {
  const t = (input || "").trim();
  if (!t) return "edge://newtab";
  if (/^(about:|edge:|data:)/i.test(t)) return t;
  if (/^https?:\/\//i.test(t)) return t;
  if (/^[^\s]+\.[A-Za-z]{2,}([/?#].*)?$/.test(t) || /^localhost/.test(t)) return "https://" + t;
  return "https://www.bing.com/search?q=" + encodeURIComponent(t);
}
const strip = (u) => u.replace(/#.*$/, "").replace(/\/+$/, "").toLowerCase();

export function resolveSite(url) {
  if (url === "edge://newtab") return { title: "新索引標籤", kind: "newtab" };
  if (url === "about:blank") return { title: "about:blank", html: "<html><body></body></html>" };
  const sites = sys.get().sites || {};
  const key = Object.keys(sites).find((k) => strip(k) === strip(url));
  if (key) return { title: sites[key].title || key, html: sites[key].html || "", url: key };
  for (const h of handlers) if (h.match(url)) return h.resolve(url);
  const m = /^https?:\/\/www\.bing\.com\/search\?q=([^&]*)/i.exec(url);
  if (m) return searchPage(decodeURIComponent(m[1].replace(/\+/g, " ")));
  return {
    title: "無法連上這個網站",
    html: `<html><body style="font-family:Segoe UI,sans-serif;padding:60px;color:#333"><div style="font-size:64px">:(</div><h2>無法連上這個網站</h2><p>找不到 <b>${url.replace(/^https?:\/\//, "").split("/")[0]}</b> 的伺服器 IP 位址。</p><p style="color:#888">ERR_NAME_NOT_RESOLVED</p></body></html>`,
  };
}

function searchPage(q) {
  const sites = sys.get().sites || {};
  const ql = q.toLowerCase();
  const hits = Object.entries(sites).filter(([u, s]) => (s.title || "").toLowerCase().includes(ql) || (s.description || "").toLowerCase().includes(ql) || u.toLowerCase().includes(ql));
  const list = hits.length
    ? hits.map(([u, s]) => `<div style="margin:18px 0"><div style="color:#555;font-size:12px">${u}</div><a href="${u}" style="font-size:18px;color:#1a0dab;text-decoration:none">${s.title || u}</a><div style="color:#444;font-size:13px">${s.description || ""}</div></div>`).join("")
    : `<p style="color:#666">找不到與「${q}」相符的結果。</p>`;
  return { title: `${q} - 搜尋`, html: `<html><body style="font-family:Segoe UI,sans-serif;margin:0"><div style="padding:14px 28px;border-bottom:1px solid #ddd;display:flex;gap:16px;align-items:center"><b style="font-size:20px;color:#0b6">搜尋</b><div style="border:1px solid #bbb;border-radius:20px;padding:6px 16px;min-width:300px">${q}</div></div><div style="padding:8px 28px;max-width:720px">${list}</div></body></html>` };
}
