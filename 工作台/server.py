# -*- coding: utf-8 -*-
"""
備課駕駛艙 · 本機伺服器（Python 標準庫，無需 pip）
功能：讀寫 materials/ 與 引導規範/、伺服面板、代理 Gemini、pptx 轉 PNG 縮圖。
"""
import json, os, sys, io, subprocess, urllib.request, urllib.parse, mimetypes, re
import base64, zipfile, html, tempfile, time, shutil
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import updater   # 自動更新（見 updater.py／《自動更新規範》）

HERE = Path(__file__).resolve().parent          # …/工作台
ROOT = HERE.parent                               # 專案根目錄
MATERIALS = ROOT / "materials"
GUIDE = ROOT / "引導規範"
WEB = HERE / "web"
CONFIG = HERE / "config.json"
PORT = 8770

# 單元層級管線階段 → 對應檔名（計畫切分是專案層級，不在此）
STAGES = [
    ("鷹架分析", "01_目標與鷹架.md"),
    ("關鍵字", "02_搜尋關鍵字.md"),
    ("素材搜尋", "03_素材候選.md"),
    ("篩選勾選", "04_素材清單與缺口.md"),
    ("教學環節", "05_教學活動流程.md"),
    ("成品", "06_成品"),          # 前綴：06_成品.*
]


def safe(rel: str) -> Path:
    """把相對路徑鎖在 ROOT 內，擋 path traversal。"""
    p = (ROOT / rel).resolve()
    if not str(p).startswith(str(ROOT)):
        raise ValueError("path escapes root")
    return p


def read_config():
    if CONFIG.exists():
        try:
            return json.loads(CONFIG.read_text("utf-8"))
        except Exception:
            pass
    return {"provider": "openai", "endpoint": "", "model": "", "key": ""}


def save_config(cfg):
    CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), "utf-8")


DEFAULT_GROUPS = [
    {"id": "g4a", "name": "四年級上學期", "collapsed": False},
    {"id": "g4b", "name": "四年級下學期", "collapsed": False},
    {"id": "g5a", "name": "五年級上學期", "collapsed": False},
    {"id": "g5b", "name": "五年級下學期", "collapsed": False},
]


def read_layout(projdir):
    f = projdir / "_layout.json"
    if f.exists():
        try:
            lay = json.loads(f.read_text("utf-8"))
            if lay.get("groups") and "items" in lay:
                return lay
        except Exception:
            pass
    return {"groups": [dict(g) for g in DEFAULT_GROUPS], "items": []}


def save_layout(project, layout):
    projdir = MATERIALS / re.sub(r'[\\/:*?"<>|]+', '_', (project or "").strip())
    if not projdir.is_dir():
        return {"ok": False, "error": "找不到專案"}
    (projdir / "_layout.json").write_text(json.dumps(layout, ensure_ascii=False, indent=2), "utf-8")
    return {"ok": True}


def _lnum(name):
    m = re.match(r'^L(\d+)', name)
    return int(m.group(1)) if m else 10 ** 6


def read_ws_layout():
    f = MATERIALS / "_layout.json"
    if f.exists():
        try:
            return json.loads(f.read_text("utf-8"))
        except Exception:
            pass
    return {"collapsed": {}}


def save_ws_layout(lay):
    (MATERIALS / "_layout.json").write_text(json.dumps(lay, ensure_ascii=False, indent=2), "utf-8")


def build_tree():
    """群組＝頂層學期資料夾；單一工作區（一個合成 project『教材庫』）。"""
    if not MATERIALS.exists():
        return {"projects": []}
    lay = read_ws_layout()
    collapsed = lay.get("collapsed", {})
    groups, lessons = [], []
    for gd in sorted([d for d in MATERIALS.iterdir() if d.is_dir()]):
        gname = gd.name
        groups.append({"id": gname, "name": gname, "collapsed": bool(collapsed.get(gname, False))})
        subs = [d for d in gd.iterdir() if d.is_dir() and d.name.startswith("L")]
        for ld in sorted(subs, key=lambda d: _lnum(d.name)):
            names = [f.name for f in ld.iterdir() if f.is_file()]
            plan_exists = "00_原始計畫.md" in names
            stages = ["done" if plan_exists else "todo"]
            for label, fn in STAGES:
                if fn == "06_成品":
                    hit = any(n.startswith("06_成品") and not n.endswith("說明.md") for n in names)
                    stages.append("done" if hit else "todo")
                else:
                    stages.append("done" if fn in names else "todo")
            products = [{"file": n, "type": ("html" if n.lower().endswith(".html")
                        else ("slides" if n.endswith(".md") else "file"))}
                        for n in names if n.startswith("06_成品") and not n.endswith("說明.md")]
            lessons.append({"folder": ld.name, "title": ld.name, "group": gname,
                            "stages": stages, "products": products})
    if not groups:
        return {"projects": []}
    return {"projects": [{"name": "教材庫", "groups": groups, "lessons": lessons}]}


def arrange(arr):
    """arr = {群組名:[folder順序,...]}。把資料夾搬到目標群組並依位置重新編號 L##。"""
    # 建立目前 folder → 群組 對照
    cur = {}
    for gd in MATERIALS.iterdir():
        if gd.is_dir():
            for ld in gd.iterdir():
                if ld.is_dir() and ld.name.startswith("L"):
                    cur[ld.name] = gd.name
    # 兩階段：先搬到目標群組的暫名，再改成 L##
    tmp = []
    n = 0
    for gname, folders in arr.items():
        gdir = MATERIALS / re.sub(r'[\\/:*?"<>|]+', '_', gname)
        gdir.mkdir(parents=True, exist_ok=True)
        for pos, folder in enumerate(folders):
            src_group = cur.get(folder)
            if not src_group:
                continue
            src = MATERIALS / src_group / folder
            n += 1
            tmpname = f"__t{n}__{folder}"
            dst = gdir / tmpname
            try:
                shutil.move(str(src), str(dst))
            except Exception:
                continue
            title = re.sub(r'^L\d+[_ ]?', '', folder)
            tmp.append((dst, gdir / f"L{pos+1:02d}_{title}"))
    for dst, final in tmp:
        try:
            shutil.move(str(dst), str(final))
        except Exception:
            pass
    return {"ok": True}


def _llm_call(provider, key, model, endpoint, prompt):
    """統一的 AI 呼叫（見《AI串接窗口設定規範》）。openai 相容聊天補全，或 gemini 原生。"""
    provider = (provider or "openai").lower()
    key = (key or "").strip(); model = (model or "").strip(); endpoint = (endpoint or "").strip()
    if not key:
        return {"ok": False, "error": "尚未填 API Key"}
    try:
        if provider.startswith("gemini"):
            base = endpoint if endpoint else "https://generativelanguage.googleapis.com/v1beta"
            url = base.rstrip("/") + f"/models/{model or 'gemini-2.0-flash'}:generateContent?key={urllib.parse.quote(key)}"
            body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode("utf-8"))
            return {"ok": True, "text": data["candidates"][0]["content"]["parts"][0]["text"]}
        if not endpoint:
            return {"ok": False, "error": "OpenAI 相容模式需填『端點 URL』（反向代理，通常結尾 /v1）"}
        url = endpoint.rstrip("/") + "/chat/completions"
        body = json.dumps({"model": model or "gpt-4o-mini",
                           "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/json", "Authorization": "Bearer " + key})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode("utf-8"))
        return {"ok": True, "text": data["choices"][0]["message"]["content"]}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:400]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def gemini_call(prompt: str):
    c = read_config()
    return _llm_call(c.get("provider"), c.get("key"), c.get("model"), c.get("endpoint"), prompt)


