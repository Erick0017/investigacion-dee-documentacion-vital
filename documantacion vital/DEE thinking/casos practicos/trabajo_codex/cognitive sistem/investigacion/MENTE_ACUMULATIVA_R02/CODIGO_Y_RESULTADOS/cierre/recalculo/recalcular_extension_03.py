"""MA02 fifth association extension: archived inputs and fixed ten-gate RAW reader."""
import argparse
import importlib.util
import json
from pathlib import Path
spec=importlib.util.spec_from_file_location('common_archived',Path(__file__).with_name('recalcular_entrada_comun.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
V={'alfa':(1,0,0),'beta':(0,1,0),'gamma':(1,1,0),'delta':(-1,1,0),'epsilon':(1,-1,0)}
def site(v,k,z=0):return tuple((33+k*v[j]+(z if j==2 else 0))%67 for j in range(3))
GATES=[site(v,4,s)for v in V.values()for s in(-1,1)]
def fp(x):return{k:x[k]for k in('N','tick','RAW_sha256','clocks_sha256')}


def calculate(root):
    a=c.Audit(root);checks=[]
    def check(name,condition):
        checks.append({'check':name,'observed':bool(condition)})
        if not condition:a.issues.append({'check':name})
    names=['24_FORK_MAIN_5','25_PREPARAR_EPSILON_MAIN_5','26_FORK_EPSILON_OPPOSITE','27_FORK_EPSILON_NOEVENT',
           '28_ADQUIRIR_EPSILON_MAIN_5','29_ADQUIRIR_EPSILON_OPPOSITE','30_EDAD_NOEVENT',
           '31_PANEL_MAIN_5','32_PANEL_OPPOSITE','33_PANEL_NOEVENT','34_GUARDAR_MAIN_5','35_REABRIR_MAIN_5']
    src={name:a.load(name+'.json.gz')for name in names};R={name:x['result']for name,x in src.items()}
    fences=[]
    for name,x in src.items():
        check(name+': successful existing command',x['returncode']==0 and not x['timed_out'])
        check(name+': JSON stdout matches record',json.loads(x['stdout'])==x['result'])
        fence=x['result'].get('INSTRUMENTO_FENCE')
        if fence:
            fences.append({'case':name,'denied':fence['denied'],'external_calls':len(fence['exact_environment_processes'])})
            check(name+': no forbidden operations or external workers',fence['denied']==[] and fence['exact_environment_processes']==[])
    prep=R['25_PREPARAR_EPSILON_MAIN_5']['result'];placements=[]
    for row in prep['rows']:
        for key in('pre','post'):a.check_observation(row[key],'preparation:'+key)
        check('preparation does not overwrite nonzero RAW '+str(row['site']),int(row['pre']['raw'])==0)
        check('prepared SEM4 state0 rather than learned content '+str(row['site']),int(row['post']['raw'])==4<<60)
        placements.append(row)
    check('six legal preparation inputs applied',len(prep['requests'])==6 and all(q['state']==0 and q['semantic']==4 and q['value']==0 and q['direction']==[0,0,0] and q['receipt']['status']=='applied'for q in prep['requests']))
    postprep=fp(R['25_PREPARAR_EPSILON_MAIN_5']['physical'])
    check('opposite/noevent forks preserve postpreparation native prefix',postprep==fp(R['26_FORK_EPSILON_OPPOSITE']['physical'])==fp(R['27_FORK_EPSILON_NOEVENT']['physical']))
    teachings=[]
    for name in('28_ADQUIRIR_EPSILON_MAIN_5','29_ADQUIRIR_EPSILON_OPPOSITE'):
        q=R[name]['result']['rows'][0];a.check_observation(q['hub'],name+':hub')
        check(name+': teaching starts from exact postpreparation cut',postprep==fp(q['before']))
        check(name+': observed acquired sign equals declared teacher',c.pure_z(q['hub'])==q['teaching_signal'])
        check(name+': both teaching inputs applied',len(q['requests'])==2 and all(z['receipt']['status']=='applied'for z in q['requests']))
        teachings.append({'case':name,'context':q['context_signal'],'input_tick':q['input_tick'],'teacher_sign':q['teaching_signal'],
                          'hub':q['hub'],'receipts':c.receipt_summary(q['requests'])})
    sessions=[]
    for name,epsilon in[('31_PANEL_MAIN_5',-1),('32_PANEL_OPPOSITE',1),('33_PANEL_NOEVENT',None),('35_REABRIR_MAIN_5',-1)]:
        rows=R[name]['result']['rows'];out=[];rs=[]
        for q in rows:
            for o in q['reader']['panel']:a.check_observation(o,name+':panel')
            frame_by_tick={f['tick']:f for f in q['frames']}
            for f in q['frames']:
                for o in f['sites']:a.check_observation(o,name+':frame'+str(f['tick']))
            decoded=c.decode(q['reader']['panel'],GATES,{site(v,4,s):s for v in V.values()for s in(-1,1)})
            check(name+': ten fixed gates decoder@'+str(q['input_tick']),decoded['decoded_sign']==q['reader']['formed_native_command'])
            check(name+': fixed q+4 window@'+str(q['input_tick']),q['read_tick']==q['input_tick']+4 and all(o['tick']==q['read_tick']for o in q['reader']['panel']))
            check(name+': simultaneous frames agree@'+str(q['input_tick']),all(next(o for o in frame_by_tick[q['read_tick']]['sites']if o['site']==p['site'])==p for p in q['reader']['panel']))
            expected={'alfa':-1,'beta':1,'gamma':1,'delta':-1,'epsilon':epsilon}[q['context_signal']]
            cue=[z for z in q['requests']if z['channel'].startswith('common.token.')];rs.extend(q['requests'])
            out.append({'context_for_scoring_only':q['context_signal'],'input_tick':q['input_tick'],**decoded,
                'historical_sign_for_auditor_only':expected,'correct_acquired_recall':expected is not None and decoded['decoded_sign']==expected,
                'all_receipts':c.receipt_summary(q['requests']),'cue_receipts':c.receipt_summary(cue)})
        sessions.append({'case':name,'rows':out,'requested_queries':len(out),'responded':sum(q['decoded_sign']is not None for q in out),
                         'correct_acquired_recall':sum(q['correct_acquired_recall']for q in out),'abstention_or_ambiguity':sum(q['decoded_sign']is None for q in out),
                         'receipts':c.receipt_summary(rs),'initial_before':rows[0]['before'],'final_physical':fp(R[name]['physical'])})
    check('teaching and noevent matched endpoint tick3688',R['28_ADQUIRIR_EPSILON_MAIN_5']['physical']['tick']==R['29_ADQUIRIR_EPSILON_OPPOSITE']['physical']['tick']==R['30_EDAD_NOEVENT']['physical']['tick']==3688)
    for name,prev in [('31_PANEL_MAIN_5','28_ADQUIRIR_EPSILON_MAIN_5'),('32_PANEL_OPPOSITE','29_ADQUIRIR_EPSILON_OPPOSITE'),('33_PANEL_NOEVENT','30_EDAD_NOEVENT'),('35_REABRIR_MAIN_5','34_GUARDAR_MAIN_5')]:
        check(name+': continues preceding full life physical cut',fp(R[name]['result']['rows'][0]['before'])==fp(R[prev]['physical']))
    check('explicit save preserves final native cut',fp(R['31_PANEL_MAIN_5']['physical'])==fp(R['34_GUARDAR_MAIN_5']['physical']))
    m,o=sessions[:2]
    check('only epsilon responses invert in matched sign histories',all((x['decoded_sign']==-y['decoded_sign'])if x['context_for_scoring_only']=='epsilon'else(x['decoded_sign']==y['decoded_sign'])for x,y in zip(m['rows'],o['rows'])))
    return {'schema':'DEE.MA02.archived_extension03.v1','new_dee_ticks':0,'sources':a.sources,'checks':checks,'fences':fences,
            'preparation':{'external_P0_only':True,'rows':placements,'receipts':c.receipt_summary(prep['requests'])},
            'teaching':teachings,'sessions':sessions,'observations_checked':a.observations,'issues':a.issues,
            'scope_and_limits':[
                'MA02_MAIN_5 is a full fork of real MAIN3625. Six prepared passive terminators are added through legal native interfaces; no world resize, learned fields transplant or clock edit.',
                'The fixed ten-gate decoder is frozen for all three histories, including the first four old-context queries. It receives no requested token or expected sign.',
                'Direction/route and type of context remain prepared P0. This is a fifth acquired sign association, not five semantic primitives or a learned strategy for allocating new supports.',
                'Main/opposite each have same teaching count and dose with different acquired epsilon sign. Noevent is age-matched, not dose-matched teaching.',
                'Noevent first uses all four old contents, then its unknown epsilon has no valid response; five later common-input cues are rejected. Do not call every old-content miss physical erasure.',
                'Operational metadata enables the context interface and counts episodes/jobs; the sign content is physically decoded, not supplied by those metadata fields.',
                'Saving and next-process five-query continuation are archived real operations. This calculation repeats only their evidence arithmetic, not physical acquisition.' ]}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    q=p.parse_args();x=calculate(q.evidencia);q.salida.parent.mkdir(parents=True,exist_ok=True)
    q.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),'observations_checked':x['observations_checked'],
        'sessions':[{'case':a['case'],'requested':a['requested_queries'],'responded':a['responded'],'correct':a['correct_acquired_recall'],'receipts':a['receipts']}for a in x['sessions']]},ensure_ascii=False))
    return 1 if x['issues']else 0

if __name__=='__main__':raise SystemExit(main())
