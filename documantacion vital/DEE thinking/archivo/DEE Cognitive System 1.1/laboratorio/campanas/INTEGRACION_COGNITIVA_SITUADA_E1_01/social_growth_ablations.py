from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
sys.path[:0]=[str(ROOT/'sistema'),str(LAB),str(ROOT/'laboratorio/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01')]
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from app.process_control import protect_current
import ic_body as body,social_habitat as social
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
expected=json.loads((EV/'MAIN_COMMITTED_BODY_38.json').read_text())['INSTRUMENTO']['snapshot_sha256'];parent=next(p for p in(s.root/'estado/checkpoints').glob('E1_INTEGRADO_MAIN.T3312.*')if digest_file(p)==expected)
cases=[('SOCIAL_SOURCE_ONLY_79',45,('PRIVATE',)),('SOCIAL_SOURCE_RECORD_80',45,('PRIVATE','RECORD')),('SOCIAL_SOURCE_RECORD_READ_81',45,('PRIVATE','RECORD','READER')),('SOCIAL_SOURCE_RECORD_USE_82',45,('PRIVATE','RECORD','ACTION')),('SOCIAL_FULL_POSITIVE_83',18,('PRIVATE','RECORD','READER','ACTION')),('SOCIAL_NO_B_RESOURCES_84',45,('RECORD','READER','ACTION'))]
for name,value,groups in cases:
    if time.monotonic()>deadline:raise TimeoutError('Original deadline')
    out=EV/(name+'.json');life='IC01_'+name
    if out.exists():continue
    s.fork('E1_INTEGRADO_MAIN',life,kind='DIAGNOSTIC_COPY',checkpoint=str(parent.relative_to(s.root)))
    def run(a):
        initial=physical(a.world,occupation=True);plan=social.make_plan(a,name,mode='full',values=(value,));rr=[]
        for e in plan['trials'][0]['inputs']:
            role=e['role'];g='PRIVATE'if e['port'].startswith('B.')else'RECORD'if 'ASSOCIATION_RESOURCE'in role else'READER'if 'READER'in role else'ACTION'
            if g not in groups:continue
            rec=(a.world.probe if e['kind']=='probe'else a.world.submit)(e['port'],e['payload'],e['tick']);rr.append({**e,'id':int(rec.id),'factor_group':g})
        h=body.attach(a);samples=[];frames=[];T=plan['trials'][0]['B_source_tick']
        times=sorted(set([3312,T,T+1,T+2,T+69,T+74,T+78,3500,3550,3600,3639,3660,3691,3710,3743,3795,3847,3899]))
        try:
            for t in times:
                a.run_until(t);samples.append(physical(a.world,occupation=True));frames.append({'tick':t,'B':body.ic.obs(a,plan['B_center']),'E1':[{'bank':b['id'],**{k:body.ic.obs(a,b[k])for k in('message_site','hub','use_site','delivery_site')}}for b in plan['E1_banks']]})
        finally:h['detach']()
        return{'initial':initial,'included_groups':groups,'private_value_B':value,'plan':plan,'samples':samples,'frames':frames,'requests':body.ic.receipts(a,rr),'native_frames':h['frames'],'final':physical(a.world,occupation=True),'scope':'New causal ablation of the original social opportunity, common native body and age; no original snapshot is repaired or replaced.'}
    r=s.mutate(life,'IC01_SOCIAL_GROWTH_FAMILY_ABLATION',run,{'groups':groups,'value':value,'code':digest_file(__file__),'prepared_before':cases});atomic_json(out,r);print(name+' '+str(r['INSTRUMENTO']['tick']),flush=True)
