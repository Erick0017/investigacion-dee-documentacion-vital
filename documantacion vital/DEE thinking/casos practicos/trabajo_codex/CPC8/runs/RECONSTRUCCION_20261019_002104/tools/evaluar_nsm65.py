"""Root-authored bounded interpretations, NOT score-to-meaning automation.

Six bounded candidate interpretations below were selected from primary review. The code
only formats those explicit judgments and checks catalogue identity. It never
feeds words, targets, meanings or evaluator decisions back to a participant.
Dimensions and levels are not forced into a single intelligence percentage.
"""
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def ref(p,loc):
 f=ROOT/p;return{'path':p,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'locator':loc}
def write(name,v):(ROOT/'revision'/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def dim(state,scope,evidence=()):return{'estado':state,'dominio':scope,'evidencia':list(evidence)}
def run():
 cat=read('referencias/NSM65/NSM65_CATALOGO_4_5.json');plan=read('configuraciones/NSM65_PLAN_INICIAL_FIJADO.json');assert len(cat['entries'])==65 and len({x['id']for x in cat['entries']})==65
 plans={x['id']:x for x in plan['entries']};claims={}
 iue=ref('resultados/integracion/IUE_P01_RETURN_USED_PLUS/MEASUREMENTS.json','frames/order31_165/common206/joint281_348_415_549, windows and exact requests')
 cts=ref('resultados/transferencia_magnitud/MCTS_P01_SOURCE31/MEASUREMENTS.json','Selected fresh MAIN; frames/renewal/contact_social_observations340_411_478_484_487_554_559_563; requests; magnitude transfer80_147_214_281')
 ctsa=ref('resultados/semantica/CONTACT_SOCIAL_E1_ANALYSIS.json','central paired opposite-route histories, controls, reserveR31 and adverseR32; fixed decoders')
 lce=ref('configuraciones/integracion/LONGITUDINAL_E1_CONFIRMATORY_FROZEN.json','predeclared decoders and reserves; wholeworld histories, not within-individual novel word transfer')
 ot=ref('resultados/integracion/ORDER_ACCESS_LECTURA.json','late re-acquisition diagnosis; selective portcut/sham and alternate reader')
 q=ref('revision/CANTIDAD_ADQUIRIDA.json','actual acquired reference, new object comparisons, additiveupdate and48native branch reconstructions')
 qfm=ref('revision/CANTIDAD_FORMA_Y_ACCESO.json','three reads of FIRSTcomparison association at140/207/274, opposite history, omission/unpaired, memorycut/sham/restore')
 mt=ref('revision/TRANSFERENCIA_MAGNITUD.json','Actual E1backup experience→native36message→recipient reference80→new current objects147/214/281; opposite history/cut/sham and no local recipient reference teacher')
 sp=ref('resultados/semantica/ANALYSIS.json','mode/spatial acquired reference and novel objects; native message, Bquery/context/delivery controls')
 spnote=ref('revision/RELACIONES_Y_COMUNICACION.md','declared component/coordinate frame, fixed decoders, actual-position sensors and reserve scope')
 count=ref('resultados/semantica/CONTACT_CARDINALITY_ANALYSIS.json','21 physical preparations, one preRuntime rejection, F1/F2/F3, 84 snapshot hashes, actual contact-unit accumulation and adverse dose challenge')
 countnote=ref('revision/CONTACTOS_UNIDADES_NORMALIZADAS.md','Frozen calibration at10/77/144; contact A/B versus both; NONE not retained at144; two technical restores')
 csign=ref('revision/COUNT_SIGN_Y_COEXISTENCIA.json','Three bounded access families, unit2prepared threshold8, acquired form94; original readers114/148 fail for A-only/TWO but pass for B-onlyG13/G31; matched G51/G52/D31/D32 omitted/unpaired/cut/sham controls; D21-D27fixed both-bank alternative readers/cuts/shams afterexperience100; CNMfreshcoexistence')
 csignnote=ref('revision/COUNT_SIGN_Y_COEXISTENCIA.md','Single identical opaque cue5 across separate one/two histories, not two acquired names; all27preparations/11forks in38primaries and4preRuntime failures retained')
 claims['NSM65.BEFORE']={
  'nivel_resumen_conservador':'E2','dimensiones_adicionales_medidas':['E4'],'estado_global_de_la_candidata':'Ejecutado parcial',
  'alcance':'Order of two actual events in a prepared relative body, preserved in a physical Xsignature and later combined with a contact consequence. Not a date variable or arbitrary temporal language.',
  'A':dim('Ejecutado positivo','Actual AB/BA event order changes later physical function under fixed encoder/decoder',[iue,lce]),
  'B':dim('Ejecutado positivo','Relative history and route-dependent native emission, no taught answer bit',[iue]),
  'C':dim('Ejecutado positivo','Order-sensitive component re-expressed31/165 and contributes common206',[iue]),
  'D':dim('Ejecutado positivo','Subsequent opaque association11 and composite214; temporal teaching and later read use declared different transduction phases, not a claim of arbitrary lexical binding',[iue]),
  'E':dim('Ejecutado positivo','Earlier order component remains in composite queried after additional acquisitions549/616',[cts]),
  'F':dim('Ejecutado parcial','Wholeworld state/dose reserves positive, but within-life later AB/BA re-acquisition collapses at original reader. No strong transfer of an old temporal word to new referents',[lce,ot]),
  'G':dim('Ejecutado positivo','Separate acquired order/contact products physically compose206 and affect use210, before complete composite form is taught214',[iue,cts]),
  'H':dim('No ejecutado por dominio documentado','Contact is communicated in CTS, not the temporal relation; do not infer BEFOREcommunication from another content',[ctsa]),
  'I':dim('Ejecutado positivo','Part of continuing CTSfreshE1, not imported trained memory',[cts]),
  'J':dim('Intervención externa explícita','Relative-body preparation, guidephases, sources/readers/cue opportunities remain researcher-designed',[lce]),
  'E3_no_acreditado_como_generalidad_semantica':True,'E4_dominio':'Native ordered contact composition, not full grammar','limite':'No independent AFTERprime association or general role-binding is credited.'}
 claims['NSM65.TOUCH']={
  'nivel_resumen_conservador':'E2','dimensiones_adicionales_medidas':['E4','E5'],'estado_global_de_la_candidata':'Ejecutado parcial',
  'alcance':'Acquired and sign-associated consequence of an actual physical actuator/opportunity/medium contact versus equal-resource off-route history; not damage or all human senses of tocar.',
  'A':dim('Ejecutado positivo','Actual contact versus same material on an off-route trajectory changes the native medium Zcomponent',[cts,ctsa]),
  'B':dim('Ejecutado positivo','History material persists, then re-expresses Z0/contact orZ−1/free in fixed readout',[cts]),
  'C':dim('Ejecutado positivo','Acquired contact contributes common206 and later contact accesses411/478; recipient uses content559/563',[cts]),
  'D':dim('Ejecutado positivo','Cue follows the physical function; same stimuli to all candidatebanks. Complementary registration/read phases are prepared, not arbitrary-dictionary generality',[cts]),
  'E':dim('Ejecutado positivo','Old combined association retained while new contact episode is acquired; new contact associated344 and reused411/478; recipient487→554 without retransmission',[cts]),
  'F':dim('Ejecutado parcial','One wholehistory reserve passes, another current-free history expresses oldcontact atA411 despite admitted queries. New episode with a new cue is new acquisition, not proof that an old sign generalized without pairing',[ctsa]),
  'G':dim('Ejecutado positivo','Native order/contact common206 and consequence210; roles/axes are explicit and not replaced by scalar load',[cts,iue]),
  'H':dim('Ejecutado positivo','Acquired source use484→physicalmessage486→new recipient memory487→query554→contextual material use559→delivery563; cut/sham/cue/noquery controls',[cts,ctsa]),
  'I':dim('Ejecutado positivo','Central CTS E1 retains preceding quantity/MODE/question/commonword functions in the same life',[cts,ctsa]),
  'J':dim('Intervención externa explícita','All geometry/readers and two fixed zero-load residual counterflows are prepared/programmed; no autonomous regulator policy or spontaneous destination selection',[ctsa]),
  'E3_no_acreditado_como_generalidad_semantica':True,'E5_dominio':'Local contact-consequence communication to a simple recipient, not a second complete mind or universal TOUCHmeaning','limite':'R32 is a valid adverse boundary before the channel, not omitted from score.'}
 claims['NSM65.MORE']={
  'nivel_resumen_conservador':'E2','dimensiones_adicionales_medidas':[],'estado_global_de_la_candidata':'Ejecutado parcial',
  'alcance':'Relative material magnitude with a physically acquired reference and prepared native gradient. A subsequent opaque sign names a PARTICULAR past comparison outcome. The comparison rule itself is not learned here.',
  'A':dim('Ejecutado positivo','Actual reference quantity and later addition alter physical reference; current objects are payloads, not class labels',[q,cts]),
  'B':dim('Ejecutado positivo','Moving magnitude acquired by actual postT0 encounters; omission/unpaired histories differ',[q]),
  'C':dim('Ejecutado positivo','Stored magnitude is used on newly presented values; valid active-zero comparison is distinguished from emptyRAW',[q,cts]),
  'D':dim('Ejecutado positivo','AuxiliaryQFM: post-function cue72, later cue-only140/207/274 re-express FIRSTcomparison history, not current object labels',[qfm]),
  'E':dim('Ejecutado positivo','AuxiliaryQFM retains named past outcome during further actual object and independent auxiliary experiences; E1 retains numeric reference after other acquisitions',[qfm,cts]),
  'F':dim('Ejecutado parcial','Acquired numeric operand transfers to new magnitudes on a prepared comparator; this does not show the learned word MORE classifying new relations without pairing',[q]),
  'G':dim('Ejecutado parcial','Quantity comparison gates a request whose acquired source content changes later use; no fully lexical MOREcomposition with preserved arguments is shown',[cts]),
  'H':dim('Operando adquirido comunicado; significado general MORE no demostrado','A separately experienced E1backup reference36 travels natively and teaches a recipient which compares new actual objects. This is useful acquired numeric-reference communication, not automatic acquisition of the abstract MOREprime',[mt,cts]),
  'I':dim('Integrada con limitaciones','Reference/actual comparisons are in E1; the newly renewed QFMwordreader is a separate world and not added as E1knowledge',[cts,qfm]),
  'J':dim('Intervención externa explícita','Gradient/supports/format5, counterflows or guards and finite remote readers are prepared. Remote QFMtargets follow declared geometry, not learned reader selection',[q,qfm]),
  'E3_no_acreditado_como_generalidad_semantica':True,'limite':'Three QFMword reads are not three newly generalized object classifications; do not convert magnitude into number-of-objects, energy, GOOD, BIG or identity.'}
 claims['NSM65.LIKE_AS']={
  'nivel_resumen_conservador':'E2','dimensiones_adicionales_medidas':['E5'],'estado_global_de_la_candidata':'Ejecutado parcial',
  'alcance':'Likeness/difference of a declared motion or positioned-gradient component relative to an acquired reference, not referent identity or the full range of como.',
  'A':dim('Ejecutado positivo','Opposite acquired reference histories with fixed current object observation change the native relational vector',[sp,spnote]),
  'B':dim('Ejecutado positivo','Reference from actual earlier observations; no classifier labels supplied as target',[sp]),
  'C':dim('Ejecutado positivo','New actual object directions/states/doses or positioned objects meet the earlier reference',[sp]),
  'D':dim('Ejecutado positivo','B learns a later opaque cue through actual native message encounters; exact same Bform can be queried alone',[sp]),
  'E':dim('Ejecutado positivo','In E1MODE, recipient acquired160 first queried428; auxiliarySPX also preserves through later context and restore',[cts,sp]),
  'F':dim('Ejecutado positivo en dominio operacional limitado','The SAME acquired component reference is used on a new second physical object after an extra experience110, without reteaching that reference. Frozen wholeworld reserves vary actual directions/states/doses/positions. This is component-level operational transfer, not unrestricted semantic transfer of the word COMO to arbitrary referents',[sp,spnote]),
  'G':dim('Ejecutado parcial','Received component plus actual physical context changes use, but broad composition of independently learned semantic relations is not established',[sp]),
  'H':dim('Ejecutado positivo','Native sender-dependent component teaches B, which queries and uses received information; cuts/omission/equal-charge-content and physical-context controls isolate content',[sp,spnote]),
  'I':dim('Integrada con limitaciones','MODEmotion component is in CTS; richer positionedSPX apparatus only partially coexists in fresh E1 candidates, not all549 functions',[cts,spnote]),
  'J':dim('Intervención externa explícita','Reference format/comparison/sensors/candidate banks/queries/context windows are researcher-prepared',[spnote]),
  'E3_no_acreditado_como_generalidad_semantica':True,'E5_dominio':'Component-level useful communication in declared frame; not identity THE_SAME or full human simile','limite':'Do not label multiple identical copies as independent learners.'}
 for prime,units in [('NSM65.ONE',1),('NSM65.TWO',2)]:
  claims[prime]={
   'nivel_resumen_conservador':'E2'if units==1 else'E1','dimensiones_adicionales_medidas':[],'estado_global_de_la_candidata':'Ejecutado parcial: asociación operacional y reutilización auxiliar B-only'if units==1 else'Ejecutado parcial: asociación operacional con acceso sólo asistido',
   'alcance':f'Native accumulation/reuse of {units} normalized contact unit(s). The prepared material calibration, not a learned invariant number category, determines this local quantity.',
   'A':dim('Ejecutado positivo limitado','Actual zero-load actors contact fixed unit-load sensory media; all histories retain both media and material budget. No host input contains the contact count',[count,countnote]),
   'B':dim('Ejecutado positivo limitado','One-contact A or B versus both-contact history changes a persistent material quantity; fixed normalizers remove the free-path bypass',[count]),
   'C':dim('Ejecutado positivo limitado','Same fixed readers recover one versus two contributions at77/144; identity of A/B changes X but not this calibrated quantity',[count]),
   'D':dim('Asociación operacional causal parcial; no dos nombres numéricos','A later auxiliary unit2 apparatus turns actual count-derived7/9 against prepared8into−/+X91; identical opaque cue5 subsequently creates12at94. One form in different histories, not separate ONE/TWOlexemes in one individual. No automatic primitive attribution from two directions',[csign,csignnote]),
   'E':dim('Ejecutado positivo limitado en B-only; asistido en A-only'if units==1 else'Parcial: conservación causal con acceso asistido, lectores originales0/2','OriginalF3one/two distinction is usable after exposure100; zero notretained144. '+('Unit2B-onlyG13 and state-reserveG31 recover the ONEcandidate sign with ORIGINAL readers114/148 afterexperience100; matched B-only noform/unpaired0/2, original-readercut0/2 versus sham2/2. A-onlyoriginalreaders0/2.'if units==1 else'Unit2TWO G12/G32 original readers114/148 fail0/2. Fixed BOTH-route diagnostic readers recover the positive sign afterexperience100; actualmemorycut abolishes that assisted reading, sham preserves it. This is not original operative access or E2TWO.')+' No branches returned to MAIN',[count,countnote,csign]),
   'F':dim('Parcial en papel/estado; no generalidad numérica de dosis'if units==1 else'No transferencia positiva de TWO con el lector original','B-only and reserved B-only states pass frozen original word readers; this is ONEcandidate evidence only, unlike A-only/TWO. Success B-only was recognized exploratorily; later matched causal controls confirm it, not a retrospectively modified decoder or E3semantic claim. TWOreserveG32 retains original-reader failure; no successful TWOsemantic transfer is borrowed from B-only. Originalunit1actorload3 gives4units/contact; newunit2calibration/threshold8 are prepared, not dose-invariant cardinality',[count,csign]),
   'G':dim('No ejecutado para la primitiva','Contact contributions combine natively, but no composition of independently learned numeric semantic forms was tested',[count]),
   'H':dim('No ejecutado','No communication of an acquired ONE/TWO relation in this auxiliary experiment',[count]),
   'I':dim('No integrado en MAIN seleccionado','Separate count/sign worlds. Two new CNMfreshMCTS+F3worlds preserve earlierMCTSfunctions616 and count10/77, but losecount144. They are not the selectedMCTS or a joint learned lexicon',[count,csign]),
   'J':dim('Intervención externa explícita','OriginalF3six initial records/unit1; final sign apparatus changes to unit2, prepared threshold8 and fixed alternative diagnostic readers. These resources are not free cognitive discoveries',[countnote,csignnote]),
   'shared_contrast_not_two_independent_words':'One identical cue5 in SEPARATE worlds. No claim that an individual acquired two distinct numeric names or both meanings together. B-only success selected exploratorily with fixed readers; subsequent matched controls documented separately.',
   'native_positive_not_lost_by_partial_semantics':'A normalized contact-unit threshold distinction has a causal post-function sign association. B-only operative reuse supports restrictedE2; TWOhas causal association and diagnostic access only, restrictedE1. These are candidate evidence scopes, not full numeric semantic mastery.',
   'limite':'ONE/E2is only the B-only calibrated contact-counter/threshold domain, not universal cardinality. TWO/E1has no successful original operative word access. Neither belongs to selectedMAIN; planned dose/type generalization and a joint differentiated lexicon remain incomplete.'}
 dimensions={'A':'Experiencia causal','B':'Relación física adquirida','C':'Función posterior dependiente de historia','D':'Asociación física con señal','E':'Retención tras experiencias adicionales','F':'Generalización reservada','G':'Composición','H':'Comunicación','I':'Participación en E1','J':'Dependencia del diseñador/instrumento'}
 evidence=[];operational=[]
 for c in cat['entries']:
  p=plans[c['id']];o={'id':c['id'],'grupo':c['grupo_documental'],'forma_es':c['forma_es'],'glosa_inglesa_id':c['glosa_inglesa_id'],'variantes':c.get('variantes_documentadas',[]),'fuentes':c['fuentes'],'pregunta_experimental':p['operational_question'],'relacion_candidata':p['operational_candidate'],'experiencias':p['experiences_before_label'],'familia':p['shared_mechanism_family'],'participantes_y_relaciones':p['participants_and_relation'],'interacciones_y_recursos_por_disenar':p['preparation_vs_acquisition'],'controles':p['minimal_controls'],'senal':'Arbitraria física fijada por configuración ejecutada; no se deriva de la palabra española','retencion':p['retention_test'],'reserva':p['reserved_generalization'],'composicion':p['composition_test'],'comunicacion':p['communicative_use'],'bloqueo_concreto_inicial':p['concrete_local_blocker']};operational.append(o)
  if c['id']in claims:e={'id':c['id'],'forma_es':c['forma_es'],**claims[c['id']]}
  else:
   blocker=p['concrete_local_blocker'];e={'id':c['id'],'forma_es':c['forma_es'],'nivel_resumen_conservador':'E0','dimensiones_adicionales_medidas':[],'estado_global_de_la_candidata':'No ejecutado en esta campaña: preparación/representación local pendiente, no imposibilidad v27','alcance':p['operational_candidate'],'bloqueo_concreto':blocker,'por_que_no_extrapolar':'Related native operations may exist, but this entry lacks its own acquired relation/sign/contrasts. The missing trial is explicit, not a universal impossibility of v27.',**{k:dim('No ejecutado para esta primitiva','Requires '+p['reserved_generalization']+' and its own causal/retention contrasts; no inherited positive copied from a neighboring prime')for k in dimensions}}
  support={
   'NSM65.SAY':('Native acquired-content emission/transmission is executed, not an acquired general meaning SAY',[cts,mt]),
   'NSM65.WORDS':('Physical opaque-form association and later query are executed, not a learned metalinguistic category WORDS',[cts,qfm]),
   'NSM65.KNOW':('Acquired versus omitted information changes functional access/use; no acquired self/other epistemic predicate KNOW is demonstrated',[cts,mt]),
   'NSM65.DO':('Actual actuator contact and consequence are executed; no acquired transferable agency predicate DO is demonstrated',[cts,ctsa]),
   'NSM65.MOVE':('Actual transported observations/carriers participate; not an independently acquired linguistic movement relation',[cts,sp]),
   'NSM65.IF':('Prepared comparison-conditioned request is executed; the conditional rule itself is not acquired as a general IFoperation',[cts])}
  if c['id']in support:e['related_native_operation_executed_not_this_semantic_prime']={'scope':support[c['id']][0],'evidence':support[c['id']][1],'does_not_raise_summary_level':True}
  e.update(semantic_equivalence_to_full_human_prime_demonstrated=False,linguistic_reference_is_not_participant_memory=True);evidence.append(e)
 assert {x['id']for x in evidence}=={x['id']for x in cat['entries']}
 source={'catalogue_path':'referencias/NSM65/NSM65_CATALOGO_4_5.json','catalogue_sha256':hashlib.sha256((ROOT/'referencias/NSM65/NSM65_CATALOGO_4_5.json').read_bytes()).hexdigest(),'reference_scope':cat['source_scope'],'initial_operational_plan':'configuraciones/NSM65_PLAN_INICIAL_FIJADO.json','initial_plan_sha256':hashlib.sha256((ROOT/'configuraciones/NSM65_PLAN_INICIAL_FIJADO.json').read_bytes()).hexdigest()}
 write('NSM65_CATALOGO_Y_OPERACIONALIZACION.json',{'schema':'CPC8R.NSM65.operationalization.v2','count':65,'source':source,'entries':operational,'all_questions_are_evaluator_questions_not_answers_supplied_to_entity':True})
 write('NSM65_EVIDENCIAS.json',{'schema':'CPC8R.NSM65.authored_evidence.v2','count':65,'source':source,'independent_dimensions':dimensions,'level_rule':'Conservative summaryE2 means causal association/conservation/use in the declared limited operationaldomain AND identified individual. Separate E4/E5 evidence can exist while E3semantic generalization remains partial; E5does not silently fill other dimensions. MOREwordretention is auxiliaryQFM; ONE/E2is auxiliary B-only original-reader retention and TWO/E1is separate assisted-only access with the SAMEcue, not two joint names. SomeMODEsign evidence belongs to simpleB, not all toE1. Never sum repertoires across these lives. No score-to-meaning automation.','entries':evidence,'interpretation_author':'Codex root investigator, from explicitly reviewed primary controls, not the participant','complete_human_semantic_mastery_asserted':False})
 counts=dict(Counter(x['nivel_resumen_conservador']for x in evidence));write('NSM65_ESTADOS_POR_PRIMITIVA.json',{'schema':'CPC8R.NSM65.states.v2','count':65,'conservative_level_counts':{k:counts.get(k,0)for k in('E0','E1','E2','E3','E4','E5')},'additional_dimensions_not_cumulative':{k:[x['id']for x in evidence if k in x['dimensiones_adicionales_medidas']]for k in('E4','E5')},'states':[{'id':x['id'],'forma':x['forma_es'],'summary':x['nivel_resumen_conservador'],'additional_measured':x['dimensiones_adicionales_medidas'],'state':x['estado_global_de_la_candidata'],'full_human_meaning':False}for x in evidence],'why_not_a_single_mastery_percentage':'Levels summarize restricted domains/individuals with unresolved semantic transfer. Six candidate entries include a shared contact threshold contrast/signal in separate worlds, not six full meanings or a joint E1lexicon.65catalogued forms are not65acquired relations.'})
 print(json.dumps({'catalogue_entries':len(evidence),'conservative_counts':counts,'additional':{k:[x['id']for x in evidence if k in x['dimensiones_adicionales_medidas']]for k in('E4','E5')}}))
if __name__=='__main__':run()
