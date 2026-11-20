"""The exact closure trajectory published as principal; no MINUS substitution."""
from pathlib import Path
from copy import deepcopy
from functools import lru_cache
import gzip,hashlib,json
from render_r08 import data_hash

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'evidencia_principal/PRINCIPAL_R08_DATOS_EXACTOS.json.gz'

@lru_cache(maxsize=1)
def evidence():return json.loads(gzip.decompress(DATA.read_bytes()))

def reader_panel(name,label):
    e=evidence()['reader_panels'][name]
    center=e['reader_sites'][0]
    points=[deepcopy(v) for v in e['points'] if all(abs(a-b)<=3 for a,b in zip(v['site'],center))]
    assert points
    coords=[p['site'] for p in points]+[e['input_site']]+e['reader_sites']
    bounds=[[min(v[i] for v in coords)-.8 for i in range(3)],
            [max(v[i] for v in coords)+.8 for i in range(3)]]
    return {'N':e['N'],'tick':e['tick'],'points':points,'reader_sites':e['reader_sites'],'bounds':bounds,
            'label':label,'input_site':e['input_site'],'output_text':'+' if e['output']>0 else '-',
            'reader_evidence':{'source':e['source'],'pointer':e['source_pointer']+'/reader',
                               'formed_native_command':e['output'],'contract':e['reader_contract']},
            'direction_sites':e['reader_sites'],'camera_roll_degrees':0,'camera_azimuth_degrees':45}

def model(scene_id,shot_id,progress):
    if scene_id!='S11':raise KeyError(scene_id)
    p=max(0,min(.999999,float(progress)));e=evidence()
    if shot_id=='S11_P03':
        name='LEX_luma' if p<.52 else 'MA_PRE'
        row=e['reader_panels'][name]
        pp=reader_panel(name,'SEÑALES, MEMORIA Y COMPARACIÓN')
        m={'title':'INSTANCIA PRINCIPAL','panels':[pp],'bounds':pp['bounds'],
            'evidence_type':'Reconstrucción de etapas','stage_jump':True,'crop_notice':True,
            'source':{'case_id':'ECI02_closure_panel/'+name,
                'branch_id':'ECI02_CIERRE_CANDIDATA_01 → ECI02_OPERATIVA_PRINCIPAL_01',
                'parent_id':'ECI02_CONSOLIDADA_OPERATIVA','N':67,'ticks':[row['input_tick'],row['tick']],
                'source_path':row['source']['resolved_source'],'source_sha256':row['source']['sha256'],
                'json_pointer':row['source_pointer'],'input_receipts':row['input_receipts'],
                'reader_contract':row['reader_contract'],'fields_shown':['raw-derived cells','direction','qualified sign'],
                'ROI':'Reader local neighbourhood; its endpoint and entry coordinate, not an invented transit.',
                'supported_claim':'Inherited luma+ and acquired alpha- are used consecutively in the source trajectory later published as principal.',
                'limitations':e['limitations']}}
    elif shot_id=='S11_P04':
        stage='before' if p<.5 else 'after';s=e['save_restore_snapshots'][stage]
        # A displayed crop, not a claim that all information lives at this port.
        lo,hi=[39,3,42],[51,11,52]
        points=[deepcopy(v) for v in s['points'] if all(a<=b<=c for a,b,c in zip(lo,v['site'],hi))]
        assert points
        label='ESTADO GUARDADO' if stage=='before' else 'MISMO ESTADO RECUPERADO'
        m={'title':label,'panels':[{'N':67,'tick':s['tick'],'points':points,'label':'','camera_roll_degrees':90}],
           'bounds':[lo,hi],'evidence_type':'Reconstrucción de etapas','stage_jump':True,'crop_notice':True,
           'source':{'case_id':'ECI02_T727225_save_restore','branch_id':'ECI02_CIERRE_CANDIDATA_01',
               'published_as':'ECI02_OPERATIVA_PRINCIPAL_01','N':67,'ticks':[727225,727225],
               'source_path':s['source_path'],'source_sha256':s['source_sha256'],
               'fields_shown':['All nonzero RAW in the declared crop, including state0'],
               'ROI':[lo,hi],'reader_contract':None,'input_receipts':[],
               'supported_claim':'Same physical fields and operational protocol restored across the two archived processes; publication taught nothing.',
               'recomputed_equality':e['recomputed_save_restore_equality'],
               'limitations':['Selected region is a crop; equality was recomputed over complete worlds and relevant protocol fields.',
                   'No unrecorded post-restore action or newly generated future is shown.']}}
    else:raise KeyError(shot_id)
    m['source']['local_extraction_sha256']=hashlib.sha256(DATA.read_bytes()).hexdigest()
    m['source_data_hash']=data_hash({'panels':m['panels'],'source':m['source']})
    return m
