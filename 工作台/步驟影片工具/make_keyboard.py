# 產生鍵盤示意圖 keyboard.html（1280x720），標出 Backspace／Delete 的位置；按鍵座標另存 shots/keyboard_pos.json 給影片 spec 用
import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
u, gap, h, step = 52, 6, 52, 58
x0, y0 = 48, 190
keys = []; pos = {}

def kw(w):
    return u if w == 1 else round(w * u + (round(w) - 1) * gap)

def row(y, items):
    x = x0
    for lab, w in items:
        wp = kw(w)
        keys.append((lab, x, y, wp, h)); pos.setdefault(lab.strip() or 'Space', (x, y, wp, h)); x += wp + gap
    return x

BS = chr(92)
rows = [
    [(c, 1) for c in ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=']] + [('Backspace', 2)],
    [('Tab', 1.5)] + [(c, 1) for c in 'QWERTYUIOP[]'] + [(BS, 1.5)],
    [('Caps', 1.75)] + [(c, 1) for c in "ASDFGHJKL;'"] + [('Enter', 2.25)],
    [('Shift', 2.25)] + [(c, 1) for c in 'ZXCVBNM,./'] + [('Shift ', 2.75)],
    [('Ctrl', 1.5), ('Win', 1.25), ('Alt', 1.25), (' ', 6.5), ('Alt ', 1.25), ('Ctrl ', 1.5)],
]
ends = [row(y0 + i * step, r) for i, r in enumerate(rows)]
nx = max(ends) + 30
for lab, cx, cy in [('Insert', 0, 0), ('Home', 1, 0), ('PgUp', 2, 0), ('Delete', 0, 1), ('End', 1, 1), ('PgDn', 2, 1),
                    ('↑', 1, 3), ('←', 0, 4), ('↓', 1, 4), ('→', 2, 4)]:
    x = nx + cx * (u + gap); y = y0 + cy * step
    keys.append((lab, x, y, u, h)); pos[lab] = (x, y, u, h)

hl = {'Backspace': '#ef4444', 'Delete': '#2563eb'}
out = ['<!DOCTYPE html><html><head><meta charset="UTF-8"><style>'
       'body{margin:0;width:1280px;height:720px;background:#f1f5f9;font-family:Arial,"Microsoft JhengHei",sans-serif;position:relative;overflow:hidden}'
       '.k{position:absolute;background:#fff;border:2px solid #cbd5e1;border-bottom-width:5px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:16px;color:#334155;font-weight:bold}'
       '.h{color:#fff}.t{position:absolute;left:0;right:0;top:50px;text-align:center;font-size:44px;font-weight:bold;color:#1e1b4b}'
       '.lab{position:absolute;font-size:30px;font-weight:bold}</style></head><body><div class="t">鍵盤上的位置</div>']
for lab, x, y, w, hh in keys:
    c = hl.get(lab)
    st = 'left:%dpx;top:%dpx;width:%dpx;height:%dpx' % (x, y, w, hh) + (';background:%s;border-color:%s;font-size:18px' % (c, c) if c else '')
    out.append('<div class="k%s" style="%s">%s</div>' % (' h' if c else '', st, lab.replace('<', '&lt;')))
bx, by, bw, bh = pos['Backspace']; dx, dy, dw, dh = pos['Delete']
out.append('<div class="lab" style="left:%dpx;top:%dpx;color:#ef4444">Backspace：刪「前面」</div>' % (bx - 150, by - 80))
out.append('<div class="lab" style="left:%dpx;top:%dpx;color:#2563eb">Delete：刪「後面」</div>' % (dx - 60, y0 + 5 * step + 10))
out.append('<div style="position:absolute;right:16px;bottom:10px;font-size:15px;color:#94a3b8">筆電的 Delete 常在右上角（Del）</div></body></html>')
open('keyboard.html', 'w', encoding='utf-8').write(''.join(out))
json.dump({k: pos[k] for k in ['Backspace', 'Delete', 'Ctrl', 'Shift', 'V']}, open('shots/keyboard_pos.json', 'w'))
print({k: pos[k] for k in ['Backspace', 'Delete']})
