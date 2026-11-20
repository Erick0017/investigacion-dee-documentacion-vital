"""Portable E3 documentary recalculation. No DEE/Native imports or replay.

python RECALCULAR_E3.py --evidence EVIDENCIA_E3_PORTABLE --out NUEVA_SALIDA
Only relative files from the exported manifest are opened; historical source
paths remain data. Analytical references never act through the Native bridge.
"""
from pathlib import Path,PurePosixPath
from collections import Counter,defaultdict
import argparse,base64,csv,gzip,hashlib,json,zlib

PREFIX='PI03.TC.R01'
Q=(19,54,5)
def require(ok,message):
    if not ok:raise ValueError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
def member(root,name):
    require(type(name)is str and name and ':'not in name and'\\'not in name,'Relative exported member only')
    require(not any(p in('','.','..')for p in name.split('/')),'Unsafe exported member components')
    rel=PurePosixPath(name);require(not rel.is_absolute(),'Absolute paths are provenance only')
    p=root
    for part in rel.parts:
        p=p/part;require(p.exists()and not p.is_symlink()and not bool(getattr(p.lstat(),'st_file_attributes',0)&0x400),'Missing/reparse member')
    require(p.resolve().is_relative_to(root.resolve())and p.is_file(),'Member outside evidence')
    return p
def raw(root,name):return member(root,name).read_bytes()
def data(root,name):
    b=raw(root,name);return gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b
def load(root,name):return json.loads(data(root,name))
def unpack(packed):
    require(type(packed)is str and packed.startswith('E3Z1:')and len(packed)<=6144,'Bounded E3Z1 plan required')
    try:encoded=base64.b64decode(packed[5:],altchars=b'-_',validate=True);d=zlib.decompressobj();b=d.decompress(encoded,32769)
    except(ValueError,zlib.error)as e:raise ValueError('Invalid encoded control plan')from e
    require(len(b)<=32768 and d.eof and not d.unconsumed_tail and not d.unused_data,'Expanded/trailing control plan')
    v=json.loads(b);require(set(v)=={'plan','sha256'}and sha(canonical(v['plan']))==v['sha256'],'Plan envelope hash differs')
    return v
def decode(o):
    r=int(o['raw']);clock=int(o['clock']);require(0<=r<2**64 and 0<=clock<2**64,'Exact uint64 observation required')
    nib=lambda k:((r>>k)&15)-16 if((r>>k)&15)>=8 else((r>>k)&15)
    actual={'state':r&0xffffffff,'s_reg':(r>>32)&65535,'semantic':(r>>60)&15,'direction':[nib(48),nib(52),nib(56)]}
    require(all(actual[k]==o[k]for k in actual),'Observation fields differ from RAW')
    return actual
def fixed_choice(reader):
    found=[];seen=set()
    for o in reader['observations']:
        v=decode(o);site=tuple(o['site']);seen.add(site)
        for sign in(-1,0,1):
            target=((Q[0]+2*sign)%67,(Q[1]+2)%67,Q[2])
            if site==target and v['state']>0 and v['semantic']==1 and v['direction']==[sign,1,0]:found.append(sign)
    require(seen=={((Q[0]+2*s)%67,(Q[1]+2)%67,Q[2])for s in(-1,0,1)},'Exactly original three q+6 sites required')
    choice=found[0]if len(found)==1 else None
    require(choice==reader['choice'],'Fixed reader/recorded choice differ')
    return choice
def outer_value(outer):
    require(outer['status']=='completed','Incomplete primary must not become a completed episode')
    value=json.loads(outer['result'])if type(outer['result'])is str else outer['result']
    require(type(value)is dict and len(value['result']['rows'])==1,'Exactly one material row required')
    return value,value['result']['rows'][0]
def specs(protocol):
    env=protocol['environment'];initial=env['initial_inherited_offers']
    out=[{'connection':initial['connection'],'delay_laps':initial['delay_laps']}for _ in range(initial['count'])]
    for supply in env['explicit_supplies']:
        require(supply['after_E3']==len(out),'Supply does not start at fixed external boundary')
        out.extend({'connection':supply['conexion'],'delay_laps':supply['demora_periodos']}for _ in range(supply['cantidad']))
    require(len(out)==protocol['opportunities_per_arm']==18,'Frozen eighteen opportunities required')
    return out
