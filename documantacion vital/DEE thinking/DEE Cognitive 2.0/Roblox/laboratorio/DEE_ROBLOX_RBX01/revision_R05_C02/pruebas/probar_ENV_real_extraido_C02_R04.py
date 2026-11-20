"""Passive actual replay recalculation from a fresh isolated small extraction."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
stage=ROOT/'pruebas'/('EXTRACCION_ENV_REAL_C02_'+stamp);stage.mkdir()
names=['analisis/RECALCULO_ENLACE_NUMERICO_AMBIENTAL_C02_R04.py']
for arm in('INTACT','CUT_B'):names.append('evidencia/CONTROL_ENLACE_NUMERICO_'+arm+'_R02/RESULTADO_AMBIENTAL_REPLAY_C02.json')
data=json.loads((ROOT/names[1]).read_text('utf8'));provenance=data['sourceProvenance']
for key in('primary_path','world_path','world_final_path'):
 source=Path(provenance[key]).resolve(strict=True);assert source.is_relative_to(ROOT)
 names.append(source.relative_to(ROOT).as_posix())
members=[]
for name in dict.fromkeys(names):
 source=ROOT/name;dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);before=sha(source)
 shutil.copyfile(source,dest);assert sha(source)==sha(dest)==before
 members.append(dict(source=str(source),archive=name,sha256=before,bytes=dest.stat().st_size,role='control'))
control=stage/'CONTROL';control.mkdir()
derived=control/'PROTECCION_CRITICOS.json';derived.write_text('{"schema":"SYNTHETIC_TRANSPORT_MEMBER_ONLY_NOT_PROTECTION_EVIDENCE"}\n',encoding='utf8')
# Actual packager ABI: this generated metadata member has no source field.
members.append(dict(archive='CONTROL/PROTECCION_CRITICOS.json',sha256=sha(derived),bytes=derived.stat().st_size,role='verification'))
(control/'MANIFIESTO_SHA256.json').write_text(json.dumps(dict(schema='DEE.RBX01.C02.analysis_manifest.R01',members=members),indent=2)+'\n',encoding='utf8')
command=[sys.executable,'-I','-B','analisis/RECALCULO_ENLACE_NUMERICO_AMBIENTAL_C02_R04.py','--package-root','.', '--output','SALIDA_ENV_NUEVA']
result=subprocess.run(command,cwd=stage,text=True,encoding='utf8',capture_output=True,timeout=90)
(stage/'stdout.txt').write_text(result.stdout,encoding='utf8');(stage/'stderr.txt').write_text(result.stderr,encoding='utf8')
assert result.returncode==0,result.stderr
report=json.loads((stage/'SALIDA_ENV_NUEVA/RECALCULO.json').read_text('utf8'))
assert report['arms']['INTACT']['deltas']['resourceCount']==1 and report['arms']['CUT_B']['deltas']['resourceCount']==0
assert all(x['matches']for x in report['source_hash_checks'])
assert report['subagent_native_ticks']==0
proof=dict(schema='DEE.RBX01.C02.actual_ENV_clean_extraction_passive_recalculation.R04',inspected_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 stage=str(stage),copied_original_files=len(members)-1,copied_original_bytes=sum(x['bytes']for x in members if'source'in x),
 generated_control_scope='Synthetic schema-compatibility metadata only; no claim of actual protected-original verification.',
 command=command,resource_delta=dict(INTACT=1,CUT_B=0),source_provenance_hashes_all_match=True,
 interpretation='Necessary environmental numeric-result link for this host-replayed recorded case; not new Native learning or independent replicas.',
 Native_calls=0,MCP_calls=0,HTTP_calls=0,model_calls=0,original_provenance_paths_opened_by_recalc=False,
 result_sha256=sha(stage/'SALIDA_ENV_NUEVA/RECALCULO.json'),members=members)
out=ROOT/'pruebas'/('ENV_REAL_EXTRAIDO_R04_'+stamp+'.json');out.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(proof=str(out),copied_files=proof['copied_original_files'],copied_bytes=proof['copied_original_bytes'],resource_delta=proof['resource_delta'],source_hashes_match=True,Native_calls=0,model_calls=0),indent=2))
