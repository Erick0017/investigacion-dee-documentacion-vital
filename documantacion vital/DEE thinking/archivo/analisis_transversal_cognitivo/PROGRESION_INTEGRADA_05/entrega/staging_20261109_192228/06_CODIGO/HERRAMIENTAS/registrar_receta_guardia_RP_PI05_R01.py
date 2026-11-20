"""Root-only additive RP JSON registration. No engine imports or executions.

Requires full materials ALREADY preserved inside stable RP. Default produces a
reviewable plan only; --aplicar is a CAS update, never a promotion/MAIN change.
Existing RP Python code and all prior recipes remain byte-identical.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,json,os,sqlite3,uuid
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
STAGE=H/'RP_GUARDIA_PI05_R01_PREPARADA';NAME='pi05_guardia_y_sham_transito_R01';ALIAS='PI03_PI05_REAL_PREFI_T817876'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text('utf8-sig'))
def regular(p):
    for q in(p,*p.parents):
        if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No reparse material/catalog path')
def members(root,rows):
    count=0;total=0;seen=set()
    for r in rows:
        rel=Path(r['file'])
        if rel.is_absolute()or '..'in rel.parts or r['file']in seen:raise ValueError('Unsafe/repeated preserved member')
        p=root/rel;regular(p)
        if not p.resolve().is_relative_to(root.resolve())or not p.is_file()or p.stat().st_size!=r['bytes']or sha(p)!=r['sha256']:raise ValueError('Material differs: '+str(p))
        seen.add(r['file']);count+=1;total+=r['bytes']
    return {'members':count,'bytes':total}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--capsula',type=Path,required=True);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args()
    capsule=a.capsula.resolve(strict=True);regular(capsule)
    if not capsule.is_relative_to((RP/'codigo_preservado').resolve()):raise ValueError('Complete capsule already inside stable RP only')
    capmanifest=capsule/'SISTEMA_CODIGO.json';cap=read(capmanifest);capcheck=members(capsule,cap['files'])
    required={'gestionar.py','app/lives.py','app/importacion_emparejada.py','app/cola_local.py','app/mundo_genesis_apd05.py',
       'capacidades/pi05_guardia_transito_R01.py','capacidades/PROTOCOLO_PI05_GUARDIA_R01.json','capacidades/pi05_transito_causal_R01.py','capacidades/observador_global_PI05_R01.py'}
    if not required<={x['file']for x in cap['files']}:raise ValueError('A4file patch is not the complete executable Cognitive capsule')
    request=read(STAGE/'SOLICITUD_MATERIALES.json')
    if sha(capsule/'capacidades/pi05_guardia_transito_R01.py')!=request['frozen_guard_module']['sha256']or sha(capsule/'capacidades/PROTOCOLO_PI05_GUARDIA_R01.json')!=request['frozen_guard_protocol']['sha256']:
        raise ValueError('Guard source/protocol differs; preserve a new explicitly versioned recipe')
    pair=RP/'materiales'/ALIAS;regular(pair);pm=pair/'EXPORTACION_SERVICIO.json';p=read(pm)
    if sha(pm)!=request['complete_pair']['manifest_sha256']or p['schema']!='DEE.persistent_service.paired_export.v1'or p['physical']['N']!=67 or p['physical']['tick']!=817876:
        raise ValueError('Exact complete qualified preFI pair required')
    paircheck=members(pair,p['members'])
    db=pair/'cola.sqlite3'
    if any(Path(str(db)+s).exists()for s in('-wal','-shm','-journal')):raise ValueError('Standalone frozen transport required')
    q=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        if q.execute('pragma integrity_check').fetchone()[0]!='ok':raise ValueError('Frozen queue integrity failure')
    finally:q.close()
    configfile=RP/'RECURSOS.json';old=configfile.read_bytes();cfg=json.loads(old);new=copy.deepcopy(cfg)
    pairentry={'alias':ALIAS,'product_relative':pair.relative_to(C).as_posix(),'manifest_sha256':sha(pm),'life_id':p['life_id'],
       'tick':817876,'members':paircheck['members'],'bytes':paircheck['bytes'],
       'source_manifest':str(P/'pares/REAL_PREFI_T817876/EXPORTACION_SERVICIO.json'),'source_manifest_sha256':sha(pm),
       'scope':'Stable complete physical preFI prefix; preserved history, not a second principal or acquisition fromT0'}
    capentry={'product_relative':capsule.relative_to(C).as_posix(),'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(capmanifest)}
    for collection,key,entry,identitykeys in((new.setdefault('pairs',{}),ALIAS,pairentry,('product_relative','manifest_sha256','life_id','tick')),
         (new.setdefault('code_capsules',{}),'PI05_TRANSITO_GUARDIA_R01',capentry,('product_relative','manifest_sha256'))):
        if key in collection:
            if any(collection[key].get(k)!=entry[k]for k in identitykeys):raise ValueError('Stable alias already points to different material')
        else:collection[key]=entry
    src=STAGE/'recetas'/(NAME+'.json');recipebytes=src.read_bytes();recipe=json.loads(recipebytes);target=RP/'recetas'/(NAME+'.json')
    if recipe['verification']['state']!='PREPARADA_REPLAY_NATIVE_PENDIENTE':raise ValueError('No fictitious Native verification on registration')
    if target.exists()and target.read_bytes()!=recipebytes:raise ValueError('Existing recipe protected')
    critical=[C/'sistema/estado/ACTIVO.json',C/'sistema/estado/vidas/ECI02_PI03_MAIN/VIDA.json']
    card=read(critical[1]);critical.append(C/'sistema'/card['snapshot'])
    hashes={str(x):sha(x)for x in critical}
    proof={'schema':'DEE.PI05.RP.additive_registration.R01','applied':False,'Native_executed':False,'new_ticks':0,
       'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'RP_Python_or_gestor_modified':False,
       'original_resources_sha256':hashlib.sha256(old).hexdigest(),'recipe':NAME,'recipe_sha256':sha(src),
       'new_pair':pairentry,'new_code_capsule':capentry,'code_material_verified':capcheck,'pair_verified':paircheck,
       'principal_or_selectors_modified':False,'protected_critical_before':hashes,
       'scientific_scope':'PREPARADA prediction/evaluation recipe, no Native replay verified or main capacity implied.'}
    report=P/'control'/('RP_GUARDIA_PI05_R01_'+('REGISTRADA'if a.aplicar else'PLAN')+'.json')
    if report.exists():raise ValueError('Prior RP registration proof protected')
    if a.aplicar:
        backup=STAGE/'RECURSOS_ANTES_REGISTRO.json'
        if backup.exists()and backup.read_bytes()!=old:raise ValueError('Prior CAS origin differs')
        if not backup.exists():backup.write_bytes(old)
        if configfile.read_bytes()!=old:raise ValueError('Concurrent RP catalog update before CAS')
        if not target.exists():
            with target.open('xb')as f:f.write(recipebytes)
        temp=configfile.with_name(configfile.name+'.PI05_'+uuid.uuid4().hex+'.tmp')
        with temp.open('x',encoding='utf8')as f:json.dump(new,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
        if configfile.read_bytes()!=old:raise ValueError('Concurrent RP update; prepared temp preserved, no overwrite')
        os.replace(temp,configfile);proof['applied']=True;proof['resources_after_sha256']=sha(configfile)
    after={str(x):sha(x)for x in critical}
    if after!=hashes:raise RuntimeError('Protected principal changed concurrently; no immutable-allproject claim')
    proof['protected_critical_after']=after;proof['selected_critical_unchanged']=True
    report.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
