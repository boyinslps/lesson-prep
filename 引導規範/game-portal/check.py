#!/usr/bin/env python3
"""檢查所有學習單的「更多遊戲」是不是連到老師自架的遊戲入口網。

用法（在專案根目錄；這台電腦用 工作台/runtime/python/python.exe）：
    python 引導規範/game-portal/check.py            # 掃 materials/ 底下所有 .html
    python 引導規範/game-portal/check.py 某檔.html   # 只掃指定檔案

規則見《學習單資料與提交規範》§3-b：
  - 「更多遊戲」按鈕的 href 必須是 PORTAL。
  - 不得留有 gemini.google.com/share/ 之類的分享連結（錯誤）。
  - 有完成獎勵區（rewardBox）卻沒有「更多遊戲」只列警告（有些專題頁刻意不放）。
有錯誤就回傳 1。
"""
import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[2]
PORTAL = "https://boyinslps.github.io/pcclass/games/"
SKIP = ("_影片原檔", "node_modules", ".git", ".pub_repo")
ANCHOR = re.compile(r'<a\b[^>]*?href="([^"]+)"[^>]*>(?:(?!</a>).)*?更多遊戲(?:(?!</a>).)*?</a>', re.S)


def targets(args):
    if args:
        return [Path(a).resolve() for a in args]
    return sorted(p for p in (ROOT / "materials").rglob("*.html")
                  if not any(s in p.parts for s in SKIP))


def main():
    errors, warns, ok = [], [], 0
    for f in targets(sys.argv[1:]):
        t = f.read_text(encoding="utf-8", errors="replace")
        rel = f.relative_to(ROOT) if ROOT in f.parents else f
        bad = False
        if "gemini.google.com/share/" in t:
            errors.append(f"{rel}：還留著 Gemini 分享連結")
            bad = True
        hrefs = ANCHOR.findall(t)
        for h in hrefs:
            if h != PORTAL:
                errors.append(f"{rel}：「更多遊戲」連到 {h}（應為 {PORTAL}）")
                bad = True
        if not hrefs and "rewardBox" in t:
            warns.append(f"{rel}：有完成獎勵區，但沒有「更多遊戲」按鈕")
        if hrefs and not bad:
            ok += 1
    for w in warns:
        print("警告", w)
    for e in errors:
        print("錯誤", e)
    print(f"\n正確 {ok} 份；錯誤 {len(errors)} 項；警告 {len(warns)} 項")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
