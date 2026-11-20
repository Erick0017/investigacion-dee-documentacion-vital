"""Conservative MI02 code delta installer, NOT a cognitive manager or memory transfer.

Default is read-only. Requires an existing Cognitive1.1 installation. Does not
install an engine, create a life, edit snapshots, change ACTIVO or run physics.
"""
import argparse,hashlib,json,os,shutil,tempfile
from pathlib import Path
from datetime import datetime,timezone
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--sistema',type=Path,required=True);ap.add_argument('--aplicar',action='store_true');args=ap.parse_args();here=Path(__file__).resolve().parent;package=here.parent;manifest=json.loads((here/'MANIFIESTO_DELTA.json').read_bytes());target=args.sistema.resolve(strict=True)
    if not(target/'gestionar.py').is_file()or not(target/'app/lives.py').is_file()or not(target/'contratos/PERFILES.json').is_file():raise ValueError('Existing Cognitive1.1 base is required; this is not a replacement installation')
    locks=[str(p)for p in(target/'estado/locks').glob('*.lock')]
    if args.aplicar and locks:raise RuntimeError('Runtime writer lock present. Close only your own operations before a code transaction. Read-only planning remains permitted.')
    plan=[]
    for row in manifest['files']:
        relative=Path(row['path'])
        if relative.is_absolute()or'..'in relative.parts:raise ValueError('Unsafe delta member')
        source=(package/'DELTA_SISTEMA'/relative).resolve(strict=True);destination=(target/relative).resolve()
        if not destination.is_relative_to(target)or not source.is_relative_to((package/'DELTA_SISTEMA').resolve()):raise ValueError('Delta path escaped its declared roots')
        if sha(source)!=row['sha256']:raise ValueError('Delta source hash mismatch '+str(relative))
        old=sha(destination)if destination.exists()else None;payload=None
        if row['path']=='capacidades/CATALOGO_CAPACIDADES.json':
            current=json.loads(destination.read_bytes());new=json.loads(source.read_bytes())
            if current.get('schema')!='DCS1.1.capabilities.registry.v1':raise ValueError('Unrecognized registry schema')
            proposed={v['id']:v for v in new['entries']if v['id'].startswith('MI02_')};present={v['id']:v for v in current['entries']};merged=[]
            for entry in current['entries']:
                id=entry['id']
                if id in proposed and entry!=proposed[id]:
                    if digest(entry)not in manifest['registry_known_entries'].get(id,[]):raise ValueError('Unknown local MI02 registry revision '+id)
                    merged.append(proposed[id])
                else:merged.append(entry)
            merged.extend(entry for id,entry in proposed.items()if id not in present)
            if merged!=current['entries']:
                current['entries']=merged;payload=(json.dumps(current,ensure_ascii=False,indent=2)+'\n').encode('utf8')
            action='SKIP'if payload is None else'MERGE_MI02_ENTRIES_ONLY'
        elif old==row['sha256']:action='SKIP'
        elif old is None:action='ADD';payload=source.read_bytes()
        elif old in row.get('known_previous_sha256',[]):action='REPLACE_KNOWN_REVISION';payload=source.read_bytes()
        else:raise ValueError('Unknown local revision, preserve it instead of overwriting '+str(relative))
        plan.append({'path':str(relative),'before_sha256':old,'after_sha256':hashlib.sha256(payload).hexdigest()if payload is not None else old,'action':action,'payload':payload,'destination':destination})
    public=[{k:v for k,v in row.items()if k not in('payload','destination')}for row in plan];backup=None
    if args.aplicar and any(r['payload']is not None for r in plan):
        backup=target/'estado/resguardos_delta'/('MI02_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S_%f'));backup.mkdir(parents=True,exist_ok=False)
        for row in plan:
            if row['payload']is None:continue
            destination=row['destination'];current=sha(destination)if destination.exists()else None
            if current!=row['before_sha256']:raise RuntimeError('Concurrent code change; transaction stopped with backup preserved')
            if destination.exists():
                q=backup/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(destination,q)
        (backup/'TRANSACCION.json').write_text(json.dumps({'plan':public,'state_snapshots_changed':False,'active_pointer_changed':False},ensure_ascii=False,indent=2),encoding='utf8')
        for row in plan:
            if row['payload']is None:continue
            destination=row['destination'];destination.parent.mkdir(parents=True,exist_ok=True)
            fd,temp=tempfile.mkstemp(prefix='.mi02_code_',dir=destination.parent)
            try:
                with os.fdopen(fd,'wb')as f:f.write(row['payload']);f.flush();os.fsync(f.fileno())
                os.replace(temp,destination)
            finally:
                if Path(temp).exists():Path(temp).unlink()
            if sha(destination)!=row['after_sha256']:raise AssertionError('Committed code differs from delta')
    print(json.dumps({'mode':'APPLY_EXPLICIT'if args.aplicar else'READ_ONLY_PLAN','base':str(target),'files':public,'writer_locks_observed':locks,'apply_blocked_while_any_writer_lock_present':True,'backup':str(backup)if backup else None,'native_ticks':0,'lives_created':0,'snapshots_changed':False,'ACTIVO_changed':False,'no_automatic_promotion':True,'base_engine_and_dependencies_still_required':manifest['external_dependencies']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
