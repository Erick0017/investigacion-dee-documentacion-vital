"""Data-only exact localbranch and observable extraction for MAIN extensions."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_primary import one_step
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def short(value):return{key:value[key]for key in('tick','site','raw','clock','state','s_reg','semantic','direction')if key in value}
def main():
    p=argparse.ArgumentParser();p.add_argument('--front',type=Path,required=True);a=p.parse_args();rows=[];branches=[]
    paths=set((a.front/'resultados').glob('E1_*/MEDICIONES.json'))|set((a.front/'resultados').glob('NF_*/MEDICIONES.json'))
    for path in sorted(paths):
        m=json.loads(path.read_text(encoding='utf8'));row={'id':path.parent.name,'primary':str(path.relative_to(a.front)),'sha256':sha(path),'schema':m['schema'],
           'status':m['status'],'continuity_type':m.get('continuity_type',m.get('classification')),'initial_physical':m.get('initial_physical'),
           'final_physical':m.get('final_physical'),'parent':m.get('parent'),'instrumental_extension':m.get('instrumental_extension'),
           'predictions':m.get('predictions_before_any_new_tick'),'interventions':m.get('interventions'),'stages':{},'reference_state_equal':m.get('reference_state_equal')}
        for field in('late_E2_observations','new_order_observations'):
            groups={}
            for index,stage in enumerate(m.get(field,[])):
                row['stages'][field+':'+str(stage['tick'])]={'stage':stage['stage'],'banks':{bank['id']:short(bank['physical'])for bank in stage['banks']}}
                for bindex,bank in enumerate(stage['banks']):groups.setdefault((bank['id'],tuple(bank['physical']['site'])),{})[stage['tick']]=(index,bindex,bank)
            for identity,ticks in groups.items():
                for tick,(index,bindex,pre)in ticks.items():
                    if tick+1 not in ticks:continue
                    postindex,postbindex,post=ticks[tick+1]
                    result=one_step(pre['Moore27']);actual=post['physical']
                    branches.append({'case':path.parent.name,'primary':str(path.relative_to(a.front)),'field':field,'bank':identity[0],'pre_tick':tick,'post_tick':tick+1,
                        'pre_locator':f'{field}/{index}/banks/{bindex}','post_locator':f'{field}/{postindex}/banks/{postbindex}',
                        'reconstruction':result,'observed':short(actual),'exact':result['raw']==actual['raw']and result['clock']==actual['clock']})
        requests=m.get('requests',[]);row['requested_inputs']=len(requests);row['rejections']=[v for v in requests if v.get('receipt',{}).get('status','').startswith('rejected')]
        rows.append(row)
    out={'schema':'CPC9.E1.late_social.data_audit.v1','engine_imported':False,'cases':rows,'local_branches':branches,
        'counts':{'cases':len(rows),'branches':len(branches),'exact_branches':sum(x['exact']for x in branches),'mismatches':sum(not x['exact']for x in branches)}}
    (a.front/'revision/MAIN_SOCIAL_RECALCULO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(out['counts']))
if __name__=='__main__':main()
