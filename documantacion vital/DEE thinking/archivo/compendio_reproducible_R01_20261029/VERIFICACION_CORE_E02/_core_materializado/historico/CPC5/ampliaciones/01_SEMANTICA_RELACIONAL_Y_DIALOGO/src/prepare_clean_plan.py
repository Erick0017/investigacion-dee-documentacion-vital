"""Freeze bounded clean replay commands from already recorded physical recipes."""
from pathlib import Path
import json

EXT=Path(__file__).resolve().parents[1]


def put(name,value):
    path=EXT/'configuraciones'/name
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def main():
    case=json.loads((EXT/'resultados/dialogue_longitudinal/LONGITUDINAL_LOWER/MEASUREMENTS.json').read_text(encoding='utf-8'))['case']
    put('clean_principal_longitudinal.json',{'schema':'CPC5.extension.clean.physical-case.v1','case':case,
        'scope':'Recipe parameters only. No terminal state, response mapping, expected outcome or target is consumed by the replay.'})
    put('clean_principal_batch.json',{'schema':'CPC5.extension.clean.principal-batch.v1','cases':[case],
        'scope':'Single physical recipe replay through the public portable batch interface; no expected outputs.'})
    capacity=json.loads((EXT/'resultados/capacity_discovery/CAP_D08_N67_G8/MEASUREMENTS.json').read_text(encoding='utf-8'))['case']
    put('clean_capacity8.json',capacity)
    causal=[]
    for name in('NAME_CF_REMOVE','NAME_CF_SHAM'):
        causal.append(json.loads((EXT/'resultados/order_forks'/name/'MEASUREMENTS.json').read_text(encoding='utf-8'))['case'])
    put('clean_causal.json',{'schema':'CPC5.extension.clean.causal-cases.v1','cases':causal})
    cmd=lambda id,args,timeout=300:{'id':id,'argv':['{python}','-I','-B','-X','utf8',*args],'timeout_seconds':timeout}
    commands=[
       cmd('principal_native_replay',['{extension}/ejecutar.py','dialogo','--config','{extension}/configuraciones/clean_principal_batch.json','--salida','{out}/principal']),
       cmd('public_longitudinal_demo',['{extension}/ejecutar.py','demostracion','--eventos','{extension}/configuraciones/demo_longitudinal.json','--salida','{out}/longitudinal']),
       cmd('public_order_demo',['{extension}/ejecutar.py','demostracion','--eventos','{extension}/configuraciones/demo_orden.json','--salida','{out}/orden']),
       cmd('another_process_new_query',['{extension}/ejecutar.py','demostracion','--eventos','{extension}/configuraciones/demo_longitudinal_continuacion.json','--checkpoint','{out}/longitudinal/LONGITUDINAL_T338.deetsnap','--salida','{out}/continuado']),
       cmd('prior_SEM01_reference',['{root}/src/references.py','--case','SEM01_A_future_UV','--output','{out}/referencia']),
       cmd('selective_causal_contrast',['{extension}/src/order_forks.py','--config','{extension}/configuraciones/clean_causal.json','--output','{out}/causal']),
       cmd('short_capacity8_replay',['{extension}/src/capacity.py','worker','--case','{extension}/configuraciones/clean_capacity8.json','--out','{out}/capacidad']),
       cmd('public_three_actor_network',['{extension}/ejecutar.py','demostracion','--eventos','{extension}/configuraciones/demo_red3.json','--salida','{out}/red']),
       cmd('network_another_process_continuation',['{extension}/ejecutar.py','demostracion','--eventos','{extension}/configuraciones/demo_red3_continuacion.json','--checkpoint','{out}/red/RED3_T204.deetsnap','--salida','{out}/red_continuado']),
       cmd('network_posttrajectory_comparisons',['{extension}/src/demo_network_checks.py','--generated','{out}','--output','{out}/NETWORK_CHECKS.json']),
       cmd('minimal_application_isolation',['{extension}/src/minimal_app_check.py','--output','{out}/aislamiento','--full-demo','{out}/longitudinal','--staging','{out}/minimal']),
       cmd('posttrajectory_primary_comparisons',['{extension}/src/clean_checks.py','--generated','{out}','--output','{out}/PRIMARY_COMPARISONS.json']),
       cmd('posttrajectory_extra_comparisons',['{extension}/src/clean_extra_checks.py','--generated','{out}','--output','{out}/EXTRA_COMPARISONS.json'])]
    put('clean_reproduction_plan.json',{'schema':'CPC5.extension.clean-reproduction-plan.v1',
        'scope':'Technical deterministic replays and new process continuation. Expected states are opened only by explicit external comparison commands after the relevant trajectories, never by participants.',
        'checkpoints':['ampliaciones/'+EXT.name+'/resultados/dialogue_longitudinal/LONGITUDINAL_LOWER/T338.deetsnap',
                       'ampliaciones/'+EXT.name+'/resultados/demo_orden_01/ORDEN_T92.deetsnap'],
        'commands':commands,
        'required_outputs':['principal/LONGITUDINAL_LOWER/MEASUREMENTS.json','longitudinal/DEMO_RESULT.json',
            'orden/DEMO_RESULT.json','continuado/DEMO_RESULT.json','continuado/CONTINUADO_T405.deetsnap',
            'referencia/MEASUREMENTS.json','causal/NAME_CF_REMOVE/MEASUREMENTS.json','causal/NAME_CF_SHAM/MEASUREMENTS.json',
            'capacidad/MEASUREMENTS.json','red/DEMO_RESULT.json','red_continuado/DEMO_RESULT.json','NETWORK_CHECKS.json',
            'aislamiento/MINIMAL_REPORT.json','PRIMARY_COMPARISONS.json','EXTRA_COMPARISONS.json'],
        'asserted_json_outputs':[{'path':name,'field_equals':{'verified':True,'comparisons_after_trajectories_only':True}}
                                 for name in('NETWORK_CHECKS.json','PRIMARY_COMPARISONS.json','EXTRA_COMPARISONS.json','aislamiento/MINIMAL_REPORT.json')]})
    print(json.dumps({'commands':len(commands),'plan':'configuraciones/clean_reproduction_plan.json'}))


if __name__=='__main__':main()
