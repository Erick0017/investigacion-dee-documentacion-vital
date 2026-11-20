"""One bounded common, content-free access transform after a material query.

Not a learned failure detector. Both possible content branches receive the
same zero-load Z+ input, and all old/new motor wires are read simultaneously.
"""
from pathlib import Path
import sys,json,time
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import atomic_json,digest_file,observe,physical
from app.process_control import protect_current
from capacidades import integracion_situada_01 as system
from capacidades.integracion_situada_01 import delayed_social as social,ic_external as ext,ic_native_core as core
protect_current();s=Store();deadline=json.loads((LAB/'PRESUPUESTO_Y_PADRE.json').read_text())['monotonic_deadline_seconds']
spec={'frozen_before_new_cases':True,'paired_parent_age':'T5698,36external steps, old received plus or minus relation','perturbation':'One new generic social query without new B private input; actual old X carrier may transform to X+/-Z-. Do not infer conservation from names.','recovery':'At the fixed query boundary, zero-load Z+ opportunities aimed3ticks later at BOTH expected X+/-Z- continuations. No old code, reference or sign supplied.','parallel_readout':'All original ports and both fixed z-3 alternative ports, same decoder for all cases, no response-dependent routing.','controls':['none','equal-dose sham19y away'],'horizon':'2 external steps to query +4 after intervention. This is one local prepared recovery procedure, not P2/R2 or general memory reconstruction.'}
if not(EV/'GENERIC_RECOVERY_SPEC_167.json').exists():atomic_json(EV/'GENERIC_RECOVERY_SPEC_167.json',spec)
for sign,key,source in[(1,'INTEGRATED_COST_SOCIAL_132','E1_INTEGRADO_COSTO_SOCIAL_01'),(-1,'INTEGRATED_OPPOSITE_133','IC01_INTEGRATED_OPPOSITE_133')]:
    parent=json.loads((EV/(key+'.json')).read_text())['final_record']
    for mode in('recover','sham','none'):
        name='GENERIC_RECOVERY_'+('PLUS'if sign==1 else'MINUS')+'_'+mode.upper()+'_167';life='IC01_'+name;out=EV/(name+'.json')
        if out.exists():continue
        if time.monotonic()>deadline-3000:raise TimeoutError('Reserve closing time')
        s.fork(source,life,kind='DIAGNOSTIC_COPY',checkpoint=parent['snapshot'])
        def run(a):
            p=social.begin(a,name=name,mode='no_partner');h=system.attach(a)
            try:first=ext.run(a,steps=2,readout='magnitude',feedback='cost',codec=2,reader='omit',social_ports=p['banks'])
            finally:h['detach']()
            start=a.tick;before=[observe(a.world,b['target'])for b in p['banks']];requests=[];parallel=list(p['banks']);targets=[]
            for b in p['banks']:
                parallel.append({**b,'target':core.move(b['target'],(0,0,-1),3),'access':'fixed_alternative_zminus3'})
                target=core.move(b['target'],(b['sign'],0,-1),3);targets.append({'bank':b['sign'],'site':target})
                if mode!='none':requests.append(core.arrive(a,'IC01.common_recovery.'+name+'.'+str(b['sign']),core.move(target,(0,1,0),19)if mode=='sham'else target,(0,0,1),start+3,0))
            frames=[]
            for t in range(start+1,start+5):
                a.run_until(t);frames.append({'tick':t,'both_expected_old_paths':[{'bank':b['sign'],'site':core.move(b['target'],(b['sign'],0,-1),t-start),'read':observe(a.world,core.move(b['target'],(b['sign'],0,-1),t-start))}for b in p['banks']],'both_recovery_sites':[{'bank':b['sign'],'site':b['site'],'read':observe(a.world,b['site'])}for b in targets]})
            r=ext.run(a,steps=4,readout='magnitude',feedback='cost',codec=2,reader='omit',social_ports=parallel)
            return{'spec':spec,'old_sign_for_auditor_only':sign,'mode':mode,'first2':first,'before_recovery':before,'generic_requests':core.receipts(a,requests),'local_frames':frames,'external':r,'parallel_ports_fixed_before_reserve':parallel,'final':physical(a.world,occupation=True),'no_reteaching_content':True,'scope':'The reader transform is designed, its different output depends on an actually acquired old carrier. No autonomous access strategy or restoration of a physically identical erased history is claimed.'}
        r=s.mutate(life,'IC01_CONTENT_FREE_FIXED_BIDIRECTIONAL_RECOVERY_CANDIDATE',run,{'spec':spec,'mode':mode,'parent':parent['snapshot_sha256'],'source':digest_file(__file__)});atomic_json(out,r);print('GENERIC_RECOVERY '+str(sign)+' '+mode+' '+str(r['INSTRUMENTO']['tick']),flush=True)
