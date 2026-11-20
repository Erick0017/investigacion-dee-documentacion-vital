"""Portable passive R03 verifier: JSON/RAW records only, no DEE imports or ticks.

python -I -B -X utf8 RECALCULAR_ADVERTENCIA_R03.py --evidence DIR --output result.json --strict
Optional --code FROZEN_PY performs static AST/source identity checks, never imports it.
Optional --expected PRIOR_RESULT verifies all listed evidence hashes before recalculation.
"""
from pathlib import Path
import argparse,ast,datetime,gzip,hashlib,json,sys

N=67;H=[4,34,24]
HISTORIES=('paired','unpaired','omit','no_training','report_only')
PROBES=((2,True),(3,False),(5,True))
def digest(data):return hashlib.sha256(data).hexdigest()
def decode(raw):
    if isinstance(raw,bool)or isinstance(raw,float):raise ValueError('RAW must be exact integer/string')
    value=int(raw)
    if not 0<=value<2**64:raise ValueError('RAW outside uint64')
    def signed(shift):
        x=(value>>shift)&15;return x-16 if x&8 else x
    return {'raw':str(value),'state':value&0xffffffff,'s_reg':(value>>32)&65535,
            'semantic':(value>>60)&15,'direction':[signed(48),signed(52),signed(56)]}
def command(observation):
    d=decode(observation['raw'])
    return 'CLOSE'if d['state']>0 and d['semantic']==1 and d['direction']==[-1,1,0]else None
def compact(o):return {k:o[k]for k in('tick','site','raw','clock','state','s_reg','semantic','direction')}
def status(row):return str(row['receipt'].get('status','')).lower()
def denominators(requests):
    ids=[int(x['id'])for x in requests];unique={int(x['id']):x for x in requests}
    return {'requested_unique':len(unique),'duplicate_aliases':len(ids)-len(unique),
            'applied':sum(status(x)=='applied'for x in unique.values()),
            'rejected':sum(status(x)=='rejected'or status(x).startswith('rejected_')for x in unique.values()),
            'nonterminal':sum(status(x)not in('applied','rejected')and not status(x).startswith('rejected_')for x in unique.values()),
            'submitted_load_sum':sum(int(x['payload'])for x in unique.values()),
            'applied_load_sum':sum(int(x['payload'])for x in unique.values()if status(x)=='applied'),
            'applied_zero_load_inputs':sum(int(x['payload'])==0 and status(x)=='applied'for x in unique.values())}
def signature_key(physical):return tuple(physical[k]for k in('N','tick','RAW_sha256','clocks_sha256'))

