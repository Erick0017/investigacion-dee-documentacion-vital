"""Portable PI02 R01/R02A documentary verifier. Python stdlib only; no DEE, no ticks.

Usage: python -I -B -X utf8 RECALCULAR_PI02.py --root EXTRACTED --out-dir OUT --strict
Packaged input: EVIDENCIA/INDICE_PI02.json. Local campaign input is also supported.
The index, evaluator and source code are auditor evidence, never participant inputs.
"""
from pathlib import Path,PurePosixPath
import argparse,ast,collections,csv,datetime,gzip,hashlib,io,json,re,struct,sys
N=67;ORIGIN=(0,5,20);E=(15,15,15);OLD_LAST_ID=112829
# The actual six-context geometry is derived once below, without a target argument.
MA_VECTORS=((1,0,0),(0,1,0),(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0))
MA_GATES={((33+4*x)%N,(33+4*y)%N,z)for x,y,_ in MA_VECTORS for z in (32,34)}
DIRECT={0:(1,0,0),1:(0,1,0)}
def sha(data):return hashlib.sha256(data).hexdigest()
def file_info(path):
    data=path.read_bytes();return {'bytes':len(data),'sha256':sha(data)}
def exact(v):
    if type(v)is int:return v
    if isinstance(v,str)and re.fullmatch(r'-?[0-9]+',v):return int(v)
    raise ValueError('An exact integer/string is required, not bool/float')
def raw_fields(v):
    v=exact(v)
    if not 0<=v<2**64:raise ValueError('RAW outside uint64')
    def nib(s):
        b=(v>>s)&15;return b-16 if b>=8 else b
    return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':(v>>60)&15,'direction':(nib(48),nib(52),nib(56))}
def observation(o):
    f=raw_fields(o['raw']);errors=[]
    for k in('state','s_reg','semantic'):
        if exact(o[k])!=f[k]:errors.append('Observation '+k+' differs from RAW')
    if tuple(o['direction'])!=f['direction']:errors.append('Observation direction differs from RAW')
    if not 0<=exact(o['clock'])<2**64:errors.append('Clock outside uint64')
    return f,errors
def direct(raw):
    f=raw_fields(raw)
    return next((k for k,v in DIRECT.items()if f['direction']==v),None)if f['state']>0 and f['semantic']==1 else None
def pure_z(raw):
    f=raw_fields(raw);x,y,z=f['direction']
    return z if f['state']>0 and f['semantic']==1 and x==0 and y==0 and z in(-1,1)else None
def fi_sign(raw):
    f=raw_fields(raw);x,y,z=f['direction']
    return x if f['state']>0 and f['semantic']==1 and x in(-1,0,1)and y==1 and z in(0,-1)else None
def safe_file(base,name):
    if not isinstance(name,str)or '\\'in name or ':'in name:raise ValueError('Safe relative slash path required')
    rel=PurePosixPath(name)
    if rel.is_absolute()or '..'in rel.parts:raise ValueError('Evidence escapes root')
    p=base.joinpath(*rel.parts)
    if not p.resolve(strict=True).is_relative_to(base.resolve(strict=True)):raise ValueError('Evidence escapes root')
    cur=p
    while cur!=base:
        if cur.is_symlink()or getattr(cur.lstat(),'st_file_attributes',0)&1024:raise ValueError('Reparse/link evidence forbidden')
        cur=cur.parent
    if not p.is_file():raise ValueError('Evidence not a file')
    return p
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
class SnapshotReader:
    """Copied/reviewed passive snapshotv2 parser structure from PI01, no runtime."""
    def __init__(self,data):self.data=data;self.i=0
    def take(self,n):
        if n<0 or self.i+n>len(self.data):raise ValueError('Truncated snapshot')
        v=self.data[self.i:self.i+n];self.i+=n;return v
    def u8(self):return self.take(1)[0]
    def u32(self):return struct.unpack('<I',self.take(4))[0]
    def u64(self):return struct.unpack('<Q',self.take(8))[0]
    def text(self):
        n=self.u32()
        if n>16*1024**2:raise ValueError('Snapshot string beyond bound')
        return self.take(n).decode('utf-8')
    def count(self):
        n=self.u32()
        if n>1000000:raise ValueError('Snapshot collection beyond bound')
        return n
