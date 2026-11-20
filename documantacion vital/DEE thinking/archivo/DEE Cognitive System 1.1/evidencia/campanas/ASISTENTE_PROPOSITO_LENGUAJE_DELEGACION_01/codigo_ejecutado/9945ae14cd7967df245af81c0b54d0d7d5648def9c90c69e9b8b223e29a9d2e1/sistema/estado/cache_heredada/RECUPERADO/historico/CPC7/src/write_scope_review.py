"""Three scope reviews from primary measurements; never imports the engine."""
from collections import Counter
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha


OWNER={'campaign':'CPC7','agent':'capacity','generator':'src/write_scope_review.py'}


def load(relative):return json.loads((ROOT/relative).read_text(encoding='utf8'))


def pointer(document,path):
    current=document
    for token in path.split('/')[1:]:
        token=token.replace('~1','/').replace('~0','~')
        current=current[int(token)] if isinstance(current,list) else current[token]
    return current


def evidence(relative,*pointers):
    p=ROOT/relative;m=load(relative)
    for q in pointers:pointer(m,q)
    return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'schema':m.get('schema'),'JSON_pointers':list(pointers)}


def cases(folder):
    return [(p.relative_to(ROOT).as_posix(),json.loads(p.read_text(encoding='utf8'))) for p in sorted((ROOT/folder).glob('*/MEASUREMENTS.json'))]


def write(name,document):
    p=ROOT/'revision'/name
    if p.exists() and load(p.relative_to(ROOT)).get('authorship')!=OWNER:raise FileExistsError('Refusing to overwrite another author/campaign: '+str(p))
    document={'schema':'CPC7.scope_review.v1','authorship':OWNER,'generator_sha256':sha(__file__),
        'separation':'DATOS are primary observations; CALCULOS are reproducible post-trajectory transforms; LECTURA_PROVISIONAL is bounded interpretation. None feeds the participant.',
        'record_counting':'These reports overlap evidence. Do not sum their tables as independent cases. BASE338_MEASUREMENTS is a boundary subrecord of the same integrated preparation, not a new world.',**document}
    put(p,document)


