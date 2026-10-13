# -*- coding: utf-8 -*-
# 把老師下載的原始影片（放在 L05_Docs查證文件一/_影片原檔/）壓成網頁版，放進 assets/，並抽一張封面。
# 規格依「影片一律壓畫質」：短邊≤480、crf 31、preload=none＋封面。
# 用法：工作台/runtime/python/python.exe -I _build_L05_L06/compress_videos.py   （做完再跑 build.py）
import glob, io, os, subprocess, sys
sys.stdout.reconfigure(encoding='utf8')
HERE = os.path.dirname(os.path.abspath(__file__))
L05 = os.path.join(os.path.dirname(HERE), 'L05_Docs查證文件一')
SRC, DST = os.path.join(L05, '_影片原檔'), os.path.join(L05, 'assets')
FFMPEG = r'C:\Users\Roki\tools\ffmpeg\bin\ffmpeg.exe'
# (檔名關鍵字, 網頁版檔名, 封面檔名, 封面取第幾秒)
JOBS = [
    ('藍牙耳機', 'M2_E_打雷藍芽耳機_新聞影片.mp4', 'M2_E_打雷藍芽耳機_新聞影片_封面.jpg', 1),
    ('手機充電時在講電話', 'M2_H_充電講電話喝水_原始影片.mp4', 'M2_H_充電講電話喝水_原始影片_封面.jpg', 2),
    ('印度', 'M2_G_印度街頭小吃_原始影片.mp4', 'M2_G_印度街頭小吃_原始影片_封面.jpg', 2),
]
VF = "scale='if(gt(iw,ih),-2,min(480,iw))':'if(gt(iw,ih),min(480,ih),-2)'"
for vid, out, poster, ts in JOBS:
    hits = [f for f in glob.glob(os.path.join(SRC, '*')) if vid in os.path.basename(f) and f.lower().endswith(('.mp4', '.mkv', '.webm', '.mov'))]
    if not hits:
        print('找不到', vid, '的原檔（檔名要含「%s」）' % vid); continue
    src = hits[0]
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', src, '-vf', VF, '-c:v', 'libx264', '-crf', '31', '-preset', 'slow',
                    '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', os.path.join(DST, out)], check=True)
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-ss', str(ts), '-i', src, '-frames:v', '1', '-q:v', '4', '-vf', VF,
                    os.path.join(DST, poster)], check=True)
    print('完成', out, round(os.path.getsize(os.path.join(DST, out)) / 1024), 'KB')
