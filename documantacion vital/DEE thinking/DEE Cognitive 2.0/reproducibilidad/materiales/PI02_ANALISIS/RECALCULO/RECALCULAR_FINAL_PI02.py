"""Portable final PI02 retention/reopening verifier. Python stdlib; no DEE.

python -I -B -X utf8 RECALCULAR_FINAL_PI02.py --root EXTRACTED --output OUT.json
Uses only EVIDENCIA/E_FINAL and the already exported D_R04 historical prefix.
Does not reopen/restore a Native world, reproduce experiments or decide adoption.
"""
from pathlib import Path,PurePosixPath
import argparse,collections,datetime,gzip,hashlib,json,re,sys

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
    b=p.read_bytes();return gzip.decompress(b)if p.suffix=='.gz'else b
def read(p):return json.loads(load(p).decode('utf-8-sig'))
def exact(v):
    if type(v)is int:return v
    if isinstance(v,str)and re.fullmatch(r'-?[0-9]+',v):return int(v)
    raise ValueError('Exact integer/string required, not float/bool')
def safe(base,name):
    q=PurePosixPath(name)
    if q.is_absolute()or'..'in q.parts or'\\'in name or':'in name:raise ValueError('Unsafe evidence path')
    p=base.joinpath(*q.parts)
    if not p.resolve(strict=True).is_relative_to(base.resolve(strict=True)):raise ValueError('Evidence escapes export')
    if not p.is_file():raise ValueError('Missing evidence file')
    return p
def raw(o):
    n=exact(o['raw'])
    if not 0<=n<2**64:raise ValueError('RAW outside uint64')
    def nib(k):
        x=(n>>k)&15;return x-16 if x&8 else x
    return {'state':n&0xffffffff,'s_reg':(n>>32)&65535,'semantic':(n>>60)&15,'direction':[nib(k)for k in(48,52,56)]}
def fi(o):
    f=raw(o);x,y,z=f['direction']
    return x if f['state']>0 and f['semantic']==1 and x in(-1,0,1)and y==1 and z in(0,-1)else None
