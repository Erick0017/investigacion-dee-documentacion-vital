"""Bounded SAME-byte rename and actual concurrent readers; no DEE or Native."""
from pathlib import Path
import json
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import sdk_common as c

class Sharing(OSError): winerror=32
class Access(OSError): winerror=5
class Atomic(unittest.TestCase):
    def test_sharing_retries_same_bytes_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'row.json';real=c.os.replace;seen=[]
            def replace(a,b):
                seen.append(Path(a).read_bytes())
                if len(seen)<3:raise Sharing('synthetic reader')
                return real(a,b)
            with patch.object(c.os,'replace',side_effect=replace):c.atomic(p,{'status':'RUNNING','id':'same'})
            self.assertEqual(len(seen),3);self.assertTrue(all(x==seen[0] for x in seen));self.assertEqual(c.read(p)['id'],'same')
    def test_exhausted_keeps_writing_and_original(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'row.json';p.write_text('{"status":"PENDING"}')
            with patch.object(c.os,'replace',side_effect=Access('synthetic ACL')),patch.object(c.time,'monotonic',side_effect=[0,3]):
                with self.assertRaises(Access):c.atomic(p,{'status':'RUNNING'})
            self.assertEqual(c.read(p)['status'],'PENDING');self.assertEqual(c.read(Path(str(p)+'.WRITING'))['status'],'RUNNING')
    def test_other_errors_not_retried(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'row.json'
            with patch.object(c.os,'replace',side_effect=OSError('other')) as replace:
                with self.assertRaises(OSError):c.atomic(p,{'x':1})
                self.assertEqual(replace.call_count,1)
    def test_real_reader_writer_stress(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'row.json';c.atomic(p,{'n':0});stop=threading.Event();errors=[]
            def reader():
                while not stop.is_set():
                    try:
                        row=c.read(p)
                        if type(row['n']) is not int:errors.append('badrow')
                    except BaseException as error:errors.append(repr(error))
                    time.sleep(.001)
            thread=threading.Thread(target=reader);thread.start()
            try:
                for n in range(1,81):c.atomic(p,{'n':n})
            finally:stop.set();thread.join(5)
            self.assertFalse(thread.is_alive());self.assertEqual(errors,[]);self.assertEqual(c.read(p)['n'],80)
    def test_read_only_sharing_retry(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'row.json';p.write_text('{"x":1}');real=Path.read_text;calls=[]
            def read_text(path,*args,**kwargs):
                calls.append(str(path))
                if len(calls)<3:raise Sharing('synthetic rename overlap')
                return real(path,*args,**kwargs)
            with patch.object(Path,'read_text',read_text):self.assertEqual(c.read(p),{'x':1})
            self.assertEqual(calls,[str(p)]*3)

if __name__=='__main__':unittest.main(verbosity=2)
