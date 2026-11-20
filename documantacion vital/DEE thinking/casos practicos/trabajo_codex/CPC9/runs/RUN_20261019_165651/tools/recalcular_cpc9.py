"""Read-only evidence auditor; no DEE import and no semantic verdict generator.

Numerical contracts are fixed in configuraciones/ before reserved targets.
This script records failures too. Rows from different individuals never form
one repertoire. SHA256+JSON pointers refer to exact primary observations.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def small(q):return{k:q.get(k)for k in('active','state','semantic','s_reg','direction','raw','clock','site')}
def ref(p,pointer):return{'member':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'pointer':pointer}
def frames(d):return{int(f['tick']):(i,f.get('view',f))for i,f in enumerate(d.get('frames',[]))}
def at(fs,t,path):
    if t not in fs:return None
    q=fs[t][1]
    for k in path:q=q[k]
    return q
def qualified(q,v,load=None):return bool(q and q.get('active')and q.get('semantic')==1 and q.get('direction')==v and(load is None or q.get('s_reg')==load))
def main():
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,default=ROOT/'revision/CALCULOS.json');args=a.parse_args()
    out={'schema':'CPC9.primary.recalculation.v1','attribution':'AUDITOR only. These results never enter a participant.',
      'formulas':{'qualified':'active AND semantic==1 AND direction==fixed_expected_vector; load equality only if predeclared',
       'observed_rate':'qualified observations / evaluable observations, with numerator and denominator retained',
       'full_state_equal':'tick equal AND SHA256(RAW uint64 bytes) equal AND SHA256(clocks uint64 bytes) equal',
       'restoration':'full_state_equal plus complete declared receipts equality; documentary metadata is separate',
       'basic_buffers_bytes':'32*N**3, excludes scratch, Python, snapshots and clones',
       'no_energy_estimate':'s_reg and ticks are not electrical energy nor CPU seconds'},
       'integral_cases':[],'continuations':[],'return_cases':[],'query_causal':[],'repertoire':[],'repertoire_causal':[],
       'interpretation_not_automated':'No code here awards NSM levels, intelligence, mind, generality or scientific superiority.'}
    for p in sorted((ROOT/'resultados/vida_integral').glob('*/MEDICIONES.json')):
        d=read(p);fs=frames(d);cfg=d.get('configuration',{});row={'case':d.get('case_id'),'status':d['status'],'source':ref(p,'/frames'),
           'configuration':cfg,'declared_preparations':d.get('preparations'),'last_tick':d.get('last_complete_tick'),'observations':{}}
        for key,ticks,path in(
          ('two_memories',(72,139,206),('two_memory','center')),
          ('quantity',(70,137,204,338,405,472,539,606,673,740,807),('quantity','center')),
          ('query_gates',(76,143,210,277),('cpc9_query_loop','gate'))):
            row['observations'][key]=[{'tick':t,**small(q),'pointer':f'/frames/{fs[t][0]}/view/'+('/'.join(path))}for t in ticks if(q:=at(fs,t,path))is not None]
        row['observations']['current_order']=[{'tick':t,'banks':[{'id':b['id'],'delta':b['delta'],**small(b[field])}for b in fs[t][1]['cpc9_current_order']]}for t,field in((482,'hub'),(549,'hub'),(555,'effect'))if t in fs]
        row['observations']['remote_contact']=[{'tick':t,'banks':[{'id':b['id'],**small(b[field])}for b in fs[t][1]['remote_contact']]}for t,field in((410,'hub'),(416,'effect'),(477,'renewed'),(483,'renewed_effect'))if t in fs]
        row['observations']['old_joint']=[{'tick':t,'banks':{n:small(b['delivery_site'])for n,b in fs[t][1]['joint'].items()}}for t in(281,616,884)if t in fs]
        row['observations']['regulation']=[{'tick':t,'quantity':{n:small(q)for n,q in fs[t][1]['cpc9_regulator']['quantity'].items()}}for t in(136,137)if t in fs]
        row['observations']['count']=[]
        for t in(114,148,215,282,349,416,483,550,617,684,751,818):
            if t not in fs:continue
            f=fs[t][1];z=1 if t==114 else 0 if t==148 else 1 if((t-215)//67)%2==0 else 0
            if t in(114,148):
                values=[{'route':v['route_axis_candidate'],'heading':v['heading'],'physical':v['reading1'if t==114 else'reading2']}for v in f['cpc9_count']['readers']]
            else:values=f['count_repeated']
            good=[{'route':v['route'],'heading':v['heading'],**small(v['physical'])}for v in values if qualified(v['physical'],[v['heading'],1,z])and v['physical']['s_reg']>7]
            row['observations']['count'].append({'tick':t,'qualified_banks':good,'count':len(good),'tested_banks':len(values)})
        receipts=d.get('requests',[]);row['receipt_statuses_recount']=dict(Counter(x.get('receipt',{}).get('status','UNRESOLVED')for x in receipts))
        out['integral_cases'].append(row)
    for p in sorted((ROOT/'resultados/continuacion').glob('*/MEDICIONES.json')):
        d=read(p);fs=frames(d);row={'case':d.get('case_id'),'status':d['status'],'source':ref(p,'/frames'),
           'parent_hash':d.get('parent_snapshot_sha256'),'continuity_type':d.get('continuity_type'),'predictions':d.get('prediction_before_any_new_tick'),
           'quantity':[],'two_memory':[],'old_count':[],'old_joint':[]}
        for t in(941,1008,1075,1142):
            q=at(fs,t,('quantity','center'))
            if q is not None:row['quantity'].append({'tick':t,**small(q)})
        for t in(943,1010,1077,1144):
            q=at(fs,t,('two_memory','center'))
            if q is not None:row['two_memory'].append({'tick':t,**small(q)})
        for t in(952,1019,1086,1153,1220):
            if t in fs:row['old_count'].append({'tick':t,'actual_nontrivial':[{'route':b['route'],'heading':b['heading'],**small(b['physical'])}for b in fs[t][1]['count_repeated']if b['physical']['active']and b['physical']['s_reg']>7]})
        for t in(951,1018,1085,1152,1219):
            if t in fs:row['old_joint'].append({'tick':t,'banks':{n:small(b['delivery_site'])for n,b in fs[t][1]['joint'].items()}})
        pred=d.get('prediction_before_any_new_tick',{}).get('predicted_direction_X',[])
        row['quantity_fixed_prediction_matches']=[q['direction']==[v,0,0]and q['active']for q,v in zip(row['quantity'],pred)]
        if 'instrumental_extension'in d:
            first=[0,0];later=[0,0];by_tick={};failures=[]
            for f in d['frames']:
                qs=f.get('repertoire_queries',[])
                if not qs:continue
                good=0
                for q in qs:
                    ok=qualified(q['physical'],q['expected_auditor_direction']);good+=int(ok)
                    target=first if q['query_index']==0 else later;target[0]+=int(ok);target[1]+=1
                    if not ok:failures.append({'tick':f['tick'],'form':q['form'],'actual':small(q['physical'])})
                by_tick[f['tick']]=[good,len(qs)]
            row['physical_repertoire']={'first_query':first,'later_queries':later,'by_tick':by_tick,'failures':failures,
                'registration_physics_equal':d['instrumental_extension']['before']==d['instrumental_extension']['after'],
                'not_native_growth':True,'not_NSM65':True}
            row['old_TM_during_extension']=[{'tick':t,**small(at(fs,t,('two_memory','center')))}for t in(1948,2015,2082,2149,2216,2283,2350)if t in fs]
            row['old_count_during_extension']=[{'tick':t,'values':[{'route':v['route'],'heading':v['heading'],**small(v['physical'])}for v in fs[t][1]['count_repeated']if v['physical']['active']and v['physical']['s_reg']>7]}for t in(1957,2024,2091,2158,2225,2292)if t in fs]
        if d.get('schema')=='CPC9.E1.post_interference.continuation.v1':
            row['post_interference']=[{'tick':f['tick'],'selected_forms':[{'id':q['id'],**small(q['physical'])}for q in f['repertoire']if q['id']in('F00','F64')],
                'old_TM':small(f['view']['two_memory']['center'])}for f in d['frames']if f['tick']in(2357,2417,2424,2484,2491,2493)]
        out['continuations'].append(row)
    for p in sorted((ROOT/'resultados/retorno').glob('*/MEDICIONES.json')):
        d=read(p)
        if 'rows'in d:
            r={'primary':ref(p,'/rows'),'conditions':[]}
            for x in d['rows']:
                fs=frames(x);vals=[]
                for t,field in((216,'hub'),(221,'use_site')):
                    if t in fs:vals.append({'tick':t,'banks':[{'id':b.get('bank',b.get('id')),**small(b[field])}for b in fs[t][1].get('return',[])]})
                r['conditions'].append({'condition':x['condition'],'full_final_equal':x['full_final_equal'],'full_receipts_equal':x['full_receipts_equal'],'parent_unchanged':x['parent_unchanged'],'observations':vals})
            out.setdefault('return_causal',[]).append(r);continue
        fs=frames(d);out['return_cases'].append({'case':d.get('case_id'),'status':d['status'],'source':ref(p,'/frames'),
           'configuration':d.get('config',d.get('configuration',{})),
           'observations':[{'tick':t,'banks':[{'id':b.get('bank',b.get('id')),**small(b[field])}for b in fs[t][1].get('return',[])]}for t,field in((216,'hub'),(221,'use_site'),(225,'delivery_site'))if t in fs]})
    p=ROOT/'resultados/consulta/QA_INTEGRAL_CAUSAL/MEDICIONES.json'
    if p.exists():
        d=read(p)
        for row in d['rows']:
            fs=frames(row);out['query_causal'].append({'condition':row['condition'],'source':ref(p,'/rows'),
              'final_equal':row['full_final_equal'],'receipts_equal':row['full_receipts_equal'],'parent_unchanged':row['parent_unchanged'],
              'gate210':small(at(fs,210,('cpc9_query_loop','gate'))),
              'TM206':small(at(fs,206,('two_memory','center'))),
              'order555':[{'id':b['id'],**small(b['effect'])}for b in fs[555][1]['cpc9_current_order']]})
    for p in sorted((ROOT/'resultados/repertorio_n67').glob('*/MEDICIONES.json')):
        d=read(p)
        if 'rows'in d:
            for x in d['rows']:
                counts=defaultdict(lambda:[0,0]);failed=[]
                for q in x['queries']:
                    ok=qualified(q['physical'],q['expected_auditor_direction']);counts[q['tick']][0]+=int(ok);counts[q['tick']][1]+=1
                    if not ok:failed.append({'form':q['form'],'tick':q['tick'],**small(q['physical'])})
                out['repertoire_causal'].append({'condition':x['condition'],'source':ref(p,'/rows'),'counts':dict(counts),'failed':failed,
                    'full_final_equal':x['full_final_equal'],'receipts_equal':x['receipts_equal'],'parent_unchanged':x['parent_unchanged']})
            continue
        rounds=defaultdict(lambda:[0,0]);first=[0,0];later=[0,0]
        for f in d['frames']:
            for q in f['queries']:
                ok=qualified(q['physical'],q['expected_auditor_direction']);rounds[f['tick']][0]+=int(ok);rounds[f['tick']][1]+=1
                target=first if q['query_index']==0 else later;target[0]+=int(ok);target[1]+=1
        out['repertoire'].append({'case':d['case_id'],'source':ref(p,'/frames'),'k':d['configuration']['k'],'mode':d['configuration']['mode'],
          'first_query':first,'later_queries':later,'by_tick':dict(rounds),'scope':'Opaque physical correspondences; neither NSM65 mastery nor E1 integration.'})
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'output':str(args.out),'integral_cases':len(out['integral_cases']),'continuations':len(out['continuations']),
      'repertoire':[{k:x[k]for k in('case','first_query','later_queries')}for x in out['repertoire']],
      'continued_comparison_matches':[(x['case'],x['quantity_fixed_prediction_matches'])for x in out['continuations']]},ensure_ascii=False))
if __name__=='__main__':main()
