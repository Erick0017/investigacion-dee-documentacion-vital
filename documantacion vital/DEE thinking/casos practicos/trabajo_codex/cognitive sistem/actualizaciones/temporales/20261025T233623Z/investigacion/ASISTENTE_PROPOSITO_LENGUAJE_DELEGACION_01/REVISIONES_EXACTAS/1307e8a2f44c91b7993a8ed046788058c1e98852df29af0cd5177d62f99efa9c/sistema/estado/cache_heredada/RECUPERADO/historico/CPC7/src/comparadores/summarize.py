"""Post-trajectory calculations from an explicit finite result registry."""
import collections,hashlib,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PROFILES=('PILOT_01','PILOT_02','B1_FINAL','B2_FINAL','B2_NO_REPLAY')


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,x):
    path=Path(path)
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def tally(rows):
    n=len(rows);responses=sum(r['response_present'] for r in rows);correct=sum(r['correct'] for r in rows)
    return {'queries':n,'responses':responses,'absent':n-responses,'correct':correct,
            'accuracy_all_queries':correct/n if n else None,'coverage':responses/n if n else None}


def summarize():
    result=ROOT/'resultados/comparadores';fixtures=ROOT/'configuraciones/comparadores/fixtures_v1';cases=[];groups=collections.defaultdict(list)
    for profile in PROFILES:
        index=read(result/profile/'INDEX.json')
        for entry in index['cases']:
            tp=ROOT/entry['trajectory'];ep=ROOT/entry['evaluation'];t=read(tp);e=read(ep)
            evalfixture=read(fixtures/entry['fixture']['evaluator']);relation={q['event_id']:q.get('relation_index') for q in evalfixture['queries']}
            q=e['queries'];late=[r for r in q if r['block']=='Q2_REVISED_AND_RETAINED']
            key=(profile,e['task'],e['mode']);groups[key].append((t,e))
            cases.append({'case_id':e['case_id'],'profile':profile,'split':index['split'],'task':e['task'],'mode':e['mode'],
                'trajectory':str(tp.relative_to(ROOT)).replace('\\','/'),'trajectory_sha256':sha(tp),
                'evaluation':str(ep.relative_to(ROOT)).replace('\\','/'),'evaluation_sha256':sha(ep),
                'stream_sha256':t['stream_sha256'],'query_performance':tally(q),'panels':e['panels'],
                'retention':{'old8_after_new8':tally([r for r in q if r['block']=='Q1_RETAIN_8_ADD_8' and relation[r['event_id']] is not None and relation[r['event_id']]<8]),
                    'revised_key':tally([r for r in late if relation[r['event_id']]==0]),
                    'other15_after_revision':tally([r for r in late if relation[r['event_id']] is not None and relation[r['event_id']]!=0])},
                'resources':t['resources'],'initialization':t['initialization'],'job_exit_code':entry['exit_code']})
    aggregate=[]
    for (profile,task,mode),values in groups.items():
        q=[r for _,e in values for r in e['queries']]
        aggregate.append({'profile':profile,'task':task,'mode':mode,'model_preparations':len(values),'input_histories':len({t['stream_sha256'] for t,_ in values}),
            'performance':tally(q),'resources':{'wall_seconds_sum':sum(t['resources']['wall_seconds'] for t,_ in values),
            'cpu_seconds_sum':sum(t['resources']['cpu_seconds'] for t,_ in values),
            'peak_worker_rss_bytes_range':[min(t['resources']['final_memory']['peak_working_set_bytes'] for t,_ in values),max(t['resources']['final_memory']['peak_working_set_bytes'] for t,_ in values)],
            'training_examples':sum(t['resources']['training_examples'] for t,_ in values),
            'training_events_seen':sum(t['resources']['training_events_seen'] for t,_ in values),
            'gradient_steps':sum(t['resources']['gradient_steps'] for t,_ in values),
            'gradient_examples':sum(t['resources']['gradient_examples'] for t,_ in values),
            'replay_examples':sum(t['resources']['replay_examples'] for t,_ in values)}})
    restores=[]
    for kind in ('B1','B2'):
        original=read(result/(kind+'_FINAL')/'DIR_101_paired/checkpoints/FINAL.json')
        restored=read(result/(kind+'_RESTORE_01')/'checkpoints/FINAL.json')
        a=read(result/(kind+'_FINAL')/'DIR_101_paired/TRAJECTORY.json');b=read(result/(kind+'_RESTORE_01')/'TRAJECTORY.json')
        projected=lambda r:{k:r[k] for k in ('event_id','operation','response','state','probability_positive') if k in r}
        expected=[projected(r) for r in a['rows'] if r['event_id'] in {x['event_id'] for x in b['rows']}]
        actual=[projected(r) for r in b['rows']]
        same=original['model']==restored['model'];assert same and expected==actual
        restores.append({'model':kind,'continued_in_another_worker_process':True,'checkpoint_after_first16_before_revision':True,
             'final_state_exact':same,'subsequent_responses_exact':expected==actual,'new_scored_queries':16,
             'role':'Technical continuation reproduction, not a new independent scientific preparation.'})
    values={'schema':'CPC7.comparator.summary.v1','primary_model_trajectories':len(cases),
       'pilot_model_preparations':sum(c['split']=='PILOT' for c in cases),'reserved_model_preparations':sum(c['split']=='RESERVED' for c in cases),
       'unique_input_streams_executed':len({c['stream_sha256'] for c in cases}),'reserved_unique_input_streams':len({c['stream_sha256'] for c in cases if c['split']=='RESERVED'}),
       'query_rows_are_not_independent_replicates':True,'fixed_model_initialization_seed_not_statistical_seed_sweep':True,
       'technical_restorations':restores,'aggregates':aggregate,'cases':cases,
       'formulas':{'accuracy':'correct / all queries, including absent','coverage':'non-absent / all queries',
          'retained_old8':'Q1 queries of relation_index0..7 without re-teaching','retained_other15':'Q2 relation_index1..15, distinct from revised index0',
          'resources':'Measured in each process; actual model training/replay counted. Whole-process RSS includes interpreter; wall includes initialization and checkpoint writes.'},
       'scope':['Finite conventional comparison, not an ImageNet or lifelong-plasticity replication.',
          'B1 has a prepared key representation and gap invariance, B2 has fixed one-hot slot features; those conveniences are reported rather than attributed to DEE.',
          'No aggregate is a verdict about mind, consciousness, general intelligence, or universal advantage.']}
    save(result/'COMPARADORES_CALCULOS.json',values)
    print(json.dumps({'model_trajectories':len(cases),'reserved':values['reserved_model_preparations'],'restores':len(restores)}))


if __name__=='__main__':summarize()
