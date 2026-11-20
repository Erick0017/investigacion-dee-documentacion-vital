"""R12 shot models from already recorded cases. No DEE import or evolution."""
from pathlib import Path
from functools import lru_cache
from copy import deepcopy
import gzip,hashlib,json
from visual_r12 import digest

ROOT=Path(__file__).resolve().parents[1]
TITLES={
'S01':'DEE Cognitive','S02':'Un mundo que procesa','S03':'Continuar la misma historia',
'S04':'Memoria que puede utilizarse','S05':'Revisar sin empezar de nuevo',
'S06':'Combinar y reutilizar','S07':'Información de otro participante',
'S08':'Consultar ante una diferencia','S09':'Consecuencias y respuestas',
'S10':'Regular una interferencia','S11':'Señales con una función',
'S12':'Transferir e integrar','S13':'Capacidades en la instancia',
'S14':'Inteligencia en desarrollo'}

@lru_cache(maxsize=1)
def data():return json.loads((ROOT/'evidencia_reutilizada/REUSO_R12_DATOS.json').read_text(encoding='utf8'))
@lru_cache(maxsize=1)
def principal():return json.loads(gzip.decompress((ROOT/'evidencia_reutilizada/PRINCIPAL_R08_DATOS_EXACTOS.json.gz').read_bytes()))
@lru_cache(maxsize=1)
def mechanisms():return json.loads((ROOT/'evidencia_reutilizada/FUENTES_MECANISMOS_S06_S11_R08.json').read_text(encoding='utf8'))
@lru_cache(maxsize=1)
def comparison_data():return json.loads((ROOT/'evidencia_reutilizada/COMPARACION_PRINCIPAL_R12.json').read_text(encoding='utf8'))
@lru_cache(maxsize=1)
def interventions():return json.loads((ROOT/'evidencia_reutilizada/INTERVENCIONES_R12.json').read_text(encoding='utf8'))
def phase(p,n=3):return min(n-1,int(max(0,min(.999999,p))*n))
def old(case,shot,index=0):return deepcopy(data()['cases'][case][shot][index])
def adapt(row,labels=None,notice='Intervalo documentado',footer='',category='Etapas'):
    m=deepcopy(row);m['evidence_type']=category;m['notice']=notice;m['footer']=footer
    m['source_extraction_sha256']=row.get('extraction_sha256')
    if labels:
        for pan,lab in zip(m['panels'],labels):pan['label']=lab
    return m
def scheme(kind,p,footer='',notice=''):
    return {'scheme':{'kind':kind},'phase':phase(p),'evidence_type':'Esquema',
            'notice':notice,'footer':footer,'panels':[],
            'limitations':['Prepared explanatory drawing, not a DEE observation or scientific trial.']}

def principal_reader(name,label='Instancia del corte',closeup=False):
    e=principal()['reader_panels'][name]
    sites=e['reader_sites'];center=sites[0]
    pts=[deepcopy(v)for v in e['points']if all(abs(a-b)<=3 for a,b in zip(v['site'],center))]
    coords=[v['site']for v in pts]+sites+[e['input_site']]
    b=[[min(v[i]for v in coords)-.8 for i in range(3)],[max(v[i]for v in coords)+.8 for i in range(3)]]
    if closeup:
        b=[[x-1.4 for x in center],[x+1.4 for x in center]]
        pts=[v for v in pts if all(a<=x<=z for a,x,z in zip(b[0],v['site'],b[1]))]
        assert pts
    result={'N':e['N'],'tick':e['tick'],'points':pts,'reader_sites':sites,'direction_sites':sites,
            'bounds':b,'camera_azimuth_degrees':45,'label':label,
            'output_text':'+' if e['output']>0 else '-' if e['output']<0 else '0',
            'reader_evidence':{'source':e['source'],'pointer':e['source_pointer']+'/reader',
                               'contract':e['reader_contract'],'observed_result':e['output']},
            'source':{'path':e['source']['resolved_source'],'sha256':e['source']['sha256'],
                      'pointer':e['source_pointer'],'life':'ECI02_CIERRE_CANDIDATA_01',
                      'published_as':'ECI02_OPERATIVA_PRINCIPAL_01','parent':'ECI02_CONSOLIDADA_OPERATIVA'},
            'input_receipts':e['input_receipts']}
    if not closeup:result['input_site']=e['input_site']
    return result

