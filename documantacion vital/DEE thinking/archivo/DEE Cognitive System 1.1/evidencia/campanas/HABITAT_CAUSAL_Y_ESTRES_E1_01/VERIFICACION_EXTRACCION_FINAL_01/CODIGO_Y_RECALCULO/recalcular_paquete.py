"""Archive-only arithmetic; no DEE import, no native ticks, no environment steps."""
from pathlib import Path
import argparse,json,hashlib,gzip
def calculate(root):
    e=root/'EVIDENCIA_ESENCIAL';out={'scope':'ARCHIVED_RECALCULATION_NOT_NATIVE_REPRODUCTION','blocks':{},'external':{}}
    for p in sorted(e.glob('*.rows.jsonl')):
        rows=[json.loads(x)for x in p.read_text(encoding='utf8').splitlines()if x]
        if not rows:continue
        if 'environment_response'in rows[0]:
            out['external'][p.stem]={'steps':len(rows),'native_nonzero':sum(bool(r['actuator']['command'])for r in rows),'executed_nonzero':sum(bool(r['executed_torque'])for r in rows),'reward_sum':sum(r['environment_response']['reward']for r in rows),'requests':len([x for r in rows for x in r['requests']]),'applied':sum(x['status']=='applied'for r in rows for x in r['requests']),'rejected':sum(x['status'].startswith('rejected')for r in rows for x in r['requests'])}
        else:
            out['blocks'][p.stem]={'opportunities':len(rows),'qualified':sum(r['actuator']['status']not in('NO_QUALIFIED_OUTPUT','CONFLICT_OUTSIDE_FIXED_CODEC')for r in rows),'reader_available':sum(r['reader_available']for r in rows),'noise_inputs':sum(len(r['noise'])for r in rows),'first_unqualified_tick':next((r['read_tick']for r in rows if r['actuator']['status']in('NO_QUALIFIED_OUTPUT','CONFLICT_OUTSIDE_FIXED_CODEC')),None)}
    a=json.loads((e/'AUTOPSIA_ORIGEN_CONFIRMADA_R1.json').read_text(encoding='utf8'))['decisive_update'];sources=a['actual_ballistic_antecedents'];post=a['destination_post'];dest=a['destination_pre']['site']
    out['collision']={'pre_tick':a['pre_tick'],'post_tick':a['post_tick'],'antecedents_reach_destination':all([(s['site'][i]+s['direction'][i])%67 for i in range(3)]==dest for s in sources),'pre_destination_RAW_zero':int(a['destination_pre']['raw'])==0,'loads_sum':sum(s['s_reg']for s in sources),'post_load':post['s_reg'],'post_direction':post['direction'],'source_RAW_exact':[s['raw']for s in sources],'post_RAW_exact':post['raw']}
    return out
def main():
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--check',action='store_true');args=p.parse_args();v=calculate(args.root)
    if args.check:
        expected=json.loads((args.root/'CALCULOS_ARCHIVADOS.json').read_text(encoding='utf8'))
        if expected!=v:raise AssertionError('Archived recalculation differs')
    print(json.dumps(v,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
