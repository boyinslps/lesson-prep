# 上游來源與致謝

- 專案：**Windows11-3.0** — <https://github.com/MishanPoudel/Windows11-3.0>（作者 Mishan Poudel）
- 取得時的版本：`502dc421b1ea31df494a0eb4ba139e6ec4260f6c`（2026-10-12 `git clone --depth 1`）
- 原專案：React＋Tailwind 的 Windows 11 作品集風格複製品（登入畫面、桌面、工作列、開始功能表、幾個 App）。

## 沿用了什麼
- 外觀參考（工作列置中、開始功能表、深色主題的配色與版型）
- 圖示與音效素材：`public/images/apps/*.png`（chrome、edge、explorer、folder、recyclebin、windows、calculator）、`public/images/options/*.png`、`public/images/folders/*.ico`、`public/audio/{shutdown,sleep,switch}.mp3`

## 重寫了什麼
上游的「檔案總管」是個人作品集導覽、視窗狀態寫死、沒有任何檔案操作，也依賴外部圖片網址，無法拿來做教學判定。因此**程式碼全部重寫**成「作業系統核心＋App 註冊表」架構（虛擬檔案系統、事件、場景、示範游標、橋接 API…），與上游已無共用程式碼。

## 授權狀態（請注意）
- 上游 repo **沒有 LICENSE 檔**。老師表示該作者的個人頁面說明可以分享，因此決定直接使用素材；**這點我（AI）無法從 repo 內容驗證**。
- 因此：保留這份致謝；若日後要把含上游素材的網站**公開發布**（例如 pcclass），建議先取得作者書面同意（GitHub issue 或 email），或把 `public/images/` 與 `public/audio/` 換成自繪／自有素材（`shell/icons.jsx` 的圖示已是自繪 SVG，只有少數 App 圖示仍用上游 png）。
- 本資料包新寫的程式碼與場景／劇本，著作權屬資訊老師黃博胤。

## 第二個參考：google-doc-clone
- <https://github.com/deeproop/google-doc-clone>（commit `ec92e5b`），無 LICENSE。只參考「標題列＋選單列＋圓角工具列＋灰底白紙」的**版面概念**；該專案的選單不可用、工具列與編輯器是第三方套件（react-draft-wysiwyg／draft-js），所以 `src/apps/GDoc.jsx` 是自寫的 contentEditable 版本，沒有使用它的程式碼或圖片。