def parse_snapshot(data):
    b=gzip.decompress(data)if data[:2]==b'\x1f\x8b'else data;r=SnapshotReader(b[:-8])
    if r.take(8)!=b'DEETSNP1'or r.u32()!=2:raise ValueError('Only known snapshotv2 supported')
    n=r.u32();t=r.u64();r.u8();r.u64();r.u64();phase=r.text();total=r.u64()
    if total!=n**3 or total>128**3*4:raise ValueError('Snapshot dimension beyond bound')
    raw=r.take(total*8);clocks=r.take(total*8);channels=r.count()
    for _ in range(channels):r.text();r.take(12+4+12+3)
    pending=r.count()
    for _ in range(pending):
        r.take(8+8+1+8+8)
        for _ in range(r.count()):r.text()
        for _ in range(r.count()):r.take(12+8)
    receipts=r.count()
    for _ in range(receipts):
        r.take(8+1+1+8)
        if r.u8():r.take(8)
        for _ in range(r.count()):r.text()
        r.text()
    r.u8();r.u64();prefix=r.i;metadata={}
    for _ in range(r.count()):
        key=r.text();value=r.text()
        if key in metadata:raise ValueError('Duplicate metadata key')
        metadata[key]=value
    if r.i!=len(b)-8:raise ValueError('Unparsed snapshot bytes')
    return {'physical':{'N':n,'tick':t,'RAW_sha256':sha(raw),'clocks_sha256':sha(clocks)},'causal_prefix_sha256':sha(b[:prefix]),'interfaces':channels,'pending':pending,'receipts':receipts,'phase':phase,'metadata':metadata,'scope':'Passive byte parser: gzipCRC and hashes checked; internal FNV is not recalculated; no DEE restoration/import.'}
def unwrap(outer):
    if outer.get('status')!='completed':raise ValueError('Noncomplete capture retained, not scored as success')
    payload=outer['payload']; payload=json.loads(payload)if isinstance(payload,str)else payload
    result=outer['result']; result=json.loads(result)if isinstance(result,str)else result
    rows=result['result']['rows']
    if len(rows)!=1:raise ValueError('Exactly one outer material command expected')
    return payload,result,rows[0]
def ma_unit(native):
    row=native['rows'][0]
    return row['result']['rows'][0]if row.get('kind')=='explicit_operator_memory_access'else row
def canonical_receipts(items,feedback=None):
    refs=[]
    for x in items:
        r=x['receipt']
        if exact(r['id'])!=exact(x['id']):raise ValueError('Request and receipt ID differ')
        refs.append((r,x.get('payload',x.get('value'))))
    if feedback is not None:refs.append((feedback,5))
    unique={};aliases=0
    for r,load in refs:
        identifier=exact(r['id'])
        if identifier<=OLD_LAST_ID:raise ValueError('Historical receipt included as new event')
        if identifier in unique:
            if unique[identifier]['receipt']!=r:raise ValueError('Conflicting aliases for one Native ID')
            aliases+=1;continue
        unique[identifier]={'receipt':r,'supplied_load':load}
    c=collections.Counter(x['receipt']['status']for x in unique.values())
    return unique,{'requested_unique':len(unique),'applied':c.get('applied',0),'rejected':sum(v for k,v in c.items()if k.startswith('rejected')),'pending_or_other':sum(v for k,v in c.items()if k!='applied'and not k.startswith('rejected')),'statuses':dict(c),'aliases_not_counted':aliases,'supplied_loads':dict(collections.Counter(str(x['supplied_load'])for x in unique.values()))}
