"""Unifica la procedencia editorial y la verificación audiovisual R04, sin DEE."""
from pathlib import Path
import json,hashlib,datetime,sys
HERE=Path(__file__).resolve().parent
VIDEOS=HERE.parent
R03=VIDEOS/'produccion_cientifica/R03'
REG=VIDEOS/'DEE_Cognitive_2_0_Verificacion_R04.json'
FINAL=VIDEOS/'DEE_Cognitive_2_0_Presentacion_R04_Concepto_y_Visual_1080p_v2.mp4'
SRT=VIDEOS/'DEE_Cognitive_2_0_Presentacion_R04_Concepto_y_Visual_EN.srt'
PROMPT=Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\21992FA8-6944-4EE7-BB8B-1FAA24C459B9\1-PROMPT_CODEX_DEE_VIDEO_R04_DIFERENCIA_COMPUTACIONAL_Y_MEJORA_VISUAL.docx')

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def identity(p):return {'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}

def main():
 final='--final' in sys.argv
 by_id={}
 for log in (HERE/'render_salida.log',HERE/'render_salida_v2.log'):
  if log.exists():
   for line in log.read_text(encoding='utf-8-sig',errors='replace').splitlines():
    if line.startswith('{"scene_finished":'):
     try:
      scene=json.loads(line)['scene_finished'];by_id[scene['scene']]=scene
     except json.JSONDecodeError:
      if final:raise
 scenes=list(by_id.values())
 timeline=read(R03/'timeline_R03.json')
 data={
  'schema':'DEE.R04.production_and_verification.v1',
  'status':'verificado' if final else 'render_en_curso',
  'started_utc':'2026-10-30T22:36:40Z',
  'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'budget':{'max_host_hours':4,'deadline_utc':'2026-10-31T02:36:40Z','disk_free_initial_bytes':609482899456,
            'memory_scope':'Dos procesos editoriales supervisados; no ejecución DEE. Consulta global RAM no disponible sin permiso; no se instaló psutil.',
            'exceeded':False},
  'request':identity(PROMPT),
  'protected_master':identity(R03/'DEE_Cognitive_2_0_Inteligencia_Funcional_R03_1080p.mp4'),
  'expected_master_sha256':'697a2b5c63c960cbc20bba90f7c403a9de7ee2ff5749c4f75a0611d2903c3726',
  'reference_910x512':{'name':'2113224b-a510-4910-89b2-7977568303e7.mp4','sha256_supplied':'704ae1dee2ac1799714fae43c4264650ddb29da1e007cc2f97a67865343d8752',
                      'used_as_master':False,'reason':'El maestro local R03 y su proyecto a1080p conservan el timeline requerido; no se amplió la copia reducida.'},
  'timeline':{'frames':12059,'fps':30,'duration_rational':'12059/30',
              'duration_seconds':12059/30,'scene_boundaries_preserved':True,
              'scenes':[{'id':s['id'],'start':s['start'],'end':s['end'],'frames':s['frames']} for s in timeline['scenes']]},
  'scope':{'new_native_ticks':0,'new_native_queries':0,'new_teaching':0,'new_scientific_controls':0,
           'kernel_modified':False,'whl_modified':False,'Cognitive_state_modified':False,
           'manual_modified':False,'ECI01_used':False,'external_upload':False,
           'writes_confined_to':str(VIDEOS),'original_media_overwritten':False},
  'editorial_choices':{
   'voice_changes':['A principal dentro s01','B principal dentro s03, conservando pregunta y frases originales de puntos/colores/movimiento'],
   'optional_C_used':False,'full_narration_regenerated':False,'voice_speed_changed':False,
   'existing_scene_durations_changed':False,'new_tail_or_credits':False,
   'new_visuals':['Capturas reales ampliadas y reencuadradas','Cámara editorial sobre coordenadas G07 documentadas',
                  'Etiquetas señal/relación/resultado','Control C6H04 rotulado como otra prueba',
                  'APD03 con asociaciones y tarea; cifras de panel como dato secundario',
                  'Tres capas Universe/thinking/Cognitive','Cierre de8s con a26:4+5→9;9−2→7'],
   'scene_categories':{'s01':'captura+registro','s02':'captura+registro','s03':'captura; reconstrucción G07',
     's04':'reconstrucción G07; control C6H04 de registros','s05a':'registros IC01; reconstrucción G08',
     's05b':'registros AA46, ramas separadas','s05c':'eventos U0; registros Ciclo02','s05d':'registros y geometría MU/FI01',
     's06':'registros APD03_MAIN','s07':'captura/configuración; capas y líneas de desarrollo','s08':'capturas y registros; a26'},
   'fidelity_limits':['Capturas GUI originales1284×932/15fps ampliadas; textos y gráficos renderizados1920×1080',
       'G07 es reconstrucción de receta, no telemetría microscópica densa.23 es derivado del protocolo;30 tiene salida archivada.',
       'Los colores, halos, flechas y movimientos de cámara son editoriales; no energía ni linaje nuevo.',
       'C6H04 no es ablación emparejada de G07.−4101 es lectura de un acceso, no resultado aritmético válido.',
       'AA46 muestra ramas opuestas y acceso aprendido, no iniciativa autónoma general.',
       'APD03 recibe13 del entorno entre oportunidades; no se atribuye memoria nativa de ese operando.',
       'a26 utiliza secuencia preparada por operador, dos proveedores nativos; no planificación inventada.',
       'No se presentan a29/a32 como éxitos de meta oculta, equilibrio, reparación o recuperación. No se dibujaq+5.']},
  'rendered_scenes':scenes,
  'rendered_scene_files_integrity':[{'scene':s['scene'],'same_sha256':sha(Path(s['file']))==s['sha256']} for s in scenes],
  'editorial_candidate_history':{
      'candidate01':{'file':str(VIDEOS/'DEE_Cognitive_2_0_Presentacion_R04_Concepto_y_Visual_1080p.mp4'),
          'sha256':'3233db1db370e3387e8762d49b90aec8d0375b208618e32fc0c789a40704ba99',
          'technical_checks_ok':True,'not_selected_reason':'Rótulo editorial parcialmente oculto entre las tarjetas de s07.',
          'preserved_code':identity(HERE/'versiones/candidato01/visual_r04.py'),
          'preserved_s07':identity(HERE/'versiones/candidato01/s07.mp4')},
      'candidate02':{'changed_scenes':['s07'],'unmodified_scenes_reused':10,
          'change':'Limpiar franja editorial650–797 antes de las tres tarjetas; foto y botones permanecen arriba.',
          'new_research_or_native_tests':False}},
  'editable_project':str(HERE),
  'editable_code':[identity(p) for p in sorted(HERE.glob('*.py'))]+[identity(p) for p in sorted((HERE/'codigo').glob('*.py'))],
  'audio':read(HERE/'datos/audio_fragmentos_R04.json') if (HERE/'datos/audio_fragmentos_R04.json').exists() else None,
  'scientific_provenance':read(HERE/'fragmento_evidencia.json'),
  'reading_coverage_R04':{'new':['Adjunto R04 completo:151 párrafos','Guion audiovisual R03 completo',
      'Código audiovisual R03/R04: funciones utilizadas','REG:continuation_R02.synthesis; continuation_R02.blocks.trajectories.primary_findings; current_primary_jobs dirigidos',
      'Campos/punteros de40fuentes primarias y extracciones seleccionadas; no40documentos íntegros',
      'APD03: eventos014–017,022,024,047 dirigidos'],
      'reused_not_reread':['Compendio','Procesamiento Nativo capítulos1–4/9–12','Manuales thinking4.5'],
      'scope':'Fundamentos reutilizados de revisión documentalR01/R02; no se declara lectura nueva de esos documentos ni una nueva auditoría científica.'},
  'verification':read(HERE/'datos/verificacion_tecnica_R04.json') if final else None,
  'visual_review':read(HERE/'datos/revision_visual_final.json') if (HERE/'datos/revision_visual_final.json').exists() else None,
  'outputs':[identity(p) for p in (FINAL,SRT) if p.exists()],
  'limits':['No escucha perceptiva humana/ASR: audio verificado por identidad, muestras, empalmes documentados, sonoridad y picos; no se certifica naturalidad auditiva.',
            'La edición no ejecuta ni revalida ciencia DEE. Reutiliza evidencia archivada identificada.',
            'Proyecto editable local: reutiliza fuentes R03 preservadas mediante rutas relativas; no es un nuevo paquete portátil del motor.']
 }
 assert data['protected_master']['sha256']==data['expected_master_sha256']
 if final:
  assert data['verification']['technical_checks_ok']
  assert len(scenes)==11 and sum(s['frames'] for s in scenes)==12059
  assert all(s['same_sha256'] for s in data['rendered_scene_files_integrity'])
  assert FINAL.exists() and SRT.exists()
  assert data['visual_review'] and data['visual_review']['reviewed']
  data['budget']['exceeded']=datetime.datetime.now(datetime.timezone.utc)>datetime.datetime(2026,10,31,2,36,40,tzinfo=datetime.timezone.utc)
 tmp=REG.with_suffix('.json.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(REG)
 print(json.dumps({'record':str(REG),'status':data['status'],'scenes':len(scenes),'sha256':sha(REG)},ensure_ascii=False))

if __name__=='__main__':main()
