// 瀏覽器（Edge 風格）：分頁、網址列、上下頁、重新整理、縮放、尋找、下載。
// 網頁內容來自 scene.sites 或 registerSite()（見 kernel/sites.js），用 sandbox iframe 顯示。
import React, { useEffect, useRef, useState } from "react";
import { FiArrowLeft, FiArrowRight, FiRefreshCw, FiHome, FiStar, FiMoreHorizontal, FiX, FiPlus, FiDownload, FiSearch, FiLock } from "react-icons/fi";
import { sys, useSys } from "../kernel/store";
import * as vfs from "../kernel/vfs";
import { known } from "../kernel/paths";
import { openApp, openPath } from "../kernel/wm";
import { normalizeUrl, resolveSite } from "../kernel/sites";
import { emit } from "../kernel/events";
import { toast } from "../kernel/ui";
import { Ico } from "../shell/icons";
import { useWin } from "../shell/WinContext";
import { useExposeState } from "../kernel/appstate";

const ZOOMS = [25, 33, 50, 67, 75, 80, 90, 100, 110, 125, 150, 175, 200, 250, 300, 400, 500];
let tabSeq = 0;
const newTab = (url = "edge://newtab") => ({ id: ++tabSeq, hist: [url], hi: 0, zoom: 100, title: "", reloads: 0 });

const BRIDGE = `<script>document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a');if(!a)return;
if(a.hasAttribute('download')||a.dataset.simDownload){e.preventDefault();parent.postMessage({sim:'download',name:a.dataset.simDownload||a.getAttribute('download')||'download',content:a.dataset.content||null,href:a.getAttribute('href')},'*');return}
var h=a.getAttribute('href');if(h&&h.charAt(0)!=='#'&&h.indexOf('javascript:')!==0){e.preventDefault();parent.postMessage({sim:'nav',href:h,blank:a.target==='_blank'},'*')}});
document.addEventListener('contextmenu',function(e){e.preventDefault()});<\/script>`;

function strippedText(html) { return (html || "").replace(/<script[\s\S]*?<\/script>/g, "").replace(/<style[\s\S]*?<\/style>/g, "").replace(/<[^>]+>/g, " "); }

function NewTabPage({ go }) {
  const [q, setQ] = useState("");
  return (
    <div className="edge-newtab">
      <div className="nt-logo">搜尋網路</div>
      <div className="nt-box"><FiSearch /><input data-sim-id="edge:newtab:search" autoFocus value={q} placeholder="搜尋網路或輸入網址" onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => { if (!e.ctrlKey && !e.metaKey && !e.altKey) e.stopPropagation(); if (e.key === "Enter") go(q); }} /></div>
    </div>
  );
}

