"""Standalone conventional APD04 references, NEVER a DEE actor or controller.

The policy sees only the two elemental bits accessible to the DEE selector.
Cache/value/loads belong to the prepared downstream executor, not choose().
Conventional arithmetic/reference20 is explicitly supplied, not learned here.
No dee_thinking import, no Runtime, no Native tick. All files are synthetic.
"""
from __future__ import annotations
import argparse
import copy
import ctypes
import hashlib
import json
import os
from pathlib import Path
import random
import time


VERSION = 'APD04.conventional_workshop_reference.N0.R02.perf_counter'


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf8')


def resources():
    result = {'process_cpu_ns': time.process_time_ns(), 'monotonic_ns': time.perf_counter_ns(),
              'scope': 'This one conventional process only, including Python and output writes; no Native or child process.'}
    result['wall_clock']={'function':'time.perf_counter_ns','advertised_resolution_seconds':time.get_clock_info('perf_counter').resolution}
    result['CPU_scope']='Windows process accounting may quantize short intervals; zero does not mean no computation.'
    if os.name == 'nt':
        class Memory(ctypes.Structure):
            _fields_ = [('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),
                        ('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),
                        ('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),
                        ('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),
                        ('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
        class IO(ctypes.Structure):
            _fields_ = [(n,ctypes.c_ulonglong) for n in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        handle = kernel.GetCurrentProcess()
        pm = Memory();pm.cb = ctypes.sizeof(pm)
        psapi = ctypes.WinDLL('psapi', use_last_error=True)
        psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p,ctypes.POINTER(Memory),ctypes.c_ulong]
        if psapi.GetProcessMemoryInfo(handle,ctypes.byref(pm),ctypes.sizeof(pm)):
            result.update(working_set_bytes=pm.WorkingSetSize,peak_working_set_bytes=pm.PeakWorkingSetSize,
                          committed_process_bytes=pm.PagefileUsage,peak_committed_process_bytes=pm.PeakPagefileUsage)
        io = IO();kernel.GetProcessIoCounters.argtypes=[ctypes.c_void_p,ctypes.POINTER(IO)]
        if kernel.GetProcessIoCounters(handle,ctypes.byref(io)):
            result['logical_IO']={name:getattr(io,name) for name,_ in IO._fields_}
            result['IO_scope']='Windows process counters; includes logical transfers/cache, not physical-disk sectors or unique bytes.'
    result['energy']='NO MEDIDA'
    return result


class FixedAlternation:
    name='fija_ciclo_INSPECT_INSPECT_USE'
    def __init__(self):self.step=0
    def choose(self, elementary_bits):
        assert len(elementary_bits)==2 and all(type(x)is int and x in(0,1) for x in elementary_bits)
        # Period3 is coprime to every tested source count2/5/10/20. An
        # alternating2-cycle would permanently confound tag parity and action.
        action='INSPECT' if self.step%3<2 else 'USE';self.step+=1;return action
    def outcome(self, elementary_bits, category):pass


class StandardWSLS:
    name='WSLS_estandar_global'
    def __init__(self):self.preferred='INSPECT';self.last=None
    def choose(self, elementary_bits):
        assert len(elementary_bits)==2 and all(type(x)is int and x in(0,1) for x in elementary_bits)
        self.last=self.preferred;return self.last
    def outcome(self, elementary_bits, category):
        if category=='FAILURE':self.preferred='USE'if self.last=='INSPECT'else'INSPECT'


class ContextWSLS:
    name='WSLS_adaptativa_por_dos_bits_publicos'
    def __init__(self):self.states={};self.last=None
    def choose(self, elementary_bits):
        assert len(elementary_bits)==2 and all(type(x)is int and x in(0,1) for x in elementary_bits)
        key=tuple(elementary_bits);choice=self.states.get(key,'INSPECT');self.last=(key,choice);return choice
    def outcome(self, elementary_bits, category):
        key,choice=self.last
        if tuple(elementary_bits)!=key:raise ValueError('Return belongs to another actual action')
        self.states[key]=choice if category=='SUCCESS'else('USE'if choice=='INSPECT'else'INSPECT')


POLICIES={c.name:c for c in (FixedAlternation,StandardWSLS,ContextWSLS)}


class Workshop:
    def __init__(self,config):
        self.config=copy.deepcopy(config);self.rng=random.Random(config['seed'])
        self.objects=[{'id':i,'tag':i%2,'value':self.rng.randrange(5,37),'observed':None,'bin':None,'version':0}for i in range(config['sources'])]
        self.cursor=0;self.goal_tag=config.get('goal_tag',0);self.word=config.get('word','clasifica')
        self.loads=list(config.get('loads',[8,4]));self.criterion=config.get('criterion',20);self.episode=0
        self.equality=config['equality_policy']
        if self.equality not in('measured_unformed','conventional_neutral_zero'):
            raise ValueError('Freeze equality transduction explicitly; no silent Native silence=HOLD')
    def exogenous(self):
        applied=[]
        for event in self.config.get('agenda',[]):
            if event['at']!=self.episode+1:continue
            if 'goal_tag'in event:self.goal_tag=event['goal_tag']
            if 'word'in event:self.word=event['word']
            if 'loads'in event:self.loads=list(event['loads'])
            if event.get('replace_values'):
                for obj in self.objects:obj['value']=self.rng.randrange(5,37);obj['version']+=1
            for change in event.get('mutaciones',[]):
                obj=next(o for o in self.objects if o['id']==change['fuente'])
                obj['value']=change['valor'];obj['version']+=1
            if event.get('rotar'):
                amount=event['rotar']%len(self.objects);self.objects=self.objects[amount:]+self.objects[:amount]
            if event.get('retirar_observados'):
                for obj in self.objects:obj['observed']=None
            applied.append(copy.deepcopy(event))
        return applied
    def public(self):
        obj=self.objects[self.cursor]
        return {'source_id':obj['id'],'tag':obj['tag'],'goal_tag':self.goal_tag,'word':self.word,
                'cached_value':None if obj['observed']is None else obj['observed']['value'],'loads':list(self.loads)}
    def commit(self, action, actor_public):
        obj=self.objects[self.cursor];self.episode+=1
        effect={'action':action,'actuator':'closed','new_fact':False,'useful':False,'valid_conventional':True}
        operation=None
        if action=='INSPECT':
            previous=obj['observed'];obj['observed']={'value':obj['value'],'version':obj['version']}
            effect['new_fact']=previous!=obj['observed'];effect['useful']=effect['new_fact']and obj['tag']==self.goal_tag
            effect['reason']='environmental_fact_exposed_by_reference_action'
        elif action=='USE':
            if self.word=='clasifica'and actor_public['cached_value']is not None:
                # Conventional supplied model of the inherited reference, never a DEE output.
                datum=actor_public['cached_value'];direction=(datum>20)-(datum<20)
                if direction==0 and self.equality=='measured_unformed':direction=None
                if direction is not None:
                    prior=obj['bin'];obj['bin']=direction
                    expected=(obj['value']>self.criterion)-(obj['value']<self.criterion)
                    correct=direction==expected and obj['observed']['version']==obj['version']
                    effect.update(correct=correct,actual_bin=direction,previous_bin=prior)
                    effect['useful']=correct and obj['tag']==self.goal_tag and prior!=direction
                else:effect['reason']='no_unique_conventional_classification_model_of_measured_Native_gap'
                operation={'conventional_classification':direction,'reference20_supplied':True}
            elif self.word=='equilibra':
                before=list(self.loads);direction=(before[0]>before[1])-(before[0]<before[1])
                if direction==0 and self.equality=='measured_unformed':direction=None
                if direction==1 and self.loads[0]>0 and self.loads[1]<20:self.loads[0]-=1;self.loads[1]+=1
                elif direction==-1 and self.loads[1]>0 and self.loads[0]<20:self.loads[1]-=1;self.loads[0]+=1
                if direction is not None:
                    old=abs(before[0]-before[1]);new=abs(self.loads[0]-self.loads[1])
                    effect['useful']=(new<old or(direction==0 and old==0))and obj['tag']==self.goal_tag
                    effect.update(loads_before=before,loads_after=list(self.loads),gap_before=old,gap_after=new,physical_move_direction=direction)
                else:effect['reason']='no_unique_conventional_balance_model_of_measured_Native_gap'
                operation={'conventional_balance':direction,'prepared_relation_supplied':True}
            else:effect['reason']='unavailable_public_fact_or_unformed_word'
        else:raise ValueError('No substitute action')
        self.cursor=(self.cursor+1)%len(self.objects)
        return effect,operation


def run_one(config, policy_name, output):
    output.mkdir(parents=True,exist_ok=False);start=resources();world=Workshop(config);policy=POLICIES[policy_name]()
    rows=[]
    for _ in range(config['opportunities']):
        exogenous=world.exogenous();public=world.public();bits=[public['tag'],public['goal_tag']]
        # Only these two elementary bits, NEVER public cache, hidden criterion or source ID, enter choose().
        action=policy.choose(tuple(bits))
        effect,operation=world.commit(action,copy.deepcopy(public))
        category='SUCCESS'if effect['useful']else'FAILURE';policy.outcome(tuple(bits),category)
        artifact=None
        if action=='USE':
            artifact=output/'artifacts'/('episode'+str(world.episode)+'.json')
            write(artifact,{'schema':'APD04.synthetic.conventional.effect.v1','episode':world.episode,
                            'source_id':public['source_id'],'tool_emitted':public['word'],'effect':effect,
                            'conventional_not_Native':True})
        rows.append({'episode':world.episode,'exogenous_before':exogenous,'public_before':public,
                     'selector_observation':bits,'chosen_before_effect':action,'operation':operation,
                     'committed_effect':effect,'feedback':category,
                     'artifact':None if artifact is None else artifact.relative_to(output).as_posix()})
    write(output/'PRIMARIOS_CONVENCIONALES.json',{'schema':VERSION,'config':config,'policy':policy_name,
                                                'no_DEE_actor_control':True,'new_native_ticks':0,'rows':rows})
    end=resources()
    files=[p for p in output.rglob('*')if p.is_file()]
    report={'policy':policy_name,'config':config,'opportunities':len(rows),
            'INSPECT':sum(r['chosen_before_effect']=='INSPECT'for r in rows),
            'USE':sum(r['chosen_before_effect']=='USE'for r in rows),
            'useful':sum(r['committed_effect']['useful']for r in rows),
            'new_facts':sum(r['committed_effect']['new_fact']for r in rows),
            'correct_classifications':sum(bool(r['committed_effect'].get('correct'))for r in rows),
            'gap_reducing_moves':sum(r['committed_effect'].get('gap_after',0)<r['committed_effect'].get('gap_before',0)for r in rows),
            'physical_output_files':len(files),'physical_output_bytes_before_report':sum(p.stat().st_size for p in files),
            'resources_before':start,'resources_after':end,
            'cpu_seconds':(end['process_cpu_ns']-start['process_cpu_ns'])/1e9,
            'elapsed_seconds':(end['monotonic_ns']-start['monotonic_ns'])/1e9,
            'scope':'One conventional local trajectory. Not a Native test, semantic acquisition, independent learner, or matched CPU cost of DEE.',
            'information_equivalence':'Selection:two elemental bits+own prior feedback/actions. Executor:actual cache/loads and supplied reference20. Goal criterion private until verification.',
            'teaching_cost':'Not included; numerical relation20 and correct conventional tool mapping are supplied preparation.',
            'equality_scope':('Matches the measured missing zero primitive output, no HOLD substitution'if world.equality=='measured_unformed'else
                              'Supplementary conventional zero-output capability; Native equality was unformed in CALIB_R02, not a proved zero/HOLD emission')}
    write(output/'RECALCULO_Y_RECURSOS.json',report)
    return report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('plan');parser.add_argument('output');args=parser.parse_args()
    plan=json.loads(Path(args.plan).read_text(encoding='utf8'));output=Path(args.output).resolve()
    if plan.get('status')!='CERRADO_PARA_REFERENCIAS_CONVENCIONALES':
        raise ValueError('Root must freeze the exact matched agenda before reference trajectories')
    if output.exists():raise FileExistsError('Preserve prior conventional trajectories; choose a new output revision')
    output.mkdir(parents=True)
    reports=[]
    for trial in plan['trials']:
        for name in plan.get('policies',list(POLICIES)):
            label='case_'+str(len(reports)).zfill(3)+'_'+name
            reports.append(run_one(trial,name,output/label))
    write(output/'RESUMEN_REFERENCIAS.json',{'schema':VERSION,'new_native_ticks':0,'reports':reports,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'not_comparison_to_APD04_until_actual_matched_primaries_exist':True})
    print(json.dumps({'trajectories':len(reports),'opportunities':sum(r['opportunities']for r in reports),
                      'new_native_ticks':0,'files':sum(1 for p in output.rglob('*')if p.is_file()),
                      'bytes':sum(p.stat().st_size for p in output.rglob('*')if p.is_file())}))


if __name__=='__main__':main()
