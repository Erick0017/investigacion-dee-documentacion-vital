"""Pure extraction-only PI09 consultation and matched-reference verifier.

No Native/DEE imports or original-source opens. All declared literal members,
including adverse attempts, are checked. The PI08 second-stage verifier and
PI07 RAW/receipt decoder are frozen stdlib documentary dependencies.
"""
from pathlib import Path, PurePosixPath
from collections import Counter,defaultdict
import argparse, hashlib, importlib.util, json

VERSION='DEE.PI09.selective_registered_consultation.R01'
VERSIONS={VERSION,'DEE.PI09.selective_registered_consultation.R02'}
OLD_SHA='4e8dd7b8df3d574c2cc7cd123ac47dc18881e285b926aa9d96ead97712523c91'
def sha(data):return hashlib.sha256(data).hexdigest()
def canon(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
def require(ok,why):
    if not ok:raise ValueError(why)
def local(root,name):
    require(isinstance(name,str)and name and'\\'not in name and':'not in name,'Relative POSIX evidence only')
    p=PurePosixPath(name);require(not p.is_absolute()and all(v not in('','.','..')for v in name.split('/')),'Evidence escape')
    file=root.joinpath(*p.parts)
    for v in(file,*file.parents):
        if v==root.parent:break
        require(not v.is_symlink()and not(getattr(v.lstat(),'st_file_attributes',0)&1024),'No linked/reparse evidence')
    file=file.resolve(strict=True);require(file.is_relative_to(root),'Escaped extraction');return file
def checked(root,item):
    data=local(root,item['file']).read_bytes();require(len(data)==item['bytes']and sha(data)==item['sha256'],'Evidence bytes/hash mismatch: '+item['file']);return data
def rows(primary):
    value=primary.get('result');value=json.loads(value)if isinstance(value,str)else value
    if value is None:return []
    value=value.get('result',value);return value.get('rows',[])
def motor(choice):return None if choice is None else 1 if choice==1 else -1
def extra(m,obj):
    v=m.observation(obj)
    if int(obj['raw'])==0:return 0
    if v['state']>0 and v['semantic']==1:
        if v['direction']==[0,0,1]:return 1
        if v['direction']==[1,0,0]:return 0
    return None
def load_literal():
    file=Path(__file__).with_name('RECALCULAR_C_PI08_LITERAL.py');require(sha(file.read_bytes())==OLD_SHA,'Frozen stdlib PI08 verifier changed')
    s=importlib.util.spec_from_file_location('pi09_documentary_literal_C',file);old=importlib.util.module_from_spec(s);s.loader.exec_module(old);old.VERSION=VERSION
    return old,old.parser()
def first_stage(first,w,row,arm,m,old,all_sources):
    q=first['query_tick'];require(w['query_tick']==q and w['ordinal']==row['ordinal']and w['observation_tick']==q+8 and first['reader']['tick']==q+4,'Fixed first windows differ')
    sample=w['actual_preview_observation'];physical=m.observation(sample);require(sample==first['sample_register']['actual_preview_observation']and sample['site']==[30,40,30]and sample['tick']==q-1 and w['first_submitted_STATE']==physical['state'],'Actual partial STATE source differs')
    choice=old.reader(w['reader'],m);native=motor(choice)
    policy='always'if arm.startswith('always')else'never'if arm=='never'else'native'
    actual=native if policy=='native'else 1 if policy=='always'else -1
    require(first['native_motor']==w['native_motor']==native and first['actual_query_motor']==w['actual_query_motor']==actual and first['query_control']==policy,'Native choice/reference action conflated')
    direct,counts,aliases=old.summary(first['requests'],first['Native_inputs'],m)
    qrequest=first['question_request'];require((qrequest is not None)==(actual==1),'Material query does not follow declared policy')
    status=None
    if qrequest:
        require(qrequest['site']==[33,40,30]and qrequest['direction']==[1,0,0]and qrequest['payload']==0 and qrequest['requested_tick']==q+7,'Fixed question inlet changed')
        status=direct[qrequest['id']]['status']
    observed=m.observation(first['question_observation']);signature=observed['state']>0 and observed['semantic']==1 and observed['direction']==[1,0,0]
    require(first['question_observation']['site']==[34,40,30]and first['question_observation']['tick']==q+8,'Fixed query reader changed')
    released=status=='applied'and signature;reg=first['sample_register'];require(reg['question_applied_and_signature']is released and not(status=='applied'and not signature),'Unrecognized material access is NULL, never0')
    copies=[r for r in first['requests']if r.get('channel')in('PI07.TC.R01.copy.plus','PI07.TC.R01.copy.minus')]
    require(len(copies)==(actual is not None),'First actual eferent copy count differs')
    if copies:require(copies[0]['actual_motor_choice']==actual and copies[0]['requested_tick']==q+7,'Reference motor not physically copied')
    data=[r for r in first['requests']if r.get('channel')=='PI07.TC.R01.datum'];require(len(data)==1 and data[0]['payload']==physical['state']and data[0]['requested_tick']==q+3,'First TC got something other than actual STATE')
    require(not any(r.get('channel','').startswith('PI07.TC.R01.outcome.')for r in first['requests'])and first['no_generic_return_scheduled_for_first_trace'],'No query-specific generic credit was established')
    if not released:
        bit=0;require(reg.get('release_source')is None,'NoQuery cannot release hidden information')
    elif arm.endswith('desacoplado'):
        source=reg['release_source'];j=(row['ordinal']+5)%12
        require(source['source_ordinal']==source['ordinal']==j and sha(canon(source['observation']))==source['observation_sha256'],'Prefixed actual sample permutation/hash differs')
        require(source['primary_sha256']in all_sources and all_sources[source['primary_sha256']]==source['observation'],'Desynchronized sample must match an included actual always-real primary')
        bit=extra(m,source['observation']);require(bit is not None,'Unrecognized actual source has no fallback')
    else:
        bit=extra(m,sample);require(bit is not None and reg['release_source']['observation']==sample and reg['release_source']['observation_sha256']==sha(canon(sample)),'Real registered content/provenance differs')
    require(reg['released_bit']==row['extra_bit_entered_second_TC']==bit,'Released bit does not reach second TC')
    return {'Native_choice':choice,'Native_valid':choice is not None,'actual_query_motor':actual,'actual_STATE':physical['state'],'actual_RAW':sample['raw'],'actual_direction':physical['direction'],'question_scheduled':qrequest is not None,'question_status':status,'question_applied':status=='applied','question_signature':signature,'extra_released':released,'bit':bit,'sample_tick':q-1,'release_tick':q+8,'external_register_age_at_release':9,'current_real_bit_if_recognized':extra(m,sample),'Native_inputs':{'unique_requested':len(direct),'status_counts':dict(counts),'aliases_not_events':aliases}},direct

def calculate(root,index_name='INDICE_PI09_CONSULTA_R01.json'):
    root=Path(root).resolve(strict=True);index=json.loads(local(root,index_name).read_bytes());require(index['schema']=='DEE.PI09.consultation.portable_primary_index.R01','Exact PI09 index required')
    verified={}
    def members(x):
        if isinstance(x,dict):
            if {'file','bytes','sha256'}<=set(x):checked(root,x);require(x['file']not in verified or verified[x['file']]==x['sha256'],'Conflicting member alias');verified[x['file']]=x['sha256']
            for v in x.values():members(v)
        elif isinstance(x,list):
            for v in x:members(v)
    members(index);p=json.loads(checked(root,index['protocol']));require(len(p['schedule'])==18 and p['yoke_permutation']==[(i+5)%12 for i in range(12)],'Prospective protocol/stock differs')
    old,m=load_literal();products={item['sha256']:checked(root,item)for item in index['products']}
    witnesses={(item['arm'],json.loads(checked(root,item))['ordinal']):json.loads(checked(root,item))for item in index['witnesses']}
    source_samples={};parsed=[];failed=[];aux=[]
    for item in index['primaries']:
        primary=json.loads(checked(root,item));rr=rows(primary)
        if primary['status']!='completed':failed.append({'file':item['file'],'arm':item['arm'],'status':primary['status'],'error':primary.get('error')})
        for row in rr:
            if row.get('version')in VERSIONS and 'first_stage'in row:
                parsed.append((item,primary,row))
                if item['arm']=='always_real':source_samples[item['sha256']]=row['first_stage']['sample_register']['actual_preview_observation']
            else:aux.append({'file':item['file'],'arm':item['arm'],'version':row.get('version'),'ready':row.get('ready')})
    complete=[];by_group=defaultdict(list);allids=defaultdict(dict)
    for item,primary,row in parsed:
        arm=item['arm'];i=row['ordinal'];require(primary['status']=='completed'and 0<=i<18,'Only actual complete opportunity counts as complete')
        require((arm,i)in witnesses,'Immediate witness missing');w=witnesses[arm,i]
        ptr=row['external_immediate_first_stage_witness'];wdata=next(v for v in index['witnesses']if v['arm']==arm and json.loads(checked(root,v))['ordinal']==i)
        require(ptr['sha256']==wdata['sha256']and ptr['bytes']==wdata['bytes'],'Immediate witness pointer/hash differs')
        first,fd=first_stage(row['first_stage'],w,row,arm,m,old,source_samples)
        old.VERSION=row['version']
        second,sd=old.stage2(row['second_stage'],first['bit'],p,i,m,products)
        direct,counts,aliases=old.summary(row['requests'],row['Native_inputs'],m)
        require(set(direct)==set(fd)|set(sd),'Outer inputs must deduplicate exactly the two direct stages')
        require(row['actual_failed']is second['actual_failed']and row['returned_failed']is second['returned_failed']and row['old_metadata_literal_unchanged']and row['no_first_trace_credit_claim'],'Outcome/genealogy/credit attribution differs')
        q1=row['first_stage']['query_tick'];q2=second['query_tick'];wait=row.get('prepared_wait_ticks',0)
        require(q2>=q1+782 and wait==p['schedule'][i]['wait_ticks']and row.get('whole_new_native_ticks',row['new_native_ticks'])==row['after_tick']-row.get('before_prepared_wait',row['before_tick']),'Actual serial calendar/wait interval differs')
        group=(row['life_id'],arm,row['version'])
        for rid,receipt in direct.items():require(rid not in allids[group]or allids[group][rid]==receipt,'Cross-primary receipt alias differs');allids[group][rid]=receipt
        record={'life_id':row['life_id'],'version':row['version'],'arm':arm,'ordinal':i,'stage':p['schedule'][i]['stage'],'nominal_cue_auditor_only':p['schedule'][i]['cue'],'before_tick':row.get('before_prepared_wait',row['before_tick']),'after_tick':row['after_tick'],'Native_ticks':row['after_tick']-row.get('before_prepared_wait',row['before_tick']),'prepared_wait_ticks':wait,'q1':q1,'q2':q2,'q2_minus_q1':q2-q1,'q1_mod67':q1%67,'q2_mod67':q2%67,'q1_mod391':q1%391,'q2_mod391':q2%391,'q1_mod782':q1%782,'q2_mod782':q2%782,'first':first,'second':second,'joint_useful':not second['actual_failed'],'Native_inputs':{'unique_requested':len(direct),'status_counts':dict(counts),'aliases_not_events':aliases},'primary_sha256':item['sha256']}
        complete.append(record);by_group[group].append(record)
    groups=[]
    for (life,arm,version),rr in sorted(by_group.items()):
        rr.sort(key=lambda r:r['ordinal']);require([r['ordinal']for r in rr]==list(range(len(rr))),'No omitted/unordered intermediate opportunity')
        statuses=Counter(v['status']for v in allids[life,arm,version].values());reserve=[r for r in rr if r['stage']=='reserved']
        groups.append({'life_id':life,'version':version,'arm':arm,'completed':len(rr),'useful':sum(r['joint_useful']for r in rr),'development_completed':sum(r['stage']=='development'for r in rr),'reserved_completed':len(reserve),'reserved_useful':sum(r['joint_useful']for r in reserve),'Native_first_valid':sum(r['first']['Native_valid']for r in rr),'questions_scheduled':sum(r['first']['question_scheduled']for r in rr),'questions_applied':sum(r['first']['question_applied']for r in rr),'extra_bits_released':sum(r['first']['extra_released']for r in rr),'actual_query1_choices':[r['first']['Native_choice']for r in rr],'actual_question_motors':[r['first']['actual_query_motor']for r in rr],'actual_query2_choices':[r['second']['Native_choice']for r in rr],'actual_failed':[r['second']['actual_failed']for r in rr],'Native_ticks':sum(r['Native_ticks']for r in rr),'Native_inputs_unique':len(allids[life,arm,version]),'Native_status_counts':dict(statuses),'candidate_floor_only_if_all12_closed':len(rr)>=12 and sum(r['joint_useful']for r in rr[:12])>=8 and sum(r['joint_useful']for r in rr[6:12])>=4,'not_an_adoption_decision':True})
    pairs=[]
    for left,right in [('native_real','always_real'),('native_real','never'),('always_real','always_desacoplado'),('native_real','native_desacoplado')]:
        for i in range(12):
            a=[r for r in complete if r['arm']==left and r['ordinal']==i];b=[r for r in complete if r['arm']==right and r['ordinal']==i]
            if len(a)!=1 or len(b)!=1:continue
            a,b=a[0],b[0];pairs.append({'left':left,'right':right,'ordinal':i,'same_q1_q2':(a['q1'],a['q2'])==(b['q1'],b['q2']),'same_age':(a['before_tick'],a['after_tick'])==(b['before_tick'],b['after_tick']),'same_request_count':a['Native_inputs']['unique_requested']==b['Native_inputs']['unique_requested'],'same_extra_release':a['first']['extra_released']==b['first']['extra_released'],'same_submitted_bit':a['first']['bit']==b['first']['bit'],'same_second_Native_choice':a['second']['Native_choice']==b['second']['Native_choice'],'same_joint_outcome':a['joint_useful']==b['joint_useful'],'left_useful':a['joint_useful'],'right_useful':b['joint_useful'],'left_questions':a['first']['question_applied'],'right_questions':b['first']['question_applied']})
    return {'schema':'DEE.PI09.consultation.recalculated_controlled_flow.R01','integrity_passed':True,'Native_executed':False,'DEE_imported':False,'fixture_MOCK_ONLY_NOT_NATIVE':index.get('fixture_MOCK_ONLY_NOT_NATIVE',False),'verified_members':len(verified),'primary_files':len(index['primaries']),'completed_opportunities':len(complete),'failed_or_preserved_attempts':failed,'auxiliary_rows':aux,'groups':groups,'rows':complete,'paired_observations':pairs,'scope':'Pure documentary RAW/receipt/product reconstruction. Distinct material branches provide actual outcomes, no offline counterfactual utility. One shared bank; first-query credit is not isolated. No permission to adopt or claim general agency.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--raiz',required=True);ap.add_argument('--indice',default='INDICE_PI09_CONSULTA_R01.json');ap.add_argument('--salida',required=True);args=ap.parse_args();out=Path(args.salida).absolute();require(not out.exists(),'New separate output only');value=calculate(args.raiz,args.indice)
    with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'integrity_passed':True,'Native_executed':False,'groups':value['groups'],'sha256':sha(out.read_bytes())},ensure_ascii=False))
