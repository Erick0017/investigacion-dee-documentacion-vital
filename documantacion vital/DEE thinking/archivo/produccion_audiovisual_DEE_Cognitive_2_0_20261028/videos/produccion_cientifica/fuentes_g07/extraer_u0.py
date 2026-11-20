"""Lectura de dos casos U0 existentes y su constructor; cero simulaciones."""
from pathlib import Path
import hashlib,json,shutil
W=Path(__file__).resolve().parent
THINK=W.parents[3]
OLD=W.parents[1]/'edicion_experiencia/fuentes'
# W=.../videos/produccion_cientifica/fuentes_g07, so videos is parents[1].
OLD=W.parents[1]/'edicion_experiencia/fuentes'
SRC=THINK/'4.5/DEE_thinking_4_5_0/source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cases={};sources=[]
for case in ['IR_P01_GUARDED_M1','IR_MATCH_CURRENT']:
    p=OLD/(case+'_RESULT.json');d=json.loads(p.read_text());frames={int(f['tick']):f for f in d['frames']}
    selected={'memory_acquired_T3':frames[3]['forms']['L02'],'question_T19':frames[19]['questions']['right.different'],'information_T70':frames[70]['own_banks']['right'],'use_T72':frames[72]['actions']['own.use.minus'],'other_use_T72':frames[72]['actions']['own.use.plus']}
    calls=[c for c in d['calls'] if c['port'] in ['L02.signal','L02.event.minus','own.use.minus','own.use.plus'] or c['port'].startswith('need.actual.')]
    cases[case]={'case_id':d['case_id'],'selected_samples':selected,'relevant_inputs':calls,'engine':d['engine'],'pointer':'/frames selected by tick3,19,70,72; /calls by port'}
    sources.append({'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
assert cases['IR_P01_GUARDED_M1']['selected_samples']['question_T19']['direction']==[1,0,0]
assert cases['IR_P01_GUARDED_M1']['selected_samples']['information_T70']['s_reg']==53
assert cases['IR_P01_GUARDED_M1']['selected_samples']['use_T72']['s_reg']==60
assert cases['IR_MATCH_CURRENT']['selected_samples']['information_T70']['s_reg']==16
assert cases['IR_MATCH_CURRENT']['selected_samples']['use_T72']['s_reg']==7
code=SRC/'src/consolidated.cpp';test=SRC/'tests/consolidated_tests.cpp'
excerpts=[]
for p,first,last in [(code,28,36),(code,116,164),(test,48,61)]:
    lines=p.read_text(encoding='utf8').splitlines();excerpts.append({'file':str(p),'sha256':sha(p),'line_first':first,'line_last':last,'lines':lines[first-1:last]})
out={'schema':'DEE.editorial.U0.information.geometry.v1','new_native_ticks':0,'N':67,'cases':cases,'sources':sources,'constructor_excerpts':excerpts,
 'reconstruction':[
 {'id':'learned_L02','from_tick':3,'to_tick':70,'origin':[31,10,46],'direction':[0,-1,0],'s_reg':16,'source':'memory acquired sampleT3 + form constructor + teaching receipts','known_wraps':[{'before_tick':13,'before_xyz':[31,0,46],'after_tick':14,'after_xyz':[31,66,46]}],'end_xyz':[31,10,46],'label':'Reconstrucción geométrica; free-transport branch is intended by constructor, not densely observed lineage'},
 {'id':'native_question','from_tick':19,'to_tick':70,'origin':[47,10,46],'direction':[1,0,0],'s_reg':37,'source':'T19 measured plus hub=move(question,{1,0,0},51,67) in constructor','known_wraps':[{'before_tick':38,'before_xyz':[66,10,46],'after_tick':39,'after_xyz':[0,10,46]}],'end_xyz':[31,10,46],'label':'Reconstrucción geométrica; actual endpoints measured, intermediate path from declared route'},
 {'id':'information_after_encounter','from_tick':70,'to_tick':72,'origin':[31,10,46],'direction':[1,-1,0],'s_reg':53,'end_xyz':[33,8,46],'source':'T70 measured info and action=move(hub,{1,-1,0},2,67); matching useT72'},
 {'id':'common_use_resource','from_tick':69,'to_tick':72,'origin':[33,8,43],'direction':[0,0,1],'s_reg':7,'end_xyz':[33,8,46],'source':'own.use.minus receipt appliedT69 and action_input=move(action,{0,0,1},-3,67)'}],
 'encounters':[{'tick':70,'xyz':[31,10,46],'inputs':[37,16],'output':53,'direction':[1,-1,0],'basis':'Measured output53 and intended directional intersection; no dense lineage proof'}, {'tick':72,'xyz':[33,8,46],'inputs':[53,7],'output':60,'direction':[1,-1,1],'basis':'Measured output60, matching input7 admittedT69 and route2; contrast present'}],
 'contrast':{'main':'question37 + learned16 → information53; information53 + common7 → use60','matching_current':'No horizontal different-question; learned16 appears atbankT70 with direction(0,-1,0), actionT72 is only common7 direction(0,0,1).','interpretation':'The data received participates in a later native transformation, distinct from selecting an externally useful task action. No autonomous scheduling or general adaptation claim.'},
 'limits':['Complete route geometry is recoverable from constructor and timing, including both periodic crossings.','Only listed sampled fields are directly observed here; no dense trajectory or identity tags were retained.','Matching payload/endpoints does not by itself prove a unique lineage. Use geometric-reconstruction label, not measured-trajectory label.','Do not depict the high bank as stationary memory: its acquired product travels around−Y and returns atT70.','Resource7 is an externally scheduled opportunity, not a spontaneous query initiated by E1.','Other activity exists in this U0; this is a selected route view, not full-world occupancy.','This U0 archive is not DEE20_DEMO_01 and must not be attributed as current-life knowledge.']}
save(W/'U0_INFORMACION_GEOMETRIA.json',out)
print('SAVED',W/'U0_INFORMACION_GEOMETRIA.json')
