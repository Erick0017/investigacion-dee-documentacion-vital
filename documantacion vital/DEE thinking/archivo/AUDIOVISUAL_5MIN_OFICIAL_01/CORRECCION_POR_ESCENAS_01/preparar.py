from pathlib import Path
import json,shutil,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parent;src=R/'trabajo'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (H/'PROYECTO_INTACTO').exists()
shutil.copytree(src,H/'PROYECTO_INTACTO/trabajo')
for p in R.iterdir():
 if p.is_file():shutil.copy2(p,H/'PROYECTO_INTACTO'/p.name)
protected=R/'CORRECCION_S07_01/DEE_S07_DESPUES_1080p.mp4'
assert sha(protected)=='7bb3ecac833399cb52d812082f0392d9044c26a16ea29feb3e8c9ec30fa64636'
shutil.copy2(protected,H/'PROYECTO_INTACTO'/protected.name)
shutil.copy2(R/'CORRECCION_S07_01/DEE_S07_INFORME_BREVE.txt',H/'PROYECTO_INTACTO/DEE_S07_INFORME_BREVE.txt')
tools=H/'herramientas';tools.mkdir(exist_ok=True)
for f in ['visual_core.py','producir_5min.py','verificar_archivo.py']:
 shutil.copy2(src/f,tools/f)
shutil.copytree(src/'render',tools/'render')
shutil.copytree(R/'CORRECCION_S07_01/PROYECTO_S07/trabajo/s07_render',tools/'s07_render')
shutil.copy2(R/'CORRECCION_S07_01/QA_AUDIO/fijar_presentacion_mp4.py',tools/'fijar_presentacion_mp4.py')
shutil.copy2(R/'DEE_Cognitive_5min_EN.srt',H/'DEE_Cognitive_5min_EN.srt')
plan=json.loads((src/'PLAN_3D_14_ESCENAS.json').read_text('utf8'))
def cases(x):
 if isinstance(x,dict):
  if 'id' in x and 'points' in x and 'source_refs' in x:return [x]
  return [y for v in x.values() for y in cases(v)]
 if isinstance(x,list):return [y for v in x for y in cases(v)]
 return []
case={p['id']:p for p in cases(plan)}
(tools/'CASOS.json').write_text(json.dumps(case,ensure_ascii=False,indent=2),'utf8')
shutil.copy2(src/'audio/guion.json',tools/'guion.json')
for n in range(1,15):
 d=H/f'escenas/S{n:02}';d.mkdir(parents=True,exist_ok=True)
 shutil.copy2(src/f'subtitles_scene_{n:02}.ass',d/'subtitles.ass')
state={'start_UTC':'2026-11-01T19:08:47+00:00','deadline_UTC':'2026-11-02T01:08:47+00:00','max_seconds':21600,
 'original_master':{'path':str(R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4'),'sha256':sha(R/'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4')},
 'protected_S07':{'path':str(protected),'sha256':sha(protected)},'source_SRT_sha256':sha(H/'DEE_Cognitive_5min_EN.srt'),
 'status':'Preparación cerrada; sólo correcciones visuales, cero DEE ticks, audio completo original protegido.',
 'scenes':{f'S{n:02}':{'status':'PENDIENTE'} for n in range(1,15)}}
(H/'CONTINUIDAD.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
print('Prepared',len(case),'frozen cases; full intact project and protected07.',flush=True)
