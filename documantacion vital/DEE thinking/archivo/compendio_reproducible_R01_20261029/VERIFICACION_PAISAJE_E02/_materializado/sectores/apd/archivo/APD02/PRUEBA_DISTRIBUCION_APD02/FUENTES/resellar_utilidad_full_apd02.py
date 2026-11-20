"""Reuse the existing manifest/ZIP updater for exactly one proof-utility repair."""
import argparse,hashlib,importlib.util,json,shutil
from pathlib import Path
OLD='da08e86ce9fc67e9077780de60b481a2275c2e0a16545cf703c49674b13a8257'
NEW='8a346d38e26e9da3fac29d06993caccf395b9422cf0a12a0fed80564ee519c05'
FULL='2155e12a7753380cd2f6313c16475c5a54d4fcd847f66b8eecb024d11b95dcdc'
NAME='actualizaciones/probar_asistente2_distribuido.py'
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--origen',type=Path,required=True);p.add_argument('--colaborador',type=Path,required=True);p.add_argument('--helper',type=Path,required=True);p.add_argument('--sello',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();source=a.origen.resolve();root=a.colaborador.resolve();seal=read(a.sello);manifest=read(root/'actualizaciones/ARCHIVOS_GESTIONADOS.json');previous=read(root/'entregas/ULTIMA_ENTREGA.json');target=root/NAME
    if sha(target)!=OLD or manifest['members'][NAME]['sha256']!=OLD or sha(a.helper)!=NEW or sha(root/'entregas/cognitive_sistem_colaborador.zip')!=FULL:raise ValueError('Exact reviewed old/full/new utility bytes required')
    for row in seal['lives']:
        card=read(source/'sistema/estado/vidas'/row['life_id']/'VIDA.json')
        if card['snapshot_sha256']!=row['snapshot_sha256']or sha(source/'sistema'/card['snapshot'])!=row['snapshot_sha256']:raise ValueError('Protected selected science source moved')
    if sha(source/seal['manual']['name'])!=seal['manual']['sha256']:raise ValueError('Word authority moved')
    updater=root/'actualizaciones/actualizar.py';spec=importlib.util.spec_from_file_location('same_existing_updater',updater);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);b=module.Build(source);b.members={k:dict(v)for k,v in b.previous['members'].items()};args=argparse.Namespace(cerrar=seal['campaign'],verificacion=a.sello.resolve().relative_to(source).as_posix(),manual=seal['manual']['name'],vida=[]);b.prepare_release(args)
    backup=root/'actualizaciones/respaldos'/b.release/NAME;backup.parent.mkdir(parents=True,exist_ok=False);shutil.copy2(target,backup);shutil.copy2(a.helper,target)
    current=b.finish()
    if b.changed!=[NAME]or current['retired_members']:raise ValueError('Repair must change only this one utility, not actors, selected states, documents, launchers or old evidence')
    result=module.seal_zip(current);result['incremental']=module.seal_zip(current,b.changed);oldzip=root/'entregas'/('cognitive_sistem_colaborador.anterior.'+previous['release']+'.zip')
    if sha(oldzip)!=FULL:raise ValueError('The exact failed-attempt Full was not retained')
    receipt={'schema':'APD02.Full.proof_utility_only_revision.R02','new_native_ticks':0,'source_main_or_Word_changed':False,'changed_members':b.changed,'retired_members':current['retired_members'],'previous_full':{'file':str(oldzip),'sha256':FULL},'old_utility':{'backup':str(backup),'sha256':OLD},'new_utility_sha256':NEW,'existing_updater_sha256':sha(updater),'new_full':result,'scope':'Reuses Build.prepare_release, Build.finish and seal_zip from the existing updater. All previous managed members are retained unchanged, except the reviewed proof utility; no old campaign traversal, experiment, actor update or historical re-audit.'}
    with a.salida.open('x',encoding='utf8')as f:json.dump(receipt,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()

