"""Portable, engine-free AA01 recalculation from primary records.

No participant imports this module. Reference86 is an auditor task reference
from the inherited EF01/PC01 contract, never a response supplied to a world.
Logical questions and material submissions keep separate denominators.
"""
from pathlib import Path,PurePosixPath
from collections import Counter
from array import array
import argparse,gzip,lzma,tarfile,json,hashlib,sys

def digest(b):return hashlib.sha256(b).hexdigest()
def unpack(raw):
    if isinstance(raw,float):raise ValueError('Lossy RAW float')
    v=int(raw)
    if not 0<=v<2**64:raise ValueError('RAW outside uint64')
    def s(k):
        b=(v>>k)&15
        return b-16 if b&8 else b
    return{'state':v&0xffffffff,'s_reg':(v>>32)&65535,'direction':[s(k)for k in(48,52,56)],'semantic':(v>>60)&15}
def valid(r,d):
    q=unpack(r['raw']);return r.get('active',True)and q['state']==1 and q['semantic']==1 and q['direction']==list(d)
def code(r):
    if valid(r,(1,1,-1)):return'menos'
    if valid(r,(1,1,1)):return'más'
    return None
def walk(v,loc='$'):
    if isinstance(v,dict):
        yield loc,v
        for k,x in v.items():
            if k not in('parent','commit','initial_record','final_record','reached_record','actual_reached_record','failed_complete_state','original_current_record','reference_primary','source_forms','scheduled_requests'):yield from walk(x,loc+'.'+k)
    elif isinstance(v,list):
        for k,x in enumerate(v):yield from walk(x,loc+'['+str(k)+']')
def records(root):
    archive=root/'EVIDENCIA_ESENCIAL/PRIMARIOS_Y_TESTIGOS.tar.xz'
    if archive.exists():
        with tarfile.open(archive,'r|xz')as tf:
            for m in tf:
                if m.isfile()and m.name.startswith('primarios/')and PurePosixPath(m.name).name in('PRIMARIOS.json','PRIMARIOS.json.gz'):
                    b=tf.extractfile(m).read();yield m.name,json.loads(gzip.decompress(b)if m.name.endswith('.gz')else b),digest(b)
    else:
        for p in sorted(root.glob('*/*/PRIMARIOS.json*')):
            b=p.read_bytes();yield p.relative_to(root).as_posix(),json.loads(gzip.decompress(b)if p.name.endswith('.gz')else b),digest(b)
def array_bytes(values):
    v=array('Q',values)
    if sys.byteorder!='little':v.byteswap()
    return v.tobytes()
def frame_check(q):
    n=q['N'];raw=[0]*(n**3);clocks=[int(q['clock_default'])]*(n**3)
    for i,v,c in q['rows']:raw[i]=int(v)
    for i,c in q['clock_exceptions']:clocks[i]=int(c)
    h={'RAW_sha256':digest(array_bytes(raw)),'clocks_sha256':digest(array_bytes(clocks)),'occupied':sum(bool(v&0xffffffff)for v in raw),'raw_nonzero':sum(bool(v)for v in raw),'state_zero_raw_nonzero':sum(bool(v)and not(v&0xffffffff)for v in raw)}
    return{'computed':h,'matches':{k:h[k]==q[k]for k in h},'row_clock_match':all(clocks[i]==int(c)for i,v,c in q['rows'])}
