"""Post-trajectory calculations. Never imported by participant/session code."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha


def main():
    folder=ROOT/'resultados/INTEGRATION_CONTROLS_01'
    index=json.loads((folder/'INDEX.json').read_text(encoding='utf-8'));rows=[]
    for item in index:
        p=ROOT/item['evidence'];m=json.loads(p.read_text(encoding='utf-8'))
        summary=m['summary']
        rows.append({'case_id':item['id'],'evidence':item['evidence'],'sha256':sha(p),
          'modality':'DIAGNOSTIC_FORK' if m['case'].get('mode')=='diagnostic' else 'EXPERIENCE_PROTOCOL',
          'stages':{stage:[{'site':x['physical']['site'],'location':x['location'],
                          'tick':x['physical']['tick'],'raw':x['physical']['raw'],
                          'clock':x['physical']['clock'],'direction':x['physical']['direction'],
                          's_reg':x['physical']['s_reg']} for x in summary[stage]]
                    for stage in ('selection','information','late_read')},
          'receipts':{'total':len(m.get('requests',[])),
             'applied':sum(q['receipt']['status']=='applied' for q in m.get('requests',[])),
             'rejected':sum(q['receipt']['status'].startswith('rejected') for q in m.get('requests',[]))},
          'preparations':m.get('preparations',1),'diagnostic_forks':m.get('diagnostic_forks',0),
          'elapsed_seconds':m['elapsed_seconds']})
    out={'schema':'CPC6.integration.controls.calculations.v1','source_sha256':sha(__file__),
         'case_count':len(rows),'new_preparations':sum(r['preparations'] for r in rows),
         'diagnostic_forks':sum(r['diagnostic_forks'] for r in rows),
         'all_primary_trajectories':rows,
         'formula':'Each stage lists records meeting the decoder frozen in life.summarize: active,semantic1,exactstage-direction. Empty list is absence of that expression, not numericalzero or proof of noinformation. Receipt total includes scheduled/originalrequests retained by diagnostic snapshot. Forks are not independentnewpreparations.',
         'scope':'8 new integrated preparations and7diagnosticcontinuations of onepreviousU0, not15independentworldhistories. Exact RAW/clock retained in primary records.'}
    put(ROOT/'resultados/INTEGRATION_CONTROLS_CALCULATIONS.json',out)
    print({'cases':len(rows),'new_preparations':out['new_preparations'],'diagnostic_forks':out['diagnostic_forks']})


if __name__=='__main__':main()