def grade_call(prompt: str):
    """評分專用 AI 窗口；未設 grade_key 則回退主 AI（見《AI串接窗口設定規範》）。"""
    c = read_config()
    if not (c.get("grade_key") or "").strip():
        return gemini_call(prompt)
    return _llm_call(c.get("grade_provider") or "openai", c.get("grade_key"),
                     c.get("grade_model"), c.get("grade_endpoint"), prompt)


def fetch_title(url):
    """讀取某網址的 <title>（新增學習單時自動帶標題用）。"""
    if not url:
        return {"ok": False, "error": "缺 url"}
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 beikeCockpit"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read(60000).decode("utf-8", "replace")
        m = re.search(r'<title[^>]*>(.*?)</title>', raw, re.S | re.I)
        return {"ok": True, "title": html.unescape(m.group(1).strip())[:80] if m else ""}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _llm_models(provider, key, endpoint):
    """列可選模型。openai：GET /models（Bearer）→ data[].id；gemini：ListModels。"""
    provider = (provider or "openai").lower(); key = (key or "").strip(); endpoint = (endpoint or "").strip()
    if not key:
        return {"ok": False, "error": "尚未填 API Key"}
    try:
        if provider.startswith("gemini"):
            base = endpoint if endpoint else "https://generativelanguage.googleapis.com/v1beta"
            url = base.rstrip("/") + f"/models?key={urllib.parse.quote(key)}"
            req = urllib.request.Request(url, headers={"User-Agent": "beikeCockpit"})
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read().decode("utf-8"))
            models = [m.get("name", "").split("/")[-1] for m in data.get("models", [])
                      if "generateContent" in (m.get("supportedGenerationMethods") or [])]
        else:
            if not endpoint:
                return {"ok": False, "error": "OpenAI 相容模式需填『端點 URL』（通常結尾 /v1）"}
            url = endpoint.rstrip("/") + "/models"
            req = urllib.request.Request(url, headers={
                "User-Agent": "beikeCockpit", "Authorization": "Bearer " + key})
            with urllib.request.urlopen(req, timeout=40) as r:
                data = json.loads(r.read().decode("utf-8"))
            models = [m.get("id", "") for m in data.get("data", [])]
        models = sorted(set(x for x in models if x))
        return {"ok": True, "models": models}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:300]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def gemini_models():
    c = read_config()
    return _llm_models(c.get("provider"), c.get("key"), c.get("endpoint"))


def grade_models():
    c = read_config()
    if not (c.get("grade_key") or "").strip():
        return _llm_models(c.get("provider"), c.get("key"), c.get("endpoint"))
    return _llm_models(c.get("grade_provider") or "openai", c.get("grade_key"), c.get("grade_endpoint"))


def pptx_thumbs(rel: str):
    """用 PowerPoint COM 把 pptx 轉成 PNG，存到同層 .thumbs/<name>/。回傳縮圖相對路徑清單。"""
    pptx = safe(rel)
    if not pptx.exists():
        return {"ok": False, "error": "找不到檔案"}
    outdir = pptx.parent / ".thumbs" / pptx.stem
    outdir.mkdir(parents=True, exist_ok=True)
    # 已轉過就直接回傳
    existing = sorted(outdir.glob("slide*.png"))
    if not existing:
        ps = f'''
$ErrorActionPreference="Stop"
$app=New-Object -ComObject PowerPoint.Application
$pres=$app.Presentations.Open("{pptx}", -1, 0, 0)
$w=[int]$pres.PageSetup.SlideWidth; $scale=1000.0/$w
$ew=[int]($w*$scale); $eh=[int]([int]$pres.PageSetup.SlideHeight*$scale)
for($i=1;$i -le $pres.Slides.Count;$i++){{
  $pres.Slides.Item($i).Export((Join-Path "{outdir}" ("slide{{0:D2}}.png" -f $i)),"PNG",$ew,$eh)
}}
$pres.Close(); $app.Quit()
'''
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                           capture_output=True, timeout=180)
        except Exception as e:
            return {"ok": False, "error": f"轉檔失敗：{e}"}
        existing = sorted(outdir.glob("slide*.png"))
    rels = [str(p.relative_to(ROOT)).replace("\\", "/") for p in existing]
    return {"ok": True, "thumbs": rels}


IMG_RE = re.compile(r'https?://[^\s()"\'<>\]]+\.(?:png|jpe?g|webp|gif)', re.I)

LM_GUIDE = """# 給 NotebookLM 的簡報生成指引

請依下列規則，把「教學內容.md」做成教學簡報。

## 顆粒度（最重要）
- 一頁只做一個微步驟：一次點擊／一個新想法／一個例子＝一頁。
- 凡「步驟1…2…3」一律拆成多頁；每種題型／選項／變體各一頁。
- 引發問題與比喻可跨多頁鋪陳。操作型一節約 15–25 頁，不要壓成 8–12 頁。

## 文字
- 標題用問句或任務句，≤ 全形 14 字。
- 每頁條列 ≤ 3 條、每條 ≤ 全形 16 字、關鍵詞開頭。
- 步驟頁每步一行祈使句並標按鈕/快捷鍵；每頁 1 重點；禁止整段文字。

## 視覺與圖片
- 圖片一律用「圖片/」資料夾裡的檔案（已下載本機，勿用外部連結）。
- 影片不嵌入：需要影片的地方放一頁只有標題的空白頁（例：▶ 播放：xxx 0:12–0:52）。

## 語氣
- 對小學生：親切、鼓勵、口語、帶冒險感；台南在地脈絡。
"""


def _fname_from_url(u):
    name = urllib.parse.unquote(u.split("?")[0].rstrip("/").split("/")[-1])
    name = re.sub(r'[^\w.\-]+', '_', name)[-80:]
    return name or "img"


def reveal(rel):
    try:
        p = safe(rel)
        subprocess.Popen(["explorer", str(p)])
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def package_lm(rel_lesson):
    base = safe(rel_lesson)
    if not base.is_dir():
        return {"ok": False, "error": "找不到節次資料夾"}
    out = base / "_LM包"
    imgdir = out / "圖片"
    imgdir.mkdir(parents=True, exist_ok=True)

    # 收集教學文字
    parts = []
    for fn in ["05_教學活動流程.md", "04_素材清單與缺口.md", "03_素材候選.md"]:
        f = base / fn
        if f.exists():
            parts.append(f"===== {fn} =====\n" + f.read_text("utf-8", "replace"))
    (out / "教學內容.md").write_text("\n\n".join(parts) or "（此節尚無教學內容）", "utf-8")
    (out / "給NotebookLM的指引.md").write_text(LM_GUIDE, "utf-8")

    # 找圖片 URL（從 md 與 html）
    urls = set()
    for f in list(base.glob("*.md")) + list(base.glob("*.html")):
        try:
            urls |= set(IMG_RE.findall(f.read_text("utf-8", "replace")))
        except Exception:
            pass
    got, failed = [], []
    for u in sorted(urls):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 beikeCockpit"})
            with urllib.request.urlopen(req, timeout=40) as r:
                (imgdir / _fname_from_url(u)).write_bytes(r.read())
            got.append(_fname_from_url(u))
        except Exception as e:
            failed.append(u)
    # 複製本機 assets/ 圖
    adir = base / "assets"
    if adir.is_dir():
        for f in adir.iterdir():
            if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                (imgdir / f.name).write_bytes(f.read_bytes())
                got.append(f.name)

    (out / "如何使用.txt").write_text(
        "把整個「_LM包」資料夾裡的檔案，一次拖進 NotebookLM 當作 sources：\n"
        "1. 教學內容.md（環節＋素材清單）\n"
        "2. 給NotebookLM的指引.md（生成規則）\n"
        "3. 圖片/（已下載的圖，NotebookLM 用得到）\n"
        "然後叫 NotebookLM 依指引做成簡報。\n", "utf-8")

    return {"ok": True, "folder": str(out.relative_to(ROOT)).replace("\\", "/"),
            "images": got, "failed": failed}


