"""Exact no-tick recalculation/export of CLOSED APD04 shared-prefix AUX controls.

No Native dependency. Signs are independently decoded from uint64 RAW at the
frozen common36 lexical gates or six current-comparison gates. Receipt terminal
states dominate stale cached scheduled copies. Exported originals are lossless
gzip; all source bytes/hashes and complete-pair locators remain identifiable.
"""
from pathlib import Path
import argparse, csv, gzip, hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
CTRL=Path(__file__).resolve().parent
GROUPS=['CONTROLES_LEXICO_REFERENCIA_AUX_R01','CONTROLES_DOCENTE_B_AUX_R01','CONTROLES_REFERENCIAS_RESTANTES_AUX_R02']
EXPECTED=['LEX_PLUS','LEX_MINUS','LEX_OMIT','REF_A','REF_B','REF_OMIT','LEX_B_OMIT','LEX_B_PLUS']

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
    b=p.read_bytes()
    return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def walk(v,path='$'):
    yield path,v
    if isinstance(v,dict):
        for k,x in v.items():
            if isinstance(x,str)and k in('result','result_json'):
                try:x=json.loads(x)
                except json.JSONDecodeError:pass
            yield from walk(x,path+'.'+k)
    elif isinstance(v,list):
        for i,x in enumerate(v):yield from walk(x,path+'['+str(i)+']')
def fields(raw):
    n=int(raw)
    if not 0<=n<2**64:raise ValueError('RAW must remain exact uint64')
    return n&0xffffffff,(n>>60)&15,[((n>>k)&15)-(16 if((n>>k)&15)>=8 else 0)for k in(48,52,56)]
def gates36():
    rows=[]
    for origin,ds in [((33,33,33),[(1,0,0),(0,1,0),(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0),(-1,0,0),(0,-1,0)]),
        ((47,47,47),[(-1,0,0),(0,-1,0),(1,0,0),(0,1,0)]),
        ((47,17,47),[(1,0,0),(0,1,0)]),
        ((47,7,47),[(-1,0,0),(0,-1,0),(1,0,0),(1,1,0)])]:
        for d in ds:
            for sign in(-1,1):rows.append((tuple((origin[i]+4*d[i]+(sign if i==2 else 0))%67 for i in range(3)),sign))
    if len(set(p for p,_ in rows))!=36:raise AssertionError('Frozen reader must have36 unique sites')
    return dict(rows)
GATES=gates36()

