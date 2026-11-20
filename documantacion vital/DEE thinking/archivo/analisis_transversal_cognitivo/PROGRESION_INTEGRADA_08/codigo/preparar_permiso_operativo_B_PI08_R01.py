"""Prepare conditional permission deltas ONLY under P8; no --apply exists.

Actual four-arm/causal/panel/reopening evidence and Root approval are required
before any deployment/adoption. B actor/episode/protocol/seal bytes remain
literal; only owner identity routing and the exact C2C permission are adapted.
"""
from pathlib import Path
from datetime import datetime, timezone
import ast, hashlib, json, shutil

P=Path(__file__).resolve().parents[1];H=P/'codigo';SOURCE=P/'estados/B_REAL_R01/sistema'
STAGE=H/'PERMISO_B_OPERATIVO_R01_PROPUESTO';PLAN=P/'control/PLAN_PERMISO_B_OPERATIVO_PI08_R01.json'

def require(ok,message):
 if not ok:raise ValueError(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x',encoding='utf8')as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write('\n')
def once(text,old,new):
 require(text.count(old)==1,'Exact conditional hook anchor changed')
 return text.replace(old,new,1)

def main():
 require(not STAGE.exists()and not PLAN.exists(),'Existing conditional stage protected')
 world_path=SOURCE/'app/mundo_genesis_apd05.py';dispatcher_path=SOURCE/'capacidades/pi04_dispatcher.py'
 world=world_path.read_text('utf8');dispatcher=dispatcher_path.read_text('utf8')
 world=once(world,"        permission.install()  # Exact prepared/COMMITTED profile; no Native policy.\n",
   "        permission.install()  # Exact prepared/COMMITTED profile; no Native policy.\n"
   "        from capacidades import pi08_permiso_B_operativo_R02 as permission_B\n"
   "        permission_B.install_legacy_access()\n"
   "        self.code_sha256['PI08B/operational_permission']=hashlib.sha256(Path(permission_B.__file__).read_bytes()).hexdigest()\n")
 lines=[];function=None;inserted=0
 for line in world.splitlines(keepends=True):
  stripped=line.strip()
  if stripped.startswith('def '):function=stripped[4:].split('(')[0]
  lines.append(line)
  if stripped=='from capacidades import pi08_revision_flexible_B_R01 as pi08b':
   indent=line[:len(line)-len(line.lstrip())]
   lines.append(indent+'from capacidades import pi08_permiso_B_operativo_R02 as permission_B\n')
   args="operation=row.get('modo'),for_dependencies=row.get('modo')=='eci01-pi08-b-estado'"if function in('validate','execute')else'for_dependencies=True'
   lines.append(indent+'pi08b=permission_B.component(self.a,pi08b,'+args+')\n');inserted+=1
 require(inserted==5,'All five B owner paths must use the same bounded permission boundary')
 world=''.join(lines)
 expr="_load('pi08_permisos_operativos_R01').configure_C2C(_load('pi05_permiso_principal_R01').configure(component,a),a)"
 require(dispatcher.count(expr)==2,'Both current C2C consumers must be routed')
 dispatcher=dispatcher.replace(expr,"_load('pi08_permiso_B_operativo_R02').configure_C2C("+expr+",a)")
 dispatcher=once(dispatcher,"    paths.append(root/'pi08_permisos_operativos_R01.py')\n",
   "    paths.append(root/'pi08_permisos_operativos_R01.py')\n    paths.append(root/'pi08_permiso_B_operativo_R02.py')\n")
 sources={'app/mundo_genesis_apd05.py':world.encode(),'capacidades/pi04_dispatcher.py':dispatcher.encode(),
   'capacidades/pi08_permiso_B_operativo_R02.py':(H/'pi08_permiso_B_operativo_R02.py').read_bytes(),
   'app/pi08_identidad_c2c_B_R01.py':(H/'pi08_identidad_c2c_B_R01.py').read_bytes()}
 STAGE.mkdir()
 for name,data in sources.items():
  ast.parse(data,filename=name);target=STAGE/name;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb')as f:f.write(data)
 for name,path in(('app/mundo_genesis_apd05.py',world_path),('capacidades/pi04_dispatcher.py',dispatcher_path)):
  target=STAGE/'ANTES'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
 # Explicitly nondeployable template. A later approved decision creates the
 # PREPARED_DIAGNOSTIC profile; Store.promote then seals it COMMITTED first.
 spec={};exec(compile(ast.Module(body=[node for node in ast.parse((H/'pi08_permiso_B_operativo_R02.py').read_bytes()).body if isinstance(node,(ast.Assign,ast.Import,ast.ImportFrom))],type_ignores=[]),'permission_constants_only','exec'),spec)
 template={'schema':'DEE.PI08.B.exact_operational_profile.v1','status':'DRAFT_NOT_DEPLOYABLE_MISSING_ACTUAL_GATES',
   'life_id':spec['LIFE'],'predecessor_selected':spec['PREDECESSOR'],'profile':'fisica_directa',
   'B_allowed_modes':['eci01-pi08-b-episodio','eci01-pi08-b-estado'],
   'C2C_allowed_modes':['eci01-pi04-c2c-oportunidad','eci01-pi04-c2c-estado'],
   'C2C_protocol_sha256':spec['C2C32'],'all_outer_FI_requests':True,'public_FI_domain':[0,20],
   'internal_C2C_FI_redirected':False,'frozen_files_sha256':spec['PINS'],
   'all_adoption_gates_met':False,'adoption_decision_sha256':None,
   'scope':'Identity/access permission only. No Native decoding, stimulus selection, action, expected answer, feedback or resupply policy.'}
 put(STAGE/'contratos/PI08_B_USO_OPERATIVO_R01.DRAFT.json',template)
 rows=[{'file':name,'source':str(STAGE/name),'bytes':len(data),'sha256':sha(STAGE/name)}for name,data in sources.items()]
 put(PLAN,{'schema':'DEE.PI08.B.conditional_operational_permission.prepared.R01','at_utc':datetime.now(timezone.utc).isoformat(),
   'approved_for_adoption':False,'applied':False,'Native_executed':False,'rows':rows,
   'source_code_before':{'app/mundo_genesis_apd05.py':sha(world_path),'capacidades/pi04_dispatcher.py':sha(dispatcher_path)},
   'literal_B_scientific_files':template['frozen_files_sha256'],'B_original_research_identity_guard_not_modified':True,
   'selected_B_namespace_identity_only':True,'dependency_uncertainty_can_be_checkpointed':True,
   'required_before_deployment':['Four completed real/none/yoked/reference arms and causal comparisons','Actual clone conservation panel plus last C2C','Source reopening/full-state persistence','Explicit Root adoption decision and fresh scoped process proof'],
   'required_adoption_order':['Whole same-ID B_REAL life/service/worker/checkpoints move with hashes/provenance; protect A861426',
     'Stage approved PREPARED_DIAGNOSTIC profile in product before unselected0reopening',
     'Map only C2C.life_id A->B_REAL using the exact same-ID relocation witness; save/reopen0Native',
     'Store.promoteCOMMITTED; immediately publish exact COMMITTED profile with actual decisionSHA before selectedOwner',
     'Refresh all six selectors/current-principal fields and existing continuation launcher',
     'Actual selected public FI/new-B opportunity and save/close; refresh only actual-cut descriptors'],
   'no_deployment_command_in_this_preparer':True})
 print(json.dumps({'plan':str(PLAN),'sha256':sha(PLAN),'conditional_files':len(rows),'Native_executed':False,'approved_for_adoption':False}))

if __name__=='__main__':main()
