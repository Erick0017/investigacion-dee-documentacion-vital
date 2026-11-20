"""Finite prospective probe of official U0: no new engine, no answer lookup.

The lower forms are deliberately NOT declared a unified autonomous selector.
This probe tests whether their acquired correspondences survive accumulation
while the same world also executes the native order/comparison/question chain.
"""
import gzip, hashlib, inspect, json, os, sys, time
from pathlib import Path
import dee_thinking as d

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA/mecanismo'
OUT.mkdir(parents=True,exist_ok=True)
os.environ['OMP_NUM_THREADS']='1'

def write(path,value):
    data=json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2).encode()
    if path.exists(): raise FileExistsError(path)
    path.write_bytes(gzip.compress(data,mtime=0) if path.suffix=='.gz' else data)

def run(mode):
    name='MA_U0_'+mode.upper()+'_T0'
    s=d.IntegratedSession.create(identifier=name)
    rows=[]
    def record(op,detail=None):
        rows.append({'operation':op,'tick':s.tick,'detail':detail,'physical':s.observe(),
                     'receipts':s.receipts()})
    def save(label):
        path=OUT/(name+'.'+label+'.deetsnap.gz')
        proof=s.save_snapshot(path,compress=True)
        return {'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'proof':str(proof)}
    record('initial'); initial=save('T0')
    s.experience_order('AB');s.consequence(1)
    # Current experiences, not a preloaded answer dictionary. The no_event arm
    # has the same cue and fixed architecture, but omits these consequences.
    for form,sign in [('L03',1),('L04',-1),('L05',1)]:
        s.acquire(form,sign,0,mode='paired' if mode=='paired' else 'no_event')
    s.action();s.teach_form();s.run_until(75);record('three_acquired_native_action')
    first=s.query(['L05','L03','L04'],134);record('first_three_use',first)
    # Fourth is added in a new phase after the first three were actually used.
    s.acquire('L06',-1,201,mode='paired' if mode=='paired' else 'no_event')
    s.run_until(204);record('fourth_experience')
    panel=s.query(['L06','L04','L05','L03'],268);record('first_retention_after_fourth',panel)
    # The official U0's published directed revision only supports L03/T402.
    s.revise('L03',-1,402,method='double_teacher',mode='treatment' if mode=='paired' else 'offpath_sham')
    s.run_until(405);record('selective_revision')
    final=s.query(['L05','L06','L03','L04'],469);record('first_use_after_revision',final)
    snap=save('T'+str(s.tick))
    result={'schema':'MA.U0.pilot.1','identifier':name,'architecture':'official integrated_u0.cpc7.v1',
            'new_life_not_EO01_continuity':True,'mode':mode,'initial_snapshot':initial,
            'final_snapshot':snap,'geometry':s.geometry,'rows':rows,
            'scope':'Native U0 order/comparison/question/action plus four acquired physical correspondences. Lower-form query is operator addressed; this is not autonomous context selection or four integrated procedures.',
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'engine_import':d.__file__}
    write(OUT/(name+'.json.gz'),result)
    print(json.dumps({'identifier':name,'tick':s.tick,'first':first,'retention':panel,'revision':final},ensure_ascii=False),flush=True)
    return result

if __name__=='__main__':
    protocol={'schema':'MA.U0.pilot.prospective.1','frozen_before_execution_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
              'teacher':11,'cue':5,'fixed_schedule':'order AB and consequence+ at11; lower L03+ L04- L05+ T0; first use134; L06-201; retention268; L03- doubleteacher402; final469/read472',
              'control':'same cue/architecture/age; lower current experiences omitted, offpath revision sham',
              'criterion':'all first-use native directional reads valid and signs match experiences; retention before re-teaching; revision L03 flips while remaining three signs persist',
              'scope':'finite pilot, operator-addressed lower association retention; not semantic breadth or an autonomous four-expert selector'}
    write(OUT/'PROTOCOLO_PILOTO_U0.json',protocol)
    for mode in ('paired','no_event'):run(mode)
