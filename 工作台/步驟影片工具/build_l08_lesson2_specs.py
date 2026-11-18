# -*- coding: utf-8 -*-
# 四上 L08 第 2 課：Google地圖路線、截圖貼上 兩組步驟圖的 spec。
# 地圖畫面：cap_l08b_*.ps1 用另開的 Chrome（CDP）截的 1280×720（shots/l08b/m*.png）。
# Canva 畫面：2026-11-19 在老師帳號新開的 B5 草稿（176×250 公釐）截的 1568×733，檔名片段見 CV。
# made by 資訊老師黃博胤
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "C:/Users/Roki/.claude/projects/D------------/1fcf8187-08da-4c39-abfd-e3b031789435/tool-results/mcp-claude-in-chrome-blob-"
FF = "C:/Users/Roki/tools/ffmpeg/bin/ffmpeg.exe"
DL = "delogo=x=1313:y=8:w=38:h=36"      # 右上角帳號頭像（含名字）
FIT = "scale=1280:-1,pad=1280:720:0:(oh-ih)/2:color=0xe9ecf3"
CV = {"cv0": "1795018538138-2cs0wa",   # 第 4 頁選取、只有標題
      "cv1": "1795018595306-m76343",   # 地圖放到紙上
      "cv2": "1795018612117-44tz2b",   # 拉大、標題下面
      "cv3": "1795018643853-jo03sy"}   # 加小字
os.makedirs(os.path.join(HERE, "shots", "l08b"), exist_ok=True)
for k, f in CV.items():
    out = os.path.join(HERE, "shots", "l08b", k + ".png")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", SRC + f + ".jpg", "-vf", DL + "," + FIT, "-q:v", "2", out], check=True)

def m(n): return "shots/l08b/%s.png" % n
def cur(*pts):
    o = []
    for t, x, y, *mm in pts:
        d = {"t": t, "x": x, "y": y}
        if mm: d["mode"] = mm[0]
        o.append(d)
    return o