def evaluate(q):
    instrument=q.get('INSTRUMENTO',{});ente=q.get('ENTE',{});out=None
    if isinstance(ente,dict)and'previous_word_signal'in ente and'current_word_signal'in ente:
        words=[]
        for word,direction in(('menos',(1,1,-1)),('más',(-1,-1,1))):
            before=ente['previous_word_signal'][word];after=ente['current_word_signal'][word];dose=q['TRADUCCION']['SIGNAL_DETAILS'][word]['declared_word_probe_dose'];delta=unpack(after['raw'])['s_reg']-unpack(before['raw'])['s_reg']-dose
            if valid(before,direction)and valid(after,direction)and delta==7:words.append(word)
        value=q['ENTORNO']['actual_object_magnitude'];expected=['menos']if value<86 else['más']if value>86 else[]
        out={'kind':'CURRENT_MAGNITUDE_USE','tick':instrument['word_tick'],'actual_value':value,'auditor_reference':86,'words':words,'stored_words':q['TRADUCCION']['SPANISH_DECODED'],'expected_task_words':expected,'task_correct':words==expected,'asked':bool(instrument['query_requested'])}
    elif'actual_dose_each'in q and isinstance(q.get('rows'),list):
        words=[];dose=q['actual_dose_each']
        for row in q['rows']:
            for key,before in row['before'].items():
                after=row['after'][key];x=unpack(before['raw']);y=unpack(after['raw']);old='cerca'if valid(before,(1,1,1))else'lejos'if valid(before,(-1,1,1))else None;new='cerca'if valid(after,(1,1,1))else'lejos'if valid(after,(-1,1,1))else None
                if old and new and y['s_reg']-x['s_reg']==2*dose:words.append(new)
        words=sorted(set(words));expected=['cerca'if q['actual_parameter']>0 else'lejos'];out={'kind':'CURRENT_SPATIAL_DOSE_USE','tick':q['rows'][-1].get('tick',q['rows'][-1].get('after_tick')),'words':words,'stored_words':q['SPANISH_DECODED'],'actual_parameter':q['actual_parameter'],'actual_dose_each':dose,'expected_task_words':expected,'task_correct':words==expected,'asked':True}
    elif isinstance(ente,dict)and'output'in ente and'frame'in instrument and'functional_use_requested'in instrument:
        words=[]
        for key,row in ente['output'].items():
            axis=-1 if key.endswith('izq')else 1;z=-1 if key.startswith('no_toca')else 0;direction=[0 if instrument['functional_use_requested']else-axis,1,z]
            if valid(row,direction):words.append('no toca'if z<0 else'toca')
        words=sorted(set(words));frame=instrument['frame'];expected=['toca']if frame=='contactoA'else['no toca']if frame=='freeRepair5'else None;out={'kind':'CONTACT_FORM_OR_USE','tick':instrument['query_tick'],'frame':frame,'words':words,'stored_words':sorted(set(q['SPANISH_DECODED'])),'expected_task_words':expected,'task_correct':None if expected is None else words==expected,'asked':True}
    elif instrument.get('stage')=='access'and isinstance(ente,dict)and'forms'in ente:
        words=[];details=instrument.get('material_access_details',{})
        if details:
            for word,item in details.items():
                before=item['pre_memory'];query=item['pre_query'];after=ente['forms'][word];signature=(1,1,-1)if word=='menos'else(-1,-1,1);qdir=(0,0,signature[2]);delta=unpack(after['raw'])['s_reg']-unpack(before['raw'])['s_reg'];qr=unpack(query['raw'])
                if valid(before,signature)and valid(after,signature)and int(query['raw'])!=0 and qr['direction']==list(qdir)and qr['s_reg']>0 and delta==qr['s_reg']:words.append(word)
        else:
            for row in ente['forms'].values():
                if valid(row,(0,0,-1)):words.append('menos')
                elif valid(row,(0,0,1)):words.append('más')
        out={'kind':'NATIVE_SELECTED_ACCESS','tick':instrument['tick'],'words':sorted(set(words)),'stored_words':q['SPANISH_DECODED'],'asked':True,'no_semantic_promotion_from_code':True}
    elif isinstance(ente,dict)and'alternative'in ente and'old_reader_supplied'in instrument:
        words=sorted(set(w for row in ente['alternative'].values()if(w:=code(row))is not None));out={'kind':'COMMON_RECIPIENT_RECOVERY','tick':instrument['alternative_tick'],'words':words,'stored_words':q['SPANISH_DECODED'],'asked':True,'old_reader_supplied':instrument['old_reader_supplied'],'no_content_Z_bit_supplied':instrument['no_Z_content_supplied']}
    if out is not None:
        out['response_qualified']=bool(out['words']);out['abstention_or_no_qualified_response']=not out['words'];out['conflicting_codes']=len(out['words'])>1;out['stored_decoder_matches']=sorted(set(out['words']))==sorted(set(out['stored_words']))
    return out
