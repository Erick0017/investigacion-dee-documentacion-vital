"""R12 offline assembly from recorded observations, native1080 source pixels."""
from pathlib import Path
from functools import lru_cache
from collections import defaultdict
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,time
from PIL import Image,ImageEnhance
from visual_r12 import render,digest,W,H,FPS
from escenas_r12 import model

ROOT=Path(__file__).resolve().parents[1]
TESTS=next(p for p in ROOT.parents if (p/'_dee20_trabajo').is_dir())
FF=TESTS/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
PROBE=TESTS/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
FINAL_NAME='DEE_Cognitive_2_0_R12_Capacidades_y_Experiencia_1080p_ES.mp4'
CORE=['visual_r12.py','escenas_r12.py','escenas_u0_r12.py','escena_regulacion_r12.py','producir_r12.py']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
    p=Path(p);p.parent.mkdir(exist_ok=True,parents=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
@lru_cache(maxsize=1)
def schedule():
    p=ROOT/'audio/TIEMPOS_ANCLAS_R12.json';d=load(p);rows=d['rows']
    assert d['all_fit'] and not d['violations']
    assert len(rows)==42 and rows[0]['first_visual_frame_30fps']==0 and rows[-1]['end_visual_frame_exclusive_30fps']==11700
    assert all(a['end_visual_frame_exclusive_30fps']==b['first_visual_frame_30fps']for a,b in zip(rows,rows[1:]))
    return rows
@lru_cache(maxsize=1)
def phases():
    d=load(ROOT/'AUDITORIA/FASES_Y_VOZ_R12.json')
    assert d['all_fragments_literal'] and d['all_boundaries_resolved'] and not d['unresolved']
    return {row['shot_id']:row for row in d['rows']}
def frame_model(i):
    row=next(x for x in schedule()if x['first_visual_frame_30fps']<=i<x['end_visual_frame_exclusive_30fps'])
    start,end=row['first_visual_frame_30fps'],row['end_visual_frame_exclusive_30fps']
    edges=[start]+phases()[row['shot_id']]['phase_boundaries_frames']+[end]
    assert all(a<b for a,b in zip(edges,edges[1:]))
    segment=next(j for j in range(3)if edges[j]<=i<edges[j+1])
    p=(segment+(i-edges[segment])/(edges[segment+1]-edges[segment]))/3
    return model(row['shot_id'],p),row
def fingerprint():
    result={name:sha(ROOT/'codigo'/name)for name in CORE}
    for rel in ['evidencia_reutilizada/REUSO_R12_DATOS.json',
                'evidencia_reutilizada/FUENTES_MECANISMOS_S06_S11_R08.json',
                'evidencia_reutilizada/PRINCIPAL_R08_DATOS_EXACTOS.json.gz',
                'evidencia_reutilizada/COMPARACION_PRINCIPAL_R12.json',
                'evidencia_reutilizada/INTERVENCIONES_R12.json',
                'evidencia_u0/U0_DATOS_R12.json.gz','evidencia_u0/COTEJO_ORIGEN_U0_R12.json',
                'evidencia_regulacion/CPC5_REGULACION_DATOS_EXACTOS.json',
                'audio/TIEMPOS_ANCLAS_R12.json','guion_fuente/SHOTLIST_R12_DERIVADO_DEL_DOCX.json']:
        result[rel]=sha(ROOT/rel)
    result['AUDITORIA/FASES_Y_VOZ_R12.json']=sha(ROOT/'AUDITORIA/FASES_Y_VOZ_R12.json')
    return result
def raster_key(m):
    panels=[]
    for pan in m.get('panels',[]):
        panels.append({k:(bool(v)if k=='reader_evidence'else v)for k,v in pan.items()
                       if k not in ['source','source_pointer','input_receipts','reader_contract','entry_receipts']})
    return digest({k:m.get(k)for k in ['title','evidence_type','notice','footer','scheme','phase','external_service_stage']}|{'panels':panels,'bounds':m.get('bounds')})
def keyframes(revision):
    out=ROOT/'qa'/('KEYFRAMES_'+revision);out.mkdir(parents=True,exist_ok=True);records=[]
    for row in schedule():
        start,end=row['first_visual_frame_30fps'],row['end_visual_frame_exclusive_30fps']
        for bound in phases()[row['shot_id']]['keyframes_voice_bound']:
            tag=bound['keyframe'];i=bound['frame'];m,_=frame_model(i)
            im,stat=render(m);dest=out/f'{row["shot_id"]}_{tag}.png';im.save(dest)
            small=dest.with_name(dest.stem+'_360.png');im.resize((360,203),Image.Resampling.LANCZOS).save(small)
            records.append({'scene_id':row['scene_id'],'shot_id':row['shot_id'],'keyframe':tag,'frame':i,
                'seconds':i/FPS,'actual_voice_anchor':row['anchor_exact'],'source_model':m,
                'physical_data_sha256':m.get('physical_data_sha256'),'image':str(dest),'image_sha256':sha(dest),
                'mobile':str(small),'mobile_sha256':sha(small),'stats':stat})
    save(out/'KEYFRAMES.json',{'source_hashes':fingerprint(),'frame_count':len(records),'new_DEE_ticks':0,'records':records})
    print(json.dumps({'keyframe_count':len(records),'path':str(out)},ensure_ascii=False))
def render_video(revision):
    src=fingerprint();out=ROOT/'renders'/f'R12_VISUAL_{revision}.mp4'
    if out.exists():raise FileExistsError('Preserve render candidates')
    snap=ROOT/'codigo'/'revisiones'/revision;snap.mkdir(parents=True,exist_ok=True)
    for name in CORE:
        dst=snap/name
        if dst.exists():assert sha(dst)==src[name]
        else:shutil.copy2(ROOT/'codigo'/name,dst)
    cache=ROOT/'renders'/('cache_1080_'+digest(src)[:16]);cache.mkdir(exist_ok=True,parents=True)
    proof=ROOT/'AUDITORIA'/f'FOTOGRAMAS_{revision}.jsonl.gz';log=ROOT/'AUDITORIA'/f'ffmpeg_render_{revision}.log'
    if proof.exists():raise FileExistsError('Preserve previous exact trace')
    cmd=[str(FF),'-v','warning','-f','rawvideo','-pixel_format','rgb24','-video_size','1920x1080','-framerate','30','-i','pipe:0',
        '-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-vf','setsar=1','-r','30','-fps_mode','cfr',
        '-threads','4','-frames:v','11700','-metadata','comment=R12 native1080 '+digest(src),'-movflags','+faststart',str(out)]
    start=time.monotonic();unique={};shots=defaultdict(dict);rgb=None;last=None
    with log.open('wb')as err,gzip.open(proof,'wt',encoding='utf8')as trace:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=err,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        try:
            for i in range(11700):
                m,row=frame_model(i);key=raster_key(m)
                if key!=last:
                    if key not in unique:
                        im,stat=render(m);assert im.size==(1920,1080)
                        path=cache/(key+'.png')
                        if path.exists():
                            with Image.open(path)as old:assert old.convert('RGB').tobytes()==im.tobytes()
                        else:im.save(path)
                        unique[key]={'source_png':str(path),'PNG_sha256':sha(path),'stats':stat}
                    with Image.open(unique[key]['source_png'])as png:rgb=png.convert('RGB').tobytes()
                    last=key
                raw=rgb
                if i>=11670:
                    im=Image.frombytes('RGB',(W,H),rgb);raw=ImageEnhance.Brightness(im).enhance(max(0,(11699-i)/29)).tobytes()
                proc.stdin.write(raw)
                physical=m.get('physical_data_sha256');binding=digest(m.get('evidence_bindings',[]))
                event={'frame':i,'time_s':i/FPS,'scene_id':row['scene_id'],'shot_id':row['shot_id'],
                       'raster_id':key,'physical_data_sha256':physical,'source_data_hash':binding}
                trace.write(json.dumps(event,separators=(',',':'))+'\n')
                if key not in shots[row['shot_id']]:
                    shots[row['shot_id']][key]={'first_frame':i,'evidence_type':m['evidence_type'],
                        'physical_data_sha256':physical,'evidence_bindings':m.get('evidence_bindings',[]),
                        'source_data_hash':binding,'source':m.get('source'),
                        'ticks':[p.get('tick')for p in m.get('panels',[])],
                        'N':[p.get('N')for p in m.get('panels',[])],'raster_id':key,
                        'limitations':m.get('limitations',[])}
                if i%300==0:
                    assert fingerprint()==src,'Preserve incomplete candidate: sources changed'
                    print(json.dumps({'frame':i,'of':11700,'native_rasters':len(unique),'host_seconds':round(time.monotonic()-start,2)}),flush=True)
            proc.stdin.close();rc=proc.wait(timeout=180)
            if rc:raise RuntimeError('Encoder error; see '+str(log))
        except BaseException:
            if proc.poll()is None:proc.terminate();proc.wait(timeout=20)
            raise
    save(ROOT/'AUDITORIA'/f'RENDER_{revision}.json',{'video':str(out),'bytes':out.stat().st_size,'sha256':sha(out),
        'frames':11700,'width':1920,'height':1080,'fps':30,'sources':src,'native_rasters':len(unique),
        'all_native_rasters':unique,'frame_trace':str(proof),'frame_trace_sha256':sha(proof),'shots':shots,
        'host_seconds':time.monotonic()-start,'new_DEE_ticks':0,'command':cmd})
    print(json.dumps({'render_finished':str(out),'bytes':out.stat().st_size,'sha256':sha(out)},ensure_ascii=False),flush=True)
def mux(revision,final=False):
    src=ROOT/'renders'/f'R12_VISUAL_{revision}.mp4';audio=ROOT/'audio/mezcla_R12_48k.wav'
    assert src.is_file()and audio.is_file()
    out=ROOT/FINAL_NAME if final else ROOT/'renders'/f'R12_ANIMATICA_{revision}.mp4'
    if out.exists():raise FileExistsError('Preserve media candidates')
    cmd=[str(FF),'-v','warning','-i',str(src),'-i',str(audio),'-map','0:v:0','-map','1:a:0',
        '-c:v','copy','-c:a','aac','-b:a','224k','-ar','48000','-ac','2','-t','390','-movflags','+faststart',str(out)]
    run=subprocess.run(cmd,capture_output=True,timeout=300);log=ROOT/'AUDITORIA'/f'ffmpeg_mux_{"FINAL"if final else revision}.log';log.write_bytes(run.stderr);run.check_returncode()
    record={'command':cmd,'exit_code':run.returncode,'stderr_log':str(log),'video_stream_copy':True,
        'video':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'visual_sha256':sha(src),
        'audio_sha256':sha(audio),'new_DEE_ticks':0,'subtitles_burned':False}
    save(ROOT/'AUDITORIA'/f'MUX_{"FINAL"if final else revision}.json',record)
    if final:shutil.copy2(ROOT/'audio/R12_ES.srt',out.with_suffix('.srt'))
    print(json.dumps(record,ensure_ascii=False),flush=True)
def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('action',choices=['keyframes','render','mux','final']);p.add_argument('--revision',default='R01');a=p.parse_args()
    if a.action=='keyframes':keyframes(a.revision)
    elif a.action=='render':render_video(a.revision)
    else:mux(a.revision,a.action=='final')
if __name__=='__main__':main()
