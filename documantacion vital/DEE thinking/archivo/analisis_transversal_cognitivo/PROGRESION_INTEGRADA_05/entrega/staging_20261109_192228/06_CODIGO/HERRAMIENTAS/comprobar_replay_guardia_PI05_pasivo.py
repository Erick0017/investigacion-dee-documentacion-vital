"""Compare actual closed Cognitive RP replay with the original guard, no DEE."""
from pathlib import Path
import hashlib,importlib.util,json
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';D=P/'estados/REPLAY_RP_GUARD_R01'
def read(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def diff(a,b,path=()):
    if type(a)is not type(b):return [list(path)]
    if isinstance(a,dict):
        out=[]
        for k in sorted(set(a)|set(b)):
            out+=diff(a.get(k),b.get(k),path+(k,))
        return out
    if isinstance(a,list):
        if len(a)!=len(b):return [list(path)+['length']]
        return sum((diff(x,y,path+(i,))for i,(x,y)in enumerate(zip(a,b))),[])
    return []if a==b else[list(path)]
def main():
    sp=importlib.util.spec_from_file_location('PI05_replay_frozen_parser',RP/'observador_pasivo.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    context=read(D/'CONTEXTO_EJECUCION.json');result=read(D/'RESULTADO_REPRODUCCION.json');life=result['life']
    assert result['status']=='COMPLETED'and result['owner_closed_coherently']and result['criteria_met']
    card=read(D/'sistema/estado/vidas'/life/'VIDA.json');replay=D/'sistema'/card['snapshot'];original=P/'pares/GUARD_POSTFI_T818074/VIDA.deetsnap.gz'
    a=m.snapshot_view(original);b=m.snapshot_view(replay)
    primary=P/'control/PI05_GUARD_FI_GLOBAL_R01.json';op=read(primary);oa=op['actual']['result']['rows'][0]
    replayprimary=D/result['rows'][0]['primary'];r=read(replayprimary);ra=json.loads(r['result'])['result']['rows'][0]
    equality={'N_tick_RAW_clocks':a['physical']==b['physical'],'full_causal_prefix_including_interfaces_pending_and_receipts':a['causal_prefix_sha256']==b['causal_prefix_sha256'],
        '177_exact_request_and_receipt_objects':oa['requests']==ra['requests'],'same_fixed_q4_answer':oa['early_physical_choice']==ra['early_physical_choice'],
        'same_fixed_q6_answer':oa['old_q6_choice']==ra['old_q6_choice'],'same_fixed_calendar':oa['calendar']==ra['calendar']}
    def frames(row):
        cap=row['external_global_capture'];index=Path(cap['directory'])/'INDEX.json';assert sha(index)==cap['index_sha256']
        return [(x['tick'],x['RAW_sha256'],x['clocks_sha256'])for x in read(index)['frames']]
    equality['all69_complete_frame_RAW_and_clock_hashes']=frames(oa)==frames(ra)
    changed=[]
    for key in sorted(set(a['metadata'])|set(b['metadata'])):
        av=a['metadata'].get(key);bv=b['metadata'].get(key)
        if av==bv:continue
        try:paths=diff(json.loads(av),json.loads(bv))
        except Exception:paths=[['ENCODED_VALUE']]
        changed.append({'key':key,'changed_JSON_paths':paths,'before_encoded_sha256':hashlib.sha256((av or'').encode()).hexdigest(),
            'after_encoded_sha256':hashlib.sha256((bv or'').encode()).hexdigest(),
            'classification':'system_or_service_transport_metadata'if key==m.SYSTEM_KEY or key==m.SERVICE_KEY or key.startswith(m.SERVICE_KEY+'.queue.')else'needs_explicit_review_not_globally_ignored'})
    proof={'schema':'DEE.PI05.Cognitive_RP_guard.actual_passive_comparison.R01','Native_executed_by_this_comparison':False,'new_ticks':0,
        'replay_life':life,'actual_replay_status':result['status'],'actual_fixed_local_criteria':result['criteria_met'],
        'actual_replay_Native_ticks':result['last_tick']-817876,'actual_replay_inputs':result['native_receipts'],
        'original_complete_pair_snapshot':{'file':str(original),'sha256':sha(original)},'replay_snapshot':{'file':str(replay),'sha256':sha(replay)},
        'original_primary':{'file':str(primary),'sha256':sha(primary)},'replay_primary':{'file':str(replayprimary),'sha256':sha(replayprimary)},
        'equalities':equality,'all_physical_and_input_equalities_hold':all(equality.values()),'metadata_differences':changed,
        'encoded_snapshot_identity_claimed':False,'scope':'Actual Native reproduction from one shared complete prefix; not independent organism, acquisition replay, global cognitivePASS, promotion or equality of technical identity/wall logs.'}
    out=P/'control/FISICA_RP_GUARDIA_REPRODUCIDA_PI05_R01.json';assert not out.exists();out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
