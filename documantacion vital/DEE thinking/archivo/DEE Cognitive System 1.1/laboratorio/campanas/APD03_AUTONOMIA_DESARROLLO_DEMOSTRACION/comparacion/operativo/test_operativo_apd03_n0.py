"""N0 operational fixtures. Fake actor/sensor/learner, no DEE import/ticks."""
from contextlib import contextmanager
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType,SimpleNamespace
import unittest

HERE=Path(__file__).resolve().parent;BASE=HERE.parent


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


class RuntimeFixture:
    def __init__(self):self.metadata={};self.channel_names=[]
    @property
    def snapshot_metadata_entries(self):return list(self.metadata.items())
    def set_snapshot_metadata(self,key,value):self.metadata[key]=value


class ActorFixture:
    def __init__(self):
        self.tick=548407;self.world=SimpleNamespace(runtime=RuntimeFixture(),actor=self)
        self.choices=[];self.pending=None;self.arithmetic_calls=0;self.previous_goal=None


@contextmanager
def modules_fixture():
    saved={};names=[]
    def put(name,module):
        if name not in saved:saved[name]=sys.modules.get(name)
        names.append(name);sys.modules[name]=module;return module
    def simple(name,**attributes):
        result=ModuleType(name)
        for key,value in attributes.items():setattr(result,key,value)
        return result
    try:
        caps=put('capacidades',simple('capacidades'));put('app',simple('app'))
        put('dee_thinking',simple('dee_thinking'))
        put('dee_thinking.persistence',simple('dee_thinking.persistence',encode_metadata=json.dumps,decode_metadata=json.loads))
        put('app.native_tools',simple('app.native_tools',physical=lambda world:{'tick':world.actor.tick,'fixture_only':True}))
        literal=load('literal_fixture',HERE/'protocolo_apd03.py');put('app.protocolo_apd03',literal)
        quality=load('quality_fixture',BASE/'vendor/evaluador_calidad_apd02.py')
        effects=load('effects_fixture',BASE/'vendor/proveedores_prueba_apd02.py')
        oldenv=load('oldenv_fixture',BASE/'vendor/entorno_objetivo_apd02.py')
        route_version='APD02.delayed_action_trace.R04'
        previous=simple('capacidades.asistente_apd02',get=lambda actor:{'route_protocol':route_version,
            'external_uncertain':None,'goal_pending':actor.previous_goal})
        old=simple('capacidades.asistente_proposito_01',admitted_forms=lambda actor:['suma','diferencia','agrega','resta','total','quita'])
        def calc(actor,text,left,right,*,detailed=False):
            actor.arithmetic_calls+=1
            value=left+right if text=='suma'else left-right
            return {'numeric_reader':{'numeric_result':value},'N0_conventional_fixture':True}
        arithmetic=simple('capacidades.aritmetica_apd_01',native_pair=calc)
        def consequence(actor,category,*,mode):
            if category not in('SUCCESS','FAILURE'):raise ValueError('Only binary')
            actor.pending=None
            return {'category':category,'mode':mode,'N0_fixture':True}
        route=simple('capacidades.ruta_adaptativa_apd02_04',VERSION=route_version,
            get=lambda actor:{'pending_window':actor.pending},consequence=consequence)
        def sensor_use(actor,raw,*,family):
            choice=actor.choices.pop(0);actor.pending={'fixture':True}
            return {'reader':{'choice':choice},'raw_observed_fact':raw,'N0_fixture':True}
        sensor=simple('capacidades.sensor_balanceado_apd03_r02',
            port_names=lambda family:['fixture.sensor.0','fixture.sensor.1'],
            preflight=lambda actor,family:{'admissible':True,'N0_fixture':True},
            declare=lambda actor,family:{'declared':True,'N0_fixture':True},use=sensor_use)
        words=simple('capacidades.lexico_generico_apd03_r01',KEY='fixture.lexical',NEW_FORMS={'luma':0,'nara':1},
            preflight=lambda actor:{'admissible':True,'N0_fixture':True},
            prepare=lambda actor:{'prepared':True,'N0_fixture':True},
            query=lambda actor,text,**kwargs:{'reader':{'formed_native_command':1},'N0_fixture':True},
            teach=lambda *args,**kwargs:{'teaching':True,'N0_fixture':True},
            use_relation=lambda *args,**kwargs:{'use':True,'N0_fixture':True})
        words.FORM_CODEC={name:None for name in('alfa','beta','gamma','delta','epsilon','zeta','suma','diferencia','agrega','resta','total','quita','compara','recuerda')}
        previous.words=words
        memory=simple('capacidades.mente_acumulativa_r02',codec=lambda actor:{k:None for k in('alfa','beta','gamma','delta','epsilon','zeta')},
            query=lambda actor,context,**kwargs:{'reader':{'formed_native_command':-1},'N0_fixture':True})
        for name,mod in [('asistente_apd02',previous),('asistente_proposito_01',old),
            ('aritmetica_apd_01',arithmetic),('evaluador_calidad_apd02',quality),
            ('proveedores_prueba_apd02',effects),('ruta_adaptativa_apd02_04',route),
            ('sensor_balanceado_apd03_r02',sensor),('lexico_generico_apd03_r02',words),
            ('mente_acumulativa_r02',memory),
            ('entorno_objetivo_apd02',oldenv)]:
            setattr(caps,name,mod);put('capacidades.'+name,mod)
        environment=load('operational_env_fixture',HERE/'entorno_compartido_apd03.py')
        setattr(caps,'entorno_compartido_apd03',environment);put('capacidades.entorno_compartido_apd03',environment)
        assistant=load('assistant_fixture',HERE/'asistente_apd03.py')
        yield assistant,environment,quality,effects,literal
    finally:
        for name in reversed(names):
            if saved[name]is None:sys.modules.pop(name,None)
            else:sys.modules[name]=saved[name]


