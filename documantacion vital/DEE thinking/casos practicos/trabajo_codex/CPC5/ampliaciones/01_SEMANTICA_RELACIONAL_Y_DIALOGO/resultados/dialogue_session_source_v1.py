"""External auditor for finite dialogue evidence, not part of its answers.

Summary arithmetic reads finished trajectories. Context replay loads retained
complete checkpoints and records missing local neighborhoods with v27; it does
not change or resume the operational participant MAIN.
"""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from dialogue import DialogueSession
from common import ROOT, put, sha, digest, operational, record, local_context


def summarize(out):
    rows=[]
    for path in sorted((ROOT/'resultados').glob('dialogue*/**/MEASUREMENTS.json')):
        r=json.loads(path.read_text(encoding='utf-8'));g=r['geometry'];case=r['case']
        banktick=g.get('bank_tick',31)
        banks={k:v for k,v in next(t for t in r['trace'] if t['tick']==banktick)['samples'].items() if k.startswith('bank.')}
        querytick=g.get('name_probe_tick')
        nameframe=next((t for t in r['trace'] if t['tick']==querytick),{'samples':{}})
        names={k:v for k,v in nameframe['samples'].items() if k.startswith('form_probe.')}
        # Older same-hub reader was explicitly retained as a confound/control.
        if not names:names={k:v for k,v in nameframe['samples'].items() if k.startswith('form.')}
        matched=[{'port':k,'class_direction_y':v['direction'][1],'physical':v}
                 for k,v in names.items() if v['active'] and v['direction'][0]==-1 and v['direction'][1] in (-1,1) and v['direction'][2]==1]
        backup={k:v for k,v in r['trace'][-1]['samples'].items() if k.endswith('.backup')}
        requests=[{**x,'receipt':next(a for a in r['receipts'] if a['id']==x['id'])}
                  for x in r['inputs'] if x['origin'] in ('HUMAN_INDUCED_PHYSICAL_REQUEST','OPAQUE_FORM_QUERY','POST_COMMUNICATION_RETENTION_QUERY_WITHOUT_REPORT')]
        rows.append({'case_id':case['id'],'source':str(path.relative_to(ROOT)),'sha256':sha(path),
                     'code_sha256':r['code_sha256'],'modality':r['modality'],'case':case,
                     'native_encounter_observations':r['messages'],'bank_tick':banktick,'banks':banks,
                     'form_probe_tick':querytick,'form_readouts':names,'directional_form_candidates':matched,
                     'retention_final_tick':r['trace'][-1]['tick'],'backup_readouts':backup,
                     'queries_and_receipts':requests,'diagnostic_edits':r['diagnostic_edits'],
                     'resources':r['resources'],'elapsed_seconds':r['elapsed_seconds']})
    output={'schema':'CPC5.extension.dialogue.external_analysis.v1','cases':rows,'primary_records':len(rows),
            'calculation':'All loads/directions/receipts copied from fixed observed times; class candidate uses active && dx=-1 && dy in{-1,+1} && dz=1. It is an operational form-response descriptor, not a full NSM meaning score.',
            'information_boundary':'This module is an external auditor. The participant never imports it, reads its outputs, or uses target classes.',
            'coverage':'Finite designed routes with observed encounters. No autonomous interlocutor selection, universal semantic mastery, or ancestry inferred by proximity.'}
    put(out,output);print(json.dumps({'primary_records':len(rows),'output':str(out)}));return output


def contexts(measurement,out):
    measurement=Path(measurement);out=Path(out);out.mkdir(parents=True,exist_ok=False)
    result=json.loads(measurement.read_text(encoding='utf-8'));g=result['geometry'];rows=[];checks=[]
    banktick=g['bank_tick']; learntick=g['name_learning_tick'];querytick=g['name_probe_tick']
    intervals=[('bank',g['stages'][-1]['time'],banktick-1,banktick,g['banks']),
               ('name_acquisition',learntick-1,learntick-1,learntick,g['name_hubs']),
               ('form_query',learntick,querytick-1,querytick,g['name_query_targets'])]
    for label,base,pre,post,targets in intervals:
        initial=measurement.parent/f'T{base}.deetsnap';session=DialogueSession.load(initial)
        session.run_until(pre)
        for name,q in targets.items():rows.append({'kind':label,'phase':'pre','tick':pre,'target_name':name,'target':q,
                                                   'Moore26_plus_center':local_context(session.world,q)})
        session.run_until(post)
        for name,q in targets.items():rows.append({'kind':label,'phase':'post','tick':post,'target_name':name,'target':q,
                                                    'Moore26_plus_center':local_context(session.world,q)})
        golden=DialogueSession.load(measurement.parent/f'T{post}.deetsnap')
        check={'kind':label,'base':initial.name,'pre_tick':pre,'post_tick':post,
               'physical_equal_full_arrays':digest(session.world)==digest(golden.world),
               'operative_equal':operational(session.world)==operational(golden.world),
               'golden_sha256':sha(measurement.parent/f'T{post}.deetsnap'),'replay_final':digest(session.world)}
        if not check['physical_equal_full_arrays'] or not check['operative_equal']:raise AssertionError('Context replay changed saved trajectory')
        checks.append(check);put(out/'INCREMENTAL.json',{'local_windows':rows,'replay_checks':checks})
    proof={'schema':'CPC5.extension.dialogue.context_replay.v1','source_measurement':str(measurement.relative_to(ROOT)),
           'source_sha256':sha(measurement),'auditor_code_sha256':sha(__file__),'modality':'PASSIVE_OBSERVATION + INTACT_DIRECTED_REPLAY',
           'primary_new_preparations':0,'local_windows':rows,'replay_checks':checks,
           'scope':'Technical directed reconstruction of an already recorded trajectory; not another scientific replicate and never returned to MAIN.'}
    put(out/'CONTEXT_REPLAY.json',proof);return proof


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['summary','contexts']);p.add_argument('--out',type=Path,required=True);p.add_argument('--measurement',type=Path);a=p.parse_args()
    if a.command=='summary':summarize(a.out)
    else:contexts(a.measurement,a.out)


if __name__=='__main__':main()
