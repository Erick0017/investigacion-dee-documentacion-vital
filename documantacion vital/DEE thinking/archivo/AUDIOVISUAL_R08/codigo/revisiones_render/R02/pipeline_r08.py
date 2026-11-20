"""R08 offline audiovisual assembly, native frames and explicit provenance.

Only rendering/encoding existing evidence. No DEE or Cognitive imports.
"""
from pathlib import Path
from collections import defaultdict
from functools import lru_cache
import argparse,csv,gzip,hashlib,importlib,json,math,os,subprocess,sys,time
from PIL import Image,ImageEnhance
from render_r08 import render,data_hash,W,H,FPS

ROOT=Path(__file__).resolve().parents[1]
TESTS=next(p for p in ROOT.parents if (p/'_dee20_trabajo').is_dir())
FF=TESTS/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
PROBE=TESTS/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
FINAL='DEE_Cognitive_2_0_R08_Experiencia_y_Procesamiento_1080p_ES.mp4'
SAMPLE_TIMES=[2,8,35,55,83,110,139,171,210,238,282,306,331,350,382]

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()

def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
    p=Path(p);p.parent.mkdir(exist_ok=True,parents=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

@lru_cache(maxsize=1)
def schedule():
    d=load(ROOT/'audio/TIEMPOS_ANCLAS_R08.json');rows=d['rows'];assert d['all_fit'] and not d['violations']
    assert rows[0]['first_visual_frame_30fps']==0 and rows[-1]['end_visual_frame_exclusive_30fps']==11700
    assert all(a['end_visual_frame_exclusive_30fps']==b['first_visual_frame_30fps'] for a,b in zip(rows,rows[1:]))
    return rows

def frame_model(index):
    if not 0<=index<11700:raise ValueError('Outside fixed montage')
    shot=next(s for s in schedule() if s['first_visual_frame_30fps']<=index<s['end_visual_frame_exclusive_30fps'])
    a,b=shot['first_visual_frame_30fps'],shot['end_visual_frame_exclusive_30fps']
    progress=(index-a)/max(1,b-a)
    scene=shot['scene_id']
    module='escenas_centrales_r08' if scene in ('S01','S02','S03','S04') else 'escenas_editoriales_r08' if scene in ('S05','S12') else 'escenas_mecanismos_r08'
    m=importlib.import_module(module).model(scene,shot['shot_id'],progress)
    m['scene_id']=scene;m['shot_id']=shot['shot_id']
    return m,shot

def visual_key(m):
    # Provenance records can contain redundant receipts; they do not change
    # the raster. The complete source hash is preserved separately per frame.
    panels=[]
    for p in m.get('panels',[]):
        panels.append({k:(bool(v) if k=='reader_evidence' else v) for k,v in p.items() if k not in ('source','input_receipts','reader_contract')})
    return data_hash({k:m.get(k) for k in ('title','scheme','evidence_type','bounds','stage_jump')}|{'panels':panels})

def source_rows(m):
    if m.get('source'):return m['source']
    if m.get('sources'):return m['sources']
    panels=m.get('panels',[])
    return {'source_refs':m.get('source_refs',[]),
            'panel_sources':[p.get('source') for p in panels],
            'case_id':[p.get('case_id') for p in panels],
            'branch_id':[p.get('branch_id') for p in panels],
            'parent_id':[p.get('parent_id') for p in panels],
            'N':[p.get('N') for p in panels],
            'ROI':[p.get('bounds',m.get('bounds')) for p in panels],
            'input_receipts':[p.get('input_receipts',[]) for p in panels],
            'reader_contract':[p.get('reader_evidence') for p in panels],
            'fields_shown':[p.get('fields_shown',[]) for p in panels],
            'replay_status':m.get('replay_status','Not a new Native execution'),
            'supported_claim':m.get('supported_claim'),
            'limitations':m.get('limitations',[])}

def preview(times,revision='R01'):
    out=ROOT/'qa'/('previas_'+revision);out.mkdir(parents=True,exist_ok=True);records=[]
    for t in times:
        m,shot=frame_model(min(11699,round(t*FPS)))
        im,stats=render(m);name=f'T{round(t*1000):06d}_{shot["shot_id"]}.png';path=out/name
        im.save(path);small=out/(path.stem+'_360.png');im.resize((360,203),Image.Resampling.LANCZOS).save(small)
        records.append({'seconds':t,'frame':round(t*FPS),'image':str(path),'mobile':str(small),'stats':stats,'source':source_rows(m)})
    save(out/'MUESTRAS_R08.json',records)
    print(json.dumps({'preview_count':len(records),'directory':str(out)},ensure_ascii=False),flush=True)

def fingerprint(scene_limit):
    names=['render_r08.py','pipeline_r08.py','escenas_centrales_r08.py']
    if scene_limit>4:names+=['escenas_editoriales_r08.py','escenas_mecanismos_r08.py','escenas_principal_r08.py']
    return {name:sha(ROOT/'codigo'/name) for name in names}

def render_video(revision,central_only=False):
    # Every source frame is produced at1080. No low-resolution preview is an
    # encoding input. Cache consists of full native-resolution PNGs only.
    total=126*FPS if central_only else 11700
    out=ROOT/'renders'/f'R08_VISUAL_{"CENTRAL_" if central_only else ""}{revision}.mp4'
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise FileExistsError('Preserve prior render candidate')
    logs=ROOT/'verificaciones';logs.mkdir(exist_ok=True)
    src=fingerprint(4 if central_only else 12)
    cache=ROOT/'renders/cache_1080';cache.mkdir(parents=True,exist_ok=True)
    proof=logs/f'FOTOGRAMAS_{"CENTRAL_" if central_only else ""}{revision}.jsonl.gz'
    log=logs/f'ffmpeg_render_{"CENTRAL_" if central_only else ""}{revision}.log'
    cmd=[str(FF),'-v','warning','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','pipe:0',
         '-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-vf','setsar=1','-r','30','-fps_mode','cfr',
         '-threads','4','-frames:v',str(total),'-metadata','comment=R08 native1080 source '+data_hash(src),'-movflags','+faststart',str(out)]
    unique={};shots=defaultdict(dict);boxes={};start=time.monotonic();last_key=None;rgb=None
    with log.open('wb') as err,gzip.open(proof,'wt',encoding='utf8') as trace:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        try:
            for i in range(total):
                m,shot=frame_model(i);key=visual_key(m)
                if key!=last_key:
                    path=cache/(key+'.png')
                    if key not in unique:
                        im,stat=render(m)
                        if im.size!=(1920,1080):raise ValueError('Source is not native1080')
                        if path.exists():
                            with Image.open(path) as prior:
                                if prior.size!=(1920,1080) or prior.convert('RGB').tobytes()!=im.tobytes():raise ValueError('Raster cache identity differs')
                        else:im.save(path)
                        unique[key]={'source_png':str(path),'PNG_sha256':sha(path),'stats':stat}
                        boxes[key]=stat
                    with Image.open(path) as image:rgb=image.convert('RGB').tobytes()
                    last_key=key
                if not central_only and i>=11670:
                    # Editorial ending fade; never an alleged physical change.
                    base=Image.frombytes('RGB',(W,H),rgb)
                    amount=max(0,(11699-i)/29)
                    raw=ImageEnhance.Brightness(base).enhance(amount).tobytes()
                else:raw=rgb
                proc.stdin.write(raw)
                source_hash=m.get('source_data_hash') or data_hash(source_rows(m))
                entry={'frame':i,'time_s':i/FPS,'scene_id':shot['scene_id'],'shot_id':shot['shot_id'],'raster_id':key,'source_data_hash':source_hash}
                trace.write(json.dumps(entry,separators=(',',':'))+'\n')
                if source_hash not in shots[shot['shot_id']]:
                    shots[shot['shot_id']][source_hash]={'first_frame':i,'source_data_hash':source_hash,'evidence_type':m['evidence_type'],'source':source_rows(m),
                        'N':[p['N'] for p in m.get('panels',[])],'ticks':[p.get('tick') for p in m.get('panels',[])],
                        'fields_shown':['Measured source site coordinates','RAW-derived discrete state','source direction when annotated','qualified reader result when present'],
                        'raster_id':key}
                if i%300==0:
                    if fingerprint(4 if central_only else 12)!=src:raise RuntimeError('Source changed during render; preserve candidate as incomplete')
                    print(json.dumps({'frame':i,'total':total,'unique_native_rasters':len(unique),'host_seconds':round(time.monotonic()-start,2)}),flush=True)
            proc.stdin.close();code=proc.wait(timeout=180)
            if code:raise RuntimeError('Encoder failed; see '+str(log))
        except BaseException:
            if proc.poll() is None:proc.terminate();proc.wait(timeout=20)
            raise
    record={'video':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'frames':total,'width':1920,'height':1080,'fps':30,
            'sources':src,'native_rasters':len(unique),'all_native_rasters':unique,'frame_trace':str(proof),'frame_trace_sha256':sha(proof),
            'shots':dict(shots),'host_seconds':time.monotonic()-start,'new_Native_ticks':0,'command':cmd}
    save(logs/f'RENDER_{"CENTRAL_" if central_only else ""}{revision}.json',record)
    print(json.dumps({k:v for k,v in record.items() if k not in ('all_native_rasters','shots')},ensure_ascii=False),flush=True)

def mux(revision,central_only=False):
    visual=ROOT/'renders'/f'R08_VISUAL_{"CENTRAL_" if central_only else ""}{revision}.mp4'
    duration=126 if central_only else 390
    out=ROOT/'renders'/f'R08_CENTRAL_CON_VOZ_{revision}.mp4' if central_only else ROOT/FINAL
    if out.exists():raise FileExistsError('Preserve existing master')
    cmd=[str(FF),'-v','warning','-i',str(visual),'-i',str(ROOT/'audio/mezcla_R08_48k.wav'),'-map','0:v:0','-map','1:a:0',
         '-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-ac','2','-t',str(duration),'-movflags','+faststart',str(out)]
    r=subprocess.run(cmd,capture_output=True,timeout=300)
    (ROOT/'verificaciones'/f'ffmpeg_mux_{"CENTRAL_" if central_only else ""}{revision}.log').write_bytes(r.stderr)
    r.check_returncode()
    print(json.dumps({'master':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'duration_expected':duration}),flush=True)

def main():
    p=argparse.ArgumentParser(__doc__)
    p.add_argument('action',choices=['preview','render','mux']);p.add_argument('--times',default='2,8,35,55,83,110,139,171,210,238,282,306,331,350,382')
    p.add_argument('--revision',default='R01');p.add_argument('--central-only',action='store_true');a=p.parse_args()
    if a.action=='preview':preview([float(x) for x in a.times.split(',')],a.revision)
    elif a.action=='render':render_video(a.revision,a.central_only)
    else:mux(a.revision,a.central_only)

if __name__=='__main__':main()
