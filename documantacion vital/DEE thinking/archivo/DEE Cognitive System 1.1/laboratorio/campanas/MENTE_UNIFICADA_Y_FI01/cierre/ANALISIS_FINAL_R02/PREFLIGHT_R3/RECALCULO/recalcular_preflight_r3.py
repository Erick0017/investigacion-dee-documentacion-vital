"""Exact archived R3_01..13 preflight recalc; stdlib only, zero native ticks.

This observer is not an actor. It does not load a world, advance a service,
execute a worker, inspect current S, or supply any decoded value to E1.
"""
from __future__ import annotations
import argparse,base64,collections,gzip,hashlib,json,zlib
from pathlib import Path

NAMES=['R3_01_ESTADO','R3_02_UNICA_EXPERIENCIA_B','R3_03_PROTECCION_P0','R3_04_SEIS_ANTES','R3_05_DATO13','R3_06_DATO32','R3_07_RAW128_INDEX4','R3_08_CADENA_PREPARAR','R3_09_GUARDAR_PENDIENTE','R3_10_CADENA_FINALIZAR','R3_11_SEIS_DESPUES','R3_12_GUARDAR_CORTE','R3_13_ESTADO_CORTE']
CONTEXTS=['alfa','beta','gamma','delta','epsilon','zeta'];SIGNS=[-1,1,1,-1,-1,1]

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def walk(x,loc='$'):
    if isinstance(x,dict):
        yield loc,x
        for k,v in x.items():yield from walk(v,loc+'.'+k)
    elif isinstance(x,list):
        for j,v in enumerate(x):yield from walk(v,loc+'['+str(j)+']')
def signed(v,k):
    a=(v>>k)&15;return a-16 if a&8 else a
