# -*- coding: utf-8 -*-
# 四上 L10（Canva 小書）4 支步驟影片的規格：截圖來自老師 Canva（2026-11-17 實錄畫面，頭像已遮），
# 截圖 1568×776 → 縮成 1280×634（shots/canva/*.png），畫面下方字卡 band=86（720−86=634）。
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
S = 580 / 776.0
OX = (1280 - 1568 * S) / 2
def p(x, y): return round(OX + x * S), round(y * S)

def cur(*pts):
    out = []
    for t, x, y, *m in pts:
        px, py = p(x, y)
        d = {"t": t, "x": px, "y": py}
        if m: d["mode"] = m[0]
        out.append(d)
    return out

def circ(t, dur, x, y, w, h, pad=10):
    px, py = p(x, y)
    return {"t": t, "dur": dur, "x": px, "y": py, "w": round(w * S), "h": round(h * S), "pad": pad}

def click(t, x, y):
    px, py = p(x, y)
    return {"t": t, "x": px, "y": py}

def img(n): return "shots/canva/%s.png" % n

def spec(name, scenes):
    d = {"w": 1280, "h": 720, "band": 140, "fps": 25, "scenes": scenes}
    with open(os.path.join(HERE, "specs", name + ".json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print("寫出", name)

# ① 改檔名
spec("四上L10_改檔名", [
 {"dur": 3.2, "img": img("a0"), "step": "1", "caption": "點右上角的檔名", "sub": "框會亮起來",
  "circles": [circ(0.5, 99, 1000, 8, 150, 36)],
  "cursor": cur((0, 600, 400), (1.6, 1075, 26), (3.2, 1075, 26)), "clicks": [click(1.7, 1075, 26)]},
 {"dur": 3.2, "img": img("a1"), "step": "2", "caption": "按 Ctrl＋A　全選", "sub": "舊的檔名會整個選起來",
  "keys": [{"t": 0.4, "dur": 1.8, "keys": ["Ctrl", "A"], "x": 640, "y": 330}],
  "cursor": cur((0, 1075, 26), (3.2, 1075, 26), )},
 {"dur": 4.0, "img": img("a1"), "imgs": [{"t": 1.2, "img": img("a2")}], "step": "3", "caption": "打上新的檔名", "sub": "年級＋班級＋座號，再加「我的台南小書」",
  "cursor": cur((0, 1075, 26), (4.0, 1075, 26))},
 {"dur": 3.2, "img": img("a2"), "imgs": [{"t": 1.4, "img": img("a3")}], "step": "4", "caption": "按 Enter　完成", "sub": "檔名改好了",
  "keys": [{"t": 0.3, "dur": 1.2, "keys": ["Enter"], "x": 640, "y": 330}],
  "cursor": cur((0, 1075, 26), (3.2, 1075, 26))},
])

# ② 改字
spec("四上L10_改字", [
 {"dur": 3.4, "img": img("b0"), "step": "★", "caption": "單擊：只會選到方塊", "sub": "這樣還不能打字",
  "boxes": [{"t": 0.3, "dur": 99, "x": round(563 * 1), "y": 232, "w": 205, "h": 26, "style": "gray-x"}] if False else [],
  "circles": [circ(0.3, 99, 690, 285, 250, 30, 12)],
  "cursor": cur((0, 1250, 500), (1.4, 815, 299), (3.4, 815, 299)), "clicks": [click(1.5, 815, 299)]},
 {"dur": 3.6, "img": img("b0"), "imgs": [{"t": 1.3, "img": img("b1")}], "step": "1", "caption": "連按兩下（雙擊）", "sub": "進到文字裡面，字會變藍",
  "cursor": cur((0, 815, 299, "ibeam"), (3.6, 815, 299, "ibeam")), "clicks": [click(0.9, 815, 299), click(1.2, 815, 299)]},
 {"dur": 3.4, "img": img("b1"), "step": "2", "caption": "按 Ctrl＋A　全選", "sub": "整段字都變藍，才打字",
  "keys": [{"t": 0.4, "dur": 1.8, "keys": ["Ctrl", "A"], "x": 640, "y": 380}],
  "cursor": cur((0, 815, 299, "ibeam"), (3.4, 815, 299, "ibeam"))},
 {"dur": 3.6, "img": img("b1"), "imgs": [{"t": 1.2, "img": img("b2")}], "step": "3", "caption": "直接打新的字", "sub": "舊的字會被換掉",
  "cursor": cur((0, 815, 299, "ibeam"), (3.6, 815, 299, "ibeam"))},
 {"dur": 3.0, "img": img("b3"), "step": "✓", "caption": "點空白處，完成", "sub": "字換成新的了",
  "cursor": cur((0, 815, 299), (1.0, 1250, 500), (3.0, 1250, 500))},
])

# ③ 換圖（取代）
spec("四上L10_換圖", [
 {"dur": 3.2, "img": img("c0"), "step": "1", "caption": "點一下要換的大圖", "sub": "上面會出現一排工具",
  "circles": [circ(0.5, 99, 820, 335, 328, 230, 6)],
  "cursor": cur((0, 1300, 600), (1.4, 983, 450), (3.2, 983, 450)), "clicks": [click(1.5, 983, 450)]},
 {"dur": 3.4, "img": img("c0"), "imgs": [{"t": 1.6, "img": img("c1")}], "step": "2", "caption": "按上面的「取代」", "sub": "左邊會出現照片",
  "circles": [circ(0.4, 1.4, 685, 62, 36, 32, 10)],
  "cursor": cur((0, 983, 450), (1.2, 702, 78), (3.4, 702, 78)), "clicks": [click(1.3, 702, 78)]},
 {"dur": 3.6, "img": img("c1"), "imgs": [{"t": 2.2, "img": img("c2")}], "step": "3", "caption": "搜尋，再找一張喜歡的", "sub": "素材庫沒有台南景點，找像的就好",
  "circles": [circ(0.3, 1.9, 100, 108, 280, 40, 6)],
  "cursor": cur((0, 702, 78), (1.0, 220, 129, "ibeam"), (3.6, 220, 129, "ibeam")), "clicks": [click(1.1, 220, 129)]},
 {"dur": 3.6, "img": img("c2"), "imgs": [{"t": 1.8, "img": img("c3")}], "step": "4", "caption": "點那張照片", "sub": "大圖就換成新的照片",
  "circles": [circ(0.3, 1.4, 81, 411, 152, 86, 8)],
  "cursor": cur((0, 220, 129), (1.2, 158, 450), (3.6, 158, 450)), "clicks": [click(1.4, 158, 450)]},
])

# ④ 分享連結
spec("四上L10_分享連結", [
 {"dur": 3.0, "img": img("c3"), "imgs": [{"t": 1.5, "img": img("d0")}], "step": "1", "caption": "右上角按「分享」", "sub": "右邊會出現分享設計",
  "circles": [circ(0.3, 1.4, 1505, 8, 56, 36, 8)],
  "cursor": cur((0, 1000, 400), (1.2, 1532, 26), (3.0, 1532, 26)), "clicks": [click(1.3, 1532, 26)]},
 {"dur": 3.4, "img": img("d0"), "imgs": [{"t": 1.5, "img": img("d1")}], "step": "2", "caption": "按「存取等級」（誰可以看）", "sub": "現在是「只有你可存取」，老師看不到",
  "circles": [circ(0.3, 1.4, 1192, 252, 354, 42, 6)],
  "cursor": cur((0, 1532, 26), (1.2, 1368, 273), (3.4, 1368, 273)), "clicks": [click(1.3, 1368, 273)]},
 {"dur": 3.8, "img": img("d1"), "imgs": [{"t": 1.5, "img": img("d2")}], "step": "3", "caption": "選「任何具有此連結者」", "sub": "預設是「可供編輯」，要改掉！",
  "circles": [circ(0.3, 1.2, 1192, 440, 354, 48, 6), circ(1.8, 99, 1440, 258, 100, 32, 8)],
  "cursor": cur((0, 1368, 273), (1.1, 1368, 464), (3.8, 1368, 464)), "clicks": [click(1.2, 1368, 464)]},
 {"dur": 3.8, "img": img("d2"), "imgs": [{"t": 1.5, "img": img("d3")}, {"t": 2.7, "img": img("d4")}], "step": "4", "caption": "權限改成「可供檢視」", "sub": "只能看，別人不能改你的小書",
  "circles": [circ(0.3, 1.2, 1440, 258, 100, 32, 8), circ(1.8, 0.8, 1385, 410, 160, 32, 8)],
  "cursor": cur((0, 1368, 464), (1.0, 1494, 273), (2.2, 1417, 425), (3.8, 1417, 425)), "clicks": [click(1.1, 1494, 273), click(2.3, 1417, 425)]},
 {"dur": 3.8, "img": img("d4"), "imgs": [{"t": 1.6, "img": img("d5")}], "step": "5", "caption": "按「複製連結」", "sub": "看到「已複製連結到剪貼簿」就好",
  "circles": [circ(0.3, 1.3, 1192, 312, 354, 38, 6)],
  "cursor": cur((0, 1417, 425), (1.2, 1368, 330), (3.8, 1368, 330)), "clicks": [click(1.4, 1368, 330)]},
])

# ⑤ 從文件複製到 Canva（地址）
spec("四上L10_複製到Canva", [
 {"dur": 4.0, "img": "shots/doc3_a.png", "step": "1", "caption": "在文件，選起「地址」的字", "sub": "從冒號後面，拖到最後",
  "boxes": [{"t": 1.5, "dur": 99, "x": 272, "y": 94, "w": 216, "h": 24, "style": "select", "grow": 1.8}],
  "cursor": [{"t": 0, "x": 700, "y": 300}, {"t": 1.2, "x": 272, "y": 106, "mode": "ibeam"}, {"t": 3.2, "x": 488, "y": 106, "mode": "ibeam"}, {"t": 4.0, "x": 488, "y": 106, "mode": "ibeam"}]},
 {"dur": 2.8, "img": "shots/doc3_a.png", "step": "2", "caption": "按 Ctrl＋C　複製", "sub": "再回到 Canva 的分頁",
  "boxes": [{"t": 0, "dur": 99, "x": 272, "y": 94, "w": 216, "h": 24, "style": "select"}],
  "keys": [{"t": 0.3, "dur": 1.8, "keys": ["Ctrl", "C"], "x": 900, "y": 300}],
  "cursor": [{"t": 0, "x": 488, "y": 106, "mode": "ibeam"}, {"t": 2.8, "x": 488, "y": 106, "mode": "ibeam"}]},
 {"dur": 3.2, "img": img("e0"), "imgs": [{"t": 1.6, "img": img("e1a")}], "step": "3", "caption": "連按兩下要換的字", "sub": "字裡面會出現閃閃的線",
  "circles": [circ(0.3, 1.2, 730, 392, 255, 30, 6)],
  "cursor": cur((0, 1250, 500), (1.2, 900, 406, "ibeam"), (3.2, 900, 406, "ibeam")), "clicks": [click(1.4, 900, 406), click(1.65, 900, 406)]},
 {"dur": 3.0, "img": img("e1a"), "imgs": [{"t": 1.4, "img": img("e1")}], "step": "4", "caption": "按 Ctrl＋A　全選", "sub": "整行字都變藍色",
  "keys": [{"t": 0.3, "dur": 1.5, "keys": ["Ctrl", "A"], "x": 640, "y": 330}],
  "cursor": cur((0, 900, 406, "ibeam"), (3.0, 900, 406, "ibeam"))},
 {"dur": 3.6, "img": img("e1"), "imgs": [{"t": 2.0, "img": img("e2")}], "step": "5", "caption": "按 Ctrl＋Shift＋V　貼上", "sub": "按住 Ctrl 和 Shift，再按 V",
  "keys": [{"t": 0.3, "dur": 1.8, "keys": ["Ctrl", "Shift", "V"], "x": 640, "y": 330}],
  "cursor": cur((0, 900, 406, "ibeam"), (3.6, 900, 406, "ibeam"))},
])
