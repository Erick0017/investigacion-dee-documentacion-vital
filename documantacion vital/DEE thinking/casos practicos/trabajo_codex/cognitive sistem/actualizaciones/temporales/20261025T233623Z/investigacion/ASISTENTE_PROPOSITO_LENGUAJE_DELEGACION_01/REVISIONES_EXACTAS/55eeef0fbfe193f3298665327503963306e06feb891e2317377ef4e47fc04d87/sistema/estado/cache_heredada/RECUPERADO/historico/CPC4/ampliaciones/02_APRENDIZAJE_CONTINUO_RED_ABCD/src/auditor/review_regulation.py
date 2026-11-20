"""Saved-trace and saved-state regulation review. No advance, input or edit."""
from datetime import datetime,timezone
import hashlib,json,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from src.auditor.passive import digest
OUT=ROOT/'resultados/auditor';REG=ROOT/'resultados/regulacion'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def compact(value):
    r=value['physical'];return {'delta':value['delta'],'A':r['A'],'B':r['B'],
        'comparator':r['comparator'],'reader':r['reader'],'source':r['source']}

def main():
    import dee_thinking as d
    rows=[];gate_rows=[]
    for p in sorted((REG/'DUAL_CONFIRMATION').glob('*/MEASUREMENTS.json')):
        m=read(p);case=m['case'];by_tick={r['tick']:r for r in m['rows']}
        points={str(t):{key:compact(value) for key,value in by_tick[t]['memories'].items()}
                for t in (0,2,259,261,262,263,264,265,399,400,401,403,520) if t in by_tick}
        row={'id':case['id'],'case':case,'evidence':str(p.relative_to(ROOT)),'sha256':sha(p),
             'final':{k:compact(v) for k,v in m['final']['memories'].items()},
             'selected_points':points,'receipts':m['receipts'],
             'post_second_acquisition_sampled_deltas':{key:sorted({r['memories'][key]['delta'] for r in m['rows'] if r['tick']>=262 and r['memories'][key]['delta'] is not None}) for key in ('1','2')},
             'source_copy_exact':sha(p.parent/'EXECUTED_SOURCE.py')==m['source_sha256']}
        rows.append(row)
        for tick in (259,262,399,403,520):
            snapshot=p.parent/f'T{tick}.deetsnap'
            if not snapshot.exists():continue
            w=d.OrganizationalWorld.load_snapshot(str(snapshot));before=digest(w)
            for memory,ports in m['spec'].items():
                for center in ('A','B'):
                    g=d.inspect_write_gate(w.runtime,d.Coordinate(*ports[center]),False)
                    keys=('local_clock','center_available','n_active','hadron','rule_value','survives_material_rule',
                          'semantic_protected','write_protected','k','period','phase_remainder','ordinary_increment_condition','branch','demux_status')
                    gate_rows.append({'case':case['id'],'tick':tick,'memory':memory,'center':center,
                        'site':ports[center],'gate':{key:getattr(g,key) for key in keys},
                        'snapshot':str(snapshot.relative_to(ROOT))})
            assert digest(w)==before
    comparison={}
    selected={r['id']:r for r in rows}
    if 'AB_AB' in selected and 'BA_AB' in selected:
        a,b=selected['AB_AB'],selected['BA_AB']
        comparison={'histories':['AB_AB','BA_AB'],
            'at520_delta_memory1':[a['final']['1']['delta'],b['final']['1']['delta']],
            'at520_comparator1':[a['final']['1']['comparator'],b['final']['1']['comparator']],
            'at401_comparator1':[a['selected_points']['401']['1']['comparator'],b['selected_points']['401']['1']['comparator']],
            'inference':'A late single comparator frame may coalesce despite retained opposite relations; a temporal panel after the second acquisition distinguishes these same histories.'}
    sustained=[]
    for name in ('SUSTAINED_DISCOVERY01','SUSTAINED_DIRECTION02'):
        p=REG/name/'MEASUREMENTS.json'
        if p.exists():
            m=read(p);sustained.append({'id':name,'case':m['case'],'final':m['final'],
                'gate_occasions_recorded':len(m['gate_occasions']),'receipts':m['receipts'],
                'evidence':str(p.relative_to(ROOT)),'sha256':sha(p),
                'scope':'Inspector reads state before advance; queued input application at a boundary precedes F_v27 and is not reflected in the immediately preceding passive gate sample.'})
    # Compare matched historical conditions at the SAME tick/memory/center;
    # this is discovery of a future candidate, never an executed new contrast.
    groups={}
    for x in gate_rows:groups.setdefault((x['tick'],x['memory'],x['center']),{})[x['case']]=x['gate']
    matched=[]
    for key,values in groups.items():
        if 'AB_AB' in values and 'BA_AB' in values:
            a,b=values['AB_AB'],values['BA_AB']
            fields=('n_active','hadron','write_protected','ordinary_increment_condition','branch')
            if any(a[k]!=b[k] for k in fields):matched.append({'tick':key[0],'memory':key[1],'center':key[2],
                'AB_AB':a,'BA_AB':b,'scope':'History-associated guard/context difference in existing worlds, not yet a causal or future common-event test.'})
    report={'utc':datetime.now(timezone.utc).isoformat(),'mode':'PASSIVE_REVIEW_NO_NEW_NATIVE_TRAJECTORIES',
        'measured_dual_worlds':len(rows),'case_rows':rows,'matched_history_guard_differences':matched,
        'memory_expression_comparison':comparison,'single_relation_discoveries':sustained,
        'interpretation':{
            'continuous_two_relations':'Two separately prepared initially naive physical pairs coexist fromT0. One acquires at0/1 and the other at260/261 within the same unreset Runtime. Both relations retain distinct values through sampled520. This is two allocated stores, not unlimited new capacity or one fibre created per experience.',
            'common_drift':'Second pair drifts100/100→102/102 before acquisition, retaining delta0. Common scalar increments alone are not a new learned relation.',
            'reader_necessity':'Persistent semantic4 source is fixed prepared supply. Finite semantic1 source disappears, but its comparator can remain physically active through520. It is not established that semantic4 supply is necessary for this horizon. No-reader retains relation with comparator absent.',
            'late_probe400':'All completed dual cases reject physical probe400 because the actual injection site is RAW-occupied. This is admission unavailability, not memory loss. The relation and existing comparator can remain available.',
            'regulation_limit':'No comparison here establishes that an acquired history autonomously changes future susceptibility to the SAME admitted experience. Prepared phases, supports and renewable supply are not themselves learned regulation.',
            'phase_sampling_limit':'gate_occasions empty in a pre-boundary trace does not exclude input-enabled writing; receipt Applied at0 accompanies A100→101 before sample1.'},
        'proposed_next_contrast':{'status':'NOT_FROZEN_NOT_EXECUTED','bounded':'At most one matched future common-event timing after passive guard/admission verification; histories AB/BA/H0 with same age/resources, each with E or omittedE. No clock reset or direct center edit.',
            'current_candidate':'SUSTAINED_DIRECTION02@520 B has clock780,n_active7,period782. Coincidence would be at522 only IF the native context remains at7; current data do not establish that condition or admission at522.',
            'no_forced_positive':'If the same event is rejected or no differential write occurs, keep that measurement. A new post-discovery reserve must be specified before running; existing eight worlds are not prospective holds for this observer.'},
        'source_sha256':sha(__file__),'gate_readings':len(gate_rows),'passive_state_equal_for_all_loaded_snapshots':True}
    put(OUT/'REGULATION_RETENTION_REVIEW.json',report)
    put(OUT/'REGULATION_LOCAL_GATES.json',{'rows':gate_rows,'scope':'Passive pre-boundary gates only; no source ablations or hidden input application.'})
    print(json.dumps({'dual_worlds':len(rows),'gate_rows':len(gate_rows),'matched_guard_differences':len(matched)}))

if __name__=='__main__':main()
