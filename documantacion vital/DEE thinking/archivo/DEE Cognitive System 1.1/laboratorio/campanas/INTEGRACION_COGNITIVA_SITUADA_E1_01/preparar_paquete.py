"""Loss-accounted extraction of this campaign, not a full system backup."""
from pathlib import Path
from datetime import datetime,timezone
from collections import defaultdict
import json,hashlib,shutil,time,ast
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';SYSTEM=ROOT/'sistema';WORKSPACE=ROOT.parents[4];STAGE=WORKSPACE/'_ic01_analysis_stage_20261021'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')
budget=read(LAB/'PRESUPUESTO_Y_PADRE.json')
if time.monotonic()>budget['monotonic_deadline_seconds']:raise TimeoutError('Original deadline')
STAGE.mkdir(exist_ok=True);sources=[];omissions=[]
def include(src,name,kind):
    src=Path(src);dst=STAGE/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);h=sha(src)
    assert sha(dst)==h;sources.append({'member':name.replace('\\','/'),'original':str(src),'original_bytes':src.stat().st_size,'original_sha256':h,'kind':kind,'byte_identical_to_source':True});return dst
def skim_record(r):
    return{k:v for k,v in r.items()if k not in('operations','storage')}

# Exact executed operation headers retain source revisions and failed reached
# states. Large result objects remain in their original primary JSON files.
result_sources=defaultdict(list)
for p in EV.glob('*.json'):
    if p.name.startswith(('CALCULOS','LECTURA_CIENTIFICA','INDICE_','MANIFIESTO')):continue
    try:d=read(p)
    except Exception:continue
    if isinstance(d,dict)and'INSTRUMENTO'in d and'result'in d:result_sources[canonical(d['result'])].append({'file':p.name,'pointer':'/result','source_sha256':sha(p)})
headers=[];failures=[];code_refs=[];lives=[]
for directory in sorted((SYSTEM/'estado/vidas').iterdir()):
    if not(directory.name.startswith(('IC01_','E1_INTEGRADO_','E1_SITUADO_'))):continue
    p=directory/'VIDA.json'
    if not p.is_file():continue
    r=read(p);record={'source_file':str(p),'source_sha256':sha(p),'life':skim_record(r),'operations':[]};lives.append(r)
    for op in r.get('operations',[]):
        h={k:v for k,v in op.items()if k!='result'}
        if'result'in op:
            ch=canonical(op['result']);h['result_value_sha256']=ch;h['original_primary_result_matches']=result_sources.get(ch,[])
        record['operations'].append(h)
        if op.get('kind','').startswith('FAILED_'):failures.append({'life':r['life_id'],'source_file':str(p),'source_sha256':record['source_sha256'],'operation':h})
        def codes(v,key=''):
            if isinstance(v,dict):
                for k,x in v.items():codes(x,k)
            elif isinstance(v,list):
                for x in v:codes(x,key)
            elif isinstance(v,str)and len(v)==64 and all(c in'0123456789abcdef'for c in v)and key!='saved_source_sha256'and not any(x in key.lower()for x in('snapshot','kernel','wheel','pyd'))and(key.endswith('.py')or any(x in key.lower()for x in('source','code'))):code_refs.append({'life':r['life_id'],'operation':op.get('kind'),'key':key,'sha256':v})
        codes(op.get('details',{}))
    headers.append(record)
write(EV/'OPERACIONES_Y_FALLOS_EXTRAIDOS.json',{'schema':'IC01.exact-operation-header-extraction.v1','native_ticks':0,'records':headers,'failures':failures,'extraction':'For each new campaign life, copy every operation except its possibly large result; preserve result canonical-value SHA and every matching original /result primary. Source file byteSHA is independent of canonical JSON equality.'})

# All primary operation files and finite specifications are retained. Only
# aggregate copies of already retained results are reduced to indexed fields.
for p in sorted(EV.glob('*.json')):
    if p.name.startswith(('CALCULOS','LECTURA_CIENTIFICA','INDICE_','MANIFIESTO')):continue
    d=read(p)
    aggregate=isinstance(d,dict)and'INSTRUMENTO'not in d and('final_record'in d or('prefix3'in d and'continuation_same_parent'in d))
    if aggregate:
        extract={};dropped=[]
        for k,v in d.items():
            if k in('prefix3','common_probe_separate_branch','continuation_same_parent'):dropped.append({'pointer':'/'+k,'value_sha256':canonical(v)});continue
            extract[k]=skim_record(v)if k in('final_record','prefix_record')and isinstance(v,dict)else v
            if k in('final_record','prefix_record')and isinstance(v,dict):dropped.append({'pointer':'/'+k+'/operations','value_sha256':canonical(v.get('operations',[]))})
        name='EXTRACTOS/'+p.name;write(STAGE/name,{'source_file':str(p),'source_sha256':sha(p),'source_bytes':p.stat().st_size,'extracted_values':extract,'excluded_duplicate_values':dropped,'scope':'Deterministic field extraction, not original-file byte identity; full operation headers and original primary results are included separately.'});omissions.append({'source':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'reason':'Aggregate duplication; deterministic extraction retains identity, genealogy and unique fields. Operations headers preserved; primary result files retained.','extraction_member':name})
    else:include(p,'EVIDENCIA_ESENCIAL/'+p.name,'primary_or_declared_protocol')

