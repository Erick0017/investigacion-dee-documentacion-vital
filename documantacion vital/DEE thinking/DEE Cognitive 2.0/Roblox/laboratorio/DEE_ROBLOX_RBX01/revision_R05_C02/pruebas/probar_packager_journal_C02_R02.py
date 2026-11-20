"""Permission delta tests; no ZIP or Native execution."""
from pathlib import Path
import ast,datetime,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'control/empacar_evidencia_C02_R02.py'
s=importlib.util.spec_from_file_location('_compact_journal_pack_fixture',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
prefix=ROOT/'native/MAIN_R02/sistema/estado/servicios_locales/ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02/RBX02_NATIVE_C02_R02'
journal=prefix/'events.jsonl';m.source_allowed(journal,'primary');m.validate_text('events.jsonl',journal.read_bytes())
tests=[dict(name='exact_compact_actor_journal_allowed_and_JSONL_readable',passed=True,bytes=journal.stat().st_size)]
card=ROOT/'native/MAIN_R02/sistema/estado/vidas/ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02/VIDA.json'
try:m.source_allowed(card,'primary')
except ValueError:tests.append(dict(name='full_native_state_path_still_denied',passed=True))
else:raise AssertionError('State path unexpectedly allowed')
a=ast.parse((ROOT/'control/empacar_evidencia_C02.py').read_text('utf8'));b=ast.parse(p.read_text('utf8'))
fa={n.name:ast.dump(n,include_attributes=False)for n in a.body if isinstance(n,ast.FunctionDef)}
fb={n.name:ast.dump(n,include_attributes=False)for n in b.body if isinstance(n,ast.FunctionDef)}
assert fa.keys()==fb.keys()and all(fa[k]==fb[k]for k in fa if k!='source_allowed')
assert m.LIMIT==15000000
tests.append(dict(name='all_other_packaging_integrity_hash_secret_size_methods_identical',passed=True))
plan=json.loads((ROOT/'control/finalexport_PLANTILLA_C02_R05.json').read_text('utf8'))
assert plan['finalized']is False
seen={};duplicates=[]
for row in plan['files']:
 if row['sha256']in seen:duplicates.append([seen[row['sha256']],row['source']])
 else:seen[row['sha256']]=row['source']
tests.append(dict(name='provisional_template_preserves_freeze_barrier',passed=True,files=len(plan['files']),content_duplicates=duplicates))
report=dict(schema='DEE.RBX01.C02.packager_actor_journal.offline.R02',tests=tests,Native_calls=0,MCP_calls=0,model_calls=0,
           zip_created=False,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
out=ROOT/'pruebas'/('PACKAGER_JOURNAL_R02_'+stamp+'.json');out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
