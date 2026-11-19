# -*- coding: utf-8 -*-
# 產生「台南小導遊｜Canva 導覽手冊」單元型網頁（2026-11-18 改版：主頁＋各課子學習單＋技能百科）。
#   主頁       L08_Canva導覽手冊/四上_L08_Canva導覽手冊.html   （發布時變成 g4/L08/index.html）
#   第 N 課    L08_Canva導覽手冊/pages/<LESSONS[n].file>       （第 1 課 worksheetId 仍是 g4-L08，舊繳交對得上）
#   技能百科   L08_Canva導覽手冊/pages/技能百科.html
# 子頁用 ../assets/ 引用素材；工作台發布會把 assets/ 與 pages/ 照搬。
#
# ── 開下一課（例：第 2 課）──
#   1. 寫一個 lesson2_steps() 回傳步驟清單（格式照 lesson1_steps()），可選 lesson2_quiz()。
#   2. 在 LESSONS 第 2 課填 steps=lesson2_steps、qdefs=[...]（q1 通常是 Canva 連結），status 改 'open'。
#   3. 執行 python build_L08.py --inject，主頁卡片、導覽列、技能卡「第 N 課」標籤會一起更新。
#   4. 05_教學活動流程.md 的單元表與漸褪表一起改。
# ── 加技能卡 ── 在 SKILLS 加一筆（lesson＝第幾課第一次用到；cats 第一個是主分類）；搜尋同義詞在 SYN。
# ── 步驟圖 ── 讀 assets/步圖/index.json（另一支工具產生）；某個操作沒有步驟圖時改用 assets/步_canva_<名>.mp4 並印警告。
#
# 生成後要跑（--inject 會自動跑）：
#   python 引導規範/chair-gate/inject.py   <各課 html>
#   python 引導規範/stepcards/inject.py    <各課 html> <技能百科 html>
#   python 引導規範/game-portal/check.py   <各課 html>
# 改內容請改這支檔案再重新產生，不要直接改 HTML。
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PROJ = os.path.dirname(os.path.dirname(ROOT))
OUTDIR = os.path.join(ROOT, 'L08_Canva導覽手冊')
PAGEDIR = os.path.join(OUTDIR, 'pages')
ASSETS = os.path.join(OUTDIR, 'assets')
STEPIMG_DIR = os.path.join(ASSETS, '步圖')
HOME_FILE = '四上_L08_Canva導覽手冊.html'
WIKI_FILE = '技能百科.html'

PORTAL = 'https://boyinslps.github.io/pcclass/games/'
CANVA_HOME = 'https://www.canva.com/'
CANVA_JOIN = 'https://www.canva.com/brand/join?token=O5u7l6t8sRfXzjBVumWtQw&brandingVariant=edu&referrer=team-invite'
TWTAINAN = 'https://www.twtainan.net/'
L04_URL = 'https://boyinslps.github.io/pcclass/g4/L04/'
L07_URL = 'https://boyinslps.github.io/pcclass/g4/L07/'
L05_URL = 'https://boyinslps.github.io/pcclass/g4/L05/'
GMAP_DIR = 'https://www.google.com/maps/dir/'
WARN = []

# ───────────────────────── 步驟圖（assets/步圖/index.json）─────────────────────────
def load_stepimgs():
    """回傳 {操作名: [{'src': '步圖/xxx_01.jpg', 'cap': ..., 'sub': ...}, ...]}；接受 dict 或 list 兩種 index.json。"""
    p = os.path.join(STEPIMG_DIR, 'index.json')
    if not os.path.exists(p):
        return {}
    try:
        with io.open(p, encoding='utf-8') as f:
            d = json.load(f)
    except Exception as e:
        WARN.append('步圖/index.json 讀不到：%s' % e)
        return {}
    groups = {}

    def add(name, e):
        fn = str(e.get('file') or e.get('src') or '').replace('\\', '/')
        if not fn:
            return
        fn = fn.split('步圖/')[-1]
        if not os.path.exists(os.path.join(STEPIMG_DIR, fn)):
            WARN.append('步圖缺檔：%s' % fn)
            return
        groups.setdefault(name, []).append(dict(src='步圖/' + fn, cap=str(e.get('caption') or ''),
                                                 sub=str(e.get('sub') or ''), step=e.get('step') or 0))

    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, dict):
                v = v.get('steps') or v.get('images') or []
            if isinstance(v, list):
                for e in v:
                    if isinstance(e, dict):
                        add(k, e)
    elif isinstance(d, list):
        for e in d:
            if not isinstance(e, dict):
                continue
            name = e.get('name') or e.get('group') or re.sub(r'_\d+\.\w+$', '', os.path.basename(str(e.get('file', ''))))
            add(name, e)
    for k in groups:
        groups[k].sort(key=lambda x: x['src'])   # 檔名 _01、_02… 就是順序（step 可能是「✓」）
    return groups


STEPIMGS = load_stepimgs()


def has_ss(name):
    return bool(STEPIMGS.get(name))


# ───────────────────────── 資料：課程、手冊頁、技能 ─────────────────────────
# status：'open' 開放（可點）／'soon' 還沒開始（灰色不可點）。ws＝worksheetId（第 1 課不可改）。
# steps／qdefs／quiz 在下面 lesson1_steps() 等函式定義後填入。
LESSONS = [
    dict(n=1, title='開工：B5 文件、認識畫面、範本封面', goal='開好 B5 文件，封面有書名和三個景點',
         status='open', file='第1課_開工與封面.html', ws='g4-L08', path='g4/L08',
         wstitle='台南小導遊：Canva 導覽手冊 第 1 課（開 B5、認識畫面、範本封面）'),
    dict(n=2, title='路線圖與行程時間表', goal='用 Google 地圖畫路線，再排出行程時間表',
         status='open', file='第2課_路線圖與行程.html', ws='g4-L08-2', path='g4/L08',
         wstitle='台南小導遊：Canva 導覽手冊 第 2 課（路線圖、行程時間表）'),
    dict(n=3, title='第 1 站景點頁', goal='照片 1～2 張、介紹、資訊；學會複製頁面',
         status='soon', file='第3課_第1站景點頁.html', ws='g4-L08-3', path='g4/L08'),
    dict(n=4, title='其他景點與美食頁', goal='複製第 1 站的頁來改，美食也算一站',
         status='soon', file='第4課_其他景點與美食.html', ws='g4-L08-4', path='g4/L08'),
    dict(n=5, title='小提醒、封底、檢查與分享', goal='做小提醒和封底，整本檢查再分享',
         status='soon', file='第5課_小提醒與完成.html', ws='g4-L08-5', path='g4/L08'),
]
LESSON_BY_N = {l['n']: l for l in LESSONS}

# 手冊 11 頁：(檔名, 頁, 頁名, 第幾課做)
PAGES = [
    ('手冊_p1.jpg', 1, '封面', 1), ('手冊_p2.jpg', 2, '目錄', 2), ('手冊_p3.jpg', 3, '行程規劃', 2),
    ('手冊_p4.jpg', 4, '路線圖', 2), ('手冊_p5.jpg', 5, '第1站景點', 3), ('手冊_p6.jpg', 6, '第2站景點', 4),
    ('手冊_p7.jpg', 7, '第3站午餐', 4), ('手冊_p8.jpg', 8, '第4站景點', 4), ('手冊_p9.jpg', 9, '第5站小吃', 4),
    ('手冊_p10.jpg', 10, '小提醒', 5), ('手冊_p11.jpg', 11, '封底', 5),
]

CATS = [('start', '開始'), ('text', '文字'), ('image', '圖片'), ('page', '頁面'), ('done', '完成')]

# 技能卡。cats：第一個是主分類（顏色、分組）；media：('op', 操作名)＝有步驟圖用步驟圖、沒有用影片
#   ('img', 檔名)／('keys', [...])／('links', [(字, 網址, 樣式)])／('big', 一句大字)
SKILLS = [
    dict(id='join', cats=['start'], lesson=1, title='加入團隊、開 Canva',
         kw=['加入', '團隊', '邀請', '登入', '帳號', '開 Canva', '第一次'],
         media=('links', [('加入班級 Canva 團隊', CANVA_JOIN, 'primary'), ('開 Canva', CANVA_HOME, 'second')]),
         points=['第一次：按「<b>加入班級 Canva 團隊</b>」，用學校帳號登入', '之後：按「<b>開 Canva</b>」就好', '登不進去，<b>舉手</b>']),
    dict(id='open-b5', cats=['start'], lesson=1, title='開 B5 新文件',
         kw=['B5', 'A4', '新文件', '建立', '自訂尺寸', '公釐', '176', '250', '紙', '怎麼開', '開檔'],
         media=('op', '開B5文件'),
         points=['按「<b>建立</b>」→「<b>自訂尺寸</b>」', '單位選「<b>公釐</b>」，寬 <b>176</b>、高 <b>250</b>', '按「<b>建立新設計</b>」']),
    dict(id='rename', cats=['start'], lesson=1, title='改作品名字',
         kw=['作品名字', '檔名', '改名', '名字', '貼上', 'Ctrl+V'],
         media=('op', '改檔名'),
         points=['點右上角的<b>作品名字</b>', '<kbd>Ctrl</kbd> + <kbd>A</kbd>，再 <kbd>Ctrl</kbd> + <kbd>V</kbd> 貼上（或打字）', '按 <kbd>Enter</kbd>；例：<b>40205 我的台南手冊</b>']),
    dict(id='screen', cats=['start'], lesson=1, title='認識編輯畫面',
         kw=['畫面', '介面', '工具列', '在哪裡', '找不到', '白紙'],
         media=('img', '介面_標記.jpg'),
         points=['<b>左邊工具列</b>：範本、文字、上傳都在這', '<b>中間白紙</b>：作品放這裡', '<b>下面</b>：小頁面圖換頁，<b>＋</b> 多一頁', '<b>右上</b>：作品名字、分享']),
    dict(id='undo', cats=['start'], lesson=1, title='弄錯了：復原',
         kw=['復原', '還原', '上一步', '弄錯', '弄亂', '打錯', '刪錯', '救回', 'Ctrl+Z', 'undo'],
         media=('keys', ['Ctrl', 'Z']),
         points=['按 <kbd>Ctrl</kbd> + <kbd>Z</kbd>，回到上一步', '多按幾次，就多回幾步', '刪錯了也按 <kbd>Ctrl</kbd> + <kbd>Z</kbd>；救不回來再<b>舉手</b>']),
    dict(id='save', cats=['start', 'done'], lesson=1, title='要存檔嗎？',
         kw=['存檔', '儲存', '存起來', '不見了', '關掉', '下次'],
         media=('big', 'Canva 會自動存，不用按存檔'),
         points=['做的東西 Canva 會<b>自動存</b>', '下次打開 Canva，在首頁點<b>你的作品</b>，就能接著做', '找不到作品，<b>舉手</b>']),
    dict(id='template', cats=['page', 'start'], lesson=1, title='選範本',
         kw=['範本', '模板', '版型', '套用', '封面', '搜尋範本'],
         media=('op', '選範本'),
         points=['左邊按「<b>範本</b>」，打關鍵字，按 <kbd>Enter</kbd>', '點你喜歡的範本', '左邊出現好幾頁，點<b>最上面那張</b>（封面）', '不要按「<b>套用全部</b>」']),
    dict(id='edit-text', cats=['text'], lesson=1, title='改文字',
         kw=['改字', '打字', '改文字', '連按兩下', '全選', 'Ctrl+A', '書名'],
         media=('op', '改封面文字'),
         points=['在字上<b>連按兩下</b>，看到打字的直線', '按 <kbd>Ctrl</kbd> + <kbd>A</kbd> 全選', '直接<b>打新的字</b>']),
    dict(id='delete', cats=['text', 'image'], lesson=1, title='刪掉不要的字或圖',
         kw=['刪', '刪掉', '刪除', '不要的', '多的', '清掉', 'Delete'],
         media=('keys', ['Delete']),
         points=['<b>點一下</b>要刪的字或圖（出現框）', '按 <kbd>Delete</kbd>', '刪錯了按 <kbd>Ctrl</kbd> + <kbd>Z</kbd>']),
    dict(id='font', cats=['text'], lesson=1, title='換字型',
         kw=['字型', '字體', '字的樣子', '字樣', '書法', '可愛的字', '繁體中文'],
         media=('img', '封面_文字字型.jpg'),
         points=['點文字，按工具列<b>最左邊的字型名字</b>', '選後面寫「<b>繁體中文</b>」的字型', '點一個就換；一頁字型<b>不超過 2 種</b>']),
    dict(id='size-color', cats=['text'], lesson=1, title='字的大小和顏色',
         kw=['大小', '放大', '變大', '縮小', '變小', '字太小', '字太大', '顏色', '粗體', '工具列'],
         media=('img', '封面_文字工具列.jpg'),
         points=['<b>＋</b> 變大、<b>－</b> 變小，也可以點數字直接打', '按 <b>A</b> 選顏色', '<b>B</b> 是粗體']),
    dict(id='move-text', cats=['text'], lesson=1, title='移動文字、調文字框',
         kw=['移動', '拖曳', '位置', '文字框', '白點', '換行', '寬度', '對齊線'],
         media=('img', '封面_文字移動.jpg'),
         points=['<b>按住</b>框，拖到新位置', '<b>四個角</b>的白點：字一起變大變小', '<b>左右</b>的白點：只改寬度，字會換行']),
    dict(id='add-text', cats=['text'], lesson=2, title='加新的文字',
         kw=['新增文字', '加字', '標題', '文字方塊', '加文字', '時間表'],
         media=('op', '加文字'),
         points=['左邊按「<b>文字</b>」', '選「<b>新增標題</b>」或「<b>新增少量內文文字</b>」', '直接打字，再拖到想放的地方']),
    dict(id='upload-photo', cats=['image'], lesson=2, title='上傳照片、放到紙上',
         kw=['上傳', '放照片', '加照片', '插入圖片', '截圖', '拉大', '地圖'],
         media=('op', '加照片'),
         points=['左邊「<b>上傳</b>」→「<b>上傳檔案</b>」', '到「<b>下載</b>」選照片', '點照片放上紙，<b>拉角</b>變大']),
    dict(id='gmap-route', cats=['image'], lesson=2, title='用 Google 地圖畫路線',
         kw=['地圖', '路線', '路線圖', 'Google 地圖', '導航', '機車', '起點', '終點', '目的地'],
         media=('op', 'Google地圖路線'),
         points=['按「<b>路線</b>」，打上<b>起點</b>和<b>終點</b>', '交通方式選「<b>機車</b>」', '按「<b>新增目的地</b>」，每一站都加進去']),
    dict(id='snip-paste', cats=['image'], lesson=2, title='截圖貼到 Canva',
         kw=['截圖', '剪取', '螢幕擷取', 'Win+Shift+S', '抓圖', '貼圖', '地圖', '貼上'],
         media=('op', '截圖貼上'),
         points=['按 <kbd>Win</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd>', '用滑鼠<b>拖一個框</b>，框住要的地方', '回 Canva，按 <kbd>Ctrl</kbd> + <kbd>V</kbd> 貼上，<b>拉角</b>變大']),
    dict(id='new-page', cats=['page'], lesson=2, title='新增頁面、換頁',
         kw=['新增頁面', '加一頁', '多一頁', '新的紙', '換頁', '下一頁', '封底'],
         media=('op', '新增頁面'),
         points=['畫面下面按「<b>＋</b>」，多一張紙', '點下面的<b>小頁面圖</b>，換到那一頁']),
    dict(id='save-photo', cats=['image'], lesson=3, title='從台南旅遊網存照片',
         kw=['存照片', '下載照片', '另存圖片', '右鍵', '台南旅遊網', '找照片'],
         media=('links', [('開台南旅遊網', TWTAINAN, 'second')]),
         points=['到台南旅遊網，找到你的景點', '在照片上按<b>右鍵</b> →「<b>另存圖片</b>」', '存到「<b>下載</b>」資料夾']),
    dict(id='align-list', cats=['text'], lesson=2, title='靠左和項目符號',
         kw=['靠左', '對齊', '置中', '圓點', '項目符號', '列點', '清單', '目錄'],
         media=('op', '目錄靠左列點'),
         points=['連按兩下 → <kbd>Ctrl</kbd> + <kbd>A</kbd>', '「<b>對齊</b>」按到靠左', '按「<b>項目符號</b>」，每行前面就有小圓點']),
    dict(id='share', cats=['done'], lesson=1, title='分享連結（交作業）',
         kw=['分享', '連結', '網址', '交作業', '繳交', '可供檢視', '權限', '複製連結', '傳給老師', '怎麼交', '貼上'],
         media=('op', '分享連結'),
         points=['<b>分享</b> → 點「只有你可存取」→ 選「<b>任何具有此連結者</b>」', '改成「<b>可供檢視</b>」', '按「<b>複製連結</b>」，回學習單 <kbd>Ctrl</kbd> + <kbd>V</kbd>']),
]

