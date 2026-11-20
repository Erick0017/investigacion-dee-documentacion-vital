"""Pure synthetic codec/analyzer tests. This never executes DEE or scientific data."""
from pathlib import Path
from array import array
from types import SimpleNamespace
import gzip,hashlib,json,runpy,shutil,sys

HERE=Path(__file__).resolve().parent
P5=HERE.parent
DEST=P5/'control'/'PRUEBA_ANALIZADOR_PURO_FAKE_R02'

def main():
    if DEST.exists():raise FileExistsError('Do not overwrite a previous pure test')
    DEST.mkdir(parents=True)
    codec=runpy.run_path(str(HERE/'observador_global_PI05_R01.py'),run_name='pure_fake_codec')
    a=runpy.run_path(str(HERE/'analizar_influencia_global_PI05_R01.py'),run_name='pure_fake_analyzer')
    checks={};count=67**3
    def value(charge):return 1|(charge<<32)|(1<<48)|(1<<52)|(1<<56)|(1<<60)
    class Runtime:
        dimension=67
        current_tick=100
        def __init__(self,charge):self.charge=charge
        def raw_copy(self):
            data=array('Q',[0])*count
            data[(1*67+2)*67+3]=4<<60 # Crucial inactive nonzeroRAW, not empty.
            if self.current_tick==101:data[(15*67+47)*67+21]=value(self.charge)
            return data
        def clock_copy(self):return array('Q',[self.current_tick])*count
    class Adapter:
        def __init__(self,charge):self.world=SimpleNamespace(runtime=Runtime(charge))
        @property
        def tick(self):return self.world.runtime.current_tick
    for name,charge in [('SYNTHETIC_A',17),('SYNTHETIC_B',18)]:
        adapter=Adapter(charge)
        recorder=codec['GlobalRecorder'](DEST/name,N=67,ticks=[100,101,102],anchor_ticks=[100],provenance={'synthetic_fixture':True,'not_DEE':True,'no_physical_trajectory_asserted':True})
        for tick in [100,101,102]:adapter.world.runtime.current_tick=tick;recorder.capture(adapter)
        recorder.close()
        primary={'result':json.dumps({'result':{'rows':[{'requests':[{'id':1,'port':'SYNTHETIC_PORT','tick':100,'payload':charge,'site':[14,46,20],'direction':[1,1,1],'receipt':{'id':1,'status':'applied'}}]}]}})}
        (DEST/(name+'_PRIMARY.json')).write_text(json.dumps(primary),encoding='utf-8')
    ca=DEST/'SYNTHETIC_A';cb=DEST/'SYNTHETIC_B';pa=DEST/'SYNTHETIC_A_PRIMARY.json';pb=DEST/'SYNTHETIC_B_PRIMARY.json'
    checks['lossless_codec_A']=codec['verify_recording'](ca)['all_RAW_clocks_hashes_match']
    ia=a['inventory'](ca,DEST/'INVENTORY_A_1',pa)
    ib=a['inventory'](ca,DEST/'INVENTORY_A_2',pa)
    members1={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in ia.parent.iterdir()if p.is_file()}
    members2={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in ib.parent.iterdir()if p.is_file()}
    checks['recalculation_member_bytes_deterministic']=members1==members2
    inv=json.loads(ia.read_text(encoding='utf-8'))
    checks['global_inventory_has_inactive_nonzeroRAW']=all(row['state0_raw_nonzero']==1 for row in inv['frames'])
    exported=[json.loads(s)for s in gzip.decompress((ia.parent/'RAW_NO_NULO_GLOBAL.jsonl.gz').read_bytes()).decode('utf-8').splitlines()]
    checks['inactive_sem4_exact_RAW_exported']=all(any(r['state']==0 and r['semantic']==4 and int(r['raw'])==4<<60 for r in row['nonzero_RAW_records'])for row in exported)
    comparison=a['compare'](ca,cb,DEST/'COMPARISON_A_B',pa,pb)
    cmp=json.loads(comparison.read_text(encoding='utf-8'))
    checks['same_initial_complete_RAW_clocks']=all(cmp['initial_physical_comparison'][k]for k in('RAW_bytes_exact','clocks_bytes_exact'))
    checks['first_last_difference_exact101']=cmp['first_observed_difference_tick']==101 and cmp['last_observed_difference_tick']==101
    checks['difference_support_all_sites_exact']=[f['union_difference_sites']for f in cmp['frames']]==[0,1,0]
    checks['single_payload_change_deduplicated']=cmp['actual_event_comparison']['single_payload_intervention_verified']
    checks['all_explicit_physical_sources_verified']=cmp['actual_event_comparison']['same_sources_timing_directions_verified_from_requests']
    witness=cmp['first_difference_window']
    checks['onset_plusminus1_complete']=witness['available_ticks']==[100,101,102]and witness['conservative_causal_neighbourhood_radius']==1 and witness['toroidal_region_sites']==27
    try:a['inventory'](ca,DEST/'INVENTORY_A_1',pa)
    except FileExistsError:checks['existing_destination_rejected']=True
    else:checks['existing_destination_rejected']=False
    corrupt=DEST/'SYNTHETIC_CORRUPT';shutil.copytree(ca,corrupt)
    payload=next(corrupt.glob('*.zlib'));content=bytearray(payload.read_bytes());content[-1]^=1;payload.write_bytes(content)
    try:list(codec['iter_frames'](corrupt))
    except (ValueError,RuntimeError):checks['corruption_rejected']=True
    else:checks['corruption_rejected']=False
    checks['no_DEE_app_modules_imported']=not any(n=='app'or n.startswith('app.')or n=='dee_thinking'or n.startswith('dee_thinking.')for n in sys.modules)
    result={'schema':'DEE.PI05.global_analyzer.pure_synthetic_test.R02','synthetic_only':True,'Native_ticks':0,'not_passivity_test':True,'not_scientific_data':True,'checks':checks,'all_checks':all(checks.values()),'source_files':[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [HERE/'observador_global_PI05_R01.py',HERE/'analizar_influencia_global_PI05_R01.py',Path(__file__)]]}
    out=DEST/'VERIFICACION_FAKE_SIN_NATIVE.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(out),'all_checks':result['all_checks'],'checks':checks,'Native_ticks':0}))
    if not result['all_checks']:raise RuntimeError('Pure synthetic test failed')

if __name__=='__main__':main()
