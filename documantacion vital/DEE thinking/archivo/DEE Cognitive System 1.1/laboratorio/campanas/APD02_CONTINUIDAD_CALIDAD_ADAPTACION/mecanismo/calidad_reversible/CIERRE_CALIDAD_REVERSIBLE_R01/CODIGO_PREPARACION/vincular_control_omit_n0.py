"""Bind an OMIT control to the SAME closed paired parent; no engine or ticks.

The fixed material is supplied by Root. Only operational identity/prefix and
session feedback real->omit may differ from the resolved MAIN protocol.
"""
import argparse,copy,hashlib,json,re,sqlite3
from pathlib import Path,PurePosixPath

FIXED_SHA='7b3d3314c73a5d780bf221be076378dc2fa82721dc05a16b6aa0d0324c259195'

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
def safe_rel(name):
    p=PurePosixPath(name)
    if not isinstance(name,str)or '\\'in name or ':'in name or p.is_absolute()or any(x in('', '.', '..')for x in p.parts):raise ValueError('Unsafe paired member')
    return p
def verify_pair(directory):
    root=Path(directory).resolve(strict=True);index=root/'EXPORTACION_SERVICIO.json';m=read(index)
    if m.get('schema')!='DEE.persistent_service.paired_export.v1'or m.get('backend')!='mente_unificada'or m.get('queue_journal_required')is not True:raise ValueError('Exact complete paired-service export required')
    names=set();size=0
    for item in m['members']:
        rel=safe_rel(item['file']);p=(root/rel).resolve(strict=True)
        if item['file']in names or not p.is_relative_to(root)or not p.is_file()or p.is_symlink():raise ValueError('Repeated/escaped paired member')
        if p.stat().st_size!=item['bytes']or sha(p)!=item['sha256']:raise ValueError('Paired bytes differ: '+item['file'])
        names.add(item['file']);size+=item['bytes']
    actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()and p!=index}
    if actual!=names or not {'VIDA.deetsnap.gz','cola.sqlite3'}<=names:raise ValueError('Missing/extra paired members')
    if m.get('native_snapshot')!='VIDA.deetsnap.gz'or sha(root/'VIDA.deetsnap.gz')!=m['snapshot_sha256']:raise ValueError('Snapshot not the declared complete parent')
    db=sqlite3.connect((root/'cola.sqlite3').as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Paired queue integrity')
        outstanding=db.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain') ORDER BY seq").fetchall()
        row=db.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=json.loads(row[0])if row else None
        count=db.execute('SELECT count(*) FROM requests').fetchone()[0]
        if outstanding:raise ValueError('Actual paired parent retains unresolved requests; do not discard them')
        if not isinstance(owner,dict)or owner.get('running')is not False:raise ValueError('PostSTOP owner state must be explicitly false')
    finally:db.close()
    return m,{'manifest_sha256':sha(index),'snapshot_sha256':m['snapshot_sha256'],'members':len(names),'member_bytes':size,'requests_preserved':count,'outstanding':outstanding,'owner':owner,'verification_native_ticks':0}

def differences(a,b,path=''):
    if type(a)is not type(b):return [{'path':path,'before':a,'after':b}]
    if isinstance(a,dict):
        out=[]
        for key in sorted(set(a)|set(b)):
            p=path+'/'+key
            if key not in a or key not in b:out.append({'path':p,'before':a.get(key),'after':b.get(key)})
            else:out+=differences(a[key],b[key],p)
        return out
    if isinstance(a,list):
        if len(a)!=len(b):return [{'path':path,'before':a,'after':b}]
        return [d for i,(x,y)in enumerate(zip(a,b))for d in differences(x,y,path+'/'+str(i))]
    return []if a==b else[{'path':path,'before':a,'after':b}]

def bind(fixed,main,pair,life,prefix):
    if fixed['events']!=main['events']or fixed['cases_before_selection']!=main['cases_before_selection']:raise ValueError('Root changed prospectively frozen material; do not adapt the control')
    if main.get('enabled_seconds')!=0 or len(main['events'])!=17:raise ValueError('Bounded fixed17-event window only')
    if main.get('snapshot_sha256')!=pair['snapshot_sha256']:raise ValueError('MAIN and control must begin from the SAME exact postSTOP native parent')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}',life)or life==main['life']:raise ValueError('Explicit unused distinct control identity required')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,30}',prefix)or prefix==main['prefix']:raise ValueError('Explicit distinct bounded control prefix required')
    derived=copy.deepcopy(main);derived['life']=life;derived['prefix']=prefix
    for e in derived['events']:
        payload=e['payload']
        if payload['operacion']!='sesion'or payload.get('retorno','real')not in('real','omit'):raise ValueError('Declared literal session feedback required')
        payload['retorno']='omit'
    diff=differences(main,derived)
    for row in diff:
        path=row['path']
        if path in('/life','/prefix'):continue
        if not re.fullmatch(r'/events/\d+/payload/retorno',path)or row['before']not in(None,'real')or row['after']!='omit':raise ValueError('Non-feedback scientific difference: '+path)
    return derived,diff