# 搜尋同義詞：一組裡任何一個字被搜尋，就用整組去找標題和關鍵字
SYN = [
    ['字型', '字體', '字的樣子', '字樣', '字形', '字的形狀', 'font'],
    ['大小', '放大', '變大', '縮小', '變小', '大一點', '小一點', '字大小', '字太小', '字太大'],
    ['顏色', '換色', '彩色', '色彩'],
    ['圖片', '照片', '相片', '圖', '上傳', 'image', 'photo'],
    ['分享', '連結', '網址', '交作業', '繳交', '可供檢視', '權限', '傳給老師', '怎麼交'],
    ['移動', '拖', '拖曳', '搬', '位置', '換位置'],
    ['文字框', '框', '白點', '換行', '寬度'],
    ['復原', '還原', '上一步', '回去', 'undo', 'ctrl+z', '弄錯', '弄亂', '打錯', '刪錯', '救回'],
    ['刪', '刪掉', '刪除', '不要的', '多的', '清掉', 'delete'],
    ['存檔', '儲存', '存起來', '不見了', '保存'],
    ['範本', '模板', '樣板', '版型', '套用'],
    ['頁面', '新增頁面', '加一頁', '多一頁', '新的紙', '換頁', '下一頁', '封底', '頁'],
    ['新增文字', '加字', '加文字', '文字方塊', '打新的字'],
    ['改字', '改文字', '打字', '連按兩下', '全選', 'ctrl+a'],
    ['貼上', '貼', 'ctrl+v', '貼連結'],
    ['名字', '檔名', '作品名字', '改名'],
    ['團隊', '加入', '邀請', '登入', '帳號'],
    ['靠左', '對齊', '置中', '圓點', '點點', '小圓點', '項目符號', '符號', '列點', '清單'],
    ['b5', 'a4', '紙張', '尺寸', '公釐', '新文件', '開新', '建立', '怎麼開', '開檔'],
    ['畫面', '介面', '工具列', '在哪', '找不到'],
    ['地圖', '路線', 'google 地圖', '導航', '路線圖'],
    ['截圖', '剪取', '螢幕擷取', 'win+shift+s', '抓圖'],
    ['時間表', '行程', '幾點', '時間'],
]


def lesson_tag(n):
    l = LESSON_BY_N.get(n)
    return ('第 %d 課' % n) if l and l['status'] == 'open' else ('第 %d 課會用到' % n)


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)


def video_of(name):
    return '步_canva_' + name


def skills_json():
    out = []
    for s in SKILLS:
        k, v = s['media']
        d = dict(id=s['id'], cat=s['cats'][0], cats=s['cats'], lesson=s['lesson'], tag=lesson_tag(s['lesson']),
                 learned=LESSON_BY_N[s['lesson']]['status'] == 'open',
                 title=s['title'], kw=s['kw'], media=[k, v], points=s['points'])
        extra = ''
        if k == 'op':
            d['video'] = video_of(v)
            d['ss'] = STEPIMGS.get(v, [])
            extra = ' '.join(i['cap'] + ' ' + i['sub'] for i in d['ss'])
        d['text'] = ' '.join(strip_tags(p) for p in s['points']) + ' ' + extra
        out.append(d)
    return json.dumps(out, ensure_ascii=False)


# ───────────────────────── 共用外觀 ─────────────────────────
CSS = r'''
  :root{
    --bg:#FFFBF3;--card:#ffffff;--ink:#1e293b;--muted:#64748b;--line:#e2e8f0;
    --brand:#ea580c;--brand-d:#c2410c;--brand-bg:#fff7ed;
    --start:#0369a1;--start-bg:#e0f2fe;--start-bd:#7dd3fc;
    --text:#c2410c;--text-bg:#ffedd5;--text-bd:#fdba74;
    --image:#047857;--image-bg:#d1fae5;--image-bd:#6ee7b7;
    --page:#6d28d9;--page-bg:#ede9fe;--page-bd:#c4b5fd;
    --done:#be123c;--done-bg:#ffe4e6;--done-bd:#fda4af;
  }
  html{scroll-behavior:smooth}
  body{font-family:'Noto Sans TC',sans-serif;background:var(--bg);color:var(--ink);font-size:19px;line-height:1.7;margin:0}
  .cute{font-family:'Baloo 2','Noto Sans TC',cursive}
  .wrap{max-width:1120px;margin:0 auto;padding:0 20px}
  .hidden.hidden,.sc-flat .sc-slide.hidden{display:none !important}
  @media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
  kbd{background:#f1f5f9;border:1px solid #cbd5e1;border-bottom-width:3px;border-radius:6px;padding:0 6px;font-family:inherit;font-weight:700;color:var(--ink)}
  .shot{border-radius:14px;border:3px solid #fff;box-shadow:0 6px 20px rgba(0,0,0,.14);width:100%;display:block;background:#fff}
  .zoomable{cursor:zoom-in}
  a{color:inherit}

  /* 頁首導覽列 */
  .topnav{background:#fff;border-bottom:3px solid #fed7aa}
  .topnav .wrap{display:flex;align-items:center;gap:18px;min-height:64px}
  .brand{display:flex;align-items:baseline;gap:10px;text-decoration:none;white-space:nowrap}
  .brand b{font-family:'Baloo 2','Noto Sans TC',cursive;font-size:1.5rem;font-weight:800;color:var(--brand)}
  .brand span{font-size:.95rem;font-weight:700;color:var(--muted)}
  .tabs{display:flex;gap:6px;flex:1}
  .tabs a{display:inline-flex;align-items:center;gap:6px;text-decoration:none;font-weight:800;font-size:1.05rem;color:#475569;padding:8px 18px;border-radius:999px;border:2px solid transparent}
  .tabs a:hover{background:var(--brand-bg);border-color:#fed7aa}
  .tabs a.on{background:var(--brand);color:#fff}
  .btn-canva{display:inline-flex;align-items:center;gap:6px;text-decoration:none;font-weight:800;color:#0f766e;border:2px solid #5eead4;background:#f0fdfa;border-radius:999px;padding:6px 16px;white-space:nowrap}
  .btn-canva:hover{background:#ccfbf1}

  /* 分類色 */
  .c-start{--c:var(--start);--cbg:var(--start-bg);--cbd:var(--start-bd)}
  .c-text{--c:var(--text);--cbg:var(--text-bg);--cbd:var(--text-bd)}
  .c-image{--c:var(--image);--cbg:var(--image-bg);--cbd:var(--image-bd)}
  .c-page{--c:var(--page);--cbg:var(--page-bg);--cbd:var(--page-bd)}
  .c-done{--c:var(--done);--cbg:var(--done-bg);--cbd:var(--done-bd)}
  .c-all{--c:#334155;--cbg:#f1f5f9;--cbd:#cbd5e1}
  .chip{display:inline-flex;align-items:center;gap:6px;font:inherit;font-weight:800;font-size:1.1rem;padding:6px 18px;border-radius:999px;border:3px solid var(--cbd);background:#fff;color:var(--c);cursor:pointer}
  .chip:hover{background:var(--cbg)}
  .chip.on{background:var(--c);border-color:var(--c);color:#fff}
  .chip .n{font-size:.85rem;opacity:.8}
  .dot{display:inline-block;width:12px;height:12px;border-radius:999px;background:var(--c);flex:none}
  .badge{display:inline-flex;align-items:center;font-weight:800;font-size:.9rem;padding:1px 12px;border-radius:999px;background:var(--cbg);color:var(--c)}
  .badge-lesson{display:inline-flex;align-items:center;font-weight:800;font-size:.9rem;padding:1px 12px;border-radius:999px;background:#ecfdf5;color:#047857;border:2px solid #a7f3d0}
  .badge-lesson.soon{background:#f8fafc;color:#64748b;border-color:#e2e8f0}

  /* 搜尋框：前面固定一個「搜尋技能」標籤（不用 placeholder） */
  .search{display:flex;align-items:stretch;border:4px solid #fdba74;border-radius:22px;background:#fff;overflow:hidden}
  .search:focus-within{border-color:var(--brand);box-shadow:0 0 0 5px rgba(234,88,12,.15)}
  .search label{display:flex;align-items:center;gap:10px;padding:0 18px;background:var(--brand-bg);color:var(--brand-d);font-weight:900;font-size:1.3rem;white-space:nowrap;border-right:3px solid #fed7aa;cursor:text}
  .search label svg{width:28px;height:28px}
  .search input{flex:1;min-width:0;border:0;font-size:1.5rem;font-weight:700;padding:14px 18px;outline:none;background:#fff;color:var(--ink)}

  /* 結果小卡 */
  .tile{display:flex;align-items:center;gap:12px;text-decoration:none;background:#fff;border:3px solid var(--cbd);border-left:12px solid var(--c);border-radius:16px;padding:10px 14px;font-weight:800;font-size:1.15rem;color:var(--ink)}
  .tile:hover{background:var(--cbg)}
  .tile small{display:block;font-size:.85rem;font-weight:700;color:var(--muted)}

  /* 步驟圖元件（三頁共用）：大圖一次一張＋上一張／下一張＋編號縮圖列＋看動畫 */
  .ss{background:#fff;border:3px solid var(--line);border-radius:20px;padding:12px}
  .ss-stage{position:relative;background:#0f172a;border-radius:14px;overflow:hidden;display:flex;justify-content:center}
  .ss-img{display:block;max-width:100%;max-height:56vh;object-fit:contain;cursor:zoom-in;background:#fff}
  .ss-hint{position:absolute;right:8px;top:8px;background:rgba(0,0,0,.55);color:#fff;font-size:13px;font-weight:700;border-radius:8px;padding:1px 8px;pointer-events:none}
  .ss-bar{display:flex;align-items:center;gap:12px;margin-top:10px}
  .ss-bar button{font:inherit;font-weight:900;font-size:1.2rem;border-radius:16px;padding:8px 20px;cursor:pointer}
  .ss-prev,.ss-next{border:3px solid #fdba74;background:#fff;color:#c2410c}
  .ss-next{background:#ea580c;border-color:#ea580c;color:#fff}
  .ss-bar button:disabled{opacity:.35;cursor:default}
  .ss-count{font-weight:900;font-size:1.2rem;color:#334155;min-width:7em;text-align:center}
  .ss-anim{margin-left:auto;border:2px solid #cbd5e1;background:#f8fafc;color:#475569;font-size:1rem !important;padding:6px 14px !important}
  .ss-thumbs{display:flex;gap:8px;margin-top:10px;overflow-x:auto;padding-bottom:4px}
  .ss-th{position:relative;flex:none;width:96px;border:3px solid #e2e8f0;border-radius:10px;padding:0;background:#fff;cursor:pointer;overflow:hidden}
  .ss-th img{display:block;width:100%;height:56px;object-fit:cover}
  .ss-th span{position:absolute;left:4px;top:4px;width:24px;height:24px;border-radius:999px;background:rgba(15,23,42,.75);color:#fff;font-size:.8rem;font-weight:900;display:flex;align-items:center;justify-content:center}
  .ss-th.on{border-color:#ea580c}
  .ss-th.on span{background:#ea580c}
  .ssov{position:fixed;inset:0;z-index:99998;background:rgba(15,23,42,.9);display:flex;align-items:center;justify-content:center;gap:14px;padding:16px;cursor:zoom-out}
  .ssov img,.ssov video{max-width:92vw;max-height:88vh;border-radius:12px;background:#fff}
  .ssov button{position:absolute;top:50%;transform:translateY(-50%);font:inherit;font-weight:900;font-size:1.4rem;border:0;border-radius:999px;width:64px;height:64px;background:rgba(255,255,255,.9);color:#c2410c;cursor:pointer}
  .ssov .l{left:14px}.ssov .r{right:14px}
  .ssov button:disabled{opacity:.3}
  .ssov .cnt{position:absolute;bottom:14px;left:50%;transform:translateX(-50%);color:#fff;font-weight:900;font-size:1.2rem;background:rgba(0,0,0,.5);border-radius:999px;padding:2px 16px}

  .sec-title{font-family:'Baloo 2','Noto Sans TC',cursive;font-size:1.9rem;font-weight:800;color:var(--ink);margin:0 0 4px}
  .sec-sub{color:var(--muted);font-weight:700;margin:0 0 14px}
  footer.sign{text-align:right;font-size:.8rem;color:#94a3b8;padding:24px 20px 18px}
'''

