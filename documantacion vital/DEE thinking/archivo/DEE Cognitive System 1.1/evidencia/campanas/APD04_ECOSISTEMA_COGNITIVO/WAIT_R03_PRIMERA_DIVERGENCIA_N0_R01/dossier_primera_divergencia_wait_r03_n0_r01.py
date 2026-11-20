"""Zero-tick global RAW/clocks audit after the first ACT_R03 consequence.

The exported arrays are exact primary field extractions, NOT complete worlds
or operational continuation checkpoints. No external reader informs a life.
"""
import argparse
from array import array
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys


def sha(value):return hashlib.sha256(value).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def emit(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
def rawfields(raw):
    def signed(s):v=(raw>>s)&15;return v-16 if v&8 else v
    return {'raw':str(raw),'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,
        'semantic':(raw>>60)&15,'direction':[signed(s)for s in(48,52,56)]}
def unpack(path):
    data=gzip.decompress(Path(path).read_bytes());a=array('Q');a.frombytes(data)
    if sys.byteorder!='little':a.byteswap()
    return data,a


def recalculate(folder):
    index=read(folder/'INDICE_PRIMARIOS.json');arrays={}
    for branch,info in index['branches'].items():
        arrays[branch]={}
        for field,item in info['arrays'].items():
            path=folder/item['file'];encoded=path.read_bytes();data,a=unpack(path)
            if sha(encoded)!=item['encoded_sha256']or sha(data)!=item['exact_field_sha256']:raise ValueError('Exact extracted field differs.')
            arrays[branch][field]=a
    N=index['N'];real=arrays['REAL'];omit=arrays['OMIT'];differences=[]
    for i,(r,o)in enumerate(zip(real['RAW'],omit['RAW'])):
        if r!=o:
            differences.append({'site':[i//(N*N),(i//N)%N,i%N],
                'REAL':rawfields(r),'OMIT':rawfields(o),'REAL_clock':str(real['clocks'][i]),'OMIT_clock':str(omit['clocks'][i])})
    return {'schema':'APD04.ACT_R03.first_consequence.global_field_contrast.N0.v1',
        'tick':index['tick'],'N':N,'RAW_differences':differences,
        'RAW_difference_count':len(differences),'clocks_exactly_equal':real['clocks']==omit['clocks'],
        'cells_examined':len(real['RAW']),'new_native_ticks':0,
        'scope':'Full RAW/clocks comparison of existing saved post-first-op snapshots; field arrays are not complete causal/operational states. No selective intervention or unique-mechanism claim.'}


def export(root):
    system=root/'sistema';ev=root/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
    out=ev/'WAIT_R03_PRIMERA_DIVERGENCIA_N0_R01'
    if out.exists():raise FileExistsError('Preserve the existing dossier; do not overwrite.')
    observer=load('wait_r03_first_consequence_pure_snapshot',system/'capacidades/observador_causal_retrospectivo_01.py')
    out.mkdir();branches={};tick=None;N=None;contexts={}
    for branch in('REAL','OMIT'):
        life='APD04_WAIT_R03_'+branch+'_AUX_R05';folder=out/branch;folder.mkdir()
        source_primary=system/'estado/servicios_persistentes'/life/'resultados'/('apd04_wait_'+branch.lower()+'_r02_opportunity_01.json')
        primary=read(source_primary);actual_tick=primary['after_tick']
        candidates=list((system/'estado/checkpoints').glob(life+'.T'+str(actual_tick)+'.*.deetsnap.gz'))
        if len(candidates)!=1:raise ValueError('Ambiguous saved first-op state; no favorable checkpoint is selected.')
        source=candidates[0];snapshot=observer.Snapshot(source,verify_checksum=False)
        physical=primary['result']['final']['physical']
        assert snapshot.tick==actual_tick and observer.sha(observer.pbytes(snapshot.raw))==physical['RAW_sha256']
        assert observer.sha(observer.pbytes(snapshot.clocks))==physical['clocks_sha256']
        if tick is not None:assert tick==snapshot.tick and N==snapshot.N
        tick=snapshot.tick;N=snapshot.N;members={}
        for name,values in(('RAW',snapshot.raw),('clocks',snapshot.clocks)):
            data=observer.pbytes(values);encoded=gzip.compress(data,mtime=0);target=folder/(name+'.u64le.gz')
            with target.open('xb')as stream:stream.write(encoded)
            members[name]={'file':target.relative_to(out).as_posix(),'encoded_sha256':sha(encoded),
                'exact_field_sha256':sha(data),'encoded_bytes':len(encoded),'decoded_bytes':len(data)}
        primary2=system/'estado/servicios_persistentes'/life/'resultados'/('apd04_wait_'+branch.lower()+'_r02_opportunity_02.json')
        for source_p in(source_primary,primary2):shutil.copy2(source_p,folder/source_p.name)
        r1=primary['result']['rows'][0]['rows'][0];r2=read(primary2)['result']['rows'][0]['rows'][0]
        contexts[branch]={'first_query_tick':r1['selection']['query_tick'],'first_raw_components':r1['raw_sensor_components'],
            'first_choice':r1['selection']['physical_choice'],'first_effect':r1['committed_effect'],
            'first_feedback':r1['feedback'],'second_query_tick':r2['selection']['query_tick'],
            'second_raw_components':r2['raw_sensor_components'],'second_public':r2['public_before'],
            'second_choice':r2['selection']['physical_choice'],'second_effect':r2['committed_effect'],
            'Native_channels':snapshot.channels,'Native_pending':snapshot.pending,
            'phase_exact':snapshot.phase,'next_event_id':snapshot.next_event_id,'next_sequence':snapshot.next_sequence}
        branches[branch]={'snapshot_source':source.relative_to(root).as_posix(),'snapshot_sha256':snapshot.encoded_sha256,
            'primary_after_tick':actual_tick,'physical_from_primary':physical,'arrays':members,
            'partial_not_continuable':True,'internal_FNV_not_recomputed':True}
    emit(out/'INDICE_PRIMARIOS.json',{'N':N,'tick':tick,'branches':branches,'new_native_ticks':0,
        'no_Runtime_created':True,'scope':'Exact extracted RAW/clocks only, not complete snapshots or states of operational queues.'})
    real=contexts['REAL'];omit=contexts['OMIT']
    emit(out/'CONTEXTO_CAUSAL.json',{'REAL':real,'OMIT':omit,
        'first_choice_and_sensor_equal':real['first_choice']==omit['first_choice']and real['first_raw_components']==omit['first_raw_components'],
        'second_q_sensor_public_equal':all(real[k]==omit[k]for k in('second_query_tick','second_raw_components','second_public')),
        'interfaces_pending_phase_equal':all(real[k]==omit[k]for k in('Native_channels','Native_pending','phase_exact')),
        'only_experimental_intervention':'Generic first-postaction FAILURE return present versus omitted, fixed in the literal protocol before outcomes.',
        'not_unique_microcausal_proof':'No new selective cut/sham was run; full metadata, receipt IDs and operational identities are not asserted equal. No global P2 or production-utility claim.'})
    shutil.copy2(__file__,out/Path(__file__).name);result=recalculate(out);emit(out/'RECALCULO_GLOBAL.json',result)
    emit(out/'MANIFIESTO.json',{'members':[{'file':p.relative_to(out).as_posix(),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}
        for p in sorted(out.rglob('*'))if p.is_file()]})
    print(json.dumps({'out':str(out),'manifest_sha256':sha((out/'MANIFIESTO.json').read_bytes()),
        'RAW_difference_count':result['RAW_difference_count'],'clocks_exactly_equal':result['clocks_exactly_equal'],
        'differences':result['RAW_differences'],'new_native_ticks':0},ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--export-root',type=Path);mode.add_argument('--recalculate',type=Path)
    args=parser.parse_args()
    if args.export_root:export(args.export_root.resolve(strict=True))
    else:print(json.dumps(recalculate(args.recalculate.resolve(strict=True)),ensure_ascii=False))
