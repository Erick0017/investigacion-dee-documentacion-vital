"""Run exactly the real R03 documentary preflight, never --apply."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
script=P/'codigo/publicar_documentos_PI05_literal_R03.py';visual=P/'documentos/INTENTO_RENDER_PI05_1_32.json'
out=P/'control/PUBLICADOR_PI05_R03_DRYRUN_REAL.json'
if out.exists():raise ValueError('Preserve the previous real proof; use no overwrite')
life='ECI02_PI03_REPRO_PI04_PI05_MAIN_01';cardfile=S/'estado/vidas'/life/'VIDA.json'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
card=read(cardfile);active=read(S/'estado/ACTIVO.json')
paths=[C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx',
 C.parent/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx',
 C/'PROYECTO.json',C/'CONTINUIDAD_DEE_COGNITIVE_2_0.json',S/'capacidades/CATALOGO_CAPACIDADES.json',
 S/'estado/ACTIVO.json',cardfile,S/card['snapshot'],S/active['snapshot'],S/'contratos/PI05_C2C_USO_PRINCIPAL_01.json',
 P/'control/CIERRE_CIENTIFICO_PI05.json',P/'documentos/ACTUALIZACION_DOCUMENTAL_PI05_1_32.json']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p)for p in dict.fromkeys(paths)}
cmd=[sys.executable,'-I','-B','-X','utf8',str(script),'--visual-proof',str(visual)]
result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8')
after={str(p):sha(p)for p in dict.fromkeys(paths)}
plan=None
if result.returncode==0:plan=json.loads(result.stdout)
valid=result.returncode==0 and before==after and plan['mode']=='DRY_RUN_NO_WRITES'and plan['Native_ticks']==0 and plan['visual_QA']=='NOT_VALIDATED'
proof={'schema':'DEE.PI05.real_publisher_R03_dry_run.v1','recorded_utc':datetime.now(timezone.utc).isoformat(),
 'command':cmd,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'parsed_plan':plan,
 'publisher_sha256':sha(script),'critical_before_sha256':before,'critical_after_sha256':after,
 'critical_originals_unchanged':before==after,'completed_read_only_preflight':valid,'Native_executed':False,
 'apply_argument_present':False,'scope':'Real complete staging/current-system documentary preflight only; no authoring or publication.'}
with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':sha(out),'exit_code':result.returncode,'completed_read_only_preflight':valid,'plan':plan,'stderr':result.stderr},ensure_ascii=False,indent=2))
raise SystemExit(0 if valid else 2)
