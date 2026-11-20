"""Fourteen official chapters, using archived cases. No experimental execution.

The planned times are film edit times; native ticks remain source metadata.
Separate cases/branches are separate render views, never merged world states.
"""
from pathlib import Path
import json,gzip,copy
import datos_c_3d as cdata,datos_m_3d as mdata
from visual_core import roi,clone_case,BLUE,AMBER,PURPLE,GREY
HERE=Path(__file__).resolve().parent
SCRIPT=json.loads((HERE/'audio/guion.json').read_text('utf8'))
SCENES=SCRIPT['blocks']
C={s:[*fn()] for s,fn in [(3,cdata.cases03),(5,cdata.cases05),(7,mdata.cases07),(8,mdata.cases08),(9,mdata.cases09),(10,cdata.cases10),(11,cdata.cases11),(12,cdata.cases12),(13,cdata.cases13)]}
CASES={x['id']:x for v in C.values() for x in v}
M=json.loads((HERE/'fuentes/ESCENAS_04_06_09.json').read_text('utf8'))
CTX=json.loads((HERE/'fuentes/CONTEXTOS_U0_3D.json').read_text('utf8'))
context={int(f['tick']):f for f in CTX['frames']}
for tick in (0,19,75,338,405,472):
 pts=roi(context[tick]['all_nonzero_points'],[33,25,42],3)
 CASES[f'body_u0_{tick}']={'id':f'body_u0_{tick}','points':pts,'focus_sites':[p['site'] for p in pts],
 'prep_markers':[],'life':'IR_P01_GUARDED_M1','N':67,'tick':tick,'classification':'Registro',
 'source_refs':CTX['sources'],'label_es':'Región observada de U0','label_en':'Observed U0 region','output_es':'','output_en':''}

# Memory: actual teaching event at T0/T3, then the same later query T335/T338.
for arm in ('AB_minus','BA_plus'):
 a=M['scenes']['04']['arms'][arm]
 for st in a['stages']:
  tick=int(st['tick']);pts=roi(st['points'],[30,30,5],3)
  result='−' if arm=='AB_minus' else '+'
  CASES[f'04_{arm}_{tick}']={'id':f'04_{arm}_{tick}','points':pts,'focus_sites':[[30,30,5]],
    'prep_markers':[],'life':a['life'],'N':67,'tick':tick,'classification':'Etapas','vectors':tick in (3,338),
    'source_refs':[a['source']],'label_es':'Historia A' if arm=='AB_minus' else 'Historia B',
    'label_en':'History A' if arm=='AB_minus' else 'History B',
    'output_es':('Salida '+result) if tick==338 else '', 'output_en':('Response '+result) if tick==338 else ''}

# CPC9: retained input/result states and the two exact historical controls.
co=M['scenes']['06'];pre=co['exact_local_composition']['pre_Moore27']
def cp(id,tick,pts,focus,out='',prep=None):
 CASES[id]={'id':id,'tick':tick,'points':pts,'focus_sites':focus,'prep_markers':prep or [],'N':67,'life':'EI_D01',
 'classification':'Etapas','source_refs':co['primary_sources'],'label_es':'CPC9','label_en':'CPC9',
 'output_es':out,'output_en':out}
cp('06_inputs',205,pre,[[19,8,13],[20,7,14],[20,8,14]])
cp('06_product',206,[co['exact_local_composition']['formed206']],[[20,8,14]],'56')
cp('06_admission',207,[],[[24,15,18]],prep=[[24,15,18]])
use=next(st for st in co['stages'] if st['tick']==210)['points']
cp('06_use',210,use,[[24,12,18]],'63')
cut,sham=co['controls']
assert cut['condition']=='cut_arrival_0' and sham['condition']=='sham_formed206'
cutpre=copy.deepcopy(pre)
for p in cutpre:
 if p['site']==cut['victim']['site']:p.update(raw='0',state=0,s_reg=0,semantic=0,direction=[0,0,0])
