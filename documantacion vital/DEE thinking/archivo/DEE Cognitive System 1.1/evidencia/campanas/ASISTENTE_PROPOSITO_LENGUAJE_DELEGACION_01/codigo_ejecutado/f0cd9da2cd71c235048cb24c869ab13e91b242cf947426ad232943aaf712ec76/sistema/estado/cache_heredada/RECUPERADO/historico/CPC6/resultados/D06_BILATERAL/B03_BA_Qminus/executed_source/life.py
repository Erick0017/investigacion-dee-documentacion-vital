"""Executed longitudinal U0 experiments, with evaluator kept outside MAIN."""
import argparse,json,time,shutil
from pathlib import Path
from common import ROOT,identity,put,sha,record,receipt,digest,operational,local_context
from integrated import create,Session
import order_memory,action_feedback,language,consolidation,curriculum
from action_feedback_access import deduplicate_requests

def summarize(rows,g):
    at={r['tick']:r for r in rows};out={}
    for stage,field,directions in (
        ('selection','actions',((0,0,1),(-1,-1,1))),
        ('information','information',((-1,-1,0),(1,-1,0))),
        ('late_read','late_queries',((-1,0,1),(1,0,1)))):
        row=at.get(g['ticks'][stage]);out[stage]=[]
        if row:
            for name,r in row['adapter'][field].items():
                if r['active'] and r['semantic']==1 and tuple(r['direction']) in directions:
                    out[stage].append({'location':name,'physical':r})
    return out

