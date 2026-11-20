"""Render only this campaign's rect/text SVG subset with Pillow for N0 QA.

Not a general SVG engine. Rejects any other tag or transformation. Does not
install software, inspect a world, or modify the original SVG/evidence bundle.
"""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists(): raise FileExistsError('Do not overwrite QA image')
    encoded = args.source.read_bytes(); root = ET.fromstring(encoded); scale = 2
    width, height = int(root.attrib['width']), int(root.attrib['height'])
    image = Image.new('RGB', (width * scale, height * scale), 'white'); draw = ImageDraw.Draw(image)
    overflow = []; counts = {'rect': 0, 'text': 0}
    for item in root:
        tag = item.tag.rsplit('}', 1)[-1]
        if tag not in counts or 'transform' in item.attrib: raise ValueError('Unsupported SVG subset')
        counts[tag] += 1
        if tag == 'rect':
            x, y = float(item.attrib.get('x', 0)), float(item.attrib.get('y', 0))
            w, h = item.attrib['width'], item.attrib['height']
            w = width if w == '100%' else float(w); h = height if h == '100%' else float(h)
            draw.rectangle((round(x * scale), round(y * scale), round((x + w) * scale) - 1,
                            round((y + h) * scale) - 1), fill=item.attrib.get('fill', 'black'))
        else:
            x, y = float(item.attrib['x']) * scale, float(item.attrib['y']) * scale
            mono = item.attrib.get('font-family') == 'monospace'
            font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf' if mono else 'C:/Windows/Fonts/arial.ttf',
                                      round(float(item.attrib.get('font-size', 12)) * scale))
            box = draw.textbbox((x, y), item.text or '', font=font, anchor='ls')
            if box[0] < 0 or box[1] < 0 or box[2] > width * scale or box[3] > height * scale:
                overflow.append({'text': item.text, 'bbox_pixels': box})
            draw.text((x, y), item.text or '', font=font, fill='black', anchor='ls')
    image.save(args.out)
    print(json.dumps({'source': str(args.source), 'source_sha256': hashlib.sha256(encoded).hexdigest(),
                      'QA_image': str(args.out), 'subset_only': True, 'counts': counts, 'text_overflow': overflow,
                      'new_Native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__': main()
