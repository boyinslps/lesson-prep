# 產生五上 L05/L06 查證文件的 4 支步驟影片規格（specs/五上L05_*.json）
# 截圖是 1280x640；有 chrome 的場景要把截圖座標 y 加 80 才是影片座標
import json, os, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
OFF = 80

def chrome(tab, url, **kw):
    d = {"tabs": [tab], "urls": [url], "active": 0}
    d.update(kw)
    return d

DOCTAB = "41230 王小明 查證文件 - Google 文件"
DOCURL = "docs.google.com/document/d/1x…/edit"

def cur(*pts):
    out = []
    for p in pts:
        d = {"t": p[0], "x": p[1], "y": p[2]}
        if len(p) > 3: d["mode"] = p[3]
        out.append(d)
    return out

def title(t, sub, dur=3):
    return {"type": "title", "dur": dur, "title": t, "subtitle": sub}

def save(name, scenes):
    spec = {"w": 1280, "h": 720, "band": 140, "fps": 25, "scenes": scenes}
    with open(os.path.join(HERE, "specs", name + ".json"), "w", encoding="utf8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)

# ============ V1 從訊息找到查核文章 ============
MSGCH = chrome("網傳訊息（示意）", "（老師給的那則訊息）")
v1 = [
  title("從訊息找到「查核文章」", "圈關鍵詞 → 加「查核」搜尋 → 認出查核機構 → 只讀幾個地方", 3.5),
  {"dur": 8, "img": "shots/v1_msg.png", "chrome": MSGCH, "step": "1",
   "caption": "先圈出 2～3 個關鍵詞", "sub": "不要整句貼去搜。挑「人、事、物」最重要的幾個詞",
   "boxes": [
     {"t": 0.8, "dur": 99, "x": 415, "y": 291 + OFF, "w": 75, "h": 28},
     {"t": 2.0, "dur": 99, "x": 790, "y": 164 + OFF, "w": 200, "h": 28},
     {"t": 3.2, "dur": 99, "x": 815, "y": 206 + OFF, "w": 100, "h": 28}],
   "labels": [{"t": 4.2, "dur": 99, "x": 330, "y": 480 + OFF, "text": "例：陌生人　操作手機　生物特徵", "color": "green", "size": 26}],
   "cursor": cur((0, 900, 420), (0.8, 452, 305 + OFF), (2.0, 890, 178 + OFF), (3.2, 865, 220 + OFF), (8, 865, 220 + OFF))},
  {"dur": 7, "img": "shots/v1_g_typed.png", "chrome": chrome("Google", "www.google.com"), "step": "2",
   "caption": "打進 Google：關鍵詞 ＋「查核」", "sub": "最後加上「查核」兩個字，才找得到查核機構的文章",
   "circles": [{"t": 1.5, "dur": 99, "x": 544, "y": 192 + OFF, "w": 40, "h": 26, "pad": 10}],
   "labels": [{"t": 2.2, "dur": 99, "x": 640, "y": 300 + OFF, "text": "別忘了「查核」！", "color": "green", "size": 28}],
   "keys": [{"t": 4.2, "dur": 1.8, "keys": ["Enter"], "x": 640, "y": 470}],
   "cursor": cur((0, 900, 520), (1.2, 560, 203 + OFF, "ibeam"), (7, 560, 203 + OFF, "ibeam"))},
  {"dur": 11, "img": "shots/v1_g_results.png", "chrome": chrome("幫陌生人操作手機 生物特徵 查核 - Google 搜尋", "google.com/search?q=幫陌生人操作手機+生物特徵+查核"),
   "imgs": [{"t": 4.0, "img": "shots/v1_g_results2.png"}], "step": "3",
   "caption": "搜尋結果最上面常有「AI 摘要」", "sub": "先不要只看它。往下滑，找查核機構寫的文章",
   "captions": [{"t": 4.2, "caption": "認出「查核機構」的文章", "sub": "網址是 tfc-taiwan.org.tw、mygopen.com，都是專門查謠言的"}],
   "boxes": [
     {"t": 0.6, "dur": 3.2, "x": 100, "y": 150 + OFF, "w": 660, "h": 340, "style": "gray-x"},
     {"t": 5.0, "dur": 99, "x": 100, "y": 128 + OFF, "w": 665, "h": 120},
     {"t": 6.4, "dur": 99, "x": 100, "y": 270 + OFF, "w": 665, "h": 120}],
   "labels": [
     {"t": 1.0, "dur": 3, "x": 800, "y": 300 + OFF, "text": "AI 摘要：先跳過", "color": "gray", "size": 26},
     {"t": 5.4, "dur": 99, "x": 790, "y": 160 + OFF, "text": "台灣事實查核中心 ✓", "color": "green", "size": 26},
     {"t": 6.8, "dur": 99, "x": 790, "y": 302 + OFF, "text": "MyGoPen ✓", "color": "green", "size": 26}],
   "cursor": cur((0, 640, 520), (1.0, 700, 300 + OFF), (3.6, 700, 400 + OFF), (5.0, 400, 190 + OFF), (6.6, 400, 330 + OFF), (11, 400, 330 + OFF))},
  {"dur": 11, "img": "shots/v1_mgp2.png", "chrome": chrome("MyGoPen", "mygopen.com/2026/02/ai-fraud.html"), "step": "4",
   "caption": "點進 MyGoPen 那篇", "sub": "不用整篇讀完，先看最重要的兩個地方",
   "captions": [
     {"t": 2.5, "caption": "① 看標題前面的標籤：【誤導】", "sub": "查核結果有：錯誤、誤導、易誤解、事實釐清、正確…"},
     {"t": 6.0, "caption": "② 看「你可以先知道」", "sub": "這一小段就是結論。想看依據，再往下看「查證說明」"}],
   "circles": [{"t": 2.6, "dur": 3.2, "x": 104, "y": 88 + OFF, "w": 138, "h": 42, "pad": 8}],
   "boxes": [{"t": 6.2, "dur": 99, "x": 103, "y": 359 + OFF, "w": 727, "h": 176, "style": "highlight"}],
   "cursor": cur((0, 400, 330 + OFF), (1.8, 200, 110 + OFF), (6.0, 460, 450 + OFF), (11, 460, 450 + OFF))},
  {"dur": 9, "img": "shots/v1_tfc.png", "chrome": chrome("台灣事實查核中心", "tfc-taiwan.org.tw/fact-check-reports/ai-biometric-fraud-claims-exaggerated"), "step": "5",
   "caption": "再點「台灣事實查核中心」那篇，對照看看", "sub": "紅色叉叉＝錯誤。下面那一句話是它的結論",
   "circles": [{"t": 1.2, "dur": 99, "x": 256, "y": 322 + OFF, "w": 104, "h": 104, "pad": 8}],
   "boxes": [{"t": 3.0, "dur": 99, "x": 232, "y": 470 + OFF, "w": 800, "h": 90, "style": "highlight"}],
   "labels": [{"t": 5.4, "dur": 99, "x": 330, "y": 662, "text": "兩個機構的結論一致 ✓", "color": "green", "size": 30}],
   "cursor": cur((0, 460, 450 + OFF), (1.2, 310, 372 + OFF), (3.0, 620, 515 + OFF), (9, 620, 515 + OFF))},
  title("兩個查核機構都說：說法太誇大了", "查核文章找到了 → 下一步：用自己的話整理進文件", 3.5),
]
save("五上L05_找到查核文章", v1)

# ============ V2 貼上七個欄位、設定標題 1 與標題 2 ============
D = chrome(DOCTAB, DOCURL)
BTN = {"x": 174, "y": 78 + OFF, "w": 92, "h": 30}
v2 = [
  title("貼上七個欄位，設定標題", "標題 1 ＋ 標題 2", 3),
  {"dur": 7, "img": "shots/doc2_p0.png", "imgs": [{"t": 3.0, "img": "shots/doc2_p1.png"}], "chrome": D, "step": "1",
   "caption": "文件第一行，按 Ctrl＋Shift＋V 貼上", "sub": "貼上老師給的 8 行：標題 ＋ 7 個欄位名稱（不套用格式）",
   "keys": [{"t": 0.8, "dur": 2.2, "keys": ["Ctrl", "Shift", "V"], "x": 640, "y": 560}],
   "labels": [{"t": 3.6, "dur": 99, "x": 760, "y": 300 + OFF, "text": "貼好了：全部都是「內文」", "color": "gray", "size": 26}],
   "cursor": cur((0, 700, 450), (0.6, 300, 176 + OFF, "ibeam"), (7, 300, 176 + OFF, "ibeam"))},
  {"dur": 5, "img": "shots/doc2_p1.png", "imgs": [{"t": 2.2, "img": "shots/doc2_p2.png"}], "chrome": D, "step": "2",
   "caption": "選取第一行（連點滑鼠三下）", "sub": "這一行要當整份文件的標題",
   "boxes": [{"t": 1.0, "dur": 99, "x": 220, "y": 157 + OFF, "w": 840, "h": 38, "style": "select", "grow": 1.0}],
   "clicks": [{"t": 0.6, "x": 400, "y": 176 + OFF}, {"t": 0.9, "x": 400, "y": 176 + OFF}, {"t": 1.2, "x": 400, "y": 176 + OFF}],
   "cursor": cur((0, 760, 400), (0.5, 400, 176 + OFF, "ibeam"), (5, 400, 176 + OFF, "ibeam"))},
  {"dur": 8, "img": "shots/doc2_p2.png", "imgs": [{"t": 1.6, "img": "shots/doc2_p3.png"}, {"t": 5.2, "img": "shots/doc2_p4.png"}], "chrome": D, "step": "3",
   "caption": "按左上角「內文」→ 選「標題 1」", "sub": "字變大了，按鈕也變成「標題 1」",
   "circles": [{"t": 0.3, "dur": 1.5, "x": BTN["x"], "y": BTN["y"], "w": BTN["w"], "h": BTN["h"], "pad": 10}],
   "boxes": [{"t": 2.2, "dur": 2.6, "x": 150, "y": 244 + OFF, "w": 270, "h": 46, "style": "highlight"}],
   "clicks": [{"t": 1.4, "x": 218, "y": 93 + OFF}, {"t": 4.6, "x": 230, "y": 267 + OFF}],
   "labels": [{"t": 6.0, "dur": 99, "x": 480, "y": 90 + OFF, "text": "標題 1 ✓", "color": "green", "size": 28}],
   "cursor": cur((0, 400, 176 + OFF), (1.2, 218, 93 + OFF), (4.4, 230, 267 + OFF), (8, 230, 267 + OFF))},
  {"dur": 10, "img": "shots/doc2_p4.png", "imgs": [{"t": 1.6, "img": "shots/doc2_p5.png"}, {"t": 3.8, "img": "shots/doc2_p6.png"}, {"t": 6.6, "img": "shots/doc2_p7.png"}], "chrome": D, "step": "4",
   "caption": "欄位名稱：選取 → 按鈕 → 「標題 2」", "sub": "例：選「我選的訊息」，改成標題 2",
   "boxes": [{"t": 1.4, "dur": 2.2, "x": 220, "y": 209 + OFF, "w": 840, "h": 38, "style": "select", "grow": 0.8},
             {"t": 4.4, "dur": 2.0, "x": 150, "y": 290 + OFF, "w": 270, "h": 40, "style": "highlight"}],
   "circles": [{"t": 2.6, "dur": 1.1, "x": BTN["x"], "y": BTN["y"], "w": BTN["w"], "h": BTN["h"], "pad": 10}],
   "clicks": [{"t": 1.0, "x": 360, "y": 228 + OFF}, {"t": 1.3, "x": 360, "y": 228 + OFF}, {"t": 1.6, "x": 360, "y": 228 + OFF}, {"t": 3.4, "x": 218, "y": 93 + OFF}, {"t": 6.0, "x": 230, "y": 310 + OFF}],
   "labels": [{"t": 7.4, "dur": 99, "x": 700, "y": 225 + OFF, "text": "標題 2 ✓", "color": "green", "size": 28}],
   "cursor": cur((0, 760, 450), (0.8, 360, 228 + OFF, "ibeam"), (3.2, 218, 93 + OFF), (5.8, 230, 310 + OFF), (10, 230, 310 + OFF))},
  {"dur": 7, "img": "shots/doc2_p8.png", "chrome": D, "step": "✓",
   "caption": "7 個欄位名稱，全部都改成「標題 2」", "sub": "快速：選取一行，按 Ctrl＋Alt＋2　(標題 1 是 Ctrl＋Alt＋1)",
   "boxes": [{"t": 0.4, "dur": 99, "x": 220, "y": 157 + OFF, "w": 840, "h": 52, "style": "highlight"},
             {"t": 1.4, "dur": 99, "x": 220, "y": 209 + OFF, "w": 840, "h": 312, "style": "highlight"}]},
]
save("五上L05_標題與副標題", v2)

# ============ V3 貼網傳截圖 ============
v3 = [
  title("把網傳訊息的截圖貼進文件", "截圖 → 貼上 → 縮小 → 寫說明", 3),
  {"dur": 8, "img": "shots/v1_msg.png", "chrome": MSGCH, "step": "1",
   "caption": "按 Win＋Shift＋S，拖曳框住那則訊息", "sub": "放開滑鼠，截圖就自動複製了（不用存檔）",
   "keys": [{"t": 0.4, "dur": 1.7, "keys": ["Win", "Shift", "S"], "x": 640, "y": 560}],
   "snip": [{"t": 1.3, "dur": 3.0, "dragStart": 1.0, "dragEnd": 2.7, "x0": 200, "y0": 112 + OFF, "x1": 1080, "y1": 360 + OFF}],
   "toasts": [{"t": 4.5, "dur": 3.5, "title": "已將截圖複製到剪貼簿", "text": "可以貼到其他地方了"}],
   "cursor": cur((0, 1150, 560), (1.3, 1150, 560, "cross"), (2.3, 200, 112 + OFF, "cross"), (4.0, 1080, 360 + OFF, "cross"), (4.3, 1080, 360 + OFF), (8, 900, 560))},
  {"dur": 7, "img": "shots/doc2_v3a.png", "imgs": [{"t": 2.6, "img": "shots/doc2_v3b.png"}], "chrome": D, "step": "2",
   "caption": "切回文件，點一下空白那一行，按 Ctrl＋V", "sub": "截圖就貼進來了",
   "clicks": [{"t": 1.0, "x": 300, "y": 272 + OFF}],
   "keys": [{"t": 1.6, "dur": 2.0, "keys": ["Ctrl", "V"], "x": 640, "y": 560}],
   "labels": [{"t": 4.0, "dur": 99, "x": 760, "y": 300 + OFF, "text": "貼上了！但太大了", "color": "red", "size": 28}],
   "cursor": cur((0, 900, 500), (0.9, 300, 272 + OFF, "ibeam"), (7, 300, 272 + OFF, "ibeam"))},
  {"dur": 8, "img": "shots/doc2_v3b.png", "imgs": [{"t": 4.6, "img": "shots/doc2_v3e.png"}], "chrome": D, "step": "3",
   "caption": "抓住圖片的角落，往內拖，縮小", "sub": "圖不要比文字還大，也不要蓋住文字",
   "circles": [{"t": 0.6, "dur": 3.5, "x": 920, "y": 607 + OFF, "w": 16, "h": 16, "pad": 14}],
   "arrows": [{"t": 1.2, "dur": 3.4, "x1": 1000, "y1": 560 + OFF, "x2": 940, "y2": 620 + OFF}],
   "cursor": cur((0, 760, 300 + OFF), (1.0, 922, 609 + OFF), (1.4, 922, 609 + OFF), (4.4, 600, 447 + OFF), (4.8, 600, 447 + OFF), (8, 600, 447 + OFF))},
  {"dur": 8, "img": "shots/doc2_v3e.png", "chrome": D, "step": "4",
   "caption": "在圖片下面，打一行說明", "sub": "說明要寫：這是什麼、從哪裡來的",
   "typing": [{"t": 1.0, "dur": 99, "x": 222, "y": 453 + OFF, "text": "圖：網傳訊息（來源：臉書）", "size": 24, "cps": 7, "bgw": 540, "bgh": 34}],
   "boxes": [{"t": 5.6, "dur": 99, "x": 218, "y": 448 + OFF, "w": 400, "h": 40, "style": "highlight"}],
   "cursor": cur((0, 600, 447 + OFF), (1.0, 300, 468 + OFF, "ibeam"), (8, 300, 468 + OFF, "ibeam"))},
  {"dur": 5, "img": "shots/doc2_v3d.png", "chrome": D, "step": "✓",
   "caption": "圖放在欄位名稱下面，說明寫在圖片下面", "sub": "查證文件裡的圖，都要有說明和來源",
   "boxes": [{"t": 0.4, "dur": 99, "x": 218, "y": 253 + OFF, "w": 386, "h": 194, "style": "highlight"}]},
]
save("五上L05_貼網傳截圖", v3)

# ============ V4 超連結＋查閱日期 ============
v4 = [
  title("設定超連結，並寫查閱日期", "複製網址 → 選取文字 → Ctrl＋K → 寫日期", 3),
  {"dur": 7, "img": "shots/v1_mgp2.png", "chrome": chrome("MyGoPen", "mygopen.com/2026/02/ai-fraud.html", urlSel=[{"t": 2.2, "dur": 99}]), "step": "1",
   "caption": "在查核文章頁，點一下上面的網址列", "sub": "整條網址變藍色 → 按 Ctrl＋C 複製",
   "boxes": [{"t": 0.3, "dur": 99, "x": 116, "y": 43, "w": 1088, "h": 36}],
   "clicks": [{"t": 2.0, "x": 420, "y": 61}],
   "keys": [{"t": 3.4, "dur": 2.4, "keys": ["Ctrl", "C"], "x": 760, "y": 300}],
   "cursor": cur((0, 600, 400), (1.8, 420, 61), (7, 420, 61))},
  {"dur": 6, "img": "shots/doc2_v4a.png", "imgs": [{"t": 2.4, "img": "shots/doc2_v4b.png"}], "chrome": D, "step": "2",
   "caption": "切回文件，選取來源那一行文字", "sub": "從句首拖到句尾，整行變藍色",
   "boxes": [{"t": 0.8, "dur": 99, "x": 220, "y": 202 + OFF, "w": 560, "h": 25, "style": "select", "grow": 1.4}],
   "cursor": cur((0, 760, 400), (0.8, 221, 214 + OFF, "ibeam"), (2.2, 778, 214 + OFF, "ibeam"), (6, 778, 214 + OFF, "ibeam"))},
  {"dur": 9, "img": "shots/doc2_v4b.png", "imgs": [{"t": 1.6, "img": "shots/doc2_v4c.png"}, {"t": 6.0, "img": "shots/doc2_v4d.png"}], "chrome": D, "step": "3",
   "caption": "按 Ctrl＋K，貼上網址，按「套用」", "sub": "Ctrl＋K 是「插入連結」。網址用 Ctrl＋V 貼上",
   "keys": [{"t": 0.4, "dur": 1.5, "keys": ["Ctrl", "K"], "x": 640, "y": 560}, {"t": 2.6, "dur": 1.8, "keys": ["Ctrl", "V"], "x": 640, "y": 560}],
   "boxes": [{"t": 3.0, "dur": 99, "x": 316, "y": 380 + OFF, "w": 528, "h": 48, "style": "highlight"}],
   "clicks": [{"t": 5.6, "x": 355, "y": 462 + OFF}],
   "labels": [{"t": 6.4, "dur": 99, "x": 800, "y": 205 + OFF, "text": "藍色底線＝連結成功", "color": "green", "size": 26}],
   "cursor": cur((0, 700, 300), (4.6, 355, 462 + OFF), (5.6, 355, 462 + OFF), (9, 355, 462 + OFF))},
  {"dur": 8, "img": "shots/doc2_v4d.png", "chrome": D, "step": "4",
   "caption": "在連結後面，打上「查閱日期」", "sub": "網頁可能改版或被刪掉，寫上哪一天看的，別人才知道版本",
   "typing": [{"t": 1.2, "dur": 99, "x": 784, "y": 202 + OFF, "text": "（2026/10/12 查閱）", "size": 22, "cps": 7, "bgw": 240, "bgh": 28}],
   "boxes": [{"t": 4.6, "dur": 99, "x": 780, "y": 198 + OFF, "w": 230, "h": 32, "style": "highlight"}],
   "cursor": cur((0, 700, 300), (1.2, 790, 214 + OFF, "ibeam"), (8, 790, 214 + OFF, "ibeam"))},
  {"dur": 5, "img": "shots/doc2_v4e.png", "chrome": D, "step": "✓",
   "caption": "來源清單：機構名稱＋文章標題（連結）＋查閱日期", "sub": "每一筆來源都要這樣寫",
   "boxes": [{"t": 0.4, "dur": 99, "x": 218, "y": 198 + OFF, "w": 780, "h": 34, "style": "highlight"}]},
]
save("五上L05_超連結與查閱日期", v4)
print("ok", os.listdir(os.path.join(HERE, "specs"))[-4:])
