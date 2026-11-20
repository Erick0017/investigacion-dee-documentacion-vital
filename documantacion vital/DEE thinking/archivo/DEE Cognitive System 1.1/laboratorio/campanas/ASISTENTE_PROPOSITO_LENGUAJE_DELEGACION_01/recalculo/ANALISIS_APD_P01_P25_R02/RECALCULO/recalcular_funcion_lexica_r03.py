"""Offline matched lexical-history -> native numeric-function contrast."""
import argparse,gzip,hashlib,importlib.util,json
from pathlib import Path
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def run(folder,auditor):
    sp=importlib.util.spec_from_file_location('apd_numeric_auditor',auditor)
    audit=importlib.util.module_from_spec(sp);sp.loader.exec_module(audit)
    protocol_file=folder/'PROTOCOLO_CONGELADO.json'
    if not protocol_file.exists():protocol_file=folder/'PROTOCOLO_DEDUPLICADO.json'
    protocol=read(protocol_file);errors=[];cases=[];nobs=0;all_gates=None
    for case in('paired','reversed'):
        path=folder/(case+'_01_PRIMARY.json.gz');p=read(path);r=p['result'];rows=[];requests={}
        for where,node in audit.walk(r):
            if 'raw'in node and all(k in node for k in('state','s_reg','semantic','direction')):
                d=audit.decode(node['raw']);nobs+=1
                if any(node[k]!=d[k]for k in d):errors.append([case,where,'RAW_FIELDS_DISAGREE'])
            for q in node.get('requests',[])if isinstance(node.get('requests'),list)else[]:
                if isinstance(q,dict)and'receipt'in q:requests[str(q.get('id',q['receipt'].get('id')))]=q['receipt']
        for i,q in enumerate(r['rows']):
            expected_form,expected_operands=protocol['opportunities'][i]
            if q['literal_form']!=expected_form or q['raw_operands']!=expected_operands:errors.append([case,i,'COMMON_OPPORTUNITY_CHANGED'])
            gates=[o['site']for o in q['word']['reader']['panel']]
            if all_gates is None:all_gates=gates
            if gates!=all_gates or len(gates)!=20:errors.append([case,i,'COMMON20GATE_READER_CHANGED'])
            sign=audit.formed_word(q['word']);operation=q['native_operation']
            if sign!=q['formed_native_sign']:errors.append([case,i,'CACHED_WORD_SIGN_DISAGREES'])
            if operation is None:
                numeric={'valid':False,'actual':None,'correct':False};issued=None
            else:
                numeric=audit.native_numeric(operation,errors,case+'.rows['+str(i)+']')
                issued='suma'if sign==1 else('diferencia'if sign==-1 else None)
                if issued!=operation['operation']:errors.append([case,i,'OPERATION_NOT_FROM_PHYSICAL_SIGN'])
            rows.append({'form':q['literal_form'],'raw_operands':q['raw_operands'],'native_sign':sign,
                'word_input_tick':q['word']['input_tick'],'word_read_tick':q['word']['read_tick'],
                'issued_operation':issued,'numeric':numeric})
        panel=[]
        expected_old=[-1,-1,1,-1,-1,1,1,-1]+([1,-1]if case=='paired'else[-1,1])
        for q,target in zip(r['panel10'],expected_old):
            gates=[o['site']for o in q['reader']['panel']]
            if gates!=all_gates:errors.append([case,q['form'],'FINAL_PANEL_READER_CHANGED'])
            sign=audit.formed_word(q)
            if sign!=q['reader']['formed_native_command']:errors.append([case,q['form'],'FINAL_PANEL_CACHE_DISAGREES'])
            panel.append({'form':q['form'],'sign':sign,'matches_this_history':sign==target,'read_tick':q['read_tick']})
        counts={}
        for receipt in requests.values():counts[receipt['status']]=counts.get(receipt['status'],0)+1
        cases.append({'case':case,'life_id':p['INSTRUMENTO']['life_id'],'tick':p['physical']['tick'],
            'snapshot_sha256':p['INSTRUMENTO']['snapshot_sha256'],'primary_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'responses':rows,'panel10':panel,'numeric_correct':sum(q['numeric']['correct']for q in rows),'numeric_denominator':len(rows),
            'old10_retained':sum(q['matches_this_history']for q in panel),'old10_denominator':len(panel),
            'requests':{'requested_unique':len(requests),'status_counts':counts}})
    if len(cases[0]['responses'])!=len(cases[1]['responses']):errors.append(['UNEQUAL_COMMON_OPPORTUNITY_COUNT'])
    for a,b in zip(cases[0]['responses'],cases[1]['responses']):
        if (a['form'],a['raw_operands'],a['word_input_tick'],a['word_read_tick'])!=(b['form'],b['raw_operands'],b['word_input_tick'],b['word_read_tick']):
            errors.append(['UNMATCHED_PRESENT_INPUT_OR_AGE',a['form']])
    return {'schema':'APD01.lexical_function_recalculation.R03','cases':cases,'common_reader_gate_sites':all_gates,
        'RAW_observations_decoded':nobs,'discrepancies':errors,'native_ticks_executed':0,
        'scope':'Different learned cue signs select different prepared native numeric operations. No new teacher, host word-meaning lookup, external calculator, acquired arithmetic algorithm or general grammar is established.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primarios',type=Path,required=True);p.add_argument('--auditor',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();r=run(a.primarios,a.auditor);b=(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with a.salida.open('xb')as f:f.write(b)
    print(json.dumps({'cases':[{'case':q['case'],'numeric_correct':q['numeric_correct'],'numeric_denominator':q['numeric_denominator'],
        'results':[w['numeric']['actual']for w in q['responses']],'old10_retained':q['old10_retained'],'requests':q['requests']}for q in r['cases']],
        'RAW_observations_decoded':r['RAW_observations_decoded'],'discrepancies':r['discrepancies'],'sha256':hashlib.sha256(b).hexdigest()}))
    raise SystemExit(bool(r['discrepancies']))
