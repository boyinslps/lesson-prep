import React, { useEffect, useState } from "react";
import * as vfs from "../kernel/vfs";
import { asset } from "../shell/icons";
import { useWin } from "../shell/WinContext";

const IMG = /\.(png|jpe?g|gif|svg|webp|bmp)$/i;

export default function Photos() {
  const w = useWin();
  const [path, setPath] = useState(w.args.path || null);
  const [zoom, setZoom] = useState(1);
  useEffect(() => { if (w.args.path) setPath(w.args.path); }, [w.args._n, w.args.path]);
  const dir = path ? vfs.dirname(path) : null;
  const sibs = dir ? vfs.list(dir).filter((n) => n.type === "file" && IMG.test(n.name)).map((n) => vfs.join(dir, n.name)) : [];
  const i = path ? sibs.findIndex((p) => p.toLowerCase() === path.toLowerCase()) : -1;
  const node = path ? vfs.get(path) : null;
  useEffect(() => { w.setTitle(node ? `${node.name} - 相片` : "相片"); }, [path]); // eslint-disable-line
  return (
    <div className="photos" data-sim-id={`photos:${w.id}`}>
      <div className="photos-bar">
        <button disabled={i <= 0} data-sim-id={`photos:${w.id}:prev`} onClick={() => setPath(sibs[i - 1])}>‹</button>
        <button disabled={i < 0 || i >= sibs.length - 1} data-sim-id={`photos:${w.id}:next`} onClick={() => setPath(sibs[i + 1])}>›</button>
        <span className="photos-name">{node ? node.name : "請從檔案總管開啟相片"}</span>
        <button onClick={() => setZoom((z) => Math.max(0.25, z - 0.25))}>－</button>
        <span>{Math.round(zoom * 100)}%</span>
        <button onClick={() => setZoom((z) => Math.min(4, z + 0.25))}>＋</button>
      </div>
      <div className="photos-view">
        {node && node.src ? <img src={asset(node.src)} alt={node.name} style={{ transform: `scale(${zoom})` }} draggable="false" /> : <div className="photos-empty">{node ? "這個檔案沒有可顯示的影像內容" : ""}</div>}
      </div>
    </div>
  );
}
