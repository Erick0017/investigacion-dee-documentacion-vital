"""Root-only matched P0 recovery diagnosis on a fresh complete failed818074.

Prepare schedules one known legal support with0ticks; original FI follows.
The pending birth is preserved/admitted legally. No extra material read or
favourable decoder is used. A stdlib snapshot parser resolves its finalreceipt.
"""
from pathlib import Path
import argparse,datetime,gzip,hashlib,importlib.util,json,re,struct,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema'
PROTOCOL=P/'control/PROTOCOLO_RECUPERACION_PI05_R01.json'
MU_KEY='DEE.Cognitive.System.1.1.MENTE_UNIFICADA_01.v1'
def need(x,msg):
    if not x:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return {'file':str(Path(p).resolve()),'bytes':Path(p).stat().st_size,'sha256':sha(p)}
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def planned_calendar(start,protected):
    requested=start+56 # Exact FI128 raw_relative_tick=-19: start+2-(-19)+35.
    effective=requested
    if protected:
        boundary=((requested-2)//391+1)*391
        if boundary<=requested+8:effective=boundary+2
    need(0<=effective-requested<=10,'Old admitted MU391calendar exceeded its fixed bound')
    return {'before_tick':start,'input_tick':start+2+effective-requested,'query_tick':effective,
        'C_tick':effective+1,'S_tick':effective+3,'early_reader_tick':effective+4,'old_reader_tick':effective+6,
        'horizon_tick':effective+142,'expected_delta_ticks':effective+142-start,'phase_protection_enabled':protected,
        'requested_query_tick':requested,'wait_ticks':effective-requested}
def snapshot_receipt_and_site(path,identifier,site):
    """Frozen DEETSNP1/v2 framing; CRC checked, no DEE imports or world query."""
    parser=load('PI05_recovery_passive_reader',C/'reproducibilidad/observador_pasivo.py')
    encoded=Path(path).read_bytes();b=gzip.decompress(encoded)if encoded[:2]==b'\x1f\x8b'else encoded
    r=parser.Reader(b[:-8]);need(r.take(8)==b'DEETSNP1'and r.u32()==2,'Known native snapshotv2 only')
    n=r.u32();tick=r.u64();r.u8();r.u64();r.u64();r.text();total=r.u64();need(total==n**3 and n==67,'Exact full N67 buffers')
    raw=r.take(8*total);clocks=r.take(8*total);idx=(site[0]*n+site[1])*n+site[2]
    field={'site':site,'raw':str(struct.unpack_from('<Q',raw,8*idx)[0]),'clock':str(struct.unpack_from('<Q',clocks,8*idx)[0]),'tick':tick}
    for _ in range(r.count()):r.text();r.take(31)
    for _ in range(r.count()):
        r.take(33)
        for _ in range(r.count()):r.text()
        for _ in range(r.count()):r.take(20)
    found=None
    statuses={1:'scheduled',2:'applied',3:'rejected_late',4:'rejected_invalid',5:'rejected_occupied',6:'rejected_conflict',7:'rejected_queue_full'}
    for _ in range(r.count()):
        rid=r.u64();kind=r.u8();status=r.u8();requested=r.u64();effective=r.u64()if r.u8()else None
        channels=[r.text()for _ in range(r.count())];reason=r.text()
        if rid==identifier:
            need(found is None,'Duplicate native receipt ID');found={'id':rid,'kind':kind,'status':statuses.get(status,'UNKNOWN_'+str(status)),
                'requested_tick':requested,'effective_tick':effective,'channels':channels,'reason':reason}
    need(found is not None,'Scheduled support receipt missing from complete saved snapshot')
    return found,field

def main(a):
    need(re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_[A-Za-z0-9_]{1,32}',a.vida),'Strict fresh PI05 diagnostic life')
    need(re.fullmatch(r'PI05_[A-Z0-9_]{1,64}',a.tag),'Fresh explicit PI05 tag')
    need(not(S/'estado/ACTIVO.json').exists(),'Never query a selected principal')
    out=P/'control'/(a.tag+'.json');need(not out.exists()and not(P/'ensayos'/(a.tag+'_PREP.json')).exists()and not(P/'ensayos'/(a.tag+'_FI.json')).exists(),'Used tag/request ID; preserve and never resend')
    p=read(PROTOCOL);need(p['status']=='PREREGISTERED_BEFORE_NATIVE'and p['runner_sha256']==sha(Path(__file__)),'Frozen recovery runner only')
    for file,h in p['dependencies_sha256'].items():need(sha(Path(file))==h,'Fixed recovery dependency changed: '+file)
    need(sha(S/'capacidades/pi05_guardia_transito_R01.py')==p['guard_module_sha256'],'Guard source not the prepared revision')
    need(sha(S/'capacidades/PROTOCOLO_PI05_GUARDIA_R01.json')==p['guard_protocol_sha256'],'Guard protocol differs')
    parser=load('PI05_recovery_source_parser',C/'reproducibilidad/observador_pasivo.py')
    cardpath=S/'estado/vidas'/a.vida/'VIDA.json';card=read(cardpath);snap=S/card['snapshot'];need(sha(snap)==card['snapshot_sha256'],'Source snapshot changed')
    view=parser.snapshot_view(snap);need(view['physical']==p['source_physical'],'Exact unchanged recorded failed818074 physical source required')
    need(not view['pending_native'],'Source pending agenda must already be complete before a new explicit support')
    mu=json.loads(view['metadata'][MU_KEY]);phase=mu.get('phase_protection');need(phase is None or phase.get('version')=='MUFI01.sensor_calendar.R3P0'and phase.get('enabled')is True,'Unknown old MU phase contract')
    calendar=planned_calendar(818074,bool(phase));need(calendar['expected_delta_ticks']<=600,'Bounded old recovery comparison horizon')
    base=load('PI05_recovery_original_FI_helpers',H/'ejecutar_FI_PI05_R01.py')
    budget=read(P/'REGISTRO_CAMPANA.json');need(datetime.datetime.now().astimezone()<datetime.datetime.fromisoformat(budget['science_cutoff_local']),'Science deadline reached')
    floor=base.closed_ticks();need(floor+calendar['expected_delta_ticks']<=budget['budget']['Native_ticks_all_branches'],'Native all-branch budget exceeded')
    instrument=read(S/'capacidades/PROTOCOLO_PI05_TRANSITO_R01.json');usage=base.frame_usage(S/'estado/observacion_pasiva')
    offsets=[x for x in instrument['capture_offsets_q']if 818074<=calendar['query_tick']+x<=calendar['horizon_tick']]
    anchors=set(offsets)&set(instrument['anchor_offsets_q'])
    need(usage['anchors']+len(anchors)<=budget['budget']['full_global_anchors_max'],'Anchor allowance exceeded')
    need(usage['delta_frames']+len(offsets)-len(anchors)<=budget['budget']['one_tick_lossless_delta_frames_max'],'Delta allowance exceeded')
    prepare={'modo':'eci01-pi05-guardia-preparar'if a.condicion=='guardia'else'eci01-pi05-sham-preparar'}
    fi={'modo':'eci01-pi05-fiplus','izquierda':14,'derecha':3,'captura':'global'}
    if a.dry_run:
        print(json.dumps({'mode':'PURE_READ_ONLY_PREFLIGHT','prepare':prepare,'FI_literal':fi,'calendar':calendar,'Native_ticks':0,'no_owner':True}));return 0
    sys.path.insert(0,str(H));from servicio_ensayo_PI05 import Owner
    prep=None;actual=None;summary=None;owner=None;closed=False;error=None;guard_final=None;support_field=None;allcounts=None
    try:
        with Owner(a.vida,a.tag)as owner:
            prep=owner.material(a.tag+'_PREP',prepare,feedback='omit',allow_failure=True)
            need(prep['before_tick']==818074 and prep['after_tick']==818074,'Support preparation advanced Native age')
            ps=prep['result']['rows'][0];need(ps['new_inputs_scheduled']==1 and ps['new_native_ticks']==0,'Exactly one pending legal support required')
            actual=owner.material(a.tag+'_FI',fi,feedback='omit',allow_failure=True);summary=base.summarize(actual,14,3)
            need(summary['before_tick']==818074 and summary['after_tick']==calendar['horizon_tick'],'Actual old comparison age differs from fixed source/calendar')
            for k in('input_tick','query_tick','C_tick','S_tick','early_reader_tick','old_reader_tick','horizon_tick'):
                need(summary['calendar'][k]==calendar[k],'Actual old calendar differs: '+k)
            need(summary['Native_inputs']['unique_requested']==176,'Old unchanged FI must contribute176inputs')
            cap=summary['external_global_capture'];need(cap and not cap['missing_planned_ticks'],'Missing frozen global frames')
            target=Path(cap['directory']).resolve();need(target.is_relative_to((S/'estado/observacion_pasiva'/a.vida).resolve()),'Unexpected telemetry directory')
            need(sha(target/'INDEX.json')==cap['index_sha256'],'Global index changed')
            rows=read(target/'INDEX.json')['frames'];need([r['tick']for r in rows]==[calendar['query_tick']+x for x in offsets],'Frozen capture times differ')
            owner.control('guardar')
    except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'no_retry':True}
    if owner is not None and owner.proc is not None:closed=bool(owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
    if closed and prep is not None and actual is not None and error is None:
        try:
            saved=read(cardpath);finalsnap=S/saved['snapshot'];need(sha(finalsnap)==saved['snapshot_sha256'],'Saved full snapshot differs')
            ps=prep['result']['rows'][0];request=ps['support']['request'];site=ps['support']['site']
            guard_final,support_field=snapshot_receipt_and_site(finalsnap,request['id'],site)
            need(guard_final['requested_tick']==818076 and guard_final['status']=='applied','Support not admitted; preserve without retry')
            need(support_field['raw']==str(4<<60),'Support not persistent after actual comparison')
            combined=[{**request,'receipt':guard_final},*actual['result']['rows'][0]['requests']]
            allcounts=base.count_receipts(combined,818074,calendar['horizon_tick']);need(allcounts['unique_requested']==177,'Expected one support plus176old IDs')
            need(saved['physical']['tick']==calendar['horizon_tick'],'Saved cut differs from actual Native end')
        except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'no_retry':True}
    status='COMPLETED_RECOVERY_DIAG_RECORDED'if closed and summary is not None and error is None else'STOPPED_PRESERVED'
    proof={'schema':'DEE.PI05.P0_recovery_matched_diagnosis.R01','status':status,'life_id':a.vida,'condition':a.condicion,
        'protocol':info(PROTOCOL),'original_source_card':card,'source_physical':view['physical'],'source_causal_prefix_sha256':view['causal_prefix_sha256'],
        'calendar_preregistered_from_old_contract':calendar,'prepare_literal':prepare,'FI_literal':fi,
        'prepare_packet':prep,'actual_FI_packet':actual,'summary':summary,'support_receipt_after_saved_snapshot':guard_final,
        'support_after_saved_snapshot':support_field,'all177_input_denominators':allcounts,'original_scheduled_receipt_preserved_in_prepare_packet':True,
        'owner_closed_coherently':closed,'error':error,'new_Native_ticks':None if actual is None else actual['after_tick']-actual['before_tick'],
        'principal_modified':False,'new_teaching_or_readquisition':False,'causal_recovery_not_claimed_without_matched_sham':True,
        'scope':'Operator-prepared P0 historical diagnostic only. No fixed67wait, favourable reader, world reset, direct RAW/clock edit or automatic adoption.'}
    with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
    print(json.dumps({'proof':str(out),'status':status,'outcome':None if summary is None else summary['outcome'],'Native_ticks':proof['new_Native_ticks'],'error':error},ensure_ascii=False))
    return 0 if status=='COMPLETED_RECOVERY_DIAG_RECORDED'else 2
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--vida',required=True);ap.add_argument('--tag',required=True);ap.add_argument('--condicion',choices=('guardia','sham'),required=True);ap.add_argument('--dry-run',action='store_true');raise SystemExit(main(ap.parse_args()))
