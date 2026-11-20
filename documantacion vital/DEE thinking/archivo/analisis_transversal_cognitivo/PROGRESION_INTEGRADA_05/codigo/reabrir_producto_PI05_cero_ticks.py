"""Root-only affected product reopening, fixed STATE/save/close, zero inputs.

No owner/DEE import at module load. Does not run a panel, query a material
sensor, teach, act, supply, reset, select or promote. After adoption use a NEW
--salida and --seleccionado; before adoption selected-parent stays untouched.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,gzip,hashlib,importlib.util,json,sqlite3,struct,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01';PARENT='ECI02_PI03_MAIN';SITE=[19,53,20]
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(Path(p).resolve()),'bytes':Path(p).stat().st_size,'sha256':sha(p)}
def need(x,msg):
    if not x:raise ValueError(msg)
def parser_module():
    p=C/'reproducibilidad/observador_pasivo.py';s=importlib.util.spec_from_file_location('PI05_product_zero_snapshot_parser',p)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def field(path,site):
    m=parser_module();encoded=Path(path).read_bytes();b=gzip.decompress(encoded)if encoded[:2]==b'\x1f\x8b'else encoded;r=m.Reader(b[:-8])
    need(r.take(8)==b'DEETSNP1'and r.u32()==2,'Official complete snapshotv2 required')
    n=r.u32();tick=r.u64();r.u8();r.u64();r.u64();r.text();count=r.u64();need(n==67 and count==n**3,'Same N67 required')
    raw=r.take(8*count);clocks=r.take(8*count);i=(site[0]*n+site[1])*n+site[2]
    return {'site':site,'tick':tick,'raw':str(struct.unpack_from('<Q',raw,8*i)[0]),'clock':str(struct.unpack_from('<Q',clocks,8*i)[0])}
def regular(path):
    for p in(path,*path.parents):
        if p.exists()and(p.is_symlink()or getattr(p.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked operational path')
def main(a):
    output=a.salida.resolve(strict=False);regular(output)
    need(not output.exists()and output.is_relative_to((P/'control').resolve()),'Fresh unique PI05/control output only')
    cardfile=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardfile);beforepath=S/card['snapshot'];regular(beforepath)
    need(card['life_id']==LIFE and card['physical']['N']==67 and sha(beforepath)==card['snapshot_sha256'],'Prepared complete target pointer/identity mismatch')
    activepath=S/'estado/ACTIVO.json';active=read(activepath);selected=active.get('life_id',active.get('preferred_life'))
    need((selected==LIFE)if a.seleccionado else(selected!=LIFE),'Reopening phase differs from actual selection')
    if a.seleccionado:
        contract=read(S/'contratos/PI05_C2C_USO_PRINCIPAL_01.json')
        need(contract.get('status')=='COMMITTED'and contract.get('life_id')==LIFE and contract.get('allowed_modes')==['eci01-pi04-c2c-oportunidad','eci01-pi04-c2c-estado'],'Actual exact permission must exist before selected Owner starts')
    need(not(S/'estado/locks'/(card['world_id']+'.lock')).exists(),'Affected target already has a writer')
    parentcard=S/'estado/vidas'/PARENT/'VIDA.json';parent=read(parentcard);parentpaths=[parentcard,S/parent['snapshot']]
    parent_before={str(p):sha(p)for p in parentpaths};active_before=sha(activepath)
    parser=parser_module();before=parser.snapshot_view(beforepath);guard_before=field(beforepath,SITE)
    need(before['pending_native']==0 and guard_before['raw']==str(4<<60),'Prepared target must have settled agenda and persistent admitted support')
    sys.path.insert(0,str(H));from servicio_ensayo_PI05 import Owner
    actual=None;owner=None;closed=False;error=None;state=None
    tag='PI05_PRODUCTO_'+('POSTADOPT'if a.seleccionado else'PRE_ADOPT')
    try:
        with Owner(LIFE,tag,system=S)as owner:
            identifier=owner.runid+'_STATE'
            actual=owner.material(identifier,{'modo':'eci01-pi04-c2c-estado'},feedback='omit',allow_failure=True)
            need(actual.get('before_tick')==card['physical']['tick']and actual.get('after_tick')==card['physical']['tick'],'Read-only STATE advanced Native time')
            state=actual['result']['rows'][0];progress=state['progress'];device=state['device']
            need(state['new_native_ticks']==0 and state['admitted'],'C2C state absent or material')
            need(progress['life_id']==LIFE and progress['ordinal']==28 and progress['ready']and progress['admitted']and progress['arm']=='real','Exact current administrative identity/closed28-opportunity state required')
            need(not any(progress.get(k)for k in('pending','uncertain','halted_reason')),'Unresolved C2C future preserved')
            need(len(device['resources'])==30 and device['ordinal']==28 and len(device['products'])==27 and len(device['rejections'])==1,'Exact explicit30/consumed28/products27/reject1 state required; no reset/supply')
            need(not any(device.get(k)for k in('pending','feedback_pending','uncertain')),'Unresolved external device')
            home=S/'estado/servicios_locales'/LIFE/'PI04_C2C_COORDINACION_R01'/'dispositivo'
            # The existing operational-dependency validator already checks all
            # resource/product files. No new effect is performed here.
            owner.control('guardar')
    except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
    if owner is not None and owner.proc is not None:closed=bool(owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
    aftercard=read(cardfile);afterpath=S/aftercard['snapshot'];after=parser.snapshot_view(afterpath);guard_after=field(afterpath,SITE)
    physical_equal=before['physical']==after['physical'];native_prefix_equal=before['causal_prefix_sha256']==after['causal_prefix_sha256']
    comparison=None
    try:comparison=parser.compare_native(before,after,allow_service=True)
    except Exception as exc:
        if error is None:error={'type':'ZERO_TICK_NATIVE_COMPARISON_FAILED','message':str(exc),'automatic_retry':False}
    db=S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3'
    auxiliaries=[str(Path(str(db)+s))for s in('-wal','-shm','-journal')if Path(str(db)+s).exists()]
    q=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        integrity=q.execute('pragma integrity_check').fetchone()[0]
        unresolved=q.execute("select id,status from requests where status in('queued','processing','uncertain','failed_preserved')").fetchall()
        cache=q.execute("select value from meta where key='owner'").fetchone();cache=None if cache is None else json.loads(cache[0])
    finally:q.close()
    pending_ok=not after['pending_native']and not unresolved and not auxiliaries and integrity=='ok'and cache and cache.get('running')is False
    valid=state is not None and error is None and guard_after['raw']==str(4<<60)and physical_equal and native_prefix_equal and pending_ok and closed
    parent_after={str(p):sha(p)for p in parentpaths};need(parent_after==parent_before,'Protected parent changed concurrently; preserve and diagnose')
    if not a.seleccionado:need(sha(activepath)==active_before,'Unselected reopening changed global selection')
    proof={'schema':'DEE.PI05.product_zero_tick_reopening.v1','recorded_utc':datetime.now(timezone.utc).isoformat(),
        'life_id':LIFE,'phase':'SELECTED_POST_ADOPTION'if a.seleccionado else'UNSELECTED_PRE_ADOPTION','new_ticks':after['physical']['tick']-before['physical']['tick'],
        'physical_unchanged':physical_equal and native_prefix_equal,'pending_reconciled':bool(pending_ok),'operational_state_valid':bool(valid),
        'owner_closed':closed,'snapshot_sha256':aftercard['snapshot_sha256'],'physical':after['physical'],
        'complete_native_prefix_comparison':comparison,'native_receipt_counts_before_after':[before['native_receipts'],after['native_receipts']],
        'guard_before':guard_before,'guard_after':guard_after,'before_card_snapshot':info(beforepath),'after_card_snapshot':info(afterpath),
        'state_packet':actual,'state_summary':None if state is None else{'ordinal':state['progress']['ordinal'],'resources':len(state['device']['resources']),
            'products':len(state['device']['products']),'rejections':len(state['device']['rejections']),'available':len(state['device']['resources'])-state['device']['ordinal']},
        'queue':{'integrity':integrity,'unresolved':unresolved,'auxiliaries':auxiliaries,'cached_closed_owner':cache},
        'protected_parent_before':parent_before,'protected_parent_after':parent_after,'global_active_before_sha256':active_before,'global_active_after_sha256':sha(activepath),
        'error':error,'scope':'Only existing target load, metadata/device STATE, save and close at0ticks. No sensors/teaching/task/action/extra supplies/promotion. Snapshot service/system metadata may change by its persistence contract.'}
    with output.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':str(output),'sha256':sha(output),'life_id':LIFE,'new_ticks':proof['new_ticks'],'operational_state_valid':bool(valid),'owner_closed':closed,'error':error},ensure_ascii=False))
    return 0 if valid else 2
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',type=Path,required=True);ap.add_argument('--seleccionado',action='store_true');raise SystemExit(main(ap.parse_args()))
