import React from "react";
import { Ico } from "../shell/icons";
import { getApp } from "../kernel/apps";
import { useWin } from "../shell/WinContext";

// 尚未開發的 app 先用這個佔位（Word / Excel / PowerPoint / Google 搜尋…）
export default function Placeholder() {
  const w = useWin();
  const app = getApp(w.win.app);
  return (
    <div className="placeholder-app">
      <Ico name={app.icon} size={72} />
      <h2>{app.name}</h2>
      <p>這個應用程式的教學模擬尚未開發。</p>
      <p className="small">新增方式請看 AI說明.md「如何新增一個 App」</p>
    </div>
  );
}
