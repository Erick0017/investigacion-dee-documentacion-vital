"""CPC5 acquired-direction regulation: archived fields only, no DEE imports.

Editorial progress chooses observed stages. It never advances a participant,
moves a cell between samples, or substitutes an observer score for DEE output.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'evidencia_regulacion/CPC5_REGULACION_DATOS_EXACTOS.json'

@lru_cache(maxsize=1)
def evidence():return json.loads(DATA.read_text(encoding='utf8'))

@lru_cache(maxsize=1)
def data_sha():return hashlib.sha256(DATA.read_bytes()).hexdigest()

def arm(name):return evidence()['cases'][name]

def frame(name,tick):
    return next(f for f in arm(name)['frames']if f['tick']==tick)

def source(name,pointer):
    a=arm(name)
    return {**a['source'],'case_id':name,'life':name,
        'organization':'Finite CPC5 experimental apparatus; not E1 or U0',
        'N':a['N'],'translation':a['translation'],'control_mode':a['mode'],
        'pointer':pointer,'extraction_path':str(DATA),'extraction_sha256':data_sha()}

def bounds(site,zminus=.9,zplus=.9):
    return [[site[0]-.9,site[1]-.9,site[2]-zminus],
            [site[0]+.9,site[1]+.9,site[2]+zplus]]

def pulse_panel(name,label):
    f=frame(name,3);q=deepcopy(f['observations']['nominal_regulator_segment'])
    q['role']='difference'
    return {'N':67,'tick':3,'points':[q],'label':label,
        'bounds':bounds(q['site']), 'direction_sites':[q['site']],
        'source':source(name,'/frames/1/forms/nominal_regulator_segment'),
        'entry_receipts':deepcopy(arm(name)['entry_receipts']),
        'same_current_external_resource_schedule_as_controls':True,
        'annotation':'Arrow displays the recorded direction, not a tracked trajectory.'}

def contact_panel(name,tick,label):
    a=arm(name);f=frame(name,tick)
    meeting=f['observations']['regulation_meeting']['site']
    if tick in (292,293):
        context=next(c for c in a['contact_contexts']if c['tick']==tick)
        # The visible axis is an explicit crop of retained dense field data.
        pts=[deepcopy(p)for p in context['points']if p['site'][:2]==meeting[:2]]
        ps='/contact_contexts/'+str(a['contact_contexts'].index(context))
        binding={'extraction_pointer':'/cases/'+name+ps,
            'raw_source':context['raw_source'],'clock_source':context['clock_source']}
    else:
        pts=[deepcopy(f['observations'][k])for k in ('regulation_meeting','nominal_regulator_segment')]
        binding={'source':f['source']}
    for p in pts:
        p['role']='site'
        # This specific location is a recorded matched-history difference.
        # It is not a claim to have found the whole memory or unique lineage.
        if tick==292 and p['site']==meeting and int(p['raw'])!=0:
            p['role']='difference'
    fi=next(i for i,v in enumerate(a['frames'])if v['tick']==tick)
    return {'N':67,'tick':tick,'points':pts,'label':label,
        'bounds':bounds(meeting,2.4,1.4),
        'direction_sites':[p['site']for p in pts if int(p['raw'])!=0],
        'source':source(name,'/frames/'+str(fi)+'/forms'),
        'sample_context':binding,'crop_notice':True,
        'coverage':'Same fixed ROI for T290..293; only existing observations, no interpolation.'}

def function_panel(name,label):
    a=arm(name);reader=deepcopy(a['qualified_readers']['Flat'])
    q=deepcopy(reader['observations']['function']);q['role']='reader'
    return {'N':67,'tick':q['tick'],'points':[q],'label':label,
        'bounds':bounds(q['site']), 'reader_sites':[q['site']],
        'direction_sites':[q['site']] if int(q['raw']) else [],
        'bottom':'Con función'if reader['qualified_function']else'Sin función',
        'reader_evidence':{'observations':reader['observations'],
            'function_contract':reader['function_contract'],
            'qualified_function':reader['qualified_function'],
            'pointer':'/cases/'+name+'/qualified_readers/Flat',
            'scope':'Function availability from the frozen physical reader. The external5/4 utility is deliberately not displayed as a DEE output.'},
        'source':source(name,'/captures/Flat/function')}

def finish(m,shot):
    m['shot_id']=shot;m['scene_id']='S10'
    m['source_refs']=[p['source']for p in m['panels']]
    m['source_extraction_sha256']=data_sha()
    m['new_DEE_ticks']=0
    m['limitations']=[
        'CPC5RegulationSession is a separate finite experimental profile, not the current E1 or U0 guards.',
        'History changes an acquired direction. Geometry, input schedule and regulatory opportunity remain prepared.',
        'No learned initiative, utility-selected timing, general attention or indefinitely reusable regulator is shown.',
        'Cuts join recorded stages; unobserved intervals and identity after encounters are not reconstructed as measured trajectories.',
        '5/4 is an external sum of resource/function qualifications; no energy, intelligence score or native answer5/4 is rendered.']
    return m

def model(shot_id,progress):
    aliases={'S10_P01':'S10.1','S10_P02':'S10.2','S10_P03':'S10.3'}
    shot=aliases.get(shot_id,shot_id)
    if not 0<=progress<=1:raise ValueError('Progress outside editorial shot')
    p=min(.999999,progress)
    if shot=='S10.1':
        other='REG_OPPOSITE'if p<.62 else'REG_UNPAIRED'
        m={'title':'Pulso adquirido','evidence_type':'Registro',
            'notice':'T3 · Historias distintas','footer':'La experiencia cambia la dirección',
            'panels':[pulse_panel('REG_PAIRED','Emparejadas'),
                      pulse_panel(other,'Opuestas'if other=='REG_OPPOSITE'else'Desacopladas')],
            'phase':'paired_vs_opposite'if p<.62 else'paired_vs_unpaired'}
    elif shot=='S10.2':
        if p<.7:
            # Stable view and literal cuts across the four retained frontiers.
            tick=(290,291,292,293)[min(3,int(p/.7*4))]
            m={'title':'Encuentro registrado','evidence_type':'Etapas',
                'notice':'T'+str(tick)+' · Recorte ampliado',
                'footer':'Mismas oportunidades posteriores',
                'panels':[contact_panel('REG_PAIRED',tick,'Emparejadas'),
                          contact_panel('REG_UNPAIRED',tick,'Desacopladas')],
                'phase':'contact_T'+str(tick),'stage_jump':True}
        else:
            translated=p>=.86
            left='REG_RESERVED_TRANSLATION'if translated else'REG_PAIRED'
            right='REG_OPPOSITE'if translated else'REG_UNPAIRED'
            m={'title':'Efecto funcional','evidence_type':'Etapas',
                'notice':'Salto a T437'+(' · Reserva traducida'if translated else''),
                'footer':'Lectores fijados antes de evaluar',
                'panels':[function_panel(left,'Reserva'if translated else'Emparejadas'),
                          function_panel(right,'Opuestas'if translated else'Desacopladas')],
                'phase':'qualified_function_reserved'if translated else'qualified_function',
                'stage_jump':True}
    elif shot=='S10.3':
        pp=contact_panel('REG_PAIRED',292,'Regulación local')
        meeting=frame('REG_PAIRED',292)['observations']['regulation_meeting']['site']
        pp['bounds']=bounds(meeting,.8,1.8)
        m={'title':'Regulación local','evidence_type':'Registro',
            'notice':'Mismo encuentro · T292',
            'footer':'Ruta y oportunidad preparadas'if p<.5 else'Dirección adquirida por experiencia',
            'panels':[pp],'phase':'prepared_opportunity'if p<.5 else'acquired_direction',
            'explanation':'The same observed contact is reused to distinguish designed opportunity from acquired direction; these are not two different worlds.'}
    else:raise KeyError(shot_id)
    return finish(m,shot)
