# -*- coding: utf-8 -*-
# 四上 L10（Canva 手冊）第二版影片：開 A4 新文件、加文字、加照片、新增頁面做目錄。
# 截圖來自 2026-11-17 老師 Canva 實錄（頭像已遮、上傳區其他圖已遮），縮成 1280×580，字卡 band=140。
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "C:/Users/Roki/.claude/projects/D------------/1fcf8187-08da-4c39-abfd-e3b031789435/tool-results/mcp-claude-in-chrome-blob-"
FF = "C:/Users/Roki/tools/ffmpeg/bin/ffmpeg.exe"
# name: (檔名片段, 高度, 要遮的區塊[(x,y,w,h)])
OLD = {
 "a0": "1794904977091-y885h4", "a1": "1794904996225-9pg7tn", "a2": "1794904996225-pq0rmh", "a3": "1794904996225-t1v2h9",
 "c3": "1794905222627-bcooxa", "d0": "1794905234175-9mlqel", "d1": "1794905244155-7znf0j", "d2": "1794905261576-h545lw",
 "d3": "1794905275063-dcrfbv", "d4": "1794905292811-x3r4jw", "d5": "1794905292811-vqnuav",
}
FR = {
 "g1": ("1794927618932-xkx6te", 776, []),
 "d1": ("1794927649672-ekisak", 733, []),
 "d2": ("1794927666306-crj4fi", 733, []),
 "t0": ("1794927666306-ntx078", 733, []),
 "t1": ("1794927718758-pp8hoz", 733, []),
 "t2": ("1794927731682-9ur2c5", 733, []),
 "t3": ("1794927751352-dzqj0r", 733, []),
 "u0": ("1794927769887-8g99zu", 733, [(229, 380, 145, 340), (80, 466, 295, 270), (80, 262, 295, 100)]),
 "u1": ("1794927782392-czeib4", 733, [(229, 380, 145, 340), (80, 466, 295, 270), (80, 262, 295, 100)]),
 "u2": ("1794927796631-c4uczh", 733, [(229, 380, 145, 340), (80, 466, 295, 270), (80, 262, 295, 100)]),
 "u3": ("1794927814763-rzwoh6", 733, [(229, 380, 145, 340), (80, 466, 295, 270), (80, 262, 295, 100)]),
 "p1": ("1794927843336-cpdxpg", 733, [(229, 380, 145, 340), (80, 466, 295, 270), (80, 262, 295, 100)]),
 "p2": ("1794927862660-3dkhcy", 733, []),
 "p3": ("1794927887590-vg2nim", 733, []),
 "tc0": ("1794961268992-lpp2y1", 733, []),
 "tc1": ("1794961268993-5vgxw0", 733, []),
 "tc2": ("1794961268993-8ls53w", 733, []),
}
for k, f in OLD.items():
    FR[k] = (f, 776, [])
os.makedirs(os.path.join(HERE, "shots", "canva"), exist_ok=True)
for k, (f, h, boxes) in FR.items():
    vf = "delogo=x=1166:y=8:w=40:h=36"
    for (x, y, w, hh) in boxes:
        vf += ",drawbox=x=%d:y=%d:w=%d:h=%d:color=0xf3f4f8:t=fill" % (x, y, w, hh)
    vf += ",scale=1280:-1,pad=1280:720:0:(oh-ih)/2:color=0xe9ecf3"
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", SRC + f + ".jpg", "-vf", vf, "-q:v", "2",
                    os.path.join(HERE, "shots", "canva", k + ".png")], check=True)

def mk(h):
    s = 1280 / 1568.0
    return s, (720 - h * s) / 2
def P(h, x, y):
    s, oy = mk(h); return round(x * s), round(oy + y * s)
def cur(h, *pts):
    out = []
    for t, x, y, *m in pts:
        px, py = P(h, x, y); d = {"t": t, "x": px, "y": py}
        if m: d["mode"] = m[0]
        out.append(d)
    return out
def circ(h, t, dur, x, y, w, hh, pad=8):
    s, oy = mk(h); px, py = P(h, x, y)
    return {"t": t, "dur": dur, "x": px, "y": py, "w": round(w * s), "h": round(hh * s), "pad": pad}
