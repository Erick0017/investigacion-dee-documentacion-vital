"""External post-trajectory calculations. Never imported by a participant."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha

def main():
    rows=[]
    groups=('semantic_discovery','semantic_exit_discovery','order_stream_discovery','order_stream_confirmation','order_forks','order_interval_access','order_access_extension')
    for group in groups:
        for path in sorted((ROOT/'resultados'/group).glob('*/MEASUREMENTS.json')):
            data=json.loads(path.read_text(encoding='utf-8'));case=data['case'];trace=data['rows']
            named=[];contexts=[];alternate=[]
            for r in trace:
                for key in ('queries','name_access'):
                    if key in r:
                        for branch,physical in r[key].items():
                            if physical['active'] and physical['semantic']==1 and physical['direction'][0]!=0:
                                named.append({'tick':r['tick'],'branch':branch,'physical':physical})
                for branch,physical in r.get('context',r.get('context_sites',{})).items():
                    if physical['active']:
                        contexts.append({'tick':r['tick'],'branch':branch,'physical':physical})
                for branch,physical in r.get('alternate_queries',{}).items():
                    if physical['active'] and physical['semantic']==1 and physical['direction'][0]!=0:
                        alternate.append({'tick':r['tick'],'branch':branch,'physical':physical})
            row={'case_id':case['id'],'group':group,'primary':str(path.relative_to(ROOT)),'sha256':sha(path),
                 'mode':data.get('modality','EXPERIENCE_PROTOCOL'),
                 'initial_delta':trace[0]['delta'],'last_delta':trace[-1]['delta'],
                 'name_access_observations_nonzero_dx':named,'context_observations':contexts,'alternate_access_observations':alternate,
                 'first_query_and_later_are_distinct':True,
                 'receipt_status_counts':{},'MAIN_unchanged':data.get('MAIN_unchanged'),
                 'interventions':data.get('interventions',[])}
            for r in data.get('receipts',[]):row['receipt_status_counts'][r['status']]=row['receipt_status_counts'].get(r['status'],0)+1
            rows.append(row)
    result={'schema':'CPC5.extension.semantic_calculations.v1','rows':rows,
            'formulas':{'name_access':'At declared query site, state>0, semantic==1 and dx!=0. Original physical record retained; no query/absence/zero collapse.',
                        'delta':'A.s_reg-B.s_reg only when both declared support centers are active',
                        'comparison':'Compare first-query physical records across separately executed histories; never treat ticks as independent samples.'},
            'scope':'Instrument calculations after all relevant native trajectories; planned capabilities are not inferred from metric counts.'}
    put(ROOT/'revision/SEMANTIC_CALCULATIONS.json',result)
    for r in rows:
        print(json.dumps({'id':r['case_id'],'delta':r['last_delta'],'name_rows':[(x['tick'],x['branch'],x['physical']['s_reg'],x['physical']['direction']) for x in r['name_access_observations_nonzero_dx']],
                          'context_rows':[(x['tick'],x['branch'],x['physical']['s_reg'],x['physical']['direction']) for x in r['context_observations'] if x['tick'] in (34,35,36)],
                          'alternate_rows':[(x['tick'],x['branch'],x['physical']['s_reg'],x['physical']['direction']) for x in r['alternate_access_observations']],'statuses':r['receipt_status_counts']}),flush=True)

if __name__=='__main__':main()
