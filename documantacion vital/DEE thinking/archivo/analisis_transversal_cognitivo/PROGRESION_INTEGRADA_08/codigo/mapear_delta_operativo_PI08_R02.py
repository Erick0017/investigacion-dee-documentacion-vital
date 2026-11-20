"""Read-only bounded Source->Product code proposal, not deployment/approval.
Only the preserved301-member source manifest,9declared A1 files and2explicit
administrative/launcher adaptations; no state/runtime/engine inventory.
"""
from pathlib import Path
import argparse,datetime,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';CS=P/'estados/RP_A01/sistema';BASE=C/'reproducibilidad/codigo_preservado/PI07_R03_LOCAL_FI_PRE34_R03'
SELECTORS=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for node in(p,*p.parents):
  if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked scoped source/target')
def main(a):
 out=a.salida.resolve()
 if out.exists()or not out.is_relative_to((P/'control').resolve()):raise ValueError('Fresh P8/control output only')
 register=P/'REGISTRO_CAMPANA.json';reg=read(register);basefile=BASE/'SISTEMA_CODIGO.json';manifest=read(basefile);deployed=read(P/'control/PI08_A1_HOOKS_APLICADOS_R04.json');names={r['file']for r in manifest['files']};names.update(r['file']for r in deployed['files']);overrides={'app/pi08_identidad_c2c_R01.py':H/'pi08_identidad_c2c_R02.py','app/usar_dee.py':H/'usar_dee_existente_PI08_R01.py'};names.update(overrides);rows=[];unchanged=[];excluded=[]
 for name in sorted(names):
  if name.startswith('procedencia/')or name=='capacidades/CATALOGO_CAPACIDADES.json':excluded.append({'file':name,'reason':'Historical before-image or live product catalogue, not a deployed code replacement.'});continue
  source=overrides.get(name,CS/name);target=C/'sistema'/name;regular(source);regular(target)
  if not source.is_file():raise ValueError('Required scoped source missing: '+name)
  after=sha(source);before=sha(target)if target.is_file()else None
  if after==before:unchanged.append({'file':name,'sha256':after});continue
  supported=(name.startswith(('app/','capacidades/'))and source.suffix in('.py','.json'))or name=='contratos/PI08_USO_OPERATIVO_R01.json'
  if not supported:raise ValueError('Different file requires explicit scoped review outside adapter allowlist: '+name)
  if source.suffix=='.json'and not Path(name).name.startswith('PROTOCOLO')and name!='contratos/PI08_USO_OPERATIVO_R01.json':raise ValueError('Different nonprotocol JSON cannot be silently deployed: '+name)
  rows.append({'file':name,'source':str(source),'sha256':after,'before_sha256':before,'bytes':source.stat().st_size,'role':'PREPARED_DIAGNOSTIC_PROFILE_NOT_COMMITTED'if name.startswith('contratos/')else'CODE_OR_IMMUTABLE_PROTOCOL'})
 protected={}
 for key,witness in reg['protected_before'].items():
  source=Path(witness['path'])
  # Existing RP is intentionally mutable by separately registered instruments;
  # code mapping never rolls back its current registry/tools.
  if source.is_relative_to(C/'reproducibilidad'):continue
  if sha(source)!=witness['sha256']:raise ValueError('A registered protected baseline changed before adoption: '+str(source))
  protected[str(source)]={'sha256':witness['sha256'],'unchanged_from_campaign_register':True}
 selectors={name:sha(C/name)for name in SELECTORS};result={'schema':'DEE.PI08.bounded_operational_delta.proposal.v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'approval':'PENDING_ROOT_REVIEW_NOT_DEPLOYED','source_system':str(CS),'target_system':str(C/'sistema'),'source_manifest':{'path':str(basefile),'sha256':sha(basefile),'member_count':len(manifest['files'])},'A1_deployment':{'path':str(P/'control/PI08_A1_HOOKS_APLICADOS_R04.json'),'sha256':sha(P/'control/PI08_A1_HOOKS_APLICADOS_R04.json')},'proposed_code_files':rows,'same_existing_product_files':unchanged,'excluded_not_for_deployment':excluded,'selectors_cas':selectors,'registered_protected_baseline':protected,'Native_executed':False,'code_or_product_modified':False,'scope':'A bounded source-manifest comparison for the one same-ID successor; no broad filesystem census, engine duplication or snapshot/state mutation.'}
 with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(out),'sha256':sha(out),'changed_files':len(rows),'changed_bytes':sum(r['bytes']for r in rows),'names':[r['file']for r in rows],'unchanged':len(unchanged),'excluded':len(excluded),'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',type=Path,required=True);main(ap.parse_args())
