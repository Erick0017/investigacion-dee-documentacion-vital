"""Initial capability contract; final status requires attached executed evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
base=read(ROOT/'evidence/product40/PRODUCT_CONTRACT.json');rows=[]
for old in base['capabilities']:
 rows.append({'id':old['id'],'name':old['name'],'origin':'PRODUCT40','origin_archive_sha256':'c78609a7d0d501324324408ed955f60f127965c77efbcbe3b3d04fc14dbb16cf',
  'state_4_0':old['technical_status'],'posterior_contribution':'No silent replacement; inherited API and geometry retained',
  'mechanism':old['operation'],'domain':old['domain'],'protocol_horizon':'Inherited finite contracts; actual test coverage reported separately',
  'resources':'Unchanged inherited resources; new optional sessions do not affect direct Runtime',
  'modality':old['modalities'],'api_4_5':old['API'],'positive_reference':old['experimental_sources'],
  'control':'Inherited tests and 4.0/4.5 neutral differential','reserve':'Frozen Runtime seeds and recipe configurations, not a new cognition claim',
  'planned_status':'ya existente y conservada','final_status':'PENDING_EXECUTION','evidence':[]})
new=[
 ('C10','Repertorios1–65','src/repertoire_reference.py','Native prepare_repertoire; RepertoireSession','N31..151; K1..65; plane_gap>=2 and gap*K<=N; separated toroidal planes','Paired signal5/event11; query afterN,2N,3N;65forms are two directional classes','CAP_H65_NEW_HISTORY_Q9','no_event;unpaired','Q13/new history','función nueva publicada'),
 ('C11','Adquisición acumulativa32+33','genealogia/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/src/capacity_longitudinal.py','RepertoireSession.acquire_block/query','N131,K65,gap2;32then33; no reset','Published longitudinal cadence, old/new panels and continuation','CAP_L65_32_THEN33','omit early query / no teaching controls','opposite history and reserved probe payload','implementación ampliada'),
 ('C12','Revisión selectivaM1/M2','src/update_methods.py','Native revise_form; RepertoireSession.revise','Declared selected form, prepared auxiliary ports; not arbitrary unlimited rewrites','M1extra teacher11; M2two zero-load counterflows; finite cadences','UP_M1_P11/UP_M2_P11; DIRECT paired','auxiliary offpath, same dose','reserved101/211','función nueva publicada'),
 ('C13','U0 continuo con acceso propio','src/integrated_public.py','Native prepare_integrated_u0; IntegratedSession','N67;16opaque banks;21initial objects/69interfaces guarded revision realization','T0..472; order0/1,forecast5,actual11,comparison15,question19,memory70,use72,name75/read142,newblock134,panels204/338,revision402/contact405/read472','IR_P01_GUARDED_M1','IR_C02_AUX_OFFPATH; source/opposite/unpaired; message cut/sham','IR_R607_GUARDED_M1','función nueva publicada'),
 ('C14','Pregunta por discrepancia','src/endogenous/comparison_need.py','IntegratedSession / native comparison preparation','Prepared comparison, learned order emission; no general learned choice of source','Finite opportunity; equal vs discrepancy; same Runtime transport','CPC7comparison_need','equal; reader absent; source untrained; message cut/sham','BA/translation/new source content','implementación ampliada'),
 ('C15','Ausencia en ventana física','src/endogenous/comparison_need_v2.py','Separate experimental recipe, not silently integrated withU0','Prepared missing-actual aperture, N67','Own v2finite cadence; not a Python timeout detector','comparison_need_v2 cases','matched; no source; reader failure','BA/translated history','receta experimental distribuida'),
 ('C16','Regulación preparada/interferencia','src/residue_regulation.py','IntegratedOptions.guard_mode; declared resources','N67six static semantic4 interceptors; matched offpath sham','Preserves14queries204/338; no external MAIN cleanup','IR_P01_GUARDED_M1','IR_C01_OFFPATH_GUARDS; diagnostic cut/sham','IR_R607_GUARDED_M1','función nueva publicada'),
 ('C17','Calibración de suministro corporal','src/endogenous/body_source.py','IntegratedOptions.body_source_load','Initial source load0 vs7, not an acquired homeostatic decision','First emission equal; second reader still occupied; direct law unchanged','two source-only calibration preparations','matched inventory except declared initial load','Do not extrapolate beyond measured finite horizon','receta experimental distribuida'),
 ('C18','Composición direccional/orden','src/order_memory.py','IntegratedSession; inherited scalar cascade retained','Prepared order body AB/BA and branch/content/use axes; roles not arbitrary grammar','X/Ycontrasts70; X/Y/Z72; post-sign losesXdirection but retains physical bank','CPC7 four branch/content contrasts','reverse order; opposite learned content; cut request','reservedBA/new directional contents','implementación ampliada'),
 ('C19','Lectura remota renovada','src/action_feedback_access.py','RemoteReaderSession experimental adapter','CPC6 apparatus and geometry; no inherited general autonomous question','First association; second acquisition; later common remote reader','CPC6 remote access includingT117','no teaching; no new request; reader cut','finite alternate contents/history','receta experimental distribuida'),
 ('C20','Signo posterior a función','src/selective_native.py','IntegratedSession.teach_form/query_form','Fixed cue transport; online physical association; not arbitrary dictionary','Use72 precedes association75; sign-only query139/read142','paired name after native use','name omitted; cue+1tickunpaired','opposite bank content/query17/19','implementación ampliada'),
 ('C21','Persistencia exacta y compresión','src/snapshot_storage.py','Native snapshots plus bounded JSON session metadata; gzip adapter','Runtimev1/v2 and explicit session schemas; reject unknown geometry; no pickle','Queue/receipt/cursor retained; new interaction in another process; lossless CRC+SHA','CPC7demo03/CPClegacy selected checkpoints','truncated/corrupt/oversizedgzip; no recreation onload','Unicode/spaces and pending queues','implementación ampliada'),
 ('C22','CatálogoNSM65 con evidencia','genealogia/CPC5/referencias/NSM65_CATALOGO_CPC4.json','Packaged resource and evidence ledger only','Exact65documented entries; no65semantic mastery claim','Registration/training/retention/use/emission/composition are independent fields','CPC7NSM65_EVIDENCIAS','Untrained rows remain untrained','No reserved success fabricated from catalog registration','ya existente y conservada')]
for cid,name,member,api,domain,protocol,positive,control,reserve,state in new:
 path=ROOT/'evidence/CPC7'/member
 rows.append({'id':cid,'name':name,'origin':'CPC3–7 selected genealogy','origin_archive_sha256':'64a9ca648d10bb8bc42c02e218091b4e7c5599a55301c65d67c7f6f8ac83a128',
  'source_member':member,'source_sha256':sha(path) if path.exists() else None,'source_available':path.exists(),
  'state_4_0':'Underlying Runtime/research APIs exist; this exact integrated recipe/session is not inherited merely by API name',
  'posterior_contribution':name,'mechanism':api,'domain':domain,'protocol_horizon':protocol,
  'resources':'Explicit initial inventory, physical inputs, queries and auxiliary resources; record measured counts per case',
  'modality':['NATIVE_EVOLUTION','EXPERIENCE_PROTOCOL','PHYSICAL_PROBE','PASSIVE_OBSERVATION'],
  'api_4_5':api,'positive_reference':positive,'control':control,'reserve':reserve,
  'planned_status':state,'final_status':'PENDING_IMPLEMENTATION_AND_TEST','evidence':[]})
put(ROOT/'MATRIZ_CAPACIDADES_CPC.json',{'schema':'DEE4.5.capability-coverage.v1','phase':'INITIAL_SCOPE_NOT_RELEASE_CLAIM','entries':rows,
 'rule':'Final publication status must cite installed API execution, causal control, reserved variant and declared domain. A distributed experimental recipe is not stable native functionality by declaration.'})
supersessions=[{'id':'S01','old':'All4.0public families/sessions','decision':'retain compatible public API','reason':'Complementary geometries and domains; new U0 does not replace N47/N34/N127 profiles'},
 {'id':'S02','old':'CPC7config with17 values for16banks','decision':'remove defective input from operational route; retain original evidence','new':'Strict length/domain validation before creating a Runtime; actual experiences still required'},
 {'id':'S03','old':'Unprotected integrated geometry','decision':'keep distinct recipe revision/control','new':'Guarded preparation with six extra objects; resource/history-matched comparison, not same physical identity'},
 {'id':'S04','old':'Ordinary single teacher revision','decision':'retain as reference; offer explicitM1/M2protocols','new':'M1/M2 add dose/routes; do not advertise as free or generic regulation'},
 {'id':'S05','old':'CPC workspace imports and source-specific identity gates','decision':'replace only in new product implementation','new':'Installed native factories/typed sessions; historical source kept for differential reference'},
 {'id':'S06','old':'Discrepancy vs missing-actual question prototypes','decision':'complementary, not silently fused','new':'Separate recipe IDs and modal domains'},
 {'id':'S07','old':'Physical raw snapshot copies','decision':'retain supported physical format; add lossless bounded storage adapter','new':'Explicitgzip/hash/CRC and schema checks, never teaching or resetting fields'}]
put(ROOT/'MATRIZ_SUPERSESIONES.json',{'schema':'DEE4.5.supersessions.v1','phase':'INITIAL_SCOPE','decisions':supersessions})
put(ROOT/'MATRIZ_4_0_A_4_5.json',{'schema':'DEE4.5.product-evolution.v1','inherited':base['compatibility'],
 'invariants':['kernel_v27.cpp byte identity','No change to physical packing/constants/clocks/reducer/branch ordering','Direct Runtime has no cognitive autoload','All4.0public names retained unless explicitly justified'],
 'new_layers':['Optional compiled native preparation/protocol helpers','Installed typed session facilitators','Lossless persistence adapter','Private validation and provenance'],
 'comparisons':['A:4.0vs4.5 same preparation/protocol exact physical and operative state','B:CPC original4.0vs published4.5 implementation','C:Changed organization/resource variants compare function and matched controls, not equalRAWhashes'],
 'status':'PENDING_VALIDATION'})
print(json.dumps({'coverage_entries':len(rows),'supersessions':len(supersessions),'missing_source_members':[r.get('source_member') for r in rows if r.get('source_available') is False]}))
