"""Comparison clips with preserved original AAC; no synthesis or audio encode."""
from pathlib import Path
import subprocess,json,hashlib,argparse
from fijar_presentacion_mp4 import limit_presentation
H=Path(__file__).resolve().parent;ROOT=H.parent;OLD=ROOT.parent/'trabajo';T=next(x for x in H.parents if x.name=='tests')
FF=T/'_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe';FP=T/'_dee20_trabajo/video_publico_definitivo/herramientas/ffprobe.exe'
BLOCKS=json.loads((H/'guion.json').read_text('utf8'))['blocks'];MASTER=ROOT/'PROYECTO_INTACTO/DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd):
 r=subprocess.run([str(x) for x in cmd],capture_output=True);assert r.returncode==0,r.stderr.decode('utf8','replace')[-1500:];return r
def packets(p):return json.loads(run([FP,'-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,dts_time,duration_time,data_hash,side_data_list','-of','json',p]).stdout)['packets']
def pcm(p,n):return run([FF,'-v','error','-i',p,'-map','0:a:0','-af',f'atrim=start_sample=0:end_sample={n}','-acodec','pcm_f32le','-f','f32le','-']).stdout
def clips(num):
 b=BLOCKS[num-1];d=ROOT/f'escenas/S{num:02}';out=d/'comparacion';out.mkdir(exist_ok=True)
 before=out/'ANTES_CON_AUDIO.mp4';after=out/'DESPUES_CON_AUDIO.mp4';assert (d/'CORREGIDA_SIN_AUDIO.mp4').exists()
 if before.exists() and after.exists() and (out/'AUDIO_IDENTICO.json').exists():print('Reusing comparison AV',num);return
 assert not before.exists() and not after.exists(),'Preserve partial candidates before replacing.'
 tmp=out/'antes_mux_sin_limite.mp4'
 cmd=[FF,'-hide_banner','-n','-i',OLD/f'clips/S{num:02}.mp4','-ss',str(b['start_s']),'-i',MASTER,'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(b['duration_s']),'-use_editlist','1','-avoid_negative_ts','disabled','-movflags','+faststart',tmp]
 r=run(cmd);(out/'antes_mux.log').write_bytes(r.stderr);patch1=limit_presentation(tmp,before,b['duration_s'])
 tmp2=out/'despues_mux_sin_limite.mp4'
 cmd2=[FF,'-hide_banner','-n','-i',d/'CORREGIDA_SIN_AUDIO.mp4','-i',before,'-map','0:v:0','-map','1:a:0','-c','copy','-t',str(b['duration_s']),'-use_editlist','1','-avoid_negative_ts','disabled','-movflags','+faststart',tmp2]
 r=run(cmd2);(out/'despues_mux.log').write_bytes(r.stderr);patch2=limit_presentation(tmp2,after,b['duration_s'])
 aa,ab=packets(before),packets(after);pa,pb=pcm(before,round(b['duration_s']*48000)),pcm(after,round(b['duration_s']*48000))
 assert aa==ab and pa==pb
 rec={'scene':num,'start_in_master':b['start_s'],'duration':b['duration_s'],'AAC_packets_identical':True,'PCM_identical_between_comparison_clips':True,
 'audio_encode':False,'notes':'OriginalAACstream preserved; cut decoder start can differ slightly from decoding the whole master. Both comparison clips are identical to each other.',
 'before':{'file':str(before),'bytes':before.stat().st_size,'sha256':sha(before)},'after':{'file':str(after),'bytes':after.stat().st_size,'sha256':sha(after)},'PCM_sha256':hashlib.sha256(pa).hexdigest(),
 'patch_before':patch1,'patch_after':patch2,'commands':[[str(x) for x in cmd],[str(x) for x in cmd2]]}
 (out/'AUDIO_IDENTICO.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),'utf8');print('OriginalAAC comparisons closed',num,flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('scene',type=int);a=ap.parse_args();clips(a.scene)