code_by_hash=defaultdict(list);syntax=[]
for p in sorted(LAB.glob('*.py')):
    try:ast.parse(p.read_text(encoding='utf8'));syntax.append({'source':p.name,'syntax_valid':True})
    except SyntaxError as e:syntax.append({'source':p.name,'syntax_valid':False,'error':str(e),'scope':'Preserved failed source, not a validated executable claim'})
    member='CODIGO_Y_RECALCULO/EXPERIMENTOS/'+p.name;include(p,member,'exact_experimental_source_revision');code_by_hash[sha(p)].append(member)
for p in sorted(LAB.glob('*.mjs')):include(p,'CODIGO_Y_RECALCULO/EXPERIMENTOS/'+p.name,'table_authoring_source')
for name in('recalcular.py','resumir_ciencia.py','reproducir_entorno.py'):
    include(LAB/name,'CODIGO_Y_RECALCULO/'+name,'portable_or_declared_dependency_recalculation')
for name in('PRESUPUESTO_Y_PADRE.json','PROTOCOLO_MAIN_CONGELADO.json','VERIFICACION_TABLAS_ARTIFACT.json'):
    include(LAB/name,'CONFIGURACION_Y_VERIFICACION/'+name,'frozen_protocol_or_technical_verification')
for p in sorted((SYSTEM/'capacidades/integracion_situada_01').glob('*.py')):
    member='CODIGO_Y_RECALCULO/INCORPORADO/capacidades/integracion_situada_01/'+p.name;include(p,member,'incorporated_system_source');code_by_hash[sha(p)].append(member)
for name in['gestionar.py','app/access_guard.py','app/lives.py','app/native_tools.py','app/process_control.py','app/habitat_externo/pendulum_worker.py','capacidades/conductos_acceso_aa01.py','capacidades/puente_adquirible.py','capacidades/habitat_externo_01.py','contratos/INTEGRACION_COGNITIVA_SITUADA_E1_01.json','contratos/HABITAT_EXTERNO_01.json','documentacion/GUIA_INTEGRACION_SITUADA_01.md']:
    p=SYSTEM/name;member='CODIGO_Y_RECALCULO/INCORPORADO/'+name;include(p,member,'existing_or_updated_dependency_contract');code_by_hash[sha(p)].append(member)
for name,expected in[('habitat.py','23c4248d18faa08f5d00b16fdcb5abeade7f327546d26c6b8668e6e60d3ef19e'),('social_habitat.py','150212491e4b012e2377ef7a6e89d4bd264277de1b0c24eb50567a2f5df9808b')]:
    p=ROOT/'laboratorio/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01'/name
    if sha(p)!=expected:raise ValueError('Reused helper revision changed; do not substitute it')
    member='CODIGO_Y_RECALCULO/DEPENDENCIAS_REUTILIZADAS/'+name;include(p,member,'exact_actually_reused_helper_not_a_new_historical_campaign');code_by_hash[sha(p)].append(member)
include(SYSTEM/'capacidades/observador_causal_retrospectivo_01.py','CODIGO_Y_RECALCULO/snapshot_reader.py','read_only_saved_byte_parser')
for p in sorted((LAB/'entrega_analisis').glob('*')):
    if p.is_file():include(p,p.name,'scientific_report_or_primary_derived_table')
manual=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_5_INTEGRACION_SITUADA_SIN_VALIDACION_VISUAL.docx';include(manual,'MANUAL/'+manual.name,'updated_actual_Word_structural_QA_only')
include(ROOT/'evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01/AUTOPSIA_ORIGEN_CONFIRMADA_R1.json','ANTECEDENTE_DIRIGIDO/AUTOPSIA_REFERENCIA78_MAS7.json','exact_relevant_HABITAT_primary_extraction_preexisting_no_repeat')

