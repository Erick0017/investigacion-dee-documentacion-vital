"""Prospective R03: actual acquired word -> contextual native action -> effect.

Requires explicit Root GO. No Main/system state is written and no favorable
control future is returned to another arm. Every arm evolves continuously.
"""
import argparse
import gc
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with path.open('xb') as stream:
        stream.write(gzip.compress(data,mtime=0) if path.suffix=='.gz' else data)


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--system',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--root-go',required=True,choices=['APD03_CONTEXT_APPLICATION_R03_ONLY'])
    args=parser.parse_args()
    if args.out.exists():raise FileExistsError('Preserve prior trials; new output directory only')
    args.out.mkdir(parents=True);sys.path.insert(0,str(args.system.resolve()))
    from app.lives import load_adapter
    from app.native_tools import physical
    from app.process_control import protect_current,current_resources
    from capacidades import ruta_adaptativa_apd02_04 as route
    from capacidades import lexico_apd02_01 as words
    from capacidades import aritmetica_apd_01 as arithmetic
    from capacidades import evaluador_calidad_apd02 as quality
    from capacidades import proveedores_prueba_apd02 as effects
    protect_current(output=args.out/'RECURSOS.json',memory_limit=512*1024*1024)
    here=Path(__file__).resolve().parent
    protocol_path=here/'APLICACION_CONTEXTUAL_R03.json';protocol=json.loads(protocol_path.read_bytes())
    sensor_path=here/'sensor_balanceado_apd03_r02.py'
    environment_path=here.parent/'comparacion/entorno_compartido_apd03_r01.py'
    vendor_path=environment_path.parent/'vendor/entorno_objetivo_apd02.py'
    snapshot=args.system/'estado/checkpoints/APD02_MAIN.T548407.1175587c1ab9.deetsnap.gz'
    if sha(snapshot)!=protocol['parent_snapshot_sha256'] or sha(sensor_path)!=protocol['sensor_source_sha256'] or sha(environment_path)!=protocol['environment_source_sha256']:
        raise ValueError('Prospectively pinned parent, sensor or environment differs; no silent alternate')
    sensor=load(sensor_path,'APD03_CONTEXT_APPLICATION_SENSOR_R02')
    environment=load(environment_path,'APD03_CONTEXT_APPLICATION_ENVIRONMENT_R01')
    paths=[Path(__file__),protocol_path,sensor_path,environment_path,vendor_path,
        Path(route.__file__),Path(words.__file__),Path(arithmetic.__file__),
        Path(quality.__file__),Path(effects.__file__),args.system/'app/lives.py',
        args.system/'app/native_tools.py',args.system/'app/process_control.py']
    # Capture existing direct and transitive Cognitive actor code BEFORE the
    # first load/tick. No motor/cache/history corpus is copied or imported.
    paths += sorted((args.system/'app').rglob('*.py'))
    paths += sorted((args.system/'capacidades').rglob('*.py'))
    paths = list(dict.fromkeys(path.resolve() for path in paths))
    source_rows=[]
    for index,path in enumerate(paths):
        target=args.out/'CODIGO_EJECUTADO'/(str(index).zfill(2)+'_'+path.name)
        target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target)
        source_rows.append({'source':str(path),'file':target.relative_to(args.out).as_posix(),
            'bytes':target.stat().st_size,'sha256':sha(target)})
    emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':protocol,'root_go':args.root_go,
        'sources':source_rows,'native_not_yet_loaded':True,'resources':current_resources(),
        'scope':'AUX mechanism trial. All complete operational service originals and MAIN stay unchanged.'})
    began=time.monotonic();deadline=began+protocol['budget_seconds'];performed=0
    arms=[];initial_witness=None;stopped=None

    class DeadlineAdapter:
        def __init__(self,adapter):self._adapter=adapter;self.world=adapter.world
        @property
        def tick(self):return self._adapter.tick
        def save(self,path):return self._adapter.save(path)
        def run_until(self,tick):
            while self.tick<tick:
                if time.monotonic()>=deadline:raise TimeoutError('Prospective wall guard; preserve actual partial future')
                self._adapter.run_until(min(tick,self.tick+67))

    def capture(adapter):
        return [sensor.observation(adapter,route.at((x,y,z)))
            for x in range(-3,4) for y in range(-1,4) for z in range(-1,2)]

    try:
        for arm_spec in protocol['arms']:
            if deadline-time.monotonic()<70:
                stopped='Frozen budget before another arm';break
            folder=args.out/arm_spec['id'];folder.mkdir()
            base=load_adapter('fisica_directa',snapshot);adapter=DeadlineAdapter(base)
            rows=[];environments=[];arm_error=None
            try:
                initial={'physical':physical(adapter.world),
                    'all_native_snapshot_metadata_sha256':hashlib.sha256(json.dumps(dict(adapter.world.runtime.snapshot_metadata_entries),sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest(),
                    'encoded_complete_snapshot_sha256':sha(snapshot)}
                if initial_witness is None:initial_witness=initial
                elif initial!=initial_witness:raise ValueError('Complete common parent differs between histories')
                if adapter.tick!=protocol['parent_tick'] or route.get(adapter)['pending_window'] is not None:
                    raise ValueError('Exact closed parent required; no pending trace can be dropped')
                emit(folder/'IGUALDAD_INICIAL.json',initial)
                adapter.save(folder/'ANTES_COMPLETO.deetsnap.gz')
                preparation=sensor.declare(adapter,protocol['sensor_family'])
                for task in protocol['tasks']:
                    if deadline-time.monotonic()<70 or performed>=protocol['maximum_action_opportunities']:
                        stopped='Frozen budget before another opportunity';break
                    task_folder=folder/task['id'];task_folder.mkdir()
                    env=environment.SharedGoalEnvironment(task_id='apd03_'+task['id'],text=task['text'],
                        left=task['left'],second=task['second'],second_initially_public=task['visible'],
                        context=task['context'],directory=task_folder/'artifacts',quality=quality,
                        effects=effects,feedback_mode='local_useful')
                    environments.append({'task':task,'environment':env})
                    adapter.save(task_folder/'ANTES_COMPLETO.deetsnap.gz')
                    emit(task_folder/'ENTORNO_ANTES.json',env.operational_state())
                    for opportunity in range(task['opportunities']):
                        if env.terminal():break
                        if deadline-time.monotonic()<70 or performed>=protocol['maximum_action_opportunities']:
                            stopped='Frozen budget before another opportunity';break
                        public=env.observation();before=physical(adapter.world)
                        word=words.query(adapter,public['text'],detailed=True)
                        operation_sign=word['reader']['formed_native_command']
                        # Public interface-validity fact, no expected action.
                        raw_fact=int(public['second'] is None)
                        selected=sensor.use(adapter,raw_fact,family=protocol['sensor_family'],capture=capture)
                        action_sign=selected['reader']['choice'];numeric=[]
                        def native_value(op,values):
                            record=arithmetic.native_pair(adapter,'suma' if op=='add' else 'diferencia',*values,detailed=True)
                            numeric.append(record)
                            return record['numeric_reader']['numeric_result']
                        effect=env.commit_selected(action_sign,operation_sign,native_value_reader=native_value,synthetic_fixture=False)
                        # Only a generic consequence AFTER the selected action.
                        projected=effect['feedback'];returned=None
                        if projected is not None:
                            returned=route.consequence(adapter,projected['category'],mode=arm_spec['feedback_mode'])
                        else:
                            raise RuntimeError('Uncertain effect; preserve it, no retry or substitute')
                        performed+=1
                        adapter.save(task_folder/('DESPUES_'+str(opportunity)+'_COMPLETO.deetsnap.gz'))
                        row={'arm':arm_spec['id'],'task':task,'opportunity_index':opportunity,
                            'before':before,'public_before':public,'word':word,
                            'raw_interface_missingness_fact':raw_fact,'native_selection':selected,
                            'native_operation_sign':operation_sign,'native_action_sign':action_sign,
                            'native_numeric':numeric,'environment_effect':effect,
                            'common_return':returned,'feedback_mode':arm_spec['feedback_mode'],
                            'sensor_sources_after':[sensor.observation(adapter,p) for p in sensor.sites(protocol['sensor_family'])],
                            'after':physical(adapter.world),
                            'first_response_captured_before_its_feedback':True,
                            'no_host_selected_action_or_route':True}
                        rows.append(row);emit(task_folder/('OPORTUNIDAD_'+str(opportunity)+'.json.gz'),row)
                        print(json.dumps({'arm':arm_spec['id'],'task':task['id'],'opportunity':opportunity,
                            'fact':raw_fact,'action_sign':action_sign,'action':effect['selected_action'],
                            'useful':effect['local_action_useful'],'file_completed':effect['final_goal_file_completed'],
                            'feedback':projected,'tick':adapter.tick}),flush=True)
                    emit(task_folder/'ENTORNO_DESPUES.json',env.operational_state())
                    if stopped:break
                final=physical(adapter.world)
                adapter.save(folder/'FINAL_COMPLETO.deetsnap.gz')
                arm={'id':arm_spec['id'],'initial':initial,'preparation':preparation,'rows':rows,
                    'final':final,'environments':[{'task':r['task'],'state':r['environment'].operational_state()} for r in environments]}
                emit(folder/'RESULTADOS.json.gz',arm);arms.append(arm)
            except Exception as error:
                arm_error={'type':type(error).__name__,'detail':str(error),'physical':physical(adapter.world),
                    'native_route_state':route.get(adapter),'no_rewind_or_favorable_replacement':True}
                adapter.save(folder/'FUTURO_AL_FALLO_COMPLETO.deetsnap.gz')
                emit(folder/'FALLO.json',arm_error)
                env_states=[{'task':r['task'],'state':r['environment'].operational_state()} for r in environments]
                emit(folder/'ENTORNOS_AL_FALLO.json',env_states)
                arms.append({'id':arm_spec['id'],'rows':rows,'error':arm_error,'environments':env_states})
                if isinstance(error,TimeoutError):stopped='Frozen wall deadline during actual opportunity'
            finally:
                del adapter,base;gc.collect()
            if stopped:break
    finally:
        closing_source_hashes=[{'source':row['source'],'sha256':sha(row['source']),
            'unchanged_since_before_first_tick':sha(row['source'])==row['sha256']} for row in source_rows]
        emit(args.out/'RESULTADOS.json',{'schema':'APD03.contextual_action_application.executed.R03',
            'protocol':protocol,'sources':source_rows,'arms':arms,'performed_action_opportunities':performed,
            'common_initial_witness':initial_witness,'stopped':stopped,
            'elapsed_seconds':time.monotonic()-began,'resources':current_resources(),
            'closing_source_hashes':closing_source_hashes,
            'scope':'Two AUX histories, not independent learning replicas; no MAIN/service mutation, no general semantics or R2 claim.'})
    return 0


if __name__=='__main__':raise SystemExit(main())
