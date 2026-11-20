"""Twelve frozen cloud frames: passive site transitions, no lineage or engine."""
from pathlib import Path
from array import array
from collections import Counter
import hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1]
OBSERVER=P.parents[2]/'DEE Cognitive 2.0/sistema/capacidades/observador_global_PI05_R01.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def site(i):return [i//(67*67),(i//67)%67,i%67]
def main():
    source=P/'ensayos/PI06_AMBIENTE_NUBE_R06_AMBIENTE_NUBE.json';transport=read(source)
    if transport['status']!='completed'or transport.get('error')is not None:raise ValueError('Closed known scientificresult only')
    row=json.loads(transport['result'])['result']['rows'][0];capture=row['external_global_capture']
    directory=Path(capture['directory']).resolve(strict=True)
    if not directory.is_relative_to(P.resolve())or sha(directory/'INDEX.json')!=capture['index_sha256']:raise ValueError('Exact captureindex only')
    spec=importlib.util.spec_from_file_location('PI06_cloud_stdlib_codec',OBSERVER)
    codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    frames=[];transitions=[];previous=None
    for frame in codec.iter_frames(directory):
        raw=array('Q');raw.frombytes(frame['raw_bytes'])
        if sys.byteorder!='little':raw.byteswap()
        support=sum(v!=0 for v in raw);active=sum((v&0xffffffff)>0 for v in raw)
        semantics=Counter(str(v>>60)for v in raw if v&0xffffffff)
        raw_semantics=Counter(str(v>>60)for v in raw if v)
        astate=Counter(str(v&0xffffffff)for v in raw if v&0xffffffff)
        stationary=sum((v&0xffffffff)>0 and ((v>>48)&4095)==0 for v in raw)
        frames.append({'tick':frame['tick'],'elapsed_from_initial':frame['tick']-row['before_tick'],
            'hashes':frame['hashes'],'RAW_nonzero_support':support,'state_positive_sites':active,
            'state0_nonzero_RAW':support-active,'active_SEM_counts':dict(sorted(semantics.items())),
            'RAW_support_SEM_counts':dict(sorted(raw_semantics.items())),
            'active_state_counts':dict(sorted(astate.items())),
            'active_direction_zero':stationary,'active_direction_nonzero':active-stationary,
            'maximum_s_reg_all_sites':max((v>>32)&65535 for v in raw),
            's_reg_sum_active_sites':sum((v>>32)&65535 for v in raw if v&0xffffffff)})
        if previous is not None:
            old_tick,old=previous;new_from_zero=0;new_from_inactive_raw=0;lost=0;retained=0;same_raw_active=0;changed_raw=0;examples=[]
            for i,(a,b)in enumerate(zip(old,raw)):
                aa=(a&0xffffffff)>0;bb=(b&0xffffffff)>0
                if a!=b:changed_raw+=1
                if aa and bb:
                    retained+=1
                    if a==b:same_raw_active+=1
                elif aa and not bb:lost+=1
                elif bb:
                    if a==0:new_from_zero+=1
                    else:new_from_inactive_raw+=1
                    if len(examples)<32:examples.append({'site':site(i),'old_RAW':str(a),'new_RAW':str(b),'new_SEM':b>>60})
            dt=frame['tick']-old_tick
            transitions.append({'from_tick':old_tick,'to_tick':frame['tick'],'elapsed_ticks':dt,
                'is_one_Native_step':dt==1,'RAW_changed_sites':changed_raw,
                'inactive_RAW0_to_active':new_from_zero,'inactive_nonzero_RAW_to_active':new_from_inactive_raw,
                'active_to_inactive':lost,'active_at_both_endpoints':retained,'active_same_RAW_at_both':same_raw_active,
                'new_active_site_examples_first32':examples,
                'same_site_is_not_unique_entity_survival':True,
                'gap_limit':'Endpoint differences only; no numberofintermediatebirths/deaths or hiddenlineage is inferred.'if dt!=1 else'One recordedNative boundary transition; inputs may also be admitted in thisstep.'})
        previous=(frame['tick'],raw)
    if len(frames)!=capture['captured_frames']:raise ValueError('Exhaustively decoded actualrecord length differs')
    first7=next((x['tick']for x in frames if x['active_SEM_counts'].get('7',0)>0),None)
    value={'schema':'DEE.PI06.cloud_growth.frozen_site_recount.R03',
        'source_primary':{'file':str(source),'sha256':sha(source)},'capture':capture,
        'actual_birth_inputs':row['birth_inputs'],'frames':frames,'transitions':transitions,
        'first_recorded_active_SEM7_tick':first7,'recorded_frames_exhaustively_verified':len(frames),
        'native_prefix_coverage':'Ticks0..10 and67, relative to826449; the10→67gap is not reconstructed.',
        'Native_executed':False,'new_Native_ticks':0,'new_queries':0,
        'limits':['Active-site growth is not demonstrated newknowledge, usefulmemory, learnedregulation or intelligentinitiative.',
            'Site activation and persistence are endpointdescriptors, not birth/survival counts of identifiableindividuals.',
            'SEM7count alone does not isolate XNOR, directedcopy or DEMUX; the frozenrules and localneighborhoods require separatecausalinterpretation.',
            'The host stopped at the first67ticksafety sample after exceeding3000RAWsupport. FI andC2C were notexecuted in thiscoarsecloudbranch.']}
    output=P/'control/CRECIMIENTO_NUBE_RECALCULADO_PI06_R03.json'
    with output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':output.name,'sha256':sha(output),'frames':len(frames),
        'counts':[{'elapsed':f['elapsed_from_initial'],'RAW':f['RAW_nonzero_support'],'active':f['state_positive_sites'],'SEM':f['active_SEM_counts']}for f in frames],
        'first_recorded_active_SEM7_tick':first7,'Native_executed':False}))
if __name__=='__main__':main()
