"""Build a bottom-band ASS file from editorial annotations made AFTER the run."""
import argparse,json
from pathlib import Path

def stamp(seconds):
    cs=round(float(seconds)*100);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100)
    return f'{h}:{m:02}:{s:02}.{cs:02}'

def main():
    p=argparse.ArgumentParser();p.add_argument('json');p.add_argument('ass');p.add_argument('--width',type=int,required=True);p.add_argument('--height',type=int,required=True);p.add_argument('--band',type=int,default=200);p.add_argument('--font-size',type=int,default=30)
    a=p.parse_args();rows=json.loads(Path(a.json).read_text(encoding='utf8'))
    head=f'''[Script Info]
ScriptType: v4.00+
PlayResX: {a.width}
PlayResY: {a.height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Banda,Arial,{a.font_size},&H00FFFFFF,&H00FFFFFF,&H00101A29,&H00101A29,0,0,0,0,100,100,0,0,1,0,0,5,55,55,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    last=-1;body=[];y=a.height-a.band//2
    for r in rows:
        start,end=float(r['start']),float(r['end'])
        if start<0 or end<=start or start<last:raise ValueError('Intervals must be ordered, positive and non-overlapping')
        text=str(r['text']).replace('\\','／').replace('{','(').replace('}',')').replace('\n',r'\N')
        # Clip subtitle rendering strictly to the reserved band, never the platform.
        tag='{'+f'\\an5\\pos({a.width//2},{y})\\clip(0,{a.height-a.band},{a.width},{a.height})'+'}'
        body.append(f'Dialogue: 0,{stamp(start)},{stamp(end)},Banda,,0,0,0,,{tag}{text}\n');last=end
    dest=Path(a.ass);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(head+''.join(body),encoding='utf8')
    print(json.dumps({'ass':str(dest.resolve()),'annotations':len(rows),'band_top':a.height-a.band,'last_caption_end':last},ensure_ascii=False))
if __name__=='__main__':main()
