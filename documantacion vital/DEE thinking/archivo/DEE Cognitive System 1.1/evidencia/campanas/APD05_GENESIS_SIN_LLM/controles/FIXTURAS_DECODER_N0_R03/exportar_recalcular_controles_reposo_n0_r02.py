"""Seven actual APD05 control cuts, including timing and interrupted negatives.

Read-only scientific export. No motor, world or tick API. Exact snapshots remain
local; exported arrays do not replace complete transport or an uncertain future.
"""
from pathlib import Path
from array import array
from collections import Counter
from datetime import datetime,timezone
import argparse,gzip,hashlib,importlib.util,json,shutil,sqlite3,sys,zlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SYSTEM=ROOT/'sistema'
EV=ROOT/'evidencia/campanas/APD05_GENESIS_SIN_LLM/controles'
OUT=EV/'REPOSO_Y_ACCESO_PORTABLE_N0_R02'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def data(p):
    value=Path(p).read_bytes();return gzip.decompress(value)if value[:2]==b'\x1f\x8b'else value
def obj(p):return json.loads(data(p))
def lines(p):return [json.loads(x)for x in data(p).splitlines()if x.strip()]


FIXED_FORM_CODEC={
 'alfa':((33,33,33),(1,0,0)),'beta':((33,33,33),(0,1,0)),
 'gamma':((33,33,33),(1,1,0)),'delta':((33,33,33),(-1,1,0)),
 'epsilon':((33,33,33),(1,-1,0)),'zeta':((33,33,33),(-1,-1,0)),
 'suma':((33,33,33),(-1,0,0)),'diferencia':((33,33,33),(0,-1,0)),
 'agrega':((47,47,47),(-1,0,0)),'resta':((47,47,47),(0,-1,0)),
 'total':((47,47,47),(1,0,0)),'quita':((47,47,47),(0,1,0)),
 'compara':((47,17,47),(1,0,0)),'recuerda':((47,17,47),(0,1,0)),
 'luma':((47,7,47),(-1,0,0)),'nara':((47,7,47),(0,-1,0)),
 'clasifica':((47,7,47),(1,0,0)),'equilibra':((47,7,47),(1,1,0))}


def strict_summary(decoder,value):
    result=decoder.summarize(value)
    expected={tuple((o[i]+4*v[i]+(sign if i==2 else 0))%67 for i in range(3)):sign
              for o,v in FIXED_FORM_CODEC.values()for sign in(-1,1)}
    nodes={(node['form'],node.get('read_tick')):node
           for _,node in decoder.walk(value)if isinstance(node,dict)and'form'in node
           and isinstance(node.get('reader'),dict)and'panel'in node['reader']}
    for word in result['words']:
        node=nodes[(word['form'],word['read_tick'])];panel=node['reader']['panel']
        if len(panel)!=36 or {tuple(x['site'])for x in panel}!=set(expected):
            raise ValueError('Fixed lexical36 coordinate domain differs')
        candidates=[]
        for obs in panel:
            f=decoder.fields(obs);sign=expected[tuple(obs['site'])]
            if f['state']>0 and f['semantic']==1 and f['direction']==[0,0,sign]:candidates.append(sign)
        previous=word['RAW_sign'];previous_count=word['candidate_count']
        word['RAW_sign']=candidates[0]if len(candidates)==1 else None;word['candidate_count']=len(candidates)
        word['prior_direction_only_auditor_sign']=previous
        word['prior_direction_only_auditor_candidate_count']=previous_count
        word['corrected_positional_recalculation_differs']=previous!=word['RAW_sign']or previous_count!=len(candidates)
        word['matches_native_fixed_reader']=word['RAW_sign']==word['reported']
        word['geometry']='36 fixed signed gates, sign-specific position AND direction; no favourable gate selected by token or expected sign.'
        inputs=decoder.summarize(node)['native_receipts']
        cues=[r for r in inputs if 'APD04.LEX.R02.cue.'+word['form'] in r['channels']]
        word['cue_status']=cues[0]['status']if len(cues)==1 else None
        word['cue_admitted']=word['cue_status']=='applied'
        word['requested_material_inputs']=len(inputs)
        word['material_statuses']=dict(Counter(r['status']for r in inputs))
        word['all_requested_material_inputs_applied']=bool(inputs)and all(r['status']=='applied'for r in inputs)
    numeric_nodes={(node['kind'],node['native_trial']['read_tick']):node
                   for _,node in decoder.walk(value)if isinstance(node,dict)
                   and node.get('kind')in('APD04_candidate_scalar_classification','APD04_candidate_native_balance')}
    for number in result['numbers']:
        node=numeric_nodes[(number['kind'],number['read_tick'])];inputs=decoder.summarize(node)['native_receipts']
        number['requested_material_inputs']=len(inputs)
        number['material_statuses']=dict(Counter(r['status']for r in inputs))
        number['all_requested_material_inputs_applied']=bool(inputs)and all(r['status']=='applied'for r in inputs)
        number['matches_native_fixed_reader']=number['RAW_sign']==number['reported']
    return result