class OperationalTests(unittest.TestCase):
    def test_lab_and_operational_environment_rows_are_identical(self):
        with modules_fixture()as(_,op,quality,effects,_),tempfile.TemporaryDirectory()as directory:
            lab=load('lab_env_fixture',BASE/'entorno_compartido_apd03_r01.py')
            def calc(operation,values):return values[0]+values[1]if operation=='add'else values[0]-values[1]
            for mode in('local_useful','file_only'):
                args=dict(task_id='same',text='suma',left=7,second=4,second_initially_public=False,
                    quality=quality,effects=effects,context=1,feedback_mode=mode)
                left=lab.SharedGoalEnvironment(directory=Path(directory)/(mode+'_lab'),**args)
                right=op.SharedGoalEnvironment(directory=Path(directory)/(mode+'_op'),**args)
                for action in(0,0,-1):
                    a=left.commit_selected(action,1,native_value_reader=calc,synthetic_fixture=True)
                    b=right.commit_selected(action,1,native_value_reader=calc,synthetic_fixture=True)
                    for row in(a,b):
                        if row.get('quality'):row['quality'].pop('evaluation_resources',None)
                    self.assertEqual(a,b)
                self.assertEqual(left.operational_state(),right.operational_state())

    def test_literal_contract_rejects_answer_or_action(self):
        literal=load('literal_only',HERE/'protocolo_apd03.py')
        valid={'modo':'apd03-tarea-iniciar','texto':'suma','operandos':[7,4],'segundo_visible':False}
        self.assertTrue(literal.validate_literal(valid))
        for key,value in [('target',11),('action','ACT'),('banco','A'),('strategy','query_then_act')]:
            with self.assertRaises(ValueError):literal.validate_literal({**valid,key:value})
        with self.assertRaises(ValueError):literal.validate_literal({'modo':'apd03-paso','oportunidades':True})

    def test_open_pending_goal_continue_and_completed_artifact(self):
        with modules_fixture()as(a,_,_,_,_),tempfile.TemporaryDirectory()as directory:
            actor=ActorFixture();a.admit(actor);actor.choices=[0,-1]
            start=a.start_task(actor,'suma',[7,4],False,Path(directory)/'start')
            self.assertIsNone(start['public_observation']['second'])
            first=a.step(actor,1,Path(directory)/'step1')
            self.assertEqual(first['opportunities'][0]['environment_effect']['feedback'],{'category':'SUCCESS'})
            self.assertFalse(first['progress']['verified_file_goal_completed'])
            self.assertEqual(actor.arithmetic_calls,0)
            with self.assertRaises(ValueError):a.start_task(actor,'suma',[8,2],True,Path(directory)/'bad')
            # Simulated serialization of exactly the same metadata, not a Native restoration claim.
            exported=json.loads(json.dumps(actor.world.runtime.metadata))
            continued=ActorFixture();continued.world.runtime.metadata=exported;continued.choices=[-1]
            second=a.step(continued,1,Path(directory)/'step2')
            self.assertTrue(second['progress']['verified_file_goal_completed'])
            self.assertEqual(second['progress']['opportunities_used'],2)
            self.assertEqual(continued.arithmetic_calls,1)
            self.assertFalse(a.state(continued)['external_uncertain'])

    def test_missing_admission_does_not_create_a_life(self):
        with modules_fixture()as(a,_,_,_,_):
            actor=ActorFixture()
            with self.assertRaises(ValueError):a.get(actor)
            self.assertEqual(actor.world.runtime.metadata,{})

    def test_uncertain_previous_goal_prevents_new_admission(self):
        with modules_fixture()as(a,_,_,_,_):
            actor=ActorFixture();actor.previous_goal={'progress':{
                'uncertain_effect':{'stage':'test'},'verified_file_goal_completed':False,'opportunities_used':1}}
            with self.assertRaises(ValueError):a.admit(actor)
            self.assertEqual(actor.world.runtime.metadata,{})

    def test_material_panel_before_admission_has14_without_creating_metadata(self):
        with modules_fixture()as(a,_,_,_,_):
            actor=ActorFixture();result=a.panel(actor)
            self.assertEqual(result['forms_requested'],14)
            self.assertEqual(result['common_lexical_reader_sites'],28)
            self.assertTrue(result['material_not_passive'])
            self.assertEqual(actor.world.runtime.metadata,{})
            with self.assertRaises(ValueError):a.panel(actor,new_forms=True)

    def test_admitted_material_panel_has16_plus6_without_targets(self):
        with modules_fixture()as(a,_,_,_,literal):
            actor=ActorFixture();a.admit(actor)
            result=a.panel(actor,new_forms=True,memories=True)
            self.assertEqual(result['forms_requested'],16)
            self.assertEqual(result['memory_queries_requested'],6)
            self.assertEqual(result['common_lexical_reader_sites'],32)
            self.assertTrue(literal.validate_literal({'modo':'apd03-panel'}))
            with self.assertRaises(ValueError):literal.validate_literal({'modo':'apd03-panel','target':1})
            with self.assertRaises(ValueError):literal.validate_literal({'modo':'apd03-panel','nuevas':1})


if __name__=='__main__':unittest.main()