def run(root):
    base=root/'EVIDENCIA/E_FINAL';index=read(base/'INDICE_E_FINAL.json');errors=[]
    def check(ok,msg):
        if not ok:errors.append(msg)
    checked=[]
    for item in index['files']:
        p=safe(base,item['file']);b=p.read_bytes();decoded=load(p)
        check(len(b)==item['bytes']and sha(b)==item['sha256'],'Stored bytes/hash '+item['file'])
        check(len(decoded)==item['decoded_bytes']and sha(decoded)==item['decoded_sha256'],'Decoded bytes/hash '+item['file']);checked.append(item['file'])
    observations=0
    def walk(x):
        nonlocal observations
        if isinstance(x,dict):
            if {'raw','clock','site','state','s_reg','semantic','direction'}<=set(x):
                for k,v in raw(x).items():check(x[k]==v,'Serialized '+k+' differs from exact RAW')
                check(0<=exact(x['clock'])<2**64,'Invalid exact clock');observations+=1
            for v in x.values():walk(v)
        elif isinstance(x,list):
            for v in x:walk(v)
    def primary(name):
        x=read(safe(base,'panel/'+name+'.json.gz'));check(x['status']=='completed','Incomplete '+name)
        payload=json.loads(x['payload'])if isinstance(x['payload'],str)else x['payload']
        result=json.loads(x['result'])if isinstance(x['result'],str)else x['result'];walk(result)
        check(len(result['result']['rows'])==1,'One command per panel use')
        return payload,result,result['result']['rows'][0]
    protocol=read(base/'PROTOCOLO_PANEL_RETENCION_PI02.json');summary=read(base/'RESUMEN_RETENCION_PI02.json')
    check(sha(load(base/'PROTOCOLO_PANEL_RETENCION_PI02.json'))==summary['protocol_sha256'],'Frozen protocol identity')
    check(sha(load(base/'fuentes/panel_retencion_PI02.py'))==protocol['script_sha256'],'Exact panel executor identity')
    pause_payload,pause,pause_row=primary('PI02_RET_FINAL_HABITAT_OFF')
    check(pause['before_tick']==pause['after_tick']==750137,'External pause must be zero ticks')
    check(pause_row.get('operator_change_not_learned_regulation')is True,'Explicit external pause attribution')
    rows=[];all_receipts={};receipt_aliases=0;previous=None;last_tick=750137;last_panel_physical=None
    for planned,witness in zip(protocol['sequence'],summary['rows']):
        label=planned['label'];payload,result,row=primary(witness['id']);before=result['before_tick'];after=result['after_tick']
        check(before==last_tick,'Panel is not a consecutive single-life trajectory');last_tick=after
        last_panel_physical=result['committed_snapshot']['physical']
        literal=planned['literal']
        if literal is None:literal={'modo':'eci01-aritmetica-directa','operacion':'diferencia','izquierda':previous,'derecha':5}
        check(payload['situaciones']==[literal],'Actual panel input deviates from frozen literal/actual predecessor')
        if label.startswith('FI'):
            o=row['early_observation'];value=fi(o);items=row['all_material_receipts']
            check(o['site']==[15,15,15]and o['tick']==row['query_tick']+4==row['early_tick'],'Frozen early FI reader')
            check(value==row['early_physical_choice'],'FI declared answer differs from RAW')
        elif label.startswith('number'):
            reader=row['numeric_reader'];trial=row['native_operation']['native_trial'];operation=literal['operacion'];at=exact(trial['datum_tick'])-2
            frames=[f for f in trial['frames']if exact(f['tick'])==at];check(len(frames)==1,'Unique frozen numeric frame')
            o=frames[0]['fields']['C'];f=raw(o)
            valid=o['site']==[12,17,18]and exact(o['tick'])==at and f['state']>0 and f['semantic']==1 and f['direction']==[1,-1,-1]
            value=f['s_reg']-(0 if operation=='suma'else 32)if valid else None;items=trial['requests']
            check(o==reader['observation']and value==reader['numeric_result']==row['numeric_result'],'Numeric result differs from frozen RAW transduction')
            check(row['provider_called']is False and row['teacher_delivered']is False,'No teacher/provider during direct arithmetic')
            if label=='number13':previous=value
        else:
            if label.startswith('alfa'):row=row['result']['rows'][0]
            reader=row['reader'];signs=[]
            for o in reader['panel']:
                f=raw(o)
                if f['state']>0 and f['semantic']==1 and f['direction']in([0,0,-1],[0,0,1]):signs.append(f['direction'][2])
            value=signs[0]if len(signs)==1 else None;items=row['requests']
            check(value==reader['formed_native_command'],'MA/lexical result differs from fixed RAW panel')
        unique={}
        for item in items:
            receipt=item['receipt'];i=exact(item['id']);check(i==exact(receipt['id']),'Native request/receipt identity')
            if i in unique:check(unique[i]==receipt,'Conflicting receipt alias')
            unique[i]=receipt
            if i in all_receipts:receipt_aliases+=1;check(all_receipts[i]==receipt,'Conflicting cross-panel receipt alias')
            else:all_receipts[i]=receipt
        counts=collections.Counter(x['status']for x in unique.values());expected=planned['auditor_only_expected']
        check(type(value)is int and value==expected,'First physical answer disagrees with frozen witness '+label)
        check(value==witness['response'],'Panel summary answer '+label)
        rows.append({'label':label,'id':witness['id'],'before_tick':before,'after_tick':after,'physical_response':value,'auditor_expected_after_decoding':expected,'requested_unique':len(unique),'statuses':dict(counts)})
    status=collections.Counter(x['status']for x in all_receipts.values())
    check(len(rows)==12 and last_tick==751546,'Panel coverage/cut')
    check(len(all_receipts)==929 and status=={'applied':929}and receipt_aliases==0,'929 canonical Native admissions, no rejected/pending/aliases')
    reopening=read(base/'REAPERTURA_Y_CONTINUACION_PI02.json.gz');walk(reopening)
    check(reopening['life_id']==index['life_id']=='ECI02_PI02_MAIN','Single life identity')
    check(reopening['before']['tick']==751546 and reopening['after']['tick']==index['final_tick']==753346,'Separate-process continuation cuts')
    check(reopening['new_Native_ticks']==1800 and reopening['owner_closed']is True,'Recorded 1800-tick closed continuation')
    physical_keys=('N','tick','RAW_sha256','clocks_sha256')
    expected_physical={k:reopening['before'][k]for k in physical_keys}
    check(reopening['initial_reopened_physical']==expected_physical,'Reopening preserved physical state')
    check(all(last_panel_physical[k]==expected_physical[k]for k in physical_keys),'Final panel committed physics equals reopened cut')
    rr=reopening['rows'];check(len(rr)==6,'Six bounded reopening operations')
    for r in rr:
        x=r['result'];check(x['after_tick']-x['before_tick']==(1800 if r['id']=='PI02_REOPEN_TIME'else 0),'Unexpected Native advance in technical/work-offer operation')
    offered=[r['result']['result']['rows'][0]for r in rr if r['id']in('PI02_REOPEN_WORK13','PI02_REOPEN_WORK7')]
    check(len(offered)==2 and all(x['new_native_ticks']==0 and x['Native_content_reintroduced']is False for x in offered),'Two public opportunities, no Native teaching/reset')
    check([(x['fixture_environment_only']['public'],x['fixture_environment_only']['warning_lead'])for x in offered]==[({'left':13,'right':5},128),({'left':7,'right':16},195)],'Predeclared final work fixtures')
    prefixp=safe(root,'EVIDENCIA/D_R04/RES_MAIN/eventos.jsonl.gz');prefix=load(prefixp);pi=index['prefix']
    check(len(prefixp.read_bytes())==pi['bytes']and sha(prefixp.read_bytes())==pi['sha256']and len(prefix)==pi['decoded_bytes']and sha(prefix)==pi['decoded_sha256'],'Frozen D_R04 prefix preserved')
    original_cut=read(safe(root,'EVIDENCIA/D_R04/RES_MAIN/summary.json.gz'))['requests'][-1]['result']['committed_snapshot']['physical']
    check(all(pause['committed_snapshot']['physical'][k]==original_cut[k]for k in physical_keys),'Panel starts from exact D_R04 committed physics')
    suffix=load(safe(base,index['journal']['suffix_file']));full=prefix+suffix;events=[json.loads(x)for x in full.splitlines()]
    check(len(events)==index['journal']['full_events']==413 and len(full)==index['journal']['full_decoded_bytes']and sha(full)==index['journal']['full_sha256']==reopening['journal_sha256'],'Exact full final journal reconstruction')
    check(len(prefix.splitlines())==344 and len(suffix.splitlines())==69,'Historical prefix and new suffix bounds')
    chain=bytes(32)
    for i,(line,event)in enumerate(zip(full.splitlines(keepends=True),events)):
        check(event['index']==i and line.endswith(b'\n'),'Journal exact order/completeness');chain=hashlib.sha256(chain+line).digest();walk(event)
    final_view=rr[-1]['result']['result']['rows'][0]['habitat']
    check(final_view['log_count']==413 and final_view['log_chain_sha256']==chain.hex(),'Committed final R04 chain')
    check(events[:344][-1]['tick']<=750137 and all(x['tick']>=751546 for x in events[344:]),'Material panel interval was not secretly habitat work')
    new_done=[x for x in events[344:]if x['kind']=='OPPORTUNITY_COMPLETED'];check(new_done==reopening['new_opportunities'],'Exact continuation outcome projection')
    device_costs=[]
    for event in events[344:]:
        if event['kind']=='DEVICE_COMMAND'and event['applied']:
            item=event['actual_control_packet'];artifact=safe(base,'banco/control_spent/'+item['file']).read_bytes()
            check(len(artifact)==item['bytes']==event['resource_cost_bytes']==64 and sha(artifact)==item['sha256'],'Actual finite control packet cost')
            check(event['command']=='CLOSE'and event['origin']=='learned_warning'and event['wiring']=='normal','Final fixed warning actuator attribution')
            device_costs.append({'tick':event['tick'],'bytes':len(artifact),'sha256':sha(artifact)})
    check(len(device_costs)==2,'Two final finite control packet costs')
    work=[]
    for done in new_done:
        ep=done['episode'];em=next(x for x in events[344:]if x['kind']=='FI_EMISSION_AND_EFFECT'and x['episode']==ep);frame=next(x for x in events[344:]if x['kind']=='FI_FRAME_FINISHED'and x['episode']==ep)
        o=em['emission']['observation'];choice=fi(o);effect=done['effect'];l,r=effect['loads_before'];nl,nr=l,r
        if choice==1 and l>0 and r<32:nl-=1;nr+=1
        elif choice==-1 and r>0 and l<32:nl+=1;nr-=1
        useful=choice is not None and(abs(nl-nr)<abs(l-r)or(l==r and choice==0))
        check(choice==em['emission']['physical_choice']==effect['physical_choice']==effect['applied_command'],'Final command originates in FI RAW')
        check(effect['loads_after']==[nl,nr]and effect['useful']==useful,'Final material actuator consequence')
        check(frame['trial']['early_observation']==o,'FI finish/emission observations agree')
        check(o['tick']==em['emission']['query_tick']+4,'Final fixed q+4 reading')
        item=effect['resource'];artifact=safe(base,'banco/collected/'+item['file']).read_bytes()
        check(useful and len(artifact)==item['bytes']==64 and sha(artifact)==item['sha256'],'Actual useful resource artifact')
        work.append({'episode':ep,'physical_choice':choice,'loads_before':[l,r],'loads_after':[nl,nr],'useful':useful,'resource_sha256':sha(artifact)})
    check([x['physical_choice']for x in work]==[1,-1]and len(work)==2,'Two opposite useful choices after reopening')
    unexpected_U=[x for x in events[344:]if x['kind']=='ACTUAL_INPUT_FAILURE_SENSOR'];check(not unexpected_U,'No additional failure teaching during final work')
    pair=read(base/'PAR_FINAL_PI02.json');check(pair['source_life']==index['life_id']and pair['source_tick']==753346,'Final local pair locator cut')
    pairphysical=pair['transport_receipt']['result'];pairphysical=json.loads(pairphysical)if isinstance(pairphysical,str)else pairphysical
    check(all(pairphysical['committed_snapshot']['physical'][k]==reopening['after'][k]for k in physical_keys),'Final pair descriptor physical witness')
    return {'schema':'PI02.final_panel_reopening.passive_recalculation.v1','calculated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_Native_ticks':0,'DEE_imports':0,'files_hash_checked':len(checked),'life_id':index['life_id'],
        'retention_panel':{'first_tick':750137,'last_tick':751546,'requested_uses':12,'formed_correct':sum(type(x['physical_response'])is int and x['physical_response']==x['auditor_expected_after_decoding']for x in rows),'Native_requested_unique':len(all_receipts),'Native_statuses':dict(status),'aliases_not_counted':receipt_aliases,'rows':rows,'scope':'Representative operator-requested first-use panel without teacher/feedback; no twelve-use panel claimed at final cut.'},
        'reopening_and_use':{'initial_tick':751546,'final_tick':753346,'recorded_new_Native_ticks_in_existing_experiment':1800,'physical_preservation_verified_from_records':True,'new_public_jobs_offered_zero_ticks':2,'new_useful_work':work,'finite_control_packet_costs':device_costs,'no_additional_U_events':not unexpected_U,'journal_events':len(events),'journal_sha256':sha(full),'journal_chain_sha256':chain.hex()},
        'RAW_observation_serializations_checked':observations,'errors':errors,'limits':['Documentary recalculation only: existing experiments were not replayed.','Equality on reopening is supported by saved physical hashes/owner receipts; no full snapshot in this export.','The continuous final history includes externally pausing/resuming the prepared habitat. These are not learned regulation actions.','Native comparison, fixed transduction, prepared environment, and actual artifact consequence are distinguished. No general policy/control/autonomy or promotion verdict.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path);a=p.parse_args();r=run(a.root)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'formed_correct':r['retention_panel']['formed_correct'],'Native_statuses':r['retention_panel']['Native_statuses'],'new_useful_work':r['reopening_and_use']['new_useful_work'],'errors':r['errors'],'new_Native_ticks':0},ensure_ascii=False,indent=2));sys.exit(bool(r['errors']))
