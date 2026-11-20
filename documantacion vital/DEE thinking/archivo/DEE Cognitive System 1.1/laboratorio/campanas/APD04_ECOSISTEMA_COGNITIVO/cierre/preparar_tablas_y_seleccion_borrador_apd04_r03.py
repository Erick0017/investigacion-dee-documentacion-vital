"""Prosa/datos de cierre DRAFT desde fuentes cerradas; no autoriza sello ni Native."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True); p.add_argument('--cas', type=Path, required=True)
    p.add_argument('--cas-reference', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    a = p.parse_args(); root = a.root.resolve(); a.out.mkdir(parents=True, exist_ok=False)
    L='laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/'; E='evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/'
    source_rows=[]
    def read(name, rel):
        path=root/rel; data=json.loads(path.read_bytes())
        source_rows.append({'id':name,'path':rel,'sha256':sha(path),'bytes':path.stat().st_size})
        return data
    data=read('LEX_REF', E+'BORRADOR_CIENTIFICO_PREFIJO_CERRADO_N0_R01/DATOS_CERRADOS_Y_HASHES.json')
    brief=read('BRIEF', L+'controles_diseno/EVIDENCIA_NIVELES_BREVES_CAS_N0_R02/RESUMEN_RESULTADOS.json')
    abc=read('ABC', E+'ATENCION_ABC_DOSIS_COMPLETA_N0_R02/RECALCULO_ABC_Y_CONCILIACION_FULL_R02.json')
    r04=read('R04', E+'CIERRE_SENSOR_R04_N0_R04/RECALCULO_CIERRE_R04_N0.json')
    guard=read('GUARD', E+'RESERVA60_CIERRE_GUARDA_N0_R03/RECALCULO_CIERRE_RESERVA_N0.json')
    wait=read('WAIT', E+'WAIT_R03_POST10_EVIDENCIA_PORTABLE_N0_R01/RECALCULO.json')
    wait_index=read('WAIT_INDEX', E+'WAIT_R03_POST10_EVIDENCIA_PORTABLE_N0_R01/INDICE.json')
    footprint=read('P1_FOOTPRINT', E+'WAIT_R03_PRIMERA_DIVERGENCIA_N0_R01/RECALCULO_GLOBAL.json')
    view_closures=[read('VIEW_'+kind,E+'VISTA_POST10_'+kind+'_R02/CIERRE_BRAZO_Y_RESUMEN_N0.json')
                   for kind in ('CIRCULAR_REAL','PERSISTENTE_REAL')]
    actuator_cards=[read('ACT_'+kind,E+'ACTUADOR_R02_AUX_R01/EVIDENCIA_PORTABLE_R01/vidas/APD04_ACTUADOR_'+kind+'_R02/VIDA_ORIGINAL.json') for kind in ('REAL','OMIT')]
    rows=[]; lives=[]; attempts=[]
    def life(identifier,tick,digest,status,available,unknown,parent=None,continuation=None):
        lives.append({'id':identifier,'parent':parent,'N':67,'tick':tick,'snapshot_sha256':digest,'status':status,
            'available':available,'not_currently_proven':unknown,'continuation':continuation or {
                'scope':'Full local state/queues and original genealogy must be used; this analysis has no operative snapshot.'}})
    def cap(life_id,moment,ability,result,source,scope,limits,level='CAPACIDAD_FUNCIONAL'):
        rows.append({'life':life_id,'moment':moment,'capability':ability,'result':result,'level':level,
            'source_id':source,'scope':scope,'limits':limits})
    def attempt(identifier,who,status,scope,requested=None,responded=None,correct=None,rejected=None,role='AUX'):
        attempts.append({'id':identifier,'life':who,'role':role,'status':status,'scope':scope,
            'source_ids':['CLOSED_CAS'],'requested':requested,'responded':responded,'correct':correct,
            'rejected':rejected,'denominator_scope':'Counts apply only to the named closed scope; null is not zero. Forks are dependent prefixes, not independent learners.'})
    cap('APD04_MAIN',639374,'Two learned signal associations',{'clasifica':1,'equilibra':-1,'new_forms':2},'LEX_REF',
        'Explicit docence, Native use and later material old panel in the same life.',
        ['Prepared pipeline/body/readers; not18new meanings, free language or NSM65.'])
    cap('APD04_MAIN',639374,'Inherited access panel',{'old_forms_unique':16,'old_forms_queried':16,'MA_unique':6,'MA_queried':6},'LEX_REF',
        'Panel after two new docences; formed_native_command recalculated from RAW.', ['16includes luma/nara; no guarantee at later adverse cuts.'])
    life('APD04_MAIN',658938,'54ed19ab65ca09c2f03d37f963c5fa50c2134d3dbe6923c01e0f09d1bb58533d',
        'PRESERVED_UNCOMMITTED_FUTURE_NOT_NORMAL_CONTINUABLE',[],['Current old or new access not established after the unfinished operation.'],
        {'life':'APD03_MAIN','tick':604825}, {'scope':'Do not clear marker/replay. Explicit fork from a named complete past only.'})
    attempt('MAIN_PILOT_R01',None,'CLOSED_INSTRUMENT_FAILURE','NameError before Native, exact code reconstructed/hash confirmed; not a cognitive failure.',role='N0_INSTRUMENT')
    attempt('MAIN_PILOT_R02','APD04_MAIN','CLOSED_RESULT','Actual pilot via same Supervisor; exact source/log kept, not a separate learning replicate.',role='MAIN')
    attempt('MAIN_PREPARATION_R03','APD04_MAIN','CLOSED_RESULT','Peripheral prepared apparatus added in declared stage; preparation is not acquired content.',role='MAIN')
    for name in ('CALIBRACION_R01','CALIBRACION_R02','ADMISION_LEXICA_R01','SENSORES_Y_LEXICO_R01'):
        attempt(name,None,'CLOSED_RESULT','All original calibration/admission/sensor primaries preserved in CAS, including negative results; no extra capability inferred from this inventory.',role='AUX')
    attempt('MAIN_LEARNED_PREFIX','APD04_MAIN','CLOSED_RESULT','Two taught forms, comparison and balance pipeline, old16+6 panel.',role='MAIN')
    attempt('MAIN_ADVERSE_PROLOGUE','APD04_MAIN','PRESERVED_UNCOMMITTED_FUTURE','25planned;9sent/8complete; unfinished operation and supervision failure. Lesson20→21, criterion19 gave1/2.',25,8,1,role='MAIN')
    cap('APD04_CONTINUABLE_R01',658754,'Old access after R04 densification',{'old_forms_formed':0,'old_forms_queried':16,'MA_formed':0,'MA_queried':6,'panel_applied':5,'panel_rejected':149},'R04',
        'Four prior work opportunities all0useful; final old panel0/22.', ['New two words not in that old panel; no proof of content destruction.'])
    life('APD04_CONTINUABLE_R01',658754,'582f7eb19ceb63909754c6ba9bc1e573f956795c97a8f90c3e4170a5e22a1577',
        'COMPLETE_ADVERSE_SAVED_STATE',[],['Old panel unavailable; two APD04 words not checked after densification.'], {'life':'APD04_MAIN','tick':639374})
    attempt('CONTINUABLE_90_SECONDS','APD04_CONTINUABLE_R01','CLOSED_RESULT','Real UI queries/new measurements; pending exact ID saved then consumed once by same ID in R04.',role='FORK')
    attempt('SENSOR_R04_ADVERSE','APD04_CONTINUABLE_R01','CLOSED_RESULT','Natural close2529.1090026s;4work0useful, old0/22;134applied+174reject/308 new IDs excluding inherited4.',4,3,0,174,role='FORK')
    for branch in data['branches']:
        committed=[x['metrics']['committed'] for x in branch['events'] if x.get('metrics',{}).get('committed')]
        if not committed: continue
        last=max(committed,key=lambda x:x['physical']['tick']); identifier=last['life_id']
        cap(identifier,last['physical']['tick'],'Lexical/reference control history',
            {'condition':branch.get('condition'),'unique_exported_inputs':branch.get('unique_exported_physical_request_IDs_in_branch')},
            'LEX_REF','Individual closed control events retained in CAS with raw witnesses.',
            ['Not added to MAIN; last exported material cut is not necessarily final postSTOP tick.'])
        life(identifier,last['physical']['tick'],last['snapshot_sha256'],'AUX_LAST_EXPORTED_MATERIAL_CUT',
             ['See exact lexical/reference rows in closed control; no global inherited repertoire claim.'],
             ['A/B transfer advantage not demonstrated; generic equality/HOLD not demonstrated.'], {'source_id':branch.get('closure_source_id')})
        attempt('CONTROL_'+identifier,identifier,'CLOSED_RESULT','Lexical/reference history, RAW-specific cases and negative results; no aggregate generalization claim.')
    for b in abc['branches']:
        cap(b['life'],b['tick'],'Prepared interface and response',{'work_completed':b['completed_work_opportunities'],
             'Native_inputs':b['all_unique_native_inputs'],'applied':b['applied'],'rejected':b['rejected'],'useful':0},
             'ABC','All port/channel IDs reconciled against complete historical receipt delta.',
             ['P0 interface contrast, not useful learned attention; C5 no committed result.'])
        life(b['life'],b['tick'],b['snapshot_sha256'],'AUX_HISTORICAL_COMMIT_CHECK_MARKER_BEFORE_CONTINUING',
             ['Recorded response/interface effects only.'], ['No useful attention or full memory-retention guarantee.'])
        attempt('ABC_'+b['branch'],b['life'],'CLOSED_RESULT','Closed completed opportunities only; any interrupted later future is preserved.',
                b['all_unique_native_inputs'],b['completed_work_opportunities'],0,b['rejected'])
    for b in brief['branches']:
        d=b['functional_denominators']; loc=b['complete_pair_local_locator']
        cap(b['life'],b['final_tick'],'Five-opportunity external source-count test',
            {'external_sources':b['sources'],**d,'Native_IDs':b['native_new_IDs'],'occupied':b['physical']['occupied']},
            'BRIEF','Five material opportunities and old4 per separate fork.',
            ['Sequential cursor and environmental cache prepared; not20objects inspected or Native numeric learning.'])
        life(b['life'],b['final_tick'],loc['complete_native_snapshot_sha256'],'CLOSED_COMPLETE_ALTERNATIVE_PROFILE',
             ['Five selected opportunities and old4 panel4/4.'], ['Long-term retention, all24panel and general attention untested.'],
             {'life':'APD04_MAIN','tick':639374},{'local_complete_pair':loc['directory'],'manifest_sha256':loc['manifest_sha256']})
        attempt('BRIEF_N'+str(b['sources']),b['life'],'CLOSED_RESULT','Work plus separate old4 dose; dependent fork.',5,5,d['environment_NEW_gain'],0)
    cap('APD04_ACTUADOR_REAL_R02',667452,'Reserve seven complete work opportunities',
        {**guard['work_counts'],'Native_IDs':guard['unique_native_inputs'],'statuses':guard['native_input_statuses'],
         'occupied':guard['last_global_fields']['occupied'],'external_mu_difference':20},'GUARD',
        '7complete works only; eighth processing unknown;64planned events not realized.',
        ['External μdifference is not Native recovery; no normal continuation certification.'])
    life('APD04_ACTUADOR_REAL_R02',667452,guard['last_snapshot_sha256'],'INTERRUPTED_FUTURE_PRESERVED',[],
         ['Old22 not rechecked after density; processing eighth work uncommitted.'],{'life':'APD04_MAIN','tick':639374},
         {'pending':guard['pending_transport'],'marker':guard['interrupted_marker'],'scope':'Do not replay/clear; no normal continuation claimed.'})
    attempt('ACTUATOR_R02_REAL_OMIT',None,'CLOSED_RESULT','Both10work1useful each;211/140Nativework IDs; old22 retained on each before reserve. Two lives, not MAIN sum.',20,20,2,0)
    for card, doses in zip(actuator_cards,(211,140)):
        cap(card['life_id'],card['physical']['tick'],'ACTR02 post10 plus old panel',
            {'work_opportunities':10,'work_formed':10,'work_useful':1,'work_Native_inputs':doses,
             'old_forms_formed':16,'MA_formed':6,'old_panel_Native_inputs':154},'ACT_'+('REAL' if doses==211 else 'OMIT'),
            'Historical post10 scope, before the later REAL reserve, not a current-access guarantee.',
            ['Not added to MAIN; two signals APD04 not both queried at this moment; cache not Native numeric memory.'])
        if 'OMIT' in card['life_id']:
            life(card['life_id'],card['physical']['tick'],card['snapshot_sha256'],'CLOSED_ACTR02_ALTERNATIVE_POST10',
                 ['Old16+6 formed at this recorded panel.'],['No long reserve, learned general attention or all-language ability.'],card.get('parent'))
    attempt('RESERVE_90MIN_GUARD','APD04_ACTUADOR_REAL_R02','PRESERVED_UNCOMMITTED_FUTURE',
        '64all events=63material+checkpoint.10material sent/9complete,7workcomplete, eighthprocessing.53material+checkpoint not executed.',64,7,1,105,role='FORK')
    for b in wait['branches']:
        index_row=wait_index['branches'][b['branch']]
        delta_path=root/(E+'WAIT_R03_POST10_EVIDENCIA_PORTABLE_N0_R01/'+index_row['full_receipts_delta'])
        delta=json.loads(delta_path.read_bytes())
        cap(index_row['life'],delta['final_tick'],'Prepared ACTR03 with history-dependent local WAIT',
            {'opportunities':b['work_requests_completed'],'formed':b['Native_formed'],'actions':b['actions'],
             'old_work_gain':b['old_work_gain'],'new_quality':b['new_quality'],'Native_IDs':b['Native_receipts']},
            'WAIT','Post10 frozen architecture; old/new criteria retained separately.',
            ['No old24panel in these originals; no useful R2 general claim; inactive view not enabled.'])
        life(index_row['life'],delta['final_tick'],delta['final_snapshot_sha256'],'CLOSED_R03_SPECIALIZED_POST10',
             ['10/10 physical responses; REAL localWAIT1, OMITnone.'],['Old24 retention not tested in this post10.'],
             {'life':'APD04_MAIN','tick':639374})
        attempt('WAIT_R03_'+b['branch'],index_row['life'],'CLOSED_RESULT','oldgain0; newquality1vs0 is different criterion, not replacement.',
             10,10,b['new_quality'],0)
    life('APD04_SEMILLA_COLABORADOR_R01',654959,'52a35b4062bc843a74a115679ba7c6f76c9db1eab145926ac9d01d22390723fc',
         'PROSPECTIVELY_SELECTED_COMPLETE_FULL_SEED_BEFORE_FINAL_PROOFS',
         ['Exact physical history inherited from R03 REAL; N0 clone is not new acquisition.'],
         ['Final24panel, Full distinct acquisition/continuation and future reserve proof pending.'],
         {'life':'APD04_WAIT_R03_REAL_AUX_R05','tick':654959},
         {'local_complete_pair':'sistema/estado/fuentes_emparejadas/APD04_SEMILLA_COLABORADOR_R01_T654959_COMPLETO_N0_R01',
          'manifest_sha256':'0658ca4404f1d676cb9d496f2c1d4f5fbdfee98188a5c717db68e760088f9b2c'})
    for v in view_closures:
        s=v['summary_N0']; f=v['actual_final']; card=f['final_record']; who=card['life_id']
        cap(who,card['physical']['tick'],'Late prepared view, incomplete six-opportunity protocol',
            {'requested':s['Native_queries_requested_in_plan'],'complete':s['opportunities_completed'],
             'actions':s['actions'],'old_gain':s['old_gain_reported'],'new_quality':s['new_WAITquality_reported'],
             'last_committed_occupied':card['physical']['occupied'],'owner_stop_confirmed':f['owner_stop_confirmed']},
            'VIEW_'+v['arm'],'Closed instrumentally at local guard; last committed result is not complete final operational state.',
            ['No FULL postSTOP seal, pending operation and uncommitted future remain; no memory destruction, learned view or sustained attention claim.'])
        for prior in lives:
            if prior['id']==who:
                prior['historical_record_before_later_view']={k:prior[k] for k in ('tick','snapshot_sha256','status','available')}
                prior.update(tick=card['physical']['tick'],snapshot_sha256=card['snapshot_sha256'],
                    status='LATER_VIEW_INTERRUPTED_FUTURE_PRESERVED_NOT_CERTIFIED_CONTINUABLE',available=[],
                    not_currently_proven=['Old24 access after incomplete view; no final FULL/STOP confirmation.'],
                    continuation={'pending':f['final_protocol'].get('pending_material'),'scope':'Do not replay or treat last historical commit as a complete closed future.'})
                break
        else:
            life(who,card['physical']['tick'],card['snapshot_sha256'],'LATE_VIEW_INTERRUPTED_FUTURE_PRESERVED',[],
                 ['No final FULL, no old24 panel after interruption.'],card.get('parent'),
                 {'pending':f['final_protocol'].get('pending_material'),'scope':'No normal continuation certified from this interrupted future.'})
        attempt('LATE_VIEW_'+v['arm'],who,'PRESERVED_UNCOMMITTED_FUTURE',
            str(s['opportunities_completed'])+'/6 completed; oldgain/newquality='+str(s['old_gain_reported'])+'/'+str(s['new_WAITquality_reported'])+
            '; wrapper exit1, local600s plus closure, outer Job0 but owner STOPfalse, no FULL. Remaining offered operations are not counted as failures.',
            6,sum(x['RAW_sign'] is not None for x in s['rows']),s['old_gain_reported'],None,role='CONTINUATION_OR_FORK')
    pending=[{'id':identifier,'status':'PENDING_ROOT_CLOSED_PRIMARY','numbers':None} for identifier in
             ('THREE_VIEW_ARMS','FINAL_LONG_RESERVE','FULL_EXACT_PROOF','WORD_1_18_EDIT_AND_RENDER')]
    pending[0].update(status='TWO_CLOSED_INSTRUMENTALLY_THIRD_IN_PROGRESS',scope='Circular3/6 and persistentREAL1/6 with pending op4/op2, no FULL. PersistentOMIT still awaiting closed evidence. No6/6 or60min inferred.')
    pending[1].update(scope='Early-persistence alternative from complete T639374 is a separate prospective fork, not T0 or post10 repair; final60plan/closure pending.')
    claims=[{'id':'LEARNED_TWO','text':'Two signal associations acquired and used in a continuous MAIN prefix.',
        'level':'CAPACIDAD_FUNCIONAL','life':'APD04_MAIN','scope':'T639374; explicit teaching and old16+6 afterwards.',
        'source_ids':['CLOSED_CAS'],'localizers':[E+'MAIN_ADQUISICION_R01/TRAYECTORIA/EVENTOS.jsonl'],
        'limits':['Prepared composition pipeline; not18new meanings or NSM65.']},
        {'id':'HISTORY_DECISION_LOCAL','text':'R03 REAL local WAIT differs from OMIT after consequence history.',
        'level':'MECANISMO_FISICO','life':'APD04_WAIT_R03_REAL_AUX_R05','scope':'Ten-opportunity domain; oldgain0both/newquality1vs0.',
        'source_ids':['CLOSED_CAS'],'localizers':[E+'WAIT_R03_POST10_EVIDENCIA_PORTABLE_N0_R01/RECALCULO.json'],
        'limits':['No general attention/R2, no old24panel, prepared codec and postaction criterion.']},
        {'id':'NO_DESTRUCTION_PROOF','text':'Access failure and externally conserved μdifference do not prove global memory loss or recovery.',
        'level':'HECHO_COMPUTACIONAL','life':'APD04_ACTUADOR_REAL_R02','scope':'T667452 arrays/receipts/markers and seven complete work rows.',
        'source_ids':['CLOSED_CAS'],'localizers':[E+'RESERVA60_CIERRE_GUARDA_N0_R03/RECALCULO_CIERRE_RESERVA_N0.json'],
        'limits':['Eighth future uncertain; no alternate Native access or matched-history convergence test.']}]
    claims.append({'id':'LOCAL_P1_FOOTPRINT','text':'At common post-op1tick640864 only one RAW site differs across300763sites; clocks/interfaces/pending/phase agree in the analysed domain. Common next opportunity yields valid0WAIT versus−INSPECT.',
        'level':'HECHO_COMPUTACIONAL','life':'APD04_WAIT_R03_REAL_AUX_R05','scope':'Local history trace: (26,12,53), s_reg615vs616. Not identity of biographical metadata or unique causal proof.',
        'source_ids':['CLOSED_CAS'],'localizers':[E+'WAIT_R03_PRIMERA_DIVERGENCIA_N0_R01/RECALCULO_GLOBAL.json'],
        'limits':['No selective intervention/sham; P1local, not P2general.']})
    coverage={'schema':'APD04.coverage.DRAFT.R01','status':'DRAFT_NOT_APPROVED','closed_sources':source_rows,
              'attempts':attempts,'pending_root':pending,'not_repeated':['Historical34families','CPC consolidation','Native experiment replay for packaging'],
              'not_demonstrated':['General useful attention','NSM65acquisition','GeneralR2','Human language','Memory destruction or universal stability'],
              'codecs':'P0 and criterion versions retained, including old gain vs new quality; no NULL→WAIT.', 'new_Native_ticks_for_this_builder':0}
    dump(a.out/'CAPACIDADES_POR_VIDA.json',{'schema':'APD04.capabilities_by_life_and_moment.DRAFT.R01','rows':rows,'pending':pending})
    dump(a.out/'COMPARACION_DE_VIDAS.json',{'schema':'APD04.lives_comparison.DRAFT.R01','lives':lives,'no_merging_of_fork_memories':True})
    dump(a.out/'DEMOSTRABILIDAD.json',{'schema':'APD04.claim_attribution.DRAFT.R01','claims':claims,
         'prepared':['Body/interfaces','Cursor/cache','Codecs','Toolchain','Curriculum','Evaluator'],
         'Native':['RAW field evolution','Signals after docence','Comparator emission','Selector valid signs'],
         'not_attributed':['Host cache as Native memory','External archive as actor memory','Calendar as initiative','Package import as new learning']})
    dump(a.out/'COBERTURA.json',coverage)
    dump(a.out/'FUENTES_DE_TABLAS.json',{'sources':source_rows,'new_Native_ticks':0})
    cas_rel=a.cas.relative_to(root).as_posix(); ref_rel=a.cas_reference.relative_to(root).as_posix()
    result={'schema':'APD04.final_analysis_selection.R01','status':'DRAFT_NOT_APPROVED','native_work_closed':False,
       'zip_name':'DEE_COGNITIVE_1_1_APD04_ECOSISTEMA_COGNITIVO_ANALISIS.zip','full_status':'PENDING_ROOT_EXACT_ARCHIVE_PROOF_SAME_PC',
       'attempts':attempts,'claims':claims,'lives':lives,
       'executed_revisions':[{'id':'EXACT_FROZEN_REVISIONS','scope':'All executed byte revisions kept by original path/hash in CAS, not current S only.',
          'source_ids':['CLOSED_CAS'],'provenance':'FUENTES_ANTES_DE_NATIVE and archived closures; failed/reconstructed R01 explicitly distinguished.'}],
       'files':[{'id':'CAS_RECALC','source':L+'cierre/recalcular_cas_en_proceso_apd04_n0_r01.py','destination':'RECALCULO/recalcular_CAS.py',
                 'kind':'Portable archived CAS recalculation','sha256':sha(root/(L+'cierre/recalcular_cas_en_proceso_apd04_n0_r01.py'))},
                {'id':'CAS_REFERENCE','source':ref_rel,'destination':'RECALCULO/REFERENCIA_CAS.json','kind':'Byte reference for closed CAS only','sha256':sha(a.cas_reference)}],
       'components':[{'id':'CLOSED_CAS','source':cas_rel,'destination':'EVIDENCIA_CAS','manifest':'MANIFIESTO_CAS.json','manifest_sha256':sha(a.cas/'MANIFIESTO_CAS.json')}],
       'jobs':[{'id':'CLOSED_CAS_RECALCULATE','base':'.','script':'RECALCULO/recalcular_CAS.py',
                'args':['--package',{'input':'EVIDENCIA_CAS'},'--out','{output}'],'expected':'RECALCULO/REFERENCIA_CAS.json','comparison':'bytes','timeout_seconds':900}],
       'omissions':[{'locator':'sistema/estado/fuentes_emparejadas and estado/checkpoints, exact locator/SHA in source indexes',
         'reason':'Full operative states stay local; no motor/WHL/history ZIP duplicate in analysis.',
         'scientific_consequence':'Analysis recalculates records but is not an operative life continuation backup.'}],
       'pending_root_closures':pending}
    for path in sorted(a.out.iterdir()):
        result['files'].append({'id':path.stem,'source':path.relative_to(root).as_posix(),'destination':path.name,
                               'kind':'DRAFT scientific table, not final approval','sha256':sha(path)})
    report=root/(L+'cierre/INFORME_CIENTIFICO_RESULTADOS_BORRADOR_APD04_R02.md')
    result['files'].append({'id':'SCIENTIFIC_DRAFT','source':report.relative_to(root).as_posix(),'destination':'INFORME_CIENTIFICO_RESULTADOS.md',
                           'kind':'DRAFT scientific report, replace closure placeholders before approval','sha256':sha(report)})
    extras=[('MANUAL_DRAFT',L+'manual/BORRADOR_MANUAL_APD04.json','BORRADORES/BORRADOR_MANUAL_APD04.json'),
            ('FULL_PROSPECTIVE_SELECTION',L+'distribucion/PROTOCOLO_FULL_APD04_CERRADO_R02.json','EVIDENCIA_CAUSAL/SELECCION_FULL_PROSPECTIVA.json')]
    extras.extend(('VIEW_CLOSURE_'+v['arm'],E+'VISTA_POST10_'+v['arm']+'_R02/CIERRE_BRAZO_Y_RESUMEN_N0.json',
                   'EVIDENCIA_CAUSAL/VISTA_'+v['arm']+'_CIERRE.json') for v in view_closures)
    for name,rel,destination in extras:
        result['files'].append({'id':name,'source':rel,'destination':destination,'kind':'Closed primary or explicitly marked draft; no Native execution',
                                'sha256':sha(root/rel)})
    dump(a.out/'RESULTADOS_FINAL.json',result)
    print(json.dumps({'rows':len(rows),'lives':len(lives),'attempts':len(attempts),'status':result['status'],'new_Native_ticks':0}))


if __name__=='__main__':main()