def decode_access(access,route):
    errors=[];details={};items=[];answer=None
    def check(label,condition):
        if not condition:errors.append(label)
    check('Unselected access must not be called',access.get('unselected_access_called')is False)
    if route==0:
        check('Route0 must use MA_alfa',access['access']=='MA_alfa');unit=ma_unit(access['native_result']);reader=unit['reader'];panel=reader['panel']
        check('MA fixed12gate set',len(panel)==12 and {tuple(o['site'])for o in panel}==MA_GATES)
        t=exact(unit['read_tick']);check('MA fixed input+4',t==exact(unit['input_tick'])+4)
        candidates=[]
        for o in panel:
            _,e=observation(o);errors+=e;check('MA fixed tick',exact(o['tick'])==t)
            z=pure_z(o['raw'])
            if z is not None:candidates.append({'site':o['site'],'sign':z,'raw':o['raw']})
        answer=candidates[0]['sign']if len(candidates)==1 else None
        check('MA recorded answer matches RAW',reader['formed_native_command']==answer)
        check('MA ambiguity matches RAW',reader['ambiguous']==(len(candidates)>1))
        items=unit['requests'];details={'kind':'MA12_unique_pureZ','read_tick':t,'candidates':candidates}
    elif route==1:
        check('Route1 must use FI early',access['access']=='FI128_early_q4');native=access['native_result'];o=native['early_observation'];q=exact(native['query_tick']);_,e=observation(o);errors+=e
        check('FI exactE q+4',tuple(o['site'])==E and exact(o['tick'])==q+4 and exact(native['early_tick'])==q+4)
        answer=fi_sign(o['raw']);check('FI recorded answer matches RAW',native['early_physical_choice']==answer)
        items=native['all_material_receipts'];details={'kind':'FI_fixedE_q4','query_tick':q,'read_tick':q+4,'observation':o}
    else:check('Invalid route has no fallback',access['access']is None and access['native_result']is None and access['physical_response']is None)
    check('Emitted access response matches RAW',access['physical_response']==answer)
    return answer,details,items,errors
def reference_policies(pairs,locks):
    refs={}
    for name in('WSLS','AllA','AllB','FixedAlternation'):
        policy=0;rows=[]
        for i,((left,right),lock)in enumerate(zip(pairs,locks)):
            route=policy if name=='WSLS'else 0 if name=='AllA'else 1 if name=='AllB'else i%2
            response=-1 if route==0 else (left>right)-(left<right)
            accepted=response==lock
            rows.append({'episode':i,'route':route,'response':response,'accepted':accepted})
            if name=='WSLS'and not accepted:policy=1-policy
        refs[name]={'resources':sum(x['accepted']for x in rows),'opportunities':len(rows),'rows':rows,'scope':'Classical auditor reference, not an E1 trial and never controls its actions. WSLS chooses only from previous generic reward; sign arithmetic here belongs to reference evaluation, not Native decoding.'}
    return refs
def frozen_pairs(code):
    tree=ast.parse(code)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='fixtures')
    assignment=next(n for n in fn.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='pairs'for t in n.targets))
    value=assignment.value.orelse if isinstance(assignment.value,ast.IfExp)else assignment.value
    pairs=ast.literal_eval(value)
    if len(pairs)!=12 or any(type(v)is not int or not 0<=v<=20 for p in pairs for v in p):raise ValueError('Unexpected frozen R02A public pair list')
    return pairs
