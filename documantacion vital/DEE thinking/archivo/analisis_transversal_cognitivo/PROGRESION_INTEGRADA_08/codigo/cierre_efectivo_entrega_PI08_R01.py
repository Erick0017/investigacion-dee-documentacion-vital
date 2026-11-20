"""Post-seal actual delivery/accounting witnesses, without modifying sealed sources."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
P=Path(__file__).resolve().parents[1];R=P.parents[2];W=P.parents[4];C=R/'DEE Cognitive 2.0'
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,j):
    with p.open('x',encoding='utf-8') as f: json.dump(j,f,ensure_ascii=False,indent=2);f.write('\n')
def main(a):
    proof=P/'control/VERIFICACION_ZIP_FINAL_PI08_R01.json';v=read(proof)
    if v['status']!='SEALED_AND_CLEAN_EXTRACTION_VERIFIED': raise ValueError('Actual verified sealed ZIP required')
    z=Path(v['zip']['path'])
    if z.stat().st_size!=v['zip']['bytes'] or sha(z)!=v['zip']['sha256']: raise ValueError('Sealed ZIP changed')
    config=P/'codigo/CONFIG_CONTABILIDAD_POSTSELLADO_PI08_R01.json'
    if a.preparar_config:
        j=read(P/'codigo/CONFIG_CONTABILIDAD_FINAL_PI08_R01.json')
        clean=Path(v['clean_extraction']).parent.resolve(strict=True)
        if clean.parent!=W.resolve() or not clean.name.startswith('p8v'): raise ValueError('Only actual short extraction root')
        j['exact_additional_storage_roots']=[{'path':str(clean),'origin_evidence':str(proof)+' SHA256 '+sha(proof)}]
        j['actual_final_ZIP']={**v['zip'],'verification':str(proof)}
        put(config,j)
        print(json.dumps({'post_config':str(config),'sha256':sha(config)}));return
    acpath=P/'control/CONTABILIDAD_POSTSELLADO_PI08_R01.json';ac=read(acpath)
    if ac['issues'] or not all(ac['checks'].values()): raise ValueError('Post-seal issues must remain explicit, do not claim closure')
    main=read(C/'sistema/estado/ACTIVO.json')
    if main['life_id']!='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01' or main['tick']!=861426 or main['snapshot_sha256']!='2eeef08e3bebac4e218178ed379fd99aa5fdeb03650c0454ad55c6534824c133': raise ValueError('Main advanced after seal; no blind closure')
    out=P/'control/CIERRE_EFECTIVO_PI08_R01.json'
    j={'schema':'DEE.PI08.effective_delivery_close.v1','at_utc':datetime.now(timezone.utc).isoformat(),
       'status':'SCIENTIFIC_OPERATIONAL_DOCUMENTARY_AND_PACKAGE_CLOSED_WITH_VISUAL_QA_LIMITATION',
       'zip':v['zip'],'actual_main':main,'manual_internal_edition':'1.36',
       'Native_ticks':ac['Native_ledger']['known_Native_ticks'],'world_slots':ac['Native_ledger']['worlds_total_for_budget'],
       'post_seal_logical_storage_bytes':ac['storage']['measured_logical_bytes'],
       'post_seal_accounting':{'path':str(acpath),'sha256':sha(acpath)},
       'clean_extraction_verification':{'path':str(proof),'sha256':sha(proof)},
       'portable_jobs_completed':len(v['access_fence']['jobs']),
       'no_original_access_or_DEE_import_in_portable_recalculation':v['access_fence']['no_original_source_access'],
       'B_adopted':False,'C_adopted':False,'F1_cut_executed':False,
       'visual_page_validation':False,'exact_limitation':'LibreOffice soffice.exe was not found on PATH; actual DOCX CRC/XML/history checks and literal full publication were completed.',
       'private_material_uploaded_or_published':False,'cleanup_performed':False,'new_Native_ticks_by_closure':0,
       'ZIP_unchanged_by_this_post_seal_witness':True,'post_seal_witness_is_local_not_claimed_inside_already_sealed_ZIP':True}
    put(out,j)
    print(json.dumps({'closure':str(out),'sha256':sha(out),'zip':v['zip'],'actual_main_T':861426,'Native_ticks':j['Native_ticks'],'storage':j['post_seal_logical_storage_bytes']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preparar-config',action='store_true');main(p.parse_args())
