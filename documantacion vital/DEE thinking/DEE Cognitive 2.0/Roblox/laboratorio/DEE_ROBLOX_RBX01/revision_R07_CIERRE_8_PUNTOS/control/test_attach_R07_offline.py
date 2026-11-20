"""Identity/sequence and transport-only adoption fixtures. No Native/MCP."""
from pathlib import Path
import ast,copy,importlib.util,unittest
P=Path(__file__).with_name('run_integrated_v3_R07_attach.py')
spec=importlib.util.spec_from_file_location('attach_pure',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Guards(unittest.TestCase):
    def values(self):
        return dict(native_life_id=m.LIFE,native_tick=1000571,boundary=dict(next_opportunity=35),S=dict(seq=68,sessionId=m.SID)),dict(life=m.LIFE,session=m.SID,participant='LIVE_NATIVE')
    def test_original_identity_and_next35(self):
        state,identity=self.values();m.guard_identity(state,identity,m.SOURCE_SHA)
    def test_old_or_future_sequence_rejected(self):
        for seq in(56,67,69):
            state,identity=self.values();state['S']['seq']=seq
            with self.assertRaises(ValueError):m.guard_identity(state,identity,m.SOURCE_SHA)
    def test_wrong_session_or_source_rejected(self):
        state,identity=self.values();identity['session']='other'
        with self.assertRaises(ValueError):m.guard_identity(state,identity,m.SOURCE_SHA)
        state,identity=self.values()
        with self.assertRaises(ValueError):m.guard_identity(state,identity,'0'*64)
    def test_adoption_method_never_initializes_or_submits_action(self):
        tree=ast.parse(P.read_text('utf8'));cls=next(n for n in ast.walk(tree)if isinstance(n,ast.ClassDef)and n.name=='AttachedWorld')
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='initialize')
        attrs=[n.func.attr for n in ast.walk(method)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)]
        self.assertNotIn('initialize',attrs);self.assertNotIn('call',attrs)
        self.assertIn('checkpoint',attrs);self.assertIn('compare',attrs)
if __name__=='__main__':unittest.main()
