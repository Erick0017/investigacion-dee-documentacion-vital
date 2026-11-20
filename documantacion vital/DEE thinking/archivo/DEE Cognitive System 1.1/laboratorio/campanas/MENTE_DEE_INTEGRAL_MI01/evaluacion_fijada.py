"""Frozen MI01 evaluation: curriculum, not an answer/repair controller.

Only existing manager operations. All nine physical opportunities and both
contents are fixed before use; the host never inspects success to choose an
access/action. The three sequential windows continue the SAME MAIN world.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from datetime import datetime,timezone

life='E1_MI01_MAIN';name='MI01_EVALUACION_FIJADA'
options={'builder':'direct_failure','name':name,'availability':[-1,-1,1,1,1,-1,1,-1,1],'private_values':[17,58,26,54,9,66,18,57,30],'mode':'intact','actor_return':False,'include_initial_failure':True,'b_context':'fixed43'}

def seal():
    p=E/'SELLO_EVALUACION_FIJADA.json'
    if p.exists():raise FileExistsError('Never reseal after outcomes')
    current=Store().record(life);files=[S/'gestionar.py',*sorted((S/'capacidades/mente_integral_mi01').glob('*.py')),S/'capacidades/integracion_situada_01/ic_native_core.py',S/'capacidades/integracion_situada_01/ic_external.py',S/'capacidades/conductos_acceso_aa01.py']
    code=[{'path':str(x.relative_to(R)),'sha256':sha(x)}for x in files]
    now=datetime.now(timezone.utc).isoformat()
    atomic_json(p,{'sealed_utc':now,'sealed_monotonic':time.monotonic(),'before_halfway':time.monotonic()<budget()['construction_freeze_latest_monotonic'],'candidate':life,'selected_snapshot':current['snapshot'],'selected_sha256':current['snapshot_sha256'],'selected_tick':current['physical']['tick'],'options':options,'physical_code':code,
      'selection_reason':'Preserve MAIN own+Y145 at24752. Late retraining345/346 did not restore B access. Local P0 B frame is useful historically340/344 and selected as explicit preparation, not proved MAIN repair. Short failure-only return avoids asserting the unsuccessful full actor loop330/331. No result from350-352 is imported or used to modify this frozen selection.',
      'sequences':[{'id':'RESERVA_1','steps':16,'mode':'closed','feedback':'cost','native_opportunities':[0,1,2],'changes':'Initial unavailable contacts, new private17/58/26 and native information requests.'},{'id':'RESERVA_2','steps':15,'mode':'delay1','feedback':'cost','native_opportunities':[3,4,5],'changes':'One external step sensory lag, fixed eight peripheral events, new private54/9/66.'},{'id':'RESERVA_3','steps':16,'mode':'closed','feedback':'omit','native_opportunities':[6,7,8],'changes':'No raw external cost supply; native B and sources remain on their predeclared schedule. New private18/57/30 and return to prior availability contexts.'}],
      'frozen_codec':'native_body_roles: positive-load state1sem1XY+ ->torque+2, XY- ->native query and externalneutral0; absent/invalid externalneutral0. No per-answer readout switching.',
      'numeric_criteria':{'native_action':'state1 semantic1 direction(1,1,0), s_reg>0, plus measured contact product(availability,1,0) with s_reg>0','native_question':'state1 semantic1 direction(1,-1,0), s_reg>0; arrival and reply counted independently','useful_action':'Actual positive-load act and successful positive native contact when availability+1. All opportunities, including silence/invalid output, remain in denominator. Unavailable act costs1, available successful act earns1; query/silence0. This audit reward never enters DEE.','retained_codes':'Three inherited exact directional codes and the acquired positive145 are read passively at each external motor tick; a consumed/diverted bank is not assumed to retain access.','strong_integration':'At least two post-experience useful acts separated by an environmental change, causal native query/reply/use, retained old function during a new acquisition, and relational-composition use in same fixed organization. This is a proposed domain criterion, not a general-mind test or automatic verdict.','external':'Report every step/action/reward/neutral; actual torque is not competence. Compare nulled actions in a separate fork, never reference-control MAIN.'},
      'uncovered_limit':'The contact/order composer was consumed during MAIN314. No reset or hidden repeat is allowed. Final reusable relational composition may therefore remain unproved. Phase29 is fixed; phase31/33 construction tests failed. Non67 temporal contrasts/peripheral offsets do not prove phase invariance.',
      'no_repair':'After this seal no physical code, anatomy, decoder, timeline or assistance selected by outcomes. Pending native learning remains active. External windows and finite supply changes are fixed environmental protocol, not learned initiative.'})
    print('SEALED '+now,flush=True)

def verify():
    spec=json.loads((E/'SELLO_EVALUACION_FIJADA.json').read_bytes())
    for x in spec['physical_code']:
        if sha(R/x['path'])!=x['sha256']:raise AssertionError('Frozen physical code changed: '+x['path'])
    return spec

phase=sys.argv[1]
if phase=='sellar':seal()
elif phase=='preparar':
    verify();v=command('MI01_400_MAIN_PREPARACION_FIJADA',['mi01-experiencia','--vida',life,'--tipo','habitat-contextual','--parametros',json.dumps(options)])
    body=v['result'];q=body['plans'][3]['query_tick'];command('MI01_401_MAIN_ENTORNO_FIJADO',['mi01-experiencia','--vida',life,'--tipo','entorno-fijado','--parametros',json.dumps({'name':name+'.noise','start_tick':q})])
    command('MI01_402_MAIN_ESTADO_PRE_RESERVAS',['mi01-estado','--vida',life])
elif phase in('1','2','3'):
    spec=verify();z=spec['sequences'][int(phase)-1];argv=['mi01-externo','--vida',life,'--pasos',str(z['steps']),'--modo',z['mode'],'--retorno',z['feedback'],'--codec-motor','native_body_roles','--habitat',name]
    if phase=='1':argv.append('--transicion')
    command('MI01_41'+phase+'_MAIN_'+z['id'],argv,timeout=1500)
    command('MI01_42'+phase+'_MAIN_ESTADO',['mi01-estado','--vida',life])
else:raise ValueError('Explicit finite evaluation phase required')