FONT_LINKS = '''<script src="https://cdn.tailwindcss.com"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Noto+Sans+TC:wght@500;700;900&display=swap" rel="stylesheet">'''

SVG_SEARCH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg>'
SVG_LOCK = '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>'
SVG_BOOK = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5"/><path d="M9 8h6"/></svg>'


def head(title, extra_css=''):
    return ('<!DOCTYPE html>\n<html lang="zh-Hant">\n<head>\n<meta charset="UTF-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            '<meta name="author" content="資訊老師黃博胤">\n<title>%s</title>\n%s\n<style>%s</style>\n%s\n</head>\n'
            % (title, FONT_LINKS, CSS, extra_css))


def search_box():
    return ('<div class="search"><label for="q">%s搜尋技能</label>'
            '<input id="q" type="search" autocomplete="off"></div>' % SVG_SEARCH)


def topnav(active, sub):
    """active：'home'／'lesson1'…／'wiki'；sub：True＝在 pages/ 底下。"""
    p = '' if sub else 'pages/'
    home = ('<a href="../" data-home>← 單元主頁</a>' if sub else '<a href="#top" class="on">單元主頁</a>')
    items = [home]
    for l in LESSONS:
        if l['status'] == 'open':
            items.append('<a href="%s%s" class="%s">第 %d 課</a>' % (p, l['file'], 'on' if active == 'lesson%d' % l['n'] else '', l['n']))
    items.append('<a href="%s%s" class="%s">%s技能百科</a>' % (p, WIKI_FILE, 'on' if active == 'wiki' else '', SVG_BOOK))
    brand = ('<a class="brand" href="../" data-home>' if sub else '<a class="brand" href="#top">')
    return ('<nav class="topnav" id="top"><div class="wrap">%s<b>台南小導遊</b><span>Canva 導覽手冊</span></a>'
            '<div class="tabs">%s</div>'
            '<a class="btn-canva" href="%s" target="_blank" rel="noopener">開 Canva ↗</a>'
            '</div></nav>\n' % (brand, ''.join(items), CANVA_HOME))


FOOTER = '<footer class="sign">made by 資訊老師黃博胤</footer>\n'

# 共用 JS：點圖放大、子頁「回主頁」本機修正、步驟圖元件
COMMON_JS = r'''
<script>
(function(){
  // 點小圖放大（留在這一頁）
  var ov=document.createElement('div');ov.className='ssov';ov.style.display='none';
  var im=document.createElement('img');im.alt='';ov.appendChild(im);document.body.appendChild(ov);
  function close(){ov.style.display='none';}
  ov.onclick=close;document.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
  document.addEventListener('click',function(e){
    var t=e.target;if(t&&t.classList&&t.classList.contains('zoomable')){im.src=t.getAttribute('src');im.alt=t.alt||'';ov.style.display='flex';}
  });
  // 發布後主頁是 ../（index.html）；本機預覽時沒有 index.html，改指成品檔
  if(!/github\.io$/.test(location.hostname)){
    [].forEach.call(document.querySelectorAll('a[data-home]'),function(a){a.href='../__HOME_FILE__';});
  }
})();

// ===== 步驟圖元件 =====
// 標記：<div class="ss" data-ss data-imgs='[{"src":"..","cap":".."}]' data-video="..mp4">（內部由 StepShow 自己畫）
window.StepShow=(function(){
  var last=null,ov=null,ovImg,ovCnt,ovL,ovR,ovSt=null;
  function vis(el){return el.offsetParent!==null;}
  function ensureOv(){
    if(ov)return;
    ov=document.createElement('div');ov.className='ssov';ov.style.display='none';
    ovImg=document.createElement('img');ovL=document.createElement('button');ovR=document.createElement('button');ovCnt=document.createElement('div');
    ovL.className='l';ovL.textContent='←';ovL.type='button';ovL.setAttribute('aria-label','上一張');
    ovR.className='r';ovR.textContent='→';ovR.type='button';ovR.setAttribute('aria-label','下一張');ovCnt.className='cnt';
    ov.appendChild(ovImg);ov.appendChild(ovL);ov.appendChild(ovR);ov.appendChild(ovCnt);document.body.appendChild(ov);
    ov.onclick=function(){closeOv();};
    ovL.onclick=function(e){e.stopPropagation();if(ovSt)ovSt.go(ovSt.i-1);};
    ovR.onclick=function(e){e.stopPropagation();if(ovSt)ovSt.go(ovSt.i+1);};
  }
  function paintOv(){if(!ovSt)return;var it=ovSt.imgs[ovSt.i];ovImg.src=it.src;ovImg.alt=it.cap||'';ovCnt.textContent='第 '+(ovSt.i+1)+'／'+ovSt.imgs.length+' 張';ovL.disabled=ovSt.i===0;ovR.disabled=ovSt.i===ovSt.imgs.length-1;}
  function openOv(st){ensureOv();ovSt=st;paintOv();ov.style.display='flex';}
  function closeOv(){if(ov){ov.style.display='none';}ovSt=null;}
  function playVideo(src){
    var o=document.createElement('div');o.className='ssov';
    var v=document.createElement('video');v.src=src;v.muted=true;v.loop=true;v.autoplay=true;v.playsInline=true;
    o.appendChild(v);document.body.appendChild(o);
    function key(e){if(e.key==='Escape')done();}
    function done(){document.removeEventListener('keydown',key);o.remove();}
    o.onclick=done;document.addEventListener('keydown',key);
    var p=v.play();if(p&&p.catch)p.catch(function(){});
  }
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function build(el){
    if(el.__ss)return;
    var imgs;try{imgs=JSON.parse(el.getAttribute('data-imgs')||'[]');}catch(e){imgs=[];}
    if(!imgs.length)return;
    var h='<div class="ss-stage"><img class="ss-img" alt=""><span class="ss-hint">點一下放大</span></div>'+
      '<div class="ss-bar"><button type="button" class="ss-prev">← 上一張</button><span class="ss-count"></span>'+
      '<button type="button" class="ss-next">下一張 →</button>'+
      (el.dataset.video?'<button type="button" class="ss-anim">看動畫</button>':'')+'</div>';
    if(imgs.length>1)h+='<div class="ss-thumbs">'+imgs.map(function(it,k){return '<button type="button" class="ss-th" aria-label="第 '+(k+1)+' 張"><img src="'+esc(it.src)+'" alt="" loading="lazy"><span>'+(k+1)+'</span></button>';}).join('')+'</div>';
    el.innerHTML=h;
    var st={el:el,imgs:imgs,i:0},img=el.querySelector('.ss-img'),cnt=el.querySelector('.ss-count'),
        pv=el.querySelector('.ss-prev'),nx=el.querySelector('.ss-next'),ths=[].slice.call(el.querySelectorAll('.ss-th'));
    st.go=function(i){
      st.i=Math.max(0,Math.min(imgs.length-1,i));var it=imgs[st.i];
      img.src=it.src;img.alt=it.cap||'步驟圖';img.title=it.cap||'';
      cnt.textContent='第 '+(st.i+1)+'／'+imgs.length+' 張';
      ths.forEach(function(t,k){t.classList.toggle('on',k===st.i);});
      pv.disabled=st.i===0;nx.disabled=st.i===imgs.length-1;
      if(ovSt===st)paintOv();
    };
    pv.onclick=function(){last=st;st.go(st.i-1);};
    nx.onclick=function(){last=st;st.go(st.i+1);};
    ths.forEach(function(t,k){t.onclick=function(){last=st;st.go(k);};});
    img.onclick=function(){last=st;openOv(st);};
    var an=el.querySelector('.ss-anim');if(an)an.onclick=function(){playVideo(el.dataset.video);};
    el.addEventListener('pointerdown',function(){last=st;});
    el.__ss=st;st.go(0);
  }
  function init(root){[].forEach.call((root||document).querySelectorAll('[data-ss]'),build);}
  function target(){
    if(last&&vis(last.el))return last;
    var best=null,bd=1e9,mid=innerHeight/2;
    [].forEach.call(document.querySelectorAll('[data-ss]'),function(el){
      if(!el.__ss||!vis(el))return;var r=el.getBoundingClientRect();if(r.bottom<0||r.top>innerHeight)return;
      var d=Math.abs((r.top+r.bottom)/2-mid);if(d<bd){bd=d;best=el.__ss;}
    });
    return best;
  }
  document.addEventListener('keydown',function(e){
    if(ov&&ov.style.display!=='none'&&ovSt){
      if(e.key==='Escape')closeOv();
      else if(e.key==='ArrowLeft'){ovSt.go(ovSt.i-1);e.preventDefault();}
      else if(e.key==='ArrowRight'){ovSt.go(ovSt.i+1);e.preventDefault();}
      return;
    }
    var t=e.target&&e.target.tagName;if(t==='INPUT'||t==='TEXTAREA'||t==='SELECT')return;
    if(e.key!=='ArrowLeft'&&e.key!=='ArrowRight')return;
    var st=target();if(!st)return;
    st.go(st.i+(e.key==='ArrowRight'?1:-1));e.preventDefault();
  });
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){init();});else init();
  return {init:init};
})();
</script>
'''

SEARCH_JS = r'''
<script>
var SKILLS=__SKILLS__;
var CATS=__CATS__;
var SYN=__SYN__;
function skNorm(s){return String(s||'').toLowerCase().replace(/\s+/g,'').replace(/＋/g,'+');}
function skCatName(c){for(var i=0;i<CATS.length;i++)if(CATS[i][0]===c)return CATS[i][1];return '';}
function skCatIdx(c){for(var i=0;i<CATS.length;i++)if(CATS[i][0]===c)return i;return 99;}
// 一個搜尋詞 → 同義詞（只拿兩個字以上的，避免「圖」「頁」這種單字到處都對到）
function skSyn(tok){
  var out=[];
  SYN.forEach(function(g){
    var hit=g.some(function(m){m=skNorm(m);return m===tok||(m.length>=2&&tok.indexOf(m)>=0)||(tok.length>=2&&m.indexOf(tok)>=0);});
    if(hit)g.forEach(function(m){m=skNorm(m);if(m!==tok&&m.length>=2)out.push(m);});
  });
  return out;
}
// 有搜尋字就在「全部」裡找（cat 只在沒打字時用）；標題完全相同排第一
function skSearch(q,cat){
  var whole=skNorm(q),toks=String(q||'').split(/[\s,，、。？?]+/).map(skNorm).filter(Boolean),res=[];
  if(toks.length)cat='all';
  SKILLS.forEach(function(s,i){
    if(cat&&cat!=='all'&&s.cats.indexOf(cat)<0)return;
    var T=skNorm(s.title),K=skNorm(s.kw.join('|')),P=skNorm(s.text),score=0,ok=true;
    if(whole&&(T===whole||T.replace(/[？?]/g,'')===whole.replace(/[？?]/g,'')))score+=100;
    toks.forEach(function(tok){
      var best=0;
      if(T.indexOf(tok)>=0)best=6;else if(K.indexOf(tok)>=0)best=5;else if(P.indexOf(tok)>=0)best=2;
      if(!best)skSyn(tok).forEach(function(t){if(T.indexOf(t)>=0||K.indexOf(t)>=0)best=Math.max(best,3);});
      if(!best)ok=false;score+=best;
    });
    if(ok)res.push({s:s,score:score,i:i});
  });
  res.sort(function(a,b){return (b.score-a.score)||(skCatIdx(a.s.cat)-skCatIdx(b.s.cat))||(a.i-b.i);});
  return res.map(function(r){return r.s;});
}
</script>
'''


def search_js():
    return (SEARCH_JS.replace('__SKILLS__', skills_json())
            .replace('__CATS__', json.dumps(CATS, ensure_ascii=False))
            .replace('__SYN__', json.dumps(SYN, ensure_ascii=False)))


def common_js():
    return COMMON_JS.replace('__HOME_FILE__', HOME_FILE)


def cat_chips(with_count=False):
    h = ['<button type="button" class="chip c-all on" data-cat="all">全部%s</button>' %
         ('<span class="n">%d</span>' % len(SKILLS) if with_count else '')]
    for c, name in CATS:
        n = sum(1 for s in SKILLS if c in s['cats'])
        h.append('<button type="button" class="chip c-%s" data-cat="%s"><span class="dot"></span>%s%s</button>' %
                 (c, c, name, '<span class="n">%d</span>' % n if with_count else ''))
    return ''.join(h)


def esc_attr(s):
    return s.replace('&', '&amp;').replace("'", '&#39;').replace('"', '&quot;')


def op_media(name, base='../'):
    """一個操作的呈現：有步驟圖用步驟圖元件（附看動畫），沒有用步驟卡影片。"""
    v = video_of(name)
    imgs = STEPIMGS.get(name)
    if imgs:
        data = json.dumps([dict(src=base + 'assets/' + i['src'], cap=i['cap']) for i in imgs], ensure_ascii=False)
        return '<div class="ss" data-ss data-imgs=\'%s\' data-video="%sassets/%s.mp4"></div>' % (esc_attr(data), base, v)
    WARN.append('沒有步驟圖，先用影片：%s（%s.mp4）' % (name, v))
    return '<div class="sc-media" data-src="%sassets/%s.mp4" data-poster="%sassets/%s_封面.jpg"></div>' % (base, v, base, v)


