# -*- coding: utf-8 -*-
# 四上 L08：選範本當封面、改封面文字 兩支影片規格。截圖來自 2026-11-18 老師 Canva 實錄（1568×733）。
# made by 資訊老師黃博胤
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "C:/Users/Roki/.claude/projects/D------------/1fcf8187-08da-4c39-abfd-e3b031789435/tool-results/mcp-claude-in-chrome-blob-"
FF = "C:/Users/Roki/tools/ffmpeg/bin/ffmpeg.exe"
DL = "delogo=x=1313:y=8:w=38:h=36"
FIT = "scale=1280:-1,pad=1280:720:0:(oh-ih)/2:color=0xe9ecf3"
FR = {  # 名稱: 檔名片段
 "t0": "1794971790123-1vwzoh",   # 範本面板、搜尋框空的
 "t1": "1794971790123-mu4ie3",   # 打了「旅遊手冊」
 "t2": "1794971790123-ixunae",   # 旅遊手冊結果
 "t3": "1794971824878-tm7pgx",   # 台南 旅行 封面 結果
 "t4": "1794971834201-626igb",   # 徒步旅行 詳細頁
 "t5": "1794971842594-7jct4i",   # 封面套到紙上
 "e1": "1794971932981-4fmexe",   # 點了書名（文字工具列）
 "e2": "1794971942104-vd4qfg",   # 字型清單
 "e3": "1794971952426-nfi0vr",   # 書名拖到照片中間
}
# 原圖裡錄下來的游標，動畫游標移走後會變成「兩個游標」，用另一張同畫面、沒游標的那一塊蓋掉：
#  e1/e2：游標停在「字型」框上（e1 還有「字型」提示泡泡）→ 用 e3 的工具列
#  t4：游標停在第 2 頁縮圖上 → 用 t5 的第 2 頁縮圖；t5：游標停在第 1 頁縮圖上 → 用 t4 的第 1 頁縮圖
PATCH = {"e1": ("e3", 600, 55, 122, 75), "e2": ("e3", 600, 55, 122, 45),
         "t4": ("t5", 228, 313, 144, 186), "t5": ("t4", 80, 313, 144, 186)}
os.makedirs(os.path.join(HERE, "shots", "canva"), exist_ok=True)
def out(k): return os.path.join(HERE, "shots", "canva", "l08_" + k + ".png")
for k, f in FR.items():
    if k in PATCH:
        donor, x, y, w, h = PATCH[k]
        fc = "[1:v]crop=%d:%d:%d:%d[p];[0:v][p]overlay=%d:%d,%s,%s" % (w, h, x, y, x, y, DL, FIT)
        cmd = [FF, "-y", "-loglevel", "error", "-i", SRC + f + ".jpg", "-i", SRC + FR[donor] + ".jpg",
               "-filter_complex", fc, "-q:v", "2", out(k)]
    else:
        cmd = [FF, "-y", "-loglevel", "error", "-i", SRC + f + ".jpg", "-vf", DL + "," + FIT, "-q:v", "2", out(k)]
    subprocess.run(cmd, check=True)

H = 733
S = 1280 / 1568.0
def P(x, y): return round(x * S), round((720 - H * S) / 2 + y * S)
def cur(*pts):
    o = []
    for t, x, y, *m in pts:
        px, py = P(x, y); d = {"t": t, "x": px, "y": py}
        if m: d["mode"] = m[0]
        o.append(d)
    return o
def circ(t, dur, x, y, w, hh, pad=8):
    px, py = P(x, y); return {"t": t, "dur": dur, "x": px, "y": py, "w": round(w * S), "h": round(hh * S), "pad": pad}
def clk(t, x, y):
    px, py = P(x, y); return {"t": t, "x": px, "y": py}
def box(t, dur, x, y, w, hh, style="red"):
    px, py = P(x, y); return {"t": t, "dur": dur, "x": px, "y": py, "w": round(w * S), "h": round(hh * S), "style": style}
