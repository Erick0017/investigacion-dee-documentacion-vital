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
    r={'schema':'CPC9.late_memory.causal.v2','preparations':0,'technical_replays':1,'diagnostic_forks':5,'parent':str(path.relative_to(ROOT)),
       'parent_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pre_tick':2282,'reference':reference,'object':obj,'reader':reader,
       'prediction_before_diagnostic_targets':'PreserveV1: full reference cut caused local stability loss, not predicted-X. Cut reader was refilled by pending current probe; passive prestate alone could not certify that row. New same-support interventions change only Rload36→5(expected-X7) or16(expectedactive7zero direction); sham must remain exact. Neither fork returns to MAIN.',
       'prior_attempt_preserved':'resultados/auditoria/MEMORIAS_TARDIAS_2283; native targets observed but V1 audit assumption omitted a current input and its assertion failed',
       'rows':[],'status':'PREDICTED'}
    write(a.out/'MEDICIONES.json',r)
    for condition,victim in(('cut_reference',reference),('cut_reader',reader),('same_support_R5',reference),('same_support_R16',reference),('sham_reference',reference)):
        if condition.startswith('sham'):
            new_raw=int(victim['raw'])
        elif condition.startswith('same_support'):
            new_load=5 if condition.endswith('R5') else 16
            new_raw=d.pack_record(reference['state'],new_load,*reference['direction'],reference['semantic'])
        else:
            new_raw=0
        edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*victim['site']);edit.raw=new_raw;edit.clock=None;edit.label=condition
        world=s.world.diagnostic_fork([edit],True);child=MainWithRepertoire(world,deepcopy(s.geometry),deepcopy(s.state),s.identifier)
        center=g['center'];pre=[child.observe(move(center,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
        predicted=one_step(pre);child.run_until(2283);post=child.observe(center)
        row={'condition':condition,'pre_Moore27':pre,'predicted_native_branch':predicted,'post':post,
             'branch_exact':predicted['raw']==post['raw']and predicted['clock']==post['clock'],
             'full_MAIN_equal':physical(world)==expected,'parent_unchanged':physical(s.world)==base,'clock_edited':False,
             'current_boundary_receipts':[x for x in child.receipts()if x.get('tick')==2282],
             'local_checker_scope':'NOT_CERTIFIED_PENDING_CURRENT_INPUT'if condition=='cut_reader'else'Complete local prestate; current probes rejected while old reader occupies target'}
        r['rows'].append(row);write(a.out/'MEDICIONES.json',r);del child,world;gc.collect()
    if not(r['rows'][-1]['full_MAIN_equal']and all(v['parent_unchanged']and(v['branch_exact']or v['condition']=='cut_reader')for v in r['rows'])):raise AssertionError('Sham or certified local diagnostic reconstruction failed')
    r['status']='MEASURED';write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'status':r['status'],'rows':[(v['condition'],v['post']['s_reg'],v['post']['direction'],v['branch_exact'])for v in r['rows']]}))
if __name__=='__main__':main()
