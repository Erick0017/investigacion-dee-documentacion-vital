"""APD02: restore exact archived aliases and recalculate with engine imports blocked."""
import argparse,hashlib,json,os,re,subprocess,sys,time
from pathlib import Path,PurePosixPath
RESERVED={'CON','PRN','AUX','NUL',*(f'COM{i}'for i in range(1,10)),*(f'LPT{i}'for i in range(1,10))}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(base,name):
    if not isinstance(name,str)or not name or'\\'in name or':'in name:raise ValueError('Unsafe relative member')
    p=PurePosixPath(name)
    if p.is_absolute()or p.as_posix()!=name or any(v in('','..','.')or v.endswith((' ','.'))or v.split('.')[0].upper()in RESERVED for v in p.parts):raise ValueError('Unsafe/nonportable relative member')
    result=base.joinpath(*p.parts)
    if not result.resolve().is_relative_to(base.resolve()):raise ValueError('Member outside root')
    return result
def regular_files(root):
    rows=[]
    for folder,dirs,files in os.walk(root,followlinks=False):
        for name in list(dirs)+files:
            p=Path(folder)/name;st=p.stat(follow_symlinks=False)
            if p.is_symlink()or getattr(st,'st_file_attributes',0)&0x400:raise ValueError('No symlinks, junctions or reparse members')
        for name in files:rows.append(Path(folder)/name)
    return rows