cp('06_cut_pre',205,cutpre,[[19,8,13],[20,7,14],[20,8,14]])
cp('06_cut_use',210,[cut['consequence210']],[[24,12,18]],'7')
cp('06_sham_use',210,[sham['consequence210']],[[24,12,18]],'63')
for id in ('06_inputs','06_cut_pre'):
 CASES[id]['point_colors']={'19,8,13':BLUE,'20,7,14':AMBER}
 CASES[id]['point_shapes']={'19,8,13':'sphere','20,7,14':'cube'}
for id in ('06_use','06_cut_use','06_sham_use'):
 CASES[id]['point_colors']={'24,12,18':'#D4CDF5'}
 CASES[id]['vectors']=True
for id in ('05_L03_402','11_cue_72','11_cue_139'):CASES[id]['focus_prepared']=True
for id,x in CASES.items():
 if id.startswith(('05_','11_')) or id.startswith('13_') and id not in ('13_principal_global','13_principal_region_1','13_principal_region_2'):
  x['vectors']=True
 if id.startswith('09_reference_'):
  x['point_colors']={'49,35,35':AMBER,'51,35,35':BLUE,'50,35,35':PURPLE}
 if id.startswith('09_action_'):x['vectors']=True
 if id.startswith('10_'):
  x['point_colors']={'22,40,56':AMBER,'22,40,10':AMBER,'22,40,11':BLUE}
 if id.startswith('12_') and x.get('N')==26:x['azimuth']=-35
CASES['12_opposite_trained']['output_es']='Salida previa +'
CASES['12_opposite_trained']['output_en']='Previous output +'

def case(id,short_es='',short_en='',**changes):
 x=clone_case(CASES[id],**changes)
 if short_es:x['short_es']=short_es
 if short_en:x['short_en']=short_en
 return x

SHOTS=[]
def add(s,a,b,ids,head,en='',phase='',phaseen='',tag='',kind=None,classification='Etapas',new=False,**extra):
 scene=SCENES[s-1]
 cases=[case(x) if isinstance(x,str) else x for x in ids]
 spec={'scene':s,'start':scene['start_s']+a,'end':scene['start_s']+b,
       'cases':cases,'header_es':head,'header_en':en,'phase_es':phase,'phase_en':phaseen,
       'case_tag':tag,'classification':classification,'new_trial':new}
 if kind:spec['kind']=kind
 spec.update(extra);SHOTS.append(spec)

#01 Overview: real instances, explicitly an editorial montage of distinct trials.
add(1,0,7,['13_principal_region_1'],'DEE Cognitive 2.0','Un universo computacional · A computational universe',tag='ECI02 · N67',classification='Registro',push=True)
add(1,7,10,[case('04_AB_minus_338','Historia A','History A'),case('04_BA_plus_338','Historia B','History B')],
    'Aprendizaje y memoria','Learning and memory',tag='U0 · ensayos / trials',new=True)
add(1,10,13,['06_product'],'Composición','Composition',tag='CPC9 · EI_D01',new=True)
add(1,13,18,['03_postreopen_memory'],'Experiencia conservada','Retained experience',phase='Uso después de reabrir',phaseen='Use after reopening',tag='ECI02 · MINUS',new=True)
add(1,18,24,['13_LEX_luma'],'Funciones en una misma instancia','Functions in one instance',tag='ECI02 · principal',new=True)

#02 The definition of physical refers to computational states/interactions.
add(2,0,7,['body_u0_0'],'Cada celda es un lugar','Each cell is a location',tag='U0 · región / region',classification='Registro',push=True)
add(2,7,13,['06_inputs'],'Una entrada encuentra un estado','An input encounters a state',phase='Aportes registrados · T205',phaseen='Recorded contributions · T205',tag='CPC9 · EI_D01',new=True)
add(2,13,18,['06_product'],'El encuentro cambia el estado','Interaction changes the state',phase='Resultado medido · T206',phaseen='Measured result · T206',tag='CPC9 · EI_D01')
add(2,18,24,['06_product'],'Estados e interacciones del modelo','States and interactions in the model',phase='No son partículas del mundo exterior',phaseen='Not particles from the outside world',tag='CPC9 · EI_D01')

