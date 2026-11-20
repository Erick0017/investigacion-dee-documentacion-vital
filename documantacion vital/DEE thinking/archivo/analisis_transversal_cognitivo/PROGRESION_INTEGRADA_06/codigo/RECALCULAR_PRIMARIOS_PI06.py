"""Standalone documentary PI06 verifier: extraction-relative files, stdlib only.

It never follows recorded source/directory/primary paths, imports DEE, advances
a world or reproduces an experiment. Expected values are auditor checks only.
"""
from pathlib import Path
from array import array
from collections import Counter,defaultdict
import argparse,hashlib,json,sys,zlib

def digest(b):return hashlib.sha256(b).hexdigest()
def local(root,relative):
    relative=Path(relative)
    if relative.is_absolute()or '..'in relative.parts:raise ValueError('Extraction-relative paths only')
    p=(root/relative).resolve(strict=True)
    if not p.is_relative_to(root):raise ValueError('No outside source path')
    for node in(p,*p.parents):
        if node==root.parent:break
        if node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024:raise ValueError('No linked evidence path')
    return p
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def observation(o):
    v=int(o['raw'])
    if not 0<=v<2**64:raise ValueError('Exact RAW uint64 required')
    ds=[(v>>k)&15 for k in(48,52,56)]
    return {'state':v&0xffffffff,'semantic':v>>60,'s_reg':(v>>32)&65535,
            'direction':[x-16 if x&8 else x for x in ds]}
def decode_early(o):
    r=observation(o);x,y,z=r['direction']
    return x if r['state']>0 and r['semantic']==1 and x in(-1,0,1)and y==1 and z in(0,-1)else None
def decode_six(reader):
    os=reader.get('observations')
    if not isinstance(os,list)or len(os)!=6:raise ValueError('All six fixed late observations must be included')
    expected={(15+2*x,17,15+2*z):(x,1,z)for x in(-1,0,1)for z in(0,-1)}
    found=[];sites=set()
    for o in os:
        site=tuple(o['site']);sites.add(site)
        if site not in expected:raise ValueError('Late fixed observation site changed')
        r=observation(o);direction=expected[site]
        if r['state']>0 and r['semantic']==1 and r['direction']==list(direction):found.append(direction[0])
    if sites!=set(expected):raise ValueError('Duplicate/missing late sites')
    return found[0]if len(found)==1 else None
def receipts(requests):
    unique={}
    for r in requests:
        rid=r['id'];receipt=r['receipt']
        if receipt['id']!=rid:raise ValueError('Receipt identity differs')
        if rid in unique and unique[rid]!=receipt:raise ValueError('Conflicting current Native alias')
        unique[rid]=receipt
    return unique
def C2C_requests(row):
    return [*row['requests'],*row['native_arithmetic']['native_operation']['native_trial']['requests'],
            *row['second_native_use']['requests']]