def analyze_work(meta,outer,pairs,resources):
    payload,envelope,trial=unwrap(outer);problems=[];work=[];all_ids={};aliases=0
    def check(label,condition):
        if not condition:problems.append(label)
    before=exact(trial['before']['tick']);after=exact(trial['after']['tick']);arm=meta['arm']
    check('Frozen4500tick horizon',after-before==4500 and exact(payload['situaciones'][0]['ticks'])==4500 and trial['horizon_tick']==after)
    check('Frozen N67 and parentcut',trial['before']['N']==67 and trial['after']['N']==67 and before==735843)
    check('One generic vivir command',payload['situaciones']==[{'modo':'eci01-pi02-vivir','ticks':4500}])
    events=trial['all_detected_returns'];event_ticks=[];busy_count=0
    for ev in events:
        f,e=observation(ev['center']);problems+=e;t=exact(ev['tick']);event_ticks.append(t);r=direct(ev['center']['raw'])
        check('Return origin/tick',tuple(ev['center']['site'])==ORIGIN and exact(ev['center']['tick'])==t and before<t<=after)
        check('Return recorded route matches RAW',ev['route']==r and r is not None)
        busy_count+=ev['busy']is True
    check('Return ticks ordered unique',event_ticks==sorted(set(event_ticks)))
    check('Recorded recurrence intervals67',all(b-a==67 for a,b in zip(event_ticks,event_ticks[1:])))
    check('Busy count',busy_count==trial['busy_discarded'])
    events_by_tick={exact(x['tick']):x for x in events};cumulative=0;access_counts=collections.Counter();feedback_counts=collections.Counter();load_counts=collections.Counter()
    for row in trial['rows']:
        ep=exact(row['episode']);q=exact(row['request_tick']);o=row['request_center'];_,e=observation(o);problems+=e;route=direct(o['raw'])
        check('Admitted event exists and is not busy',q in events_by_tick and events_by_tick[q]['busy']is False)
        check('Admitted event matches physical return',q in events_by_tick and events_by_tick[q]['center']==o and row['native_route']==route)
        check('Prepared busy/feedback deadlines',row['busy_until']==q+308 and row['feedback_tick']==q+268)
        check('No initiating sensor/normalizer',row['sensor_inputs']==0 and row['normalizer_inputs']==0)
        answer,reader,requests,errors=decode_access(row['selected_access'],route);problems+=['ep'+str(ep)+':'+e for e in errors]
        receipts,den=canonical_receipts(requests,row['feedback']);aliases+=den['aliases_not_counted'];access_counts[row['selected_access']['access']]+=1
        for identifier,item in receipts.items():
            if identifier in all_ids:problems.append('Native ID reused across jobs:'+str(identifier))
            all_ids[identifier]=item;load_counts[str(item['supplied_load'])]+=1
            rr=item['receipt']
            if rr['status']=='applied':check('Applied receipt effective/requested equality',rr['effective_tick']==rr['requested_tick'])
        effect=row['effect'];command=answer if arm!='nulled'and payload['actuador']=='closed'else None
        # The hidden condition is consulted only here, after RAW decoding.
        lock=-1 if ep<3 or ep>=8 else 1;accepted=command is not None and command==lock
        check('Recorded private lock matches frozen environment',effect['private_lock_used_after_action']==lock)
        check('Actuation follows formed answer/null control',effect['response']==answer and effect['applied_command']==command)
        check('Resource utility law after action',effect['accepted']==accepted)
        resource=effect['resource']
        if accepted:
            cumulative+=1;entry=resources.get((arm,ep));check('Actual resource bytes present',entry is not None)
            if entry is not None:check('Resource record matches exported bytes',resource['bytes']==entry['bytes']==64 and resource['sha256']==entry['sha256'])
        else:check('No resource invented after failure',resource is None)
        check('Resource counter continuity',effect['resources_after']==cumulative)
        feedback=row['feedback'];expected_feedback=not accepted and arm!='omit'
        check('Feedback only actual negative effect',expected_feedback==(feedback is not None))
        if feedback is not None:
            channel=('PI02.R02.sham'if arm=='sham'else 'PI01.R03.penalty')+str(route)
            check('Feedback echoes actual route on fixed channel',feedback['channels']==[channel])
            check('Feedback fixed time',feedback['requested_tick']==q+267 and (feedback['status']!='applied'or feedback['effective_tick']==q+267))
            feedback_counts[feedback['status']]+=1
        # Auditor operand reference comes after the physical decoder and never fills an answer.
        reference=-1 if route==0 else (pairs[ep][0]>pairs[ep][1])-(pairs[ep][0]<pairs[ep][1])if route==1 else None
        work.append({'id':outer['id'],'life':meta['life'],'arm':arm,'episode':ep,'query_tick':q,'route_from_RAW':route,'access':row['selected_access']['access'],'reader':reader,'physical_response':answer,'reference_response_auditor_only':reference,'reference_matches_physical':answer==reference,'applied_command':command,'accepted':accepted,'resource':resource,'native_denominators':den,'native_ids':sorted(receipts),'feedback':feedback,'busy_until':row['busy_until']})
    exclusions=trial['capacity_fence_events'];admitted={x['query_tick']for x in work};busy_ticks={exact(x['tick'])for x in events if x['busy']};excluded_ticks={exact(x['tick'])for x in exclusions}
    check('Events split into admitted,busy,excluded',admitted|busy_ticks|excluded_ticks==set(event_ticks)and not(admitted&busy_ticks or admitted&excluded_ticks or busy_ticks&excluded_ticks))
    check('Reported denominators',len(events)==trial['native_requested_work']and len(work)==trial['admitted_work']and sum(x['physical_response']is not None for x in work)==trial['formed_responses']and cumulative==trial['actual_resources'])
    check('All12bank jobs represented',len(work)==12 and [x['episode']for x in work]==list(range(12)))
    statuses=collections.Counter(x['receipt']['status']for x in all_ids.values())
    return {'id':outer['id'],'life':meta['life'],'arm':arm,'before_tick':before,'after_tick':after,'elapsed_ticks':after-before,'detected_return_signatures':len(events),'admitted_jobs':len(work),'busy_discarded':busy_count,'excluded':exclusions,'formed_responses':sum(x['physical_response']is not None for x in work),'resources':cumulative,'access_counts':dict(access_counts),'new_native_requested_unique':len(all_ids),'new_native_applied':statuses.get('applied',0),'new_native_rejected':sum(v for k,v in statuses.items()if k.startswith('rejected')),'new_native_pending_or_other':sum(v for k,v in statuses.items()if k!='applied'and not k.startswith('rejected')),'native_statuses':dict(statuses),'valence_load_fixed_by_protocol':5,'negative_feedback_requested':sum(feedback_counts.values()),'negative_feedback_statuses':dict(feedback_counts),'supplied_load_distribution':dict(load_counts),'sensor_inputs':0,'normalizer_inputs':0,'transport_host_elapsed_seconds':envelope['host_elapsed_seconds'],'rows':work,'native_ids':sorted(all_ids),'inconsistencies':problems,'scope':'One related-prefix life, repeated jobs not independent acquisitions. Native return signatures are prepared requests, not learned timing or general initiative. Private environment used only after RAW decoding.'}
