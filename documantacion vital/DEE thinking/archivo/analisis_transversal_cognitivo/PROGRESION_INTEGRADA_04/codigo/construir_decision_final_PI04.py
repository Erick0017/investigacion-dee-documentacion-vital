"""Prepare a reasoned PI04 decision from ACTUAL closed gates; no Native.

Default PLAN creates nothing. --generar requires an explicitly reviewed Root
assessment, the actual final stable pair, fresh process evidence and actual
bounded storage accounting. This script never chooses a scientific verdict
from a score, runs a gate, imports the motor or performs adoption.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,os,runpy,sys
P4=Path(__file__).resolve().parents[1];R=P4.parents[2];C=R/'DEE Cognitive 2.0';S=C/'sistema';CS=P4/'estados/candidato_R02/sistema'
LIFE='ECI02_PI03_REPRO_PI04_MAIN_02';PARENT='ECI02_PI03_MAIN';PARENT_T=775355
ADAPTER=P4/'codigo/incorporar_PI04_REVISADO.py'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):p=Path(p);return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def evidence(descriptor):
    if not isinstance(descriptor,dict)or not{'path','sha256'}<=set(descriptor):raise ValueError('Exact evidence path/hash required')
    path=Path(descriptor['path']).resolve(strict=True)
    if not path.is_relative_to(P4.resolve())or sha(path)!=descriptor['sha256']:raise ValueError('Gate evidence is outside PI04 or changed')
    return descriptor
def approved_diff():
    seeds={'gestionar.py','app/pi04_cliente_acotado.py','app/lives.py','app/importacion_emparejada.py','app/estructuras_externas_pi03.py','app/servicio_persistente.py','app/mundo_genesis_apd05.py',
      'capacidades/pi04_dispatcher.py','capacidades/pi04_e3_contingencia.py','capacidades/pi04_coordinacion_adquirida.py','capacidades/pi04_coordinacion_simetrica_C2B.py','capacidades/pi04_coordinacion_central_C2C.py','capacidades/pi04_sensor_central_C2C_R01.py','capacidades/pi04_selector_contextual_C2_R01.py','capacidades/pi04_sensor_simetrico_C2B_R01.py','capacidades/pi04_diagnostico_campo.py','capacidades/pi04_diagnostico_C2C_pasivo.py','capacidades/e3_retorno_desacoplado_R01.py'}
    protocol=read(CS/'capacidades/PROTOCOLO_PI04_C2C_R01.json')
    seeds.update('capacidades/'+name for name in protocol['dependencies_sha256'])
    pending=list(seeds);used=set()
    while pending:
        name=pending.pop()
        if name in used:continue
        path=CS/name
        if not path.is_file():
            if name in seeds:raise FileNotFoundError('Actual used source missing:'+name)
            continue
        used.add(name);tree=ast.parse(path.read_text(encoding='utf-8-sig'))
        for n in ast.walk(tree):
            targets=[]
            if isinstance(n,ast.Import):targets.extend(x.name for x in n.names)
            elif isinstance(n,ast.ImportFrom):
                if n.level and name.startswith('app/'):
                    base='app'+('.'+n.module if n.module else'');targets.append(base)
                    if not n.module:targets.extend('app.'+x.name for x in n.names)
                elif n.module:
                    targets.append(n.module)
                    if n.module in('app','capacidades'):targets.extend(n.module+'.'+x.name for x in n.names)
            for module in targets:
                if module.startswith(('app.','capacidades.')):
                    relative=module.replace('.','/')+'.py'
                    if(CS/relative).is_file()and relative not in used:pending.append(relative)
    used.update('capacidades/'+n for n in('PROTOCOLO_PI03_R01.json','PROTOCOLO_PI03_TAREA_R02.json','PROTOCOLO_PI04_C2_R01.json','PROTOCOLO_PI04_C2B_R01.json','PROTOCOLO_PI04_C2C_R01.json'))
    changed=[]
    for name in sorted(used):
        source=CS/name;target=S/name
        if not source.is_file():raise FileNotFoundError(source)
        before=sha(target)if target.is_file()else None;after=sha(source)
        if before!=after:changed.append({'file':name,'sha256':after,'product_before_sha256':before})
    if not changed:raise ValueError('No actual changed implementation; this is not a repeated promotion')
    return changed,sorted(used)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--generar',action='store_true')
    ap.add_argument('--evaluacion-root',type=Path);ap.add_argument('--exportacion-final',type=Path)
    ap.add_argument('--procesos',type=Path);ap.add_argument('--almacenamiento',type=Path)
    ap.add_argument('--bytes-contabilizados',type=int);ap.add_argument('--salida',type=Path,default=P4/'control/DECISION_FINAL_PI04.json');args=ap.parse_args()
    if not args.generar:
        print(json.dumps({'mode':'PLAN_READONLY_NO_DECISION_NO_NATIVE','assessment_required_schema':'DEE.PI04.root_adoption_assessment.v1','required_assessment_fields':['approved_for_adoption:true','adapter_reviewed_for_PI04:true','reviewed_adapter_sha256','scope','gains','losses','uncertainties','assistance','regression_coverage','gates.functional_gain','gates.conservation','gates.source_reopening','gates.new_function_at_final_cut','evidence'],
          'other_required_arguments':['--exportacion-final actual stable_closed_full_pair proof','--procesos fresh no-live-affected-writer proof','--almacenamiento actual bounded accounting evidence','--bytes-contabilizados actual P4 plus NEW RP scope bytes'],
          'actual_parent_protected':{'life_id':PARENT,'tick':PARENT_T},'final_candidate_tick_not_fixed':True,'storage_limit_bytes':8000000000,'Native_ticks':0},ensure_ascii=False,indent=2));return
    if not all((args.evaluacion_root,args.exportacion_final,args.procesos,args.almacenamiento))or args.bytes_contabilizados is None:ap.error('--generar requires all actual Root assessment/export/process/storage arguments')
    if args.salida.exists():raise FileExistsError('Never overwrite an existing final decision')
    if not args.salida.absolute().resolve().is_relative_to((P4/'control').resolve()):raise ValueError('Decision output must stay inside PI04 control')
    assessment=read(args.evaluacion_root)
    if assessment.get('schema')!='DEE.PI04.root_adoption_assessment.v1'or assessment.get('approved_for_adoption')is not True or assessment.get('adapter_reviewed_for_PI04')is not True or assessment.get('reviewed_adapter_sha256')!=sha(ADAPTER):raise ValueError('Root has not explicitly approved/reviewed these actual adapter bytes; no decision produced')
    required=('scope','gains','losses','uncertainties','assistance','regression_coverage','gates','evidence')
    if any(k not in assessment for k in required):raise ValueError('Actual reasoned assessment is incomplete')
    for name in('functional_gain','conservation','source_reopening','new_function_at_final_cut'):
        gate=assessment['gates'].get(name,{})
        if gate.get('satisfied')is not True or not gate.get('criterion')or not gate.get('result')or not gate.get('evidence'):raise ValueError('Gate is not actually closed and satisfied:'+name)
        for item in gate['evidence']:evidence(item)
    for item in assessment['evidence']:evidence(item)
    card=read(CS/'estado/vidas'/LIFE/'VIDA.json');export=read(args.exportacion_final)
    if export.get('completed')is not True or export.get('life_id')!=LIFE or export.get('tick')!=card['physical']['tick']:raise ValueError('Export does not identify actual final current source cut')
    pair=Path(export['destination']).resolve(strict=True);manifest=read(pair/'EXPORTACION_SERVICIO.json')
    if card['physical']['N']!=67 or card['physical']['tick']<=PARENT_T:raise ValueError('Actual later N67 continuation required')
    changed,closure=approved_diff();desired={'N':67,'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256']}
    adapter=runpy.run_path(str(ADAPTER),run_name='pure_actual_PI04_adapter_checks')
    contract_file='contratos/PROGRESION_INTEGRADA_04.json';contract_path=S/contract_file
    contract={'schema':'DEE.Cognitive.PI04.contextual_coordination.contract.v1','id':'PI04_C2C_COORDINACION_CONTEXTUAL_ASISTIDA','status':'OPERATIVE_ONLY_WHEN_PUBLISHED_AFTER_COMMITTED_PROMOTION',
       'domain':'Native contextual choice of a prepared arithmetic capability, actual-number transfer into Native comparison and a fixed output-to-conduit action; bounded finite opportunities/resources.',
       'life_id':LIFE,'physical_source':card['physical'],'physical_parent':{'life_id':PARENT,'tick':PARENT_T},
       'scope':assessment['scope'],'gains':assessment['gains'],'assistance':assessment['assistance'],'limits':assessment['uncertainties'],'preserved_adverse_results':assessment['losses'],
       'observation':'Designed centralQ q+4 reader, original single datum and fixed q+6 IO hold. Observed material0 is distinct from NULL. Reader selection is prepared, not discovered by the individual.',
       'contingency_limit':'Real and phase-yoked histories must be reported separately; do not claim specific own-action contingency advantage, learned planning, initiative or general regulation from a score alone.',
       'commands':{'state':'motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py pi04-coordinacion-estado --vida '+LIFE+' --id ID_NUEVO',
          'one_consumable_opportunity':'motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py pi04-coordinacion-oportunidad --vida '+LIFE+' --id ID_NUEVO --material',
          'list_reproduction':'motor/python313/python.exe -I -B -X utf8 sistema/gestionar.py reproducibilidad listar',
          'known_acquisition_recipe':'pi04_c2c_adquisicion_20_R01'},
       'use_requirements':'The existing adopted owner is explicitly opened and paused, request IDs are fresh, all pending/uncertain work is reconciled, and finite declared stock remains. These clients never select a different life or create a world.',
       'evidence':assessment['evidence'],'regression_coverage':assessment['regression_coverage'],
       'reproduction_recipe':info(C/'reproducibilidad/recetas/pi04_c2c_adquisicion_20_R01.json'),
       'selected_full_pair':{'path_relative_to_product':pair.relative_to(C).as_posix(),'manifest_sha256':export['manifest_sha256']}}
    catalog_entry=dict(assessment.get('catalog_entry',{}));catalog_entry.setdefault('id','PI04_C2C_COORDINACION_CONTEXTUAL_ASISTIDA');catalog_entry.setdefault('title','PI04: coordinación contextual asistida con resultados Native reales');catalog_entry.setdefault('classification','LIFE_SPECIFIC_BOUNDED_ASSISTED_CAPABILITY');catalog_entry.setdefault('scope',assessment['scope']);catalog_entry.setdefault('knowledge_not_imputed_to_other_lives',True)
    minimum=sum(x['bytes']for x in manifest['members'])+2*(CS/card['snapshot']).stat().st_size+(CS/'estado/vidas'/LIFE/'HISTORIA.jsonl').stat().st_size+2*sum((CS/x['file']).stat().st_size for x in changed)+64*1024*1024
    if args.bytes_contabilizados<0 or args.bytes_contabilizados+minimum>8000000000:raise ValueError('Actual8GB scope plus conservative import would be exceeded; report it to Root, do not adjust the count or approve')
    accounting=read(args.almacenamiento)
    if accounting.get('accounted_bytes_before')!=args.bytes_contabilizados or not accounting.get('scope_roots')or not accounting.get('recorded_utc'):raise ValueError('Actual accounting evidence must contain the same accounted_bytes_before plus scope_roots/recorded_utc; do not reuse an old estimate')
    storage={'limit_bytes':8000000000,'accounted_bytes_before':args.bytes_contabilizados,'estimated_additional_bytes':minimum,'evidence':info(args.almacenamiento),'scope':'PI04 campaign plus its NEW stable RP pairs/code/evidence; old entire Cognitive/engine is not charged again. The supplied exact count is matched to actual bounded accounting evidence.'}
    decision={k:assessment[k]for k in required};decision.update(campaign='PROGRESION_INTEGRADA_04',approved_for_adoption=True,adapter_reviewed_for_PI04=True,reviewed_adapter_sha256=sha(ADAPTER),life_id=LIFE,decision_id=assessment.get('decision_id','PI04_ADOPCION_OPERATIVA_01'),desired_cut=desired,
       pair={'directory':str(pair),'manifest_sha256':export['manifest_sha256']},pair_relocation=info(args.exportacion_final),stable_pair_relative_to_product=pair.relative_to(C).as_posix(),approved_code_files=changed,
       new_contract={'file':contract_file,'product_before_sha256':sha(contract_path)if contract_path.is_file()else None,'document':contract},catalog_entry=catalog_entry,process_proof=str(args.procesos.resolve()),storage_budget=storage,
       source_before={'card':info(CS/'estado/vidas'/LIFE/'VIDA.json'),'snapshot':info(CS/card['snapshot']),'source_pair_manifest':info(pair/'EXPORTACION_SERVICIO.json')},
       Root_assessment=info(args.evaluacion_root),reviewed_source_closure=closure,created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),Native_ticks_by_decision_builder=0)
    # Reuse the actual reviewed adapter checks, never a second import/promoter.
    adapter['protect_parent']();adapter['require_unused_product_identity']();adapter['no_writers'](decision);adapter['frozen_engine']();parser=adapter['passive_parser']()
    source,_,_,_,_=adapter['source_state'](decision,parser);_,pair_proof=adapter['stable_pair'](decision)
    code=adapter['approved_code'](decision);adapter['check_json_plans'](decision);adapter['storage_gate'](decision,pair_proof,source,code)
    for descriptor in decision['source_before'].values():
        if sha(descriptor['path'])!=descriptor['sha256']:raise ValueError('Exact source card/snapshot/pair changed during decision validation')
    adapter['protect_parent']();adapter['approved_code'](decision)
    if any(name=='app'or name.startswith(('app.','dee_thinking'))for name in sys.modules):raise AssertionError('Decision builder imported Native/app')
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    with args.salida.open('x',encoding='utf-8')as f:json.dump(decision,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'decision':info(args.salida),'actual_source_cut':desired,'approved_changed_files':len(changed),'import_estimate_bytes':minimum,'storage_limit_bytes':8000000000,'Native_ticks':0,'adoption_performed':False},ensure_ascii=False))
if __name__=='__main__':main()
