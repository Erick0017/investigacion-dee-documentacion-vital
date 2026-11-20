"""Zero-tick full-field MAIN/U comparison before their first chain finish."""
import gc,gzip,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parent;ROOT=LAB.parents[2];SYSTEM=ROOT/'sistema'
sys.path.insert(0,str(LAB/'transferencia_b'))
import frontend_b01_r2 as f
from comparar_tuh_sin_ticks_r1 import public,digest_array
OUT=ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/comparacion_cadena_b'
EV=OUT.parent
def main():
    authorization,ni=f.bootstrap()
    from dee_thinking.persistence import load_world_snapshot
    from dee_thinking.consolidated import exact_receipt
    worlds={};base=None
    for label,p in[('U',EV/'composicion_b/U1.json.gz'),('MAIN',EV/'B_MAIN_05_CADENA_1_INICIO.json.gz')]:
        o=json.loads(gzip.decompress(p.read_bytes()));ins=o['INSTRUMENTO']if label=='U'else o['result']['INSTRUMENTO'];tick=ins['tick']
        if tick!=31765:raise ValueError('No age equalization or clock editing allowed')
        cps=[q for q in(SYSTEM/'estado/checkpoints').glob(ins['life_id']+'.T31765.*.deetsnap.gz')if f.digest(q)==ins['snapshot_sha256']]
        if len(cps)!=1:raise ValueError('No unique complete exact source checkpoint')
        cp=cps[0];w,proof=load_world_snapshot(cp);before=int(w.runtime.current_tick);raw=[str(int(x))for x in w.runtime.raw_copy()];clock=[str(int(x))for x in w.runtime.clock_copy()]
        rr=w.runtime.receipts()if callable(w.runtime.receipts)else w.runtime.receipts;receipts=[exact_receipt(r)for r in rr]
        row={'snapshot_path':str(cp),'snapshot_sha256':f.digest(cp),'source_primary':str(p),'source_primary_sha256':f.digest(p),'tick_before':before,'tick_after':int(w.runtime.current_tick),
          'raw_sha256':digest_array(raw),'clock_sha256':digest_array(clock),'interfaces':[public(x)for x in w.interfaces],'protocols':[public(x)for x in w.protocols],
          'receipts':receipts,'unfinished_receipts':[r for r in receipts if r['status']not in('applied','cancelled','failed')and not r['status'].startswith('rejected')],
          'snapshot_metadata_entries_exact':dict(w.runtime.snapshot_metadata_entries),'load_proof':proof}
        if label=='U':row['raw']=raw;row['clock']=clock;base=(raw,clock)
        else:
            row['base']='U';row['raw_delta']=[{'index':j,'site':[j//4489,(j//67)%67,j%67],'raw':v,'base_raw':base[0][j]}for j,v in enumerate(raw)if v!=base[0][j]]
            row['clock_delta']=[{'index':j,'clock':v,'base_clock':base[1][j]}for j,v in enumerate(clock)if v!=base[1][j]]
        worlds[label]=row;del w,raw,clock,receipts;gc.collect();f.memory_guard()
    u,m=worlds['U'],worlds['MAIN'];key='DEE.Cognitive.System.1.1.MENTE_UNIFICADA_01.v1'
    from dee_thinking.persistence import decode_metadata
    opu=decode_metadata(u['snapshot_metadata_entries_exact'][key]);opm=decode_metadata(m['snapshot_metadata_entries_exact'][key])
    comparison={'raw_differences':len(m['raw_delta']),'clock_differences':len(m['clock_delta']),'raw_sites':[x['site']for x in m['raw_delta']],
      'interfaces_equal':u['interfaces']==m['interfaces'],'protocols_equal':u['protocols']==m['protocols'],'unfinished_equal':u['unfinished_receipts']==m['unfinished_receipts'],
      'external_pending_exact_equal':opu.get('external_pending')==opm.get('external_pending'),'external_pending_U':opu.get('external_pending'),'external_pending_MAIN':opm.get('external_pending'),
      'cascade_pending_exact_equal':opu.get('cascade_pending')==opm.get('cascade_pending'),'no_total_causal_identity_claim':True}
    f.dump(OUT/'MAIN_U_T31765_COMPLETO.json.gz',{'schema':'MUFI01.B.chain_prepared.full_arrays.v1','authorization':authorization,'native_ticks_executed':0,'max_simultaneous_loaded_worlds':1,
      'code_sha256':f.digest(__file__),'worlds':worlds,'comparison':comparison,'scope':'AllRAW/clocks lossless base+deltas and exposed operational context. No unique past inference, no replay or tick advance.'})
    print(json.dumps({'comparison':{k:v for k,v in comparison.items()if not k.startswith('external_pending_')or k.endswith('equal')},'sha256':f.digest(OUT/'MAIN_U_T31765_COMPLETO.json.gz')}))
if __name__=='__main__':main()