def scan(v):
    lexical=[];primitives=[];teachers=[];references=[];requests={};seen=set();checks=[];causal=None;committed=None
    for loc,n in walk(v):
        if not isinstance(n,dict):continue
        if n.get('operation')=='sesion'and'before_tick'in n:causal={'before_tick':n['before_tick'],'after_tick':n['after_tick']}
        if 'committed_snapshot'in n:committed=n['committed_snapshot']
        if isinstance(n.get('references'),list)and len(n['references'])==2:
            rs=n['references']
            if [r.get('site')for r in rs]==[[14,14,15],[16,14,15]]:
                stamp=('references',tuple((r.get('tick'),r['raw'])for r in rs))
                if stamp not in seen:
                    seen.add(stamp);values=[(int(r['raw'])>>32)&65535 for r in rs]
                    checks.append({'check':'reference_s_reg_exact_RAW','ok':all(values[i]==int(r['s_reg'])for i,r in enumerate(rs)),'locator':loc})
                    references.append({'observations':rs,'RAW_s_reg':values,'B_minus_A':values[1]-values[0],'locator':loc})
        if n.get('kind')in('APD04_explicit_lexical_lesson','APD04_explicit_lexical_revision'):
            stamp=('teacher',n['form'],n['input_tick'])
            if stamp not in seen:
                seen.add(stamp);teachers.append({k:n.get(k)for k in('kind','form','teacher_sign','teacher_mode','revision','input_tick','teacher_tick','end_tick','hub','before','after')})
        if n.get('kind')=='APD04_common36_lexical_query':
            stamp=('lex',n['form'],n['read_tick'])
            if stamp in seen:continue
            seen.add(stamp);panel=n['reader']['panel'];c=[]
            checks.append({'check':'all36_frozen_sites','ok':len(panel)==36 and set(tuple(o['site'])for o in panel)==set(GATES),'locator':loc})
            for o in panel:
                st,se,di=fields(o['raw'])
                if st and se==1 and di==[0,0,GATES[tuple(o['site'])]]:c.append({'sign':di[2],'site':o['site'],'raw':o['raw'],'clock':o.get('clock')})
            sign=c[0]['sign']if len(c)==1 else None
            checks.append({'check':'lexical_RAW_equals_formed_native_command','ok':sign==n['reader'].get('formed_native_command'),'locator':loc})
            lexical.append({'form':n['form'],'read_tick':n['read_tick'],'input_tick':n['input_tick'],'end_tick':n['end_tick'],
                'RAW_sign':sign,'reported':n['reader'].get('formed_native_command'),'candidate_count':len(c),'candidates':c,'locator':loc})
        if n.get('kind')in('APD04_candidate_scalar_classification','APD04_candidate_native_balance'):
            t=n['native_trial'];stamp=('numeric',n['kind'],t['read_tick'])
            if stamp in seen:continue
            seen.add(stamp);panel=t['reader']['observations'];c=[]
            expected={(15+2*x,17,15+2*z)for x in(-1,0,1)for z in(0,-1)}
            checks.append({'check':'six_frozen_numeric_sites','ok':len(panel)==6 and set(tuple(o['site'])for o in panel)==expected,'locator':loc})
            for o in panel:
                st,se,di=fields(o['raw']);x=(o['site'][0]-15)//2;z=(o['site'][2]-15)//2
                if st and se==1 and di==[x,1,z]:c.append({'sign':x,'site':o['site'],'raw':o['raw'],'clock':o.get('clock')})
            sign=c[0]['sign']if len(c)==1 else None
            checks.append({'check':'numeric_RAW_equals_physical_choice_and_reader_choice','ok':sign==n.get('physical_choice')and sign==t['reader'].get('choice'),'locator':loc})
            primitives.append({'kind':n['kind'],'value':t.get('raw_sensor_value'),'loads':n.get('public_independent_loads'),
                'read_tick':t['read_tick'],'RAW_sign':sign,'reported':n.get('physical_choice'),'candidate_count':len(c),'candidates':c,'locator':loc})
        if isinstance(n.get('receipt'),dict)and'id'in n['receipt']:
            r=n['receipt'];key=str(r['id']);old=requests.get(key)
            if old is None or old['receipt'].get('status')in('scheduled','pending','admitted'):
                requests[key]={'receipt':r,'site':n.get('site'),'direction':n.get('direction'),'channel':n.get('channel',n.get('port')),'value':n.get('value',n.get('payload')),'locator':loc}
    status={}
    for n in requests.values():
        k=n['receipt'].get('status');status[k]=status.get(k,0)+1
    return {'causal_window':causal,'committed':committed,'lexical':lexical,'primitives':primitives,'teachers':teachers,'references':references,
        'receipts':list(requests.values()),'receipt_statuses':status,'physical_requests':len(requests),'checks':checks}

def recalc(index,base):
    rows=[];checks=[]
    for item in index['primaries']:
        data=base/item['export'];encoded=data.read_bytes();b=gzip.decompress(encoded)
        checks.extend([{'check':'original_decompressed_bytes','ok':sha(b)==item['original_sha256'],'file':item['export']},
                       {'check':'exported_gzip_bytes','ok':sha(encoded)==item['export_sha256'],'file':item['export']}])
        out=scan(json.loads(b));checks.extend(out.pop('checks'));rows.append({**item,'metrics':out})
    summary=[]
    for branch in index['branches']:
        subset=[r for r in rows if r['branch']==branch['label']]
        summary.append({**branch,'events':len(subset),'lexical':[{'event':r['event'],**q}for r in subset for q in r['metrics']['lexical']],
            'primitives':[{'event':r['event'],**q}for r in subset for q in r['metrics']['primitives']],
            'reference_history':[{'event':r['event'],**q}for r in subset for q in r['metrics']['references']],
            'teacher_admission':[{'event':r['event'],'teachers':r['metrics']['teachers'],'requests':r['metrics']['receipts']}for r in subset if r['metrics']['teachers']],
            'receipt_statuses':{k:sum(r['metrics']['receipt_statuses'].get(k,0)for r in subset)for k in sorted({k for r in subset for k in r['metrics']['receipt_statuses']})}})
    return {'schema':'APD04.controls.recalculated_no_ticks.R01','new_native_ticks':0,'branches':summary,'events':rows,
        'checks':checks,'check_count':len(checks),'issues':[c for c in checks if not c['ok']],
        'scope':'Eight dependent AUX branches share one P0 snapshot, not independently trained learners. Material queries may change history. NULL is not zero/HOLD. Omission is not sham. No semantic or P2 verdict from checksum equality.'}