#03 The actual full saved state is shown, then the separately recorded post-reopen use.
add(3,0,5,['03_saved_memory_roi'],'Continuar desde la historia','Continuing from history',phase='Estado guardado',phaseen='Saved state',tag='ECI02 · MINUS',classification='Registro',new=True)
add(3,5,9,['03_loaded_memory_roi'],'El mismo estado, reabierto','The same state, reopened',phase='Identidad física comprobada',phaseen='Physical-state identity verified',tag='ECI02 · MINUS',classification='Registro')
add(3,9,13,['03_postreopen_lexical'],'Nueva interacción después de cargar','New interaction after loading',tag='ECI02 · MINUS')
add(3,13,19,['03_postreopen_memory'],'Lo conservado vuelve a utilizarse','What was retained is used again',phase='Lectura posterior verificada',phaseen='Verified later readout',tag='ECI02 · MINUS')

#04 Two histories; none of their knowledge is attributed to the principal.
add(4,0,3,['body_u0_0'],'Experiencia dentro de una organización','Experience within an organisation',tag='U0 · CPC7',new=True)
add(4,3,7,[case('04_AB_minus_3','Contenido A','Content A'),case('04_BA_plus_3','Contenido B','Content B')],
    'Historias adquiridas diferentes','Different acquired histories',tag='U0 · dos vidas / two lives')
add(4,7,11,[case('04_AB_minus_335','Historia A','History A'),case('04_BA_plus_335','Historia B','History B')],
    'La misma consulta posterior','The same later query',tag='U0 · T335')
add(4,11,18,[case('04_AB_minus_338','Historia A','History A'),case('04_BA_plus_338','Historia B','History B')],
    'La respuesta depende de la historia','The response depends on history',tag='U0 · T338')
add(4,18,23,['05_L03_338'],'Conservar no garantiza acceso','Retention does not guarantee access',tag='U0 · alcance local / local scope')

#05 A revised association and real witnesses, not lights claiming total memory.
add(5,0,4,['05_L03_338'],'Una asociación ya adquirida','An acquired association',phase='Antes: salida −',phaseen='Before: response −',tag='U0 · L03')
add(5,4,7,['05_L03_402'],'Nueva experiencia de revisión','A new revision experience',tag='U0 · T402')
add(5,7,11,['05_L03_405'],'Cambió el estado adquirido','The acquired state changed',tag='U0 · T405')
add(5,11,14,['05_L03_472'],'La consulta ahora produce otra respuesta','The query now produces a different response',phase='Después: salida +',phaseen='After: response +',tag='U0 · T472')
add(5,14,17,[case('05_witness_L04','Testigo L04','Witness L04'),case('05_witness_L05','Testigo L05','Witness L05')],
    'Otras asociaciones siguieron disponibles','Other associations remained available',tag='U0 · mismo ensayo / same trial')
add(5,17,20,['05_witness_L06'],'Revisión selectiva en este panel','Selective revision in this panel',phase='Ejemplos de 13 testigos comprobados',phaseen='Examples from 13 verified witnesses',tag='U0 · T472')