def check_row(row,ordinal,spec,expected_before):
    require(row['before_tick']==expected_before and row['opportunity']==24+ordinal,'Cumulative Native genealogy/counter gap')
    require(row['after_tick']-row['before_tick']==row['new_native_ticks']<=1500,'Unexpected finite horizon')
    e3=row['PI04_E3'];c=row['calendar'];n=e3['calendar']
    require(e3['ordinal']==ordinal and row['spec']['delay_laps']==spec['delay_laps']==c['delay_laps'],'Ordinal/delay mismatch')
    require(c['delay_ticks']==67*c['delay_laps']and c['seed_tick']==c['query_read_tick']+1,'Delay/efference boundary changed')
    require(c['query_read_tick']==c['query_tick']+6 and row['reader']['tick']==c['query_read_tick'],'Original q+6 timing changed')
    require(c['collision_tick']-c['seed_tick']==67*c['delay_laps']and c['contact_tick']==c['collision_tick']+1,'Native hub/contact timing changed')
    require(c['outcome_injection_tick']==c['contact_tick']-2 and row['actual_effect']['consequence_tick']==c['outcome_injection_tick']-1,'Actual consequence/return timing changed')
    require(row['after_tick']==c['contact_tick']+2,'Original settled boundary changed')
    phase=[]
    for b in row['bank_before']:
        decode(b);phase.append((int(b['clock'])+c['contact_tick']-row['before_tick'])%782)
    for b in row['bank_after']:decode(b)
    require(phase==[391,391]and n['reference_contact_phase']==391,'Bank contact phase not matched')
    require(all(n[k]==c[k]for k in('query_tick','query_read_tick','outcome_injection_tick','contact_tick','delay_laps')),'E3/physical calendar mismatch')
    choice=fixed_choice(row['reader']);motor=-1 if choice==0 else choice
    require(choice is not None and motor in(-1,1),'Full18formed-response contrast cannot hide a NULL')
    require(row['emitted_motor']==row['applied_motor']==motor,'Native action replaced by external choice')
    useful=motor==spec['connection'];effect=row['actual_effect'];failed=effect['failed']
    require(type(failed)is bool and useful==row['useful_product']==(not failed),'Actual fixed device law/result differ')
    require(e3['actual_failed']==failed and e3['returned_failed']==row['returned_failed'],'Actual consequence conflated with signal')
    requests=row['requests'];require(len(requests)==5,'Five required material task inputs per formed response')
    require(all(r['payload']==0 and r['receipt']['status']=='applied'and r['id']==r['receipt']['id']and r['requested_tick']==r['receipt']['requested_tick']==r['receipt']['effective_tick']for r in requests),'Admission, zero-load, receipt identity or requested/effective boundary differs')
    query=[r for r in requests if r['channel']in(PREFIX+'.query',PREFIX+'.support.plus',PREFIX+'.support.minus')]
    copy=[r for r in requests if r['channel']in(PREFIX+'.copy.plus',PREFIX+'.copy.minus')]
    outcome=[r for r in requests if r['channel'].startswith(PREFIX+'.outcome.')]
    require(len(query)==3 and len(copy)==len(outcome)==1,'Fixed interface composition differs')
    require({r['channel']for r in query}=={PREFIX+'.query',PREFIX+'.support.plus',PREFIX+'.support.minus'}and all(r['requested_tick']==c['query_tick']for r in query),'Query/support sites/dose/time differ')
    require(copy[0]['actual_motor_choice']==motor and copy[0]['requested_tick']==c['seed_tick'],'Efference is not the actual current motor')
    require(copy[0]['channel']==PREFIX+('.copy.minus'if motor==-1 else'.copy.plus'),'Fixed inverse motor codec label differs')
    returned=row['returned_failed'];require(type(returned)is bool,'Return bool must not coerce NULL/zero')
    require(outcome[0]['channel']==PREFIX+('.outcome.failure'if returned else'.outcome.nonfailure')and outcome[0]['requested_tick']==c['outcome_injection_tick'],'Generic signal type/timing differs')
    require(outcome[0]['actual_environment_failed']==returned,'Legacy request field must equal admitted bit, not an invented effect')
    require(row['reconciliation']['finished']is True and row['reconciliation']['status']=='applied','Generic feedback receipt not finished')
    return {'ordinal':ordinal,'task_opportunity':24+ordinal,'before_tick':row['before_tick'],'after_tick':row['after_tick'],'reader_choice':choice,'material_zero':choice==0,'motor':motor,'connected_motor_evaluator_only':spec['connection'],'actual_failed':failed,'returned_failed':returned,'useful':useful,'delay_laps':c['delay_laps'],'reference_contact_phase':391,'calendar':n,'actual_product_bytes':effect['actual_product_bytes'],'actual_product_sha256':effect['actual_product_sha256'],'bank_before':[b['s_reg']for b in row['bank_before']],'bank_after':[b['s_reg']for b in row['bank_after']],'requests':requests}