def fixtures(decoder):
    points=[[(o[i]+4*v[i]+(sign if i==2 else 0))%67 for i in range(3)]
            for o,v in FIXED_FORM_CODEC.values()for sign in(-1,1)]
    definitions=[('empty_NULL',[],None,0),
                 ('negative_signal_on_positive_gate_is_NOT_an_emission',[(1,-1)],None,0),
                 ('positive_signal_on_positive_gate',[(1,1)],1,1),
                 ('opposite_coherent_pair_is_ambiguous',[(0,-1),(1,1)],None,2)]
    result=[]
    for label,entries,expected,count in definitions:
        panel=[{'site':site,'raw':'0'}for site in points]
        for position,sign in entries:panel[position]['raw']=str((1<<60)+((sign&15)<<56)+1)
        fake={'form':'alfa','read_tick':1,'reader':{'panel':panel,'formed_native_command':expected}}
        actual=strict_summary(decoder,fake)['words'][0]
        if actual['RAW_sign']!=expected or actual['candidate_count']!=count:raise ValueError('Synthetic positional decoder fixture failed')
        result.append({'label':label,'actual':actual,'expected_candidates':count})
    return {'scope':'SYNTHETIC_CODE_FIXTURES_NOT_NATIVE_EXPERIENCES','Native_ticks':0,'cases':result}