#06 Full20s: distinct product/use locations, a declared record gap, exact controls.
add(6,0,2,['06_inputs'],'Dos contribuciones','Two contributions',phase='Aportes · T205',phaseen='Contributions · T205',tag='CPC9 · EI_D01',new=True)
add(6,2,4,['06_product'],'Producto formado','Product formed',phase='Estado posterior · T206',phaseen='Later state · T206',tag='CPC9 · EI_D01')
add(6,4,5.8,['06_admission'],'Admisión preparada','Prepared admission',phase='Recurso 7 · sin cuadro físico',phaseen='Resource7 · no physical frame',tag='CPC9 · T207')
add(6,5.8,7.4,['06_use'],'Uso posterior','Later use',phase='Salto de registro · consecuencia T210',phaseen='Record gap · consequence at T210',tag='CPC9 · EI_D01')
add(6,7.4,10.4,[case('06_product','Producto · T206','Product · T206'),case('06_use','Uso · T210','Use · T210')],
    'Dos cortes del mismo mundo','Two stages of the same world',tag='CPC9 · orden y contacto / order & contact')
add(6,10.4,13.4,[case('06_inputs','Original','Original'),case('06_cut_pre','Corte de un aporte','One contribution cut')],
    'Retirar una contribución','Removing one contribution',tag='CPC9 · control diagnóstico / diagnostic control')
add(6,13.4,16.1,[case('06_use','Original','Original'),case('06_cut_use','Corte selectivo','Selective cut')],
    'La consecuencia cambia','The consequence changes',tag='CPC9 · 63 / 7')
add(6,16.1,20,[case('06_use','Original','Original'),case('06_sham_use','Intervención simulada','Sham intervention')],
    'El control conserva el resultado','The control preserves the result',tag='CPC9 · 63 / 63')

#07 Acquired information from B, then later native use in the recipient.
add(7,0,4,['07_B_source'],'Información privada de otro participante','Private information from another participant',phase='Participante B',phaseen='Participant B',tag='IC01 · N67',new=True)
add(7,4,7.4,['07_observed_encounter'],'Un mensaje interviene físicamente','A message acts through a physical interaction',tag='IC01 · T16563')
add(7,7.4,11,['07_later_full'],'El receptor la utiliza después','The receiver uses it later',phase='Consulta genérica, contenido de la historia',phaseen='Generic query, content from history',tag='IC01 · T16619')
add(7,11,15.6,[case('07_later_full','Mensaje intacto','Intact message'),case('07_later_cut','Mensaje cortado','Cut message')],
    'El corte altera la respuesta','The cut changes the response',tag='IC01 · controles / controls')
add(7,15.6,20,[case('07_later_sham','Control simulado','Sham control'),case('07_later_no_B','Sin nueva información','No new information')],
    'Transmisión y uso, no conversación humana','Transmission and use, not human conversation',tag='IC01 · alcance concreto / limited scope')

#08 Prepared comparison conditions; actual emitted question and subsequent use.
add(8,0,5,['08_discrepant_15'],'Comparar lo previo con lo actual','Comparing earlier and current information',phase='Funciones del protocolo, no posiciones físicas',phaseen='Protocol roles, not physical positions',tag='U0 · otro episodio / another episode',kind='comparison_schema',classification='Esquema',new=True)
add(8,5,10,[case('08_discrepant_19','Discrepancia','Mismatch'),case('08_matching_current_19','Coincidencia','Match')],
    'La discrepancia produce una pregunta','The mismatch produces a question',tag='U0 · T19')
add(8,10,14,['08_discrepant_70'],'La pregunta accede a información','The question accesses information',tag='U0 · banco / bank · T70')
add(8,14,20,['08_discrepant_72'],'La información interviene en un uso','The information contributes to a use',phase='Oportunidades y tiempos preparados',phaseen='Prepared opportunities and timing',tag='U0 · T72')

#09 Feedback learning and the separate external-service trial are not one life.
add(9,0,1.6,['09_action_full_0'],'Una acción produjo una consecuencia','An action produced a consequence',phase='Acción nativa registrada',phaseen='Recorded native action',tag='Ciclo02 · N67',new=True)
add(9,1.6,4.4,['09_reference_full_1'],'El retorno modificó la referencia','The return changed the reference',phase='Referencia adquirida: 5 → 11',phaseen='Acquired reference:5 →11',tag='Ciclo02 · estado posterior / later state')
add(9,4.4,7.3,[case('09_reference_full_1','Con retorno','With feedback'),case('09_reference_omit_1','Sin retorno','Without feedback')],
    'Una oportunidad actual común','A common current opportunity',tag='Ciclo02 · entradas emparejadas / matched inputs')