def clk(h, t, x, y):
    px, py = P(h, x, y); return {"t": t, "x": px, "y": py}
def img(n): return "shots/canva/%s.png" % n
def spec(name, scenes):
    with open(os.path.join(HERE, "specs", name + ".json"), "w", encoding="utf-8") as f:
        json.dump({"w": 1280, "h": 720, "band": 140, "fps": 25, "scenes": scenes}, f, ensure_ascii=False, indent=1)
    print("寫出", name)

H7, H8 = 733, 776

# ① 開新文件（A4）
spec("四上L10_開A4文件", [
 {"type": "title", "dur": 2.6, "title": "開一份 A4 空白文件", "subtitle": "Canva 首頁 → 建立 → 文件 (A4，直式)"},
 {"dur": 4.2, "img": img("g1"), "step": "1", "caption": "按「建立」，選「文件 (A4，直式)」", "sub": "不要選 Docs，也不要選「文件 (數位)」",
  "circles": [circ(H8, 0.5, 99, 641, 438, 219, 154, 10)],
  "cursor": cur(H8, (0, 1250, 300), (2.0, 750, 515), (4.2, 750, 515)), "clicks": [clk(H8, 2.2, 750, 515)]},
 {"dur": 3.4, "img": img("d1"), "step": "✓", "caption": "出現一張空白的紙，就開好了", "sub": "A4＝一張 A4 紙的大小（21×29.7 公分）",
  "cursor": cur(H7, (0, 750, 515), (3.4, 1100, 350))},
])

# ② 加文字（書名、副標題）
spec("四上L10_加文字", [
 {"dur": 3.4, "img": img("t0"), "step": "1", "caption": "左邊按「文字」，按「新增標題」", "sub": "書名用標題",
  "circles": [circ(H7, 0.4, 99, 82, 345, 288, 56, 6)],
  "cursor": cur(H7, (0, 1250, 500), (1.4, 225, 373), (3.4, 225, 373)), "clicks": [clk(H7, 1.5, 225, 373)]},
 {"dur": 3.2, "img": img("t1"), "step": "2", "caption": "字是藍色的，直接打書名", "sub": "新增的字會自動選好",
  "circles": [circ(H7, 0.3, 99, 906, 326, 156, 52, 8)],
  "cursor": cur(H7, (0, 225, 373), (3.2, 983, 352, "ibeam"))},
 {"dur": 3.4, "img": img("t2"), "step": "3", "caption": "打好了：我的台南一日小旅行", "sub": "按住字，拖到上面",
  "cursor": cur(H7, (0, 983, 352, "ibeam"), (3.4, 983, 352, "ibeam"))},
 {"dur": 3.4, "img": img("t3"), "step": "4", "caption": "再按「新增副標題」，打三個景點", "sub": "用同樣的方法",
  "cursor": cur(H7, (0, 225, 432), (3.4, 983, 262, "ibeam"))},
])

# ③ 加照片（台南旅遊網的照片）
spec("四上L10_加照片", [
 {"dur": 3.6, "img": img("u0"), "step": "1", "caption": "左邊按「上傳」，按「上傳檔案」", "sub": "選你從台南旅遊網存的照片",
  "circles": [circ(H7, 0.3, 99, 82, 127, 262, 38, 6)],
  "cursor": cur(H7, (0, 1250, 500), (1.3, 212, 145), (3.6, 212, 145)), "clicks": [clk(H7, 1.5, 212, 145)]},
 {"dur": 3.4, "img": img("u0"), "imgs": [{"t": 1.8, "img": img("u1")}], "step": "2", "caption": "上傳好了，點一下這張照片", "sub": "照片會放到頁面上",
  "circles": [circ(H7, 0.3, 1.5, 80, 382, 143, 80, 6)],
  "cursor": cur(H7, (0, 212, 145), (1.2, 152, 420), (3.4, 152, 420)), "clicks": [clk(H7, 1.4, 152, 420)]},
 {"dur": 3.6, "img": img("u1"), "imgs": [{"t": 2.0, "img": img("u2")}], "step": "3", "caption": "拉照片的角，讓照片變大", "sub": "拉角不會變形",
  "circles": [circ(H7, 0.3, 1.6, 1084, 402, 30, 30, 6)],
  "cursor": cur(H7, (0, 1000, 500), (0.9, 1098, 416), (2.4, 1143, 470), (3.6, 1143, 470))},
 {"dur": 3.2, "img": img("u2"), "imgs": [{"t": 1.8, "img": img("u3")}], "step": "4", "caption": "按住照片，拖到中間", "sub": "放開就好",
  "cursor": cur(H7, (0, 1000, 375), (1.6, 971, 420), (3.2, 1350, 500))},
])

