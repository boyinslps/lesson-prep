import React, { useEffect, useState } from "react";
import { sys, useSys } from "../kernel/store";
import { allApps, getApp } from "../kernel/apps";
import { openApp, openPath } from "../kernel/wm";
import * as vfs from "../kernel/vfs";
import * as power from "../kernel/power";
import { home } from "../kernel/paths";
import { Ico, FileIco } from "./icons";
import { showContextMenu } from "../kernel/ui";

function searchFiles(q) {
  const out = [];
  const walk = (dir) => {
    for (const n of vfs.list(dir, { hidden: false })) {
      const p = vfs.join(dir, n.name);
      if (n.name.toLowerCase().includes(q)) out.push({ path: p, node: n });
      if (n.type === "dir" && out.length < 20) walk(p);
    }
  };
  walk(home());
  return out.slice(0, 8);
}

export default function StartMenu() {
  const open = useSys((s) => s.startOpen);
  const userMenu = useSys((s) => s.userMenuOpen);
  const user = useSys((s) => s.user.name);
  const startPins = useSys((s) => s.startPins);
  const recent = useSys((s) => s.recent);
  const [q, setQ] = useState("");
  const [powerMenu, setPowerMenu] = useState(false);
  const [all, setAll] = useState(false);
  useEffect(() => { if (!open) { setQ(""); setPowerMenu(false); setAll(false); } }, [open]);
  if (!open) return null;

  const apps = allApps().filter((a) => a.startMenu && !a.hidden);
  const pinned = (startPins && startPins.length ? startPins.map(getApp).filter(Boolean) : apps);
  const ql = q.trim().toLowerCase();
  const appHits = ql ? apps.filter((a) => a.name.toLowerCase().includes(ql) || a.id.includes(ql)) : [];
  const fileHits = ql ? searchFiles(ql) : [];
  const launch = (id) => { openApp(id); };
  const first = () => { if (appHits[0]) launch(appHits[0].id); else if (fileHits[0]) { openPath(fileHits[0].path); sys.set({ startOpen: false }); } };

  return (
    <div className="start" data-sim-id="start" onPointerDown={(e) => e.stopPropagation()} onContextMenu={(e) => e.preventDefault()}>
      <div className="start-search">
        <Ico name="search" size={16} />
        <input data-sim-id="start:search" autoFocus value={q} placeholder="在此輸入以搜尋" onChange={(e) => setQ(e.target.value)} onKeyDown={(e) => e.key === "Enter" && first()} />
      </div>
      {ql ? (
        <div className="start-results">
          {appHits.length > 0 && <div className="start-h">應用程式</div>}
          {appHits.map((a) => <div key={a.id} className="start-result" data-sim-id={"start:result:" + a.name} onClick={() => launch(a.id)}><Ico name={a.icon} size={22} /><span>{a.name}</span><em>應用程式</em></div>)}
          {fileHits.length > 0 && <div className="start-h">文件</div>}
          {fileHits.map((f) => <div key={f.path} className="start-result" data-sim-id={"start:result:" + f.node.name} onClick={() => { openPath(f.path); sys.set({ startOpen: false }); }}><FileIco name={f.node.name} type={f.node.type} size={22} /><span>{f.node.name}</span><em>{vfs.dirname(f.path)}</em></div>)}
          {!appHits.length && !fileHits.length && <div className="start-none">找不到相符的項目</div>}
        </div>
      ) : all ? (
        <div className="start-body">
          <div className="start-sec"><b>所有應用程式</b><button className="start-link" data-sim-id="start:back" onClick={() => setAll(false)}>‹ 返回</button></div>
          <div className="start-alllist">
            {apps.slice().sort((a, b) => a.name.localeCompare(b.name, "zh-TW")).map((a) => <div key={a.id} className="start-result" data-sim-id={"start:app:" + a.name} onClick={() => launch(a.id)}><Ico name={a.icon} size={22} /><span>{a.name}</span></div>)}
          </div>
        </div>
      ) : (
        <div className="start-body">
          <div className="start-sec"><b>已釘選</b><button className="start-link" data-sim-id="start:all" onClick={() => setAll(true)}>所有應用程式 ›</button></div>
          <div className="start-grid">
            {pinned.map((a) => (
              <div key={a.id} className="start-app" data-sim-id={"start:app:" + a.name} onClick={() => launch(a.id)}
                onContextMenu={(e) => { e.preventDefault(); showContextMenu(e.clientX, e.clientY, [{ label: "開啟", onClick: () => launch(a.id) }, { label: "釘選到工作列", onClick: () => sys.set((s) => ({ taskbarPins: s.taskbarPins.includes(a.id) ? s.taskbarPins : [...s.taskbarPins, a.id] })) }]); }}>
                <Ico name={a.icon} size={32} /><span>{a.name}</span>
              </div>
            ))}
          </div>
          <div className="start-sec"><b>建議的項目</b></div>
          <div className="start-recent">
            {(recent || []).filter((r) => vfs.exists(r.path)).slice(0, 6).map((r) => (
              <div key={r.path} className="start-rec" data-sim-id={"start:recent:" + vfs.basename(r.path)} onClick={() => { openPath(r.path); }}>
                <FileIco name={vfs.basename(r.path)} type={vfs.isDir(r.path) ? "dir" : "file"} size={26} />
                <div><div>{vfs.basename(r.path)}</div><small>{r.when || "最近"}</small></div>
              </div>
            ))}
            {!(recent || []).length && <div className="start-none small">開啟過的檔案會出現在這裡</div>}
          </div>
        </div>
      )}
      <div className="start-foot">
        <div className="start-user" data-sim-id="start:user" onClick={() => sys.set({ userMenuOpen: !userMenu })}>
          <div className="start-avatar"><Ico name="user" size={26} /></div><span>{user}</span>
          {userMenu && (
            <div className="start-menu up" onPointerDown={(e) => e.stopPropagation()}>
              <div className="start-menu-item" data-sim-id="start:lock" onClick={(e) => { e.stopPropagation(); power.lock(); }}>鎖定</div>
              <div className="start-menu-item" data-sim-id="start:signout" onClick={(e) => { e.stopPropagation(); power.signOut(); }}>登出</div>
            </div>
          )}
        </div>
        <div className="start-power" data-sim-id="start:power" title="電源" onClick={() => setPowerMenu((v) => !v)}>
          <svg width="18" height="18" viewBox="0 0 18 18"><path d="M9 1.5v7M4.8 4a6 6 0 1 0 8.4 0" stroke="currentColor" strokeWidth="1.6" fill="none" strokeLinecap="round" /></svg>
          {powerMenu && (
            <div className="start-menu up right">
              <div className="start-menu-item" data-sim-id="start:sleep" onClick={(e) => { e.stopPropagation(); power.sleep(); }}>睡眠</div>
              <div className="start-menu-item" data-sim-id="start:shutdown" onClick={(e) => { e.stopPropagation(); power.shutdown(); }}>關機</div>
              <div className="start-menu-item" data-sim-id="start:restart" onClick={(e) => { e.stopPropagation(); power.restart(); }}>重新啟動</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
