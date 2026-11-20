"""Directed reading of existing S07 records; no DEE import, query or tick."""
from pathlib import Path
import json,hashlib,datetime
HERE=Path(__file__).resolve().parent
PROD=HERE.parents[1];WORK=PROD/'trabajo'
DATA=WORK/'fuentes/ESCENAS_04_06_09.json'
R08=PROD.parent/'AUDIOVISUAL_R08/infraestructura/FUENTES_MECANISMOS_S06_S11_R08.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text('utf-8-sig'))
scene=read(DATA)['scenes']['07']; r08=read(R08)['cases']['IC01_SOCIAL']
sources=[];arms={}
def reference(p,pointer=''):
 return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'pointer':pointer}
def nonzero_context(frame):
 out={}
 for port in frame['ports']:
  for v in [port['read']]+port.get('context125',[]):
   if int(v['raw']):
    key=tuple(v['site'])
    if key in out:assert out[key]==v
    out[key]=v
 return list(out.values())
for key,ex in scene['recorded_cases']['arms'].items():
 p=Path(ex['source']['path']); assert sha(p)==ex['source']['sha256'];z=read(p);r=z['result']
 idx,row=next((i,v) for i,v in enumerate(r['external']['rows']) if v['tick']==16619)
 assert row['social_reads']==next(v for v in ex['first_external_rows'] if v['tick']==16619)['social_reads']
 assert r['new_social_progress']['source']==ex['progress']['source']
 frames=[]
 for tick in [16563,16564,16618,16619]:
  f=next(v for v in r['passive_frames'] if v['tick']==tick)
  frames.append({'tick':tick,'original_frame_index':r['passive_frames'].index(f),'observed_nonzero_context':nonzero_context(f),
                 'port_reads':[{'bank':v['bank'],'expected_site_observer_only':v['expected_site'],'unwrapped_observer_only':v['unwrapped'],'read':v['read']} for v in f['ports']]})
 arms[key]={'source':reference(p,'/result'),'life':z['INSTRUMENTO'],'private_input':r['new_plan']['value_private_B'],
            'plan':r['new_plan'],'source16562':r['new_social_progress']['source'],'cuts_after_formed_source':r['new_social_progress']['cuts'],
            'frames':frames,'reading16619':{'pointer':f'/result/external/rows/{idx}/social_reads','social_reads':row['social_reads']},
            'external_command_separate':{'native_command':row['native_command'],'executed_torque':row['executed_torque']}}
 sources.append(reference(p,'/result'))
 # Every R08 sampled observation is directly contained in the primary frame, not generated coordinates.
 if key=='full':
  checked=0
  for sf in r08['passive_sampled_frames']:
   f=next(v for v in r['passive_frames'] if v['tick']==sf['tick'])
   allpoints=[v for port in f['ports'] for v in [port['read']]+port.get('context125',[])]
   for observation in sf['observations']:
    v={k:x for k,x in observation.items() if k!='pointer'}
    assert v in allpoints,(sf['tick'],v);checked+=1
  observation_check={'sampled_ticks':len(r08['passive_sampled_frames']),'checked_observations':checked,'all_match_primary':True}
  # Store actual measurements on the nominal negative branch for exact staged display.
  track=[]
  for f in r['passive_frames']:
   if 16563<=f['tick']<=16619:
    port=next(v for v in f['ports'] if v['bank']==-1)
    track.append({'tick':f['tick'],'observed':port['read'],'observer_unwrapped':port['unwrapped']})
samep=Path(scene['recorded_cases']['arms']['full']['source']['path']).with_name('LATE_SOCIAL_SAME_166.json')
if samep.exists():
 z=read(samep);r=z['result'];idx,row=next((i,v) for i,v in enumerate(r['external']['rows']) if v['tick']==16619)
 arms['same_private18']={'source':reference(samep,'/result'),'life':z['INSTRUMENTO'],
                       'private_input':r['new_plan']['value_private_B'],'source16562':r['new_social_progress']['source'],
                       'reading16619':{'pointer':f'/result/external/rows/{idx}/social_reads','social_reads':row['social_reads']},
                       'external_command_separate':{'native_command':row['native_command'],'executed_torque':row['executed_torque']}}
 sources.append(reference(samep,'/result'))
passivep=Path(r08['passive_source']['path']);assert sha(passivep)==r08['passive_source']['sha256']
result={'schema':'DEE.S07.directed_existing_sources.R01','read_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'new_DEE_ticks':0,'new_experiments':0,'arms':arms,'source_refs':[reference(DATA),reference(R08),reference(passivep)]+sources,
 'passive_observation_validation':observation_check,'observed_negative_branch_samples':track,
 'participants':{'sender':'B, material participant at [21,59,40] at source tick16562; private input45 belongs initially to B.',
                 'receiver':'E1, connected receiving organization with generic acquisition banks and subsequent prepared reader. Not a separately proven full mind.'},
 'permitted_visualizations':[
  'Illustrative schematic: two role-labelled objects, a generic message transfer and its later use, with explicit nonmetric pedagogical motion.',
  'Etapas/Registro: exact observed fields and positions. Display measurement samples without assigning unique physical identity solely from equal RAW.',
  'Matched reader comparison: same camera/site at16619; full has a horizontal negative qualified field, cut has active downward unqualified zero-load field.',
  'Cut timing: B source already formed at16562; SEM4 at association fields is observed16563. No count of missing admission receipts is invented.'
 ],
 'prohibited_inferences':[
  'No claim that private45 was numerically copied; formed message is direction-minus with scalar7.',
  'No claim that the unwrapped nominal observer track proves unique lineage through all encounters.',
  'No claim that no qualified reading equals no matter, zero state, erased memory or global silence.',
  'Do not display external torque0/full vs1/cut as the native social minus code.',
  'No autonomous interlocutor choice, human conversation or general language claimed.'
 ]}
out=HERE/'RECIBO_FUENTES_S07.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'file':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'observation_check':observation_check,
                  'same18':arms.get('same_private18')},ensure_ascii=False,indent=2))
