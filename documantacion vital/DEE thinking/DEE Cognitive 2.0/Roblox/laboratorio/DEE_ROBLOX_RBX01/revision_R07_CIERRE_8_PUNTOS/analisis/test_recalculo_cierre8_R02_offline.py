"""Inherited passive fixtures plus synthetic recovery fragments. No Native/SDK."""
from pathlib import Path
import hashlib
import json
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_recalculo_cierre8_R07_offline as base
from RECALCULO_CIERRE8_R07_R02 import Sources,run,save_outputs
base.Sources=Sources
base.run=run
base.save_outputs=save_outputs

class FragmentFixtures(base.PassiveFixtures):
    def recovered(self):
        spec=base.fixture(self.root/'case',count=6,loop=True)
        block=spec['arms'][0]['blocks'][0]
        events=Path(block.pop('events'))
        rows=[json.loads(x)for x in events.read_text('utf-8').splitlines()]
        # Cycle34 Q1 was really executed in the original file; resume has only Q2/feedback.
        split=next(i+1 for i,e in enumerate(rows)if e.get('cycle')==34 and e.get('kind')=='NATIVE_COMPLETED' and e.get('phase')=='decision')
        a=self.root/'case/original.jsonl';b=self.root/'case/continuation.jsonl'
        a.write_text('\n'.join(json.dumps(x)for x in rows[:split])+'\n','utf-8')
        b.write_text('\n'.join(json.dumps(x)for x in rows[split:])+'\n','utf-8')
        block['event_fragments']=[str(a),str(b)]
        return spec
    def test_15_recovered_six_full_cycles_no_Q1_replay(self):
        spec=self.recovered();facts=self.analyze(spec);a=facts['arms'][0]
        self.assertEqual(facts['issues_total'],0)
        self.assertEqual(a['completed_new'],6)
        self.assertEqual(a['deduplicated_completed_operations'],18)
        self.assertEqual(a['native_ticks_from_unique_phases'],9384)
        loc=a['native_tick_checks'][-3]['operation_id']
        self.assertEqual(loc,'SYNTH_34_decision')
        self.assertEqual(a['rows'][-1]['source']['source'],spec['arms'][0]['blocks'][0]['event_fragments'][1])
    def test_16_duplicate_completion_document_is_not_new_tick(self):
        spec=self.recovered();keys=spec['arms'][0]['blocks'][0]['event_fragments']
        old=[json.loads(x)for x in Path(keys[0]).read_text().splitlines()]
        q1=next(e for e in old if e.get('cycle')==34 and e.get('kind')=='NATIVE_COMPLETED')
        p=Path(keys[1]);p.write_text(json.dumps(q1)+'\n'+p.read_text())
        a=self.analyze(spec)['arms'][0]
        self.assertEqual(a['native_ticks_from_unique_phases'],9384)
        self.assertEqual(a['duplicate_operation_localizers'],1)
    def test_17_fragment_portable_without_originals(self):
        spec=self.recovered();block=spec['arms'][0]['blocks'][0]
        keys=[spec['parent_world'],block['result'],block['world'],*block['event_fragments']]
        package=self.root/'pkg';(package/'CONTROL').mkdir(parents=True);members=[]
        for i,key in enumerate(keys):
            raw=Path(key).read_bytes();name='EVIDENCIA/'+str(i)+'.txt'
            target=package/name;target.parent.mkdir(exist_ok=True);target.write_bytes(raw)
            members.append({'source':key,'archive':name,'sha256':hashlib.sha256(raw).hexdigest()})
        (package/'CONTROL/MANIFIESTO_SHA256.json').write_text(json.dumps({'members':members}))
        (self.root/'case').rename(self.root/'old_sources_unavailable')
        facts=run(spec,Sources(self.root,package))
        self.assertEqual(facts['issues_total'],0)
        self.assertEqual(facts['arms'][0]['native_ticks_from_unique_phases'],9384)
        self.assertTrue(all(str(package)in s['resolved']for s in facts['sources']))
    def test_18_ambiguous_fragments_refused(self):
        spec=self.recovered();block=spec['arms'][0]['blocks'][0]
        block['events']=block['event_fragments'][0]
        with self.assertRaisesRegex(ValueError,'never both'):self.analyze(spec)

if __name__=='__main__':unittest.main(verbosity=2)
