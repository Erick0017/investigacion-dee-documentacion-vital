"""Root-only complete Discovery prefix -> exact D diagnostic base.

No permission adapter is invented here. Code preparation copies the existing
Discovery code and rebinds its administrative identity only. I4 must install
and close D adapters before Root supplies the final code-manifest SHA to import.
Default prints a plan. The coding agent never prepares/imports any world.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,re,shutil
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
SOURCE=P/'estados/DISCOVERY';ROOT12=P/'pares/NATIVE_POST12_T903603'
R12SHA='0cce6bcfe366551b52b0ca25c5959bd6e07ed4493221ec26b76af962c13b6553'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'
IDS={slug:PREFIX+slug+'_01'for slug in ('STAGE3_NONE','STAGE3_YOKE','DREPRO')}
PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
KEY='DEE.Cognitive.PI09.selective_registered_consultation.R02'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,message):
 if not ok:raise ValueError(message)
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(p,value):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def args_checked(a):
 pair=Path(a.prefijo).resolve(strict=True)
 require(pair.parent in {(P/'pares').resolve(),(RP/'materiales').resolve()}and not pair.is_symlink(),'Explicit stable pair in approved store only')
 require(re.fullmatch('[0-9a-f]{64}',a.manifest_sha256)and sha(pair/'EXPORTACION_SERVICIO.json')==a.manifest_sha256,'Actual complete Discovery manifest SHA required')
 m=read(pair/'EXPORTACION_SERVICIO.json');require(m['life_id']==PARENT and m['physical']['N']==67 and m['physical']['tick']>903603,'No old C/post12 seed substituted for actual post-panel Discovery')
 return pair,m,IDS[a.slug],P/'estados'/a.slug
def prepare(a,pair,m,life,dest):
 require(not dest.exists(),'Fresh unused diagnostic code destination only')
 verifier=load('D_pair_byte_contract',SOURCE/'sistema/app/importacion_emparejada.py');verifier.verify_export(pair)
 parser=load('D_passive_byte_parser',RP/'observador_pasivo.py');view=parser.snapshot_view(pair/'VIDA.deetsnap.gz')
 require(sha(ROOT12/'EXPORTACION_SERVICIO.json')==R12SHA,'Complete canonical12 ancestor changed')
 old=parser.snapshot_view(ROOT12/'VIDA.deetsnap.gz');meta=json.loads(view['metadata'][KEY])
 require(view['metadata'][KEY]==old['metadata'][KEY]and meta['ordinal']==12 and meta['ready']and not meta.get('pending')and not meta.get('uncertain'),'Old R02literal12 required; D is a new finite environment, never reset12')
 require(view['encoded_sha256']==m['snapshot_sha256']and all(view['physical'][k]==m['physical'][k]for k in ('N','tick','RAW_sha256','clocks_sha256')),'Full parent physical hash mismatch')
 sm=SOURCE/'SISTEMA_CODIGO_PI09.json';source_manifest=read(sm);system=dest/'sistema';system.mkdir(parents=True)
 for row in source_manifest['files']:
  name=row['file'];rel=Path(name);require(not rel.is_absolute()and ':'not in name and '..'not in rel.parts and not name.startswith(('estado/','runtime/')),'Relative code only')
  source=SOURCE/'sistema'/name;require(source.is_file()and not source.is_symlink()and sha(source)==row['sha256'],'Discovery code changed: '+name)
  target=system/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 scopefile=system/'capacidades/PI09_TRANSPORTE_HEREDADO_R02.json';scope=read(scopefile)
 scope['life_id']=life;scope['immediate_parent_Discovery']={'life_id':PARENT,'tick':view['physical']['tick'],'manifest_sha256':a.manifest_sha256,'snapshot_sha256':view['encoded_sha256']}
 scope['D_adapter_status']='PENDING_I4_EXACT_READONLY_ADAPTER_BEFORE_OWNER'
 scopefile.write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n','utf8')
 (system/'estado/checkpoints').mkdir(parents=True);(system/'runtime').mkdir()
 whl='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';wheel=C/'sistema/runtime'/whl
 require(sha(wheel)=='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c','Official shared engine differs');os.link(wheel,system/'runtime'/whl)
 rows=[{'file':p.relative_to(system).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(system.rglob('*'))if p.is_file()and not p.is_relative_to(system/'runtime')]
 manifest=dest/'SISTEMA_CODIGO_PI09.json';write(manifest,{'schema':'DEE.PI09.D.base_code_before_exact_adapter.R01','files':rows,'source_Discovery_manifest_sha256':sha(sm),'old_scientific_bodies_literal':True,'D_permissions_resolved':False})
 tools=('reproducir.py','importar_diagnostico.py','ejecutar_diagnostico.py','propietario_diagnostico.py','observador_pasivo.py')
 context={'schema':'DEE.reproduction.explicit_diagnostic.v1','life':life,'recipe':'PI09_D_BASE_'+a.slug,'variant':a.slug,'prefix':str(pair),'prefix_manifest_sha256':a.manifest_sha256,'system':str(system),'python':str(C/'motor/python313/python.exe'),'product':str(C),'destination':str(dest),'source_code_manifest_sha256':sha(manifest),'tool_sources':[{'file':name,'sha256':sha(RP/name)}for name in tools],'never_select_or_promote':True,'old_R02_ordinal12_literal':True,'D_adapter_required_before_owner':True}
 write(dest/'CONTEXTO_EJECUCION.json',context);write(dest/'PREPARACION_PI09.json',{'schema':'DEE.PI09.D.base_prepared_no_Native.R01','life_id':life,'system':str(system),'context_sha256':sha(dest/'CONTEXTO_EJECUCION.json'),'Native_executed':False,'D_permissions_resolved':False,'old_R02_literal12':True})
 print(json.dumps({'prepared_code_only':True,'life_id':life,'system':str(system),'source_tick':view['physical']['tick'],'requires_I4_D_adapter':True,'Native':0}))
def main(a):
 pair,m,life,dest=args_checked(a)
 if a.preparar:prepare(a,pair,m,life,dest)
 elif a.importar:
  require(re.fullmatch('[0-9a-f]{64}',a.codigo_cerrado_sha256 or '')and sha(dest/'SISTEMA_CODIGO_PI09.json')==a.codigo_cerrado_sha256,'Root must provide actual final code closure SHA after I4 adapters')
  require(read(dest/'PREPARACION_PI09.json').get('D_permissions_resolved')is True,'I4 actual adapter closure must declare ready before official import; this helper never grants permission')
  ledger=load('D_budget_same_identity',P/'codigo/ledger_PI09_misma_identidad_R01.py').ledger();budget=read(P/'REGISTRO_CAMPANA.json')['budget']
  require(ledger['world_count']+1<=budget['diagnostic_worlds_all_new'],'No world-budget override for optional controls/replay')
  base=load('D_official_same_pair_import',P/'codigo/clonar_C_PI09_R02.py');base.PAIR=pair;base.PAIR_SHA=a.manifest_sha256;a.vida=life;base.import_once(a,dest,dest/'sistema')
 else:print(json.dumps({'mode':'PLAN_ONLY_NO_NATIVE','source':str(pair),'manifest_sha256':a.manifest_sha256,'life_id':life,'source_tick':m['physical']['tick'],'system':str(dest/'sistema'),'next':['--preparar (code/base only)','I4 exact D adapter/closure without old metadata edits','--importar --codigo-cerrado-sha256 ACTUAL (Root0tick Native importer)','Root explicit D Owner only after closed import'],'optional_yoke_replay_not_budget_authorization':True,'Native':0},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--slug',choices=tuple(IDS),required=True);p.add_argument('--prefijo',required=True);p.add_argument('--manifest-sha256',required=True);p.add_argument('--codigo-cerrado-sha256');g=p.add_mutually_exclusive_group();g.add_argument('--preparar',action='store_true');g.add_argument('--importar',action='store_true');main(p.parse_args())
