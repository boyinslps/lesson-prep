// 錄影：開啟模擬 Windows 11 → 載入場景 → 用示範游標執行劇本 → 把畫面變化錄成 MP4。
// 用法（在專案根目錄）：
//   工作台\runtime\node\node.exe 模擬Win11\tools\record.mjs --script 模擬Win11\scripts\示範_重新命名.json --out 輸出.mp4
// 選項：--scene <場景名>（預設用劇本裡的 scene）  --size 1280x720  --out-size 854x480（嵌進學習單建議）
//       --crf 31  --keep-frames  --headed（看得到瀏覽器視窗）  --chrome <chrome.exe 路徑>
// 劇本格式見 AI說明.md「錄影劇本」。需要：Chrome、ffmpeg（C:\Users\Roki\tools\ffmpeg\bin\ffmpeg.exe）。
import fs from "node:fs";
import path from "node:path";
import http from "node:http";
import os from "node:os";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const pkg = path.resolve(here, "..");
const arg = (n, d) => { const i = process.argv.indexOf("--" + n); return i < 0 ? d : (process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[i + 1] : true); };
const scriptPath = arg("script");
if (!scriptPath) { console.error("缺少 --script <劇本.json>"); process.exit(1); }
const script = JSON.parse(fs.readFileSync(path.resolve(scriptPath), "utf8"));
const [W, H] = String(arg("size", "1280x720")).split("x").map(Number);
const [OW, OH] = String(arg("out-size", `${W}x${H}`)).split("x").map(Number);
const out = path.resolve(arg("out", "out.mp4"));
const crf = arg("crf", "30");
const chrome = arg("chrome", ["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"].find(fs.existsSync));
const ffmpeg = arg("ffmpeg", "C:\\Users\\Roki\\tools\\ffmpeg\\bin\\ffmpeg.exe");
if (!chrome || !fs.existsSync(ffmpeg)) { console.error("找不到 Chrome 或 ffmpeg"); process.exit(1); }
const dist = path.join(pkg, "dist");
if (!fs.existsSync(path.join(dist, "index.html"))) { console.error("找不到 dist/，先執行 tools\\build.ps1"); process.exit(1); }

// 1. 靜態伺服器
const MIME = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".ico": "image/x-icon", ".mp3": "audio/mpeg" };
const server = http.createServer((req, res) => {
  const p = path.join(dist, decodeURIComponent(req.url.split("?")[0]).replace(/^\/+/, "") || "index.html");
  if (!p.startsWith(dist) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end("404"); }
  res.writeHead(200, { "content-type": MIME[path.extname(p)] || "application/octet-stream" });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const sitePort = server.address().port;

// 2. 啟動 Chrome（暫存設定檔，不動平常用的）
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "win11sim-rec-"));
const dbgPort = 9400 + Math.floor(Math.random() * 400);
const flags = [`--remote-debugging-port=${dbgPort}`, `--user-data-dir=${profile}`, `--window-size=${W},${H + 120}`, "--no-first-run", "--disable-extensions", "--mute-audio", "--hide-scrollbars", "about:blank"];
if (!arg("headed", false)) flags.unshift("--headless=new");
const ch = spawn(chrome, flags, { stdio: "ignore" });
const cleanup = () => { try { ch.kill(); } catch (e) { /* ignore */ } try { server.close(); } catch (e) { /* ignore */ } };
process.on("exit", cleanup);

let target;
for (let i = 0; i < 60 && !target; i++) {
  try { const list = await (await fetch(`http://127.0.0.1:${dbgPort}/json`)).json(); target = list.find((t) => t.type === "page"); } catch (e) { /* 等 Chrome 起來 */ }
  if (!target) await new Promise((r) => setTimeout(r, 250));
}
if (!target) { console.error("連不上 Chrome"); cleanup(); process.exit(1); }

// 3. CDP
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
let id = 0; const pending = new Map(); const frames = []; const frameDir = fs.mkdtempSync(path.join(os.tmpdir(), "win11sim-frames-"));
ws.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pending.has(d.id)) { const { res, rej } = pending.get(d.id); pending.delete(d.id); d.error ? rej(new Error(d.error.message)) : res(d.result); }
  else if (d.method === "Page.screencastFrame") {
    const f = path.join(frameDir, String(frames.length).padStart(6, "0") + ".jpg");
    fs.writeFileSync(f, Buffer.from(d.params.data, "base64"));
    frames.push({ f, t: d.params.metadata.timestamp });
    send("Page.screencastFrameAck", { sessionId: d.params.sessionId }).catch(() => {});
  }
};
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
const evalJs = async (expression) => {
  const r = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
  return r.result.value;
};

await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 1, mobile: false });
const scene = arg("scene", script.scene || "basic");
await send("Page.navigate", { url: `http://127.0.0.1:${sitePort}/index.html?scene=${encodeURIComponent(scene)}&fast=1${script.start ? "&start=" + script.start : ""}` });
for (let i = 0; i < 80; i++) { if (await evalJs(`document.documentElement.getAttribute('data-sim-ready')`).catch(() => null)) break; await new Promise((r) => setTimeout(r, 150)); }
await new Promise((r) => setTimeout(r, 400));

// 4. 錄製
console.log("錄影中…（場景 " + scene + "，" + script.steps.length + " 步）");
await send("Page.startScreencast", { format: "jpeg", quality: 90, maxWidth: W, maxHeight: H, everyNthFrame: 1 });
await new Promise((r) => setTimeout(r, script.intro ?? 800));
await evalJs(`Win11Sim.demo.run(${JSON.stringify(script.steps)}, {cursorVisible: ${script.cursor !== false}})`);
await new Promise((r) => setTimeout(r, script.outro ?? 1200));
await send("Page.stopScreencast");
const t0 = frames.length ? frames[0].t : 0, tEnd = frames.length ? frames[frames.length - 1].t + 1.0 : 0;
ws.close();
cleanup();
if (frames.length < 2) { console.error("沒錄到畫面"); process.exit(1); }

// 5. 組成 MP4（依時間戳決定每格停留多久）
const list = path.join(frameDir, "list.txt");
let txt = "";
frames.forEach((fr, i) => { const dur = Math.max(0.02, (i + 1 < frames.length ? frames[i + 1].t : tEnd) - fr.t); txt += `file '${fr.f.replace(/\\/g, "/")}'\nduration ${dur.toFixed(3)}\n`; });
txt += `file '${frames[frames.length - 1].f.replace(/\\/g, "/")}'\n`;
fs.writeFileSync(list, txt);
fs.mkdirSync(path.dirname(out), { recursive: true });
const r = spawnSync(ffmpeg, ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", list, "-vf", `fps=25,scale=${OW}:${OH}:flags=lanczos,format=yuv420p`, "-c:v", "libx264", "-crf", String(crf), "-preset", "veryfast", "-movflags", "+faststart", out], { stdio: "inherit" });
if (r.status !== 0) { console.error("ffmpeg 失敗"); process.exit(1); }
const cover = out.replace(/\.mp4$/i, "") + "_封面.jpg";
fs.copyFileSync(frames[Math.min(frames.length - 1, Math.floor(frames.length * 0.6))].f, cover);
if (!arg("keep-frames", false)) fs.rmSync(frameDir, { recursive: true, force: true });
fs.rmSync(profile, { recursive: true, force: true });
console.log(`完成：${out}（${(fs.statSync(out).size / 1024).toFixed(0)} KB，${frames.length} 格，${(tEnd - t0).toFixed(1)} 秒）\n封面：${cover}`);
process.exit(0);
