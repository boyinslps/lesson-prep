# -*- coding: utf-8 -*-
# 產生「查證作答」T02：L01 式的多則訊息選真假、最後送出。
# 生成後請執行 引導規範/chair-gate/inject.py 內嵌「靠椅子」關卡。
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
L01 = os.path.join(HERE, '..', '五年級上學期', 'L01_假消息與目的辨識', '五上_L01_假消息與目的辨識.html')
src = io.open(L01, encoding='utf8').read()
FB_PUMPKIN = re.search(r"var FB_PUMPKIN='([^']+)'", src).group(1)
FB_HONEY = re.search(r"var FB_HONEY='([^']+)'", src).group(1)

TEMPLATE = io.open(os.path.join(HERE, '_T02_template.html'), encoding='utf8').read()
html = TEMPLATE.replace('@@FB_PUMPKIN@@', FB_PUMPKIN).replace('@@FB_HONEY@@', FB_HONEY)
out = os.path.join(HERE, 'T02_查證作答', '五上_T02_查證作答.html')
io.open(out, 'w', encoding='utf8', newline='\n').write(html)
print('wrote', out, len(html) // 1024, 'KB')
