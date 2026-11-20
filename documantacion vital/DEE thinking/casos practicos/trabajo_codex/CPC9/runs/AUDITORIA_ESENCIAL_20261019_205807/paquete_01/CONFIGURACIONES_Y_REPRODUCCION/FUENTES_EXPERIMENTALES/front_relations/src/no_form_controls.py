"""Environmental/diagnostic matched controls of the no-form alternate route."""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,json,os,sys,time,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from continuar_main_social2 import ContinuedSocialSession,ShiftedInputs,schedule_order
from integracion.relational_pair import physical,move
from dee_thinking import _native as d
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)
def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True);p.add_argument('--config',type=Path,required=True);p.add_argument('--case',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(row for row in cfg['cases']if row['id']==a.case);a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();s=None
    r={'schema':'CPC9.E1.no_form.causal_control.v1','case_id':a.case,'case':case,'configuration_sha256':sha(a.config),'preparations':0,'continuations':int(not case.get('cue_intervention')),'diagnostic_forks':int(bool(case.get('cue_intervention'))),
       'continuity_type':'AUDITOR_MATCHED_COUNTERFACTUAL_NEVER_RETURNED_TO_MAIN','parent':{'path':str(a.parent),'sha256':sha(a.parent)},'RAW_clock_edits_on_MAIN':[],
       'frames':[],'snapshots':[],'meeting_local':[],'status':'RUNNING'}
    r['source_sha256']={str(Path(module.__file__).resolve()):sha(module.__file__)for module in list(sys.modules.values())if getattr(module,'__file__',None)and Path(module.__file__).suffix=='.py'and Path(module.__file__).resolve().is_relative_to(ROOT)}
    try:
        parent=ContinuedSocialSession.load(a.parent)
        if parent.tick!=1371:raise ValueError('Exact sameE1T1371 parent required')
        r['parent'].update(identifier=parent.identifier,physical=physical(parent.world));s=parent
        if case.get('cue_intervention'):
            edits=[];descriptions=[]
            for bank in parent.geometry['late_E2']['banks']:
                site=move(bank['hub'],(0,1,0),1371-1298);pre=parent.observe(site)
                if pre['s_reg']!=5 or pre['direction']!=[0,1,0]:raise ValueError('Declared oldcue not found in bank'+bank['id'])
                edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=0 if case['cue_intervention']=='cut'else int(pre['raw']);edit.label='CPC9_AUDITOR_OLD_B_CUE_'+case['cue_intervention'];edits.append(edit);descriptions.append({'bank':bank['id'],'site':site,'pre':pre,'requested_raw':str(edit.raw),'clock_edit':None})
            s=ContinuedSocialSession(parent.world.diagnostic_fork(edits,True),parent.geometry,parent.state,parent.identifier)
            r['diagnostic_edits']=descriptions;r['parent_unchanged']=physical(parent.world)==r['parent']['physical']
        r['initial_physical']=physical(s.world)
        schedule_order(ShiftedInputs(s,938),tile_order='BA',interval=3,form='omitted',event_a=case['event_a'],event_b=case['event_b'],b_route=case['b_route'])
        for bank in s.geometry['late_E2']['banks']:
            s.input(bank['source_port'],7,1557,'probe','IDENTICAL_RETAINED_E1_ORDER_READER_ALL_BANKS');s.input(bank['probe']['name'],7,1630,'probe','LATER_E2_ONLY_QUERY_NO_NEW_E2TEACHER');s.input(bank['use']['name'],11,1636,origin='E2_RESOURCE_NO_CLEARING_OLD_CARRIERS')
        for tick,key in((1418,'minus_port'),(1485,'plus_port')):
            for name in sorted({row[key]for row in s.geometry['cpc9_life']['count_repeated_readers']}):s.input(name,7,tick,'probe','OLD_COUNT_CONTINUED_ALTERNATION_NO_RETEACHING')
        for tick in(1417,1484):
            for bank in s.geometry['joint_names'].values():s.input(bank['query_port'],17,tick,'probe','OLD_JOINT_NO_RETEACHING_DURING_NEW_ORDER')
        for tick in(1411,1478):s.two_memory.input('quantity.reader',7,tick,True)
        def save():
            path=a.out/('T'+str(s.tick)+'.deetsnap.gz');storage=s.save(path);r['snapshots'].append({'path':path.name,'sha256':sha(path),'bytes':path.stat().st_size,'tick':s.tick,'storage':storage,'physical':physical(s.world)})
        save()
        for tick in(1407,1410,1411,1412,1413,1414,1419,1420,1421,1478,1479,1486,1487,1488,1492,1493,1559,1560,1565,1566,1632,1633,1638,1639):
            s.run_until(tick);r['frames'].append({'tick':tick,'physical':physical(s.world),'view':s.view()})
            if tick in(1413,1414):
                for bank in s.geometry['tiled_order']['surfaces']:
                    q=bank['meeting'];r['meeting_local'].append({'tick':tick,'id':bank['id'],'center':q,'Moore27':[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]})
            if tick in(1493,1566,1639):save()
            r.update(last_complete_tick=s.tick,requests=s.receipts(),new_order_observations=s.state['new_order_observations'],late_E2_observations=s.state['late_E2_observations'],elapsed_seconds=time.monotonic()-start);put(a.out/'MEDICIONES.json',r)
        r.update(status='MEASURED',final_physical=physical(s.world),parent_file_unchanged=sha(a.parent)==r['parent']['sha256'])
    except BaseException as error:r.update(status='TECHNICAL_ERROR',error=repr(error),traceback=traceback.format_exc());raise
    finally:
        if s is not None:r.update(last_complete_tick=s.tick,requests=s.receipts(),new_order_observations=s.state.get('new_order_observations',[]),late_E2_observations=s.state.get('late_E2_observations',[]),elapsed_seconds=time.monotonic()-start)
        r['sources_unchanged_during_execution']=all(sha(path)==digest for path,digest in r['source_sha256'].items());put(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'status':r['status'],'tick':s.tick,'seconds':r['elapsed_seconds']}))
if __name__=='__main__':main()
