"""Exact named-life chain and reconciled receipt IDs, not replica inflation."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
STAGES=[
 ('resultados/vida_integral/EI_D01',None,0,884),
 ('resultados/continuacion/E1_MAIN_884_1220','resultados/vida_integral/EI_D01/T884.deetsnap.gz',884,1220),
 ('front_relations/resultados/E1_MAIN_1220_1371','resultados/continuacion/E1_MAIN_884_1220/T1220.deetsnap.gz',1220,1371),
 ('front_relations/resultados/E1_MAIN_1371_1639','front_relations/resultados/E1_MAIN_1220_1371/T1371.deetsnap.gz',1371,1639),
 ('front_relations/resultados/E1_MAIN_1639_1907','front_relations/resultados/E1_MAIN_1371_1639/T1639.deetsnap.gz',1639,1907),
 ('resultados/continuacion/E1_MAIN_K65_1907_2353','front_relations/resultados/E1_MAIN_1639_1907/T1907.deetsnap.gz',1907,2353),
 ('resultados/continuacion/E1_MAIN_TAIL_2353_2493','resultados/continuacion/E1_MAIN_K65_1907_2353/T2353.deetsnap.gz',2353,2493)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'revision/VIDA_PRINCIPAL.json');a=p.parse_args()
    rows=[];last=None;old_ids=set();all_ids=set();identity=set()
    for folder,parent,t0,t1 in STAGES:
        path=ROOT/folder/'MEDICIONES.json';d=json.loads(path.read_text(encoding='utf8'))
        if d['status']!='MEASURED':raise ValueError('A MAIN stage is not closed: '+folder)
        current={int(q['receipt']['id']):q['receipt']for q in d['requests']};ids=set(current)
        parent_decl=d.get('parent_snapshot_sha256',d.get('parent',{}).get('sha256'))
        first=d.get('initial_physical',d.get('parent',{}).get('physical',d['frames'][0]['physical']))
        row={'primary':folder+'/MEDICIONES.json','sha256':sha(path),'case_id':d['case_id'],'start_tick':t0,'end_tick':t1,
            'native_tick_span':t1-t0,'preparations':d.get('preparations',0),'declared_continuity_type':d.get('continuity_type','INITIAL_PREPARATION'),
            'parent_snapshot':parent,'parent_hash_declared':parent_decl,'parent_hash_actual':sha(ROOT/parent)if parent else None,
            'parent_hash_matches':parent_decl==sha(ROOT/parent)if parent else None,
            'initial_physical':first,'previous_final_physics_equal':first==last if last else None,
            'final_physical':d['final_physical'],'unique_receipt_ids_cumulative':len(ids),'new_receipt_ids':len(ids-old_ids),
            'new_receipt_statuses':dict(Counter(current[i]['status']for i in ids-old_ids)),
            'prior_IDs_retained':old_ids<=ids,'RAW_clock_edits_declared':d.get('MAIN_RAW_clock_edits'),
            'instrument_extension':d.get('instrumental_extension')}
        ident=d.get('parent_identifier',d.get('parent',{}).get('identifier'))
        if ident:identity.add(ident)
        if parent and not(row['parent_hash_matches']and row['previous_final_physics_equal']):raise AssertionError('Broken same-life chain')
        if not row['prior_IDs_retained']or row['RAW_clock_edits_declared']:raise AssertionError('Unreported history/field replacement')
        rows.append(row);last=d['final_physical'];all_ids|=ids;old_ids=ids
    if len(identity)>1:raise AssertionError('Identity label changed within declared chain')
    out={'schema':'CPC9.E1.same_life.reconciliation.v1','N_fixed':67,'initial_material':107,'preparations':1,'serialized_main_continuations':len(rows)-1,
       'main_tick_span':sum(x['native_tick_span']for x in rows),'final_tick':2493,'identity_labels':sorted(identity),'stages':rows,
       'unique_receipts_final':len(all_ids),'diagnostics_returned_to_MAIN':False,
       'scope':'Seven sequential serialized phases of one causal life, not seven independent individuals. Auxiliary worlds/forks/replays have separate ledgers. New interfaces at1220/1907 are external instruments, not native architectural growth.',
       'history_before_new_interface_registration':'Full RAW/clocks/tick before/after registration are compared in each primary, while changed channel registry is declared separately.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'stages':len(rows),'chain_edges_exact':sum(x['parent_hash_matches']is True and x['previous_final_physics_equal']is True for x in rows),'main_ticks':out['main_tick_span'],'unique_receipts':len(all_ids),'new_receipts':[(x['case_id'],x['new_receipt_ids'],x['new_receipt_statuses'])for x in rows]}))
if __name__=='__main__':main()
