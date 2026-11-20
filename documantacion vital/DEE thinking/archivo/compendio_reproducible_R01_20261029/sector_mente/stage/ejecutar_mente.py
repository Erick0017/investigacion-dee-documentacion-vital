"""Replays existing protocols in a fresh private tree, never the active system.

Only roots, supervision budget and documentary identities are new. Scientific
sources are copied byte for byte; outputs are compared after native evolution.
"""
from pathlib import Path
import argparse,ast,gzip,hashlib,json,os,runpy,shutil,sys,time,traceback,importlib,tempfile
HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parents[1]
def read(p):
    p=Path(p);return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
SKIP=set()
def payload(row):
    if isinstance(row.get('data'),dict):return row['data'].get('result',row['data'])
    v=row.get('result',row)
    while isinstance(v,dict)and 'result'in v and isinstance(v['result'],dict):v=v['result']
    return v
def observed(value):
    """Exact discrete witnesses, excluding only host file references/identities."""
    found=[]
    def walk(x,p=''):
        if isinstance(x,dict):
            if 'raw'in x and 'clock'in x and 'direction'in x:
                found.append((p,{k:v for k,v in x.items()if k in('raw','clock','direction','state','semantic','s_reg','site')}));return
            if {'id','status'}.issubset(x)and('actual_tick'in x or'applied_tick'in x or'scheduled_tick'in x):
                found.append((p,x));return
            for k,v in x.items():
                if k not in('before','after','sources','initial','final','pre_snapshot','history_snapshot','post_joint_snapshot','intervention_snapshot')and k not in SKIP:walk(v,p+'/'+k)
        elif isinstance(x,list):
            for i,v in enumerate(x):walk(v,p+'/'+str(i))
    walk(value);return found
