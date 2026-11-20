"""Selective, byte-exact CPC7 genealogy inventory. No historical runner is run."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT.parents[1]
DOC = CASES.parent.parent
PRODUCT = CASES.parent / '4.0'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def archive(path, source_id, expected=None):
    data = path.read_bytes()
    observed = sha(data)
    if expected and observed != expected:
        raise ValueError(f'Source identity mismatch: {source_id}: {observed}')
    with zipfile.ZipFile(path) as z:
        return {'id':source_id,'file':path.name,'sha256':observed,'bytes':len(data),
                'members':len(z.infolist()),'expected_sha256':expected,
                'identity':'MATCH_REFERENCE' if expected else 'IDENTIFIED_CURRENT_SOURCE',
                'source_modified':False}

def main():
    paths={
        'CPC3':CASES/'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip',
        'CPC4':CASES/'CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip',
        'CPC5':CASES/'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip',
        'CPC6':CASES/'CPC6_MENTE_DEE_INTEGRADA_APRENDIZAJE_Y_COMUNICACION_RESULTADOS.zip',
        'PRODUCT4':PRODUCT/'DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip',
    }
    expected={
        'CPC3':'1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6',
        'CPC4':'4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723',
        'CPC5':'d31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05',
        'CPC6':'9d8c72a2536a7d8a782e0f3885d6d9ceba48b5f3d9111f618386def13fff708b',
    }
    ancestors={
        'ING01':('ingenieria','INGENIERIA_01_'), 'ING02':('ingenieria','INGENIERIA_02_'),
        'ING05':('ingenieria','INGENIERIA_05_'), 'ING06':('ingenieria','INGENIERIA_06_'),
        'CORE06':('cores','06_'), 'CORE07':('cores','07_'),
        'PROC01':('procesos','PROCESOS_01_'), 'PROC02':('procesos','PROCESOS_02_'),
        'PROC03':('procesos','PROCESOS_03_')}
    for sid,(folder,prefix) in ancestors.items():
        found=list((DOC/folder).glob(prefix+'*.zip'))
        if len(found)!=1:raise ValueError(f'Ambiguous source {sid}: {found}')
        paths[sid]=found[0]
    identities=[archive(p,sid,expected.get(sid)) for sid,p in paths.items()]
    ident={r['id']:r for r in identities}
    selected=[];missing=[]
    def take(sid,member,destination=None,suffix=False):
        with zipfile.ZipFile(paths[sid]) as z:
            candidates=[n for n in z.namelist() if n.endswith(member)] if suffix else [member] if member in z.namelist() else []
            if len(candidates)!=1:
                missing.append({'source':sid,'requested_member':member,'matches':len(candidates)})
                return None
            member=candidates[0];info=z.getinfo(member);data=z.read(member)
        if destination is None:
            parts=member.split('/')
            if parts[0] in (sid,'DEE_thinking_4_0_0'):parts=parts[1:]
            destination=Path('genealogia')/sid/Path(*parts)
        destination=Path(destination)
        target=ROOT/destination
        if not target.resolve().is_relative_to((ROOT/'genealogia').resolve()):raise ValueError('Selection outside genealogy')
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=data:raise FileExistsError(target)
        if not target.exists():target.write_bytes(data)
        selected.append({'file':destination.as_posix(),'source_id':sid,'source_archive':paths[sid].name,
            'archive_sha256':ident[sid]['sha256'],'member':member,'member_sha256':sha(data),
            'member_crc32':f'{info.CRC:08x}','bytes':len(data),'mode':'BYTE_EXACT_SELECTION'})
        return destination.as_posix()

    # Reuse the already-selected CPC6 genealogy routes, but verify against their
    # actual canonical source archives. No historical snapshots are duplicated.
    oldmanifest=json.loads((CASES/'trabajo_codex/CPC6/genealogia/SOURCE_MANIFEST.json').read_text(encoding='utf8'))
    for row in oldmanifest['files']:
        if Path(row['file']).suffix.lower() not in ('.py','.md','.json'):continue
        sid=next((k for k,v in paths.items() if v.name==row['source_archive']),None)
        if sid:
            take(sid,row['source_member'],Path('genealogia/historico_minimo')/Path(row['file']).relative_to('genealogia'))

    c3=['CPC3/genealogia/CP01_C08/INFORME_CIENTIFICO.md',
        'CPC3/genealogia/CP02_B/INFORME.md','CPC3/INFORME_CIENTIFICO.md','CPC3/CAPACIDADES.json']
    for n in c3:take('CPC3',n)
    for n in ['CPC4/INFORME.md','CPC4/CAPACIDADES.json',
        'CPC4/ampliaciones/02_APRENDIZAJE_CONTINUO_RED_ABCD/INFORME.md',
        'CPC4/ampliaciones/02_APRENDIZAJE_CONTINUO_RED_ABCD/RETENCION.json']:
        take('CPC4',n)
    ext='CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/'
    for n in ['src/capacity.py','src/capacity_longitudinal.py','src/capacity_access_analysis.py',
        'configuraciones/capacity_discovery.json','configuraciones/capacity_confirmation.json',
        'configuraciones/capacity_longitudinal.json','resultados/capacity_discovery/INDEX.json',
        'resultados/capacity_confirmation/INDEX.json','resultados/capacity_longitudinal/INDEX.json',
        'revision/LEER_PRIMERO.md','revision/LECTURA_PROVISIONAL.md']:
        take('CPC5',ext+n)
    for n in ['CPC5/revision/LEER_PRIMERO.md','CPC5/revision/LECTURA_PROVISIONAL.md',
        'CPC5/referencias/NSM65_CATALOGO_CPC4.json']:
        take('CPC5',n)
    for n in ['src/common.py','src/integrated.py','src/order_memory.py','src/consolidation.py',
        'src/language.py','src/order_language.py','src/life.py','src/word_bus.py',
        'src/retention_access.py','src/late_access.py','src/consolidation_controls.py',
        'src/word_bus_controls.py','src/architecture_bridge_delayed.py','src/architecture_screen.py',
        'revision/LEER_PRIMERO.md','revision/LECTURA_PROVISIONAL.md','revision/MAPA_CPC1_A_5.json',
        'resultados/RETENTION_SYNTHESIS.json','resultados/LATE_ACCESS_CALCULATIONS.json',
        'resultados/ARCHITECTURES_AND_DIALOGUE.json','resultados/referencias/REFERENCE_REPRODUCTION_CHECK.json',
        'configuraciones/R03_WORD_BUS_V2.json']:
        take('CPC6','CPC6/'+n)
    for n in ['PRODUCT_CONTRACT.json','docs/API_AND_SCOPE.md','source/include/dee_thinking/cognitive.hpp',
        'source/include/dee_thinking/informative.hpp','source/include/dee_thinking/integrated_protocols.hpp',
        'source/tests/python/test_cognitive_api.py','source/python/dee_thinking/cognition.py',
        'source/python/dee_thinking/dialogue.py']:
        take('PRODUCT4','DEE_thinking_4_0_0/'+n)
    extra={
        'ING01':['DEE_REUSABLE_FEEDBACK_LOOP.json','DEE_NATIVE_RESET_REPLENISHMENT.json',
            'REWRITE_WORK/RUNNERS/run_r04_reset_corrected_holdout.py','REWRITE_WORK/RUNNERS/run_r14_feedback_holdout.py'],
        'ING02':['ING02_TEMPORAL_HISTORY_MEMORY.json','ING02_DISTRIBUTED_MEMORY.json',
            'RUNNERS/paired_relative_apparatus_v2.py','RUNNERS/run_d09_relative_readout_longevity.py'],
        'ING05':['INGENIERIA_05/05_HISTORY_CONDITIONED_TRANSFORMATION/SCIENTIFIC_REPORT.md',
            'INGENIERIA_05/07_RECURRENT_HISTORY_CHANGE/SCIENTIFIC_REPORT.md'],
        'ING06':['INGENIERIA_06/09_ENDOGENOUS_FREE_RUN/SCIENTIFIC_REPORT.md',
            'INGENIERIA_06/12_CAUSALLY_SENSITIVE_OPPORTUNITIES/SCIENTIFIC_REPORT.md'],
        'CORE06':['LEARNING_CAUSAL_MECHANISM.md','RESULTS/C6D04_reversal_extinction_transfer.json',
            'RUNNERS/run_c6d04_reversal_extinction_transfer.py'],
        'CORE07':['LEARNING_TRANSFER.md','CANONICAL_WITNESSES/W_REPROGRAMMING.json',
            'RUNNERS/run_c7h03_reprogrammable_functional_matter.py'],
        'PROC01':['PROCESOS_01/10_HB_P2_CAUSAL_AMPLIFICATION_CHARACTERIZATION/REPORT/CHARACTERIZATION_REPORT.md'],
        'PROC02':['SCIENTIFIC_REPORT.md'],
        'PROC03':['CONTRACT.json','SUMMARY.json']}
    for sid,members in extra.items():
        for n in members:take(sid,n,suffix=(sid=='CORE06'))

    # Documentary extracts preserve whole selected chapters, not a claim of
    # layout inspection or page numbering. They are not executed source code.
    documents=[]
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for f in [PRODUCT/'DEE_thinking_4_0_0_Maestro_Arquitectura_Reconstruccion.docx',
              PRODUCT/'DEE_thinking_4_0_0_Libro_Blanco_y_Manual_Tecnico.docx',
              DOC/'FISICA DEE Y PROCESAMIENTO NATIVO/Procesamiento_Nativo_DEE_Libro_Manual_v1.docx',
              DOC/'FISICA DEE Y PROCESAMIENTO NATIVO/DEE_V4_0_1.docx']:
        data=f.read_bytes()
        with zipfile.ZipFile(f) as z:
            rootxml=ET.fromstring(z.read('word/document.xml'));pars=rootxml.findall('.//w:p',ns)
            texts=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in pars]
            heads=[]
            for i,p in enumerate(pars):
                style=p.find('w:pPr/w:pStyle',ns)
                if style is not None and style.get('{'+ns['w']+'}val')=='Heading1':heads.append((i,texts[i]))
            if 'Maestro' in f.name:
                label='MAESTRO_4_0';wanted={7,12,14,15,16,17,18,19,20,21,23,24,25,33,34,35,36,37}
            elif 'Libro_Blanco' in f.name:
                label='MANUAL_4_0';wanted={12,18,21,22,23,24,25,27,28,29,31,32,33,34,35,36,37,38}
            elif f.name.startswith('Procesamiento'):
                label='PROCESAMIENTO_NATIVO';wanted={6,7,8,9,11,12,14,15,16,17}
            else:
                label='FISICA_4_0_1';wanted={6,7,8,9,12,24,29,30}
            chapters=[]
            for j,(start,title) in enumerate(heads):
                leading=title.split('.',1)[0]
                if not leading.isdigit() or int(leading) not in wanted:continue
                end=heads[j+1][0] if j+1<len(heads) else len(pars)
                chapters.append({'heading':title,'paragraph_start_zero_based':start,'paragraph_end_exclusive':end,
                    'paragraphs':[{'index':i,'text':texts[i]} for i in range(start,end) if texts[i]]})
            capsule=[{'member':n,'bytes':z.getinfo(n).file_size,'sha256':sha(z.read(n))} for n in z.namelist() if n.startswith('dee_payload/')]
        dest=Path('genealogia/documentos')/(label+'_EXTRACTOS.json')
        put(ROOT/dest,{'source_file':f.name,'source_sha256':sha(data),'source_bytes':len(data),
            'selection':'Whole specified content chapters from OOXML; no layout/page certification',
            'capsule_members_identified_not_executed':capsule,'chapters':chapters})
        documents.append({'file':dest.as_posix(),'source_file':f.name,'source_sha256':sha(data),
            'chapters':[r['heading'] for r in chapters],'hash':sha((ROOT/dest).read_bytes())})

    rows=[]
    def row(id,source,mechanism,domain,controls,limits,question,api=None,evidence=None):
        rows.append({'id':id,'source':source,'mechanism':mechanism,'domain':domain,'controls':controls,
            'published_limits':limits,'CPC7_question':question,'API_or_code':api or [],'evidence':evidence or [],
            'state':{'reference_selected':True,'source_identity_verified':True,'reproduced_in_CPC7':False,
                'adapted_in_CPC7':False,'integrated_in_CPC7':False},
            'reproduction_rule':'Prior successful execution is not a CPC7 reproduction; a new preparation or integration needs its own measurements.'})
    cp=[
        ('C01','event-order phase latch','N47 relative body; finite two-event order','opposite, unpaired','two events, not arbitrary sequence grammar'),
        ('C02','online mobile collision calibration','N34; bounded affine/additive relation','untrained, unpaired','query payload and readout geometry constrained'),
        ('C03','passive plus physical-probe diagnosis','local relative/reader domains','full/reader absent/phase/route','diagnosis supplied by external instrument'),
        ('C04','native convergence/competition','N34 encounter windows','single source, delayed, opposition','host admission distinct from native encounter'),
        ('C05','mobile native transfer','N127 corridor','route cut, virgin source','finite route and compatible encounter'),
        ('C06','action/consequence and return','prepared action/habitat','late cut, no return, yoked','environment law external where declared'),
        ('C07','causal signature panel','complete diagnostic forks','sham and targeted cuts','auditor, not introspection'),
        ('C08','persistent communicative mobile session','finite symbols and external mod31 habitat','opposite/no history','same session within finite physical resource domain')]
    for cid,m,d,c,l in cp:row('CP01_'+cid,'CPC3/genealogia/CP01_C08',m,d,c,l,'Reuse only a relevant component; do not re-run the eight-field campaign.', ['src/fronts.py','src/sesion.py'])
    row('CP02_B','CPC3/genealogia/CP02_B','Past actual outcomes write relative memory and support a live directional forecast','N47 seed at32; finite opportunities','none/unpaired/equalized/route blocked/independent barrier change','external barrier law; fork forecasts do not imply MAIN introspection','Can a new observer use a retained relation after new experience?',['src/predictor.py'],['CPC6 three-reference reproduction record'])
    row('CPC3_MAIN_AND_COMPARISON','CPC3','Current MAIN readout; physical expectation/consequence encounter','N47; one comparison marker84; finite phase slots','opposite,H0,report omitted,barrier change','marker not a reusable new forecast','Separate current readout, expectation and later factual contrast',['CognitiveSession','core/entity.py','core/central_comparison.py','core/comparison_entity.py'])
    row('CPC3_POLICY','CPC3 and ING01_R14','Finite native keep/switch after current consequence','N67; prepared finite policy realization','unpaired/reversed/absent consequence','not general utility optimization or replenishing learning','Use only if causal policy transition is relevant to new task',['FinitePolicySession','core/revisable_selection.py','core/policy_session.py'])
    row('SEM01','CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO','Opaque cue paired with present physical consequence; later cue-alone anticipates and acts','N67; acquired17/45, queried84/112, final129','opposite assignments,unpaired,omitted cue/outcome,memory intervention,action cut','outcome sensor external; residual toroidal activity changes actual received experience','Retain acquired association under a new curriculum',['src/memory.py','src/experiment.py'])
    row('CPC4_AB','CPC4','A product travels in one Runtime and interacts with acquired relation of B','R1/R2/R3 finite windows','virgin,inverted,unpaired,channel cut,constant/changed content,sham','R1 partly solvable virgin; R2 isolates learned contribution; no unlimited renewable action','Use physical transport with an acquired receiver, not copied output',['src','ampliaciones/02_APRENDIZAJE_CONTINUO_RED_ABCD/src/red'])
    row('CPC4_REGULATION_ABCD','CPC4 ampliacion02','Four prepared regions; programmed counterflow neutralizes residual relay; relative relation persists under another experience','frozen red geometry and agendas','selective cut,offpath,virgin,opposite,sham','external timing of counterflow, distinct W1/W2 interference; assisted M2 is not autonomous recovery','Distinguish prepared regulation, native generation and history-modified use',['regulated_session.py','recipe_v3.py','session_v3.py'])
    row('CPC5_COMPOUND','CPC5 initial','Acquired mobile stages coupled physically with separately experienced backup relations','four stages73; eight stages165; bounded cadence','stage omission,path cut,backup absent,opposite direction','partitions are subcircuits, not renewable autonomous bodies; loads do not measure concepts','Compare organization and coupling without hiding extra resources',['src/compound.py','src/network.py','src/relative_compound.py'])
    row('CPC5_CAPACITY65','CPC5 ampliacion01','Distinct opaque forms in isolated z planes; actual paired collision; cyclic renewed probes','K8/16/32/65 tested; K65,N131,gap2; three queries in reference','no event,unpaired,wrong phase,new histories,Q9/Q13,translations','65 forms over two directional classes; later controls can acquire through residual/query contact','Append relations while old ones remain accessible; test any update as new candidate',['CapacitySession.create','submit','save','load','src/repertoire_reference.py'],['capacity_discovery/INDEX.json','capacity_confirmation/INDEX.json'])
    row('CPC5_LONGITUDINAL65','CPC5 ampliacion01','32 initial relations followed by33 separately experienced new relations in same world','N131,K65; round2/3 old32 and new33 all usable in reported two cohorts','early evaluation versus omitted early evaluation','additional acquisition, not arbitrary overwrite; no65 semantic classes','Preserve old function while acquiring new and distinguish query interference',['capacity_longitudinal.py'],['capacity_longitudinal/INDEX.json'])
    row('CPC5_ORDER_AND_DIALOGUE','CPC5 ampliacion01','Temporal stream; order-sensitive physical composition; finite request/reply/use network','published local worlds; 1..4 groups growth of resources','order inversion,omission,request cut,reply cut,untrained receiver','prepared order encoder differs from acquired association; finite protocol not unbounded dialogue','Acquire different relation classes without conmutative collapse of roles',['order_stream.py','ordered_composition.py','network_dialogue.py','network_session.py'])
    row('CPC6_INTEGRATED','CPC6','One new U0 combines acquired order, forecast, comparison, information and first sign','N67; same MAIN finite trajectory through170','opposite history,changed consequence,unpaired,name omission,source omission','not autonomous policy discovery; roles and resources prepared','Extend a coherent individual instead of summing unrelated apparatus successes',['src/integrated.py','src/order_memory.py','src/life.py'])
    row('CPC6_TWO_FORMS','CPC6 R03_WORD_BUS_V2','F1 first use53; F2 historical relation acquired80 and used90; renewed F1 read162 after new input117','three reserved history/content cells; finite bus supply','no117,first-name unpaired,opposite histories/content; discoveryV1 preserved','two opaque operational protocols, not two general NSM primitives; no full factorial or general bidirectional grammar','Measure retained use after another relation without hidden reset',['src/word_bus.py','src/order_language.py'],['R03_WORD_BUS_V2/WR01_BA_balanced_Qminus/MEASUREMENTS.json'])
    row('CPC6_RETENTION_CAUSAL','CPC6 retention/consolidation controls','Renewed access and causal forks separate memory scalar, reader, context and cue','early97 scalar necessity; late162 scalar alone not necessary; late original-history access110/111','same-clock equalization,physical cue cut,shams,noquery; MAIN unchanged','no unique memory localization; missing local readout not proof of destruction','Diagnose retention vs accessibility before declaring loss',['src/consolidation_controls.py','src/word_bus_controls.py','src/retention_access.py','src/late_access.py'])
    row('CPC6_ARCHITECTURES','CPC6 architectures','Physical message->comparison->action->information->later use in one/two/four prepared groups','last-method boundaries30/75/80/83/93; values110/117/145/168/175 are loads','path and component controls,late cuts,constant-resource opportunities where matched','three-group independent preparation not run; growing resources not pure architecture advantage','Compare common-task retention and access with explicit resource differences',['src/architecture_screen.py','src/architecture_bridge_delayed.py'],['resultados/ARCHITECTURES_AND_DIALOGUE.json'])
    row('CORE06_RELEARNING','CORE06 C6D04','Ordinary reset carrier followed by paired retraining changes mobile route','N47; train4,reset12,retrain15,query24; discovery','no retrain,history shuffled,matched exposure,old-channel comparison','not the same plus/minus CapacitySession lane and not confirmed arbitrary overwrite','Candidate precedent only; new geometry must be verified',['run_c6d04_reversal_extinction_transfer.py::run_reversal'])
    row('CORE07_REPROGRAMMING','CORE07 C7H03','Positive native update and zero-load redirection revise additive response','frozen four cells,48 positives,96 negatives','programmer missing/offpath,memory cut,state/clock nuisances,damage controls','all training/programming carriers prepared atT0; not arbitrary online learned utility','Bounded native revisions, distinct from external state copying',['run_c7h03_reprogrammable_functional_matter.py','run_reusable_revision'])
    row('ING01_R04_R14','ING01','Replenished oscillator separately from finite consequence-driven policy','R04 fixed semantic4 grammar; R14 finite action/consequence/policy','source missing,finite source,wrong writer; consequence controls','renewal and learning not already integrated in one unlimited learner','Do not relabel replenishment as retention of a learned perturbation',['run_r04_reset_corrected_holdout.py','run_r14_feedback_holdout.py'])
    row('ING02_RELATIVE','ING02','Supported pair stores differential increment; renewed midpoint readout; temporal bank','finite phase apparatus; zero-payload two-event order; eight distributed relations','H0,opposite chronology,phase and no-reader controls','absolute load threshold can fail while relation persists; address placement external','Native relation/readout alternatives when mobile port occupancy blocks use',['paired_relative_apparatus_v2.py','run_d09_relative_readout_longevity.py'])
    row('ING05_06_CONTEXT','ING05/ING06','Same new experience transforms a history-conditioned landscape; free evolution changes diagnostic reachability','fresh N19/N25 and frozen H0/HA/HB configurations; host-stop4 windows','factorial W00/W10/W01/W11; separated routes; omissions; common diagnostic challenges','native evolving causal state, not automatically autonomous useful function or new contingent experience','Use a functional task to test which historical distinction remains accessible')
    row('PROCESOS_OBSERVERS','PROC01/PROC02/PROC03','Observer-dependent visibility; preexisting component changed by history-dependent front; calibrated finite exchange studies','individual frozen apertures,fronts and contact windows','matched omission,fresh symmetries,diagnostic clones; component/backaction control','counts/support alone miss functional change; diagnostic reinstantiation not spontaneous MAIN action; finite flux not universal temperature','Calibrate observers and keep future-relevance separate from raw distinction')
    row('PROCESAMIENTO_NATIVO','Documentary manual, selected whole chapters','Mechanistic synthesis of mobile acquisition, finite reprogramming, separated fibers, relative memory and renewed reading','Each cited original apparatus keeps its own dimension, phase and resources','Source-specific causal controls; observer versus physical query separated','Documentary synthesis is not a new executable proof or a shared universal representation','Select the source mechanism, then test the new coupling',['genealogia/documentos/PROCESAMIENTO_NATIVO_EXTRACTOS.json'])
    row('FISICA_META_ROSETTA','Fisica DEE4.0.1, selected whole chapters','Observer-dependent predictive equivalence, operational persistence and information retained by a projection','Theorem, executed apparatus and external correspondence remain distinct','Compare future-relevant signatures and explicit interventions within a frozen panel','A cluster or equal scalar does not imply functional equivalence; no claim of external-universe identification from native data','Use multiple observers and causal controls, not scalar output alone',['genealogia/documentos/FISICA_4_0_1_EXTRACTOS.json'])
    row('PRODUCT4_CONTRACT','PRODUCT4 and Maestro/Manual4.0','One frozen v27 implementation with declared construction,experience,probe,observation,diagnostic and persistence layers','recipes N31/34/47/127 differ; research representability not functionality guarantee','public suites and explicit domains; prior release status is historical evidence','CPC7 does not modify product; Python may coordinate but not calculate native answers','Use research interfaces and correct lifecycle, receipts and checkpoint loaders',['OrganizationalWorld','InterfaceSpec','CognitiveSession','NativeAssociationSession','NativeInformationSession','FinitePolicySession'])

    module=ROOT/'src/repertoire_reference.py'
    copied={'source_id':'CPC5','member':'CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/src/capacity.py',
        'source_sha256':'6440f93a9760ddc7abcb73451fdb3dc1e18c646c168f82f036a50207755fd6e8',
        'destination':'src/repertoire_reference.py','copied_verbatim_before_adaptation':True,
        'destination_sha256_at_inventory':sha(module.read_bytes()),
        'status':'VERBATIM_MODULE_AVAILABLE_NOT_A_NEW_NATIVE_RESULT'}
    kernel_member='DEE_thinking_4_0_0/source/src/kernel_v27.cpp'
    with zipfile.ZipFile(paths['PRODUCT4']) as z:kernel_hash=sha(z.read(kernel_member))
    wheel=PRODUCT/'dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
    with zipfile.ZipFile(wheel) as z:
        pyd=[n for n in z.namelist() if n.endswith('.pyd')]
        if len(pyd)!=1:raise ValueError('Ambiguous native binary')
        pyd_hash=sha(z.read(pyd[0]))
    instrument={'version':'4.0.0','wheel_sha256':sha(wheel.read_bytes()),'pyd_sha256':pyd_hash,
        'kernel_source_sha256':kernel_hash,'kernel':'v27 frozen','native_execution_performed_by_this_inventory':False}
    assert instrument['wheel_sha256']=='17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
    assert instrument['pyd_sha256']=='20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
    assert kernel_hash=='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
    put(ROOT/'genealogia/SOURCE_MANIFEST.json',{'schema':'CPC7.selected_genealogy.v1','archives':identities,
        'selected_members':selected,'documentary_extracts':documents,'module_copy':copied,
        'missing_requested_members':missing,'selection_bytes':sum(r['bytes'] for r in selected),
        'historical_mains_executed':False,'source_originals_modified':False})
    put(ROOT/'revision/MAPA_CPC1_A_6.json',{'schema':'CPC7.genealogy_map.v1','instrument':instrument,
        'archives':identities,'rows':rows,'source_manifest':'genealogia/SOURCE_MANIFEST.json',
        'module_copy':copied,'documentary_extracts':documents,
        'coverage_notes':[
            'CP01/C01-C08 and CP02-B are recovered inside canonical CPC3; no separate current CP01/CP02 ZIP was found in the cases root.',
            'CP02-A is not present in the CPC3 genealogy inventory selected here; it is not invented or marked reproduced.',
            'CPC6 already reproduced CP02-B, CPC3 comparison and SEM01 with complete RAW/clocks/tick equality; those are prior results, not CPC7 executions.',
            'CPC6 source inventory has129 scientific records; technical attempts are distinct; CPC7 does not relabel them independent new samples.',
            '65 forms/two physical classes, two opaque protocols, and65 NSM entries are three different counts.',
            'Statuses reference/adapted/integrated/reproduced are independent. Initial map states do not certify current campaign execution.',
            'No old runner main or cleanup script was executed; no ZIP, product or Word source was modified.'
        ],'pending':['Record CPC7 native reproductions and changed integrations from their own measurements before promoting any status.']})
    print(json.dumps({'archives':len(identities),'selected_members':len(selected),'selected_bytes':sum(r['bytes'] for r in selected),
        'map_rows':len(rows),'missing':missing,'instrument':instrument},ensure_ascii=True))

if __name__=='__main__':main()
