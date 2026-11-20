import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from predictor import *

root=Path(sys.argv[1]);log=AuditLog(root/'PREDICCIONES_TIMING.jsonl');rows=[]
for opened in (True,False):
    for delay in (0,1,2):
        s=PredictorSession(build(),PersistentTransportHabitat(opened));rs=s.experience_past_results(delay=delay);em=s.predict([70],log,'TIMING_'+str(opened)+'_'+str(delay));ev=s.evaluate(70,log,'TIMING_'+str(opened)+'_'+str(delay));rows.append({'initial_hidden_evaluator_condition':opened,'delay':delay,'receipts':rs,'emission':em,'evaluation':ev})
atomic_json(root/'resultados'/'TIMING_DOMAIN.json',{'rows':rows,'declared_before_execution':'EXPERIMENT_CONFIG.discovery_timing_controls','not_new_independent_random_replicates':True})
print(json.dumps([{'opened':r['initial_hidden_evaluator_condition'],'delay':r['delay'],'delta':r['emission']['panel_before']['delta'],'pred':r['emission']['prediction_set'],'admission':[x['status'] for x in r['receipts']]} for r in rows]))