def run(evidence,code=None,expected=None):
    evidence=Path(evidence).resolve();errors=[];sources=[];lives=[]
    expected_hashes={}if expected is None else{x['file']:x['sha256']for x in json.loads(Path(expected).read_text(encoding='utf-8-sig'))['source_files']}
    def check(ok,message):
        if not ok:errors.append(message)
    def read(name,role):
        if '/'in name or'\\'in name or':'in name:raise ValueError('Only fixed local evidence names accepted')
        p=evidence/name
        if not p.exists():p=evidence/(name+'.gz')
        if p.is_symlink()or getattr(p.stat(),'st_file_attributes',0)&1024:raise ValueError('Evidence link/reparse refused')
        stored=p.read_bytes();data=gzip.decompress(stored)if p.suffix=='.gz'else stored;h=digest(data)
        if expected is not None:check(expected_hashes.get(name)==h,'Expected evidence identity:'+name)
        sources.append({'file':name,'bytes':len(data),'sha256':h,'role':role,
                        'stored_file':p.name,'stored_bytes':len(stored),'stored_sha256':digest(stored)})
        return json.loads(data.decode('utf-8-sig'))
    def observation(o,label,site=None):
        d=decode(o['raw'])
        for key in('state','s_reg','semantic','direction'):check(o[key]==d[key],label+': RAW/'+key+' disagree')
        if site is not None:check(o['site']==site,label+': wrong physical site')
        for key in('tick','clock'):
            check(not isinstance(o[key],(float,bool))and int(o[key])>=0,label+': exact '+key)
        return d
    def capture(name,history,operation):
        outer=read(name,'Primary queue capture, not a summary verdict')
        check(outer['status']=='completed',name+': queue operation not completed')
        check(outer['error']is None,name+': queue error present')
        payload=outer['payload'];check(digest(payload.encode('utf-8'))==outer['payload_sha'],name+': payload hash')
        literal=json.loads(payload);check(set(literal)=={'actuador','operacion','retorno','situaciones'},name+': undeclared payload keys')
        check(literal['actuador']=='closed'and literal['operacion']=='sesion'and literal['retorno']=='real',name+': changed wrapper contract')
        check(len(literal['situaciones'])==1,name+': unexpected multiple situations')
        envelope=json.loads(outer['result'])if isinstance(outer['result'],str)else outer['result']
        check(envelope['id']==outer['id'],name+': result ID')
        row=envelope['result']['rows'][0]
        check(len(envelope['result']['rows'])==1,name+': result rows')
        check(row['version']=='PI02.warning_association.R03.experimental.v2',name+': executed source revision')
        check(row['operation']==operation,name+': wrong operation')
        life=envelope['committed_snapshot']['life_id']
        check(life=='ECI02_PI02_W_'+history.upper(),name+': life identity')
        check(row['before']['tick']==envelope['before_tick']and row['after']['tick']==envelope['after_tick'],name+': before/after boundary')
        frames=row['frames'];ticks=[int(x['tick'])for x in frames]
        check(ticks==list(range(int(row['before']['tick']),int(row['after']['tick'])+1)),name+': frame coverage/gaps')
        for frame in frames:
            observation(frame['hub'],name+'H'+str(frame['tick']),H)
            check(int(frame['hub']['tick'])==int(frame['tick']),name+': frame/hub time')
            check(frame['fixed_signature_diagnostic']==command(frame['hub']),name+': diagnostic signature differs from RAW')
            if 'context_radius3'in frame:
                region=frame['context_radius3'];check(len(region)==343,name+': ROI size')
                check(len({tuple(x['site'])for x in region})==343,name+': ROI duplicate sites')
                for point in region:
                    observation(point,name+'ROI')
                    check(max(min(abs(point['site'][j]-H[j]),N-abs(point['site'][j]-H[j]))for j in range(3))<=3,name+': ROI escapes radius3')
        requests=row['requests']
        for req in requests:
            check(int(req['id'])==int(req['receipt']['id']),name+': request/receipt ID')
            check(req['receipt']['requested_tick']==req['requested_tick'],name+': requested boundary')
            check(req['receipt']['channels']==[req['channel']],name+': receipt channel')
        deps=envelope['committed_snapshot']['operational_dependencies']['PI02']['R03_warning_protocol']
        check(deps['version']==row['version']and deps['hub']==H,name+': operational dependency version/hub')
        check(deps['in_progress']is None and deps['uncertain']is False,name+': unclosed protocol progress')
        return outer,envelope,row,literal['situaciones'][0],deps
    def frame_at(row,tick):return next(x for x in row['frames']if x['tick']==tick)
    def encounter(row,tick):
        before=frame_at(row,tick-1);after=frame_at(row,tick);candidates=[]
        for o in before.get('context_radius3',[]):
            if o['site']==H:continue
            dist=max(min(abs(o['site'][j]-H[j]),N-abs(o['site'][j]-H[j]))for j in range(3))
            if dist<=1 and any(o['direction'])and[(o['site'][j]+o['direction'][j])%N for j in range(3)]==H:
                candidates.append(compact(o))
        load=min(sum(x['s_reg']for x in candidates),19664)
        sums=[sum(x['direction'][j]for x in candidates)for j in range(3)]
        reduced=[(x>0)-(x<0)for x in sums]
        return {'tick':tick,'pre_H':compact(before['hub']),'post_H':compact(after['hub']),
                'direct_ballistic_candidates_in_recorded_Moore_context':candidates,
                'candidate_reducer':{'s_reg':load,'direction':reduced},
                'matches_candidate_reduction':len(candidates)>1 and int(before['hub']['raw'])==0 and after['hub']['s_reg']==load and after['hub']['direction']==reduced,
                'attribution':'Recorded immediate proposals plus matching reducer, not unique full genealogy or kernel reproduction'}
    for history in HISTORIES:
        label=history.upper();base='PI02_R03_W_'+label
        imported=read(base+'_IMPORT.json','Import provenance only; no new acquisition')
        check(imported['exit_code']==0,base+': import exit code')
        imported_result=json.loads(imported['stdout']);check(imported_result['tick']==740937 and imported_result['new_ticks']==0,base+': import cut')
        prepare_outer=read(base+'_PREPARE.json','Interface preparation primary')
        check(prepare_outer['status']=='completed',base+': interface preparation status')
        prepared=json.loads(prepare_outer['result'])['result']['rows'][0]
        check(prepared['new_material_inputs']==0 and prepared['raw_or_clock_edits']==0 and prepared['seed_inserted']is False,base+': preparation inserted content')
        outer,env,training,literal,deps=capture(base+'_TRAIN.json',history,'train')
        check(literal=={'historia':history,'modo':'eci01-pi02-advertencia-adquirir'},base+': training literal/metadata leak')
        t=training['before']['tick']+2;anchor=t+8
        w=t+1 if history=='unpaired'else t if history in('paired','omit')else None
        u=t+5 if history in('paired','unpaired','report_only')else None
        check(training['W_input_tick']==w and training['U_input_tick']==u,base+': fixed experience times')
        check(training['anchor_external']==anchor and training['after']['tick']==anchor+2*N+3,base+': common training calendar')
        expected_requests=[]
        if w is not None:expected_requests.append(('PI02.R03.warning',w,7))
        if u is not None:expected_requests.append(('PI02.R03.alteration_report',u,11))
        check([(x['channel'],x['requested_tick'],x['payload'])for x in training['requests']]==expected_requests,base+': experience content')
        check(deps['training']['anchor_external']==anchor and deps['training']['history_record_only']==history,base+': protocol record')
        rows=[];all_requests=list(training['requests']);before_next=signature_key(training['after'])
        for index,(periods,warning)in enumerate(PROBES):
            name=base+'_PROBE%02d.json'%index
            _,penv,probe,pliteral,pdeps=capture(name,history,'probe')
            check(pliteral=={'aviso':warning,'modo':'eci01-pi02-advertencia-usar','periodos':periods},name+': probe literal/metadata leak')
            check(signature_key(probe['before'])==before_next,name+': same-life continuity')
            before_next=signature_key(probe['after'])
            q=anchor+((probe['before']['tick']+10-anchor+N-1)//N)*N+periods*N
            check(probe['fixed_read_tick']==q==probe['fixed_query_tick']and probe['fixed_read_window_radius']==0,name+': frozen reader')
            check(probe['fixed_end_tick']==q+N+3==probe['after']['tick'],name+': frozen horizon')
            fixed=frame_at(probe,q)['hub'];observation(probe['fixed_observation'],name+'fixed',H)
            check(fixed==probe['fixed_observation'],name+': selected alternate frame')
            calculated=command(fixed);check(probe['fixed_command']==calculated,name+': output not RAW-derived')
            wanted=[('PI02.R03.warning',q-8,7),('PI02.R03.normalizer',q+N-3,0)]if warning else[]
            check([(x['channel'],x['requested_tick'],x['payload'])for x in probe['requests']]==wanted,name+': input/normalizer schedule')
            recorded=[(x['tick'],x['hub']['raw'])for x in probe['all_signature_events_diagnostic_only']]
            calculated_events=[(x['tick'],x['hub']['raw'])for x in probe['frames']if command(x['hub'])=='CLOSE']
            check(recorded==calculated_events,name+': diagnostic event coverage')
            reqW=next((x for x in probe['requests']if x['channel']=='PI02.R03.warning'),None)
            rows.append({'index':index,'periods_external':periods,'warning_offered':warning,'before_tick':probe['before']['tick'],'after_tick':probe['after']['tick'],
                         'q':q,'fixed_observation':compact(fixed),'RAW_recalculated_command':calculated,'reported_command':probe['fixed_command'],
                         'W_requested':reqW is not None,'W_status':None if reqW is None else status(reqW),'admissions':denominators(probe['requests']),
                         'request_receipts':probe['requests'],'normalizer_tick_observation':compact(frame_at(probe,q+N)['hub']),
                         'encounter_at_q':encounter(probe,q),'encounter_at_normalizer':encounter(probe,q+N),
                         'signature_events_diagnostic_not_scored':calculated_events,
                         'zero_and_NULL':'NULL means the fixed CLOSE signature is absent; it is not a scalar zero. Gpayload0 is still material.'})
            all_requests.extend(probe['requests'])
        ids=[x['id']for x in all_requests];check(len(ids)==len(set(ids)),base+': duplicate Native IDs within this life')
        summary=read('RESUMEN_'+base+'.json','Reported summary checked against primaries, not used to compute responses')
        check(summary['life']==env['committed_snapshot']['life_id']and summary['history']==history,base+': summary life/history')
        for index,row in enumerate(rows):
            sr=summary['rows'][index]
            check(sr['fixed_command']==row['RAW_recalculated_command']and sr['fixed_observation']['raw']==row['fixed_observation']['raw'],base+': summary differs from primary')
        lives.append({'life':env['committed_snapshot']['life_id'],'history':history,'training_before_reported_global':training['before'],'training_after_reported_global':training['after'],
                      'training_anchor':anchor,'training_admissions':denominators(training['requests']),'training_requests':training['requests'],
                      'training_encounters':[encounter(training,anchor),encounter(training,anchor+1)],
                      'training_H_and_returns':[compact(frame_at(training,anchor+k)['hub'])for k in(0,1,N,2*N)],
                      'first_probe':rows[0],'all_probes':rows,'all_scored_requests_in_this_life':denominators(all_requests),
                      'final_tick':rows[-1]['after_tick'],'shared_prefix':'Related clones from post_B mainT740937; not independent learned organisms'})
    comparison={'same_reported_initial_N_T_RAW_clocks':len({signature_key(x['training_before_reported_global'])for x in lives})==1,
                'same_training_end':len({x['training_after_reported_global']['tick']for x in lives})==1,
                'same_probe_qs':len({tuple(y['q']for y in x['all_probes'])for x in lives})==1,
                'same_final_tick':len({x['final_tick']for x in lives})==1}
    unpaired=next(x for x in lives if x['history']=='unpaired');report=next(x for x in lives if x['history']=='report_only')
    comparison['unpaired_report_only_training_RAW_clocks_equal']=signature_key(unpaired['training_after_reported_global'])==signature_key(report['training_after_reported_global'])
    comparison['equality_scope']='Reported physical N/T/RAW/clocks hashes only; receipts, life labels and metadata differ. Not complete causal-state identity.'
    code_audit=None
    if code is not None:
        b=Path(code).read_bytes();tree=ast.parse(b.decode('utf-8'));functions={x.name:x for x in tree.body if isinstance(x,ast.FunctionDef)}
        decoder=functions['decode_fixed'];names=sorted({x.id for x in ast.walk(decoder)if isinstance(x,ast.Name)})
        code_audit={'file':Path(code).name,'bytes':len(b),'sha256':digest(b),'AST_only_not_imported':True,'decoder_parameters':[x.arg for x in decoder.args.args],
                    'decoder_referenced_names':names,'top_level_imports':[ast.unparse(x)for x in tree.body if isinstance(x,(ast.Import,ast.ImportFrom))],
                    'interpretation':'decode_fixed receives only the observation; probe reads training anchor as a prepared calendar, not history label/expected answer to select CLOSE. Static local source review, not formal whole-process noninterference proof.'}
        check(code_audit['sha256']=='b7fb74f53f7e9c1384f88718bf07819bdb00a731429fc848f7b34f6739b42e90','Executed warning code identity')
    for source in sources:
        f=evidence/source['stored_file'];b=f.read_bytes()
        check(digest(b)==source['stored_sha256'],'Stored source changed during recalculation:'+source['file'])
        check(digest(gzip.decompress(b)if f.suffix=='.gz'else b)==source['sha256'],'Source changed during recalculation:'+source['file'])
    return {'schema':'PI02.warning.R03.passive_recalculation.v1','calculated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_ticks':0,'DEE_imports':0,
            'source_files':sources,'lives':lives,'comparability':comparison,'source_code_audit':code_audit,'inconsistencies':errors,
            'verdict_scope':'Counts and RAW/signature consistency only; no automatic cognitive/anticipation/promotion verdict.',
            'limits':['Three material probes per related history, not independent replications','Development protocol, not reserved functional regulation test','No valve or useful external consequence in these records','No-warning omits W and G, so lower dose; not a matched-dose query-effect ablation','Material probes and G change later control states; admission, propagation, current reader output and learned utility remain distinct']}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--code',type=Path);parser.add_argument('--expected',type=Path);parser.add_argument('--strict',action='store_true');args=parser.parse_args()
    result=run(args.evidence,args.code,args.expected);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'histories':[{'history':x['history'],'training':x['training_admissions'],'probes':[{'q':y['q'],'warning':y['warning_offered'],'W_status':y['W_status'],'command':y['RAW_recalculated_command'],'s_reg':y['fixed_observation']['s_reg'],'direction':y['fixed_observation']['direction']}for y in x['all_probes']]}for x in result['lives']],'comparability':result['comparability'],'inconsistencies':result['inconsistencies']},ensure_ascii=False,indent=2))
    return 2 if args.strict and result['inconsistencies']else 0
if __name__=='__main__':sys.exit(main())
