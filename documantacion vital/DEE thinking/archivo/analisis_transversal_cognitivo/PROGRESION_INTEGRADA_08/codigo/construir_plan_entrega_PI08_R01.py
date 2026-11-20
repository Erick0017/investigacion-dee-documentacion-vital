"""Build an explicit actual PI08 package plan; never creates/extracts a ZIP.

Default is read-only. --guardar writes only a fresh small index/plan directory.
--cerrar-plan also requires all actual gates, current1.36 documents and B72.
Source states/SQLite/telemetry are never copied or modified. No DEE imports.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,fnmatch,hashlib,json,os,re,sys,zlib
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0'
LIMIT=15_000_000;BAN={'.zip','.gz','.sqlite','.sqlite3','.db','.pyd','.whl','.deetsnap'}

def require(x,t):
    if not x:raise ValueError(t)
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def safe_name(s):
    require(isinstance(s,str) and s and '\\'not in s and ':'not in s,'Portable member name')
    q=PurePosixPath(s);require(not q.is_absolute() and not any(x in ('.','..')for x in q.parts),'Unsafe member path');return q
def plain(q,exists=True):
    q=Path(q);q=q if q.is_absolute()else P/q;q=q.resolve(strict=exists)
    require(q.is_relative_to(R.resolve()),'Source outside declared DEE root')
    for n in (q,*q.parents):
        if n.exists():require(not n.is_symlink()and not(getattr(n.lstat(),'st_file_attributes',0)&1024),'No reparse/link source')
        if n==R.resolve():break
    return q
def ptr(j,p):
    if p=='':return j
    require(isinstance(p,str)and p.startswith('/'),'Explicit JSON pointer required')
    for k in p[1:].split('/'):
        k=k.replace('~1','/').replace('~0','~');j=j[int(k)]if isinstance(j,list)else j[k]
    return j
def entry(source,file,role):
    q=plain(source);require(q.is_file(),'Source file absent');safe_name(file)
    require(Path(file).suffix.lower()not in BAN,'State/archive/runtime must remain local, with locator')
    return {'source':str(q),'file':file,'bytes':q.stat().st_size,'sha256':sha(q),'role':role}
def rows(doc):
    env=doc.get('result')
    if isinstance(env,str):env=json.loads(env)
    if not isinstance(env,dict):return []
    if isinstance(env.get('result'),dict):env=env['result']
    return env.get('rows',[])
def leaves(row):
    # Only explicit execution wrappers/stages. Never operational_dependencies.
    inner=row.get('original_result')
    if isinstance(inner,dict):yield from leaves(inner);return
    yield row
def artifacts(doc):
    out=[]
    for outer in rows(doc):
        for r in leaves(outer):
            m=r.get('message')
            if isinstance(m,dict)and isinstance(m.get('artifact'),dict):out.append(m['artifact'])
            effect=r.get('actual_effect')
            if isinstance(effect,dict)and isinstance(effect.get('product'),dict):out.append(effect['product'])
    return out
def deflate_size(q):
    obj=zlib.compressobj(9,zlib.DEFLATED,-15);n=0
    with Path(q).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):n+=len(obj.compress(b))
    return n+len(obj.flush())
def select_group(g):
    home=plain(g.get('directory','ensayos'));require(home.is_dir(),'Primary directory absent')
    # Deliberately shallow, finite selected names, no corpus census.
    candidates=sorted(q for q in home.iterdir()if q.is_file()and q.suffix=='.json')
    chosen=[q for q in candidates if any(fnmatch.fnmatchcase(q.name,v)for v in g['include'])and not any(fnmatch.fnmatchcase(q.name,v)for v in g.get('exclude',[]))]
    return chosen
def body_version(doc):
    return sorted({str(r.get('version'))for outer in rows(doc)for r in leaves(outer)if r.get('version')})

def main(a):
    config_path=plain(Path(a.config).resolve(strict=True));config=read(config_path)
    require(config.get('schema')=='DEE.PI08.package_selection.v1','Exact explicit selection schema')
    require(not a.cerrar_plan or a.guardar,'--cerrar-plan requires --guardar')
    output=plain(Path(a.destino).resolve(),False) if a.destino else P/'fuentes'/('PLAN_ENTREGA_GENERADO_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
    require(output.is_relative_to(P/'fuentes')and not output.exists(),'Fresh P8/fuentes plan directory only')
    missing=[];members={};sources={};selected=[];deferred_C=[];groups={}
    def add(q,name,role):
        e=entry(q,name,role);key=name.casefold()
        if key in members:
            require(members[key]['sha256']==e['sha256'],'Conflicting archive member '+name);return members[key]
        members[key]=e;sources[e['source']]=e['sha256'];return e
    for g in config.get('primary_groups',[]):
        found=select_group(g);groups[g['id']]=len(found)
        if len(found)<g.get('minimum',0):missing.append('primary group '+g['id']+' below actual required minimum')
        for q in found:
            require(q not in selected and q not in deferred_C,'Primary selected twice')
            (deferred_C if g.get('delegate')=='C' else selected).append(q)
    for s in config.get('exact_primaries',[]):
        q=plain(s)
        require(q not in selected,'Exact primary duplicated by a group');selected.append(q)
    index={'schema':'DEE.PI08.portable_primary_index.v1','primaries':[],'products':[],
      'new_Native_ticks':0,'scope':'Exact actual A/F1/administrative primaries only. B material episodes are verified separately from the B bundle index and never relabelled as R03. All source-reference paths are provenance only.'}
    needed={};versions={};primary_summaries=[]
    for q in selected:
        e=add(q,'04_EVIDENCIAS/PRIMARIOS/'+q.name,'Literal selected actual primary; negative/technical outcomes retained')
        doc=read(q);vv=body_version(doc);versions[q.name]=vv
        require('DEE.PI08.successive_contextual_regulation.B.R01'not in vv,'B episodes must travel once through the B delegated bundle, not as R03 general aliases')
        index['primaries'].append({'file':e['file'],'bytes':e['bytes'],'sha256':e['sha256'],'source_reference_for_packager_only':e['source']})
        primary_summaries.append({'file':q.name,'status':doc.get('status'),'versions':vv,'complete_rows':len(rows(doc))})
        for artifact in artifacts(doc):
            require(artifact.get('bytes')==64 and re.fullmatch('[0-9a-f]{64}',artifact.get('sha256','')),'Actual64B product contract required')
            needed.setdefault(artifact['sha256'],[]).append({'primary':q.name,'artifact':artifact})
    found_artifacts={};files_checked=0
    # Explicit narrow environment roots only; never follow a recorded path.
    for root in config.get('artifact_roots',[]):
        home=plain(root)
        if not home.is_dir():missing.append('artifact root absent: '+str(home));continue
        require(home.is_relative_to(C/'sistema/estado/servicios_locales')or home.is_relative_to(C/'reproducibilidad/materiales')or home.is_relative_to(P/'estados'),'Artifact root must be an explicit DEE worker/preserved pair')
        for parent,dirs,files in os.walk(home,followlinks=False):
            plain(parent)
            for name in dirs:plain(Path(parent)/name)
            for name in files:
                q=Path(parent)/name
                if not name.endswith('.bin')or q.stat().st_size!=64:continue
                files_checked+=1;require(files_checked<=config.get('maximum_artifact_files',3000),'Narrow artifact-search bound exceeded')
                h=sha(plain(q))
                if h in needed:found_artifacts.setdefault(h,[]).append(q)
    for h,refs in needed.items():
        if h not in found_artifacts:missing.append('actual64B artifact not recovered '+h);continue
        q=found_artifacts[h][0];e=add(q,'04_EVIDENCIAS/PRIMARIOS/product_'+h[:20]+'.bin','Actual immutable64B product, deduplicated only by exact bytes/hash')
        index['products'].append({'file':e['file'],'bytes':64,'sha256':h,'source_reference_for_packager_only':str(q),
          'source_aliases_same_bytes':[str(x)for x in found_artifacts[h][1:]],'required_by':refs})
    for e in config.get('files',[]):
        q=plain(e['source'],False)
        if not q.is_file():missing.append('explicit file absent '+str(q));continue
        add(q,e['file'],e.get('role','Explicit selected current evidence/code'))
    for spec in config.get('code_manifests',[]):
        proof=plain(spec['source']);items=ptr(read(proof),spec['rows_pointer'])
        require(isinstance(items,list)and len(items)<=spec.get('maximum_files',100),'Bounded explicit code delta list only')
        home=plain(spec['source_root']);excluded=set(spec.get('excluded_files',[]))
        for row in items:
            name=row[spec.get('file_key','file')];safe_name(name)
            if name in excluded:continue
            q=plain(home.joinpath(*PurePosixPath(name).parts));expected=row[spec.get('sha256_key','sha256')]
            require(sha(q)==expected,'Actual/preserved delta differs from its witness '+name)
            add(q,(safe_name(spec['prefix'])/name).as_posix(),spec.get('role','Exact witnessed operating-code delta; no kernel/runtime copy'))
    for spec in config.get('directories',[]):
        home=plain(spec['source'],False)
        if not home.is_dir():missing.append('explicit directory absent '+str(home));continue
        count=0
        for parent,dirs,files in os.walk(home,followlinks=False):
            plain(parent)
            if spec.get('recursive')is False:dirs[:]=[]
            for name in dirs:plain(Path(parent)/name)
            for name in sorted(files):
                q=Path(parent)/name;rel=q.relative_to(home).as_posix()
                if any(fnmatch.fnmatchcase(rel,x)for x in spec.get('exclude',[])):continue
                if spec.get('include')and not any(fnmatch.fnmatchcase(rel,x)for x in spec['include']):continue
                require(q.suffix.lower()not in BAN,'Forbidden large/archive source must be an omission locator')
                add(q,(safe_name(spec['prefix'])/rel).as_posix(),spec.get('role','Explicit selected finite portable/source directory'));count+=1
                require(count<=spec.get('maximum_files',1000),'Explicit directory member bound exceeded')
    b=config.get('B_bundle');Bjob=None
    if b:
        home=plain(b['source'],False)
        if not home.is_dir():missing.append('actual B portable bundle not yet present')
        else:
            bi=read(home/b.get('index','INDICE_B_PI08_R01.json'))
            require(bi['schema']=='DEE.PI08.B.portable_primary_index.R01','Actual B portable index schema')
            actual_B=sum(len(v['primaries'])for v in bi['arms'].values())
            if config.get('require_B_four_closed18',True):
                if set(bi['arms'])!={'real','none','yoked','reference'}or actual_B!=72:missing.append('B actual four-arm72 primary coverage incomplete')
                for role,arm in bi['arms'].items():
                    if not arm.get('summary'):missing.append('B summary absent '+role);continue
                    summary=read(home/arm['summary']['file'])
                    if not(summary.get('closed')is True and summary.get('error')is None and summary.get('opportunities_completed')==18):missing.append('B arm not actually closed18 '+role)
            prefix=b.get('prefix','04_EVIDENCIAS/B')
            for parent,dirs,files in os.walk(home,followlinks=False):
                plain(parent)
                for name in dirs:plain(Path(parent)/name)
                for name in files:
                    if name in b.get('exclude_names',['RESULTADO_RECALCULO.json']):continue
                    q=Path(parent)/name;add(q,(safe_name(prefix)/q.relative_to(home).as_posix()).as_posix(),'B portable actual primary/control/protocol/product; distinct Native and external-reference motors')
            Bjob={'script':prefix+'/RECALCULAR_B_PI08_R01.py','argv':['--raiz','{EXTRACTION}/'+prefix,'--indice',b.get('index','INDICE_B_PI08_R01.json'),'--salida','{OUTPUT}/B.json'],
              'result_file':'B.json','result_schema':'DEE.PI08.B.recalculated_primary_comparison.R01',
              'expect':{'/integrity_passed':True,'/Native_executed':False,'/DEE_imported':False,'/evidence_status':'ALL_FOUR_ARMS_CLOSED18'}}
    else:missing.append('Explicit B portable bundle selection pending')
    Cjob=None;cb=config.get('C_bundle')
    if cb:
        home=plain(cb['source'],False)
        if not home.is_dir():missing.append('Actual C portable bundle not yet present')
        else:
            ci=read(home/cb.get('index','INDICE_C_PI08_R03.json'))
            require(ci['schema']=='DEE.PI08.C.portable_primary_index.R03','Actual C two-stage portable index schema')
            c_entries=list(ci.get('episode_primaries',[]))
            if ci.get('preparation_primary'):c_entries.append(ci['preparation_primary'])
            indexed={v['sha256']for v in c_entries}
            for q in deferred_C:
                if sha(q)not in indexed:missing.append('Actual selected C primary not in delegated Cindex '+q.name)
            prefix=cb.get('prefix','04_EVIDENCIAS/C')
            for parent,dirs,files in os.walk(home,followlinks=False):
                plain(parent)
                for name in dirs:plain(Path(parent)/name)
                for name in files:
                    if name in cb.get('exclude_names',['RESULTADO_RECALCULO.json']):continue
                    q=Path(parent)/name;add(q,(safe_name(prefix)/q.relative_to(home).as_posix()).as_posix(),'C two-stage actual attempts/immediate witnesses; incomplete second stages preserved')
            Cjob={'script':prefix+'/RECALCULAR_C_PI08_R03.py','argv':['--raiz','{EXTRACTION}/'+prefix,'--indice',cb.get('index','INDICE_C_PI08_R03.json'),'--salida','{OUTPUT}/C.json'],
              'result_file':'C.json','result_schema':'DEE.PI08.C.recalculated_two_stage_flow.R03',
              'expect':{'/integrity_passed':True,'/Native_executed':False,'/DEE_imported':False}}
    elif deferred_C:missing.append('Actual C primaries exist; complete delegated Cindex/witness bundle required, never R03alias')
    docs={}
    for key,q,name in [('Manual',C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx','02_MANUAL/DEE_Cognitive_Manual_Maestro.docx'),('Compendium',R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx','02_MANUAL/COMPENDIO_MAESTRO_DEE.docx')]:
        docs[key]=entry(q,name,'Literal complete actual current original, no summary/substitution');sources[str(q)]=docs[key]['sha256']
        expected=config.get('final_documents',{}).get(key)
        if not expected or expected.get('sha256')!=docs[key]['sha256']or expected.get('edition')!='1.36':missing.append('Final published1.36 document binding absent/mismatch '+key)
    gates=[]
    for name in ('scientific_closure','operational_writer_scope','literal_document_publication'):
        g=config.get('gates',{}).get(name)
        if not g or not g.get('source'):missing.append('Actual gate not supplied '+name);continue
        q=plain(g['source'],False)
        if not q.is_file():missing.append('Actual gate file absent '+name);continue
        e=entry(q,'05_CONTROL/'+q.name,'Actual closure/publication gate')
        if ptr(read(q),g['pointer'])!=g['expected']:missing.append('Actual gate false '+name)
        gates.append({'name':name,'evidence':{k:e[k]for k in ('source','bytes','sha256')},'pointer':g['pointer'],'expected':g['expected']})
        add(q,e['file'],e['role'])
    for needed_name in ('00_LEER_PRIMERO.txt','01_INFORME_CIENTIFICO_PI08.md','05_RECALCULO/RECALCULAR_PRIMARIOS_PI08.py','05_RECALCULO/auditoria_documental_PI08.py','05_RECALCULO/heredado/RECALCULAR_PRIMARIOS_PI07_LITERAL.py'):
        if needed_name.casefold()not in members:missing.append('Required actual package member not selected '+needed_name)
    generated={'04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json':index,
      '05_CONTROL/SELECCION_Y_OMISIONES_PI08.json':{'schema':'DEE.PI08.package_selection_and_omissions.v1','config_source':str(config_path),
        'config_sha256':sha(config_path),'primary_groups_actual_counts':groups,'general_primaries_actual':primary_summaries,
        'product_hashes_required':sorted(needed),'product_hashes_recovered':sorted(found_artifacts),'artifact64B_files_examined':files_checked,
        'C_actual_sources_delegated_not_R03_episodes':[str(q)for q in deferred_C],
        'omissions_as_explicitly_declared':config.get('omissions',[]),'new_Native_ticks':0,'full_state_backup':False}}
    verifications=[{'script':'05_RECALCULO/RECALCULAR_PRIMARIOS_PI08.py','argv':['--raiz','{EXTRACTION}','--salida','{OUTPUT}/PRIMARIOS.json'],
      'result_file':'PRIMARIOS.json','result_schema':'DEE.PI08.portable_primary_recalculation.v1','expect':{'/all_checks_passed':True,'/new_Native_ticks':0,'/DEE_imports':0}}]
    if Bjob:verifications.append(Bjob)
    if Cjob:verifications.append(Cjob)
    verifications+=config.get('portable_verifications_additional',[])
    plan={'schema':'DEE.PI08.final_package_plan.v1','status':'OPEN_ACTUAL_FILES_INCOMPLETE_DO_NOT_SEAL','new_Native_ticks_by_packager':0,
      'gates':gates,'complete_documents':docs,'members':list(members.values()),'protected_files':config.get('protected_files',[]),
      'visual_QA_status':config.get('visual_QA_status'),'portable_verifications':verifications,'missing':missing,
      'scope':'Single analysis archive, not executable state backup. All current originals remain local. Prepared paths/results are never evidence.'}
    if a.cerrar_plan:
        require(not missing,'Cannot close plan; actual prerequisites missing: '+'; '.join(missing))
        require(config.get('visual_QA_status')in ('VALIDATED_WITH_REAL_RENDER_WITNESS','NOT_VALIDATED_WITH_ACTUAL_LIMITATION'),'Actual final visual status required')
        plan['status']='CLOSED_ACTUAL_FILES_READY_TO_PACKAGE'
    estimate=None
    if a.estimar:
        estimates=[]
        for e in [*members.values(),*docs.values()]:
            n=deflate_size(e['source']);estimates.append({'file':e['file'],'bytes':e['bytes'],'deflate_payload_bytes':n})
        generated_bytes={k:(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()for k,v in generated.items()}
        payload=sum(v['deflate_payload_bytes']for v in estimates)+sum(len(zlib.compress(v,9))-6 for v in generated_bytes.values())
        headers=sum(76+2*len(e['file'].encode('utf-8'))for e in [*members.values(),*docs.values()])+sum(76+2*len(k.encode())for k in generated)
        estimate={'compressed_payload':payload,'estimated_headers':headers,'manifest_and_finalproof_allowance':524288,
          'conservative_estimated_ZIP_bytes':payload+headers+524288,'strict_final_limit':LIMIT,'is_actual_ZIP_size':False,
          'members_by_compressed_size':sorted(estimates,key=lambda v:v['deflate_payload_bytes'],reverse=True)}
        if estimate['conservative_estimated_ZIP_bytes']>LIMIT:
            missing.append('Compression estimate exceeds15,000,000bytes; explicit evidence selection review required, no automatic omission')
            plan['status']='OPEN_ESTIMATED_OVER_LIMIT_DO_NOT_SEAL'
    # Explicit source originals and all selected artifacts are checked again;
    # the constructor never silently follows a changing life/receipt database.
    if a.cerrar_plan:require(not missing,'Actual closing prerequisites incomplete: '+'; '.join(missing))
    if a.guardar:
        require(all(sha(q)==h for q,h in sources.items()),'Selected source changed concurrently')
        output.mkdir(parents=True,exist_ok=False)
        for name,obj in generated.items():
            q=output/Path(name).name;q.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            plan['members'].append(entry(q,name,'Generated small portable index/explicit coverage; no scientific outcome manufactured'))
        if estimate is not None:
            q=output/'ESTIMACION_COMPRESION.json';q.write_text(json.dumps(estimate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            plan['members'].append(entry(q,'05_CONTROL/ESTIMACION_COMPRESION.json','Estimate only; final ZIP bytes independently checked by packager'))
        if a.cerrar_plan:require(not missing,'Compression or actual prerequisites block closed plan')
        q=output/'PLAN_ENTREGA_PI08.json';q.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'mode':'SMALL_PLAN_AND_INDEX_WRITTEN_NO_ZIP'if a.guardar else'READ_ONLY_PLAN_NO_ZIP',
      'status':plan['status'],'selected_general_primaries':len(selected),'distinct_required64B_products':len(needed),
      'recovered64B_products':len(found_artifacts),'current_documents':docs,'actual_members_selected':len(members),
      'missing':missing,'estimated_ZIP_bytes':None if estimate is None else estimate['conservative_estimated_ZIP_bytes'],
      'output_directory':str(output)if a.guardar else None,'new_Native_ticks':0,'DEE_imports':0},ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--config',required=True);ap.add_argument('--destino',type=Path)
    ap.add_argument('--guardar',action='store_true');ap.add_argument('--cerrar-plan',action='store_true');ap.add_argument('--estimar',action='store_true');main(ap.parse_args())
