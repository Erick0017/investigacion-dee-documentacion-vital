"""Portable engine-free recalculation for the thin PC01 analysis package.

Reads primary bytes, recomputes physical fields and fixed instrument decoders.
Targets are used ONLY after decoding to score the declared audit task.
Never imports the engine, changes a world, teaches or chooses a native reply.
"""
from pathlib import Path,PurePosixPath
from collections import Counter
import argparse,array,gzip,hashlib,json,sys,tarfile,struct

def sha(b):return hashlib.sha256(b).hexdigest()
def read(path):
    b=gzip.decompress(path.read_bytes())if path.name.endswith('.gz')else path.read_bytes()
    return json.loads(b),sha(b)
def unpack(raw):
    v=int(raw)
    if not 0<=v<2**64:raise ValueError('RAW outside uint64')
    def signed(k):
        n=(v>>k)&15
        return n-16 if n&8 else n
    return{'state':v&0xffffffff,'s_reg':(v>>32)&65535,'direction':[signed(k)for k in(48,52,56)],'semantic':(v>>60)&15}
def native_word(record):
    r=unpack(record['raw'])
    if r['state']==1 and r['semantic']==1 and r['direction'][1:]==[1,1]and abs(r['direction'][0])==1:return'cerca'if r['direction'][0]==1 else'lejos'
    return None
def valid(record,direction):
    r=unpack(record['raw']);return r['state']==1 and r['semantic']==1 and r['direction']==list(direction)
def walk(obj,loc='$'):
    if isinstance(obj,dict):
        yield loc,obj
        for k,v in obj.items():
            if k not in('parent','commit'):yield from walk(v,loc+'.'+k)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):yield from walk(v,loc+'['+str(i)+']')
def primary_paths(root):
    packed=root/'EVIDENCIA_ESENCIAL/primarios'
    if packed.exists():return sorted(packed.glob('*/*/PRIMARIOS.json.gz'))+sorted(packed.glob('*/*/PRIMARIOS.json'))
    if(root/'primarios').exists():return sorted((root/'primarios').glob('*/*/PRIMARIOS.json'))
    return sorted(root.glob('*/*/PRIMARIOS.json'))
def primary_records(root):
    archives=[root/'EVIDENCIA_ESENCIAL/REGISTROS_MEDIDOS.tar.xz',root/'EVIDENCIA_ESENCIAL/REGISTROS_COMPLETOS.tar.xz']
    archive=next((p for p in archives if p.exists()),None)
    if archive:
        with tarfile.open(archive,'r|xz')as tf:
            found=False
            for member in tf:
                if member.name.startswith('primarios/')and member.name.endswith('/PRIMARIOS.json'):
                    if not member.isfile():raise ValueError('Primary is not a regular data file')
                    b=tf.extractfile(member).read();yield PurePosixPath(member.name),json.loads(b),sha(b);found=True
                elif found:break
    else:
        for path in primary_paths(root):
            v,h=read(path);yield path,v,h
def header_fields(hex_value):
    b=bytes.fromhex(hex_value)
    if b[:8]!=b'DEETSNP1'or struct.unpack_from('<I',b,8)[0]!=2:raise ValueError('Unexpected native header')
    n=struct.unpack_from('<I',b,12)[0];tick=struct.unpack_from('<Q',b,16)[0];paused=bool(b[24]);next_id=struct.unpack_from('<Q',b,25)[0];sequence=struct.unpack_from('<Q',b,33)[0];length=struct.unpack_from('<I',b,41)[0];phase=b[45:45+length].decode('utf8');count=struct.unpack_from('<Q',b,45+length)[0]
    if count!=n**3 or len(b)!=53+length:raise ValueError('Native header length/dimension mismatch')
    return{'N':n,'tick':tick,'paused':paused,'next_event_id':next_id,'next_sequence':sequence,'protocol_phase':phase}
