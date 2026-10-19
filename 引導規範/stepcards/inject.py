#!/usr/bin/env python3
"""把 stepcards.css／stepcards.js 內嵌進有 data-sc 步驟卡的互動學習單 .html。

用法（在專案根目錄；這台電腦用 工作台/runtime/python/python.exe）：
    python 引導規範/stepcards/inject.py            # 套用到 materials/ 底下所有符合的學習單
    python 引導規範/stepcards/inject.py --check    # 只列出狀態，不改檔
    python 引導規範/stepcards/inject.py 某檔.html   # 只處理指定檔案

idempotent：用 <!--STEPCARDS-START--> … <!--STEPCARDS-END--> 包住，已經有就整段換成最新版，沒有就插在 </body> 前
（有靠椅子關卡的話，兩段互不影響）。符合條件＝檔案裡有 data-sc。換行風格跟著原檔。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
START, END = "<!--STEPCARDS-START-->", "<!--STEPCARDS-END-->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
LABEL = {"new": "新增", "update": "更新", "same": "已是最新"}


def block():
    def rd(n):
        with open(HERE / n, encoding="utf-8", newline="") as fh:
            return fh.read().replace("\r\n", "\n")
    js = rd("stepcards.js").replace("</script", "<\\/script")
    return START + "\n<style>\n" + rd("stepcards.css") + "</style>\n<script>\n" + js + "</script>\n" + END


def targets(args):
    if args:
        return [Path(a).resolve() for a in args]
    return sorted((ROOT / "materials").rglob("*.html"))


def eligible(text):
    return "data-sc" in text and "class=\"sc\"" in text


def main():
    argv = sys.argv[1:]
    check_only = "--check" in argv
    files = targets([a for a in argv if not a.startswith("--")])
    base = block()
    n_new = n_upd = n_same = 0
    for p in files:
        with open(p, encoding="utf-8", newline="") as fh:
            text = fh.read()
        if not eligible(text):
            continue
        nl = "\r\n" if "\r\n" in text else "\n"
        blk = base.replace("\n", nl)
        try:
            rel = p.relative_to(ROOT)
        except ValueError:
            rel = p
        if BLOCK_RE.search(text):
            updated = BLOCK_RE.sub(lambda m: blk, text, count=1)
            state = "same" if updated == text else "update"
        else:
            idx = text.rfind("</body>")
            if idx < 0:
                print("[略過] 沒有 </body>：%s" % rel)
                continue
            updated = text[:idx] + blk + nl + text[idx:]
            state = "new"
        print("[%s] %s" % (LABEL[state], rel))
        if state == "same":
            n_same += 1
            continue
        n_new += state == "new"
        n_upd += state == "update"
        if not check_only:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(updated)
    print("\n新增 %d、更新 %d、已是最新 %d%s" % (n_new, n_upd, n_same, "（--check：未寫檔）" if check_only else ""))


if __name__ == "__main__":
    main()