def export(target):
    if target.exists():raise FileExistsError('Never replace a sealed export')
    branches=[];sources=[]
    for group in GROUPS:
        group_root=EV/group
        for p in sorted(group_root.glob('*/CIERRE.json')):
            c=load(p)
            if c['label']not in EXPECTED:raise ValueError('Unexpected control')
            note=None
            if c.get('error')or c.get('source_changed'):
                q=p.parent/'CONTINUACION_MISMA_VIDA_R04/CIERRE_CONTINUACION.json'
                if c['label']!='REF_OMIT'or not q.is_file():raise ValueError('Preserved error/source change lacks authorized same-life closure')
                continuation=load(q)
                if continuation.get('error')or continuation.get('source_changed')or not continuation['continued_same_world_id']:raise ValueError('Continuation is not closed/identity retained')
                note={'preserved_original_error':c['error'],'preserved_original_source_changed':c['source_changed'],
                    'original_failed_interface_tick':c['final_tick'],'continuation':continuation,
                    'scope':'Declared instrument/curriculum revision: same life, explicit aging, paused material protocol; not an exact A/B age/dose match or retrospective cleanup.'}
                c={**c,'final_tick':continuation['final_tick'],'snapshot_sha256':continuation['snapshot_sha256'],'paired':continuation['paired']}
            branch={k:c.get(k)for k in('label','life','kind','condition','prefix_snapshot_sha256','initial_tick','final_tick','snapshot_sha256','elapsed_seconds','paired')}
            branch['preserved_same_life_instrument_continuation']=note;branches.append(branch)
            for source in sorted(p.parent.rglob('[0-9][0-9]_*.json')):sources.append((c['label'],source))
    if set(b['label']for b in branches)!=set(EXPECTED):raise ValueError('Not all authorized8closed; no partial final export')
    target.mkdir(parents=True);index={'schema':'APD04.controls.essential_export.R01','branches':branches,'primaries':[],'closed_artifacts':[]}
    for label,p in sources:
        b=p.read_bytes();original_branch=p.parent
        while original_branch.name!=label:original_branch=original_branch.parent
        within=p.relative_to(original_branch)
        q=target/'PRIMARIOS'/label/(within.as_posix()+'.gz');q.parent.mkdir(parents=True,exist_ok=True);z=gzip.compress(b,compresslevel=9,mtime=0);q.write_bytes(z)
        if gzip.decompress(z)!=b:raise ValueError('Lossless compression failed')
        index['primaries'].append({'branch':label,'event':within.with_suffix('').as_posix(),'original':str(p.relative_to(ROOT)),'original_sha256':sha(b),'original_bytes':len(b),
            'export':q.relative_to(target).as_posix(),'export_sha256':sha(z),'compressed_bytes':len(z)})
    for group in GROUPS:
        for p in sorted((EV/group).rglob('*.json')):
            if len(p.name)>3 and p.name[:2].isdigit()and p.name[2]=='_':continue
            q=target/'CIERRES_Y_PLANES'/group/p.relative_to(EV/group);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
            index['closed_artifacts'].append({'original':str(p.relative_to(ROOT)),'export':q.relative_to(target).as_posix(),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size})
    relevant=['capacidades/lexico_compartido_apd04.py','capacidades/acciones_nativas_apd04.py','capacidades/ecosistema_apd04.py',
        'capacidades/mente_unificada_01.py','capacidades/percepcion_cruda_fi01.py','capacidades/observador_causal_retrospectivo_01.py']
    frozen=CTRL/'FUENTES_CONTROLES_EJECUTADO_R01'
    for rel in relevant:
        p=frozen/'sistema'/rel;q=target/'CODIGO_EJECUTADO'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    for p in [Path(__file__),CTRL/'ejecutar_controles_lexico_referencia_apd04_r01.py',CTRL/'EXTENSION_DOCENTE_B_EJECUTADO_R01/ejecutar_dos_controles_docente_B_apd04_r01.py',
        CTRL/'EXTENSION_REFERENCIAS_NO_INICIADAS_EJECUTADO_R02/completar_solo_referencias_no_iniciadas_apd04_r02.py',
        EV/'CONTROLES_REFERENCIAS_RESTANTES_AUX_R02/REF_OMIT/CONTINUACION_MISMA_VIDA_R03/continuar_misma_vida_ref_omit_apd04_r03.py',
        EV/'CONTROLES_REFERENCIAS_RESTANTES_AUX_R02/REF_OMIT/CONTINUACION_MISMA_VIDA_R04/continuar_ID_existente_ref_omit_apd04_r04.py',frozen/'MANIFEST_FUENTES.json']:
        q=target/'CODIGO_EJECUTADO'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    for p in [CTRL/'HUELLAS_LEXICAS_SNAPSHOTS_N0_R01.json',CTRL/'extraer_huellas_lexicas_snapshots_n0_r01.py']:
        q=target/'EXTRACCION_SNAPSHOTS_N0'/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    index['omissions']={'full_snapshots_and_sqlite':'Complete postSTOP paired exports in each branch.paired remain local, without duplication of engine or every checkpoint.',
        'all_frozen_source_bytes':str(frozen.relative_to(ROOT)),'full_sources_manifest_sha256':sha((frozen/'MANIFEST_FUENTES.json').read_bytes()),
        'not_a_continuable_backup':True,'no_engine_whl_historical_zips':True}
    dump(target/'INDICE.json',index);out=recalc(index,target);dump(target/'RECALCULO.json',out)
    table=[]
    for b in out['branches']:
        for q in b['lexical']+b['primitives']:
            loads=q.get('loads');reading='FORMED_UNIQUE'if q['candidate_count']==1 else'UNFORMED_ZERO_CANDIDATES'if not q['candidate_count']else'AMBIGUOUS_MULTIPLE_CANDIDATES'
            primary=next(r for r in index['primaries']if r['branch']==b['label']and r['event']==q['event'])
            table.append({'branch':b['label'],'life':b['life'],'event':q['event'],'form_or_kind':q.get('form',q.get('kind')),
                'read_tick':q['read_tick'],'RAW_sign':q['RAW_sign'],'reading_state':reading,'candidate_count':q['candidate_count'],'value':q.get('value'),
                'load_left':None if loads is None else loads[0],'load_right':None if loads is None else loads[1],
                'original_primary':primary['original'],'original_sha256':primary['original_sha256'],'JSON_locator':q['locator']})
    with(target/'RESPUESTAS.csv').open('x',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
    with(target/'RESPUESTAS.csv').open(encoding='utf-8-sig',newline='')as f:restored=list(csv.DictReader(f))
    expected_rows=[{k:''if v is None else str(v)for k,v in row.items()}for row in table]
    if restored!=expected_rows:raise ValueError('Flat CSV table failed exact value/NULL-marker roundtrip')
    dump(target/'VERIFICACION_TABLA_CSV.json',{'rows':len(table),'exact_roundtrip':True,'numeric_sign_not_inferred_from_blank':True,
        'unformed_rows':sum(row['reading_state']=='UNFORMED_ZERO_CANDIDATES'for row in table),
        'raw_uint64_primary_remains_exact_JSON_string':True,'format':'Derived flat analytical CSV, one scalar per column; original observations remain in compressed JSON, not a formatted workbook.'})
    manifest=[{'file':p.relative_to(target).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(target.rglob('*'))if p.is_file()]
    dump(target/'MANIFIESTO.json',{'members':manifest,'new_native_ticks_by_export':0})
    print(json.dumps({'closed_branches':len(branches),'primaries':len(sources),'checks':out['check_count'],'issues':len(out['issues']),
        'files':len(manifest)+1,'bytes':sum(r['bytes']for r in manifest),'output':str(target)},ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--export',type=Path);g.add_argument('--recalc',type=Path);args=ap.parse_args()
    if args.export:export(args.export)
    else:
        result=recalc(load(args.recalc/'INDICE.json'),args.recalc)
        print(json.dumps({'new_native_ticks':0,'branches':len(result['branches']),'checks':result['check_count'],'issues':result['issues']},ensure_ascii=False,indent=2))
