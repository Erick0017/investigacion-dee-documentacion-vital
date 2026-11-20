"""Read-only-instrument inventory formatter; no native engine import."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

PREPARATIONS={
    'COUNT_ACCESS_V1':12,'COUNT_ACCESS_V2':12,'REL_PERSPECTIVE_AUX_V1':9,
    'TWO_MEMORY_PILOT':2,'TWO_MEMORY_CONFIRMATORY':10,
    'PRESENCE_COUNT_PILOT':3,'PRESENCE_COUNT_GEOMETRY_V2':4,'PRESENCE_COUNT_V3':4,'PRESENCE_COUNT_DOSE_RESERVE':20,
    'PRESENCE_REMOTE_PILOT':4,'PRESENCE_REMOTE_ACCESS_V2':4,'PRESENCE_REMOTE_V3':4,'PRESENCE_REMOTE_RESERVE':8,
    'ACTION_TRACE_V1_COMPLETE':6,'ACTION_TRACE_V2':6,'CONTENT_REFLECTION_V1':9,'CONTENT_REFLECTION_V2':9}
MODALITIES={
    'COUNT_ACCESS_CAUSAL_RESTORE':(4,2),'TWO_MEMORY_CAUSAL_RESTORE':(4,2),
    'PRESENCE_CAUSAL_RESTORE':(4,1),'PRESENCE_REMOTE_CAUSAL_RESTORE':(6,3),
    'ACTION_TRACE_CAUSAL_RESTORE':(6,2),'CONTENT_REFLECTION_CAUSAL_RESTORE':(4,2)}
PASSIVE=['PRESENCE_TRACE_ONE_A','PRESENCE_TRACE_ONE_A_TO76','PRESENCE_LOCAL_RECONSTRUCTION','PRESENCE_REMOTE_MIDDLE_TRACE']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    inventory=[]
    for folder,expected in PREPARATIONS.items():
        root=ROOT/'resultados'/folder
        paths=sorted(root.glob('*/MEASUREMENTS.json'))
        if folder.startswith(('ACTION_','CONTENT_')):paths=sorted(p for p in root.glob('*.json') if p.name!='BATCH.json')
        if len(paths)!=expected:raise AssertionError((folder,len(paths),expected))
        inventory.append({'directory':'resultados/'+folder,'completed_preparations':len(paths),
                          'primaries':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]})
    trajectories=[]
    for folder,(forks,continuations) in MODALITIES.items():
        root=ROOT/'resultados'/folder;paths=sorted(root.glob('*/MEASUREMENTS.json'))
        if folder.startswith(('ACTION_','CONTENT_')):paths=sorted(p for p in root.glob('*.json') if p.name!='BATCH.json')
        if len(paths)!=forks+continuations:raise AssertionError((folder,len(paths),forks,continuations))
        trajectories.append({'directory':'resultados/'+folder,'diagnostic_forks':forks,'cross_process_continuations':continuations,
                             'primaries':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':sha(p)} for p in paths]})
    passive=[{'path':'resultados/'+folder+'/MEASUREMENTS.json','sha256':sha(ROOT/'resultados'/folder/'MEASUREMENTS.json')} for folder in PASSIVE]
    files=[p for p in ROOT.rglob('*') if p.is_file()]
    data={'schema':'CPC9.semantics.inventory.v1','scope':'This auxiliary front only; no knowledge or subjects summed into rootE1.',
          'completed_preparations':sum(PREPARATIONS.values()),'diagnostic_forks':sum(x[0] for x in MODALITIES.values()),
          'cross_process_continuations':sum(x[1] for x in MODALITIES.values()),'passive_technical_continuations':len(PASSIVE),
          'nonindependent_deterministic_reproduction':{'case':'RP_C05_EQUAL_EFFECT_ACTOR_B','included_in_prepared_records':True,'reason':'Same actual physical inputs/state as RP_C04; actorlabel is auditor-only and cannot be counted as independent replication.'},
          'incomplete_technical_preparation':{'case':'AT_P01_A in failed S_ACTION_TRACE_V1_ABSPATH job','count':1,
                                            'reached_tick':1,'included_in_completed_preparations':False,'reason':'Snapshot suffix rejected before first primary file; job/stderr preserved. No scientific outcome adjudicated.'},
          'resource_or_launch_failures_without_Runtime':['S_ACTION_TRACE_V1 relative interpreter path','S_ACTION_TRACE_V2 RAM reserve blocked','S_ACTION_TRACE_CAUSAL isolated import failure'],
          'preparation_families':inventory,'derived_trajectories':trajectories,'passive_continuations':passive,
          'expanded_size_at_inventory_bytes':sum(p.stat().st_size for p in files),'file_count_at_inventory':len(files),
          'no_engine_import':True,'sha256_calculations':sha(ROOT/'revision/FRONT_SEMANTICS_CALCULOS.json')}
    out=ROOT/'revision/FRONT_RECONCILIACION.json';out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(out),'sha256':sha(out),'preparations':data['completed_preparations'],'forks':data['diagnostic_forks'],'continuations':data['cross_process_continuations'],'passive':len(PASSIVE)}))
if __name__=='__main__':main()
