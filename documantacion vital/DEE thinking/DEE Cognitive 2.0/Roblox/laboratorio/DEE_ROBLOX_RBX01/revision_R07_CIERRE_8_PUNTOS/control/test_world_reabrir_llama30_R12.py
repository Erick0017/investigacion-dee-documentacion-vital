"""Pure fixtures; no Studio, Native, model or actual policy history is opened."""
from pathlib import Path
import copy,importlib.util,unittest
p=Path(__file__).with_name('world_reabrir_llama30_R12.py');s=importlib.util.spec_from_file_location('r12_fixture_world',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def state():
    return {'physical':{'parts':[{'path':n,'canCollide':bool(i%2),'attributes':{'R07PreparedBody':True}}for i,n in enumerate(sorted(m.LIMBS))]}}
class Mask(unittest.TestCase):
    def test_saved_false_and_true_exact(self):
        rows,indices=m.saved_mask(state());self.assertEqual(len(rows),4);self.assertEqual({r['canCollide']for r in rows},{False,True})
    def test_missing_rejected(self):
        x=state();x['physical']['parts'].pop()
        with self.assertRaises(ValueError):m.saved_mask(x)
    def test_nonboolean_rejected(self):
        x=state();x['physical']['parts'][0]['canCollide']=0
        with self.assertRaises(ValueError):m.saved_mask(x)
    def test_only_collision_difference_permitted(self):
        x=state();old=x['physical']['parts'][0]['canCollide'];m.require_only_collision_diffs({'differences':[{'path':'physical.parts[0].canCollide','before':old,'after':not old}]},x)
        with self.assertRaises(ValueError):m.require_only_collision_diffs({'differences':[{'path':'S.permissionStock','before':163,'after':164}]},x)
    def test_zero_difference_does_not_need_relaxation(self):self.assertEqual(len(m.require_only_collision_diffs({'differences':[]},state())),4)
    def test_generated_hook_no_route_or_clock_write(self):
        code=m.repair_code(state());self.assertIn('hook.applySavedMask',code);self.assertNotIn('PivotTo(',code);self.assertNotIn('MoveTo(',code);self.assertNotIn('set_snapshot_metadata',code)
    def test_original_comparator_still_rejects_boolean(self):
        x={'physical':{'parts':[{'canCollide':False}]}};y=copy.deepcopy(x);y['physical']['parts'][0]['canCollide']=True
        self.assertFalse(m.BASE.compare_values(x,y)['equal_with_declared_geometry_tolerance'])
if __name__=='__main__':unittest.main()