def final_physical(row):
    if isinstance(row.get('data'),dict)and isinstance(row['data'].get('physical'),dict):return row['data']['physical']
    if isinstance(row.get('physical'),dict):return row['physical']
    if isinstance(row.get('result'),dict)and isinstance(row['result'].get('physical'),dict):return row['result']['physical']
    r=payload(row)
    if isinstance(r,dict)and isinstance(r.get('final'),dict):
        f=r['final'];return f.get('physical',f)if('RAW_sha256'in f or'physical'in f)else None
    return None
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--id',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--case',help='Replay only one named historical manager operation (or its declared consecutive group).');args=ap.parse_args()
    config=read(HERE/'sector_config.json');m=next(x for x in config['mechanisms']if x['id']==args.id)
    if args.case:
        chosen=next(x for x in m.get('api_program',[])if x['case']==args.case)
        m={**m,'entries':[],'api_program':[x for x in m['api_program']if x['parent']==chosen['parent']]}
        m['references']=[x['reference']for x in m['api_program']]
        aliases={x['parent']for x in m['api_program']};m['parents']=[x for x in m['parents']if x['life']in aliases]
    global SKIP;SKIP=set(m.get('omit_comparison_keys',[]))
    if m.get('pending'):raise RuntimeError('Not admitted for native replay: '+str(m['pending']))
    out=args.out.resolve()
    assert not out.exists()or(out.is_dir()and all(p.is_file()and p.name in('EJECUCION_STDOUT.log','EJECUCION_STDERR.log')for p in out.iterdir())),'Use a new result directory; no historical state or output is overwritten'
    assert out!=HERE and not HERE.is_relative_to(out),'Output cannot replace the library'
    out.mkdir(parents=True,exist_ok=True);started=time.monotonic();(out/'sistema/estado/checkpoints').mkdir(parents=True)
    for name in('vidas','locks'):(out/'sistema/estado'/name).mkdir()
    common=PACKAGE/'codigo_comun/cognitive'
    if not common.exists():common=PACKAGE/'codigo_comun/sistema'
    if not common.exists():raise FileNotFoundError('Shared private backend codigo_comun/cognitive')
    shutil.copytree(common,out/'sistema',dirs_exist_ok=True)
    runtime=out/'sistema/runtime';runtime.mkdir(exist_ok=True)
    whls=list((PACKAGE/'motor').glob('dee_thinking-4.5.0-*.whl'))
    assert len(whls)==1,'One identified official4.5 wheel is required'
    shutil.copy2(whls[0],runtime/whls[0].name)
    # These are experiment code only, not old evidence, checkpoints or the GUI.
    shutil.copytree(HERE/'laboratorio',out/'laboratorio')
    for camp in(out/'laboratorio/campanas').iterdir():
        if camp.is_dir():(out/'evidencia/campanas'/camp.name).mkdir(parents=True,exist_ok=True)
    deadline=started+int(m['timeout_seconds'])+2400
    for camp in {p.parent for p in(out/'laboratorio/campanas').glob('*/*.py')}:
        (camp/'PRESUPUESTO.json').write_text(json.dumps({'monotonic_deadline':deadline,'reserved_closure_seconds':2400,'scope':'Technical reproduction supervisor; no historical deadline or experiment result is rewritten'}),encoding='utf8')
    sys.path.insert(0,str(out/'sistema'))
    if (PACKAGE/'codigo_comun/terceros').exists():sys.path.insert(0,str(PACKAGE/'codigo_comun/terceros'))
    os.chdir(out)
    # The outer package launcher gives this process its own temporary-I/O root.
    # Official4.5 lossless snapshot materialization uses that root, not old data.
    temporary=Path(tempfile.gettempdir()).resolve()
    opened=set();allowed=[PACKAGE,out,temporary,Path(sys.prefix).resolve(),Path(sys.base_prefix).resolve(),Path(os.environ.get('SystemRoot','C:/Windows')).resolve()]
    def permitted(p):return any(p==r or p.is_relative_to(r)for r in allowed)
    def audit(event,values):
        if event=='open'and values and isinstance(values[0],(str,bytes,os.PathLike)):
            p=Path(os.fsdecode(values[0])).resolve()
            if not permitted(p):raise PermissionError('Reproduction cannot read a historical/original file: '+str(p))
            mode=values[1]if len(values)>1 else None;flags=values[2]if len(values)>2 else 0
            writing=isinstance(mode,str)and any(c in mode for c in('w','a','x','+'))or isinstance(flags,int)and bool(flags&(os.O_WRONLY|os.O_RDWR))
            if writing and not(p==out or p.is_relative_to(out)or p==temporary or p.is_relative_to(temporary)):raise PermissionError('Only the new result directory or launcher-owned temporary I/O is writable: '+str(p))
            opened.add(str(p))
    sys.addaudithook(audit)
    from app.lives import Store
    from app.native_tools import identity,physical
    from dee_thinking.persistence import load_world_snapshot
    engine=identity(out/'sistema');store=Store(out/'sistema')
    for p in m['parents']:
        src=HERE/p['snapshot'];assert digest(src)==p['sha256'];r=store.import_state(src,p['life'],p['profile'],expected=p['sha256'])
        for k in('N','tick','RAW_sha256','clocks_sha256'):assert r['physical'][k]==p['physical'][k],(p['life'],k)
        if p.get('checkpoint_alias'):shutil.copy2(src,out/'sistema/estado/checkpoints'/p['checkpoint_alias'])
    # Expected results are deliberately not read before this native execution.
    old_argv=sys.argv[:];errors=[]
    try:
        with (out/'PROTOCOLO.log').open('w',encoding='utf8')as log:
            from contextlib import redirect_stdout,redirect_stderr
            with redirect_stdout(log),redirect_stderr(log):
                active_overlay=set()
                for operation in m.get('api_program',[]):
                    for relative in active_overlay:
                        original=common/relative
                        if original.exists():shutil.copy2(original,out/'sistema'/relative)
                    active_overlay=set()
                    for ov in operation.get('overlay',[]):
                        destination=out/'sistema'/ov['destination'];destination.parent.mkdir(parents=True,exist_ok=True)
                        shutil.copy2(HERE/ov['relative'],destination);active_overlay.add(ov['destination'])
                    for module in list(sys.modules):
                        if module=='capacidades'or module.startswith('capacidades.'):del sys.modules[module]
                    importlib.invalidate_caches()
                    if operation.get('source_module'):
                        path=out/operation['source_module'];spec=importlib.util.spec_from_file_location('compendio_'+operation['case'],path)
                        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
                        if operation.get('refresh_deadline'):
                            from datetime import datetime,timezone,timedelta
                            module.DEADLINE=(datetime.now(timezone.utc)+timedelta(seconds=m['timeout_seconds'])).isoformat()
                        if operation.get('configure'):module.configure(out/'sistema')
                    else:module=importlib.import_module(operation['module'])
                    function=getattr(module,operation['function'])
                    work=out/'artefactos'/operation['parent'];work.mkdir(parents=True,exist_ok=True)
                    def substitute(v):
                        if isinstance(v,dict):return{k:substitute(x)for k,x in v.items()}
                        if isinstance(v,list):return[substitute(x)for x in v]
                        return work if v=='{work}'else out/'sistema'if v=='{system}'else v
                    kwargs=substitute(operation['kwargs'])
                    if operation.get('native_imports'):
                        from datetime import datetime,timezone,timedelta
                        support=sys.modules.get('arbol_umbral_adquirido_b01')
                        if support:
                            support.DEADLINE=datetime.now(timezone.utc)+timedelta(seconds=m['timeout_seconds']);support.B_MONOTONIC_DEADLINE=time.monotonic()+m['timeout_seconds']
                        kwargs['ni']=module.native_imports()
                        from capacidades import selector_acrecion_nativo as sel
                        kwargs['sel']=sel
                    original_parent=next(p for p in m['parents']if p['life']==operation['parent'])
                    result=store.mutate(operation['parent'],original_parent['original_operation'],lambda a:function(a,**kwargs))
                    relative=Path(*Path(operation['reference']).parts[1:]);dest=out/'evidencia/campanas'/relative
                    dest.parent.mkdir(parents=True,exist_ok=True);encoded=json.dumps({'case':operation['case'],'result':result},ensure_ascii=False,indent=2).encode('utf8')
                    dest.write_bytes(gzip.compress(encoded,mtime=0)if dest.suffix=='.gz'else encoded)
                for entry in m['entries']:
                    path=out/entry;sys.argv=[str(path)]
                    if m.get('explicit_snapshot'):
                        p=m['explicit_snapshot'];sys.argv+=['--snapshot',str(HERE/p['relative']),'--sha256',p['sha256']]
                    if m.get('prefix_only_external'):
                        tree=ast.parse(path.read_text(encoding='utf8'))
                        class Prefix(ast.NodeTransformer):
                            def visit_Call(self,node):
                                if isinstance(node.func,ast.Attribute)and node.func.attr=='act_external':return ast.copy_location(ast.Dict(keys=[ast.Constant('not_executed')],values=[ast.Constant('Historical suffix external step excluded from native composition prefix')]),node)
                                return self.generic_visit(node)
                        tree=ast.fix_missing_locations(Prefix().visit(tree));exec(compile(tree,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
                    else:runpy.run_path(str(path),run_name='__main__')
    except BaseException as e:
        errors.append({'type':type(e).__name__,'detail':str(e),'traceback':traceback.format_exc()})
    finally:sys.argv=old_argv
    checks=[]
    compare_references=[x['reference']for x in m['api_program']]if m.get('api_program')else m['references']
    for rel in compare_references:
        original=read(HERE/rel);name=Path(rel).name
        if name.endswith('.json.gz')and not original.get('case')and original.get('id'):name=name[:-3]
        camp=Path(rel).parts[1];within=Path(*Path(rel).parts[2:]);new=out/'evidencia/campanas'/camp/within
        if not new.exists()and new.suffix=='.gz':new=new.with_suffix('')
        if not new.exists():
            # Protocol declarations are explanatory; primaries must be present.
            if any(k in original for k in('data','rows','receipts')):checks.append({'reference':rel,'reproduced':False,'reason':'No resulting primary at '+str(new.relative_to(out))})
            continue
        current=read(new);ep=final_physical(original);np=final_physical(current);item={'reference':rel,'new_primary':str(new.relative_to(out)),'native_observations':len(observed(payload(original)))}
        if m.get('prefix_only_external')and rel in config.get('expected_snapshots',{}):
            world,_=load_world_snapshot(HERE/config['expected_snapshots'][rel],max_bytes=512*1024**2);ep=physical(world)
        ev=observed(payload(original));nv=observed(payload(current));item['exact_native_witnesses']=ev==nv
        if ep and np:
            fields=('N','tick','RAW_sha256','clocks_sha256');item['exact_full_RAW_and_clocks']=all(ep.get(k)==np.get(k)for k in fields);item['reference_physical']={k:ep.get(k)for k in fields};item['new_physical']={k:np.get(k)for k in fields}
        else:
            reference_state=config.get('expected_snapshots',{}).get(rel)
            pr=payload(current);final=pr.get('final',pr.get('final_snapshot',pr.get('snapshot',{})))if isinstance(pr,dict)else{}
            if reference_state and isinstance(final,dict)and final.get('path'):
                w,_=load_world_snapshot(HERE/reference_state,max_bytes=512*1024**2);wanted=physical(w)
                w,_=load_world_snapshot(Path(final['path']),max_bytes=512*1024**2);actual=physical(w)
                item['exact_full_RAW_and_clocks']=wanted==actual;item['reference_physical']=wanted;item['new_physical']=actual
        item['reproduced']=item.get('exact_full_RAW_and_clocks',item['exact_native_witnesses'])and item['exact_native_witnesses'];checks.append(item)
    result={'id':args.id,'mode':m['mode'],'elapsed_seconds':time.monotonic()-started,'engine':engine,'private_reads_isolated_by_allowlist':True,'read_paths':sorted(opened),'native_checks':checks,'errors':errors,'all_selected_primaries_match':bool(checks)and all(x['reproduced']for x in checks),'no_original_life_or_state_modified':True,'selected_case':args.case,'scope':'Technical replay of declared historical protocols on complete copies; identities, timestamps and host paths are new. Only native_checks listed here are re-executed. Other archived controls remain available for recalculation and explicit replay, not silently counted as reproduced. No claim of an independent scientific replication or combined knowledge.'}
    (out/'REPRODUCCION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k]for k in('id','elapsed_seconds','errors','all_selected_primaries_match')},ensure_ascii=False))
    return 0 if result['all_selected_primaries_match']and not errors else 2
if __name__=='__main__':raise SystemExit(main())
