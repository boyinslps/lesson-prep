# 電腦急救站（技能闖關）

學生電腦基本技能的闖關網站：看影片 → 練習 → 挑戰，自動判定過關，用年級／班級／座號保存紀錄，達成條件頒發電子證書。

- 企畫：[企畫書.md](企畫書.md)
- 進度與夜間施工規則：[PROGRESS.md](PROGRESS.md)
- 新增關卡規範：[../引導規範/技能關卡設計規範.md](../引導規範/技能關卡設計規範.md)

## 結構

```
設定.json        網站名稱、類別、證書條件、Firebase
levels/          每關一個資料夾（level.json＋assets/）
_原始碼/         共用樣式、程式、判定器、頁面樣板
build.py         產生 site/
site/            產出的網站（發布到 pcclass/skills/）
firestore.rules  worksheet-f47f3 的完整規則（與賀卡創作營共用）
```

## 產生與預覽

```bash
工作台/runtime/python/python.exe 技能闖關/build.py
```

預覽：`.claude/launch.json` 的 `skills`（http://localhost:8791）。

made by 資訊老師黃博胤
