#!/usr/bin/env python3
"""Turn the large originals (for example the 28 Leonardo.ai files named like "[SG-A1] Title.jpeg") into the small WebP files the site uses.
    python3 tools/convert_images.py /path/to/originals       (needs Pillow: pip install pillow)
Wide pictures become 1000 px wide, portraits 720 px wide, WebP quality 74. Output goes to src/img/ as A1.webp ... D6.webp and S0.webp ... S3.webp
(SG-00 to SG-03 become S0 to S3). Then run: python3 build.py"""
import os, re, sys
from PIL import Image
src = sys.argv[1] if len(sys.argv) > 1 else '.'; out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'img'); os.makedirs(out, exist_ok=True)
n = 0
for f in sorted(os.listdir(src)):
    m = re.match(r'\[SG-([0-9A-D]+)\]', f)
    if not m or not f.lower().endswith(('.jpg', '.jpeg', '.png')): continue
    k = m.group(1); key = 'S' + k[1] if k.startswith('0') else k
    im = Image.open(os.path.join(src, f)).convert('RGB'); w, h = im.size; tw = 720 if w / h < 1.3 else 1000
    im = im.resize((tw, round(h * tw / w)), Image.LANCZOS); im.save(os.path.join(out, key + '.webp'), 'WEBP', quality=74, method=6); n += 1
print('wrote', n, 'files to', os.path.normpath(out))
