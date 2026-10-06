# 電腦急救站｜施工進度

> 夜間排程（每天 00:00）讀這份檔案，從「下一個工作包」開始做。一個工作包做完就在這裡打勾、寫日期。
> 規格以 [企畫書.md](企畫書.md) 為準；關卡怎麼設計看 [../引導規範/技能關卡設計規範.md](../引導規範/技能關卡設計規範.md)。

## 夜間施工規則（排程任務照這裡做）

1. 先查用量：每週已用 ≥ 60% 或 5 小時已用 ≥ 90% → 在當天日誌寫「略過」就結束。
2. 從下面清單挑**第一個沒打勾、沒標「需老師」**的工作包。
3. 每做完一包：跑 `工作台/runtime/python/python.exe 技能闖關/build.py`（不能有錯誤）→ 用預覽（launch.json 的 `skills`，port 8791）實際走過改到的關卡 → 在這裡打勾 → `git commit`（**不 push、不發布**）。
4. 每包之間再查一次用量：每週 ≥ 60%、或 5 小時 ≥ 95%、或「已過 03:00 且 5 小時窗口的重置時間晚於 08:00」就收工。（老師規定：5 小時額度可以用完，但早上 08:00 要有全新的 5 小時能用。）
5. 收工前寫 `技能闖關/施工日誌/YYYY-MM-DD.md`：做了哪些包、怎麼驗證、需要老師決定的事。
6. 遇到要老師決定的事 → 寫進日誌「待老師決定」，該包標「需老師」，跳到下一包，不要自己猜。
7. **不能做**：push／發布、改 Firebase Console、改其他節次教材、用 computer use（半夜沒人能按允許）。

## 已完成

- [x] P0-1 骨架（2026-10-06）：`設定.json`、`level.json` 格式、`build.py`（驗證代碼／類別／先修不可繞圈）、地圖頁、關卡外框（看／練／闖）、身分列、本機＋Firestore 存檔、證書條件判斷（含 minLevels 未達不開放）、證書頁暫代版
- [x] P0-2 判定器第一批：`selectText`、`copyPaste`、`plainPaste`
- [x] 示範關卡 A1 選取文字、B1 複製貼上、B3 純文字貼上（判定已用模擬事件測過；真實鍵盤剪貼簿待實機確認）
- [x] `firestore.rules` 合併版（cardWork＋skillQuest）
- [x] P0-3 發布管線（2026-10-06）：`POST /api/git-publish` body `{"group":"技能闖關"}` → 先 build 再把 site/ 換到 pcclass `skills/`；加 `"dryRun":true` 只列變動不推（已測 dry-run）
- [x] P1-1／P2-1／P2-2（2026-10-06）：判定器 `fileUpload`（文字檔驗證碼、改名比對含 .txt.txt／少副檔名／沒改名提示、圖片 SHA-256）；關卡 C1 下載檔案、C2 檔案重新命名、D1 另存圖片（圖片用 System.Drawing 繪製）
- [x] P1-2／P1-3（2026-10-06）：判定器 `popup`（cookie／notify／ad／prize／subscribe，陷阱按鈕說明原因、廣告 × 可延遲出現）、`tabPair`（site/tab/ 密碼小卡＋BroadcastChannel，關分頁用 ping 偵測）；關卡 E3 處理彈出視窗、E1 開新分頁與切換分頁
- [x] P3-1（2026-10-06）：證書頁 Canvas（1600×1131，可自填姓名不上傳、下載 PNG、列印 A4 橫式）；未達成時列出還差哪些關；進網站時補發已達成的證書。8 個必修關卡到齊，第一階證書已可取得
- [x] P3-2（2026-10-06）：教師後台 `site/admin/`（Google 登入、全班×關卡進度表、通過率、點日期重設、證書編號查驗）；`admin/?demo=1` 用 28 人假資料驗證過畫面。真實資料要等 Firebase 開啟匿名＋Google 登入
- [x] P2-3（2026-10-06）：判定器 `keyTask`（文字框任務＋指定快速鍵，自己重打會被擋）、`quiz`（choice 選擇題／bucket 拖曳分類，可點選代替拖曳）；關卡 A4 復原與取消復原、C4 認識副檔名
- [x] P0-4（2026-10-06）：地圖同類別先修連線（SVG，過關變綠實線）；手機 375px 無橫向捲動；E3 挑戰模式任務清單不再透露視窗種類
- [x] 影片（2026-10-06）：E3 新做（specs/技能闖關_E3_彈出視窗.json，CDP 截判定器畫面）；B3 沿用四上 L04「複製資料貼文件」
- [x] P5 部分（2026-10-06）：copyPaste 加 `cut` 模式、判定器 `tabUrl`、`tabReopen`、`reload`；關卡 B2 剪下與移動、B4 複製網址（沿用四上 L04 複製網址影片）、E2 救回分頁、F3 網頁卡住；paste／input 合併判定避免錯一次算兩次
- [x] P5-1（2026-10-06）：A2 拖曳（quiz bucket＋`dragOnly`）、A3 中英與全半形（keyTask＋`bad` 規則：全形字、全大寫提示）
- [x] P5-5 部分（2026-10-06）：判定器 `zoom`（devicePixelRatio＋Ctrl+0）、`findWord`（要偵測到 Ctrl+F，次數自動數）；關卡 E4 網頁縮放、E5 找字

