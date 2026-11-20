"""Stage prospective R02 permission, preserving unused R01 stages."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'pi10_permiso_operativo_R01.py';dst=H/'pi10_permiso_operativo_R02.py';t=src.read_text('utf8')
for old,new in(('DEE.PI10.exact_public_permission.R01','DEE.PI10.exact_public_permission.R02'),('DEE.PI10.exact_operational_permission.v1','DEE.PI10.exact_operational_permission.v2'),('PI10_REAL_01','PI10_REAL2_01'),('DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01','DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02'),('PROTOCOLO_PI10_R01.json','PROTOCOLO_PI10_R02.json'),('18<=m[\'ordinal\']<=24','12<=m[\'ordinal\']<=18'),("m.get('ordinal',0)<18","m.get('ordinal',0)<12"),('Real18+','Real12+')):
 assert old in t,old;t=t.replace(old,new)
old="p.get('source_P0_manifest_sha256')==P0_SHA";new="p.get('source_P02_manifest_sha256')==__import__('capacidades.pi10_transporte_ancestral_R01',fromlist=['config']).config()['source_main_manifest_sha256']";assert t.count(old)==1;t=t.replace(old,new)
anchor="def acquired(a):\n";extra="""def acquired(a):
 oldkey='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01';oldliteral=entries(a)[oldkey];old=json.loads(oldliteral)
 need(old.get('ready')and not old.get('admitted')and old['ordinal']==0 and not old['rows']and not old.get('pending')and not old.get('uncertain'),'R01 neutral preparation remains literal, never four acquired adverse episodes')
""";assert t.count(anchor)==1;t=t.replace(anchor,extra)
anchor="m=json.loads(entries(a)[KEY]);";replacement=anchor+"need(m.get('preparation_life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_P02_01'and m.get('source_R01_P0_metadata_sha256')==hashlib.sha256(oldliteral.encode('utf8')).hexdigest(),'Actual R02 neutral-P02 genealogy and R01-P0 history required');";assert t.count(anchor)==1;t=t.replace(anchor,replacement)
anchor=" from capacidades import pi09_permiso_operativo_D_R01 as old\n previous=old.configure_C2C\n old.configure_C2C=lambda component,a:configure_C2C(component,a)if applies(a)else previous(component,a)"
replacement=""" from capacidades import pi09_permiso_operativo_D_R01 as old,pi04_dispatcher as dispatcher
 # PI04 uses its own importlib namespace. Bind that actual consumer as well
 # as the ordinary module; no scientific function body or Native field edits.
 for module in(old,dispatcher._load('pi09_permiso_operativo_D_R01')):
  previous=module.configure_C2C
  module.configure_C2C=lambda component,a,_old=previous:configure_C2C(component,a)if applies(a)else _old(component,a)"""
assert t.count(anchor)==1;t=t.replace(anchor,replacement)
ast.parse(t)
if dst.exists():assert dst.read_text('utf8')==t
else:
 with dst.open('x',encoding='utf8')as f:f.write(t)
print(json.dumps({'file':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'Native':0,'product_modified':False,'contract_filename_compatible':'PI10_USO_OPERATIVO_R01.json','schema':'DEE.PI10.exact_operational_permission.v2'}))
