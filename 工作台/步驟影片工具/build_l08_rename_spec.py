# -*- coding: utf-8 -*-
# 四上 L08：改檔名影片（畫面沿用 build_l10b_specs.py 的 a0～a3，舊實錄 1568×776）。
# 只重寫這一支，不動 b 腳本裡其他影片。每場 ≥ 4.5 秒，換場字卡不疊字（bandCut）。
# made by 資訊老師黃博胤
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "C:/Users/Roki/.claude/projects/D------------/1fcf8187-08da-4c39-abfd-e3b031789435/tool-results/mcp-claude-in-chrome-blob-"
FF = "C:/Users/Roki/tools/ffmpeg/bin/ffmpeg.exe"
OLD = {"a0": "1794904977091-y885h4", "a1": "1794904996225-9pg7tn", "a2": "1794904996225-pq0rmh", "a3": "1794904996225-t1v2h9"}
os.makedirs(os.path.join(HERE, "shots", "canva"), exist_ok=True)
for k, f in OLD.items():   # 和 b 腳本同一套前處理
    vf = "delogo=x=1166:y=8:w=40:h=36,scale=1280:-1,pad=1280:720:0:(oh-ih)/2:color=0xe9ecf3"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", SRC + f + ".jpg", "-vf", vf, "-q:v", "2",
                    os.path.join(HERE, "shots", "canva", k + ".png")], check=True)
H = 776
S = 1280 / 1568.0
def P(x, y): return round(x * S), round((720 - H * S) / 2 + y * S)
def cur(*pts): return [dict(zip(("t", "x", "y"), (t,) + P(x, y))) for t, x, y in pts]
def circ(t, dur, x, y, w, hh, pad=8):
    px, py = P(x, y); return {"t": t, "dur": dur, "x": px, "y": py, "w": round(w * S), "h": round(hh * S), "pad": pad}
def clk(t, x, y):
    px, py = P(x, y); return {"t": t, "x": px, "y": py}
def img(n): return "shots/canva/%s.png" % n
scenes = [
 {"dur": 4.5, "img": img("a0"), "step": "1", "caption": "點右上角的作品名字", "sub": "框會亮起來。你的紙是白的沒關係",
  "circles": [circ(0.5, 99, 1000, 8, 150, 36)],
  "cursor": cur((0, 600, 400), (1.6, 1075, 26), (4.5, 1075, 26)), "clicks": [clk(1.7, 1075, 26)]},
 {"dur": 4.5, "img": img("a1"), "step": "2", "caption": "按 Ctrl＋A　全選", "sub": "舊的名字會整個選起來",
  "keys": [{"t": 0.4, "dur": 2.2, "keys": ["Ctrl", "A"], "x": 640, "y": 330}], "cursor": cur((0, 1075, 26), (4.5, 1075, 26))},
 {"dur": 5.0, "img": img("a1"), "imgs": [{"t": 2.0, "img": img("a2")}], "step": "3", "caption": "貼上新的名字",
  "sub": "貼上學習單上的名字（Ctrl＋V）",
  "keys": [{"t": 0.4, "dur": 1.6, "keys": ["Ctrl", "V"], "x": 640, "y": 330}],
  "cursor": cur((0, 1075, 26), (5.0, 1075, 26))},
 {"dur": 4.5, "img": img("a2"), "imgs": [{"t": 1.6, "img": img("a3")}], "step": "4", "caption": "按 Enter　完成", "sub": "名字改好了",
  "keys": [{"t": 0.3, "dur": 1.3, "keys": ["Enter"], "x": 640, "y": 330}], "cursor": cur((0, 1075, 26), (4.5, 1075, 26))},
]
with open(os.path.join(HERE, "specs", "四上L10_改檔名.json"), "w", encoding="utf-8") as f:
    json.dump({"w": 1280, "h": 720, "band": 140, "fps": 25, "bandCut": True, "scenes": scenes}, f, ensure_ascii=False, indent=1)
print("四上L10_改檔名", sum(s["dur"] for s in scenes), "s")
