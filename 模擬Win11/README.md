# 模擬 Windows 11（教學用共用資料包）

一個在瀏覽器裡跑、**比照真實 Windows 11 行為**的模擬桌面，用來：

1. **技能闖關關卡**：學生在網頁裡真的操作（改名、複製貼上、刪除還原、下載、開關機…），系統用事件＋檔案狀態自動判定。
2. **上課操作影片**：寫一份劇本，一鍵錄成 MP4（假游標＋字卡），不需要老師在場。
3. **教材截圖**：場景固定（時鐘、檔案、視窗位置都可指定），每次畫面一樣。

有真的檔案系統（重新命名、新增、刪除到資源回收筒、還原、移動、複製、另存新檔、復原），並預留好擴充：以後加 Word、PowerPoint、Excel、Google 搜尋只要註冊一個 App。

## 快速開始

- 預覽：`.claude/launch.json` 的 `win11sim`（port 8792）→ <http://localhost:8792/?scene=basic>
- 嵌進關卡網頁：看 `public/examples/embed-demo.html`
- 錄影：`工作台\runtime\node\node.exe 模擬Win11\tools\record.mjs --script 模擬Win11\scripts\示範_重新命名.json --out 輸出.mp4`
- **AI 請先讀 [AI說明.md](AI說明.md)**（完整 API、場景格式、事件、`data-sim-id` 命名、擴充方式、多 session 共用規則）。

## 內容

| 資料夾 | 用途 |
|---|---|
| `dist/` | 建好的成品（直接用，不需 Node） |
| `public/scenes/` | 場景 JSON（起始畫面＋檔案內容） |
| `scripts/` | 錄影劇本 |
| `src/` | 原始碼（React） |
| `tools/` | 建置、錄影、冒煙測試 |
| `tests/smoke.js` | 21 項自動化操作測試 |

來源與致謝見 [UPSTREAM.md](UPSTREAM.md)。

made by 資訊老師黃博胤
