"""External audit of heterogeneous components and native inter-family bridge."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha


def main():
    hetero=[];data={}
    for path in sorted((ROOT/'resultados/heterogeneous_01').glob('*/MEASUREMENTS.json')):
        m=json.loads(path.read_text(encoding='utf-8'));data[m['case']['id']]=m
        hetero.append({'case_id':m['case']['id'],'architecture':m['case']['architecture'],'phase':m['case']['phase'],
            'primary':path.relative_to(ROOT).as_posix(),'sha256':sha(path),
            'N':67,'components':4,'initial_sites':m['geometry']['initial_material_sites'],
            'exact_calls':len(m['calls']),'experience_kind_calls':sum(c['kind']=='submit' for c in m['calls']),
            'probe_kind_calls':sum(c['kind']=='probe' for c in m['calls']),
            'total_input_load':sum(c['payload'] for c in m['calls']),
            'reader_receipts':[r for r in m['receipts'] if any('m2.read'==x for x in r['channels'])],
            'longitudinal_relative_panel':[r for r in m['rows'] if r['tick'] in (2,259,262,265,270,399,403,520)],
            'mobile_outputs':[r['center'] for r in m['mobile_encounters'] if r['phase']=='post'],
            'final_physics':m['physics']})
    contrasts=[]
    for a,b in [('HET_D01_R4','HET_D02_R5'),('HET_C01_R4_HISTORY','HET_C02_R5_HISTORY'),('HET_H01_R4_NEW_VALUES','HET_H02_R5_NEW_VALUES')]:
        x,y=data[a],data[b]
        contrasts.append({'R4':a,'R5':b,'same_N':True,'same_component_types':True,
            'same_initial_site_count':x['geometry']['initial_material_sites']==y['geometry']['initial_material_sites'],
            'same_call_count':len(x['calls'])==len(y['calls']),
            'same_total_input_load':sum(c['payload'] for c in x['calls'])==sum(c['payload'] for c in y['calls']),
            'all_sampled_relative_fields_equal':all(a['relative_cells']==b['relative_cells'] for a,b in zip(x['rows'],y['rows'])),
            'scope':'R4 second query reads its second mobile group; R5 second query is dose lane. Interface/operation kind differs, and mobile geometry differs. Relative equality is confined to all recorded sampled fields and horizon0..520; no universal independence assertion.'})
    put(ROOT/'resultados/heterogeneous_SUMMARY.json',{'schema':'CPC5.heterogeneous.audit.v1','cases':hetero,'paired_contrasts':contrasts,
        'new_independent_preparations':len(hetero),'scope':'Different actual mechanism types coexist. R5 coupling applies to mobile subgraph only. No architecture win score or native mobile-to-relative acquisition inferred from coexistence.'})
    bridges=[]
    for folder in ('heterobridge_01','heterobridge_reserved_01'):
        for path in sorted((ROOT/'resultados'/folder).glob('*/MEASUREMENTS.json')):
            m=json.loads(path.read_text(encoding='utf-8'))
            bridges.append({'case_id':m['case']['id'],'phase':m['case']['phase'],'primary':path.relative_to(ROOT).as_posix(),
                'sha256':sha(path),'N':47,'preparations':1,'same_Runtime':True,
                'receipts':m['receipts'],'geometry':m['geometry'],
                'physical_window':[r for r in m['rows'] if r['tick'] in (2,3,5,6,7,8,20)],
                'source_sha256':json.loads((path.parent/'CONFIG.json').read_text(encoding='utf-8'))['source_sha256'],
                'no_postT0_RAW_clock_edits':not m['host_RAW_clock_writes_after_T0']})
    put(ROOT/'resultados/heterobridge_SUMMARY.json',{'schema':'CPC5.inter_family_bridge.audit.v1','cases':bridges,
        'new_independent_preparations':len(bridges),
        'measured_chain':'Online collision-produced mobile carrier reaches reader; same incoming load gives a different x output when acquired A/B history is reversed.',
        'counterexamples_and_controls':'Unpaired and off-path mobile experiences retain delta+1 but do not activate comparator within0..20.',
        'scope':'Native functional readout across two mechanism families, with prepared geometry and fresh acquired histories. No renewed subsequent mobile querying, no65NSM general meanings, and no architecture-wide superiority implied.'})
    put(ROOT/'resultados/AUXILIARY_TECHNICAL_HOTFIXES.json',{
        'events':[{'jobs':['heterogeneous_six_01','heterobridge_four_01'],
                   'error':'relative_to called on a relative output path when ROOT is absolute; failure occurred after first MEASUREMENTS had been closed',
                   'repair':'Resolve reporting path and include completed case in reconstructed index; skip physical rerun of completed case',
                   'retained_initial_sources':['src/heterogeneous_initial_index_v1.py','src/heterobridge_initial_index_v1.py'],
                   'repair_changed_physics':False,'same_error_corrections':1}],
        'preserved_source_hashes_match_first_cases':{
            'heterogeneous':sha(ROOT/'src/heterogeneous_initial_index_v1.py')==json.loads((ROOT/'resultados/heterogeneous_01/HET_D01_R4/CONFIG.json').read_text(encoding='utf-8'))['source_sha256'],
            'heterobridge':sha(ROOT/'src/heterobridge_initial_index_v1.py')==json.loads((ROOT/'resultados/heterobridge_01/BRIDGE_D01_AB/CONFIG.json').read_text(encoding='utf-8'))['source_sha256']},
        'later_discovery_bridge_source':'src/heterobridge_discovery_v2.py',
        'reserve_update':'Add parameterized translation and loads only; default physical values retained. Discovery was not reclassified as reserve.'})
    print(json.dumps({'heterogeneous_worlds':len(hetero),'bridge_worlds':len(bridges),'paired_relative_equal':[x['all_sampled_relative_fields_equal'] for x in contrasts]}))

if __name__=='__main__':main()