# ───────────────────────── 主頁 ─────────────────────────
HOME_CSS = r'''<style>
  .hero{background:linear-gradient(135deg,#fff7ed 0%,#ffedd5 55%,#fde68a 100%);border:4px solid #fdba74;border-radius:32px;padding:28px 30px;display:grid;grid-template-columns:minmax(0,1fr) 160px;gap:24px;align-items:center;margin-top:24px}
  .hero h1{font-family:'Baloo 2','Noto Sans TC',cursive;font-size:2.8rem;line-height:1.15;font-weight:900;color:var(--brand-d);margin:0}
  .hero .lead{font-size:1.3rem;font-weight:800;color:#7c2d12;margin:8px 0 16px}
  .bigbtns{display:flex;gap:12px;flex-wrap:nowrap;align-items:center}
  .bigbtns .arrow{font-size:1.6rem;font-weight:900;color:#c2410c}
  .bigbtn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:68px;padding:0 18px;border-radius:20px;font-size:1.25rem;font-weight:900;text-decoration:none;white-space:nowrap;box-shadow:0 5px 0 rgba(0,0,0,.18)}
  .bigbtn:active{transform:translateY(3px);box-shadow:0 2px 0 rgba(0,0,0,.18)}
  .bigbtn.primary{background:var(--brand);color:#fff}.bigbtn.primary:hover{background:var(--brand-d)}
  .bigbtn.second{background:#0f766e;color:#fff}.bigbtn.second:hover{background:#115e59}
  .bigbtn.third{background:#7c3aed;color:#fff}.bigbtn.third:hover{background:#6d28d9}
  .bigbtn .step{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;border-radius:999px;background:rgba(255,255,255,.25);font-size:1.1rem}
  .hero .note{margin:12px 0 0;font-weight:800;color:#9a3412;font-size:1.1rem}
  .hero .cover{transform:rotate(3deg)}
  section.block{background:#fff;border:3px solid var(--line);border-radius:28px;padding:24px 26px;margin-top:24px}
  .lesson{display:grid;grid-template-columns:110px minmax(0,1fr) 200px;gap:18px;align-items:center;border:3px solid var(--line);border-radius:22px;padding:14px 18px;margin-bottom:12px}
  .lesson .lnum{font-family:'Baloo 2','Noto Sans TC',cursive;font-weight:900;font-size:1.35rem;text-align:center;border-radius:18px;padding:12px 4px}
  .lesson .ltitle{font-size:1.4rem;font-weight:900;margin:0;line-height:1.35}
  .lesson .lgoal{margin:2px 0 6px;font-weight:700;color:var(--muted)}
  .lesson .lskills{display:flex;flex-wrap:wrap;gap:6px}
  .lesson .lgo{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:58px;border-radius:18px;font-size:1.2rem;font-weight:900;text-decoration:none;text-align:center}
  .lesson.open{border-color:#fdba74;background:#fffaf5}
  .lesson.open .lnum{background:var(--brand);color:#fff}
  .lesson.open .lgo{background:var(--brand);color:#fff;box-shadow:0 4px 0 #9a3412}
  .lesson.open .lgo:hover{background:var(--brand-d)}
  .lesson.soon{background:#f8fafc;color:#94a3b8}
  .lesson.soon .lnum{background:#e2e8f0;color:#64748b}
  .lesson.soon .ltitle{color:#64748b}
  .lesson.soon .lgo{background:#e2e8f0;color:#64748b;cursor:not-allowed}
  .pgs{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:16px}
  .pg{margin:0;text-align:center}
  .pg figcaption{margin-top:6px;font-weight:800;font-size:1.05rem;line-height:1.3}
  .pg figcaption b{color:var(--brand)}
  .pg figcaption .badge-lesson{display:table;margin:4px auto 0;font-size:.8rem}
  .chips{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 16px}
  .results{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
  .empty{font-size:1.2rem;font-weight:800;color:var(--muted);padding:10px 4px}
  .datarow{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-top:18px;padding-top:14px;border-top:2px dashed var(--line);font-weight:800}
  .datarow a{text-decoration:none;border:3px solid #fcd34d;background:#fffbeb;color:#92400e;border-radius:16px;padding:6px 16px}
  .datarow a:hover{background:#fef3c7}
</style>'''


def home_page():
    rows = []
    for l in LESSONS:
        sk = [s for s in SKILLS if s['lesson'] == l['n']]
        if l['status'] == 'open':
            chips = ''.join('<a class="badge c-%s" href="pages/%s#%s" style="text-decoration:none">%s</a>' %
                            (s['cats'][0], WIKI_FILE, s['id'], s['title']) for s in sk)
            rows.append('<div class="lesson open"><div class="lnum">第 %d 課</div>'
                        '<div class="lbody"><p class="ltitle">%s</p><p class="lgoal">%s</p><div class="lskills">%s</div></div>'
                        '<a class="lgo" href="pages/%s">進入第 %d 課 →</a></div>'
                        % (l['n'], l['title'], l['goal'], chips, l['file'], l['n']))
        else:
            chips = ''.join('<span class="badge c-all">%s</span>' % s['title'] for s in sk)
            rows.append('<div class="lesson soon" aria-disabled="true"><div class="lnum">第 %d 課</div>'
                        '<div class="lbody"><p class="ltitle">%s</p><p class="lgoal">%s</p><div class="lskills">%s</div></div>'
                        '<span class="lgo">%s還沒開始</span></div>' % (l['n'], l['title'], l['goal'], chips, SVG_LOCK))
    thumbs = ['<figure class="pg"><img src="assets/%s" alt="第 %d 頁：%s" class="shot zoomable" loading="lazy">'
              '<figcaption><b>%d</b> %s<span class="badge-lesson%s">第 %d 課</span></figcaption></figure>'
              % (f, n, name, n, name, '' if LESSON_BY_N[ln]['status'] == 'open' else ' soon', ln)
              for f, n, name, ln in PAGES]
    cur = [l for l in LESSONS if l['status'] == 'open'][-1]   # 最新開放的課

    body = '''<body>
%s
<main class="wrap">
  <header class="hero">
    <div>
      <h1>台南小導遊｜Canva 導覽手冊</h1>
      <p class="lead">用 Canva 做一本 B5 台南旅遊導覽手冊，一課做幾頁。</p>
      <div class="bigbtns">
        <a class="bigbtn primary" href="%s" target="_blank" rel="noopener"><span class="step">1</span>加入班級 Canva 團隊 ↗</a>
        <span class="arrow" aria-hidden="true">→</span>
        <a class="bigbtn second" href="%s" target="_blank" rel="noopener"><span class="step">2</span>開 Canva ↗</a>
        <span class="arrow" aria-hidden="true">→</span>
        <a class="bigbtn third" href="pages/%s"><span class="step">3</span>照第 %d 課做 →</a>
      </div>
      <p class="note">第一次用：先按「加入班級 Canva 團隊」，用學校帳號登入。</p>
    </div>
    <img class="shot cover zoomable" src="assets/手冊_p1.jpg" alt="手冊封面範例">
  </header>

  <section class="block" aria-labelledby="t-lessons">
    <h2 class="sec-title" id="t-lessons">單元進度</h2>
    <p class="sec-sub">一課做幾頁，五課做完一整本。</p>
    %s
  </section>

  <section class="block" aria-labelledby="t-search">
    <h2 class="sec-title" id="t-search">忘記怎麼做？查技能</h2>
    <p class="sec-sub">打字找，或點分類。點一下看步驟。</p>
    %s
    <div class="chips" id="cats">%s</div>
    <div class="results" id="results"></div>
  </section>

  <section class="block" aria-labelledby="t-book">
    <h2 class="sec-title" id="t-book">我們的手冊長這樣</h2>
    <p class="sec-sub">一共 11 頁，點圖放大。<b style="color:var(--brand)">美食也算一站</b>：午餐、小吃各一頁。</p>
    <div class="pgs">%s</div>
    <div class="datarow">手冊的資料在你的 Google 文件：
      <a href="%s" target="_blank" rel="noopener">選景點（L04）↗</a>
      <a href="%s" target="_blank" rel="noopener">文件檢查（L07）↗</a>
    </div>
  </section>
</main>
%s''' % (topnav('home', False), CANVA_JOIN, CANVA_HOME, cur['file'], cur['n'], '\n    '.join(rows), search_box(),
         cat_chips(), '\n      '.join(thumbs), L04_URL, L07_URL, FOOTER)

    script = r'''
<script>
(function(){
  var q=document.getElementById('q'),host=document.getElementById('results'),cat='all';
  var chips=[].slice.call(document.querySelectorAll('#cats .chip'));
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function setCat(c){cat=c;chips.forEach(function(x){x.classList.toggle('on',x.dataset.cat===c);});}
  function render(){
    if(q.value.trim()&&cat!=='all')setCat('all');
    var list=skSearch(q.value,cat);
    if(!list.length){host.innerHTML='<p class="empty">找不到。換個字試試：字型、照片、分享</p>';return;}
    host.innerHTML=list.map(function(s){
      return '<a class="tile c-'+s.cat+'" href="pages/__WIKI__#'+s.id+'"><span class="dot"></span><span>'+esc(s.title)+
        '<small>'+skCatName(s.cat)+'・'+esc(s.tag)+'</small></span></a>';
    }).join('');
  }
  q.addEventListener('input',render);
  q.addEventListener('keydown',function(e){
    if(e.key==='Enter'){var list=skSearch(q.value,cat);
      if(list.length===1)location.href='pages/__WIKI__#'+list[0].id;
      else if(q.value.trim())location.href='pages/__WIKI__?q='+encodeURIComponent(q.value.trim());}
  });
  chips.forEach(function(b){b.onclick=function(){q.value='';setCat(b.dataset.cat);render();};});
  render();
})();
</script>
'''.replace('__WIKI__', WIKI_FILE)
    return head('台南小導遊｜Canva 導覽手冊', HOME_CSS) + body + search_js() + common_js() + script + '</body>\n</html>\n'


# ───────────────────────── 技能百科 ─────────────────────────
WIKI_CSS = r'''<style>
  .wikihead{display:grid;grid-template-columns:auto minmax(0,1fr);gap:22px;align-items:center;margin:22px 0 12px}
  .wikihead h1{font-family:'Baloo 2','Noto Sans TC',cursive;font-size:2.4rem;font-weight:900;color:var(--brand-d);margin:0;white-space:nowrap}
  .chips{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 18px}
  .wiki{display:grid;grid-template-columns:330px minmax(0,1fr);gap:22px;align-items:start}
  .list{background:#fff;border:3px solid var(--line);border-radius:24px;padding:12px;position:sticky;top:12px;max-height:calc(100vh - 24px);overflow:auto}
  .list h3{display:flex;align-items:center;gap:8px;font-size:1rem;font-weight:900;color:var(--c);margin:10px 8px 6px}
  .list h3:first-child{margin-top:2px}
  .item{display:flex;align-items:center;gap:10px;width:100%;text-align:left;font:inherit;font-weight:800;font-size:1.12rem;padding:9px 12px;border-radius:14px;border:2px solid transparent;background:none;color:var(--ink);cursor:pointer}
  .item:hover{background:var(--cbg)}
  .item.on{background:var(--c);color:#fff}
  .item.on .dot{background:#fff}
  .item .soon{margin-left:auto;font-size:.75rem;font-weight:800;color:#94a3b8}
  .item.on .soon{color:#fff;opacity:.85}
  .detail{background:#fff;border:4px solid var(--cbd);border-top:14px solid var(--c);border-radius:28px;padding:22px 26px}
  .detail h2{font-family:'Baloo 2','Noto Sans TC',cursive;font-size:2.3rem;font-weight:900;color:var(--c);margin:0 0 6px;line-height:1.2}
  .detail .meta{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
  .detail .media{margin-bottom:18px}
  .detail .media .shot{max-height:420px;object-fit:contain;width:100%}
  .detail .media .sc-media video{max-height:420px}
  .detail .media .ss-img{max-height:420px}
  .points{list-style:none;margin:0;padding:0;counter-reset:pt}
  .points li{counter-increment:pt;display:flex;gap:14px;align-items:flex-start;font-size:1.4rem;font-weight:800;line-height:1.5;margin:0 0 12px}
  .points li:before{content:counter(pt);flex:none;display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:999px;background:var(--c);color:#fff;font-size:1.2rem;margin-top:2px}
  .points b{color:var(--c)}
  .keys{display:flex;align-items:center;justify-content:center;gap:18px;background:var(--cbg);border-radius:20px;padding:40px 10px;font-size:2.4rem;font-weight:900;color:var(--ink)}
  .keys kbd{font-size:3rem;padding:6px 28px;border-radius:14px;border-bottom-width:7px;background:#fff}
  .bigsay{background:var(--cbg);border-radius:20px;padding:40px 20px;text-align:center;font-size:2.1rem;font-weight:900;color:var(--c)}
  .links{display:flex;gap:14px;flex-wrap:wrap;background:var(--cbg);border-radius:20px;padding:28px}
  .links a{display:inline-flex;align-items:center;min-height:64px;padding:0 26px;border-radius:18px;font-size:1.35rem;font-weight:900;text-decoration:none;color:#fff;box-shadow:0 4px 0 rgba(0,0,0,.18)}
  .links a.primary{background:var(--brand)}.links a.second{background:#0f766e}
  .empty{font-size:1.2rem;font-weight:800;color:var(--muted);padding:12px}
</style>'''


