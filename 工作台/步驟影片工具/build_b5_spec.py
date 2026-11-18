# -*- coding: utf-8 -*-
# 四上 L08：開 B5 空白文件（建立 → 自訂尺寸 → 公釐 176×250）影片規格。截圖來自 2026-11-18 老師 Canva 實錄。
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "C:/Users/Roki/.claude/projects/D------------/1fcf8187-08da-4c39-abfd-e3b031789435/tool-results/mcp-claude-in-chrome-blob-"
FF = "C:/Users/Roki/tools/ffmpeg/bin/ffmpeg.exe"
FR = {  # 名稱: (檔名片段, 高度, delogo 頭像)
 "h0": ("1794964797130-z0nxrs", 732, "drawbox=x=90:y=395:w=1470:h=340:color=0xf3f4f8:t=fill,drawbox=x=10:y=680:w=50:h=50:color=0xf3f4f8:t=fill"),
 "m0": ("1794964804866-8izbf8", 732, None),
 "m1": ("1794964812652-k7v7fm", 732, None),
 "m2": ("1794964820487-h2y7iy", 732, None),
 "m3": ("1794964828965-47uwbd", 732, None),
 "m4": ("1794964846749-b10lbh", 733, "delogo=x=1313:y=8:w=38:h=36"),
}
os.makedirs(os.path.join(HERE, "shots", "canva"), exist_ok=True)
for k, (f, h, dl) in FR.items():
    vf = (dl + "," if dl else "") + "scale=1280:-1,pad=1280:720:0:(oh-ih)/2:color=0xe9ecf3"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", SRC + f + ".jpg", "-vf", vf, "-q:v", "2",
                    os.path.join(HERE, "shots", "canva", "b5_" + k + ".png")], check=True)
def P(h, x, y):
    s = 1280 / 1568.0; return round(x * s), round((720 - h * s) / 2 + y * s)
def cur(h, *pts):
    out = []
    for t, x, y, *m in pts:
        px, py = P(h, x, y); d = {"t": t, "x": px, "y": py}
        if m: d["mode"] = m[0]
        out.append(d)
    return out
def circ(h, t, dur, x, y, w, hh, pad=8):
    s = 1280 / 1568.0; px, py = P(h, x, y); return {"t": t, "dur": dur, "x": px, "y": py, "w": round(w * s), "h": round(hh * s), "pad": pad}
def clk(h, t, x, y):
    px, py = P(h, x, y); return {"t": t, "x": px, "y": py}
def img(n): return "shots/canva/b5_%s.png" % n
H = 732
scenes = [
 {"type": "title", "dur": 2.8, "title": "開一份 B5 空白文件", "subtitle": "Canva 首頁 → 建立 → 自訂尺寸 → 176 × 250 公釐"},
 {"dur": 3.2, "img": img("h0"), "imgs": [{"t": 1.9, "img": img("m0")}], "step": "1", "caption": "左邊按「建立」", "sub": "會跳出「建立設計」視窗",
  "circles": [circ(H, 0.3, 1.5, 10, 62, 46, 52, 6)],
  "cursor": cur(H, (0, 1250, 300), (1.2, 32, 85), (3.2, 32, 85)), "clicks": [clk(H, 1.4, 32, 85)]},
 {"dur": 3.4, "img": img("m0"), "imgs": [{"t": 1.9, "img": img("m1")}], "step": "2", "caption": "左邊按「自訂尺寸」", "sub": "不要選「文件 (A4，直式)」",
  "circles": [circ(H, 0.3, 1.5, 135, 647, 230, 36, 6)],
  "cursor": cur(H, (0, 700, 400), (1.3, 198, 664), (3.4, 198, 664)), "clicks": [clk(H, 1.5, 198, 664)]},
 {"dur": 4.0, "img": img("m1"), "imgs": [{"t": 1.5, "img": img("m2")}, {"t": 2.6, "img": img("m3")}], "step": "3", "caption": "單位選「公釐」，寬打 176，高打 250", "sub": "176 × 250 公釐＝B5 紙的大小",
  "circles": [circ(H, 0.3, 1.1, 990, 136, 284, 38, 6), circ(H, 1.6, 0.9, 1000, 265, 270, 32, 6), circ(H, 2.7, 99, 408, 136, 584, 38, 6)],
  "cursor": cur(H, (0, 700, 400), (0.9, 1131, 155), (1.8, 1017, 281), (2.7, 549, 155, "ibeam"), (3.4, 840, 155, "ibeam"), (4.0, 840, 155, "ibeam")),
  "clicks": [clk(H, 1.0, 1131, 155), clk(H, 1.9, 1017, 281)]},
 {"dur": 3.4, "img": img("m3"), "imgs": [{"t": 1.9, "img": img("m4")}], "step": "4", "caption": "按「建立新設計」", "sub": "會在新的分頁打開編輯畫面",
  "circles": [circ(H, 0.3, 1.5, 1340, 136, 94, 38, 6)],
  "cursor": cur(H, (0, 840, 155), (1.3, 1386, 155), (3.4, 1386, 155)), "clicks": [clk(H, 1.5, 1386, 155)]},
 {"dur": 3.4, "img": img("m4"), "step": "✓", "caption": "出現一張空白的紙，就開好了", "sub": "上面名字寫「176 公釐 × 250 公釐」就對了",
  "circles": [circ(733, 0.4, 99, 1100, 12, 195, 30, 6)],
  "cursor": cur(733, (0, 1386, 155), (3.4, 1200, 350))},
]
with open(os.path.join(HERE, "specs", "四上L08_開B5文件.json"), "w", encoding="utf-8") as f:
    json.dump({"w": 1280, "h": 720, "band": 140, "fps": 25, "scenes": scenes}, f, ensure_ascii=False, indent=1)
print("ok")