def recalc(bundle):
    index=read(bundle/'INDICE.json');issues=[];verified=0
    for row in index['members']:
        path=bundle/row['file']
        if path.stat().st_size!=row['bytes']or sha(path)!=row['sha256']:raise ValueError('Portable member changed: '+row['file'])
        if row.get('original_sha256')and hashlib.sha256(data(path)).hexdigest()!=row['original_sha256']:
            raise ValueError('Original source bytes differ')
        verified+=1
    decoder=load('APD05_controls_frozen_pure_RAW_decoders',bundle/'CODIGO/ejecutar_reposo_y_acceso_r04.py')
    schema_tool=load('APD05_transport_structural_N0',bundle/'CODIGO/comparar_esquema_transporte_n0_r01.py')
    schema_check=schema_tool.compare(bundle/'CODIGO/FUENTES_R03/app/cola_local.py',bundle/'CODIGO/FUENTES_R04/app/cola_local.py')
    schema_reference=obj(bundle/index['transport_AST_witness'])
    for key in('old_decoded_sha256','new_sha256','old_complete_module_AST_equals_new_without_added_branch'):
        if schema_check[key]!=schema_reference[key]:raise ValueError('Transport structural witness does not reproduce')
    p=read(bundle/'CODIGO/PROTOCOLO_REPOSO_Y_ACCESO_R04.json');expected=p['frozen_evaluation']['lexical_expected_RAW_signs'];cases=[];matched_intervals={}
    for case in index['cases']:
        life=case['life'];sessions=lines(bundle/case['sessions']);observations=lines(bundle/case['observations'])
        recorded_sources=obj(bundle/case['source_identity'])['source_hashes'];source_checks=[]
        for name,expected_source in recorded_sources.items():
            name=name.replace('\\','/')
            source=bundle/'CODIGO'/('FUENTES_R03'if case['revision']=='R03'and name=='app/cola_local.py'else'FUENTES_R04')/name
            if not source.is_file()or sha(source)!=expected_source:raise ValueError('Executed Source bytes not preserved: '+life+' '+name)
            source_checks.append({'file':source.relative_to(bundle).as_posix(),'sha256':expected_source})
        panel=[x for x in sessions if x['label'].startswith('common_panel_')]
        all_new=strict_summary(decoder,sessions);post=strict_summary(decoder,panel)
        delta=obj(bundle/case['native_receipt_delta']);journal=obj(bundle/case['transport_witness'])
        native={r['id']:r for r in delta['new_committed_receipts']};from_rows={r['id']:r for r in all_new['native_receipts']}
        if set(native)!=set(from_rows):issues.append(life+': new committed Native IDs and exported request receipts differ')
        for identifier,r in from_rows.items():
            real=native.get(identifier)
            if real is None:continue
            for key in ('requested_tick','effective_tick','channels'):
                if r[key]!=real[key]:issues.append(life+': receipt field differs '+str(identifier)+' '+key)
            enum={'applied':2,'rejected_occupied':5}.get(r['status'])
            if enum is not None and enum!=real['status']:issues.append(life+': receipt terminal status differs '+str(identifier))
        for word in post['words']:
            word['expected']=expected[word['form']];word['correct']=word['RAW_sign']==word['expected']
            if not word['matches_native_fixed_reader']:issues.append(life+': exact positional RAW and native fixed lexical reader disagree')
        for i,number in enumerate(post['numbers']):
            number['expected']=p['frozen_evaluation']['numeric_expected_RAW_signs'][i]
            number['correct']=number['RAW_sign']==number['expected']
            if not number['matches_native_fixed_reader']:issues.append(life+': exact positional RAW and native fixed numeric reader disagree')
        if case['status']=='CLOSED_RESULT'and(len(post['words'])!=6 or len(post['numbers'])!=2):
            issues.append(life+': completed case lacks its fixed6+2 panel')
        if case['status']=='CLOSED_RESULT':
            saved=obj(bundle/case['terminal'])
            old_numeric=[{k:v for k,v in row.items()if k in saved['panel_summary']['numbers'][i]}for i,row in enumerate(post['numbers'])]
            if saved['panel_summary']['numbers']!=old_numeric:
                issues.append(life+': saved and freshly RAW-decoded numeric panel differ')
        interval=[x for x in observations if x['label']=='interval_end_before_material_panel']
        dense=[x for x in observations if x['physical']['occupied']>1000]
        fields=[];field_arrays=[]
        for row in case['field_exports']:
            blob=(bundle/row['file']).read_bytes()
            if hashlib.sha256(blob).hexdigest()!=row['sha256']:raise ValueError('Field archive differs')
            exact=zlib.decompress(blob);count=row['N']**3
            if len(exact)!=count*16:raise ValueError('Field dimensions differ')
            if hashlib.sha256(exact[:count*8]).hexdigest()!=row['RAW_sha256']or hashlib.sha256(exact[count*8:]).hexdigest()!=row['clocks_sha256']:
                raise ValueError('Exact RAW or clock integers differ')
            raw=array('Q');raw.frombytes(exact[:count*8])
            if sys.byteorder!='little':raw.byteswap()
            clocks=array('Q');clocks.frombytes(exact[count*8:])
            if sys.byteorder!='little':clocks.byteswap()
            occupied=sum(bool(x&0xffffffff)for x in raw)
            if occupied!=row['occupied']:raise ValueError('Global occupancy differs from exact field')
            fields.append({'role':row['role'],'tick':row['tick'],'occupied':occupied,
                           'RAW_sha256':row['RAW_sha256'],'clocks_sha256':row['clocks_sha256']})
            field_arrays.append((row,raw,clocks))
            if row['role']=='interval_endpoint':matched_intervals[life]=(row,raw,clocks)
        transitions=[]
        for (a,ra,ca),(b,rb,cb)in zip(field_arrays,field_arrays[1:]):
            transitions.append({'from_role':a['role'],'to_role':b['role'],'ticks':[a['tick'],b['tick']],
                                'RAW_different_sites':sum(x!=y for x,y in zip(ra,rb)),
                                'clock_different_sites':sum(x!=y for x,y in zip(ca,cb)),
                                'scope':'Exact global partial physical arrays, not equality of the complete causal/operational state or proof of functional information loss.'})
        timing=[]
        for entry in sessions:
            if not entry['label'].startswith('ordinary_work_'):continue
            if 'result'not in entry:
                timing.append({'label':entry['label'],'status':'NO_COMMITTED_REQUEST_RESULT','scope':'No physical choice or precise duration inferred from an unfinished transport result.'});continue
            owner=entry['result'];body=owner['result']['rows'][0]['rows'][0];selection=body['selection']
            k=(owner['before_tick']+1410+5+390)//391;k=k if k%2 else k+1
            predicted_boundary=k*391;predicted_query=predicted_boundary-1410
            timing.append({'label':entry['label'],'before_tick':owner['before_tick'],
                           'query_tick':selection['query_tick'],'boundary':selection['boundary'],'after_tick':owner['after_tick'],
                           'predicted_P0_query_tick':predicted_query,'predicted_P0_boundary':predicted_boundary,
                           'predicted_P0_endpoint':predicted_boundary+15,
                           'matches_P0_clock_calendar':selection['query_tick']==predicted_query and selection['boundary']==predicted_boundary and owner['after_tick']==predicted_boundary+15,
                           'scope':'Prepared phase calendar with DELAY1410 and odd multiples of391; not learned initiative, a claim of thought duration, or a kernel modification.'})
        all_new.pop('native_receipts');post.pop('native_receipts')
        imported=obj(bundle/case['imported']);end_tick=None if not interval else interval[0]['physical']['tick']
        row={'life':life,'status':case['status'],'parent':case['parent'],'revision':case['revision'],
             'scope':case['scope'],'initial_tick':imported['physical']['tick'],
             'verified_recorded_source_files':source_checks,
             'interval_end':None if not interval else interval[0]['physical'],
             'new_interval_ticks_actual':None if end_tick is None else end_tick-imported['physical']['tick'],
             'ancestral_origin_tick':case['ancestral_origin_tick'],
             'comparison_age_ticks':None if end_tick is None else end_tick-case['ancestral_origin_tick'],
             'new_task_opportunities_scheduled':case['new_tasks_scheduled'],
             'new_task_opportunities_committed':sum(x['label'].startswith('ordinary_work_')and'result'in x for x in sessions),
             'ordinary_task_P0_phase_timing':timing,
             'historical_tasks_at_import':case['historical_tasks_at_import'],
             'common_panel_transport_planned':7,'common_panel_transport_committed':len(panel),
             'common_panel_native_questions_planned':8,'common_panel_questions_observed':len(post['words'])+len(post['numbers']),
             'common_panel_formed':None if not panel else sum(x['candidate_count']==1 for x in post['words']+post['numbers']),
             'common_panel_correct':None if not panel else sum(x['correct']for x in post['words']+post['numbers']),
             'common_panel_correct_with_all_inputs_applied_conservative':None if not panel else sum(x['correct']and x['all_requested_material_inputs_applied']for x in post['words']+post['numbers']),
             'common_panel_native_requested_inputs':None if not panel else post['native_receipts_unique'],
             'common_panel_native_input_status_counts':None if not panel else post['native_receipt_statuses'],
             'common_panel_questions_with_all_inputs_applied':None if not panel else sum(x['all_requested_material_inputs_applied']for x in post['words']+post['numbers']),
             'words':post['words'],'numbers':post['numbers'],
             'new_committed_Native_IDs':len(native),'new_committed_status_counts_enum':dict(Counter(str(r['status'])for r in native.values())),
             'in_flight_Native_future_complete':case['status']!='PRESERVED_UNCOMMITTED_FUTURE',
             'uncommitted_Native_input_counts':None if case['status']=='PRESERVED_UNCOMMITTED_FUTURE'else 0,
             'all_completed_requests_recalculated':all_new,
             'first_observed_occupied_over_1000':None if not dense else {'tick':dense[0]['physical']['tick'],'label':dense[0]['label'],'occupied':dense[0]['physical']['occupied']},
             'field_endpoints':fields,'field_transitions':transitions,'transport_witness':journal,'complete_pair':case['complete_pair'],
             'supervision':None if not case.get('supervision')else obj(bundle/case['supervision']),
             'logical_IO_measurement':None,'logical_IO_scope':'This controls supervisor recorded whole-tree CPU/RAM and wall time, not validated Job I/O counters; sizes of exported files are not substituted for logical I/O.',
             'energy':'NO_MEDIDA'}
        cases.append(row)
    matched=[x for x in cases if x['life']in('APD05_CTL_PREV_REST_R03','APD05_CTL_PREV_OMIT_CONT_R04','APD05_CTL_PREV_ORD_REAL_R04')]
    if len(matched)!=3:issues.append('Missing one declared healthy-history comparison')
    comparisons=[]
    for life_a,life_b in (('APD05_CTL_PREV_REST_R03','APD05_CTL_PREV_OMIT_CONT_R04'),
                          ('APD05_CTL_PREV_REST_R03','APD05_CTL_PREV_ORD_REAL_R04'),
                          ('APD05_CTL_PREV_OMIT_CONT_R04','APD05_CTL_PREV_ORD_REAL_R04'),
                          ('APD05_CTL_REC_REST_R04','APD05_CTL_REC_ORD_REAL_R04')):
        if life_a not in matched_intervals or life_b not in matched_intervals:continue
        a,ra,ca=matched_intervals[life_a];b,rb,cb=matched_intervals[life_b]
        if a['N']!=b['N']or a['tick']!=b['tick']:raise ValueError('Declared matched intervals differ in dimension or age')
        comparisons.append({'life_a':life_a,'life_b':life_b,'N':a['N'],'common_tick':a['tick'],
                            'RAW_different_sites':sum(x!=y for x,y in zip(ra,rb)),
                            'clock_different_sites':sum(x!=y for x,y in zip(ca,cb)),
                            'scope':'Same-age exact global RAW/clocks contrast. Life metadata are intentionally distinct; this is not complete-state convergence, independent replication, or a functional memory decoder.'})
    return {'schema':'APD05.rest_access.all_actual_cuts.N0.R02','Native_ticks':0,'verified_files':verified,
            'cases':cases,'same_age_partial_physical_comparisons':comparisons,'issues':issues,
            'transport_schema_comparison':{k:v for k,v in schema_check.items()if k not in('old_source','new_source')},
            'matching':'REST_R03 at8192 is reused. OMIT_R04 inherits exactly the three already executed OMIT_R03 tasks, then advances1955 more ticks; REAL_R04 has exactly three new tasks at the same scheduled Native offsets. Prefix and descendant are not independent samples or merged memories.',
            'coverage':'Global fields are measured at fixed age-fill boundaries and after whole protocols. Local frames inside tasks cover declared reader/reference regions, not every encounter or the exact first global growth tick.',
            'limits':'An unexecuted panel has correct=null, not0. Failed timing is an instrument/protocol limit. Uncertain REAL_R03 has a last committed state, not a known final physical state. Occupancy is not memory, death or energy. Exact RAW/clocks are not complete operational snapshots.'}


