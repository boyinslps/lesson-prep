# 產生五上 L06「格式檢查」4 支步驟影片的規格（specs/五上L06_格式*.json）
# 截圖：shots/doc4_*.png（mockdoc4.html，1280x640）；影片座標 y = 截圖 y + 80（上面有分頁列與網址列）
import json, os, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
OFF = 80
RECTS = {k: (json.loads(v) if isinstance(v, str) else v)
         for k, v in json.load(open(os.path.join(HERE, 'shots', 'doc4_rects.json'), encoding='utf-8-sig')).items()}
D = {"tabs": ["50123 王小明 查證文件 - Google 文件"], "urls": ["docs.google.com/document/d/1x…/edit"], "active": 0, "urlSel": []}


def r(state, key):
    return RECTS[state][key]


def cx(state, key):
    b = r(state, key)
    return b['x'] + b['w'] // 2


def cy(state, key):
    b = r(state, key)
    return b['y'] + b['h'] // 2 + OFF


def cur(*pts):
    out = []
    for p in pts:
        d = {"t": p[0], "x": p[1], "y": p[2]}
        if len(p) > 3:
            d["mode"] = p[3]
        out.append(d)
    return out


def title(t, sub, dur=3):
    return {"type": "title", "dur": dur, "title": t, "subtitle": sub}


