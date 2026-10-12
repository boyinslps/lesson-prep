// 冒煙測試：在瀏覽器頁面內執行（由 tools/smoke.mjs 載入，或手動貼進 DevTools / javascript_tool）。
// 全部用「示範游標」真的在畫面上操作，所以同時驗證了 UI 與檔案系統。回傳 {pass, fail, lines}。
(async () => {
  const S = window.Win11Sim, lines = []; let pass = 0, fail = 0;
  const ok = (name, cond) => { (cond ? pass++ : fail++); lines.push((cond ? "PASS " : "FAIL ") + name); };
  const H = "C:\\Users\\學生", D = H + "\\文件", DT = H + "\\桌面";
  const run = (steps) => S.demo.run(steps);
  const winOf = (app) => S.snapshot().windows.find((w) => w.app === app);

  await S.loadScene("basic"); await S.demo.wait(300);

  // --- 檔案總管 ---
  await run([{ do: "click", target: "taskbar:app:explorer" }, { do: "wait", ms: 300 }]);
  const wid = winOf("explorer").id, E = (x) => `explorer:${wid}:${x}`;
  await run([{ do: "click", target: E("item:日記.txt") }, { do: "key", key: "F2" }, { do: "type", text: "我的日記" }, { do: "key", key: "Enter" }]);
  ok("F2 重新命名（副檔名隱藏時保留 .txt）", S.fs.exists(D + "\\我的日記.txt") && !S.fs.exists(D + "\\日記.txt"));
  await run([{ do: "click", target: E("item:報告.docx") }, { do: "key", key: "Delete" }, { do: "wait", ms: 200 }]);
  ok("Delete 刪除進資源回收筒", !S.fs.exists(D + "\\報告.docx") && S.fs.bin().some((b) => b.name === "報告.docx"));
  await run([{ do: "click", target: E("nav:資源回收筒") }, { do: "wait", ms: 300 }, { do: "click", target: E("item:報告.docx") }, { do: "click", target: E("cmd:還原") }, { do: "wait", ms: 300 }]);
  ok("資源回收筒還原", S.fs.exists(D + "\\報告.docx"));
  await run([{ do: "click", target: E("nav:文件") }, { do: "wait", ms: 200 }, { do: "click", target: E("cmd:新增") }, { do: "wait", ms: 200 }, { do: "click", target: "ctx:資料夾" }, { do: "wait", ms: 200 }, { do: "type", text: "作業" }, { do: "key", key: "Enter" }]);
  ok("新增資料夾並命名", S.fs.isDir(D + "\\作業"));
  await run([{ do: "click", target: E("item:簡報.pptx") }, { do: "key", key: "Ctrl+C" }, { do: "key", key: "Ctrl+V" }, { do: "wait", ms: 200 }]);
  ok("複製貼上同資料夾 → 「- 複製」", S.fs.exists(D + "\\簡報 - 複製.pptx"));
  await run([{ do: "drag", from: E("item:成績表.xlsx"), to: E("item:作業") }, { do: "wait", ms: 300 }]);
  ok("拖曳檔案到資料夾", S.fs.exists(D + "\\作業\\成績表.xlsx") && !S.fs.exists(D + "\\成績表.xlsx"));
  await run([{ do: "key", key: "Ctrl+Z" }, { do: "wait", ms: 200 }]);
  ok("Ctrl+Z 復原移動", S.fs.exists(D + "\\成績表.xlsx"));
  S.wm.closeAll();

  // --- 開始功能表＋記事本＋另存新檔 ---
  await run([{ do: "click", target: "taskbar:start" }, { do: "wait", ms: 300 }, { do: "type", text: "記事" }, { do: "wait", ms: 200 }, { do: "click", target: "start:result:記事本" }, { do: "wait", ms: 400 }]);
  const np = winOf("notepad"); ok("開始功能表搜尋並開啟記事本", !!np);
  const N = (x) => `notepad:${np.id}:${x}`;
  await run([{ do: "click", target: N("text") }, { do: "type", text: "你好，教學模擬！" }, { do: "key", key: "Ctrl+S" }, { do: "wait", ms: 300 }]);
  ok("Ctrl+S 跳出另存新檔", S.snapshot().dialogs.some((d) => d.kind === "save-as"));
  await run([{ do: "click", target: "fdlg:nav:桌面" }, { do: "click", target: "fdlg:filename" }, { do: "type", text: "打招呼" }, { do: "click", target: "dialog:btn:儲存" }, { do: "wait", ms: 300 }]);
  ok("另存到桌面並自動補 .txt", S.fs.exists(DT + "\\打招呼.txt") && S.fs.read(DT + "\\打招呼.txt") === "你好，教學模擬！");
  await run([{ do: "click", target: N("text") }, { do: "type", text: "x" }, { do: "click", target: `win:${np.id}:close` }, { do: "wait", ms: 300 }]);
  ok("未存檔關閉會詢問", S.snapshot().dialogs.some((d) => d.kind === "save-changes"));
  await run([{ do: "click", target: "dialog:btn:不要儲存" }, { do: "wait", ms: 300 }]);
  ok("不要儲存後視窗關閉", !winOf("notepad"));

  // --- 桌面 ---
  await run([{ do: "click", target: "desktop:icon:作業.txt" }, { do: "key", key: "F2" }, { do: "type", text: "作業一" }, { do: "key", key: "Enter" }]);
  ok("桌面 F2 重新命名", S.fs.exists(DT + "\\作業一.txt"));
  await run([{ do: "drag", from: "desktop:icon:作業一.txt", to: "desktop:icon:資源回收筒" }, { do: "wait", ms: 300 }]);
  ok("桌面檔案拖到資源回收筒", !S.fs.exists(DT + "\\作業一.txt") && S.fs.bin().some((b) => b.name === "作業一.txt"));
  await run([{ do: "rightclick", target: { x: 700, y: 300 } }, { do: "wait", ms: 200 }, { do: "click", target: "ctx:新增" }, { do: "wait", ms: 200 }, { do: "click", target: "ctx:資料夾" }, { do: "wait", ms: 200 }, { do: "key", key: "Enter" }]);
  ok("桌面右鍵 → 新增 → 資料夾", S.fs.isDir(DT + "\\新增資料夾"));

  // --- 瀏覽器 ---
  await run([{ do: "click", target: "taskbar:app:edge" }, { do: "wait", ms: 400 }]);
  const ed = winOf("edge"), B = (x) => `edge:${ed.id}:${x}`;
  await run([{ do: "click", target: B("address") }, { do: "type", text: "school.example/download" }, { do: "key", key: "Enter" }, { do: "wait", ms: 500 }]);
  ok("瀏覽器開網址", winOf("edge").state_app.tabs[0].url.includes("school.example/download"));
  await run([{ do: "click", target: B("root") }, { do: "key", key: "Ctrl+T" }, { do: "wait", ms: 200 }, { do: "key", key: "Ctrl+W" }, { do: "wait", ms: 200 }, { do: "key", key: "Ctrl+Shift+T" }, { do: "wait", ms: 200 }]);
  ok("Ctrl+T / Ctrl+W / Ctrl+Shift+T 救回分頁", winOf("edge").state_app.tabs.length === 2);
  await run([{ do: "key", key: "Ctrl++" }, { do: "key", key: "Ctrl++" }]);
  ok("Ctrl++ 縮放到 125%", winOf("edge").state_app.tabs.find((t) => t.active).zoom === 125);
  S.wm.closeAll();

  // --- 電源 ---
  S.sys.setSetting("fastBoot", true);
  await run([{ do: "click", target: "taskbar:start" }, { do: "wait", ms: 300 }, { do: "click", target: "start:power" }, { do: "wait", ms: 200 }, { do: "click", target: "start:shutdown" }, { do: "wait", ms: 300 }]);
  ok("關機 → 黑畫面", S.snapshot().phase === "off");
  await run([{ do: "click", target: "off:poweron" }, { do: "wait", ms: 600 }]);
  ok("開機 → 鎖定畫面", S.snapshot().phase === "lock");
  await run([{ do: "click", target: "lock" }, { do: "wait", ms: 200 }, { do: "click", target: "login:signin" }, { do: "wait", ms: 300 }]);
  ok("登入 → 桌面", S.snapshot().phase === "desktop");

  S.demo.cursor.hide();
  return { pass, fail, lines };
})();