def main():
    p=argparse.ArgumentParser();p.add_argument('--fixed-material',type=Path,required=True);p.add_argument('--main-protocol',type=Path,required=True);p.add_argument('--paired-export',type=Path,required=True);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--window-runner',type=Path,required=True);p.add_argument('--vida',required=True);p.add_argument('--prefix',required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    if sha(a.fixed_material)!=FIXED_SHA:raise ValueError('Root frozen material SHA mismatch')
    fixed=read(a.fixed_material);mainproto=read(a.main_protocol);pair,verification=verify_pair(a.paired_export)
    control,diff=bind(fixed,mainproto,pair,a.vida,a.prefix)
    s=a.sistema.resolve(strict=True)
    if (s/'estado/vidas'/a.vida).exists()or(s/'estado/servicios_persistentes'/a.vida).exists():raise FileExistsError('Control may only be imported once into an UNUSED identity')
    out=a.salida.resolve();out.mkdir(parents=True,exist_ok=False)
    for name,source in(('MATERIAL_ROOT_FIJO.json',a.fixed_material),('PROTOCOLO_MAIN_RESUELTO.json',a.main_protocol),('EJECUTOR_ORIGINAL.py',a.window_runner)):(out/name).write_bytes(source.read_bytes())
    write(out/'PROTOCOLO_OMIT.json',control)
    write(out/'VINCULACION_N0.json',{'schema':'APD02.quality_reversal.exact_paired_omit_binding.v1','fixed_material_sha256':FIXED_SHA,'resolved_main_protocol_sha256':sha(a.main_protocol),'control_protocol_sha256':sha(out/'PROTOCOLO_OMIT.json'),'scientific_differences_exhaustive':diff,'paired_parent':verification,'native_ticks':0,'import_executed':False,'scope':'Only life/prefix and session feedback differ. Exact same inherited complete native world, closed queue and artifact bytes. New identity is an operational diagnostic branch, never experience imported into MAIN.'})
    write(out/'CONFIG_EJECUCION.json',{'status':'BOUND_AWAITING_EXPLICIT_ROOT_NATIVE_GO','system_root':str(s),'paired_export':str(a.paired_export.resolve()),'pair_manifest_sha256':verification['manifest_sha256'],'parent_snapshot_sha256':pair['snapshot_sha256'],'life':a.vida,'prefix':a.prefix,'protocol':'PROTOCOLO_OMIT.json','protocol_sha256':sha(out/'PROTOCOLO_OMIT.json'),'window_runner':'EJECUTOR_ORIGINAL.py','window_runner_sha256':sha(out/'EJECUTOR_ORIGINAL.py'),'system_manager_sha256':sha(s/'gestionar.py'),'pair_importer_sha256':sha(s/'app/importacion_emparejada.py'),'process_control_sha256':sha(s/'app/process_control.py'),'max_total_wall_seconds':600,'memory_limit_bytes':536870912,'OMP_NUM_THREADS':'1','campaign_deadline_utc':'2026-10-26T11:17:43+00:00','no_reseed_reteaching_cursor_reset_or_host_choice':True})
    print(json.dumps({'out':str(out),'new_ticks':0,'changes':diff,'pair':verification},ensure_ascii=False))
if __name__=='__main__':main()
