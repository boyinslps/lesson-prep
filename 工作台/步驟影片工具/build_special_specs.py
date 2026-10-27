# 產生「查證小偵探（特教版）」步驟影片規格：specs/特教_*.json
# 截圖 1280x640；影片座標 y = 截圖 y + 80
import json, os, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
OFF = 80
KW = {k: json.loads(v) for k, v in json.load(open(os.path.join(HERE, 'shots', 'sp_kw_rects.json'), encoding='utf-8-sig')).items()}
GBOX = json.load(open(os.path.join(HERE, 'shots', 'sp_g_box.json'), encoding='utf-8-sig'))

def chrome(tab, url):
    return {"tabs": [tab], "urls": [url], "active": 0, "urlSel": []}

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
    with open(os.path.join(HERE, "specs", name + ".json"), "w", encoding="utf8") as f:
        json.dump({"w": 1280, "h": 720, "band": 140, "fps": 25, "scenes": scenes}, f, ensure_ascii=False, indent=1)

def ctr(b):
    return b['x'] + b['w'] // 2, b['y'] + b['h'] // 2 + OFF

# ---------- 1 選關鍵字、按複製 ----------
P = chrome("查證複習", "（老師給的網址）")
w0, w1, w4 = (KW['k3']['[data-w="%d"]' % i] for i in (0, 1, 4))
cb = KW['k3']['#copyBtn']
x0, y0 = ctr(w0); x1, y1 = ctr(w1); x4, y4 = ctr(w4); xc, yc = ctr(cb)
v_kw = [
    title("選關鍵字，按「複製」", "不用打字，點一點就好", 3),
    {"dur": 12.5, "img": "shots/sp_kw_k0.png",
     "imgs": [{"t": 2.0, "img": "shots/sp_kw_k1.png"}, {"t": 5.4, "img": "shots/sp_kw_k2.png"}, {"t": 8.8, "img": "shots/sp_kw_k3.png"}],
     "chrome": P, "caption": "點「手機充電」", "sub": "是什麼東西？",
     "captions": [{"t": 3.6, "caption": "再點「講電話」", "sub": "在做什麼事？"}, {"t": 7.0, "caption": "再點「喝水」", "sub": "一共選 3 個"}, {"t": 10.2, "caption": "選滿 3 個了", "sub": "下面會出現「複製關鍵字」的按鈕"}],
     "clicks": [{"t": 1.8, "x": x0, "y": y0}, {"t": 5.2, "x": x1, "y": y1}, {"t": 8.6, "x": x4, "y": y4}],
     "circles": [{"t": 0.4, "dur": 1.4, "x": w0['x'], "y": w0['y'] + OFF, "w": w0['w'], "h": w0['h'], "pad": 8},
                 {"t": 3.8, "dur": 1.4, "x": w1['x'], "y": w1['y'] + OFF, "w": w1['w'], "h": w1['h'], "pad": 8},
                 {"t": 7.2, "dur": 1.4, "x": w4['x'], "y": w4['y'] + OFF, "w": w4['w'], "h": w4['h'], "pad": 8}],
     "cursor": cur((0, 900, 560), (1.6, x0, y0), (3.0, x0, y0), (5.0, x1, y1), (6.4, x1, y1), (8.4, x4, y4), (12.5, x4, y4))},
    {"dur": 7, "img": "shots/sp_kw_k3.png", "imgs": [{"t": 3.2, "img": "shots/sp_kw_k4.png"}],
     "chrome": P, "caption": "按藍色的「複製關鍵字」", "sub": "按一下，就複製好了",
     "captions": [{"t": 3.4, "caption": "出現「已複製」", "sub": "下一步：貼到 Google"}],
     "circles": [{"t": 0.4, "dur": 2.4, "x": cb['x'], "y": cb['y'] + OFF, "w": cb['w'], "h": cb['h'], "pad": 10}],
     "clicks": [{"t": 3.0, "x": xc, "y": yc}],
     "cursor": cur((0, 900, 450), (2.6, xc, yc), (7, xc, yc))},
]
save("特教_v_keyword", v_kw)

# ---------- 2 到 Google 貼上、按 Enter ----------
G = chrome("Google", "www.google.com")
bx, by = GBOX['x'] + GBOX['w'] // 2, GBOX['y'] + GBOX['h'] // 2 + OFF
v_g = [
    title("貼上關鍵字，按 Enter", "點搜尋框 → Ctrl＋V → Enter", 3),
    {"dur": 8, "img": "shots/sp_g_empty.png", "imgs": [{"t": 4.6, "img": "shots/sp_g_typed.png"}],
     "chrome": G, "caption": "點一下搜尋框", "sub": "Google 的最中間，長長的那一格",
     "captions": [{"t": 2.6, "caption": "按 Ctrl ＋ V，貼上", "sub": "剛剛複製的關鍵字就出現了"}],
     "circles": [{"t": 0.3, "dur": 2.0, "x": GBOX['x'], "y": GBOX['y'] + OFF, "w": GBOX['w'], "h": GBOX['h'], "pad": 8}],
     "clicks": [{"t": 1.6, "x": bx, "y": by}],
     "keys": [{"t": 3.0, "dur": 1.8, "keys": ["Ctrl", "V"], "x": 640, "y": 580}],
     "cursor": cur((0, 900, 480), (1.4, bx, by, "ibeam"), (8, bx, by, "ibeam"))},
    {"dur": 7, "img": "shots/sp_g_typed.png", "imgs": [{"t": 3.6, "img": "shots/sp_g_results.png"}],
     "chrome": G, "caption": "按 Enter", "sub": "鍵盤右邊，寫著 Enter 的大按鍵",
     "captions": [{"t": 3.8, "caption": "出現搜尋結果了", "sub": "下一步：看結果，找查核機構"}],
     "keys": [{"t": 1.0, "dur": 2.0, "keys": ["Enter"], "x": 640, "y": 580}],
     "cursor": cur((0, bx, by, "ibeam"), (7, bx, by, "ibeam"))},
]
save("特教_v_google", v_g)