export default function Browser() {
  const w = useWin();
  useSys((s) => s.docs); // 線上文件改名時分頁標題要跟著變
  const [tabs, setTabs] = useState(() => [newTab(w.args.url ? normalizeUrl(w.args.url) : "edge://newtab")]);
  const [cur, setCur] = useState(tabs[0].id);
  const [closed, setClosed] = useState([]);
  const [addr, setAddr] = useState(null);
  const [find, setFind] = useState(null); // {term}
  const [downloads, setDownloads] = useState([]);
  const [dlOpen, setDlOpen] = useState(false);
  const frames = useRef({});
  const root = useRef(null);
  const sid = (n) => `edge:${w.id}:${n}`;

  const tab = tabs.find((t) => t.id === cur) || tabs[0];
  useExposeState(() => ({ tabs: tabs.map((t) => ({ url: t.hist[t.hi], zoom: t.zoom, active: t.id === cur })), downloads, find }));
  const url = tab.hist[tab.hi];
  const site = resolveSite(url);
  const patch = (id, p) => setTabs((ts) => ts.map((t) => (t.id === id ? { ...t, ...(typeof p === "function" ? p(t) : p) } : t)));

  useEffect(() => { w.setTitle(`${site.title || "新索引標籤"} - Microsoft Edge`); }, [url, tab.id, site.title]); // eslint-disable-line

  const go = (input, id = cur) => {
    const u = normalizeUrl(input);
    patch(id, (t) => ({ hist: [...t.hist.slice(0, t.hi + 1), u], hi: t.hi + 1, zoom: 100 }));
    setAddr(null);
    emit("app:edge:navigate", { id: w.id, url: u });
  };
  const back = () => patch(cur, (t) => (t.hi > 0 ? { hi: t.hi - 1 } : {}));
  const fwd = () => patch(cur, (t) => (t.hi < t.hist.length - 1 ? { hi: t.hi + 1 } : {}));
  const openTab = (u) => { const t = newTab(u); setTabs((ts) => [...ts, t]); setCur(t.id); emit("app:edge:newtab", { id: w.id, url: u || "edge://newtab" }); };
  const refocus = () => setTimeout(() => { const a = document.activeElement; if ((!a || a === document.body || !root.current.contains(a)) && root.current) root.current.focus(); }, 30);
  const closeTab = (id) => {
    const t = tabs.find((x) => x.id === id);
    const rest = tabs.filter((x) => x.id !== id);
    emit("app:edge:closetab", { id: w.id, url: t.hist[t.hi] });
    if (!rest.length) { w.close(true); return; }
    setClosed((c) => [t, ...c].slice(0, 10));
    setTabs(rest);
    refocus();
    if (id === cur) setCur(rest[Math.min(tabs.findIndex((x) => x.id === id), rest.length - 1)].id);
  };
  const reopen = () => { const [t, ...rest] = closed; if (!t) return; setClosed(rest); setTabs((ts) => [...ts, t]); setCur(t.id); refocus(); emit("app:edge:reopentab", { id: w.id, url: t.hist[t.hi] }); };
  const setZoom = (z) => { patch(cur, { zoom: z }); emit("app:edge:zoom", { id: w.id, zoom: z }); };
  const zoomStep = (d) => { const i = ZOOMS.indexOf(tab.zoom); const ni = Math.min(ZOOMS.length - 1, Math.max(0, (i < 0 ? ZOOMS.indexOf(100) : i) + d)); setZoom(ZOOMS[ni]); };

  const download = (name, content, href) => {
    const dir = known("downloads");
    let nm = name, n = 0;
    while (vfs.exists(vfs.join(dir, nm))) { n++; nm = `${vfs.baseOf(name)} (${n})${name.slice(vfs.baseOf(name).length)}`; }
    let data = content;
    if (data == null && href && href.startsWith("data:")) { try { data = decodeURIComponent(href.split(",")[1] || ""); } catch (e) { data = ""; } }
    const p = vfs.create(dir, nm, "file", { content: data || "", auto: false });
    setDownloads((d) => [{ name: nm, path: p }, ...d]);
    setDlOpen(true);
    emit("app:edge:download", { id: w.id, name: nm, path: p, from: url });
    return p;
  };

  // iframe 內的連結／下載
  useEffect(() => {
    const h = (ev) => {
      const d = ev.data;
      if (!d || !d.sim) return;
      const tid = Object.keys(frames.current).find((k) => frames.current[k] && frames.current[k].contentWindow === ev.source);
      if (!tid) return;
      if (d.sim === "download") download(d.name, d.content, d.href);
      else if (d.sim === "nav") {
        let target = d.href;
        try { target = new URL(d.href, url.startsWith("http") ? url : "https://example.com/").toString(); } catch (e) { /* ignore */ }
        if (d.blank) openTab(target); else go(target, +tid);
      }
    };
    window.addEventListener("message", h);
    return () => window.removeEventListener("message", h);
    // eslint-disable-next-line
  }, [url, cur, tabs]);

  const onKey = (e) => {
    const k = e.key.toLowerCase();
    if (e.target.tagName === "INPUT" && !(e.ctrlKey && ["t", "w", "l", "f", "tab", "+", "-", "=", "0"].includes(k))) return;
    if (e.ctrlKey && e.shiftKey && k === "t") { e.preventDefault(); reopen(); }
    else if (e.ctrlKey && k === "t") { e.preventDefault(); openTab(); }
    else if (e.ctrlKey && k === "w") { e.preventDefault(); closeTab(cur); }
    else if (e.ctrlKey && k === "tab") { e.preventDefault(); const i = tabs.findIndex((t) => t.id === cur); setCur(tabs[(i + (e.shiftKey ? tabs.length - 1 : 1)) % tabs.length].id); }
    else if (e.ctrlKey && k === "l") { e.preventDefault(); setAddr(url === "edge://newtab" ? "" : url); }
    else if (e.ctrlKey && k === "f") { e.preventDefault(); setFind({ term: "" }); }
    else if (e.ctrlKey && (k === "+" || k === "=")) { e.preventDefault(); zoomStep(1); }
    else if (e.ctrlKey && k === "-") { e.preventDefault(); zoomStep(-1); }
    else if (e.ctrlKey && k === "0") { e.preventDefault(); setZoom(100); }
    else if (e.key === "F5") { e.preventDefault(); patch(cur, (t) => ({ reloads: t.reloads + 1 })); }
    else if (e.altKey && e.key === "ArrowLeft") back();
    else if (e.altKey && e.key === "ArrowRight") fwd();
    else if (e.key === "Escape") setFind(null);
    else if (e.key === "F11") { e.preventDefault(); }
  };

  const findCount = find && find.term ? (strippedText(site.html).toLowerCase().split(find.term.toLowerCase()).length - 1) : 0;
  useEffect(() => { if (find && find.term) emit("app:edge:find", { id: w.id, term: find.term, count: findCount }); }, [find && find.term]); // eslint-disable-line

  const secure = url.startsWith("https://");
  const shown = addr != null ? addr : url === "edge://newtab" ? "" : url.replace(/^https:\/\//, "");

  return (
    <div className="edge" ref={root} tabIndex={0} onKeyDown={onKey} data-sim-id={sid("root")}>
      <div className="edge-tabs">
        {tabs.map((t) => {
          const u = t.hist[t.hi], s = resolveSite(u);
          return (
            <div key={t.id} className={"edge-tab" + (t.id === cur ? " active" : "")} data-sim-id={sid("tab:" + (s.title || "新索引標籤"))} onClick={() => { setCur(t.id); setAddr(null); emit("app:edge:switchtab", { id: w.id, url: u }); }}>
              <Ico name="globe" size={14} /><span className="edge-tab-title">{s.title || "新索引標籤"}</span>
              <button className="edge-tab-x" data-sim-id={sid("tab:close")} onClick={(e) => { if (!e.ctrlKey && !e.metaKey && !e.altKey) e.stopPropagation(); closeTab(t.id); }}><FiX size={12} /></button>
            </div>
          );
        })}
        <button className="edge-newtab-btn" data-sim-id={sid("newtab")} title="開新索引標籤" onClick={() => openTab()}><FiPlus /></button>
      </div>
      <div className="edge-bar">
        <button className="ex-nav" disabled={tab.hi === 0} data-sim-id={sid("back")} onClick={back}><FiArrowLeft /></button>
        <button className="ex-nav" disabled={tab.hi >= tab.hist.length - 1} data-sim-id={sid("forward")} onClick={fwd}><FiArrowRight /></button>
        <button className="ex-nav" data-sim-id={sid("reload")} onClick={() => patch(cur, (t) => ({ reloads: t.reloads + 1 }))}><FiRefreshCw /></button>
        <button className="ex-nav" data-sim-id={sid("home")} onClick={() => go("edge://newtab")}><FiHome /></button>
        <div className="edge-addr">
          {secure ? <FiLock size={13} /> : <FiSearch size={13} />}
          <input data-sim-id={sid("address")} value={shown} placeholder="搜尋或輸入網址" onFocus={(e) => { setAddr(url === "edge://newtab" ? "" : url); e.target.select(); }} onChange={(e) => setAddr(e.target.value)} onBlur={() => setAddr(null)} onKeyDown={(e) => { if (!e.ctrlKey && !e.metaKey && !e.altKey) e.stopPropagation(); if (e.key === "Enter") { go(addr); e.target.blur(); } else if (e.key === "Escape") { setAddr(null); e.target.blur(); } }} />
          {tab.zoom !== 100 && <span className="edge-zoom" data-sim-id={sid("zoom")} onClick={() => setZoom(100)}>{tab.zoom}%</span>}
          <FiStar size={14} />
        </div>
        <button className="ex-nav" data-sim-id={sid("downloads")} title="下載" onClick={() => setDlOpen((v) => !v)}><FiDownload /></button>
        <button className="ex-nav"><FiMoreHorizontal /></button>
      </div>
      {find && (
        <div className="edge-find" data-sim-id={sid("find")}>
          <input autoFocus data-sim-id={sid("find:input")} value={find.term} placeholder="在頁面上尋找" onChange={(e) => setFind({ term: e.target.value })} onKeyDown={(e) => { if (!e.ctrlKey && !e.metaKey && !e.altKey) e.stopPropagation(); if (e.key === "Escape") setFind(null); }} />
          <span data-sim-id={sid("find:count")}>{find.term ? `${findCount ? 1 : 0}/${findCount}` : "0/0"}</span>
          <button onClick={() => setFind(null)}><FiX /></button>
        </div>
      )}
      {dlOpen && (
        <div className="edge-dl" data-sim-id={sid("downloads:panel")}>
          <div className="edge-dl-h">下載 <button onClick={() => setDlOpen(false)}><FiX /></button></div>
          {!downloads.length && <div className="edge-dl-none">沒有下載項目</div>}
          {downloads.map((d, i) => (
            <div key={i} className="edge-dl-item"><Ico name="file" size={24} /><div><div>{d.name}</div><a data-sim-id={sid("dl:open")} onClick={() => openPath(d.path)}>開啟檔案</a>　<a data-sim-id={sid("dl:folder")} onClick={() => openApp("explorer", { path: vfs.dirname(d.path) })}>在資料夾中顯示</a></div></div>
          ))}
        </div>
      )}
      <div className="edge-page">
        {tabs.map((t) => {
          const u = t.hist[t.hi], s = resolveSite(u);
          if (t.id !== cur) return null;
          return (
            <div key={t.id + ":" + t.reloads} className="edge-view" style={t.zoom !== 100 ? { zoom: t.zoom / 100 } : undefined}>
              {s.kind === "newtab" ? <NewTabPage go={(q) => go(q, t.id)} /> : s.component ? <s.component url={u} nav={(x) => go(x, t.id)} /> : (
                <iframe ref={(el) => { frames.current[t.id] = el; }} data-sim-id={sid("page")} title={s.title} sandbox="allow-scripts allow-forms" srcDoc={(s.html || "") + BRIDGE} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export { toast };