def analyze_r01(meta,outer):
    payload,envelope,row=unwrap(outer);problems=[];kind=meta['kind'];out={'id':outer['id'],'kind':kind,'arm':meta['arm'],'life':meta['life'],'before_tick':row['before']['tick'],'after_tick':row['after']['tick'],'before_physical':row['before'],'after_physical':row['after'],'host_elapsed_seconds':envelope['host_elapsed_seconds']}
    if kind=='R01_observation':
        frames=row['frames'];enabled=row['record_enabled'];ticks=[exact(x['tick'])for x in frames]
        if row['material_inputs']!=[]:problems.append('Material input in passive observation arm')
        if ticks!=(list(range(out['before_tick']+1,out['after_tick']+1))if enabled else []):problems.append('Observation frame coverage differs')
        for frame in frames:
            _,e=observation(frame['center']);problems+=e
            if frame['direct_route']!=direct(frame['center']['raw']):problems.append('Observation route differs from RAW')
        out.update(record_enabled=enabled,recorded_frames=len(frames),new_material_inputs=0)
    else:
        events=[]
        for e in row['events']:
            f,errors=observation(e['center']);problems+=errors;r=direct(e['center']['raw'])
            if e['route']!=r:problems.append('Calibration route differs from RAW')
            events.append({'tick':e['tick'],'route_from_RAW':r,'s_reg':f['s_reg'],'direction':list(f['direction'])})
        receipt=row['negative_receipt'];out.update(events=events,negative_requested=int(receipt is not None),negative_applied=int(receipt is not None and receipt['status']=='applied'),negative_receipt=receipt,sensor_inputs=row['sensor_inputs'],normalizer_inputs=row['normalizer_inputs'])
        if out['sensor_inputs']or out['normalizer_inputs']:problems.append('Unexpected calibration sensor/normalizer')
    out['inconsistencies']=problems;return out
