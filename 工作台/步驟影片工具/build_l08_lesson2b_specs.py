# -*- coding: utf-8 -*-
# 四上 L08 第 2 課：新增頁面／加文字／目錄靠左列點 三組步驟圖（Canva「頁面上下排列」直式畫面）的 spec。
# Canva 畫面：2026-11-19 在老師帳號的 B5 草稿 DAHbSPgy-tQ（176×250 公釐）截的 1568×776，縮放 61%。
# made by 資訊老師黃博胤
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "C:/Users/Roki/.claude/projects/D------------/1fcf8187-08da-4c39-abfd-e3b031789435/tool-results/mcp-claude-in-chrome-blob-"
FF = "C:/Users/Roki/tools/ffmpeg/bin/ffmpeg.exe"
DL = "delogo=x=1313:y=8:w=38:h=36"      # 右上角帳號頭像（含名字）
FIT = "scale=1280:-1,pad=1280:720:0:(oh-ih)/2:color=0xe9ecf3"
SW, SH = 1568.0, 776.0
S = 1280 / SW
CV = {
 # 新增頁面
 "a0": "1795047332263-7k6knr", "a1": "1795047333215-e6w9ns", "a2": "1795047347096-pfcvow", "a3": "1795047358881-3gn6wh",
 # 加文字
 "b0": "1795047384898-ws7j9n", "b1": "1795047386847-xq6x8l", "b2": "1795047394623-sotjxq", "b3": "1795047409847-mdjabd",
 "b4": "1795047414369-60dfw3", "b5": "1795047423200-t6p4up", "b6": "1795047447428-h7cays",
 # 目錄
 "c0": "1795047465784-db0v2m", "c1": "1795047466947-7xdjhw", "c2": "1795047504933-cpq32e", "c3": "1795047518650-b3aeqy",
 "c4": "1795047519599-9qxyhy", "c5": "1795047527584-sghcjn", "c6": "1795047528553-4xpkda"}
os.makedirs(os.path.join(HERE, "shots", "l08c"), exist_ok=True)
for k, f in CV.items():
    out = os.path.join(HERE, "shots", "l08c", k + ".png")
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", SRC + f + ".jpg", "-vf", DL + "," + FIT, "-q:v", "2", out], check=True)

def P(x, y): return round(x * S), round((720 - SH * S) / 2 + y * S)
def im(n): return "shots/l08c/%s.png" % n
def cc(t, dur, x, y, w, h, pad=8):   # x,y 給圓心（原圖座標）
    px, py = P(x - w / 2.0, y - h / 2.0); return {"t": t, "dur": dur, "x": px, "y": py, "w": round(w * S), "h": round(h * S), "pad": pad}
def cur(*pts): return [dict(zip(("t", "x", "y"), (t,) + P(x, y))) for t, x, y in pts]
def clk(t, x, y):
    px, py = P(x, y); return {"t": t, "x": px, "y": py}
def keys(t, dur, ks, x, y):
    px, py = P(x, y); return {"t": t, "dur": dur, "keys": ks, "x": px, "y": py}

# ---------- 新增頁面 ----------
BTN = (802, 707)
v1 = [
 {"type": "title", "dur": 4.0, "title": "新增頁面", "subtitle": "捲到最下面 → 按「＋ 新增頁面」"},
 {"dur": 5.0, "img": im("a0"), "step": "1", "caption": "捲到最下面，找到「＋ 新增頁面」", "sub": "頁面下方那顆寬寬的按鈕",
  "circles": [cc(0.3, 99, BTN[0], BTN[1], 380, 40, 6)],
  "cursor": cur((0, 1200, 300), (1.4, BTN[0], BTN[1]), (5, BTN[0], BTN[1]))},
 {"dur": 5.0, "img": im("a0"), "imgs": [{"t": 2.6, "img": im("a1")}], "step": "2", "caption": "按一下，多出第 2 頁", "sub": "新的頁面是空白的",
  "circles": [cc(0.3, 99, BTN[0], BTN[1], 380, 40, 6)],
  "cursor": cur((0, 1200, 300), (1.0, BTN[0], BTN[1]), (5, BTN[0], BTN[1])), "clicks": [clk(1.3, BTN[0], BTN[1])]},
 {"dur": 6.0, "img": im("a1"), "imgs": [{"t": 3.4, "img": im("a2")}], "step": "3", "caption": "再按兩次，一共 4 頁：封面、目錄、行程規劃、路線圖", "sub": "頁面會一頁一頁往下排",
  "circles": [cc(0.3, 99, BTN[0], BTN[1], 380, 40, 6)],
  "cursor": cur((0, BTN[0], BTN[1]), (6, BTN[0], BTN[1])), "clicks": [clk(1.0, BTN[0], BTN[1]), clk(2.0, BTN[0], BTN[1])]},
 {"dur": 5.0, "img": im("a3"), "step": "4", "caption": "不小心多按了？點頁面上方的垃圾桶刪掉", "sub": "要刪哪一頁，就點那一頁上面的垃圾桶",
  "circles": [cc(0.3, 99, 958, 396, 34, 34, 8)],
  "cursor": cur((0, 1200, 300), (1.4, 958, 396), (5, 958, 396))},
]