def recompute(root,deep=False):
    report={'schema':'AA01.engine_free.recalculation.v1','cases':[],'field_checks':0,'frame_checks':0,'decoder_checks':0,'errors':[],'reference_scope':'Reference86 comes from the existing EF01/PC01 quantity contract, not a target supplied during these trials. Physical submissions and logical questions are never added together.','independence':'Forks, repeated queries, diagnostics and replays are not independent individuals.'};allcases={}
    for name,data,source_hash in records(root):
        parts=PurePosixPath(name).parts;batch,case=parts[-3:-1];key=batch+'/'+case;allcases[key]=data;pre=data.get('pre',{});post=data.get('post',{});row={'id':key,'life':data.get('life'),'source_file':name,'source_sha256':source_hash,'initial_tick':pre.get('tick',data.get('epoch')),'final_tick':post.get('tick',data.get('final_record',{}).get('physical',{}).get('tick')),'instrument_failure':data.get('instrument_failure',data.get('failure')),'logical_evaluations':[],'material_submissions':{},'strategy_samples':[],'local_accesses':[]};request_ids=set();receipt_map={};evaluation_map={};frames_seen=set()
        for loc,q in walk(data):
            if{'raw','state','s_reg','semantic','direction'}<=q.keys():
                fields=unpack(q['raw']);report['field_checks']+=1
                if isinstance(q.get('clock'),float)or any(fields[k]!=q[k]for k in fields):report['errors'].append({'case':key,'kind':'RAW_FIELDS_OR_FLOAT','locator':loc})
            if type(q.get('id'))is int and type(q.get('payload'))is int and('channel'in q or'port'in q):request_ids.add(q['id'])
            if type(q.get('id'))is int and'status'in q and'channels'in q:
                prior=receipt_map.get(q['id']);status=q['status']
                if prior is None or prior['status']=='scheduled'and status!='scheduled':receipt_map[q['id']]=q
                elif prior['status']!=status and status!='scheduled':report['errors'].append({'case':key,'kind':'CONFLICTING_FINAL_RECEIPT','id':q['id']})
            if deep and{'rows','clock_default','clock_exceptions','N','RAW_sha256','clocks_sha256'}<=q.keys()and q['clock_exceptions']is not None:
                signature=(q.get('tick'),q['RAW_sha256'],q['clocks_sha256'])
                if signature not in frames_seen:
                    frames_seen.add(signature);v=frame_check(q);report['frame_checks']+=1
                    if not all(v['matches'].values())or not v['row_clock_match']:report['errors'].append({'case':key,'kind':'SPARSE_FULL_FIELD_RECONSTRUCTION','locator':loc,'detail':v})
            ev=evaluate(q)
            if ev is not None:
                signature=(ev['kind'],ev.get('tick'),tuple(ev['words']),ev.get('actual_value'),ev.get('actual_parameter'),ev.get('frame'))
                if signature in evaluation_map:evaluation_map[signature]['equivalent_locators'].append(loc)
                else:ev.update(locator=loc,equivalent_locators=[]);evaluation_map[signature]=ev;report['decoder_checks']+=1
                if not ev['stored_decoder_matches']:report['errors'].append({'case':key,'kind':'FIXED_DECODER_MISMATCH','locator':loc,'detail':ev})
        row['logical_evaluations']=list(evaluation_map.values());statuses=Counter(receipt_map[i]['status']if i in receipt_map else'final_receipt_not_in_primary'for i in request_ids);row['material_submissions']={'explicit_submission_IDs_in_primary':len(request_ids),'statuses':dict(statuses),'applied':statuses['applied'],'rejected_at_application':sum(v for k,v in statuses.items()if k.startswith('rejected')),'pending':statuses['scheduled'],'not_inferred_from_logical_answers':True}
        for sample in data.get('samples',[]):
            if'policy'in sample and isinstance(sample['policy'],dict)and'raw'in sample['policy']and sample.get('relative_tick')in(23,90):row['strategy_samples'].append({'tick':sample['tick'],'relative_tick':sample['relative_tick'],**unpack(sample['policy']['raw'])})
            if sample.get('relative_tick')==161 and isinstance(sample.get('memories'),dict):
                for bank,r in sample['memories'].items():
                    z=unpack(r['raw']);row['local_accesses'].append({'bank':bank,'raw':r['raw'],**z,'qualified_XYZ':valid(r,(1,int(bank),z['direction'][2]))and abs(z['direction'][2])==1})
        if'decoded'in data:row['loss_assay_code']=data['decoded'];row['explicit_relearned_code']=data.get('relearned_decoded');row['full_causal_state6']=data.get('native_after6_excluding_only_documental_life')
        if'old_decoded'in data:row['recipient_old']=data['old_decoded'];row['recipient_recovered']=data['recovered_decoded'];row['recipient_later']=data['later_decoded']
        report['cases'].append(row)
    report['totals']={'case_primary_files':len(report['cases']),'logical_evaluations':sum(len(q['logical_evaluations'])for q in report['cases']),'unique_material_submission_IDs_within_each_case_not_independent_worlds':sum(q['material_submissions']['explicit_submission_IDs_in_primary']for q in report['cases']),'decoder_mismatches':sum(e['kind']=='FIXED_DECODER_MISMATCH'for e in report['errors'])}
    loss={k:v for k,v in allcases.items()if k.startswith('PERDIDA_Y_REAPRENDIZAJE_13/')and 'no_wall'not in k and'sham'not in k and'no_history'not in k};report['natural_loss_13']={'cases':{k:v.get('native_after6_excluding_only_documental_life')for k,v in loss.items()},'number_distinct_exact_causal_state6_hashes':len({v['native_after6_excluding_only_documental_life']['native_sha256']for v in loss.values()})if loss else None,'interpretation':'Only documentary life metadata erased on non-evolved serialization copies. Identical whole causal state and same future cannot recover distinct earlier content in this domain.'}
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--deep',action='store_true');a=p.parse_args();r=recompute(a.root,a.deep);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'totals':r['totals'],'field_checks':r['field_checks'],'frame_checks':r['frame_checks'],'errors':len(r['errors'])}));return int(bool(r['errors']))
if __name__=='__main__':raise SystemExit(main())