def extract_text(name, raw):
    """從匯入檔抽取純文字：md/txt 直讀；docx 用 zipfile；pdf/doc 用 Word COM。"""
    ext = (name.rsplit(".", 1)[-1] if "." in name else "").lower()
    try:
        if ext in ("md", "txt", "csv"):
            return {"ok": True, "text": raw.decode("utf-8", "replace")}
        if ext == "docx":
            z = zipfile.ZipFile(io.BytesIO(raw))
            xml = z.read("word/document.xml").decode("utf-8", "replace")
            xml = xml.replace("</w:p>", "\n").replace("<w:tab/>", "\t")
            text = re.sub(r"<[^>]+>", "", xml)
            return {"ok": True, "text": html.unescape(text)}
        if ext in ("pdf", "doc"):
            tmp = Path(tempfile.gettempdir()) / ("_import_" + str(os.getpid()) + "." + ext)
            out = Path(tempfile.gettempdir()) / ("_import_" + str(os.getpid()) + ".txt")
            tmp.write_bytes(raw)
            ps = (
                "$ErrorActionPreference='Stop';"
                "$w=New-Object -ComObject Word.Application;$w.Visible=$false;"
                "try{$w.DisplayAlerts=0}catch{};"
                f"$d=$w.Documents.Open('{tmp}',$false,$true);"
                f"[System.IO.File]::WriteAllText('{out}',$d.Content.Text,[System.Text.Encoding]::UTF8);"
                "$d.Close($false);$w.Quit()"
            )
            r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                               capture_output=True, timeout=120)
            if out.exists():
                text = out.read_text("utf-8", "replace")
                try:
                    tmp.unlink(); out.unlink()
                except Exception:
                    pass
                return {"ok": True, "text": text}
            return {"ok": False, "error": "Word 抽取失敗（需安裝 Word）：" +
                    r.stderr.decode("utf-8", "replace")[:200]}
        return {"ok": False, "error": f"不支援的格式：.{ext}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def segment_plan(text):
    """把計畫依週次標頭切成 {code: 原文段落}。code 例：W1-3。"""
    pat = re.compile(r'第\s*(\d+)(?:\s*-\s*(\d+))?\s*週')
    marks = [(m.start(), int(m.group(1)), int(m.group(2) or m.group(1)))
             for m in pat.finditer(text)]
    secs = {}
    order = []
    for j, (pos, a, b) in enumerate(marks):
        end = marks[j + 1][0] if j + 1 < len(marks) else len(text)
        body = re.split(r'◎教學期程', text[pos:end])[0].strip()
        code = 'W%d-%d' % (a, b) if b != a else 'W%d' % a
        if code not in secs:
            secs[code] = body
            order.append(code)
    return secs, order


def _yt_id(url):
    m = re.search(r'(?:v=|youtu\.be/|/embed/)([\w-]{11})', url)
    return m.group(1) if m else None


def _fetch_meta(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 beikeCockpit"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read(60000).decode("utf-8", "replace")
        t = re.search(r'<title[^>]*>(.*?)</title>', raw, re.S | re.I)
        d = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', raw, re.I) \
            or re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)', raw, re.I)
        title = html.unescape(t.group(1).strip())[:80] if t else ""
        desc = html.unescape(d.group(1).strip())[:160] if d else ""
        return title, desc
    except Exception:
        return "", ""


def crawl_materials(group, folder):
    """爬取『素材候選(03)/關鍵字(02)』裡提到的 URL：圖片下載本機、影片取縮圖、網站取標題說明。"""
    ld = safe(f"materials/{group}/{folder}")
    if not ld.is_dir():
        return {"ok": False, "error": "找不到節次"}
    text = ""
    for fn in ("03_素材候選.md", "02_搜尋關鍵字.md"):
        f = ld / fn
        if f.exists():
            text += f.read_text("utf-8", "replace") + "\n"
    if not text.strip():
        return {"ok": False, "error": "先完成『素材搜尋』(03) 才有素材可爬"}
    assets = ld / "assets"
    assets.mkdir(exist_ok=True)
    url_re = re.compile(r'(?:\[([^\]]*)\]\()?(https?://[^\s)\]<>"]+)')
    items, seen = [], set()
    for line in text.splitlines():
        for m in url_re.finditer(line):
            url = m.group(2).rstrip('.,;）)')
            if url in seen:
                continue
            seen.add(url)
            cap = (m.group(1) or "").strip()
            if not cap:
                cap = re.sub(re.escape(m.group(0)), '', line)
                cap = re.sub(r'[\|\-•*#>`　]+', ' ', cap).strip()[:50]
            low = url.lower()
            if re.search(r'\.(jpe?g|png|webp|gif)(\?|$)', low):
                name = _fname_from_url(url)
                rel = f"materials/{group}/{folder}/assets/{name}"
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 beikeCockpit"})
                    with urllib.request.urlopen(req, timeout=30) as r:
                        (assets / name).write_bytes(r.read())
                    items.append({"type": "image", "url": url, "file": rel, "caption": cap or name})
                except Exception as e:
                    items.append({"type": "image", "url": url, "caption": cap, "error": str(e)[:60]})
            elif _yt_id(url):
                vid = _yt_id(url)
                items.append({"type": "video", "url": url,
                              "thumb": f"https://img.youtube.com/vi/{vid}/hqdefault.jpg", "caption": cap})
            else:
                title, desc = _fetch_meta(url)
                items.append({"type": "site", "url": url, "title": title or cap, "desc": desc})
    return {"ok": True, "items": items, "count": len(items)}


# ========== 素材搜尋（Tavily 真實搜尋 → AI 判斷）==========
# 為什麼要有這段：AI 本身不能上網，直接叫它給素材網址一定是幻覺（實測它回的深層網址是 404）。
# 所以 AI 的角色改成它真正擅長的兩件事——「想查詢字串」與「讀真實內容下判斷」，
# 中間夾一個真的搜尋 API，網址一律只能來自搜尋結果，不能來自模型記憶。
TAVILY_URL = "https://api.tavily.com/search"
# 優先站內搜的高價值教學來源（找不到才退回全網搜）
EDU_SITES = ["adl.edu.tw", "junyiacademy.org", "phet.colorado.edu", "naer.edu.tw",
             "data.gov.tw", "tn.edu.tw", "commons.wikimedia.org", "openverse.org"]


def tavily_search(query, max_results=6, include_domains=None, include_images=False):
    c = read_config()
    key = (c.get("tavily_key") or "").strip()
    if not key:
        return {"ok": False, "error": "尚未填 Tavily API Key（右上 ⚙ 設定 → 素材搜尋）"}
    body = {"query": query, "max_results": max_results, "search_depth": "basic",
            "include_images": bool(include_images), "api_key": key}
    if include_domains:
        body["include_domains"] = include_domains
    try:
        req = urllib.request.Request(TAVILY_URL, data=json.dumps(body).encode("utf-8"),
                                     headers={"Content-Type": "application/json",
                                              "Authorization": "Bearer " + key})
        with urllib.request.urlopen(req, timeout=60) as r:
            return {"ok": True, "data": json.loads(r.read().decode("utf-8"))}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def search_test():
    """設定面板的「測試搜尋」：真的送一次搜尋，證明金鑰可用、且回來的是真網址。"""
    r = tavily_search("教育部 因材網 數位學習平台", max_results=3)
    if not r.get("ok"):
        return r
    res = (r["data"] or {}).get("results") or []
    if not res:
        return {"ok": False, "error": "搜尋成功但沒有結果"}
    return {"ok": True, "count": len(res), "sample": res[0].get("url", "")}


def _ai_queries(ctx, title):
    """AI 把鷹架/關鍵字轉成幾組實際要送進搜尋引擎的查詢字串（它擅長這個，不擅長記網址）。"""
    prompt = (
        "你是國小資訊課教師的備課協作者。下面是某一節課的鷹架分析與關鍵字。\n"
        f"節次主題：{title}\n{ctx}\n\n"
        "請產生 4–6 組**實際要丟進搜尋引擎**的查詢字串，用來找這節課可以用的教學素材"
        "（圖片、影片、真實案例、新聞、互動網站都算）。要求：\n"
        "- 每組查詢針對不同角度，不要只是同義詞換來換去。\n"
        "- 用搜尋引擎查得到的講法，不要用教案術語（例如別寫「鷹架」「LV1」）。\n"
        "- 優先能找到台灣、台南在地或繁體中文的素材；必要時可混英文查詢。\n\n"
        '只輸出 JSON（無多餘文字、無程式碼圍欄）：{"queries":["查詢1","查詢2","..."]}'
    )
    r = gemini_call(prompt)
    if not r.get("ok"):
        return []
    m = re.search(r'\{.*\}', r.get("text", ""), re.S)
    if not m:
        return []
    try:
        qs = json.loads(m.group(0)).get("queries") or []
        return [str(q).strip() for q in qs if str(q).strip()][:6]
    except Exception:
        return []


def _ai_judge(items, title, ctx):
    """把**真實搜到並爬回來的內容**交給 AI 判斷。鍵名由伺服器指定（k0、k1…）再換回去，
    避免 AI 自己編名字導致對不上——跟評分平台批次評分同一個手法。"""
    if not items:
        return {}
    aliases = [f"k{i}" for i in range(len(items))]
    blocks = []
    for a, it in zip(aliases, items):
        blocks.append(f"【{a}】標題：{it.get('title','')}\n網址：{it.get('url','')}\n"
                      f"內容摘要：{(it.get('content') or '')[:600]}")
    prompt = (
        "你是國小資訊課教師的備課協作者。以下是為節次「" + title + "」實際搜尋並抓回來的素材，"
        "請逐一判斷它能不能用在這節課。\n" + ctx[:1500] + "\n\n" + "\n\n".join(blocks) +
        "\n\n只輸出一個 JSON 物件（無多餘文字、無程式碼圍欄），每則都要用【】裡的代號當鍵名、一個不漏：\n"
        '{"k0":{"fit":"高|中|低","summary":"一句話說這是什麼內容","use":"具體怎麼用在這節課（哪個環節、給學生看什麼）",'
        '"caution":"要注意的地方，沒有就空字串"},...}\n'
        "fit 判準：高＝直接可用；中＝要老師加工或只取一部分；低＝離題或不適合國小。"
    )
    r = gemini_call(prompt)
    if not r.get("ok"):
        return {}
    m = re.search(r'\{.*\}', r.get("text", ""), re.S)
    if not m:
        return {}
    try:
        parsed = json.loads(m.group(0))
    except Exception:
        return {}
    out = {}
    for a, it in zip(aliases, items):
        e = parsed.get(a)
        if isinstance(e, dict):
            out[it["url"]] = {"fit": e.get("fit", ""), "summary": e.get("summary", ""),
                              "use": e.get("use", ""), "caution": e.get("caution", "")}
    return out


def material_search(group, folder, force=False, edu_first=True, peek=False):
    """素材搜尋主流程：AI 想查詢字串 → Tavily 真搜 → 去重 → AI 判斷真實內容 → 存快取。
    peek=True：只讀快取、絕不發動搜尋（打開階段時用，避免一進畫面就扣 API 額度）。"""
    ld = safe(f"materials/{group}/{folder}")
    if not ld.is_dir():
        return {"ok": False, "error": "找不到節次"}
    cache = ld / "03_素材候選.json"
    if cache.exists() and not force:
        try:
            d = json.loads(cache.read_text("utf-8"))
            d["cached"] = True
            return d
        except Exception:
            pass
    if peek:
        return {"ok": False, "cached": False, "error": "尚未搜尋過"}
    ctx = ""
    for fn in ("01_目標與鷹架.md", "02_搜尋關鍵字.md"):
        f = ld / fn
        if f.exists():
            ctx += f"\n=== {fn} ===\n" + f.read_text("utf-8", "replace")[:3000]
    if not ctx.strip():
        return {"ok": False, "error": "先完成『鷹架分析(01)』與『關鍵字(02)』，才有東西可以拿去搜"}
    title = re.sub(r'^L\d+_', '', folder)
    queries = _ai_queries(ctx, title)
    if not queries:
        return {"ok": False, "error": "AI 產生查詢字串失敗（檢查 ⚙ 設定的 AI 端點）"}
    items, seen, errors, images = [], set(), [], []
    for q in queries:
        # 先站內搜高價值教學來源，再全網搜補足——品質差很多
        rounds = ([(EDU_SITES, 4)] if edu_first else []) + [(None, 6)]
        for domains, n in rounds:
            r = tavily_search(q, max_results=n, include_domains=domains, include_images=(domains is None))
            if not r.get("ok"):
                errors.append(f"{q}：{r.get('error','')}")
                continue
            data = r["data"] or {}
            for res in (data.get("results") or []):
                u = res.get("url", "")
                if not u or u in seen:
                    continue
                seen.add(u)
                items.append({"type": "site", "url": u, "title": res.get("title", ""),
                              "content": (res.get("content") or "")[:800],
                              "score": res.get("score"), "query": q,
                              "domain": urllib.parse.urlparse(u).netloc})
            for img in (data.get("images") or [])[:4]:
                iu = img if isinstance(img, str) else (img or {}).get("url", "")
                if iu and iu not in seen:
                    seen.add(iu)
                    images.append({"type": "image", "url": iu, "title": "", "content": "", "query": q,
                                   "domain": urllib.parse.urlparse(iu).netloc})
    if not items and not images:
        return {"ok": False, "error": "搜尋沒有結果" + ("；" + "；".join(errors[:3]) if errors else "")}
    judged = _ai_judge(items, title, ctx)
    for it in items:
        it.update(judged.get(it["url"], {}))
    order = {"高": 0, "中": 1, "低": 2, "": 3}
    items.sort(key=lambda x: order.get(x.get("fit", ""), 3))
    out = {"ok": True, "queries": queries, "items": items + images,
           "count": len(items) + len(images), "errors": errors, "cached": False}
    try:
        cache.write_text(json.dumps(out, ensure_ascii=False, indent=1), "utf-8")
    except Exception:
        pass
    return out


def split_plan(group, plan_text):
    """計畫切分（群組層級，含 section 週次編碼）：AI 切節並標段落 → 系統掛正確原始計畫。"""
    group = re.sub(r'[\\/:*?"<>|]+', '_', (group or "").strip())
    if not group:
        return {"ok": False, "error": "請填目標群組（學期）"}
    if not (plan_text or "").strip():
        return {"ok": False, "error": "請貼上課程計畫內容"}
    secs, order = segment_plan(plan_text)
    codes = order or ["W?"]
    prompt = (
        "你是這位教師的備課協作者。請把下面的課程計畫切分成節次，**盡量切小**。\n"
        "切分原則：\n"
        "- 一節只引入 1–2 個新概念或工具操作；寧可多切幾節、每節內容少。\n"
        "- 工具型單元切小：文書/簡報/Canva 約 3–4 節、Scratch 約 5 節、影片/網站約 2–3 節、發表/反思約 1–2 節。\n"
        "- 名目節數打約 8 折，但寧可節數多。LV1 底線寫成可觀察行為（能做出…），勿用「了解/認識」。\n"
        "- **每一節都要標註它來自哪個計畫段落代碼 section**，代碼只能從這個清單選："
        + "、".join(codes) + "。同一段落可對應多節。\n\n"
        "**只輸出 JSON**（無多餘文字、無程式碼圍欄），格式：\n"
        '{"lessons":[{"id":"L01","title":"單元主題(可當資料夾名)","lv1":"可觀察行為","section":"'
        + codes[0] + '"}]}\n\n===課程計畫===\n'
        + plan_text[:14000]
    )
    r = gemini_call(prompt)
    if not r.get("ok"):
        return {"ok": False, "error": "AI：" + r.get("error", "失敗")}
    txt = r.get("text", "")
    m = re.search(r'\{.*\}', txt, re.S)
    if not m:
        return {"ok": False, "error": "AI 未回傳 JSON。原始：" + txt[:300]}
    try:
        lessons = json.loads(m.group(0)).get("lessons") or []
    except Exception as e:
        return {"ok": False, "error": f"JSON 解析失敗：{e}。原始：{txt[:300]}"}
    if not lessons:
        return {"ok": False, "error": "AI 回傳沒有 lessons"}
    gdir = MATERIALS / group
    gdir.mkdir(parents=True, exist_ok=True)
    (gdir / "課程計畫").mkdir(exist_ok=True)
    (gdir / "課程計畫" / "課程計畫.md").write_text("# 課程計畫（原始）\n\n" + plan_text, "utf-8")
    created = []
    for i, L in enumerate(lessons, 1):
        title = str(L.get("title") or "單元").strip()
        fname = re.sub(r'[\\/:*?"<>|\s]+', '', title)[:24] or "單元"
        folder = f"L{i:02d}_{fname}"
        ld = gdir / folder
        ld.mkdir(exist_ok=True)
        sec_code = str(L.get("section") or "").strip()
        sec_text = secs.get(sec_code, "（AI 未標註或找不到對應段落）")
        ld.joinpath("00_原始計畫.md").write_text(
            f"# 原始計畫段落 · {sec_code}（{title}）\n> 本節所屬計畫段落原文；同段落的多節內容相同。\n\n{sec_text}\n", "utf-8")
        created.append(folder)
    return {"ok": True, "group": group, "lessons": created}


def lesson_add(group, title):
    group = re.sub(r'[\\/:*?"<>|]+', '_', (group or "").strip())
    gdir = MATERIALS / group
    if not gdir.is_dir():
        return {"ok": False, "error": "找不到群組"}
    nums = [int(re.match(r'^L(\d+)', d.name).group(1)) for d in gdir.iterdir()
            if d.is_dir() and re.match(r'^L\d+', d.name)]
    lid = f"L{(max(nums) + 1) if nums else 1:02d}"
    fname = re.sub(r'[\\/:*?"<>|\s]+', '', (title or "").strip())[:24] or "新單元"
    folder = f"{lid}_{fname}"
    (gdir / folder).mkdir(exist_ok=True)
    return {"ok": True, "group": group, "folder": folder}


def lesson_delete(group, folder):
    group = re.sub(r'[\\/:*?"<>|]+', '_', (group or "").strip())
    target = safe(f"materials/{group}/{folder}")
    if not target.is_dir() or target.parent != (MATERIALS / group):
        return {"ok": False, "error": "路徑不合法"}
    shutil.rmtree(target)
    return {"ok": True}


# ========== Google Classroom / Drive / GitHub 串接 ==========
REDIRECT_URI = f"http://127.0.0.1:{PORT}/oauth/callback"
GOOGLE_SCOPES = " ".join([
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.announcements",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials",
    "https://www.googleapis.com/auth/classroom.coursework.students",
    "https://www.googleapis.com/auth/classroom.rosters.readonly",  # 讀名單→座號/姓名對應 userId（回寫成績用）
    "https://www.googleapis.com/auth/drive.file",
])


def _http(url, method="GET", headers=None, data=None, timeout=90):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read().decode("utf-8", "replace")
    return json.loads(raw) if raw.strip() else {}


def _post_form(url, form):
    data = urllib.parse.urlencode(form).encode()
    return _http(url, "POST", {"Content-Type": "application/x-www-form-urlencoded"}, data)


def google_auth_url():
    cfg = read_config()
    cid = (cfg.get("google_client_id") or "").strip()
    if not cid:
        return {"ok": False, "error": "尚未填 Google client_id"}
    params = {"client_id": cid, "redirect_uri": REDIRECT_URI, "response_type": "code",
              "scope": GOOGLE_SCOPES, "access_type": "offline", "prompt": "consent",
              "include_granted_scopes": "true"}
    return {"ok": True, "url": "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)}


def google_exchange(code):
    cfg = read_config()
    tok = _post_form("https://oauth2.googleapis.com/token", {
        "code": code, "client_id": cfg.get("google_client_id", ""),
        "client_secret": cfg.get("google_client_secret", ""),
        "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"})
    cfg["google_token"] = {"access_token": tok.get("access_token"),
                           "refresh_token": tok.get("refresh_token"),
                           "expires_at": time.time() + tok.get("expires_in", 3600),
                           "scope": tok.get("scope", "")}
    save_config(cfg)
    return tok


def google_access_token():
    cfg = read_config()
    t = cfg.get("google_token") or {}
    if not t.get("access_token"):
        return None
    if t.get("expires_at", 0) < time.time() + 60 and t.get("refresh_token"):
        nt = _post_form("https://oauth2.googleapis.com/token", {
            "refresh_token": t["refresh_token"], "client_id": cfg.get("google_client_id", ""),
            "client_secret": cfg.get("google_client_secret", ""), "grant_type": "refresh_token"})
        if nt.get("access_token"):
            t["access_token"] = nt["access_token"]
            t["expires_at"] = time.time() + nt.get("expires_in", 3600)
            cfg["google_token"] = t
            save_config(cfg)
    return t.get("access_token")


def _gapi(url, method="GET", body=None):
    token = google_access_token()
    if not token:
        raise RuntimeError("尚未授權 Google（請在設定按『授權 Google』）")
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body is not None else None
    return _http(url, method, headers, data)


def google_courses():
    try:
        data = _gapi("https://classroom.googleapis.com/v1/courses?courseStates=ACTIVE&teacherId=me&pageSize=100")
        courses = [{"id": c["id"], "name": c.get("name", ""), "section": c.get("section", "")}
                   for c in data.get("courses", [])]
        return {"ok": True, "courses": courses}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def drive_upload(rel, name):
    token = google_access_token()
    if not token:
        return {"ok": False, "error": "尚未授權 Google"}
    p = safe(rel)
    if not p.exists():
        return {"ok": False, "error": "找不到檔案"}
    boundary = "beikeBoundary1234"
    meta = json.dumps({"name": name}).encode()
    ct = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
    body = (b"--" + boundary.encode() + b"\r\n"
            + b"Content-Type: application/json; charset=UTF-8\r\n\r\n" + meta + b"\r\n"
            + b"--" + boundary.encode() + b"\r\n"
            + ("Content-Type: " + ct + "\r\n\r\n").encode() + p.read_bytes() + b"\r\n"
            + b"--" + boundary.encode() + b"--")
    headers = {"Authorization": "Bearer " + token,
               "Content-Type": "multipart/related; boundary=" + boundary}
    try:
        r = _http("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,webViewLink",
                  "POST", headers, body)
        return {"ok": True, "id": r.get("id"), "link": r.get("webViewLink")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def classroom_publish(course_id, ptype, title, text, drive_id=None, link=None):
    materials = []
    if drive_id:
        materials.append({"driveFile": {"driveFile": {"id": drive_id}, "shareMode": "VIEW"}})
    if link:
        materials.append({"link": {"url": link}})
    base = f"https://classroom.googleapis.com/v1/courses/{course_id}/"
    try:
        if ptype == "announcement":
            body = {"text": text or title or "（無內容）", "materials": materials, "state": "PUBLISHED"}
            r = _gapi(base + "announcements", "POST", body)
        elif ptype == "coursework":
            body = {"title": title or "作業", "description": text, "workType": "ASSIGNMENT",
                    "state": "PUBLISHED", "maxPoints": 100, "materials": materials}
            r = _gapi(base + "courseWork", "POST", body)
        elif ptype == "question":
            # 單選問題（例如每週簽到）。text 是每行一個選項；沒填就用「簽到」。
            # 標題慣例「第X週 單元名稱」，供評分平台回寫成績時依週次比對到同一份，不必每份學習單各建一份作業。
            choices = [c.strip() for c in (text or "").split("\n") if c.strip()] or ["簽到"]
            body = {"title": title or "簽到", "workType": "MULTIPLE_CHOICE_QUESTION",
                    "state": "PUBLISHED", "multipleChoiceQuestion": {"choices": choices}, "materials": materials}
            r = _gapi(base + "courseWork", "POST", body)
        else:  # material
            body = {"title": title or "教材", "description": text, "materials": materials, "state": "PUBLISHED"}
            r = _gapi(base + "courseWorkMaterials", "POST", body)
        return {"ok": True, "id": r.get("id"), "link": r.get("alternateLink")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def classroom_coursework(course_id):
    """列某課程的作業（courseWork）：id＋標題＋滿分，供回寫成績時選擇。"""
    if not course_id:
        return {"ok": False, "error": "缺 courseId"}
    try:
        data = _gapi(f"https://classroom.googleapis.com/v1/courses/{course_id}/courseWork?pageSize=100")
        works = [{"id": w["id"], "title": w.get("title", ""), "maxPoints": w.get("maxPoints")}
                 for w in data.get("courseWork", [])]
        return {"ok": True, "courseWork": works}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def classroom_students(course_id):
    """列某課程的學生：userId＋姓名，供平台座號/姓名對應到 Classroom 帳號。"""
    if not course_id:
        return {"ok": False, "error": "缺 courseId"}
    try:
        data = _gapi(f"https://classroom.googleapis.com/v1/courses/{course_id}/students?pageSize=200")
        studs = [{"userId": s["userId"],
                  "name": (s.get("profile", {}).get("name", {}) or {}).get("fullName", "")}
                 for s in data.get("students", [])]
        return {"ok": True, "students": studs}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def classroom_grades(course_id, coursework_id, grades):
    """回寫成績：grades=[{userId, grade}]。設 draft＋assigned 後 return 給學生。"""
    if not (course_id and coursework_id):
        return {"ok": False, "error": "缺 courseId 或 courseWorkId"}
    base = f"https://classroom.googleapis.com/v1/courses/{course_id}/courseWork/{coursework_id}/studentSubmissions"
    try:
        subs = _gapi(base + "?pageSize=200")
        by_user = {s.get("userId"): s.get("id") for s in subs.get("studentSubmissions", [])}
    except Exception as e:
        return {"ok": False, "error": "讀取作業繳交失敗：" + str(e)}
    done, failed = [], []
    for g in (grades or []):
        uid, grade = g.get("userId"), g.get("grade")
        sid = by_user.get(uid)
        if not sid:
            failed.append({"userId": uid, "error": "此作業找不到該生的繳交"})
            continue
        try:
            _gapi(f"{base}/{sid}?updateMask=draftGrade,assignedGrade", "PATCH",
                  {"draftGrade": grade, "assignedGrade": grade})
        except Exception as e:
            failed.append({"userId": uid, "error": str(e)[:100]})
            continue
        try:
            _gapi(f"{base}/{sid}:return", "POST", {})
        except Exception:
            pass  # 已發還過會報錯，忽略
        done.append(uid)
    return {"ok": True, "done": len(done), "failed": failed}


def github_publish(rel, dest_path):
    cfg = read_config()
    token = (cfg.get("github_token") or "").strip()
    _, owner, name = _repo_ssh()
    if not token or not owner or not name:
        return {"ok": False, "error": "尚未填 GitHub token 或 repo（owner/repo 或網址）"}
    p = safe(rel)
    if not p.exists():
        return {"ok": False, "error": "找不到檔案"}
    api = f"https://api.github.com/repos/{owner}/{name}/contents/{urllib.parse.quote(dest_path)}"
    hdr = {"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
           "User-Agent": "beikeCockpit"}
    sha = None
    try:
        cur = _http(api, "GET", hdr)
        sha = cur.get("sha")
    except Exception:
        pass
    payload = {"message": "publish " + dest_path, "content": base64.b64encode(p.read_bytes()).decode()}
    if sha:
        payload["sha"] = sha
    try:
        _http(api, "PUT", {**hdr, "Content-Type": "application/json"}, json.dumps(payload).encode())
        pages = f"https://{owner}.github.io/{name}/{dest_path}"
        return {"ok": True, "url": pages}
    except Exception as e:
        return {"ok": False, "error": str(e)}


PUB_CACHE = HERE / ".pub_repo"          # 發布用的本機快取儲存庫（SSH）


def _grade_code(group):
    """群組名 → 年級資料夾碼。四上→g4、四下→g4b、五上→g5、五下→g5b。"""
    g = group or ""
    grade = "4" if "四" in g else ("5" if "五" in g else "")
    if not grade:
        return None
    return f"g{grade}" + ("b" if "下" in g else "")


def _repo_ssh():
    """從 config 的 github_repo 取 (ssh_url, owner, name)。接受 owner/repo 或 GitHub 網址。"""
    repo = (read_config().get("github_repo") or "").strip()
    m = re.search(r'github\.com[:/]+([^/]+)/([^/.\s]+)', repo)
    if m:
        return f"git@github.com:{m.group(1)}/{m.group(2)}.git", m.group(1), m.group(2)
    if "/" in repo:
        owner, name = repo.split("/", 1)
        name = name.rstrip("/").replace(".git", "").strip()
        return f"git@github.com:{owner.strip()}/{name}.git", owner.strip(), name
    return None, None, None


def _run_git(args, cwd, timeout=180):
    env = dict(os.environ)
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new")
    r = subprocess.run(["git"] + args, cwd=str(cwd), capture_output=True, timeout=timeout, env=env)
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


def git_publish(group, folder):
    """把某節的 06_成品.html＋assets/ 推到 pcclass 的 g{年級}/L##/（SSH，整包一次 commit）。"""
    ssh_url, owner, name = _repo_ssh()
    if not ssh_url:
        return {"ok": False, "error": "設定的 github_repo 需為 owner/repo 或 GitHub 網址"}
    code = _grade_code(group)
    if not code:
        return {"ok": False, "error": f"無法從群組「{group}」判斷年級碼（需含 四/五 年級）"}
    m = re.match(r'(L\d+)', folder or "")
    if not m:
        return {"ok": False, "error": "節次資料夾需以 L## 開頭"}
    lcode = m.group(1)
    src = safe(f"materials/{group}/{folder}")
    prod = next((src / n for n in sorted(os.listdir(src))
                 if n.startswith("06_成品") and n.lower().endswith(".html")), None)
    if not prod:
        return {"ok": False, "error": "找不到 06_成品*.html（先完成成品）"}
    # 準備快取庫：沒有就 clone；有就抓最新並硬重置到 origin/main
    try:
        if not (PUB_CACHE / ".git").exists():
            if PUB_CACHE.exists():
                shutil.rmtree(PUB_CACHE, ignore_errors=True)
            rc, so, se = _run_git(["clone", ssh_url, str(PUB_CACHE)], HERE, timeout=240)
            if rc != 0:
                return {"ok": False, "error": "clone 失敗（檢查 SSH 金鑰）：" + (se or so)[:300]}
        else:
            _run_git(["remote", "set-url", "origin", ssh_url], PUB_CACHE)
            _run_git(["fetch", "origin", "main"], PUB_CACHE, timeout=120)
            _run_git(["reset", "--hard", "origin/main"], PUB_CACHE)
            _run_git(["clean", "-fd"], PUB_CACHE)
    except Exception as e:
        return {"ok": False, "error": f"準備儲存庫失敗：{e}"}
    # 複製整包 → g{code}/L##/
    dest = PUB_CACHE / code / lcode
    if dest.exists():
        shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(prod), str(dest / "index.html"))
    adir = src / "assets"
    if adir.is_dir():
        shutil.copytree(str(adir), str(dest / "assets"))
    gi = PUB_CACHE / ".gitignore"
    if not gi.exists():
        gi.write_text("*.md\nclient_secret*.json\n*credentials*.json\n*.env\n.env*\n*.key\n*.pem\n.DS_Store\nThumbs.db\n__pycache__/\n", "utf-8")
    _run_git(["config", "user.name", owner or "cockpit"], PUB_CACHE)
    _run_git(["config", "user.email", (read_config().get("teacher_email") or "cockpit@local")], PUB_CACHE)
    _run_git(["add", "-A"], PUB_CACHE)
    rc, so, se = _run_git(["commit", "-m", f"publish {code}/{lcode}"], PUB_CACHE)
    nothing = "nothing to commit" in (so + se)
    if rc != 0 and not nothing:
        return {"ok": False, "error": "commit 失敗：" + (se or so)[:300]}
    if not nothing:
        rc, so, se = _run_git(["push", "origin", "HEAD:main"], PUB_CACHE, timeout=240)
        if rc != 0:
            return {"ok": False, "error": "push 失敗（SSH）：" + (se or so)[:300]}
    return {"ok": True, "url": f"https://{owner}.github.io/{name}/{code}/{lcode}/",
            "path": f"{code}/{lcode}/", "nothing": nothing}


def _norm(v):
    if isinstance(v, list):
        return sorted(_norm(x) for x in v)
    return str(v).strip().lower()


def _ai_grade(open_items, rubric, questions):
    """開放題交 AI 評分（走既有 gemini_call）。回 {ok, score, feedback, perItem}。"""
    qmap = {q.get("qid"): q for q in (questions or [])}
    blocks = []
    for qid, ans in open_items.items():
        pq = (qmap.get(qid, {}) or {}).get("prompt", "")
        blocks.append(f"[{qid}] 題目：{pq or '(無題幹)'}\n學生作答：{ans}")
    if rubric and rubric.get("criteria"):
        rub = "評分規準：\n" + "\n".join(
            f"- {c.get('name','')}（{c.get('points','')} 分）：{c.get('desc','')}" for c in rubric["criteria"])
    else:
        rub = "評分規準：未提供。請就內容完整度、正確性、是否切題，給 0–100 分。"
    prompt = (
        "你是國小資訊課的閱卷老師，語氣鼓勵但誠實。請依規準為以下開放題作答評分。\n"
        + rub + "\n\n" + "\n\n".join(blocks) +
        '\n\n只輸出 JSON（無多餘文字、無程式碼圍欄）：'
        '{"score":<0到100整數,整份總評分>,"feedback":"<給學生的兩三句中文回饋>",'
        '"perItem":[{"qid":"..","score":<0到100>,"feedback":"<一句>"}]}'
    )
    r = grade_call(prompt)
    if not r.get("ok"):
        return {"ok": False, "error": r.get("error", "AI 呼叫失敗")}
    m = re.search(r'\{.*\}', r.get("text", ""), re.S)
    if not m:
        return {"ok": False, "error": "AI 未回傳 JSON：" + r.get("text", "")[:200]}
    try:
        d = json.loads(m.group(0))
        return {"ok": True, "score": d.get("score"), "feedback": d.get("feedback", ""),
                "perItem": d.get("perItem", [])}
    except Exception as e:
        return {"ok": False, "error": f"JSON 解析失敗：{e}"}


def grade_submission(payload):
    """評一份繳交。客觀題有 answerKey 直接核對；其餘開放題交 AI（有 rubric 更準）。"""
    answers = payload.get("answers") or {}
    answer_key = payload.get("answerKey") or {}
    rubric = payload.get("rubric")
    questions = payload.get("questions") or []
    per_item, auto_ok, auto_total = [], 0, 0
    for qid, correct in answer_key.items():
        got = answers.get(qid)
        ok = _norm(got) == _norm(correct)
        auto_total += 1
        auto_ok += 1 if ok else 0
        per_item.append({"qid": qid, "type": "objective", "correct": ok,
                         "expected": correct, "got": got})
    auto_score = round(auto_ok / auto_total * 100) if auto_total else None
    open_items = {q: v for q, v in answers.items() if q not in answer_key}
    ai_score, ai_feedback = None, ""
    if open_items:
        ai = _ai_grade(open_items, rubric, questions)
        if ai.get("ok"):
            ai_score = ai.get("score")
            ai_feedback = ai.get("feedback", "")
            for it in (ai.get("perItem") or []):
                it["type"] = "open"
                per_item.append(it)
        else:
            ai_feedback = "AI 評分失敗：" + ai.get("error", "")
    return {"ok": True, "autoScore": auto_score, "aiScore": ai_score,
            "aiFeedback": ai_feedback, "perItem": per_item,
            "autoCorrect": auto_ok, "autoTotal": auto_total}


def _scratch_inventory(project):
    """從 Scratch3 project.json 盤點：精靈、積木、變數、以及用到哪些概念。"""
    targets = project.get("targets", []) or []
    sprites = [t for t in targets if not t.get("isStage")]
    all_blocks = {}
    for t in targets:
        for bid, b in (t.get("blocks") or {}).items():
            if isinstance(b, dict):
                all_blocks[bid] = b
    opcodes = {}
    for b in all_blocks.values():
        op = b.get("opcode")
        if op:
            opcodes[op] = opcodes.get(op, 0) + 1
    nvars = sum(len(t.get("variables") or {}) for t in targets)
    nlists = sum(len(t.get("lists") or {}) for t in targets)

    def has(*names):
        return any(opcodes.get(n) for n in names)

    def any_prefix(pfx):
        return any(op.startswith(pfx) for op in opcodes)

    concepts = {
        "事件(綠旗/按鍵/點擊)": has("event_whenflagclicked", "event_whenkeypressed", "event_whenthisspriteclicked"),
        "動作(移動/座標)": any_prefix("motion_"),
        "外觀(造型/說話)": any_prefix("looks_"),
        "聲音": any_prefix("sound_"),
        "迴圈(重複)": has("control_repeat", "control_forever", "control_repeat_until"),
        "條件(如果)": has("control_if", "control_if_else"),
        "變數": nvars > 0 or has("data_setvariableto", "data_changevariableby"),
        "清單": nlists > 0,
        "廣播": has("event_broadcast", "event_broadcastandwait", "event_whenbroadcastreceived"),
        "偵測(碰到/鍵盤)": any_prefix("sensing_"),
        "運算": any_prefix("operator_"),
        "隨機": has("operator_random"),
        "分身(clone)": has("control_create_clone_of", "control_start_as_clone"),
        "自訂積木": any_prefix("procedures_"),
    }
    top = sorted(opcodes.items(), key=lambda x: -x[1])[:15]
    return {
        "sprites": len(sprites), "spriteNames": [s.get("name") for s in sprites][:30],
        "blocks": len(all_blocks), "variables": nvars, "lists": nlists,
        "opcodeCount": len(opcodes),
        "topOpcodes": [{"opcode": k, "count": v} for k, v in top],
        "concepts": concepts,
    }


def grade_scratch(b64, rubric=None, questions=None):
    """解析上傳的 .sb3（Scratch3 專案 zip）→ 盤點。評分邏輯（rubric/AI）後續接。"""
    try:
        raw = base64.b64decode(b64 or "")
        z = zipfile.ZipFile(io.BytesIO(raw))
        pj = json.loads(z.read("project.json").decode("utf-8", "replace"))
    except Exception as e:
        return {"ok": False, "error": "無法讀取 .sb3（需為 Scratch 3 專案檔）：" + str(e)}
    return {"ok": True, "inventory": _scratch_inventory(pj)}


def diagnostics():
    cfg = read_config()
    out = {}
    # AI
    out["ai"] = {"configured": bool(cfg.get("key")), "provider": cfg.get("provider", "")}
    # Google
    g = {"client": bool(cfg.get("google_client_id")), "authorized": bool((cfg.get("google_token") or {}).get("access_token"))}
    if g["authorized"]:
        c = google_courses()
        g["ok"] = c.get("ok", False)
        g["detail"] = (f"{len(c['courses'])} 門課程" if c.get("ok") else c.get("error", "")[:120])
    out["google"] = g
    # GitHub
    gh = {"configured": bool(cfg.get("github_token") and cfg.get("github_repo"))}
    if gh["configured"]:
        try:
            u = _http("https://api.github.com/user", "GET",
                      {"Authorization": "Bearer " + cfg["github_token"], "User-Agent": "beikeCockpit",
                       "Accept": "application/vnd.github+json"})
            gh["ok"] = True
            gh["detail"] = "登入為 " + u.get("login", "?")
        except Exception as e:
            gh["ok"] = False
            gh["detail"] = str(e)[:120]
    out["github"] = gh
    return {"ok": True, "diag": out}


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _serve_file(self, path: Path):
        if not path.exists() or not path.is_file():
            return self._send(404, {"error": "not found"})
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        try:
            if u.path == "/" or u.path == "/index.html":
                return self._serve_file(WEB / "index.html")
            if u.path == "/api/tree":
                return self._send(200, build_tree())
            if u.path == "/api/settings":
                c = read_config(); c = dict(c);
                return self._send(200, c)
            if u.path == "/api/file":
                rel = q.get("path", [""])[0]
                p = safe(rel)
                if not p.exists():
                    return self._send(200, {"ok": True, "content": "", "exists": False})
                return self._send(200, {"ok": True, "content": p.read_text("utf-8", "replace"), "exists": True})
            if u.path == "/api/guides":
                gs = sorted([f.name for f in GUIDE.glob("*.md")]) if GUIDE.exists() else []
                return self._send(200, {"files": gs})
            if u.path == "/api/pptx":
                return self._send(200, pptx_thumbs(q.get("path", [""])[0]))
            if u.path == "/api/reveal":
                return self._send(200, reveal(q.get("path", [""])[0]))
            if u.path == "/api/gemini-models":
                return self._send(200, gemini_models())
            if u.path == "/api/grade-models":
                return self._send(200, grade_models())
            if u.path == "/api/fetch-title":
                return self._send(200, fetch_title(q.get("url", [""])[0]))
            if u.path == "/api/search-test":
                return self._send(200, search_test())
            if u.path == "/oauth/callback":
                code = q.get("code", [""])[0]; err = q.get("error", [""])[0]
                if err:
                    return self._send(200, f"<h2>授權失敗：{err}</h2>", "text/html; charset=utf-8")
                try:
                    google_exchange(code)
                    return self._send(200, "<meta charset='utf-8'><h2>✓ Google 授權成功</h2><p>可關閉此分頁，回工作台按『連線診斷』確認。</p>", "text/html; charset=utf-8")
                except Exception as e:
                    return self._send(200, f"<meta charset='utf-8'><h2>換 token 失敗</h2><pre>{html.escape(str(e))}</pre>", "text/html; charset=utf-8")
            if u.path == "/api/google/auth-url":
                return self._send(200, google_auth_url())
            if u.path == "/api/google/courses":
                return self._send(200, google_courses())
            if u.path == "/api/classroom/coursework":
                return self._send(200, classroom_coursework(q.get("courseId", [""])[0]))
            if u.path == "/api/classroom/students":
                return self._send(200, classroom_students(q.get("courseId", [""])[0]))
            if u.path == "/api/diagnostics":
                return self._send(200, diagnostics())
            if u.path == "/api/update/check":
                return self._send(200, updater.check_update(ROOT))
            # 靜態：materials/、引導規範/、web/ 底下的檔（圖片、html…）
            rel = u.path.lstrip("/")
            if rel.startswith(("materials/", "引導規範/", "web/", "評分平台/")):
                return self._serve_file(safe(urllib.parse.unquote(rel)))
            return self._send(404, {"error": "no route"})
        except Exception as e:
            return self._send(500, {"error": str(e)})

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        ln = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(ln) if ln else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            data = {}
        try:
            if u.path == "/api/update/apply":
                return self._send(200, updater.apply_update(ROOT))
            if u.path == "/api/file":
                p = safe(data.get("path", ""))
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(data.get("content", ""), "utf-8")
                return self._send(200, {"ok": True})
            if u.path == "/api/settings":
                cfg = read_config()
                cfg.update(data)   # 合併，保留 google_token / github_token 等
                save_config(cfg)
                return self._send(200, {"ok": True})
            if u.path == "/api/drive-upload":
                return self._send(200, drive_upload(data.get("path", ""), data.get("name", "檔案")))
            if u.path == "/api/classroom-publish":
                return self._send(200, classroom_publish(
                    data.get("courseId", ""), data.get("type", "material"),
                    data.get("title", ""), data.get("text", ""),
                    data.get("driveId"), data.get("link")))
            if u.path == "/api/github-publish":
                return self._send(200, github_publish(data.get("path", ""), data.get("dest", "")))
            if u.path == "/api/git-publish":
                return self._send(200, git_publish(data.get("group", ""), data.get("folder", "")))
            if u.path == "/api/grade":
                return self._send(200, grade_submission(data))
            if u.path == "/api/grade-scratch":
                return self._send(200, grade_scratch(data.get("b64", ""), data.get("rubric"), data.get("questions")))
            if u.path == "/api/classroom/grades":
                return self._send(200, classroom_grades(data.get("courseId", ""), data.get("courseWorkId", ""), data.get("grades", [])))
            if u.path == "/api/google/logout":
                cfg = read_config(); cfg.pop("google_token", None); save_config(cfg)
                return self._send(200, {"ok": True})
            if u.path == "/api/layout":
                lay = read_ws_layout(); lay["collapsed"] = data.get("collapsed", {}); save_ws_layout(lay)
                return self._send(200, {"ok": True})
            if u.path == "/api/gemini":
                return self._send(200, gemini_call(data.get("prompt", "")))
            if u.path == "/api/package-lm":
                return self._send(200, package_lm(data.get("lesson", "")))
            if u.path == "/api/split":
                return self._send(200, split_plan(data.get("group", ""), data.get("plan", "")))
            if u.path == "/api/lesson-add":
                return self._send(200, lesson_add(data.get("group", ""), data.get("title", "")))
            if u.path == "/api/lesson-delete":
                return self._send(200, lesson_delete(data.get("group", ""), data.get("folder", "")))
            if u.path == "/api/arrange":
                return self._send(200, arrange(data.get("arr", {})))
            if u.path == "/api/crawl":
                return self._send(200, crawl_materials(data.get("group", ""), data.get("folder", "")))
            if u.path == "/api/material-search":
                return self._send(200, material_search(data.get("group", ""), data.get("folder", ""),
                                                       bool(data.get("force")), bool(data.get("eduFirst", True)),
                                                       bool(data.get("peek"))))
            if u.path == "/api/extract":
                raw = base64.b64decode(data.get("b64", ""))
                return self._send(200, extract_text(data.get("name", ""), raw))
            return self._send(404, {"error": "no route"})
        except Exception as e:
            return self._send(500, {"error": str(e)})


def main():
    WEB.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"備課駕駛艙 running → http://127.0.0.1:{PORT}")
    print(f"專案根目錄：{ROOT}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
