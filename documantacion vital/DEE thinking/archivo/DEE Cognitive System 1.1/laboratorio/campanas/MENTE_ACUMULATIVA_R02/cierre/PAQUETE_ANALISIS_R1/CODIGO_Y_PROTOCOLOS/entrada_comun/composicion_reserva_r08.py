"""R08: realiza igualdad de admisión que R07 no logró.

R07 pidió3 señales por historia pero tercera misma-sign fue rechazada.
R08 usa dos diagonales compensadas que no ocupan la órbita del recuerdo.
"""
import hashlib,importlib.util,time
from array import array
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('r07_exact',HERE/'composicion_reserva_r07_ejecutado_xyz_invertido.py');p=importlib.util.module_from_spec(sp);sp.loader.exec_module(p)
b=p.b;r=p.r
def revise_four(s,i,sign,t,mode='double'):
    v=b.V[i];h=b.add(b.I,v,3);rs0=len(s.requests);before=s.save('pre_revision4_'+str(t))
    s.send('common.token.'+str(i),b.I,v,5,t)
    dv=(-v[0],-v[1],sign);s.send('experience.'+str(i)+'.'+str(sign),b.add(h,dv,-3),dv,11,t)
    for dx in(-1,1):
        dv=(dx,dx,sign);s.send('contrast.r08.'+str(i)+'.'+str(sign)+'.'+str(dx),b.add(h,dv,-3),dv,11,t)
    s.world.run_until(t+3)
    s.rows.append({'kind':'revision','bank':i,'new_signal':sign,'input_tick':t,'tick':s.tick,'mode':'four_inputs_compensated_diagonals','pre_snapshot':before,'hub':s.observe(h),'new_request_ids':[x['id']for x in s.requests[rs0:]],'requested_dose':38,'requested_count':4,'actual_admission_must_be_recalculated':True})
def global_frame(s):
    raw=s.world.runtime.raw_copy();cl=s.world.runtime.clock_copy()
    out=[{'site':[k//4489,(k//67)%67,k%67],'raw':str(x),'clock':str(cl[k])}for k,x in enumerate(raw)if x]
    return {'tick':s.tick,'nonzero_raw':out,'RAW_sha256':hashlib.sha256(array('Q',raw).tobytes()).hexdigest(),'clocks_sha256':hashlib.sha256(array('Q',cl).tobytes()).hexdigest(),'coverage':'Native idx3d=(x*N+y)*N+z. All nonzero RAW including state0 every tick. ZeroRAW clocks hash committed, full snapshots local.'}
p.p.p.p.revise=revise_four
p.global_frame=global_frame
if __name__=='__main__':
    b.put(b.OUT/'PROTOCOLO_RESERVA_R08.json',{'fixed_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'reason':'R07 actual third same-sign input rejected; retain that observation, use compensated diagonal experience routes for matched4requests/dose38','prefix':'MA02_MAIN2486 remains protected while reservations fork','future_same_as_R07':True,'reader_unchanged':'pureZ atbothcentral±6sites2689','histories':'beta− vsbeta+; alpha− remains, same4requestedinputs anddose; verify actualadmission before inference','cut_sham':'First already formed stream2622, raw-only cut/clockpreserved vs exact sham','spatial_index_correction':'Global frames now native(x*N+y)*N+z; R07 primary bytes unchanged'})
    p.run('MA02_R08_RES_CONCORDANT',-1);p.run('MA02_R08_RES_MIXED',1);p.run('MA02_R08_RES_CUT',-1,True,False);p.run('MA02_R08_RES_SHAM',-1,False,True)