def recompute(root,deep=False):
    result={'schema':'PC01.engine_free.recalculation.v2','cases':{},'record_field_checks':0,'uint64_float_errors':[],'decoder_checks':0,'decoder_mismatches':[],'factorial07':{},'not_independent_n':'Repeated observations, exact forks and technical replays are not independent learners.'};families={};case_receipts={}
    for path,v,bytehash in primary_records(root):
        casekey='/'.join(path.parts[-3:-1]);batch=path.parts[-3];case=path.parts[-2];families[casekey]=v
        parent=v.get('parent',{});parent=parent if isinstance(parent,dict)else{}
        pre=v.get('pre',{});pre=pre if isinstance(pre,dict)else{}
        post=v.get('post',{});post=post if isinstance(post,dict)else{}
        row={'source_uncompressed_sha256':bytehash,'life':v.get('life'),'tick_initial':pre.get('tick',parent.get('physical',{}).get('tick')),'tick_final':post.get('tick'),'dose_current':[],'legacy_current':[],'magnitude_current':[],'contact_free_queries':[],'logged_new_requests':{},'field_errors':[]};request_ids=set();receipt_map={}
        for loc,q in walk(v):
            if {'raw','state','s_reg','direction','semantic'}<=q.keys():
                if isinstance(q['raw'],float)or isinstance(q.get('clock'),float):result['uint64_float_errors'].append([casekey,loc])
                physical=unpack(q['raw']);result['record_field_checks']+=1
                if any(physical[k]!=q[k]for k in physical):row['field_errors'].append({'locator':loc,'record':q,'computed':physical})
            if type(q.get('id'))is int and type(q.get('payload'))is int and('port'in q or'channel'in q):request_ids.add(q['id'])
            if type(q.get('id'))is int and'status'in q and'channels'in q:receipt_map[q['id']]=q
            if 'actual_dose_each'in q and isinstance(q.get('rows'),list):
                dose=q['actual_dose_each'];words=[]
                for rr in q['rows']:
                    phasewords=[]
                    for bank,before in rr['before'].items():
                        after=rr['after'][bank];old=native_word(before);new=native_word(after);delta=unpack(after['raw'])['s_reg']-unpack(before['raw'])['s_reg']
                        if old and new and delta==2*dose:phasewords.append(new)
                    words.extend(phasewords)
                words=sorted(set(words));result['decoder_checks']+=1
                if words!=q['SPANISH_DECODED']:result['decoder_mismatches'].append({'case':casekey,'locator':loc,'computed':words,'stored':q['SPANISH_DECODED']})
                parameter=q['actual_parameter'];expected=['cerca'if parameter>0 else'lejos'];row['dose_current'].append({'locator':loc,'parameter':parameter,'dose':dose,'words':words,'standard_task_correct':words==expected,'physical_presentations':len(q['rows'])})
            if isinstance(q.get('ENTE'),list)and q.get('ENTORNO',{}).get('teacher_token_supplied')is False and'actual_parameter'in q.get('ENTORNO',{})and q['ENTE']and'before'in q['ENTE'][0]:
                words=[];probe=q['INSTRUMENTO']['word_probe_dose_per_bank'];decoder=q['INSTRUMENTO']['decoder_revision'];accepted=(6,10)if decoder=='strict'else(6,7,8,10,11,12)
                for rr in q['ENTE']:
                    for bank,before in rr['before'].items():
                        after=rr['after'][bank];old=native_word(before);new=native_word(after);delta=unpack(after['raw'])['s_reg']-unpack(before['raw'])['s_reg']-probe
                        if old and new and delta in accepted:words.append(new)
                stored=sorted(set(r['text']for r in q['SPANISH_DECODED']));words=sorted(set(words));result['decoder_checks']+=1
                if words!=stored:result['decoder_mismatches'].append({'case':casekey,'locator':loc,'computed':words,'stored':stored})
                row['legacy_current'].append({'locator':loc,'words':words,'parameter':q['ENTORNO']['actual_parameter'],'physical_presentations':len(q['ENTE'])})
            if isinstance(q.get('ENTE'),dict)and'previous_word_signal'in q['ENTE']and'current_word_signal'in q['ENTE']:
                old=q['ENTE']['previous_word_signal'];new=q['ENTE']['current_word_signal'];words=[]
                for name,direction in(('menos',(1,1,-1)),('más',(-1,-1,1))):
                    declared=q['TRADUCCION']['SIGNAL_DETAILS'][name]['declared_word_probe_dose'];delta=unpack(new[name]['raw'])['s_reg']-unpack(old[name]['raw'])['s_reg']-declared
                    if valid(old[name],direction)and valid(new[name],direction)and delta==7:words.append(name)
                stored=q['TRADUCCION']['SPANISH_DECODED'];result['decoder_checks']+=1
                if words!=stored:result['decoder_mismatches'].append({'case':casekey,'locator':loc,'computed':words,'stored':stored})
                row['magnitude_current'].append({'locator':loc,'actual_magnitude':q['ENTORNO']['actual_object_magnitude'],'words':words,'native_comparison':unpack(q['ENTE']['native_comparison']['raw'])})
            if isinstance(q.get('ENTE'),dict)and isinstance(q['ENTE'].get('read'),dict)and'raw'in q['ENTE']['read']and'SPANISH_DECODED'in q and'NATIVE_ACTION_OBSERVED'in q:
                native=native_word(q['ENTE']['read']);decoded=[]if native is None else[native];result['decoder_checks']+=1
                if decoded!=q['SPANISH_DECODED']:result['decoder_mismatches'].append({'case':casekey,'locator':loc+'.ENTE.read','computed':decoded,'stored':q['SPANISH_DECODED']})
                if q['ENTE'].get('action')is not None:
                    observed=valid(q['ENTE']['action'],(0,0,1));result['decoder_checks']+=1
                    if observed!=q['NATIVE_ACTION_OBSERVED']:result['decoder_mismatches'].append({'case':casekey,'locator':loc+'.ENTE.action','computed':observed,'stored':q['NATIVE_ACTION_OBSERVED']})
            output=q.get('ENTE',{}).get('output')if isinstance(q.get('ENTE'),dict)else None
            if isinstance(output,dict)and output and set(output)<={'toca_izq','toca_der','no_toca_izq','no_toca_der'}and'SPANISH_DECODED'in q:
                decoded=[];consumptive=q['INSTRUMENTO']['functional_use_requested']
                for name,value in output.items():
                    axis=-1 if name.endswith('izq')else 1;z=-1 if name.startswith('no_toca')else 0
                    if valid(value,(0 if consumptive else-axis,1,z)):decoded.append('no toca'if z==-1 else'toca')
                decoded=list(dict.fromkeys(decoded));result['decoder_checks']+=1
                if decoded!=q['SPANISH_DECODED']:result['decoder_mismatches'].append({'case':casekey,'locator':loc+'.ENTE.output','computed':decoded,'stored':q['SPANISH_DECODED']})
                row['contact_free_queries'].append({'locator':loc,'frame':q['INSTRUMENTO']['frame'],'tick':q['INSTRUMENTO']['query_tick'],'words':decoded,'consumptive':consumptive})
        for q in v.get('receipts',[]):
            if type(q.get('id'))is int:receipt_map[q['id']]=q
        case_receipts[casekey]=receipt_map
        if isinstance(v.get('reader'),dict)and'raw'in v['reader']and'SPANISH_DECODED'in v:
            word=native_word(v['reader']);decoded=[]if word is None else[word];result['decoder_checks']+=1
            if decoded!=v['SPANISH_DECODED']:result['decoder_mismatches'].append({'case':casekey,'locator':'$.reader','computed':decoded,'stored':v['SPANISH_DECODED']})
            row['transformed_reader']={'words':decoded,'native_fields':unpack(v['reader']['raw'])}
            if 'NATIVE_ACTION_OBSERVED'in v:
                correct=valid(v['action'],(0,0,1));result['decoder_checks']+=1
                if correct!=v['NATIVE_ACTION_OBSERVED']:result['decoder_mismatches'].append({'case':casekey,'locator':'$.action','computed':correct,'stored':v['NATIVE_ACTION_OBSERVED']})
                row['transformed_reader']['native_action']=correct
        statuses=Counter(receipt_map[i]['status']if i in receipt_map else'NOT_RETRIEVED'for i in request_ids);row['logged_new_requests']={'unique_explicit_requests':len(request_ids),'statuses':dict(sorted(statuses.items())),'denominator_not_reduced_by_rejections':True,'scope':'IDs in explicit new request wrappers, excluding the documentary parent and commit. Full native receipt history also remains in the primary; no assumption that a functional response requires a fresh reader to be admitted.'};row['dose_current_correct']=sum(r['standard_task_correct']for r in row['dose_current']);row['dose_current_total']=len(row['dose_current']);result['cases'][casekey]=row
    parent_index=families.get('INDICE_ESTADOS_COMPLETOS_47/passive',{}).get('parents',{})
    result['parent_header_checks']={}
    for h,v in parent_index.items():
        decoded=header_fields(v['header']['header_bytes_hex']);equal=all(decoded[k]==v['header'][k]for k in decoded)
        if not equal:raise AssertionError('Extracted native parent header fields disagree')
        result['parent_header_checks'][h]={'decoded':decoded,'matches':equal,'parent_snapshot_sha256':v['snapshot_sha256']}
    for key,v in families.items():
        row=result['cases'][key];parent=v.get('parent',{});h=parent.get('snapshot_sha256')if isinstance(parent,dict)else None
        if key.startswith(('AGENDAS_Y_CANALES_20/','INDICE_ESTADOS_COMPLETOS_47/','OBSERVACION_02/'))or v.get('no_evolution_or_material_probe')or v.get('passive_no_evolution'):
            row['admission_accounting']={'mode':'PASSIVE_EXISTING_STATE_INSPECTION','new_requests':0,'new_applied':0,'scope':'Old receipt histories in inspected states are not counted as newly requested inputs.'}
        elif isinstance(v.get('worlds'),dict):
            row['admission_accounting']={'mode':'SEPARATE_NEW_RUNTIME_NAMESPACES','worlds':{name:{'requested':len(w['receipts']),'statuses':dict(Counter(r['status']for r in w['receipts']))}for name,w in v['worlds'].items()},'not_merged_by_repeated_local_event_id':True}
        elif h in parent_index:
            first=parent_index[h]['header']['next_event_id'];new=[r for i,r in case_receipts[key].items()if i>=first];row['admission_accounting']={'mode':'FULL_PARENT_HEADER_BOUNDARY_PLUS_FINAL_RECEIPTS_OR_COMPLETE_OPERATION_WRAPPERS','first_new_event_id':first,'new_requests':len(new),'statuses':dict(sorted(Counter(r['status']for r in new).items())),'parent_pending':parent_index[h]['pending_count'],'parent_header_extraction_verified':True,'all_rejected_and_pending_retained':True}
        else:row['admission_accounting']={'mode':'EXPLICIT_REQUEST_WRAPPERS_ONLY','counts':row['logged_new_requests'],'scope':'No initial-ID boundary recovered here. Do not treat this as a complete total beyond the recorded request wrappers; source code/native receipts remain included.'}
    fact={key.rsplit('/',1)[-1]:v for key,v in families.items()if key.startswith('FACTORIAL_E1_07/')}
    if len(fact)==4:
        result['factorial07']['pair_checks']={x+'_'+y:{k:fact[x]['before_I'][k]==fact[y]['before_I'][k]for k in('physical','native_projection','receipts')}for x,y in(('W00','W01'),('W10','W11'))}
        for stage in('immediate','late'):
            rs={k:{i:int(v)for i,v,c in f[stage]['rows']}for k,f in fact.items()};keys=set().union(*(set(v)for v in rs.values()));different=[i for i in sorted(keys)if(rs['W01'].get(i,0)^rs['W00'].get(i,0))!=(rs['W11'].get(i,0)^rs['W10'].get(i,0))];result['factorial07'][stage]={'differing_XOR_effect_sites':len(different),'indices':different}
    result['summary']={'primary_cases':len(result['cases']),'cases_with_field_errors':sum(bool(v['field_errors'])for v in result['cases'].values()),'record_field_checks':result['record_field_checks'],'decoder_checks':result['decoder_checks'],'decoder_mismatches':len(result['decoder_mismatches']),'uint64_float_errors':len(result['uint64_float_errors'])}
    # Selected full-field frames can be checked without assuming the sparse ROI
    # is a complete operational snapshot. These are physical data only.
    if deep:
        source=root/'EVIDENCIA_ESENCIAL/campos'
        checks=[]
        def verify_lines(name,lines):
            count=0;not_global=0
            for line in lines:
                q=json.loads(line)
                if not {'rows','N','clock_default','clock_exceptions','RAW_sha256','clocks_sha256'}<=q.keys():not_global+=1;continue
                n=q['N'];raw=array.array('Q',[0])*n**3;clocks=array.array('Q',[int(q['clock_default'])])*n**3
                for i,v,c in q['rows']:raw[i]=int(v);clocks[i]=int(c)
                for i,c in q['clock_exceptions']:clocks[i]=int(c)
                if sys.byteorder!='little':raw.byteswap();clocks.byteswap()
                if sha(raw.tobytes())!=q['RAW_sha256']or sha(clocks.tobytes())!=q['clocks_sha256']:raise AssertionError('Sparse exact field reconstruction mismatch '+name+' tick'+str(q['tick']))
                count+=1
            checks.append({'source':name,'checked_global_frames':count,'non_global_route_records':not_global})
        archive=next((p for p in(root/'EVIDENCIA_ESENCIAL/REGISTROS_MEDIDOS.tar.xz',root/'EVIDENCIA_ESENCIAL/REGISTROS_COMPLETOS.tar.xz')if p.exists()),None)
        if archive:
            with tarfile.open(archive,'r|xz')as tf:
                for member in tf:
                    if member.isfile()and member.name.startswith('campos/')and member.name.endswith('.jsonl'):verify_lines(member.name,tf.extractfile(member))
        elif source.exists():
            for path in sorted(source.rglob('*.jsonl.gz')):
                with gzip.open(path,'rt',encoding='utf8')as f:verify_lines(path.relative_to(source).as_posix(),f)
        else:raise ValueError('Deep field verification requested but no packaged global-field records are available')
        result['deep_field_hash_checks']=checks
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--out',type=Path,required=True);p.add_argument('--deep',action='store_true');a=p.parse_args();r=recompute(a.root,a.deep);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps(r['summary'],ensure_ascii=False));return 1 if r['summary']['cases_with_field_errors']or r['summary']['decoder_mismatches']or r['summary']['uint64_float_errors']else 0
if __name__=='__main__':raise SystemExit(main())
