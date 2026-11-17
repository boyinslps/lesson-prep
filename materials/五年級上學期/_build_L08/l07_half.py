# -*- coding: utf-8 -*-
# 把 L07 的「看示範」「跟 AI 聊天」兩步原樣借給 L08（老師 2026-11-17：L08 也要有 L07 後半的看示範、和 AI 對話）。
# 直接從 build_L07.py 的原始碼切出來執行，L07 改了，L08 重建就跟著改，不用兩邊各維護一份。
import io, os, re

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)                     # materials/五年級上學期
_src = io.open(os.path.join(_ROOT, '_build_L07', 'build_L07.py'), encoding='utf8').read().replace('\r\n', '\n')


def _slice(a, b):
    i = _src.index(a)
    j = _src.index(b, i)
    return _src[i:j]


_ns = {'os': os, 're': re, 'ROOT': _ROOT}
exec(_slice('DEMOS = [', '_KINDS = ['), _ns)       # DEMOS、demo_card、STEP1（看示範）、_TIPS、STEP2（跟 AI 聊天）
exec(_slice('CFG = {', "HOOKS = r'''"), _ns)       # 只為了拿 CFG['choices']（demo、tip1、tip2 的選項與正解）

STEP_VIDEOS = _ns['STEP1']
STEP_TIPS = _ns['STEP2']
CHOICES = {k: _ns['CFG']['choices'][k] for k in ('demo', 'tip1', 'tip2')}

# L08 用的小改：第 2 步的開場句從「找題目」改成「寫台詞」
_a = '等一下找題目，可以請 AI 幫忙。先看這 4 個提醒，再做兩題。'
assert STEP_TIPS.count(_a) == 1
STEP_TIPS = STEP_TIPS.replace(_a, '等一下寫台詞，可以請 AI 教練幫忙。先看這 4 個提醒，再做兩題。')
# L07 的「怎麼在 Classroom 打開 Gem」影片檔放在 L07/assets；L08 沒有，真的要放時再處理，不要悄悄產生壞連結
assert 'assets/教學_開啟Gem' not in STEP_TIPS, 'L07 已放入 Gem 操作影片：L08 的路徑要另外處理（assets 在 L07 資料夾）'
assert 'data-step="1"' in STEP_VIDEOS and 'data-step="2"' in STEP_TIPS
