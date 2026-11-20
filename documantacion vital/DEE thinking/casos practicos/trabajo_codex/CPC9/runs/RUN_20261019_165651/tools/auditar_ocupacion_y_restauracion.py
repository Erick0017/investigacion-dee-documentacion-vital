"""Passive global field summaries at saved frontiers, plus exact continuation.

An auditor view is not E1 knowledge. No extracted state returns to MAIN.
No dense arrays are saved here and no source/clock edits are made.
"""
from pathlib import Path
from collections import Counter
import argparse,gc,hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from dee_thinking.persistence import load_world_snapshot
from vida_repertorio_extension import MainWithRepertoire
from integracion.relational_pair import physical
from ejecutar_retorno import write
def stats(w):
    raw=w.runtime.raw_copy();semantic=Counter();directional=0;occupied=0;alive=0;maxload=0;limit=0;states=Counter()
    for r in raw:
        state=r&0xffffffff;load=(r>>32)&65535;sem=(r>>60)&15
        occupied+=int(state>0);alive+=int(state>0 and sem!=5);semantic[sem]+=1;states[state]+=1
        directional+=int(bool(r&0xfff000000000000));maxload=max(maxload,load);limit+=int(load>=19664)
    return{'sites':len(raw),'occupied_state_gt0':occupied,'alive_except_sem5':alive,'directional_fields_nonzero':directional,
        'semantic_counts':dict(semantic),'state_counts':dict(states),'max_s_reg':maxload,'at_or_above_reducer_cap':limit,
        'note':'State/field counts are auditor measures, not energy or contents known by the organism.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    paths=['resultados/vida_integral/EI_D01/T0.deetsnap.gz','resultados/vida_integral/EI_D01/T884.deetsnap.gz',
      'resultados/continuacion/E1_MAIN_884_1220/T1220.deetsnap.gz',
      'front_relations/resultados/E1_MAIN_1220_1371/T1371.deetsnap.gz','front_relations/resultados/E1_MAIN_1371_1639/T1639.deetsnap.gz',
      'front_relations/resultados/E1_MAIN_1639_1907/T1907.deetsnap.gz',
      'resultados/continuacion/E1_MAIN_K65_1907_2353/T1912.deetsnap.gz','resultados/continuacion/E1_MAIN_K65_1907_2353/T2152.deetsnap.gz',
      'resultados/continuacion/E1_MAIN_K65_1907_2353/T2219.deetsnap.gz','resultados/continuacion/E1_MAIN_K65_1907_2353/T2353.deetsnap.gz',
      'resultados/continuacion/E1_CF_K65_NO_EVENT/T2353.deetsnap.gz','resultados/continuacion/E1_CF_K65_UNPAIRED/T2353.deetsnap.gz',
      'resultados/continuacion/E1_MAIN_TAIL_2353_2493/T2493.deetsnap.gz']
    out={'schema':'CPC9.passive.global_occupation.v1','preparations':0,'passive_saved_state_loads':0,'technical_restored_continuations':1,'rows':[]}
    for name in paths:
        path=ROOT/name
        if not path.exists():out['rows'].append({'member':name,'missing':True});continue
        w,_=load_world_snapshot(path,max_bytes=1024**3);before=physical(w)
        out['rows'].append({'member':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'physical':before,'statistics':stats(w),'passive_physics_unchanged':physical(w)==before})
        out['passive_saved_state_loads']+=1;del w;gc.collect();write(a.out/'MEDICIONES.json',out)
    source=ROOT/'resultados/continuacion/E1_MAIN_TAIL_2353_2493';d=json.loads((source/'MEDICIONES.json').read_text())
    s=MainWithRepertoire.load(source/'T2357.deetsnap.gz');initial=physical(s.world);s.run_until(2493)
    out['restoration']={'parent':str((source/'T2357.deetsnap.gz').relative_to(ROOT)),'initial_physical':initial,'final_physical':physical(s.world),
      'equal_final2493':physical(s.world)==d['final_physical'],'complete_receipts_equal':s.receipts()==d['requests']}
    if not(out['restoration']['equal_final2493']and out['restoration']['complete_receipts_equal']):raise AssertionError('Official restoration changed future history')
    # This is an explicitly labelled technical continuation after the original
    # MAIN endpoint; no answer is assumed and this branch does not replace MAIN.
    s.repertoire.input(s.repertoire.geometry['forms'][1]['ports']['read.plus'],7,2494,True);receipt=s.repertoire.receipts()[-1]
    s.run_until(2498);out['new_interaction_after_restore']={'status':'TECHNICAL_CONTINUATION_NOT_MAIN','submitted':receipt,'final_receipt':s.repertoire.receipts()[-1],
      'observation':s.repertoire.observe(s.repertoire.geometry['forms'][1]['hub']),'physical':physical(s.world)}
    out['status']='MEASURED';write(a.out/'MEDICIONES.json',out);print(json.dumps({'status':out['status'],'states':out['passive_saved_state_loads'],'restored_exact':out['restoration']['equal_final2493'],'receipts_exact':out['restoration']['complete_receipts_equal']}))
if __name__=='__main__':main()
