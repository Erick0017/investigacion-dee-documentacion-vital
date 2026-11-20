"""Register an explicitly CLOSED APD source for the existing updater; zero ticks."""
import argparse,hashlib,json,shutil
from datetime import datetime,timezone
from pathlib import Path
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def read(p):return json.loads(p.read_bytes())
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--corte',type=Path,required=True);p.add_argument('--manual',type=Path,required=True);p.add_argument('--manual-sha256',required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--closed-authorized',action='store_true');a=p.parse_args()
    if not a.closed_authorized:raise ValueError('Maintainer must explicitly authorize the final CLOSED source; neither current tick nor a favorable score is a closure')
    system=a.sistema.resolve();root=system.parent;collab=root.parent/'cognitive sistem';cut=read(a.corte);life=cut['main']['life_id'];record_path=system/'estado/vidas'/life/'VIDA.json';record=read(record_path)
    if life!='APD02_MAIN'or cut['persistent_service']['owner_stopped']is not True or cut['persistent_service']['pending_or_uncertain']or cut['issues']:raise ValueError('Declared actual stopped APD02 cut is incomplete or has integrity discrepancies')
    if(system/'estado/locks'/(record['world_id']+'.lock')).exists():raise ValueError('Selected source has a writer')
    if record['snapshot_sha256']!=cut['main']['snapshot_sha256']or sha(system/record['snapshot'])!=record['snapshot_sha256']:raise ValueError('Actual source moved after continuity cut')
    db=Path(cut['persistent_service']['journal'])
    if sha(db)!=cut['persistent_service']['journal_sha256']:raise ValueError('Complete paired source journal moved')
    if not cut['protected_sources']or not all(row['unchanged']and sha(Path(row['file']))==row['expected_sha256']for row in cut['protected_sources']):raise ValueError('A protected original differs')
    manual=a.manual.resolve(strict=True)
    if manual.parent!=root or manual.suffix.lower()!='.docx'or sha(manual)!=a.manual_sha256:raise ValueError('The final root Word authority differs')
    out=a.salida.resolve();out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise FileExistsError('Previous closed seal is never overwritten')
    managed=read(collab/'actualizaciones/ARCHIVOS_GESTIONADOS.json')['members'];helpers=[]
    for name in('actualizaciones/actualizar.py','actualizaciones/arrancar.py','actualizaciones/verificar_entrega_independiente.py','actualizaciones/probar_servicio_distribuido.py','actualizaciones/probar_asistente2_distribuido.py','actualizaciones/SELECCION.json','LEER_PRIMERO.md','documentos/INDICE.md'):
        source=collab/name
        if not source.exists():helpers.append({'file':name,'did_not_exist':True});continue
        known=managed.get(name)
        if known is None or sha(source)!=known['sha256']:raise ValueError('A personally modified/unmanaged helper must be preserved: '+name)
        target=out.parent/'respaldo_colaborador'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        if sha(source)!=sha(target):raise ValueError('Helper preimage differs')
        helpers.append({'file':name,'sha256':sha(source),'backup':str(target)})
    previous=collab/'entregas/cognitive_sistem_colaborador.zip';personal=[{'file':f.relative_to(collab).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted((collab/'trabajo_personal').rglob('*'))if f.is_file()]
    result={'schema':'DEE.APD02.closed_distribution_cut.v1','campaign':'APD02_CONTINUIDAD_CALIDAD_ADAPTACION','authorization':'Maintainer explicitly declared CLOSED; only distribution/exact-archive operational checks remain. No automatic global promotion.','registered_utc':datetime.now(timezone.utc).isoformat(),'new_native_ticks':0,'source_cut':{'file':str(a.corte),'sha256':sha(a.corte)},'lives':[{'life_id':life,'tick':record['physical']['tick'],'snapshot':record['snapshot'],'snapshot_sha256':record['snapshot_sha256'],'snapshot_bytes':(system/record['snapshot']).stat().st_size,'record_sha256':sha(record_path)}],'manual':{'name':manual.name,'bytes':manual.stat().st_size,'sha256':sha(manual),'visual_validation_claimed':False},'paired_source':{'file':cut['paired_export']['manifest'],'sha256':cut['paired_export']['manifest_sha256'],'journal_sha256':sha(db)},'previous_collaboration_zip':{'path':str(previous),'bytes':previous.stat().st_size,'sha256':sha(previous)},'personal_before':personal,'collaboration_helpers_preserved':helpers,'source_active':{'path':'sistema/estado/ACTIVO.json','sha256':sha(system/'estado/ACTIVO.json')},'scope':'Byte/identity registration of a closed real state, not new physical science or a global cognitive PASS.'}
    with out.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'seal':str(out),'sha256':sha(out),'life':life,'tick':record['physical']['tick'],'personal_files':len(personal)}))
if __name__=='__main__':main()
