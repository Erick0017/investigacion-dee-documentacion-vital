"""PLAN by default. Static PI11 stable-RP registration only with --aplicar.

No DEE import, owner, Native evolution or automatic material replay. Preserves
one complete historical prefix and exact code capsule, shares official engine.
Public listar/verificar/recalcular/reproducir remain the existing entry point.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,ast,hashlib,importlib.util,json,os,shutil

P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
PAIR=P/'pares/PRINCIPAL_REAL2_T947395';SOURCE=P/'estados/MAIN01/sistema';SOURCE_MANIFEST=P/'estados/MAIN01/SISTEMA_CODIGO_PI11.json'
RID='pi11_habitat16_familia_desde_REAL2_R01';CAP='PI11_HABITAT16_FAMILIA_R01';PREFIX='PI11_SOURCE_REAL2_T947395'
PAIR_NAME='reproducibilidad/materiales/PI11_REAL2_PRE_T947395'
CAP_NAME='reproducibilidad/codigo_preservado/PI11_HABITAT16_FAMILIA_R01'
ANALYSIS_NAME='reproducibilidad/evidencia/PI11_HABITAT16_R01'
TOOLS=('pi11_guardia_reproduccion_R01.py','pi11_vinculo_reproduccion_R01.py')
ANALYSIS_TOOLS=('pi11_recalculo_estable_R01.py','recalcular_PI11_R01.py')
SOURCE_PAIR_SHA='f80c72145dc5b20e1c0c066d0bab9755183eea6e7c7ef89c8ce33b8339788d19'
SOURCE_SNAPSHOT_SHA='fd7372b7f2adc9040866fab8adfaca0d79e0bd18e997c0abc0651fe4fa3c23dc'

def need(ok,why):
    if not ok:raise ValueError(why)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def sha(p):
    digest=hashlib.sha256()
    with Path(p).open('rb')as f:
        for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()
def regular(p):
    p=Path(p).absolute()
    for q in(p,*p.parents):need(not q.is_symlink()and(not q.exists()or not(getattr(q.lstat(),'st_file_attributes',0)&1024)),'No linked/reparse installation path')
    return p
def inside(root,name):
    need(isinstance(name,str),'Relative path string required');rel=PurePosixPath(name)
    need('\\'not in name and ':'not in name and not rel.is_absolute()and rel.parts and all(p not in('.','..')for p in rel.parts),'Unsafe relative member')
    p=regular(root.joinpath(*rel.parts));need(p.resolve().is_relative_to(root.resolve()),'Member escaped root');return p
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def new(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(encoded(value));f.flush();os.fsync(f.fileno())
def copy_file(src,dst,digest=None,size=None):
    regular(src);regular(dst);need(src.is_file()and not dst.exists(),'Exact source/new target required')
    if digest is not None:need(sha(src)==digest,'Source hash changed: '+str(src))
    if size is not None:need(src.stat().st_size==size,'Source size changed: '+str(src))
    dst.parent.mkdir(parents=True,exist_ok=True)
    with src.open('rb')as inp,dst.open('xb')as out:shutil.copyfileobj(inp,out);out.flush();os.fsync(out.fileno())
    need(sha(src)==sha(dst)and src.stat().st_size==dst.stat().st_size,'Literal copy mismatch')
def compare_swap(path,before,data):
    need(sha(path)==before,'Concurrent original mutation; do not overwrite '+str(path))
    temporary=path.with_name(path.name+'.PI11_INSTALL_WRITING');need(not temporary.exists(),'Previous partial installation preserved')
    with temporary.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
    need(sha(path)==before,'Concurrent original mutation before atomic replace')
    os.replace(temporary,path)

def checked_sources(args):
    for p in(P,H,C,RP,PAIR,SOURCE,SOURCE_MANIFEST,args.testigos,args.primarios,args.cierre):regular(p)
    closure=read(args.cierre)
    need(closure.get('closed_for_documentary_read')is True and isinstance(closure.get('closure_evidence'),(str,dict,list)),'Coordinator closed-export declaration and actual proof locator required')
    pair=read(PAIR/'EXPORTACION_SERVICIO.json')
    need(sha(PAIR/'EXPORTACION_SERVICIO.json')==SOURCE_PAIR_SHA and pair.get('schema')=='DEE.persistent_service.paired_export.v1'and pair.get('queue_journal_required')is True,'Exact complete historical REAL2 export')
    need(pair['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'and pair['physical']['N']==67 and pair['physical']['tick']==947395 and pair['snapshot_sha256']==SOURCE_SNAPSHOT_SHA,'Complete REAL2 source identity')
    need(sha(PAIR/'VIDA.deetsnap.gz')==SOURCE_SNAPSHOT_SHA,'Actual source snapshot changed')
    for row in pair['members']:
        source=inside(PAIR,row['file']);need(source.is_file()and source.stat().st_size==row['bytes']and sha(source)==row['sha256'],'Paired member changed: '+row['file'])
    code=read(SOURCE_MANIFEST);need(code.get('schema')=='DEE.PI11.exact_diagnostic_code_closure.R01'and code.get('PI11_actor_ready')is True,'Exact source MAIN01 ready code manifest')
    for row in code['files']:
        need(not row['file'].startswith(('estado/','runtime/')),'No Native state/engine in code capsule')
        source=inside(SOURCE,row['file']);need(source.is_file()and source.stat().st_size==row['bytes']and sha(source)==row['sha256'],'MAIN01 exact code changed: '+row['file'])
    expected=[]
    for n in range(16):
        source=args.testigos/('episodio_%04d.json'%n);regular(source);need(source.is_file(),'Actual closed MAIN sixteen witness missing')
        expected.append(read(source))
    need(all(row['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_MAIN01'for row in expected),'Expected trajectory must be actual MAIN01; not a selected favorable control')
    primary=[]
    for source in sorted(args.primarios.rglob('episodio_*.json')):
        regular(source);need(source.resolve().is_relative_to(args.primarios.resolve()),'Primary escaped closed export')
        value=read(source);need(value.get('version','').startswith('DEE.PI11.')and isinstance(value.get('life_id'),str)and type(value.get('ordinal'))is int,'Closed Native witness only')
        relative=source.relative_to(args.primarios).as_posix();primary.append({'file':relative,'bytes':source.stat().st_size,'sha256':sha(source)})
    need(primary,'At least one closed-primary set must be preserved')
    for name in(*TOOLS,*ANALYSIS_TOOLS,'pi11_adaptar_frontdoor_R01.py','pi11_construir_receta_R01.py'):
        source=H/name;need(source.is_file(),'Required stable tool missing');ast.parse(source.read_text('utf-8-sig'))
    return pair,code,expected,primary,closure

def main(args):
    args.testigos=regular(args.testigos).resolve(strict=True);args.primarios=regular(args.primarios).resolve(strict=True);args.cierre=regular(args.cierre).resolve(strict=True)
    pair,code,expected,primary,closure=checked_sources(args)
    targets=[C/PAIR_NAME,C/CAP_NAME,C/ANALYSIS_NAME,RP/'recetas'/(RID+'.json'),*(RP/name for name in TOOLS)]
    for target in targets:regular(target);need(not target.exists(),'Prior installation/partial output preserved: '+str(target))
    frontdoor=RP/'reproducir.py';resources=RP/'RECURSOS.json';before={'frontdoor':sha(frontdoor),'resources':sha(resources),'ACTIVO':sha(C/'sistema/estado/ACTIVO.json')}
    delta=load('PI11_pure_frontdoor_delta',H/'pi11_adaptar_frontdoor_R01.py');proposed=delta.adapt_frontdoor(frontdoor.read_text('utf-8-sig'))
    builder=load('PI11_pure_frozen_recipe_builder',H/'pi11_construir_receta_R01.py')
    need(not any((RP/name).exists()for name in TOOLS),'New helper names only')
    plan={'schema':'DEE.PI11.stable_reproduction.installation.R01','mode':'APPLY_STATIC_ONLY'if args.aplicar else'PLAN_ONLY',
          'prefix_files':len(pair['members']),'prefix_bytes':sum(row['bytes']for row in pair['members']),
          'code_files':len(code['files']),'prefix_target':str(C/PAIR_NAME),'code_target':str(C/CAP_NAME),'analysis_target':str(C/ANALYSIS_NAME),
          'original_hashes':before,'source_pair_manifest_sha256':SOURCE_PAIR_SHA,'source_code_manifest_sha256':sha(SOURCE_MANIFEST),
          'expected_opportunities':16,'closed_primary_files':len(primary),'Native_imported':False,'Native_ticks':0,
          'source_engine_shared_not_copied':True,'selected_principal_modified':False,'registration_does_not_mean_material_replay':True}
    if not args.aplicar:print(json.dumps(plan,ensure_ascii=False,indent=2));return
    need(not(P/'PI11_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'One writer: wait for coordinator Native close before static registration')
    backup=P/'control/INSTALACION_REPRODUCCION_PI11_R01';need(not backup.exists(),'Prior partial registration preserved; reconcile instead of repeat')
    backup.mkdir();new(backup/'INTENCION.json',plan);copy_file(frontdoor,backup/'reproducir_ANTES.py',before['frontdoor']);copy_file(resources,backup/'RECURSOS_ANTES.json',before['resources'])
    # One literal full operational prefix. Large stores are not multiplied per capability.
    target=C/PAIR_NAME;target.mkdir(parents=True)
    for row in pair['members']:copy_file(inside(PAIR,row['file']),inside(target,row['file']),row['sha256'],row['bytes'])
    copy_file(PAIR/'EXPORTACION_SERVICIO.json',target/'EXPORTACION_SERVICIO.json',SOURCE_PAIR_SHA)
    for name in pair.get('empty_directories_preserved',[]):inside(target,name).mkdir(parents=True,exist_ok=True)
    # Exact reached actor/source code only; no state or second motor.
    capsule=C/CAP_NAME;capsule.mkdir(parents=True)
    for row in code['files']:copy_file(inside(SOURCE,row['file']),inside(capsule,row['file']),row['sha256'],row['bytes'])
    capsule_manifest={'schema':'DEE.PI11.stable_code_capsule.R01','source_MAIN01_code_manifest_sha256':sha(SOURCE_MANIFEST),
                      'source_code_literal':True,'state_or_engine_included':False,'files':code['files']}
    new(capsule/'SISTEMA_CODIGO.json',capsule_manifest)
    analysis=C/ANALYSIS_NAME;analysis.mkdir(parents=True)
    for name in ANALYSIS_TOOLS:copy_file(H/name,analysis/name)
    new(analysis/'CIERRE_DOCUMENTAL.json',closure)
    for row in primary:copy_file(inside(args.primarios,row['file']),inside(analysis/'primarios',row['file']),row['sha256'],row['bytes'])
    analysis_rows=[]
    for source in sorted(analysis.rglob('*')):
        if source.is_file():analysis_rows.append({'file':source.relative_to(analysis).as_posix(),'bytes':source.stat().st_size,'sha256':sha(source)})
    new(analysis/'MANIFIESTO_ESTABLE.json',{'schema':'DEE.PI11.closed_documentary_material.R01','files':analysis_rows})
    for name in TOOLS:copy_file(H/name,RP/name)
    prefix={'product_relative':PAIR_NAME,'manifest_sha256':SOURCE_PAIR_SHA,'life_id':pair['life_id'],'tick':947395,'snapshot_sha256':SOURCE_SNAPSHOT_SHA}
    analysis_entry={'interface':'DEE.recalculation.root_outdir.v1','product_relative':ANALYSIS_NAME,
                    'manifest':'MANIFIESTO_ESTABLE.json','manifest_sha256':sha(analysis/'MANIFIESTO_ESTABLE.json'),'recalculation_script':'pi11_recalculo_estable_R01.py'}
    recipe=builder.build_recipe(expected,prefix,sha(RP/TOOLS[1]),sha(RP/TOOLS[0]),analysis_entry)
    new(RP/'recetas'/(RID+'.json'),recipe)
    updated=read(resources);need(PREFIX not in updated['pairs']and CAP not in updated.get('code_capsules',{}),'Recipe keys already registered')
    updated['pairs'][PREFIX]=prefix;updated.setdefault('code_capsules',{})[CAP]={'product_relative':CAP_NAME,'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(capsule/'SISTEMA_CODIGO.json')}
    compare_swap(resources,before['resources'],encoded(updated));compare_swap(frontdoor,before['frontdoor'],proposed.encode('utf8'))
    need(sha(C/'sistema/estado/ACTIVO.json')==before['ACTIVO'],'Static reproduction registration changed ACTIVO')
    plan.update(mode='REGISTERED_STATIC_PENDING_PUBLIC_CHECK_AND_NATIVE_REPLAY',files_after={'frontdoor':sha(frontdoor),'resources':sha(resources),'recipe':sha(RP/'recetas'/(RID+'.json'))},
                preserved_complete_prefix=str(target),prefix_manifest_sha256=sha(target/'EXPORTACION_SERVICIO.json'),capsule_manifest_sha256=sha(capsule/'SISTEMA_CODIGO.json'),analysis_manifest_sha256=sha(analysis/'MANIFIESTO_ESTABLE.json'))
    new(backup/'REGISTRO_COMPLETADO.json',plan);print(json.dumps(plan,ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--testigos',type=Path,required=True);parser.add_argument('--primarios',type=Path,required=True);parser.add_argument('--cierre',type=Path,required=True);parser.add_argument('--aplicar',action='store_true')
    main(parser.parse_args())
