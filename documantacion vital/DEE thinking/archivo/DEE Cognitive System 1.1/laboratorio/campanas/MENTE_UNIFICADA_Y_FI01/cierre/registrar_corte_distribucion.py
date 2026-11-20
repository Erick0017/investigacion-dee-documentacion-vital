"""Register an explicitly CLOSED MUFI cut; hashes/copies only, no native ticks."""
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01'
COLLAB=ROOT.parent/'cognitive sistem'


def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--manual',type=Path,required=True);parser.add_argument('--manual-sha256',required=True);parser.add_argument('--proteccion',type=Path,required=True);parser.add_argument('--vida',action='append',default=[],help='Explicit maintainer-selected life; no automatic latest-tick selection.');parser.add_argument('--manual-validacion-visual',action='store_true',help='Sólo con comprobante real de la edición final, no inferido de su extensión DOCX.');args=parser.parse_args()
    folder=EV/'cierre/entrega';folder.mkdir(parents=True,exist_ok=True)
    target=folder/'SELLO_CORTE_DISTRIBUCION.json'
    if target.exists():raise FileExistsError('Existing distribution cut is not replaced.')
    continuity=ROOT/'CONTINUIDAD_MENTE_UNIFICADA_Y_FI01.json'
    parent=args.proteccion.resolve(strict=True)
    protected=json.loads(parent.read_bytes())
    entries=protected.get('protected',protected.get('protected_identity_checks',protected.get('protected_original_checks')))
    if isinstance(entries,dict):entries=list(entries.values())
    if not entries or not all(row['record_unchanged']and row['snapshot_unchanged']for row in entries):raise ValueError('Protected sources changed or current comparison missing.')
    if protected.get('active_pointer_unchanged')is False:raise ValueError('Protected global active pointer changed')
    cut=json.loads(continuity.read_bytes());lives=[]
    selected=list(args.vida)
    if not selected:raise ValueError('This schema requires an explicit --vida list, not inference from a high tick or favorable output')
    for life in dict.fromkeys(selected):
        card=ROOT/'sistema/estado/vidas'/life/'VIDA.json';row=json.loads(card.read_bytes())
        if(ROOT/'sistema/estado/locks'/(row['world_id']+'.lock')).exists():raise ValueError('Selected life still has an active writer: '+life)
        p=ROOT/'sistema'/row['snapshot'];digest=sha(p)
        if digest!=row['snapshot_sha256']:raise ValueError('Life snapshot mismatch.')
        if life==cut.get('main',{}).get('life_id')and row['snapshot_sha256']!=cut['main']['snapshot_sha256']:raise ValueError('Selected principal moved after the closed continuity receipt')
        lives.append({'life_id':row['life_id'],'tick':row['physical']['tick'],'snapshot':row['snapshot'],
            'snapshot_sha256':digest,'snapshot_bytes':p.stat().st_size,'record_sha256':sha(card)})
    manual=args.manual.resolve(strict=True)
    if manual.parent!=ROOT or manual.suffix.lower()!='.docx'or sha(manual)!=args.manual_sha256:raise ValueError('The root Word differs from its explicitly authorized final bytes.')
    previous=COLLAB/'entregas/cognitive_sistem_colaborador.zip'
    personal=[{'file':p.relative_to(COLLAB).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted((COLLAB/'trabajo_personal').rglob('*'))if p.is_file()]
    helpers=[]
    managed=json.loads((COLLAB/'actualizaciones/ARCHIVOS_GESTIONADOS.json').read_bytes())['members']
    for name in('actualizaciones/actualizar.py','actualizaciones/arrancar.py','actualizaciones/verificar_entrega_independiente.py','actualizaciones/probar_servicio_distribuido.py','actualizaciones/SELECCION.json','LEER_PRIMERO.md','documentos/INDICE.md'):
        p=COLLAB/name;backup=folder/'respaldo_colaborador'/name
        if not p.exists():
            helpers.append({'file':name,'did_not_exist_before':True});continue
        expected=managed.get(name)
        if expected is None or sha(p)!=expected['sha256']:raise ValueError('Unmanaged or personally modified collaboration file preserved; resolve explicitly before replacing: '+name)
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,backup)
        if sha(p)!=sha(backup):raise ValueError('Backup mismatch.')
        helpers.append({'file':name,'sha256':sha(p),'backup':str(backup)})
    result={'schema':'DEE.MUFI.closed_distribution_cut.v1','campaign':'MENTE_UNIFICADA_Y_FI01',
        'registered_utc':datetime.now(timezone.utc).isoformat(),'authorization':'Parent explicitly declared CLOSED after physical/source/manual cut; only delivery checks remain.',
        'new_native_ticks':0,'native_results_not_recomputed':True,
        'source_continuity':{'path':str(continuity),'sha256':sha(continuity)},
        'protected_source_receipt':{'path':str(parent),'sha256':sha(parent)},'lives':lives,
        'manual':{'name':manual.name,'bytes':manual.stat().st_size,'sha256':sha(manual),'visual_validation':args.manual_validacion_visual},
        'previous_collaboration_zip':{'path':str(previous),'bytes':previous.stat().st_size,'sha256':sha(previous)},
        'personal_before':personal,'collaboration_helpers_preserved':helpers,
        'source_active':{'path':'sistema/estado/ACTIVO.json','sha256':sha(ROOT/'sistema/estado/ACTIVO.json')},
        'scope':'Identity and byte registration of a closed source cut, not a new scientific audit or global capability PASS.'}
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'path':str(target),'sha256':sha(target),'manual':result['manual'],'lives':len(lives),'personal_files':len(personal)},ensure_ascii=False))


if __name__=='__main__':main()
