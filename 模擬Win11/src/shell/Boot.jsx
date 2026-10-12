// 非桌面畫面：鎖定畫面、登入、睡眠、關機、開機中、重新啟動
import React, { useEffect, useState } from "react";
import { useSys } from "../kernel/store";
import { simNow } from "../kernel/clock";
import { asset, Ico } from "./icons";
import * as power from "../kernel/power";
import { useClock } from "./hooks";

const Spinner = () => <div className="spinner" />;

function Lock() {
  const t = useClock();
  const wp = useSys((s) => s.settings.wallpaper);
  return (
    <div className="lockscreen" style={{ backgroundImage: `url(${asset(wp)})` }} data-sim-id="lock" tabIndex={0} autoFocus
      onClick={power.unlockToLogin} onKeyDown={power.unlockToLogin}>
      <div className="lock-clock">
        <div className="lock-time">{t.toLocaleTimeString("zh-TW", { hour: "numeric", minute: "2-digit", hour12: false })}</div>
        <div className="lock-date">{t.toLocaleDateString("zh-TW", { month: "long", day: "numeric", weekday: "long" })}</div>
      </div>
      <div className="lock-hint">按一下或按任意鍵解除鎖定</div>
    </div>
  );
}

function Login() {
  const user = useSys((s) => s.user);
  const wp = useSys((s) => s.settings.wallpaper);
  const [pw, setPw] = useState("");
  const [err, setErr] = useState(false);
  const submit = (e) => { e && e.preventDefault(); if (!power.login(pw)) { setErr(true); setPw(""); } };
  return (
    <div className="loginscreen" style={{ backgroundImage: `url(${asset(wp)})` }} data-sim-id="login">
      <div className="login-box">
        <div className="login-avatar"><Ico name="user" size={96} /></div>
        <div className="login-name" data-sim-id="login:username">{user.name}</div>
        {user.password ? (
          <form onSubmit={submit} className="login-form">
            <input type="password" autoFocus className="login-input" data-sim-id="login:password" placeholder="密碼" value={pw} onChange={(e) => { setPw(e.target.value); setErr(false); }} />
            <button className="login-go" type="submit" data-sim-id="login:submit" aria-label="登入">→</button>
            {err && <div className="login-err">密碼不正確。請再試一次。</div>}
          </form>
        ) : (
          <button className="btn primary login-btn" autoFocus data-sim-id="login:signin" onClick={() => submit()}>登入</button>
        )}
      </div>
      <div className="login-power" title="電源" data-sim-id="login:power" onClick={power.shutdown}>⏻</div>
    </div>
  );
}

export default function Boot() {
  const phase = useSys((s) => s.phase);
  if (phase === "lock") return <Lock />;
  if (phase === "login") return <Login />;
  if (phase === "sleep") return <div className="blackscreen" data-sim-id="sleep" onClick={power.wake} onKeyDown={power.wake} tabIndex={0} />;
  if (phase === "off") {
    return (
      <div className="blackscreen off" data-sim-id="off">
        <button className="power-on" data-sim-id="off:poweron" onClick={power.powerOn}>⏻ 按一下開機</button>
      </div>
    );
  }
  if (phase === "booting" || phase === "restarting") {
    return (
      <div className="blackscreen" data-sim-id={phase}>
        <div className="boot-center">
          {phase === "restarting" ? <><Spinner /><div className="boot-text">正在重新啟動</div></> : <><Ico name="windows" size={72} /><div style={{ height: 40 }} /><Spinner /></>}
        </div>
      </div>
    );
  }
  return null;
}
