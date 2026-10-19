#!/usr/bin/env python3
"""把 chair-gate.js 內嵌進每份有「繳交學習單」按鈕(#submitBtn)的互動學習單 .html。

用法（在專案根目錄；這台電腦用 工作台/runtime/python/python.exe）：
    python 引導規範/chair-gate/inject.py            # 套用到 materials/ 底下所有符合的學習單
    python 引導規範/chair-gate/inject.py --check    # 只列出狀態，不改檔
    python 引導規範/chair-gate/inject.py 某檔.html   # 只處理指定檔案

idempotent：用 <!--CHAIR-GATE-START--> … <!--CHAIR-GATE-END--> 包住，已經有就整段換成最新版，沒有就插在 </body> 前。
符合條件＝檔案裡有 id="submitBtn" 且會寫 submissions（才是正式的繳交學習單）。
換行風格跟著原檔（學習單多半是 CRLF），不會整檔 diff。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent / "chair-gate.js"
START, END = "<!--CHAIR-GATE-START-->", "<!--CHAIR-GATE-END-->"
# 只認「標記 + <script>…</script> + 標記」的完整結構（JS 裡的 </script 已跳脫成 <\/script，第一個 </script> 就是結尾）
BLOCK_RE = re.compile(re.escape(START) + r"\r?\n<script>.*?</script>\r?\n" + re.escape(END), re.S)
LABEL = {"new": "新增", "update": "更新", "same": "已是最新"}


def block():
    with open(SRC, encoding="utf-8", newline="") as fh:
        js = fh.read().replace("\r\n", "\n").replace("</script", "<\\/script")
    return START + "\n<script>\n" + js + "</script>\n" + END


def targets(args):
    if args:
        return [Path(a).resolve() for a in args]
    return sorted((ROOT / "materials").rglob("*.html"))


def eligible(text):
    return 'id="submitBtn"' in text and "collection('submissions')" in text


def main():
    argv = sys.argv[1:]
    check_only = "--check" in argv
    files = targets([a for a in argv if not a.startswith("--")])
    base = block()
    n_new = n_upd = n_same = 0
    for p in files:
        with open(p, encoding="utf-8", newline="") as fh:   # newline="" 保留原本的換行
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
