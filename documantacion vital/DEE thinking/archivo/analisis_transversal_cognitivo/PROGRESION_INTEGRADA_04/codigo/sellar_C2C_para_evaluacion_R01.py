"""Root-only CAL->EVAL status seal after a closed three-value calibration.

Stdlib only. No DEE/SQLite/state import, world query, owner or adoption. The
source/sensor VERSION and all protocol fields except status remain literal.
This seal is a scientific workflow action, never a positive experiment result.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os
P=Path(__file__).resolve().parents[1]

def sha(file):return hashlib.sha256(Path(file).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--system-root',type=Path,default=P/'estados/candidato_R02/sistema')
    ap.add_argument('--calibration-proof',type=Path,required=True)
    ap.add_argument('--criteria',type=Path,default=P/'control/C2C_CRITERIOS_PRE_EVALUACION_R01.json')
    a=ap.parse_args();system=a.system_root.resolve(strict=True)
    if system!=(P/'estados/candidato_R02/sistema').resolve(strict=True):raise ValueError('Only isolated S2 source, never original/product')
    for part in(system,system/'capacidades'):
        if part.is_symlink()or(getattr(part.stat(),'st_file_attributes',0)&0x400):raise ValueError('No reparse/junction source')
    proof=a.calibration_proof.resolve(strict=True);criteria=a.criteria.resolve(strict=True)
    if not proof.is_relative_to(P/'control')or not criteria.is_relative_to(P/'control'):raise ValueError('Actual preserved control evidence only')
    cal=json.loads(proof.read_text(encoding='utf-8-sig'));cr=json.loads(criteria.read_text(encoding='utf-8-sig'))
    if cal.get('schema')!='DEE.PI04.C2C.calibration.actual.R01'or cal.get('actual_owner_closed')is not True or cal.get('Native_reserve_executed')is not False:raise ValueError('Closed actual instrument calibration, no reserved use, required')
    if not str(cal.get('life','')).startswith('ECI02_PI03_REPRO_PI04_C2CCAL_')or [r.get('input')for r in cal.get('Q',[])]!=[0,4,5]:raise ValueError('Exact separate C2CCAL three-value history required')
    for row in cal['Q']:
        if row['reader'].get('choice')is None:raise ValueError('NULL calibration requires diagnosis, not automatic evaluation seal')
        if len(row.get('requests',[]))!=4 or not all(r['receipt']['status']=='applied'for r in row['requests']):raise ValueError('Complete four-input B calibration receipt set required')
        if row.get('feedback_inserted')is not False or row.get('efference_inserted')is not False:raise ValueError('Calibration unexpectedly acquired via feedback/efference')
    if cr.get('status')!='FIXED_BEFORE_C2C_EVALUATIVE_OPPORTUNITIES_NOT_A_RESULT'or cr['opportunities']['total_prepared_resources']!=26:raise ValueError('Actual preregistered26-resource criteria required')
    cap=system/'capacidades';file=cap/'PROTOCOLO_PI04_C2C_R01.json';old=file.read_bytes();p=json.loads(old.decode('utf-8-sig'))
    if p['status']!='SEALED_FOR_CALIBRATION'or p['schema']!='DEE.PI04.C2C.protocol.R01'or len(p['schedule'])!=26:raise ValueError('Exact sealed-calibration protocol26 required')
    draft_path=P/'codigo/PROTOCOLO_PI04_C2C_R01.json';draft=json.loads(draft_path.read_text(encoding='utf-8-sig'))
    if draft['status']!='DRAFT'or {k:v for k,v in p.items()if k!='status'}!={k:v for k,v in draft.items()if k!='status'}:raise ValueError('Any body change since frozen DRAFT must be an explicit new revision, not a status seal')
    sources={}
    for name,expected in p['dependencies_sha256'].items():
        if Path(name).name!=name or not name.endswith('.py'):raise ValueError('Bounded dependency basename only')
        actual=sha(cap/name)
        if actual!=expected:raise ValueError('Scientific dependency changed after calibration: '+name)
        sources[name]=actual
    if sha(cap/'pi04_coordinacion_central_C2C.py')!='0b3f2f72cbcd461561555c1168295f6d08c43a48ddeb4835791528df92632607':raise ValueError('Candidate module/VERSION changed')
    folder=P/'codigo/revisiones/C2C_PROTOCOLO_CAL_ANTES_EVAL_R01'
    if folder.exists():raise ValueError('Prior CAL literal protected; do not repeat seal')
    folder.mkdir(parents=True)
    with(folder/file.name).open('xb')as f:f.write(old);f.flush();os.fsync(f.fileno())
    if(folder/file.name).read_bytes()!=old:raise ValueError('Literal calibration protocol preservation failed')
    p['status']='SEALED_FOR_EVALUATION';new=(json.dumps(p,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    pending=file.with_name(file.name+'.C2C_EVAL.pending')
    with pending.open('xb')as f:f.write(new);f.flush();os.fsync(f.fileno())
    if file.read_bytes()!=old:raise ValueError('Concurrent protocol change; preserve pending')
    os.replace(pending,file)
    result={'schema':'DEE.PI04.C2C.protocol_seal.EVAL.R01','local_cut':datetime.datetime.now().astimezone().isoformat(),
        'protocol':str(file),'before_sha256':hashlib.sha256(old).hexdigest(),'after_sha256':sha(file),
        'literal_calibration_protocol':str(folder/file.name),'sources_checked':sources,
        'calibration_proof':{'path':str(proof),'sha256':sha(proof)},'criteria':{'path':str(criteria),'sha256':sha(criteria)},
        'only_status_changed':True,'module_VERSION_unchanged':True,'Native_imports':False,'Native_ticks':0,
        'scope':'Root chose to seal evaluation after actual instrument review. No useful learning/adoption result is implied.'}
    out=P/'control/C2C_PROTOCOLO_SELLADO_EVALUACION_R01.json'
    if out.exists():raise ValueError('Prior seal proof protected')
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
