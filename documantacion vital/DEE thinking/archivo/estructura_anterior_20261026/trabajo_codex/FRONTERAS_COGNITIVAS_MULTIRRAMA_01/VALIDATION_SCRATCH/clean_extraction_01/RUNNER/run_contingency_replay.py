"""Post-emission native contrasts and a declared external environmental replay control."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as dt
from observations import *
from apparatus import edited
from run_multibranch import Case,append_ledger,utc
from branches import basal_intervention, response

def main():
    root=Path(sys.argv[1]);configpath=root/'CAMPAIGN_CONFIG.json'
    config=json.loads(configpath.read_text(encoding='utf-8'))
    source=root/'CHECKPOINTS/L03/contingent_intact/T8.deetsnap'
    full13=root/'CHECKPOINTS/L03/contingent_intact/T13.deetsnap'
    full=dt.Runtime.load_snapshot(str(full13));env=(20,20,20);action=(20,20,15)
    replayraw=full.observe(c(env)).raw
    frozen={'frozen_utc':utc(),'parent_t8':str(source.relative_to(root)),'parent_sha256':sha(source),
            'reference_t13':str(full13.relative_to(root)),'reference_sha256':sha(full13),
            'cut_site':action,'copy_environment_site':env,'copy_raw':replayraw,'copy_clock':False,
            'horizon_relative':170,'modality':'DIAGNOSTIC / externally replayed control; not a native treatment',
            'purpose':'Does replacing one native environmental product recover measured return/reader effects after emitted action was removed?'}
    if 'L03_replay_control_lock' not in config:
        config['L03_replay_control_lock']=frozen
        for j,origin in enumerate(((22,20,24),(28,26,18))):
            for cut in (None,'action'):
                config['cases'].append({'branch':'L03','case':f'reserve{j}_'+('intact' if cut is None else 'late_action_cut'),
                                       'kind':'basal_intervention','role':'treatment' if cut is None else 'control',
                                       'level':1,'configuration':0,'frozen_utc':utc(),
                                       'spec':{'origin':origin,'cut':cut,'cut_tick':8,'horizon':26}})
        dump(configpath,config)
    for arm in ('intact_followup','action_cut_followup','action_cut_open_replay','action_cut_identical_copy'):
        d=root/'BRANCHES/L03'/arm
        if (d/'MEASUREMENTS.json').exists():
            m=json.loads((d/'MEASUREMENTS.json').read_text(encoding='utf-8'))
            assert all(sha(root/x['path'])==x['sha256'] for x in m['checkpoints']);print('SKIP_VERIFIED',arm);continue
        spec={'branch':'L03','case':arm,'kind':'late_contingency_replay','role':'control' if arm!='intact_followup' else 'treatment',
              'level':0,'configuration':1,'spec':{'arm':arm,**frozen}}
        ctx=Case(root,spec);rt=ctx.track(dt.Runtime.load_snapshot(str(source)));ctx.recipe(frozen);ctx.cp(rt,'AFTER_NATIVE_ACTION')
        edits=[]
        if arm!='intact_followup':rt,e=edited(rt,action,0,label='late_action_remove');ctx.track(rt);edits.append(e)
        ctx.to(rt,45);ctx.cp(rt,'PRE_ENV_REPLAY')
        equalbody={name:response(rt,q)==response(full,q) for name,q in [('A',(14,15,15)),('B',(16,15,15))]}
        if arm in ('action_cut_open_replay','action_cut_identical_copy'):
            raw=replayraw if arm=='action_cut_open_replay' else rt.observe(c(env)).raw
            rt,e=edited(rt,env,raw,label='external_environmental_replay' if arm=='action_cut_open_replay' else 'identical_copy_sham')
            ctx.track(rt);edits.append(e);ctx.cp(rt,'POST_ENV_REPLAY')
        sites={'A':(14,15,15),'B':(16,15,15),'comparator':(15,15,15),'action':action,'environment':env,
               'return':(19,19,19),'reader':(15,16,15)}
        rows=[]
        for rel in (13,14,17,18,20,26,50,100,131,132,170):
            ctx.to(rt,32+rel)
            rows.append({'relative_tick':rel,'sites':{k:response(rt,q) for k,q in sites.items()},
                         'gateA':gate(rt,(14,15,15)),'gateB':gate(rt,(16,15,15))})
        ctx.cp(rt,'FINAL');ctx.data('REPLAY_TRACE',rows);ctx.data('DIAGNOSTIC_WRITES',edits)
        result=ctx.finish({'context_rows':rows,'phi':[[rows[-1]['sites'][k]['s_reg'],rows[-1]['sites'][k]['direction']] for k in ('A','B','comparator','reader')],
                           'interventions':edits,'matched_A_B_before_replay':equalbody,'host_writes_after_t0_main':ctx.effective_writes(rt,32),
                           'external_diagnostic_writes':len(edits),'modality':frozen['modality'],
                           'pending':'Conditional environmental replay does not establish acquired discrimination of action contingency.'})
        append_ledger(root,{'case':'L03/'+arm,'status':'MEASURED','level':0,'result_sha256':sha(d/'MEASUREMENTS.json')})
        print('MEASURED',arm,'ticks',result['runtime_ticks_executed'],flush=True)

if __name__=='__main__':main()
