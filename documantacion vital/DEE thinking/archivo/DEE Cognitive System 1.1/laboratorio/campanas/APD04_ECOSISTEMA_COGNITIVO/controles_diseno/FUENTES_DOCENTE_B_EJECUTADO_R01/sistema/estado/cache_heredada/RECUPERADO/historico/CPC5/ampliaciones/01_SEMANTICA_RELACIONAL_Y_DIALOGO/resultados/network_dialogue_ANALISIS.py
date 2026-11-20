"""External post-trajectory comparison; never imported by participants."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    cases={}
    for p in sorted((ROOT/'resultados').glob('network_dialogue*/**/MEASUREMENTS.json')):
        r=load(p);cases[r['case']['id']]={'path':p,'r':r}
    rows=[]
    for name,item in cases.items():
        r=item['r'];overlaps=r['geometry']['source_site_overlaps']
        rows.append({'case_id':name,'source':str(item['path'].relative_to(ROOT)),'source_sha256':sha(item['path']),
                     'case':r['case'],'resources':r['resources'],'elapsed_seconds':r['elapsed_seconds'],
                     'calculations':r['calculations'],'diagnostic_edits':r['diagnostic_edits'],
                     'source_site_aliases':len(overlaps),
                     'cross_loop_source_site_overlaps':[x for x in overlaps if x['first'].split('.')[0]!=x['second'].split('.')[0]],
                     'receipts':r['receipts']})
    base=cases['RING_A2_DUPLEX']['r'];comparisons=[]
    for name in ('RING_A2_SOURCE_U2_OMITTED','RING_A2_SENT_MESSAGE_CUT','RING_A2_SENT_MESSAGE_SHAM'):
        r=cases[name]['r'];a={x['tick']:x for x in base['rows']};b={x['tick']:x for x in r['rows']};shared=sorted(a.keys()&b.keys())
        perloop=[]
        for loop in (0,1):
            same=[t for t in shared if a[t]['loops'][str(loop)]==b[t]['loops'][str(loop)]]
            different=[t for t in shared if t not in same]
            perloop.append({'loop':loop,'sampled_ticks':len(shared),'identical_sample_frames':len(same),
                            'all_sampled_fields_equal':len(same)==len(shared),'different_ticks':different,
                            'baseline_banks':base['calculations'][loop]['banks'],'control_banks':r['calculations'][loop]['banks'],
                            'baseline_backups':base['calculations'][loop]['backup_readouts'],'control_backups':r['calculations'][loop]['backup_readouts'],
                            'scope':'All declared sampled physical fields are compared, not unsampled whole-region identity.'})
        comparisons.append({'baseline':'RING_A2_DUPLEX','control':name,'per_loop':perloop})
    role=cases['RING_A2_RESERVED_ROLE_EXCHANGE']['r']
    role_frames=[{'tick':x['tick'],'loops':{i:{k:v for k,v in values.items() if k.endswith('.backup') or k.startswith('bank.')} for i,values in x['loops'].items()}}
                 for x in role['rows'] if x['tick'] in (70,137,204,209,338)]
    result={'schema':'CPC5.extension.network_dialogue.external_analysis.v1','primary_records':len(rows),'cases':rows,
            'census':{'fresh_preparations':len(rows),'native_ticks':sum(x['r']['resources']['native_ticks'] for x in cases.values()),
                      'input_calls':sum(len(x['r']['inputs']) for x in cases.values()),
                      'API_probes':sum(x['r']['resources']['API_probes'] for x in cases.values()),
                      'diagnostic_forks':sum(len(x['r']['diagnostic_edits']) for x in cases.values())},
            'selective_edge_comparisons':comparisons,'role_exchange_observations':role_frames,
            'method':'Copied exact primary fields, compared dictionaries at matching ticks, counted recorded requests; no simulated target enters a participant.',
            'scope':'Measured finite two-function distributed candidates and prepared neighboring request/response routes. Not equal-inventory superiority, adaptive dialogue policy, joint three-way decision, or renewable compound identity.'}
    out=Path(__file__).with_suffix('.json');out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(out),'census':result['census'],'edge_other_loop_preserved':[(x['control'],x['per_loop'][1]['all_sampled_fields_equal']) for x in comparisons]}))

if __name__=='__main__':main()
