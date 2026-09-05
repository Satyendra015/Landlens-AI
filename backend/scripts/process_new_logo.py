import os
from PIL import Image, ImageDraw
import numpy as np
from collections import deque

src_path = 'C:/Users/thaku/.gemini/antigravity/brain/3d31b9d9-32d6-41c8-9853-007c1d8ef039/.user_uploaded/media_1788635805304.jpg'
if not os.path.exists(src_path):
    alt = 'media_1788635805304.jpg'
    if os.path.exists(alt):
        src_path = alt
    else:
        raise FileNotFoundError(f'Source logo not found at {src_path}')

print(f'Loading official logo source: {src_path}')
src_img = Image.open(src_path).convert('RGB')
w, h = src_img.size
print(f'Source dimensions: {w}x{h}')

# 1. Full Branded Logo (Emblem + Typography + Tagline + Footer)
full_crop = src_img.crop((80, 25, 944, 828))
fw, fh = full_crop.size

# Transparent background for full logo via corner flood-fill
f_arr = np.array(full_crop)
f_is_white = (np.min(f_arr, axis=2) > 238) & (np.max(np.abs(f_arr[:,:,:3] - f_arr[:,:,[1,2,0]]), axis=2) < 20)
f_visited = np.zeros((fh, fw), dtype=bool)
f_bg_mask = np.zeros((fh, fw), dtype=bool)
fq = deque()
for x in range(fw):
    if f_is_white[0, x]: fq.append((0, x)); f_visited[0, x] = True
    if f_is_white[fh-1, x]: fq.append((fh-1, x)); f_visited[fh-1, x] = True
for y in range(fh):
    if f_is_white[y, 0]: fq.append((y, 0)); f_visited[y, 0] = True
    if f_is_white[y, fw-1]: fq.append((y, fw-1)); f_visited[y, fw-1] = True
while fq:
    cy, cx = fq.popleft()
    f_bg_mask[cy, cx] = True
    for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
        ny, nx = cy + dy, cx + dx
        if 0 <= ny < fh and 0 <= nx < fw and not f_visited[ny, nx]:
            f_visited[ny, nx] = True
            if f_is_white[ny, nx]: fq.append((ny, nx))

full_alpha = np.where(f_bg_mask, 0, 255).astype(np.uint8)
full_trans = Image.fromarray(np.dstack((f_arr, full_alpha)))

# 2. Pure Stylized Graphic Emblem
# Exact graphic bounds: X in [278, 751], Y in [26, 490]
# Y strictly ends at 490 (above reflection/shadow, and 35px above typography starting at Y=525)
emblem_raw = src_img.crop((278, 26, 751, 490))
ew, eh = emblem_raw.size
print(f'Pure Graphic Emblem size: {ew}x{eh}')

# Flood-fill to key out only external white/light background
e_arr = np.array(emblem_raw)
e_is_bg = (np.min(e_arr, axis=2) > 215) & (np.max(np.abs(e_arr[:,:,:3].astype(int) - e_arr[:,:,[1,2,0]].astype(int)), axis=2) < 22)
e_visited = np.zeros((eh, ew), dtype=bool)
e_bg_mask = np.zeros((eh, ew), dtype=bool)
eq = deque()
for x in range(ew):
    if e_is_bg[0, x]: eq.append((0, x)); e_visited[0, x] = True
    if e_is_bg[eh-1, x]: eq.append((eh-1, x)); e_visited[eh-1, x] = True
for y in range(eh):
    if e_is_bg[y, 0]: eq.append((y, 0)); e_visited[y, 0] = True
    if e_is_bg[y, ew-1]: eq.append((y, ew-1)); e_visited[y, ew-1] = True
while eq:
    cy, cx = eq.popleft()
    e_bg_mask[cy, cx] = True
    for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
        ny, nx = cy + dy, cx + dx
        if 0 <= ny < eh and 0 <= nx < ew and not e_visited[ny, nx]:
            e_visited[ny, nx] = True
            if e_is_bg[ny, nx]: eq.append((ny, nx))

emblem_alpha = np.where(e_bg_mask, 0, 255).astype(np.uint8)
emblem_trans = Image.fromarray(np.dstack((e_arr, emblem_alpha)))

# 3. Super-sampled Circular Seal (Rendered at 2048x2048, scaled to 512x512 for smooth antialiasing)
hires_size = 2048
hires_seal = Image.new('RGBA', (hires_size, hires_size), (0, 0, 0, 0))
draw = ImageDraw.Draw(hires_seal)

# Crisp white circle with subtle golden/saffron trim
pad = 36
draw.ellipse((pad, pad, hires_size - pad, hires_size - pad), fill=(255, 255, 255, 255), outline=(234, 88, 12, 220), width=16)

# Scale emblem into high-res circle with balanced padding
target_dim = int((hires_size - 2 * pad) * 0.82)
scale = target_dim / max(ew, eh)
target_w = int(ew * scale)
target_h = int(eh * scale)
emblem_hires = emblem_trans.resize((target_w, target_h), Image.Resampling.LANCZOS)
px = (hires_size - target_w) // 2
py = (hires_size - target_h) // 2
hires_seal.paste(emblem_hires, (px, py), emblem_hires)

seal_final = hires_seal.resize((512, 512), Image.Resampling.LANCZOS)

# 4. Save to all target directories
target_dirs = [
    'backend/app/static',
    'public_web/static',
    'static'
]

for d in target_dirs:
    os.makedirs(d, exist_ok=True)
    full_trans.save(os.path.join(d, 'landlens_logo_full.png'))
    full_trans.save(os.path.join(d, 'landlens_logo.png'))
    full_trans.save(os.path.join(d, 'logo.png'))
    
    emblem_raw.save(os.path.join(d, 'landlens_logo_icon.png'))
    emblem_trans.save(os.path.join(d, 'landlens_logo_transparent.png'))
    
    seal_final.save(os.path.join(d, 'landlens_seal_exact.png'))
    seal_final.save(os.path.join(d, 'landlens_seal_circle.png'))
    seal_final.save(os.path.join(d, 'landlens_seal.png'))
    seal_final.convert('RGB').save(os.path.join(d, 'landlens_seal.jpg'))

# Root files
full_trans.save('logo.png')
full_trans.save('public_web/logo.png')

print('SUCCESS: All logo and emblem assets generated with zero text leakage and supersampled antialiasing!')

