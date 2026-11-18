# -*- coding: utf-8 -*-
# 四上 L08：把 Canva 步驟影片轉成「步驟圖」（每個非字卡場景取 1～2 張，含下方字卡），給學習單用。
# 來源：render.ps1 留下的逐格 PNG（frames_out_<spec>），和 out_<spec>.mp4 同一批，畫質比壓縮後的 mp4 好。
# 輸出：materials\四年級上學期\L08_Canva導覽手冊\assets\步圖\{影片名}_{01..}.jpg ＋ index.json
# made by 資訊老師黃博胤
import json, os, subprocess, glob
HERE = os.path.dirname(os.path.abspath(__file__))
FF = "C:/Users/Roki/tools/ffmpeg/bin/ffmpeg.exe"
OUT = os.path.join(HERE, "..", "..", "materials", "四年級上學期", "L08_Canva導覽手冊", "assets", "步圖")
VIDEOS = [  # 影片名（assets 檔名去掉「步_canva_」）: spec 名
 ("開B5文件", "四上L08_開B5文件"), ("選範本", "四上L08_選範本"), ("改封面文字", "四上L08_改封面文字"),
 ("改檔名", "四上L10_改檔名"), ("加文字", "四上L10_加文字"), ("加照片", "四上L10_加照片"),
 ("新增頁面", "四上L10_新增頁面"), ("目錄靠左列點", "四上L10_目錄靠左列點"), ("分享連結", "四上L10_分享連結"),
 ("Google地圖路線", "四上L08_Google地圖路線"), ("截圖貼上", "四上L08_截圖貼上"),
]
# 只重做指定的操作（保留其他組的圖與 index.json）：python export_l08_steps.py Google地圖路線 截圖貼上
import sys
ONLY = sys.argv[1:]
FPS = 25
OVER = ("circles", "boxes", "labels", "keys", "arrows", "typing")

def live(sc, t):
    """t 時畫面上「已畫好」的標記（圈圈畫完要 0.5 秒）"""
    s = set()
    for k in OVER:
        for i, b in enumerate(sc.get(k, [])):
            st, du = b.get("t", 0), b.get("dur", 999)
            ready = 0.55 if k in ("circles", "arrows") else 0.3
            if st + ready <= t < st + du:
                s.add((k, i))
    return s

def img_at(sc, t):
    im = sc.get("img")
    for sw in sc.get("imgs", []):
        if t >= sw["t"]: im = sw["img"]
    return im

def moving(sc, t):
    kf = sc.get("cursor", [])
    for a, b in zip(kf, kf[1:]):
        if a["t"] <= t < b["t"] and (a["x"], a["y"]) != (b["x"], b["y"]): return True
    return False

def clicks_done(sc, t):
    return sum(1 for c in sc.get("clicks", []) if c["t"] + 0.5 <= t)

def band(sc, t):
    cap, sub = sc.get("caption"), sc.get("sub")
    for c in sc.get("captions", []):
        if t >= c.get("t", 0): cap = c.get("caption", cap); sub = c.get("sub", sub)
    return cap or "", sub or ""

def pick(sc):
    """回傳場景內要截的時間（場景內秒數）"""
    dur = sc["dur"]
    cuts = sorted({c.get("t", 0) for c in sc.get("captions", []) if c.get("t", 0) > 0})
    bounds = [0] + cuts + [dur]
    res = []
    for a, b in zip(bounds, bounds[1:]):
        ts = [round(a + 0.45 + i * 0.04, 2) for i in range(int((b - a - 0.57) / 0.04) + 1)]
        ts = [t for t in ts if t <= b - 0.12] or [round((a + b) / 2, 2)]
        final_img = img_at(sc, ts[-1])
        def score(t): return (len(live(sc, t)), clicks_done(sc, t), not moving(sc, t), t)
        fin = max([t for t in ts if img_at(sc, t) == final_img], key=score)
        best = max(ts, key=lambda t: (len(live(sc, t)), not moving(sc, t), clicks_done(sc, t), t))
        lb, lf = live(sc, best), live(sc, fin)
        if lb - lf and lb:          # 有圈圈只在換圖前出現 → 多取一張
            res.append(best)
        res.append(fin)
    return res

os.makedirs(OUT, exist_ok=True)
idx_path = os.path.join(OUT, "index.json")
if ONLY:
    index = json.load(open(idx_path, encoding="utf-8"))
    for n in ONLY:
        for f in glob.glob(os.path.join(OUT, n + "_*.jpg")): os.remove(f)
else:
    for f in glob.glob(os.path.join(OUT, "*.jpg")): os.remove(f)
    index = {}
report = []
for name, sp in VIDEOS:
    if ONLY and name not in ONLY: continue
    spec = json.load(open(os.path.join(HERE, "specs", sp + ".json"), encoding="utf-8"))
    fdir = os.path.join(HERE, "frames_out_" + sp)
    nfr = len(glob.glob(os.path.join(fdir, "f*.png")))
    total = sum(int(round(s["dur"] * FPS)) for s in spec["scenes"])
    assert nfr == total, "%s 逐格數 %d ≠ spec %d（請重渲染）" % (sp, nfr, total)
    start, items, k = 0, [], 0
    for sc in spec["scenes"]:
        n = int(round(sc["dur"] * FPS))
        if sc.get("type") != "title":
            for t in pick(sc):
                fi = min(start + int(round(t * FPS)), start + n - 1)
                k += 1
                fn = "%s_%02d.jpg" % (name, k)
                subprocess.run([FF, "-y", "-loglevel", "error", "-i", os.path.join(fdir, "f%05d.png" % fi), "-q:v", "3",
                                os.path.join(OUT, fn)], check=True)
                cap, sub = band(sc, t)
                items.append({"file": fn, "step": sc.get("step", ""), "caption": cap, "sub": sub})
                report.append("%s  scene@%.2f+%.2f  frame %d" % (fn, start / FPS, t, fi))
        start += n
    index[name] = items
with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=1)
print("\n".join(report))
print({k: len(v) for k, v in index.items()})
