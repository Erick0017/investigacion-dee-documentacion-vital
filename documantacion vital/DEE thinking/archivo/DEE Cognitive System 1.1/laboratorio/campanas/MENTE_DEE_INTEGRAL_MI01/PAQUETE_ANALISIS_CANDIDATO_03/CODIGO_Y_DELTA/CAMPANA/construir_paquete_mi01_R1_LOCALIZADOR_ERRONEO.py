"""Exportación científica exacta sin motor ni nuevos ticks. No borra originales."""
import gzip,hashlib,json,shutil,sys,time,zipfile
from pathlib import Path
from datetime import datetime,timezone

L=Path(__file__).resolve().parent;R=L.parents[2];E=R/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01';S=R/'sistema';O=L/'EXPORTACION_ANALISIS';P=L/'PAQUETE_ANALISIS_CANDIDATO_01'
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def copy(p,q):q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
def rel(p):return p.relative_to(R).as_posix()
def body(d):
    if'data'in d:return d['data'].get('result',d['data'])
    q=d.get('result',d);return q.get('result',q)if isinstance(q,dict)else q
assert not P.exists(),'Crear otra revisión, no sobrescribir un candidato existente'
P.mkdir();entries=[];selected=[]
for p in O.iterdir():
    if p.is_file():copy(p,P/p.name)
copy(L/'recalcular_mi01.py',P/'RECALCULO/recalcular_mi01.py')
copy(S/'capacidades/observador_causal_retrospectivo_01.py',P/'RECALCULO/snapshot_lector.py')
copy(L/'verificar_paquete_mi01.py',P/'RECALCULO/verificar_paquete_mi01.py')
copy(L/'TABLAS_DATOS.json',P/'RECALCULO/TABLAS_DATOS.json')
copy(L/'PRESUPUESTO.json',P/'CONTINUIDAD/PRESUPUESTO.json')
copy(R/'REANUDACION_MI01.json',P/'CONTINUIDAD/REANUDACION_MI01.json')
copy(R/'LEER_PRIMERO.md',P/'CONTINUIDAD/LEER_PRIMERO_SISTEMA.md')
for p in(S/'estado/vidas').glob('*/VIDA.json'):
    if p.parent.name.startswith(('MI01_','E1_MI01_')):
        target=P/'CONTINUIDAD/VIDAS'/p.parent.name/p.name;copy(p,target)

# Todos los registros únicos JSON de campaña, positivos y adversos. Los productos
# derivados quedan separados para no alimentar el recálculo con su propia salida.
generated=('CALCULOS','TABLAS','DECISIVOS','REFERENCIA_CALCULOS','VERIFICACION','INSPECCION_EDITORIAL','MANIFEST','INDICE_PAQUETE')
for p in sorted(E.glob('*.json')):
    b=p.read_bytes();excluded=p.name.startswith(generated)
    row={'original':rel(p),'absolute_local':str(p),'original_bytes':len(b),'original_sha256':sha(b),'kind':'derived_not_primary'if excluded else'original_campaign_JSON'}
    if not excluded:
        q=P/'EVIDENCIA_CAUSAL/PRIMARIOS'/(p.name+'.gz');q.parent.mkdir(parents=True,exist_ok=True);packed=gzip.compress(b,compresslevel=9,mtime=0);assert gzip.decompress(packed)==b;q.write_bytes(packed)
        row.update({'included':True,'member':q.relative_to(P).as_posix(),'transport':'lossless gzip of EXACT original bytes','member_bytes':len(packed),'member_sha256':sha(packed)})
    else:row.update({'included':False,'why':'Producto derivado o inspección, no primario; recálculo y comprobantes seleccionados se entregan aparte.'})
    entries.append(row)

for p in sorted((E/'FUENTES_POR_SHA256').iterdir()):
    if not p.is_file():continue
    b=p.read_bytes();h=sha(b);assert p.stem==h
    q=P/'CODIGO_Y_DELTA/FUENTES_POR_SHA256'/p.name;copy(p,q)
    entries.append({'original':rel(p),'original_bytes':len(b),'original_sha256':h,'included':True,'member':q.relative_to(P).as_posix(),'kind':'exact_archived_source_revision'})
for p in sorted(L.iterdir()):
    if p.is_file()and p.suffix in('.py','.mjs'):
        q=P/'CODIGO_Y_DELTA/CAMPANA'/p.name;copy(p,q)
        entries.append({'original':rel(p),'original_bytes':p.stat().st_size,'original_sha256':sha(p.read_bytes()),'included':True,'member':q.relative_to(P).as_posix(),'kind':'current_campaign_source; earlier archived versions remain separate'})
seal=read(E/'SELLO_EVALUACION_FIJADA.json')
for f in seal['physical_code']:
    p=R/f['path'];assert sha(p.read_bytes())==f['sha256'];copy(p,P/'CODIGO_Y_DELTA/OPERATIVO'/Path(f['path']))
