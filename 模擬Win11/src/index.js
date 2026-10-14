import React from "react";
import { createRoot } from "react-dom/client";
import "./styles/sim.css";
import "./styles/gdocs.css";
import "./apps";
import Shell from "./shell/Shell";
import api, { installBridge } from "./kernel/api";
import { sys } from "./kernel/store";

window.Win11Sim = api;

// 網址參數：?scene=basic  &start=lock|login|desktop  &clock=2026-10-12T09:30:00  &fsbtn=1  &fast=1
const q = new URLSearchParams(window.location.search);
const spec = q.get("scene") || "basic";

createRoot(document.getElementById("root")).render(<Shell />);
installBridge();

api.loadScene(spec).then(() => {
  if (q.get("start")) sys.set({ phase: q.get("start") });
  if (q.get("clock")) api.sys.setClock(q.get("clock"));
  if (q.get("fsbtn")) sys.set({ fsButton: true });
  if (q.get("nosig")) sys.set({ hideSig: true });
  if (q.get("fast")) api.sys.setSetting("fastBoot", true);
  document.documentElement.setAttribute("data-sim-ready", "1");
  api.events.emit("sim:ready", { scene: spec });
}).catch((e) => {
  document.body.insertAdjacentHTML("beforeend", `<pre style="color:#f66;padding:20px">載入場景失敗：${e.message}</pre>`);
});