def wiki_page():
    body = '''<body>
%s
<main class="wrap">
  <div class="wikihead"><h1>技能百科</h1>%s</div>
  <div class="chips" id="cats" role="tablist">%s</div>
  <div class="wiki">
    <aside class="list" id="list" aria-label="技能清單"></aside>
    <div class="sc sc-flat sc-nonum" data-sc><article class="detail" id="detail" aria-live="polite"></article></div>
  </div>
</main>
%s''' % (topnav('wiki', True), search_box(), cat_chips(True), FOOTER)

    script = r'''
<script>
(function(){
  var q=document.getElementById('q'),listEl=document.getElementById('list'),det=document.getElementById('detail');
  var cat='all',sel=null;
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function byId(id){for(var i=0;i<SKILLS.length;i++)if(SKILLS[i].id===id)return SKILLS[i];return null;}
  function media(s){
    var m=s.media,k=m[0],v=m[1];
    if(k==='op'){
      if(s.ss&&s.ss.length){
        var data=JSON.stringify(s.ss.map(function(i){return {src:'../assets/'+i.src,cap:i.cap};}));
        return '<div class="ss" data-ss data-imgs="'+esc(data)+'" data-video="../assets/'+s.video+'.mp4"></div>';
      }
      return '<div class="sc-media" data-src="../assets/'+s.video+'.mp4" data-poster="../assets/'+s.video+'_封面.jpg"></div>';
    }
    if(k==='img')return '<img class="shot zoomable" src="../assets/'+v+'" alt="'+esc(s.title)+' 的畫面（點一下放大）">';
    if(k==='keys')return '<div class="keys">'+v.map(function(x){return '<kbd>'+esc(x)+'</kbd>';}).join(' + ')+'</div>';
    if(k==='big')return '<div class="bigsay">'+esc(v)+'</div>';
    if(k==='links')return '<div class="links">'+v.map(function(x){return '<a class="'+x[2]+'" href="'+x[1]+'" target="_blank" rel="noopener">'+esc(x[0])+' ↗</a>';}).join('')+'</div>';
    return '';
  }
  function showDetail(s){
    if(!s){det.className='detail c-all';det.innerHTML='<p class="empty">找不到。換個字試試：字型、照片、分享</p>';return;}
    det.className='detail c-'+s.cat;
    det.innerHTML='<h2>'+esc(s.title)+'</h2><div class="meta">'+s.cats.map(function(c){return '<span class="badge c-'+c+'">'+skCatName(c)+'</span>';}).join('')+
      '<span class="badge-lesson'+(s.learned?'':' soon')+'">'+esc(s.tag)+'</span></div>'+
      '<div class="media">'+media(s)+'</div><ol class="points">'+s.points.map(function(p){return '<li><span>'+p+'</span></li>';}).join('')+'</ol>';
    StepShow.init(det);
  }
  function render(){
    var list=skSearch(q.value,cat);
    if(!list.length){listEl.innerHTML='<p class="empty">找不到</p>';sel=null;det.__cur=null;showDetail(null);return;}
    if(!sel||list.indexOf(sel)<0)sel=list[0];
    var h='',last=null,grouped=!q.value.trim();
    list.forEach(function(s){
      var gc=(grouped&&cat!=='all')?cat:s.cat;
      if(grouped&&gc!==last){h+='<h3 class="c-'+gc+'"><span class="dot"></span>'+skCatName(gc)+'</h3>';last=gc;}
      h+='<button type="button" class="item c-'+s.cat+(s===sel?' on':'')+'" data-id="'+s.id+'"><span class="dot"></span>'+esc(s.title)+
        (s.learned?'':'<span class="soon">第 '+s.lesson+' 課</span>')+'</button>';
    });
    listEl.innerHTML=h;
    if(!det.__cur||det.__cur!==sel){det.__cur=sel;showDetail(sel);}
  }
  function setCat(c){
    cat=c;[].forEach.call(document.querySelectorAll('#cats .chip'),function(x){var on=x.dataset.cat===c;x.classList.toggle('on',on);x.setAttribute('aria-selected',on?'true':'false');});
  }
  listEl.addEventListener('click',function(e){var b=e.target.closest('.item');if(!b)return;sel=byId(b.dataset.id);history.replaceState(null,'','#'+sel.id);render();det.scrollIntoView({behavior:'smooth',block:'start'});});
  q.addEventListener('input',function(){if(q.value.trim())setCat('all');sel=null;render();});
  [].forEach.call(document.querySelectorAll('#cats .chip'),function(b){b.onclick=function(){q.value='';setCat(b.dataset.cat);sel=null;render();};});
  function fromUrl(){
    var sp=new URLSearchParams(location.search),h=decodeURIComponent(location.hash.replace(/^#/,''));
    q.value=sp.get('q')||'';
    var c=sp.get('cat');setCat(c&&skCatName(c)?c:'all');
    sel=null;
    if(h&&byId(h)){q.value='';setCat('all');sel=byId(h);}
    render();
  }
  window.addEventListener('hashchange',fromUrl);
  fromUrl();
})();
</script>
'''
    return head('技能百科｜台南小導遊', WIKI_CSS) + body + search_js() + common_js() + script + '</body>\n</html>\n'


# ───────────────────────── 子學習單（通用）─────────────────────────
LESSON_CSS = r'''<style>
  .idbar{background:#fff;border-bottom:2px solid #fed7aa}
  .idbar .wrap{display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding-top:6px;padding-bottom:6px;font-size:1rem}
  .idbar label{display:flex;align-items:center;gap:6px;color:var(--muted);font-weight:700}
  .idbar .ltitle{margin-left:auto;font-weight:900;color:#c2410c;font-size:1.1rem}
  .idbar .ltitle small{color:var(--muted);font-weight:800;margin-right:6px}
  .idnum{width:58px;text-align:center;border:2px solid #e2e8f0;border-radius:10px;padding:3px 6px;font-weight:800;font-size:1.05rem;color:var(--ink);outline:none}
  .idnum:focus{border-color:#fb923c}
  .stepbar{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.96);backdrop-filter:blur(6px);border-bottom:2px solid #ffedd5}
  .stepbar .wrap{padding-top:8px;padding-bottom:8px}
  .stepdot{width:40px;height:40px;font-size:1.05rem}
  .stepname{font-size:1.05rem;font-weight:800;margin-top:2px;white-space:nowrap}
  main.wrap{padding-top:16px}
  .step{background:#fff;border:4px solid var(--sbd);border-radius:30px;padding:20px 24px;scroll-margin-top:90px}
  .s-sky{--s:#0369a1;--sbd:#7dd3fc;--sbg:#f0f9ff}
  .s-violet{--s:#6d28d9;--sbd:#c4b5fd;--sbg:#f5f3ff}
  .s-teal{--s:#0f766e;--sbd:#5eead4;--sbg:#f0fdfa}
  .s-orange{--s:#c2410c;--sbd:#fdba74;--sbg:#fff7ed}
  .s-rose{--s:#be123c;--sbd:#fda4af;--sbg:#fff1f2}
  .shead{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}
  .shead h2{font-family:'Baloo 2','Noto Sans TC',cursive;font-size:2.1rem;font-weight:900;color:var(--s);margin:0;line-height:1.2}
  .shead h2 .no{display:inline-flex;align-items:center;justify-content:center;width:46px;height:46px;border-radius:999px;background:var(--s);color:#fff;font-size:1.5rem;margin-right:12px;vertical-align:middle}
  .wlink{display:inline-flex;align-items:center;gap:6px;flex:none;text-decoration:none;font-weight:800;font-size:1rem;color:var(--s);border:2px solid var(--sbd);background:var(--sbg);border-radius:999px;padding:5px 14px}
  .wlink:hover{background:#fff}
  /* 步驟卡元件的 CSS 由 inject 插在 body 尾端，這裡用 .step 前綴提高權重 */
  .step .sc-t{font-size:1.5rem}
  .step .sc-t b{color:var(--s)}
  .step .sc-flat .sc-slide{border-color:var(--sbd)}
  .step .sc-flat .sc-t:before{background:var(--s)}
  .sub{font-size:1.2rem;font-weight:800;color:#334155;margin:6px 0 0}
  .sub b{color:var(--s)}
  .tip{display:block;font-size:1.2rem;font-weight:800;color:#334155;background:var(--sbg);border-radius:14px;padding:6px 14px;margin:10px 0 0}
  .tip b{color:var(--s)}
  .warn{font-size:1.25rem;font-weight:900;color:#be123c;background:#fff1f2;border:3px solid #fda4af;border-radius:16px;padding:8px 14px;margin:12px 0 0}
  .checkbox{background:var(--sbg);border:3px solid var(--sbd);border-radius:22px;padding:14px 18px;margin-top:16px}
  .checkbox .cbt{font-family:'Baloo 2','Noto Sans TC',cursive;font-size:1.4rem;font-weight:900;color:var(--s);margin:0 0 6px}
  .checkbox label{display:flex;align-items:center;gap:12px;font-size:1.3rem;font-weight:800;margin:6px 0;cursor:pointer}
  .checkbox input{width:28px;height:28px;accent-color:var(--s);flex:none}
  .stepnav{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:20px;padding-top:14px;border-top:2px solid #f1f5f9}
  .legend{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px 18px;margin-top:14px}
  .legend div{display:flex;align-items:center;gap:10px;font-size:1.25rem;font-weight:800;background:var(--sbg);border-radius:16px;padding:8px 12px}
  .legend .n{flex:none;display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;border-radius:999px;background:#ea580c;color:#fff;font-weight:900}
  .legend span.d{color:var(--muted);font-weight:700;font-size:1.05rem}
  .ptype{border:4px solid #bae6fd;background:#fff;border-radius:18px;padding:4px 16px;font-weight:800;font-size:1.2rem;color:#0369a1}
  .ptype.on{background:#0ea5e9;border-color:#0ea5e9;color:#fff}
  .kwchips{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:12px}
  .kwchips .lab{font-size:1.2rem;font-weight:900;color:#334155}
  .kw{font:inherit;font-size:1.3rem;font-weight:900;border:3px solid var(--sbd);background:#fff;color:var(--s);border-radius:999px;padding:2px 18px;cursor:pointer}
  .kw:hover{background:var(--sbg)}
  .kw.done{background:var(--s);color:#fff;border-color:var(--s)}
  .three{list-style:none;margin:0;padding:0}
  .three li{display:flex;gap:12px;align-items:flex-start;font-size:1.3rem;font-weight:800;line-height:1.45;margin:0 0 10px}
  .three .n{flex:none;display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border-radius:999px;background:var(--s);color:#fff;font-weight:900;margin-top:1px}
  .goalcard{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:20px;align-items:center;background:var(--sbg);border:3px solid var(--sbd);border-radius:22px;padding:14px 16px;margin-bottom:16px}
  .goalcard .say{font-size:1.3rem;font-weight:800;line-height:1.6}
  .goalcard b{color:var(--s)}
  .btn-s{display:inline-flex;align-items:center;gap:8px;margin-top:8px;text-decoration:none;font-size:1.1rem;font-weight:900;color:var(--s);background:#fff;border:3px solid var(--sbd);border-radius:16px;padding:6px 16px}
  .btn-s:hover{background:var(--sbg)}
  .bigwiki{display:inline-flex;align-items:center;gap:10px;margin-top:12px;text-decoration:none;font-size:1.2rem;font-weight:900;color:#fff;background:var(--s);border-radius:18px;padding:10px 20px;box-shadow:0 4px 0 rgba(0,0,0,.2)}
  .projname{font-family:'Baloo 2','Noto Sans TC',cursive;font-size:1.9rem;font-weight:900;color:var(--s);margin:0}
  .btn-o{font:inherit;font-weight:800;border:2px solid var(--sbd);background:#fff;color:var(--s);border-radius:14px;padding:4px 16px;cursor:pointer}
  .joinbtns{display:flex;gap:14px;flex-wrap:wrap;margin-top:6px}
  .joinbtns a{display:inline-flex;align-items:center;min-height:60px;padding:0 24px;border-radius:18px;font-size:1.35rem;font-weight:900;color:#fff;text-decoration:none;box-shadow:0 4px 0 rgba(0,0,0,.18)}
  .namerow{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:10px}
  .terms{margin-top:14px;background:#fffbeb;border:3px solid #fcd34d;border-radius:18px;padding:10px 16px}
  .terms .th{display:inline-flex;align-items:center;gap:6px;font-weight:900;font-size:1rem;color:#92400e;background:#fef3c7;border-radius:999px;padding:0 12px;margin-bottom:4px}
  .terms dl{margin:0}.terms dt{display:inline;font-weight:900;font-size:1.2rem;color:#b45309}
  .terms dd{display:inline;margin:0;font-weight:700;font-size:1.15rem;color:#334155}
  .terms .row{margin:6px 0;display:flex;align-items:center;gap:14px}
  .terms .tx{flex:1;min-width:0}
  .bicon{flex:none;display:inline-flex;align-items:center;justify-content:center;min-width:64px;height:64px;padding:0 10px;background:#fff;border:3px solid #94a3b8;border-radius:14px;box-shadow:0 3px 0 #cbd5e1;color:#1e293b;font-weight:900;font-size:1.15rem;white-space:nowrap}
  .bicon svg{width:40px;height:40px}
  .bicon.share{background:#7c3aed;border-color:#6d28d9;color:#fff;box-shadow:0 3px 0 #5b21b6}
  .bicon.wide{padding:0 18px}
  .ttwrap{display:flex;gap:18px;align-items:flex-start;margin-bottom:14px}
  .ttwrap img{width:190px;flex:none}
  .tt{background:var(--sbg);border:3px solid var(--sbd);border-radius:22px;padding:14px 16px;margin-top:12px}
  .tthead{font-size:1.25rem;font-weight:900;color:var(--s);margin-bottom:8px}
  .ttcols,.ttrow{display:grid;grid-template-columns:78px minmax(0,1fr) 120px 120px 80px;gap:8px;align-items:center}
  .ttcols{font-weight:900;color:var(--muted);font-size:1rem;margin-bottom:2px}
  .ttrow{margin-bottom:8px}
  .ttn{color:var(--s);font-size:1.15rem}
  .ttin,.ttsel{font:inherit;font-weight:800;font-size:1.15rem;border:3px solid var(--sbd);border-radius:12px;padding:4px 10px;background:#fff;color:var(--ink);outline:none;min-width:0}
  .ttin:focus,.ttsel:focus{border-color:var(--s)}
  .ttmin{text-align:center}
  .ttbtns{display:flex;gap:10px;margin:4px 0 12px}
  .btn-o:disabled{opacity:.35;cursor:default}
  .ttout{white-space:pre-wrap;background:#fff;border:3px dashed var(--sbd);border-radius:16px;padding:10px 16px;font-size:1.2rem;font-weight:800;line-height:1.65;margin-bottom:6px}
</style>'''


def wiki_link(target, label='忘記怎麼做？查技能百科'):
    href = WIKI_FILE + (target if target.startswith('?') else '#' + target)
    return '<a class="wlink" href="%s">%s%s</a>' % (href, SVG_BOOK, label)


