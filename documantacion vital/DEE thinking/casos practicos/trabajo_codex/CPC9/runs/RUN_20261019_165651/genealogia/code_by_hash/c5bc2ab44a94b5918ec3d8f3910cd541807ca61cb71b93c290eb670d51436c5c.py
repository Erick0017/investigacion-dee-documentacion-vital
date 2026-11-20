"""Causal use of old operands late in actual E1, not mere visible remnants."""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,json,sys,gc
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from dee_thinking import _native as d
from vida_repertorio_extension import MainWithRepertoire
from integracion.relational_pair import physical,move
from audit_primary import one_step
from ejecutar_retorno import write
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    source=ROOT/'resultados/continuacion/E1_MAIN_K65_1907_2353';data=json.loads((source/'MEDICIONES.json').read_text());path=source/'T2219.deetsnap.gz'
    s=MainWithRepertoire.load(path);s.run_until(2282);base=physical(s.world);g=s.two_memory.geometry
    reference=s.observe(g['reference_site']);obj=s.observe(g['object_site']);reader=s.observe(g['center'])
    if not(reference['s_reg']==36 and obj['s_reg']==16 and reader['s_reg']==7 and reader['direction']==[0,0,1]):raise ValueError('Late declared operands/reader are not currently accessible')
    expected=next(f['physical']for f in data['frames']if f['tick']==2283)
    r={'schema':'CPC9.late_memory.causal.v1','preparations':0,'technical_replays':1,'diagnostic_forks':3,'parent':str(path.relative_to(ROOT)),
       'parent_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pre_tick':2282,'reference':reference,'object':obj,'reader':reader,
       'prediction_before_diagnostic_targets':'With actual old36/16 and current reader7, sham2283 equals MAIN +X7. Removing reference36 should reverse comparison to -X7, not prove global lesion. Removing current reader7 should remove this qualified output. Neither fork returns to MAIN.',
       'rows':[],'status':'PREDICTED'}
    write(a.out/'MEDICIONES.json',r)
    for condition,victim in(('cut_reference',reference),('cut_reader',reader),('sham_reference',reference)):
        edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*victim['site']);edit.raw=int(victim['raw'])if condition.startswith('sham')else 0;edit.clock=None;edit.label=condition
        world=s.world.diagnostic_fork([edit],True);child=MainWithRepertoire(world,deepcopy(s.geometry),deepcopy(s.state),s.identifier)
        center=g['center'];pre=[child.observe(move(center,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
        predicted=one_step(pre);child.run_until(2283);post=child.observe(center)
        row={'condition':condition,'pre_Moore27':pre,'predicted_native_branch':predicted,'post':post,
             'branch_exact':predicted['raw']==post['raw']and predicted['clock']==post['clock'],
             'full_MAIN_equal':physical(world)==expected,'parent_unchanged':physical(s.world)==base,'clock_edited':False}
        r['rows'].append(row);write(a.out/'MEDICIONES.json',r);del child,world;gc.collect()
    if not(r['rows'][-1]['full_MAIN_equal']and all(v['branch_exact']and v['parent_unchanged']for v in r['rows'])):raise AssertionError('Late use diagnostic reconstruction failed')
    r['status']='MEASURED';write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'status':r['status'],'rows':[(v['condition'],v['post']['s_reg'],v['post']['direction'],v['branch_exact'])for v in r['rows']]}))
if __name__=='__main__':main()
