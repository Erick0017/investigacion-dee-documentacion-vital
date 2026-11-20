"""Prospective4-input reserve with real post-action environmental contact.

The fixed environment owns its4-component gate law. Only independent raw
components enter DEE. The callback runs AFTER material action is emitted.
"""
from pathlib import Path
import gzip,json,os,sys,time
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'));sys.path.insert(0,str(HERE))
from app.lives import Store
from app.native_tools import digest_file,physical
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import cierre_funcional_cf01 as cf
from capacidades import ente_evolucion_02_core as core
from serie_sin_canceladores_r06 import submit_extra
from serie_cuatro_r05 import ram
PLAN={'reference_environment':14,'four_input_reserve':[[4,15,2,5],[7,19,2,3],[3,13,3,7]],
      'two_input_retention':[[11,25],[5,20]],'initial_parent':'AUX_EO02_CAP_R06_NO_CENTER',
      'criterion':'Physical joint sums exact for4; preserve2-input use after real feedback; report every failure without retargeting.'}
class FourGate:
    def __init__(self,values):self.values=values
    def act(self,*,formed,executed,posture,public,native_tick):
        L=self.values[0]+self.values[2];R=self.values[1]+self.values[3]
        available=1 if L+14>=R else-1;completed=executed is not None and executed==available
        before={'law':'EO02.material_four_component_gate.v1','components':self.values,'calibration':14,
           'computed_only_in_external_environment_after_emission':True,'available_gate_not_injected':available}
        observed={'tick':native_tick,'movement':executed is not None,'contact':executed is not None and not completed,
           'actuator_posture':posture,'effect':'gate_passed'if completed else'closed_gate_contact'if executed is not None else'no_movement','job_completed':completed}
        return{'before':before,'after':{**before,'actual_actuator_posture':posture,'observed_result':observed},'observed':observed}
def experiment(a):
    old=core._sample;rows=[];initial=physical(a.world)
    def passive(a,plan,detailed):
        q=old(a,plan,detailed);q['fanin_targets']=[body.obs(a,p)for p in[(5,13,15),(7,13,15)]];return q
    core._sample=passive
    try:
        for values in PLAN['four_input_reserve']:
            extra=submit_extra(a,values)
            r=core.external_episode(a,public=values[:2],reference=14,actuator='closed',feedback='real',trace=True,environment=FourGate(values))
            rows.append({'kind':'FOUR_RESERVE','values':values,'extra':extra,'extra_receipts':body.receipts(a,extra['requests']),'native':r})
        for values in PLAN['two_input_retention']:
            r=core.external_episode(a,public=values,reference=14,actuator='closed',feedback='real',trace=True)
            rows.append({'kind':'TWO_RETENTION','values':values,'native':r})
    finally:core._sample=old
    return{'revision':'EO02.fanin4.reserve_real.r07','plan':PLAN,'rows':rows,'physical_before':initial,'physical_after':physical(a.world,occupation=True),'memory_after':cf.witness(a)}
def main():
    dest=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad/RESERVA_R07_REAL_Y_REUSO_DOS.json.gz'
    if dest.exists():raise FileExistsError(dest)
    archive=HERE/'revisiones/R07';archive.mkdir(parents=True,exist_ok=True)
    files=[Path(__file__),HERE/'serie_sin_canceladores_r06.py',HERE/'serie_cuatro_r05.py',ROOT/'sistema/capacidades/ente_evolucion_02_core.py']
    for f in files:
        d=archive/f.name
        if d.exists()and digest_file(d)!=digest_file(f):raise ValueError('Source conflict')
        if not d.exists():d.write_bytes(f.read_bytes())
    store=Store();life='AUX_EO02_CAP_R07_RESERVA_REAL';parent=store.fork(PLAN['initial_parent'],life,kind='EO02_CAPACITY_RESERVE_CONTINUATION');beg=time.monotonic()
    result=store.mutate(life,'EO02_CAPACITY4_R07_REAL',experiment,details={'frozen_plan':PLAN,'new_reserve_no_targets_to_DEE':True})
    out={'life_id':life,'parent':parent['parent'],'sources':{str(f):digest_file(f)for f in files},'elapsed_seconds':time.monotonic()-beg,'ram':ram(),'result':result}
    with gzip.open(dest,'wt',encoding='utf8',compresslevel=6)as f:json.dump(out,f,ensure_ascii=False,allow_nan=False)
    print(json.dumps({'path':str(dest),'tick':result['INSTRUMENTO']['tick'],'rows':[{'kind':r['kind'],'v':r['values'],'command':r['native']['formed_native_command'],'ok':r['native']['job_completed'],
       'own_before':[v['s_reg']for v in r['native']['before']['own']],'own_after':[v['s_reg']for v in r['native']['after']['own']],
       'extra_status':[v['receipt']['status']for v in r.get('extra_receipts',[])]}for r in result['result']['rows']]},ensure_ascii=False))
if __name__=='__main__':main()