def act(title, inner, num=True):
    """一個小動作：一句話＋內容（放在 sc-flat 步驟卡裡，編號自動）。"""
    return '<div class="sc-slide"><p class="sc-t">%s</p>%s</div>' % (title, inner)


def acts(*items, nonum=False):
    return '<div class="sc sc-flat%s" data-sc>%s</div>' % (' sc-nonum' if nonum else '', ''.join(items))


def lesson1_steps():
    """第 1 課：回傳步驟清單 [{name, color, title, wiki, body, checks, checks_title?}]。
    原則：每步一句話＋步驟圖（字卡已在圖裡，頁面不重複）＋勾選；圖裡沒有的提醒才寫在頁面上。"""
    legend = [('作品名字', '點一下可以改'), ('左邊工具列', '範本、文字、上傳都在這'), ('白色的紙', '作品放這裡'),
              ('小頁面圖', '點一下換頁'), ('＋', '多一張紙'), ('分享', '拿連結')]
    legend_html = ''.join('<div><span class="n">%d</span><span>%s<br><span class="d">%s</span></span></div>' % (i + 1, a, b)
                          for i, (a, b) in enumerate(legend))
    kw_html = ''.join('<button type="button" class="kw">%s</button>' % k for k in ['台南', '旅行', '旅遊', '封面', '手冊', '景點'])

    # 1 開文件
    s1 = acts(
        act('第一次：先<b>加入團隊</b>，再開 Canva',
            '<div class="joinbtns"><a href="%s" target="_blank" rel="noopener" style="background:#ea580c">加入班級 Canva 團隊 ↗</a>'
            '<a href="%s" target="_blank" rel="noopener" style="background:#0f766e">開 Canva ↗</a></div>'
            '<p class="sub">用學校帳號登入。登不進去，<b>舉手</b>。</p>' % (CANVA_JOIN, CANVA_HOME)),
        act('開一張 <b>B5</b> 紙（176 × 250 公釐）', op_media('開B5文件')),
        act('改<b>作品名字</b>',
            '<div class="namerow"><p class="projname" id="projName">先填上面的年級、班級、座號</p>'
            '<button type="button" id="projCopy" class="btn-o">複製名字</button></div>'
            + ('' if has_ss('改檔名') else
               '<p class="sub">到 Canva 點名字 → <kbd>Ctrl</kbd> + <kbd>A</kbd> → <kbd>Ctrl</kbd> + <kbd>V</kbd> → <kbd>Enter</kbd></p>')
            + op_media('改檔名')))
    # 2 認識畫面（標記圖維持原樣）
    s2 = ('<img src="../assets/介面_標記.jpg" alt="Canva 編輯畫面，標上 1～6 號：作品名字、左邊工具列、白色的紙、小頁面圖、＋、分享" class="shot zoomable">'
          '<div class="legend">%s</div>'
          '<p class="warn">弄亂了？按 <kbd>Ctrl</kbd> + <kbd>Z</kbd> 復原。</p>'
          '<div class="checkbox" style="background:#fffbeb;border-color:#fcd34d">'
          '<p class="cbt" style="color:#b45309">小測驗：這一區做什麼？</p>'
          '<div id="faceQuiz" class="space-y-3"></div><p id="faceMsg" class="text-xl font-extrabold mt-3 min-h-[32px]"></p></div>'
          '<div class="hidden"><input type="checkbox" class="chk" id="faceOk" disabled></div>' % legend_html)
    # 3 選範本
    tpl_extra = '' if has_ss('選範本') else (
        '<ol class="three" style="margin-top:12px"><li><span class="n">1</span><span>點你喜歡的範本</span></li>'
        '<li><span class="n">2</span><span>左邊出現好幾頁，點<b>最上面那張</b>（封面）</span></li></ol>')
    s3 = acts(act('左邊按<b>範本</b>，搜尋，選一個當封面',
                  op_media('選範本') + tpl_extra +
                  '<div class="kwchips"><span class="lab">換關鍵字（點一下複製）：</span>%s</div>'
                  '<p class="tip">不喜歡：<kbd>Ctrl</kbd> + <kbd>Z</kbd>，再選一個。</p>' % kw_html), nonum=True) + \
        '<p class="warn">不要按「套用全部」。</p>'
    # 4 改封面字
    edit_extra = '' if has_ss('改封面文字') else (
        '<ol class="three" style="margin-top:12px">'
        '<li><span class="n">1</span><span>連按兩下（看到打字的直線）→ <kbd>Ctrl</kbd> + <kbd>A</kbd> → 打字；其他字也這樣改</span></li>'
        '<li><span class="n">2</span><span>工具列：<b>字型</b>、<b>大小</b>、<b>顏色</b></span></li>'
        '<li><span class="n">3</span><span>按住框拖過去；白點調大小</span></li></ol>')
    s4 = ('<div class="goalcard"><img src="../assets/封面_改哪裡.jpg" alt="範本封面：1 書名改這裡、2 三個景點改這裡、3 用不到的字改掉或刪掉" class="shot zoomable">'
          '<div class="say">改成你的：<br><b>1 書名</b>（例：我的台南一日小旅行）<br><b>2 你選的 3 個景點</b>（不用寫美食）<br>'
          '<a class="btn-s" href="%s" target="_blank" rel="noopener">打開我的景點資料（L04）↗</a>'
          '<p class="sub" style="color:var(--muted)">範本的照片先留著。</p></div></div>' % L04_URL) + \
        acts(act('連按兩下改字，再調樣子和位置',
                 op_media('改封面文字') + edit_extra +
                 '<p class="tip">字型：選後面寫「<b>繁體中文</b>」的。</p>'
                 '<p class="tip">用不到的字：點一下框 → <kbd>Delete</kbd>。</p>'
                 '<a class="bigwiki" href="%s?cat=text">%s忘記怎麼做？→ 技能百科：文字</a>' % (WIKI_FILE, SVG_BOOK)), nonum=True)
    # 5 交作業
    share_extra = '' if has_ss('分享連結') else (
        '<p class="sub">分享 → 點「只有你可存取」→ 選「<b>任何具有此連結者</b>」→ 改「<b>可供檢視</b>」→ 複製連結</p>')
    s5 = acts(
        act('<b>分享</b>，複製「可供檢視」的連結', op_media('分享連結') + share_extra),
        act('回這裡，<kbd>Ctrl</kbd> + <kbd>V</kbd> <b>貼上</b>',
            '<label class="block text-xl font-extrabold mb-1" for="canvaLink">Canva 連結</label>'
            '<input id="canvaLink" type="text" autocomplete="off" class="w-full border-4 border-slate-300 rounded-2xl px-4 py-3 text-xl font-bold focus:border-rose-400 outline-none">'
            '<p id="linkMsg" class="text-lg font-bold mt-1 min-h-[28px]"></p>'))
    s1 += terms(('B5', '一種紙張大小，比 A4 小，適合做小冊子'), ('自訂尺寸', '自己決定紙的寬和高，不用現成的大小'))
    s2 = s2.replace('<p class="warn">弄亂了', terms(('工具列', '左邊那一排按鈕，要加東西都從這裡開始'), ('復原', '回到上一步，快速鍵是 Ctrl + Z', 'undo'), ('分享', '做好以後，按右上角這顆，拿到作品的連結', 'share')) + '<p class="warn">弄亂了', 1)
    s3 += terms(('範本', '別人做好的版型，改成自己的字就能用'), ('套用全部', '把範本所有頁一次放進你的作品，這次不要按'))
    s4 += terms(('文字框', '圍住一段字的框，拖框就能移動字'), ('字型', '字的樣子；要選標示「繁體中文」的，中文才會正常顯示'))
    s5 += terms(('分享連結', '一串網址，老師貼到瀏覽器就能打開你的作品'), ('可供檢視', '拿到連結的人只能看，不能改你的作品'))
    return [
        dict(name='開文件', color='sky', title='開一份 B5 新文件', wiki='open-b5', body=s1,
             checks=['開好空白的 <b>B5</b>（176 × 250 公釐）', '<b>作品名字</b>改好了']),
        dict(name='認識畫面', color='violet', title='認識編輯畫面', wiki='screen', body=s2,
             checks=['在自己的畫面找到：<b>作品名字、左邊工具列、＋、分享</b>']),
        dict(name='選範本', color='teal', title='選一個範本當封面', wiki='template', body=s3,
             checks=['第 1 頁用了一個<b>範本</b>', '只有<b>一頁</b>封面（沒有套用全部）']),
        dict(name='改封面字', color='orange', title='改封面的字', wiki='?cat=text', body=s4,
             checks=['<b>書名</b>改成我自己的', '有我選的 <b>3 個景點</b>', '<b>字型、大小、顏色、位置</b>，至少改了一項']),
        dict(name='交作業', color='rose', title='分享連結，交作業', wiki='share', body=s5, submit=True,
             checks=['連結<b>貼好</b>了（顯示 ✓）', '權限是<b>可供檢視</b>', '開<b>新分頁</b>貼上連結，打得開'], checks_title='交之前檢查'),
    ]


LESSON1_QUIZ = [
    {'img': '../assets/介面題_左邊.jpg', 'q': '橘色框起來的左邊這一排，是做什麼的？', 'o': ['要加文字、照片、圖形，來這裡', '看這份作品有幾頁', '把作品分享給老師', '改作品的名字'], 'a': 0, 'why': '左邊工具列：要加東西，來這裡'},
    {'img': '../assets/介面題_右上.jpg', 'q': '橘色框起來的「分享」，是做什麼的？', 'o': ['把字變大', '做好了，從這裡拿連結', '多一張新的紙', '換顏色'], 'a': 1, 'why': '分享：做好了，從這裡拿連結'},
    {'img': '../assets/介面題_下方.jpg', 'q': '橘色框起來的「＋」，按了會怎樣？', 'o': ['刪掉這份作品', '把照片放大', '多一張新的紙', '存到電腦'], 'a': 2, 'why': '＋：多一張新的紙'},
    {'img': '../assets/介面題_名字.jpg', 'q': '點一下橘色框起來的名字，可以做什麼？', 'o': ['換下一頁', '加照片', '拿分享連結', '改作品的名字'], 'a': 3, 'why': '點作品名字，可以改名'},
]

# 繳交題目：kind 'link'＝Canva 連結；其餘＝steps 裡的勾選全部打勾（第 2 步含介面小測驗全對）
LESSON1_QDEFS = [
    dict(id='q1', kind='link', text='學生貼上的 Canva 分享連結（老師開連結看封面）。'),
    dict(id='q2', steps=[1], label='開 B5、改作品名字', text='開好空白 B5（176 × 250 公釐）、作品名字改好，兩項都勾選。'),
    dict(id='q3', steps=[2], label='認識畫面', text='在自己的畫面找到作品名字、左邊工具列、＋、分享（勾選），而且介面小測驗 4 題全對。'),
    dict(id='q4', steps=[3, 4], label='封面', text='封面用了一個範本、只有一頁封面、書名改成自己的、有自己選的 3 個景點，字型／大小／顏色／位置至少改一項（全部勾選）。'),
]

LESSON_BY_N[1].update(steps=lesson1_steps, quiz=LESSON1_QUIZ, qdefs=LESSON1_QDEFS)




BICONS = {
    'bullet': '<span class="bicon"><svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"><circle cx="7" cy="9" r="2.4" fill="currentColor"/><circle cx="7" cy="20" r="2.4" fill="currentColor"/><circle cx="7" cy="31" r="2.4" fill="currentColor"/><path d="M15 9h20M15 20h20M15 31h20"/></svg></span>',
    'alignleft': '<span class="bicon"><svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"><path d="M5 8h30M5 16h19M5 24h30M5 32h19"/></svg></span>',
    'addpage': '<span class="bicon wide">＋ 新增頁面</span>',
    'trash': '<span class="bicon"><svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M8 11h24M16 11V7h8v4M11 11l1.5 22h15L29 11M17 17v11M23 17v11"/></svg></span>',
    'undo': '<span class="bicon"><svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9L7 16l7 7"/><path d="M7 16h15a9 9 0 0 1 0 18h-8"/></svg></span>',
    'share': '<span class="bicon share wide">分享</span>',
}


def terms(*pairs):
    """名詞解釋框：每項＝(專有名詞, 一句白話解釋)。學生頁固定用 Canva 的正式名稱，解釋放在這個獨立的框。"""
    return ('<div class="terms"><span class="th">📖 名詞小卡</span><dl>%s</dl></div>'
            % ''.join('<div class="row">%s<div class="tx"><dt>%s</dt><dd>：%s</dd></div></div>' % (BICONS.get(x[2], '') if len(x) > 2 else '', x[0], x[1]) for x in pairs))


