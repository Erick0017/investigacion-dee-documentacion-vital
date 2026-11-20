from pathlib import Path
import sys,time,json,argparse
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB),str(ROOT/'laboratorio/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01')]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_body as body,ic_external as ext,social_habitat as social
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
cases=[('PROTECTED_INTEGRATED_60','E1_INTEGRADO_PROTEGIDO_01','full','closed','cost','live',True),('PROTECTED_NO_PARTNER_61','IC01_PROTECTED_NO_PARTNER','no_partner','closed','cost','live',True),('PROTECTED_MESSAGE_CUT_62','IC01_PROTECTED_CUT','message_cut','closed','cost','live',True),('PROTECTED_MESSAGE_SHAM_63','IC01_PROTECTED_SHAM','message_sham','closed','cost','live',True),('PROTECTED_ACTION_NULL_64','IC01_PROTECTED_NULL','full','nulled','cost','live',True),('PROTECTED_RETURN_OMIT_65','IC01_PROTECTED_NO_COST','full','closed','omit','live',True),('PROTECTED_OBSERVATION_CLAMP_66','IC01_PROTECTED_CLAMP','full','closed','cost','clamp',True)]
prediction={'fixed_before_cases':'Exact branch from causal protection53 at3691, not a replacement or rewind of MAIN3899. Future A-turn shunts are prepared identically. Native environment is unchanged. Private18 only to B. Motor clock13, both body and social output wires read simultaneously, no cached last output. Social wire at fixed delivery+6(direction) predicts a possible torque only if a native message reaches it. Torque summing is external anatomy, not native composition. Pendulum balance learning is not assumed.', 'protected_default_unchanged':True,'known_limit':'R11 cold-start reserve failed, warm curriculum improved25/32 vs11/32 but not indefinitely stable; do not generalize.'}
for name,life,smode,mode,feedback,sensor,social_enabled in cases:
    if time.monotonic()>deadline:raise TimeoutError('Original deadline')
    out=EV/(name+'.json')
    if out.exists():continue
    s.fork('IC01_CAUSAL_ZERO_DIVERT_53',life,kind='CANDIDATE'if name=='PROTECTED_INTEGRATED_60'else'DIAGNOSTIC_COPY')
    def run(a):
        initial=physical(a.world,occupation=True);protection=body.protect_pending(a,name=name);plan=social.make_plan(a,name,mode=smode,values=(18,));social.schedule(a,plan);h=body.attach(a);base_advance=a.run_until
        def joint_advance(t):
            if a.tick<plan['trials'][-1]['end_tick']:
                until=min(t,plan['trials'][-1]['end_tick']);a.run_until=base_advance
                try:social.advance(a,name,through_tick=until)
                finally:a.run_until=joint_advance
            if a.tick<t:return base_advance(t)
            return a.view()
        a.run_until=joint_advance
        try:external=ext.run_clocked(a,steps=17,mode=mode,feedback=feedback,sensor=sensor,social_output=social_enabled)
        finally:h['detach']()
        social_record=social._state(a)['episodes'][name]
        return{'prediction':prediction,'initial':initial,'prepared_protection':protection,'native_frames':h['frames'],'social':social_record,'external':external,'body_requests':[body.ic.receipts(a,rr)for rr in body.get(a)['requests']],'final':physical(a.world,occupation=True)}
    result=s.mutate(life,'IC01_PROTECTED_SOCIAL_EXTERNAL_IN_ONE_CONTINUATION',run,{'prediction':prediction,'variant':{'social':smode,'mode':mode,'feedback':feedback,'sensor':sensor},'sources':{p.name:digest_file(p)for p in[LAB/'ic_native_core.py',LAB/'ic_body.py',LAB/'ic_external.py',Path(social.__file__),Path(__file__)]}});atomic_json(out,result);print(name+' '+str(result['INSTRUMENTO']['tick']),flush=True)
