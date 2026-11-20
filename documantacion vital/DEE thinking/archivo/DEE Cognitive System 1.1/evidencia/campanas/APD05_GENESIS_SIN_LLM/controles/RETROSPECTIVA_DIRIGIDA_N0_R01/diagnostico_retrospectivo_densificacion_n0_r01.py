"""Directed APD04 primary re-reading. Standard library only; zero new ticks.

Exports only sources needed for the identified historical contrasts, rather
than another corpus inventory. A local frame is not global occupancy evidence.
"""
from pathlib import Path
from array import array
from collections import Counter
import argparse
import gzip
import hashlib
import json
import shutil
import sys
import zlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=ROOT/'evidencia/campanas/APD05_GENESIS_SIN_LLM/controles/RETROSPECTIVA_DIRIGIDA_N0_R01'
APD04=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_bytes())
def write(p,v):
    with Path(p).open('x',encoding='utf8',newline='\n')as f:
        json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False); f.write('\n')


def recurse(x,path='$'):
    yield path,x
    if isinstance(x,dict):
        for k,v in x.items(): yield from recurse(v,path+'.'+k)
    elif isinstance(x,list):
        for k,v in enumerate(x): yield from recurse(v,path+'['+str(k)+']')


def recalc(folder):
    index=read(folder/'INDICE_FUENTES.json'); checks=[]; objects={}
    for item in index['files']:
        source=folder/item['exported']
        if sha(source)!=item['exported_sha256']: raise ValueError('Exported bytes changed')
        data=gzip.decompress(source.read_bytes()) if item['encoding']=='gzip_exact_source_bytes' else source.read_bytes()
        if hashlib.sha256(data).hexdigest()!=item['source_sha256']: raise ValueError('Original source bytes changed')
        objects[item['id']]=json.loads(data); checks.append(item['id'])
    a=objects['A_C_MATCHED_INPUTS']; contexts=objects['C_CONTEXTS']; fields_index=objects['C_FIELD_INDEX']
    metrics=[]
    for row in fields_index['fields']:
        item=next(x for x in index['arrays'] if x['file']==row['file'])
        compressed=(folder/item['exported']).read_bytes()
        if hashlib.sha256(compressed).hexdigest()!=row['sha256']: raise ValueError('Array bytes changed')
        data=zlib.decompress(compressed); n=row['N']; count=n**3
        if len(data)!=count*16: raise ValueError('Array dimensions changed')
        if hashlib.sha256(data[:count*8]).hexdigest()!=row['decoded_RAW_sha256']: raise ValueError('RAW changed')
        if hashlib.sha256(data[count*8:]).hexdigest()!=row['decoded_clocks_sha256']: raise ValueError('clocks changed')
        raw=array('Q'); raw.frombytes(data[:count*8]); clocks=array('Q');clocks.frombytes(data[count*8:])
        if sys.byteorder!='little': raw.byteswap();clocks.byteswap()
        state=Counter(x&0xffffffff for x in raw)
        actual={'tick':row['tick'],'sites':count,'occupied':count-state[0],
                'RAW_nonzero':sum(bool(x)for x in raw),
                'state_zero_RAW_nonzero':sum(bool(x)and not x&0xffffffff for x in raw),
                'max_s_reg':max((x>>32)&65535 for x in raw),
                'clock_nonmatching_tick':sum(x!=row['tick']for x in clocks)}
        for key in ('occupied','RAW_nonzero','state_zero_RAW_nonzero','max_s_reg'):
            if actual[key]!=row['metrics'][key]: raise ValueError('Metric changed: '+key)
        metrics.append(actual)
    work=objects['R04_WORK03']; frame=work['result']['rows'][0]['rows'][0]['native_return']['frames'][0]
    occupied=[x for x in frame['all_three_potential_trace_sites'] if int(x['raw'])&0xffffffff]
    local_tick=frame['tick']
    rejects=[]
    for path,node in recurse(work):
        if isinstance(node,dict) and isinstance(node.get('receipt'),dict) and node['receipt'].get('status')=='rejected_occupied':
            r=node['receipt']; rejects.append({'id':r['id'],'requested_tick':r['requested_tick'],'channels':r['channels'],'locator':path+'.receipt'})
    unique={r['id']:r for r in rejects}; rejects=sorted(unique.values(),key=lambda x:(x['requested_tick'],x['id']))
    goal=objects['R04_GOAL1']; low=goal['result']['final']['physical']
    high=work['result']['final']['physical']
    if low['tick']!=653846 or low['occupied']!=89 or high['tick']!=655722 or high['occupied']!=297699:
        raise ValueError('R04 global bracket differs from primaries')
    if local_tick!=655704 or len(occupied)!=3: raise ValueError('R04 local witness differs')
    earliest=min(x['requested_tick']for x in a['receipt_status_differences'])
    changed=[x['C_input']['tick']for x in a['input_spec_differences']]
    return {'schema':'APD05.retro.directed.recalculation.N0.R01','Native_ticks':0,'source_checks':checks,
      'C_exact_global_fields':metrics,
      'A_C':{'query_ticks_A':a['query_ticks_A'],'query_ticks_C':a['query_ticks_C'],
             'same_query_calendar':a['query_ticks_A']==a['query_ticks_C'],
             'final_A':a['A_final'],'final_C':a['C_final'],'clocks_equal_at_648684':a['A_final']['clocks_sha256']==a['C_final']['clocks_sha256'],
             'changed_sensor_input_ticks':changed,'earliest_different_rejected_input_tick':earliest,
             'last_changed_sensor_input_already_later_than_first_rejection':changed[-1]>earliest,
             'attribution_limit':'The two earlier changed sensory payloads alter both symmetry and dose. The third changed payload was rejected after the first measured failure, so cannot be its initial cause. No pre-every-input full snapshot exists in this evidence.'},
      'R04':{'last_exact_global_low':low,'first_exact_global_high_in_selected_primaries':high,
             'global_first_densification_tick':'NOT_RESOLVED; bracket (653846,655722]',
             'local_frame_tick':local_tick,'local_three_sites':occupied,'selected_work_rejected_requests':rejects,
             'local_witness_precedes_first_rejected_clear':local_tick<min(x['requested_tick']for x in rejects),
             'attribution_limit':'T655704 is a local three-site obstruction witness, not a global occupancy measurement or a proved onset. T655705/717 rejected clearing inputs cannot explain occupation already measured at655704. This does not identify its source or rule out earlier interactions.'},
      'complete_recovery_parent':objects['ADVERSE_PAIR_LOCATOR']['pair']['directory'],
      'rest_and_maintenance_limits':'The paired adverse state can be used for a recovery experiment. Sparse healthy-prefix forks are prevention. No implicit memory destruction, energy, death or validated restorative maintenance follows from occupancy or these observations.'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path);parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    if args.root:
        result=recalc(args.root); write(args.out,result); print(json.dumps({'Native_ticks':0,'sources':len(result['source_checks'])})); return
    if OUT.exists(): raise FileExistsError('Never overwrite retrospective extraction')
    OUT.mkdir(parents=True); (OUT/'PRIMARIOS').mkdir()
    service=ROOT/'sistema/estado/servicios_persistentes/APD04_CONTINUABLE_R01/resultados'
    sources={
      'A_C_MATCHED_INPUTS':APD04/'C_DENSIFICACION_CONTEXTOS_R02_N0/CONTRASTE_A_C_PRIMERAS6_T648684_N0.json',
      'C_CONTEXTS':APD04/'C_DENSIFICACION_CONTEXTOS_R02_N0/RECALCULO_CONTEXTOS_N0.json',
      'C_FIELD_INDEX':APD04/'C_DENSIFICACION_CONTEXTOS_R02_N0/INDICE_CAMPOS.json',
      'R04_GOAL1':service/'apd04continuable_r04_goal1_r01.json',
      'R04_WORK03':service/'apd04continuable_r04_work03_r01.json',
      'ADVERSE_PAIR_LOCATOR':APD04/'SELLO_CONTINUABLE_T658754_ADVERSO_N0_R01/CORTE_COMPLETO_POSTSTOP.json'}
    rows=[]
    for key,source in sources.items():
        target=OUT/'PRIMARIOS'/(key+'.json.gz'); target.write_bytes(gzip.compress(source.read_bytes(),mtime=0))
        rows.append({'id':key,'source':str(source),'source_sha256':sha(source),'source_bytes':source.stat().st_size,
                     'exported':target.relative_to(OUT).as_posix(),'exported_sha256':sha(target),'encoding':'gzip_exact_source_bytes'})
    arrays=[]
    for row in read(sources['C_FIELD_INDEX'])['fields']:
        source=sources['C_FIELD_INDEX'].parent/row['file']; target=OUT/'PRIMARIOS'/row['file']; shutil.copy2(source,target)
        arrays.append({'file':row['file'],'source':str(source),'sha256':sha(source),'exported':target.relative_to(OUT).as_posix()})
    write(OUT/'INDICE_FUENTES.json',{'files':rows,'arrays':arrays,'scope':'Exact targeted originals, not complete snapshot backups.'})
    shutil.copy2(__file__,OUT/Path(__file__).name)
    result=recalc(OUT); write(OUT/'RECALCULO_N0.json',result)
    write(OUT/'MANIFIESTO.json',{'Native_ticks':0,'members':[{'file':q.relative_to(OUT).as_posix(),'bytes':q.stat().st_size,'sha256':sha(q)}for q in sorted(OUT.rglob('*'))if q.is_file()]})
    print(json.dumps({'out':str(OUT),'sources':len(rows),'arrays':len(arrays),'Native_ticks':0}))


if __name__=='__main__':main()