for sub in('contratos/MENTE_DEE_INTEGRAL_MI01.json','capacidades/CATALOGO_CAPACIDADES.json','documentacion/USO_MENTE_DEE_INTEGRAL_MI01.md'):
    p=S/sub
    if not p.exists()and p.name=='CATALOGO_CAPACIDADES.json':p=R/'CATALOGO_CAPACIDADES.json'
    if p.exists():copy(p,P/'CODIGO_Y_DELTA/OPERATIVO'/p.relative_to(R))
for p in S.glob('**/CATALOGO_CAPACIDADES.json'):
    copy(p,P/'CODIGO_Y_DELTA/OPERATIVO'/p.relative_to(R))
manual=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_7_MI01_SIN_VALIDACION_VISUAL.docx';copy(manual,P/manual.name)
for name in('VERIFICACION_WORD_MI01_ESTRUCTURAL.json','OBSERVADOR_INOCUIDAD_470.json'):
    copy(E/name,P/'VERIFICACIONES'/name)

def bysha(pattern,digest):
    for p in(S/'estado/checkpoints').glob(pattern):
        if sha(p.read_bytes())==digest:return p
    raise FileNotFoundError('Exact snapshot missing '+digest)
cont=read(R/'CONTINUIDAD_MENTE_DEE_INTEGRAL_MI01.json')
specs=[('main_final',S/cont['main']['snapshot'],'Full operational boundary; adverse MAIN current state'),
('main_functional_24525',S/cont['historical_functional_cuts'][1]['snapshot'],'Full operational historical cut;pending2; not current MAIN'),
('main_preparation_selected',S/seal['selected_snapshot'],'Full operational past before frozen preparation; pending0'),
('main_frozen_prefix',bysha('E1_MI01_MAIN.T24752.*.deetsnap.gz','afc1d19c27da44ec1810704cfd08cd6c2c2ff0148dcc5af8411f7b91c9402713'),'Full prepared prefix used by reserved/control trajectories'),
('main_reserved1',bysha('E1_MI01_MAIN.T25757.*.deetsnap.gz','3429dc96e70df2abe142300864ca3e1c7c1583c96f16c0b5d7382bba3bcc7320'),'Full operational end of reserve1'),
('observer470_end',E/'MI01_OBSERVACION_PASIVA_470.FINAL_OPERATIVO.deetsnap.gz','Full replay operation boundary for passive observer equality'),
('main_reserved_end',bysha('E1_MI01_MAIN.T27834.*.deetsnap.gz','b9ab7008451496eed3315612f103fb991fab895e02b9421d638705292ff425e2'),'Full operational end of three reserves'),
('null_reserved_end',bysha('MI01_ACTUADOR_ANULADO_450.T27834.*.deetsnap.gz','081b763136e773d2fca74eb9ce63abbcdec8571229d452b2f235189c46293fd9'),'Full operational nulled-actuator matched branch'),
('free490_end',E/'MI01_VARIACION_LIBRE_490.FINAL.deetsnap.gz','Full operation end after67consecutive no-input ticks')]
for tick in(25008,25009):specs.append(('original470_'+str(tick),E/('MI01_OBSERVACION_PASIVA_470.T'+str(tick)+'.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz'),'Physical diagnostic ONLY: in-flight bridge local variables not a supported continuation boundary'))
for case in(476,477):
    for tick in(25009,25154):specs.append(('intervention'+str(case)+'_'+str(tick),E/('MI01_COALESCENCIA_'+str(case)+'.T'+str(tick)+'.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz'),'Physical diagnostic ONLY: local guard/sham; not supported continuation checkpoint'))
for tick in(25093,25094):specs.append(('second479_'+str(tick),E/('MI01_SEGUNDO_OBSTACULO_479.T'+str(tick)+'.DIAGNOSTICO_NO_OPERATIVO.deetsnap.gz'),'Physical diagnostic ONLY: second encounter; not supported continuation checkpoint'))
selected_paths=set()
for label,p,role in specs:
    assert p.exists(),p;b=p.read_bytes();q=P/'EVIDENCIA_CAUSAL/ESTADOS_SELECCIONADOS'/p.name;copy(p,q);selected_paths.add(p.resolve())
    row={'id':label,'original':rel(p),'absolute_local':str(p),'original_bytes':len(b),'original_sha256':sha(b),'member':q.relative_to(P).as_posix(),'role':role,'included':True};selected.append(row);entries.append({**row,'kind':'selected_complete_snapshot_bytes; not always operational'})
save(P/'EVIDENCIA_CAUSAL/ESTADOS_SELECCIONADOS/INDICE_ESTADOS.json',selected)

