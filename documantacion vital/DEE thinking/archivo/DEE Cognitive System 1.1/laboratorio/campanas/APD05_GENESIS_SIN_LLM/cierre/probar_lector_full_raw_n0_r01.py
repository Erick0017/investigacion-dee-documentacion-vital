"""N0 reader tests. Synthetic fields are never imported into a DEE world."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).with_name('recalcular_prueba_full_genesis_raw_n0_r01.py')
spec = importlib.util.spec_from_file_location('full_raw_reader', path)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def raw(direction):
    value = 1 | (7 << 32) | (1 << 60)
    for shift, component in zip((48,52,56), direction): value |= (component & 15) << shift
    return str(value)


def panel(codec=reader.CODEC36):
    return [{'site':list(site),'raw':'0','clock':'42','tick':42} for site in reader.gates(codec)]


class Tests(unittest.TestCase):
    def test_common36_single_positive(self):
        rows=panel(); signs=reader.gates(reader.CODEC36)
        row=next(row for row in rows if signs[tuple(row['site'])]==1);row['raw']=raw([0,0,1])
        value=reader.decode_lexical({'panel':rows,'formed_native_command':1},42)
        self.assertEqual(value['formed_from_RAW'],1);self.assertTrue(value['exact_frozen_geometry'])

    def test_wrong_sign_gate_never_candidate(self):
        rows=panel();signs=reader.gates(reader.CODEC36)
        next(row for row in rows if signs[tuple(row['site'])]==1)['raw']=raw([0,0,-1])
        value=reader.decode_lexical({'panel':rows},42)
        self.assertIsNone(value['formed_from_RAW']);self.assertEqual(value['candidates_from_RAW'],[])

    def test_two_emissions_are_ambiguous_not_zero(self):
        rows=panel();signs=reader.gates(reader.CODEC36)
        for sign in(-1,1):next(row for row in rows if signs[tuple(row['site'])]==sign)['raw']=raw([0,0,sign])
        value=reader.decode_lexical({'panel':rows},42)
        self.assertIsNone(value['formed_from_RAW']);self.assertTrue(value['ambiguous_from_RAW'])

    def test_incomplete_geometry_is_not_a_decoder(self):
        rows=panel();rows.pop();value=reader.decode_lexical({'panel':rows},42)
        self.assertFalse(value['exact_frozen_geometry']);self.assertIsNone(value['formed_from_RAW'])

    def test_common24_is_distinct_supported_domain(self):
        rows=panel(reader.CODEC24);signs=reader.gates(reader.CODEC24)
        next(row for row in rows if signs[tuple(row['site'])]==-1)['raw']=raw([0,0,-1])
        value=reader.decode_lexical({'panel':rows},42)
        self.assertEqual(value['common_gate_count'],24);self.assertEqual(value['formed_from_RAW'],-1)

    def test_rejected_query_not_usable_by_resident_sign(self):
        value=reader.admission([{'channel':'cue.x','receipt':{'status':'rejected_occupied'}}]*4)
        self.assertEqual(value['applied'],0);self.assertEqual(value['rejected'],4)
        self.assertFalse(value['all_declared_inputs_applied'])

    def test_clock_cannot_be_float(self):
        rows=panel();rows[0]['clock']=42.0
        with self.assertRaises(ValueError):reader.decode_lexical({'panel':rows},42)

    def test_reported_field_disagreement_invalidates_emission(self):
        rows=panel();signs=reader.gates(reader.CODEC36)
        row=next(row for row in rows if signs[tuple(row['site'])]==1)
        row['raw']=raw([0,0,1]);row['state']=999
        value=reader.decode_lexical({'panel':rows},42)
        self.assertIsNone(value['formed_from_RAW']);self.assertTrue(value['field_decode_mismatches'])


if __name__=='__main__':unittest.main(verbosity=2)