# ④ 新增頁面、做目錄
spec("四上L10_新增頁面", [
 {"dur": 3.4, "img": img("u3"), "imgs": [{"t": 1.8, "img": img("p1")}], "step": "1", "caption": "畫面下面按「＋」", "sub": "就會多一張空白頁",
  "circles": [circ(H7, 0.3, 1.5, 988, 627, 64, 56, 6)],
  "cursor": cur(H7, (0, 1250, 500), (1.2, 1020, 655), (3.4, 1020, 655)), "clicks": [clk(H7, 1.4, 1020, 655)]},
 {"dur": 3.4, "img": img("p2"), "step": "2", "caption": "文字 →「新增標題」，打「目錄」", "sub": "再按「新增少量內文文字」",
  "circles": [circ(H7, 0.3, 99, 82, 462, 288, 44, 6)],
  "cursor": cur(H7, (0, 983, 170), (1.4, 225, 485), (3.4, 225, 485))},
 {"dur": 3.8, "img": img("p3"), "step": "3", "caption": "一行一個章節，後面打頁碼", "sub": "按 Enter 換下一行",
  "keys": [{"t": 0.4, "dur": 1.6, "keys": ["Enter"], "x": 640, "y": 330}],
  "cursor": cur(H7, (0, 983, 400, "ibeam"), (3.8, 983, 400, "ibeam"))},
])

# ⑤ 改檔名（舊畫面重做）
spec("四上L10_改檔名", [
 {"dur": 3.2, "img": img("a0"), "step": "1", "caption": "點右上角的作品名字", "sub": "框會亮起來",
  "circles": [circ(H8, 0.5, 99, 1000, 8, 150, 36)],
  "cursor": cur(H8, (0, 600, 400), (1.6, 1075, 26), (3.2, 1075, 26)), "clicks": [clk(H8, 1.7, 1075, 26)]},
 {"dur": 3.2, "img": img("a1"), "step": "2", "caption": "按 Ctrl＋A　全選", "sub": "舊的名字會整個選起來",
  "keys": [{"t": 0.4, "dur": 1.8, "keys": ["Ctrl", "A"], "x": 640, "y": 330}], "cursor": cur(H8, (0, 1075, 26), (3.2, 1075, 26))},
 {"dur": 4.0, "img": img("a1"), "imgs": [{"t": 1.2, "img": img("a2")}], "step": "3", "caption": "打上新的名字", "sub": "年級＋班級＋座號，再加「我的台南小書」",
  "cursor": cur(H8, (0, 1075, 26), (4.0, 1075, 26))},
 {"dur": 3.2, "img": img("a2"), "imgs": [{"t": 1.4, "img": img("a3")}], "step": "4", "caption": "按 Enter　完成", "sub": "名字改好了",
  "keys": [{"t": 0.3, "dur": 1.2, "keys": ["Enter"], "x": 640, "y": 330}], "cursor": cur(H8, (0, 1075, 26), (3.2, 1075, 26))},
])

