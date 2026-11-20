"""Single correction of R02: admit raw data at actual RAW-empty origins.

Two fixed peripheral sensors reach the existing two candidate datum sites;
generic B activation remains P0 assistance. No fields or memories are edited.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from capacidades import cierre_funcional_cf01 as cf
from capacidades import arquitectura_distribuida_mi02_r8 as body
from capacidades import ente_operativo_01_core as core
EV=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/contexto'

def experiment(a,pair):
    before=cf.witness(a);common_A=core.external_episode(a,public=list(pair),reference=12,feedback='omit',trace=False)
    start=int(a.tick);t=start+4;C=cf.geometry(a)['B'];rr=[]
    sites=[body.xyz(a,C,(r,-1,1))for r in(-1,1)]
    origins=[[19,13,14],[19,12,14]];directions=[[-1,0,1],[1,1,1]]
    pre={'targets':[body.obs(a,p)for p in sites],'origins':[body.obs(a,p)for p in origins],'Q':body.obs(a,C)}
    rr.append(body.send(a,'EO02.B.generic_query',C,(0,0,-1),t,0))
    for j,value in enumerate(pair):rr.append(body.send(a,'EO02.B.raw.peripheral.'+str(j),origins[j],directions[j],t-1,value))
    frames=[]
    for tick in range(start+1,t+41):
        a.run_until(tick)
        frames.append({'tick':tick,'witness':cf.witness(a),'data':[body.obs(a,p)for p in sites],'origins':[body.obs(a,p)for p in origins],
            'buses':{n:body.obs(a,p)for n,p in [('minus',[12,19,9]),('plus',[0,19,9])]},'waypoints':cf.message_witness(a)})
    return {'pair':pair,'before':before,'common_A':common_A,'B_generic_query_tick':t,'new_sensor_sites_before':pre,'requests':body.receipts(a,rr),'frames':frames,'after':cf.witness(a),'attribution':'Fixed peripheral raw sensors and query are prepared P0; A/B outputs and all transformations belong to the shared Runtime. Not a learned selector.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--pair',required=True);p.add_argument('--case',required=True);args=p.parse_args()
    pair=[int(v)for v in args.pair.split(',')]
    if len(pair)!=2 or any(not 0<=v<=64 for v in pair):raise ValueError('Two raw scalars0..64')
    if time.monotonic()>=json.loads((HERE.parent/'PRESUPUESTO.json').read_bytes())['deadline_monotonic']:raise TimeoutError('Original EO02 deadline')
    life='AUX_EO02_CTX_R03_'+args.case;out=EV/(life+'.json.gz')
    if out.exists():raise FileExistsError(out)
    s=Store(ROOT/'sistema');fork=s.fork('EO01_MAIN',life,kind='DIAGNOSTIC_EXACT_FORK')
    result=s.mutate(life,'EO02_B_TWO_PERIPHERAL_RAW_SENSORS_R03',lambda a:experiment(a,pair),details={'raw_pair':pair,'generic_B_query':True,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    r=result['result'];row={'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'parent':fork,'result':result,'new_ticks_only_on_auxiliary':True}
    EV.mkdir(parents=True,exist_ok=True)
    with gzip.open(out,'wt',encoding='utf8')as f:json.dump(row,f,ensure_ascii=False,allow_nan=False)
    events=[{'t':f['tick'],'B':[f['witness']['B']['state'],f['witness']['B']['s_reg'],f['witness']['B']['direction']],'data':[[q['state'],q['s_reg'],q['semantic'],q['direction']]for q in f['data']]}for f in r['frames']if f['witness']['B']['state']>0]
    print(json.dumps({'life':life,'pair':pair,'A_command':r['common_A']['formed_native_command'],'B_events':events,'new_requests':r['requests'],'after_B_references':[q['s_reg']for q in r['after']['private_B']],'primary':str(out)},ensure_ascii=False))
if __name__=='__main__':main()
