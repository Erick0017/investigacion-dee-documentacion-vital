"""Register an explicitly closed MA02 cut; hashes/copies only, no native ticks."""
from datetime import datetime,timezone
import hashlib,json,shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02'
COLLAB=ROOT.parent/'cognitive sistem'


def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def main():
    folder=EV/'cierre/entrega';folder.mkdir(parents=True,exist_ok=True)
    target=folder/'SELLO_CORTE_DISTRIBUCION.json'
    if target.exists():raise FileExistsError('Existing distribution cut is not replaced.')
    continuity=ROOT/'CONTINUIDAD_MENTE_ACUMULATIVA_R02.json'
    parent=EV/'cierre/PROTECCION_Y_CORTE_FINAL.json'
    protected=json.loads(parent.read_bytes())
    if not all(row['record_unchanged']and row['snapshot_unchanged']for row in protected['protected']):raise ValueError('Protected sources changed.')
    cut=json.loads(continuity.read_bytes());lives=[]
    for row in cut['lives']:
        p=ROOT/'sistema'/row['snapshot'];digest=sha(p)
        if digest!=row['snapshot_sha256']:raise ValueError('Life snapshot mismatch.')
        card=ROOT/'sistema/estado/vidas'/row['life_id']/'VIDA.json'
        lives.append({'life_id':row['life_id'],'tick':row['physical']['tick'],'snapshot':row['snapshot'],
            'snapshot_sha256':digest,'snapshot_bytes':p.stat().st_size,'record_sha256':sha(card)})
    manuals=list(ROOT.glob('*1_13*.docx'))
    if len(manuals)!=1:raise ValueError('A unique current1.13Word is required.')
    manual=manuals[0]
    if sha(manual)!='be370184f8e0e2e561c3c28c8c12d9148ad1fae64c8651663ab15f76d1d98daa':raise ValueError('Word differs from authorized final cut.')
    previous=COLLAB/'entregas/cognitive_sistem_colaborador.zip'
    personal=[{'file':p.relative_to(COLLAB).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted((COLLAB/'trabajo_personal').rglob('*'))if p.is_file()]
    helpers=[]
    for name in('arrancar.py','verificar_entrega_independiente.py','SELECCION.json'):
        p=COLLAB/'actualizaciones'/name;backup=folder/'respaldo_colaborador'/name
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,backup)
        if sha(p)!=sha(backup):raise ValueError('Backup mismatch.')
        helpers.append({'file':'actualizaciones/'+name,'sha256':sha(p),'backup':str(backup)})
    result={'schema':'DEE.MA02.closed_distribution_cut.v1','campaign':'MENTE_ACUMULATIVA_R02',
        'registered_utc':datetime.now(timezone.utc).isoformat(),'authorization':'Parent explicitly declared CLOSED after physical/source/manual cut; only delivery checks remain.',
        'new_native_ticks':0,'native_results_not_recomputed':True,
        'source_continuity':{'path':str(continuity),'sha256':sha(continuity)},
        'protected_source_receipt':{'path':str(parent),'sha256':sha(parent)},'lives':lives,
        'manual':{'name':manual.name,'bytes':manual.stat().st_size,'sha256':sha(manual),'visual_validation':False},
        'previous_collaboration_zip':{'path':str(previous),'bytes':previous.stat().st_size,'sha256':sha(previous)},
        'personal_before':personal,'collaboration_helpers_preserved':helpers,
        'source_active':{'path':'sistema/estado/ACTIVO.json','sha256':sha(ROOT/'sistema/estado/ACTIVO.json')},
        'scope':'Identity and byte registration of a closed source cut, not a new scientific audit or global capability PASS.'}
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'path':str(target),'sha256':sha(target),'manual':result['manual'],'lives':len(lives),'personal_files':len(personal)},ensure_ascii=False))


if __name__=='__main__':main()