NO_ENGINE_WRAPPER=r'''
import importlib.abc,runpy,sys
class NoNativeEngine(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0] in {'dee_thinking','dee_universe','capacidades','app','numpy'}:
            raise ImportError('Archived-only recalculation forbids engine/system imports: '+fullname)
sys.meta_path.insert(0,NoNativeEngine())
script=sys.argv[1];sys.argv=sys.argv[1:]
runpy.run_path(script,run_name='__main__')
'''

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',type=Path,required=True)
    ap.add_argument('--permitir-preparacion',action='store_true',help='Explicitly run a NON-FINAL preparation; never certifies campaign closure')
    ap.add_argument('--solo-desplegar',action='store_true');a=ap.parse_args()
    root=Path(__file__).resolve().parent;index=json.loads((root/'INDICE_OBJETOS_Y_ALIASES.json').read_text(encoding='utf8'))
    plan=json.loads((root/'PLAN_GLOBAL.json').read_text(encoding='utf8'))
    final=plan['status']in('CLOSED_APPROVED_FOR_ANALYSIS','CLOSED_APPROVED_FOR_PACKAGING')
    if not final and not a.permitir_preparacion:raise ValueError('NON-FINAL preparation: pass --permitir-preparacion explicitly; final campaign components remain pending')
    if final and plan.get('pending_components'):raise ValueError('Final plan has pending components')
    if plan.get('expected_case_count')!=len(plan['cases']):raise ValueError('Global case denominator mismatch')
    manifest=json.loads((root/'MANIFIESTO_HASHES.json').read_text(encoding='utf8'));members=manifest['members']
    if len({x['path']for x in members})!=len(members):raise ValueError('Duplicate immutable manifest member')
    expected={x['path']for x in members}|{'MANIFIESTO_HASHES.json'};actual={p.relative_to(root).as_posix()for p in regular_files(root)}
    if actual!=expected:raise ValueError({'missing':sorted(expected-actual),'extra':sorted(actual-expected)})
    for m in members:
        p=safe(root,m['path'])
        if p.stat().st_size!=m['bytes']or sha(p)!=m['sha256']:raise ValueError('Changed analysis member: '+m['path'])
    output=a.salida.resolve()
    if output.is_relative_to(root.resolve())or root.resolve().is_relative_to(output):raise ValueError('Use a new result directory outside the immutable extracted analysis tree, not its parent')
    if output.exists():raise FileExistsError('Fresh output directory required; prior verification is never overwritten')
    output.mkdir(parents=True);restored=output/'ARCHIVO_RECUPERADO';restored.mkdir();count=0;expanded=0
    namespace_ids=[n['id']for n in index['namespaces']]
    if len(set(namespace_ids))!=len(namespace_ids):raise ValueError('Duplicate namespace')
    for namespace in index['namespaces']:
        if not re.fullmatch(r'[A-Z][A-Z0-9_]{0,63}',namespace['id']):raise ValueError('Unsafe namespace')
        base=restored/namespace['id'];base.mkdir()
        seen=set()
        for item in namespace['members']:
            if item['path']in seen:raise ValueError('Duplicate logical alias')
            seen.add(item['path']);blob=index['objects'][item['sha256']];src=safe(root,blob['storage'])
            if blob['bytes']!=item['bytes']or src.stat().st_size!=item['bytes']or sha(src)!=item['sha256']:raise ValueError('Changed deduplicated content object')
            dst=safe(base,item['path']);dst.parent.mkdir(parents=True,exist_ok=True)
            with dst.open('xb')as f:f.write(src.read_bytes())
            if sha(dst)!=item['sha256']:raise ValueError('Restored original bytes differ')
            count+=1;expanded+=item['bytes']
    results=output/'RESULTADOS_RECALCULO';results.mkdir();runs=[];issues=[]
    if not a.solo_desplegar:
        for number,item in enumerate(plan['cases']):
            base=safe(restored,item['base']);script=safe(base,item['script'])
            if not script.is_file():raise FileNotFoundError(str(script))
            dest=results/(str(number).zfill(2)+'_'+item['case']+'.json')
            argv=[str(dest)if x=='{output}'else x for x in item['args']]
            if argv.count(str(dest))!=1:raise ValueError('Each case must have one explicit external output')
            command=[sys.executable,'-I','-B','-X','utf8','-c',NO_ENGINE_WRAPPER,str(script),*argv]
            started=time.monotonic();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf8');env.pop('PYTHONPATH',None)
            try:
                run=subprocess.run(command,cwd=base,env=env,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=item.get('timeout_seconds',180))
                code=run.returncode;stdout=run.stdout;stderr=run.stderr
            except subprocess.TimeoutExpired as error:code=None;stdout=str(error.stdout or'');stderr='Auditor recalculation timeout: '+str(error)
            generated=dest.read_bytes()if dest.is_file()else None
            expected_sha=item['reference_sha256'];expected_bytes=item['reference_bytes']
            if item.get('reference'):
                reference=safe(base,item['reference']);fixed=reference.read_bytes()
                if sha(reference)!=expected_sha or len(fixed)!=expected_bytes:raise ValueError('Fixed reference altered')
                exact=generated==fixed;comparison='BYTE_FOR_BYTE_WITH_INCLUDED_FIXED_REFERENCE'
            else:
                exact=generated is not None and len(generated)==expected_bytes and hashlib.sha256(generated).hexdigest()==expected_sha
                comparison='SHA256_AND_SIZE_OF_EXACT_ORIGINAL_RECONSTRUCTION'
            accepted=code==0 and exact
            record={'case':item['case'],'returncode':code,'stdout':stdout,'stderr':stderr,
                    'reference_comparison':comparison,'reference_sha256':expected_sha,
                    'actual_sha256':hashlib.sha256(generated).hexdigest()if generated is not None else None,
                    'reference_bytes':expected_bytes,'actual_bytes':len(generated)if generated is not None else None,
                    'exact':exact,'accepted':accepted,'elapsed_seconds':time.monotonic()-started,'native_ticks':0}
            runs.append(record)
            if not accepted:issues.append({'case':item['case'],'error':'Archived recalculation differs or did not complete'})
    report={'schema':'APD02.CAS.archived_recalculation.verification.v1','native_ticks':0,'engine_imports_blocked':True,
            'campaign_final_status':final,'pending_components':plan.get('pending_components',[]),
            'immutable_analysis_members_verified':len(members),'restored_logical_files':count,'restored_logical_bytes':expanded,
            'unique_content_objects':len(index['objects']),'cases':runs,'issues':issues,
            'all_selected_cases_exact':bool(runs)and not issues,'only_materialization_requested':a.solo_desplegar,
            'scope':'Archived recalculation, not native replay, a new external run, a new acquisition or proof that pending campaign components are finished. Original gzip/code bytes are restored unchanged; no scientific row is removed by content deduplication.'}
    (output/'VERIFICACION_RECALCULOS.json').write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({'cases':len(runs),'issues':issues,'restored_files':count,'unique_objects':len(index['objects']),'native_ticks':0,'campaign_final_status':final}))
    return 2 if issues else 0

if __name__=='__main__':raise SystemExit(main())
