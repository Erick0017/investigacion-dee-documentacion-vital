"""Root explicit stable code preservation, safe beside an unrelated active world.

Reads frozen source/config only, excludes all states/runtime/caches. Never
imports Cognitive/DEE, opens a world, stops a process or updates selectors.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,shutil
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema'
DEST=C/'reproducibilidad/codigo_preservado/PI05_TRANSITO_DIAGNOSTICO_R01'
EXPECTED={'app/cola_local.py':'d6cc7534495a7c9941422b0e1515681f8895b4bdef07e05521ad0253c0b4f626',
 'app/mundo_genesis_apd05.py':'6b988948f50cd5d3b1faec61a5368714de175c182ffafb36fb23e476f06796f5',
 'capacidades/pi04_dispatcher.py':'6964188e7c2a91974df74457788dc532c6a564eafc8a8c3bc21ff5de4e56076c',
 'capacidades/pi04_coordinacion_central_C2C.py':'31778467ef0917f74fe422d538b9ed97a8144e05aaff1717dae4124b1ade87dd',
 'capacidades/pi05_guardia_transito_R01.py':'0bf733e663ff5968ef7bf1cc464878f8d28610bed475ffc51b3db587b399276c',
 'capacidades/pi05_c2c_ofertas_R01.py':'3b7054996f694dd596f551d15612c649741d56df1710af47d651d31b51f98bbe'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
    for q in(p,*p.parents):
        if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked code preservation path')
def collect():
    rows=[];omit={'estado','runtime','__pycache__','.git','.venv','site-packages','node_modules'}
    for base,dirs,files in os.walk(S,followlinks=False):
        base=Path(base);regular(base);dirs[:]=[d for d in dirs if d not in omit]
        for d in dirs:regular(base/d)
        for name in sorted(files):
            p=base/name
            if p.suffix not in('.py','.json'):continue
            regular(p);rows.append({'file':p.relative_to(S).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    return sorted(rows,key=lambda r:r['file'])
def verify(root,rows):
    for r in rows:
        p=root/r['file'];regular(p)
        if p.stat().st_size!=r['bytes']or sha(p)!=r['sha256']:raise ValueError('Exact code preservation mismatch: '+r['file'])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--aplicar',action='store_true');a=ap.parse_args();rows=collect();byname={r['file']:r for r in rows}
    if any(byname.get(n,{}).get('sha256')!=h for n,h in EXPECTED.items()):raise ValueError('Current S5 source is not qualified diagnostic revision; no silent permission/deployment delta')
    regular(DEST)
    if not DEST.resolve(strict=False).is_relative_to((C/'reproducibilidad/codigo_preservado').resolve()):raise ValueError('Exact stable capsule store only')
    manifest=DEST/'SISTEMA_CODIGO.json';reused=DEST.exists();action='PLAN_ONLY'
    if reused:
        old=json.loads(manifest.read_text('utf8'))
        if old['files']!=rows:raise ValueError('Existing diagnostic capsule differs; never overwrite')
        verify(DEST,rows);action='REUSED_VERIFIED'
    elif a.aplicar:
        DEST.mkdir(parents=True,exist_ok=False)
        for r in rows:
            p=DEST/r['file'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(S/r['file'],p)
        verify(DEST,rows)
        m={'schema':'DEE.Cognitive.frozen_source_capsule.v1','id':'PI05_TRANSITO_DIAGNOSTICO_R01','source_root':str(S),
           'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':rows,
           'exclude':['All Native snapshots/SQLite/world states','runtime/WHL/PYD/engine','caches'],
           'scope':'Full exact diagnostic Cognitive code GUARD+explicitenvironment30. Dormant adoption permission not included in this historical code revision.',
           'engine_shared_once':'Official Thinking4.5.0/Universev27 remain in product; not duplicated in capsule',
           'Native_executed_by_preservation':False}
        manifest.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8');action='COPIED_VERIFIED'
    if collect()!=rows:raise ValueError('Source code changed concurrently; preserve target and do not register')
    proof={'schema':'DEE.PI05.stable_diagnostic_code_preservation.R01','action':action,'source':str(S),'destination':str(DEST),
       'files':len(rows),'bytes':sum(r['bytes']for r in rows),'manifest_sha256':sha(manifest)if manifest.exists()else None,
       'all_source_hashes_unchanged_after':True,'Native_executed':False,'new_ticks':0,'states_queues_selectors_modified':False,
       'scope':'Read-only code copy while an unrelated existing owner may run; no source/world/engine changes.'}
    out=P/'control'/('CAPSULA_DIAGNOSTICA_PI05_R01_'+('PRESERVADA'if a.aplicar or reused else'PLAN')+'.json')
    if out.exists():raise ValueError('Prior preservation proof protected')
    out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof,ensure_ascii=False))
if __name__=='__main__':main()