# A small selection of complete field/agenda witnesses, not every checkpoint.
selected=[('E1_INTEGRADO_MAIN',3639,None),('E1_INTEGRADO_MAIN',3899,None),('E1_INTEGRADO_COSTO_SOCIAL_01',5698,read(EV/'INTEGRATED_COST_SOCIAL_132.json')['final_record']['snapshot_sha256']),('IC01_INTEGRATED_OPPOSITE_133',5698,None),('IC01_COMMON_ACTION_INTEGRATED_COST_SOCIAL_132_D0_160',5765,None),('IC01_COMMON_ACTION_INTEGRATED_NULL_138_D0_160',5765,None),('IC01_COMMON_ACTION_INTEGRATED_RETURN_OMIT_137_D0_160',5765,None),('E1_INTEGRADO_CONTINUABLE_01',16485,None),('E1_INTEGRADO_RECUPERACION_01',17155,None),('IC01_GENERIC_RECOVERY_R2_PLUS_RECOVER_167',6100,None),('IC01_GENERIC_RECOVERY_R2_MINUS_RECOVER_167',6100,None),('IC01_STRESS_SEVERE_146',7440,None),('E1_INTEGRADO_COSTO_SOCIAL_01',7440,None)]
witness=[];included_cp=set()
for life,tick,expected in selected:
    candidates=list((SYSTEM/'estado/checkpoints').glob(life+'.T'+str(tick)+'.*'))
    if expected:candidates=[p for p in candidates if sha(p)==expected]
    elif len(candidates)>1:
        rec=next((r for r in lives if r['life_id']==life),None)
        if rec and rec['physical']['tick']==tick:candidates=[SYSTEM/rec['snapshot']]
    if len(candidates)!=1:raise ValueError('Ambiguous witness: '+life+' T'+str(tick))
    p=candidates[0];member='TESTIGOS_ESTADO/'+p.name;include(p,member,'selected_complete_world_witness_not_full_system');included_cp.add(p.resolve());witness.append({'member':member,'source':str(p),'sha256':sha(p),'tick':tick,'life':life})
for pattern in('AUTOPSY_MAIN_FIRST_LOSS_51_T364*.deetsnap.gz','STRESS_FIRST_STATE2_WITNESS_159_T638*.deetsnap.gz','STRESS_REPLAY_ALL_148_T636*.deetsnap.gz'):
    for p in sorted(EV.glob(pattern)):
        member='TESTIGOS_ESTADO/'+p.name;include(p,member,'decisive_pre_post_world_witness');included_cp.add(p.resolve());witness.append({'member':member,'source':str(p),'sha256':sha(p),'tick':int(p.name.split('_T')[-1].split('.')[0]),'life':'DIAGNOSTIC_NATIVE_INTERVAL','scope':'Mid-motor snapshots are not advertised as independently resumable external protocol states.'})
write(STAGE/'TESTIGOS_ESTADO/INDICE_TESTIGOS.json',{'witnesses':witness,'scope':'Selected full native worlds contain exact fields, clocks, queues and owner metadata. The ZIP lacks the official runtime and complete system install; witnesses are not an operational backup.'})
for p in sorted((SYSTEM/'estado/checkpoints').glob('*.deetsnap.gz')):
    if not p.name.startswith(('IC01_','E1_INTEGRADO_','E1_SITUADO_'))or p.resolve()in included_cp:continue
    omissions.append({'source':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'reason':'Full nonselected operational checkpoint kept locally, not needed for archived main-metric recalculation. Required for its own native continuation/replay.'})
for p in sorted(EV.glob('*.gz')):
    if p.resolve()not in included_cp:omissions.append({'source':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'reason':'Deep diagnostic state or trace retained locally; compact primaries of all trials are included.'})
coverage=[dict(r,member_matches=code_by_hash.get(r['sha256'],[]),status='EXACT_SOURCE_BYTES_INCLUDED'if r['sha256']in code_by_hash else'NO_MATCH_IN_SELECTED_SOURCE_BYTES_OR_EXPLICIT_EXTERNAL_DEPENDENCY')for r in code_refs]
write(STAGE/'CODIGO_Y_RECALCULO/COBERTURA_VERSIONES_EJECUTADAS.json',{'references':coverage,'missing':[r for r in coverage if not r['member_matches']],'scope':'No missing source revision is silently replaced by the latest code. Official engine/wheel bytes are intentionally omitted; hashes and installed identity are declared separately.'})
write(STAGE/'CODIGO_Y_RECALCULO/SINTAXIS_REVISIONES.json',{'sources':syntax,'scope':'Syntax only, not physical validation or a global capability verdict.'})
write(STAGE/'INDICE_FUENTES_Y_OMISIONES.json',{'schema':'IC01.compact.analysis.provenance.v1','included_original_sources':sources,'omitted_or_reduced':omissions,'source_bytes_included_before_ZIP':sum(r['original_bytes']for r in sources),'omitted_original_bytes':sum(r['bytes']for r in omissions),'excluded_by_contract':['official4.5wheel/PYD/kernel source','historical CPC ZIPs','all full deep-checkpoint collections','node_modules/bundled runtimes'],'not_a_historical_integral_archive':True,'no_loss_claim_for_excluded_history':False,'native_reproduction_requires':'Official4.5 and full compatible local DCS system/owner code plus referenced full starting snapshots; archived recalculation requires only included evidence and Python stdlib.'})
write(LAB/'PREPARACION_PAQUETE.json',{'stage':str(STAGE),'included_sources':len(sources),'witnesses':len(witness),'omissions':len(omissions),'code_references':len(coverage),'unmatched_code_references':sum(not r['member_matches']for r in coverage),'native_ticks':0})
print(json.dumps(read(LAB/'PREPARACION_PAQUETE.json')))
