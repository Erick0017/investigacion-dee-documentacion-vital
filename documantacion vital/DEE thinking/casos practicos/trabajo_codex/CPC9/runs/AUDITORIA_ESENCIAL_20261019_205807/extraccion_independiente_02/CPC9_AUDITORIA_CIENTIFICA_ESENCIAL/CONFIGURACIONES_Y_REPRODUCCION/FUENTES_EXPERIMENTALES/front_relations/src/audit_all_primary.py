"""All front primary files: exact uint64, source identity and finite local law."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_primary import one_step,MASK
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);a=p.parse_args();root=a.run.resolve();front=root/'front_relations';files={}
    for folder in(root/'src',root/'base_validada/cpc8/src',root/'front_semantics/src',front/'src'):
        for path in folder.rglob('*.py'):files.setdefault(sha(path),[]).append(str(path.relative_to(root)))
    report={'schema':'CPC9.all_front.primary_audit.v1','engine_imported':False,'scope':'Finite low-load localbranch check, not globalphysicsproof or semanticverdict. Firstdeviation histories preserve gaps and do notassign lineage afterward.',
      'cases':[],'unresolved_sources':[],'invalid_integer_fields':[],'branches':[],'exact_integer_fields':0}
    def check(value,where):
        if isinstance(value,dict):
            for key,item in value.items():
                if key.lower()in('raw','clock'):
                    if (isinstance(item,str)and item.isdigit()and 0<=int(item)<=MASK)or(type(item)is int and 0<=item<=MASK):report['exact_integer_fields']+=1
                    else:report['invalid_integer_fields'].append({'field':where+'/'+key,'value':item})
                else:check(item,where+'/'+key)
        elif isinstance(value,list):
            for index,item in enumerate(value):check(item,where+'/'+str(index))
    paths=sorted(set((front/'resultados').glob('*/MEASUREMENTS.json'))|set((front/'resultados').glob('*/MEDICIONES.json')))
    for path in paths:
        m=json.loads(path.read_text(encoding='utf8'));where=str(path.relative_to(root));check(m,where);groups={}
        report['cases'].append({'primary':where,'sha256':sha(path),'schema':m['schema'],'status':m['status'],'classification':m.get('continuity_type',m.get('classification')),
          'preparations':m.get('preparations',0),'continuations':m.get('continuations',m.get('restored_continuations',0)),'diagnostic_forks':m.get('diagnostic_forks',0),'reference_state_equal':m.get('reference_state_equal'),
          'sources_unchanged_during_execution':m.get('sources_unchanged_during_execution'),'final_physical':m.get('final_physical')})
        for field in('source_sha256','source_sha256_before_execution'):
            for name,digest in m.get(field,{}).items():
                if digest not in files:report['unresolved_sources'].append({'primary':where,'declared_source':name,'sha256':digest})
        for field in('local','decisive_destination_coverage','counterflow_local','meeting_local'):
            if field=='local'and m['schema']=='CPC9.late_export.measurements.v1':continue
            for index,row in enumerate(m.get(field,[])):
                if 'Moore27'not in row:continue
                identity=(field,row.get('id',row.get('bank',row.get('port'))),row.get('surface'),tuple(row['center']))
                groups.setdefault(identity,{})[row['tick']]=(field+'/'+str(index),row['Moore27'])
        for field in('counterprop_observations','tiled_order_observations','order_social_observations','late_E2_observations','new_order_observations'):
            for index,row in enumerate(m.get(field,[])):
                for bankindex,item in enumerate(row.get('surfaces',row.get('banks',[]))):
                    if'Moore27'not in item:continue
                    identity=(field,item['id'],tuple(item['physical']['site']))
                    groups.setdefault(identity,{})[row['tick']]=(field+'/'+str(index)+'/bank/'+str(bankindex),item['Moore27'])
        for identity,ticks in groups.items():
            for tick,(preloc,pre)in ticks.items():
                if tick+1 not in ticks:continue
                postloc,post=ticks[tick+1]
                try:
                    result=one_step(pre);actual=post[13];report['branches'].append({'primary':where,'identity':identity,'pre_tick':tick,'post_tick':tick+1,'pre_locator':preloc,'post_locator':postloc,
                        'reconstruction':result,'observed_raw':actual['raw'],'observed_clock':actual['clock'],'exact':result['raw']==actual['raw']and result['clock']==actual['clock']})
                except ValueError as error:report['branches'].append({'primary':where,'pre_locator':preloc,'not_certified':str(error)})
        if m.get('first_deviation')and'pre_Moore27'in m['first_deviation']:
            row=m['first_deviation'];result=one_step(row['pre_Moore27']);actual=row['post_center']
            report['branches'].append({'primary':where,'pre_locator':'first_deviation/pre_Moore27','post_locator':'first_deviation/post_center','pre_tick':row['pre_tick'],'post_tick':row['post_tick'],
                'reconstruction':result,'observed_raw':actual['raw'],'observed_clock':actual['clock'],'exact':result['raw']==actual['raw']and result['clock']==actual['clock']})
    report['counts']={'primary_containers':len(report['cases']),'preparations':sum(c['preparations']for c in report['cases']),'continuations':sum(c['continuations']for c in report['cases']),'diagnostic_forks':sum(c['diagnostic_forks']for c in report['cases']),
        'local_branch_matches':sum(b.get('exact',False)for b in report['branches']),'local_branch_mismatches':sum(b.get('exact')is False for b in report['branches']),'not_certified':sum('not_certified'in b for b in report['branches']),
        'invalid_uint64':len(report['invalid_integer_fields']),'unresolved_source_identities':len(report['unresolved_sources'])}
    (front/'revision/ALL_PRIMARY_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report['counts']))
if __name__=='__main__':main()