def local_index(root):
    protocol_path=root/'control/PROTOCOLO_RESERVA_R02A.json';protocol=read(protocol_path);captures=[];resources=[]
    def item(path,**extra):return {'file':path.relative_to(root).as_posix(),**file_info(path),**extra}
    for arm,tag in [('real','REAL'),('omit','OMIT'),('sham','SHAM'),('nulled','NULLED')]:
        path=root/'ensayos'/('PI02_R02A_'+tag+'_VIVIR.json')
        if path.is_file():captures.append(item(path,kind='R02_work',arm=arm,life=protocol['lives'][arm]))
        bank=root/'estados/candidato/sistema/estado/servicios_locales'/protocol['lives'][arm]/'PI02_RESOURCE_BANK_R02/collected'
        if bank.is_dir():
            for f in sorted(bank.glob('*.bin')):resources.append(item(f,arm=arm,episode=int(f.stem)))
    for stage,kind in [('OBSERVATION','R01_observation'),('CALIBRATION','R01_calibration')]:
        for arm in ('ON','OFF'):
            f=root/'ensayos'/('PI02_R01_'+stage+'_'+arm+'.json')
            if f.is_file():captures.append(item(f,kind=kind,arm=arm.lower(),life='ECI02_PI02_OBS_'+arm))
    code=root/'codigo/revisiones/R02B_RESERVA_CONGELADA/capacidades/progresion_integrada_02.py'
    index={'schema':'PI02.portable.evidence.index.v1','captures':captures,'resources':resources,'protocol':item(protocol_path),'frozen_code':item(code),'journal':item(root/'ENSAYOS.jsonl'),'source_mode':'Local existing campaign files; absolute provenance paths do not enter participant or decoder.'}
    proof=root/'control/COMPARACION_OBSERVACION_R01.json'
    if proof.is_file():
        index['observer_comparison']=item(proof);p=read(proof);index['observer_snapshots']=[]
        for arm in p['arms']:
            path=Path(arm['checkpoint']['path']);entry=item(path,arm='on'if 'record_fixed'in arm['arm']else'off')
            if entry['sha256']!=arm['checkpoint']['sha256']:raise ValueError('Frozen R01 snapshot changed since its witness')
            index['observer_snapshots'].append(entry)
    return index