def export():
    if OUT.exists():raise FileExistsError('Never overwrite an evidence revision')
    OUT.mkdir();(OUT/'CODIGO').mkdir();(OUT/'PRIMARIOS').mkdir();(OUT/'CAMPOS').mkdir()
    protocols={rev:read(HERE/('PROTOCOLO_REPOSO_Y_ACCESO_'+rev+'.json'))for rev in('R03','R04')}
    for name in ('ejecutar_reposo_y_acceso_r01.py','ejecutar_reposo_y_acceso_r02.py','ejecutar_reposo_y_acceso_r03.py','ejecutar_reposo_y_acceso_r04.py','comparar_esquema_transporte_n0_r01.py','PROTOCOLO_REPOSO_Y_ACCESO_R01.json','PROTOCOLO_REPOSO_Y_ACCESO_R02.json','PROTOCOLO_REPOSO_Y_ACCESO_R03.json','PROTOCOLO_REPOSO_Y_ACCESO_R04.json'):
        shutil.copy2(HERE/name,OUT/'CODIGO'/name)
    shutil.copy2(__file__,OUT/'CODIGO'/Path(__file__).name)
    observer_path=SYSTEM/'capacidades/observador_causal_retrospectivo_01.py';observer=load('offline_native_snapshot_parser_APD05_controls',observer_path)
    shutil.copy2(observer_path,OUT/'CODIGO'/observer_path.name)
    lexical_path=SYSTEM/'capacidades/lexico_compartido_apd04.py'
    lexical=load('existing_frozen_common36_geometry_N0',lexical_path)
    if lexical.FORM_CODEC!=FIXED_FORM_CODEC:raise ValueError('Copied fixed36 geometry differs from actual existing reader source')
    shutil.copy2(lexical_path,OUT/'CODIGO'/lexical_path.name)
    for name in ('sensor_balanceado_apd04.py','ruta_adaptativa_apd02_04.py','sensor_balanceado_apd03_r02.py','selector_acrecion_nativo.py','mente_unificada_01.py'):
        source=SYSTEM/'capacidades'/name;target=OUT/'CODIGO/FUENTES_COMUNES/capacidades'/name
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    configs=[('R03','APD05_CTL_PREV_REST_R03'),('R03','APD05_CTL_PREV_ORD_OMIT_R03'),('R03','APD05_CTL_PREV_ORD_REAL_R03')]
    configs += [('R04',x['life'])for x in protocols['R04']['prevention_arms']+protocols['R04']['recovery_arms']]
    members=[];cases=[];cache={};array_members={}
    def add(source,name):
        target=OUT/'PRIMARIOS'/(name+'.gz');target.write_bytes(gzip.compress(source.read_bytes(),mtime=0))
        members.append({'file':target.relative_to(OUT).as_posix(),'bytes':target.stat().st_size,'sha256':sha(target),
                        'original':str(source),'original_sha256':sha(source),'encoding':'gzip_exact_bytes'})
        return target.relative_to(OUT).as_posix()
    def snap(path,keep=False):
        key=str(path.resolve())
        if key in cache:return cache[key]
        value=observer.Snapshot(path)
        if keep:cache[key]=value
        return value
    def field(s,role):
        raw=observer.pbytes(s.raw);clock=observer.pbytes(s.clocks);decoded=raw+clock;key=hashlib.sha256(decoded).hexdigest()
        target=OUT/'CAMPOS'/(key+'.zlib')
        if key not in array_members:target.write_bytes(zlib.compress(decoded,9));array_members[key]=target
        return {'file':target.relative_to(OUT).as_posix(),'sha256':sha(target),'role':role,'N':s.N,'tick':s.tick,
                'occupied':sum(bool(x&0xffffffff)for x in s.raw),'RAW_sha256':hashlib.sha256(raw).hexdigest(),'clocks_sha256':hashlib.sha256(clock).hexdigest(),
                'source_full_snapshot':str(s.path),'source_full_snapshot_sha256':s.encoded_sha256,
                'scope':'Exact partial physical arrays; agenda, interfaces, transport and metadata remain at the full local state.'}
    for revision,life in configs:
        p=protocols[revision];branch=next(x for x in p['prevention_arms']+p['recovery_arms']if x['life']==life)
        parent=p['parents'][branch.get('parent_key','adverse'if'_REC_'in life else'functional')]
        native=SYSTEM/'estado/observatorios'/('APD05_CONTROLES_'+revision)/life
        control=EV/('REPOSO_Y_ACCESO_'+revision)/life
        success=native/'RESULTADO.json';failure=native/'FALLO_PRESERVADO.json';marker=SYSTEM/'estado/vidas'/life/'FUTURO_INTERRUMPIDO.json'
        terminal=success if success.is_file()else(failure if failure.is_file()else marker)
        if not terminal.is_file():raise ValueError('Actual case has not closed or preserved an explicit uncertain future: '+life)
        if success.is_file():status='CLOSED_RESULT';closed=read(success);full=closed['complete_pair'];scope='Complete actual physical trajectory and fixed common panel.'
        elif failure.is_file():
            closed=read(failure);full=closed.get('complete_pair')
            status='CLOSED_PROTOCOL_LIMIT'if'Fixed task boundary overrun'in closed.get('detail','')or'Fixed common-age target overrun'in closed.get('detail','')else'CLOSED_PRESERVED_FAILURE'
            scope='Actual prior experiences and adverse cut preserved. The terminal error is exported verbatim; no unsent panel is scored as incorrect and no process/protocol error is silently relabelled a cognitive failure.'
        else:
            status='PRESERVED_UNCOMMITTED_FUTURE';closed=read(marker);full=None
            scope=('Codex stopped its own supervising job after the preceding calendar failure. This R03 branch had already entered its second task. '
                   if life=='APD05_CTL_PREV_ORD_REAL_R03'else'The predeclared supervisor ended this owned branch; its exact timeout/exit receipt is exported when available. ')
            scope+='Its uncommitted Native future is unknown and is never resumed or treated as a cognitive failure.'
        initial=snap(SYSTEM/parent['pair_relative_to_system']/'VIDA.deetsnap.gz',keep=True)
        if initial.encoded_sha256!=parent['snapshot_sha256']:raise ValueError('Complete parent identity differs')
        if full:
            pair=Path(full['directory']);manifest=read(pair/'EXPORTACION_SERVICIO.json')
            if sha(pair/'EXPORTACION_SERVICIO.json')!=full['manifest_sha256']:raise ValueError('Complete export identity differs')
            final=snap(pair/'VIDA.deetsnap.gz')
            if final.encoded_sha256!=full['snapshot_sha256']:raise ValueError('Complete terminal snapshot differs')
            database=pair/'cola.sqlite3';db_copy=None
        else:
            record=read(SYSTEM/'estado/vidas'/life/'VIDA.json');final=snap(SYSTEM/record['snapshot'])
            if final.encoded_sha256!=record['snapshot_sha256']:raise ValueError('Last committed snapshot differs')
            local=EV/'CIERRES_INCIERTOS_N0_R02'/life;local.mkdir(parents=True,exist_ok=False);database=local/'cola.sqlite3'
            originals=[]
            for suffix in ('','-wal','-shm'):
                source=SYSTEM/'estado/servicios_persistentes'/life/('cola.sqlite3'+suffix)
                if source.is_file():
                    target=local/source.name;shutil.copy2(source,target);originals.append({'source':str(source),'sha256':sha(source),'bytes':source.stat().st_size})
            write(local/'COPIA_SIN_EDICION_DE_ORIGINALES.json',{'original_files':originals,'scope':'Read analysis of copied interrupted journal only. Never opens or checkpoints the original SQLite. The copy is not an acknowledged complete Native future.'})
            db_copy={'directory':str(local),'source_files':originals}
        inherited={r['id']:r for r in initial.receipts};final_map={r['id']:r for r in final.receipts}
        if any(final_map.get(k)!=v for k,v in inherited.items()):raise ValueError('An inherited Native terminal receipt changed or disappeared')
        new=[r for r in final.receipts if r['id']not in inherited]
        delta={'Native_ticks':0,'initial_snapshot_sha256':initial.encoded_sha256,'terminal_or_last_committed_snapshot_sha256':final.encoded_sha256,
               'inherited_receipts':len(inherited),'inherited_exact':True,'new_committed_receipts':new,'Native_pending_at_that_committed_cut':final.pending,
               'does_not_cover_uncommitted_future':status=='PRESERVED_UNCOMMITTED_FUTURE'}
        delta_file=OUT/'PRIMARIOS'/(life+'_DELTA_RECIBOS.json');write(delta_file,delta)
        uri=database.resolve().as_uri()+('?mode=ro&immutable=1'if full else'?mode=ro')
        con=sqlite3.connect(uri,uri=True)
        try:
            if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Transport integrity failed')
            counts=dict(con.execute('SELECT status,count(*) FROM requests GROUP BY status').fetchall())
            unresolved=con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')").fetchall()
            own=[dict(zip(('id','payload','payload_sha','status'),r))for r in con.execute('SELECT id,payload,payload_sha,status FROM requests WHERE id LIKE ? ORDER BY seq',(life.lower()+'_%',)).fetchall()]
        finally:con.close()
        if full and unresolved:raise ValueError('A closed complete pair contains unresolved transport')
        tw={'status_counts':counts,'unresolved':unresolved,'own_new_transport_requests':own,'database_sha256':sha(database),'copied_interrupted_journal':db_copy,
            'scope':'Complete paired journal for closed cases. For the uncertain case these are copied transport records and a last committed Native snapshot; they do not determine its lost in-memory future.'}
        tw_file=OUT/'PRIMARIOS'/(life+'_TRANSPORTE.json');write(tw_file,tw)
        sessions=[json.loads(x)for x in(native/'SESIONES.jsonl').read_text(encoding='utf8').splitlines()if x]
        interval_sources=[x for x in sessions if x['label'].startswith(('age_fill_','ordinary_work_'))and'result'in x]
        if interval_sources:
            point=interval_sources[-1]['result']['committed_snapshot'];interval=snap(SYSTEM/point['snapshot'])
        else:interval=initial
        field_rows=[field(initial,'complete_parent'),field(interval,'interval_endpoint'if status=='CLOSED_RESULT'else'last_committed_interval_prefix'),field(final,'final_after_panel'if status=='CLOSED_RESULT'else'terminal_or_last_committed_NOT_uncommitted_future')]
        case={'life':life,'revision':revision,'status':status,'scope':scope,'parent':parent,
              'ancestral_origin_tick':branch.get('ancestral_origin_tick',parent['tick']),
              'historical_tasks_at_import':branch.get('historical_completed_tasks',0),'new_tasks_scheduled':len(branch['task_offsets']),
              'sessions':add(native/'SESIONES.jsonl',life+'_SESIONES.jsonl'),
              'observations':add(native/'OBSERVACION_PASIVA.jsonl',life+'_OBSERVACION_PASIVA.jsonl'),
              'imported':add(native/'IMPORTACION_N0.json',life+'_IMPORTACION_N0.json'),
              'source_identity':add(native/'IDENTIDAD_Y_FUENTES.json',life+'_IDENTIDAD_Y_FUENTES.json'),
              'terminal':add(terminal,life+'_TERMINAL.json'),'native_receipt_delta':delta_file.relative_to(OUT).as_posix(),
              'transport_witness':tw_file.relative_to(OUT).as_posix(),'field_exports':field_rows,'complete_pair':full,
              'supervision':add(control/'SUPERVISION.json',life+'_SUPERVISION.json')if(control/'SUPERVISION.json').is_file()else None}
        for source in (native/'RECURSOS_NATIVE.json',native/'PROGRESO_ACTUAL.json',control/'STDERR.txt',control/'RECURSOS_ARBOLES.jsonl'):
            if source.is_file()and source.stat().st_size:add(source,life+'_'+source.name)
        frozen=native/'FUENTES_EJECUTADAS'
        if frozen.is_dir():
            for source in sorted(frozen.rglob('*')):
                if source.is_file():
                    target=OUT/'CODIGO'/'FUENTES_R04'/source.relative_to(frozen)
                    if target.is_file():
                        if sha(target)!=sha(source):raise ValueError('R04 Source changed between arms')
                    else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        cases.append(case)
    old=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CIERRE_SENSOR_R04_N0_R04/FUENTES_EJECUTADAS/008_cola_local.py.gz'
    target=OUT/'CODIGO/FUENTES_R03/app/cola_local.py';target.parent.mkdir(parents=True);target.write_bytes(gzip.decompress(old.read_bytes()))
    if sha(target)!='81c3036f4842f5b91a62abdcfe669d5a731d84188c4674fc0eb64ec5f6eefc69':raise ValueError('Original R03 transport code unavailable')
    schema_witness=add(EV/'EQUIVALENCIA_RAMA_PREVIA_COLA_N0_R01.json','EQUIVALENCIA_RAMA_PREVIA_COLA_N0_R01.json')
    known={x['file']for x in members}
    for source in sorted(OUT.rglob('*')):
        if source.is_file()and source.relative_to(OUT).as_posix()not in known:
            members.append({'file':source.relative_to(OUT).as_posix(),'bytes':source.stat().st_size,'sha256':sha(source)})
    write(OUT/'INDICE.json',{'Native_ticks':0,'members':members,'cases':cases,'transport_AST_witness':schema_witness,
                           'pre_native_instrument_revisions':[
                               {'revision':'R01','status':'DRAFT_NOT_NATIVE_EXECUTED','detail':'Initial alfa/beta oracle signs were corrected prospectively before any Native run. Exact draft code and protocol are included for provenance, not counted as physical trials.'},
                               {'revision':'R02','status':'PRE_OWNER_IMPORT_ASSERTION_FAILED','detail':'The executor incorrectly expected byte-identical imported snapshot metadata. Native ownership/ticks had not started; preserved partial imports were not reused. R03 fixed documentary identity while checking exact inherited physical arrays and source mapping. Exact R02 code/protocol are included; deep import records remain local.'}],
                           'omissions':['Full Native snapshots, SQLite, worker artifacts and historical outboxes remain at exact local complete-pair locations.','Interrupted Native futures were never saved; only their last committed states and copied journals exist.','R02 pre-owner import assertion evidence remains in original laboratory/evidence paths and is not counted as physical learning trials.']})
    result=recalc(OUT);write(OUT/'RECALCULO_N0.json',result)
    write(OUT/'MANIFIESTO.json',{'Native_ticks':0,'members':[{'file':q.relative_to(OUT).as_posix(),'bytes':q.stat().st_size,'sha256':sha(q)}for q in sorted(OUT.rglob('*'))if q.is_file()]})
    print(json.dumps({'out':str(OUT),'cases':len(cases),'issues':result['issues'],'Native_ticks':0}))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path);p.add_argument('--out',type=Path);p.add_argument('--fixtures',action='store_true');a=p.parse_args()
    if a.fixtures:
        decoder=load('pure_fixture_decoder',HERE/'ejecutar_reposo_y_acceso_r04.py')
        value=fixtures(decoder);write(a.out,value);print(json.dumps({'synthetic_cases':len(value['cases']),'Native_ticks':0}))
    elif a.root:
        value=recalc(a.root);write(a.out,value);print(json.dumps({'cases':len(value['cases']),'issues':value['issues'],'Native_ticks':0}))
    else:export()


if __name__=='__main__':main()