def run(case,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();engine=identity()
    s=curriculum.new_individual(backend=case.get('backend','LAZY'),bilateral=case.get('bilateral',False)) if case.get('longitudinal') else create(adapter=case.get('adapter',True),backend=case.get('backend','LAZY'),
             consolidation=case.get('consolidation',False),consolidation_phase=case.get('consolidation_phase',171))
    w=s.world;g=s.geometry['adapter'];rows=[];snaps=[];windows=[];forecasts=[]
    bundle=out/'executed_source';bundle.mkdir()
    code_hashes={}
    for name in ('life.py','integrated.py','common.py','order_memory.py','action_feedback.py','action_feedback_access.py','language.py','consolidation.py','curriculum.py'):
        source=Path(__file__).parent/name;shutil.copyfile(source,bundle/name);code_hashes[name]=sha(source)
    put(out/'CONFIG.json',{'schema':'CPC6.U0.config.v1','case':case,'source_sha256':sha(__file__),'executed_source':code_hashes,
        'preparation':s.geometry,'participant_information':'Only admitted physical events and native fields, no target or evaluator map.',
        'frozen_decoder':'Semantic1, active state, exact direction at all predeclared candidate sites; silence/rejection/other direction kept distinct.',
        'criterion':'Forecast at5 before actual observation request11; native comparison15 -> policy19 -> action20 -> source information23 -> physical later query33.',
        'resource_note':'Separate source exposures for each candidate lane; Q-positive has two contributors. Prepared finite controller is not generic optimal policy learning.'})
    def snap(label):
        p=out/(label+'.deetsnap');a=s.save(p);a['path']=p.name;snaps.append(a);put(out/'SNAPSHOTS.json',snaps)
    if case.get('history','AB')!='NONE':s.stimulate(order_memory.experience(case.get('history','AB'),load=case.get('event_load',3),gap=case.get('gap',1)))
    s.stimulate([{'port':'order.read','payload':7,'tick':2,'kind':'probe','origin':'COMMON_READER'}])
    alias_groups=[]
    def stimulate(requests):
        if case.get('access')=='deduplicated':
            admitted=deduplicate_requests(w,requests);alias_groups.append(admitted);s.stimulate(admitted['requests'])
        else:s.stimulate(requests)
    if g:
        s.stimulate(action_feedback.source_protocol(g,case.get('source_values',{'P':1,'Q':-1}),mode=case.get('source_mode','paired'),omit=case.get('omit_sources',[])))
        if not case.get('late_omitted'):stimulate(action_feedback.query_protocol(g,case.get('late_payload',7)))
    if case.get('consolidation') and case.get('consolidation_query_tick') is not None:
        s.stimulate(consolidation.query(case['consolidation_query_tick']))
    if case.get('longitudinal'):
        s.stimulate(consolidation.query(case.get('consolidation_query_tick',94),bilateral=case.get('bilateral',False)))
        for item in case.get('renewed_queries',[]):
            s.stimulate(curriculum.query(s,item['memory'],item['tick'],item['payload']))
    snap('INITIAL_T0')
    for tick in range(case.get('horizon',40)+1):
        s.advance_to(tick)
        row={'tick':tick,'body':order_memory.observations(w,s.geometry['body'])}
        if g:row['adapter']=action_feedback.capture(w,g)
        if s.geometry.get('consolidation'):row['consolidation']=consolidation.capture(w,s.geometry['consolidation'])
        if s.geometry.get('renewed_interfaces'):row['renewed']=curriculum.capture(s)
        if s.geometry.get('language') and case.get('language_mode'):
            row['language']=language.capture(w,s.geometry['language'])
            row['decoded_language']=language.decode(row['language'])
        rows.append(row)
        if tick==5:
            forecasts.append({'tick_emission':5,'target_tick':15,'horizon_ticks':10,
                'information_available':'Order events0/1, common reader2 and current source experiences0; actual consequence not yet requested.',
                'physical_emission':row['body']['emission'],'provenance':'ENTE'})
            put(out/'PREDICCIONES.json',forecasts)
            if g and not case.get('actual_omitted'):s.stimulate(action_feedback.actual_protocol(g,case.get('actual',-1)))
        if tick==34 and case.get('language_mode'):
            # Native experience and use precede introduction of the opaque name.
            stimulate(language.teaching(s.geometry['language'],mode=case['language_mode']))
            stimulate(language.query(s.geometry['language'],payload=case.get('language_query_load',7)))
        if tick in (4,5,14,15,18,19,20,22,23,32,33):
            windows.append({'tick':tick,'body':local_context(w,s.geometry['body']['center']),
                'comparison':{k:local_context(w,q) for k,q in g['comparison_hubs'].items()} if g else {}})
        if s.geometry.get('consolidation') and tick in (68,69,70,88,89,90,91,93,94,95,96,97,98,160,161,162,163,164):
            cg=s.geometry['consolidation']
            windows.append({'tick':tick,'new_memory':local_context(w,cg['center']),
                'left_new_memory':local_context(w,cg['left']['center']) if 'left' in cg else [],
                'original':local_context(w,s.geometry['body']['center'])})
        if tick in case.get('checkpoints',[5,14,23,33,40]):snap('T'+str(tick))
        if tick in (5,15,19,20,23,33,40,43,53):put(out/'INCREMENTAL.json',{'last_complete_tick':tick,'rows':rows,'requests':s.receipts()})
    result={'schema':'CPC6.U0.life.v1','case':case,'engine':engine,'geometry':s.geometry,
       'rows':rows,'requests':s.receipts(),'predictions':forecasts,'local_windows':windows,'snapshots':snaps,
       'summary':summarize(rows,g) if g else {},'final_physical':digest(w),'final_operative':operational(w),
       'identity':'U0' if case.get('central') else case['id'],'parent':None,'preparations':1,'alias_admission':alias_groups,
       'host_RAW_clock_edits_after_T0':[],'evaluator_only':{'history':case.get('history','AB'),'actual':case.get('actual')},
       'coverage':'Fixed points and local windows; full state at listed boundaries. No unique genealogy inferred across uncovered intervals.',
       'elapsed_seconds':time.monotonic()-start}
    put(out/'MEASUREMENTS.json',result)
    print(json.dumps({'id':case['id'],'delta5':rows[5]['body']['delta'],'forecast':rows[5]['body']['emission']['direction'],
        'summary':result['summary'],'seconds':result['elapsed_seconds']}),flush=True)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    cases=json.loads(a.config.read_text(encoding='utf-8'))['cases'];index=[];a.out.mkdir(parents=True,exist_ok=True)
    for case in cases:
        target=a.out/case['id']
        if (target/'MEASUREMENTS.json').exists():r=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf-8'))
        else:r=run(case,target)
        index.append({'id':case['id'],'summary':r['summary'],'evidence':str((target/'MEASUREMENTS.json').relative_to(ROOT))})
        put(a.out/'INDEX.json',index)
if __name__=='__main__':main()
