"""Portable auditor of exact integer primary fields. Never imports the engine."""
import argparse,gzip,hashlib,json
from pathlib import Path
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def fields(raw):
    r=int(raw)
    if not 0<=r<2**64:raise ValueError('uint64 required')
    return {'state':r&0xffffffff,'s_reg':(r>>32)&65535,'semantic':(r>>60)&15,
        'direction':[((r>>s)&15)-(16 if((r>>s)&15)>=8 else 0)for s in(48,52,56)]}
def gate(observed):
    candidates=[]
    for o in observed:
        f=fields(o['raw']);clock=int(o['clock'])
        assert 0<=clock<2**64
        if f['state']and f['semantic']==1 and f['direction']==[0,1,0]:
            candidates.append({'site':o['site'],'value':f['s_reg']-4096})
    return candidates[0]['value']if len(candidates)==1 else None
def main():
    q=argparse.ArgumentParser();q.add_argument('--evidence',type=Path,required=True);q.add_argument('--output',type=Path,required=True);args=q.parse_args()
    if args.output.exists():raise FileExistsError('Existing recalculation preserved')
    cases=[];issues=[];raws=0;sources=[]
    for run in('R01','R02'):
        for file in sorted((args.evidence/run).glob('*_PRIMARY.json.gz')):
            p=read(file);rows=list(p['uses'])
            if p.get('last_use')is not None:rows.append(p['last_use'])
            numbers=[];requests=[]
            for row in rows:
                for frame in row['frames']:
                    observed=frame['reader']['sites'];raws+=len(observed)
                    independently=gate(observed)
                    if independently!=frame['reader']['value']:
                        issues.append([file.name,frame['tick'],'reader/frame mismatch'])
                number=gate(row['frames'][-1]['reader']['sites']);numbers.append(number)
                if number!=row['numeric_result']:issues.append([file.name,row['read_tick'],'reported scalar mismatch'])
                requests.extend(row['requests'])
            old=p.get('old_panel',[])
            old_values=[]
            for item in old:
                rr=item['query']['reader']
                material=[]
                for ob in rr['panel']:
                    f=fields(ob['raw']);raws+=1
                    if f['state']and f['semantic']==1 and f['direction'][:2]==[0,0]and f['direction'][2]in(-1,1):
                        material.append(f['direction'][2])
                derived=material[0]if len(material)==1 else None
                reported=rr.get('formed_native_command',rr.get('command',rr.get('choice')))
                if derived!=reported:issues.append([file.name,item['form'],'old-reader raw mismatch',derived,reported])
                old_values.append(derived)
            if run=='R01':
                origin=gate(p['initial_column25_z30']);raws+=len(p['initial_column25_z30'])
                expected=[];total=origin
                for row in rows:
                    total=total+row['increment']if total is not None else None
                    expected.append(total if p['case']=='real'else None)
            else:
                # Historical teaching pairs T(7,10),H(7,4),U omitted were
                # acquired before these copied snapshots. These are auditor
                # references, never inputs to the runtime candidate.
                origin={'historical_T_positive':10-7,'historical_H_opposite':4-7,
                    'historical_U_teacher_omitted':None,'MAIN_R01_continuity':42}[p['case']]
                expected=[];total=origin
                for row in rows:
                    total=total+row['increment']if total is not None else None
                    expected.append(total)
            if numbers!=expected:issues.append([file.name,'history/increment mismatch',numbers,expected])
            start=p.get('legacy_before',p.get('inherited_legacy'))['uses']
            end=p['legacy_after']['uses']
            if end-start!=len(rows):issues.append([file.name,'nonmonotonic or inconsistent cursor',start,end,len(rows)])
            statuses={}
            for req in requests:
                status=req['receipt']['status'];statuses[status]=statuses.get(status,0)+1
            cases.append({'run':run,'case':p['case'],'before_tick':p['before']['tick'],'after_tick':p['after']['tick'],
                'raw_derived_numbers':numbers,'auditor_expected_from_history':expected,
                'origin_external_physical_or_historical':origin,'old_panel_values':old_values,
                'old_panel_valid_signs':sum(v in(-1,1)for v in old_values),'old_panel_queries':len(old_values),
                'legacy_cursor_start':start,'legacy_cursor_end':end,'cursor_was_reset':end<start,
                'requests_in_accumulator_uses':len(requests),'admission':statuses,'error':p['error'],
                'full_snapshot_local':p.get('full_snapshot',p.get('snapshot')),
                'full_snapshot_sha256':p.get('full_snapshot_sha256',p.get('snapshot_sha256'))})
            sources.append({'file':str(file.relative_to(args.evidence)).replace('\\','/'),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    result={'schema':'APD02.recirculating_accumulator.archive_audit.R1','new_native_ticks':0,'engine_imported':False,
        'RAW_gate_and_initial_column_observations_checked':raws,'cases':cases,'issues':issues,'sources':sources,
        'limits':['Local exact observations are partial, not a full global causal atlas',
            'Historical T/H/U are retained old histories, not new APD02 lessons',
            'MAIN_R01 and R02 continuation are one diagnostic trajectory, not independent learners',
            'Generic turns, alternation and phase timing are prepared P0; no autonomous maintenance or general binary learning claimed']}
    with args.output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps({'cases':len(cases),'RAW':raws,'issues':issues,'output':str(args.output)},ensure_ascii=False))
    if issues:raise SystemExit(1)
if __name__=='__main__':main()
