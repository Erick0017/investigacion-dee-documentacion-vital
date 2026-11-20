"""Read completed scene clips and extract selected encoded frames. No DEE.

Only clips with their closed .json and an exact matching file SHA are read.
Writes commands, stderr and PNGs exclusively below QA_C. No production imports.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
TESTS = next(p for p in WORK.parents if p.name == 'tests')
FFMPEG = TESTS/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe'
FFPROBE = TESTS/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):
            h.update(data)
    return h.hexdigest()


def write_new(path, value):
    with path.open('x',encoding='utf8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenes',nargs='+',default=['03','05','10','11','12','13'])
    args = parser.parse_args()
    plan_path = WORK/'PLAN_3D_14_ESCENAS.json'
    plan = json.loads(plan_path.read_text(encoding='utf8'))
    for number in args.scenes:
        number = f'{int(number):02}'
        clip = WORK/'clips'/('S'+number+'.mp4')
        closed = clip.with_suffix('.json')
        if not clip.exists() or not closed.exists():
            print(json.dumps({'scene':number,'status':'not_yet_closed','has_clip':clip.exists(),'has_closed_json':closed.exists()}),flush=True)
            continue
        metadata_bytes=closed.read_bytes()
        metadata_digest=hashlib.sha256(metadata_bytes).hexdigest()
        meta = json.loads(metadata_bytes)
        digest = sha(clip)
        if digest != meta['sha256'] or clip.stat().st_size != meta['bytes']:
            raise ValueError('Clip differs from its closed JSON: '+str(clip))
        out = HERE/('S'+number+'_'+digest[:12])
        if (out/'EXTRACCION.json').exists():
            print(json.dumps({'scene':number,'status':'already_extracted','path':str(out/'EXTRACCION.json')}),flush=True)
            continue
        out.mkdir(exist_ok=False)
        shots = [s for s in plan['shots'] if s['scene']==int(number)]
        start = min(s['start'] for s in shots)
        samples = {}
        def sample(frame,reason,shot):
            frame=max(0,min(int(meta['frames'])-1,int(frame)))
            row=samples.setdefault(frame,{'frame':frame,'local_time_s':frame/30,
                                         'film_time_s':start+frame/30,'reasons':[],'shots':[]})
            row['reasons'].append(reason)
            if shot['id'] not in row['shots']:
                row['shots'].append(shot['id'])
        for s in shots:
            mid=round((((s['start']+s['end'])/2)-start)*30)
            sample(mid,'shot_midpoint',s)
            # A frame shortly after each editorial stage cut checks that the
            # old/new geometry and text do not remain superposed.
            sample(round((s['start']-start)*30)+12,'stage_start_plus_0.4s',s)
        frames=sorted(samples)
        cmd_probe=[str(FFPROBE),'-v','error','-show_streams','-show_format','-of','json',str(clip)]
        probe=subprocess.run(cmd_probe,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
        (out/'ffprobe.stdout.json').write_bytes(probe.stdout)
        (out/'ffprobe.stderr.log').write_bytes(probe.stderr)
        if probe.returncode:
            write_new(out/'FAILURE.json',{'command':cmd_probe,'exit_code':probe.returncode})
            raise RuntimeError('ffprobe failed')
        select='+'.join('eq(n\\,'+str(f)+')' for f in frames)
        graph='[0:v]select='+select+',split=2[native][small];[small]scale=360:-2:flags=lanczos[mobile]'
        cmd=[str(FFMPEG),'-v','error','-nostdin','-threads','1','-filter_complex_threads','1',
             '-i',str(clip),'-filter_complex',graph,
             '-map','[native]','-vsync','0',str(out/'1080_%03d.png'),
             '-map','[mobile]','-vsync','0',str(out/'360_%03d.png')]
        write_new(out/'COMMANDS.json',{'ffprobe':cmd_probe,'ffmpeg':cmd,'cwd':str(WORK)})
        run=subprocess.run(cmd,cwd=WORK,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
        (out/'ffmpeg.stdout.log').write_bytes(run.stdout)
        (out/'ffmpeg.stderr.log').write_bytes(run.stderr)
        if run.returncode:
            write_new(out/'FAILURE.json',{'command':cmd,'exit_code':run.returncode})
            raise RuntimeError('ffmpeg extraction failed')
        if sha(clip)!=digest or sha(closed)!=metadata_digest:
            raise RuntimeError('Input changed during extraction')
        rows=[]
        for i,frame in enumerate(frames,1):
            row=samples[frame]
            for size in ['1080','360']:
                path=out/(size+'_'+f'{i:03}'+'.png')
                row[size]={'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size}
            rows.append(row)
        report={'scope':'Selected encoded frames; no whole-film viewing/listening or universal scientific approval.',
                'created_utc':datetime.now(timezone.utc).isoformat(),
                'scene':number,'clip':str(clip),'clip_sha256':digest,'clip_bytes':meta['bytes'],
                'closed_metadata':{'path':str(closed),'sha256':sha(closed)},
                'plan':{'path':str(plan_path),'sha256':sha(plan_path)},
                'source_canvas':meta.get('source_canvas'),'frames_total':meta['frames'],
                'samples':rows,'ffmpeg_exit_code':run.returncode,
                'visual_inspection_performed_by_this_script':False,'new_DEE_ticks':0}
        write_new(out/'EXTRACCION.json',report)
        print(json.dumps({'scene':number,'status':'extracted','samples':len(rows),'path':str(out/'EXTRACCION.json')}),flush=True)


if __name__=='__main__':
    main()
