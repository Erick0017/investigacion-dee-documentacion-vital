"""Post-trajectory check of the explicit demo curriculum, never a participant."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import put,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    first=json.loads((a.directory/'INITIAL.json').read_text(encoding='utf-8'))
    later=json.loads((a.directory/'CONTINUATION.json').read_text(encoding='utf-8'))
    verify=json.loads((a.directory/'VERIFICATION.json').read_text(encoding='utf-8'))
    panels=[]
    for event in later['events']:
        r=event.get('result') or {}
        if r.get('operacion')=='SONDAS_FISICAS_CONSUMIBLES':
            panels.append({'tick':r['tick_lectura'],'responses':{x['forma']:x['respuesta_a_esta_consulta'] for x in r['respuestas']},
                           'all_admitted':all(x['consulta_admitida'] for x in r['respuestas'])})
    names=[x for e in first['events'] for x in ((e.get('result') or {}).get('respuestas',[]) if (e.get('result') or {}).get('operacion')=='CONSULTA_FISICA_POR_SENAL_SOLA' else []) if x['coverage']]
    expected_before={'L03':-1,'L04':1,'L09':1};expected_after={'L03':1,'L04':1,'L09':1}
    report={'schema':'CPC7.demo.posttrajectory-outcomes.v1','physical_exact_on_restore':verify['physical_exact_on_restore'],
        'operative_exact_on_restore':verify['operative_exact_on_restore_excluding_declared_serialization_envelope'],
        'panels':panels,'before_revision_matches_explicit_demo':len(panels)==2 and panels[0]['tick']==338 and panels[0]['responses']==expected_before,
        'after_revision_matches_explicit_demo':len(panels)==2 and panels[1]['tick']==472 and panels[1]['responses']==expected_after,
        'one_opaque_association_from_native_information':len(names)==1 and names[0]['value']==1,
        'initial_transcript_sha256':sha(a.directory/'INITIAL.json'),'continued_transcript_sha256':sha(a.directory/'CONTINUATION.json'),
        'scope':'Only the explicit finite event curriculum; auditor comparisons after both native workers exited. Expectations are not read by the console.'}
    put(a.out,report)
    assert all(report[k] is True for k in ('physical_exact_on_restore','operative_exact_on_restore','before_revision_matches_explicit_demo','after_revision_matches_explicit_demo','one_opaque_association_from_native_information'))
    assert all(p['all_admitted'] for p in panels)
    print(json.dumps({'demo_outcomes':'VERIFIED','final_tick':472}))

if __name__=='__main__':main()
