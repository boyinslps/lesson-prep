# 模擬 Windows 11 資料包｜給 AI 的使用說明

> **誰該讀這份**：任何要用到「模擬的 Windows 11 桌面」的 session——做技能闖關關卡、錄上課操作影片、做教材截圖、擴充新的模擬 App（Word／PPT／Google 搜尋…）。
> **先讀這份，再動手。** 這份資料包被多個 session 共用，不要為了單一需求改壞它（規則在最後一節）。
> 位置：`模擬Win11/`（在工作區根目錄底下）。人類看的簡介是 [README.md](README.md)。

---

## 0. 三十秒上手

| 我要… | 做這個 |
|---|---|
| **看一眼** 模擬器長怎樣 | 啟動預覽：`.claude/launch.json` 的 `win11sim`（port 8792，直接伺服 `模擬Win11/dist`），開 `http://localhost:8792/?scene=basic` |
| **做關卡**（學生在網頁裡操作、系統自動判定） | 用 `<iframe src=".../模擬Win11/dist/index.html?scene=XXX">` 嵌進關卡頁，用 postMessage 橋接取得事件與檔案狀態 → §6、§9；可直接參考 `public/examples/embed-demo.html` |
| **錄操作影片**（游標動畫＋字卡→MP4） | 寫一份劇本 JSON，跑 `tools/record.mjs` → §10 |
| **新增場景**（不同的起始畫面、不同的檔案） | 在 `public/scenes/` 新增一個 JSON → §5（**不用改程式、不用 build**，改完複製到 `dist/scenes/` 即可；build 也會自動複製） |
| **新增模擬 App**（Word、PPT、Google 搜尋…） | 寫一個 React 元件＋ `registerApp()` → §11（要 build） |
| **改核心程式** | 改 `src/` → 跑 `tools/build.ps1` → 跑 `tools/smoke.mjs`（必須全過）→ §13 |

**重要**：`dist/` 是建好的成品，**已提交進 git**。只是「使用」模擬器（做關卡、錄影、改場景）**不需要 Node、不需要 build**。只有改 `src/` 才需要 build。

---

## 1. 這是什麼（以及不是什麼）

