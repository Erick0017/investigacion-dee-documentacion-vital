"""Close the agent's exact archival cut without importing the DEE engine."""
from pathlib import Path
import csv,gzip,hashlib,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];E=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/capacidad'
sys.path.insert(0,str(ROOT/'sistema'))
from capacidades.observador_causal_retrospectivo_01 import Snapshot
def read(p):
    p=Path(p);return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,q):
    p=Path(p)
    if p.exists():raise FileExistsError('Closed cut is not overwritten: '+str(p))
    p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    c=read(E/'RECALCULO_CAPACIDAD.json')
    if c['issues']:raise ValueError('Outstanding recalculation issues')
    names=['EO02_SENSORIAL_R10_T0.T16893.263657f7e71c.deetsnap.gz','EO02_SENSORIAL_R10_T0.T18457.76ab5932c016.deetsnap.gz','EO02_SENSORIAL_R10_T0.T37225.59ee1e94b518.deetsnap.gz']
    snapshots=[]
    for name in names:
        path=ROOT/'sistema/estado/checkpoints'/name;s=Snapshot(path)
        snapshots.append({'snapshot':path.relative_to(ROOT).as_posix(),'summary':s.summary(),
          'own':[s.observation(p)for p in[(5,15,15),(7,15,15)]],
          'context':[s.observation(p)for p in[(5,15,13),(7,15,13)]],
          'B':[s.observation(p)for p in[(18,15,15),(20,15,15)]],
          'pending':s.pending,'not_a_new_native_run':True})
    main_files=['R10_pilot.json.gz','R10_CONT_TRAIN_REST.json.gz','R10_CONT_RESERVA1.json.gz','R10_CONT_RESERVA2.json.gz','R10_CONT_RESERVA3.json.gz','R10_CONT_REUSO2.json.gz',
       'R10_V2_reserve_FRONTERA1.json.gz','R10_V2_reserve_FRONTERA2.json.gz','R10_V2_reserve_FRONTERA3.json.gz','R10_V2_RESERVA_ESCALA_NUEVA.json.gz']
    rows=[row for row in c['episodes']if row['file']in main_files]
    if len(rows)!=48:raise ValueError('Wrong closed R10 episode count')
    g=read(E/'R10_create.json.gz')['result']['geometry']
    out={'schema':'EO02.capacity.agent_closed_cut.v1','new_ticks_in_closure':0,'recalculation':{'file':'RECALCULO_CAPACIDAD.json','sha256':sha(E/'RECALCULO_CAPACIDAD.json'),'totals':c['totals'],'issues':c['issues']},
       'main_R10':{'life_id':'EO02_SENSORIAL_R10_T0','closed_tick':37225,'episodes':48,'valid':sum(r['valid']for r in rows),'useful':sum(r['job_completed_as_actually_executed']for r in rows),
         'incorrect':sum(not r['job_completed_as_actually_executed']for r in rows),'eight_input_episodes':sum(len(r['values']or[])==8 for r in rows),'exact_eight_material_sums':sum(len(r['values']or[])==8 and r['sum_exact']is True for r in rows),
         'requested':sum(r['requested']for r in rows),'statuses':{status:sum(r['statuses'].get(status,0)for r in rows)for status in['applied','rejected_occupied','rejected_conflict']},
         'newly_opened_T0_sites':len(g['r10_newly_opened']),'newly_opened_sites':g['r10_newly_opened'],'no_EO01_memory_import':True,
         'files':main_files,'cut_not_necessarily_latest_after_root_extension':True},
       'exact_snapshots':snapshots,'all_sources_in_archives':True,'raw_clock_no_float':True,
       'component_relevance':{'R9_R03_first_use':c['relevant_component_contrasts'],'R10_late':c['R10_relevant_component_contrasts']},
       'passive_observation_equivalence':c['passive_observation_physical_equivalence'],
       'scope':'Joint8 scalar observations through native reducer and acquired spatial comparison in a new R10 life; sixteen/thirty-two are serial observation windows, not joint arity.'}
    write(HERE/'CIERRE_CAPACIDAD_T37225.json',out)
    with(HERE/'TABLA_TODOS_ENSAYOS_CAPACIDAD.csv').open('x',encoding='utf8',newline='')as f:
        w=csv.writer(f);w.writerow(['primary','pointer','critical_tick','values','native_command','auditor_target','sum_exact','completed_externally','actuator','feedback','requested','applied','rejected_occupied','rejected_conflict','resource_only'])
        for r in c['episodes']:w.writerow([r['file'],r['episode'],r['critical_tick'],json.dumps(r['values']),r['command'],r['auditor_target'],r['sum_exact'],r['job_completed_as_actually_executed'],r['actuator'],r['feedback'],r['requested'],r['statuses'].get('applied',0),r['statuses'].get('rejected_occupied',0),r['statuses'].get('rejected_conflict',0),r['resource_only_not_a_data_answer']])
    print(json.dumps({'report':str(HERE/'CIERRE_CAPACIDAD_T37225.json'),'R10':out['main_R10'],'snapshots':[{'tick':s['summary']['tick'],'sha':s['summary']['encoded_sha256'],'pending':s['summary']['pending_count'],'receipts':s['summary']['receipts']}for s in snapshots]},ensure_ascii=False))
if __name__=='__main__':main()
