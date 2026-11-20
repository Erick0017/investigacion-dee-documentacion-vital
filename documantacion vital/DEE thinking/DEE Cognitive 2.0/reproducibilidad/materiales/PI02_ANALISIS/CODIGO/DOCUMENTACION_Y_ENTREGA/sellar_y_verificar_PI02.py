"""One final standard Deflate analysis ZIP, checked by clean portable recalculation.

No DEE import/ticks, original writes, deletion, network or live SQLite copy.
The final ZIP hash lives only in the external verification witness.
"""
from pathlib import Path,PurePosixPath
import csv,datetime,hashlib,io,json,os,stat,subprocess,sys,zipfile
P=Path(__file__).resolve().parent.parent;R=P.parent.parent.parent;C=R/'DEE Cognitive 2.0';S=C/'sistema';E=P/'entrega/EXPEDIENTE'
ZIP=P/'entrega/DEE_PROGRESION_INTEGRADA_02_2026_11_08_ANALISIS.zip'
EXTRACT=R.parents[1]/'PI02_EXTRACCION_FINAL_20261108'
OUT=P/'control/RECALCULO_DESDE_ZIP_FINAL_PI02'
PROOF=P/'control/VERIFICACION_FINAL_EXTERNA_PI02.json'
MANIFEST=E/'CONTROL/MANIFIESTO_SHA256.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def desc(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def safe_name(n):
    rel=PurePosixPath(n)
    if not n or '\\'in n or ':'in n or rel.is_absolute()or any(p in('..','.')for p in rel.parts):raise ValueError('Unsafe archive member:'+n)
    return rel
if ZIP.exists()or PROOF.exists()or EXTRACT.exists()or OUT.exists()or MANIFEST.exists():raise ValueError('A previous final artifact/check exists; inspect it, never overwrite/repeat blindly')
if not(P/'documentos/DOCUMENTOS_PUBLICADOS_PI02_FINAL.json').exists():raise ValueError('Complete Master must be actually published')
selection=read(P/'control/SELECCION_CANONICA_EXPORTACION.json');rows=selection['inclusions']
if not rows:raise ValueError('Empty package')
known={}
for row in rows:
    rel=safe_name(row['file']);p=E/rel;info=p.lstat()
    if stat.S_ISLNK(info.st_mode)or getattr(info,'st_file_attributes',0)&1024:raise ValueError('No reparse/link members')
    if p.suffix.lower()in('.whl','.pyd','.zip','.sqlite3'):raise ValueError('Engine, historical ZIP or operational DB must remain local:'+row['file'])
    if p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:raise ValueError('Closed staging changed:'+row['file'])
    if row['file']in known:raise ValueError('Duplicate selected name')
    known[row['file']]=row
