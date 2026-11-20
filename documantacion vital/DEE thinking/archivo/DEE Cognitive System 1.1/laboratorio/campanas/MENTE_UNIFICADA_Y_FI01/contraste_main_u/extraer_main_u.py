"""Exact retrospective MAIN/U comparison, one loaded world, zero native ticks."""
import gc,gzip,hashlib,json,struct
from collections import Counter
from pathlib import Path
from dee_thinking.persistence import load_world_snapshot
from dee_thinking.consolidated import exact_receipt
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];EV=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01';OUT=EV/'contraste_main_u';CP=ROOT/'sistema/estado/checkpoints'
CASES=[('A33_MAIN_CONSECUENCIAS_PROPIAS','MU_MAIN.T14892.20fb96f88d97.deetsnap.gz','4ad31f5a6f34e9fecdac60f910f5c506ec34befdd0d512f58c155fb7894831d2',14892),('A41_U_IGUALAR_CONSULTA_PREACTUACION','MU_SELECTOR_RETURN_U.T14892.6158fefc83d2.deetsnap.gz','acbd9bd60530f11bd47a49b49027e0c4f15bc729f263cfe9c0733b14812a2db9',14892),('A42_MAIN_DOS_CONSECUENCIAS','MU_MAIN.T16033.63c9308cd9fd.deetsnap.gz','28a746cbfd5e8dfde7b1ef26cf2e7de5c899134117b02f573df8876a328f7540',16033),('A44_U_IGUALAR_EDAD','MU_SELECTOR_RETURN_U.T16033.9fa038ca533c.deetsnap.gz','becf5e60aedf9b48a0eba6242c8c2aeed853345f0b9daa07b8d8f0c21b007205',16033),('A45_MAIN_RESERVAS_UTILES','MU_MAIN.T16066.45026dec06c5.deetsnap.gz','b61b03602b2c98f0f05e49983513fa3a89717ee829501fcc4ddab8e579603ef8',16066),('A46_U_RESERVAS_UTILES','MU_SELECTOR_RETURN_U.T16066.039da88eadde.deetsnap.gz','9471100a4cec341c40d9b3f03e402032d1cd3319937dd4347af6792f79bff5de',16066)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(xs):return hashlib.sha256(b''.join(struct.pack('<Q',int(v))for v in xs)).hexdigest()
def public(x,depth=0):
    if x is None or isinstance(x,(str,int,float,bool)):return x
    if isinstance(x,bytes):return {'bytes_hex':x.hex()}
    if isinstance(x,dict):return {str(k):public(v,depth+1)for k,v in sorted(x.items(),key=lambda z:str(z[0]))}
    if isinstance(x,(tuple,list)):return [public(v,depth+1)for v in x]
    if hasattr(x,'name')and hasattr(x,'value')and isinstance(x.name,str)and isinstance(x.value,int):
        return {'type':type(x).__name__,'enum_name':x.name,'enum_value':int(x.value)}
    if depth>7:return {'type':type(x).__name__,'not_exported':'depthlimit'}
    values={}
    for k in dir(x):
        if k.startswith('_'):continue
        v=getattr(x,k)
        if not callable(v):values[k]=public(v,depth+1)
    return {'type':type(x).__name__,'fields':values}
def main():
    OUT.mkdir(parents=True,exist_ok=True);target=OUT/'MAIN_U_COMPLETO_T14892_T16033_T16066.json.gz'
    if target.exists():raise FileExistsError(target)
    worlds={}
    for case,name,expected,tick in CASES:
        p=CP/name;primary=EV/(case+'.json.gz');primarydata=json.loads(gzip.decompress(primary.read_bytes()));actual=sha(p)
        if actual!=expected:raise ValueError('Exact primary snapshot identity mismatch '+case)
        if case.startswith('A33'):
            ins=json.loads(primarydata['stderr'])['INSTRUMENTO'];reported=ins['recorded_failed_operation'];reported_tick=reported['tick'];reported_hash=reported['snapshot_sha256']
        else:
            reported=primarydata['result']['INSTRUMENTO'];reported_tick=reported['tick'];reported_hash=reported['snapshot_sha256']
        if reported_tick!=tick or reported_hash!=expected:raise ValueError('Do not silently equalize ticks '+case)
        w,proof=load_world_snapshot(p);before=int(w.runtime.current_tick)
        if before!=tick:raise ValueError('Snapshot currenttick differsfromprimary '+case)
        raw=[str(int(v))for v in w.runtime.raw_copy()];clocks=[str(int(v))for v in w.runtime.clock_copy()]
        receipts=w.runtime.receipts()if callable(w.runtime.receipts)else w.runtime.receipts;receipts=[exact_receipt(r)for r in receipts]
        metadata=dict(w.runtime.snapshot_metadata_entries);interfaces=[public(i)for i in w.interfaces];protocols=[public(i)for i in w.protocols]
        worlds[case]={'snapshot_path':str(p),'snapshot_sha256':actual,'snapshot_bytes':p.stat().st_size,'primary_path':str(primary),'primary_sha256':sha(primary),'primary_reported_tick':reported_tick,'load_proof':proof,'N':67,'tick_before':before,'tick_after':int(w.runtime.current_tick),'raw':raw,'clock':clocks,'raw_le_uint64_sha256':digest(raw),'clock_le_uint64_sha256':digest(clocks),'interfaces':interfaces,'protocols':protocols,'channel_names':sorted(w.runtime.channel_names),'receipts':receipts,'receipt_status_counts':dict(Counter(r['status']for r in receipts)),'unfinished_by_public_receipt_status':[r for r in receipts if r['status']not in('applied','rejected','cancelled','failed')],'snapshot_metadata_entries_exact':metadata,'coverage':'FullRAW/clocks; publicinterfaces/protocols/channels/receipts and exactsnapshotmetadata. Doesnotparseunexposedbinaryinternalsorcompareexternalfilesbycontent.'}
        del w,receipts;gc.collect()
    pairs=[]
    for i in(0,2,4):
        left,right=CASES[i][0],CASES[i+1][0];u,v=worlds[left],worlds[right];ri=[j for j,(a,b)in enumerate(zip(u['raw'],v['raw']))if a!=b];ci=[j for j,(a,b)in enumerate(zip(u['clock'],v['clock']))if a!=b]
        keys=sorted(set(u['snapshot_metadata_entries_exact'])|set(v['snapshot_metadata_entries_exact']))
        pairs.append({'left':left,'right':right,'same_age':u['tick_before']==v['tick_before'],'tick':u['tick_before'],'raw_differences':[{'index':j,'site':[j//4489,(j//67)%67,j%67],'left_raw':u['raw'][j],'right_raw':v['raw'][j]}for j in ri],'clock_differences':[{'index':j,'left_clock':u['clock'][j],'right_clock':v['clock'][j]}for j in ci],'interfaces_equal':u['interfaces']==v['interfaces'],'protocols_equal':u['protocols']==v['protocols'],'channels_equal':u['channel_names']==v['channel_names'],'receipts_equal':u['receipts']==v['receipts'],'unfinished_receipts_equal':u['unfinished_by_public_receipt_status']==v['unfinished_by_public_receipt_status'],'metadata_equal_keys':[k for k in keys if u['snapshot_metadata_entries_exact'].get(k)==v['snapshot_metadata_entries_exact'].get(k)],'metadata_different_keys':[k for k in keys if u['snapshot_metadata_entries_exact'].get(k)!=v['snapshot_metadata_entries_exact'].get(k)],'no_total_causal_identity_claim':True})
    r={'schema':'MUFI01.main_u.exact_read_only.v2','native_ticks_executed':0,'max_simultaneous_loaded_worlds':1,'source_sha256':sha(Path(__file__)),'worlds':worlds,'comparisons':pairs,'serialization_revision':'Enums serializedbyexactname/value ratherthanrecursivereflectionofclassmembers; initialdeepreflectionretainedlocallySHAa97cd2addf1cc3896e4b3f959330ab0372975f5731a222991d8854d388569205. No physicalsimulation repeated.','scope':'Retrospective read-only comparison of exact checkpoints specified by archived primaries. Fullphysicalfields plus exposedoperationalcontext; metadata andexternal histories areallowedtodiffer. No clockediting or unique lineage inference.'}
    target.write_bytes(gzip.compress(json.dumps(r,ensure_ascii=False,sort_keys=True).encode(),mtime=0));print(json.dumps({'bytes':target.stat().st_size,'sha256':sha(target),'pairs':[{'tick':p['tick'],'raw':len(p['raw_differences']),'clock':len(p['clock_differences']),'sites':[x['site']for x in p['raw_differences']],'interfaces_equal':p['interfaces_equal'],'unfinished_equal':p['unfinished_receipts_equal'],'metadata_differences':p['metadata_different_keys']}for p in pairs]}),flush=True)
if __name__=='__main__':main()
