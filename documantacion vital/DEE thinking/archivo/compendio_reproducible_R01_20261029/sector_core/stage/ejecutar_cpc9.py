from pathlib import Path
import json,hashlib,os,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def compare(a,b,path=''):
    diffs=[]
    if type(a)!=type(b):
        if a==b:return []
        return [{'path':path,'actual':str(a)[:300],'expected':str(b)[:300]}]
    if isinstance(a,dict):
        for k in sorted(set(a)|set(b)):
            if k not in a or k not in b:diffs.append({'path':path+'/'+k,'missing':True})
            else:diffs+=compare(a[k],b[k],path+'/'+k)
    elif isinstance(a,list):
        if len(a)!=len(b):diffs.append({'path':path,'lengths':[len(a),len(b)]})
        for i,(x,y) in enumerate(zip(a,b)):diffs+=compare(x,y,path+'/'+str(i))
    elif a!=b:diffs.append({'path':path,'actual':a,'expected':b})
    return diffs
def execute(identifier,mat,out,package,recalc=False):
    if identifier=='M038' and recalc:return recalc_k65_limits(mat,out)
    if identifier in ('M039','M040','M041'):
        if recalc:return recalc_observers(identifier,mat,out)
        from ejecutar_core1517 import execute as core1517
        return core1517(identifier,mat,out,package)
    if identifier in ('M042','M043','M044','M045','M046','M047'):
        from ejecutar_ingenierias import execute as engineering
        return engineering(identifier,mat,out,package,recalc)
    spec=json.loads((ROOT/'configuraciones/CPC9_RECUPERACION.json').read_text(encoding='utf8'))
    cases=[x for x in spec['cases'] if x['mechanism']==identifier]
    if not cases:raise ValueError('Mecanismo desconocido: '+identifier)
    report={'mechanism':identifier,'mode':'ARCHIVED_RECALCULATION' if recalc else 'NATIVE_CONTINUATION' if identifier=='M036' else 'NATIVE_REPRODUCTION','status':'RUNNING','cases':[],'historical_folders_required':False}
    for item in cases:
        ref=mat/item['reference'];assert sha(ref)==item['reference_sha256'];expected=json.loads(ref.read_text(encoding='utf8'))
        if recalc:
            report['cases'].append({'case':item['id'],'status':'ARCHIVED_PRIMARY_LOADED','final_physical':expected.get('final_physical'),'requests':len(expected.get('requests',[])),'qualifier':'Inspección de primario y hash, no evolución nativa ni recálculo funcional completo'});continue
        source=mat/item['source_root']
        for n,h in item['source_versions'].items():assert sha(source/n)==h,(item['id'],n)
        target=out/'casos'/item['id'];assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
        cfg=dict(item['input_configuration']);argv=[]
        for key,value in cfg.items():
            if value is None or key in ('schema','stage','dimension'):continue
            flag='--'+key.replace('_','-')
            if isinstance(value,bool):
                if value:argv.append(flag)
            elif isinstance(value,(int,float,str)):argv.extend([flag,str(value)])
        if item.get('parent_snapshot'):argv.extend(['--parent',str(mat/item['parent_snapshot'])])
        argv.extend(['--out',str(target)])
        command=[sys.executable,'-I','-B',ROOT/'replay_native.py','--script',source/item['entry'],'--output',target,'--allow-root',mat,'--',*argv]
        logs=out/'logs';logs.mkdir(exist_ok=True)
        with (logs/(item['id']+'.stdout.log')).open('w',encoding='utf8') as so,(logs/(item['id']+'.stderr.log')).open('w',encoding='utf8') as se:
            child=subprocess.Popen(list(map(str,command)),cwd=out,stdout=so,stderr=se,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            try:code=child.wait(timeout=1200)
            except subprocess.TimeoutExpired:child.kill();child.wait();code=-1
        result=target/'MEDICIONES.json';actual=json.loads(result.read_text(encoding='utf8')) if result.is_file() else {}
        keys=[k for k in ('geometry','initial_physical','preparations','restored_continuations','architecture_changed','parent_identifier','frames','local_neighborhoods','decisive_local','MAIN_RAW_clock_edits','requests','final_physical','receipt_statuses','auditor_experiences','queries','rows','trace','source_file_unchanged','parent_file_unchanged','parent_unchanged') if k in expected]
        # Los SHA de contenedores y ubicaciones del anfitrión son procedencia.
        # El núcleo físico, orden, recibos y ventanas se comparan exactamente.
        diffs=compare({k:actual.get(k) for k in keys},{k:expected[k] for k in keys})
        accesses=json.loads((target/'ACCESOS_DEL_PROCESO.json').read_text(encoding='utf8')) if (target/'ACCESOS_DEL_PROCESO.json').is_file() else {'denied_files':['missing audit report']}
        row={'case':item['id'],'status':'PASS' if code==0 and not diffs and not accesses['denied_files'] else 'FAIL','exit_code':code,'compared_fields':keys,'differences':diffs[:100],'difference_count':len(diffs),'reference_sha256':item['reference_sha256'],'primary_sha256':sha(result) if result.is_file() else None,'command':list(map(str,command)),'blocked_reads':accesses['denied_files']}
        report['cases'].append(row);put(out/'RESULTADO.json',report)
    report['status']='PASS' if all(x['status']=='PASS' for x in report['cases']) else 'ARCHIVED_INSPECTION_ONLY' if recalc else 'FAIL'
    report['scope']='Realizaciones y controles históricos aislados; la vida actual de Cognitive no se carga. M036 usa el estado histórico completo T884 incluido, no reconstruye otra biografía.'
    return report

def recalc_k65_limits(mat,out):
    """Recalculate frozen K65 readouts and final rejections, with zero ticks."""
    from collections import Counter
    base=mat/'cpc9/limites';loaded={};sources=[]
    names=('E1_MAIN_K65_1907_2353','E1_CF_K65_NO_EVENT','E1_CF_K65_UNPAIRED','E1_MAIN_TAIL_2353_2493','E1_TAIL_NO_NEW')
    for name in names:
        p=base/name/'MEDICIONES.json';loaded[name]=json.loads(p.read_bytes());sources.append({'case':name,'primary':p.relative_to(mat).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
    def raw_fields(value):
        raw=int(value)
        if not 0<=raw<2**64:raise ValueError('RAW outside uint64')
        return raw&0xffffffff,(raw>>60)&15,[((raw>>k)&15)-(16 if ((raw>>k)&15)>=8 else 0) for k in (48,52,56)]
    cases=[];checks={}
    for name in names[:3]:
        primary=loaded[name];experiences={x['form']:x for x in primary['auditor_experiences']};groups=[];current=[]
        for frame in primary['frames']:
            queries=frame.get('repertoire_queries',[])
            if not queries:continue
            if queries[0]['form']=='F00' and current:groups.append(current);current=[]
            for q in queries:
                state,semantic,direction=raw_fields(q['physical']['raw'])
                # The teacher labels are used only by this external evaluator.
                # The historical decoder was frozen before the Native run.
                sign=experiences[q['form']]['actual_event_direction'][1]
                expected=[0,sign,1 if q['query_index']%2==0 else 0]
                if q['expected_auditor_direction']!=expected:raise ValueError('Frozen decoder/history mismatch')
                current.append({'form':q['form'],'query_index':q['query_index'],'tick':q['physical']['tick'],'raw':q['physical']['raw'],'clock':q['physical']['clock'],'state':state,'semantic':semantic,'direction':direction,'expected':expected,'correct':bool(state and semantic==1 and direction==expected)})
        if current:groups.append(current)
        rounds=[]
        for q in groups:
            if len({x['form'] for x in q})!=len(q):raise ValueError('Duplicate form in a sweep')
            rounds.append({'first_tick':q[0]['tick'],'last_tick':q[-1]['tick'],'requested_readouts':len(q),'correct':sum(x['correct'] for x in q),'incorrect_or_invalid':sum(not x['correct'] for x in q),'readouts':q})
        full=[x for x in rounds if x['requested_readouts']==65]
        expected=[57,53,4] if name==names[0] else [0,0,0]
        checks[name+'_three_full_sweeps']=[x['correct'] for x in full]==expected and len(full)==3
        cases.append({'case':name,'rounds':rounds,'full_sweep_counts':[{'correct':x['correct'],'total':65,'first_tick':x['first_tick'],'last_tick':x['last_tick']} for x in full],'recorded_queries':len(primary['queries']),'recalculated_readouts':sum(len(x) for x in groups)})
    before=loaded[names[0]];tail=loaded[names[3]];control=loaded[names[4]]
    old_ids={x['id'] for x in before['requests']}
    new=[x for x in tail['requests'] if x['id'] not in old_ids];statuses=dict(Counter(x['receipt']['status'] for x in new))
    checks['tail_178_new_requests']=len(new)==178 and len({x['id'] for x in new})==178
    checks['tail_177_rejected_one_applied']=statuses=={'rejected_occupied':177,'applied':1}
    fields=('tick','RAW_sha256','clocks_sha256');same={k:tail['final_physical'][k]==control['final_physical'][k] for k in fields}
    checks['tail_and_no_new_same_final_RAW_clocks_tick']=all(same.values()) and tail['final_physical']['tick']==2493
    report={'mechanism':'M038','mode':'ARCHIVED_RECALCULATION','status':'PASS' if all(checks.values()) else 'FAIL','new_native_ticks':0,'sources':sources,'cases':cases,'tail':{'new_requests':len(new),'statuses':statuses,'exact_new_receipts':new,'final':tail['final_physical'],'no_new_final':control['final_physical'],'equality_of_recorded_fields':same,'not_full_causal_state_identity_proof':True},'checks':checks,'scope':'Opaque acquired directional forms of this historical E1 and its controls; not65NSM meanings. Exact decoder uses uint64 RAW. Full-world snapshots/interfaces/pending queues are not reconstructed by matching the recorded RAW/clock digests.'}
    put(out/'K65_Y_COLA_RECALCULADOS.json',report)
    return report
def recalc_observers(identifier,mat,out):
    target=out/'OBSERVADORES_RECALCULADOS.json'
    command=[sys.executable,'-I','-B','-X','utf8',ROOT/'reproduccion/recalcular_observadores.py','--materialized',mat,'--out',target]
    run=subprocess.run(list(map(str,command)),cwd=out,capture_output=True,text=True,timeout=120)
    (out/'stdout.log').write_text(run.stdout,encoding='utf8');(out/'stderr.log').write_text(run.stderr,encoding='utf8')
    value=json.loads(target.read_text(encoding='utf8')) if target.is_file() else {}
    return {'mechanism':identifier,'mode':'ARCHIVED_RECALCULATION','status':'PASS' if run.returncode==0 else 'FAIL','recalculated':value,'command':list(map(str,command)),'scope':'Recálculo de observadores de CORE15–17 desde primarios; no reproducción nativa de esos tres paquetes.'}