# ---------- 加文字 ----------
v2 = [
 {"type": "title", "dur": 4.0, "title": "給每一頁打標題", "subtitle": "文字 → 新增標題 → 連按兩下 → 直接打字"},
 {"dur": 5.0, "img": im("b0"), "step": "1", "caption": "點左邊的「文字」", "sub": "先到第 2 頁，要打標題了",
  "circles": [cc(0.3, 99, 33, 226, 52, 72, 6)],
  "cursor": cur((0, 1200, 400), (1.4, 33, 226), (5, 33, 226)), "clicks": [clk(1.6, 33, 226)]},
 {"dur": 5.2, "img": im("b1"), "imgs": [{"t": 2.6, "img": im("b2")}], "step": "2", "caption": "點「新增標題」", "sub": "頁面上出現「新增標題」四個字",
  "circles": [cc(0.3, 99, 225, 372, 290, 58, 6)],
  "cursor": cur((0, 33, 226), (1.2, 225, 372), (5.2, 225, 372)), "clicks": [clk(1.5, 225, 372)]},
 {"dur": 7.0, "img": im("b2"), "imgs": [{"t": 2.4, "img": im("b3")}, {"t": 4.4, "img": im("b4")}], "step": "3",
  "caption": "連按兩下，Ctrl＋A，直接打字", "sub": "打「目錄」，舊的字就被換掉了",
  "keys": [keys(2.5, 1.6, ["Ctrl", "A"], 983, 520)],
  "circles": [cc(0.3, 99, 983, 435, 190, 70, 6)],
  "cursor": cur((0, 225, 372), (1.0, 983, 435), (7, 983, 435)), "clicks": [clk(1.3, 983, 435), clk(1.6, 983, 435)]},
 {"dur": 5.0, "img": im("b4"), "imgs": [{"t": 2.8, "img": im("b5")}], "step": "4", "caption": "按住文字，拖到頁面上方中間", "sub": "標題放在紙的最上面",
  "circles": [cc(0.3, 2.5, 983, 435, 110, 66, 6)],
  "cursor": cur((0, 1250, 450), (0.8, 983, 435), (1.2, 983, 435), (2.6, 983, 235), (5, 983, 235))},
 {"dur": 6.0, "img": im("b6"), "step": "5", "caption": "每一頁都這樣打好標題", "sub": "第 3 頁打「行程規劃」，第 4 頁打「路線圖」",
  "circles": [cc(0.3, 99, 983, 262, 190, 70, 6)],
  "cursor": cur((0, 1250, 450), (6, 1250, 450))},
]

# ---------- 目錄靠左列點 ----------
v3 = [
 {"type": "title", "dur": 4.0, "title": "做目錄", "subtitle": "打章節名 → 靠左 → 加圓點"},
 {"dur": 5.2, "img": im("c0"), "imgs": [{"t": 2.6, "img": im("c1")}], "step": "1", "caption": "文字 →「新增少量內文文字」", "sub": "頁面上多出一個小字的框",
  "circles": [cc(0.3, 99, 225, 484, 290, 44, 6)],
  "cursor": cur((0, 1250, 450), (1.2, 225, 484), (5.2, 225, 484)), "clicks": [clk(1.5, 225, 484)]},
 {"dur": 7.0, "img": im("c1"), "imgs": [{"t": 3.4, "img": im("c2")}], "step": "2", "caption": "一行一個章節，先不用打頁碼", "sub": "打完一行，按 Enter 換下一行",
  "keys": [keys(0.8, 1.4, ["Ctrl", "A"], 983, 640), keys(2.2, 1.6, ["Enter"], 983, 640)],
  "cursor": cur((0, 1250, 450), (7, 1250, 450))},
 {"dur": 7.0, "img": im("c2"), "imgs": [{"t": 2.8, "img": im("c3")}, {"t": 4.6, "img": im("c4")}], "step": "3", "caption": "連按兩下，Ctrl＋A，按上面的「對齊」", "sub": "字就靠左了",
  "keys": [keys(0.9, 1.6, ["Ctrl", "A"], 983, 560)],
  "circles": [cc(2.9, 99, 1029, 78, 36, 36, 8)],
  "cursor": cur((0, 1250, 450), (0.4, 983, 517), (2.4, 983, 517), (3.4, 1029, 78), (7, 1029, 78)),
  "clicks": [clk(0.5, 983, 517), clk(0.8, 983, 517), clk(3.6, 1029, 78)]},
 {"dur": 5.2, "img": im("c4"), "imgs": [{"t": 2.6, "img": im("c5")}], "step": "4", "caption": "按「項目符號」", "sub": "每一行前面出現圓點",
  "circles": [cc(0.3, 99, 1063, 78, 36, 36, 8)],
  "cursor": cur((0, 1029, 78), (1.2, 1063, 78), (5.2, 1063, 78)), "clicks": [clk(1.5, 1063, 78)]},
 {"dur": 6.0, "img": im("c6"), "step": "5", "caption": "靠左、有圓點，就是目錄了", "sub": "每一行是一個章節名",
  "circles": [cc(0.3, 99, 1000, 505, 215, 190, 8)],
  "cursor": cur((0, 1063, 78), (1.2, 1250, 450), (6, 1250, 450))},
]

for name, sc in (("四上L08_新增頁面_直式", v1), ("四上L08_加文字_直式", v2), ("四上L08_目錄靠左列點_直式", v3)):
    with open(os.path.join(HERE, "specs", name + ".json"), "w", encoding="utf-8") as f:
        json.dump({"w": 1280, "h": 720, "band": 140, "fps": 25, "bandCut": True, "scenes": sc}, f, ensure_ascii=False, indent=1)
    print(name, round(sum(s["dur"] for s in sc), 1), "s")