## 待老師處理（不在夜間做）

- [ ] **Firebase 匿名登入沒開**：測試時 `auth/configuration-not-found`。到 Firebase Console（worksheet-f47f3）→ Authentication → 開始使用 → 登入方式 → 啟用「匿名」。賀卡創作營也受影響（目前也只存在本機）。
- [ ] 把 `技能闖關/firestore.rules` 整份貼到 Firestore 規則並發布。
- [ ] Firebase Console → Authentication → 登入方式 → 也要啟用「Google」（教師後台用）；「設定 → 已授權網域」加上 `boyinslps.github.io`。
- [ ] 實機用 Chrome 試 B1、B3：真的按 Ctrl+C／Ctrl+V／Ctrl+Shift+V 是否都正確判定。
- [ ] P4 錄影（computer use，需老師在電腦前）：見下方「錄影待辦」。

## 工作包清單（依序）

> **介面改版（v2 深色主題）優先**：規格在 [施工_介面改版.md](施工_介面改版.md)，老師已回覆 §1（2026-10-06），依序施工。

- [ ] UI-1 設計基礎（深色主題、元件、小機器人「小急」）
- [ ] UI-2 登入畫面與訪客模式、拿掉座號列
- [ ] UI-3 主畫面類別面板＋技能卡＋右下總進度
- [ ] UI-4 個人資料面板＋6 枚類別徽章
- [ ] UI-5 示範游標引擎＋前 5 種判定器腳本
- [ ] UI-6 示範游標其餘判定器
- [ ] UI-7 技能卡預覽動畫產線（WebP）
- [ ] UI-8 關卡頁改版（影片兩段、過關動畫）
- [ ] UI-9 收尾與全站回歸

- [ ] P2-4 網頁類教學影片：A1、B1、E1、A4（步驟影片工具 cdp.ps1＋render.ps1，影片放 levels/xx/assets/教學.mp4＋封面.jpg；做法參考 specs/技能闖關_E3_彈出視窗.json：用 CDP 開本機預覽站，呼叫 window.Checkers 把判定器畫面單獨畫滿 1280×640 再截圖，量按鈕座標寫進 spec；Chrome 用暫存設定檔、port 9333）
- [ ] P5-3 C3 資料夾、C5 資源回收筒
- [ ] P5-4 D2 複製圖片貼上、D3 螢幕截圖
- [ ] P5-5 E6 全螢幕（F11 進入、F11／Esc 離開；用 innerHeight≈screen.height 判斷）
- [ ] P5-6 F1 視窗不見（quiz＋影片）、F2 Insert 覆寫（模擬覆寫模式，按 Insert 修好再打字）

## 錄影待辦（需老師在場，computer use）

桌面、檔案總管、右鍵選單類，夜間不能做：C1、C2、C3、C5、D1、D3、F1。錄影前準備乾淨的 `D:\示範` 資料夾與 Chrome 設定檔。

made by 資訊老師黃博胤
