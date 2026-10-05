# 步驟影片工具

把截圖做成「游標動畫＋紅圈／框＋按鍵提示＋下方字卡」的 MP4，嵌進學習單。

- `cdp.ps1`：用 Chrome DevTools 協定開一個**另外的** Chrome（暫存設定檔，不是平常用的）截 1280×640/720 原尺寸圖、點按鈕、選字。
  啟動：`chrome.exe --remote-debugging-port=9333 --user-data-dir=<暫存資料夾> about:blank`，再 `. .\cdp.ps1; Connect-Cdp 9333; Size 1280 720; Shot 'x.png'`。
  無頭模式（headless）會被 Cloudflare 擋（例：TinEye），所以用一般視窗。
- `mockdoc.html`：Google 文件的**示意畫面**（不用登入），`?ticket=1&url=1` 切換內容。
- `StepVideo.cs`＋`render.ps1`：讀 `specs/*.json` 畫逐格 PNG，再用 ffmpeg 合成 H.264 MP4。
  `powershell -File render.ps1 -spec specs\xxx.json -out xxx.mp4`（ffmpeg 路徑：`C:\Users\Roki\tools\ffmpeg\bin\ffmpeg.exe`）。
  spec 裡的圖片路徑相對於本資料夾（例：`shots/xxx.png`），截圖請放 `shots/`。

spec 每個場景可用：`img`／`imgs`（依時間換圖）、`chrome`（模擬分頁列與網址列）、`cursor`（關鍵影格，mode：arrow／cross／ibeam）、`clicks`、`circles`、`boxes`（red／highlight／select／gray-x）、`labels`、`keys`、`snip`（Win+Shift+S 截圖動畫）、`toasts`、`caption`／`sub`／`captions`、`step`；`type:"title"` 是全畫面字卡。

made by 資訊老師黃博胤
