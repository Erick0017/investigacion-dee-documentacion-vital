"""Real window capture and exact-timeline editorial derivative. Never drives DEE.

Capture is an FFmpeg gdigrab stream, not a JSONL replay or screen-shot montage.
Interactive recorder: send 'q\n' to this script's stdin to close MP4 gracefully.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import threading
import time

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def run(cmd, timeout=120):
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if r.returncode:raise RuntimeError(f'command failed {r.returncode}: '+r.stderr.decode('utf8','replace')[-5000:])
    return r

def mp4_clocks(path):
    """Exact integer clock durations from ISO BMFF, without another dependency."""
    def boxes(blob):
        pos=0
        while pos+8<=len(blob):
            size,kind=struct.unpack('>I4s',blob[pos:pos+8]);head=8
            if size==1:size=struct.unpack('>Q',blob[pos+8:pos+16])[0];head=16
            if size==0:size=len(blob)-pos
            if size<head or pos+size>len(blob):raise ValueError('Invalid MP4 box')
            yield kind,blob[pos+head:pos+size];pos+=size
    def clock(blob):
        if blob[0]==0:scale,duration=struct.unpack('>II',blob[12:20])
        elif blob[0]==1:scale,duration=struct.unpack('>IQ',blob[20:32])
        else:raise ValueError('Unsupported MP4 clock version')
        return {'timescale':scale,'duration_units':duration}
    moov=None
    with Path(path).open('rb') as f:
        end=f.seek(0,2);f.seek(0)
        while f.tell()+8<=end:
            start=f.tell();size,kind=struct.unpack('>I4s',f.read(8));head=8
            if size==1:size=struct.unpack('>Q',f.read(8))[0];head=16
            if size==0:size=end-start
            if size<head or start+size>end:raise ValueError('Invalid MP4 top-level box')
            if kind==b'moov':
                if size>16*1024*1024:raise ValueError('Unexpectedly large MP4 moov')
                moov=f.read(size-head);break
            f.seek(start+size)
    if moov is None:raise ValueError('MP4 has no moov')
    result={'movie':None,'video_tracks':[]}
    for kind,data in boxes(moov):
        if kind==b'mvhd':result['movie']=clock(data)
        if kind!=b'trak':continue
        for sub,mdia in boxes(data):
            if sub!=b'mdia':continue
            children=dict(boxes(mdia))
            if children.get(b'hdlr',b'')[8:12]==b'vide':result['video_tracks'].append(clock(children[b'mdhd']))
    if not result['movie'] or not result['video_tracks']:raise ValueError('Missing MP4 video clocks')
    return result

def probe(ffmpeg, path, crop_band=0):
    # Decode every frame; SHA-256 framehash exposes content and exact timestamps.
    cmd=[ffmpeg,'-hide_banner','-i',str(path),'-map','0:v:0','-an']
    if crop_band:cmd+=['-vf',f'crop=iw:ih-{crop_band}:0:0']
    r=run(cmd+['-c:v','rawvideo','-f','framehash','-hash','sha256','-'],timeout=1800)
    text=r.stdout.decode('utf8','replace')
    tb=re.search(r'#tb 0: ([^\r\n]+)',text).group(1)
    dimensions=re.search(r'#dimensions 0: ([^\r\n]+)',text).group(1)
    frames=[];content=[]
    for line in text.splitlines():
        if line and not line.startswith('#'):
            p=[x.strip() for x in line.split(',')]
            frames.append([int(p[1]),int(p[2]),int(p[3])])
            content.append(p[-1])
    if not frames:raise RuntimeError('No decoded frames')
    num,den=map(int,tb.split('/'))
    duration=(frames[-1][1]+frames[-1][2]-frames[0][1])*num/den
    return {'file':str(Path(path).resolve()),'bytes':Path(path).stat().st_size,'sha256':sha(path),'time_base':tb,'dimensions':dimensions,'frames':len(frames),'first':frames[0],'last':frames[-1],'duration_seconds':duration,'container_clocks':mp4_clocks(path),'timeline_sha256':hashlib.sha256(json.dumps(frames,separators=(',',':')).encode()).hexdigest(),'decoded_frame_sha256_sequence_sha256':hashlib.sha256(json.dumps(content,separators=(',',':')).encode()).hexdigest(),'crop_bottom_pixels':crop_band,'full_decode':True}

def record(a):
    out=Path(a.output).resolve()
    if out.exists():raise FileExistsError(out)
    out.parent.mkdir(parents=True,exist_ok=True)
    source=f'title={a.window_title}' if a.window_title else f'hwnd={a.hwnd}'
    cmd=[a.ffmpeg,'-hide_banner','-n','-f','gdigrab','-framerate',str(a.fps),'-draw_mouse','1','-i',source]
    if a.seconds:cmd+=['-t',str(a.seconds)]
    # Native captured image is never cropped or sped up. Blank band exists in both versions.
    cmd+=['-vf',f'pad=ceil(iw/2)*2:ceil(ih/2)*2+{a.band}:0:0:color=0x101a29','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-bf','0','-fps_mode','cfr','-movflags','+faststart',str(out)]
    log=out.with_suffix('.capture.log')
    meta=out.with_suffix('.capture.json')
    start=time.time()
    with log.open('wb') as err:
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=err)
        print(json.dumps({'recorder_pid':p.pid,'output':str(out),'utc_unix_start':start,'command':cmd}),flush=True)
        if not a.seconds:
            def input_loop():
                for line in sys.stdin:
                    if line.strip()=='q':
                        if p.poll() is None:
                            p.stdin.write(b'q\n');p.stdin.flush()
                        return
            threading.Thread(target=input_loop,daemon=True).start()
        try:code=p.wait(timeout=a.max_seconds)
        except subprocess.TimeoutExpired:
            p.stdin.write(b'q\n');p.stdin.flush()
            try:code=p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.terminate();code=p.wait(timeout=15)
        end=time.time()
    capture_start=re.search(r'Duration: N/A, start: ([0-9.]+),',log.read_text(encoding='utf8',errors='replace'))
    report={'schema':'DEE20.real_window_capture.v1','pid':p.pid,'returncode':code,'start_unix':start,'input_start_unix':float(capture_start.group(1)) if capture_start else None,'end_unix':end,'wall_seconds':end-start,'command':cmd,'log':str(log),'band_pixels':a.band,'frame_rate_requested':a.fps,'capture_device':'gdigrab; exact dedicated native window only','capture_source':source,'real_capture_not_replay':True}
    if out.exists() and out.stat().st_size:
        try:report['decoded']=probe(a.ffmpeg,out)
        except Exception as exc:report['decode_error']=repr(exc)
    meta.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False),flush=True)
    return 0 if code==0 and report.get('decoded',{}).get('full_decode') else 1

def explained(a):
    src=Path(a.original).resolve();dst=Path(a.output).resolve();ass=Path(a.ass).resolve()
    if dst.exists():raise FileExistsError(dst)
    # Work in ASS directory so subtitle filenames need no Windows-colon escaping.
    cmd=[a.ffmpeg,'-hide_banner','-n','-i',str(src),'-vf',f'ass=filename={ass.name}','-map','0:v:0','-an','-c:v','libx264','-preset','veryfast','-qp','0','-pix_fmt','yuv420p','-bf','0','-fps_mode','passthrough','-movflags','+faststart',str(dst)]
    r=subprocess.run(cmd,cwd=ass.parent,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=a.max_seconds)
    dst.with_suffix('.encode.log').write_bytes(r.stderr)
    if r.returncode:raise RuntimeError(r.stderr.decode('utf8','replace')[-5000:])
    one=probe(a.ffmpeg,src);two=probe(a.ffmpeg,dst)
    keys=['time_base','dimensions','frames','first','last','duration_seconds','container_clocks','timeline_sha256']
    same={k:one[k]==two[k] for k in keys}
    roi_one=probe(a.ffmpeg,src,a.band);roi_two=probe(a.ffmpeg,dst,a.band)
    roi_exact=roi_one['decoded_frame_sha256_sequence_sha256']==roi_two['decoded_frame_sha256_sequence_sha256']
    report={'schema':'DEE20.same_demonstration.v1','original':one,'explained':two,'equal':same,'no_time_cuts_or_speed_changes':all(same.values()),'source_unchanged':one['sha256']==sha(src),'platform_all_frames_decoded_bit_exact':roi_exact,'original_roi':roi_one,'explained_roi':roi_two,'ass_sha256':sha(ass),'command':cmd}
    dst.with_suffix('.verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False),flush=True)
    return 0 if all(same.values()) and roi_exact else 2

def main():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',required=True)
    sub=p.add_subparsers(dest='operation',required=True)
    r=sub.add_parser('record');target=r.add_mutually_exclusive_group(required=True);target.add_argument('--hwnd');target.add_argument('--window-title');r.add_argument('--output',required=True);r.add_argument('--fps',type=int,default=15);r.add_argument('--band',type=int,default=160);r.add_argument('--seconds',type=float);r.add_argument('--max-seconds',type=int,default=7200)
    e=sub.add_parser('explain');e.add_argument('--original',required=True);e.add_argument('--output',required=True);e.add_argument('--ass',required=True);e.add_argument('--band',type=int,default=200);e.add_argument('--max-seconds',type=int,default=3600)
    t=sub.add_parser('probe');t.add_argument('input');t.add_argument('--crop-band',type=int,default=0)
    a=p.parse_args()
    if a.operation=='record':return record(a)
    if a.operation=='explain':return explained(a)
    print(json.dumps(probe(a.ffmpeg,a.input,a.crop_band),ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
