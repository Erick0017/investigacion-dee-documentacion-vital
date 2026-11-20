"""Engine-free calculations from PC01 exact primary records only."""
from pathlib import Path
from collections import Counter
import argparse,gzip,json,hashlib,sys
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();root=a.evidence;out={'schema':'DCS1.1.PC01.calculations.v1','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'not_a_mind_verdict':True}
def read(p):return json.loads(p.read_bytes())
def rows(p):
    with gzip.open(p,'rt',encoding='utf8')as f:
        for line in f:yield json.loads(line)
out['influence_04']={}
for phase in('early','long'):
    base=root/'INFLUENCIA_ANTERIOR_04'/phase
    if not(base/'PRIMARIOS.json').exists():continue
    prim=read(base/'PRIMARIOS.json');qualified=[];changes=[];segments=[];start=None;last=None;crossings=[];multiparents=[];edges=Counter()
    for r in rows(base/'RUTA_CANDIDATA.jsonl.gz'):
        edges[r['edge']]+=1;q=r['post'];good=q['state']==1 and q['semantic']==1 and q['direction']==[-1,1,1]
        if good:
            if start is None:start=q['tick']
            qualified.append({'tick':q['tick'],'site':q['site'],'s_reg':q['s_reg']})
            if r['source_candidate']['direction']==[-1,1,1]and q['s_reg']!=r['source_candidate']['s_reg']:changes.append({'pre_tick':r['pre_tick'],'post':q,'pre_source':r['source_candidate'],'incoming':r['incoming_sources'],'edge':r['edge']})
            if r['edge']=='EXACT_MULTIPARENT_REDUCER':multiparents.append({'pre_tick':r['pre_tick'],'destination':r['destination'],'incoming':r['incoming_sources'],'post':q})
            if any(r['crossings_candidate'])and r['edge'].startswith('EXACT_'):crossings.append({'tick':q['tick'],'from':r['source_candidate']['site'],'to':r['destination'],'crossings':r['crossings_candidate']})
        elif start is not None:segments.append([start,r['pre_tick']]);start=None
        last=r
    if start is not None:segments.append([start,last['post_tick']])
    first=qualified[0]if qualified else None;episode=next((r for r in prim['events']if first and r['tick']>=first['tick']),None)
    out['influence_04'][phase]={'source':str(base/'PRIMARIOS.json'),'sha256':hashlib.sha256((base/'PRIMARIOS.json').read_bytes()).hexdigest(),'historical_equivalence':prim['historical_equivalence'],'qualified_count':len(qualified),'first_qualified_candidate':first,'first_containing_event':None if episode is None else{'label':episode['label'],'tick':episode['tick']},'qualified_segments':segments,'edge_counts':dict(edges),'load_changes':changes,'multiparent_contributions':multiparents,'boundary_crossing_count':len(crossings),'crossings':crossings,'max_load':max((r['s_reg']for r in qualified),default=None),'path_scope':'Every tick on the candidate trajectory. Only EXACTedges establish empty-target ancestry. No identity inferred from load equality.'}
out['reference_05']={}
for p in sorted((root/'REFERENCIA_CAUSAL_05').glob('*/PRIMARIOS.json')):
    v=read(p);r=v['commit']['result'];out['reference_05'][v['case']]={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'new_magnitudes':r['new_magnitudes'],'nonempty_count':sum(bool(x)for x in r['new_magnitudes']),'denominator':len(r['new_magnitudes']),'old_functions':r['old_functions'],'current_equality':[{ 'label':r['label'],'words':r['result']['SPANISH_DECODED']}for r in v['phases']if r['label'].startswith('current_equality')],'post':v['post']}
out['global_atlas']={}
for p in sorted(root.glob('*/*/*CAMPO*.jsonl.gz')):
    if not(p.parent/'PRIMARIOS.json').exists():continue
    visits=set();encounters=Counter();blocks=Counter();occ=[];statezero=[];frames=0
    for r in rows(p):
        frames+=1;visits.update(i for i,v,c in r['rows']);occ.append(r['occupied']);statezero.append(r['state_zero_raw_nonzero']);blocks.update(r['blocks8'])
        for e in r['encounters']:encounters[','.join(map(str,e['destination']))]+=1
    if not frames:continue
    out['global_atlas'][str(p.relative_to(root))]={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sampled_frames':frames,'visited_sites_in_sampled_frames':len(visits),'max_occupied':max(occ),'min_occupied':min(occ),'max_state_zero_raw_nonzero':max(statezero),'top10_encounter_sites':encounters.most_common(10),'encounter_candidate_events':sum(encounters.values()),'blocks8_integrated_raw_observations':dict(blocks),'coverage':'Every stored global frame; stride and temporal bounds are in the primary. Sampled union is not full-window union when stride>1. Ballistic candidate encounters are not all gradient interactions.'}
for group,key in(('ESPECIALISTA_FASE_06','specialist06'),('FACTORIAL_E1_07','factorial07'),('ACOPLAMIENTO_TARDIO_08','late08')):
    out[key]={v['case']:{'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'result':v['commit']['result']}for p in sorted((root/group).glob('*/PRIMARIOS.json'))if(v:=read(p))}
fact={v['case']:v for p in(root/'FACTORIAL_E1_07').glob('*/PRIMARIOS.json')if(v:=read(p))}
if len(fact)==4:
    out['factorial07_pair_checks']={x+'_'+y:{k:fact[x]['before_I'][k]==fact[y]['before_I'][k]for k in('physical','native_projection','receipts')}for x,y in(('W00','W01'),('W10','W11'))}
    out['factorial07_XOR_effects']={}
    for stage in('immediate','late'):
        rs={k:{i:int(v)for i,v,c in f[stage]['rows']}for k,f in fact.items()};keys=set().union(*(set(r)for r in rs.values()));diff=[{'index':i,'effect_without_H':str(rs['W01'].get(i,0)^rs['W00'].get(i,0)),'effect_with_H':str(rs['W11'].get(i,0)^rs['W10'].get(i,0))}for i in sorted(keys)if(rs['W01'].get(i,0)^rs['W00'].get(i,0))!=(rs['W11'].get(i,0)^rs['W10'].get(i,0))];out['factorial07_XOR_effects'][stage]={'differing_effect_sites':len(diff),'differences':diff}
dest=root/'CALCULOS_PROVISIONALES.json';dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'influence':{k:{z:v[z]for z in('qualified_segments','first_qualified_candidate','first_containing_event','boundary_crossing_count','historical_equivalence')}for k,v in out['influence_04'].items()},'reference05':{k:v['nonempty_count']for k,v in out['reference_05'].items()},'factorial07':out.get('factorial07_pair_checks'),'late08':out['late08']},ensure_ascii=False))
