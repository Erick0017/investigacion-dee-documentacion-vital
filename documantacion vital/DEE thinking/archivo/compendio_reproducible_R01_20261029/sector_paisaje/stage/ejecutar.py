"""Adaptador de reproducción técnica; nunca calcula la respuesta del ente.

Cada protocolo histórico se ejecuta en un proceso y Store aislados. Los
primarios de referencia se leen sólo al terminar para comparar las salidas.
"""
from pathlib import Path
import argparse,sys,json,gzip,hashlib,shutil,subprocess,importlib.util,os,time,tempfile
BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def get(d,pointer):
    for part in pointer.strip('/').split('/'):
        d=d[int(part)]if isinstance(d,list)else d[part]
    return d
def unpack(raw):
    v=int(raw);assert 0<=v<2**64 and not isinstance(raw,float)
    def sign(k):q=(v>>k)&15;return q-16 if q&8 else q
    return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'direction':[sign(k)for k in(48,52,56)],'semantic':(v>>60)&15}
def walk(d,path='$'):
    if isinstance(d,dict):
        yield path,d
        for k,v in d.items():
            if k not in('parent','commit'):yield from walk(v,path+'.'+k)
    elif isinstance(d,list):
        for i,v in enumerate(d):yield from walk(v,path+'['+str(i)+']')
def words(records):
    result=[]
    for key,row in records.items():
        r=unpack(row['raw']);v=r['direction']
        if r['state']==1 and r['semantic']==1 and v[1:]==[1,1]and abs(v[0])==1:result.append({'text':'cerca'if v[0]>0 else'lejos','bank':key,'native_X':v[0]})
    return result
def integrity_variant(v):
    ref=BASE/v['reference'];b=gzip.decompress(ref.read_bytes())
    assert hashlib.sha256(b).hexdigest()==v['reference_uncompressed_sha256']
    for f in v['source_files']:
        p=BASE/f['relative'];assert p.is_file()and sha(p)==f.get('stored_sha256',f['sha256']),str(p)
    return json.loads(b)
def recalc(m,out):
    data_root=out/'datos';rows=[];campaigns={};errors=[];field_count=0;query_count=0
    for v in m['variants']:
        d=integrity_variant(v);group,case=v['historical_case'].split('/',1);campaign=m['campaigns'][0]
        dest=data_root/campaign/group/case/'PRIMARIOS.json';save(dest,d);campaigns[campaign]=True
        for loc,r in walk(d):
            if {'raw','state','s_reg','direction','semantic'}<=r.keys():
                q=unpack(r['raw']);field_count+=1
                if any(q[k]!=r[k]for k in q):errors.append({'case':v['id'],'at':loc,'error':'RAW_FIELDS_MISMATCH'})
                if isinstance(r.get('clock'),float):errors.append({'case':v['id'],'at':loc,'error':'FLOAT_CLOCK'})
            if 'records'in r and'SPANISH_DECODED'in r and isinstance(r['records'],dict)and all(isinstance(x,dict)and'raw'in x for x in r['records'].values()):
                decoded=words(r['records']);query_count+=1
                if decoded!=r['SPANISH_DECODED']:errors.append({'case':v['id'],'at':loc,'error':'QUERY_DECODER_MISMATCH','computed':decoded,'stored':r['SPANISH_DECODED']})
        rows.append({'variant':v['id'],'source_uncompressed_sha256':v['reference_uncompressed_sha256'],'parent_tick':v.get('parent_tick'),'final_tick':d.get('post',{}).get('tick'),'historical_result':d.get('commit',{}).get('result')})
    reports={}
    for campaign in campaigns:
        source=BASE/'codigo'/campaign/'recalcular_original.py'
        if not source.exists():continue
        spec=importlib.util.spec_from_file_location('_recalculo_'+campaign,source);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        if campaign=='ESPANOL_FUNCIONAL_01':r=module.run(data_root/campaign);errors.extend(r['uint64_errors']+r['translated_record_mismatches'])
        elif campaign=='PAISAJE_CAUSAL_01':
            r=module.recompute(data_root/campaign);z=r['summary'];errors.extend([z]if z['cases_with_field_errors']or z['decoder_mismatches']or z['uint64_float_errors']else[])
        else:r=module.recompute(data_root/campaign);errors.extend(r['errors'])
        reports[campaign]=r
    causal={}
    if m['id']=='M122':
        spec=importlib.util.spec_from_file_location('_snapshot_reader',BASE/'codigo/observador_snapshot.py');observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
        snaps={v['case']:observer.Snapshot(BASE/v['causal_state6']['relative'])for v in m['variants']if v.get('causal_state6')}
        a,b=snaps['wall11'],snaps['wall17'];comparison=observer.compare(a,b);oa,ob=observer.organization(a),observer.organization(b)
        ja,jb=oa.pop('operations'),ob.pop('operations')
        causal={'snapshots':{k:s.summary()for k,s in snaps.items()},'comparison_wall11_wall17':comparison,'owner_equal_except_documentary_operations':oa==ob,'different_documentary_operation_journals':[ja,jb],
                'boundary':'RAW,clocks,interfaces,agendas,recibos y ejecución iguales; identidad documental y diarios de instrumentación diferentes. El futuro común no consulta estos diarios. No se afirma igualdad de bytes de los archivos.'}
        if not(comparison['prefix_through_execution_before_metadata_equal']and comparison['pending_equal']and comparison['channels_equal']and comparison['receipts_equal']and oa==ob):errors.append({'error':'AA13_COMPLETE_CAUSAL_BOUNDARY_NOT_EQUAL'})
    result={'mechanism':m['id'],'mode':'RECALCULO_DE_PRIMARIOS_SIN_MOTOR','new_native_ticks':0,'variants':rows,'raw_fields_recomputed':field_count,'lexical_queries_redecoded':query_count,'reports':reports,'causal_state_comparison':causal,'errors':errors}
    save(out/'RECALCULO.json',result);print(json.dumps({'mechanism':m['id'],'mode':result['mode'],'variants':len(rows),'errors':len(errors)}));return int(bool(errors))
