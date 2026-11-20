"""Run existing passive comparison from a fresh small extraction-like directory.

This is documentary recalculation, not a Native, model or Roblox run. The AI arm
is intentionally absent in this smoke check and is reported as unobserved.
"""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
stage=ROOT/'pruebas'/('EXTRACCION_RECALCULO_C02_'+stamp);stage.mkdir()
life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02'
base=f'native/MAIN_R02/sistema/estado/servicios_locales/{life}/RBX02_NATIVE_C02_R02'
names=['analisis/RECALCULO_COMPARATIVA_C02.py','analisis/RECALCULO_FUNCIONES_Y_MUNDO_C02.py',
 'evidencia/MAIN_R02_PERIODO_02/WORLD_FINAL.json','evidencia/PROGRAMMED_PERIODO_02/WORLD_CHECKPOINT.json',
 'comparadores/PROGRAMMED_R02_01/POLICY_EVENTS_C02.jsonl',base+'/events.jsonl']
names.extend(p.relative_to(ROOT).as_posix()for p in sorted((ROOT/base/'functions').glob('*.json')))
manifest=[]
for name in names:
 src=ROOT/name;dst=stage/name;dst.parent.mkdir(parents=True,exist_ok=True)
 before=sha(src);shutil.copyfile(src,dst);assert sha(src)==sha(dst)==before
 manifest.append(dict(source=str(src),archive=name,sha256=before,bytes=dst.stat().st_size))
control=stage/'CONTROL';control.mkdir();(control/'MANIFIESTO_SHA256.json').write_text(json.dumps(dict(members=manifest),indent=2)+'\n',encoding='utf8')
command=[sys.executable,'-I','-B','analisis/RECALCULO_COMPARATIVA_C02.py',
 '--native-world','evidencia/MAIN_R02_PERIODO_02/WORLD_FINAL.json',
 '--programmed-world','evidencia/PROGRAMMED_PERIODO_02/WORLD_CHECKPOINT.json',
 '--programmed-journal','comparadores/PROGRAMMED_R02_01/POLICY_EVENTS_C02.jsonl',
 '--native-functions',base+'/functions','--native-events',life+'='+base+'/events.jsonl',
 '--output','SALIDA_RECALCULO_NUEVA']
result=subprocess.run(command,cwd=stage,text=True,encoding='utf8',capture_output=True,timeout=120)
(stage/'stdout.txt').write_text(result.stdout,encoding='utf8');(stage/'stderr.txt').write_text(result.stderr,encoding='utf8')
assert result.returncode==0,result.stderr
report=json.loads((stage/'SALIDA_RECALCULO_NUEVA/RESUMEN_COMPARATIVO.json').read_text('utf8'))
assert report['Native_executed']is False and report['MCP_HTTP_model_calls']==0
assert report['arms']['LIVE_NATIVE']['completed_opportunities']==18 and report['arms']['PROGRAMMED']['completed_opportunities']==18
assert report['arms']['CONVENTIONAL_AI']['completed_opportunities']==0
assert report['common_completed_observed_prefix']==0
assert all(str(Path(row['path']).resolve()).startswith(str(stage))for row in report['sources'])
proof=dict(schema='DEE.RBX01.C02.clean_extraction_passive_recalculation.R01',inspected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 stage=str(stage),copied_bytes=sum(r['bytes']for r in manifest),copied_files=len(manifest),command=command,
 actual_inputs='Frozen Native18 and PROGRAMMED18 only. AI intentionally omitted from this smoke check; no AI failure is inferred.',
 completed=dict(Native=18,PROGRAMMED=18,AI_unobserved=0),common_prefix=0,
 all_opened_input_sources_inside_stage=True,Native_calls=0,Roblox_calls=0,model_calls=0,
 documentary_recalculation_only=True,issues=report['issues'],
 source_manifest=manifest,output_sha256=sha(stage/'SALIDA_RECALCULO_NUEVA/RESUMEN_COMPARATIVO.json'))
out=ROOT/'pruebas'/('RECALCULO_EXTRAIDO_'+stamp+'.json');out.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(proof=str(out),stage=str(stage),files=len(manifest),bytes=proof['copied_bytes'],completed=proof['completed'],issues=len(report['issues']),Native_calls=0,model_calls=0),indent=2))