def circ(t, dur, x, y, w, h, pad=8):   # x,y 給圓心；spec 要左上角
    return {"t": t, "dur": dur, "x": x - w // 2, "y": y - h // 2, "w": w, "h": h, "pad": pad}
def clk(t, x, y): return {"t": t, "x": x, "y": y}
def keys(t, dur, ks, x, y): return {"t": t, "dur": dur, "keys": ks, "x": x, "y": y}

# ---------- Google地圖路線 ----------
v1 = [
 {"type": "title", "dur": 4.5, "title": "用 Google 地圖排路線", "subtitle": "路線 → 起點終點 → 機車 → 新增目的地"},
 {"dur": 5.0, "img": m("m0"), "step": "1", "caption": "打開 Google 地圖，按「路線」", "sub": "搜尋框旁邊的藍色箭頭",
  "circles": [circ(0.3, 99, 437, 36, 36, 36, 8)],
  "cursor": cur((0, 900, 400), (1.2, 437, 36), (5, 437, 36)), "clicks": [clk(1.4, 437, 36)]},
 {"dur": 6.0, "img": m("m1"), "imgs": [{"t": 2.2, "img": m("m2a")}], "step": "2", "caption": "起點打「赤崁樓」", "sub": "跳出選單，點第一個",
  "circles": [circ(0.3, 99, 276, 114, 282, 40, 6)],
  "cursor": cur((0, 437, 36), (0.9, 276, 114), (3.6, 276, 114), (4.4, 230, 227), (6, 230, 227)),
  "clicks": [clk(1.0, 276, 114), clk(4.6, 230, 227)]},
 {"dur": 5.0, "img": m("m2b"), "step": "3", "caption": "終點打「安平古堡」", "sub": "一樣點選單裡的第一個",
  "circles": [circ(0.3, 99, 276, 162, 282, 40, 6)],
  "cursor": cur((0, 230, 227), (1.0, 276, 162), (5, 276, 162)), "clicks": [clk(1.2, 276, 162)]},
 {"dur": 5.2, "img": m("m3"), "imgs": [{"t": 2.4, "img": m("m4")}], "step": "4", "caption": "交通方式選「機車」", "sub": "小機車的圖示，時間會跟著變",
  "circles": [circ(0.3, 99, 251, 52, 58, 58, 6)],
  "cursor": cur((0, 276, 162), (1.4, 251, 49), (5.2, 251, 49)), "clicks": [clk(1.6, 251, 49)]},
 {"dur": 8.0, "img": m("m5"), "imgs": [{"t": 3.0, "img": m("m6")}, {"t": 4.4, "img": m("m7")}, {"t": 5.8, "img": m("m8c")}],
  "step": "5", "caption": "按「新增目的地」", "sub": "多出一格，打下一站（也要選第一個）",
  "captions": [{"t": 0, "caption": "按「新增目的地」", "sub": "多出一格，打下一站（也要選第一個）"},
               {"t": 3.0, "caption": "一站一站加，照順序", "sub": "府城食府 → 安平老街 → 安平貴記"}],
  "circles": [circ(0.3, 2.5, 160, 212, 134, 36, 6), circ(5.9, 99, 160, 356, 134, 36, 6)],
  "cursor": cur((0, 251, 49), (1.0, 108, 212), (3.0, 108, 212), (5.6, 108, 356), (8, 108, 356)),
  "clicks": [clk(1.2, 108, 212), clk(5.7, 108, 356)]},
 {"dur": 9.0, "img": m("m8c"), "step": "6", "caption": "整條路線出現了", "sub": "地圖上有路線，旁邊寫著總時間",
  "captions": [{"t": 0, "caption": "整條路線出現了", "sub": "地圖上有路線，旁邊寫著總時間"},
               {"t": 4.5, "caption": "每段幾分鐘，看你的文件就好", "sub": "你在 L05 已經查過了"}],
  "circles": [circ(0.3, 4.2, 846, 288, 66, 44, 8), circ(4.6, 99, 432, 522, 70, 34, 8)],
  "cursor": cur((0, 108, 356), (1.0, 900, 330), (9, 900, 330))},
]

# ---------- 截圖貼上 ----------
S = 1280 / 1568.0
def P(x, y): return round(x * S), round((720 - 733 * S) / 2 + y * S)
def cc(t, dur, x, y, w, h, pad=8):
    px, py = P(x, y); return {"t": t, "dur": dur, "x": px, "y": py, "w": round(w * S), "h": round(h * S), "pad": pad}
def ccur(*pts): return [dict(zip(("t", "x", "y"), (t,) + P(x, y))) for t, x, y in pts]
def cclk(t, x, y):
    px, py = P(x, y); return {"t": t, "x": px, "y": py}
def ckeys(t, dur, ks, x, y):
    px, py = P(x, y); return {"t": t, "dur": dur, "keys": ks, "x": px, "y": py}
def cv(n): return "shots/l08b/%s.png" % n

v2 = [
 {"type": "title", "dur": 4.5, "title": "把地圖截下來，貼到 Canva", "subtitle": "Win＋Shift＋S → 框起來 → 回 Canva 貼上"},
 {"dur": 4.8, "img": m("m9"), "step": "1", "caption": "在地圖畫面按 Win＋Shift＋S", "sub": "三個鍵一起按，畫面會變暗",
  "keys": [keys(0.5, 99, ["Win", "Shift", "S"], 640, 360)], "cursor": cur((0, 900, 450), (4.8, 900, 450))},
 {"dur": 6.0, "img": m("m9"), "step": "2", "caption": "拖一個框，把路線框起來", "sub": "放開滑鼠，圖就複製好了",
  "snip": [{"t": 0.3, "dur": 99, "dragStart": 0.8, "dragEnd": 2.8, "x0": 520, "y0": 190, "x1": 1260, "y1": 540}],
  "cursor": cur((0, 900, 450), (0.8, 520, 190, "cross"), (2.8, 1260, 540, "cross"), (6, 1260, 540, "cross"))},
 {"dur": 5.0, "img": cv("cv0"), "step": "3", "caption": "回到 Canva，點第 4 頁「路線圖」的紙", "sub": "紙的外框變紫色就對了",
  "circles": [cc(0.4, 99, 810, 135, 348, 493, 6)],
  "cursor": ccur((0, 400, 400), (1.3, 983, 520), (5, 983, 520)), "clicks": [cclk(1.5, 983, 520)]},
 {"dur": 5.2, "img": cv("cv0"), "imgs": [{"t": 2.4, "img": cv("cv1")}], "step": "4", "caption": "按 Ctrl＋V", "sub": "地圖出現在紙上了",
  "keys": [ckeys(0.5, 1.9, ["Ctrl", "V"], 330, 560)],
  "circles": [cc(2.8, 99, 712, 331, 210, 99, 6)],
  "cursor": ccur((0, 983, 520), (5.2, 983, 520))},
 {"dur": 8.0, "img": cv("cv1"), "imgs": [{"t": 4.4, "img": cv("cv2")}], "step": "5", "caption": "拉四個角的白點，把地圖變大",
  "captions": [{"t": 0, "caption": "拉四個角的白點，把地圖變大", "sub": "角落的白點＝整張圖一起放大"},
               {"t": 4.4, "caption": "拖到標題下面，剛剛好", "sub": "按住地圖的中間就能拖"}],
  "circles": [cc(0.3, 4.0, 712, 331, 0, 0, 12), cc(0.4, 3.9, 921, 331, 0, 0, 12), cc(0.5, 3.8, 712, 430, 0, 0, 12), cc(0.6, 3.7, 921, 430, 0, 0, 12),
              cc(4.6, 99, 650, 252, 340, 160, 6)],
  "cursor": ccur((0, 983, 520), (1.0, 921, 430), (3.8, 984, 410), (8, 984, 410))},
 {"dur": 6.0, "img": cv("cv3"), "step": "6", "caption": "在地圖下面加一行小字", "sub": "寫上「圖片：Google 地圖」，說明圖從哪來",
  "circles": [cc(0.4, 99, 758, 427, 120, 18, 10)],
  "cursor": ccur((0, 984, 410), (1.2, 816, 436), (6, 816, 436))},
]

for name, sc in (("四上L08_Google地圖路線", v1), ("四上L08_截圖貼上", v2)):
    with open(os.path.join(HERE, "specs", name + ".json"), "w", encoding="utf-8") as f:
        json.dump({"w": 1280, "h": 720, "band": 140, "fps": 25, "bandCut": True, "scenes": sc}, f, ensure_ascii=False, indent=1)
    print(name, round(sum(s["dur"] for s in sc), 1), "s")
