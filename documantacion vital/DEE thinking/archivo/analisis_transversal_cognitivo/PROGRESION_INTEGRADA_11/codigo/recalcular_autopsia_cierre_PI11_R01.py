"""Passive PI11 closure autopsy. Standard library only; no runtime restoration.

Reads frozen JSON/JSONL and complete DEETSNP1/v2 snapshots. The only optional
write is a new documentary JSON file. No DEE imports, Native, queue, or SQLite.
"""
from array import array
from collections import Counter
from pathlib import Path
import argparse, ast, gzip, hashlib, importlib.util, json, struct, sys

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
S = P / 'estados/MAIN01/sistema'
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_MAIN01'
TICKS = (972419, 975259, 977111, 978675, 979389)

def need(ok, message):
    if not ok: raise ValueError(message)

def sha(b): return hashlib.sha256(b).hexdigest()
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def parsed(v): return json.loads(v) if isinstance(v, str) else v
def locator(p):
    p = Path(p).resolve(strict=True)
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': sha(b)}

def reviewed_observer():
    p = C / 'reproducibilidad/observador_pasivo.py'
    source = p.read_text('utf-8-sig'); tree = ast.parse(source)
    allowed = {'pathlib', 'gzip', 'hashlib', 'struct'}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): need(all(x.name in allowed for x in n.names), 'Observer nonstdlib import')
        if isinstance(n, ast.ImportFrom): need(n.module in allowed, 'Observer nonstdlib import')
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            need(n.func.id not in {'exec','eval','compile','__import__'}, 'Observer dynamic execution')
    spec = importlib.util.spec_from_file_location('PI11_reviewed_passive_observer', p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod, locator(p)

def fields(v):
    ds = [(v >> s) & 15 for s in (48,52,56)]
    return {'raw': str(v), 'state': v & 0xffffffff, 's_reg': (v >> 32) & 65535,
            'direction': [d-16 if d&8 else d for d in ds], 'semantic': (v >> 60)&15}

def arrays(p):
    encoded = p.read_bytes(); b = gzip.decompress(encoded) if encoded[:2] == b'\x1f\x8b' else encoded
    need(b[:8] == b'DEETSNP1' and struct.unpack_from('<I',b,8)[0] == 2, 'Known v2 only')
    n = struct.unpack_from('<I',b,12)[0]; t = struct.unpack_from('<Q',b,16)[0]
    size = struct.unpack_from('<I',b,41)[0]; off = 45+size
    total = struct.unpack_from('<Q',b,off)[0]; off += 8
    need(n == 67 and total == n**3, 'N67 complete world required')
    raw = array('Q'); raw.frombytes(b[off:off+8*total])
    clocks = array('Q'); clocks.frombytes(b[off+8*total:off+16*total])
    if sys.byteorder != 'little': raw.byteswap(); clocks.byteswap()
    return t, n, raw, clocks

def coord(i,n): return [i//(n*n),(i//n)%n,i%n]
def idx(site,n): return (site[0]*n+site[1])*n+site[2]
def summary(raw, clocks, n, tick):
    active = sum(bool(v & 0xffffffff) for v in raw)
    nonzero = sum(bool(v) for v in raw)
    return {'sites':len(raw),'RAW_nonzero_support':nonzero,'active_STATE_nonzero':active,
            'STATE0_RAW_nonzero':nonzero-active,'max_s_reg':max((v>>32)&65535 for v in raw),
            'clock_min':min(clocks),'clock_max':max(clocks),'clock_equal_tick':sum(v==tick for v in clocks),
            'clock_age_histogram':dict(sorted(Counter(str(tick-v) for v in clocks).items(),key=lambda x:int(x[0]))),
            'semantic_nonzero_RAW_histogram':dict(sorted(Counter(str((v>>60)&15) for v in raw if v).items())),
            'Q1_A':{**fields(raw[idx((23,11,12),n)]),'clock':clocks[idx((23,11,12),n)]},
            'Q1_B':{**fields(raw[idx((25,11,12),n)]),'clock':clocks[idx((25,11,12),n)]},
            'Q2_A':{**fields(raw[idx((7,39,50),n)]),'clock':clocks[idx((7,39,50),n)]},
            'Q2_B':{**fields(raw[idx((9,39,50),n)]),'clock':clocks[idx((9,39,50),n)]}}

def primary(name):
    p=P/'ensayos'/name; j=read(p)
    j['result']=parsed(j.get('result')); j['error']=parsed(j.get('error'))
    return p,j

def receipt_view(p, reader, minimum_id):
    b=gzip.decompress(p.read_bytes());r=reader(b[:-8]);r.take(8);r.u32();n=r.u32();r.u64();r.take(17);r.text();total=r.u64();r.take(total*16)
    for _ in range(r.count()): r.text();r.take(31)
    pending=r.count()
    for _ in range(pending):
        r.take(33)
        for _ in range(r.count()):r.text()
        for _ in range(r.count()):r.take(20)
    result=[]
    for _ in range(r.count()):
        ident=r.u64();kind=r.u8();status=r.u8();requested=r.u64();effective=r.u64() if r.u8() else None
        channels=[r.text() for _ in range(r.count())];reason=r.text()
        if ident>=minimum_id:result.append({'id':ident,'kind_code':kind,'status_code':status,'requested_tick':requested,'effective_tick':effective,'channels':channels,'reason':reason})
    return {'pending_native':pending,'receipts':result}

def source_function(p, name):
    p=Path(p);tree=ast.parse(p.read_text('utf-8-sig'))
    for n in ast.walk(tree):
        if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name:
            return {**locator(p),'symbol':name,'line':n.lineno,'end_line':n.end_lineno}
    raise ValueError('Missing symbol '+name)

def delta(a,b,n):
    _,ra,ca=a;_,rb,cb=b
    return {'RAW_changed_sites':sum(x!=y for x,y in zip(ra,rb)),
            'RAW0_to_nonzero':sum(not x and bool(y) for x,y in zip(ra,rb)),
            'RAW_nonzero_to0':sum(bool(x) and not y for x,y in zip(ra,rb)),
            'STATE0_to_active':sum(not(x&0xffffffff) and bool(y&0xffffffff) for x,y in zip(ra,rb)),
            'active_to_STATE0':sum(bool(x&0xffffffff) and not(y&0xffffffff) for x,y in zip(ra,rb)),
            'clocks_changed_sites':sum(x!=y for x,y in zip(ca,cb)),
            'clock_delta_histogram':dict(sorted(Counter(str(y-x) for x,y in zip(ca,cb)).items(),key=lambda x:int(x[0])))}

def finalize(value):
    resource_path=S/'estado/servicios_locales'/LIFE/'PI11_HABITAT_ADAPTATIVO_R01/PI11_HABITAT_R01/offers/result_0018.json'
    resource=read(resource_path);ref=locator(resource_path)
    need(resource['ordinal']==18 and resource['tick']==979181 and not resource['physical_delivered'],'Frozen incomplete episode consequence mismatch')
    if not any(x['path']==ref['path'] for x in value['sources']):value['sources'].append(ref)
    value['failed_third']['environmental_consequence_already_committed']={'source':ref,'result':resource,
        'distinction':'External consequence committed at979181 and environmental completed counter became19. PI11 Native-return sequence did not complete; no episodio_0018 witness exists and no Q1/Q2 generic return was scheduled before HostSafetyStop.'}
    value['interpretation']['pending_semantics']='Zero pending Native events and terminal Native receipts do not imply completed PI11 episode. The PI11 metadata remains PRESERVED_INCOMPLETE/uncertain; the external environment already committed consequence18, completed19 and open_offer=null. These are distinct completion levels.'
    value['safety_and_causality']['recorded_growth']='Saved support was389 atMAIN16,390 afterPanel12,389 afterpost16,423 afterpost17,19161 atstop. STATE0/nonzeroRAW stayed240 at every saved cut; the large final increase is in STATE-nonzero sites. The first saved post17 increase is33 above Panel12; no first internal expansion tick is established.'
    value['safety_and_causality']['clocks_limit']='Every one of300763 site clocks equals the global tick in each saved complete cut; clock differences here do not identify a carrier age or ancestry.'
    value['recalculation_script']=locator(__file__)
    return value

def analyze():
    observer,obsref=reviewed_observer(); snapshots=[]; cache={}; variants={}; sources=[]
    checkpoints=S/'estado/checkpoints'
    grouped={}
    for p in sorted(checkpoints.glob(LIFE+'.T*.deetsnap.gz')):
        t=int(p.name.split('.T')[1].split('.')[0])
        if t>=TICKS[0]:grouped.setdefault(t,[]).append(p)
    for tick,paths in sorted(grouped.items()):
        canonical=None; vv=[]
        for p in paths:
            t,n,raw,clocks=arrays(p)
            current=(sha(raw.tobytes()),sha(clocks.tobytes()))
            if canonical is None:canonical=current;chosen=(p,n,raw,clocks)
            need(current==canonical,'Same-tick variants changed physical arrays')
            vv.append(locator(p))
        p,n,raw,clocks=chosen
        entry={'tick':tick,'source':locator(p),'variants':vv,'same_tick_RAW_clocks_equal':True,
               'RAW_sha256':canonical[0],'clocks_sha256':canonical[1],**summary(raw,clocks,n,tick)}
        if tick in TICKS:
            v=observer.snapshot_view(p)
            need(v['physical']['RAW_sha256']==entry['RAW_sha256'] and v['physical']['clocks_sha256']==entry['clocks_sha256'],'Independent passive parser mismatch')
            entry['passive_observer']={k:v[k] for k in ('physical','encoded_sha256','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase','scope')}
            key='DEE.Cognitive.PI11.persistent_habitat.native_continuation.R01'
            m=parsed(v['metadata'][key]);entry['PI11_progress']={k:m.get(k) for k in ('ordinal','pending','uncertain','log_count','log_chain_sha256')}
            cache[tick]=(p,raw,clocks);variants[tick]=vv
        snapshots.append(entry)
    need(all(t in cache for t in TICKS),'All declared complete cuts required')
    post=[];known_receipts={}
    for number in (0,1):
        p,j=primary('PI11_MAIN01_POST4_OWNER_R01_%02d.json'%number);sources.append(locator(p));r=j['result'];row=r['result']['rows'][0];two=row['second_stage'];fi=two['FI']
        req=row['requests'];counts=Counter(x['receipt']['status'] for x in req)
        for x in req:known_receipts[x['id']]=x['receipt']
        post.append({'source':locator(p),'json_pointer':'/result [JSON text]/result/rows/0','status':j['status'],'ordinal':row['ordinal'],
                     'before_tick':r['before_tick'],'after_tick':r['after_tick'],'ticks':r['after_tick']-r['before_tick'],
                     'q1_choice':row['first_stage']['reader']['choice'],'q2_choice':two['reader']['choice'],
                     'refresh_FI':two['refresh_FI'],'FI':None if fi is None else {k:fi[k] for k in ('before_tick','after_tick','instrument','capture_mode','early_physical_choice','old_q6_choice','Native_inputs')},
                     'resource':row['resource'],'actual_failed':row['actual_failed'],'returned_failed':row['returned_failed'],
                     'calendar':row['calendar'],'Q1_references_before':row['Q1_references_before'],'references_after':row['references_after'],
                     'Native_inputs':row['Native_inputs'],'independently_counted_request_statuses':dict(counts),
                     'requests':req,'coupled_environment_clock_samples':[{k:x[k] for k in ('tick',)} for x in row['coupled_clock_samples']],
                     'committed_snapshot':r['committed_snapshot']})
    failpath,failed=primary('PI11_MAIN01_POST4_OWNER_R01_02.json');sources.append(locator(failpath));err=failed['error'];proofpath=P/'control/PI11_MAIN01_POST4_OWNER_R01.json';proof=read(proofpath);sources.append(locator(proofpath))
    error_snapshot=S/err['failed_native_future_preserved']['snapshot'];need(sha(error_snapshot.read_bytes())==err['failed_native_future_preserved']['snapshot_sha256'],'Exact preserved failure hash mismatch')
    need(proof['closed'] is True and proof['status']=='STOPPED_PRESERVED','Closed preserved phase required')
    rv=receipt_view(error_snapshot,observer.Reader,min(known_receipts));code_to_name={};kind_to_name={}
    for x in rv['receipts']:
        if x['id'] in known_receipts:
            ref=known_receipts[x['id']];need(x['requested_tick']==ref['requested_tick'] and x['effective_tick']==ref['effective_tick'] and x['channels']==ref['channels'],'Binary receipt validation mismatch')
            code_to_name[x['status_code']]=ref['status'];kind_to_name[x['kind_code']]=ref['kind']
    for x in rv['receipts']:
        x['status']=code_to_name.get(x['status_code'],'UNMAPPED_ENUM');x['kind']=kind_to_name.get(x['kind_code'],'UNMAPPED_ENUM')
    last_complete_id=max(known_receipts);failed_receipts=[x for x in rv['receipts'] if x['id']>last_complete_id]
    journal=S/'estado/servicios_locales'/LIFE/'PI11_HABITAT_ADAPTATIVO_R01/eventos.jsonl';lines=[json.loads(x) for x in journal.read_text('utf8').splitlines()];intent=next(x for x in reversed(lines) if x['kind']=='OPPORTUNITY_INTENT');sources.append(locator(journal))
    hp=S/'estado/vidas'/LIFE/'HISTORIA.jsonl';history=[json.loads(x) for x in hp.read_text('utf8').splitlines()];sources.append(locator(hp))
    ending=[{'line':i+1,**r} for i,r in enumerate(history) if r['tick']>=TICKS[0]]
    environment=S/'estado/servicios_locales'/LIFE/'PI11_HABITAT_ADAPTATIVO_R01/PI11_HABITAT_R01/ESTADO.json';environment_state=read(environment);sources.append(locator(environment))
    observation=P/'fuentes/OBSERVACION_ABIERTA_Q1_PI11_R01.json';explore=read(observation);sources.append(locator(observation))
    protected=[]
    for path,digest in proof['protected_after'].items():
        need(proof['protected_before'][path]==digest and sha(Path(path).read_bytes())==digest,'Protected principal changed')
        protected.append(locator(path))
    functions=[source_function(S/'capacidades/pi07_regulacion_R01.py','SafeAdapter'),source_function(S/'capacidades/pi11_actor_R01.py','episode'),source_function(S/'capacidades/pi11_actor_R01.py','CoupledTime'),source_function(S/'capacidades/pi11_habitat_persistente_R01.py','execute'),source_function(S/'capacidades/pi05_transito_causal_R01.py','_fiplus'),source_function(P/'codigo/pi11_ejecutar_plan_R01.py','main')]
    first_over=next((x for x in snapshots if x['RAW_nonzero_support']>3000),None)
    result={'schema':'DEE.PI11.passive.closure_autopsy.R01','status':'CLOSED_PASSIVE_DOCUMENTARY_AUTOPSY','new_Native_ticks':0,'DEE_imports':0,'owner_calls':0,'SQLite_opened':False,
      'scope':'Complete frozen physical arrays plus closed documentary evidence. Global universe support is not identified with a mind or a memory metric.',
      'recalculation_script':locator(__file__),'reviewed_passive_observer':obsref,'sources':sources,'source_functions':functions,
      'closed_phase':{'source':locator(proofpath),'status':proof['status'],'closed':proof['closed'],'initial_tick':proof['initial_tick'],'final_tick':proof['final_tick'],'new_ticks_already_executed':proof['new_Native_ticks'],'completed_operations':len(proof['records']),'error':proof['error'],'no_live_affected_writer':proof['closed_process_queue']['no_live_affected_writer']},
      'complete_snapshot_cuts':snapshots,'pairwise_physical_changes':[{'before_tick':a,'after_tick':b,**delta(cache[a],cache[b],67)} for a,b in zip(TICKS,TICKS[1:])],
      'two_completed_post_episodes':post,
      'failed_third':{'source':locator(failpath),'transport_id':failed['id'],'transport_status':failed['status'],'result':None,'error':{k:v for k,v in err.items() if k!='failed_native_future_preserved'},'before_tick':978675,'preserved_tick':979389,'advanced_ticks':714,'error_snapshot':locator(error_snapshot),'failure_physical_report':err['failed_native_future_preserved']['physical'],'saved_pending_Native':rv['pending_native'],'new_Native_receipts_after_second_complete':failed_receipts,'receipt_status_counts':dict(Counter(x['status'] for x in failed_receipts)),'intent_journal_line':len(lines),'intent':{k:v for k,v in intent.items() if k!='environment_before'},'environment_at_end':{k:environment_state.get(k) for k in ('tick','prepared','completed','next_ordinal','open_offer','FI_refreshes','physical_deliveries','attributed_deliveries','certificate')},'PI11_pending_uncertain_is_separate_from_transport_external_uncertainty':True},
      'history_localizers':{'source':locator(hp),'records':ending},'protected_principal_PI10':{'tick':947395,'hashes_unchanged':True,'files':protected},
      'safety_and_causality':{'external_host_rule':'After each SafeAdapter.run_until block <=32 ticks, count RAW!=0 over all N^3 sites; raise if count>3000. CoupledTime requests <=16 ticks, so its normal blocks check <=16 ticks. Nested FIplus runs through the same coupled adapter.',
       'first_saved_cut_over_threshold':None if first_over is None else {'tick':first_over['tick'],'RAW_nonzero_support':first_over['RAW_nonzero_support'],'source':first_over['source']},
       'safety_samples_preserved_in_MAIN_primaries':False,'missing_sample_limit':'The failed local SafeAdapter.safety list is not serialized by episode exception handling. Exact first internal threshold crossing and last passing safety sample are unavailable. Saved cut bounds do not reconstruct intervening encounters.',
       'proximate_stop_cause':'HostSafetyStop from external count rule; wrapper subsequently reports Missing complete receipt because failed_preserved has no completed result.',
       'physical_change_cause_limit':'Physical expansion is measured between frozen cuts. No intervening full RAW trace identifies a unique carrier genealogy or separates accumulated recurrence, inputs, return interactions, FI geometry and context causally.',
       'no_repair':'No retry, rollback, cleaning, threshold increase, corrective input or new Native observation.'},
      'exploratory_actor_feedback13_relation':{'source':locator(observation),'source_witness':explore['source_witness'],'global_comparison':explore['global_comparison'],'facts':explore['facts'],'relation':'Same continuous MAIN history includes ordinal13 and subsequent preserved cuts. Ordinal13 is an exploratory local Q1 observation after nonfailure; it does not establish that its carriers produced the later global expansion. RAW equality and clock differences do not identify unique ancestry.','new_capacity_established':False},
      'interpretation':{'host_limit_vs_native_damage':'Observed: external host criterion exceeded and candidate future preserved. No direct measure here establishes Native corruption, cognitive damage, pain, death, total memory loss or improved capacity. The stopped candidate is not the protected PI10 principal.',
        'two_post_results':'Both episodes completed legally but failed the prepared external delivery criterion; no post delivery. One skipped FI with an expired certificate; one performed the inherited FI comparison successfully but selected the unavailable route.',
        'STATE0_is_not_empty_RAW':'Nonzero RAW can retain S_REG, direction or semantic fields while STATE=0. Active sites and nonzero RAW support are counted separately; neither global count is a cognitive capacity score.',
        'pending_semantics':'Zero pending Native events and terminal Native receipts do not imply completed PI11 episode: the PI11 metadata and external offer remain incomplete/uncertain and must be preserved.',
        'no_general_capacity_claim':True},
      'verification':{'complete_N67_arrays':True,'gzip_CRC_checked':True,'encoded_SHA256_checked':True,'RAW_clocks_cross_checked_with_observer':True,'all_same_tick_variants_physical_equal':True,'internal_FNV_recalculated':False,'source_hashes_rechecked_after_read':True}}
    result=finalize(result)
    snapshot_sources=[ref for entry in snapshots for ref in entry['variants']]
    for ref in result['sources']+[obsref]+functions+protected+snapshot_sources:
        need(sha(Path(ref['path']).read_bytes())==ref['sha256'],'Source changed during autopsy')
    return result

if __name__ == '__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path); a=ap.parse_args();value=analyze()
    if a.output:
        need(not a.output.exists(),'Never overwrite a documentary autopsy')
        with a.output.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
        print(json.dumps({'output':str(a.output),'sha256':sha(a.output.read_bytes()),'saved_support':[(x['tick'],x['RAW_nonzero_support'],x['active_STATE_nonzero']) for x in value['complete_snapshot_cuts']],'failed_receipt_counts':value['failed_third']['receipt_status_counts'],'new_Native_ticks':0}))
    else:print(json.dumps(value,ensure_ascii=False,indent=2))