- 是：一個在瀏覽器裡跑的、**比照真實 Windows 11 行為**的教學用模擬桌面。有登入／鎖定畫面、桌面、工作列、開始功能表、視窗、右鍵選單、檔案總管（真的檔案系統）、記事本、瀏覽器（Edge 風格）、相片檢視器、資源回收筒、開關機／睡眠／重新啟動。
- 是：**可用程式控制**的——任何東西都能用 JS 驅動、讀取狀態、重設到固定場景，所以能自動判定、自動錄影。
- 不是：真的作業系統。檔案都在記憶體裡，重新整理頁面就回到場景的初始狀態；不會碰到真實電腦的檔案。
- 外觀與素材（圖示、開機音效、版型）來自 [MishanPoudel/Windows11-3.0](https://github.com/MishanPoudel/Windows11-3.0)（React 作品集，老師確認該作者開放分享）；**程式幾乎全部重寫**成教學用的架構。來源與致謝見 [UPSTREAM.md](UPSTREAM.md)。
- 預設桌布是老師給的 ROKI 貓頭鷹圖（`public/wallpapers/roki.jpg`）。
- **外觀是仿 Windows 11**（含 Edge、檔案總管圖示與「Microsoft Edge」名稱）。技能闖關施工單 §5.1 當初寫「通用版、不放商標」，老師後來要求「比照真實操作環境」，以後者為準；若某處要避開商標，改 `apps/index.js` 的 `name`／`icon` 即可。

---

## 2. 檔案地圖

```
模擬Win11/
├─ AI說明.md            ← 這份（給 AI）
├─ README.md            ← 給人看的簡介
├─ UPSTREAM.md          ← 上游來源、致謝
├─ CHANGELOG.md         ← 改動紀錄（改核心要在這裡寫一行）
├─ dist/                ← 建好的成品（要提交；技能闖關／錄影直接用這個）
├─ public/              ← 靜態資源（build 時整個複製進 dist/）
│   ├─ scenes/          ← ★場景 JSON（basic、empty、practice-rename…）＋ index.json 清單
│   ├─ wallpapers/      ← 桌布
│   ├─ assets/sample/   ← 範例圖片（svg）
│   ├─ images/ audio/   ← 上游沿用的圖示與音效
│   └─ examples/embed-demo.html ← ★嵌入關卡的最小範例（含判定）
├─ scripts/             ← ★錄影劇本 JSON（示範_重新命名.json…）
├─ examples/            ← 範例輸出（錄好的 mp4、封面）
├─ tests/smoke.js       ← 冒煙測試（31 項，用示範游標真的操作 UI）
├─ tools/
│   ├─ build.ps1        ← 建置（用 工作台\runtime\node 的可攜版 Node）
│   ├─ record.mjs       ← 錄影成 MP4
│   └─ smoke.mjs        ← 跑冒煙測試
└─ src/                 ← 原始碼（React，CRA）
    ├─ index.js         ← 進入點：掛 window.Win11Sim、讀網址參數、載入場景
    ├─ kernel/          ← 作業系統核心（無畫面邏輯）
    │   ├─ store.js     ← 全域狀態 sys + useSys()
    │   ├─ vfs.js       ← ★虛擬檔案系統（路徑、改名、移動、複製、資源回收筒、復原）
    │   ├─ apps.js      ← ★App 註冊表 registerApp()
    │   ├─ wm.js        ← 視窗管理（開／關／最小化／最大化／貼齊／焦點）
    │   ├─ fileops.jsx  ← 帶對話框的檔案操作（覆蓋確認、改副檔名警告、永久刪除確認…）
    │   ├─ ui.jsx       ← 對話框、右鍵選單、通知的服務函式
    │   ├─ dnd.js       ← 拖放（用 pointer 事件實作，自動化也能驅動）
    │   ├─ scene.js     ← 場景載入器
    │   ├─ events.js    ← 事件匯流排＋事件紀錄
    │   ├─ demo.js      ← ★示範游標引擎＋UI 定位（locate / describeUI）
    │   ├─ api.js       ← ★window.Win11Sim 對外介面＋postMessage 橋
    │   ├─ sites.js     ← 瀏覽器的網站來源（scene.sites、registerSite）
    │   ├─ power.js     ← 睡眠／關機／重新啟動／登出／鎖定
    │   └─ paths.js clock.js appstate.js dnd.js DemoCursor.jsx
    ├─ shell/           ← 桌面外殼：Desktop、Taskbar、StartMenu、Window、ContextMenu、Dialogs、FileDialog、Boot、Flyouts、icons（自繪 SVG 圖示）
    ├─ apps/            ← 各 App：Explorer、Notepad、Browser、Photos、Placeholder；index.js 負責註冊
    └─ styles/sim.css   ← 全部樣式（深色／淺色主題用 CSS 變數）
```

---

## 3. 核心概念（五個東西）

1. **Scene（場景）**＝一份 JSON，描述起始畫面：使用者、時鐘、桌布、桌面圖示、工作列釘選、**檔案系統內容**、資源回收筒內容、要先開的視窗、瀏覽器網站。載入場景＝整台電腦重設。**每個關卡／每支影片都應該指定一個場景**，這樣畫面永遠一樣。
2. **VFS（虛擬檔案系統）**＝真的樹狀結構，行為比照 Windows：路徑 `C:\Users\學生\桌面\a.txt`（大小寫不分，`/` `\` 皆可）、重複名稱自動編號（`新增資料夾 (2)`、`a - 複製.txt`）、非法字元警告、改副檔名警告、移動／複製遇到同名跳「取代或略過」、刪除進資源回收筒（可還原、可清空、原資料夾沒了會重建）、Ctrl+Z 復原。
3. **App 註冊表**＝每個 App 是一個 React 元件＋一筆 `registerApp()`。副檔名關聯（雙擊 `.txt` 開記事本）也來自註冊。
4. **事件（events）**＝所有有意義的操作都會 `emit`（`fs:rename`、`win:open`…）。**關卡判定靠事件＋檔案系統狀態**，不靠猜螢幕。
5. **Demo（示範游標）**＝一個會真的在畫面上移動、點擊、拖曳、打字、按快速鍵的假滑鼠，產生**真的 DOM 事件**，所以模擬器對它的反應跟對學生一模一樣。錄影、技能卡預覽、關卡「看示範」都用它。

### 預設使用者與資料夾
- 使用者名稱 `學生`（可在場景改）。家目錄 `C:\Users\學生`，底下一定有 `桌面 下載 文件 圖片 音樂 影片`（繁中名稱，比照繁體中文版 Windows 11）。
- 場景路徑裡的 `~` ＝家目錄。**寫場景請用正斜線 `/`**（`~/桌面/作業.txt`），不用跳脫反斜線。
- 桌面上顯示的 ＝ 系統圖示（本機、資源回收筒…）＋ `~/桌面` 資料夾裡的項目。

### 與真實 Windows 一致的細節（寫關卡時可以放心依賴）
- 預設**隱藏已知副檔名**（`settings.showExtensions:false`）；改名時只改主檔名、副檔名保留。顯示副檔名時，改掉副檔名會跳「如果變更副檔名，檔案可能會無法使用」確認。
- 檔案總管：新增（資料夾／文字文件）、剪下／複製／貼上、重新命名（F2、慢雙擊、右鍵）、刪除（Delete→資源回收筒；Shift+Delete→永久刪除確認）、拖放（Ctrl 為複製）、橡皮筋選取、Ctrl／Shift 多選、排序、檢視切換、搜尋、位址列（麵包屑＋可輸入）、上一頁／下一頁／上一層、Alt+方向鍵、Ctrl+A、Ctrl+Z／Y、Ctrl+Shift+N、屬性（內容）。資源回收筒有專屬欄位與「清空」「還原」。
- 桌面：選取、橡皮筋、F2、Delete、Ctrl+C/X/V/A/Z、右鍵（檢視／排序／重新整理／貼上／新增／顯示設定…）、拖到資源回收筒、拖到資料夾圖示。
- 記事本：選單、狀態列（行／欄／字元）、`*` 未存檔標記、關閉時詢問「要儲存變更嗎？」、另存新檔對話框（自動補 `.txt`、同名覆蓋確認）、Ctrl+S／O／N／Z／Y／A、Insert 改寫模式、F5 插入時間、縮放。
- 瀏覽器：多分頁、Ctrl+T／W／Shift+T／Tab、Ctrl+L、Ctrl+F（尋找）、Ctrl+±／0（縮放，有 % 提示）、F5、上下頁、下載（存到 `~/下載`，同名自動 `(1)`）、下載面板「開啟檔案／在資料夾中顯示」。
- 開始功能表：搜尋（App＋檔案）、已釘選、所有應用程式、建議的項目（最近開啟）、使用者選單（鎖定／登出）、電源選單（睡眠／關機／重新啟動）。電源動作真的會切換畫面（黑畫面、開機、鎖定、登入）。
- 視窗：拖曳、八向縮放、雙擊標題列最大化、拖到螢幕邊緣貼齊／最大化、最小化、工作列按鈕行為（單一視窗：點一下最小化／還原；多視窗：列表）、Alt+F4。
- 工作列：右下角時鐘＋日曆小視窗、快速設定小視窗（音量、Wi-Fi 開關…）、顯示桌面。

---

## 4. 啟動與網址參數

`dist/index.html?scene=<場景名>&…`

| 參數 | 意義 |
|---|---|
| `scene` | 場景名（對應 `scenes/<名>.json`），預設 `basic` |
| `start` | 覆寫起始畫面：`desktop`（預設）／`lock`／`login`／`off`／`sleep` |
| `clock` | 固定時鐘起點，ISO 格式，如 `2026-10-12T09:30:00`（場景也可設） |
| `fast=1` | 開機／重新啟動動畫縮短（錄影、測試用） |
| `fsbtn=1` | 右上角顯示全螢幕按鈕（也可由外層呼叫 `Win11Sim.sys.fullscreen()`） |
| `nosig=1` | 隱藏右下角的「made by 資訊老師黃博胤」署名（外層網頁已有署名時才用） |

頁面載入完成會在 `<html>` 設 `data-sim-ready="1"`，並 emit `sim:ready`。**等這個再操作。**

預設視窗尺寸是跟著瀏覽器視窗（`window.innerWidth/innerHeight`）。**錄影／截圖請固定 1280×720**（record.mjs 預設）。

---

## 5. Scene JSON 完整欄位

```jsonc
{
  "id": "practice-rename",               // 識別用
  "title": "練習：檔案重新命名",           // 給人看
  "user": { "name": "學生", "password": null },   // password 非 null 會在登入畫面要求輸入
  "clock": "2026-10-12T09:30:00",        // 固定時鐘（錄影畫面才會一致）；省略＝真實時間
  "wallpaper": "wallpapers/roki.jpg",    // public/ 底下的相對路徑，或 "#1a3a6a" 純色
  "settings": {
    "theme": "dark",                     // dark | light
    "showExtensions": false,             // true＝顯示副檔名（教「副檔名」、「改名陷阱」時用）
    "showHidden": false,
    "desktopIcons": true
  },
  "start": "desktop",                    // desktop | lock | login | off | sleep
  "taskbarPins": ["start", "explorer", "edge", "notepad"],   // 可加 "search"
  "desktopSystemIcons": ["thisPC", "recycle", "edge"],       // 也可填任何 App id（會顯示成捷徑）
  "startPins": ["explorer", "notepad", "edge"],              // 開始功能表釘選；省略＝所有 App
  "drives": ["C"],                       // 磁碟機，可加 "D"
  "files": [                             // 檔案系統內容；上層資料夾自動建立
    { "path": "~/桌面/作業.txt", "content": "文字內容" },
    { "path": "~/桌面/小貓.svg", "src": "assets/sample/cat.svg", "size": 18432 },   // src＝圖片來源（public/ 底下）；縮圖與相片檢視器會用
    { "path": "~/文件/報告.docx", "size": 24576 },                                  // 沒有 content 的二進位檔，只需要 size（位元組）
    { "path": "~/桌面/備份", "type": "dir" },
    { "path": "~/文件/.secret.txt", "hidden": true, "content": "…" }
  ],
  "recycleBin": [                        // 資源回收筒初始內容
    { "name": "舊筆記.txt", "from": "~/文件", "content": "…" }
  ],
  "windows": [                           // 一開始就開著的視窗
    { "app": "explorer", "args": { "path": "~/文件" }, "rect": [100, 60, 900, 560], "state": "normal" }
    // rect = [x, y, 寬, 高]；state: normal | max | min；args 依 App 而定（explorer/notepad/photos 吃 path，edge 吃 url）
  ],
  "docs": {                              // 線上文件（仿 Google 文件）：網址 https://docs.google.com/document/d/<id>/edit
    "practice1": { "title": "我的自我介紹", "html": "<p>大家好…</p>" }   // html 只用 <p> <h1-3> <b> <ul> 等簡單標籤
  },
  "sites": {                             // 瀏覽器可以「連上」的網站
    "https://school.example/": { "title": "示範學校", "description": "搜尋用的描述", "html": "<html>…</html>" }
  }
}
```

**網站 HTML 的特殊功能**（在 sandbox iframe 裡）：
- 一般 `<a href>` 會導覽到 `sites` 內的其他網址（找不到的網址會出現「無法連上這個網站」）。
- 下載連結：`<a href="#" data-sim-download="學習單.txt" data-content="檔案內容">下載</a>`（或 `<a download="x.txt" href="data:…">`）→ 存進 `~/下載`、emit `app:edge:download`。
- 網址列輸入非網址的文字 → 內建搜尋結果頁，會搜尋 `sites` 的 title／description／網址。

**常用場景模板**：`basic`（完整示範桌面）、`empty`（只有資源回收筒）、`practice-rename`（顯示副檔名）。新場景請複製其中一個改。清單寫在 `scenes/index.json`（給人／AI 查；載入不依賴它）。

> 載入場景：`await Win11Sim.loadScene("basic")` 或直接傳物件 `await Win11Sim.loadScene({...場景...})`（**關卡可以把場景內嵌在關卡 JSON 裡，不一定要放進 scenes/**）。

---

## 6. `window.Win11Sim` API 速查

所有方法都掛在 `Win11Sim`（頁面內）。外層網頁用 postMessage 呼叫同樣的路徑（見 §9）。

**場景與狀態**
- `loadScene(名稱|物件, {keepLog?})` → 重設整台電腦。`reset()` → 重載最近一次的場景。
- `snapshot()` → 目前完整狀態 JSON：`phase`、`windows[]`（含各 App 內部狀態 `state_app`）、`desktop.selection`、`clipboard`、`dialogs[]`、`contextMenu`（顯示中的選單文字）、`fs`（整個檔案樹＋資源回收筒）、`recent`…
- `describeUI({prefix})` → 畫面上所有帶 `data-sim-id` 的可見元素與座標（**AI 的眼睛，免截圖**）。`locate(目標)` → `{x,y,w,h,cx,cy}`。

**檔案系統 `Win11Sim.fs`**（會 emit 事件，也會讓畫面更新）
`exists(path) isDir(path) list(dir) stat(path) read(path) tree() mkdir(path) create(dir,name,"file"|"dir",{content}) write(path,content) save(path,content) rename(path,新名) move([paths],dir) copy([paths],dir) trash([paths]) restore([binIds]) emptyBin() deleteForever([paths]) undo() redo() bin()`

**視窗 `Win11Sim.wm`**：`openApp(id,args,{rect,state}) openPath(path) close(id) closeAll() focus(id) minimize(id) maximize(id) restore(id) showDesktop() list()`

**事件 `Win11Sim.events`**：`on(型別,fn)`（型別可寫 `"fs:*"`、`"*"`）、`log`（陣列）、`clear()`、`waitFor(型別, 條件fn, 逾時ms)`（Promise；**會先看過去的紀錄**，要判定「之後才發生」請先 `clear()`）、`emit()`。

**系統 `Win11Sim.sys`**：`setSetting(鍵,值)`（如 `showExtensions`）、`setClock(iso)`、`power.{sleep,wake,shutdown,powerOn,restart,lock,signOut,login}`、`toast({title,text})`、`fullscreen()`。

**示範 `Win11Sim.demo`**（見 §7）：`run(steps)`、`click dblclick rightclick drag key type wait caption`、`cursor.{show,hide,moveTo}`。

**擴充**：`registerApp(def)`、`registerSite(def)`（見 §11）。

---

## 7. 示範游標與「目標」寫法

`demo.run(steps)` 依序執行。每一步 `{do: "...", ...}`：

| do | 參數 | 說明 |
|---|---|---|
| `click` / `dblclick` / `rightclick` | `target` | 游標滑過去（`ms` 移動時間，預設 600）並點擊；也會模擬「按下滑鼠時焦點移到輸入框」 |
| `move` | `target` | 只移動游標（用來「指」某個東西） |
| `drag` | `from`, `to` | 拖放（走 pointer 事件，真的會觸發拖放判定） |
| `select` | `target`, `text` / `all:true` / `caret:"end"` | 選取文件／文字區裡的某段字（假事件選不到字，所以直接設定選取範圍，游標會從頭拖到尾做給人看） |
| `key` | `key` | `"F2"` `"Delete"` `"Enter"` `"Ctrl+C"` `"Ctrl+Shift+T"` `"Alt+F4"` `"Ctrl++"`（加號本身） |
| `type` | `text`, `delay` | 逐字打進**目前焦點**的輸入框／文字區（先 click 它或讓它自動取得焦點）；支援中文 |
| `wait` | `ms` | 停一下 |
| `caption` | `text`, `sub` | 畫面下方字卡（錄影用）；`text:""` 清除 |
| `scene` | `name` | 中途換場景 |

**target 寫法**
- `"taskbar:start"`：`data-sim-id` 精確比對
- `"desktop:icon:*作業*"`：含 `*` 萬用字元
- `"text:重新命名"`：畫面上文字符合的元素
- `{x: 700, y: 300}`：螢幕座標

被捲動區域遮住的元素會自動捲到可見再點。

### `data-sim-id` 命名表（找按鈕就靠它；不確定就呼叫 `describeUI()`）
| 範圍 | id |
|---|---|
| 桌面 | `desktop`、`desktop:icon:<名稱>`（系統圖示用顯示名，如 `資源回收筒`、`本機`；檔案用完整檔名含副檔名） |
| 工作列 | `taskbar:start` `taskbar:app:<appId>` `taskbar:clock` `taskbar:quick` `taskbar:showdesktop` `taskbar:search` `taskbar:win:<視窗id>` |
| 視窗框 | `win:<視窗id>`、`win:<id>:title|minimize|maximize|close`（視窗 id 形如 `w1`，從 `snapshot().windows` 取） |
| 檔案總管 | `explorer:<id>:item:<檔名>`、`:nav:<名稱>`（導覽窗格：桌面／下載／文件／圖片／音樂／影片／資源回收筒／本機）、`:cmd:<新增|剪下|複製|貼上|重新命名|刪除|排序|檢視|更多|還原|清空資源回收筒>`、`:address`、`:address:input`、`:crumb:<名>`、`:back|forward|up`、`:search`、`:content`、`:status`、`:sort:<欄名>` |
| 記事本 | `notepad:<id>:text`、`:menu:<檔案|編輯|檢視>`、`:item:<選項名>` |
| 瀏覽器 | `edge:<id>:address`、`:back|forward|reload|home|newtab|downloads|page`、`:tab:<標題>`、`:find:input`、`:dl:open|folder` |
| 線上文件 | `gdoc:page`（編輯區）、`gdoc:title`、`gdoc:title:input`、`gdoc:star`、`gdoc:status`、`gdoc:menu:<檔案|編輯|檢視|插入|格式|工具|說明>`＋`:<選項>`（如 `gdoc:menu:檔案:下載：純文字 (.txt)`）、`gdoc:tb:<復原|重做|粗體|斜體|底線|連結|靠左對齊|置中對齊|靠右對齊|項目符號清單|編號清單|清除格式|縮小字級|放大字級|字級>`、下拉：`gdoc:tb:樣式`＋`:<一般文字|標題 1|標題 2|標題 3>`、`gdoc:tb:字型`＋`:<微軟正黑體|標楷體>`、`gdoc:tb:文字顏色`＋`:<黑色|紅色|藍色>`；連結：`gdoc:link:input|apply|cancel`；分享：`gdoc:share`、`gdoc:share:email|add|access|copy|done`、`gdoc:share:access:<受限|知道連結的任何人>` |
| 選單 | `ctx:menu`、`ctx:<選項文字>`（例：`ctx:新增`、`ctx:資料夾`、`ctx:重新命名`） |
| 對話框 | `dialog:btn:<按鈕文字>`（`確定` `是` `否` `儲存` `不要儲存` `取消` `取代目的地中的檔案` `略過這個檔案` `兩個檔案都保留`）、`dialog:close`；開／存檔：`fdlg:nav:<名>` `fdlg:filename` `fdlg:item:<檔名>` `fdlg:type` `fdlg:up` |
| 開始功能表 | `start`、`start:search`、`start:app:<名>`、`start:result:<名>`、`start:all`、`start:user`、`start:power`、`start:shutdown|restart|sleep|lock|signout` |
| 登入／電源畫面 | `lock`、`login`、`login:signin`、`login:password`、`login:submit`、`login:power`、`off`、`off:poweron`、`sleep` |

---

## 8. 事件清單（判定用）

`Win11Sim.events.log` 每筆 `{seq, t, type, data}`。

| type | data | 何時 |
|---|---|---|
| `fs:create` | `path, kind("file"|"dir"), name` | 新增檔案／資料夾 |
| `fs:rename` | `from, to, oldName, newName` | 重新命名 |
| `fs:move` / `fs:copy` | `from[], to[], destDir` | 移動／複製（拖放、剪下貼上） |
| `fs:delete` | `paths[], toBin(bool)`（資源回收筒內刪除：`fromBin:true, binIds`） | 刪除 |
| `fs:restore` / `fs:emptyBin` | `paths[]` / `count` | 還原／清空 |
| `fs:write` | `path, length` | 檔案內容寫入（如記事本存檔） |
| `fs:undo` / `fs:redo` | `label` | 復原／取消復原 |
| `win:open|close|focus|minimize|maximize|restore|snap|showDesktop` | `id, app` | 視窗動作 |
| `file:open` | `path, app` | 雙擊／開啟檔案 |
| `desktop:open` | `id` | 雙擊桌面系統圖示 |
| `clipboard:set` / `clipboard:paste` / `clipboard:text` | `paths,mode` / `to,count,mode` / `length` | 剪貼簿（檔案／文字） |
| `ui:contextmenu` / `ui:drop` / `ui:toast` | `labels` / `paths,target` / `title,text` | 右鍵選單出現、拖放、通知 |
| `dialog:open` / `dialog:close` | `kind, title` / `kind, value` | 對話框（kind：`message` `confirm-delete` `confirm-ext` `rename-exists` `conflict` `save-as` `open-file` `save-changes` `properties`） |
| `app:explorer:navigate|new|refresh` | `id, path` | 檔案總管 |
| `app:notepad:edit|save|undo|redo|overwrite` | `id, path/length/on` | 記事本 |
| `app:edge:navigate|newtab|closetab|reopentab|switchtab|zoom|find|download` | `id, url / zoom / term,count / name,path` | 瀏覽器 |
| `app:gdocs:format|edit|title|link|paste|star|download|create|share-add|share-access|copylink|share-done` | `cmd,value`（`style` `font` `color` `fontSize` `bold`…）／`email`／`access`／`url`… | 線上文件 |
| `sys:login|loginFailed|lock|signout|sleep|wake|shutdown|boot|restart|setting` | — | 登入、電源、設定 |
| `scene:loaded` / `sim:ready` / `demo:start|end|key` | — | 生命週期（`ui:*`、`demo:*` 判定時通常要忽略） |

---

## 9. 做「技能闖關關卡」：配方

技能闖關網站在 `技能闖關/`（見該資料夾 `PROGRESS.md`，**SIM-1～5 工作包就是用這個資料包**）。做法：

1. **發布位置**：把 `模擬Win11/dist/` 整份放到網站底下（例：`site/sim/`），關卡頁用 iframe 嵌入 `sim/index.html?scene=<場景>&fast=1`。場景可用名稱，也可在關卡載入後用 `loadScene(物件)` 傳入內嵌場景。
2. **橋接**（可直接複製 `public/examples/embed-demo.html` 的 `call()` 函式）：
   - 外層→模擬器：`iframe.contentWindow.postMessage({sim:"win11", id:1, method:"fs.exists", args:["C:\\Users\\學生\\桌面\\自我介紹.txt"]}, "*")`，`method` 是 `Win11Sim` 底下的路徑（`snapshot`、`fs.read`、`demo.run`、`loadScene`、`reset`…）。
   - 模擬器→外層：回覆 `{sim:"win11", id, ok, result|error}`；所有事件即時推送 `{sim:"win11-event", type, data}`；載入完成推 `type:"ready"`。
3. **判定**：監聽 `fs:*`／`win:*`／`app:*` 事件，觸發時用 `fs.exists`／`fs.read`／`snapshot` 驗證**結果**（檔案真的在、內容對、視窗真的開著），不要只信事件。例：
   - 改名關卡：`fs:rename` 後檢查 `fs.exists("…/自我介紹.txt")`。
   - 刪除關卡：`fs.bin()` 含該檔名且原路徑不存在；永久刪除則 bin 也沒有。
   - 複製貼上：目的資料夾 `fs.list` 含檔名，且來源仍在。
   - 下載關卡：`app:edge:download` ＋ `~/下載` 有該檔。
   - 開關機關卡：`sys:shutdown` → `sys:boot` → `sys:login`。
4. **「看示範」按鈕**：`demo.run(steps)`；示範前先 `reset()`，示範完再 `reset()` 讓學生自己做。
5. **重設**：學生卡住 → `reset()`。每次進關卡一定先 `loadScene`。
6. **同一技能換多種環境練**（技能闖關企畫要求）：同一個判定邏輯配不同場景（`basic` 桌面、檔案總管開著、記事本開著、瀏覽器開著）→ 用 `windows` 欄位換起始視窗即可。
7. 關卡文案裡的步驟若涉及按鈕，**用 `describeUI()` 確認 id 與畫面上的文字**，不要憑記憶。

> 陷阱類關卡（改副檔名、同名覆蓋、永久刪除）都已內建真實警告對話框，直接把場景設成 `showExtensions:true` 或放同名檔即可，不用自己寫對話框。

---

## 10. 做「操作影片」：配方

兩種做法，選一種：

### A. 一鍵錄影（推薦）：`tools/record.mjs`
```
工作台\runtime\node\node.exe 模擬Win11\tools\record.mjs --script 模擬Win11\scripts\示範_重新命名.json --out 輸出\xxx.mp4 --out-size 854x480 --crf 31
```
- 它會：啟一個暫存設定檔的無頭 Chrome → 載入 `dist/` → 載入場景 → 執行劇本（游標、字卡都會被錄進去）→ 依畫面變化的時間戳合成 MP4 ＋輸出 `xxx_封面.jpg`。**不需要老師在場、不用 computer use。**
- 選項：`--size 1280x720`（錄製解析度）、`--out-size`（輸出，**嵌進學習單請 854x480、crf≥31**，符合「影片一律壓畫質」規則）、`--scene`、`--keep-frames`、`--headed`。
- 需要：Chrome、`C:\Users\Roki\tools\ffmpeg\bin\ffmpeg.exe`。

**劇本 JSON**（`scripts/*.json`）：
```json
{ "scene": "practice-rename", "intro": 800, "outro": 1200, "cursor": true, "start": "desktop",
  "steps": [ {"do":"caption","text":"第 1 步　在檔案上按一下","sub":"…"},
             {"do":"click","target":"desktop:icon:新增文字文件.txt"}, … ] }
```
`steps` 就是 §7 的步驟。看 `scripts/示範_重新命名.json` 當範本；成品範例在 `examples/示範_重新命名.mp4`。

### B. 截圖＋步驟影片工具（要自己排版的）
`工作台/步驟影片工具/`（cdp.ps1＋render.ps1，spec 格式見該資料夾 README）可以把截圖做成「紅圈、箭頭、按鍵提示、字卡」。用模擬器當截圖來源：開 `?scene=…`，`Win11Sim.locate("…")` 取得按鈕座標寫進 spec，`Win11Sim.demo.run([...])` 把畫面推到每一步再截圖。

### 影片規範（老師的規定）
內嵌影片短邊 ≤480、crf ≥31、`preload="none"` 加封面圖；原檔放 `_影片原檔/`。

---

## 11. 如何新增一個 App（Word／PPT／Excel／Google 搜尋…）

資料包**已預留**：`apps/index.js` 底下已註冊 `word`、`excel`、`powerpoint` 三個**佔位 App**（`hidden:true`，已綁好 `.docx/.xlsx/.pptx` 副檔名；雙擊檔案會開出「尚未開發」視窗）。要做真的，**把 `component` 換成你寫的元件、拿掉 `hidden`** 即可。

步驟：
1. 在 `src/apps/` 新增元件（參考 `Notepad.jsx`，約 150 行的完整範例）：
   ```jsx
   import { useWin, useCloseGuard } from "../shell/WinContext";
   import { useExposeState } from "../kernel/appstate";
   import { emit } from "../kernel/events";
   import { fileDialog } from "../shell/FileDialog";      // 開啟／另存新檔對話框（通用）
   export default function Word() {
     const w = useWin();            // w.args（開啟參數，如 path）、w.setTitle()、w.close()、w.messageBox()
     useExposeState(() => ({ ... })); // 讓 snapshot() 看得到 App 內部狀態（判定／AI 用）
     useCloseGuard(async () => true); // 關閉前攔截（未存檔提示）
     // 元素加 data-sim-id={`word:${w.id}:xxx`}，示範游標與 describeUI 才找得到
   }
   ```
2. 在 `src/apps/index.js` 註冊：
   ```js
   registerApp({ id: "word", name: "Word", icon: "word", component: Word, fileTypes: ["docx"],
                 defaultSize: { w: 1000, h: 640 }, newFile: { ext: "docx", label: "新增 Microsoft Word 文件" } });
   ```
   欄位說明在 `kernel/apps.js` 最上面。`icon` 可用內建名稱（見 `shell/icons.jsx`，已有 `word excel powerpoint notepad photos calculator…`）或 `"img:路徑"`。
3. 檔案內容：VFS 的檔案是 `{content:字串}`。docx／pptx 可以把「文件模型」序列化成 JSON 字串存在 `content`（副檔名維持 `.docx`），開啟時解析；沒內容的檔案（只有 `size`）就當空白文件。
4. 把要判定的操作 `emit("app:word:xxx", {...})`；元素都加 `data-sim-id`。
5. 在 `tests/smoke.js` 加幾條測試，`build.ps1` → `smoke.mjs` 全過。
6. 在 §6／§7／§8 與 `CHANGELOG.md` 補上新 id 與事件。

**Google 搜尋／Google 文件這類「網站」不需要做成 App**，用 `registerSite`（在瀏覽器裡顯示）：
```js
import { registerSite } from "../kernel/sites";
registerSite({
  id: "google",
  match: (url) => /^https:\/\/www\.google\.com/.test(url),
  resolve: (url) => ({ title: "Google", component: GoogleHome }),   // 或 { title, html: "<html>…</html>" }
});
```
元件收到 `{url, nav}`（`nav("https://…")` 導覽）。這樣 Chrome／Edge 視窗、分頁、網址列、縮放、尋找、下載都現成可用。

### 已內建：線上文件（仿 Google 文件的練習前端）
- 版面像 Google 文件，但**刻意精簡成單一操作**：字型 2 種（微軟正黑體、標楷體）、文字顏色 3 種（黑／紅／藍）、字級 4 級（11／14／18／24，用 −＋ 調）、樣式 4 種（一般文字、標題 1～3）、粗體／斜體／底線、連結、對齊（左／中／右）、項目符號／編號清單、清除格式、復原／重做；選單（檔案／編輯／格式…）只有少數項目可用，其餘灰掉；分享對話框（新增人員、一般存取權 受限／知道連結的任何人、複製連結、完成）；檔案→下載 `.docx`／`.txt`（存進 `~/下載`）；標題可改名；「已儲存至雲端硬碟」狀態。
- 開啟：`https://docs.google.com/document/d/<id>/edit`（瀏覽器網址，或場景 `windows` 開 edge 並帶 `args.url`）；`…/document/create` 會新建一份。內容放在場景 `docs`，執行中用 `Win11Sim.docs.get(id)` 讀。
- **判定**：`Win11Sim.docs.get("practice1")` 回傳 `{title, html, text, bold, italic, underline, colors[], fonts[], sizes[], align[], headings[{level,text}], links[{href,text}], bullets, numbered, share:{people[], access}}`——關卡直接檢查這些欄位（例：標題 1 → `headings` 有 level 1；紅字 → `colors` 含 `#d93025`）。其他方法：`docs.create/patch/url/list`。
- 要**選取文字再套格式**請用示範步驟 `select`；關卡裡學生自己用滑鼠拖選即可。
- 範例場景 `docs-practice`、測試見 `tests/smoke.js`「線上文件」段。想加功能（更多顏色、字型…）改 `src/apps/GDoc.jsx` 最上面的 `FONTS` `COLORS` `SIZES` `STYLES` 常數即可。
- 版面概念參考 deeproop/google-doc-clone（只參考視覺，程式為自寫，見 UPSTREAM.md）。

**其他可擴充點**：新的開始功能表／桌面系統圖示（`desktopSystemIcons` 填 App id 即成捷徑）、新的右鍵選單（用 `showContextMenu()`）、新的對話框（`openDialog({render})`）、新的場景欄位（改 `kernel/scene.js`）。

---

## 12. 已知限制（誠實清單）

- 剪貼簿：**檔案**的剪下／複製／貼上是模擬器自己的剪貼簿，不會碰到真實系統剪貼簿。記事本的**文字**複製貼上：真人操作時走瀏覽器原生（可從外面貼進來）；自動操作（demo）時走模擬器內部剪貼簿。
- 瀏覽器只能顯示 `sites` 與已註冊網站，不會連真實網路。尋找（Ctrl+F）只算次數、不畫螢光標示。
- 瀏覽器分頁內無法用外部自動化工具點 iframe 內容（瀏覽器的安全限制）；請用 `demo`（不受影響，但同樣點不進 iframe）或讓網頁用 `postMessage` 觸發。需要自動點網頁內容時，改用 `registerSite` 的 `component`（React 元件，不在 iframe 裡）。
- 還沒有：Word／Excel／PPT（只有佔位）、Google 搜尋、Google 試算表／簡報、小畫家、計算機、設定 App、截圖工具（Win+Shift+S）、工作管理員、多使用者切換、全螢幕 F11 模擬、桌面圖示自由位置（目前自動排列）、檔案總管分頁、拖曳選取文字以外的 IME 輸入法模擬（中英切換、全形半形需另做，見技能闖關 A3）。
- 真實鍵盤的 Win 鍵、Alt+Tab、Ctrl+T/W/N（瀏覽器保留鍵）攔不到；這些情境請改用畫面上的按鈕，或在關卡裡用 demo 示範。
- `desktop:refresh`／`app:explorer:refresh` 目前只 emit 事件、不做事（檔案系統本來就即時更新）。

---

## 13. 多個 session 共用的規則（務必遵守）

1. **不要為單一關卡／單支影片改核心。** 新需求先看能不能用「新增場景」「新增劇本」解決（零風險）。
2. 要改 `src/`：先在 `CHANGELOG.md` 加一行，改完 `tools/build.ps1` → `tools/smoke.mjs` **全過**才提交，並把重建的 `dist/` 一起提交（沒裝 Node 的 session 要靠它）。
3. 不要改別人的場景／劇本內容；要變體就複製成新檔名（建議 `<用途>_<名稱>.json`）。
4. 新增 `data-sim-id` 或事件要同步更新本文件 §7／§8。既有 id 與事件名稱**不要改名**（關卡判定依賴它）。
5. 不要 push／發布；發布流程見 `記憶：push＝兩個都要`（老師說 push 才做）。
6. 署名：模擬器右下角已內建小字「made by 資訊老師黃博胤」（錄影也會帶到）；外層關卡網頁自己也要有署名（`embed-demo.html` 已含），這時可加 `nosig=1` 避免重複。
7. 不寫入學生姓名、學號、成績、金鑰到場景或劇本。

### 建置環境（只有改 `src/` 才需要）
- Node：`工作台\runtime\node\`（可攜版 v22 LTS win-x64，**不在 git 裡**；`.gitignore` 排除了 `工作台/runtime/`）。別台電腦沒有時：從 https://nodejs.org/dist/v22.23.3/node-v22.23.3-win-x64.zip 下載，驗證 SHA256（見同目錄 `SHASUMS256.txt`），解壓縮成 `工作台\runtime\node\node.exe`。
- 建置：`powershell -NoProfile -ExecutionPolicy Bypass -File 模擬Win11\tools\build.ps1`（第一次會自動 `npm install`，`node_modules/` 不進 git）。
- 測試：`工作台\runtime\node\node.exe 模擬Win11\tools\smoke.mjs`（無頭 Chrome，約 20 秒，預期 `通過 31／31`）。
- 開發時想即時預覽：`工作台\runtime\node\npm.cmd start`（port 3011）。
- Windows 注意：寫 `.ps1` 若含中文要存成 UTF-8 **帶 BOM**，否則 PowerShell 5.1 會亂碼。

---

*made by 資訊老師黃博胤*
