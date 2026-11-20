"""R08 S05/S12: explicit explanatory diagrams and cited reused records.

All physical displays delegate to the already verified case adapters. A
conceptual neuronal diagram is labelled C and never passed off as DEE data.
"""
from copy import deepcopy
from render_r08 import data_hash


def model(scene_id,shot_id,progress):
    from escenas_centrales_r08 import model as central
    p=max(0,min(.999999,float(progress)))
    if scene_id=='S05':
        if shot_id=='S05_P01':
            m=deepcopy(central('S02','S02_P03',p))
            m['title']='DEE TAMBIÉN ES SOFTWARE'
            m['panels'][0]['label']='CAMBIAN LOS ESTADOS'
        elif shot_id=='S05_P02':
            if p<.56:
                m={'title':'EJEMPLO NEURONAL: PARÁMETROS','panels':[],
                   'scheme':{'kind':'network','weight':round(3+7*p/.56),'phase':p/.56},
                   'evidence_type':'Esquema explicativo','source':{'case_id':'editorial_neural_mechanism',
                   'supported_claim':'Conceptual parameter adjustment; no comparative performance experiment.',
                   'limitations':['This diagram is explanatory C, not a recorded neural or DEE execution.']}}
            else:
                m=deepcopy(central('S02','S02_P03',(p-.56)/.44))
                m['title']='DEE: ESTADOS Y ENCUENTROS'
                m['panels'][0]['label']='CAMBIAN LOS ESTADOS'
        elif shot_id=='S05_P03':
            i=min(2,int(p*3));labels=['UNIVERSE: REGLAS','THINKING: EJECUCIÓN','COGNITIVE: ACCESO Y CONTINUIDAD']
            m={'title':labels[i],'panels':[],'scheme':{'kind':'layers','labels':labels,'active':i},
               'evidence_type':'Esquema explicativo','source':{'case_id':'software_architecture_C',
               'supported_claim':'Declared software layers, not the geometry of native matter.',
               'limitations':['Universe rules / Thinking execution / Cognitive operational access and continuity.']}}
        else:raise KeyError(shot_id)
    elif scene_id=='S12':
        if shot_id=='S12_P01':
            m=deepcopy(central('S02','S02_P03',p))
            m['title']='POSIBILIDADES DE DESARROLLO'
            m['panels'][0]['label']='EXPERIENCIA Y RESPUESTA'
        elif shot_id=='S12_P02':
            from escenas_mecanismos_r08 import model as historical
            m=deepcopy(historical('S06','S06_P02',.25))
            m['title']='POSIBLES DESARROLLOS'
            m['panels'][0]['label']='INVESTIGACIÓN EN CURSO'
        elif shot_id=='S12_P03':
            m=deepcopy(central('S02','S02_P04',.82))
            m['title']='UNA EXPERIENCIA CAMBIA EL PROCESAMIENTO'
            if m['panels']:m['panels'][0]['label']=''
        elif shot_id=='S12_P04':
            m=deepcopy(central('S02','S02_P04',.82))
            m['title']='DEE COGNITIVE 2.0'
            if m['panels']:m['panels'][0]['label']='INVESTIGACIÓN Y COLABORACIÓN'
        else:raise KeyError(shot_id)
        m.setdefault('source',{})['prospective_scope']='Future lines are prospects, not demonstrated commercial products.'
    else:raise KeyError(scene_id)
    m.setdefault('source',{})['editorial_scene']=scene_id
    m['source']['editorial_shot']=shot_id
    m['source_data_hash']=data_hash({k:v for k,v in m.items() if k not in ('title','source_data_hash')})
    return m
