"""Freeze R03 from the stopped, reached APD life; pure standard library, zero ticks.

Reuses literal payload validation from R02. Pair novelty excludes archived root
P01--P26 and ALL planned R01/R02 cases, not just favorable/finished examples.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,sqlite3
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def scan_pairs(value,found):
    if isinstance(value,dict):
        for key,child in value.items():
            if key in('operandos','raw_operands','valores','values')and isinstance(child,list)and len(child)==2 and all(type(x)is int for x in child):found.add(tuple(child))
            scan_pairs(child,found)
    elif isinstance(value,list):
        for child in value:scan_pairs(child,found)

def prepare(system,previous_config,evidence,interruption,out):
    out.mkdir(parents=True,exist_ok=False);base=json.loads(previous_config.read_bytes());witness=json.loads(interruption.read_bytes());record=json.loads((system/'estado/vidas/ASISTENTE_MAIN/VIDA.json').read_bytes())
    if witness['main']['snapshot_sha256']!=record['snapshot_sha256']or record['physical']['tick']!=257480:raise ValueError('Actual stopped R02 complete cut differs')
    queue_path=system/'estado/servicios_persistentes'/record['world_id']/'cola.sqlite3'
    with sqlite3.connect(queue_path.as_uri()+'?mode=ro&immutable=1',uri=True)as c:
        c.row_factory=sqlite3.Row;pending=[dict(r)for r in c.execute("SELECT * FROM requests WHERE status IN('queued','processing','uncertain') ORDER BY seq")]
        historical=[dict(r)for r in c.execute('SELECT id,payload,status FROM requests')]
    if len(pending)!=8 or any(r['status']!='queued'for r in pending):raise ValueError('Preserve exactly eight queued rows')
    begin=[r for r in pending if r['id']=='apd61_00223']
    if len(begin)!=1 or json.loads(begin[0]['payload'])['situaciones'][0]['modo']!='cadena-iniciar':raise ValueError('Original inherited BEGIN differs')
    finish_ids=[r['id']for r in historical if any(q.get('modo')=='cadena-finalizar'for q in json.loads(r['payload']).get('situaciones',[]))and r['id'].startswith('apd61_')]
    if finish_ids:raise ValueError('A FINISH was already admitted in R02; inspect before prospective action')
    exclusion_files=sorted(evidence.glob('P*.json.gz'))+[previous_config,evidence/'servicio/RESERVA_CONGELADA_R01/CONFIG_READY.json']
    exclusion=set();index=[]
    for path in exclusion_files:
        if not path.is_file():raise FileNotFoundError(path)
        value=json.loads(gzip.decompress(path.read_bytes()))if path.suffix=='.gz'else json.loads(path.read_bytes());scan_pairs(value,exclusion);index.append({'file':str(path),'bytes':path.stat().st_size,'sha256':sha(path)})
    selected=[]
    for a in range(17,33):
        for b in range(1,17):
            if(a,b)not in exclusion:selected.append([a,b])
            if len(selected)==8:break
        if len(selected)==8:break
    if len(selected)!=8:raise ValueError('Eight literally new pairs unavailable under fixed enumeration')
    novelty={'selection_rule':'Lexicographic (a,b), a17..32, b1..16; first eight pairs absent from recursive operandos/raw_operands/valores/values pairs in indexed complete primaries/configs. No output, correctness or useful-route is inspected for selection.','sources':index,'excluded_pairs':sorted(exclusion),'selected_pairs':selected,'old_public_compositions_not_claimed_new':True,'new_native_ticks':0}
    dump(out/'RESERVA_PARES_NUEVOS.json',novelty)
    source=base['source_sha256'];expected_patch={'app/access_guard.py':'6e9e159a9623ec0ecbc71bd00223b33f94cf4ec66455d4df92f5fe216fbaa682','app/servicio_persistente.py':'7f68f9f2726f8063d46aa0a5d21b3f05c887a795db0dff3777d0280a6626d25d','gestionar.py':'c69786e1b0d37087ac32f0d82e455e3cb5184b19c8c0ca99562fa6c76c32bdcc'}
    for name,old in list(source.items()):
        actual=sha(system/name)
        if actual!=expected_patch.get(name,old):raise ValueError('Source beyond approved metadata patch changed: '+name)
        source[name]=actual
    config=copy.deepcopy(base);config.update(request_prefix='apd62_',seconds=4500,nominal_events=120,source_sha256=source,initial_cut={'life_id':'ASISTENTE_MAIN','tick':257480,'N':67,'snapshot_sha256':record['snapshot_sha256']},inherited_pending_rows=pending,pending_contract='REAL_FIFO_AND_OPERATIONAL_STATE_WITHOUT_REQUIRED_CASCADE')
    config['continuation_note']='Same reached ASISTENTE_MAIN after two preserved technical negative trajectories. Eight original R02 queued rows execute once, and a declared one-time FINISH is submitted only if the already-admitted BEGIN forms an actual chain. R01/R02 time is not credited. No reinitialization, snapshot restoration, reader repair or favorable-action selection.'
    config['prior_interrupted_reserves']=[{'file':str(interruption),'sha256':sha(interruption),'minutes_credited_to_R03':0}]
    config['novel_pair_selection']={'file':'RESERVA_PARES_NUEVOS.json','sha256':sha(out/'RESERVA_PARES_NUEVOS.json'),'selected_pairs':selected}
    config['fixed_events']=[v for v in config['fixed_events']if v['purpose']not in('actual_MUFI_pending_BEGIN_operator_context_P0','actual_MUFI_pending_FINISH_after_process_reload')]
    # Public curriculum stays semantically fixed; new operands are used in the
    # second and third regimes, independent of whether DEE responds correctly.
    config['families']['new_pairs_old_apd']=[{'operacion':'sesion','retorno':'real','situaciones':[{'modo':'apd','texto':('suma','diferencia','agrega','resta')[i%4],'operandos':pair}]}for i,pair in enumerate(selected)]
    config['curriculum_switches']=[{'at_seconds':1300,'family_cycle':[('new_pairs_old_apd'if f=='old_apd'else f)for f in config['family_cycle']]},{'at_seconds':2010,'family_cycle':[('new_pairs_old_apd'if f=='old_apd'else f)for f in base['curriculum_switches'][0]['family_cycle']]}]
    module_path=Path(__file__).with_name('preparar_reserva_apd_r02.py');spec=importlib.util.spec_from_file_location('r03_literal_validation',module_path);validation=importlib.util.module_from_spec(spec);spec.loader.exec_module(validation)
    events=[];usage={k:0 for k in config['families']}
    # 120 opportunities over4200seconds: mean35s, fixed two-client labels.
    # Replacements below retain120, preserving all non-replaced opportunities.
    for i in range(120):
        when=300+33*i;cycle=config['family_cycle']
        for switch in config['curriculum_switches']:
            if when>=switch['at_seconds']:cycle=switch['family_cycle']
        family=cycle[i%len(cycle)];templates=config['families'][family];payload=templates[usage[family]%len(templates)];usage[family]+=1
        events.append({'id':'apd62_'+str(i).zfill(5),'at_seconds':float(when),'regime':1 if when<1300 else(2 if when<2600 else 3),'client':i%2,'audit_family_not_actor_input':family,'payload':validation.payload(payload,config['admitted_modes'])})
    occupied=set()
    for fixed in config['fixed_events']:
        chosen=min((e for e in events if e['id']not in occupied),key=lambda e:(abs(e['at_seconds']-fixed['at_seconds']),e['id']));occupied.add(chosen['id']);chosen.update(at_seconds=float(fixed['at_seconds']),audit_family_not_actor_input=fixed['purpose'],payload=validation.payload(fixed['payload'],config['admitted_modes']))
    events.sort(key=lambda e:(e['at_seconds'],e['id']))
    for event in events:
        for row in event['payload']['situaciones']:
            forms=[row['texto']]if row['modo']=='apd'else row.get('formas',[])if row['modo']=='apd-componer'else[]
            if any(event['at_seconds']<config['new_forms_reserved_until'].get(form,0)for form in forms):raise ValueError('New-word use precedes fixed lesson boundary')
    dump(out/'CONFIG_READY.json',config)
    harness=Path(__file__).with_name('ensayo_servicio_apd_r03.py');helper=Path(__file__).with_name('ensayo_servicio_apd_r02.py')
    protocol={'schema':'DEE.APD01.prospective_service_curriculum.v2','status':'FROZEN_FOR_ONE_SELECTED_CANDIDATE','life_id':'ASISTENTE_MAIN','backend':'mente_unificada','request_prefix':'apd62_','seconds':4500,'nominal_events':120,'events':events,'regimes':[{'id':r,'planned_events':sum(e['regime']==r for e in events)}for r in(1,2,3)],'initial_cut':config['initial_cut'],'source_sha256':source,'source_contract':config['source_contract'],'inherited_pending_rows':pending,'continuation_scope':config['continuation_note'],'pending_contract':config['pending_contract'],'requires_existing_paired_queue':True,'inherited_completion_deadline_seconds':600,'inherited_finish':{'id':'apd62_inherited_finish','client':'declared_operator_continuation','payload':{'operacion':'sesion','retorno':'omit','situaciones':[{'modo':'cadena-finalizar'}]},'begin_id':'apd61_00223','prior_finish_ids':finish_ids,'wait_seconds':300},'technical_pause_windows':[600,1800,3000],'technical_control_wait_seconds':300,'idle_interval_seconds':.1,'idle_quantum_ticks':1,'save_seconds':60,'maximum_drain_seconds':300,'maximum_closure_seconds':900,'owner_startup_allowance_seconds':90,'burst_at_first_pause':14,'burst_material_capacity':8,'burst_payload':config['burst_payload'],'pending_transport_payload':config['pending_transport_payload'],'invalid_tests_at_seconds':300,'invalid_payloads':[{'operacion':'sesion','situaciones':[]},{'operacion':'sesion','situaciones':[{'modo':'apd','texto':'suma','operandos':[1,2],'target':3}]},{'operacion':'guardar','shell':'never_execute'},{'operacion':'sesion','situaciones':[{'modo':'apd','texto':'FORMA_FUERA_DEL_DOMINIO','operandos':[1,2]}]}],'maximum_process_RAM_bytes':536870912,'minimum_free_disk_bytes':2147483648,'budget_deadline_utc':config['budget_deadline_utc'],'configuration_sha256':hashlib.sha256(validation.canonical(config).encode('utf8')).hexdigest(),'configuration_file_sha256':sha(out/'CONFIG_READY.json'),'passive_helper_sha256':sha(helper),'harness_sha256':sha(harness),'novel_pair_selection':config['novel_pair_selection'],'new_native_ticks':0,'assistance':config['assistance'],'measurement':'All exact pause/reload spans discounted; any unplanned pause aborts. FIFO acceptance, native inputs, emitted operator/history, numerical correctness, artifacts and modeled utility remain separate. Pending transport is not native cascade; source3descriptor updates change metadata only.'}
    dump(out/'PROTOCOLO.json',protocol)
    for file in(harness,helper,Path(__file__),module_path):shutil_copy=file.read_bytes();(out/file.name).write_bytes(shutil_copy)
    return {'config':str(out/'CONFIG_READY.json'),'config_sha256':sha(out/'CONFIG_READY.json'),'protocol':str(out/'PROTOCOLO.json'),'protocol_sha256':sha(out/'PROTOCOLO.json'),'harness_sha256':sha(harness),'selected_new_pairs':selected,'native_ticks':0}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sistema',type=Path,required=True);parser.add_argument('--configuracion-previa',type=Path,required=True);parser.add_argument('--evidencia',type=Path,required=True);parser.add_argument('--interrupcion',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True);a=parser.parse_args();print(json.dumps(prepare(a.sistema,a.configuracion_previa,a.evidencia,a.interrupcion,a.salida),ensure_ascii=False))
