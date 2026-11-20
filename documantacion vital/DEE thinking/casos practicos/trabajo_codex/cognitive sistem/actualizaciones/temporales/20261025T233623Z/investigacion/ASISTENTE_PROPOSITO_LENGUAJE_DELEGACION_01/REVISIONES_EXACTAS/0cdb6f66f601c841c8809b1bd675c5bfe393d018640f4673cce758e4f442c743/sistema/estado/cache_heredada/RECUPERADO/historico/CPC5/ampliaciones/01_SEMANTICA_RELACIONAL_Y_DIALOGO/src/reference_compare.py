"""Compare completed old-reference reproduction; no native evolution or edits."""
from pathlib import Path
import json,sys,time
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from common import ROOT,BASE,sha,put,identity,receipt,digest,operational


def main():
    import dee_thinking as d
    start=time.monotonic();engine=identity();old=BASE/'resultados/references/SEM01_A_future_UV';new=ROOT/'resultados/referencia_previa_SEM01';rows=[]
    for opath in sorted(old.glob('*.deetsnap')):
        npath=new/opath.name
        if not npath.exists():rows.append({'snapshot':opath.name,'missing_new':True});continue
        a=d.OrganizationalWorld.load_snapshot(str(opath));b=d.OrganizationalWorld.load_snapshot(str(npath))
        ar,br=a.runtime.raw_copy(),b.runtime.raw_copy();ac,bc=a.runtime.clock_copy(),b.runtime.clock_copy()
        ra=[receipt(a,x.id)for x in a.runtime.receipts];rb=[receipt(b,x.id)for x in b.runtime.receipts]
        oa,ob=operational(a),operational(b)
        row={'snapshot':opath.name,'parent_file_sha256':sha(opath),'reproduced_file_sha256':sha(npath),
          'physical_parent':digest(a),'physical_reproduced':digest(b),'full_RAW_array_equal':ar==br,'full_clock_array_equal':ac==bc,
          'tick_equal':a.runtime.current_tick==b.runtime.current_tick,'dimension_equal':a.runtime.dimension==b.runtime.dimension,
          'receipt_fields_equal':ra==rb,'parent_receipts':ra,'reproduced_receipts':rb,
          'channels_equal':oa['channels']==ob['channels'],'protocols_equal':oa['protocols']==ob['protocols'],
          'metadata_equal':oa['metadata']==ob['metadata'],'external_operations_equal':oa['external_operations']==ob['external_operations']}
        if ar!=br:row['RAW_changed_indices']=[i for i,(x,y)in enumerate(zip(ar,br))if x!=y]
        if ac!=bc:row['clock_changed_indices']=[i for i,(x,y)in enumerate(zip(ac,bc))if x!=y]
        rows.append(row)
    fields=('full_RAW_array_equal','full_clock_array_equal','tick_equal','dimension_equal','receipt_fields_equal','channels_equal','protocols_equal')
    ok=bool(rows)and all(all(r.get(k,False)for k in fields)for r in rows)
    report={'schema':'CPC5.extension.prior_reference_reproduction_check.v1','status':'VERIFIED'if ok else'FAILED',
      'kind':'TECHNICAL_DIRECTED_REPRODUCTION; not a new independent scientific sample','engine':engine,'source_sha256':sha(__file__),
      'executed_command':'CPC5/ejecutar.py referencia --caso SEM01_A_future_UV --salida EXT/resultados/referencia_previa_SEM01',
      'supervisor':'EXT/src/supervisor.py; current extension budget, not historical CPC5 BUDGET',
      'original_measurements_sha256':sha(old/'MEASUREMENTS.json'),'reproduction_measurements_sha256':sha(new/'MEASUREMENTS.json'),
      'checkpoints_compared':len(rows),'comparisons':rows,'elapsed_seconds':time.monotonic()-start,
      'scope':'Both full arrays compared directly, not just endpoint scalars. Metadata and external logs listed separately; no expected value supplied until after the reproduced trajectory completed.'}
    put(ROOT/'resultados/reference_reproduction_check.json',report);assert ok
    print(json.dumps({'status':report['status'],'checkpoints':len(rows),'receipts_equal':all(x['receipt_fields_equal']for x in rows)}),flush=True)


if __name__=='__main__':main()
