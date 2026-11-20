"""Root-only one conservation code/context clone from the full closed B_REAL.

Default is a plan. --preparar copies only the exact existing B code and writes
the fresh explicit import context. It creates no Native world and never changes
A/B_REAL, their resources, protocols, selectors or historical transport IDs.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, ast, hashlib, json, os, shutil

P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
DEST=P/'estados/B_CONSERVACION_R01';SOURCE=P/'estados/B_REAL_R01/sistema'
OUT=P/'control/SISTEMA_CONSERVACION_B_PI08_R01_PREPARADO.json'

def require(ok,text):
    if not ok:raise ValueError(text)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
    for node in(p,*p.parents):
        require(not node.exists()or not(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024),'No linked source/target')
def put(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

def main(args):
    seal=read(H/'SELLO_PI08_B_R01.json');life=seal['conservation_life_id']
    require(life=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_CONSERVACION_01','Exact prospectively fixed conservation identity required')
    if not args.preparar:
        print(json.dumps({'mode':'PLAN_ONLY_NO_NATIVE','life_id':life,'destination':str(DEST),'source_code':str(SOURCE),
                          'requires':'Actual full closed B_REAL18 pair at875451','Native_executed':False}));return
    require(args.prefijo is not None,'Explicit complete B_REAL prefix required')
    pair=Path(args.prefijo).resolve(strict=True);regular(pair)
    require(pair.name=='PI08_B_REAL_POST18_T875451'and pair.parent in((P/'pares').resolve(),(RP/'materiales').resolve()),'One bounded closed18 source prefix only')
    manifest=read(pair/'EXPORTACION_SERVICIO.json');real=seal['research_life_ids']['real']
    require(manifest['life_id']==real and manifest['physical']['tick']==875451,'Actual B_REAL18 physical source required')
    closedfile=P/'control/PI08_B_REAL_R02.json';closed=read(closedfile)
    require(sha(closedfile)=='f57c6039a48112371454b3d35f67bcfd579d1851230d35b5085570e1eb7a5531'and closed['closed']is True and closed['opportunities_completed']==18,'Actual closed18 proof required')
    source_card=read(SOURCE/'estado/vidas'/real/'VIDA.json')
    require(source_card['snapshot_sha256']==manifest['snapshot_sha256']and source_card['physical']==manifest['physical'],'B_REAL changed after export')
    require(not DEST.exists()and not OUT.exists(),'Unused conservation slot/destination only; never overwrite')
    require(not(RP/'EJECUCION_MATERIAL.lock').exists(),'RP writer remains')
    # Existing bounded manifest, not a recursive state/source inventory.
    codefile=H/'FUENTES_B_PI08_R02_PREPARADAS/SISTEMA_CODIGO.json';code=read(codefile)
    for row in code['files']:
        name=row['file'];require(not name.startswith(('estado/','runtime/'))and not name.endswith('.sqlite3'),'No state/engine copied as code')
        source=SOURCE/name;regular(source);require(source.is_file()and sha(source)==row['sha256'],'Used B source differs: '+name)
    system=DEST/'sistema';system.mkdir(parents=True)
    for row in code['files']:
        source=SOURCE/row['file'];target=system/row['file'];target.parent.mkdir(parents=True,exist_ok=True)
        with source.open('rb')as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
        require(sha(source)==sha(target)==row['sha256'],'Exact source changed/copied incorrectly')
        if target.suffix=='.py':ast.parse(target.read_text('utf-8-sig'))
    (system/'estado/checkpoints').mkdir(parents=True);(system/'runtime').mkdir()
    wheel='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';os.link(C/'sistema/runtime'/wheel,system/'runtime'/wheel)
    context={'schema':'DEE.PI08.B.conservation_complete_import.v1','life':life,'system':str(system),'prefix':str(pair),
             'prefix_manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),'source_code_manifest_sha256':sha(codefile),
             'source_B_REAL_proof':{'path':str(closedfile),'sha256':sha(closedfile)},'never_select_or_promote':True,
             'tool_sources':[{'file':name,'sha256':sha(RP/name)}for name in('importar_diagnostico.py','observador_pasivo.py')],
             'directory_transport_supplement':{'source':str(H/'directorios_pareados_PI08_R01.py'),'sha256':sha(H/'directorios_pareados_PI08_R01.py')},
             'Native_executed_by_preparation':False}
    contextfile=DEST/'CONTEXTO_EJECUCION.json';put(contextfile,context)
    item={'directory':str(DEST),'system':str(system),'life':life,'context':str(contextfile),'context_sha256':sha(contextfile)}
    put(OUT,{'schema':'DEE.PI08.B.conservation_system.prepared.v1','recorded_utc':datetime.now(timezone.utc).isoformat(),
             'context':item,'code_files':len(code['files']),'source_code_manifest':str(codefile),'source_code_manifest_sha256':sha(codefile),
             'source_B_REAL_not_modified':True,'Native_executed':False,'new_world_created':False,
             'next':'Root official import once, directory supplement before firstOwner, then ejecutar_conservacion_B_PI08_R02.py.'})
    print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'context':item,'Native_executed':False}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prefijo');p.add_argument('--preparar',action='store_true');main(p.parse_args())
