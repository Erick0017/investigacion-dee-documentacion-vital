"""Root-only isolated F1 code/context preparation. Default plan; never Native.

Uses the exact pre-A1 complete R03 capsule, never the current product source.
One imported CUT world plus two Runtime forks counts as three world slots.
No principal, code, selector or source-state mutation. --preparar is explicit.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, ast, hashlib, json, os, shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
BASE=RP/'codigo_preservado/PI07_R03_LOCAL_FI_PRE34_R03';MANIFEST=BASE/'SISTEMA_CODIGO.json'
STAGE=H/'FUENTES_F1_PI08_R02_PREPARADAS';DEST=P/'estados/F1_CUT_R02'
OUT=P/'control/SISTEMA_F1_PI08_R02_PREPARADO.json'
CAP_SHA='b9c3d9632f57af52d1325db4e2605f36f59c1f35dcba1e6e593f40a40c036060'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(x,t):
    if not x:raise ValueError(t)
def regular(p):
    p=Path(p)
    for n in (p,*p.parents):
        if n.exists():require(not n.is_symlink() and not(getattr(n.lstat(),'st_file_attributes',0)&1024),'No reparse source/destination')
    return p
def relative(s):
    q=PurePosixPath(s);require(not q.is_absolute() and ':' not in s and '\\' not in s and not any(x in ('.','..') for x in q.parts),'Unsafe code member')
    require(not s.startswith(('estado/','runtime/')) and not s.endswith(('.sqlite3','.db')),'No world-state file in capsule')
    return q
def put(p,j):
    regular(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')
def once(t,a,b):
    require(t.count(a)==1,'Exact frozen hook anchor changed: '+a[:70]);return t.replace(a,b)
def world_hooks(t):
    t=once(t,'        return result\n\n    def validate(self,payload):',
      "        from capacidades import pi08_diagnostico_cola_diagonal_R02 as f1\n        f1.operational_dependencies(self.a,self.work_directory)\n        for path in f1.code_files():\n            self.code_sha256['PI08F1/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n        return result\n\n    def validate(self,payload):")
    anchor="        if row is not None and str(row.get('modo','')).startswith('eci01-pi07-'):"
    require(t.count(anchor)==2,'Expected frozen validate/execute routers')
    i=t.index(anchor);t=t[:i]+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi08-f1-'):\n            from capacidades import pi08_diagnostico_cola_diagonal_R02 as f1\n            f1.validate(self.a,row)\n            return\n"+t[i:]
    i=t.index(anchor,t.index('    def execute(self,payload):'))
    t=t[:i]+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi08-f1-'):\n            from capacidades import pi08_diagnostico_cola_diagonal_R02 as f1\n            f1.validate(self.a,row)\n            self.before_mutation('PI08_F1_EXTERNAL_DIAGNOSTIC_RAW_CUT_NOT_LEARNED_REGULATION')\n            value=f1.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':f1.VERSION,'rows':[value]}\n"+t[i:]
    t=once(t,"        result['PI07']=pi07.operational_dependencies(self.a,self.work_directory)\n",
      "        result['PI07']=pi07.operational_dependencies(self.a,self.work_directory)\n        from capacidades import pi08_diagnostico_cola_diagonal_R02 as f1\n        result['PI08_F1']=f1.operational_dependencies(self.a,self.work_directory)\n")
    t=once(t,'    def external_uncertainty(self):\n',
      '    def external_uncertainty(self):\n        from capacidades import pi08_diagnostico_cola_diagonal_R02 as f1\n        if f1.uncertain(self.a):return True\n')
    ast.parse(t);return t
def queue_hooks(t):
    anchor="            if str(row.get('modo','')).startswith('eci01-pi07-'):"
    t=once(t,anchor,"            if str(row.get('modo','')).startswith('eci01-pi08-f1-'):\n                from capacidades.pi08_diagnostico_cola_diagonal_R02 import validate_literal\n                validate_literal(row)\n                continue\n"+anchor)
    ast.parse(t);return t

def main(a):
    protocol=read(H/'PROTOCOLO_F1_DIAGONAL_PI08_R02.json')
    require(protocol['status']=='PREPARED_REQUIRES_ROOT_SEAL_NOT_EXECUTABLE_YET','Preserve original prepared protocol')
    require(sha(H/'pi08_diagnostico_cola_diagonal_R02.py')==protocol['wrapper_sha256'],'Exact F1 wrapper pin')
    require(sha(MANIFEST)==CAP_SHA,'Exact complete PRE34 R03 capsule required')
    prefix=RP/'materiales/PI07_R03_POST4_T849645'
    require(sha(prefix/'EXPORTACION_SERVICIO.json')==protocol['source_manifest_sha256'],'Exact complete POST4 manifest')
    sources=[]
    for row in read(MANIFEST)['files']:
        q=relative(row['file']);src=regular(BASE.joinpath(*q.parts))
        require(src.is_file() and src.stat().st_size==row['bytes'] and sha(src)==row['sha256'],'Frozen capsule member mismatch '+row['file'])
        sources.append({**row,'source':str(src)})
    # The lossless recorder is already a pinned capsule dependency.
    codec=BASE/'capacidades/observador_global_PI05_R01.py'
    require(sha(codec)==protocol['codec_sha256'],'Exact existing lossless recorder')
    world=world_hooks((BASE/'app/mundo_genesis_apd05.py').read_text('utf-8-sig'))
    queue=queue_hooks((BASE/'app/cola_local.py').read_text('utf-8-sig'))
    life=protocol['allowed_lives']['raw_cut']
    if not a.preparar:
        print(json.dumps({'mode':'READ_ONLY_PLAN_NO_NATIVE','capsule_files':len(sources),'source_manifest_sha256':CAP_SHA,
          'destination':str(DEST),'life_id':life,'world_slots_reserved':3,'Native_tick_bound':2600,
          'hooks_AST_valid':True,'new_DOCX':False,'new_world_imported':False},ensure_ascii=False,indent=2));return
    require(not STAGE.exists() and not DEST.exists() and not OUT.exists(),'Fresh exact F1 destination only')
    require(not (RP/'EJECUCION_MATERIAL.lock').exists() and not (P/'PI08_ROOT_NATIVE_WRITER.lock').exists(),'Prepare only after current Root writer is closed')
    STAGE.mkdir()
    for row in sources:
        dst=STAGE/row['file'];dst.parent.mkdir(parents=True,exist_ok=True)
        with Path(row['source']).open('rb') as s,dst.open('xb') as d:shutil.copyfileobj(s,d)
        require(sha(dst)==row['sha256'],'Literal capsule copy mismatch')
    (STAGE/'app/mundo_genesis_apd05.py').write_text(world,encoding='utf-8',newline='\n')
    (STAGE/'app/cola_local.py').write_text(queue,encoding='utf-8',newline='\n')
    shutil.copy2(H/'pi08_diagnostico_cola_diagonal_R02.py',STAGE/'capacidades/pi08_diagnostico_cola_diagonal_R02.py')
    sealed={**protocol,'status':'SEALED_FOR_OPTIONAL_F1_NATIVE','sealed_at':datetime.now(timezone.utc).isoformat(),
      'Root_explicit_preparation':True,'preparation_only_No_Native':True,'source_code_manifest_sha256':CAP_SHA}
    put(STAGE/'capacidades/PROTOCOLO_F1_DIAGONAL_PI08_R02.json',sealed)
    rows=[]
    names=[r['file'] for r in sources]+['capacidades/pi08_diagnostico_cola_diagonal_R02.py','capacidades/PROTOCOLO_F1_DIAGONAL_PI08_R02.json']
    for name in names:
        q=STAGE/name
        if q.suffix=='.py':ast.parse(q.read_text('utf-8-sig'))
        rows.append({'file':name,'bytes':q.stat().st_size,'sha256':sha(q)})
    put(STAGE/'SISTEMA_CODIGO.json',{'schema':'DEE.PI08.F1.frozen_isolated_code.R02','files':rows,
      'source_capsule':str(BASE),'source_manifest_sha256':CAP_SHA,
      'only_hooks_modified':['app/cola_local.py','app/mundo_genesis_apd05.py'],'new_wrapper_and_protocol':True,
      'original_R03_and_engine_unchanged':True,'new_Native_ticks':0})
    system=DEST/'sistema';system.mkdir(parents=True)
    for row in rows:
        dst=system/row['file'];dst.parent.mkdir(parents=True,exist_ok=True)
        with (STAGE/row['file']).open('rb') as s,dst.open('xb') as d:shutil.copyfileobj(s,d)
        require(sha(dst)==row['sha256'],'Diagnostic system copy mismatch')
    (system/'estado/checkpoints').mkdir(parents=True)
    (system/'runtime').mkdir();wheel='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
    os.link(C/'sistema/runtime'/wheel,system/'runtime'/wheel)
    require(sha(system/'runtime'/wheel)==sha(C/'sistema/runtime'/wheel),'Shared official WHL differs')
    context={'schema':'DEE.PI08.F1.explicit_complete_pair_import.R02','life':life,'system':str(system),'prefix':str(prefix),
      'prefix_manifest_sha256':protocol['source_manifest_sha256'],'source_code_manifest_sha256':sha(STAGE/'SISTEMA_CODIGO.json'),
      'tool_sources':[{'file':n,'sha256':sha(RP/n)} for n in ('importar_diagnostico.py','observador_pasivo.py')],
      'never_select_or_promote':True,'world_slots_one_import_plus_two_forks':3,'Native_executed_by_preparation':False}
    cp=DEST/'CONTEXTO_EJECUCION.json';put(cp,context)
    require(all(sha(Path(row['source']))==row['sha256'] for row in sources),'Source capsule changed concurrently')
    put(OUT,{'schema':'DEE.PI08.F1.system_prepared.R02','status':'PREPARED_NO_WORLD_IMPORTED','at':datetime.now(timezone.utc).isoformat(),
      'context':str(cp),'context_sha256':sha(cp),'directory':str(DEST),'system':str(system),'life':life,
      'source_capsule_manifest_sha256':CAP_SHA,'isolated_manifest':str(STAGE/'SISTEMA_CODIGO.json'),
      'isolated_manifest_sha256':sha(STAGE/'SISTEMA_CODIGO.json'),'world_slots_reserved':3,'new_Native_ticks':0,
      'sealed_protocol_sha256':sha(STAGE/'capacidades/PROTOCOLO_F1_DIAGONAL_PI08_R02.json')})
    print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'Native_executed':False},ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--preparar',action='store_true');main(ap.parse_args())
