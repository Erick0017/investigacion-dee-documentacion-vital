"""Root-invoked stdlib-only seal: preserve draft, verify hashes, set CAL status.

Does not run/import DEE, open SQLite, write a state, execute a life or install
code. It changes only the explicit new C2C protocol after exact source checks.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os
P=Path(__file__).resolve().parents[1]

def sha(file):return hashlib.sha256(Path(file).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--system-root',type=Path,default=P/'estados/candidato_R02/sistema')
    a=ap.parse_args();system=a.system_root.resolve(strict=True)
    expected=(P/'estados/candidato_R02/sistema').resolve(strict=True)
    if system!=expected:raise ValueError('Only the declared isolated PI04 S2 source tree, never product/original')
    for part in (system,system/'capacidades'):
        if part.is_symlink()or(getattr(part.stat(),'st_file_attributes',0)&0x400):raise ValueError('No reparse/junction source')
    cap=system/'capacidades';file=cap/'PROTOCOLO_PI04_C2C_R01.json'
    old=file.read_bytes();p=json.loads(old.decode('utf-8-sig'))
    if p['schema']!='DEE.PI04.C2C.protocol.R01'or p['status']!='DRAFT'or p['calibration_values']!=[0,4,5]:raise ValueError('Exact unexecuted B draft required; never reseal/rewrite a previous run')
    expected_code='0b3f2f72cbcd461561555c1168295f6d08c43a48ddeb4835791528df92632607'
    expected_sensor='11597f81fed67b54533fa58015a1aab65f537e92fa68dfbcddc6460bbfb005c4'
    if sha(cap/'pi04_coordinacion_central_C2C.py')!=expected_code or sha(cap/'pi04_sensor_central_C2C_R01.py')!=expected_sensor:raise ValueError('Exact reviewed C2C source/sensor mismatch')
    checked={}
    for name,h in p['dependencies_sha256'].items():
        if Path(name).name!=name or not name.endswith('.py'):raise ValueError('Bounded dependency basename only')
        actual=sha(cap/name)
        if actual!=h:raise ValueError('Dependency mismatch: '+name)
        checked[name]=actual
    before_dir=P/'codigo/revisiones/C2C_PROTOCOLO_DRAFT_ANTES_CAL_R01'
    if before_dir.exists():raise ValueError('Prior draft archive protected; do not repeat seal')
    before_dir.mkdir(parents=True)
    preserved=before_dir/file.name
    with preserved.open('xb')as out:out.write(old);out.flush();os.fsync(out.fileno())
    if preserved.read_bytes()!=old:raise ValueError('Literal draft preservation failed')
    p['status']='SEALED_FOR_CALIBRATION';new=(json.dumps(p,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    pending=file.with_name(file.name+'.C2C_CAL.pending')
    with pending.open('xb')as out:out.write(new);out.flush();os.fsync(out.fileno())
    if file.read_bytes()!=old:raise ValueError('Concurrent draft change detected; preserve pending and stop')
    os.replace(pending,file)
    proof={'schema':'DEE.PI04.C2C.protocol_seal.CAL.R01','local_cut':datetime.datetime.now().astimezone().isoformat(),
        'system_root':str(system),'protocol':str(file),'status':'SEALED_FOR_CALIBRATION','preserved_literal_draft':str(preserved),
        'before_sha256':hashlib.sha256(old).hexdigest(),'after_sha256':sha(file),'sources_checked':checked,
        'C2C_source_sha256':expected_code,'sensor_sha256':expected_sensor,'Native_imports':False,'Native_ticks':0,
        'only_protocol_status_changed':{k:v for k,v in p.items()if k!='status'}=={k:v for k,v in json.loads(old.decode('utf-8-sig')).items()if k!='status'}}
    out=P/'control/C2C_PROTOCOLO_SELLADO_CALIBRACION_R01.json'
    if out.exists():raise ValueError('Prior seal proof protected')
    with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
    print(json.dumps(proof,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