required={'00_LEER_PRIMERO.txt','01_INFORME_CIENTIFICO_PI02.md','MAPAS/CONTINUIDAD_PI02.json','MAPAS/MATRIZ_ANTES_DESPUES.csv','RECALCULO/RECALCULO_TODO.py','MANUAL/DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'}
if not required<=set(known):raise ValueError('Required core missing:'+repr(required-set(known)))
manual=C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx';manual_rel='MANUAL/'+manual.name
if known[manual_rel]['sha256']!=sha(manual):raise ValueError('The entire current Master was not copied literally')
manifest={'schema':'DEE.PI02.content_manifest.SHA256.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'algorithm':'SHA-256','content_members':rows,'exclusions':selection['omissions'],'scope':'Content hashes exclude this manifest itself and the final ZIP. Exact original/canonical evidence and full current Master; no claim of executable backup.','master':desc(manual),'life':'ECI02_PI02_MAIN','N':67,'tick':753346,'internal_manual_edition':'1.29'}
write(MANIFEST,manifest)
allfiles=rows+[{'file':'CONTROL/MANIFIESTO_SHA256.json','bytes':MANIFEST.stat().st_size,'sha256':sha(MANIFEST)}]
with zipfile.ZipFile(ZIP,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True)as z:
    for row in sorted(allfiles,key=lambda x:x['file']):z.write(E/row['file'],row['file'])
if ZIP.stat().st_size>15000000:raise ValueError('Preserved candidate exceeds exact15,000,000byte budget; do not deliver it as compliant')
EXTRACT.mkdir(parents=True,exist_ok=False)
text_checks={'utf8':0,'JSON':0,'CSV':0,'DOCX':0}
with zipfile.ZipFile(ZIP)as z:
    names=z.namelist()
    if len(names)!=len(set(names))or set(names)!={r['file']for r in allfiles}:raise ValueError('ZIP membership differs')
    if z.testzip()is not None:raise ValueError('CRC corruption')
    for row in allfiles:
        data=z.read(row['file'])
        if len(data)!=row['bytes']or hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError('ZIP content differs:'+row['file'])
        rel=safe_name(row['file']);dest=EXTRACT/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb')as f:f.write(data)
        suffix=rel.suffix.lower()
        if suffix in('.json','.jsonl','.csv','.txt','.md','.py','.ps1'):
            txt=data.decode('utf-8-sig');text_checks['utf8']+=1
            if suffix=='.json':json.loads(txt);text_checks['JSON']+=1
            if suffix=='.jsonl':
                for line in txt.splitlines():
                    if line.strip():json.loads(line)
            if suffix=='.csv':
                rs=list(csv.reader(io.StringIO(txt)))
                if not rs or any(len(r)!=len(rs[0])for r in rs):raise ValueError('CSV shape invalid:'+row['file'])
                text_checks['CSV']+=1
        if suffix=='.docx':
            with zipfile.ZipFile(io.BytesIO(data))as doc:
                if doc.testzip()is not None or'word/document.xml'not in doc.namelist():raise ValueError('Invalid complete DOCX')
            text_checks['DOCX']+=1
if sha(EXTRACT/manual_rel)!=sha(manual):raise ValueError('Extracted Master not byte identical')
# Recalculate from the fresh extraction only, no CWD/source-case imports.
command=[sys.executable,'-I','-B','-X','utf8',str(EXTRACT/'RECALCULO/RECALCULO_TODO.py'),'--root',str(EXTRACT),'--out-dir',str(OUT)]
result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',cwd=EXTRACT)
write(P/'control/RECALCULO_DESDE_ZIP_SUBPROCESS_PI02.json',{'command':command,'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'scope':'Documentary recalculation from clean extracted files only, no Native execution.'})
if result.returncode:raise ValueError('Clean archive recalculation failed; preserve candidate and diagnose actual missing bytes')
recfile=OUT/'RECALCULO_TODO_RESULTADO.json';recalc=read(recfile)
engine=[(S/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl','09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'),(C/'motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd','17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'),(S/'estado/checkpoints/ECI02_PI01_MAIN.T735843.085696415346.deetsnap.gz','4c585112f33b126a0ee6114e19ef203f0bab658f76545636a6e70f573d628a50'),(S/'estado/vidas/ECI02_PI01_MAIN/VIDA.json','b70385593dda8feeb3f501d8be3a21f0ef6256e9c8f8d8dde6ab19c8611b6982'),(S/'estado/servicios_persistentes/ECI02_PI01_MAIN/cola.sqlite3','da5f1e75d7c83dc4d9d8ede34afba0466336941c8fecaeed611399a824e8d515')]
preserved=[]
for p,expected in engine:
    actual=desc(p);actual['expected_initial_sha256']=expected;actual['same_bytes_as_initial']=actual['sha256']==expected;preserved.append(actual)
    if not actual['same_bytes_as_initial']:raise ValueError('Critical protected identity differs:'+str(p))
active=read(S/'estado/ACTIVO.json');card=read(S/'estado/vidas/ECI02_PI02_MAIN/VIDA.json')
if active['life_id']!='ECI02_PI02_MAIN'or card['physical']['tick']!=753346:raise ValueError('Principal advanced during final packaging; reconcile instead of describing an old snapshot as current')
verified={'schema':'DEE.PI02.final.external_archive_verification.v1','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ZIP':desc(ZIP),'strict_limit_bytes':15000000,'compression':'ZIP_DEFLATED','one_container_no_password_no_parts':True,'members':len(allfiles),'all_member_CRC_and_bytes_SHA256_verified':True,'manifest':desc(MANIFEST),'manifest_self_hash_excluded':True,'clean_extraction':str(EXTRACT),'text_legibility':text_checks,'extracted_full_Master_equals_actual_product':True,'master':desc(manual),'portable_recalculation':{'result':desc(recfile),'exit_code':0,'record':recalc,'no_Native_execution':True},'critical_preservation_checked':preserved,'scope_of_preservation':'Only listed critical files compared; not blanket immutability of the whole project. Cognitive code/manual/selection changes were authorized and separately witnessed.','final_principal':{'life_id':active['life_id'],'N':67,'tick':753346,'parent':'ECI02_PI01_MAIN T735843'},'current_manual_internal_edition':'1.29','temporary_scope':'Clean extraction and documentQA are regenerable delivery temporaries after review; not the state/evidence directories. Nothing was deleted.','new_Native_ticks_for_archive_verification':0}
write(PROOF,verified)
regpath=P/'REGISTRO_CAMPANA.json';reg=read(regpath);reg.update(phase='CLOSED_COMMITTED_AND_PORTABLE_ZIP_VERIFIED',final_verification=desc(PROOF),delivery=desc(ZIP),finalized_local=datetime.datetime.now().astimezone().isoformat());write(regpath,reg)
print(json.dumps({'zip':desc(ZIP),'members':len(allfiles),'clean_recalculation_exit':0,'proof':str(PROOF),'principal':'ECI02_PI02_MAIN T753346','new_Native_ticks':0},ensure_ascii=False,indent=2))
