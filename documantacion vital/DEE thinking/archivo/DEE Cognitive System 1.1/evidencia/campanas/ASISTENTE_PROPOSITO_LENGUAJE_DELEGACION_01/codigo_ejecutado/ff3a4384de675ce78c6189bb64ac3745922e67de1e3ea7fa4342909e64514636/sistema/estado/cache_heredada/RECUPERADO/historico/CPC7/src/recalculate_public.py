"""Recalculate common fixed-stream metrics from primary data, outside the engine."""
import argparse
import collections
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha
from comparadores.evaluate_common import evaluate_file

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    prior=json.loads((ROOT/'revision/COMPARACION_METODOS.json').read_text(encoding='utf-8'))
    rows=[];counts=collections.defaultdict(lambda:collections.Counter())
    for item in prior['cases']:
        primary=ROOT/item['primary'];fixture=ROOT/'configuraciones/comparadores/fixtures_v1/RESERVED'/item['case_id']
        actual=evaluate_file(primary,fixture/'STREAM.json',fixture/'EVALUATOR.json')
        same=actual['performance']==item['performance']
        assert same,(item['primary'],'Stored and recalculated measurements differ')
        counts[(item['method'],item['mode'])].update({k:actual['performance'][k] for k in ('measured_queries','valid_responses','correct','absent_or_invalid')})
        rows.append({'primary':item['primary'],'sha256':sha(primary),'stored_summary_equal':same,'performance':actual['performance']})
    put(a.out/'CALCULOS.json',{'schema':'CPC7.public-recalculation.v1','cases':rows,
        'aggregates':[{'method':key[0],'mode':key[1],**dict(v)} for key,v in counts.items()],
        'all_stored_summaries_equal':all(r['stored_summary_equal'] for r in rows),
        'formulas':{'coverage':'valid_responses/measured_queries','accuracy_all':'correct/measured_queries',
                    'valid_accuracy':'correct/valid_responses; null if denominator0'},
        'layer':'Instrumented calculation after sealed trajectories; no engine import or participant update.'})
    print(json.dumps({'recalculated_cases':len(rows),'all_equal':True}))

if __name__=='__main__':main()