# ⑥ 分享連結
spec("四上L10_分享連結", [
 {"dur": 3.0, "img": img("c3"), "imgs": [{"t": 1.5, "img": img("d0")}], "step": "1", "caption": "右上角按「分享」", "sub": "右邊會出現分享設計",
  "circles": [circ(H8, 0.3, 1.4, 1505, 8, 56, 36, 8)],
  "cursor": cur(H8, (0, 1000, 400), (1.2, 1532, 26), (3.0, 1532, 26)), "clicks": [clk(H8, 1.3, 1532, 26)]},
 {"dur": 3.4, "img": img("d0"), "imgs": [{"t": 1.5, "img": img("d1")}], "step": "2", "caption": "按「存取等級」（誰可以看）", "sub": "現在是「只有你可存取」，老師看不到",
  "circles": [circ(H8, 0.3, 1.4, 1192, 252, 354, 42, 6)],
  "cursor": cur(H8, (0, 1532, 26), (1.2, 1368, 273), (3.4, 1368, 273)), "clicks": [clk(H8, 1.3, 1368, 273)]},
 {"dur": 3.8, "img": img("d1"), "imgs": [{"t": 1.5, "img": img("d2")}], "step": "3", "caption": "選「任何具有此連結者」", "sub": "預設是「可供編輯」，要改掉！",
  "circles": [circ(H8, 0.3, 1.2, 1192, 440, 354, 48, 6), circ(H8, 1.8, 99, 1440, 258, 100, 32, 8)],
  "cursor": cur(H8, (0, 1368, 273), (1.1, 1368, 464), (3.8, 1368, 464)), "clicks": [clk(H8, 1.2, 1368, 464)]},
 {"dur": 3.8, "img": img("d2"), "imgs": [{"t": 1.5, "img": img("d3")}, {"t": 2.7, "img": img("d4")}], "step": "4", "caption": "權限改成「可供檢視」", "sub": "只能看，別人不能改你的作品",
  "circles": [circ(H8, 0.3, 1.2, 1440, 258, 100, 32, 8), circ(H8, 1.8, 0.8, 1385, 410, 160, 32, 8)],
  "cursor": cur(H8, (0, 1368, 464), (1.0, 1494, 273), (2.2, 1417, 425), (3.8, 1417, 425)), "clicks": [clk(H8, 1.1, 1494, 273), clk(H8, 2.3, 1417, 425)]},
 {"dur": 3.8, "img": img("d4"), "imgs": [{"t": 1.6, "img": img("d5")}], "step": "5", "caption": "按「複製連結」", "sub": "看到「已複製連結到剪貼簿」就好",
  "circles": [circ(H8, 0.3, 1.3, 1192, 312, 354, 38, 6)],
  "cursor": cur(H8, (0, 1417, 425), (1.2, 1368, 330), (3.8, 1368, 330)), "clicks": [clk(H8, 1.4, 1368, 330)]},
])

# ⑦ 目錄：靠左＋列點
spec("四上L10_目錄靠左列點", [
 {"dur": 3.4, "img": img("tc0"), "step": "1", "caption": "連按兩下目錄的字，按 Ctrl＋A", "sub": "整段字都變藍色，才做下一步",
  "keys": [{"t": 0.4, "dur": 1.6, "keys": ["Ctrl", "A"], "x": 640, "y": 330}],
  "cursor": cur(H7, (0, 983, 410, "ibeam"), (3.4, 983, 410, "ibeam"))},
 {"dur": 3.4, "img": img("tc0"), "imgs": [{"t": 1.8, "img": img("tc1")}], "step": "2", "caption": "按上面的「對齊」，變成靠左", "sub": "按一次換一種，看到字靠左就停",
  "circles": [circ(H7, 0.3, 1.5, 1010, 60, 38, 36, 6)],
  "cursor": cur(H7, (0, 1250, 500), (1.2, 1029, 78), (3.4, 1029, 78)), "clicks": [clk(H7, 1.4, 1029, 78)]},
 {"dur": 3.4, "img": img("tc1"), "imgs": [{"t": 1.8, "img": img("tc2")}], "step": "3", "caption": "再按旁邊的「項目符號」", "sub": "每一行前面多一個圓點",
  "circles": [circ(H7, 0.3, 1.5, 1043, 60, 38, 36, 6)],
  "cursor": cur(H7, (0, 1029, 78), (1.2, 1062, 78), (3.4, 1062, 78)), "clicks": [clk(H7, 1.4, 1062, 78)]},
])
