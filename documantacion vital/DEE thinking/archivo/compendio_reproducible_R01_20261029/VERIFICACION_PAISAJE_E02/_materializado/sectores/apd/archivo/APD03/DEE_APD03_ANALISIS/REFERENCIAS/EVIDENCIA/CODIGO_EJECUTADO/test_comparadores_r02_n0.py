"""Public-fence fixtures, not MAIN results or Native experiments."""
import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('reference_r02',Path(__file__).with_name('comparadores_apd03_r02.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


def fixture():
    events=[]
    for i in range(4):
        acts=['ACT']if i==1 else['ACT','QUERY']
        event={'kind':'task','task_id':'fixture_'+str(i),'text':'suma','left':5+i,'second':3,
            'second_initially_public':i!=3,'context':i%2,'required_operation':'add','max_opportunities':1 if i==1 else 4,
            'opportunity_invocations':[1]if i==1 else[1,3],
            'origin_block':'FIXTURE','scheduled_enabled_seconds':i,'feedback':'omit'if i==3 else'real',
            'feedback_mode':'file_quality'if i==1 else'local_useful','allowed_procedures':['native','external'],
            'public_resources':{'allowed_actions':acts,'allowed_procedures':['native','external'],'query_price':0},
            'laws':{route:{'price':1,'delay_ticks':0,'available':True}for route in c.base.ROUTES},
            'faults':{'native':'wrong_value'if i==1 else'none','external':'none'}}
        events.append(event)
    return {'schema':'DEE.APD03.common_task_program.R01','derived_without_Main_outcomes':True,'events':events,
        'preparation':{'prior_knowledge':[{'text':'suma','operation':'add'}]}}


class Fixtures(unittest.TestCase):
    def test_magnitude_context_hidden_laws_invariant(self):
        original=fixture()['events'][0]
        for name in c.POLICIES:
            for missing in(False,True):
                outcomes=[];projections=[]
                for left,second,ctx in((0,0,0),(32,31,1),(17,9,None)):
                    event=copy.deepcopy(original);event.update(left=left,second=second,context=ctx)
                    event['faults']['native']='wrong_value';event['laws']['native']['available']=False
                    p=c.POLICIES[name]();p.teach({'text':'suma','operation':'add'});p.begin_task()
                    obs=c.projection(event,None if missing else second);projections.append(obs);outcomes.append(p.choose(obs))
                self.assertEqual(outcomes,[outcomes[0]]*3);self.assertEqual(projections,[projections[0]]*3)

    def test_fixed_respects_action_only(self):
        p=c.Fixed();p.teach({'text':'suma','operation':'add'});p.begin_task()
        event=fixture()['events'][1];obs=c.projection(event,event['second'])
        self.assertEqual(p.choose(obs),{'kind':'ACT','operation':'add','procedure':'native'})

    def test_binary_feedback_fence(self):
        p=c.base.WinStayLoseShift()
        with self.assertRaises(ValueError):p.feedback({}, {'kind':'ACT'}, {'category':'FAILURE','right_route':'external'})

    def test_three_fixture_rollouts_and_archived_files(self):
        with tempfile.TemporaryDirectory(prefix='dee_apd03_reference_r02_')as folder:
            root=Path(folder);program=root/'fixture.json';program.write_bytes(c.base.canonical(fixture()))
            for name in c.POLICIES:
                out=root/name;summary=c.run(program,out,name);recalc=c.recalculate(out)
                self.assertEqual(recalc['issues'],0);self.assertEqual(summary['task_count'],4)
                self.assertLess(summary['process_total']['peak_working_set_bytes_process_to_date'],256*1024**2)
                rows=[json.loads(line)for line in(out/'eventos_primarios.jsonl').read_bytes().splitlines()]
                omitted=[r for r in rows if r['kind']=='opportunity'and r['task_id']=='fixture_3']
                self.assertTrue(omitted);self.assertTrue(all(r['public_return']is None and not r['return_delivered']for r in omitted))
                self.assertTrue(all(r['policy_state_after']=={**r['policy_state_before'],'queries':r['policy_state_after']['queries']}
                    for r in omitted))
                self.assertTrue(all(r['committed_action']['kind']=='ACT'for r in rows if r['kind']=='opportunity'and r['task_id']=='fixture_1'))
                self.assertTrue(list((out/'artifacts').glob('*.json')))


if __name__=='__main__':unittest.main()
