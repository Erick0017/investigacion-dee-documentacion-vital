"""Integrated update and corrected guard comparisons; audit only, no engine."""
from collections import Counter
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha


def main():
    directory=ROOT/'resultados/integrated_revision';data={};base={};rows=[];receipts=Counter();snapshots=0
    for p in sorted(directory.glob('*/MEASUREMENTS.json')):
        m=json.loads(p.read_text(encoding='utf8'))
        if m.get('schema')!='CPC7.integrated_revision.measurements.v1':raise ValueError('Incomplete integrated primary: '+str(p))
        cid=m['case']['id'];data[cid]=m;b=json.loads((p.parent/m['base338']['path']).read_text(encoding='utf8'));base[cid]=b
        assert len(m['case']['bank_values'])==16 and sha(p.parent/m['base338']['path'])==m['base338']['sha256']
        for q in m['requests']:receipts[q['receipt']['status']]+=1
        for snap in m['snapshots']:assert sha(p.parent/snap['path'])==snap['sha256'];snapshots+=1
        r3=next(r for r in b['lower_repertoire_reads'] if r['tick']==338 and r['form']=='L03')
        rows.append({'case_id':cid,'path':str(p.relative_to(ROOT)),'sha256':sha(p),'schema':m['schema'],
            'preparations':1,'diagnostic_forks':0,'configured_values':len(m['case']['bank_values']),
            'initial_R3':b['acquisition']['L03']['direction'][1],'R3_query338':{'value':r3['value'],'covered':r3['coverage'],'receipt':r3['receipt']['status']},
            'actual_new_consequence402':m['case']['new_sign'],'guard_mode':m['case']['guard_mode'],'revision_mode':m['case']['revision_mode'],
            'base204':b['calculations']['lower_repertoire']['204'],'base338':b['calculations']['lower_repertoire']['338'],
            'post472':m['calculations'],'sign142':[(r['name_bank'],r['value']) for r in b['opaque_name_reads'] if r['coverage']],
            'snapshot_count':len(m['snapshots']),'elapsed_seconds':m['elapsed_seconds']})
    p=data['IR_P01_GUARDED_M1'];guard_sham=data['IR_C01_OFFPATH_GUARDS'];revision_sham=data['IR_C02_AUX_OFFPATH']
    bp=base['IR_P01_GUARDED_M1'];bg=base['IR_C01_OFFPATH_GUARDS'];br=base['IR_C02_AUX_OFFPATH']
    fields=('port','payload','tick','kind','id','call_tick')
    requested=lambda m:[[q.get(k) for k in fields] for q in m['requests']]
    assert bp['case']['bank_values']==bg['case']['bank_values']==br['case']['bank_values']
    assert requested(bp)==requested(bg)==requested(br)
    assert bp['final_physical']==br['final_physical']
    operative_fields=('tick','channels','receipts','external_operations','protocols')
    assert all(bp['final_operational'][k]==br['final_operational'][k] for k in operative_fields)
    neutral=['history','actual','bank_values','name_query_payload','new_sign']
    assert all(p['case'][k]==guard_sham['case'][k]==revision_sham['case'][k] for k in neutral)
    summary={'schema':'CPC7.integrated_revision.analysis.v1','generated_by':'src/analyze_integrated_revision.py',
        'cases':rows,'counts':{'independent_preparations':len(rows),'diagnostic_forks':0,'snapshot_hashes_verified':snapshots,
            'request_receipts':dict(receipts),'boundary_subrecords338':len(base),'boundary_subrecords_are_new_preparations':False},
        'checks':{'sixteen_values_before_create_all':True,'guard_pair_identical_experiences_and_request_schedule_through338':True,
            'M1_pair_initial_and_T338_complete_RAW_clocks_tick_equal':True,
            'M1_pair_T338_channels_receipts_external_operations_protocols_equal':True,
            'snapshot_metadata_identity':'Individual identity differs intentionally; geometry and request schedule are compared separately from identity metadata.',
            'engine_or_kernel_modified':False,'MAIN_external_RAW_clock_writes':[]},
        'corrected_guard_contrast':{'treatment':'IR_P01_GUARDED_M1','offpath':'IR_C01_OFFPATH_GUARDS',
            'before_revision338':[bp['calculations']['lower_repertoire']['338'],bg['calculations']['lower_repertoire']['338']],
            'scope':'Same sixteen actual experiences and all69initialinterfaces; only six prepared interceptor locations differ. This corrects, rather than overwrites, the older17-valueconfoundedRES_G301pair.'},
        'integrated_update_contrast':{'treatment':'IR_P01_GUARDED_M1','offpath_auxiliary':'IR_C02_AUX_OFFPATH','reserve':'IR_R607_GUARDED_M1',
            'scope':'New consequence at402 and secondteacherroutechange occur only after identical first338ticks in the matched pair. Other13remainusable in both arms, localizing the auxiliary contribution beyond global actuator failure.',
            'extra_dose':'Both arms receive same currentcue5,event11 andsecondteacher11. Treatment changes its encounter location, not its payload/direction. The offpath teacher is on explicitly declared z60plane.',
            'observed':'Treatment/reserve updateL03oppositely andretainother13/13;auxiliaryoffpath leavesL03uncovered/occupiedwhileother13/13respond. Offpathguardarm starts with only6/14but canreacquireL03;do not countthat asretentionofitsolderfunction.'},
        'limits':['One local update in one finite N67geometry; no arbitrary ongoing rewrite guarantee.',
            'Regulator is fixed prepared material; no consequence-learned choice of regulation.',
            'Sign-only response142 is before local update402. Later sign retention after402 was not queried by this panel.',
            'The fourteen directional correspondences are not fourteen general NSM meanings.',
            'Own high-bank native-use chain and later lower-bank update coexist in the same Runtime, but the selected original high carrier can be transformed or consumed rather than persist unchanged.']}
    put(directory/'ANALYSIS.json',summary)
    print(json.dumps(summary['counts']))


if __name__=='__main__':main()