def verify_source(source):
    first,second=source['first'],source['second'];intermediate=first['numeric_result'];final=second['numeric_result']
    require(type(intermediate)is int and type(final)is int and 0<=final<=65535,'Actual preserved integer source required')
    require(second['literal_operator_request']['izquierda']==intermediate,'Actual first-to-second source link changed')
    for t in(first,second):
        reader=t['numeric_reader'];o=reader['observation'];decode(o)
        require(reader['fixed_site_direction_valid']is True and t['numeric_result']==reader['numeric_result']==o['s_reg']-reader['representation_bias'],'Actual numeric RAW/reader/result differ')
    payload=final.to_bytes(2,'little')+bytes(62)
    require(source['actual_final_result']==final and source['payload_bytes']==64 and source['payload_sha256']==sha(payload),'Preserved source codec differs')
    return payload,{'actual_first':intermediate,'actual_final':final,'payload_sha256':sha(payload),'scope':'Prepared Native numeric apparatus; actual recorded outputs, no learned arithmetic algorithm claim.'}
def analytical_references(spec):
    result=[]
    for name in('fixed_minus','fixed_plus','alternating_plus_first','WSLS_minus_first','WSLS_plus_first'):
        action=-1 if name in('fixed_minus','WSLS_minus_first')else 1;rows=[]
        for i,s in enumerate(spec):
            if name=='alternating_plus_first':action=1 if i%2==0 else-1
            success=action==s['connection'];rows.append({'ordinal':i,'action':action,'useful_if_payload_available':success})
            if name.startswith('WSLS')and not success:action=-action
        result.append({'name':name,'products_if_same_payload_available':sum(r['useful_if_payload_available']for r in rows),'rows':rows,'mode':'Analytical reference under the frozen law; never controls DEE or writes the device','information':'Fixed/alternating policy uses its own ordinal only; WSLS uses only its own previous action and own previous consequence.'})
    return result