add(9,7.3,11.6,[case('09_action_full_1','Con retorno','With feedback'),case('09_action_omit_1','Sin retorno','Without feedback')],
    'La historia cambia la actuación','History changes the action',tag='Ciclo02 · acción − / acción +')
add(9,11.6,14.1,['09_external_native_action'],'Una salida actuó fuera de DEE','An output acted outside DEE',phase='Otro ensayo · EO01',phaseen='Another trial · EO01',tag='EO01 · N26',new=True)
add(9,14.1,17.2,['09_external_contact'],'Acción, servicio y retorno','Action, service and return',phase='Contacto registrado; tarea sin completar',phaseen='Contact recorded; task incomplete',tag='EO01 · puente externo / external bridge',kind='service',classification='Esquema')
add(9,17.2,21,['09_external_actual_feedback'],'El efecto regresó como experiencia','The effect returned as experience',phase='Entrada admitida, no trayectoria reconstruida',phaseen='Admitted input, not a reconstructed path',tag='EO01 · T96565',classification='Esquema')

#10 Local regulation in its own finite profile, including zero-load real carriers.
regpulse=lambda id,es,en:case(id,es,en,focus_sites=[[22,40,56]],vectors=True,crop_radius=3)
add(10,0,6,[regpulse('10_REG_PAIRED_3','Historia asociada','Paired history'),regpulse('10_REG_OPPOSITE_3','Historia opuesta','Opposite history')],
    'La experiencia cambia una dirección','Experience changes a direction',tag='CPC5 · perfil local / local profile',new=True)
add(10,6,9,[case('10_REG_PAIRED_292','Pulso adquirido','Acquired pulse',vectors=True),case('10_REG_UNPAIRED_292','Control no asociado','Unpaired control',vectors=True)],
    'Encuentro con una interferencia','An encounter with interference',tag='CPC5 · T292')
add(10,9,13,[case('10_REG_PAIRED_293','Historia asociada','Paired history'),case('10_REG_UNPAIRED_293','Control','Control')],
    'El efecto local es diferente','The local effect differs',tag='CPC5 · T293')
add(10,13,20,[case('10_REG_PAIRED_437','Historia asociada','Paired history'),case('10_REG_UNPAIRED_437','Control','Control')],
    'Regulación local en un aparato preparado','Local regulation in a prepared apparatus',tag='CPC5 · lector / reader · T437')

#11 Signal+experience and signal-only later use are visually distinct stages.
add(11,0,3,['11_cue_72'],'Una señal y una experiencia','A signal and an experience',tag='U0 · asociación / association',new=True)
add(11,3,7,['11_cue_75'],'Se forma una asociación concreta','A specific association forms',tag='U0 · T75')
add(11,7,11,['11_cue_139'],'La señal vuelve, sin repetir la enseñanza','The signal returns, without reteaching',tag='U0 · T139')
add(11,11,15.5,['11_cue_142'],'La señal recupera una respuesta','The signal retrieves a response',tag='U0 · T142')
add(11,15.5,19,['11_cue_142'],'Uso funcional limitado','Limited functional use',phase='No es conversación libre',phaseen='Not free conversation',tag='U0 · alcance / scope')

#12 First action is shown before destination feedback, then the opposing rule.
add(12,0,3,['12_source_after'],'Una historia adquirida previamente','A previously acquired history',tag='ENTE02 · N26',new=True)
add(12,3,8,[case('12_first_trained','Con experiencia','With experience'),case('12_first_control','Control','Control')],
    'Primera actuación en otro contexto','First action in another context',tag='ENTE02 · antes del nuevo retorno / before new feedback')
