# 五上 L05「以圖搜圖：兩種方法」影片規格
# 方法一：老師錄的智慧鏡頭影片（L04 的 智慧鏡頭.mp4）疊字卡；方法二：真實 Google 畫面＋示意畫面
import json, os, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
OFF = 80

def chrome(tab, url): return {"tabs": [tab], "urls": [url], "active": 0}
def cur(*pts):
    out = []
    for p in pts:
        d = {"t": p[0], "x": p[1], "y": p[2]}
        if len(p) > 3: d["mode"] = p[3]
        out.append(d)
    return out
def title(t, sub, dur=3): return {"type": "title", "dur": dur, "title": t, "subtitle": sub}
def save(name, spec):
    with open(os.path.join(HERE, "specs", name + ".json"), "w", encoding="utf8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)

# ---- A：片頭＋「方法一」字卡
save("五上L05_以圖搜圖_A片頭", {"w": 1280, "h": 720, "band": 140, "fps": 25, "scenes": [
    title("以圖搜圖：用圖片找查核文章", "兩種方法：① 智慧鏡頭　② Google 的相機圖示", 3.5),
    title("方法一：智慧鏡頭", "在網頁的圖片上按右鍵，最快", 2.5)]})

# ---- M1：疊在老師錄的影片上
save("五上L05_以圖搜圖_M1智慧鏡頭", {
  "w": 1280, "h": 720, "band": 140,
  "source": "materials/五年級上學期/L04_認識農場文與業配文/assets/智慧鏡頭.mp4",
  "keep": [[0.3, 9.4]],
  "scenes": [
    {"from": 0, "to": 3.2, "step": "1", "caption": "在圖片上按滑鼠右鍵，選「透過 Google 智慧鏡頭搜尋圖片」",
     "sub": "選單最下面那一項",
     "boxes": [{"t": 0.3, "x": 56, "y": 128, "w": 566, "h": 378}]},
    {"from": 3.2, "to": 6.2, "step": "2", "caption": "畫面變暗、出現十字線：拖曳框住整張圖片",
     "sub": "框住要查的那張圖",
     "boxes": [{"t": 0.2, "x": 60, "y": 198, "w": 384, "h": 266}]},
    {"from": 6.2, "to": 8.9, "step": "3", "caption": "右邊跳出搜尋結果，往下看有沒有查核文章",
     "sub": "AI 摘要先別全信，往下找新聞和查核機構的標題",
     "boxes": [{"t": 0.3, "x": 910, "y": 60, "w": 360, "h": 560}]}]})

# ---- B：方法二
D = chrome("Google", "google.com")
steps = [
  title("方法二：Google 的相機圖示", "適合圖片在別的分頁，或已經複製起來", 2.5),
  {"dur": 6, "img": "shots/img_g_home.png", "chrome": chrome("新分頁", ""), "step": "1",
   "caption": "開一個新分頁（Ctrl＋T），點右上角的「九宮格」", "sub": "九宮格是 Google 的應用程式選單",
   "circles": [{"t": 0.8, "dur": 99, "x": 1137, "y": 8 + OFF, "w": 40, "h": 40, "pad": 10}],
   "clicks": [{"t": 3.0, "x": 1157, "y": 28 + OFF}],
   "cursor": cur((0, 700, 400), (2.8, 1157, 28 + OFF), (6, 1157, 28 + OFF))},
  {"dur": 6, "img": "shots/_t_apps.png", "chrome": chrome("新分頁", ""), "step": "2",
   "caption": "在選單裡點「搜尋」", "sub": "彩色的 G 就是 Google 搜尋",
   "circles": [{"t": 0.6, "dur": 99, "x": 1033, "y": 126 + OFF, "w": 70, "h": 80, "pad": 8}],
   "clicks": [{"t": 3.0, "x": 1068, "y": 150 + OFF}],
   "cursor": cur((0, 1157, 28 + OFF), (2.8, 1068, 160 + OFF), (6, 1068, 160 + OFF))},
  {"dur": 8, "img": "shots/img_g_home.png", "imgs": [{"t": 3.6, "img": "shots/img_g_lens_dialog.png"}], "chrome": D, "step": "3",
   "caption": "進到 Google 搜尋頁，點搜尋框裡的「相機」圖示", "sub": "那個框有一個小相機",
   "captions": [{"t": 3.8, "caption": "跳出「用智慧鏡頭搜尋所有圖片」視窗", "sub": "先不要關！去找要查的那張圖片"}],
   "circles": [{"t": 0.6, "dur": 3.0, "x": 840, "y": 186 + OFF, "w": 36, "h": 36, "pad": 12}],
   "clicks": [{"t": 3.0, "x": 858, "y": 204 + OFF}],
   "cursor": cur((0, 700, 450), (2.8, 858, 204 + OFF), (8, 858, 204 + OFF))},
  {"dur": 9, "img": "shots/img_copy_base.png", "imgs": [{"t": 3.0, "img": "shots/img_copy_menu.png"}], "chrome": chrome("查核文章（示意）", "（有那張圖片的網頁）"), "step": "4",
   "caption": "到有圖片的分頁，在圖片上按右鍵 → 「複製圖片」", "sub": "複製的是網頁上的「原始圖片」，不用截圖",
   "boxes": [{"t": 0.4, "dur": 99, "x": 80, "y": 90 + OFF, "w": 560, "h": 400}],
   "circles": [{"t": 3.4, "dur": 99, "x": 420, "y": 340 + OFF, "w": 330, "h": 42, "pad": 8}],
   "labels": [{"t": 1.0, "dur": 1.8, "x": 700, "y": 330 + OFF, "text": "按滑鼠右鍵", "color": "gray", "size": 28}],
   "clicks": [{"t": 2.6, "x": 500, "y": 300 + OFF}, {"t": 6.0, "x": 520, "y": 361 + OFF}],
   "cursor": cur((0, 900, 500), (2.4, 500, 300 + OFF), (5.8, 520, 361 + OFF), (9, 520, 361 + OFF))},
  {"dur": 8, "img": "shots/img_g_lens_dialog.png", "imgs": [{"t": 3.6, "img": "shots/img_lens_result_B.png"}], "chrome": D, "step": "5",
   "caption": "切回 Google 那個分頁，按 Ctrl＋V 貼上", "sub": "圖片貼上去，就自動開始搜尋",
   "keys": [{"t": 1.0, "dur": 2.4, "keys": ["Ctrl", "V"], "x": 640, "y": 560}],
   "cursor": cur((0, 520, 361 + OFF), (1.0, 640, 420 + OFF), (8, 640, 420 + OFF))},
  {"dur": 10, "img": "shots/img_lens_result_B2.png", "chrome": chrome("Google 搜尋", "google.com/search?vsrid=…"), "step": "6",
   "caption": "往下看結果：哪些是新聞或查核機構的文章？", "sub": "標題有「誤導」「錯誤」，就是查核文章。點進去讀",
   "boxes": [{"t": 0.6, "dur": 99, "x": 88, "y": 100 + OFF, "w": 206, "h": 245}, {"t": 1.6, "dur": 99, "x": 306, "y": 100 + OFF, "w": 206, "h": 245}],
   "labels": [{"t": 2.4, "dur": 99, "x": 780, "y": 220 + OFF, "text": "標題有【誤導】 ✓", "color": "green", "size": 30}],
   "cursor": cur((0, 640, 420 + OFF), (1.2, 190, 220 + OFF), (3.0, 410, 220 + OFF), (10, 410, 220 + OFF))},
  {"dur": 8, "img": "shots/img_lens_exact_B.png", "chrome": chrome("Google 搜尋", "google.com/search?vsrid=…"), "step": "＋",
   "caption": "上面的 AI 摘要只是整理，不要只讀它", "sub": "點進去，讀「查核機構」寫的原始文章，才是自己查到的證據",
   "boxes": [{"t": 0.6, "dur": 99, "x": 82, "y": 160 + OFF, "w": 640, "h": 350, "style": "gray-x"}, {"t": 3.0, "dur": 99, "x": 756, "y": 203 + OFF, "w": 426, "h": 188}],
   "labels": [{"t": 1.0, "dur": 99, "x": 300, "y": 530 + OFF, "text": "AI 摘要：先放一邊", "color": "gray", "size": 26}, {"t": 3.4, "dur": 99, "x": 800, "y": 410 + OFF, "text": "點這個，讀原始文章", "color": "green", "size": 26}]},
  title("找到查核文章後，回文件用自己的話整理", "兩種方法都可以，選你順手的", 3.5)]
save("五上L05_以圖搜圖_B方法二", {"w": 1280, "h": 720, "band": 140, "fps": 25, "scenes": steps})
print("ok")