def lesson2_steps():
    """第 2 課：路線圖與行程時間表。每步一句話＋步驟圖＋勾選。"""
    pmap = [('2', '目錄', '下一步做'), ('3', '行程規劃', '時間表'), ('4', '路線圖', 'Google 地圖截圖')]
    pmap_html = ''.join('<div><span class="n">%s</span><span>第 %s 頁：%s<br><span class="d">%s</span></span></div>' % (n, n, a, b) for n, a, b in pmap)
    s1 = acts(act('按 <b>＋</b> 多三張紙，每張<b>打上標題</b>',
                  '<div class="legend">%s</div>' % pmap_html + op_media('新增頁面') + op_media('加文字')
                  + terms(('新增頁面', '頁面下方這顆按鈕，按一下多一張新的頁面', 'addpage'), ('刪除頁面', '多按了？點頁面上方的垃圾桶刪掉', 'trash'), ('頁面', 'Canva 裡的一張紙，手冊的一頁就是一個頁面'), ('標題', '一頁最上面最大的字，說明這頁是什麼'))), nonum=True)
    s2 = acts(act('開 <b>Google 地圖</b>，畫出整條路線',
                  '<div class="joinbtns"><a href="%s" target="_blank" rel="noopener" style="background:#0f766e">開 Google 地圖 ↗</a></div>' % GMAP_DIR
                  + op_media('Google地圖路線')
                  + '<p class="tip">交通方式選「<b>機車</b>」。搭公車的人也選機車，只是用來畫線。</p>'), nonum=True)
    s3 = acts(act('把地圖<b>截圖</b>，貼到第 4 頁',
                  op_media('截圖貼上') + '<p class="tip">地圖下面打一行「<b>圖片：Google 地圖</b>」。</p>'
                  + terms(('截圖', '把螢幕上看到的畫面拍成一張圖'), ('圖片來源', '這張圖是從哪裡來的，寫出來是尊重原作者'))), nonum=True)
    must = [('景點', '每一站的名字'), ('時間', '幾點到、停多久'), ('交通方式', '走路、機車、開車…'), ('看得出順序', '第 1 站、第 2 站…照順序排')]
    must_html = ''.join('<div><span class="n">%d</span><span>%s<br><span class="d">%s</span></span></div>' % (k + 1, x, y) for k, (x, y) in enumerate(must))
    s4 = acts(act('第 3 頁做<b>時間表</b>，下面 4 樣一定要有',
                  '<div class="legend">%s</div>' % must_html
                  + '<div class="ttwrap" style="margin-top:14px"><img src="../assets/手冊_p3.jpg" alt="行程規劃範例頁：每一站有時間、站名、停留時間，站與站之間寫交通方式和分鐘" class="shot zoomable">'
                  '<div><p class="sub">照<b>你的 L05 文件</b>做，不用重查。排法可以不一樣，只要 4 樣都有。</p>'
                  '<a class="btn-s" href="%s" target="_blank" rel="noopener">打開 L05 學習單 ↗</a></div></div>' % L05_URL
                  + op_media('加文字')), nonum=True)
    grp = [('#e0f2fe', '#0369a1', '先看全貌', ['封面', '目錄', '行程規劃', '路線圖']),
           ('#ffedd5', '#c2410c', '景點介紹', ['第 1 站', '第 2 站', '…', '美食也算一站']),
           ('#ffe4e6', '#be123c', '最後收尾', ['旅行小提醒', '封底'])]
    grp_html = ''.join('<div style="flex:%d;background:%s;border:3px solid %s;border-radius:16px;padding:8px 12px"><p style="margin:0 0 4px;font-weight:900;color:%s;font-size:1.15rem">%s</p>%s</div>'
                       % (len(c) + 1, bg, fg, fg, t, ''.join('<span style="display:inline-block;background:#fff;border-radius:10px;padding:0 10px;margin:2px 4px 2px 0;font-weight:800;font-size:1.1rem">%s</span>' % x for x in c))
                       for bg, fg, t, c in grp)
    mu = [('章節名', '手冊有哪些章節，一行一個'), ('照順序', '從行程規劃寫到旅行小提醒'), ('靠左', '每行都靠左邊'), ('項目符號', '每行前面有小圓點')]
    mu_html = ''.join('<div><span class="n">%d</span><span>%s<br><span class="d">%s</span></span></div>' % (k + 1, x, y) for k, (x, y) in enumerate(mu))
    s_toc = acts(act('第 2 頁做<b>目錄</b>：看一眼就知道手冊有什麼',
                     '<p class="sub" style="margin:0 0 8px">手冊分三塊：先看全貌 → 景點介紹 → 最後收尾。目錄列出<b>封面、目錄以外</b>的每個章節。</p>'
                     '<div style="display:flex;gap:10px;align-items:stretch;flex-wrap:wrap">%s</div>' % grp_html
                     + '<div class="legend" style="margin-top:14px">%s</div>' % mu_html
                     + '<p class="tip"><b>頁碼</b>先不用打，之後景點頁做好了再補。</p>'
                     + terms(('目錄', '列出手冊有哪些章節的一頁，翻開就知道要去哪裡找'), ('項目符號', '每一行最前面的小圓點，用來一行一行列出東西；按工具列上這顆', 'bullet'), ('靠左對齊', '每一行的字都從左邊開始排；按工具列上這顆，按到字靠左就停', 'alignleft'))
                     + op_media('目錄靠左列點')), nonum=True)
    s6 = acts(act('連結和第 1 課一樣，<b>再貼一次</b>就好',
                  '<details style="margin:6px 0 10px"><summary class="sub" style="cursor:pointer">忘記怎麼分享？看步驟圖</summary>%s</details>' % op_media('分享連結')
                  + '<label class="block text-xl font-extrabold mb-1" for="canvaLink">Canva 連結</label>'
                  '<input id="canvaLink" type="text" autocomplete="off" class="w-full border-4 border-slate-300 rounded-2xl px-4 py-3 text-xl font-bold focus:border-rose-400 outline-none">'
                  '<p id="linkMsg" class="text-lg font-bold mt-1 min-h-[28px]"></p>'
                  + terms(('分享連結', '一串網址，老師貼到瀏覽器就能打開你的作品'), ('可供檢視', '拿到連結的人只能看，不能改你的作品'))), nonum=True)
    return [
        dict(name='加三頁', color='sky', title='加三張新的紙', wiki='new-page', body=s1,
             checks=['多了<b>三頁</b>', '三頁都有<b>標題</b>']),
        dict(name='目錄', color='orange', title='做目錄', wiki='align-list', body=s_toc,
             checks=['有每一個<b>章節名</b>，一行一個', '目錄<b>靠左</b>，每行前面有<b>項目符號</b>（小圓點）']),
        dict(name='畫路線', color='teal', title='用 Google 地圖畫路線', wiki='gmap-route', body=s2,
             checks=['地圖上有我<b>全部的站</b>', '看到<b>整條路線</b>']),
        dict(name='貼地圖', color='violet', title='截圖貼到路線圖頁', wiki='snip-paste', body=s3,
             checks=['第 4 頁有<b>地圖</b>', '地圖<b>夠大</b>', '有寫<b>圖片來源</b>']),
        dict(name='時間表', color='orange', title='排行程時間表', wiki='add-text', body=s4,
             checks=['每一站都有<b>景點</b>和<b>時間</b>', '站與站之間有<b>交通方式</b>', '一看就知道<b>先後順序</b>']),
        dict(name='交作業', color='rose', title='分享連結，交作業', wiki='share', body=s6, submit=True,
             checks=['連結<b>貼好</b>了（顯示 ✓）', '權限是<b>可供檢視</b>', '開<b>新分頁</b>貼上連結，打得開'], checks_title='交之前檢查'),
    ]


LESSON2_QDEFS = [
    dict(id='q1', kind='link', text='學生貼上的 Canva 分享連結（老師開連結看目錄、行程規劃與路線圖）。'),
    dict(id='q2', steps=[1], label='加三頁', text='手冊多了三頁（目錄、行程規劃、路線圖），三頁都有標題（勾選）。'),
    dict(id='q3', steps=[2], label='目錄', text='第 2 頁目錄有每個章節名（一行一個）、靠左、每行有項目符號（小圓點），頁碼先不填（全部勾選）。'),
    dict(id='q4', steps=[3, 4], label='路線圖', text='Google 地圖上有全部的站、看到整條路線；第 4 頁貼了夠大的地圖並寫了圖片來源（全部勾選）。'),
    dict(id='q5', steps=[5], label='時間表', text='第 3 頁的時間表有景點、時間、交通方式，而且看得出順序（全部勾選）。'),
]

LESSON_BY_N[2].update(steps=lesson2_steps, qdefs=LESSON2_QDEFS)


def checks_html(items, title='這一步檢查'):
    return ('<div class="checkbox"><p class="cbt">%s</p>%s</div>' %
            (title, ''.join('<label><input type="checkbox" class="chk"> <span>%s</span></label>' % it for it in items)))


SUBMIT_HTML = '''
    <div class="checkbox" style="background:#fff7ed;border-color:#fdba74">
      <p class="sub" style="margin:0 0 6px">還沒做完？先交，之後可以再交一次。</p>
      <button id="submitBtn" class="w-full bg-orange-600 hover:bg-orange-700 text-white cute text-2xl font-extrabold rounded-2xl py-3">繳交學習單</button>
      <p id="submitStat" class="text-base font-bold mt-2 min-h-[22px] text-center"></p>
    </div>
    <div id="rewardBox" class="hidden text-center bg-gradient-to-b from-amber-100 to-orange-100 border-4 border-amber-300 rounded-3xl p-6 mt-4">
      <h3 class="cute text-2xl font-extrabold text-orange-700">恭喜你已經做完今日的作業，可以遊玩！</h3>
      <div class="flex flex-wrap gap-3 justify-center mt-3">
        <a href="%s" target="_blank" rel="noopener"
           class="cute inline-block bg-orange-600 hover:bg-orange-700 text-white text-lg font-extrabold rounded-2xl px-6 py-2">電腦教室遊戲網站</a>
      </div>
    </div>''' % PORTAL


def lesson_page(lesson):
    steps = lesson['steps']()
    secs = []
    for i, s in enumerate(steps):
        n = i + 1
        secs.append('''
  <section class="step s-%s%s" data-step="%d">
    <div class="shead"><h2><span class="no">%d</span>%s</h2>%s</div>
    %s
    %s%s
    <div class="stepnav"></div>
  </section>''' % (s['color'], '' if n == 1 else ' hidden', n, n, s['title'],
                   wiki_link(s['wiki'], '技能百科：文字' if s['wiki'] == '?cat=text' else '忘記怎麼做？查技能百科'),
                   s['body'], checks_html(s['checks'], s.get('checks_title', '這一步檢查')),
                   SUBMIT_HTML if s.get('submit') else ''))
    cfg = dict(ws=lesson['ws'], path=lesson['path'], wstitle=lesson.get('wstitle') or lesson['title'],
               names=[s['name'] for s in steps], quiz=lesson.get('quiz') or [], qdefs=lesson['qdefs'])
    body = '''<body>
%s
<div class="idbar"><div class="wrap">
  <span class="cute" style="font-weight:900;color:#c2410c">我是誰</span>
  <label>年級<input id="idGrade" class="idnum" inputmode="numeric" maxlength="2"></label>
  <label>班級<input id="idClass" class="idnum" inputmode="numeric" maxlength="2"></label>
  <label>座號<input id="idStudent" class="idnum" inputmode="numeric" maxlength="2"></label>
  <span id="idOk" class="hidden" style="color:#059669;font-weight:800;font-size:.9rem">✓ 已記住</span>
  <span class="ltitle"><small>第 %d 課</small>%s</span>
</div></div>
<div class="stepbar" id="stepbar"><div class="wrap"><div id="stepper" class="flex items-start"></div></div></div>
<main class="wrap">%s
</main>
%s''' % (topnav('lesson%d' % lesson['n'], True), lesson['n'], lesson['title'], ''.join(secs), FOOTER)
    return (head('第 %d 課｜台南小導遊' % lesson['n'], LESSON_CSS) + body + common_js()
            + LESSON_JS.replace('__CFG__', json.dumps(cfg, ensure_ascii=False)) + '</body>\n</html>\n')


