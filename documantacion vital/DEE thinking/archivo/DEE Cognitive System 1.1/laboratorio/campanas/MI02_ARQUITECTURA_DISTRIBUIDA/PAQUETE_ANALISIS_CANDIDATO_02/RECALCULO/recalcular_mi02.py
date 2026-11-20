"""Portable recorded-evidence calculation. Stdlib only. ZERO native ticks.

Never imports the DEE engine, restores a participant or supplies an answer.
Original result flags remain evidence; motor absence is independently counted
from exact contact fields, including wrong outputs whose return was omitted.
"""
import argparse,collections,gzip,hashlib,importlib.util,json,math
from pathlib import Path

def fields(raw):
    v=int(raw)
    if not 0<=v<1<<64:raise ValueError('RAW outside uint64')
    def signed(k):x=(v>>k)&15;return x-16 if x&8 else x
    return{'state':v&0xffffffff,'s_reg':(v>>32)&65535,'direction':[signed(k)for k in(48,52,56)],'semantic':(v>>60)&15}
def qualified(o):
    f=fields(o['raw']);return f['state']>0 and f['semantic']==1 and f['direction'][0]in(-1,0,1)and f['direction'][1:]==[-1,-1]
def walk(x):
    if isinstance(x,dict):
        yield x
        for v in x.values():yield from walk(v)
    elif isinstance(x,list):
        for v in x:yield from walk(v)
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def motor_rows(result):
    if isinstance(result,dict):
        if'rows'in result and isinstance(result['rows'],list):
            for r in result['rows']:
                if'critical_tick'in r and'frames'in r:yield r
        if'native_result'in result:yield from motor_rows(result['native_result'])
def contact_score(r):
    t=r['critical_tick']-15;f=next((f for f in r['frames']if f['tick']==t),None)
    if not f or'contacts'not in f:return{'covered':False}
    good=[];bad=[];reflected=[];emitted=[]
    for label,o in f['contacts'].items():
        v=fields(o['raw']);sign=int(label);action=1 if sign>=0 else-1
        if v['state']<=0 or v['semantic']!=1:continue
        if v['direction']in([sign,-1,-1],[sign,-1,0]):emitted.append(sign)
        if v['direction']==[sign,-1,-1]:
            (good if action==r['availability']else bad).append(sign)
        if v['direction']==[sign,-1,0]and action!=r['availability']:reflected.append(sign)
    conflict=bool(good and(bad or reflected))
    return{'covered':True,'tick':t,'useful':bool(good)and not conflict,'wrong':bool(bad or reflected),'reflected_failure':bool(reflected),'absent':not emitted,'conflict':conflict,'emitted':emitted,'useful_signs':good,'wrong_unreturned':bad,'original_absence_flag':r.get('no_motor_output'),'original_absence_flag_disagrees':('no_motor_output'in r and r['no_motor_output']!=(not emitted))}