def comparison_social():
    m=adapt(old('IC01_communication','S08_P03'),['Mensaje recibido','Mensaje cortado'],
            footer='El mensaje cambia el uso posterior')
    for panel in m['panels']:
        r=panel['reader_evidence']
        good=[x for x in r['physical_social_readings']if x['qualified']]
        if good:
            sign=good[0]['prepared_gain1_command']
            panel['output_text']='+' if sign>0 else '-'
            panel['reader_evidence']={'original':r,'qualified_physical_social_output':sign,
                'scope':'Native social sign. External torque sum deliberately not displayed as native sign.'}
        else:
            panel['output_text']=None;panel['bottom']='Sin lectura'
            panel['reader_evidence']={'original':r,'scope':'Neither social bank qualifies; not zero and not negation.'}
    return m

def comparison_principal():
    v=comparison_data();point=deepcopy(v['point']);point['role']='reader';site=point['site']
    return {'N':v['N'],'tick':v['tick'],'points':[point],'reader_sites':[site],
        'direction_sites':[site],'label':'Comparación',
        'bounds':[[x-1.1 for x in site],[x+1.1 for x in site]],
        'output_text':'+'if v['choice']>0 else'-'if v['choice']<0 else'0',
        'reader_evidence':{'source':v['source'],'contract':v['reader_contract'],
                           'qualified_choice':v['choice'],'query_tick':v['query_tick']},
        'source':v['source'],'input_receipts':v['input_receipts']}

def composition(p,control=False):
    if control:
        if p<1/3:
            m=adapt(old('CPC9_composition','S07_P01'),['Dos aportes'],
                    notice='Intervención diagnóstica',footer='Se retira una contribución en una copia')
            right=deepcopy(m['panels'][0]);right['label']='Uno retirado'
            record=interventions()['CPC9'];edit=record['intervention'];site=edit['victim']['site']
            assert edit['new_raw']=='0'and edit['clock_preserved']
            for point in right['points']:
                if point['site']==site:
                    point.update(raw='0',state=0,s_reg=0,semantic=0,direction=[0,0,0],active=False,role='control')
            right['difference_sites']=[site];right['source']=record['source']
            right['diagnostic_edit_record']=edit
            m['panels'].append(right)
            m.setdefault('limitations',[]).append('Recorded external diagnostic edit, not an autonomous DEE removal or inferred global poststate.')
            return m
        m=adapt(old('CPC9_composition','S07_P04'),['Con dos aportes','Sin un aporte'],
                footer='El corte cambia la consecuencia')
        if p>=2/3:
            records=mechanisms()['cases']['CPC9_COMPOSITION']['data']['conditions']
            index=next(i for i,x in enumerate(records)if x['condition']=='sham_formed206')
            sham=records[index];point=deepcopy(sham['consequence210']);point['role']='reader'
            panel=deepcopy(m['panels'][0]);panel['label']='Control sham';panel['points']=[point]
            panel['source']={'path':str(ROOT/'evidencia_reutilizada/FUENTES_MECANISMOS_S06_S11_R08.json'),
                'sha256':hashlib.sha256((ROOT/'evidencia_reutilizada/FUENTES_MECANISMOS_S06_S11_R08.json').read_bytes()).hexdigest(),
                'pointer':f'/cases/CPC9_COMPOSITION/data/conditions/{index}'}
            assert sham['baseline_qualified_consequence_present']
            panel['reader_evidence']={'record':point,'condition':sham['condition'],
                'intervention_pre_tick':sham['pre_tick'],'intervention_new_raw':sham['new_raw'],
                'clock_preserved':sham['clock_preserved'],'source':panel['source']}
            panel['output_text']=str(point['s_reg']);m['panels'][1]=panel
            m['notice']='Corte y sham separados';m['footer']='Sham: se reescribe el mismo estado'
        return m
    i=phase(p)
    row=old('CPC9_composition',['S07_P01','S07_P02','S07_P03'][i])
    return adapt(row,[['Dos contribuciones','Producto formado','Uso posterior'][i]],
                 footer='Etapas del mismo mundo')