def fields(v):return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':v>>60,'direction':[signed(v,k)for k in(48,52,56)]}
def physical_signature(q):return {k:q[k]for k in('N','tick','RAW_sha256','clocks_sha256')}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--evidencia',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
    checks=0;observations=0;receipts={};timeline=[];cases={};source_hashes={};response_rows=[]
    def ck(ok,label):
        nonlocal checks
        checks+=1
        if not ok:raise AssertionError(label)
    def exact(o):
        nonlocal observations
        d=fields(int(o['raw']));ck(all(o[k]==v for k,v in d.items()),'exact RAW field decoding '+str(o.get('site')));observations+=1
    def native_reader(reader):
        cs=[]
        for o in reader['observations']:
            exact(o);x=(o['site'][0]-15)//2;z=(o['site'][2]-15)//2
            if o['state']>0 and o['semantic']==1 and o['direction']==[x,1,z]:cs.append(x)
        answer=cs[0]if len(cs)==1 else None;ck(reader['choice']==answer,'fixed six-direction decoder');return answer
    def memory_reader(reader):
        cs=[]
        for o in reader['panel']:
            exact(o);sg=o['site'][2]-33
            if sg in(-1,1)and o['state']>0 and o['semantic']==1 and o['direction']==[0,0,sg]:cs.append(sg)
        answer=cs[0]if len(cs)==1 else None;ck(reader['formed_native_command']==answer,'fixed old12gate decoder');return answer
    def rows(num):return cases[num]['result']['result']['rows']
    def final(num):
        r=cases[num]['result'];return r['result']['final']if num not in(1,3,9,12,13)else r
    for num,name in enumerate(NAMES,1):
        p=a.evidencia/(name+'.json.gz');d=load(p);cases[num]=d;source_hashes[p.name]=sha(p.read_bytes())
        ck(d['case']==name and d['phase']=='B'and d['returncode']==0 and not d['timed_out'],'successful exact operation '+name)
        ck(d['stderr']=='','no ignored stderr diagnostic '+name)
        ck(json.loads(d['stdout'])==d['result'],'stdout exactly equals parsed primary '+name)
        ck('--vida'in d['argv']and d['argv'][d['argv'].index('--vida')+1]=='MU_MAIN_FASE_R3','single declared life '+name)
        unique={}
        for loc,q in walk(d['result']):
            if {'raw','state','s_reg','semantic','direction','site'}<=set(q):exact(q)
            r=q.get('receipt')
            if isinstance(r,dict)and 'status'in r:
                rid=r['id'];ck(q['id']==rid,'receipt request id '+name)
                normalized=json.dumps(q,sort_keys=True,separators=(',',':'))
                if rid in receipts:ck(receipts[rid]['request']==normalized,'no conflicting duplicate receipt '+str(rid))
                receipts[rid]={'request':normalized,'receipt':r,'case':name};unique[rid]=r
                ck(r['requested_tick']==q['tick']and r['effective_tick']==q['tick'],'admission exactly at requested tick '+str(rid))
        ph=d['result']['physical'];timeline.append({'case':name,'tick':ph['tick'],'RAW_sha256':ph['RAW_sha256'],'clocks_sha256':ph['clocks_sha256'],'requested_unique':len(unique),'statuses':dict(collections.Counter(r['status']for r in unique.values()))})
    ck(len({d['code_revision_sha256']for d in cases.values()})==1,'one frozen execution revision')
    ck(sorted(receipts)==list(range(6511,6791))and len(receipts)==280,'complete unique receipt range6511..6790')
    ck(all(q['receipt']['status']=='applied'for q in receipts.values()),'280/280applied including teaching and all generic resources')
    before=cases[1]['result'];teach=rows(2)[0];after=final(2)
    ck([o['s_reg']for o in before['references']]==[120,141],'actual initialDminus21')
    ck(teach['side_declared_by_teacher']=='B'and teach['request']['payload']==0 and teach['request']['port']=='MU.selector.experience.B','one explicit B0 contact, not a field repair')
    ck(teach['request']['tick']==69204 and teach['arrival_tick']==69207,'explicit B0 contact times')
    ck([o['s_reg']for o in after['references']]==[121,141],'actual post-teachingDminus20')
    ck(physical_signature(teach['before'])==physical_signature(before['physical']),'own unchanged fork prefix before teaching')
    ck(before['operational']['explicit_teaching_events']==20 and after['operational']['explicit_teaching_events']==21,'exactly one new explicit teaching event')
    protection=cases[3]['result']['result']
    ck(protection['native_ticks_advanced']==0 and protection['learned_fields_edited']is False,'protection is metadata-only zero-tick P0')
    ck(physical_signature(cases[3]['result']['physical'])==physical_signature(cases[2]['result']['physical']),'protection unchanged full physical hashes')
    ck(protection['phase_protection']['enabled']is True and protection['phase_protection']['admitted_tick']==69209,'explicit enabled flag')
    # All native operations are consecutive; checkpoint saves do not rewind time.
    previous=cases[3]['result']['physical'];old_panels=[]
    for num in range(4,14):
        if num in(9,12,13):
            ck(physical_signature(cases[num]['result']['physical'])==physical_signature(previous),'save/read does not advance or replace physical state '+str(num));continue
        rr=rows(num)
        if num in(4,11):
            qs=[row['result']['rows'][0]for row in rr]
            ck([q['context_signal']for q in qs]==CONTEXTS,'old fixed panel order '+str(num));commands=[]
            for q in qs:
                ck(physical_signature(q['before'])==physical_signature(previous),'continuous old query prefix '+str(num));command=memory_reader(q['reader']);commands.append(command)
                response_rows.append({'case':NAMES[num-1],'context':q['context_signal'],'choice':command,'kind':'old_memory'});previous=q['after']
            ck(commands==SIGNS,'all six old contents retained '+str(num));old_panels.append({'case':NAMES[num-1],'commands':commands,'requested':42,'admitted':42})
        elif num in(5,6,7):
            q=rr[0];ck(physical_signature(q['before'])==physical_signature(previous),'continuous sensory prefix '+str(num));answer=native_reader(q['reader'])
            expected=-1 if num==5 else 1
            ck(answer==expected,'frozen sensory answer '+str(num));previous=q['after'];response_rows.append({'case':NAMES[num-1],'choice':answer,'kind':'raw128'if num==7 else'current'})
            timing=q['timing'];ck(timing['enabled']and timing['wait_ticks']==0 and timing['effective_query_tick']==q['query_tick'],'preflight sensor calendars have no delay '+str(num))
            ck((q['query_tick']-2)//391==(q['query_tick']+8)//391,'fixed window excludes writing boundary '+str(num))
            if num in(5,6):ck(q['raw_sensor_value']==(13 if num==5 else 32),'exact raw scalar '+str(num))
            else:
                vector=[0]*128;vector[0]=19;vector[4]=2;ck(q['raw_components']==vector and q['all_components_same_tick'],'same128-component prepared vector')
                ck(len(q['requests'])==176,'128raw+48generic count')
        elif num==8:
            q=rr[0]['memory_use']['rows'][0];ck(physical_signature(q['before'])==physical_signature(previous),'chain begins from actual prefix')
            command=memory_reader(q['reader']);ck(q['context_signal']=='gamma'and command==1,'gamma native selects prepare+')
            previous=q['after'];response_rows.append({'case':NAMES[num-1],'choice':command,'kind':'memory_for_actual_prepare'})
        elif num==10:
            q=rr[0]['native_use'];ck(physical_signature(q['before'])==physical_signature(previous),'same saved/reloaded physical prefix')
            answer=native_reader(q['reader']);ck(answer==-1 and q['raw_sensor_value']==13,'actual byte count drives fixed native comparator, not expected worker')
            previous=q['after'];response_rows.append({'case':NAMES[num-1],'choice':answer,'kind':'current_for_actual_verify'})
            ck(q['timing']['wait_ticks']==0,'chain final sensor had no calendar displacement')
        ck(physical_signature(previous)==physical_signature(cases[num]['result']['physical']),'outer physical witness equals actual end '+str(num))
    # Reconstruct exact external bytes contained in the archived pending record.
    begin=rows(8)[0];finish=rows(10)[0];wr0=begin['external']['worker_receipt'];wr1=finish['external']['worker_receipt'];pending=wr0['pending_transaction']
    ck(begin['external']['feedback']=='omit'and finish['external']['feedback']=='omit'and begin['external']['return']is None and finish['external']['return']is None,'no hidden environmental outcome-teaching in the actual chain')
    payload=base64.b64decode(pending['payload_base64'],validate=True);artifact=base64.b64decode(pending['prepared_output_base64'],validate=True)
    ck(len(payload)==122 and sha(payload)==pending['payload_sha256']==wr0['input_sha256']==wr1['input_sha256'],'exact122Bpayload across processes')
    ck(len(artifact)==13 and sha(artifact)==pending['prepared_output_sha256']==wr0['output_sha256'],'exact13Bserialized prepared artifact')
    ck(zlib.decompress(artifact)==payload,'prepared artifact actually decodes to serialized payload')
    ck(wr0['worker']==begin['external']['native_choice']==1 and wr0['accepted']and wr0['operation']=='prepare','actual native-selected prepare receipt')
    ck(finish['measurement']['bytes']==len(artifact)and finish['measurement']['sha256']==sha(artifact)and finish['measurement']['restored_exact_serialized_external_state'],'sensor used exact serialized artifact bytes')
    check=wr1['prepared_artifact_check'];ck(check['actual_file_read']and check['valid']and check['bytes']==13 and check['sha256']==sha(artifact)and check['restored_from_exact_snapshot_external_bytes'],'actual verify witness carried pending bytes after reload')
    ck(wr1['worker']==finish['external']['native_choice']==-1 and wr1['accepted']and wr1['transaction_completed']and wr1['operation']=='verify_commit','actual opposite native-selected commit')
    digest=hashlib.sha256(payload).digest();ck(wr1['output_bytes']==len(digest)==32 and wr1['output_sha256']==sha(digest),'exact32Bverify product digest')
    ck(final(8)['operational']['external_pending']==pending and final(8)['operational']['cascade_pending']['values']==[29,4],'pending complete content in archived operational state')
    ck(final(10)['operational']['external_pending']is None and final(10)['operational']['cascade_pending']is None,'pending really cleared after accepted commit')
    end=cases[13]['result'];ck([o['s_reg']for o in end['references']]==[123,143],'actual finalDminus20')
    ck(end['physical']['tick']==70223 and end['operational']['explicit_teaching_events']==21,'closed preflight tick and no second teaching')
    result={'classification':'Archived preflight recalc, zero native ticks and no external worker execution','cases':13,'checks':checks,'failures':0,'RAW_observation_instances_decoded':observations,
      'source_primaries_sha256':source_hashes,'code_revision_sha256':next(iter(cases.values()))['code_revision_sha256'],'timeline':timeline,
      'native_admission':{'requested_unique':280,'applied':280,'rejected':0,'unresolved':0,'ids':[6511,6790]},'functional_responses':response_rows,
      'old_panels':old_panels,'reference':{'initial':[120,141],'initial_difference':-21,'after_explicit_B0':[121,141],'after_explicit_B0_difference':-20,'final':[123,143],'final_difference':-20},
      'explicit_teaching_events':1,'P0_protection_ticks':0,'sensor_calendar_displacements_in_this_preflight':[0,0,0,0],
      'actual_chain':{'prepared_bytes':13,'payload_bytes':122,'committed_digest_bytes':32,'accepted_operations':2,'commits':1,'same_physical_hashes_before_save_and_finish':True,'serialized_pending_artifact_verified':True,
       'identity_scope':'Same declared life, native RAW/clocks prefix and exact pending external bytes; these13compact primaries alone do not establish byte identity of all saved metadata/queues.'},
      'limits':['B0 is explicit content/reference revision, not retention or autonomous recovery.','P0 adds no learned field or tick, but this preflight has zero actual phase displacements; the positive delayed contrast is R16, not reproduced here.','Two six-content panels are consecutive uses of one life, not12independent learners.','17native reads are not17new skills,128raw fields are not128concepts.','This recalc does not reproduce the native world or new3720second service.']}
    a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':main()
