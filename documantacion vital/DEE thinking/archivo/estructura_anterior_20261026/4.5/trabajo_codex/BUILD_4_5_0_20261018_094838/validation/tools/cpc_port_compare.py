"""Post-trajectory port differential: no engine and no response generation."""
from collections import Counter
from pathlib import Path
import argparse,gzip,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import put,sha
from neutral_checks import binary_equal


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def op(value):return {**value,'snapshot_metadata':{k:v for k,v in value['snapshot_metadata'].items()
    if not(k.startswith('dee_thinking.organizational.') or k.startswith('dee_thinking.consolidated.'))}}


def compare(a,b,adir,bdir):
    checks=[];failures=[]
    if len(a['frames'])!=len(b['frames']):failures.append('frame count differs')
    for x,y in zip(a['frames'],b['frames']):
        tick=x['tick'];row={'tick':tick,'tick_equal':tick==y['tick']}
        for field in ('forms','body','questions','own_banks','actions','names'):
            if field in x or field in y:row[field+'_equal']=x.get(field)==y.get(field)
        if 'raw' in x or 'raw' in y:
            if 'raw' not in x or 'raw' not in y:row['RAW_equal']=False;row['clock_equal']=False
            else:
                row['RAW_equal'],row['RAW_bytes_compared']=binary_equal(adir/x['raw']['path'],bdir/y['raw']['path'])
                row['clock_equal'],row['clock_bytes_compared']=binary_equal(adir/x['clock']['path'],bdir/y['clock']['path'])
                row['operative_equal_excluding_inert_envelopes']=op(x['operative'])==op(y['operative'])
        if any(not v for k,v in row.items() if k.endswith('_equal') or k.endswith('_envelopes')):failures.append('frontier'+tick)
        checks.append(row)
    calls_equal=a['calls']==b['calls'];reads_equal=a['readouts']==b['readouts']
    if not calls_equal:failures.append('input/receipt ledger differs')
    if not reads_equal:failures.append('fixed physical readout differs')
    aop=op(a['final_operative']);bop=op(b['final_operative'])
    if aop!=bop:failures.append('final operational fields differ')
    return {'frontiers':checks,'input_and_receipt_ledger_equal':calls_equal,'fixed_readouts_equal':reads_equal,
        'final_operative_equal_excluding_inert_envelopes':aop==bop,'failures':failures,'status':'PASS' if not failures else 'FAIL'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case-id');args=p.parse_args()
    before=read(args.before/'INDEX.json');after=read(args.after/'INDEX.json')
    if before['config_sha256']!=after['config_sha256']:raise ValueError('Differing frozen configurations')
    aa={r['case_id']:r for r in before['cases']};bb={r['case_id']:r for r in after['cases']}
    if args.case_id:
        aa={args.case_id:aa[args.case_id]};bb={args.case_id:bb[args.case_id]}
    if set(aa)!=set(bb):raise ValueError('Different case coverage')
    rows=[]
    for key,item in aa.items():
        a_path=args.before/item['result'];b_path=args.after/bb[key]['result']
        if not a_path.exists() and a_path.with_name('RESULT_RECOVERED.json').exists():a_path=a_path.with_name('RESULT_RECOVERED.json')
        if not b_path.exists() and b_path.with_name('RESULT_RECOVERED.json').exists():b_path=b_path.with_name('RESULT_RECOVERED.json')
        a=read(a_path);b=read(b_path)
        data=compare(a,b,a_path.parent,b_path.parent)
        counts=Counter(r['final_receipt']['status'] for r in b['calls'])
        rows.append({'case_id':key,'kind':a['kind'],**data,'before_primary_sha256':sha(a_path),'after_primary_sha256':sha(b_path),
            'queries':len(b['readouts']),'covered_fixed_readout':sum(r['covered'] for r in b['readouts']),
            'request_status_counts':dict(counts),'before_lab_constructor_sources':a['constructor_sources'],
            'candidate_historical_lab_imports':b['technical']['candidate_historical_lab_imports']})
    report={'schema':'DEE45.CPC_native_port.comparison.v1','before_library':before['library'],'after_library':after['library'],
        'config_sha256':before['config_sha256'],'case_filter':args.case_id,'cases':rows,'total':len(rows),'pass_count':sum(x['status']=='PASS' for x in rows),
        'identity_scope':'Source apparatus4.0 constructor vs installed native4.5 factory in separate interpreters. Configured experiences, receipt semantics, full RAW/clocks/tick and fixed readouts compared.',
        'documental_differences_excluded':'Inert OrganizationalWorld/consolidated snapshot envelopes and organization descriptor class names; not request payloads, queues, clocks, physical fields or mutable protocol progress.',
        'scientific_scope':'Software validation and preserved counterexamples, not additional semantic concepts or independent replication counts.'}
    put(args.out,report)
    print(json.dumps({'compared':len(rows),'passed':report['pass_count']}))
    if any(x['status']!='PASS' for x in rows):raise SystemExit(1)

if __name__=='__main__':main()
