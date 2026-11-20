"""PI05 analysis ZIP: default read-only plan, Root-only explicit sealing.

Reuses the PI04 packaging pattern. No engine imports, Native, GUI, cleanup,
document authoring or operational writes. Complete current Word1.32 is literal.
"""
from pathlib import Path,PurePosixPath
import argparse,collections,csv,datetime,hashlib,io,json,os,subprocess,sys
import xml.etree.ElementTree as ET
import zipfile

P=Path(__file__).resolve().parent.parent;R=P.parents[2];W=P.parents[4]
C=R/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';D=P/'documentos'
LIMIT=15_000_000;MANIFEST='05_CONTROL/MANIFIESTO_SHA256.json'
BUNDLE=P/'fuentes/RECALCULO_GLOBAL_PORTABLE_PI05_R01'
FORBIDDEN=('.deetsnap.gz','.deetsnap','.sqlite3','.sqlite3-wal','.sqlite3-shm','.whl','.pyd','.exe','.dll','.zip')

def need(v,message):
    if not v:raise ValueError(message)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def info(p):return {'path':str(Path(p).resolve()),'bytes':Path(p).stat().st_size,'sha256':sha(p)}
def encode(v):return(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')
def write_new(p,b):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(b)
def safe_name(n):
    need(isinstance(n,str)and'\\'not in n and':'not in n and'\x00'not in n,'Unsafe ZIP member')
    q=PurePosixPath(n);need(not q.is_absolute()and'..'not in q.parts and all(p not in('','.')for p in q.parts),'Unsafe ZIP member')
    return q.as_posix()
def regular(p):
    p=Path(p).absolute();need(p.resolve(strict=True).is_relative_to(R.resolve()),'Source outside directed DEE scope')
    for x in(p,*p.parents):
        need(not x.is_symlink()and not(getattr(x.lstat(),'st_file_attributes',0)&1024),'Linked/reparse source')
        if x==R:break
    need(p.is_file(),'Regular file required');return p
def validate_docx(b,manual=False):
    with zipfile.ZipFile(io.BytesIO(b))as z:
        need(z.testzip()is None,'DOCX CRC failure')
        for n in z.namelist():
            if n.endswith(('.xml','.rels')):ET.fromstring(z.read(n))
        if manual:
            core=ET.fromstring(z.read('docProps/core.xml'))
            need('1.32'in[n.text for n in core if n.tag.endswith('}version')],'Full actual Manual must be internal1.32')
            body=z.read('word/document.xml').decode('utf-8')
            need('[[CIERRE_REAL_PENDIENTE]]'not in body and'[[PENDIENTE'not in body,'Unresolved authoring marker')
def validate_content(n,b):
    ext=Path(n).suffix.lower()
    if ext=='.json':json.loads(b.decode('utf-8-sig'))
    elif ext in('.csv','.tsv'):list(csv.reader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t'if ext=='.tsv'else','))
    elif ext=='.jsonl':
        for line in b.decode('utf-8-sig').splitlines():
            if line.strip():json.loads(line)
    elif ext in('.txt','.md','.py','.srt'):b.decode('utf-8-sig')
    elif ext=='.docx':validate_docx(b,'DCS11_MM_001'in n)

def required_paths(a):
    return[a.cierre,a.publicacion,P/'control/ADOPCION_PRODUCTO_PI05.json',a.deltas,
      P/'control/DECISION_FINAL_PI05.json',P/'INFORME_CIENTIFICO_PI05.md',BUNDLE/'MANIFIESTO_SHA256.json',P/'ENSAYOS.jsonl']
def prerequisites(a):
    missing=[str(p)for p in required_paths(a)if not p.is_file()]
    need(not missing,'Closure prerequisites missing: '+', '.join(missing))
    facts=read(a.cierre);need(facts.get('closed_for_authoring')is True,'Scientific closure is not final')
    adopted=read(P/'control/ADOPCION_PRODUCTO_PI05.json');need(adopted.get('phase')=='COMMITTED','No actual PI05 COMMITTED')
    active=read(S/'estado/ACTIVO.json');life=adopted['life_id'];need(active['life_id']==life,'Active life differs from actual adoption')
    card=read(S/'estado/vidas'/life/'VIDA.json');need(card['physical']['N']==67,'N67 expected')
    need(read(C/'PROYECTO.json')['selected_life']==life and read(S/'estado/genesis/SELECCION_PERSONAL.json')['life_id']==life,'Principal selectors disagree')
    principal=facts.get('principal',facts.get('m',{}).get('principal',{}))
    need(principal.get('life_id',principal.get('id'))==life,'Scientific closure life does not match actual selected life')
    tick=principal.get('tick',principal.get('T',principal.get('physical',{}).get('tick')))
    need(tick==card['physical']['tick'],'Scientific closure tick differs from current selected card')
    publication=read(a.publicacion);need(publication.get('status')=='PUBLISHED_LITERAL_STRUCTURALLY_VERIFIED','Literal document publication not completed')
    docs={}
    for label in('Manual','Compendium'):
        item=publication['documents'][label];p=regular(item['published']['path']);b=p.read_bytes()
        need(item.get('literal_staging_equal')is True and len(b)==item['published']['bytes']and digest(b)==item['published']['sha256'],'Published literal differs:'+label)
        validate_docx(b,label=='Manual');docs[label]=p
    deployed=read(a.deltas);need(deployed.get('phase')in('PREPARED_NOT_PROMOTED','COMMITTED'),'Actual deployed manifest required')
    code=deployed.get('deployed_code');need(isinstance(code,list)and len(code)==a.expected_deltas,'Expected exact deployed delta count differs')
    for row in code:
        rel=safe_name(row['file']);p=regular(S/rel);need(sha(p)==row['sha256'],'Current deployed bytes differ:'+rel)
    return facts,publication,docs,life,card,code

RESOURCE_FIELDS=('peak_job_committed_bytes','peak_process_committed_bytes','job_memory_limit','working_set_bytes','peak_working_set_bytes','private_bytes','cpu_user_seconds','cpu_kernel_seconds')
def aggregate_resources(path):
    before=info(path);seen=set();duplicates=0;groups={};requests={};aliases=0;conflicts=[];kinds=collections.Counter();lines=0
    with Path(path).open('rt',encoding='utf-8-sig')as f:
        for number,line in enumerate(f,1):
            if not line.strip():continue
            lines+=1;row=json.loads(line);finger=digest(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
            if finger in seen:duplicates+=1;continue
            seen.add(finger);kind=row.get('kind','UNKNOWN');kinds[kind]+=1
            if kind not in('OWNED_PROCESS_RESOURCES','OWNER_STARTED','OWNER_CLOSED','MATERIAL_REQUEST'):continue
            run=row.get('run');life=row.get('life');need(isinstance(run,str)and isinstance(life,str),'Owner log run/life missing')
            g=groups.setdefault((run,life),{'run':run,'life':life,'pids':set(),'resource_samples':0,'started_records':0,'closed_records':0,'maxima':{},'duration_seconds_max':0.0,'exit_codes':set(),'material_request_ids':set()})
            if type(row.get('pid'))is int:g['pids'].add(row['pid'])
            if kind=='OWNED_PROCESS_RESOURCES':
                g['resource_samples']+=1
                for key in RESOURCE_FIELDS:
                    value=row.get(key)
                    if type(value)in(int,float):g['maxima'][key]=max(g['maxima'].get(key,value),value)
            elif kind=='OWNER_STARTED':g['started_records']+=1
            elif kind=='OWNER_CLOSED':g['closed_records']+=1;g['exit_codes'].add(row.get('exit_code'))
            else:
                identifier=row.get('id');need(isinstance(identifier,str),'Transport request ID missing');key=(life,identifier)
                value={k:row.get(k)for k in('literal','status','before_tick','after_tick','sha256')}
                if key in requests:
                    aliases+=1
                    if requests[key]!=value:conflicts.append({'life':life,'id':identifier,'line':number,'reason':'Same transport ID has different terminal record; not counted twice'})
                else:requests[key]=value
                g['material_request_ids'].add(identifier)
            if type(row.get('elapsed_seconds'))in(int,float):g['duration_seconds_max']=max(g['duration_seconds_max'],row['elapsed_seconds'])
    need(info(path)==before,'Owner resource log changed during closed aggregation')
    output=[]
    for key,g in sorted(groups.items()):
        g['pids']=sorted(g['pids']);g['exit_codes']=sorted(g['exit_codes'],key=str);g['material_requests_unique_in_run']=len(g.pop('material_request_ids'));output.append(g)
    need(not conflicts,'Conflicting transport aliases in owner log')
    need(all(g['closed_records']>=1 for g in output if g['started_records']),'Owner started without a closed record; do not seal yet')
    result={'schema':'DEE.PI05.owner_resources.closed_log_aggregate.R01','source_log':before,'mode':'PASSIVE_LOG_RECALCULATION_ONLY','Native_ticks_executed':0,'lines':lines,'unique_rows':len(seen),'exact_duplicate_rows_excluded':duplicates,'event_kind_counts':dict(kinds),'owners':output,'distinct_owner_runs':len(output),'material_transport_requests_unique':len(requests),'transport_aliases_not_counted_twice':aliases,'conflicting_aliases':conflicts,'max_observed_per_field':{key:max((g['maxima'].get(key,0)for g in output),default=0)for key in RESOURCE_FIELDS},'sum_distinct_owner_cpu_user_seconds':sum(g['maxima'].get('cpu_user_seconds',0)for g in output),'sum_distinct_owner_cpu_kernel_seconds':sum(g['maxima'].get('cpu_kernel_seconds',0)for g in output),'scope':'Per-run CPU counters use their maximum, never sum repeated samples. RAM maxima are host resources, not cognitive memory or simultaneous whole-machine peaks. MATERIAL_REQUEST counts transport operations, not Native inputs or concepts. Native scientific tick/input ledger remains separate.'}
    rp=P/'estados/REPLAY_RP_GUARD_R01';notes=[]
    for name in('RESULTADO_REPRODUCCION.json','CONTEXTO_EJECUCION.json'):
        p=rp/name
        if p.is_file():
            value=read(p);found=[]
            def visit(x,loc='',depth=0):
                if depth>10:return
                if isinstance(x,dict):
                    for k,v in x.items():
                        if k in RESOURCE_FIELDS and type(v)in(int,float):found.append({'pointer':loc+'/'+k,'value':v})
                        elif isinstance(v,(dict,list)):visit(v,loc+'/'+k,depth+1)
                elif isinstance(x,list):
                    for i,v in enumerate(x):visit(v,loc+'/'+str(i),depth+1)
            visit(value);notes.append({'source':info(p),'resource_fields_found':found,'not_merged_as_a_duplicate_owner_run':True})
    result['RP_replay_context_sources']=notes;result['RP_host_resource_coverage']='These separate RP contexts are retained. Any missing per-owner resource samples are a coverage limit, not inferred from the normal-owner log or represented as0.'
    return result

def build_items(a,facts,publication,docs,life,card,code):
    items={};excluded=[];dedup=[]
    def add(source,name,reason):
        source=regular(source);name=safe_name(name);need(not source.name.lower().endswith(FORBIDDEN),'State/engine/archive forbidden in analysis ZIP')
        b=source.read_bytes();need(len(b)<=32_000_000,'Unexpected oversized selected member; do not silently truncate:'+str(source))
        need(name.casefold()not in{n.casefold()for n in items},'Member collision:'+name)
        items[name]={'source':str(source),'data':b,'reason':reason}
    def generated(name,value,reason):items[safe_name(name)]={'source':'generated:closed_documentary_records','data':encode(value),'reason':reason}
    def tree(source,target,reason):
        need(Path(source).is_dir(),'Required directory missing:'+str(source))
        for p in sorted(Path(source).rglob('*')):
            if p.is_file()and'__pycache__'not in p.parts:add(p,target+'/'+p.relative_to(source).as_posix(),reason)
    add(P/'INFORME_CIENTIFICO_PI05.md','01_INFORME_CIENTIFICO.md','Single actual scientific report')
    for label,p in docs.items():add(p,'02_MANUAL/'+p.name,'Complete literal current '+label)
    for root in(P/'mapas',):
        need(root.is_dir(),'Final maps directory missing:'+str(root));names=[]
        for p in sorted(root.iterdir()):
            if p.is_file()and p.suffix.lower()in('.json','.csv','.tsv','.md','.txt'):add(p,'03_MAPAS/'+p.name,'Final coverage/continuity/capability map');names.append(p.name)
        need(any('CONTINUIDAD'in n.upper()for n in names)and any('MATRIZ'in n.upper()and n.lower().endswith('.csv')for n in names),'Final continuity/matrix missing')
    for p in sorted((P/'ensayos').glob('*.json')):add(p,'04_EVIDENCIAS/PRIMARIOS/'+p.name,'Every actual primary, including adverse and technical outcomes')
    need(any(n.startswith('04_EVIDENCIAS/PRIMARIOS/')for n in items),'No actual primaries')
    for p in sorted((P/'control').glob('*.json')):
        if p.name=='VERIFICACION_ZIP_FINAL_PI05.json':continue
        add(p,'04_EVIDENCIAS/CONTROL/'+p.name,'Closed campaign controls/protocols/decisions; protocol is not automatically execution')
    for p in sorted(D.iterdir()):
        if p.is_file()and p.suffix.lower()in('.json','.txt','.md')and'RESPALDO'not in p.name.upper():add(p,'04_EVIDENCIAS/DOCUMENTOS/'+p.name,'Actual document publication/structure/render witness')
    for p in sorted((P/'fuentes').iterdir()):
        if p.is_file()and p.suffix.lower()in('.json','.csv','.md','.txt'):add(p,'04_EVIDENCIAS/FUENTES/'+p.name,'Directed scientific source/extract; reading coverage explicit')
    tree(BUNDLE,'05_RECALCULO/GLOBAL_PORTABLE','One complete37file portable bundle; no duplicated original frames')
    prior=P/'control/PRUEBA_BUNDLE_GLOBAL_REUBICADO_PI05_R01/VERIFICACION_REUBICADA_SIN_ORIGINALES.json'
    add(prior,'05_CONTROL/VERIFICACION_PORTABLE_PREVIA.json','Previously executed isolated documentary check; final extraction is tested again')
    # Keep29/28exact path identities from the real deployed manifest, never a
    # source candidate guessed by date. Count is supplied/frozen by Root.
    for row in code:add(S/row['file'],'06_CODIGO/DELTA_OPERATIVO/'+row['file'],'Actual deployed Cognitive delta; no kernel/WHL')
    protected_hashes={digest(v['data']):n for n,v in items.items()if n.startswith(('06_CODIGO/DELTA_OPERATIVO/','05_RECALCULO/GLOBAL_PORTABLE/'))}
    for p in sorted((P/'codigo').iterdir()):
        if not p.is_file()or p.suffix.lower()not in('.py','.json','.txt','.md'):continue
        b=p.read_bytes();same=protected_hashes.get(digest(b))
        if same:dedup.append({'source':str(p),'identical_included_member':same,'sha256':digest(b)});continue
        add(p,'06_CODIGO/HERRAMIENTAS/'+p.name,'Exact campaign protocol/runner/recalculation/incorporation source; not automatically executed')
    for rel in('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json','sistema/estado/vidas/'+life+'/VIDA.json'):
        add(C/rel,'03_MAPAS/PRODUCTO/'+rel,'Current actual product pointer/card, not complete operational backup')
    decision=read(P/'control/DECISION_FINAL_PI05.json');contract=decision['new_contract']['file'];add(S/contract,'03_MAPAS/CONTRATO_PI05/'+Path(contract).name,'Actual committed continuation contract')
    resources=read(RP/'RECURSOS.json');add(RP/'RECURSOS.json','03_MAPAS/RECURSOS_REPRODUCIBILIDAD_ACTUALES.json','Actual stable resource catalog; no large payload duplication')
    pairloc=[]
    historical_required={'PI03_FINAL_T775355','PI03_PI04_C2B_STOP_T800379','PI03_PI04_C2C_POST_RES_T816019'}
    for alias,entry in resources.get('pairs',{}).items():
        if 'PI05'not in alias and alias not in historical_required:continue
        p=C/entry['product_relative']/'EXPORTACION_SERVICIO.json';need(sha(p)==entry['manifest_sha256'],'Pair manifest changed:'+alias)
        add(p,'03_MAPAS/PARES/'+alias+'/EXPORTACION_SERVICIO.json','Complete local pair manifest only; large payload remains local');pairloc.append({'alias':alias,**entry,'manifest':info(p)})
    need(pairloc,'No stable PI05 full-pair locator')
    for p in sorted((RP/'recetas').glob('*pi05*.json')):add(p,'06_CODIGO/RECETAS/'+p.name,'Actual PI05 recipe; analysis ZIP does not execute Native')
    for name in('RESULTADO_REPRODUCCION.json','CONTEXTO_EJECUCION.json'):
        path=P/'estados/REPLAY_RP_GUARD_R01'/name
        if path.is_file():add(path,'04_EVIDENCIAS/RP_REPLAY/'+name,'Actual closed RP replay context/result; absence of host-resource fields is explicit in aggregate')
    generated('04_EVIDENCIAS/RECURSOS_PROPIETARIOS_PI05.json',aggregate_resources(P/'ENSAYOS.jsonl'),'Deduplicated per-owner resource aggregate, not Native scientific ledger')
    generated('05_CONTROL/COBERTURA_OMISIONES_Y_LOCALIZADORES.json',{'schema':'DEE.PI05.final_analysis.omissions.R01','deep_owner_log':info(P/'ENSAYOS.jsonl'),'full_pair_locators':pairloc,'code_duplicates_replaced_by_identical_members':dedup,'not_included':['All complete operational snapshots/SQLite/queues/outboxes/artifact trees and deep local telemetry','Raw compressed global capture originals: exact RAW/clocksfeatures and original-buffer hashes are included in the portable bundle','Universe/Thinkingbinaries, the two large officialThinkingmanuals, oldZIPcorpus, video/Mac/business material','Nested obsolete sourcecapsules; actual deployed delta and top-level exact runners/protocols are included'],'scope':'Analysis ZIP, not an executable backup. Local Native replay was already performed; clean verification only recalculates archived data. No deletion or cleanup is performed.'},'Explicit exclusions and stable locators')
    readme=P/'entrega/00_LEER_PRIMERO.txt'
    if readme.is_file():add(readme,'00_LEER_PRIMERO.txt','Root final concise reading guide')
    else:
        text='DEE PI05 · análisis y continuidad\nCorte local: '+datetime.datetime.now().astimezone().isoformat()+'\nPrincipal efectivamente seleccionado: '+life+' N67 T'+str(card['physical']['tick'])+'\nManual vigente completo: '+docs['Manual'].name+' (edición interna1.32).\n\nOrden:01_INFORME_CIENTIFICO.md;03_MAPAS;02_MANUAL;04_EVIDENCIAS;05_RECALCULO/GLOBAL_PORTABLE/00_LEER_PRIMERO.txt.\n\nEl ZIP contiene resultados positivos, adversos, controles, código y recálculo. El conjunto operativo grande sigue preservado localmente; sus manifiestos/localizadores viajan aquí. No es un respaldo ejecutable. El recálculo incluido no avanza DEE; la reproducción Native previa y la integración efectiva tienen sus primarios propios. Fuente de verdad: informe, cierre y selector reales; no un PASSglobal.\n'
        items['00_LEER_PRIMERO.txt']={'source':'generated:actual_closed_current_selection','data':text.encode('utf-8'),'reason':'Concise truthful current reading guide'}
    return items

FENCE=r'''from pathlib import Path
import hashlib,json,os,runpy,sys
extraction=Path(sys.argv[1]).resolve();destination=Path(sys.argv[2]).resolve();auditpath=Path(sys.argv[3]);stdlib=Path(sys.base_prefix).resolve();denied=[];counts={'extraction':0,'destination':0,'stdlib':0};imports=[]
def inside(p,r):return p==r or r in p.parents
def hook(event,args):
 if event=='import'and(args[0]=='app'or args[0].startswith('app.')or args[0]=='dee_thinking'or args[0].startswith('dee_thinking.')):imports.append(args[0]);raise PermissionError('No DEE/app import')
 if event!='open'or not args or not isinstance(args[0],(str,bytes,os.PathLike)):return
 p=Path(os.fsdecode(args[0])).resolve();mode=str(args[1]if len(args)>1 else'r');write=any(x in mode for x in('w','a','x','+'))
 if inside(p,extraction)and not write:counts['extraction']+=1;return
 if inside(p,destination):counts['destination']+=1;return
 if p==auditpath.resolve():return
 if inside(p,stdlib)and not write:counts['stdlib']+=1;return
 denied.append(str(p));raise PermissionError('Original workspace/source locator access refused')
sys.addaudithook(hook)
runner=extraction/'05_RECALCULO/GLOBAL_PORTABLE/verificar_y_recalcular.py'
sys.argv=[str(runner),'--recalcular','--grupo','todos','--destino',str(destination)]
try:runpy.run_path(str(runner),run_name='__main__')
finally:
 with auditpath.open('x',encoding='utf8')as f:json.dump({'denied':denied,'DEE_or_app_imports':imports,'open_counts':counts,'external_source_locator_opened':bool(denied),'Native_ticks':0},f,ensure_ascii=False,indent=2)
'''

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--crear-y-verificar',action='store_true');ap.add_argument('--cierre',type=Path,default=P/'control/CIERRE_CIENTIFICO_PI05.json');ap.add_argument('--publicacion',type=Path,default=D/'DOCUMENTOS_PUBLICADOS_PI05_1_32.json');ap.add_argument('--deltas',type=Path,default=P/'control/PREPARACION_PRODUCTO_PI05.json');ap.add_argument('--expected-deltas',type=int,default=28);ap.add_argument('--nombre',default='DEE_PROGRESION_INTEGRADA_05_'+datetime.datetime.now().astimezone().strftime('%Y_%m_%d')+'_ANALISIS.zip');a=ap.parse_args()
    if not a.crear_y_verificar:
        print(json.dumps({'mode':'READ_ONLY_PLAN_NO_ZIP_NO_NATIVE','missing_required':[str(p)for p in required_paths(a)if not p.is_file()],'requires_before_create':['closed_for_authoringtrue and actualMainmatchingcurrentcard','literal published Manual1.32+Compendium','actualCOMMITTED/deployed28exactbytes','finalmaps continuity+matrix and all ownersclosed'],'future_output':str(P/'entrega'/a.nombre),'strict_limit':LIMIT,'Native_ticks':0},ensure_ascii=False));return
    need(safe_name(a.nombre)==a.nombre and len(PurePosixPath(a.nombre).parts)==1 and Path(a.nombre).name==a.nombre and a.nombre.lower().endswith('.zip'),'One safe final ZIP leafname required')
    facts,publication,docs,life,card,code=prerequisites(a);items=build_items(a,facts,publication,docs,life,card,code)
    for n,v in items.items():validate_content(n,v['data'])
    stamp=datetime.datetime.now().astimezone().strftime('%Y%m%d_%H%M%S');home=P/'entrega';home.mkdir(exist_ok=True);stage=home/('staging_'+stamp);need(not stage.exists(),'Staging exists');stage.mkdir()
    final=home/a.nombre;partial=home/(a.nombre+'.writing');proof=P/'control/VERIFICACION_ZIP_FINAL_PI05.json';need(not final.exists()and not partial.exists()and not proof.exists(),'Prior delivery/attempt/proof preserved; choose another reviewed delivery name')
    manifest={'schema':'DEE.PI05.final_analysis.content_manifest.R01','created_local':datetime.datetime.now().astimezone().isoformat(),'content':[{'file':n,'bytes':len(v['data']),'sha256':digest(v['data']),'source':v['source'],'reason':v['reason']}for n,v in sorted(items.items())],'self_hash_and_ZIP_hash_excluded':True};mb=encode(manifest)
    for n,v in items.items():write_new(stage/Path(*PurePosixPath(n).parts),v['data'])
    write_new(stage/Path(*PurePosixPath(MANIFEST).parts),mb)
    with zipfile.ZipFile(partial,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=False)as z:
        for n,v in sorted(items.items()):z.writestr(n,v['data'])
        z.writestr(MANIFEST,mb)
    need(partial.stat().st_size<=LIMIT,'ZIP exceeds15,000,000bytes; candidate/staging retained unchanged, no evidence truncated')
    short=W/('pi05_verificacion_'+datetime.datetime.now().strftime('%H%M%S'));need(not short.exists(),'Fresh extraction already exists');extraction=short/'x';recalc=short/'r';extraction.mkdir(parents=True)
    with zipfile.ZipFile(partial)as z:
        need(z.testzip()is None,'ZIP CRC failure');names=z.namelist();need(len(names)==len(set(n.casefold()for n in names))and set(names)==set(items)|{MANIFEST},'Archive member set differs')
        for n in names:
            safe_name(n);b=z.read(n);dest=extraction/Path(*PurePosixPath(n).parts);need(dest.resolve().is_relative_to(extraction.resolve()),'Extraction escape');need(len(str(dest))<255,'Short Windows extraction path budget exceeded:'+n);write_new(dest,b)
            if n!=MANIFEST:need(b==items[n]['data'],'Archive literal differs');validate_content(n,b)
    need((extraction/'02_MANUAL'/docs['Manual'].name).read_bytes()==docs['Manual'].read_bytes(),'Full current Manual differs after extraction')
    launcher=short/'fence.py';audit=short/'AUDIT.json';write_new(launcher,FENCE.encode('utf-8'))
    command=[sys.executable,'-I','-B','-X','utf8',str(launcher),str(extraction),str(recalc),str(audit)]
    process=subprocess.run(command,cwd=extraction,capture_output=True,text=True,encoding='utf-8',errors='strict',timeout=600,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));write_new(short/'stdout.txt',process.stdout.encode('utf-8'));write_new(short/'stderr.txt',process.stderr.encode('utf-8'))
    need(process.returncode==0,'Fresh extraction documentary batch failed; preserved:'+process.stderr[-1800:]);av=read(audit);need(not av['denied']and not av['DEE_or_app_imports']and av['external_source_locator_opened']is False,'Read fence violation')
    rv=read(recalc/'VERIFICACION_RECALCULO_PORTABLE.json');need(rv['Native_ticks']==0 and rv['DEE_imports']==0 and rv['all_frozen_support_and_original_buffer_hashes_match']is True and len(rv['comparisons'])==6,'Portable batch did not verify all6contrasts')
    for n,v in items.items():
        if not v['source'].startswith('generated:'):need(sha(v['source'])==digest(v['data']),'Selected source changed:'+v['source'])
    need(sha(P/'ENSAYOS.jsonl')==read(stage/'04_EVIDENCIAS/RECURSOS_PROPIETARIOS_PI05.json')['source_log']['sha256'],'Owner log changed after aggregation');prerequisites(a)
    need(not final.exists(),'Concurrent final delivery appeared');partial.rename(final)
    result={'schema':'DEE.PI05.final_analysis.verified.R01','status':'SEALED_AND_CLEAN_EXTRACTION_VERIFIED','zip':info(final),'strict_limit_bytes':LIMIT,'content_members':len(items),'ZIP_members':len(items)+1,'manifest_sha256':digest(mb),'staging':str(stage),'clean_extraction':str(extraction),'pure_recalculation_output':str(recalc),'pure_verifier_command':command,'pure_verifier_returncode':process.returncode,'pure_recalculation':rv,'access_fence':av,'actual_Manual':info(docs['Manual']),'manual_copy_literal':True,'principal_at_sealing':{'life_id':life,'physical':card['physical'],'snapshot_sha256':card['snapshot_sha256']},'new_Native_ticks':0,'no_originals_modified_by_packager':True,'no_cleanup_performed':True,'scope':'Final clean verification reconstructs archived records, not Native. DOCXCRC/XML validation is not visual QA; separate publication/render witness remains authoritative.'}
    write_new(proof,encode(result));print(json.dumps({'zip':result['zip'],'proof':info(proof),'Native_ticks':0,'members':len(items)+1},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
