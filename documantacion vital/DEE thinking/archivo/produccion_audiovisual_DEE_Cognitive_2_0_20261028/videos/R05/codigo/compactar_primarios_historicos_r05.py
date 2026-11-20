"""Select existing samples for 3D production; never advances physical state."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import struct
import zipfile

HERE=Path(__file__).resolve().parents[1]
DIR=HERE/'datos/primarios_historicos_R05'
OUT=HERE/'datos/evidencia_fundamentos_R05.json'

def read(name):
    b=(DIR/name).read_bytes()
    return json.loads(gzip.decompress(b) if name.endswith('.gz') else b)

def observations(value):
    """Keep all supplied nonzero RAW observations, including state0."""
    result=[]
    def walk(v, path=''):
        if isinstance(v,dict):
            if 'site' in v and 'raw' in v:
                if int(v['raw']): result.append({'pointer':path,**v})
            else:
                for k,x in v.items(): walk(x,path+'/'+str(k))
        elif isinstance(v,list):
            for i,x in enumerate(v): walk(x,path+'/'+str(i))
    walk(value)
    return result

def npy(z,name):
    b=z.read(name+'.npy'); assert b[:8]==b'\x93NUMPY\x01\x00'
    n=struct.unpack('<H',b[8:10])[0]; h=ast.literal_eval(b[10:10+n].decode('ascii'))
    assert h['descr']=='<u8' and not h['fortran_order']
    return h['shape'],struct.unpack('<'+str((len(b)-10-n)//8)+'Q',b[10+n:])

def main():
    d=json.loads(OUT.read_text(encoding='utf8'));sc=d['scenes']
    ing=read('NRD05.json'); case=ing['executed_cases']['SEPARATED_S0']; frames=[]
    with zipfile.ZipFile(DIR/'NRD05_ORIGINAL.npz') as z:
        for stage,tick in [('D0',8),('D64',72)]:
            shape,a=npy(z,'SEPARATED_S0_'+stage+'_W00_raw_a'); _,b=npy(z,'SEPARATED_S0_'+stage+'_W10_raw_a')
            _,ca=npy(z,'SEPARATED_S0_'+stage+'_W00_clock_a');_,cb=npy(z,'SEPARATED_S0_'+stage+'_W10_clock_a');n=shape[0]
            points=[]
            for i,(x,y) in enumerate(zip(a,b)):
                if x or y:
                    points.append({'xyz':[i//n//n,(i//n)%n,i%n],'without_history_raw':str(x),
                                   'with_history_raw':str(y),'without_history_clock':str(ca[i]),
                                   'with_history_clock':str(cb[i]),'raw_different':x!=y})
            frames.append({'stage':stage,'tick':tick,'points':points,'global_RAW_difference_sites':sum(x!=y for x,y in zip(a,b))})
    sc['S05_ING05']={'case':'NRD05/SEPARATED_S0','N':23,'representation':'A',
                    'label':'Registros DEE · Ingeniería05', 'frames':frames,
                    'E1_touched':case['E1_touched']['W10'],'E1_direct_route':case['E1_direct_route'],
                    'E2_touched':case['E2_touched']['W11'],'E2_direct_route':case['E2_direct_route'],
                    'direct_routes_disjoint':case['direct_routes_disjoint'],
                    'retained_conditioning':case['retained_conditioning'],
                    'limits':['Displayed difference sites are historical state differences, not individually established memory sites.',
                              'The finite factorial demonstrates changed later processing. No word content or autonomous retrieval is identified.',
                              'Only two retained cuts are visualized; no invented intermediate frames or connections.']}
    sc['S06_M014']={}
    for kind,name in [('AB','M014_AB.json'),('BA','M014_BA.json')]:
        q=read(name);sc['S06_M014'][kind]={'case':q['case'],'geometry':q['geometry'],
            'primary_observations':q['primary_observations'],'trace':q['trace'],
            'limits':'Prepared order and routing geometries differ. A finite order-sensitive composition, not abstract ANTES or an addition permutation.'}
    # IC01: exact sampled read points, not inferred identity from equal load.
    thinking=HERE.parents[3]
    ic_path=thinking/'archivo/DEE Cognitive System 1.1/evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01/LATE_SOCIAL_OPPOSITE_166.json'
    ib=ic_path.read_bytes();ic=json.loads(ib)['result']
    sc['S07_IC01']['source_primary']={'path':str(ic_path),'sha256':hashlib.sha256(ib).hexdigest(),'pointer':'/result'}
    sc['S07_IC01']['plan']=ic['new_social_progress']['plan']
    sc['S07_IC01']['passive_local_frames']=[{'tick':f['tick'],'observations':observations(f['ports'])}
                                           for f in ic['passive_frames'] if 16563<=f['tick']<=16619]
    cp=read('CPC9_RET_D01_P.json')
    sc['S07_CPC9']={'case':'CPC9/RET_D01_P','N':cp['geometry']['N'],'representation':'A',
                    'geometry':cp['geometry']['cpc9_return'],
                    'frames':[{'tick':f['tick'],'observations':observations({'magnitude_transfer':f['magnitude_transfer'],'return':f['return']})}
                              for f in cp['frames'] if 143<=f['tick']<=225],
                    'input_reference':31,'private_first_object':18,
                    'limits':['Show first positive material message and its retained later use only.',
                              'Later B reader inputs at213/280 were rejected; they do not establish successful updates.',
                              'These are local observed sites, not a global trajectory or two complete minds.']}
    pt=read('C02_COMMIT_340_PROTEGIDO.json.gz');pr=pt['data']['result']
    sc['S08_PROTECTION']={'case':'C02_COMMIT_340_PROTEGIDO','life':pt['life'],'N':67,
                         'representation':'A for sampled points; B for frozen input positions',
                         'prepared_inputs':pr['protection_requests'],
                         'frames':[{'tick':f['tick'],'observations':observations({k:f.get(k) for k in ('B','ports','social','answer')})}for f in pr['frames']],
                         'initial':pr['initial'],'final':pr['final'],'scope':pr['scope'],
                         'limits':['The counterflow is prepared, not acquired regulation. No deletion or invisible shield.']}
    sc['S08_TRANSFER']={}
    for label,name in [('T','28T_TRANSFER.json.gz'),('U','28U_TRANSFER.json.gz')]:
        q=read(name)['result']['result'];rows=[]
        for x in q['rows']:
            rows.append({'domain':x['domain'],'public_raw':x['row']['public_raw'],'start_tick':x['row']['start_tick'],
                         'reader_tick':x['reader']['source_tick'],'native_command':x['formed_native_command'],
                         'own_before':x['before']['own'],'own_after':x['after']['own'],'job_completed':x['job_completed'],
                         'frames':[{'tick':f['tick'],'observations':observations(f)} for f in x['frames']],
                         'transaction_completed':x.get('local_service',{}).get('observed',{}).get('transaction_completed')})
        sc['S08_TRANSFER'][label]={'case':'EO02/28'+label+'_TRANSFER','rows':rows,'contract':q['contract'],
                                 'completed_transactions':q['final']['service']['environments']['transaccion']['completed_transactions']}
    cp=read('CP02_REPORT.json.gz')['native']['cases']
    sc['S10_CP02']={'case':'CP02/gate_open/paired-versus-none','representation':'A for local fields; C for external habitat schematic',
                   'cases':[{k:x[k] for k in ['gate','history','emission','outcome']}for x in cp if x['gate'] and x['history']in('paired','none')],
                   'limits':['Learned correspondence concerns retained past gate outcome class; no general forecasting claim.',
                             'T70 is an independent external habitat outcome, not an input revealing the target to DEE.']}
    pen=read('PENS01_HA_INTACT.json')
    sc['S10_PENS01']={'case':'PENSAMIENTO01/HA_INTACT','representation':'A', 'geometry':pen['geometry'],
                     'trace':pen['trace'],'measured':pen['measured'],'post_t0_host_writes':pen['post_t0_host_writes'],
                     'limits':['Finite prepared supplies and opportunities, native dependent transformations. No perpetual loop.',
                               'HA/HB do not isolate last-event identity from order; no abstract order cognition claim.']}
    # NumPy is only a reader of archived arrays, not the DEE engine.
    import numpy as np
    cuts=[]
    with np.load(DIR/'PENS01_HA_INTACT.npz',allow_pickle=False) as z:
        for tick in (6,12,38,58):
            raw=z[f't{tick}_raw'];clock=z[f't{tick}_clock']
            cuts.append({'tick':tick,'N':127,
                         'points':[{'xyz':[int(v) for v in q],'raw':str(int(raw[tuple(q)])),
                                    'clock':str(int(clock[tuple(q)]))} for q in np.argwhere(raw!=0)],
                         'RAW_sha256':hashlib.sha256(raw.tobytes(order='C')).hexdigest(),
                         'clocks_sha256':hashlib.sha256(clock.tobytes(order='C')).hexdigest()})
    sc['S10_PENS01']['physical_cuts']=cuts
    eci=thinking/'archivo/analisis_transversal_cognitivo/ECI01'
    recalc_path=eci/'recalculos/PRUEBA_GESTOR_FRIO_RECALCULO_R01.json'
    rc=json.loads(recalc_path.read_text(encoding='utf8'))
    proof=json.loads((eci/'datos/PRUEBA_GESTOR_FRIO_R01.json').read_text(encoding='utf8'))
    reopened=[]
    def find_reopened(v,path=''):
        if isinstance(v,dict):
            if v.get('site')==[15,15,15] and v.get('active') and int(v.get('tick',0))>713886:
                reopened.append({'pointer':path,**v})
            for k,x in v.items():
                if k not in ('data','buffers'):find_reopened(x,path+'/'+str(k))
        elif isinstance(v,list):
            for i,x in enumerate(v):find_reopened(x,path+'/'+str(i))
        elif isinstance(v,str) and v.startswith('{'):
            try: nested=json.loads(v)
            except ValueError:return
            find_reopened(nested,path+'(json)')
    find_reopened(proof['cycles'][1],'/cycles/1')
    sc['S05_REOPEN']={'source':str(recalc_path),'source_sha256':hashlib.sha256(recalc_path.read_bytes()).hexdigest(),
                     'original_proof_sha256':rc['source_sha256'],'life':rc['life'],
                     'pair_equality':rc['pair_equality'],'cycles':rc['cycles'],
                     'reopened_local_observations':reopened,
                     'scope':'Imported fork of the exact ALT export, with a separate ID. Nara/alfa were tested before export, not after this reopening.'}
    d['pending_here']=[]
    d['sources']+=json.loads((HERE/'datos/fuentes_historicas_R05.json').read_text(encoding='utf8'))['files']
    d['sources']=list({json.dumps(x,sort_keys=True,ensure_ascii=False):x for x in d['sources']}.values())
    tmp=OUT.with_suffix('.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(OUT)
    print(json.dumps({'file':str(OUT),'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'scenes':list(sc),'Native':0}))

if __name__=='__main__': main()
