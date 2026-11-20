"""Pure instrument/parser regressions. These are not physical experiments."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.console import exact_text,integer,Instrument

class ContractTests(unittest.TestCase):
    def test_exact_uint64_string_preserved(self):
        self.assertEqual(exact_text('{"raw":"18446744073709551615"}')['raw'],'18446744073709551615')
    def test_reject_float_nan_and_duplicate(self):
        for text in ('{"tick":1.5}','{"tick":NaN}','{"tick":Infinity}','{"tick":1,"tick":2}'):
            with self.subTest(text=text),self.assertRaises(ValueError):exact_text(text)
    def test_bool_not_integer(self):
        for x in (True,False,1.0,'1',-1):
            with self.subTest(value=x),self.assertRaises(ValueError):integer(x,'field')
        self.assertEqual(integer(65535,'field'),65535)
    def test_targets_not_accepted_as_event_fields(self):
        # Field validation runs before a world can be requested or accessed.
        app=object.__new__(Instrument)
        with self.assertRaises(ValueError):app._apply({'op':'nuevo','target':'the answer'})
    def test_unknown_operation_not_executed(self):
        app=object.__new__(Instrument)
        with self.assertRaises(ValueError):app._apply({'op':'execute_python','code':'print(1)'})

if __name__=='__main__':unittest.main()