# ---------- 3 找查核機構 ----------
def box(x, y, w, h, t, style="red", dur=99):
    return {"t": t, "dur": dur, "x": x, "y": y + OFF, "w": w, "h": h, "style": style}
v_f = [
    title("找到「查核機構」的報告", "AI 摘要可以先讀，要確定就往下找", 3.5),
    {"dur": 9, "img": "shots/sp_g_results.png", "chrome": G, "caption": "最上面是「AI 摘要」，可以先讀", "sub": "它說：這則訊息是「假消息」",
     "captions": [{"t": 4.8, "caption": "要確定，就往下找查核機構", "sub": "AI 可能會錯，要看查核報告"}],
     "boxes": [box(98, 168, 665, 90, 1.2)],
     "cursor": cur((0, 900, 500), (1.2, 330, 255 + OFF), (4.0, 330, 255 + OFF), (6.0, 700, 500 + OFF), (9, 700, 500 + OFF))},
    {"dur": 10, "img": "shots/sp_g_results2.png", "chrome": G, "caption": "往下找：誰是「查核機構」？", "sub": "專門查謠言的：台灣事實查核中心、MyGoPen",
     "boxes": [box(98, 150, 665, 120, 1.6), box(98, 300, 665, 120, 3.2)],
     "labels": [{"t": 2.0, "dur": 99, "x": 790, "y": 190 + OFF, "text": "台灣事實查核中心 ✓", "color": "green", "size": 28},
                {"t": 3.6, "dur": 99, "x": 790, "y": 340 + OFF, "text": "MyGoPen ✓", "color": "green", "size": 28}],
     "cursor": cur((0, 900, 560), (1.6, 300, 186 + OFF), (3.2, 300, 336 + OFF), (10, 300, 336 + OFF))},
    {"dur": 8, "img": "shots/sp_g_results2.png", "imgs": [{"t": 3.4, "img": "shots/sp_tfc_H.png"}],
     "chrome": G, "caption": "點進去，打開它的文章", "sub": "點藍色的標題",
     "captions": [{"t": 3.6, "caption": "這就是查核報告", "sub": "下一步：看標題前面的標籤"}],
     "clicks": [{"t": 3.0, "x": 300, "y": 186 + OFF}],
     "cursor": cur((0, 700, 400), (2.8, 300, 186 + OFF), (8, 300, 186 + OFF))},
]
save("特教_v_find", v_f)

# ---------- 4 看標籤 ----------
v_l = [
    title("看標題前面的「標籤」", "錯誤、詐騙、誤導 ＝ 假的　正確 ＝ 真的", 3.5),
    {"dur": 9, "img": "shots/sp_mgp_H.png", "chrome": chrome("MyGoPen 麥擱騙", "www.mygopen.com/2022/01/Charging-Phone.html"),
     "caption": "看標題最前面，有一個標籤", "sub": "這一篇的標籤是「錯誤」",
     "captions": [{"t": 4.4, "caption": "「錯誤」＝ 這則訊息是假的", "sub": "查核機構已經查過了"}],
     "circles": [{"t": 1.0, "dur": 99, "x": 100, "y": 232 + OFF, "w": 152, "h": 52, "pad": 12}],
     "labels": [{"t": 5.0, "dur": 99, "x": 300, "y": 360 + OFF, "text": "錯誤 ＝ 假的", "color": "red", "size": 34}],
     "cursor": cur((0, 800, 500), (1.0, 330, 258 + OFF), (9, 330, 258 + OFF))},
    {"dur": 7, "img": "shots/sp_tfc_H.png", "chrome": chrome("台灣事實查核中心", "tfc-taiwan.org.tw/fact-check-reports/migration-6824"),
     "caption": "另一家查核機構，也是「錯誤」", "sub": "紅色的標籤，寫著「錯誤」",
     "circles": [{"t": 1.0, "dur": 99, "x": 268, "y": 543 + OFF, "w": 158, "h": 54, "pad": 12}],
     "cursor": cur((0, 800, 400), (1.0, 345, 570 + OFF), (7, 345, 570 + OFF))},
]
save("特教_v_label", v_l)
print("ok")