def save(name, scenes):
    spec = {"w": 1280, "h": 720, "band": 140, "fps": 25, "scenes": scenes}
    with open(os.path.join(HERE, "specs", name + ".json"), "w", encoding="utf8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)


def circ(state, key, t, dur, pad=10):
    b = r(state, key)
    return {"t": t, "dur": dur, "x": b['x'], "y": b['y'] + OFF, "w": b['w'], "h": b['h'], "pad": pad}


def hbox(state, key, t, w=None):
    b = r(state, key)
    return {"t": t, "dur": 99, "x": b['x'] - 6, "y": b['y'] + OFF - 4, "w": (w or b['w']) + 12, "h": b['h'] + 8, "style": "highlight"}


def select_scene(state0, state1, line_key, cap, sub, dur=5.5):
    b = r(state0, line_key)
    y = b['y'] + b['h'] // 2 + OFF
    return {"dur": dur, "img": "shots/doc4_%s.png" % state0, "imgs": [{"t": 2.0, "img": "shots/doc4_%s.png" % state1}], "chrome": D,
            "caption": cap, "sub": sub,
            "clicks": [{"t": 1.0, "x": 400, "y": y}, {"t": 1.3, "x": 400, "y": y}, {"t": 1.6, "x": 400, "y": y}],
            "cursor": cur((0, 800, 470), (0.8, 400, y, "ibeam"), (dur, 400, y, "ibeam"))}


def font_scene(s_sel, s_dd, s_done, cap, sub, dur=7.5):
    fb = r(s_sel, 'fontbtn')
    fk = r(s_dd, 'f_kai')
    p0 = (400, 300)
    fx, fy = fb['x'] + fb['w'] // 2, fb['y'] + fb['h'] // 2 + OFF
    kx, ky = fk['x'] + 60, fk['y'] + fk['h'] // 2 + OFF
    return {"dur": dur, "img": "shots/doc4_%s.png" % s_sel,
            "imgs": [{"t": 2.4, "img": "shots/doc4_%s.png" % s_dd}, {"t": 5.4, "img": "shots/doc4_%s.png" % s_done}],
            "chrome": D, "caption": cap, "sub": sub,
            "circles": [circ(s_sel, 'fontbtn', 0.3, 2.0, 8)],
            "clicks": [{"t": 2.2, "x": fx, "y": fy}, {"t": 5.2, "x": kx, "y": ky}],
            "arrows": [{"t": 0.3, "dur": 1.8, "x1": 560, "y1": 330, "x2": fx + 30, "y2": fy + 18}],
            "cursor": cur((0, p0[0], p0[1]), (1.9, fx, fy), (3.0, fx, fy), (5.0, kx, ky), (dur, kx, ky))}


def size_scene(s_before, s_edit, s_done, new, cap, sub, dur=8.5):
    sb = r(s_before, 'sizenum')
    se = r(s_edit, 'sizenum')
    sx, sy = sb['x'] + sb['w'] // 2, sb['y'] + sb['h'] // 2 + OFF
    return {"dur": dur, "img": "shots/doc4_%s.png" % s_before,
            "imgs": [{"t": 2.5, "img": "shots/doc4_%s.png" % s_edit}, {"t": 6.4, "img": "shots/doc4_%s.png" % s_done}],
            "chrome": D, "caption": cap, "sub": sub,
            "circles": [circ(s_before, 'sizenum', 0.3, 2.0, 10)],
            "clicks": [{"t": 2.3, "x": sx, "y": sy}],
            "typing": [{"t": 3.4, "dur": 3.0, "x": se['x'] + 8, "y": se['y'] + OFF + 4, "text": new, "size": 20, "cps": 2.5,
                        "bgw": se['w'] - 16, "bgh": se['h'] - 8}],
            "keys": [{"t": 5.2, "dur": 1.2, "keys": ["Enter"], "x": 640, "y": 560}],
            "arrows": [{"t": 0.3, "dur": 1.8, "x1": 640, "y1": 330, "x2": sx + 20, "y2": sy + 20}],
            "cursor": cur((0, 700, 300), (1.9, sx, sy), (dur, sx, sy))}


# ============ A：標題 標楷體、26 ============
a = [
    title("標題：標楷體、26", "選取 → 字型 → 字級", 3),
    select_scene('a0', 'a1', 'l1', "選取標題那一行（連點滑鼠三下）", "這一行是整份文件的標題"),
    font_scene('a1', 'a2', 'a3', "字型：點「Arial」，選「標楷體」", "工具列的字型按鈕在「標題 1」右邊"),
    size_scene('a3', 'a4', 'a5', '26', "字級：點數字，輸入 26，按 Enter", "「標題 1」本來是 20，要改成 26"),
    {"dur": 6, "img": "shots/doc4_a6.png", "chrome": D, "caption": "標題完成：標楷體、26",
     "sub": "點一下標題，上面會顯示「標題 1」「標楷體」「26」",
     "boxes": [hbox('a6', 'l1', 0.4)],
     "circles": [circ('a6', 'fontbtn', 1.0, 99, 8), circ('a6', 'sizenum', 1.0, 99, 8)],
     "labels": [{"t": 2.0, "dur": 99, "x": 880, "y": 400 + OFF, "text": "標楷體・26 ✓", "color": "green", "size": 30}]},
]
save("五上L06_格式A_標題26", a)

# ============ B：4 個欄位名稱 標楷體、16 ============
b = [
    title("欄位名稱：標楷體、16", "7 個欄位名稱，都是標題 2、標楷體、16", 3.5),
    select_scene('b0', 'b1', 'h0', "選取第一個欄位名稱「查核網址」（連點三下）", "標題 2 的字級本來就是 16"),
    font_scene('b1', 'b2', 'b3', "字型：點「Arial」，選「標楷體」", "字級看一下，要是 16"),
    {"dur": 7, "img": "shots/doc4_b3.png", "imgs": [{"t": 3.0, "img": "shots/doc4_b4.png"}], "chrome": D,
     "caption": "其他 6 個欄位名稱，也一樣做", "sub": "每個欄位名稱都是：標題 2、標楷體、16",
     "circles": [circ('b3', 'fontbtn', 0.4, 2.2, 8), circ('b3', 'sizenum', 0.4, 2.2, 8)],
     "labels": [{"t": 3.4, "dur": 99, "x": 760, "y": 330 + OFF, "text": "每個欄位名稱：標楷體・16 ✓", "color": "green", "size": 28}],
     "boxes": [{"t": 3.2, "dur": 99, "x": 214, "y": 336 + OFF, "w": 400, "h": 200, "style": "highlight"}]},
]
save("五上L06_格式B_欄位16", b)

# ============ D：內容 一般文字（內文） ============
d_sn = r('d2', 's_normal')
dsb = r('d1', 'stylebtn')
dm = r('d0', 'm0')
dx, dy = dsb['x'] + dsb['w'] // 2, dsb['y'] + dsb['h'] // 2 + OFF
nx, ny = d_sn['x'] + 50, d_sn['y'] + d_sn['h'] // 2 + OFF
ym = dm['y'] + dm['h'] // 2 + OFF
d = [
    title("內容：一般文字", "內容如果變得很大，是被設成標題了", 3),
    select_scene('d0', 'd1', 'm0', "選取內容那一行（連點三下）", "字比別的內容大很多，可能被設成了標題"),
    {"dur": 7.5, "img": "shots/doc4_d1.png", "imgs": [{"t": 2.4, "img": "shots/doc4_d2.png"}, {"t": 5.4, "img": "shots/doc4_d3.png"}],
     "chrome": D, "caption": "左上角按鈕，選「內文」", "sub": "「內文」就是一般文字",
     "circles": [circ('d1', 'stylebtn', 0.3, 2.0, 8)],
     "clicks": [{"t": 2.2, "x": dx, "y": dy}, {"t": 5.2, "x": nx, "y": ny}],
     "arrows": [{"t": 0.3, "dur": 1.8, "x1": 520, "y1": 330, "x2": dx + 30, "y2": dy + 18}],
     "cursor": cur((0, 500, ym, "ibeam"), (1.9, dx, dy), (3.0, dx, dy), (5.0, nx, ny), (7.5, nx, ny))},
    {"dur": 6, "img": "shots/doc4_d4.png", "chrome": D, "caption": "內容都要是「內文」（一般文字）",
     "sub": "標題、欄位名稱以外的字，都是內文",
     "boxes": [hbox('d4', 'm0', 0.4)],
     "circles": [circ('d4', 'stylebtn', 1.0, 99, 8)],
     "labels": [{"t": 2.0, "dur": 99, "x": 700, "y": 520 + OFF, "text": "內文 ✓", "color": "green", "size": 30}]},
]
save("五上L06_格式D_一般文字", d)
print("ok")