def fine_buffers(root,relative):
    base=local(root,relative);cfg=read(local(root,Path(relative)/'CAPTURA.json'))
    rows=[json.loads(x)for x in local(root,Path(relative)/'FRAMES.jsonl').read_text(encoding='utf8').splitlines()if x]
    index=read(local(root,Path(relative)/'INDEX.json'))
    if cfg['N']!=67 or rows!=index['frames']:raise ValueError('Fixed complete fine frame/index contract')
    size=16*67**3;previous=None;counts=[]
    for i,row in enumerate(rows):
        if row['sequence']!=i or Path(row['file']).name!=row['file']:raise ValueError('Invalid frame sequence')
        compressed=local(root,Path(relative)/row['file']).read_bytes()
        if len(compressed)!=row['compressed_bytes']or digest(compressed)!=row['compressed_sha256']:raise ValueError('Frame compressed hash mismatch')
        dec=zlib.decompressobj();payload=dec.decompress(compressed,size+1)
        if len(payload)!=size or not dec.eof or dec.unconsumed_tail or digest(payload)!=row['payload_sha256']:raise ValueError('Bounded frame payload mismatch')
        if row['kind']=='anchor':complete=payload
        elif row['kind']=='xor_uint64'and previous is not None and row['previous_sequence']==i-1:
            # Bytewise XOR via bounded Python integers; same published uint64
            # wire format. Every resulting RAW/clocks hash is verified below.
            complete=(int.from_bytes(payload,'little')^int.from_bytes(previous,'little')).to_bytes(size,'little')
        else:raise ValueError('Broken frame chain')
        raw=complete[:size//2];clock=complete[size//2:]
        if digest(complete)!=row['complete_buffers_sha256']or digest(raw)!=row['RAW_sha256']or digest(clock)!=row['clocks_sha256']:raise ValueError('Exact reconstructed buffers mismatch')
        a=array('Q');a.frombytes(raw)
        if sys.byteorder!='little':a.byteswap()
        counts.append({'tick':row['tick'],'RAW_nonzero_support':sum(v!=0 for v in a)})
        previous=complete
    return counts

def main(a):
    root=Path(a.raiz).resolve(strict=True);index=read(local(root,'04_EVIDENCIAS/CONTROL/INDICE_PRIMARIOS_PI06.json'))
    if index['schema']!='DEE.PI06.portable_primary_selection.v1':raise ValueError('Exact portable input selection required')
    material_ticks=0;native_by_life=defaultdict(dict);intervals=defaultdict(list);families=defaultdict(list);fi_checks=[];C2C=None;fine=None
    for member in index['primaries']:
        p=local(root,Path('04_EVIDENCIAS/PRIMARIOS')/member['file']);data=p.read_bytes()
        if len(data)!=member['bytes']or digest(data)!=member['sha256']:raise ValueError('Selected primary changed: '+member['file'])
        t=json.loads(data)
        if t['status']!='completed'or t.get('error')is not None:raise ValueError('Ambiguous/failed transport is not accepted as a material record')
        actual=json.loads(t['result'])if isinstance(t['result'],str)else t['result']
        payload=json.loads(t['payload'])if isinstance(t['payload'],str)else t['payload']
        literal=payload['situaciones'][0];rows=actual['result']['rows']
        if len(rows)!=1:raise ValueError('One material operation per selected transport')
        row=rows[0];life=actual['committed_snapshot']['life_id'];before=actual['before_tick'];after=actual['after_tick']
        if after<before:raise ValueError('No rewind in evidence')
        material_ticks+=after-before;intervals[life].append((before,after,t['id']))
        requests=row.get('requests',[])
        if literal['modo']=='eci01-pi04-c2c-oportunidad':requests=C2C_requests(row)
        unique=receipts(requests)
        for rid,r in unique.items():
            if rid in native_by_life[life]and native_by_life[life][rid]!=r:raise ValueError('Contradictory current receipt across operations')
            native_by_life[life][rid]=r
        if literal['modo']=='eci01-pi06-fiplus':
            q=row['calendar']['query_tick'];legacy=row['legacy_result'];early=decode_early(legacy['early_observation']);late=decode_six(legacy['original_result']['native_trial']['reader'])
            if early!=row['early_physical_choice']or late!=row['old_q6_choice']or legacy['early_tick']!=q+4:raise ValueError('Fixed-reader RAW recount differs')
            if legacy['original_result']['native_trial']['read_tick']!=q+6:raise ValueError('Old late read timing changed')
            if len(unique)!=176+int(literal['condicion']!='intacto'):raise ValueError('Current FI receipt count differs')
            statuses=Counter(x['status']for x in unique.values())
            if statuses.get('applied',0)!=row['Native_inputs']['applied']:raise ValueError('FI admission summary differs')
            entry={'transport_id':t['id'],'q':q,'q4':early,'q6':late,'Native_inputs':dict(statuses),'condition':literal['condicion'],
                   'public_operands':[literal['izquierda'],literal['derecha']],'NULL_is_not_zero':True}
            fi_checks.append(entry);families[member['family']].append(entry)
        if literal['modo']in('eci01-pi06-ambiente-fino','eci01-pi06-control67','eci01-pi06-ambiente'):
            statuses=Counter(x['status']for x in unique.values());birth=row['birth_inputs']
            if len(unique)!=birth['unique_requested']or dict(statuses)!=birth['status_counts']:raise ValueError('Actual birth receipts differ')
            if literal['modo']=='eci01-pi06-ambiente-fino':
                obs=row['host_safety_observations'];cross=[x for x in obs if x['RAW_nonzero_support']>3000]
                if not cross or cross[0]!=obs[-1]or any(y['tick']-x['tick']!=1 for x,y in zip(obs,obs[1:])):raise ValueError('Fine first-crossing stop rule differs')
                fine={'actual_counts':obs,'first_above_limit':cross[0],'previous':obs[-2],'births':dict(statuses),'elapsed_ticks':after-before}
        if literal['modo']=='eci01-pi04-c2c-oportunidad':
            numeric_reader=row['native_arithmetic']['numeric_reader'];obs=observation(numeric_reader['observation']);actual_number=obs['s_reg']-numeric_reader['representation_bias']
            if obs['state']==0 or obs['semantic']!=1 or obs['direction']!=[1,-1,-1]or actual_number!=row['actual_numeric_result']:raise ValueError('Actual Native numeric transduction mismatch')
            second=decode_six(row['second_native_use']['reader'])
            values=[r.get('value')for r in row['second_native_use']['requests']if r.get('channel')=='MU.current.datum']
            if values!=[actual_number]or second!=row['second_motor']or row['applied_route']!=second:raise ValueError('Actual arithmetic value was not transported to the second Native function')
            product=row['actual_effect']['product'];binary=local(root,'04_EVIDENCIAS/PRIMARIOS/PI06_CONTROL67_C2C_0028.bin').read_bytes()
            if len(binary)!=64 or digest(binary)!=product['sha256']or int.from_bytes(binary[:2],'little')!=actual_number:raise ValueError('Actual useful external product differs')
            if len(unique)!=186 or any(x['status']!='applied'for x in unique.values()):raise ValueError('C2C direct Native counts differ')
            C2C={'actual_numeric_result_from_RAW':actual_number,'second_Native_choice_from_RAW':second,'product_bytes':len(binary),'product_sha256':digest(binary),
                'Native_inputs_unique':len(unique),'actual_ticks':after-before,'prospective_step_bound':800,
                'actual_over_bound':after-before>800,'excess_ticks':after-before-800,'useful_product':row['useful_product'],
                'scope':'An actual useful old assisted chain; campaign finite-bound failure remains preserved.'}
    for life,values in intervals.items():
        values.sort()
        if any(b[0]<a[1]for a,b in zip(values,values[1:])):raise ValueError('Same-life Native intervals overlap; do not double count')
    expected={'dev_izq0':[-1,1,-1],'dev_none':[1,1,1],'dev_sham':[1,1,1],'dev_right':[-1,1,1],
              'reserve_izq7_11':[-1,1,-1],'reserve_none_11':[1,1,1],'cut_contraflow':[1],'cut_sham':[-1],
              'RP600':[-1,1,-1],'control67':[1]}
    series={}
    for name,sequence in expected.items():
        actual=sorted(families[name],key=lambda x:x['q']);q4=[r['q4']for r in actual];q6=[r['q6']for r in actual]
        if q4!=sequence or q6!=sequence:raise ValueError('Fixed observed sequence differs: '+name)
        series[name]={'q4':q4,'q6':q6,'q':[r['q']for r in actual]}
    native_status=Counter(x['status']for rows in native_by_life.values()for x in rows.values())
    if material_ticks!=7882 or len(intervals)!=12 or len(fi_checks)!=24:raise ValueError('Final Native clock/world/FI coverage differs')
    if native_status!={'applied':4533,'rejected_occupied':6}:raise ValueError('Fresh direct receipt denominators differ')
    if fine is None or C2C is None:raise ValueError('Required negative/functional witnesses missing')
    if a.captura_fina:
        reconstructed=fine_buffers(root,a.captura_fina)
        if reconstructed!=fine['actual_counts']:raise ValueError('Threshold differs from actual frozen full RAW buffers')
        fine['full_RAW_threshold_recomputed']=True
    else:fine['full_RAW_threshold_recomputed']=False;fine['scope']='Primary observer counts recounted; full global buffers not reopened by this invocation.'
    result={'schema':'DEE.PI06.portable_documentary_recalculation.v1','Native_executed':False,'DEE_imports':False,
        'experiment_reproduced':False,'Native_ticks_from_actual_material_intervals':material_ticks,'worlds':len(intervals),
        'FI_fixed_RAW_reader_checks':len(fi_checks),'fixed_sequences':series,'direct_current_Native_receipts':dict(native_status),
        'receipt_scope':'Sum of fresh operations within twelve paired histories; shared prefix is not independent experience. Aliases deduplicated only within each life.',
        'fine_threshold':fine,'control_C2C':C2C,
        'functional_limits':['Reproduced expected wrong FI signs are not functional successes.',
            'Coarse/fine safety stops contain no later cognitive test.',
            'The control useful product does not erase the prospective time-bound violation.',
            'Nothing here demonstrates acquired regulation, autonomous recovery or a new principal.']}
    out=Path(a.salida).absolute()
    if out.exists():raise FileExistsError('New documentary result only')
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'result':str(out),'sha256':digest(out.read_bytes()),'Native_ticks':material_ticks,'worlds':len(intervals),
        'FI_RAW_checks':len(fi_checks),'Native_receipts':dict(native_status),'Native_executed':False}))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--raiz',required=True);ap.add_argument('--salida',required=True)
    ap.add_argument('--captura-fina',help='Optional extraction-relative complete fine capture folder')
    main(ap.parse_args())
