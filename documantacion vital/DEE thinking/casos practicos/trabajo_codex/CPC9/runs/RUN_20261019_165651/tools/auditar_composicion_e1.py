"""Physical composition, selective arrivals and same-load direction controls.

Auditor copies of actual E1 only. No cuts, reconstructed answers or other
futures are returned to MAIN. Incoming vectors identify a local branch, not a
unique global semantic genealogy inferred merely from load/proximity.
"""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,json,sys,gc
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from dee_thinking import _native as d
from vida_integral import IntegralLifeSession
from integracion.relational_pair import physical,move
from audit_primary import one_step
from ejecutar_retorno import write
def moore(s,q):return[s.observe(move(q,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    source=ROOT/'resultados/vida_integral/EI_D01';data=json.loads((source/'MEDICIONES.json').read_text());path=source/'T136.deetsnap.gz'
    parent=IntegralLifeSession.load(path);parent.run_until(205);q=parent.geometry['common_join'];pre=moore(parent,q)
    expected205=next(f['physical']for f in data['frames']if f['tick']==205)
    if physical(parent.world)!=expected205:raise AssertionError('Pre-composition replay mismatch')
    incoming=[x for x in pre if any(x['direction'])and[(x['site'][i]+x['direction'][i])%67 for i in range(3)]==q]
    if not 2<=len(incoming)<=4:raise ValueError('No bounded multiple-arrival composition to test')
    baseline=IntegralLifeSession(parent.world.fork(),parent.geometry,deepcopy(parent.state),parent.identifier);baseline.run_until(206)
    formed=baseline.observe(q);prediction=one_step(pre)
    if prediction['raw']!=formed['raw']or prediction['clock']!=formed['clock']:raise AssertionError('Local native composition not reconstructed')
    r={'schema':'CPC9.E1.composition.causal.v1','status':'PREDICTED','preparations':0,'technical_replays':1,'diagnostic_forks':len(incoming)+3,
      'parent':str(path.relative_to(ROOT)),'parent_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'target':q,'pre_Moore27':pre,
      'native_branch':prediction,'actual_formed206':formed,'local_branch_exact':True,'incoming':incoming,
      'prediction_before_diagnostics':'Cut each actual arrival before206; inspect local/posterior consequences. Preserve aggregate load but erase X or Z after206 to test direction-sensitive use. Sham must reproduce full RAW/clocks884; no global lesion or semantic-productivity inference.',
      'rows':[]}
    write(a.out/'MEDICIONES.json',r)
    conditions=[('cut_arrival_'+str(i),parent,x,0)for i,x in enumerate(incoming)]
    conditions += [('erase_composed_X',baseline,formed,d.pack_record(formed['state'],formed['s_reg'],0,formed['direction'][1],formed['direction'][2],formed['semantic'])),
       ('erase_composed_Z',baseline,formed,d.pack_record(formed['state'],formed['s_reg'],formed['direction'][0],formed['direction'][1],0,formed['semantic'])),
       ('sham_formed206',baseline,formed,int(formed['raw']))]
    parent_before=physical(parent.world);baseline_before=physical(baseline.world)
    for name,origin,victim,raw in conditions:
        edit=d.ResearchStateEdit();edit.coordinate=d.Coordinate(*victim['site']);edit.raw=raw;edit.clock=None;edit.label=name
        world=origin.world.diagnostic_fork([edit],True);s=IntegralLifeSession(world,origin.geometry,deepcopy(origin.state),origin.identifier)
        row={'condition':name,'pre_tick':s.tick,'victim':victim,'new_raw':str(raw),'clock_preserved':s.observe(victim['site'])['clock']==victim['clock'],'frames':[]}
        for t in(206,210,214,281,884):
            if t<s.tick:continue
            s.run_until(t);row['frames'].append({'tick':t,'view':s.view(),'physical':physical(world)})
        row.update(full_original884_equal=physical(world)==data['final_physical'],parents_unchanged=physical(parent.world)==parent_before and physical(baseline.world)==baseline_before)
        if name=='sham_formed206'and not row['full_original884_equal']:raise AssertionError('Sham changed MAIN continuation')
        if not(row['clock_preserved']and row['parents_unchanged']):raise AssertionError('Diagnostic contaminated parent or clocks')
        r['rows'].append(row);write(a.out/'MEDICIONES.json',r);del s,world;gc.collect()
    r['status']='MEASURED';write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'status':r['status'],'incoming':len(incoming),'formed':(formed['s_reg'],formed['direction']),
       'conditions':[(x['condition'],x['full_original884_equal'])for x in r['rows']]}))
if __name__=='__main__':main()
