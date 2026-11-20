"""Portable R12 audiovisual edition from retained, referenced observations.

No Cognitive/DEE imports. Does not require private operative snapshots. Editing
labels/camera is possible; the native observation hashes must remain intact.
"""
from pathlib import Path
import argparse,bisect,gzip,hashlib,json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_project(path):
    b=Path(path).read_bytes();return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def physical(m):
    panels=[]
    for p in m.get('panels',[]):
        panels.append({'N':p.get('N'),'tick':p.get('tick'),
            'observations':[{k:v for k,v in q.items()if k in ['site','raw','clock','state','s_reg','semantic','direction','tick','active']}for q in p.get('points',[])]})
    return digest(panels)if panels else None
def verify(d):
    assert d['fps']==30 and d['total_frames']==11700 and d['duration_seconds']==390
    prior=0;used=set()
    for x in d['intervals']:
        assert x['start_frame']==prior and x['end_frame_exclusive']>prior
        assert x['model_id']in d['models'];used.add(x['model_id']);prior=x['end_frame_exclusive']
    assert prior==11700
    for key,m in d['models'].items():
        assert physical(m)==m.get('physical_data_sha256'),'Native observations changed: '+key
        for panel in m.get('panels',[]):
            n=panel['N'];assert isinstance(n,int)and n>0
            for q in panel['points']:
                assert isinstance(q['raw'],str)and 0<=int(q['raw'])<2**64
                assert all(isinstance(a,int)and 0<=a<n for a in q['site'])
    return {'new_DEE_ticks':0,'frames':11700,'duration_seconds':390,
            'retained_model_variants':len(d['models']),'timeline_intervals':len(d['intervals']),
            'all_observation_hashes_preserved':True,'scope':'Audiovisual project integrity; not a native experimental reproduction or proof of cognition.'}
def chosen(d,frame):
    starts=[x['start_frame']for x in d['intervals']]
    row=d['intervals'][bisect.bisect_right(starts,frame)-1]
    assert row['start_frame']<=frame<row['end_frame_exclusive']
    return row['model_id'],d['models'][row['model_id']]
def main():
    p=argparse.ArgumentParser(__doc__)
    p.add_argument('--project',type=Path,default=ROOT/'PROYECTO_EDITABLE/MODELOS_POR_INTERVALO_R12.json.gz')
    p.add_argument('--verify-only',action='store_true')
    p.add_argument('--extract-editable-json',type=Path)
    p.add_argument('--preview-frame',type=int);p.add_argument('--preview-out',type=Path)
    p.add_argument('--output',type=Path);p.add_argument('--ffmpeg',type=Path)
    a=p.parse_args();d=read_project(a.project);result=verify(d)
    if a.extract_editable_json:
        with a.extract_editable_json.open('x',encoding='utf8')as f:json.dump(d,f,ensure_ascii=False,indent=2)
    if a.preview_frame is not None:
        assert a.preview_out is not None and not a.preview_out.exists()and 0<=a.preview_frame<11700
        from visual_r12 import render
        _,m=chosen(d,a.preview_frame);im,_=render(m);im.save(a.preview_out)
        result['preview']={'frame':a.preview_frame,'path':str(a.preview_out),'sha256':sha(a.preview_out)}
    if a.output:
        from PIL import Image,ImageEnhance
        from visual_r12 import render
        out=a.output.resolve();assert not out.exists(),'Preserve existing outputs'
        ff=a.ffmpeg or Path(os.environ.get('DEE_R12_FFMPEG')or shutil.which('ffmpeg')or 'FFMPEG_NOT_FOUND')
        if not ff.is_file():raise FileNotFoundError('Supply --ffmpeg or DEE_R12_FFMPEG')
        audio=ROOT/'audio/mezcla_R12_48k.flac';assert audio.is_file()
        temp=out.with_name(out.stem+'_IMAGEN_1080p.mp4');assert not temp.exists()
        cmd=[str(ff),'-v','warning','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','pipe:0',
             '-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr',
             '-frames:v','11700','-threads','2','-movflags','+faststart',str(temp)]
        log=out.with_suffix('.render.log');last=None;rgb=None
        with log.open('xb')as stderr:
            proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=stderr,stdout=subprocess.DEVNULL,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:
                for i in range(11700):
                    key,m=chosen(d,i)
                    if key!=last:
                        im,_=render(m);assert im.size==(1920,1080);rgb=im.tobytes();last=key
                    raw=rgb
                    if i>=11670:raw=ImageEnhance.Brightness(Image.frombytes('RGB',(1920,1080),rgb)).enhance(max(0,(11699-i)/29)).tobytes()
                    proc.stdin.write(raw)
                proc.stdin.close();rc=proc.wait(timeout=180)
                if rc:raise RuntimeError('Image encoder failed; see log')
            except BaseException:
                if proc.poll()is None:proc.terminate();proc.wait(timeout=20)
                raise
        mux=[str(ff),'-v','warning','-i',str(temp),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy',
             '-c:a','aac','-b:a','224k','-ar','48000','-ac','2','-t','390','-movflags','+faststart',str(out)]
        run=subprocess.run(mux,capture_output=True,timeout=300);out.with_suffix('.mux.log').write_bytes(run.stderr);run.check_returncode()
        subtitles=ROOT/'audio/R12_ES.srt'
        if subtitles.exists()and not out.with_suffix('.srt').exists():shutil.copy2(subtitles,out.with_suffix('.srt'))
        result['new_edition']={'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),
            'render_command':cmd,'mux_command':mux,'meaning':'New audiovisual edition, never a new DEE life or experiment.'}
    if not(a.verify_only or a.output or a.preview_frame is not None or a.extract_editable_json):p.error('Choose --verify-only, --preview-frame, --extract-editable-json or --output')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
