// 冒煙測試：無頭 Chrome 載入 dist/，執行 tests/smoke.js，印出 PASS/FAIL。改完核心程式、build 之後一定要跑。
// 用法：工作台\runtime\node\node.exe 模擬Win11\tools\smoke.mjs
import fs from "node:fs";
import path from "node:path";
import http from "node:http";
import os from "node:os";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const pkg = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dist = path.join(pkg, "dist");
const chrome = ["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"].find(fs.existsSync);
if (!chrome) { console.error("找不到 Chrome／Edge"); process.exit(2); }
const MIME = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".ico": "image/x-icon" };
const server = http.createServer((req, res) => {
  const p = path.join(dist, decodeURIComponent(req.url.split("?")[0]).replace(/^\/+/, "") || "index.html");
  if (!p.startsWith(dist) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end("404"); }
  res.writeHead(200, { "content-type": MIME[path.extname(p)] || "application/octet-stream" });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "win11sim-smoke-"));
const port = 9300 + Math.floor(Math.random() * 90);
const ch = spawn(chrome, ["--headless=new", `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, "--window-size=1280,840", "--no-first-run", "--mute-audio", "about:blank"], { stdio: "ignore" });
const done = (code) => { try { ch.kill(); } catch (e) { /* ignore */ } server.close(); process.exit(code); };
let target;
for (let i = 0; i < 60 && !target; i++) { try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === "page"); } catch (e) { /* wait */ } if (!target) await new Promise((r) => setTimeout(r, 250)); }
if (!target) { console.error("連不上 Chrome"); done(2); }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
let id = 0; const pend = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } };
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: `http://127.0.0.1:${server.address().port}/index.html?scene=basic&fast=1` });
for (let i = 0; i < 80; i++) { const r = await send("Runtime.evaluate", { expression: "document.documentElement.getAttribute('data-sim-ready')", returnByValue: true }); if (r.result?.result?.value) break; await new Promise((r) => setTimeout(r, 150)); }
const code = fs.readFileSync(path.join(pkg, "tests", "smoke.js"), "utf8");
const r = await send("Runtime.evaluate", { expression: code, awaitPromise: true, returnByValue: true });
if (r.result?.exceptionDetails) { console.error("測試腳本出錯：", r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text); done(2); }
const v = r.result.result.value;
console.log(v.lines.join("\n"));
console.log(`\n通過 ${v.pass}／${v.pass + v.fail}`);
done(v.fail ? 1 : 0);
