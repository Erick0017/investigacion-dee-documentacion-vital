"""Auditor forks only: cut the received query answer before local acquisition.

The exact E1 MAIN parent remains unmodified. No fork result is written back.
"""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,json,sys,time,gc
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_receipt
from vida_integral import IntegralLifeSession
from integracion.relational_pair import physical
from ejecutar_retorno import write

def operation(s):return{'channels':sorted(s.world.runtime.channel_names),'receipts':[exact_receipt(x)for x in s.world.runtime.receipts]}
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    original=ROOT/'resultados/vida_integral/EI_D01';parent_path=original/'T136.deetsnap.gz'
    original_data=json.loads((original/'MEDICIONES.json').read_text(encoding='utf8'))
    parent=IntegralLifeSession.load(parent_path);pre=physical(parent.world);op=operation(parent)
    site=next(x['site']for x in parent.query_loop.geometry['turns']if x['id']=='return_home')
    observed=parent.observe(site)
    if not(observed['active']and observed['s_reg']==16 and observed['direction']==[1,1,0]):
        raise ValueError('Actual qualified B return is absent; cannot perform claimed cut')
    r={'schema':'CPC9.query.integral.causal.v1','status':'PREDICTED','parent':str(parent_path.relative_to(ROOT)),
       'parent_sha256':hashlib.sha256(parent_path.read_bytes()).hexdigest(),'preparations':0,'diagnostic_forks':2,'technical_restored_continuations':1,
       'site':site,'before':observed,'rows':[],
       'prediction_before_targets':'Cut actual B-derived16 carrier at136: no locally acquired Y21@137, no -X+Y response28@204, question210 remains +X-Y. Sham/restore equal complete E1 physical state/receipts884. Other component outputs remain measurable.'}
    write(a.out/'MEDICIONES.json',r)
    for condition in('restore','cut_return','sham_return'):
        if condition=='restore':world=parent.world.fork()
        else:
            edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*site);edit.raw=0 if condition=='cut_return'else int(observed['raw'])
            edit.clock=None;edit.label=condition;world=parent.world.diagnostic_fork([edit],True)
        s=IntegralLifeSession(world,parent.geometry,deepcopy(parent.state),parent.identifier)
        row={'condition':condition,'initial_physical':physical(world),'clock_preserved':s.observe(site)['clock']==observed['clock'],'operative_initial_equal':operation(s)==op,'frames':[]}
        for tick in(136,137,139,143,148,204,206,210,216,221,277,281,343,410,416,482,549,555,616,673,818,884):
            s.run_until(tick);row['frames'].append({'tick':tick,'view':s.view(),'physical':physical(world)})
        row.update(final_physical=physical(world),full_final_equal=physical(world)==original_data['final_physical'],
            full_receipts_equal=operation(s)['receipts']==sorted([x['receipt']for x in original_data['requests']],key=lambda x:x['id']),
            parent_unchanged=physical(parent.world)==pre and operation(parent)==op)
        if condition!='cut_return'and not(row['full_final_equal']and row['full_receipts_equal']):raise AssertionError('Exact continuation mismatch')
        if not(row['clock_preserved']and row['parent_unchanged']):raise AssertionError('Parent or clocks changed')
        r['rows'].append(row);write(a.out/'MEDICIONES.json',r);del s,world;gc.collect()
    r.update(status='MEASURED',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest());write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'status':r['status'],'conditions':[{'condition':x['condition'],'exact_final':x['full_final_equal'],'parent_intact':x['parent_unchanged']}for x in r['rows']]}))
if __name__=='__main__':main()
