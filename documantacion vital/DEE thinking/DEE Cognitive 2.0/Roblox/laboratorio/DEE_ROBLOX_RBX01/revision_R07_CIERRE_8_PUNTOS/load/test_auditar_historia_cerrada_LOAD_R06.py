"""Small offline fixtures for actual-admission reporting; no Native dependency."""
from pathlib import Path
import importlib.util, json, tempfile, unittest

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('auditar_historia_cerrada_LOAD_R06.py'))
audit = importlib.util.module_from_spec(spec); spec.loader.exec_module(audit)


class ActualAdmission(unittest.TestCase):
    def fixture(self, root, kind='LESSON'):
        context = dict(operation_id='x', session_id='s', sequence=58, observation_id='o', mode='LIVE_NATIVE')
        request = dict(id=1, channel='teacher.x.1', tick=13, value=11, site=[1,2,3],
                       direction=[0,0,1], receipt=dict(status='rejected_occupied'))
        record = dict(life_id='life', context=context, visible_tool=dict(kind=kind),
                      before_tick=10, after_tick=20, input_admission_complete=False,
                      Native_inputs=dict(applied=0, rejected=1),
                      requests_normalized=[dict(channel='teacher.x.1', payload=11, requested_tick=13,
                                                receipt=dict(status='rejected_occupied'))],
                      public_tool_result=dict(kind=kind, memory_value=-1, numeric_result=0,
                                              operation='diferencia', inputs=[2,2], reason='observed'),
                      native_function=[dict(form='x', observed_sign=1, before_tick=10, after_tick=20,
                                            native_lesson=dict(requests=[request]))])
        path = root/'sistema/estado/servicios_locales/life/RBX07_NATIVE_INTEGRAL_V3/functions/x.json'
        path.parent.mkdir(parents=True); path.write_text(json.dumps(record), encoding='utf8')
        return context, record, path

    def test_offered_sign_does_not_override_rejected_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); context,_,_=self.fixture(root)
            result=audit.function_primary(root,'life',dict(context=context))
            self.assertEqual(result['lexical_exposures'][0]['offered_sign'],1)
            self.assertFalse(result['lexical_exposures'][0]['all_inputs_applied'])
            self.assertEqual(result['lexical_exposures'][0]['requests'][0]['receipt']['status'],'rejected_occupied')

    def test_actual_numeric_zero_survives(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); context,_,_=self.fixture(root,'CALCULATE')
            result=audit.function_primary(root,'life',dict(context=context))
            self.assertIs(type(result['actual_composition']['numeric_result']),int)
            self.assertEqual(result['actual_composition']['numeric_result'],0)

    def test_wrong_life_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); context,record,path=self.fixture(root)
            record['life_id']='other'; path.write_text(json.dumps(record),encoding='utf8')
            with self.assertRaisesRegex(ValueError,'EXACT_FUNCTION_LIFE_AND_CONTEXT'):
                audit.function_primary(root,'life',dict(context=context))


if __name__=='__main__':unittest.main()
