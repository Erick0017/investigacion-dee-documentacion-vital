"""Lossless N0 CAS extraction of the sealed four-brief analysis, not a ZIP."""
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE=Path(__file__).resolve().parent
OLD=HERE/'EVIDENCIA_NIVELES_BREVES_CERRADOS_N0_R01'
OUT=HERE/'EVIDENCIA_NIVELES_BREVES_CAS_N0_R02'


def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')


def main():
    if OUT.exists():raise FileExistsError('Preserve every previous output')
    for x in read(OLD/'MANIFIESTO.json')['members']:
        if sha((OLD/x['file']).read_bytes())!=x['sha256']:raise ValueError('Original essential archive changed')
    OUT.mkdir();(OUT/'CAS').mkdir();entries=[];unique={}
    for p in sorted(OLD.rglob('*')):
        if not p.is_file():continue
        b=p.read_bytes();digest=sha(b);rel='CAS/'+digest+'.gz'
        if digest not in unique:
            z=gzip.compress(b,compresslevel=9,mtime=0)
            with(OUT/rel).open('xb')as f:f.write(z)
            if gzip.decompress((OUT/rel).read_bytes())!=b:raise ValueError('Not lossless')
            unique[digest]={'file':rel,'gzip_sha256':sha(z),'gzip_bytes':len(z)}
        item=unique[digest]
        entries.append({'original_file':p.relative_to(OLD).as_posix(),'original_bytes':len(b),
            'original_sha256':digest,'CAS_payload':rel,'CAS_payload_sha256':item['gzip_sha256'],'compression':'gzip_lossless_outer'})
    write(OUT/'INDICE_CAS.json',{'schema':'APD04.brief_levels.lossless_CAS.N0.R02','original_folder_local':str(OLD),
        'original_manifest_sha256':sha((OLD/'MANIFIESTO.json').read_bytes()),'original_members':entries,
        'new_native_ticks':0,'no_originals_modified':True,'unique_payloads':len(unique),
        'original_expanded_bytes':sum(x['original_bytes']for x in entries),
        'CAS_payload_bytes':sum(x['gzip_bytes']for x in unique.values()),
        'scope':'Byte-exact lossless repack of all63 files in the sealed R01 analysis. Raw/clocks and all cases preserved. Full Native snapshots/transport remain local and are indexed, not included or reconstructible here.'})
    r=read(OLD/'RECALCULO.json');summ=[]
    for x in r['branches']:
        summ.append({'sources':x['sources'],'life':x['life'],'initial_tick':x['initial_tick'],'final_tick':x['final_tick'],
            'actions':x['actions'],'functional_denominators':x['functional_denominators'],
            'dose_by_scope':{k:{a:b for a,b in v.items()if a!='IDs'}for k,v in x['dose_by_scope'].items()},
            'native_new_IDs':x['unique_new_native_IDs'],'terminal_statuses':x['terminal_native_statuses'],
            'physical':x['physical'],'physical_difference':x['physical_difference_from_shared_prefix'],
            'complete_pair_local_locator':x['pairs_local_only']})
    write(OUT/'RESUMEN_RESULTADOS.json',{'schema':'APD04.brief_levels.closed_summary.N0.R02','branches':summ,
        'attribution':r['attribution'],'scope':r['scope'],'resources':r['budget_and_resource_scope'],
        'original_recalc_checks':len(r['checks']),'original_recalc_issues':r['issues'],
        'commands':{'verify':'python recalcular_cas_niveles_n0_r02.py --verify-only',
            'recalculate_without_histories':'python recalcular_cas_niveles_n0_r02.py',
            'restore_readable_analysis_files':'python recalcular_cas_niveles_n0_r02.py --extract R01_REHIDRATADO'},
        'not_operational_backup':True,'no_zip_generated':True})
    shutil.copy2(HERE/'recalcular_cas_niveles_n0_r02.py',OUT/'recalcular_cas_niveles_n0_r02.py')
    shutil.copy2(Path(__file__),OUT/Path(__file__).name)
    write(OUT/'MANIFIESTO.json',{'self_hash_excluded':True,'members':[{'file':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in sorted(OUT.rglob('*'))if p.is_file()]})
    s=importlib.util.spec_from_file_location('CAS_verification_only_no_Native',OUT/'recalcular_cas_niveles_n0_r02.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    proof=m.reconstruct(OUT)
    if len(proof)!=len(entries):raise ValueError('CAS coverage incomplete')
    if any(k.startswith('dee_thinking')for k in sys.modules):raise RuntimeError('Unexpected Native import')
    print(json.dumps({'out':str(OUT),'files':sum(p.is_file()for p in OUT.rglob('*')),
        'bytes':sum(p.stat().st_size for p in OUT.rglob('*')if p.is_file()),
        'original_files_verified':len(proof),'original_bytes':sum(x['original_bytes']for x in entries),
        'manifest_sha256':sha((OUT/'MANIFIESTO.json').read_bytes()),'Native_ticks':0}))


if __name__=='__main__':main()
