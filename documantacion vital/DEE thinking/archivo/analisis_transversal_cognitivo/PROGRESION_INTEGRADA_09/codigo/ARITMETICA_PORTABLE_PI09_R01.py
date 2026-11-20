"""Closed arithmetic evidence: literal export and stdlib documentary recalc.

Recalculation opens indexed relative files only, never source_reference paths.
No DEE imports, snapshots, Runtime, engine execution or changes to a world.
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, shutil


def read(path): return json.loads(Path(path).read_text('utf-8-sig'))


def info(path,relative=None):
    path=Path(path)
    return {'file':relative if relative is not None else path.name,
            'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def require(value,message):
    if not value: raise ValueError(message)


def write_new(path,value):
    with Path(path).open('x',encoding='utf8')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')


def local(root,relative):
    name=PurePosixPath(relative)
    require(not name.is_absolute()and name.parts and all(p not in ('..','.','')for p in name.parts),'Indexed relative path required')
    require(':'not in relative and '\\'not in relative,'Portable forward-slash path required')
    p=root.joinpath(*name.parts)
    require(not p.is_symlink()and p.resolve().is_relative_to(root.resolve()),'Indexed path escaped bundle')
    return p


def decode(value):
    raw=int(value)
    require(0<=raw<2**64,'Exact uint64 RAW required')
    def signed(shift):
        v=(raw>>shift)&15
        return v-16 if v>=8 else v
    return {'raw':str(raw),'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,
            'semantic':(raw>>60)&15,'direction':[signed(s)for s in(48,52,56)]}


def material_rows(doc):
    result=doc.get('result')
    if isinstance(result,str):result=json.loads(result)
    require(isinstance(result,dict)and isinstance(result.get('result'),dict),'Actual transport envelope required')
    return result['result']['rows']


def summarize(row):
    op=row['native_operation'];trial=op['native_trial'];query=trial['query_tick'];datum=trial['datum_tick']
    require(type(query)is int and type(datum)is int and datum==query+3,'Existing frozen FI128 calendar')
    require(op['operation']in ('suma','diferencia'),'Existing numeric representation only')
    frames=trial['frames'];gate=[f for f in frames if f['tick']==datum-2]
    require(len(gate)==1,'Unique fixed C gate')
    observation=gate[0]['fields']['C'];decoded=decode(observation['raw'])
    valid=(observation['site']==[12,17,18]and observation['tick']==datum-2
           and decoded['state']>0 and decoded['semantic']==1 and decoded['direction']==[1,-1,-1])
    value=(decoded['s_reg']-(32 if op['operation']=='diferencia'else 0))if valid else None
    require(value==row['numeric_result']==op['numeric_reader']['numeric_result'],'Fixed C decoder disagrees with declared actual result')
    requests=trial['requests'];dedup={}
    for request in requests:
        identifier=request['id']
        require(identifier not in dedup or dedup[identifier]==request,'Conflicting repeated Native receipt')
        dedup[identifier]=request
    counts={}
    for request in dedup.values():
        receipt=request['receipt'];require(receipt['id']==request['id'],'Receipt identifier mismatch')
        status=receipt['status'];counts[status]=counts.get(status,0)+1
        require(status in ('applied','rejected_occupied','rejected_conflict','rejected_invalid'),'Unresolved Native receipt')
    require(len(dedup)==176,'FI128 unchanged176 direct requests; no metadata-history scan')
    expected_components=[0]*128
    expected_components[0]=op['operands'][0]
    expected_components[1]=op['operands'][1]if op['operation']=='suma'else 32-op['operands'][1]
    require(trial['raw_components']==expected_components,'Independent per-operand codec mismatch')
    node_frames=[];fixed=[]
    for frame in frames:
        for name,ob in sorted(frame['fields'].items()):
            entry={'offset_from_query':frame['tick']-query,'name':name,'site':ob['site'],
                   'clock':str(ob['clock']),'clock_age_at_frame':frame['tick']-int(ob['clock']),
                   **decode(ob['raw'])}
            require(ob['tick']==frame['tick'],'Frame/observation tick mismatch')
            (node_frames if name.startswith(('left.','right.'))else fixed).append(entry)
    return {'operation':op['operation'],'operands':op['operands'],'query_tick':query,
            'query_moduli':{str(m):query%m for m in(67,391,782)},
            'numeric_gate_tick':datum-2,'numeric_gate':{'observation':observation,**decoded},
            'numeric_result':value,'fixed_signature_valid':valid,'NULL':value is None,
            'material_zero':valid and value==0,
            'before':trial['before'],'after':trial['after'],
            'condition_wait_ticks':row.get('condition_wait_ticks',0),
            'before_condition_wait':row['before'],'after_wait':row.get('after_wait',row['before']),
            'direct_receipts':{'unique_requested':len(dedup),'counts':counts,'aliases':len(requests)-len(dedup)},
            'canonical_requests':[{'id':x['id'],'port':x['port'],'tick':x['tick'],
                                   'offset_from_query':x['tick']-query,'site':x.get('site'),
                                   'direction':x.get('direction'),'payload':x.get('payload'),
                                   'receipt':x['receipt']}for x in dedup.values()],
            'fixed_frames':fixed,'nominal_node_frames':node_frames,
            'recorded_node_names':sorted({x['name']for x in node_frames}),
            'scope':'Observed RAW/clocks at fixed sites; node names identify apparatus locations, never particle ancestry.'}


def physical_equal(a,b):
    fields=('N','tick','RAW_sha256','clocks_sha256')
    return {'equal':all(a.get(k)==b.get(k)for k in fields),
            'fields':{k:{'a':a.get(k),'b':b.get(k),'equal':a.get(k)==b.get(k)}for k in fields}}


def observation_key(item):return item['offset_from_query'],item['name']


def observations_compare(a,b,group):
    left={observation_key(x):x for x in a[group]};right={observation_key(x):x for x in b[group]}
    shared=sorted(set(left)&set(right));diff=[]
    for key in shared:
        changes={f:{'a':left[key][f],'b':right[key][f]}for f in ('site','raw','clock_age_at_frame')if left[key][f]!=right[key][f]}
        if changes:diff.append({'offset_from_query':key[0],'name':key[1],'differences':changes})
    return {'common_observations':len(shared),'a_only':len(set(left)-set(right)),
            'b_only':len(set(right)-set(left)),'differences':diff,
            'first_recorded_disagreement':diff[0]if diff else None,
            'scope':'First sampled nominal-site disagreement only; not first global causal divergence.'}


def recalculate(root,index_path,out):
    root=Path(root).resolve(strict=True);index=read(local(root,index_path))
    require(index['schema']=='DEE.PI09.F1.portable_arithmetic_index.R01','Exact index schema')
    for record in index['files']:
        f=local(root,record['file']);actual=info(f,record['file'])
        require(actual=={k:record[k]for k in ('file','bytes','sha256')},'Indexed member mismatch: '+record['file'])
    cases={};casechecks=[]
    for case in index['cases']:
        proof=read(local(root,case['proof']));require(proof['closed']is True and proof['error']is None,'Only finite closed arithmetic phases')
        rows=[]
        for member in case['primaries']:
            r=material_rows(read(local(root,member)));require(len(r)==1,'One arithmetic row per primary')
            rows.append(summarize(r[0]))
        require(len(rows)==4,'The prospectively fixed4-operation sequence')
        require([(r['operation'],r['operands'])for r in rows[:3]]==[('suma',[6,7]),('suma',[4,5]),('suma',[8,3])],'Fixed development/reserve order')
        require(rows[3]['operation']=='diferencia'and rows[3]['operands']==[rows[2]['numeric_result'],2],'Actual previous integer transported to difference; no expected substitution')
        for a,b in zip(rows,rows[1:]):
            require(a['after']['tick']==b['before_condition_wait']['tick'],'One consecutive physical trajectory without reset')
        require(rows[0]['before_condition_wait']['tick']==884835,'Matched complete source C884835')
        require(all(r['condition_wait_ticks']==case['wait']for r in rows),'Fixed wait before every operation')
        require(all(bool(r['nominal_node_frames'])==case['detailed']for r in rows),'Detailed instrumentation fixed within case')
        cases[case['label']]={'rows':rows,'proof':case['proof'],
                            'actual_results':[r['numeric_result']for r in rows],
                            'new_Native_ticks':proof['new_Native_ticks'],
                            'dedup_direct_requests':sum(r['direct_receipts']['unique_requested']for r in rows)}
        casechecks.append({'case':case['label'],'passed':True})
    comparisons={}
    if 'AR0'in cases and 'AR0NOD'in cases:
        paired=[]
        for n,(a,b)in enumerate(zip(cases['AR0']['rows'],cases['AR0NOD']['rows'])):
            paired.append({'ordinal':n,'physical_before':physical_equal(a['before_condition_wait'],b['before_condition_wait']),
                           'physical_after':physical_equal(a['after'],b['after']),
                           'fixed_frames':observations_compare(a,b,'fixed_frames'),
                           'direct_requests_and_receipts_exact_equal':a['canonical_requests']==b['canonical_requests'],
                           'actual_result_equal':a['numeric_result']==b['numeric_result']})
        comparisons['AR0_vs_AR0NOD']={'rows':paired,
            'all_recorded_physical_endpoints_equal':all(x['physical_before']['equal']and x['physical_after']['equal']for x in paired),
            'scope':'Endpoint full-RAW/clocks hashes, common fixed observations and direct receipt records. '
                    'Global intermediary state, interfaces, agenda and full causal prefix require separately included Root snapshot proof; not inferred here.'}
    if 'AR0'in cases:
        for arm in ('AR36','AR64'):
            if arm not in cases:continue
            comparisons['AR0_vs_'+arm]={'rows':[{'ordinal':i,
                    'nominal_nodes':observations_compare(a,b,'nominal_node_frames'),
                    'fixed_fields':observations_compare(a,b,'fixed_frames')}
                    for i,(a,b)in enumerate(zip(cases['AR0']['rows'],cases[arm]['rows']))],
                    'scope':'Declared waits alter age, phase and consequent encounters. No isolated67 effect or unique carrier ancestry.'}
    result={'schema':'DEE.PI09.F1.portable_arithmetic_recalculation.R01','integrity':True,
            'cases':cases,'case_checks':casechecks,'comparisons':comparisons,
            'Native_executions_by_recalculation':0,'original_source_paths_opened':0,
            'claims_not_made':['Acquired arithmetic','Global content loss','Binary payload identifies ancestry',
                               'Full causal equality from RAW/clocks hashes alone','Detailed observer universally passive']}
    write_new(out,result)
    return result


def export(destination,proofs):
    destination=Path(destination)
    require(not destination.exists(),'Fresh explicit documentary destination only')
    destination.mkdir(parents=True)
    files=[];cases=[]
    def copy(source,relative):
        source=Path(source).resolve(strict=True);before=info(source,relative);target=local(destination,relative)
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        require(info(source,relative)==before==info(target,relative),'Literal source/copy changed')
        files.append({**before,'source_reference_for_packager_only':str(source)});return relative
    for proofpath in proofs:
        proofpath=Path(proofpath).resolve(strict=True);proof=read(proofpath)
        require(proof.get('closed')is True and proof.get('error')is None and len(proof.get('records',[]))==4,'Await actual closed four-step phase; never export in-flight')
        tag=proof['tag'];label=tag.removeprefix('PI09_').removesuffix('_R02')
        require(label in ('AR0','AR36','AR64','AR0NOD'),'Declared four arms only')
        plan=read(Path(proof['plan']));members=[]
        for record in proof['records']:
            primary=Path(record['primary']);require(info(primary)['sha256']==record['sha256'],'Closed primary changed')
            members.append(copy(primary,'primarios/'+primary.name))
        cases.append({'label':label,'wait':plan['wait_applied_before_each_operation'],'detailed':plan['detailed'],
                      'proof':copy(proofpath,'control/'+proofpath.name),'primaries':members})
    self_path=Path(__file__).resolve();copy(self_path,self_path.name)
    index={'schema':'DEE.PI09.F1.portable_arithmetic_index.R01','files':files,'cases':cases,
           'scope':'Literal closed primaries/proofs and a documentary stdlib reader. No complete Native state or engine; not a runnable backup.'}
    write_new(destination/'INDICE_ARITMETICA_PI09_R01.json',index)
    result=recalculate(destination,'INDICE_ARITMETICA_PI09_R01.json',destination/'RESULTADO_RECALCULO.json')
    return {'destination':str(destination),'cases':list(result['cases']),'files':len(files),'Native':0}


if __name__=='__main__':
    parser=argparse.ArgumentParser();commands=parser.add_subparsers(dest='mode',required=True)
    p=commands.add_parser('exportar');p.add_argument('--destino',type=Path,required=True);p.add_argument('--proof',type=Path,action='append',required=True)
    p=commands.add_parser('recalcular');p.add_argument('--raiz',type=Path,required=True);p.add_argument('--indice',default='INDICE_ARITMETICA_PI09_R01.json');p.add_argument('--salida',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='exportar':print(json.dumps(export(args.destino,args.proof),ensure_ascii=False))
    else:
        result=recalculate(args.raiz,args.indice,args.salida)
        print(json.dumps({'integrity':result['integrity'],'cases':list(result['cases']),'Native':0},ensure_ascii=False))
