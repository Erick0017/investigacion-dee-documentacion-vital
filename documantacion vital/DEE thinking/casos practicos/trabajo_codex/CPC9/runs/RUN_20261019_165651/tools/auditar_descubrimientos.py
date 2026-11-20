"""Pure auditor: recalculate local incoming reducers and finite query outcomes.

Never imported by participants. No native engine dependency and no cognitive
verdicts. A local incoming sum does not establish global unique genealogy.
"""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def h(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    out={'schema':'CPC9.discovery.recalculation.v1','queries':[],'return_reducers':[]}
    for p in sorted((ROOT/'resultados/consulta_conservada').glob('*/MEDICIONES.json')):
        d=read(p);delay=d['configuration']['delay'];g=d['geometry']
        out['queries'].append({'case':d['case_id'],'primary':str(p.relative_to(ROOT)),'sha256':h(p),
            'configuration':d['configuration'],'gates':[{'tick':f['tick'],**f['gate']}for f in d['frames']if f['tick']-delay in g['question_ticks']],
            'operands':[{'tick':f['tick'],'fields':f['quantity']}for f in d['frames']if f['tick']-delay in (136,137,203,204,270,271,337,338,404,405)]})
    p=ROOT/'resultados/retorno/RET_CAUSAL/MEDICIONES.json'
    if p.exists():
        d=read(p)
        for row in d['trace']:
            target=row['target'];incoming=[]
            for q in row['pre_Moore27']:
                if any(q['direction'])and[(q['site'][i]+q['direction'][i])%67 for i in range(3)]==target:incoming.append(q)
            if len(incoming)>1:
                sums=[sum(q['direction'][i]for q in incoming)for i in range(3)]
                load=min(19664,sum(q['s_reg']for q in incoming))
                vector=[(x>0)-(x<0)for x in sums];post=row['post']
                out['return_reducers'].append({'primary':str(p.relative_to(ROOT)),'sha256':h(p),'target_tick':row['target_tick'],'bank':row['bank'],
                    'incoming':incoming,'sum_load':load,'sign_sum_direction':vector,'post':post,
                    'local_sum_equals_observed':load==post['s_reg']and vector==post['direction'],
                    'scope':'Only declared Moore27 path; not exhaustive global genealogy'})
        out['return_causal']=[{'condition':row['condition'],'full_final_equal':row['full_final_equal'],'full_receipts_equal':row['full_receipts_equal'],'parent_unchanged':row['parent_unchanged']}for row in d['rows']]
    dest=ROOT/'revision/DESCUBRIMIENTOS_RECALCULO.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'queries':[{'case':q['case'],'gates':[(x['tick'],x['s_reg'],x['direction'])for x in q['gates']]}for q in out['queries']],
        'return_multi_incoming':len(out['return_reducers']),'all_local_sums_match':all(x['local_sum_equals_observed']for x in out['return_reducers'])},ensure_ascii=False))
if __name__=='__main__':main()
