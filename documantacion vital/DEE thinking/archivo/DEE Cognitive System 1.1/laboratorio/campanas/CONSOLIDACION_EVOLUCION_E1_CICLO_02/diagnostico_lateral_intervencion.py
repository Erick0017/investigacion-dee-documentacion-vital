"""Only134ticks from the lived first-use checkpoint: actual further input
versus no new entries, keeping initial queued feedback. MAIN never advanced.
"""
import sys,importlib.util
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import integracion_situada_01 as ic
from capacidades.integracion_situada_01 import ic_native_core as core
sp=importlib.util.spec_from_file_location('snapshot_only',SYSTEM/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
s=Store();source_info=json.loads((EV/'C02_LATOP_306_USO.json').read_text(encoding='utf8'))['result']['INSTRUMENTO']
source=next(p for p in(s.root/'estado/checkpoints').glob('E1_CICLO02_LATERAL_LOCAL_01.T21108.*')if digest_file(p)==source_info['snapshot_sha256'])
reference_info=json.loads((EV/'C02_LATOP_309_SIN_NUEVO_B.json').read_text(encoding='utf8'))['result']['INSTRUMENTO']
reference=next(p for p in(s.root/'estado/checkpoints').glob('E1_CICLO02_LATERAL_LOCAL_01.T21242.*')if digest_file(p)==reference_info['snapshot_sha256'])
CASES=[('C02_LATDIAG_314_MATERIAL','material'),('C02_LATDIAG_315_PASIVO','passive')]
atomic_json(EV/'DIAGNOSTICO_LATERAL_PROTOCOLO_314.json',{'source':str(source.relative_to(s.root)),'sha256':digest_file(source),'cases':CASES,'native_window':[21108,21242],
 'question':'Is new material querying necessary for the old-code loss after one lateral update? Both begin with the same complete state and pending feedback. Passive means no NEW entries, not emptying the environment or cancelling its legitimate agenda.',
 'clock':'Same native age. Pendulum is explicitly paused in passive arm, so this is an internal-input contrast, not a claim of identical closed-loop environmental futures.',
 'logger':'Passive every-tick ROI; complete immutable pre-state only until first departure in this one bounded diagnostic interval. Full post retained. Not default dense campaign recording.',
 'comparison':'Material arm must match the already executed original21242 RAW/clocks/interfaces/agenda/receipts. No new independent acquisition claimed.'})
for name,mode in CASES:
    fork('E1_CICLO02_LATERAL_LOCAL_01',name,checkpoint=str(source.relative_to(s.root)))
    def test(a):
        initial=physical(a.world,occupation=True);frames=[];first=None;folder=EV/(name+'_VENTANA');folder.mkdir(exist_ok=True);base=a.run_until
        def observed(target):
            nonlocal first
            for t in range(a.tick+1,target+1):
                pre=None
                if first is None:pre=folder/('PRE_T'+str(t)+'.deetsnap.gz');a.save(pre)
                base(t);site=[(11+t-20572)%67,59,23];read=observe(a.world,site);qualified=read['state']==1 and read['semantic']==1 and read['s_reg']==7 and read['direction']==[1,0,0]
                row={'tick':t,'expected_site':site,'read':read,'qualified_old_tube':qualified,
                     'context_nonzero':[v for x in(-2,-1,0,1,2)for y in(-2,-1,0,1,2)for z in(-2,-1,0,1,2)if(v:=observe(a.world,core.move(site,(x,y,z))))['raw']!='0']}
                if first is None and not qualified:
                    post=EV/(name+'.POST_DEPARTURE.deetsnap.gz');a.save(post);first={'tick':t,'pre':str(pre.relative_to(ROOT)),'pre_sha256':digest_file(pre),'post':str(post.relative_to(ROOT)),'post_sha256':digest_file(post),'row':row}
                frames.append(row)
        a.run_until=observed
        try:
            use=ic.act_external(a,steps=2)if mode=='material'else ic.advance(a,until=21242,record=False)
        finally:a.run_until=base
        return{'initial':initial,'mode':mode,'first_departure':first,'frames':frames,'operation':use,'final':physical(a.world,occupation=True),
               'attribution':'Same starting native state and initial pending events. No new private B input, no repair and no hidden target. Later material events are the controlled factor.'}
    r=run(name,name,test,{'spec':'DIAGNOSTICO_LATERAL_PROTOCOLO_314.json'})
    if mode=='material':
        a=m.Snapshot(s.snapshot(s.record(name)));b=m.Snapshot(reference)
        c={'RAW_equal':a.raw==b.raw,'clocks_equal':a.clocks==b.clocks,'interfaces_equal':a.channels==b.channels,'pending_equal':a.pending==b.pending,'receipts_equal':a.receipts==b.receipts,'reference_sha256':digest_file(reference),'source_sha256':digest_file(source)}
        atomic_json(EV/'OBSERVACION_LATERAL_COMPARACION_314.json',c);assert all(c[k]for k in('RAW_equal','clocks_equal','interfaces_equal','pending_equal','receipts_equal'))
command('C02_LATDIAG_316_USO_PASIVO',['integrado-externo','--vida','C02_LATDIAG_315_PASIVO','--pasos','1'])
