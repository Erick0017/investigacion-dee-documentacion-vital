"""MI01 fixed budget, preselected parent and complete-state check. Zero ticks."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from zipfile import ZipFile
import ctypes,hashlib,importlib.util,json,platform,shutil,sys,time,xml.etree.ElementTree as ET
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/MENTE_DEE_INTEGRAL_MI01';E.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(S))
from app.lives import Store
from app.native_tools import identity,physical
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
if not(L/'PRESUPUESTO.json').exists():
    now=datetime.now(timezone.utc);start=datetime(2026,10,22,4,49,tzinfo=timezone.utc);remaining=28800-(now-start).total_seconds();assert remaining>0
    class MEM(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),*[(k,ctypes.c_ulonglong)for k in('total','available','page_total','page_avail','virt_total','virt_avail','extended')]]
    mem=MEM();mem.length=ctypes.sizeof(mem);ok=ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem));disk=shutil.disk_usage(R)
    save(L/'PRESUPUESTO.json',{'campaign':'MENTE_DEE_INTEGRAL_MI01','start_bound_utc':start.isoformat(),'registered_utc':now.isoformat(),
      'monotonic_registered':time.monotonic(),'monotonic_deadline':time.monotonic()+remaining,'deadline_utc':(start+timedelta(hours=8)).isoformat(),
      'maximum_seconds':28800,'already_elapsed_deducted_seconds':(now-start).total_seconds(),'construction_freeze_latest_utc':(start+timedelta(hours=4)).isoformat(),
      'construction_freeze_latest_monotonic':time.monotonic()+remaining-14400,'reserved_closure_seconds':2700,'native_writers_max':1,
      'own_ram_limit_bytes':6_000_000_000,'ram_available_bytes':mem.available if ok else None,'ram_total_bytes':mem.total if ok else None,
      'campaign_storage_limit_bytes':12_000_000_000,'D_free_bytes':disk.free,'no_reinstalls_or_OS_policy_bypass':True,
      'note':'Prior C2 campaign is closed. This new explicit8h request has one fixed new cutoff; no clock restart.'})
if(E/'INICIO_Y_PADRE.json').exists():raise FileExistsError('Do not repeat or overwrite MI01 start')
store=Store();parent_name='E1_CICLO02_SEPARACION_TRIPLE_01';p=store.record(parent_name);active=store.record();motor=identity()
assert motor['build_info']['product_version']=='4.5.0'and motor['build_info']['kernel_version']==27
assert motor['native_sha256']=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
sp=importlib.util.spec_from_file_location('snapshot_only',S/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
x=m.Snapshot(store.snapshot(p));assert x.encoded_sha256==p['snapshot_sha256']and x.tick==p['physical']['tick']
assert x.tick>=21711
if x.tick==21711:assert x.encoded_sha256=='e5298f9e32e75ec986e2427bf396cd547989aae80ab74e28205dd7310ed8ef82'
before=sha(store.snapshot(p));record,a=store.load(parent_name);physical_before=physical(a.world);physical_after=physical(a.world)
assert physical_before==physical_after and before==sha(store.snapshot(p));del a
parent_selected={'life_id':parent_name,'tick':x.tick,'snapshot':p['snapshot'],'sha256':p['snapshot_sha256'],'profile':p['profile'],
 'reason_before_evaluation':'Predeclared C2 complement with three actually used native codes, scalar consequence acquisition, prior comparators and external bridge. Selected by documented previous functions, not new MI01 outcome.',
 'not_inherited':'No divergent MAIN21/21future, no re-created finite selector, no transplanted CPC7/U0/AA01 memory.'}
main=store.fork(parent_name,'E1_MI01_MAIN',kind='CANDIDATE')
doc=R/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx'
with ZipFile(doc)as z:
    tree=ET.fromstring(z.read('word/document.xml'));ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    paras=[''.join(n.itertext())for n in[]] # OOXML text extraction below never executes fields.
    paras=[''.join(t.text or''for t in node.findall('.//w:t',ns))for node in tree.findall('.//w:body/w:p',ns)]
alltext='\n'.join(paras);(E/'LECTURA_MANUAL_TEXTO.txt').write_text(alltext,encoding='utf8')
chapter23=next(i for i,t in enumerate(paras)if t=='23 Consolidación y evolución de E1 Ciclo 02');end=next((i for i in range(chapter23+1,len(paras))if paras[i].startswith('Apéndice A.')),len(paras))
directed=paras[:22]+paras[chapter23:end];(E/'MANUAL_LECTURA_DIRIGIDA.txt').write_text('\n'.join(directed),encoding='utf8')
save(E/'INICIO_Y_PADRE.json',{'identity':motor,'python':sys.executable,'platform':platform.platform(),'parent_selected_before_evaluation':parent_selected,
 'parent_complete_state':x.summary(),'pending_inputs':x.pending,'active_protected':{k:active.get(k)for k in('life_id','snapshot','snapshot_sha256','physical')},
 'main_fork':{k:main.get(k)for k in('life_id','snapshot','snapshot_sha256','parent','physical')},'native_ticks_advanced':0,
 'manual':{'path':str(doc.relative_to(R)),'sha256':sha(doc),'directed_extract':'MANUAL_LECTURA_DIRIGIDA.txt','known_editorial_defect_to_fix':'Control field still says1.4 inside1.6; exact OOXML/table context to be changed only at closure.'}})
save(E/'CRITERIOS_INICIALES.json',{'classification_is_reasoned_not_global_PASS':True,'principal':'E1_MI01_MAIN','architecture_alternative_limit':1,
 'construction_then_fixed_evaluation':True,'criteria_before_reserves':[
 {'criterion':'aprendizaje_util','measurement':'Native output/actual action and consequence under paired intact/omitted/null histories. Improvement must affect predefined task utility, not merely raw change.'},
 {'criterion':'seleccion_o_iniciacion_nativa','measurement':'Physically emitted request/route precedes fixed dispatcher operation. Same present opportunity with different learned histories; no host failure/answer based routing.'},
 {'criterion':'retencion_y_nueva_adquisicion','measurement':'Fixed decoded prior contents used before/after new experience in the same trajectory; first-use and later-use counts separated.'},
 {'criterion':'tres_familias_y_compuesta','measurement':'Action/consequence, information access/social source, and native relational combination interleaved. One compound reserved situation, not sum of forks or external motor addition.'},
 {'criterion':'reserva','measurement':'Freeze source/decoder/assistance before three causally different reserved sequences; record missing coverage. Learning remains native-active; no architecture repair.'},
 {'criterion':'comunicacion_causal','measurement':'Private B input, native formed message and later E1 use; admitted postformed cut/sham where needed.'},
 {'criterion':'continuidad','measurement':'Whole native world/owner/protocol/interfaces/pending/environment/RNG saved, reloaded and continued in another process. No favorable rewind.'}],
 'possible_outcomes':['organizacion_integrada_con_autonomia_en_dominio','integracion_util_todavia_asistida','adaptaciones_especializadas_sin_integracion_suficiente','construccion_no_conseguida'],
 'numeric_task_criteria':'Will be fixed with the selected realizable apparatus BEFORE its reserved evaluation; no score chosen after seeing outcomes.',
 'existing_evidence_reused_not_new_acquisition':'C2/IC01/AA01/CPC7; no full inherited34family suite'})
print(json.dumps({'budget':json.loads((L/'PRESUPUESTO.json').read_bytes()),'parent':parent_selected,'active':active['life_id'],'main':main['life_id'],'engine':motor['build_info']['product_version'],'tick':x.tick,'pending':len(x.pending),'manual_directed_paragraphs':len(directed),'native_ticks':0},ensure_ascii=False))
