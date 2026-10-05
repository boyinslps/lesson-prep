# -*- coding: utf-8 -*-
"""電腦急救站｜產生網站

用法（在專案根目錄）：
    工作台/runtime/python/python.exe 技能闖關/build.py

讀 設定.json＋levels/*/level.json，輸出到 site/：
    site/index.html          技能地圖
    site/{代碼}/index.html   每一關（levels/xx/assets/ 一起複製過去）
    site/cert/index.html     證書頁
新增關卡＝在 levels/ 新增一個「代碼_名稱」資料夾放 level.json，再跑一次這支。
"""
import io, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, '_原始碼')
OUT = os.path.join(ROOT, 'site')
REQUIRED = ['code', 'title', 'category', 'summary', 'learn', 'practice', 'challenge']


def rd(*p):
    return io.open(os.path.join(*p), encoding='utf-8').read()


def die(msg):
    print('[錯誤] ' + msg)
    sys.exit(1)


def load_levels(cfg):
    cats = [c['id'] for c in cfg['categories']]
    levels = []
    for name in sorted(os.listdir(os.path.join(ROOT, 'levels'))):
        d = os.path.join(ROOT, 'levels', name)
        f = os.path.join(d, 'level.json')
        if not os.path.isfile(f):
            continue
        try:
            lv = json.loads(rd(f))
        except ValueError as e:
            die('%s/level.json 格式錯誤：%s' % (name, e))
        if lv.get('enabled', True) is False:
            continue
        for k in REQUIRED:
            if k not in lv:
                die('%s 缺少欄位 %s' % (name, k))
        if not name.startswith(lv['code'] + '_'):
            die('%s：資料夾名稱要以「%s_」開頭' % (name, lv['code']))
        if lv['category'] not in cats:
            die('%s：類別 %s 不在 設定.json' % (name, lv['category']))
        lv['_dir'] = d
        lv.setdefault('prereq', [])
        lv.setdefault('core', False)
        lv.setdefault('order', 99)
        levels.append(lv)
    codes = [l['code'] for l in levels]
    dup = set(c for c in codes if codes.count(c) > 1)
    if dup:
        die('關卡代碼重複：' + '、'.join(sorted(dup)))
    by = {l['code']: l for l in levels}
    for l in levels:
        for p in l['prereq']:
            if p not in by:
                die('%s 的先修 %s 不存在（或被停用）' % (l['code'], p))
    # 先修不能繞成一圈
    state = {}

    def visit(c, path):
        if state.get(c) == 1:
            die('先修關係繞成一圈：' + ' → '.join(path + [c]))
        if state.get(c) == 2:
            return
        state[c] = 1
        for p in by[c]['prereq']:
            visit(p, path + [c])
        state[c] = 2
    for c in codes:
        visit(c, [])
    levels.sort(key=lambda l: (cats.index(l['category']), l['order'], l['code']))
    return levels


def js(o):
    return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')


def page(title, body, site, cfg, css, sprite, scripts, color=None):
    return u'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="author" content="資訊老師黃博胤">
<meta name="description" content="{desc}">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
{sprite}
<script>window.SITE={site};</script>
<script>
{scripts}
</script>
{body}
<div class="toast" id="toast"></div>
<footer><div class="wrap"><span>{name}｜學生電腦技能闖關</span><span class="sign">made by 資訊老師黃博胤</span></div></footer>
</body>
</html>
'''.format(desc=cfg['tagline'], title=title, css=css, sprite=sprite, site=js(site), scripts=scripts, body=body, name=cfg['siteTitle'])


def main():
    cfg = json.loads(rd(ROOT, '設定.json'))
    levels = load_levels(cfg)
    css, sprite = rd(SRC, 'common.css'), rd(SRC, 'sprite.svg')
    app, checkers = rd(SRC, 'app.js'), rd(SRC, 'checkers.js')
    summary = [{k: l[k] for k in ('code', 'title', 'category', 'core', 'prereq', 'summary')} for l in levels]
    base = {'config': cfg, 'levels': summary}

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    def write(rel, html):
        p = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        io.open(p, 'w', encoding='utf-8', newline='\n').write(html)

    body = rd(SRC, 'map.html').replace('{{SITE_TITLE}}', cfg['siteTitle']).replace('{{TAGLINE}}', cfg['tagline'])
    write('index.html', page(cfg['siteTitle'], body, base, cfg, css, sprite, app))

    body = rd(SRC, 'cert.html')
    write(os.path.join('cert', 'index.html'), page('我的證書｜' + cfg['siteTitle'], body, base, cfg, css, sprite, app))

    body = rd(SRC, 'admin.html')
    write(os.path.join('admin', 'index.html'), page('教師後台｜' + cfg['siteTitle'], body, base, cfg, css, sprite, app))

    body = rd(SRC, 'tab.html')
    write(os.path.join('tab', 'index.html'), page('密碼小卡｜' + cfg['siteTitle'], body, base, cfg, css, sprite, app))

    cats = {c['id']: c for c in cfg['categories']}
    tpl = rd(SRC, 'level.html')
    for l in levels:
        full = {k: v for k, v in l.items() if not k.startswith('_') and k != 'production'}
        site = dict(base, level=full)
        cat = cats[l['category']]
        body = (tpl.replace('{{CODE}}', l['code']).replace('{{TITLE}}', l['title'])
                .replace('{{SUMMARY}}', l['summary']).replace('{{COLOR}}', cat['color']).replace('{{SOFT}}', cat['soft']))
        write(os.path.join(l['code'], 'index.html'),
              page('%s %s｜%s' % (l['code'], l['title'], cfg['siteTitle']), body, site, cfg, css, sprite, app + '\n' + checkers))
        a = os.path.join(l['_dir'], 'assets')
        if os.path.isdir(a):
            shutil.copytree(a, os.path.join(OUT, l['code'], 'assets'))

    print('完成：%d 關 → %s' % (len(levels), OUT))
    for l in levels:
        v = (l.get('production') or {}).get('video', '')
        print('  %-4s %-10s 先修:%-8s 影片:%s' % (l['code'], l['title'], ','.join(l['prereq']) or '-', v or '-'))


if __name__ == '__main__':
    main()
