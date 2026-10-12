# 改動紀錄

> 改核心程式（`src/`）請在最上面加一行：日期｜誰（哪個專案的 session）｜改了什麼｜為什麼。

## 2026-10-12｜v1.0.0｜初版（技能闖關／上課錄影共用）
- 以 MishanPoudel/Windows11-3.0 的外觀與素材為基礎，重寫成教學用架構：虛擬檔案系統、App 註冊表、事件、場景 JSON、示範游標、postMessage 橋接。
- App：檔案總管（含資源回收筒、此電腦）、記事本、瀏覽器（Edge 風格）、相片；Word／Excel／PowerPoint 為佔位。
- 桌面、工作列、開始功能表、視窗管理、右鍵選單、對話框（含通用開啟／另存新檔）、鎖定／登入／睡眠／關機／重新啟動。
- 工具：`tools/build.ps1`、`tools/record.mjs`（錄成 MP4）、`tools/smoke.mjs`＋`tests/smoke.js`（21 項）。
- 場景：`basic`、`empty`、`practice-rename`；劇本：`示範_重新命名`。