def native(m,out,common,only=None):
    # common is the private minimal code/runtime extracted from this package,
    # never the installed original Cognitive system.
    common=common.resolve();results=[]
    if not(common/'app/lives.py').is_file():raise FileNotFoundError('Missing declared minimal common Store: '+str(common))
    for v in m['variants']:
        if only and v['id']not in only:continue
        result_file=out/v['id']/'RESULTADO.json'
        if result_file.exists():
            results.append(read(result_file));continue
        record=integrity_variant(v);folder=out/v['id'];job=folder/'trabajo';system=job/'sistema'
        hard=[s for s in v['pending']if not s.startswith('Revisión de dependencia histórica')]
        if hard:
            row={'variant':v['id'],'status':'BLOCKED_MISSING_PRIVATE_MATERIAL','reason':hard};save(result_file,row);results.append(row);continue
        shutil.copytree(common,system,ignore=shutil.ignore_patterns('__pycache__','*.pyc','estado'),dirs_exist_ok=False)
        for name in ['vidas','checkpoints','locks']:(system/'estado'/name).mkdir(parents=True,exist_ok=True)
        # No ACTIVO pointer is supplied; every legacy operation names its life.
        if v['parent_record']:
            parent=read(BASE/v['parent_record']);snapshot=BASE/v['parent_snapshot'];assert sha(snapshot)==parent['snapshot_sha256']
            target=system/parent['snapshot'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(snapshot,target)
            save(system/'estado/vidas'/parent['life_id']/'VIDA.json',parent)
        for ov in v['overrides']:
            src=BASE/ov['source'];assert sha(src)==ov['sha256'];dst=system/ov['module'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        for item in v.get('inputs',[]):
            source=BASE/item['source'];target=job/item['target'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        for campaign in ['PAISAJE_CAUSAL_01','ACCESO_ADAPTATIVO_01']:
            source=BASE/'codigo'/campaign
            if source.exists():shutil.copytree(source,job/'laboratorio/campanas'/campaign,dirs_exist_ok=True)
        campaign=m['campaigns'][0];src=BASE/v['protocol'];dest=job/'laboratorio/campanas'/campaign/src.name;dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():shutil.copy2(src,dest)
        assert sha(dest)==v['protocol_sha256'];physical_out=folder/'salida'
        command=[sys.executable,'-I','-B','-X','utf8',str(dest),'--system',str(system),'--out',str(physical_out),'--case',v['case']]
        env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1');env.pop('PYTHONPATH',None)
        begin=time.monotonic()
        with(folder/'stdout.log').open('w',encoding='utf8')as so,(folder/'stderr.log').open('w',encoding='utf8')as se:
            try:p=subprocess.run(command,cwd=tempfile.gettempdir(),env=env,stdout=so,stderr=se,timeout=m['native'].get('timeout_seconds',2400));exit_code=p.returncode
            except subprocess.TimeoutExpired:exit_code=124
        actual_file=physical_out/v['output_primary'];checks=[]
        if actual_file.exists():
            actual=read(actual_file)
            for pointer in v['checks']:
                try:a=get(actual,pointer);b=get(record,pointer);checks.append({'pointer':pointer,'matches':a==b,'actual':a,'reference':b})
                except(KeyError,IndexError,TypeError)as e:checks.append({'pointer':pointer,'matches':False,'error':str(e)})
        status='NATIVE_EXACT_COMPARISON_MATCHED'if exit_code==0 and checks and all(c['matches']for c in checks)else'NATIVE_REPRODUCTION_FAILED_OR_DIFFERENT'
        row={'variant':v['id'],'status':status,'exit_code':exit_code,'seconds':time.monotonic()-begin,'command':command,'checks':checks,'historical_dependencies_not_recovered':v['pending'],'adaptation':'Original protocol bytes and full historical parent. Current common modules only where historical dependency revision was not preserved; exact physical and functional outputs are tested, never assumed.'}
        save(result_file,row);results.append(row);print(json.dumps({'variant':v['id'],'status':status,'exit_code':exit_code,'seconds':round(row['seconds'],2)}),flush=True)
    final={'mechanism':m['id'],'mode':'NATIVE_PROTOCOL_REPRODUCTION_IN_ISOLATED_STORES','results':results,'matched':sum(r['status']=='NATIVE_EXACT_COMPARISON_MATCHED'for r in results),'total':len(results)}
    save(out/'REPRODUCCION.json',final);return int(final['matched']!=len(results))
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['native','recalc']);p.add_argument('mechanism');p.add_argument('--out',type=Path,required=True);p.add_argument('--common',type=Path);p.add_argument('--variant',action='append');a=p.parse_args()
    manifest=read(BASE/'sector.json');m=next(m for m in manifest['mechanisms']if m['id']==a.mechanism);a.out.mkdir(parents=True,exist_ok=True)
    return recalc(m,a.out)if a.mode=='recalc'else native(m,a.out,a.common,a.variant)
if __name__=='__main__':raise SystemExit(main())