def export_evidence(root,destination,include_snapshots=False):
    """Copy only this verifier's required bytes, never overwrite a different export."""
    root=root.resolve();destination=destination.resolve();index=local_index(root);targetindex=destination/'EVIDENCIA/INDICE_PI02.json'
    if targetindex.exists():raise ValueError('Evidence index already exists; do not overwrite later campaign additions')
    def copy(entry,relative):
        source=safe_file(root,entry['file']);data=source.read_bytes()
        if sha(data)!=entry['sha256']:raise ValueError('Source changed during evidence export')
        out=destination/relative;out.parent.mkdir(parents=True,exist_ok=True)
        if out.exists()and out.read_bytes()!=data:raise ValueError('Different existing evidence is protected:'+str(out))
        if not out.exists():out.write_bytes(data)
        return {**entry,'file':relative,'source_localizer_at_export':str(source)}
    exported={'schema':index['schema'],'captures':[copy(x,'EVIDENCIA/PRIMARIOS/'+Path(x['file']).name)for x in index['captures']],'resources':[copy(x,'EVIDENCIA/RECURSOS_R02A/'+x['arm']+'/'+('%04d.bin'%x['episode']))for x in index['resources']],'protocol':copy(index['protocol'],'EVIDENCIA/PROTOCOLO_RESERVA_R02A.json'),'frozen_code':copy(index['frozen_code'],'CODIGO/CONGELADO_R02B/progresion_integrada_02.py'),'journal':copy(index['journal'],'EVIDENCIA/ENSAYOS_CAMPAÑA.jsonl'),'scope':'Initial R01/R02A evidence only; other stages must be indexed and recalculated separately before a whole-campaign claim.'}
    if index.get('observer_comparison'):exported['observer_comparison']=copy(index['observer_comparison'],'EVIDENCIA/OBSERVACION/COMPARACION_OBSERVACION_R01.json')
    exported['observer_snapshots']=[copy(x,'EVIDENCIA/OBSERVACION/'+x['arm']+'_T735977.deetsnap.gz')for x in index.get('observer_snapshots',[])]if include_snapshots else []
    exported['observer_snapshot_omission']='Only two Native diagnostic checkpoints included, not Cognitive operational pairs.'if include_snapshots else'Complete observation-state comparison is retained in its literal prior witness; dense checkpoints omitted from this export.'
    targetindex.parent.mkdir(parents=True,exist_ok=True);targetindex.write_text(json.dumps(exported,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return targetindex
def run(root,out,strict=False):
    root=root.resolve();indexpath=root/'EVIDENCIA/INDICE_PI02.json';index=read(indexpath)if indexpath.is_file()else local_index(root);errors=[];identities=[]
    def load(meta,text=False):
        p=safe_file(root,meta['file']);data=p.read_bytes()
        if sha(data)!=meta['sha256']or len(data)!=meta['bytes']:raise ValueError('Evidence identity differs:'+meta['file'])
        identities.append({'file':meta['file'],'bytes':len(data),'sha256':sha(data)})
        return data.decode('utf-8-sig')if text else data
    protocol=json.loads(load(index['protocol'],True));code=load(index['frozen_code'],True);pairs=frozen_pairs(code)
    if sha(code.encode('utf-8'))!=next(x['sha256']for x in protocol['code']if x['file']=='capacidades/progresion_integrada_02.py'):errors.append('Frozen code differs from protocol')
    resources={}
    for entry in index.get('resources',[]):
        data=load(entry);resources[(entry['arm'],exact(entry['episode']))]={'bytes':len(data),'sha256':sha(data),'file':entry['file']}
    work=[];r01=[]
    for meta in index['captures']:
        try:
            outer=json.loads(load(meta,True))
            if sha(outer['payload'].encode('utf-8'))!=outer['payload_sha']:raise ValueError('Payload SHA differs')
            if meta['kind']=='R02_work':work.append(analyze_work(meta,outer,pairs,resources))
            elif meta['kind']in('R01_observation','R01_calibration'):r01.append(analyze_r01(meta,outer))
            else:errors.append('Unsupported declared capture kind retained:'+meta['kind'])
        except (ValueError,KeyError,TypeError,IndexError)as exc:errors.append(meta['file']+':'+str(exc))
    missing=[a for a in('real','omit','sham','nulled')if a not in {x['arm']for x in work}]
    refs=reference_policies(pairs,[-1 if i<3 or i>=8 else 1 for i in range(len(pairs))])
    main=next((x for x in work if x['arm']=='real'),None)
    if main is not None:refs['WSLS']['matches_recorded_MAIN_routes']=all(a['route']==b['route_from_RAW']and a['response']==b['physical_response']and a['accepted']==b['accepted']for a,b in zip(refs['WSLS']['rows'],main['rows']))
    runtime=[]
    if index.get('journal'):
        text=load(index['journal'],True);journal=[json.loads(line)for line in text.splitlines()if line.strip()]
        for case in work:
            rec=next((x for x in journal if x.get('kind')=='MATERIAL_REQUEST'and x.get('id')==case['id']),None)
            if rec is None:errors.append('Missing runtime journal request:'+case['id']);continue
            runid=rec['run'];samples=[x for x in journal if x.get('kind')=='OWNED_PROCESS_RESOURCES'and x.get('run')==runid];closed=[x for x in journal if x.get('kind')=='OWNER_CLOSED'and x.get('run')==runid]
            def maximum(k):return max((x[k]for x in samples if type(x.get(k))in(int,float)),default=None)
            runtime.append({'life':case['life'],'arm':case['arm'],'run':runid,'samples':len(samples),'peak_working_set_bytes':maximum('peak_working_set_bytes'),'peak_job_committed_bytes':maximum('peak_job_committed_bytes'),'job_memory_limit':maximum('job_memory_limit'),'cpu_user_seconds_cumulative_max':maximum('cpu_user_seconds'),'cpu_kernel_seconds_cumulative_max':maximum('cpu_kernel_seconds'),'host_elapsed_seconds_closed':closed[-1]['elapsed_seconds']if closed else None,'closed_exit_code':closed[-1]['exit_code']if closed else None,'scope':'Low-cost host process/job measurements. Cumulative CPU maxima are not summed across samples. Not cognitive memory, native regulation or proof of Mac behavior.'})
    observed={x['arm']:x['resources']for x in work};criteria=protocol['criteria'];gates={}
    if not missing:
        gates={'main_at_least_frozen_minimum':observed['real']>=criteria['main_resources_minimum'],'gain_vs_omit':observed['real']-observed['omit'],'gain_vs_sham':observed['real']-observed['sham'],'nulled_resource_count':observed['nulled'],'same_elapsed_ticks':len({x['elapsed_ticks']for x in work})==1,'all12formed':all(x['formed_responses']==criteria['valid_responses_required']for x in work),'scope':'Predeclared local criteria only, not an intelligence or automatic-promotion verdict.'}
    observer={'mode':'captures_and_prior_witness_only','binary_comparison_recalculated_here':False}
    if index.get('observer_comparison'):
        prior=json.loads(load(index['observer_comparison'],True));observer['prior_causal_prefix_equal']=prior['causal_prefix_comparison']['equal'];observer['prior_witness_scope']=prior['interpretation']
    if index.get('observer_snapshots'):
        vs={x['arm']:parse_snapshot(load(x))for x in index['observer_snapshots']}
        if set(vs)!={'on','off'}:errors.append('Both observation snapshots required')
        else:
            a,b=vs['on'],vs['off'];service='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1';life='DEE.Cognitive.System.1.1.life.v1'
            excluded={k for k in set(a['metadata'])|set(b['metadata'])if k==life or k==service or k.startswith(service+'.queue.')}
            differences=[k for k in sorted(set(a['metadata'])|set(b['metadata']))if k not in excluded and a['metadata'].get(k)!=b['metadata'].get(k)]
            equal=a['physical']==b['physical']and a['causal_prefix_sha256']==b['causal_prefix_sha256']and not differences
            observer.update(mode='recalculated_frozen_snapshot_bytes',binary_comparison_recalculated_here=True,physical_equal=a['physical']==b['physical'],physical=a['physical'],causal_prefix_equal=a['causal_prefix_sha256']==b['causal_prefix_sha256'],causal_prefix_sha256=a['causal_prefix_sha256'],nonadministrative_metadata_differences=differences,excluded_administrative_keys=sorted(excluded),interfaces=[a['interfaces'],b['interfaces']],pending=[a['pending'],b['pending']],receipts=[a['receipts'],b['receipts']],parser_limit=a['scope'])
            if not equal:errors.append('Observation snapshots differ')
    missing_r01=[kind+':'+arm for kind in('R01_observation','R01_calibration')for arm in('on','off')if not any(x['kind']==kind and x['arm']==arm for x in r01)]
    report={'schema':'PI02.portable.documentary-recalculation.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'engine_imports':0,'new_ticks':0,'index':str(indexpath)if indexpath.is_file()else'LOCAL_AUTOINDEX','file_checks':identities,'identity_or_structure_errors':errors,'missing_R02_arms_not_invented':missing,'missing_R01_captures_not_invented':missing_r01,'R01':r01,'R01_observer_comparison':observer,'R02A':work,'predeclared_criteria_observations':gates,'classical_references_separate':refs,'owned_host_runtime':runtime,'limits':['All arms are related-prefix deterministic branches, not independent new learners.','Detected recurrence and busy are prepared; no learned timing inferred.','Classical references are evaluator computations, not new Native trials or controllers ofE1.','When snapshots are omitted, the prior R01 global comparison is reported as a witness rather than claimed newly recalculated.','R03/B/C/retention/adoption are not certified by this initial R01/R02A verifier. Unknown capture kinds are explicitly listed.','Not a runnable life backup or fresh experimental reproduction.']}
    out.mkdir(parents=True,exist_ok=True);(out/'RECALCULO_PI02.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with(out/'RECALCULO_PI02_R02A.csv').open('w',encoding='utf-8-sig',newline='')as f:
        fields=['life','arm','episode','query_tick','route_from_RAW','access','physical_response','reference_response_auditor_only','reference_matches_physical','applied_command','accepted','native_requested','native_applied','native_rejected'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for case in work:
            for row in case['rows']:
                v={k:row.get(k)for k in fields};v.update(native_requested=row['native_denominators']['requested_unique'],native_applied=row['native_denominators']['applied'],native_rejected=row['native_denominators']['rejected']);w.writerow({k:'NULL'if x is None else x for k,x in v.items()})
    print(json.dumps({'resources_by_arm':observed,'missing_arms':missing,'native_counts':{x['arm']:{k:x[k]for k in ('detected_return_signatures','admitted_jobs','busy_discarded','new_native_requested_unique','new_native_applied','new_native_rejected','negative_feedback_requested')}for x in work},'reference_resources':{k:v['resources']for k,v in refs.items()},'errors':errors,'case_inconsistencies':{x['arm']:x['inconsistencies']for x in work},'outputs':['RECALCULO_PI02.json','RECALCULO_PI02_R02A.csv'],'new_native_ticks':0},ensure_ascii=False,indent=2))
    return 2 if strict and(errors or missing or missing_r01 or any(x['inconsistencies']for x in work+r01))else 0
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);p.add_argument('--strict',action='store_true');p.add_argument('--export-to',type=Path);p.add_argument('--include-observer-snapshots',action='store_true');args=p.parse_args()
    if args.export_to:print('Exported:',export_evidence(args.root,args.export_to,args.include_observer_snapshots))
    raise SystemExit(run(args.root,args.out_dir,args.strict))