def main():
    updates=cases('resultados/update_methods');selected=cases('resultados/selective_native');residues=cases('resultados/residue_regulation');integrated=cases('resultados/integrated_revision')
    update_rows=[]
    for path,m in updates:
        update_rows.append({'case_id':m['case']['id'],'method':m['case']['method'],'mode':m['case']['mode'],
            'before70':[{'form':q['form'],'value':q['decoded']['value'],'covered':q['decoded']['coverage'],'receipt':q['receipt']['status']} for q in m['old_queries']],
            'after338':[{'form':q['form'],'value':q['decoded']['value'],'covered':q['decoded']['coverage'],'receipt':q['receipt']['status'],'load':q['physical']['s_reg']} for q in m['new_queries']],
            'evidence':evidence(path,'/initial_acquisition','/old_queries','/new_queries','/revision_receipts','/host_RAW_clock_writes_after_T0','/calculations')})
    retention_rows=[]
    for path,m in selected+residues:
        retention_rows.append({'case_id':m['case']['id'],'preparations':m['preparations'],'diagnostic_forks':m['diagnostic_forks'],
            'configured_values_count':len(m['case']['bank_values']),'lower_panel':m['calculations']['lower_repertoire'],
            'receipt_scope':'Applied, rejected_occupied and uncovered response remain separate.',
            'evidence':evidence(path,'/case/bank_values','/acquisition','/lower_repertoire_reads','/calculations/lower_repertoire','/snapshots')})
    integrated_rows=[]
    for path,m in integrated:
        if m.get('schema')!='CPC7.integrated_revision.measurements.v1':continue
        integrated_rows.append({'case_id':m['case']['id'],'guard_mode':m['case']['guard_mode'],'revision_mode':m['case']['revision_mode'],
            'baseline338':m['base338']['calculations']['lower_repertoire']['338'],'after472':m['calculations'],
            'evidence':evidence(path,'/base338','/responses','/calculations','/requests','/host_RAW_clock_writes_on_MAIN','/snapshots'),
            'base_subrecord':evidence((Path(path).parent/m['base338']['path']).as_posix(),'/acquisition','/lower_repertoire_reads','/final_physical')})
    retention={'title':'RETENCIÓN Y PLASTICIDAD: función disponible, actualización y acceso separados',
        'DATOS':{'isolated_two_relation_update':update_rows,'own_memory_integrations':retention_rows,'same_U0_integrated_revision':integrated_rows},
        'CALCULOS':{'isolated_update_counts':load('resultados/update_methods/ANALYSIS.json')['counts'],
            'selective_counts':load('resultados/selective_native/ANALYSIS.json')['counts'],
            'residue_counts':load('resultados/residue_regulation/ANALYSIS.json')['counts'],
            'formulas':{'coverage':'Applied receipt AND active semantic1 AND load>query AND decoded fixed directional domain; null otherwise.',
                'retention_matches':'Count covered responses whose measured direction-class equals that form first acquired record, after new experiences without re-teaching the earlier form.',
                'updated_match':'Only auditor compares response472 against the separately supplied current new consequence. Stimulus does not read old decoded class.',
                'denominators':'Each lower panel14 includes6 older and8 newly acquired lower correspondences. L01/L02 own high banks are not included. Multiple ticks/queries/forks are not independent worlds.'}},
        'LECTURA_PROVISIONAL':[
            {'capacity':'Two finite update protocols revise one acquired directional correspondence while another remains usable.',
                'mechanism':'M1 supplies one additional current-consequence teacher through another fixed route. M2 uses two externally scheduled zero-load counterflows, then a new experience.',
                'evidence':'Six independent treatments (two pilots plus four frozen reserves) express both later queries; two offpath shams reject the revised-form reader while the other relation responds.',
                'domain':'N67,K2, one revision, response338. Extra input doses differ by method; not a resource-free or unlimited rewrite mechanism.'},
            {'capacity':'A native question can use a high acquired bank while later new experiences coexist with usable lower correspondences.',
                'mechanism':'Own selected memory70 is consumed/transformed through action72 and later cue75; lower banks receive their own real experiences0/134.',
                'domain':'Fourteen lower forms and one selected high-bank use per individual. The unselected high bank was not subsequently functionally queried in that same MAIN. No inference of16 permanently renewable answers.'},
            {'capacity':'Removing a declared residual-stream class rescues functional access without returning the fork to MAIN.',
                'mechanism':'External diagnostic cut76 removes four records matching predeclared positions/directions. Its sham is full-final-physical identical to parentR301.',
                'evidence':'RES_C01_CUT14/14 versus RES_C02_SHAM6/14 in204/338, with sign142 conserved. It locates a collective interference contribution, not the necessity of each individual stream.'},
            {'capacity':'Prepared interception is separately evaluated from acquired regulation scheduling.',
                'mechanism':'Six stationary semantic4 zero-load records are initial material, not host clearing afterT0.',
                'configuration_revision':'RES_G301 had17configured values; first16differed from intended parent/sham atL14-L16. Its14/14 versus oldG3026/14 is not a history-matched causal contrast. Old primaries/configuration remain. Corrected matched integrated cases use strict16validator and identical input histories.',
                'domain':'Prepared fixed interference management. No observation here demonstrates a policy learning when or what to regulate.'},
            {'capacity':'One guarded U0 changes one previously usable correspondence while thirteen others remain usable after its earlier communication/sign curriculum.',
                'mechanism':'IR_P01andIR_R607receive a new actual consequence402 through the fixed M1codec; common panel472 expresses the revisedL03(+1and−1respectively) and13/13unretrainedothers.',
                'controls':'IR_C02has identical complete physical state338and identical earlier inputs; moving the equal-dose second teacher to a declared other plane leavesL03query472occupied/uncovered while13/13othersrespond. Corrected guard comparisonIR_P01/IR_C01uses identical16experiences and69interfaces, yielding14/14versus6/14before any402revision.',
                'domain':'Four fresh N67preparations, one local update, final472; no global concept-count claim. Sign142was measured before, not after, revision402.'}],
        'boundaries':{'technical_snapshot_restore':'A successful software restore is continuity verification, not another acquired relation. Isolated update tests have8 same-process technical restores, not8additionalworlds.',
            'silence':'Uncovered response, empty site, occupied port, missing supply and absence of memory are distinct observations; none is automatically global forgetting.',
            'NSM':'Two directional output classes and65declared interfaces are not65semantic relations. No general NSM primitive count is generated by these panels.'},
        'analysis_sources':[evidence('resultados/update_methods/ANALYSIS.json','/counts','/limits'),evidence('resultados/selective_native/ANALYSIS.json','/causal','/counterexamples'),evidence('resultados/residue_regulation/ANALYSIS.json','/configuration_audit','/interpretation'),evidence('resultados/integrated_revision/ANALYSIS.json','/counts','/checks','/integrated_update_contrast')]}
    write('RETENCION_Y_PLASTICIDAD.json',retention)

    comparison=[]
    for folder in ('comparison_discovery','comparison_confirm','missing_actual_fallback'):
        for path,m in cases('resultados/endogenous/'+folder):
            comparison.append({'case_id':m['case']['id'],'family':folder,'history':m['case'].get('history'),
                'native_question19':len(m['native_questions']),'information24':len(m['received_information']),'physical_use29':len(m['later_physical_use']),
                'evidence':evidence(path,'/case','/native_questions','/received_information','/later_physical_use','/diagnostic_edits','/requests')})
    own=[]
    for path,m in selected:
        own.append({'case_id':m['case']['id'],'history':m['case']['history'],'actual_sensor':m['case']['actual'],
            'question19':None if m['diagnostic_forks'] else len(m['native_questions']),
            'information70':[{'bank':p['bank'],'direction':p['physical']['direction'],'load':p['physical']['s_reg']} for p in m['native_selected_information']],
            'actions72':len(m['native_actions']),'name142':[{'bank':p['name_bank'],'value':p['value']} for p in m['opaque_name_reads'] if p['coverage']],
            'evidence':evidence(path,'/rows','/native_questions','/native_selected_information','/native_actions','/opaque_name_reads','/diagnostic_edits')})
    recurrent=[]
    for path,m in cases('resultados/endogenous/recurrent'):
        recurrent.append({'case_id':m['case']['id'],'eligible_ticks':m['calculations'],
            'evidence':evidence(path,'/positive_Y_gate_ticks','/calculations','/host_inputs_after_T0','/host_RAW_clock_writes_after_T0')})
    consultations={'title':'CONSULTAS Y ACCESO: petición física condicionada y ventanas declaradas',
        'DATOS':{'comparison_and_finite_absence_families':comparison,'own_memory_access':own,'renewable_opportunity_component':recurrent},
        'CALCULOS':{'native_question':'Count only observed active horizontal records at configured question sites in19. For selective diagnostic forks beginning20,19is unobserved and is null, not0.',
            'information':'In comparator source family, count mixed physical product24. In own-memory family, count70record with Xbranch andYmemory direction. These are different geometries/horizons, not interchangeable rows.',
            'first_body_sign':'In measured ABbody, delta A−B=−1 and emission5 directionX=+1; BA reverses. Neither sign is borrowed from another apparatus.',
            'renewal_denominator':'91observed ticks10–100 within each of5prepared trajectories.46eligible ticks are not46independentparticipants.',
            'reader_limit':load('resultados/endogenous/BODY_SOURCE_SUMMARY.json')['retention_limit']},
        'LECTURA_PROVISIONAL':[
            {'capacity':'A learned-body emission and later actual report produce a native horizontal request on discrepancy.',
                'mechanism':'Physical comparison15 plus fixed preT0normalizer19; no host reading of mismatch to select the emitted question.',
                'controls':'Current matching report produces no request. Missing relevant history or omitted reader can also be silent. Source absent/unpaired permits a question but no coupled information/use.',
                'domain':'Prepared finite binary comparator, not an autonomous six-way diagnosis, utility optimizer, or general uncertainty policy.'},
            {'capacity':'An additional prepared route requests information when an expected current report is absent within a finite physical window.',
                'mechanism':'FallbackV2opportunity contacts the expectation carrier that stayed on its original path; matching report still suppresses that route.',
                'domain':'FALLfamily only. This property is not silently imported into selective_nativeV3, which deliberately reuses comparatorV1without the missing-actual fallback.'},
            {'capacity':'The physical request can reach a memory acquired by the same U0 rather than a separately supplied answer carrier.',
                'mechanism':'Question19travels51ticks to the returning high bank at70; its learnedYdirection participates in action72 and later cue-only142.',
                'control':'Selectivequestioncut20eliminates own-memory contact/use/sign; identicalRAWsham preserves it while14otherlowerfunctionsremainusable.',
                'domain':'Two prepared candidate banks and one selected use per individual. The route is prepared; the information content depends on actual earlier cue/event experience.'},
            {'capacity':'Prepared native opportunities can recur and be directionally suppressed without external entries afterT0.',
                'mechanism':'Internalsemantic4source andfixedcounterflow produce46/91versus0/91observedeligiblepatterns; offplaneandcodirectionalcontrols retain46/91.',
                'domain':'Component calibration, not the complete repeatedly interrogable guardedU0, nor evidence of learned choice to ask.'}],
        'instrument_vs_participant':{'participant':'Physical carrier, encounter, acquired state and emitted products.',
            'interface':'User requests and fixed sensory codecs; all alternatives supplied on a declared schedule, never selected from a target readout.',
            'auditor':'Counts, snapshots, exact field inspection, diagnostic forks and cause labels. These do not return a chosen response to MAIN.',
            'absence':'Silence and host timeout are not assigned a native logicalNO. A detector requires its specific prepared path and window.'},
        'sources':[evidence('resultados/endogenous/COMPARISON_SUMMARY.json','/counts','/causal_contrast','/six_requested_conditions_scope'),evidence('resultados/endogenous/FALLBACK_SUMMARY.json','/causal_diagnostic','/measured_scope'),evidence('resultados/endogenous/RECURRENT_SUMMARY.json','/counts','/scope'),evidence('resultados/endogenous/BODY_SOURCE_SUMMARY.json','/exact_emission5_equal','/traffic','/retention_limit')]}
    write('CONSULTAS_Y_ACCESO.json',consultations)

    chain=[]
    for path,m in selected:
        if m['case']['id'] not in ('SEL_P21_AB','SEL_P22_BA','SEL_R301_AB','SEL_R411_BA','SEL_N21_UNPAIRED','SEL_N22_OMITTED'):continue
        chain.append({'case_id':m['case']['id'],'history':m['case']['history'],'actual':m['case']['actual'],
            'own_bank_read70':[{'bank':x['bank'],'vector':x['physical']['direction'],'load':x['physical']['s_reg']} for x in m['native_selected_information']],
            'common_use72':[{'site_role':x['shared_site'],'vector':x['physical']['direction'],'load':x['physical']['s_reg']} for x in m['native_actions']],
            'sign142':[{'bank':x['name_bank'],'value':x['value'],'vector':x['physical']['direction'],'load':x['physical']['s_reg']} for x in m['opaque_name_reads'] if x['coverage']],
            'evidence':evidence(path,'/case','/native_selected_information','/native_actions','/opaque_name_reads','/requests','/local_windows')})
    factorial=[]
    for c in chain:
        if c['case_id'] in ('SEL_P21_AB','SEL_P22_BA','SEL_R301_AB','SEL_R411_BA'):
            info=c['own_bank_read70'][0];action=c['common_use72'][0]
            factorial.append({'case_id':c['case_id'],'branch_X':info['vector'][0],'acquired_content_Y':info['vector'][1],
                'native_information70':info['vector'],'native_use72':action['vector'],
                'same_X_Y_preserved_use':action['vector']==[info['vector'][0],info['vector'][1],1]})
    assert {(x['branch_X'],x['acquired_content_Y']) for x in factorial}=={(-1,-1),(-1,1),(1,-1),(1,1)}
    composition={'title':'COMPOSICIÓN Y DIÁLOGO: cadena física integrada, contenido adquirido y alcance del intercambio',
        'DATOS':{'same_U0_chains':chain,'integrated_later_revision':integrated_rows,
            'question_source_component':'The shorter comparator apparatus has source experience inside the same Runtime and request19→information24→use29. It is not the relocated own-bank70apparatus.'},
        'CALCULOS':{'primary_positive_preparations':'SEL_P21_AB,SEL_P22_BA,SEL_R301_AB,SEL_R411_BA: four independently prepared histories with one own-bank contact, one native-use product and one covered later sign each. A sham reuses a saved state and is counted separately.',
            'branch_by_acquired_content_2x2':factorial,
            'binding_check':'Compare each covered sign bank prefix(left/right) and decodedY to the selected own bank70. Do not count only equal output magnitude as preservation of role.',
            'same_signal_histories':'Within ABpairs(P21,R301) andBApairs(P22,R411), selected bank route is fixed and opposing earlier bank experience changes the physicalYcontent70/142. Reserved query loads11/15 are explicit variations.',
            'teaching_control':'Unpairedcue73vs72and omitted cue preserve question/information/use but yield0coveredcue-only142responses.',
            'new_learning_between_name_and_query':'Opaque cue75 precedes eight additional real form experiences134/acquisition137, then sign-only query139/read142 in the same MAIN. No reconstruction between these stages.'},
        'LECTURA_PROVISIONAL':[
            {'capacity':'Acquired body history, selected directional memory and a later common resource combine natively before a new opaque association.',
                'mechanism':'BranchXcomesfromthebody/actualcomparison; Ycomesfromanindependentlyexperiencedownbank; +Zresourceactsat72; externalopaque cueat75cancelsX/Zandproducesadirectionalnewmemory.',
                'evidence':'Four positive preparations, formed-questioncut/sham and name-pairing controls. Exact vectors/loads/ticks are in the table, not obtained from expected-output lookup.',
                'domain':'One prepared finite computational composition. Not an arbitraryR(A,B) syntax or unconstrained semantic role binding.'},
            {'capacity':'A later signo-response depends on preceding physical experience and survives the added acquisition block.',
                'mechanism':'Both possible lanes and bothYcontent routes have fixed identical physical teaching/query opportunities. No host chooses which active lane receives the correct word.',
                'domain':'One opaque protocol with two directional contents. The spatial address preserves which prepared lane is observed; final carrier direction alone does not encode all participants or abstract identity.'},
            {'capacity':'Question, transport, acquisition-dependent response and subsequent physical use are observed inside one Runtime.',
                'mechanism':'Prepared physical regions exchange porters without an outputA→host-calculation→inputBcallback.',
                'domain':'This establishes a finite communicative operation among coupled regions/components. It does not by itself demonstrate two self-renewing complete minds, dialogue-selected interlocutors, unlimited turns, or an acquired general communication convention.'},
            {'capacity':'Prepared regulation and one local revision are combined with the same U0chain in two positive complete preparations.',
                'evidence':'IR_P01andreservedIR_R607firstexpress question→own-bank→use→sign142and14/14lowerfunctions338, then reviseL03byactualnewexperience402and expressitsnewvalueplus13/13others472. Integrated rows are actual same-Runtime338→472continuations of their own preparations, not a concatenation of isolatedK2updates with a separate dialogueworld.',
                'domain':'Interpret only executed covered responses, preserve offpath/occupied outcomes, and use corrected history-matched guards rather than old17-valueconfoundedcase.'}],
        'not_inferred':{'NSM':'No65NSM meanings, generalANTES/DESPUÉS, YO/TÚ, MISMO/OTRO or logicalNOare credited from two direction classes or fixed participantIDs.',
            'order':'The body acquired a distinction from the order ofA/Bphysicalevents. Generalization to arbitrary participant identities/intervals or role reversal requires separate trials.',
            'language':'Textnamesandrendererareinterfaceconventions. The measured acquired relation is physicalcue/functionmapping, not fluentSpanishconversation.',
            'policy':'An endogenous physical question is not equivalent to a policy that learned to maximize information or utility. The preparation provides the finite route and opportunity.'},
        'causal_references':[evidence('resultados/selective_native/ANALYSIS.json','/causal','/counterexamples','/domain'),evidence('resultados/residue_regulation/ANALYSIS.json','/configuration_audit','/checks','/interpretation'),evidence('resultados/integrated_revision/ANALYSIS.json','/checks','/corrected_guard_contrast','/integrated_update_contrast','/limits')]}
    write('COMPOSICION_Y_DIALOGO.json',composition)
    print(json.dumps({'written':['revision/RETENCION_Y_PLASTICIDAD.json','revision/CONSULTAS_Y_ACCESO.json','revision/COMPOSICION_Y_DIALOGO.json'],
        'integrated_complete_records':len(integrated_rows),'engine_calls':0}))


if __name__=='__main__':main()
