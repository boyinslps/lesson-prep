# -*- coding: utf-8 -*-
"""
驗證「課程進度彙整 JSON」是否符合《引導規範/課程進度與甘特圖規範.md》。純標準庫、唯讀、不連網。

用法（專案根目錄；Windows 用可攜式 Python）：
    工作台\\runtime\\python\\python.exe 課程進度\\驗證進度彙整.py            ← 先驗 進度彙整.json，沒有就驗範例
    工作台\\runtime\\python\\python.exe 課程進度\\驗證進度彙整.py 某檔.json   ← 驗指定檔案

結束碼：0＝沒有錯誤（可能有警告）、1＝有錯誤。
重點檢查：欄位白名單（多出來的欄位＝疑似夾帶個資）、狀態與繳交比例是否一致、日期格式與先後、
          節次對照、個資關鍵字。這支只「檢查」，不產生資料——彙整由本機另一個 Claude Code session 做。
"""
import json, re, sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATUSES = {"done", "partial", "in_progress", "not_started", "skipped"}
KEYS = {
    "top": {"schema", "generatedAt", "term", "courses", "classes", "mappingNotes", "notes"},
    "term": {"name", "start", "end", "weeks"},
    "course": {"id", "gradeLabel", "title", "lessons"},
    "plan": {"code", "name", "plannedWeek", "periods"},
    "class": {"id", "grade", "course", "students", "current", "lessons"},
    "rec": {"code", "status", "firstDate", "lastDate", "submitted", "total", "source", "note"},
    "map": {"assignment", "lesson", "needsConfirm"},
}
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
RE_CODE = re.compile(r"^L\d{2}$")
PII_WORDS = re.compile(r"座號|學號|姓名|e-?mail|@|身分證", re.I)
PII_DIGITS = re.compile(r"\d{7,}")

errors, warns = [], []
def err(path, msg): errors.append(f"{path}: {msg}")
def warn(path, msg): warns.append(f"{path}: {msg}")


def parse_date(s):
    if not isinstance(s, str) or not RE_DATE.match(s):
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def derive_status(sub, total):
    """完成度門檻（整數運算，避免浮點誤差）：≥80% done、30–79% partial、<30% in_progress、0 人 not_started。"""
    if sub <= 0 or total <= 0:
        return "not_started"
    if sub * 10 >= total * 8:
        return "done"
    if sub * 10 >= total * 3:
        return "partial"
    return "in_progress"


def check_keys(obj, kind, path):
    if not isinstance(obj, dict):
        err(path, "必須是物件")
        return False
    extra = set(obj) - KEYS[kind]
    if extra:
        err(path, f"多出規格以外的欄位 {sorted(extra)}（班級層級資料不可夾帶其他欄位，疑似個資就更不行）")
    return True


