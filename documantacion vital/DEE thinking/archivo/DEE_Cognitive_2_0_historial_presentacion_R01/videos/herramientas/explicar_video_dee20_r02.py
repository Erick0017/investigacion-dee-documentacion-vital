"""Editorial-only CRF18 derivative: same packets' timeline, no crop or retiming."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re, subprocess, time
from pathlib import Path

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def command(cmd,cwd=None,timeout=1800):
    r=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if r.returncode:raise RuntimeError(f'FFmpeg failed {r.returncode}: '+r.stderr.decode('utf8','replace')[-5000:])
    return r

def timeline(ffmpeg,path,clocks):
    # H.264 bf=0: each compressed video packet is exactly one displayed frame.
    r=command([ffmpeg,'-hide_banner','-i',str(path),'-map','0:v:0','-an','-c:v','copy','-f','framehash','-hash','sha256','-'])
    text=r.stdout.decode('utf8','replace');tb=re.search(r'#tb 0: ([^\r\n]+)',text).group(1)
    data=[]
    for line in text.splitlines():
        if line and not line.startswith('#'):
            p=[x.strip() for x in line.split(',')];data.append([int(p[1]),int(p[2]),int(p[3])])
    if not data or any(dts!=pts for dts,pts,duration in data):raise ValueError('Expected non-reordered bf=0 timeline')
    n,d=map(int,tb.split('/'));normalized=[[dts*n,pts*n,duration*n,d] for dts,pts,duration in data]
    return {'file':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'time_base':tb,'frames':len(data),'first':data[0],'last':data[-1],'duration_seconds':(data[-1][1]+data[-1][2]-data[0][1])*n/d,'timeline_sha256':hashlib.sha256(json.dumps(normalized,separators=(',',':')).encode()).hexdigest(),'container_clocks':clocks(path)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',required=True);p.add_argument('--original',required=True);p.add_argument('--output',required=True);p.add_argument('--ass',required=True);p.add_argument('--recorder',required=True);p.add_argument('--expected-original-sha256',required=True);p.add_argument('--band',type=int,default=200)
    a=p.parse_args();src=Path(a.original).resolve();dst=Path(a.output).resolve();ass=Path(a.ass).resolve();ff=str(Path(a.ffmpeg).resolve())
    if dst.exists():raise FileExistsError(dst)
    if sha(src)!=a.expected_original_sha256:raise ValueError('Original source SHA mismatch')
    spec=importlib.util.spec_from_file_location('capture_helpers',a.recorder);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    before=timeline(ff,src,mod.mp4_clocks)
    if before['frames']!=24009 or before['duration_seconds']!=1600.6:raise ValueError('Unexpected recovered original timeline')
    progress=dst.with_suffix('.encode.progress')
    cmd=[ff,'-hide_banner','-n','-i',str(src),'-vf',f'ass=filename={ass.name}','-map','0:v:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-profile:v','high','-pix_fmt','yuv420p','-bf','0','-fps_mode','passthrough','-video_track_timescale','15360','-movflags','+faststart','-progress',str(progress),str(dst)]
    with dst.with_suffix('.encode.log').open('wb') as log:
        proc=subprocess.Popen(cmd,cwd=ass.parent,stdout=subprocess.DEVNULL,stderr=log)
        print(json.dumps({'encoder_pid':proc.pid,'command':cmd,'original':before,'source_immutable_sha256':a.expected_original_sha256}),flush=True)
        code=proc.wait(timeout=1800)
    if code:raise RuntimeError(f'Encoder failed {code}')
    after=timeline(ff,dst,mod.mp4_clocks)
    equal={k:before[k]==after[k] for k in ['time_base','frames','first','last','duration_seconds','timeline_sha256','container_clocks']}
    if not all(equal.values()):raise ValueError('Timeline or clock mismatch: '+str(equal))
    strict=[ff,'-hide_banner','-v','error','-xerror','-err_detect','explode','-i',str(dst),'-map','0:v:0','-an','-progress','pipe:1','-f','null','NUL']
    dec=command(strict,timeout=300);dst.with_suffix('.decode.progress').write_bytes(dec.stdout)
    frames=re.findall(r'^frame=(\d+)\r?$',dec.stdout.decode('utf8','replace'),re.MULTILINE)
    if not frames or int(frames[-1])!=24009:raise ValueError('Strict decode frame count mismatch')
    samples=[]
    # Sampled SSIM only: lossy recoding is permitted; no all-frame pixel identity claim.
    for at in [1,430,1380,1599]:
        filtr=f'[0:v]crop=iw:ih-{a.band}:0:0[a];[1:v]crop=iw:ih-{a.band}:0:0[b];[a][b]ssim'
        r=command([ff,'-hide_banner','-ss',str(at),'-i',str(src),'-ss',str(at),'-i',str(dst),'-lavfi',filtr,'-frames:v','15','-an','-f','null','NUL'],timeout=120)
        matches=re.findall(r'SSIM .*?All:([0-9.]+)',r.stderr.decode('utf8','replace'))
        samples.append({'start_seconds':at,'requested_frames':15,'region':'platform only; bottom band excluded','ssim_all':float(matches[-1]) if matches else None})
    report={'schema':'DEE20.same_recording_editorial_crf18.v2','source_original_unchanged':sha(src)==a.expected_original_sha256,'original':before,'explained':after,'equal_timeline':equal,'no_cuts_speed_changes_or_extra_frames':all(equal.values()),'codec':'H264 High yuv420p CRF18, bf=0','editorial_band_bottom_pixels':a.band,'ass_sha256':sha(ass),'strict_decode_frame_count':int(frames[-1]),'strict_decode_returncode':0,'sampled_ssim_platform':samples,'decoded_platform_bit_exact_claim':False,'new_native_ticks':0,'new_capture':False,'command':cmd}
    dst.with_suffix('.verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
