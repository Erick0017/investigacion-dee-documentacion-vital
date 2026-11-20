"""Synthetic fixture histories only; no real DEE/model/Studio execution."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from RECALCULO_CIERRE8_R07 import Sources,run,save_outputs

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def parent():
    return{'native_tick':991187,'native_life_id':'SYNTHETIC_PARENT','world_id':'R06',
      'S':{'completedCycles':28,'station':2,'permissionStock':164,'queries':28,'moves':28,'waits':0,
       'skips':0,'collisions':0,'resourceCount':3,'delivered':3,'tollSpent':8,'querySpent':28,
       'functionCalls':10,'functionNoResult':0,'codeRejected':1,'inventoryResource':False,
       'numberAPresent':True,'numberA':11,'numberAVersion':5,'codeBPresent':False,
       'sessionId':'OLD'},'boundary':{'phase':'BOUNDARY'},'events':[{'kind':'HISTORICAL','data':{'cycle':28}}]}

def fixture(p,participant='LIVE_NATIVE',count=1,loop=False,numeric=None,duplicate=False,stale=False,wait=False):
    par=parent();p.mkdir(parents=True,exist_ok=True)
    (p/'parent.json').write_text(json.dumps(par),'utf-8');events=[];rows=[];tick=991187;S=copy.deepcopy(par['S'])
    worldevents=copy.deepcopy(par['events'])
    for c in range(29,29+count):
        obs={'observationId':'obs'+str(c),'seq':56+2*(c-29)+1,'phase':'QUERY_CHOICE',
             'sensors':{'stationSignal':-1,'publicContactCode':S['station']}}
        route_obs=dict(obs,phase='ROUTE_CHOICE',sensors=dict(obs['sensors'],stationSignal=1))
        phases=[('decision',{'observation':obs},356),('query_sensor',{'observation':route_obs},22)]
        if numeric is not None:phases.append(('function',{'tool':{'kind':'CALCULATE','slot':'B','form':'nara','left':11,'right':11}},258))
        phases.append(('feedback',{'outcome':'TOOL_NO_RESULT'if stale else'MOVED','materialConsequence':stale,
             'collision':False,'resourceCollected':False,'resourceDelivered':False,'permissionSpent':1},928 if numeric is not None else 1186))
        out_by_phase={}
        for phase,payload,delta in phases:
            op='SYNTH_'+str(c)+'_'+phase;ctx={'operation_id':op,'sequence':obs['seq'],'session_id':'SYNTH','observation_id':obs['observationId']}
            events.append({'kind':'NATIVE_INTENT'if participant=='LIVE_NATIVE'else'BACKEND_INTENT','cycle':c,'phase':phase,'payload':payload,'context':ctx})
            if participant=='LIVE_NATIVE':tick+=delta
            out={'nativeTick':tick if participant=='LIVE_NATIVE'else 0,'nativeTicks':delta if participant=='LIVE_NATIVE'else 0,
                 'accepted':True,'null':False}
            if phase=='decision':out.update(action='ASK_STATION')
            if phase=='query_sensor':out.update(action='SAFE_WAIT'if wait else'EXIT_1',voluntary_wait=wait,invalid=False)
            if phase=='function':out['toolResult']={'kind':'CALCULATE','slot':'B','form':'nara','memory_value':-1,
                 'operation':'diferencia','numeric_result':numeric if type(numeric)is int else None,
                 'formed':type(numeric)is int,'capability_execution_admitted':type(numeric)is int}
            row={'kind':'NATIVE_COMPLETED'if participant=='LIVE_NATIVE'else'BACKEND_COMPLETED','cycle':c,'phase':phase,
                 'operation_id':op,'result':out,'wall_seconds':.5}
            events.append(row)
            if duplicate:events.append(dict(row,utc='duplicate documentary timestamp'))
            out_by_phase[phase]=out
        if not wait:S['station']=(3 if S['station']==2 else 2)if loop else 4;S['moves']+=1
        S['queries']+=1;S['permissionStock']-=1;S['querySpent']+=1;S['completedCycles']=c
        S['sessionId']='SYNTH';S['numberA']=11
        wr={'outcome':'MOVED','motor':{'status':'ARRIVED'},'resourceCollected':False,'resourceDelivered':False}
        if stale:events.append({'kind':'MCP_COMPLETED','label':'feedback_fields','result':{'S':{'cycle':c},
            'feedback':{'outcome':'TOOL_NO_RESULT','materialConsequence':True}}})
        opp={'cycle':c,'state_after':copy.deepcopy(S),'world_result':wr,'Native_Q1':out_by_phase['decision'],
             'Native_Q2':out_by_phase['query_sensor'],'executed_route':out_by_phase['query_sensor']['action'],
             'Native_route':out_by_phase['query_sensor']['action'],'host_order_prepared':False}
        rows.append(opp);events.append({'kind':'OPPORTUNITY_COMPLETED',**opp})
        worldevents.append({'kind':'SYNTHETIC_ONLY','data':{'cycle':c}})
    world={'native_tick':tick if participant=='LIVE_NATIVE'else 0,'native_life_id':'SYNTHETIC',
      'S':S,'boundary':{'phase':'BOUNDARY'},'events':worldevents,'world_id':'R07'}
    (p/'events.jsonl').write_text('\n'.join(json.dumps(e)for e in events)+'\n','utf-8')
    (p/'result.json').write_text(json.dumps({'owner_closed':True,'source_tick':991187,
      'final_tick':tick if participant=='LIVE_NATIVE'else 0,'rows':rows}),'utf-8')
    (p/'world.json').write_text(json.dumps(world),'utf-8')
    block={k:str(p/f)for k,f in[('events','events.jsonl'),('result','result.json'),('world','world.json')]}
    return{'schema':'DEE.R07.recalculation.inputs.v1','parent_world':str(p/'parent.json'),
      'arms':[{'name':'SYNTHETIC_'+participant,'participant':participant,'sensor_arm':'local_tag','blocks':[block]}]}

class PassiveFixtures(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def analyze(self,spec):return run(spec,Sources(self.root))
    def test_01_dedup_ids_and_phase_ticks(self):
        spec=fixture(self.root/'case',duplicate=True)
        facts=self.analyze(spec);a=facts['arms'][0]
        self.assertEqual(facts['issues_total'],0);self.assertEqual(a['deduplicated_completed_operations'],3)
        self.assertEqual(a['duplicate_operation_localizers'],3);self.assertEqual(a['native_ticks_from_unique_phases'],1564)
    def test_02_old_resources_not_counted_and_no_carry(self):
        a=self.analyze(fixture(self.root/'case'))['arms'][0]
        self.assertEqual(a['delta']['resourceCount'],0);self.assertEqual(a['delta']['delivered'],0)
        self.assertEqual(a['parent_counters']['delivered'],3);self.assertEqual(a['inherited_delivery_credit'],0)
    def test_03_material_zero_is_correct_integer(self):
        a=self.analyze(fixture(self.root/'case',numeric=0))['arms'][0]
        self.assertEqual(a['formed_integer_outputs'],1);self.assertEqual(a['correct_given_actual_opcode'],1)
        self.assertEqual(a['numeric_no_integer'],0)
    def test_04_absent_numeric_is_not_wrong_arithmetic(self):
        a=self.analyze(fixture(self.root/'case',numeric='ABSENT'))['arms'][0]
        self.assertEqual(a['formed_integer_outputs'],0);self.assertEqual(a['wrong_given_actual_opcode'],0)
        self.assertEqual(a['numeric_no_integer'],1)
    def test_05_feedback_overrides_stale_summary_only_documentarily(self):
        a=self.analyze(fixture(self.root/'case',numeric='ABSENT',stale=True))['arms'][0]
        self.assertEqual(a['rows'][0]['outcome'],'TOOL_NO_RESULT')
        self.assertEqual(a['rows'][0]['world_result_locator']['source'],str(self.root/'case/events.jsonl'))
    def test_06_loop_two_three_and_fixed_criterion(self):
        a=self.analyze(fixture(self.root/'case',count=6,loop=True))['arms'][0]
        self.assertEqual(a['loop_2_3_transitions'],6)
        self.assertFalse(a['first6_P02']['sustained_exit_criterion_met'])
    def test_07_unoffered_not_scored(self):
        a=self.analyze(fixture(self.root/'case'))['arms'][0]
        self.assertEqual(a['completed_new'],1);self.assertEqual(a['completed_cycles'],[29])
        self.assertEqual(a['uncompleted_offered'],[])
    def test_08_valid_reference_wait_not_NULL(self):
        a=self.analyze(fixture(self.root/'case',participant='CONVENTIONAL_AI',wait=True))['arms'][0]
        self.assertEqual(a['phase_choice_counts']['voluntary_wait'],1)
        self.assertEqual(a['phase_choice_counts']['material_null'],0)
        self.assertEqual(a['native_ticks_from_unique_phases'],0)
    def test_09_refuses_live_or_unknown_owner(self):
        spec=fixture(self.root/'case');r=self.root/'case/result.json';v=json.loads(r.read_text());v['owner_closed']=False;r.write_text(json.dumps(v))
        with self.assertRaisesRegex(ValueError,'Only closed'):self.analyze(spec)
    def test_10_portable_manifest_no_original_read(self):
        spec=fixture(self.root/'original');package=self.root/'package';(package/'CONTROL').mkdir(parents=True)
        members=[]
        for n in('parent.json','events.jsonl','result.json','world.json'):
            src=self.root/'original'/n;data=src.read_bytes();dst=package/'EVIDENCIA'/n;dst.parent.mkdir(exist_ok=True);dst.write_bytes(data)
            members.append({'source':str(src),'archive':'EVIDENCIA/'+n,'sha256':hashlib.sha256(data).hexdigest()})
        members.append({'archive':'CONTROL/PROTECCION_CRITICOS.json','sha256':'0'*64,'role':'verification'})
        (package/'CONTROL/MANIFIESTO_SHA256.json').write_text(json.dumps({'members':members}))
        # Historical source names remain in spec, but source originals are now unreadable by relocation.
        original=self.root/'original';moved=self.root/'not_original';original.rename(moved)
        facts=run(spec,Sources(self.root,package))
        self.assertEqual(facts['issues_total'],0)
        self.assertTrue(all(str(package)in x['resolved']for x in facts['sources']))
    def test_11_common_observed_prefix_not_projected(self):
        s1=fixture(self.root/'native',count=2);s2=fixture(self.root/'program',participant='PROGRAMMED',count=1)
        s1['arms']+=s2['arms'];facts=self.analyze(s1)
        self.assertEqual(facts['common_observed_cycles'],[29])
        self.assertEqual([x['completed']for x in facts['comparison']if x['scope']=='FULL_OBSERVED'],[2,1])
    def test_12_source_changes_and_fresh_output_guards(self):
        spec=fixture(self.root/'case');source=Sources(self.root);facts=run(spec,source)
        p=self.root/'case/world.json';p.write_text(p.read_text()+' ')
        with self.assertRaisesRegex(ValueError,'changed'):source.verify_unchanged()
        output=self.root/'output';save_outputs(output,facts)
        with self.assertRaisesRegex(ValueError,'Fresh analysis'):save_outputs(output,facts)
    def test_13_fixed_encoder_recalculation_not_retuned(self):
        spec=fixture(self.root/'case',count=2,loop=True)
        main=self.analyze(spec)['arms'][0]
        self.assertEqual(main['rows'][0]['q2_datum_recalculated_from_frozen_contract'],7)
        self.assertEqual(main['rows'][1]['q2_datum_recalculated_from_frozen_contract'],10)
        spec['arms'][0]['sensor_arm']='constant_tag2'
        control=self.analyze(spec)['arms'][0]
        self.assertEqual(control['rows'][0]['q2_datum_recalculated_from_frozen_contract'],7)
        self.assertEqual(control['rows'][1]['q2_datum_recalculated_from_frozen_contract'],7)
    def test_14_paired_control_does_not_claim_all_three_or_equal_dose(self):
        spec=fixture(self.root/'main',count=6,loop=True)
        ctrl=fixture(self.root/'control',count=6,loop=True)['arms'][0]
        ctrl.update(name='SYNTHETIC_CONTROL',sensor_arm='constant_tag2');spec['arms'].append(ctrl)
        facts=self.analyze(spec);pair=facts['P02_paired_comparisons'][0]
        self.assertFalse(facts['has_all_three_configurations'])
        self.assertTrue(pair['first_contract_datum_equal'])
        self.assertTrue(pair['Native_physical_prefix_equality_requires_import0_proof'])
        self.assertIn('endogenously',pair['dose_note'])

if __name__=='__main__':unittest.main(verbosity=2)
