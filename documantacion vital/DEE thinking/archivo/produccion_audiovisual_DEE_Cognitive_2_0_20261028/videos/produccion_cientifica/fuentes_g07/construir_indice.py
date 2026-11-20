"""Índice de registros existentes y reconstrucción geométrica. Cero ticks nuevos."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET,json,hashlib,collections
W=Path(__file__).resolve().parent
B=Path(r'D:\GENESIS AI\GENESIS 5.0\simulador de universo ab-initio\dee_libreria\VERSION_27\tests')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def paras(p):
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    r=ET.fromstring(ZipFile(p).read('word/document.xml'))
    return [''.join(t.text or '' for t in x.findall('.//w:t',ns)) for x in r.findall('.//w:p',ns)]
def source_doc(p,terms,near=2):
    rows=paras(p);indices=set()
    for i,s in enumerate(rows):
        if any(t.lower() in s.lower() for t in terms):indices.update(range(max(0,i-near),min(len(rows),i+near+1)))
    return {'path':str(p),'sha256':sha(p),'paragraphs':[{'index':i,'text':rows[i]} for i in sorted(indices)][:130]}

core=B/'documantacion vital/cores/06_DEE_V27_NATIVE_LEARNING_C_RELATIVITY_AND_ROSETTA_CLOSURE_RESULTADOS.zip'
z=ZipFile(core);member=next(n for n in z.namelist() if n.endswith('RESULTS/C6H04_compositional_translation_holdout.json'))
blob=z.read(member);p=W/'C6H04_compositional_translation_holdout_original.json';p.write_bytes(blob);d=json.loads(blob)
selected=[{'case_index':i,'value':d['cases'][i]} for i in [0,1,2,3,8,9]]
assert selected[0]['value']['record_first']['sreg']==4091
assert selected[0]['value']['record_second']['sreg']==8189
assert selected[1]['value']['record_second']['sreg']==4091
control={'source_zip':str(core),'source_zip_sha256':sha(core),'member':member,'member_sha256':hashlib.sha256(blob).hexdigest(),'copy':str(p),'selected_cell':d['cells'][0],'selected_cases':selected,'total_counts':dict(collections.Counter(c['mode'] for c in d['cases'])),'warning':'These are C6H04 controls, NOT omission runs of the compact G07. N and geometry differ. Null decoded is absence of readable result, not zero.'}
report=json.loads((W/'VERIFICACION_EDITORIAL_LINUX_original.json').read_text())
g=report['groups']['07'];assert g['examples'][0]=={'d1':3,'d2':7,'query':20,'output_sreg':8222,'decoded':30}
events=[
 {'time':0,'event':'prepare_two_experiences','measured_status':'Exact initial-condition recipe in original verifier lines138–140','carriers':[{'id':'cue1','xyz':[15,15,30],'direction':[1,0,0],'s_reg':4085},{'id':'teacher1','xyz':[25,10,30],'direction':[-1,1,0],'s_reg':14},{'id':'cue2','xyz':[22,30,15],'direction':[1,0,0],'s_reg':4085},{'id':'teacher2','xyz':[32,30,10],'direction':[-1,0,1],'s_reg':18}]},
 {'time':5,'event':'both_memories_form_simultaneously','measured_status':'Meeting geometry documented in book; after-contact fields inferred from additive sector and recipe, no saved full frame','products':[{'id':'memory1','xyz':[20,15,30],'direction':[0,1,0],'s_reg':4099,'functional_delta':3},{'id':'memory2','xyz':[27,30,15],'direction':[0,0,1],'s_reg':4103,'functional_delta':7}]},
 {'time':10,'event':'query_inserted','measured_status':'Exact operation in original verifier line141, arrival helper line72','query':{'xyz':[17,23,30],'direction':[1,0,0],'s_reg':20},'memory1_xyz':[20,20,30],'memory2_xyz':[27,30,20]},
 {'time':13,'event':'first_encounter','xyz':[20,23,30],'output_s_reg':4119,'decoded_after_one_memory':23,'output_direction':[1,1,0],'measured_status':'Position/time explicitly documented; register4119/functional23 derived from recipe plus documented native-sector rule; no retained sample of G07 middle RAW'},
 {'time':20,'event':'second_encounter_and_final_read','xyz':[27,30,30],'output_s_reg':8222,'output_direction':[1,1,1],'reference':8192,'functional_result':30,'measured_status':'Retained editorial execution report confirms final s_reg8222 and decoded30. Position/time in book and verifier. Direction from known encounter rule, not separately retained final sample.'}
]
paths=[
 {'id':'cue1','from_time':0,'until_time':5,'origin':[15,15,30],'direction':[1,0,0],'kind':'geometric reconstruction of recipe'},
 {'id':'teacher1','from_time':0,'until_time':5,'origin':[25,10,30],'direction':[-1,1,0],'kind':'geometric reconstruction of recipe'},
 {'id':'cue2','from_time':0,'until_time':5,'origin':[22,30,15],'direction':[1,0,0],'kind':'geometric reconstruction of recipe'},
 {'id':'teacher2','from_time':0,'until_time':5,'origin':[32,30,10],'direction':[-1,0,1],'kind':'geometric reconstruction of recipe'},
 {'id':'memory1','from_time':5,'until_time':13,'origin':[20,15,30],'direction':[0,1,0],'kind':'transport geometry explicitly documented'},
 {'id':'memory2','from_time':5,'until_time':20,'origin':[27,30,15],'direction':[0,0,1],'kind':'transport geometry explicitly documented'},
 {'id':'query','from_time':10,'until_time':13,'origin':[17,23,30],'direction':[1,0,0],'kind':'query recipe reconstruction'},
 {'id':'first_output','from_time':13,'until_time':20,'origin':[20,23,30],'direction':[1,1,0],'kind':'transport geometry explicitly documented'}]
frames=[]
for t in range(21):
    carriers=[]
    for path in paths:
        if path['from_time']<=t<path['until_time']:
            pos=[(a+v*(t-path['from_time']))%67 for a,v in zip(path['origin'],path['direction'])]
            carriers.append({'id':path['id'],'xyz':pos})
    if t==20:carriers.append({'id':'final_output','xyz':[27,30,30]})
    frames.append({'t':t,'category':'Reconstrucción geométrica','carriers':carriers})
docs={
 'fisica':source_doc(B/'documantacion vital/FISICA DEE Y PROCESAMIENTO NATIVO/DEE_V4_0_1.docx',['toro tridimensional','Moore-26','al comienzo del tick','Con una fuente','dos fuentes','signo de la suma'],1),
 'obp':source_doc(B/'documantacion vital/mente basal/ORGANIZACION_BASAL_PERSISTENTE_DOCUMENTO_MAESTRO_V2_1.docx',['cubo 2×2×2','soporte; la escritura','dos realizaciones complementarias','materia DEE','Centro soportado y escribible','cierre positivo','continuidad'],1),
 'procesamiento':source_doc(B/'documantacion vital/FISICA DEE Y PROCESAMIENTO NATIVO/Procesamiento_Nativo_DEE_Libro_Manual_v1.docx',['G07','n=20,','Dos memorias, una consulta','37.','consulta','una región'],0)
}
out={'schema':'DEE.editorial.G07.evidence.v1','N':67,'B_per_memory':4096,'number_memories':2,'final_baseline':8192,'new_native_ticks':0,'category_required':'Reconstrucción geométrica','source_report':{'file':str(W/'VERIFICACION_EDITORIAL_LINUX_original.json'),'sha256':sha(W/'VERIFICACION_EDITORIAL_LINUX_original.json'),'pointer':'/groups/07','data':g,'runtime':report['runtime']},'source_recipe':{'file':str(W/'verificar_dee_original.py'),'sha256':sha(W/'verificar_dee_original.py'),'lines':[134,146],'helper_lines':[58,72]},'causal_events':events,'paths':paths,'geometric_site_frames':frames,'controls':control,'documents':docs,'limits':['No new ticks or imports of the kernel.','The G07 report retains four final values, not a dense state/clock trajectory.','All intermediate particle motion must be labelled geometric reconstruction, not measured microscopic footage.','No toroidal boundary is crossed in the selected G07 interval0–20.','Both acquisitions occur atT5; editorial focus may alternate, physical time must not be falsified.','This is an engine-research demonstration, not acquired knowledge of DEE20_DEMO_01.','The historical PN kernel identity is recorded from its sources; do not silently present it as a fresh run of thinking4.5.','G07 compact has no retained omission control. C6H04 controls use other geometries/N and cannot be transplanted into this trajectory.']}
save(W/'G07_EVIDENCIA_Y_GEOMETRIA.json',out)
print('SAVED',W/'G07_EVIDENCIA_Y_GEOMETRIA.json')
print('DOC_SOURCE_PARAGRAPHS',{k:len(v['paragraphs']) for k,v in docs.items()})
