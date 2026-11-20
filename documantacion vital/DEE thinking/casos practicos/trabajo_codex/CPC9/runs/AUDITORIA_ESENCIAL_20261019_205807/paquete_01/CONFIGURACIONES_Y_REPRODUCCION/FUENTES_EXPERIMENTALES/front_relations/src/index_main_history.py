"""Compact provenance chain and counted receipts, data-only auditor."""
import argparse,collections,hashlib,json
from pathlib import Path
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--extra-main',type=Path,action='append',default=[]);a=p.parse_args();root=a.run.resolve();front=root/'front_relations';steps=[];previous_ids=set();previous_final=None
    candidates=[root/'resultados/vida_integral/EI_D01/MEDICIONES.json',root/'resultados/continuacion/E1_MAIN_884_1220/MEDICIONES.json']
    candidates += sorted((front/'resultados').glob('E1_MAIN_*/MEDICIONES.json'),key=lambda path:int(path.parent.name.split('_')[2]))
    candidates += sorted((root/'resultados/continuacion').glob('E1_MAIN_K65_*/MEDICIONES.json'))
    candidates += [path if path.is_absolute()else root/path for path in a.extra_main]
    def local_parent(value):
        if not value:return None
        path=Path(value)
        if not path.is_absolute():return root/path
        if path.is_relative_to(root):return path
        # Restore provenance paths against the current extraction, never read
        # the development checkout outside the declared extracted root.
        markers=[i for i,part in enumerate(path.parts)if part.startswith('RUN_')]
        if markers:return root.joinpath(*path.parts[markers[-1]+1:])
        return None
    for path in candidates:
        if not path.is_file():continue
        m=json.loads(path.read_text(encoding='utf8'));requests=m.get('requests',[]);by_id={}
        for value in requests:by_id.setdefault(value.get('id'),[]).append(value)
        ids=set(by_id);new_ids=ids-previous_ids
        parent=m.get('parent',{});parent_file=local_parent(parent.get('path'))
        if not parent_file and path.parent.name=='E1_MAIN_884_1220':parent_file=root/'resultados/vida_integral/EI_D01/T884.deetsnap.gz'
        claimed=parent.get('sha256',m.get('parent_snapshot_sha256'))
        snapshots=[]
        for item in m.get('snapshots',[]):
            name=item.get('path',item.get('name'))
            if not name:continue
            file=path.parent/Path(name).name
            snapshots.append({'path':str(file.relative_to(root)),'exists':file.is_file(),'sha256':sha(file)if file.is_file()else None,'declared_sha256':item.get('sha256'),'bytes':file.stat().st_size if file.is_file()else None,'physical':item.get('physical')})
        final=m.get('final_physical');initial=m.get('initial_physical')
        step={'primary':str(path.relative_to(root)),'sha256':sha(path),'case_id':m.get('case_id',path.parent.name),'status':m['status'],'continuity_type':m.get('continuity_type','NEW_MAIN_FROM_T0'),
          'parent_file':str(parent_file.relative_to(root))if parent_file and parent_file.is_relative_to(root)else str(parent_file)if parent_file else None,
          'parent_sha256_claimed':claimed,'parent_sha256_actual':sha(parent_file)if parent_file and parent_file.is_file()else None,
          'parent_hash_match':claimed==sha(parent_file)if claimed and parent_file and parent_file.is_file()else None,
          'initial_physical':initial,'final_physical':final,'initial_equals_previous_final':initial==previous_final if previous_final else None,
          'snapshots':snapshots,'source_unchanged':m.get('sources_unchanged_during_execution'),'RAW_clock_edits':m.get('MAIN_RAW_clock_edits',m.get('MAIN_RAW_clock_edits',[])),
          'receipts':{'reported_rows':len(requests),'unique_ids':len(ids),'duplicated_ids':sorted(v for v in ids if len(by_id[v])>1),'new_ids_vs_previous':len(new_ids),
            'cumulative_statuses':dict(collections.Counter(rows[-1].get('receipt',{}).get('status','unreported')for rows in by_id.values())),
            'new_statuses':dict(collections.Counter(by_id[v][-1].get('receipt',{}).get('status','unreported')for v in new_ids)),
            'new_rejections':[by_id[v][-1]for v in sorted(new_ids)if by_id[v][-1].get('receipt',{}).get('status','').startswith('rejected')]}}
        if m.get('instrumental_extension'):step['instrumental_extension']=m['instrumental_extension']
        steps.append(step);previous_ids=ids;previous_final=final
    phenomena=[]
    for name in('E1_CF_NO_NEW_FORM_1371_1639','NF_C01_NO_A','NF_C02_NO_B','NF_C03_B_OFFROUTE','NF_C04_B_CUECUT','NF_C05_B_CUESHAM'):
        path=front/'resultados'/name/'MEDICIONES.json'
        if not path.is_file():continue
        m=json.loads(path.read_text(encoding='utf8'));records=[]
        for field in('new_order_observations','late_E2_observations'):
            for index,row in enumerate(m.get(field,[])):
                if row['stage'].startswith('pre_'):continue
                records.append({'field':field,'tick':row['tick'],'stage':row['stage'],'locator':f'{field}/{index}',
                  'all_banks':[{key:item['physical'][key]for key in('site','raw','clock','s_reg','direction')}|{'id':item['id']}for item in row['banks']]})
        phenomena.append({'primary':str(path.relative_to(root)),'sha256':sha(path),'classification':'COUNTERFACTUAL_BRANCH_NOT_MAIN','case':m.get('case',m.get('interventions')),'status':m['status'],'final_physical':m.get('final_physical'),'records':records})
    result={'schema':'CPC9.E1.compact_hashchain_and_noform.v1','engine_imported':False,'notes':['All cumulative IDs are counted once perstep; only newIDs countas newexposures.','Interface declaration is instrumentalextension; equalphysicalhashs do not imply architecture grew natively.','No-form CFpositive is not added to MAIN knowledge.','TheoriginalMAINpredictions remain adverse evenwhen an alternativeCFfunction is identified.'],
      'MAIN_steps':steps,'noform_counterfactuals':phenomena,'causal_trace':{'primary':'front_relations/resultados/E1_NOFORM_TRACE/MEDICIONES.json','local_encounters':[1426,1493,1499,1633,1639],
        'mechanism':'6YZ+11−Y→17Z;after67ticks+11−Y→28−YZ;receiver28−YZ+old5Y+probe7Z→40Z;later+7Y→47YZ;+11−Z→58Y',
        'scope':'Currentphysicalorder in fixedframe, acquired/reusedreceiverstate and consequence. Notnewwordassociation, humanBEFOREuniversal, bidirectionallanguage orR2.'}}
    (front/'revision/MAIN_HASHCHAIN_Y_FENOMENOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'MAIN_steps':len(steps),'counterfactuals':len(phenomena),'bad_parent_hashes':sum(s['parent_hash_match']is False for s in steps),'state_link_mismatches':sum(s['initial_equals_previous_final']is False for s in steps)}))
if __name__=='__main__':main()
