"""Tiny synthetic transfer package only; NOT a final project delivery."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];source=ROOT/'control/empacar_evidencia_C02.py'
s=importlib.util.spec_from_file_location('_C02_pack_fixture',source);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');work=ROOT/'pruebas'/('PACK_FIXTURE_'+stamp);work.mkdir()
m.ROOT=m.PRODUCT=m.PROJECT=work
inputs=work/'inputs';inputs.mkdir();critical=work/'protected_original.txt';critical.write_text('Synthetic protected bytes, no cognitive content.\n',encoding='utf8')
baseline=work/'critical_before.json';baseline.write_text(json.dumps({'files':[{'path':str(critical),'role':'synthetic_protected','sha256':m.sha(critical)}]}),encoding='utf8')
data={'LEER_PRIMERO.txt':'Synthetic fixture only; Native not executed.\n','INFORME.md':'Synthetic report for package validator.\n','EVIDENCIA/record.json':json.dumps({'actual_zero':0,'no_response':None,'synthetic':True})}
files=[]
for name,text in data.items():
    p=inputs/Path(name).name;p.write_text(text,encoding='utf8')
    files.append({'source':str(p),'archive':name,'sha256':m.sha(p),'role':'readme'if name.startswith('LEER')else'report'if name.startswith('INFORME')else'primary'})
plan=work/'finalexport.json';plan.write_text(json.dumps({'schema':'DEE.RBX01.C02.final_export.R01','finalized':True,'files':files,'critical_baseline':str(baseline)}),encoding='utf8')
before={str(p):m.sha(p)for p in inputs.iterdir()};before[str(critical)]=m.sha(critical)
result=m.build(plan,work/'stage',work/'synthetic_analysis.zip');checks=[]
assert result['bytes']<15000000 and result['protected_hashes_before_after_match'];checks.append('Synthetic standard ZIP below exact15000000 bytes, protected hashes checked')
assert all(m.sha(Path(p))==h for p,h in before.items());checks.append('All input and protected files unchanged')
assert m.verify_zip(work/'synthetic_analysis.zip')['members']==5;checks.append('All manifest members/CRC/UTF8/JSON verified')
with zipfile.ZipFile(work/'synthetic_analysis.zip')as z:
    record=json.loads(z.read('EVIDENCIA/record.json'));assert record['actual_zero']==0 and record['no_response']is None
checks.append('Zero and absent response remain distinguishable')
assert Path(result['clean_extraction']).is_dir();checks.append('Clean extraction and hashes verified')
for bad in('../outside.txt','NUL.txt','ok/COM1.txt','bad\\path.json'):
    try:m.member(bad)
    except ValueError:pass
    else:raise AssertionError('Unsafe archive member accepted')
checks.append('Traversal and Windows device names refused')
private=work/'configuracion_privada';private.mkdir();secret=b'SYNTHETIC_PRIVATE_BEARER_NOT_A_REAL_CREDENTIAL';(private/'fixture.token').write_bytes(secret)
leak=inputs/'leak.json';leak.write_text(json.dumps({'secret':secret.decode()}),encoding='utf8')
bad=json.loads(plan.read_text('utf8'));bad['files'].append({'source':str(leak),'archive':'EVIDENCIA/leak.json','sha256':m.sha(leak),'role':'primary'})
badpath=work/'badexport.json';badpath.write_text(json.dumps(bad),encoding='utf8')
try:m.plan_check(badpath)
except ValueError:checks.append('Known private bearer refused without printing it')
else:raise AssertionError('Private bearer packed')
report={'scope':'SYNTHETIC_PACKAGE_ONLY_NOT_FINAL_EXPORT','tests':len(checks),'checks':checks,'fixture':str(work),
        'Native_imports':0,'Native_ticks':0,'MCP_calls':0,'actual_project_critical_files_read':0,
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
out=ROOT/'pruebas'/('PACK_SINTETICO_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({'report':str(out),**report}))
