# 遊戲入口網（學生許可資源入口網）

學習單「繳交成功」後的「🕹️ 更多遊戲」按鈕，**一律連到這個入口網**：

**https://boyinslps.github.io/pcclass/games/**

- `index.html`：入口網原始碼（唯一的版本來源）。內容是老師審過、學生可以用的網站清單（教學平台、打字、PaGamO、Silk、E-game、Quick Draw…）與課堂守則。
- `check.py`：掃 `materials/` 底下所有學習單，確認「更多遊戲」指向上面的網址、沒有留 Gemini 分享連結。
- 規定寫在《學習單資料與提交規範》§3-b；按鈕連結固定，**不用為了增減遊戲去改學習單**。

## 為什麼自架

原本「更多遊戲」連到 Gemini Canvas 的分享頁（`gemini.google.com/share/…`）：內容放在別人的伺服器上、要按「繼續」才顯示、隨時可能失效，也不在版本管理裡。2026-11-04 把它的原始碼抓下來（只是一份純連結的 HTML）放到自己的 GitHub，14 份學習單全部改連過來。

## 新增、移除或修改遊戲

1. 改 `引導規範/game-portal/index.html`（照現有卡片複製一張，改標題、說明、`href`；連結要加 `target="_blank" rel="noopener noreferrer"`）。
2. 複製到發布庫並推上去（工作台的發布庫在 `工作台/.pub_repo/`，它是 `boyinslps/pcclass`）：

   ```
   copy 引導規範\game-portal\index.html 工作台\.pub_repo\games\index.html
   cd 工作台\.pub_repo
   git add games && git commit -m "更新遊戲入口網" && git push origin main
   ```

3. GitHub Pages 約 1～2 分鐘後更新，用 `https://boyinslps.github.io/pcclass/games/` 確認。
4. 備課庫（`lesson-prep`）也 commit 這份 `index.html`，之後別人（或另一台電腦）才有來源。

## 新學習單怎麼放

獎勵區的兩顆按鈕照其他學習單複製：

```html
<a href="https://boyinslps.github.io/typehero/index.html" target="_blank" rel="noopener" class="…">🎮 打字英雄</a>
<a href="https://boyinslps.github.io/pcclass/games/" target="_blank" rel="noopener" class="…">🕹️ 更多遊戲</a>
```

做完跑 `工作台/runtime/python/python.exe 引導規範/game-portal/check.py`，確認沒有錯誤。

made by 資訊老師黃博胤