def calculate(root):
    index=json.loads((root/'INDICE_EVIDENCIA.json').read_bytes());mapping={x['jsonl_line_1based']:x for x in index['index']};summaries=[];native=[];external=[];word=[];ephemeral=[];process=[];editorial=[];total_fields=0;receipts_by_life={};social=[]
    with gzip.open(root/'EVIDENCIA_ESENCIAL/REGISTROS_PRIMARIOS.jsonl.gz','rb')as z:
        for line_number,line in enumerate(z,1):
            packet=json.loads(line);h=hashlib.sha256(line.rstrip(b'\n')).hexdigest()
            if h!=mapping[line_number]['projection_sha256']:raise AssertionError('Projection hash mismatch line'+str(line_number))
            x=packet['data'];typ=packet['type'];id=x.get('id',Path(packet['original']['original']).stem)if isinstance(x,dict)else Path(packet['original']['original']).stem
            if typ=='proceso_operativo':
                if id.startswith('VERIFICACION_WORD_'):
                    editorial.append({'id':id,'returncode':x['returncode'],'command':x['command'],'visual_validation':x.get('visual_validation',False),'stderr':x.get('stderr')});continue
                process.append({'id':id,'returncode':x['returncode'],'command':x['command'],'fence':x.get('result',{}).get('INSTRUMENTO_FENCE')})
                v=x.get('result',{})
                if not isinstance(v,dict)or not isinstance(v.get('result'),dict)or'life_id'not in v.get('INSTRUMENTO',{}):continue
                x={'id':id,'life':v['INSTRUMENTO']['life_id'],'before':{},'after':{'physical':v.get('physical',{})},'data':v,'error':None};typ='trayectoria'
            if typ!='trayectoria':continue
            result=(x.get('data')or{}).get('result');life=x['life'];before=x.get('before')or{};after=x.get('after')or{};row={'id':id,'life':life,'tick_before':before.get('physical',{}).get('tick'),'tick_after':after.get('physical',{}).get('tick'),'error':x.get('error'),'source':packet['original']['original'],'source_sha256':packet['original']['original_sha256']}
            requests={};field_count=0
            for o in walk(result):
                if'raw'in o and isinstance(o['raw'],str)and o['raw'].isdigit()and isinstance(o.get('state'),int)and isinstance(o.get('semantic'),int)and isinstance(o.get('direction'),list):
                    expected=fields(o['raw'])
                    for key in('state','s_reg','semantic','direction'):
                        if key in o and o[key]!=expected[key]:raise AssertionError('RAW decode differs '+id+' '+key)
                    if' clock'in o:raise AssertionError('Unexpected ambiguous clock field')
                    if'clock'in o and not str(o['clock']).isdigit():raise AssertionError('Clock not exact integer')
                    field_count+=1
                if isinstance(o.get('receipt'),dict)and'id'in o['receipt']:
                    r=o['receipt'];key=str(r['id'])
                    if key in requests and requests[key]!=r:raise AssertionError('Conflicting receipts in one record '+id+' '+key)
                    requests[key]=r
            total_fields+=field_count;row['exact_fields_checked']=field_count;row['requests_unique']=len(requests);row['receipt_statuses']=dict(collections.Counter(r['status']for r in requests.values()))
            for key,value in requests.items():receipts_by_life.setdefault(life,{})[key]=value
            scores=[contact_score(r)for r in motor_rows(result)]
            if scores:
                row['motor']={'opportunities':len(scores),'covered':sum(s['covered']for s in scores),'useful':sum(s.get('useful',False)for s in scores),'wrong':sum(s.get('wrong',False)for s in scores),'reflected_failure':sum(s.get('reflected_failure',False)for s in scores),'absent':sum(s.get('absent',False)for s in scores),'conflicts':sum(s.get('conflict',False)for s in scores),'old_absence_flags_disagree':sum(s.get('original_absence_flag_disagrees',False)for s in scores),'scores':scores}
                for i,s in enumerate(scores):native.append({'experiment':id,'life':life,'opportunity':i,'source':row['source'],'source_sha256':row['source_sha256'],**s})
            if isinstance(result,dict)and isinstance(result.get('rows'),list):
                erows=[r for r in result['rows']if'codec_revision'in r and'executed_torque'in r and'native'in r]
                if erows:
                    reward=0.0;signs=collections.Counter()
                    for i,r in enumerate(erows):
                        expected=(2 if fields(r['native']['raw'])['direction'][0]>=0 else-2)if qualified(r['native'])else 0
                        if r['native_torque']!=expected:raise AssertionError('External native torque decode differs '+id)
                        if r['response']['applied_torque']!=r['executed_torque']:raise AssertionError('Actuator transduction differs '+id)
                        if r['mode']=='nulled'and r['executed_torque']!=0:raise AssertionError('Null actuator control not null')
                        reward+=r['response']['reward'];signs[str(r['native_torque'])]+=1
                    row['external']={'steps':len(erows),'reward_sum':reward,'native_torques':dict(signs),'executed_nonzero':sum(r['executed_torque']!=0 for r in erows),'sensor_requests':sum(len(r['requests'])for r in erows),'sensor_applied':sum(q['receipt']['status']=='applied'for r in erows for q in r['requests']),'mode':erows[0]['mode'],'sensor_mode':erows[0]['sensor_mode'],'codec_revision':erows[0]['codec_revision']};external.append({'experiment':id,'life':life,'source':row['source'],'source_sha256':row['source_sha256'],**row['external']})
                wrows=[r for r in result['rows']if'word'in r and'native_command'in r]
                if wrows:
                    for r in wrows:
                        expected=(1 if fields(r['native']['raw'])['direction'][0]>=0 else-1)if qualified(r['native'])else None
                        if expected!=r['native_command']:raise AssertionError('Word signal native decode differs '+id)
                        if r.get('target_or_teacher_sent')is not False:raise AssertionError('Word use not separated from teacher')
                    row['word_use']={'trials':len(wrows),'intended_label_correct':sum(r['native_command']=={'izquierda':1,'derecha':-1}[r['word']]for r in wrows),'valid':sum(r['native_command']is not None for r in wrows),'commands':[r['native_command']for r in wrows],'words':[r['word']for r in wrows],'semantic_attribution':'Not acquired word-specific meaning: unpaired-consequence control also separates the two fixed codes.'};word.append({'experiment':id,'life':life,**row['word_use']})
                qrows=[r for r in result['rows']if'raw_current_observation'in r and'native_class'in r and'after_Q'in r]
                if qrows:
                    for r in qrows:
                        v=r['frames'][1]['Q'];expected=fields(v['raw'])['direction'][0]if qualified(v)else None
                        if expected!=r['native_class']:raise AssertionError('Ephemeral native decode differs '+id)
                    row['ephemeral']={'uses':len(qrows),'valid':sum(r['native_class']is not None for r in qrows),'empty_reader_after_use':sum(fields(r['after_Q']['raw'])['state']==0 for r in qrows),'RAW_zero_reader_after_use':sum(int(r['after_Q']['raw'])==0 for r in qrows),'values':[r['raw_current_observation']for r in qrows],'classes':[r['native_class']for r in qrows]};ephemeral.append({'experiment':id,'life':life,**row['ephemeral']})
            if isinstance(result,dict)and'passive_every_tick'in result:
                frames=result['passive_every_tick'];runs=[];old=None;start=None;last=None
                for f in frames:
                    if last is not None and f['tick']!=last+1:raise AssertionError('Supposed continuous B trace has a gap')
                    active=fields(f['B']['raw'])['state']>0
                    if active!=old:
                        if old is not None:runs.append({'start':start,'end':last,'active':old})
                        start=f['tick'];old=active
                    last=f['tick']
                if old is not None:runs.append({'start':start,'end':last,'active':old})
                by_tick={f['tick']:f for f in frames};activations=[]
                for run in runs:
                    if run['active']and run['start']-3 in by_tick:activations.append({'reader_activation':run['start'],'preceding_last_gate_tick':run['start']-3,'gate':by_tick[run['start']-3]['query_last']})
                row['social_reader']={'complete_tick_observations':len(frames),'reader_state_runs':runs,'activations_with_gate_witness':activations,'qualified_private_response_samples':sum(qualified(f['B'])for f in frames),'not_independent_queries':'Bursts of a continuing native query train, not independent agents or learned conversation turns.'};social.append({'experiment':id,'life':life,**row['social_reader']})
            summaries.append(row)
    snapshots=[]
    spec=importlib.util.spec_from_file_location('portable_snapshot_observer',root/'CODIGO_EXACTO/observador_snapshot.py');observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
    for row in index['selected_lives']:
        p=root/row['included_snapshot'];s=observer.Snapshot(p)
        if sha(p)!=row['native_snapshot_sha256']:raise AssertionError('Selected snapshot changed')
        expected=row['record']['physical'];actual=s.summary()
        for k in('N','tick','RAW_sha256','clocks_sha256'):
            if expected[k]!=actual[k]:raise AssertionError('Snapshot/record mismatch '+row['life']+' '+k)
        snapshots.append({'life':row['life'],'included_snapshot':row['included_snapshot'],'summary':actual})
    initial=[];initial_comparisons=[]
    for v in index.get('diagnostic_initial_snapshots',[]):
        p=root/v['snapshot'];a=observer.Snapshot(p)
        if sha(p)!=v['sha256']:raise AssertionError('Initial diagnostic snapshot changed')
        initial.append(a)
    if initial:
        for other in initial[1:]:
            result=observer.compare(initial[0],other,sample_limit=4)
            if result['RAW_different_sites']!=1 or result['clock_different_sites']!=0:raise AssertionError('One-site structural contrast is not one-site')
            initial_comparisons.append({'baseline':initial[0].path.name,'other':other.path.name,'comparison':result})
    parent_validation=None
    if'historical_parent_snapshot'in index:
        row=index['historical_parent_snapshot'];p=root/row['snapshot'];parent=observer.Snapshot(p)
        if sha(p)!=row['sha256']or parent.tick!=24752 or parent.N!=67 or parent.pending:raise AssertionError('Historical father identity/agenda differs')
        sites=[[(40+dx)%67,(40+dy)%67,(10+dz)%67]for dx in range(-8,9)for dy in range(-8,9)for dz in range(-8,9)]
        nonzero=sum(int(parent.observation(p)['raw'])!=0 for p in sites)
        if nonzero:raise AssertionError('Inherited added frame was not prepared in an initially RAW-zero region')
        summary=parent.summary();summary.pop('path',None);parent_validation={'summary':summary,'prepared_box_positions_checked':len(sites),'nonzero_RAW_before_added_frame':nonzero,'scope':'Checks original father and stated peripheral preparation opportunity, NOT functional integration of old knowledge into the new region.'}
    counts={life:dict(collections.Counter(r['status']for r in rr.values()))for life,rr in sorted(receipts_by_life.items())}
    return{'scope':'RECORDED_EVIDENCE_RECALCULATION_ONLY_NO_NATIVE_EXECUTION','primary_records':len(summaries),'exact_field_observations_checked':total_fields,'unique_receipts_by_life':counts,'summaries':summaries,'native_opportunities':native,'external_trajectories':external,'word_signal_tests':word,'ephemeral_tests':ephemeral,'social_reader_tests':social,'manager_processes':process,'editorial_processes':editorial,'selected_snapshots':snapshots,'one_site_preparation_comparisons':initial_comparisons,'historical_parent_validation':parent_validation,'not_a_cognitive_verdict':True}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--raiz',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--salida',type=Path);ap.add_argument('--comparar',type=Path);args=ap.parse_args();result=calculate(args.raiz.resolve())
    if args.comparar:
        expected=json.loads(args.comparar.read_bytes())
        # Paths in forensic snapshot summaries differ between independent extractions.
        for x in(result,expected):
            for s in x['selected_snapshots']:s['summary'].pop('path',None)
        if result!=expected:raise AssertionError('Independent recalculation differs')
    if args.salida:args.salida.parent.mkdir(parents=True,exist_ok=True);args.salida.write_bytes(canonical(result)+b'\n')
    print(json.dumps({'primary_records':result['primary_records'],'native_opportunities':len(result['native_opportunities']),'external_trajectories':len(result['external_trajectories']),'word_signal_tests':len(result['word_signal_tests']),'ephemeral_tests':len(result['ephemeral_tests']),'exact_field_observations_checked':result['exact_field_observations_checked'],'snapshot_checks':len(result['selected_snapshots']),'compared':bool(args.comparar),'native_ticks_executed':0},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