def analyze(root):
    manifest=load(root,'MANIFEST.json')
    for item in manifest['files']:
        b=raw(root,item['file']);require(len(b)==item['bytes']and sha(b)==item['sha256'],'Exported member hash differs '+item['file'])
    protocol=load(root,'protocol.json');spec=specs(protocol);all_cases={};plans={}
    for arm in('real','desacoplado'):
        case=load(root,arm+'/summary.json.gz')
        require(case['arm']==arm and case['owner_closed']is True and case['included']==case['completed']==18,'Closed18/18 history required, not an interrupted attempt')
        init,initial=outer_value(load(root,arm+'/admit.json.gz'));require(init['before_tick']==init['after_tick']==775355 and initial['new_native_ticks']==0,'Admission changed physical age')
        result=[];ids={};before=775355;logical=load(root,arm+'/files.json')['files'];by_index={v['index']:v for v in logical}
        verified_payloads={};source_proofs=[]
        for source_item in load(root,arm+'/sources.json')['sources']:
            source_bytes=raw(root,source_item['source_blob'])
            require(sha(source_bytes)==source_item['source_sha256'],'Actual source archive hash differs')
            source=json.loads(source_bytes);require(canonical(source)==source_bytes,'Actual source is not the preserved canonical archive')
            payload,proof=verify_source(source)
            require(payload==raw(root,source_item['source_payload_blob']),'Actual source and exported decoded bytes differ')
            verified_payloads[source_item['source_payload_blob']]=payload;source_proofs.append(proof)
        for i in range(18):
            outer=load(root,arm+'/primaries/%02d.json.gz'%i);value,row=outer_value(outer)
            require(outer['id']==case['rows'][i]['id']and value['before_tick']==row['before_tick']and value['after_tick']==row['after_tick'],'Primary/runner outer boundary differs')
            entry=check_row(row,i,spec[i],before);before=entry['after_tick']
            require(case['rows'][i]['choice']==entry['reader_choice']and case['rows'][i]['useful']==entry['useful'],'Runner summary/primary differ')
            for request in entry['requests']:
                k=str(request['id']);require(k not in ids,'Repeated Native input ID is not an additional event');ids[k]=request
            file=by_index[24+i];compressed=raw(root,file['encoded_blob']);payload=zlib.decompress(compressed)
            require(len(compressed)==file['encoded_bytes']and sha(compressed)==file['encoded_sha256']and len(payload)==64,'Actual encoded capsule differs')
            require(file['source_payload_blob']in verified_payloads and payload==verified_payloads[file['source_payload_blob']],'Real resource differs from verified actual Native source bytes')
            if entry['useful']:
                product=raw(root,file['product_blob']);require(product==payload and len(product)==entry['actual_product_bytes']==64 and sha(product)==entry['actual_product_sha256'],'Actual useful file lost or replaced by counter')
            else:require(file['product_blob']is None and entry['actual_product_bytes']==0 and entry['actual_product_sha256']is None,'Rejected encoded capsule is not a useful product')
            entry['requests_count']=len(entry.pop('requests'));result.append(entry)
        require(len(ids)==90 and all(x['receipt']['status']=='applied'for x in ids.values()),'Exactly90unique applied Native task inputs required')
        require(case['new_native_ticks']==before-775355 and case['products']==sum(r['useful']for r in result),'Summary ticks/product denominator differs')
        final,final_state=outer_value(load(root,arm+'/final.json.gz'));m=final_state['progress']
        require(m['ordinal']==18 and m['start_opportunity']==24 and not m['pending']and not m['uncertain'],'Final Native E3 progress unresolved')
        require(m['rows']==[{'ordinal':r['ordinal'],'calendar':r['calendar'],'failed':r['actual_failed']}for r in result],'Snapshot-bound actual E3 history differs')
        require(final['before_tick']==final['after_tick']==before,'Final state lookup changed age')
        for supply in protocol['environment']['explicit_supplies']:
            val,sr=outer_value(load(root,arm+'/supplies/%02d.json.gz'%supply['after_E3']))
            require(val['before_tick']==val['after_tick']and sr['new_native_ticks']==0 and sr['old_opportunity_unchanged']==24+supply['after_E3']and sr['historical_prefix_preserved'],'Supply resets history or advances Native')
            sup=sr['supply'];require(sup['quantity']==4 and sup['connection']==supply['conexion']and sup['delay_laps']==supply['demora_periodos'],'External supply differs from fixed schedule')
        all_cases[arm]={'life':case['life'],'offered':18,'completed':18,'formed':18,'NULL':0,'material_zero':sum(r['material_zero']for r in result),'products':sum(r['useful']for r in result),'actual_product_bytes':sum(r['actual_product_bytes']for r in result),'unique_inputs':90,'applied':90,'rejected':0,'pending':0,'first_tick':775355,'last_tick':before,'rows':result,'native_id_bounds':[min(map(int,ids)),max(map(int,ids))],'actual_source_proofs':source_proofs}
        plans[arm]=final_state
    real=all_cases['real'];control=all_cases['desacoplado'];plan=unpack(plans['real']['replay_plan_encoded']);body=plan['plan']
    require(body['source_records']==[{'ordinal':r['ordinal'],'calendar':r['calendar'],'failed':r['actual_failed']}for r in real['rows']],'Plan not derived from complete actual real history')
    require(sha(canonical(body['source_records']))==body['source_records_sha256'],'Plan source hash differs')
    require(plans['desacoplado']['progress']['plan']==plan,'Control Native progress stores another plan')
    admit=load(root,'desacoplado/admit.json.gz');literal=json.loads(admit['payload'])['situaciones'][0]
    require(unpack(literal['plan'])==plan,'Control request used another plan')
    require(body['frozen_rule']=='rotate_plus_one_within_delay_phase','Posthoc permutation rule changed')
    groups=defaultdict(list)
    for r in real['rows']:groups[(r['delay_laps'],r['reference_contact_phase'])].append(r['ordinal'])
    strata=[];changes=0;mismatches=0
    for key,indices in sorted(groups.items()):
        for pos,i in enumerate(indices):
            j=indices[(pos+1)%len(indices)];slot=body['slots'][i];r=real['rows'][i];c=control['rows'][i]
            require(slot['source_ordinal']==j and slot['returned_failed']==real['rows'][j]['actual_failed'],'Not the fixed circular rotation')
            require(r['calendar']==c['calendar']==slot['calendar'],'Paired calendar/phase differs')
            require(r['returned_failed']==r['actual_failed']and c['returned_failed']==slot['returned_failed'],'Real contingency/control replay mismatch')
            changes+=r['actual_failed']!=slot['returned_failed'];mismatches+=c['actual_failed']!=c['returned_failed']
        a=Counter(real['rows'][i]['returned_failed']for i in indices);b=Counter(control['rows'][i]['returned_failed']for i in indices)
        require(a==b,'Signal-type dose not equal within delay/phase stratum')
        strata.append({'delay_laps':key[0],'reference_contact_phase':key[1],'opportunities':len(indices),'failure':a[True],'nonfailure':a[False]})
    require(changes==body['source_signal_changes'],'Plan changed-signal count differs')
    require(real['rows'][0]['bank_before']==control['rows'][0]['bank_before'],'Initial physical reference values differ')
    refs=analytical_references(spec)
    for r in refs:r['matches_real_actions']=sum(x['action']==n['motor']for x,n in zip(r['rows'],real['rows']))
    return {'schema':'DEE.PI04.E3.portable_recalculation.v1','mode':'RECORDED_DATA_RECALCULATION_NOT_NATIVE','new_native_ticks':0,'source_path_fields_opened':False,'manifest_sha256':sha(raw(root,'MANIFEST.json')),'cases':all_cases,
            'comparison':{'real_products':real['products'],'permuted_products':control['products'],'difference':real['products']-control['products'],'same90input_count_per_arm':True,'same_signal_type_dose_by_delay_phase':strata,'changed_source_signals':changes,'actual_control_effect_return_mismatches':mismatches,'false_failure_signals':sum(not r['actual_failed']and r['returned_failed']for r in control['rows']),'real_failures_not_signaled':sum(r['actual_failed']and not r['returned_failed']for r in control['rows']),'manipulation_effective':changes>0 and mismatches>0,'siblings_share_prefix_not_independent_replicates':True},
            'analytical_references':refs,'limits':['Fixed opportunities, sensor, motor-zero default, prepared anatomy and environment law remain external assistance.','An equal finite dose is not statistical independence; report actual mismatches rather than claim a perfect yoke.','Native controls and record recalculation are different modalities. Reference policies are mathematical comparisons only.','Full snapshots, interfaces, agenda, SQLite and resources remain local; this export is analysis evidence, not an executable backup.']}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--evidence',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    root=a.evidence.resolve(strict=True);require(not a.out.exists(),'Fresh output directory required')
    report=analyze(root);a.out.mkdir(parents=True)
    (a.out/'RECALCULO_E3.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows=[]
    for arm,case in report['cases'].items():
        for r in case['rows']:rows.append({'arm':arm,**{k:(json.dumps(v,ensure_ascii=False)if isinstance(v,(dict,list))else v)for k,v in r.items()}})
    with(a.out/'TRAYECTORIAS_E3.csv').open('x',encoding='utf-8',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps({'mode':report['mode'],'Native_ticks':0,'comparison':report['comparison'],'analytical_reference_products':{r['name']:r['products_if_same_payload_available']for r in report['analytical_references']}},ensure_ascii=False))
if __name__=='__main__':main()