def scan_strings(o, path):
    if isinstance(o, str):
        if PII_WORDS.search(o):
            err(path, f"字串含疑似個資字眼（座號／學號／姓名／email）：{o[:40]!r}")
        elif PII_DIGITS.search(o):
            warn(path, f"字串含 7 位以上數字，確認不是學號或帳號：{o[:40]!r}")
        if len(o) > 200:
            warn(path, "字串超過 200 字，note 請精簡")
    elif isinstance(o, dict):
        for k, v in o.items():
            scan_strings(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            scan_strings(v, f"{path}[{i}]")


def validate(d):
    if not check_keys(d, "top", "$"):
        return
    scan_strings(d, "$")
    if d.get("schema") != 1:
        err("$.schema", f"必須是 1，目前是 {d.get('schema')!r}")
    gen = d.get("generatedAt")
    gdate = None
    if not (isinstance(gen, str) and re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$", gen)):
        err("$.generatedAt", "必須是帶時區的 ISO 8601，例：2026-11-04T16:00:00+08:00")
    else:
        gdate = parse_date(gen[:10])

    # ── term ──
    T = d.get("term")
    start = end = None
    weeks = 0
    if check_keys(T, "term", "$.term"):
        start, end = parse_date(T.get("start")), parse_date(T.get("end"))
        weeks = T.get("weeks")
        if not start: err("$.term.start", "必須是 YYYY-MM-DD")
        if not end: err("$.term.end", "必須是 YYYY-MM-DD")
        if not (isinstance(weeks, int) and weeks >= 1): err("$.term.weeks", "必須是正整數")
        if start and start.weekday() != 0: warn("$.term.start", "不是星期一；甘特圖以 start 為第 1 週起點，每週 7 天往後排")
        if start and end and isinstance(weeks, int) and weeks != -(-((end - start).days + 1) // 7):
            warn("$.term.weeks", f"與 start～end 算出的週數（{-(-((end - start).days + 1) // 7)}）不同")
    if not isinstance(T, dict) or not isinstance(weeks, int): weeks = 0

    # ── courses ──
    courses, plan = {}, {}
    if not isinstance(d.get("courses"), list) or not d["courses"]:
        err("$.courses", "必須是非空陣列")
    else:
        for ci, c in enumerate(d["courses"]):
            p = f"$.courses[{ci}]"
            if not check_keys(c, "course", p): continue
            if c.get("id") in courses: err(p + ".id", f"重複：{c.get('id')}")
            courses[c.get("id")] = c
            plan[c.get("id")] = {}
            for li, l in enumerate(c.get("lessons") or []):
                lp = f"{p}.lessons[{li}]"
                if not check_keys(l, "plan", lp): continue
                if not RE_CODE.match(str(l.get("code"))): err(lp + ".code", "格式必須是 L 加兩位數字，例 L07")
                if l.get("code") in plan[c.get("id")]: err(lp + ".code", f"同一課程內重複：{l.get('code')}")
                plan[c.get("id")][l.get("code")] = l
                pw, per = l.get("plannedWeek"), l.get("periods")
                if not (isinstance(pw, int) and pw >= 1): err(lp + ".plannedWeek", "必須是 ≥1 的整數")
                elif weeks and pw > weeks: err(lp + ".plannedWeek", f"{pw} 超過學期週數 {weeks}")
                if not (isinstance(per, int) and per >= 1): err(lp + ".periods", "必須是 ≥1 的整數")
                elif isinstance(pw, int) and weeks and pw + per - 1 > weeks: warn(lp, f"計畫週 {pw} 起 {per} 節，超出學期最後一週")

    # ── classes ──
    ids = set()
    if not isinstance(d.get("classes"), list) or not d["classes"]:
        err("$.classes", "必須是非空陣列")
    else:
        for i, c in enumerate(d["classes"]):
            p = f"$.classes[{i}]"
            if not check_keys(c, "class", p): continue
            cid = c.get("id")
            if not (isinstance(cid, str) and re.match(r"^\d{3}$", cid)): err(p + ".id", f"必須是 3 位數字字串（年級＋兩位班號，例 407），目前 {cid!r}")
            if cid in ids: err(p + ".id", f"重複：{cid}")
            ids.add(cid)
            g = c.get("grade")
            if g not in (4, 5, 6): err(p + ".grade", f"必須是 4／5／6，目前 {g!r}")
            elif isinstance(cid, str) and cid[:1] != str(g): warn(p + ".id", f"班級 id {cid} 與 grade {g} 不一致")
            cs = c.get("course")
            if cs not in courses: err(p + ".course", f"{cs!r} 不在 courses 裡")
            elif g in (4,) and cs != "g4" or g in (5, 6) and cs != "g5": warn(p + ".course", f"{g} 年級通常對應 {'g4' if g == 4 else 'g5'}（六年級也填 g5）")
            st = c.get("students")
            if not (isinstance(st, int) and st > 0): err(p + ".students", "必須是正整數（人數，不是名單）")
            cur = c.get("current")
            if cur is not None and cs in plan and cur not in plan[cs]: err(p + ".current", f"{cur!r} 不在課程 {cs} 的節次裡")
            seen, ranges = set(), []
            for j, r in enumerate(c.get("lessons") or []):
                rp = f"{p}.lessons[{j}]"
                if not check_keys(r, "rec", rp): continue
                code, s = r.get("code"), r.get("status")
                if code in seen: err(rp + ".code", f"同一班重複：{code}")
                seen.add(code)
                if cs in plan and code not in plan[cs]: err(rp + ".code", f"{code!r} 不在課程 {cs} 的節次裡")
                if s not in STATUSES: err(rp + ".status", f"必須是 {sorted(STATUSES)} 其中之一，目前 {s!r}"); continue
                sub, tot = r.get("submitted"), r.get("total")
                if not (isinstance(sub, int) and isinstance(tot, int) and sub >= 0 and tot >= 0):
                    err(rp, "submitted、total 必須是 ≥0 的整數"); continue
                if sub > tot: err(rp, f"submitted {sub} 大於 total {tot}")
                if s != "skipped" and derive_status(sub, tot) != s:
                    err(rp + ".status", f"{sub}/{tot}＝{sub * 100 / tot if tot else 0:.1f}% 應為 {derive_status(sub, tot)}，不是 {s}"
                        "（門檻：done≥80%、partial 30–79%、in_progress<30%、0 人＝not_started）")
                a, b = parse_date(r.get("firstDate")), parse_date(r.get("lastDate"))
                for k in ("firstDate", "lastDate"):
                    if r.get(k) is not None and parse_date(r.get(k)) is None: err(rp + "." + k, f"必須是 YYYY-MM-DD 或 null，目前 {r.get(k)!r}")
                if s in ("done", "partial", "in_progress") and not (a and b): err(rp, f"{s} 必須有 firstDate 與 lastDate")
                if s in ("not_started", "skipped") and (a or b): warn(rp, f"{s} 通常沒有日期，條狀會依前後節的空檔示意")
                if a and b:
                    if a > b: err(rp, "firstDate 晚於 lastDate")
                    if start and a < start - timedelta(days=7): warn(rp, "日期早於學期開始")
                    if end and b > end + timedelta(days=7): warn(rp, "日期晚於學期結束")
                    if gdate and b > gdate + timedelta(days=1): err(rp + ".lastDate", "晚於資料產生日，未來的日期不可能有繳交")
                    ranges.append((code, a, b))
                if not isinstance(r.get("source"), str) or not r.get("source"): warn(rp + ".source", "建議填來源（classroom／firestore／both／manual／none）")
                if not isinstance(r.get("note", ""), str): err(rp + ".note", "必須是字串")
            ranges.sort(key=lambda x: x[0])
            for (c1, a1, b1), (c2, a2, b2) in zip(ranges, ranges[1:]):
                if a2 <= b1: warn(p, f"{c1}（至 {b1}）與 {c2}（自 {a2}）日期重疊；遲交不要把 lastDate 拉進下一節的期間，否則甘特圖的條會疊在一起")

    # ── mappingNotes ──
    allcodes = {code for pl in plan.values() for code in pl}
    for i, m in enumerate(d.get("mappingNotes") or []):
        p = f"$.mappingNotes[{i}]"
        if not check_keys(m, "map", p): continue
        if not isinstance(m.get("assignment"), str) or not m.get("assignment"): err(p + ".assignment", "必須是作業標題字串")
        if not isinstance(m.get("needsConfirm"), bool): err(p + ".needsConfirm", "必須是 true／false")
        if m.get("lesson") is None:
            if m.get("needsConfirm") is not True: err(p, "lesson 為 null（無法判斷節次）時 needsConfirm 必須是 true")
        elif m.get("lesson") not in allcodes: err(p + ".lesson", f"{m.get('lesson')!r} 不在任何課程的節次裡")
    if not isinstance(d.get("notes", []), list) or any(not isinstance(n, str) for n in d.get("notes", [])):
        err("$.notes", "必須是字串陣列")


def main():
    if len(sys.argv) > 1:
        f = Path(sys.argv[1])
    else:
        f = HERE / "進度彙整.json"
        if not f.is_file():
            f = HERE / "範例進度彙整.json"
            print("（找不到 進度彙整.json，改驗範例）")
    try:
        sys.stdout.reconfigure(errors="replace")      # Windows 主控台編碼不支援時不要當掉
    except Exception:
        pass
    print("檢查：", f)
    try:
        d = json.loads(f.read_text("utf-8-sig"))
    except (OSError, ValueError) as e:
        print("錯誤：讀取或解析失敗：", e)
        return 1
    validate(d)
    for w in warns: print("警告 ", w)
    for e in errors: print("錯誤 ", e)
    n = sum(len(c.get("lessons") or []) for c in d.get("classes", []) if isinstance(c, dict)) if isinstance(d, dict) else 0
    print(f"\n{'通過' if not errors else '未通過'}：{len(errors)} 個錯誤、{len(warns)} 個警告"
          + (f"（{len(d.get('classes', []))} 個班、{n} 筆節次紀錄）" if isinstance(d, dict) else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