def lab(t, dur, x, y, text, color="red", size=22):
    px, py = P(x, y); return {"t": t, "dur": dur, "x": px, "y": py, "text": text, "color": color, "size": size}
def keys(t, dur, ks, x, y):
    px, py = P(x, y); return {"t": t, "dur": dur, "keys": ks, "x": px, "y": py}
def img(n): return "shots/canva/l08_%s.png" % n

def arw(t, dur, x1, y1, x2, y2):
    a, b = P(x1, y1); c, d = P(x2, y2); return {"t": t, "dur": dur, "x1": a, "y1": b, "x2": c, "y2": d}
def caret(t, dur, x, y, size):
    px, py = P(x, y); return {"t": t, "dur": dur, "text": "", "x": px, "y": py, "size": round(size * S)}

# 每個場景 ≥ 4.5 秒（主字卡＋副字卡讀得完再加動作時間）；換場時字卡區不淡入（bandCut），舊字不會疊到新字上。
# ---------- 影片 1：選範本 ----------
v1 = [
 {"type": "title", "dur": 4.5, "title": "選一個範本當封面", "subtitle": "範本 → 搜尋 → 點封面那一頁"},
 {"dur": 4.5, "img": img("t0"), "step": "1", "caption": "左邊按「範本」", "sub": "旁邊會打開範本清單",
  "circles": [circ(0.3, 99, 14, 70, 38, 50, 6)],
  "cursor": cur((0, 900, 380), (1.2, 33, 90), (4.5, 33, 90)), "clicks": [clk(1.4, 33, 90)]},
 {"dur": 5.2, "img": img("t0"), "imgs": [{"t": 1.5, "img": img("t1")}, {"t": 2.7, "img": img("t2")}],
  "step": "2", "caption": "搜尋框打字，按 Enter", "sub": "找不到？換字再搜：台南、旅行、封面、手冊",
  "circles": [circ(0.2, 99, 82, 68, 302, 50, 6)],
  "keys": [keys(2.0, 1.2, ["Enter"], 980, 330)],
  "cursor": cur((0, 33, 90), (0.9, 205, 93), (5.2, 205, 93)), "clicks": [clk(1.1, 205, 93)]},
 {"dur": 5.0, "img": img("t3"), "imgs": [{"t": 2.4, "img": img("t4")}],
  "step": "3", "caption": "點你喜歡的範本", "sub": "例：搜「台南 旅行 封面」有中文範本",
  "circles": [circ(0.5, 1.9, 229, 352, 141, 183, 6)],
  "cursor": cur((0, 205, 100), (1.5, 300, 447), (5.0, 300, 447)), "clicks": [clk(1.9, 300, 447)]},
 {"dur": 5.6, "img": img("t4"), "imgs": [{"t": 3.2, "img": img("t5")}],
  "step": "4", "caption": "左邊出現好幾頁，點最上面那張（封面）", "sub": "不要按「套用全部」！",
  "boxes": [box(0.3, 99, 81, 270, 289, 37, "gray-x")],
  "circles": [circ(1.2, 2.0, 82, 315, 140, 182, 6)],
  "cursor": cur((0, 300, 447), (2.2, 150, 410), (5.6, 150, 410)), "clicks": [clk(2.6, 150, 410)]},
 {"dur": 4.5, "img": img("t5"), "step": "✓", "caption": "封面放到紙上了", "sub": "照片之後再換，今天改文字",
  "circles": [circ(0.3, 99, 812, 156, 343, 446, 6)],
  "cursor": cur((0, 150, 410), (4.5, 150, 410))},
]

