"""Portable stdlib archived calculation; ZERO native imports/ticks.

The sums here are examiner calculations AFTER physical evolution. This module
is never imported by the actor or transport. Wrong/missing native answers stay
in the result table, not integrity errors. No hidden reinterpretation of silence.
"""
import argparse,gzip,hashlib,json
from pathlib import Path
def raw_fields(raw):
    r=int(raw);vv=[(r>>k)&15 for k in(48,52,56)]
    return {'state':r&0xffffffff,'s_reg':(r>>32)&65535,'semantic':(r>>60)&15,'direction':[v-16 if v>=8 else v for v in vv]}
def observations(x):
    if isinstance(x,dict):
        if all(k in x for k in('raw','state','s_reg','semantic','direction','clock','site')):yield x
        for v in x.values():yield from observations(v)
    elif isinstance(x,list):
        for v in x:yield from observations(v)
def native_reader(panel,E=(15,15,15)):
    cs=[]
    for o in panel:
        u=raw_fields(o['raw']);p=list(o['site']);sx=p[0]-E[0]
        if p[1:]!=[E[1]+2,E[2]]or sx not in(-2,0,2):continue
        s=sx//2
        if u['state']>0 and u['semantic']==1 and u['direction']==[s,1,0]:cs.append(s)
    return cs[0]if len(cs)==1 else None
def old_reader(panel):
    cs=[]
    for o in panel:
        u=raw_fields(o['raw'])
        if u['state']>0 and u['semantic']==1 and u['direction']in([0,0,-1],[0,0,1]):cs.append(u['direction'][2])
    return cs[0]if len(cs)==1 else None
def calculate(folder):
    errors=[];rows=[];total_obs=0;total_reader=0
    paths=sorted(folder.glob('B0[234]_TREE_R1_N*/*.json.gz'))+sorted(folder.glob('B02_ENDPOINT_R1/*.json.gz'))
    for p in paths:
        blob=p.read_bytes();x=json.loads(gzip.decompress(blob));r=x['result'];label=str(p.relative_to(folder))
        for o in observations(x):
            total_obs+=1
            if raw_fields(o['raw'])!={k:o[k]for k in('state','s_reg','semantic','direction')}:errors.append(label+':RAWdecode')
            if isinstance(o['clock'],float)or int(o['clock'])<0:errors.append(label+':clockprecision')
        rd=r['reader'];choice=native_reader(rd['observations']);total_reader+=1
        if choice!=rd['choice']:errors.append(label+':frozen_reader')
        receipts=r['requests'];counts={'requested':len(receipts),'applied':0,'rejected':0,'pending':0,'other':0}
        for q in receipts:
            status=q['receipt']['status']
            counts['applied'if status=='applied'else'rejected'if status.startswith('rejected')else'pending'if status in('pending','queued')else'other']+=1
            if 'payload'in q and q.get('receipt',{}).get('requested_tick')!=q.get('tick'):errors.append(label+':receipt_tick')
        old=[]
        if r.get('old_six_panel_after_2N'):
            for z in r['old_six_panel_after_2N']['rows']:
                v=old_reader(z['reader']['panel']);total_reader+=1;old.append(v)
                if v!=z['reader']['formed_native_command']:errors.append(label+':old_fixed_reader')
        raw=r.get('raw_components');datum=None;nodechecks=[]
        if raw is not None:
            t=r['native_datum_tick'];frame=next((z for z in r['frames']if z['tick']==t),None)
            if frame and'D'in frame['fields']:
                u=raw_fields(frame['fields']['D']['raw']);datum={'tick':t,'field':frame['fields']['D'],'examiner_sum_after_execution':sum(raw),
                  'present':u['state']>0,'matches_sum_if_present':u['state']>0 and u['s_reg']==sum(raw)}
            g=r['geometry'];rt=r['leaf_tick']-g['raw_relative_tick']
            for n in g['nodes']:
                z=next((z for z in r['frames']if z['tick']==rt+n['join_tick_relative']),None)
                if not z:continue
                u=raw_fields(z['fields'][n['id']]['raw']);ix=[q['component_index']for q in g['raw_sources']if q['id'].startswith(n['id']+'.')]
                expected=sum(raw[i]for i in ix)
                nodechecks.append({'node':n['id'],'component_indices':ix,'examiner_sum_after_execution':expected,'observed_s_reg':u['s_reg'],'state':u['state'],'matches':u['state']>0 and u['s_reg']==expected})
        ph=r.get('passive_after_2N',r.get('after_2N_passive'))
        expected_old=[-1,-1,1,-1,-1,1]
        rows.append({'file':label,'sha256':hashlib.sha256(blob).hexdigest(),'life':x['INSTRUMENTO']['life_id'],
          'source_tick':r['initial']['tick'],'level':r.get('level'),'case':r['label'],'physical_choice':choice,'counts':counts,
          'valid_binary_response':choice in(-1,1),'neutral_native_response':choice==0,'abstention_or_invalid':choice is None,
          'datum':datum,'nodes':nodechecks,'old_six_responses':old or None,'old_six_matches':sum(a==b for a,b in zip(old,expected_old))if old else None,
          'old_six_expectation_origin':'Same-six baseline from A closure, examiner only, never supplied as actor input',
          'occupied_after_passive':ph['occupied']if ph else None,'end_tick':x['physical']['tick'],'snapshot_sha256':x['INSTRUMENTO']['snapshot_sha256']})
    return {'schema':'MUFI01.B.archived_recalculation.v1','native_ticks':0,'files':len(paths),'RAW_observations_checked':total_obs,
      'fixed_readers_reconstructed':total_reader,'errors':errors,'cases':rows,
      'scope':'Archived arithmetic/readers/admission and matched tables, NOT a replay of the engine. Technical forks are not independent histories. Failures remain represented.'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    r=calculate(a.evidence);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:r[k]for k in('files','RAW_observations_checked','fixed_readers_reconstructed','errors')}))
    if r['errors']:raise SystemExit(1)
if __name__=='__main__':main()