LESSON_JS = r'''
<script>
var firebaseConfig = {
  apiKey:"AIzaSyAaodBvsP-BSovON14izt22DOXeH40TTGM",
  authDomain:"pcclass-94300.firebaseapp.com",
  projectId:"pcclass-94300",
  storageBucket:"pcclass-94300.firebasestorage.app",
  messagingSenderId:"1034787516465",
  appId:"1:1034787516465:web:73c334b2ddad152c472510",
  measurementId:"G-37P75R7TZ7"
};
var LESSON=__CFG__;

(function(){
  function $(id){return document.getElementById(id);}
  function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
  var WS=LESSON.ws;   // 第 1 課＝g4-L08（改版前已有人繳交，不可改）

  // ===== 識別列 =====
  var ID_KEY='wk_identity';
  function digits(s){return String(s||'').replace(/[^0-9]/g,'');}
  function loadIdentity(){try{return JSON.parse(localStorage.getItem(ID_KEY)||'{}')}catch(e){return {}}}
  function saveIdentity(o){try{localStorage.setItem(ID_KEY,JSON.stringify(o))}catch(e){}}
  function getIdentity(){
    var g=digits($('idGrade').value),c=digits($('idClass').value),s=digits($('idStudent').value);
    return {grade:g?Number(g):null,className:c?Number(c):null,studentId:s?Number(s):null};
  }
  function identityValid(id){return id.grade!=null&&id.className!=null&&id.className>=1&&id.className<=14&&id.studentId!=null;}
  function pad2(n){return (n<10?'0':'')+n;}
  // 作品名字：年級 1 位＋班級 2 位＋座號 2 位＋空格＋我的台南手冊（例：40205 我的台南手冊）
  function projName(){var i=getIdentity();return identityValid(i)?(i.grade+pad2(i.className)+pad2(i.studentId)+' 我的台南手冊'):'';}
  function showProj(){if(!$('projName'))return;var n=projName();$('projName').textContent=n||'先填上面的年級、班級、座號';}
  (function initIdentity(){
    var saved=loadIdentity();
    if(saved.grade)$('idGrade').value=saved.grade;
    if(saved.className)$('idClass').value=saved.className;
    if(saved.studentId)$('idStudent').value=saved.studentId;
    if(identityValid(saved))$('idOk').classList.remove('hidden');
    ['idGrade','idClass','idStudent'].forEach(function(id){
      var e=$(id);
      e.addEventListener('input',function(){
        var d=digits(e.value);if(d!==e.value)e.value=d;
        var idn=getIdentity();
        if(identityValid(idn)){saveIdentity(idn);$('idOk').classList.remove('hidden');}
        else $('idOk').classList.add('hidden');
        showProj();
      });
    });
    showProj();
  })();

  // ===== Firebase：只用來寫入繳交 =====
  var db=null,auth=null;
  function loadScript(src){return new Promise(function(res,rej){var s=document.createElement('script');s.src=src;s.onload=res;s.onerror=rej;document.head.appendChild(s)})}
  function ensureAuth(){return (auth&&auth.currentUser)?Promise.resolve(auth.currentUser):auth.signInAnonymously().then(function(c){return c.user});}
  (function boot(){
    var base='https://www.gstatic.com/firebasejs/10.8.0/';
    loadScript(base+'firebase-app-compat.js')
      .then(function(){return loadScript(base+'firebase-auth-compat.js')})
      .then(function(){return loadScript(base+'firebase-firestore-compat.js')})
      .then(function(){firebase.initializeApp(firebaseConfig);db=firebase.firestore();auth=firebase.auth();})
      .catch(function(e){console.warn('Firebase 啟用失敗，改用單機模式',e);});
  })();

  function copyText(text,btn,doneText){
    var old=btn.textContent;
    function done(){btn.textContent=doneText||'✓ 已複製';btn.classList.add('done');setTimeout(function(){btn.textContent=old;btn.classList.remove('done');},1600);}
    function fallback(){
      var ta=document.createElement('textarea');ta.value=text;ta.style.cssText='position:fixed;left:-9999px;top:0';
      document.body.appendChild(ta);ta.select();
      try{document.execCommand('copy');done();}catch(e){btn.textContent='請按 Ctrl+C 複製';}
      document.body.removeChild(ta);
    }
    try{navigator.clipboard.writeText(text).then(done,fallback);}catch(e){fallback();}
  }
  if($('projCopy'))$('projCopy').onclick=function(){var n=projName();if(!n){alert('先在最上方填好年級、班級、座號。');window.scrollTo({top:0,behavior:'smooth'});return;}copyText(n,this);};
  [].forEach.call(document.querySelectorAll('.kw'),function(b){b.onclick=function(){copyText(b.textContent,b,'✓ '+b.textContent);};});

  // ===== 看截圖選功能小測驗 =====
  var FQ=LESSON.quiz,fqDone={};
  (function buildFaceQuiz(){
    var host=$('faceQuiz');if(!host||!FQ.length)return;
    FQ.forEach(function(q,qi){
      var row=el('div','bg-white border-2 border-amber-200 rounded-2xl p-3');
      var im=el('img','zoomable');im.src=q.img;im.alt='Canva 畫面的一小塊';im.style.cssText='max-width:100%;max-height:340px;border-radius:10px;border:2px solid #e2e8f0;margin-bottom:8px;display:block';
      row.appendChild(im);
      row.appendChild(el('p','text-xl font-extrabold mb-2',(qi+1)+'. '+q.q));
      var btns=el('div','flex flex-wrap items-center gap-2');
      var fb=el('span','text-lg font-extrabold ml-2');
      q.o.forEach(function(o,oi){
        var b=el('button','ptype',o);b.type='button';
        b.onclick=function(){
          if(oi===q.a){
            fqDone[qi]=true;fb.className='text-lg font-extrabold ml-2 text-emerald-700';fb.textContent='✓ '+q.why;
            [].forEach.call(btns.querySelectorAll('button'),function(x){x.classList.toggle('on',x===b);});
          }else{fb.className='text-lg font-extrabold ml-2 text-amber-700';fb.textContent='再想想';}
          var ok=Object.keys(fqDone).length===FQ.length;
          $('faceMsg').textContent=ok?'全對了！每個區都認得了。':'';
          $('faceMsg').className='text-xl font-extrabold mt-3 min-h-[32px] '+(ok?'text-emerald-700':'');
          var c=$('faceOk');if(c&&c.checked!==ok){c.checked=ok;}
          renderStepper();
        };
        btns.appendChild(b);
      });
      btns.appendChild(fb);row.appendChild(btns);host.appendChild(row);
    });
  })();

  // ===== Canva 連結 =====
  // ok：/design/<id>/<token>/view…（分享連結）或 canva.link/…
  // edit：/design/<id>/<token>/edit（分享時選了可供編輯）
  // addr：/design/<id>/edit 或其他沒有 view 的 canva 網址（從網址列複製的）
  function linkKind(v){
    v=String(v||'').trim();
    var m=v.match(/^https:\/\/(?:www\.)?canva\.com\/design\/([A-Za-z0-9_-]{8,})\/([A-Za-z0-9_-]+)\/(view|edit)\b/);
    if(m&&m[2]!=='edit'&&m[2]!=='view')return m[3]==='view'?'ok':'edit';
    if(/^https:\/\/canva\.link\/[A-Za-z0-9]+/.test(v))return 'ok';
    if(/^https?:\/\/([a-z0-9-]+\.)*canva\.com\//i.test(v))return 'addr';
    return 'bad';
  }
  function linkOk(v){return linkKind(v)==='ok';}
  var LINK_MSG={ok:'✓ 連結對了',edit:'這是「可供編輯」的連結，改成「可供檢視」再複製',
    addr:'這是網址列的網址。要按右上角「分享」→「複製連結」',bad:'要貼 Canva 的分享連結'};
  function showLink(){
    var c=$('canvaLink');if(!c)return;
    var v=(c.value||'').trim(),m=$('linkMsg'),k=linkKind(v);
    m.textContent=v?LINK_MSG[k]:'';
    m.className='text-lg font-bold mt-1 min-h-[28px] '+(!v?'':(k==='ok'?'text-emerald-700':'text-amber-700'));
    renderStepper();
  }
  if($('canvaLink')){$('canvaLink').addEventListener('input',showLink);$('canvaLink').addEventListener('paste',function(){setTimeout(showLink,0);});}

  // ===== 繳交學習單（題目由 LESSON.qdefs 決定；全部 experience 不計分）=====
  function workDocId(idn){return WS+'__'+idn.grade+'-'+idn.className+'-'+idn.studentId;}
  function stepChecksDone(n){
    var cs=document.querySelectorAll('.step[data-step="'+n+'"] input.chk');
    if(!cs.length)return false;
    for(var i=0;i<cs.length;i++)if(!cs[i].checked)return false;
    return true;
  }
  var sb=$('submitBtn');
  if(sb)sb.onclick=function(){
    var idn=getIdentity();
    if(!identityValid(idn)){alert('請先在最上方填好年級、班級、座號（都是數字，班級是 1 到 14）。');window.scrollTo({top:0,behavior:'smooth'});return;}
    var url=$('canvaLink')?($('canvaLink').value||'').trim():'';
    var needLink=LESSON.qdefs.some(function(d){return d.kind==='link';});
    if(needLink&&!linkOk(url)){alert('先把 Canva 的分享連結貼在「Canva 連結」格子裡。');$('canvaLink').focus();return;}
    if(!db){alert('系統尚未連線，請稍後再試或重新整理頁面。');return;}
    var answers={},qtypes={},qtexts={},exp={},done=0,lines=[];
    LESSON.qdefs.forEach(function(d){
      qtypes[d.id]='experience';qtexts[d.id]=d.text;
      if(d.kind==='link'){answers[d.id]={url:url};exp[d.id]={given:{url:url},correct:null,isCorrect:true};done++;lines.push('Canva 連結：已貼');}
      else{var ok=d.steps.every(stepChecksDone);
        if(d.extraFrom){var xe=document.querySelector(d.extraFrom),xt=xe?(xe.textContent||'').trim():'';answers[d.id]={done:ok,text:xt};exp[d.id]={given:{done:ok,text:xt},correct:null,isCorrect:ok};}
        else{answers[d.id]=ok;exp[d.id]={given:ok,correct:null,isCorrect:ok};}
        if(ok)done++;lines.push(d.label+'：'+(ok?'都完成了':'還沒全完成'));}
    });
    var experienceCompletion=Math.round(done/LESSON.qdefs.length*100);
    if(!confirm('確定要繳交學習單嗎？\n'+lines.join('\n')))return;
    var payload={worksheetId:WS,worksheetTitle:LESSON.wstitle,lessonPath:LESSON.path,
      grade:idn.grade,className:idn.className,studentId:idn.studentId,
      answers:answers,qtypes:qtypes,qtexts:qtexts,bonusQids:[],
      scoreAnswers:{},experienceAnswers:exp,openAnswers:{},bonusAnswers:{},
      accuracyRate:null,experienceCompletion:experienceCompletion,
      status:'submitted',submittedAt:firebase.firestore.FieldValue.serverTimestamp()};
    var btn=this,stat=$('submitStat');
    btn.disabled=true;stat.className='text-base font-bold mt-2 min-h-[22px] text-center text-orange-600';stat.textContent='繳交中…';
    ensureAuth().then(function(){return db.collection('submissions').doc(workDocId(idn)).set(payload,{merge:true});})
      .then(function(){
        btn.disabled=false;btn.textContent='重新繳交（覆蓋）';
        stat.className='text-base font-bold mt-2 min-h-[22px] text-center text-emerald-600';
        stat.textContent='✓ 已繳交！';submittedOnce=true;renderStepper();
        var rb=$('rewardBox');rb.classList.remove('hidden');rb.scrollIntoView({behavior:'smooth'});
      }).catch(function(e){
        console.warn('繳交失敗',e);btn.disabled=false;
        stat.className='text-base font-bold mt-2 min-h-[22px] text-center text-amber-600';
        stat.textContent='繳交失敗，請檢查網路後再按一次；還是不行就告訴老師。';
      });
  };

  // ===== 學習路徑 =====
  var STEP_NAMES=LESSON.names;
  var stepEls=[].slice.call(document.querySelectorAll('.step'));
  var curStep=1,visited={1:true},submittedOnce=false;
  function stepDone(n){
    if(n===STEP_NAMES.length&&sb)return submittedOnce;
    var cs=stepEls[n-1].querySelectorAll('input.chk');
    if(!cs.length)return !!visited[n]&&n!==curStep;
    for(var i=0;i<cs.length;i++)if(!cs[i].checked)return false;
    return true;
  }
  function renderStepper(){
    var host=$('stepper');host.innerHTML='';
    STEP_NAMES.forEach(function(name,idx){
      var n=idx+1,cur=n===curStep,done=stepDone(n);
      var cell=el('div','flex flex-col items-center');
      var b=el('button','stepdot cute rounded-full border-2 font-extrabold flex items-center justify-center transition '+
        (cur?'bg-orange-500 border-orange-500 text-white':(done?'bg-emerald-500 border-emerald-500 text-white':'bg-white border-slate-300 text-slate-400 hover:border-orange-300')));
      b.type='button';
      b.textContent=done&&!cur?'✓':String(n);
      b.setAttribute('aria-label','第 '+n+' 步：'+name);
      if(cur)b.setAttribute('aria-current','step');
      b.onclick=function(){showStep(n);};
      cell.appendChild(b);
      cell.appendChild(el('span','stepname '+(cur?'text-orange-600':'text-slate-500'),name));
      host.appendChild(cell);
      if(n<STEP_NAMES.length)host.appendChild(el('div','flex-1 h-1 mt-5 mx-1 rounded '+(done&&!cur?'bg-emerald-300':'bg-slate-200')));
    });
  }
  // 換步：捲到該步標題（扣掉固定在上面的進度列）
  function showStep(n){
    curStep=n;visited[n]=true;
    stepEls.forEach(function(s){s.classList.toggle('hidden',Number(s.dataset.step)!==n);});
    renderStepper();
    var sec=stepEls[n-1],bar=$('stepbar');
    var y=sec.getBoundingClientRect().top+window.pageYOffset-(bar?bar.offsetHeight:0)-12;
    window.scrollTo({top:Math.max(0,y),behavior:'smooth'});
  }
  stepEls.forEach(function(s){
    var n=Number(s.dataset.step),nav=s.querySelector('.stepnav');
    if(n>1){var p=el('button','bg-white border-2 border-slate-300 hover:border-orange-400 text-slate-600 text-lg font-bold rounded-2xl px-5 py-2','← 上一步');p.type='button';p.onclick=function(){showStep(n-1);};nav.appendChild(p);}
    else nav.appendChild(el('span',''));
    if(n<STEP_NAMES.length){var x=el('button','cute bg-orange-500 hover:bg-orange-600 text-white text-xl font-extrabold rounded-2xl px-6 py-2','下一步：'+STEP_NAMES[n]+' →');x.type='button';x.onclick=function(){showStep(n+1);};nav.appendChild(x);}
  });
  document.addEventListener('change',function(e){if(e.target&&e.target.classList&&e.target.classList.contains('chk'))renderStepper();});
  renderStepper();
})();
</script>
'''


# ───────────────────────── 輸出 ─────────────────────────
def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(html)
    print('寫出', os.path.relpath(path, OUTDIR), len(html), '字元')


def check_assets(*htmls):
    miss = set()
    for h in htmls:
        for m in re.findall(r'(?:\.\./)?assets/([^"\'()\s&;]+?\.(?:jpg|png|mp4))', h):
            if not os.path.exists(os.path.join(ASSETS, m)):
                miss.add(m)
    for s in SKILLS:
        k, v = s['media']
        if k == 'op':
            for f in (video_of(v) + '.mp4', video_of(v) + '_封面.jpg'):
                if not os.path.exists(os.path.join(ASSETS, f)):
                    miss.add(f)
            if not has_ss(v):
                WARN.append('沒有步驟圖，技能百科先用影片：%s' % v)
        elif k == 'img' and not os.path.exists(os.path.join(ASSETS, v)):
            miss.add(v)
    for m in sorted(miss):
        print('  [缺素材] assets/' + m)


def build(inject=False):
    outs = []
    write(os.path.join(OUTDIR, HOME_FILE), home_page())
    for l in LESSONS:
        if l['status'] != 'open':
            continue
        if not l.get('steps'):
            print('  [錯誤] 第 %d 課是 open，但沒有 steps 內容，略過' % l['n'])
            continue
        p = os.path.join(PAGEDIR, l['file'])
        write(p, lesson_page(l))
        outs.append(p)
    p_wiki = os.path.join(PAGEDIR, WIKI_FILE)
    write(p_wiki, wiki_page())
    htmls = [io.open(p, encoding='utf-8').read() for p in [os.path.join(OUTDIR, HOME_FILE), p_wiki] + outs]
    check_assets(*htmls)
    for w in sorted(set(WARN)):
        print('  [警告]', w)
    if inject:
        py = sys.executable
        g = os.path.join(PROJ, '引導規範')
        for args in ([os.path.join(g, 'chair-gate', 'inject.py')] + outs,
                     [os.path.join(g, 'stepcards', 'inject.py')] + outs + [p_wiki],
                     [os.path.join(g, 'game-portal', 'check.py')] + outs):
            r = subprocess.run([py] + args, capture_output=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
            print(r.stdout.decode('utf-8', 'replace').strip())
            if r.returncode:
                print(r.stderr.decode('utf-8', 'replace'))


if __name__ == '__main__':
    build(inject='--inject' in sys.argv)
