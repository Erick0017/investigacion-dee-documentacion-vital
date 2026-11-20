"""Published 4.5 session protocols; expected data is confined to tests."""
import gzip
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import dee_thinking as d
from dee_thinking.consolidated import (RepertoireSession, IntegratedSession,
    load_consolidated_session)
from dee_thinking.persistence import (decode_metadata, encode_metadata,
    inspect_snapshot, materialized_snapshot)


def physics(s):
    r=s.world.runtime
    return r.current_tick,r.raw_copy(),r.clock_copy()


class ConsolidatedApiTests(unittest.TestCase):
    def test_exact_metadata_validation(self):
        v={"clock":2**64-1,"raw":"18446744073709551615","vector":[-1,0,1]}
        self.assertEqual(decode_metadata(encode_metadata(v)),v)
        for bad in ({"tick":1.0},{"x":2**64},{"x":object()}):
            with self.assertRaises((TypeError,ValueError)):encode_metadata(bad)
        for text in ('{"x":1,"x":2}','{"tick":1.0}','{"x":NaN}'):
            with self.assertRaises(ValueError):decode_metadata(text)
        with self.assertRaises(ValueError):decode_metadata('"'+'x'*50+'"',max_bytes=10)

    def test_acquire_repeated_query_and_passive_observation(self):
        for sign in(-1,1):
            s=RepertoireSession.create(count=2)
            initial=physics(s)
            for _ in range(3):s.observe()
            self.assertEqual(initial,physics(s))
            s.acquire_block({"L01":sign,"L02":-sign},0)
            s.run_until(3)
            for at in(67,134,201):
                rows=s.query(["L01","L02"],at)["responses"]
                self.assertEqual([r["value"] for r in rows],[sign,-sign])
                self.assertTrue(all(r["covered"] and r["receipt"]["status"]=="applied" for r in rows))

    def test_unpaired_and_absence_do_not_become_numeric_zero(self):
        for mode in("unpaired","no_event","no_symbol"):
            s=RepertoireSession.create(count=2)
            s.acquire("L01",1,0,mode=mode)
            r=s.query("L01",67)["responses"][0]
            self.assertFalse(r["covered"])
            self.assertIsNone(r["value"])
            self.assertIn("status",r)

    def test_finite_revision_both_methods_retains_other_relation(self):
        for method in("double_teacher","symmetric_counterflow"):
            for sign in(-1,1):
                s=RepertoireSession.create(count=2)
                s.acquire_block({"L01":-sign,"L02":sign},0)
                old=s.query(["L01","L02"],67)
                self.assertEqual([r["value"] for r in old["responses"]],[-sign,sign])
                s.revise("L01",sign,268,method=method)
                new=s.query(["L01","L02"],335)
                self.assertEqual([r["value"] for r in new["responses"]],[sign,sign])
                if method=="symmetric_counterflow":
                    counter=[r for r in s.journal if any('.counter.' in c for c in r['channels'])]
                    self.assertEqual(len(counter),2)
                    self.assertTrue(all(r['payload']==0 and r['requested_tick']==264 for r in counter))

    def test_pending_query_gzip_restore_and_deep_fork(self):
        s=RepertoireSession.create(count=2)
        s.acquire_block({"L01":-1,"L02":1},0)
        q=s.schedule_query(["L01","L02"],67)
        s.run_until(68)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"continuidad.deetsnap.gz"
            proof=s.save_snapshot(path)
            self.assertTrue(proof['gzip_crc_verified'])
            restored=load_consolidated_session(path,expected_sha256=proof['decoded_sha256'])
            self.assertEqual(physics(restored),physics(s))
            self.assertEqual(restored.queries,s.queries)
            s.run_until(70);restored.run_until(70)
            self.assertEqual(physics(restored),physics(s))
            self.assertEqual(restored.queries,s.queries)
            self.assertEqual(restored.queries[0]['id'],q['id'])
            self.assertEqual([r['value'] for r in restored.queries[0]['captured']['responses']],[-1,1])
            before=path.read_bytes()
            with self.assertRaises(FileExistsError):s.save_snapshot(path)
            self.assertEqual(path.read_bytes(),before)
            child=s.fork()
            self.assertEqual(physics(child),physics(s))
            child.query('L01',134)
            self.assertEqual(s.tick,70)
            self.assertNotEqual(child.tick,s.tick)

    def test_invalid_inputs_do_not_schedule_partial_blocks(self):
        s=RepertoireSession.create(count=2)
        before=physics(s)
        for args in(("L01",True,0),("L01",1,False),("L01",1.0,0),("L99",1,0)):
            with self.assertRaises((ValueError,TypeError)):s.acquire(*args)
        with self.assertRaises(ValueError):s.acquire_block({'L01':1,'L99':-1},0)
        with self.assertRaises(ValueError):s.schedule_query(['L01','L01'],67)
        self.assertEqual(s.journal,[])
        self.assertEqual(before,physics(s))
        for count in(0,66,True):
            with self.assertRaises((TypeError,ValueError)):RepertoireSession.create(count=count)

    def test_snapshot_crc_bounds_and_hash(self):
        s=RepertoireSession.create(count=1)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'one.deetsnap.gz';s.save_snapshot(p)
            with self.assertRaises(ValueError):inspect_snapshot(p,max_bytes=1)
            with self.assertRaises(ValueError):inspect_snapshot(p,expected_sha256='0'*64)
            broken=Path(tmp)/'truncated.deetsnap.gz';broken.write_bytes(p.read_bytes()[:-5])
            with self.assertRaises(ValueError):load_consolidated_session(broken)
            wrong=Path(tmp)/'not_native.deetsnap.gz'
            with gzip.open(wrong,'wb') as stream:stream.write(b'not a native snapshot')
            with self.assertRaises((ValueError,RuntimeError)):load_consolidated_session(wrong)

    def test_other_process_continuation(self):
        s=RepertoireSession.create(count=2)
        s.acquire_block({'L01':1,'L02':-1},0)
        s.schedule_query(['L01','L02'],67);s.run_until(68)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'pending.deetsnap.gz';s.save_snapshot(path)
            code=('import json;from dee_thinking.consolidated import load_consolidated_session;'
                  's=load_consolidated_session('+repr(str(path))+');s.run_until(70);'
                  'print(json.dumps([r["value"] for r in s.queries[0]["captured"]["responses"]]))')
            result=subprocess.run([sys.executable,'-I','-B','-c',code],capture_output=True,text=True,timeout=60,check=True)
            self.assertEqual(json.loads(result.stdout),[1,-1])

    def test_integrated_current_information_then_name_and_revision(self):
        values=[1,-1,-1,1,1,1,-1,-1,-1,1,1,-1,-1,1,-1,1]
        s=IntegratedSession.create()
        s.experience_order('AB')
        s.acquire_block({f'L{i+1:02d}':values[i] for i in range(8)},0)
        s.run_until(11);s.consequence(-1)
        s.run_until(69);s.action()
        s.run_until(72);s.teach_form()
        s.run_until(134);s.acquire_block({f'L{i+1:02d}':values[i] for i in range(8,16)},134)
        words=s.query_form(139)
        self.assertEqual(sum(r['covered'] for r in words['responses']),1)
        lower=[f'L{i:02d}' for i in range(3,17)]
        first=s.query(lower,201)
        second=s.query(lower,335)
        self.assertEqual([r['value'] for r in first['responses']],values[2:])
        self.assertEqual([r['value'] for r in second['responses']],values[2:])
        s.revise('L03',1,402)
        final=s.query(lower,469)
        self.assertEqual([r['value'] for r in final['responses']],[1]+values[3:])
        self.assertEqual(s.tick,472)


if __name__=='__main__':unittest.main()
