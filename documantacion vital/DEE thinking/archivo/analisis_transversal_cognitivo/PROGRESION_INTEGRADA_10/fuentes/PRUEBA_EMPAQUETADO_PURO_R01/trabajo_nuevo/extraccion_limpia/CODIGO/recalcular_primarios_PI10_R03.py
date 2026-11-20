"""Read-only primary RAW/receipt/file projection for closed PI10 records.

No DEE imports, owner, database, subprocess, engine or environment action.
Use a closed explicit INDEX.json whose witness/resource paths are relative
to its directory. The tool never follows absolute paths embedded by actors.
An archive recalc checks recorded physical observations and host effects;
it is not a Native replay, capability test or automatic promotion.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json

SCHEMA='DEE.PI10.closed_primary_bundle.R01'
VERSION='DEE.PI10.independent_RAW_recalc.R03'
TERMINAL={'applied','rejected_conflict','rejected_invalid','rejected_past','rejected_closed','rejected_quota'}
RESERVED={2,3,4,5,8,9,10,11,14,15,16,17}

def need(ok,why):
    if not ok:raise ValueError(why)

def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))

def exact_int(v):
    if type(v)is int:return v
    if isinstance(v,str)and v.isdecimal():return int(v)
    raise ValueError('Exact integer/decimal-string required; no float or bool')

def raw_observation(o):
    raw=exact_int(o['raw']);need(0<=raw<2**64,'RAW uint64 domain')
    direct=[(raw//(2**s))%16 for s in(48,52,56)]
    d={'raw':raw,'state':raw%(2**32),'s_reg':(raw//(2**32))%(2**16),
       'semantic':raw//(2**60),'direction':[v-16 if v>=8 else v for v in direct]}
    for k in('state','s_reg','semantic','direction'):need(o[k]==d[k],'Decoded RAW disagrees with '+k)
    if 'active'in o:need(o['active']is(d['state']>0 and d['semantic']!=5),'Active flag disagrees with RAW')
    need(type(o['tick'])is int and o['tick']>=0,'Actual observation tick')
    need(len(o['site'])==3 and all(type(x)is int and 0<=x<67 for x in o['site']),'N67 actual site')
    d.update(tick=o['tick'],site=list(o['site']));return d

def extra_bit(o):
    d=raw_observation(o)
    if d['raw']==0:return 0
    if d['state']>0 and d['semantic']==1:
        if d['direction']==[0,0,1]:return 1
        if d['direction']==[1,0,0]:return 0
    return None

def central(reader,site,q):
    o=raw_observation(reader['observation']);need(o['site']==site and o['tick']==q+4,'Frozen central q+4 site/tick')
    ds=o['direction'];valid=o['state']>0 and o['semantic']==1 and ds[0]in(-1,0,1)and ds[1]==1 and ds[2]in(-1,0)
    choice=ds[0]if valid else None
    need(reader['choice']==choice and reader['tick']==o['tick']and reader['site']==site,'Central choice must decode from RAW')
    return choice

def motor(c):return (-1 if c==0 else c)if type(c)is int and c in(-1,0,1)else None

def reference(v,origin):
    a=raw_observation(v['A']);b=raw_observation(v['B'])
    need(a['site']==[(origin[0]-1)%67,(origin[1]-1)%67,origin[2]]and b['site']==[(origin[0]+1)%67,(origin[1]-1)%67,origin[2]],'Fixed reference sites')
    delta=a['s_reg']-b['s_reg'];need(v['A_minus_B']==delta,'Bank delta from actual RAW s_reg')
    need(v['reference_clocks']==[exact_int(v['A']['clock']),exact_int(v['B']['clock'])],'Actual reference clocks')
    return delta

def fi_reader(fi):
    legacy=fi['legacy_result'];trial=legacy['original_result']['native_trial'];q=trial['query_tick'];reader=trial['reader']
    observations=reader['observations'];need(len(observations)==6,'Unchanged six-site FI reader')
    candidates=[];sites=[]
    for x in(-1,0,1):
        for z in(0,-1):sites.append([15+2*x,17,15+2*z])
    for o,site in zip(observations,sites):
        d=raw_observation(o);need(d['site']==site and d['tick']==q+6,'Frozen inherited FI q+6 six-site classes')
        x=(site[0]-15)//2;z=(site[2]-15)//2
        if d['state']>0 and d['semantic']==1 and d['direction']==[x,1,z]:candidates.append(x)
    choice=candidates[0]if len(candidates)==1 else None
    need(reader['choice']==choice and legacy['old_q6_choice']==choice and fi['old_q6_choice']==choice,'FI old q+6 choice decoded from RAW, not early q+4')
    return choice

def unique_receipts(rows):
    ids={}
    for r in rows:
        ident=r['id'];receipt=r['receipt'];need(type(ident)is int and receipt['id']==ident,'Own exact Native receipt ID')
        need(receipt['status']in TERMINAL,'Pending/uncertain receipt is not completed task')
        if ident in ids:need(ids[ident]==receipt,'Contradictory alias receipt')
        ids[ident]=receipt
    return ids

def named_request(rows,channel,tick,payload=0):
    found=[r for r in rows if r.get('channel',r.get('port'))==channel and r.get('requested_tick',r.get('tick'))==tick]
    ids={r['id']:r for r in found};need(len(ids)==1,'One actual fixed request: '+channel)
    r=next(iter(ids.values()));need(r['payload']==payload,'Fixed actual payload: '+channel);return r

def project_episode(v,p):
    """Independent frozen-record check; returns plain auditor metrics only."""
    generation=p.get('schema');need(generation in('DEE.PI10.adaptive_query.protocol.R01','DEE.PI10.adaptive_query.protocol.R02'),'Explicit supported prospective protocol, never inferred from a successful result')
    expected='DEE.PI10.adaptive_query.two_native_traces.'+('R01'if generation.endswith('R01')else'R02')
    need(v.get('version')==expected,'Exact actor generation agrees with protocol')
    horizon,total=(18,24)if generation.endswith('R01')else(12,18)
    reserved={2,3,4,5,8,9,10,11,14,15,16,17}if horizon==18 else{1,2,3,5,6,7,9,10,11}
    need(p['evaluation_horizon']==horizon and p['total_offers']==total and set(p['reserved_ordinals'])==reserved,'Prospectively fixed horizon/supply/reserve')
    ordinal=v['ordinal'];need(type(ordinal)is int and 0<=ordinal<total,'Finite prospectively supplied opportunity')
    calibration=v['operator_calibration'];need(type(calibration)is bool,'Explicit calibration distinction')
    spec=(p['calibration_schedule']if calibration else p['schedule'])[ordinal]
    need(v['environment_spec']==spec,'No post-hoc environmental schedule edit')
    first=v['first_stage'];second=v['second_stage'];q1=first['query_tick'];q2=second['query_tick'];reg=first['sample_register']
    one=v['calendar']['first'];two=v['calendar']['second']
    need(one['query_tick']==q1 and two['query_tick']==q2 and q2>q1+8,'Actual fixed sequential query timing')
    for cal,laps in((one,18),(two,6)):
        need(cal['delay_laps']==laps and cal['collision_tick']-cal['seed_tick']==laps*67,'Frozen toroidal eligibility delay')
        # fixed_schedule retains a legacy q+6 planning label (seed-1).
        # The actual fixed central reader is independently checked at q+4
        # by central(). Do not rewrite this recorded metadata as a reading.
        need(cal['query_read_tick']==cal['query_tick']+6 and cal['seed_tick']==cal['query_tick']+7,'Legacy schedule label q+6 and actual efference schedule')
        need(cal['outcome_injection_tick']==cal['collision_tick']-1 and cal['contact_tick']==cal['collision_tick']+1,'Fixed generic-return hub')
    need(two['settled_after_tick']<one['outcome_injection_tick'],'q1 task consequence follows actual q2 work')
    need(v['after_tick']-v['before_tick']==v['new_native_ticks']and 0<=v['new_native_ticks']<=p['max_ticks_per_episode'],'Declared Native tick bound')
    c1=central(first['reader'],p['query_origin'],q1);c2=central(second['reader'],p['old_origin'],q2)
    m1=motor(c1);m2=motor(c2);need(first['native_motor']==m1 and second['native_motor']==m2 and second['actual_motor']==m2,'Fixed zero-to-minus codec, NULL never replaced')
    forced=first['operator_forced_query'];actual_m1=(1 if forced else -1)if calibration and type(forced)is bool else m1
    need(first['actual_query_motor']==actual_m1 and(calibration or forced is None),'Forced calibration never attributed as Native decision')
    sample=reg['actual_preview_observation'];d=raw_observation(sample);bit=extra_bit(sample)
    need(d['site']==[30,40,30]and d['tick']==q1-1 and bit is not None and 0<=d['state']<=3,'Frozen actual pre-choice preview domain')
    need(reg['first_submitted_STATE']==d['state'],'Only measured STATE drives first query')
    qo=raw_observation(first['question_observation']);need(qo['site']==[34,40,30]and qo['tick']==q1+8,'Frozen physical question signature')
    signature=qo['state']>0 and qo['semantic']==1 and qo['direction']==[1,0,0]
    qr=first['question_request'];requested=actual_m1==1
    need((qr is not None)==requested and reg['question_scheduled']is requested,'Fixed query actuator; no case-specific activation')
    applied=qr is not None and qr['receipt']['status']=='applied';released=bool(applied and signature)
    access_valid=not applied or signature
    need(reg['question_applied']is applied and reg['question_signature']is signature and reg['question_applied_and_signature']is released and reg['access_valid']is access_valid,'Admitted material question and actual signature remain distinct')
    need(reg['released_bit']==(bit if released else 0),'NoQuery/rejected query supplies declared zero, not hidden current bit')
    rows=v['requests'];ids=unique_receipts(rows)
    named_request(rows,p['query_prefix']+'.datum',q1+3,d['state'])
    named_request(rows,p['old_prefix']+'.datum',q2+3,2*(bit if released else 0))
    for prefix,q in((p['query_prefix'],q1),(p['old_prefix'],q2)):
        for suffix in('query','support.plus','support.minus'):named_request(rows,prefix+'.'+suffix,q,0)
    cp=second['copy_receipt'];valid2=m2 is not None and cp is not None and cp['status']=='applied'
    route=(1 if m2==1 else 0)if valid2 else None
    need(second['actual_route']==route and second['command_valid']is valid2,'Only admitted Native efference selects a bin')
    if second['copy_request']is not None:
        need(second['copy_request']['id']in ids and ids[second['copy_request']['id']]==cp,'Own actual actuator receipt reconciled')
    fichoice=fi_reader(second['FI']);need(p['fi_required']is True,'Prospectively fixed Native FI work requirement')
    offer=v['offer'];res=v['resource'];available=0 if spec['regime']=='bypass'else bit
    need(offer['prepared_tick']==q1-1 and offer['query1_tick']==q1 and offer['sample']==sample and offer['available_bin']==available,'Environment law fixed before Native choice')
    payload=d['raw'].to_bytes(8,'little')*8;payloadsha=sha(payload)
    need(offer['resource']['bytes']==64 and offer['resource']['sha256']==payloadsha,'64B actual measured RAW resource, not an answer payload')
    delivered=bool(valid2 and route==available and fichoice==1);valid1=m1 is not None and access_valid
    useful=bool(delivered and valid1);failed=not useful
    need(res['physical_delivered']is delivered and res['attributed_useful']is useful and res['actual_failed']is failed and v['actual_failed']is failed,'Separate physical file transfer from whole-task attribution')
    need(res['FI_required']is True and res['actual_Native_FI_choice']==fichoice and res['available_bin']==available and res['actual_route']==route,'Recorded environment gate uses actual FI and motor')
    need(res.get('process_error')is None,'Process/I/O failure requires separate preserved diagnosis')
    if delivered:need(res['product']['bytes']==64 and res['product']['sha256']==payloadsha,'Actual delivered bytes identity')
    else:need(res['product']is None,'No fabricated product after a miss')
    returned=v['returned_failed'];need(type(returned)is bool,'Actual generic return class')
    if v['feedback_arm']=='real':need(returned is failed,'Contingent true consequence')
    elif v['feedback_arm']=='nonfailure':need(returned is False,'Fixed nonfailure control')
    else:need(v['feedback_arm']=='yoked','Only prospectively declared control arm')
    named_request(rows,p['query_prefix']+'.outcome.'+('failure'if returned else'nonfailure'),one['outcome_injection_tick'])
    named_request(rows,p['old_prefix']+'.outcome.nonfailure',two['outcome_injection_tick'])
    refs={'q1_before':reference(v['Q1_references_before'],p['query_origin']),
      'q1_after':reference(v['references_after']['q1'],p['query_origin']),
      'q2_before':reference(v['Q2_references_before'],p['old_origin']),
      'q2_after':reference(v['references_after']['q2'],p['old_origin'])}
    stable=refs['q2_before']==refs['q2_after'];need(v['Q2_reference_difference_stable']is stable,'Q2 stability must come from RAW refs')
    need(v['Native_inputs']['unique_requested']==len(ids)and v['Native_inputs']['applied']==sum(r['status']=='applied'for r in ids.values()),'Receipt denominators deduplicated, not aliases')
    return {'ordinal':ordinal,'life_id':v['life_id'],'calibration':calibration,'arm':v['feedback_arm'],'trace_control':v['trace_control'],
      'regime':spec['regime'],'reserved':not calibration and ordinal in reserved,'q1_STATE':d['state'],'actual_preview_bit':bit,
      'evaluation_horizon':horizon,'reserved_horizon':len(reserved),'protocol_generation':generation,
      'q1_Native_choice':c1,'q1_actual_motor':actual_m1,'q1_valid':valid1,'q1_Native_zero':type(c1)is int and c1==0,
      'query_requested':requested,'query_applied':applied,'query_released':released,'q2_Native_choice':c2,'actual_route':route,
      'FI_choice_old_q6':fichoice,'physical_delivered':delivered,'attributed_useful':useful,'actual_failed':failed,'returned_failed':returned,
      'resource_payload_sha256':payloadsha,'Native_ticks':v['new_native_ticks'],'before_tick':v['before_tick'],'after_tick':v['after_tick'],
      'unique_Native_requested':len(ids),'Native_applied':sum(r['status']=='applied'for r in ids.values()),
      'Native_rejected':sum(r['status']!='applied'for r in ids.values()),'receipt_id_status':{str(k):r['status']for k,r in ids.items()},
      'Q2_stable':stable,**refs,'query1_tick':q1,'query2_tick':q2,
      'central_actual_read_offsets':[first['reader']['tick']-q1,second['reader']['tick']-q2],
      'legacy_schedule_read_labels':[one['query_read_tick']-q1,two['query_read_tick']-q2],
      'schedule_label_is_not_actual_reading':True}

def safe_file(root,relative):
    pp=PurePosixPath(relative);need(not pp.is_absolute()and '..'not in pp.parts and '\\'not in relative and ':'not in relative,'Simple bundle-relative path only')
    path=root.joinpath(*pp.parts);need(path.resolve().is_relative_to(root.resolve()),'Bundle boundary')
    for parent in(path,*path.parents):need(not parent.is_symlink()and not(getattr(parent.lstat(),'st_file_attributes',0)&1024),'No linked/reparse evidence')
    need(path.is_file(),'Existing closed primary file');return path

def bundle(index_path):
    root=index_path.parent;idx=read(index_path);need(idx.get('schema')==SCHEMA and idx.get('closed')is True,'Explicit closed primary index required')
    protocolpath=safe_file(root,idx['protocol']['file']);need(sha(protocolpath.read_bytes())==idx['protocol']['sha256'],'Pinned exact protocol bytes')
    p=read(protocolpath);horizon=p['evaluation_horizon'];reserved_total=len(p['reserved_ordinals']);rows=[];checked=[]
    for entry in idx['episodes']:
        witness=safe_file(root,entry['witness']['file']);b=witness.read_bytes();need(len(b)==entry['witness']['bytes']and sha(b)==entry['witness']['sha256'],'Immutable closed episode witness')
        v=json.loads(b);r=project_episode(v,p);offer_dir=entry['offer_dir'].rstrip('/')
        manifest=safe_file(root,offer_dir+'/OFERTA.json');result=safe_file(root,offer_dir+'/RESULTADO.json')
        need(sha(manifest.read_bytes())==v['offer']['manifest_sha256']and sha(manifest.read_bytes())==v['resource']['offer_manifest_sha256'],'Recorded actual environment manifest bytes')
        ov=read(manifest);need(ov=={k:val for k,val in v['offer'].items()if k not in('environment_relative_home','manifest_file','manifest_sha256','new_Native_inputs','new_Native_ticks')},'Exact original prepared environment manifest')
        need(read(result)==v['resource'],'Original environment result agrees with immutable witness')
        resource='entregado64.bin'if r['physical_delivered']else ov['resource']['relative_file'];data=safe_file(root,offer_dir+'/'+resource).read_bytes()
        need(len(data)==64 and sha(data)==r['resource_payload_sha256'],'Actual64B moved/preserved resource readback')
        r['witness_sha256']=sha(b);rows.append(r);checked.append({'file':entry['witness']['file'],'sha256':sha(b),'bytes':len(b)})
    keys=[(r['life_id'],r['ordinal'])for r in rows];need(len(keys)==len(set(keys)),'No repeated opportunities counted as independent')
    groups={}
    for arm in('real','nonfailure','yoked'):
        rr=sorted([r for r in rows if not r['calibration']and r['arm']==arm and r['trace_control']=='none'and r['ordinal']<horizon],key=lambda r:r['ordinal'])
        if rr:
            need(len({r['life_id']for r in rr})==1,'One continuous lineage per primary arm')
            for a,b in zip(rr,rr[1:]):need(a['ordinal']+1==b['ordinal']and a['after_tick']<=b['before_tick'],'Unreset ordered opportunities, no hidden divergent futures')
        groups[arm]={'observed':len(rr),'planned':horizon,'reserved_planned':reserved_total,'complete_horizon':[r['ordinal']for r in rr]==list(range(horizon)),
          'physical_delivered':sum(r['physical_delivered']for r in rr),'attributed_useful':sum(r['attributed_useful']for r in rr),
          'reserved_opportunities':sum(r['reserved']for r in rr),'reserved_useful':sum(r['reserved']and r['attributed_useful']for r in rr),
          'query_requested':sum(r['query_requested']for r in rr),'query_released':sum(r['query_released']for r in rr),
          'q1_NULL':sum(r['q1_Native_choice']is None for r in rr),'FI_all_plus':bool(rr)and all(r['FI_choice_old_q6']==1 for r in rr),
          'Q2_all_stable':bool(rr)and all(r['Q2_stable']for r in rr),
          'by_regime':{reg:{'offered':sum(r['regime']==reg for r in rr),'useful':sum(r['regime']==reg and r['attributed_useful']for r in rr),'query':sum(r['regime']==reg and r['query_requested']for r in rr)}for reg in('need','bypass','need_return')}}
    real=[r for r in rows if not r['calibration']and r['arm']=='real'and r['trace_control']=='none']
    complete=all(v['complete_horizon']for v in groups.values())
    gain=groups['real']['reserved_useful']-groups['nonfailure']['reserved_useful']if complete else None
    return {'schema':VERSION,'Native_executed':False,'DEE_imported':False,'closed_index_sha256':sha(index_path.read_bytes()),
      'protocol_sha256':sha(protocolpath.read_bytes()),'evaluation_horizon':horizon,'reserved_horizon':reserved_total,'rows':rows,'groups':groups,'complete_three_paired_arms':complete,
      'reserved_gain_vs_nonfailure':gain,'bounded_gain_gate':None if gain is None else gain>=2,
      'useful_NoQuery_STATE1_Z_in_bypass':[r['ordinal']for r in real if r['regime']=='bypass'and r['reserved']and r['q1_STATE']==1 and r['actual_preview_bit']==1 and r['q1_actual_motor']==-1 and r['attributed_useful']],
      'useful_return_to_query_reserved':[r['ordinal']for r in real if r['regime']=='need_return'and r['reserved']and r['query_released']and r['attributed_useful']],
      'primary_files_checked':checked,'automatic_adoption':False,
      'scope':'Independent decode of archived RAW, own receipt identities, fixed-law projection and actual64B file verification. Not Native reproduction, subjective state, general autonomy or full adoption check.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--indice',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True);args=parser.parse_args()
    need(not args.salida.exists(),'Never overwrite a previous primary recalc');out=bundle(args.indice)
    with args.salida.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(args.salida),'sha256':sha(args.salida.read_bytes()),'Native_executed':False,'rows':len(out['rows'])}))
if __name__=='__main__':main()