add(12,8,13.5,[case('12_opposite_trained','Historia transferida','Transferred history'),case('12_opposite_control','Control','Control')],
    'Con una regla opuesta, también perjudica','With the opposite rule, it can also hurt',tag='ENTE02 · regla opuesta / opposite rule')
add(12,13.5,21,[case('12_aggregate_ref_sham_zero','Control 1','Control1'),case('12_aggregate_ref_sham_two','Control 2','Control2')],
    'Otros ensayos: contribuciones múltiples','Other trials: multiple contributions',tag='FI01 · N67 · otro ensayo / another trial',new=True)

#13 Only the actual principal's own consecutive uses, then software-role diagram.
add(13,0,3.5,['13_principal_region_2'],'Resultados de ensayos identificados','Results from identified trials',tag='ECI02 · principal',classification='Registro',new=True)
add(13,3.5,5.8,['13_LEX_luma'],'Asociación','Association',tag='ECI02 · misma instancia / same instance')
add(13,5.8,7.9,['13_MA_PRE'],'Memoria','Memory',tag='ECI02 · misma instancia / same instance')
add(13,7.9,9.9,['13_comparison'],'Comparación preparada','Prepared comparison',tag='ECI02 · misma instancia / same instance')
add(13,9.9,15.6,[],'Universe · Thinking · Cognitive','Funciones del software · Software roles',kind='architecture',classification='Esquema',tag='Arquitectura / Architecture')
add(13,15.6,20,['13_principal_region_1'],'Integración parcial, con continuidad','Partial integration, with continuity',phase='No reúne todos los experimentos',phaseen='It does not include every experiment',tag='ECI02 · T727225',classification='Registro')

#14 Recap of shown evidence and explicitly prospective development, not new claims.
add(14,0,2.7,['03_postreopen_memory'],'Conservar experiencia','Retaining experience',tag='Montaje de ensayos / Trial montage',new=True)
add(14,2.7,5.0,['05_L03_472'],'Revisarla','Revising it',tag='U0 · revisión / revision',new=True)
add(14,5.0,7.1,['06_product'],'Combinarla','Combining it',tag='CPC9 · composición / composition',new=True)
add(14,7.1,10.0,['07_later_full'],'Utilizar información','Using information',tag='IC01 · comunicación / communication',new=True)
add(14,10.0,18.7,['13_principal_region_2'],'Una base para investigar','A basis for research',phase='Aplicaciones y ventajas: por evaluar',phaseen='Applications and advantages: to be evaluated',tag='Desarrollo / Development',classification='Registro',new=True)
add(14,18.7,23.8,['13_principal_region_1'],'DEE Cognitive','Capacidades demostradas · Demonstrated capabilities',phase='Un sistema inteligente en desarrollo',phaseen='An intelligent system in development',tag='ECI02 · principal',classification='Registro')
add(14,23.8,29,['13_principal_region_1'],'Investigar · Reproducir · Desarrollar','Investigate · Reproduce · Develop',tag='DEE Cognitive 2.0',classification='Registro',push=True)

SHOTS.sort(key=lambda s:s['start'])
assert SHOTS[0]['start']==0 and SHOTS[-1]['end']==300
assert all(abs(a['end']-b['start'])<1e-8 for a,b in zip(SHOTS,SHOTS[1:]))
for i,s in enumerate(SHOTS):s['id']=f'S{s["scene"]:02}_{i+1:03}'

if __name__=='__main__':
 (HERE/'PLAN_3D_14_ESCENAS.json').write_text(json.dumps({'scope':'Native1080;recorded sites;editorial time;no DEE evolution',
 'official_windows':[{k:b[k] for k in ('block','start_s','end_s','literal_ES')} for b in SCENES],
 'shots':SHOTS},ensure_ascii=False,indent=2),'utf8')
 print('Plan:',len(SHOTS),'shots;',len(CASES),'available archived case views;300s')
