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
exec(_slice('DEMOS = [', "STEP4 = '''"), _ns)      # DEMOS、demo_card、STEP1（看示範）、STEP2（跟 AI 聊天）、_KINDS、STEP3（題目範圍＝三種類型）
exec(_slice('CFG = {', "HOOKS = r'''"), _ns)       # 只為了拿 CFG['choices']（demo、tip1、tip2 的選項與正解）

STEP_VIDEOS = _ns['STEP1']
STEP_TIPS = _ns['STEP2']
STEP_KINDS = _ns['STEP3']
CHOICES = {k: _ns['CFG']['choices'][k] for k in ('demo', 'tip1', 'tip2')}

# L08 用的小改：第 2 步的開場句從「找題目」改成「寫台詞」
_a = '等一下找題目，可以請 AI 幫忙。先看這 4 個提醒，再做兩題。'
assert STEP_TIPS.count(_a) == 1
STEP_TIPS = STEP_TIPS.replace(_a, '等一下寫台詞，可以請 AI 教練幫忙。先看這 4 個提醒，再做兩題。')
# L07 的「怎麼在 Classroom 打開 Gem」影片檔放在 L07/assets；L08 沒有，真的要放時再處理，不要悄悄產生壞連結
assert 'assets/教學_開啟Gem' not in STEP_TIPS, 'L07 已放入 Gem 操作影片：L08 的路徑要另外處理（assets 在 L07 資料夾）'
assert 'data-step="1"' in STEP_VIDEOS and 'data-step="2"' in STEP_TIPS

# 三種類型下面加「選主題三個欄位怎麼填」（老師 2026-11-20 給的重點，改成國小生的說法）
_EXPLAIN = '''
    <div class="bg-white border-4 border-emerald-300 rounded-3xl p-6 mb-5 shadow-sm">
      <h3 class="cute text-2xl font-extrabold text-emerald-700 m-0">選主題要填三格，怎麼填？</h3>
      <div class="grid lg:grid-cols-3 gap-4 mt-4">
        <div class="bg-rose-50 border-2 border-rose-200 rounded-2xl p-4">
          <p class="cute text-xl font-extrabold text-rose-700 m-0">① 開頭句</p>
          <p class="text-lg text-slate-700 mt-2"><b>是什麼：</b>影片的第一句話。</p>
          <p class="text-lg text-slate-700 mt-1"><b>為什麼要有：</b>前 3 秒決定別人要不要看下去。沒有好的開頭，大家就滑走了。</p>
          <p class="text-lg text-slate-700 mt-1"><b>怎麼吸引人：</b></p>
          <ul class="list-disc pl-6 text-lg text-slate-700"><li><b>保持神秘</b>：話只說一半，讓人想知道答案。</li><li><b>提供震撼的事實</b>：說一件大家想不到的事。</li></ul>
        </div>
        <div class="bg-sky-50 border-2 border-sky-200 rounded-2xl p-4">
          <p class="cute text-xl font-extrabold text-sky-700 m-0">② 參考資料</p>
          <p class="text-lg text-slate-700 mt-2"><b>不能拿 AI 的網站當參考資料</b>，因為 AI 也會說錯。</p>
          <p class="text-lg text-slate-700 mt-1">要自己用<b>關鍵字</b>上網查，找<b>可以信任的網站</b>（查核機構、政府、學校、新聞媒體），把網址貼上來。</p>
          <p class="text-lg text-slate-700 mt-1">貼之前，點開來看：網頁上真的有寫嗎？</p>
        </div>
        <div class="bg-emerald-50 border-2 border-emerald-200 rounded-2xl p-4">
          <p class="cute text-xl font-extrabold text-emerald-700 m-0">③ 核心訊息</p>
          <p class="text-lg text-slate-700 mt-2"><b>是什麼：</b>影片最想讓大家知道的事，也就是整支影片的結論，還要<b>回應開頭句</b>。</p>
          <ul class="list-disc pl-6 text-lg text-slate-700 mt-1"><li>開頭句是<b>問句</b>：就要<b>回答</b>它。</li><li>開頭句是<b>事實</b>：要<b>補充說明</b>，再說出結論。</li></ul>
        </div>
      </div>
    </div>
'''
assert STEP_KINDS.count('    <div class="stepnav"></div>') == 1
STEP_KINDS = STEP_KINDS.replace('    <div class="stepnav"></div>', _EXPLAIN + '    <div class="stepnav"></div>')