def model(shot_id,p):
    p=max(0,min(.999999,float(p)));scene=shot_id.split('.')[0];part=int(shot_id.split('.')[1])
    if scene in ['S04','S05','S08','S11']:
        from escenas_u0_r12 import model as u0
        m=u0(shot_id,p)
    elif scene=='S10':
        from escena_regulacion_r12 import model as reg
        m=reg(shot_id,p)
    elif scene=='S01':
        if part==1:m=scheme('universe',p,'Inteligencia en desarrollo')
        elif part==2:
            if p<.5:m={'panels':[principal_reader('LEX_luma','Memoria utilizada')],
                'evidence_type':'Etapas','notice':'Primer ensayo','footer':'Asociación conservada en su trayectoria'}
            else:m=adapt(old('IC01_communication','S08_P02',1),['Mensaje utilizado'],notice='Otro ensayo',footer='Un mensaje influye después')
        else:m=scheme('universe',p,'Lugar · Entrada · Lectura')
    elif scene=='S02':
        if part==1:m=scheme('site_state',p)
        elif part==2:m=composition(p)
        else:
            m=adapt(old('CPC9_composition','S07_P02'),['Transformación registrada'],
                     footer='Estados e interacciones del modelo')
    elif scene=='S03':
        if part==1:
            names=['LEX_luma','MA_PRE','LUMA_POST']
            pan=principal_reader(names[phase(p)],'Misma trayectoria')
            m={'panels':[pan],'evidence_type':'Etapas','notice':'Cortes reales','footer':'La historia no empieza de nuevo'}
        elif part==2:
            m=adapt(old('ECI02_principal','S11_P04',0 if p<.5 else 1),
                ['Estado guardado'if p<.5 else'Mismo estado'],notice='Guardado y reapertura',
                footer='Se conservan estado, colas y contexto')
        else:
            # A reprise of the actual recorded use, not a newly invented query
            # after the final restore. Explicitly labelled on screen.
            pan=principal_reader('MA_PRE','Uso registrado')
            m={'panels':[pan],'evidence_type':'Etapas','notice':'Antes del guardado mostrado',
               'footer':'Contenido utilizado en esta trayectoria',
               'limitations':['This archived request precedes the final save/reopen. No new post-restore event is claimed.']}
    elif scene=='S06':m=composition(p,control=(part==2))
    elif scene=='S07':
        if part==1:
            stages=[old('IC01_communication','S08_P01',0),old('IC01_communication','S08_P01',1),old('IC01_communication','S08_P02',1)]
            m=adapt(stages[phase(p)],[['Origen','Recepción','Uso del receptor'][phase(p)]],footer='Contenido recibido y utilizado')
        elif part==2:
            if p<1/3:
                panels=[];refs=[]
                for arm,label in [('full','Mensaje'),('cut','Corte material')]:
                    row=interventions()['IC01']['observed_ports'][arm]
                    pt=deepcopy(row['point']);pt['role']='input'if arm=='full'else'control'
                    s=pt['site'];src={**row['source'],'pointer':row['source_pointer']}
                    panels.append({'N':row['N'],'tick':pt['tick'],'points':[pt],
                        'label':label,'bounds':[[v-1.1 for v in s],[v+1.1 for v in s]],
                        'direction_sites':[s],'source':src,
                        'bottom':'Campo observado'if arm=='full'else'Intervención'})
                    refs.append(src)
                m={'panels':panels,'evidence_type':'Etapas','notice':'Intervención registrada',
                   'footer':'Corte material sobre la comunicación','source_refs':refs,
                   'limitations':['Separate cut admission receipts were not retained. SEM4 is directly observed at the port in the cut control.',
                                  'Only these observed cells are shown; no invisible interception trajectory is interpolated.']}
            else:
                m=comparison_social();m['notice']='Contraste causal'
        else:
            m=adapt(old('IC01_communication','S08_P02',1),['Uso posterior'],footer='Participantes y canal definidos')
    elif scene=='S09':
        if part in [1,2]:
            idx=phase(p) if part==1 else (1 if p<.45 else 2)
            m=adapt(old('CYCLE02_consequence','S09_P01',idx),['Con retorno','Sin retorno'],
                    notice='Historias emparejadas',footer='La consecuencia cambia una referencia')
        else:
            k=phase(p)
            row=old('ENTE01_external','S09_P03',0) if k==0 else old('ENTE01_external','S09_P03',1)if k==1 else old('ENTE01_external','S09_P04')
            m=adapt(row,[['Salida DEE','Estado DEE','Retorno a DEE'][k]],
                    notice='Otro ensayo',footer='Servicio y puente externos preparados')
            m['external_service_stage']=k
            m['external_service_record']=mechanisms()['cases']['ENTE01_RETURN']['data']['environment_after']
            # Schematic service bridge appears in an explicit separate region
            # only if the renderer supports it, never as a DEE cell.
    elif scene=='S12':
        if part==1:
            m=adapt(old('ENTE02_transfer','S10_P02',0 if p<.75 else 1),['Con experiencia','Control'],
                    footer='Primera acción, antes del retorno'if p<.75 else'Retorno posterior documentado')
        elif part==2:
            m=adapt(old('ENTE02_transfer','S10_P04'),['Con experiencia','Control'],
                    notice='Regla ambiental opuesta',footer='La historia puede perjudicar')
        else:
            m=adapt(old('FI01_many_contributions','S11_P01',phase(p)),['Entrada original','Cambia una'],
                    notice='Otro ensayo',footer='127 de 128 entradas permanecen iguales')
    elif scene=='S13':
        if part==1:
            k=phase(p)
            pan=principal_reader('LEX_luma','Asociación',True)if k==0 else principal_reader('MA_PRE','Memoria utilizada',True)if k==1 else comparison_principal()
            m={'panels':[pan],'evidence_type':'Etapas','notice':'Continuidad propia',
               'footer':'Accesos preparados · historia adquirida'}
        elif part==2:m=scheme('layers',p,'Un mismo proyecto, funciones distintas')
        else:
            m=adapt(old('ECI02_principal','S11_P04',0 if p<.5 else 1),
                    ['Guardado'if p<.5 else'Reabierto'],notice='Instancia principal',
                    footer='Integración parcial, no repertorio total')
    elif scene=='S14':
        if part==1:
            if p<1/3:m={'panels':[principal_reader('MA_PRE','Memoria utilizada')],
                'evidence_type':'Etapas','notice':'Ensayo identificado','footer':'Conservar y utilizar'}
            elif p<2/3:m=composition((p-1/3)*3)
            else:
                from escenas_u0_r12 import model as u0
                m=u0('S08.2',(p-2/3)*3);m['notice']='Otro ensayo'
        elif part==2:m=scheme('future',p,'Posibilidades que requieren pruebas')
        else:m=scheme('close',p,'Investigar · Reproducir · Desarrollar')
    else:raise KeyError(shot_id)
    m['title']=TITLES[scene];m['scene_id']=scene;m['shot_id']=shot_id
    m.setdefault('limitations',[])
    if m.get('evidence_type')=='Esquema':
        m.setdefault('evidence_bindings',[])
    else:
        m.setdefault('evidence_bindings',[])
        for x in [m.get('source')]+list(m.get('source_refs')or[])+[pan.get('source')for pan in m.get('panels',[])]:
            if x and x not in m['evidence_bindings']:m['evidence_bindings'].append(deepcopy(x))
    physical=[]
    for pan in m.get('panels',[]):
        physical.append({'N':pan.get('N'),'tick':pan.get('tick'),
            'observations':[{k:v for k,v in pt.items()if k in ['site','raw','clock','state','s_reg','semantic','direction','tick','active']}for pt in pan.get('points',[])]})
    m['physical_data_sha256']=digest(physical)if physical else None
    return m
