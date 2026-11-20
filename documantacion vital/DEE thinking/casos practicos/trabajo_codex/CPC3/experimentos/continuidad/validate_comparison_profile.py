"""API integration checks; existing comparison science is not counted again."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from core.comparison_entity import CentralComparisonEntity
from core.entity import Entity,atomic_json

def main(root):
    folder=root/'experimentos/continuidad/comparison_profile';folder.mkdir(parents=True,exist_ok=True);checkpoints=root/'checkpoints/comparison_profile';checkpoints.mkdir(parents=True,exist_ok=True);cases=[];checks={}
    for name,change in [('changed',80),('stable',None)]:
        e=CentralComparisonEntity.create(initial_open=False,change_tick=change);e.event_sink=folder/(name+'.jsonl');e.sense();em=e.predict();before=e.physical_digest();e.save(checkpoints/(name+'_PENDING_T37.deetsnap'));restored=CentralComparisonEntity.load(checkpoints/(name+'_PENDING_T37.deetsnap'))
        checks[name+'_pending_loaded_physical']=restored.physical_digest()==before
        checks[name+'_pending_protocol_loaded']=restored.pending_expectation==e.pending_expectation and restored.comparison_stage==e.comparison_stage
        out=e.compare();restored_out=restored.compare();checks[name+'_restore_comparison_future_same']=restored.physical_digest()==e.physical_digest() and restored_out['comparison_decoder']==out['comparison_decoder']
        checks[name+'_report_applied']=out['input_receipt']['status']=='applied';checks[name+'_proper_singleton_domain']=out['comparison_decoder']['represented_expectation_before_report'] is True
        checks[name+'_registered_before_actual']=em['emission_tick']==37 and em['target_tick']==83 and out['episode']['native_readout_tick']==84
        checks[name+'_not_decoded_as_forecast']=e.predict()['status']=='OUTSIDE_FORECAST_DOMAIN' and e.observe()['prediction_set']==[False,True]
        before=e.physical_digest()
        for _ in range(10):e.observe()
        checks[name+'_observation_passive']=before==e.physical_digest()
        cp=e.save(checkpoints/(name+'_MAIN_FINAL_T84.deetsnap'));loaded=CentralComparisonEntity.load(checkpoints/(name+'_MAIN_FINAL_T84.deetsnap'));checks[name+'_loaded_current_marker_not_log']=loaded.observe()['comparison_live']==e.observe()['comparison_live'];checks[name+'_no_reinstallation_on_load']=loaded.physical_digest()==e.physical_digest()
        cases.append({'case':name,'scope':'API_INTEGRATION_NOT_NEW_SCIENTIFIC_REPLICA','emission':em,'comparison':out,'final':cp,'events':e.events,'operation_calls':e.operation_calls})
    h=CentralComparisonEntity.create();n_before=len([x for x in h.operation_calls if x['operation']=='submit']);unknown=h.predict();refused=h.compare();checks['H0_no_false_comparison']=len(unknown['prediction_set'])==2 and refused['status']=='NO_SINGLETON_NATIVE_EXPECTATION' and len([x for x in h.operation_calls if x['operation']=='submit'])==n_before
    late=CentralComparisonEntity.create();late.sense();late.predict();late.advance(47);before=late.physical_digest();r=late.compare();checks['late_report_not_injected']=r['status']=='MISSED_COMPARISON_WINDOW' and before==late.physical_digest()
    base=Entity.create();base.save(checkpoints/'LEGACY_BASE_NO_PROFILE.deetsnap');refused=False
    try:CentralComparisonEntity.load(checkpoints/'LEGACY_BASE_NO_PROFILE.deetsnap')
    except ValueError:refused=True
    checks['legacy_missing_profile_rejected_not_installed']=refused
    out={'schema':1,'checks':checks,'all_technical_assertions':all(checks.values()),'cases':cases,'scope':'new API persistence and domain validation around already measured physical comparison, not an extra capability count','no_operative_forks':True,'module':'src/core/comparison_entity.py'};atomic_json(folder/'VALIDATION.json',out);print(json.dumps({'checks':checks,'physical_comparisons':[(x['case'],x['comparison']['comparison_decoder']) for x in cases]},ensure_ascii=True));assert all(checks.values())
if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT)