# Indice de estados profundos no exportados: no se regeneran ni se borran.
for p in sorted(E.glob('*.gz')):
    if p.resolve()in selected_paths:continue
    b=p.read_bytes();entries.append({'original':rel(p),'absolute_local':str(p),'original_bytes':len(b),'original_sha256':sha(b),'included':False,'kind':'local_complete_or_diagnostic_snapshot','why':'Detalle profundo conservado localmente; contraste esencial seleccionado y primarios íntegros exportados.'})
for p in sorted((S/'estado/checkpoints').iterdir()):
    if not p.is_file()or not p.name.startswith(('MI01_','E1_MI01_'))or p.resolve()in selected_paths:continue
    b=p.read_bytes();entries.append({'original':rel(p),'absolute_local':str(p),'original_bytes':len(b),'original_sha256':sha(b),'included':False,'kind':'local_operation_snapshot','why':'Estado operativo profundo local, no todos los checkpoints caben en el análisis.'})
for p in E.glob('*.txt'):
    b=p.read_bytes();entries.append({'original':rel(p),'absolute_local':str(p),'original_bytes':len(b),'original_sha256':sha(b),'included':False,'kind':'directed_document_reading_extract','why':'Lecturas de antecedente, no nuevos primarios físicos. Se evita duplicar manuales históricos; THINKING45_CONSULTA_DIRIGIDA vacío no se presenta como fuente leída.'})
save(P/'INDICE_FUENTES_Y_OMISIONES.json',{'native_ticks':0,'original_root':str(R),'not_a_complete_backup':True,'contains_no_engine_WHL':True,'primary_JSON_exact_bytes':True,'historical_corpus_not_reaudited':'Only MI01 direct sources and referenced antecedents, not a new inventory of all CPC. No universal recovery/autosufficiency claim.','source_revision_gap':'Some early command/frontend/codec revisions were not archived before subsequent edits. Exact native helper revisions and all frozen physical sources are preserved; no byte-identical certification of every early frontend.','entries':entries})

# Small immediately readable raw evidence, not just verdicts. Each subtree points
# back to an exact source/hash in the primary index. No target feeds a participant.
views=[]
for name,paths in[
('MI01_411_MAIN_RESERVA_1',('rows','native_habitat_frames')),
('MI01_412_MAIN_RESERVA_2',('native_habitat_frames',)),
('MI01_413_MAIN_RESERVA_3',('native_habitat_frames',)),
('MI01_321_MAIN_REUSO',('output',)),
('MI01_COMPUESTA_220',('composition',)),
('MI01_COMPUESTA_223',('composition',)),
('MI01_476_COALESCENCIA_INTERVENCION',('guard_request','frames')),
('MI01_477_COALESCENCIA_INTERVENCION',('guard_request','frames')),
('SENSIBILIDAD_FISICA_EXTERNA_483_0TICKS',('comparison',)),
('MI01_490_VARIACION_LIBRE',('phase3_readings','unique_RAW_hashes','native_inputs_added'))]:
    p=E/(name+'.json');b=p.read_bytes();v=body(json.loads(b));views.append({'source':rel(p),'source_sha256':sha(b),'subtrees':{k:v[k]for k in paths if k in v},'omitted_here':'Other fields are not destroyed; exact full original JSON.gz is included.'})
save(P/'EVIDENCIA_CAUSAL/LECTURA_PRIMARIA_DECISIVA.json',{'is_lossy_view_of_included_full_sources':True,'source_bytes_are_authoritative':True,'cases':views})
save(P/'VERIFICACIONES/RENDER_WORD_NO_DISPONIBLE.json',{'native_ticks':0,'renderer':'bundled documents26.1011.51657/render_docx.py','runtime':'bundled artifact Python3.12; not physical Python3.13','command':'render_docx.py <root Word1.7> --output_dir <lab WORD_RENDER_1_7> --emit_pdf','exit_code':1,'exception':'FileNotFoundError: LibreOffice soffice.exe was not found on PATH','structural_QA_only':True,'visual_QA_completed':False,'no_OS_policy_bypass_or_install':True})
stats={'native_ticks':0,'files_at_stage':sum(p.is_file()for p in P.rglob('*')),'uncompressed_stage_bytes':sum(p.stat().st_size for p in P.rglob('*')if p.is_file()),'selected_states':len(selected),'original_JSON_count':sum(x.get('kind')=='original_campaign_JSON'for x in entries),'original_JSON_bytes':sum(x['original_bytes']for x in entries if x.get('kind')=='original_campaign_JSON'),'primary_gzip_bytes':sum(x.get('member_bytes',0)for x in entries),'omitted_entries':sum(not x.get('included',False)for x in entries),'scope':'Selected states plus all unique campaign primary JSON. No full engine, WHL or historical archive.'}
save(P/'TAMANOS_Y_COBERTURA.json',stats)
print(json.dumps({'candidate_directory':str(P),**stats},ensure_ascii=False,indent=2),flush=True)