# ---------- 影片 2：改封面文字（3 段＋結尾，和學習單一致）----------
TX, TY = 940, 205   # 書名中間
v2 = [
 {"type": "title", "dur": 4.5, "title": "改封面的字", "subtitle": "改書名 → 字型、大小、顏色 → 移動"},
 {"dur": 6.5, "img": img("t5"), "imgs": [{"t": 1.5, "img": img("e1")}], "step": "1",
  "caption": "連按兩下書名",
  "captions": [{"t": 0, "caption": "連按兩下書名", "sub": "看到打字的直線就對了"},
               {"t": 3.0, "caption": "按 Ctrl＋A，打自己的書名", "sub": "其他字也照這樣改"}],
  "circles": [circ(1.5, 0.6, 828, 168, 284, 70, 6)],
  "typing": [caret(1.6, 1.9, 1060, 176, 58)],
  "arrows": [arw(2.0, 1.5, 1135, 290, 1068, 215)],
  "keys": [keys(3.2, 1.8, ["Ctrl", "A"], 980, 430)],
  "boxes": [box(3.5, 99, 832, 176, 226, 62, "select")],
  "cursor": cur((0, 150, 410), (1.0, TX, TY), (6.5, TX, TY)),
  "clicks": [clk(1.15, TX, TY), clk(1.4, TX, TY)]},
 {"dur": 8.0, "img": img("e1"), "imgs": [{"t": 4.2, "img": img("e2")}], "step": "2",
  "caption": "工具列：字型、大小、顏色",
  "captions": [{"t": 0, "caption": "工具列：字型、大小、顏色", "sub": "按＋／－ 字會變大、變小"},
               {"t": 3.6, "caption": "按字型，左邊點一個", "sub": "選後面寫「繁體中文」的字型"}],
  "circles": [circ(0.3, 3.3, 608, 64, 112, 30, 5), circ(1.0, 2.6, 724, 64, 86, 30, 5), circ(1.7, 1.9, 816, 64, 28, 30, 5),
              circ(3.6, 0.8, 608, 64, 112, 30, 5), circ(4.6, 99, 72, 450, 312, 34, 6)],
  "labels": [lab(0.5, 3.1, 638, 102, "字型", size=18), lab(1.2, 2.4, 736, 102, "大小", size=18), lab(1.9, 1.7, 812, 102, "顏色", size=18)],
  "cursor": cur((0, TX, TY), (3.0, TX, TY + 10), (3.8, 665, 82), (4.4, 665, 82), (5.5, 200, 466), (8.0, 200, 466)),
  "clicks": [clk(4.0, 665, 82), clk(5.7, 200, 466)]},
 {"dur": 8.0, "img": img("e1"), "imgs": [{"t": 2.4, "img": img("e3")}], "step": "3",
  "caption": "按住框拖過去；白點調大小",
  "captions": [{"t": 0, "sub": "按住書名的框，拖到想放的地方"},
               {"t": 3.0, "sub": "四個角的白點＝字一起變大小"},
               {"t": 5.5, "sub": "左右中間的白點＝只改寬度"}],
  "circles": [circ(0.3, 0.9, 828, 168, 284, 70, 6),
              circ(3.1, 2.4, 828, 265, 0, 0, 12), circ(3.2, 2.3, 1111, 265, 0, 0, 12),
              circ(3.3, 2.2, 828, 336, 0, 0, 12), circ(3.4, 2.1, 1111, 336, 0, 0, 12),
              circ(5.6, 99, 828, 300, 0, 0, 12), circ(5.7, 99, 1111, 300, 0, 0, 12)],
  "cursor": cur((0, 200, 466), (0.9, TX + 5, TY), (1.1, TX + 5, TY), (2.4, 945, 305), (8.0, 945, 305))},
 {"dur": 4.5, "img": img("e3"), "step": "✓", "caption": "封面的字改好了", "sub": "書名、副標題都換成你的",
  "cursor": cur((0, 945, 305), (4.5, 945, 305))},
]

for name, sc in (("四上L08_選範本", v1), ("四上L08_改封面文字", v2)):
    with open(os.path.join(HERE, "specs", name + ".json"), "w", encoding="utf-8") as f:
        json.dump({"w": 1280, "h": 720, "band": 140, "fps": 25, "bandCut": True, "scenes": sc}, f, ensure_ascii=False, indent=1)
    print(name, round(sum(s["dur"] for s in sc), 1), "s")
