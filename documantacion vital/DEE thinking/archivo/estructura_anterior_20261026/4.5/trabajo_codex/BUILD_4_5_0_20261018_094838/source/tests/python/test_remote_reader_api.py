"""Finite experimental reader; no unbounded-language claim is evaluated."""
from pathlib import Path
import tempfile
import unittest
from dee_thinking.remote_reader import RemoteReaderSession
from dee_thinking.consolidated import load_nsm_catalogue,load_nsm_scope


def physics(s):
    r=s.world.runtime
    return r.current_tick,r.raw_copy(),r.clock_copy()


def prepared(q,*,source_mode='paired',name_mode='paired',reader=True,repeat=True):
    s=RemoteReaderSession.create()
    s.experience_order('BA',reader=reader)
    s.acquire_sources(1,q,mode=source_mode)
    s.late_use()
    s.run_until(5);s.consequence(1)
    s.run_until(34);s.teach_first_form(mode=name_mode)
    s.query_first_form(tick=50)
    s.learn_second_form()
    if repeat:s.query_first_form(tick=117)
    return s


def values(s,kind,tick):
    rows=[r for r in s.readings if r['kind']==kind and r['tick']==tick]
    if not rows:return []
    return [v['value'] for v in rows[0]['captured']['responses'] if v['covered']]


class RemoteReaderTests(unittest.TestCase):
    def test_documentary_catalogue_is_not_training(self):
        cat=load_nsm_catalogue();scope=load_nsm_scope()
        self.assertEqual(cat['count'],65);self.assertEqual(len(cat['entries']),65)
        self.assertEqual(len({e['id'] for e in cat['entries']}),65)
        self.assertEqual(scope['kind'],'DOCUMENTARY_RESOURCE_NOT_PARTICIPANT_MEMORY')
        self.assertTrue(all(e['DEE_thinking_4_5_0']['new_NSM_semantic_experiment']=='NOT_PERFORMED_IN_THIS_PRODUCT_PORT' for e in scope['entries']))

    def test_reserved_current_source_contents_and_new_association(self):
        for q in(-1,1):
            s=prepared(q);s.run_until(162)
            self.assertEqual(values(s,'first_form',53),[q])
            self.assertEqual(len(values(s,'second_form',90)),1)
            self.assertEqual(values(s,'remote_reader',162),[q])

    def test_unpaired_opaque_name_retains_negative_result(self):
        s=prepared(-1,name_mode='unpaired');s.run_until(162)
        self.assertEqual(values(s,'remote_reader',162),[])
        self.assertTrue(any(r['receipt']['status']=='applied' for r in s.receipts()))

    def test_no_source_experience_or_no_renewed_request(self):
        s=prepared(-1,source_mode='omitted');s.run_until(162)
        self.assertEqual(values(s,'remote_reader',162),[])
        s=prepared(-1,repeat=False);s.run_until(162)
        # Inspect the actual current physical target, not a missing capture row.
        self.assertEqual([r['value'] for r in s.read_current_reader()['responses'] if r['covered']],[])

    def test_remote_cut_sham_save_load_do_not_replace_MAIN(self):
        s=prepared(-1);s.run_until(160);before=physics(s)
        cut=s.diagnostic_remote_cut();sham=s.diagnostic_remote_cut(sham=True)
        self.assertEqual(physics(s),before)
        self.assertEqual(physics(sham),before)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'remote.deetsnap.gz';s.save_snapshot(p)
            restored=RemoteReaderSession.load_snapshot(p)
            self.assertEqual(physics(restored),physics(s))
            self.assertEqual(restored.readings,s.readings)
            restored.run_until(162);s.run_until(162);cut.run_until(162);sham.run_until(162)
            self.assertEqual(physics(restored),physics(s))
            self.assertEqual(values(s,'remote_reader',162),[-1])
            self.assertEqual(values(sham,'remote_reader',162),[-1])
            self.assertEqual(values(cut,'remote_reader',162),[])


if __name__=='__main__':unittest.main()
