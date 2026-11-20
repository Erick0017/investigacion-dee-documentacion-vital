"""Portable archive-only RAW/effect/receipt recalculation for four brief forks.

Export requires all four originally authorized, closed branches. No Native
import, evolution, SQLite or response selection. Recalc only uses exported data.
"""
import argparse
from array import array
from collections import Counter
import csv
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
EV=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/NIVELES_BREVES_AUX_R02'
PARENT=ROOT/'sistema/estado/fuentes_emparejadas/APD04_MAIN_T639374_EXPLORACION_R01/VIDA.deetsnap.gz'
PSHA='771e041363b39ef830603cb32ed2bbe7fc5938e4783a9dfe2a733a6e3ee4f9a8'


def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
    b=Path(p).read_bytes();return json.loads(gzip.decompress(b)if b[:2]==b'\x1f\x8b'else b)
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def walk(v,loc='$'):
    yield loc,v
    if isinstance(v,dict):
        for k,x in v.items():
            if k in('result','result_json')and isinstance(x,str):
                try:x=json.loads(x)
                except json.JSONDecodeError:pass
            yield from walk(x,loc+'.'+k)
    elif isinstance(v,list):
        for i,x in enumerate(v):yield from walk(x,loc+'['+str(i)+']')
def fields(raw):
    n=int(raw)
    if not 0<=n<2**64:raise ValueError('Exact uint64 required')
    return n&0xffffffff,(n>>60)&15,[((n>>k)&15)-(16 if((n>>k)&15)>=8 else 0)for k in(48,52,56)]
def numid(x):return x if type(x)is int else int(x)if isinstance(x,str)and x.isdecimal()else None
def receipt_ids(value):
    found=set()
    for _,n in walk(value):
        if isinstance(n,dict)and isinstance(n.get('receipt'),dict):
            rid=numid(n['receipt'].get('id'))
            if rid is not None:found.add(rid)
    return sorted(found)
def gates36():
    result={}
    for origin,ds in [((33,33,33),[(1,0,0),(0,1,0),(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0),(-1,0,0),(0,-1,0)]),
        ((47,47,47),[(-1,0,0),(0,-1,0),(1,0,0),(0,1,0)]),((47,17,47),[(1,0,0),(0,1,0)]),
        ((47,7,47),[(-1,0,0),(0,-1,0),(1,0,0),(1,1,0)])]:
        for d in ds:
            for sign in(-1,1):result[tuple((origin[i]+4*d[i]+(sign if i==2 else 0)) % 67 for i in range(3))]=(sign,[0,0,sign])
    return result
G36=gates36()


def decode_reader(reader,kind):
    obs=reader.get('observations',reader.get('panel',[]))
    expected=({(25+2*x,15,53):(x,[x,1,0])for x in(-1,0,1)}if kind=='selector'else
        {(15+2*x,17,15+2*z):(x,[x,1,z])for x in(-1,0,1)for z in(0,-1)}if kind=='numeric'else G36)
    coverage=len(obs)==len(expected)and{tuple(o['site'])for o in obs}==set(expected)
    if not coverage:raise ValueError('Frozen '+kind+' reader coverage differs')
    candidates=[]
    for o in obs:
        st,se,di=fields(o['raw']);sign,direction=expected[tuple(o['site'])]
        if st and se==1 and di==direction:candidates.append(sign)
    return(candidates[0]if len(candidates)==1 else None),len(candidates),obs


def scan_journal(data):
    source_rows=[json.loads(line)for line in data.splitlines()]
    works={};lex={};receipt_witnesses={};issues=[];checks=[];events=[]
    for line,top in enumerate(source_rows,1):
        if top.get('kind')=='scheduled_material_result':
            events.append({'line':line,'id':top.get('requested_id'),'event':top.get('event'),
                'window_seconds':top.get('window_seconds'),'lateness_seconds':top.get('lateness_seconds')})
        for loc,n in walk(top,'line'+str(line)):
            if not isinstance(n,dict):continue
            if isinstance(n.get('receipt'),dict):
                r=n['receipt'];rid=numid(r.get('id'))
                if rid is not None:receipt_witnesses.setdefault(rid,[]).append({'locator':loc,'receipt':r,
                    'channel':n.get('channel',n.get('port')),'wrapper':'port'if'port'in n else'channel'if'channel'in n else'neither'})
            if set(('public_before','committed_effect','selection'))<=set(n):
                s=n['selection'];r=s.get('reader',s.get('native_trial',{}).get('reader',{}));key=(n['episode'],s.get('query_tick'))
                if key in works:continue
                sign,count,obs=decode_reader(r,'selector');effect=n['committed_effect'];codec=effect.get('prepared_action_codec','R01')
                maps={'R01':{-1:'USE',0:'INSPECT',1:'INSPECT'},'R02':{-1:'INSPECT',0:'INSPECT',1:'USE'}}
                if codec not in maps:raise ValueError('Explicit newer action codec requires separate revision')
                action=maps[codec].get(sign)
                checks += [{'check':'selector_RAW','ok':sign==s.get('physical_choice',s.get('native_trial',{}).get('physical_choice')),'locator':loc},
                    {'check':'action_codec_'+codec,'ok':action==n.get('physical_action'),'locator':loc}]
                prim=n.get('native_operation');psign=None;pobs=[]
                if prim:
                    psign,pc,pobs=decode_reader(prim['native_trial']['reader'],'numeric')
                    checks.append({'check':'numeric_RAW','ok':psign==prim.get('physical_choice'),'locator':loc})
                public=n['public_before'];aud=n.get('auditor_only_after_effect')
                eligible=public['tag']==public['goal_tag'];useful=False
                if effect.get('actuator')=='nulled':useful=False
                elif action=='INSPECT':useful=bool(effect['new_fact'])and eligible
                elif 'actual_bin'in effect:
                    if aud is None:raise ValueError('Cannot recalc stale/version correctness without audit data')
                    expected=(aud['actual_source_value']>aud['criterion'])-(aud['actual_source_value']<aud['criterion'])
                    correct=psign==expected and aud['observed_version']==aud['source_version']
                    checks.append({'check':'class_current_value_version','ok':correct==effect['correct'],'locator':loc})
                    useful=correct and eligible and effect['previous_bin']!=psign
                elif 'loads_before'in effect:
                    lb=effect['loads_before'];la=effect['loads_after'];gb=abs(lb[0]-lb[1]);ga=abs(la[0]-la[1])
                    expectedloads=list(lb)
                    if psign==1 and lb[0]>0 and lb[1]<20:expectedloads=[lb[0]-1,lb[1]+1]
                    elif psign==-1 and lb[1]>0 and lb[0]<20:expectedloads=[lb[0]+1,lb[1]-1]
                    checks.append({'check':'fixed_native_to_load_transduction','ok':expectedloads==la,'locator':loc})
                    useful=(ga<gb or(psign==0 and gb==0))and eligible
                checks.append({'check':'frozen_new_gain','ok':useful==bool(effect['useful']),'locator':loc})
                works[key]={'locator':loc,'episode':n['episode'],'query_tick':s.get('query_tick'),'read_tick':r.get('tick'),
                    'public':public,'raw_sensor_components':n.get('raw_sensor_components'),'selector_RAW':obs,
                    'RAW_selector_sign':sign,'selector_candidate_count':count,'prepared_action_codec':codec,
                    'action':action,'numeric_RAW':pobs,'RAW_numeric_sign':psign,'effect':effect,
                    'native_receipt_IDs':receipt_ids(n),
                    'auditor_only_after_effect':aud,'eligible_by_tag':eligible,'recalculated_old_gain':useful,
                    'feedback':n.get('feedback'),'native_return_category':(n.get('native_return')or{}).get('category')}
            if n.get('kind')=='APD04_common36_lexical_query':
                key=(n['form'],n['read_tick'])
                if key in lex:continue
                sign,count,obs=decode_reader(n['reader'],'lexical')
                checks.append({'check':'common36_RAW','ok':sign==n['reader'].get('formed_native_command'),'locator':loc})
                lex[key]={'locator':loc,'form':n['form'],'read_tick':n['read_tick'],'RAW_sign':sign,'candidate_count':count,'RAW_observations':obs,
                    'native_receipt_IDs':receipt_ids(n)}
    return{'works':list(works.values()),'lexical':list(lex.values()),'receipt_witnesses':receipt_witnesses,
        'checks':checks,'events':events,'issues':issues}


def buffer_summary(rawbytes,clockbytes,N):
    raw=array('Q');raw.frombytes(rawbytes);clock=array('Q');clock.frombytes(clockbytes)
    if sys.byteorder!='little':raw.byteswap();clock.byteswap()
    if len(raw)!=N**3 or len(clock)!=N**3:raise ValueError('Array length differs')
    return{'sites':len(raw),'occupied':sum(bool(x&0xffffffff)for x in raw),'raw_nonzero':sum(bool(x)for x in raw),
        'state_zero_raw_nonzero':sum(bool(x)and not(x&0xffffffff)for x in raw),'max_s_reg':max((x>>32)&65535 for x in raw),
        'state_counts':dict(Counter(str(x&0xffffffff)for x in raw)),'clock_min':min(clock),'clock_max':max(clock),
        'RAW_sha256':sha(rawbytes),'clocks_sha256':sha(clockbytes)}


def u64(b):
    v=array('Q');v.frombytes(b)
    if sys.byteorder!='little':v.byteswap()
    return v


def recalc(base):
    index=read(base/'INDICE.json');report={'schema':'APD04.brief_source_count.N0.recalculated.R01','new_Native_ticks':0,'branches':[],'checks':[]}
    if(base/'MANIFIESTO.json').exists():
        for member in read(base/'MANIFIESTO.json')['members']:
            report['checks'].append({'check':'export_member_exact_hash','ok':sha((base/member['file']).read_bytes())==member['sha256'],'file':member['file']})
    pf=read(base/index['prefix_physical_witness_file'])
    oldbaseline=read(base/index['old4_preexisting_baseline_recalculation'])
    frozen_old={r['name']:r['RAW_sign']for r in oldbaseline['rows']if r['family']=='forms'and r['name']in('suma','resta','compara','recuerda')}
    if set(frozen_old)!=set(('suma','resta','compara','recuerda')):raise ValueError('Preexisting old4 baseline incomplete')
    report['old4_expected_signs_and_source']={'expected':frozen_old,'source':index['old4_preexisting_baseline_recalculation'],
        'primary_line_sha256':oldbaseline['primary_line_sha256'],'scope':'Expected signs come from the closed same-line MAIN inherited panel before these four branches, not from their favorable results.'}
    prb=gzip.decompress((base/pf['raw_file']).read_bytes());pcb=gzip.decompress((base/pf['clock_file']).read_bytes())
    prold,pcold=u64(prb),u64(pcb)
    report['checks'].append({'check':'prefix_RAW_clocks','ok':buffer_summary(prb,pcb,pf['N'])==pf['calculated_physical']})
    for item in index['branches']:
        path=base/item['journal_export'];z=path.read_bytes();b=gzip.decompress(z)
        report['checks'] += [{'check':'journal_original_exact_bytes','ok':sha(b)==item['journal_original_sha256'],'branch':item['sources']},
            {'check':'journal_gzip_exact_bytes','ok':sha(z)==item['journal_export_sha256'],'branch':item['sources']}]
        result=scan_journal(b);fw=read(base/item['physical_witness_file']);rb=gzip.decompress((base/fw['raw_file']).read_bytes());cb=gzip.decompress((base/fw['clock_file']).read_bytes())
        phys=buffer_summary(rb,cb,fw['N'])
        report['checks'].append({'check':'full_RAW_clocks_hash_and_physical','ok':phys==fw['calculated_physical'],'branch':item['sources']})
        rs=read(base/item['receipt_delta_file']);new=rs['new_receipts'];w=result.pop('receipt_witnesses');missing=[];wrong=[]
        for r in new:
            rid=r['id'];witness=w.get(rid,[]);terminal=[x['receipt']['status']for x in witness if x['receipt'].get('status')not in('scheduled','pending','admitted')]
            expected={2:'applied',5:'rejected_occupied'}.get(r['status'])
            if not witness:missing.append(rid)
            elif expected is not None and(expected not in terminal or any(x!=expected for x in terminal)):wrong.append({'id':rid,'native':r['status'],'witnesses':terminal})
        report['checks'].append({'check':'FULL_terminal_all_new_IDs_union_port_channel','ok':not missing and not wrong,'branch':item['sources'],
            'missing_IDs':missing,'wrong_terminal':wrong})
        checks=result.pop('checks');report['checks']+=checks
        nr,nc=u64(rb),u64(cb);dt=fw['tick']-pf['tick']
        workids={i for w0 in result['works']for i in w0['native_receipt_IDs']}
        oldids={i for l in result['lexical']if l['form']in('suma','resta','compara','recuerda')for i in l['native_receipt_IDs']}
        fullbyid={r['id']:r for r in new}
        dose={}
        for label,ids in(('work_rows',workids),('old4_queries',oldids),('other_exported_new_IDs',set(fullbyid)-workids-oldids)):
            dose[label]={'requested_unique_IDs':len(ids),'terminal_statuses':dict(Counter(str(fullbyid[i]['status'])for i in ids if i in fullbyid)),
                'IDs_outside_final_delta':sorted(ids-set(fullbyid)),'IDs':sorted(ids)}
        result.update(sources=item['sources'],life=item['life'],initial_tick=item['initial_tick'],final_tick=fw['tick'],
            physical=phys,unique_new_native_IDs=len(new),terminal_native_statuses=dict(Counter(str(r['status'])for r in new)),
            dose_by_scope=dose,
            physical_difference_from_shared_prefix={'RAW_different_sites':sum(a!=b for a,b in zip(prold,nr)),
                'clocks_different_sites':sum(a!=b for a,b in zip(pcold,nc)),
                'clocks_all_advance_exact_elapsed_ticks':all(b-a==dt for a,b in zip(pcold,nc))},
            old_gain=sum(r['recalculated_old_gain']for r in result['works']),actions=dict(Counter(str(r['action'])for r in result['works'])),
            wrapper=read(base/item['wrapper_file']),closed=item['closed'],pairs_local_only=item['pair_locator'],
            same_prefix_not_independent_learner=True)
        oldlex=[v for v in result['lexical']if v['form']in('suma','resta','compara','recuerda')]
        result['functional_denominators']={'work_opportunities_planned':5,'work_opportunities_completed':len(result['works']),
            'selector_formed_unique_responses':sum(v['RAW_selector_sign']is not None for v in result['works']),
            'selector_unformed_or_ambiguous':sum(v['RAW_selector_sign']is None for v in result['works']),
            'environment_NEW_gain':result['old_gain'],'eligible_tag_opportunities':sum(v['eligible_by_tag']for v in result['works']),
            'old4_queries_planned':4,'old4_queries_completed':len(oldlex),
            'old4_unique_expected_sign':sum(v['RAW_sign']==frozen_old[v['form']]for v in oldlex),
            'old4_unformed_or_ambiguous':sum(v['RAW_sign']is None for v in oldlex),
            'old4_wrong_unique_sign':sum(v['RAW_sign']is not None and v['RAW_sign']!=frozen_old[v['form']]for v in oldlex)}
        report['branches'].append(result)
    report['issues']=[x for x in report['checks']if not x['ok']]
    report['pairwise_endpoint_RAW_only']=[{'source_counts':[a['sources'],b['sources']],
        'RAW_equal':a['physical']['RAW_sha256']==b['physical']['RAW_sha256'],
        'clocks_equal':a['physical']['clocks_sha256']==b['physical']['clocks_sha256'],
        'complete_causal_state_equality_not_claimed':True}for i,a in enumerate(report['branches'])for b in report['branches'][i+1:]]
    jobs=[x['wrapper']['final_total_job']for x in report['branches']]
    report['budget_and_resource_scope']={'logistic_wall_seconds_including_import_and_seals':index['logistic_wall_seconds'],
        'original_new_arm_start_cut_seconds':2400,'minimum_remaining_before_each_arm':510,
        'per_arm_outer_wall_guard_seconds':480,'Native_owner_limit_bytes':536870912,
        'wrapper_tree_limit_bytes':1073741824,'OMP_NUM_THREADS':1,
        'sum_disjoint_wrapper_job_CPU_seconds':sum(j['cpu_user_seconds']+j['cpu_kernel_seconds']for j in jobs),
        'max_wrapper_job_peak_committed_bytes':max(j['peak_job_committed_bytes']for j in jobs),
        'scope':'Each wrapper Job includes its own driver+Native owner+descendants; disjoint sequential jobs may be summed, but owner subjobs are NOT added again. N0 import/seal CPU and whole-machine energy/RAM are NOT measured. Actual full logistics wall is separately reported; CPU speed is not a cognitive-capacity criterion.'}
    report['scope']='Four FULL forks from one trained past, five opportunities each; external2/5/10/20sources, NativeN67 fixed. First five cursor slots only, not20simultaneous or20objects examined. Cache/circular view/tool pipeline/codec prepared. Real new-gain feedback is a posteffect external transduction; Native selects action. RAW/clocks exports are observations, not complete continuable snapshots.'
    report['attribution']={
        'DEE':'Material tag/goal inputs, native selector evolution and the fixed RAW reader determine the emitted sign. A USE may then invoke an inherited lexical association and Native scalar comparison. These are not a host policy computing the selected answer.',
        'host_preparation':'External object list, circular source cursor, environmental cache, fixed action codec R02, tool sequence, timing and objective/quality evaluation are prepared. Extra external sources do not add Native cells or automatically teach their values.',
        'INSPECT_limit':'new_fact updates the environmental observed-value/version cache. A number cached by the environment is NOT thereby a newly acquired Native scalar memory.',
        'old_gain_limit':'Old useful measures NEW environmental gain under tag relevance, not every correct maintenance action, utility of silence, general control or acquisition of a policy.',
        'history_and_sample_limit':'Four dependent forks of one past, not independent learners. Repeated questions are material interactions. Five short opportunities cannot settle late failure or scalable Native semantic capacity.',
        'no_cognitive_overclaim':'Matching four old lexical signs is a limited material access panel, not retention of every old capability or human understanding of four words.'}
    return report


def export(out):
    if out.exists():raise FileExistsError('New revision only')
    if not(EV/'CIERRE_CUATRO_RAMOS.json').is_file():raise ValueError('All four closed arms required')
    spec=importlib.util.spec_from_file_location('snapshot_read_only_no_Native',ROOT/'sistema/capacidades/observador_causal_retrospectivo_01.py')
    obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs)
    parent=obs.Snapshot(PARENT,verify_checksum=False)
    if parent.encoded_sha256!=PSHA:raise ValueError('Wrong trained past')
    before={r['id']:r for r in parent.receipts};out.mkdir(parents=True)
    index={'schema':'APD04.brief_source_count.essential.N0.R01','parent_snapshot_sha256':PSHA,'parent_tick':parent.tick,
        'Native_checksum_note':'Encoded SHA+gzip CRC+known-format parsed; FNV not repeated in this N0 export. Existing Native import verification remains indexed locally.',
        'branches':[],'omissions':['Complete snapshots, SQLite transport and worker artefacts remain at exact paired local paths; this is not an operative backup.']}
    index['logistic_wall_seconds']=read(EV/'CIERRE_CUATRO_RAMOS.json')['total_wall_seconds']
    code_index=[]
    logistic=read(EV/'PLAN_LOGISTICO_CERRADO_ANTES_IMPORT.json')
    for source in logistic['sources']:
        b=(EV/source['copy']).read_bytes()
        if sha(b)!=source['sha256']:raise ValueError('Exact executed source copy changed')
        name='CODIGO_EJECUTADO/'+Path(source['copy']).name
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb')as f:f.write(b)
        code_index.append({'source':source['source'],'export':name,'sha256':sha(b)})
    index['exact_executed_code_copied_once']=code_index
    def original(src,name):
        b=src.read_bytes();p=out/name;p.parent.mkdir(parents=True,exist_ok=True);z=gzip.compress(b,compresslevel=9,mtime=0)
        with p.open('xb')as f:f.write(z)
        if gzip.decompress(p.read_bytes())!=b:raise ValueError('Compression not byte-exact')
        return name,sha(b),sha(z)
    oldbase=ROOT/'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/PANEL_HEREDADO_RAW_N0_R01'
    oldfile,_,_=original(oldbase/'RECALCULO_PANEL_HEREDADO.json','EVIDENCIA/BASELINE_OLD4/RECALCULO_PANEL_HEREDADO.json.gz')
    index['old4_preexisting_baseline_recalculation']=oldfile
    original(oldbase/'PANEL_EVENTO_ORIGINAL.jsonl.gz','EVIDENCIA/BASELINE_OLD4/PANEL_EVENTO_ORIGINAL.jsonl.gz.outer.gz')
    prefixstem='EVIDENCIA/PREFIJO';(out/prefixstem).mkdir(parents=True)
    prb=obs.pbytes(parent.raw);pcb=obs.pbytes(parent.clocks)
    prf=prefixstem+'/RAW_u64le.bin.gz';pcf=prefixstem+'/CLOCK_u64le.bin.gz'
    for file,b in((prf,prb),(pcf,pcb)):
        with(out/file).open('xb')as f:f.write(gzip.compress(b,compresslevel=9,mtime=0))
    pff=prefixstem+'/TESTIGO_FISICO.json'
    write(out/pff,{'N':parent.N,'tick':parent.tick,'snapshot_local':str(PARENT),'snapshot_encoded_sha256':PSHA,
        'raw_file':prf,'clock_file':pcf,'calculated_physical':buffer_summary(prb,pcb,parent.N),
        'pending_native':parent.pending,'interfaces':parent.channels,
        'environment_metadata_exact_string':parent.metadata.get('DEE.Cognitive.System.1.1.APD04.ecosystem.R01'),
        'not_complete_operational_state':True,'no_ticks':True})
    index['prefix_physical_witness_file']=pff
    for n in(2,5,10,20):
        folder=EV/('N'+str(n));closed=read(folder/'CIERRE_RAMA.json')
        if closed['supervision']['final_total_job']['job_active_processes']!=0:raise ValueError('No stopped proof')
        initial=obs.Snapshot(ROOT/'sistema'/closed['initial_record']['snapshot'],verify_checksum=False)
        if initial.encoded_sha256!=closed['initial_record']['snapshot_sha256']:raise ValueError('Initial imported snapshot differs')
        initial_equivalence={'tick_N_equal':initial.tick==parent.tick and initial.N==parent.N,
            'RAW_exact_equal':obs.pbytes(initial.raw)==prb,'clocks_exact_equal':obs.pbytes(initial.clocks)==pcb,
            'interfaces_exact_equal':initial.channels==parent.channels,'pending_native_exact_equal':initial.pending==parent.pending,
            'environment_metadata_exact_equal':initial.metadata.get('DEE.Cognitive.System.1.1.APD04.ecosystem.R01')==parent.metadata.get('DEE.Cognitive.System.1.1.APD04.ecosystem.R01'),
            'full_causal_documentary_identity_not_claimed_equal':True,
            'reason':'Import declares another life/world and transport ancestry; only listed physical/operational fields are equal.'}
        if not all(initial_equivalence[k]for k in('tick_N_equal','RAW_exact_equal','clocks_exact_equal','interfaces_exact_equal','pending_native_exact_equal','environment_metadata_exact_equal')):
            raise ValueError('Imported physical/environmental parent differs')
        snap=obs.Snapshot(ROOT/'sistema'/closed['final_record']['snapshot'],verify_checksum=False)
        if snap.encoded_sha256!=closed['final_record']['snapshot_sha256']:raise ValueError('Final snapshot bytes differ')
        stem='EVIDENCIA/N'+str(n);jf,js,jz=original(folder/'SUPERVISION/TRAYECTORIA/EVENTOS.jsonl',stem+'/EVENTOS.jsonl.gz')
        wr,_,_=original(folder/'SUPERVISION/RESULTADO_SUPERVISION.json',stem+'/SUPERVISION.json.gz')
        original(folder/'PLAN_CERRADO_CON_ESTADO_REAL.json',stem+'/PLAN_CERRADO.json.gz')
        original(folder/'CIERRE_RAMA.json',stem+'/CIERRE_RAMA.json.gz')
        raw=obs.pbytes(snap.raw);clock=obs.pbytes(snap.clocks)
        rf=stem+'/RAW_u64le.bin.gz';cf=stem+'/CLOCK_u64le.bin.gz'
        for file,b in((rf,raw),(cf,clock)):
            with(out/file).open('xb')as f:f.write(gzip.compress(b,compresslevel=9,mtime=0))
        env=snap.metadata.get('DEE.Cognitive.System.1.1.APD04.ecosystem.R01')
        fw={'N':snap.N,'tick':snap.tick,'snapshot_local':str(snap.path),'snapshot_encoded_sha256':snap.encoded_sha256,
            'raw_file':rf,'clock_file':cf,'calculated_physical':buffer_summary(raw,clock,snap.N),
            'pending_native':snap.pending,'interfaces':snap.channels,'environment_metadata_exact_string':env,
            'not_complete_operational_state':True,'no_ticks':True}
        ff=stem+'/TESTIGO_FISICO.json';write(out/ff,fw)
        final={r['id']:r for r in snap.receipts};new=[r for i,r in final.items()if i not in before]
        changed={str(i):{'before':before[i],'after':r}for i,r in final.items()if i in before and r!=before[i]}
        if changed or set(before)-set(final):raise ValueError('Inherited terminal receipts changed/disappeared')
        rfile=stem+'/RECIBOS_FULL_DELTA.json';write(out/rfile,{'parent_snapshot_sha256':PSHA,'final_snapshot_sha256':snap.encoded_sha256,
            'new_receipts':new,'old_receipts_unchanged':True,'parent_receipt_count':len(before),'final_receipt_count':len(final)})
        index['branches'].append({'sources':n,'life':closed['life'],'initial_tick':closed['initial_record']['physical']['tick'],
            'initial_imported_snapshot_sha256':initial.encoded_sha256,'initial_snapshot_local':str(initial.path),
            'initial_vs_shared_full_parent_offline_verification':initial_equivalence,
            'journal_export':jf,'journal_original_sha256':js,'journal_export_sha256':jz,'journal_source':str(folder/'SUPERVISION/TRAYECTORIA/EVENTOS.jsonl'),
            'physical_witness_file':ff,'receipt_delta_file':rfile,'wrapper_file':wr,
            'closed':{'wrapper_returncode':closed['wrapper_returncode'],'seal_error':closed['seal_error'],
                'protected_ACTIVO_unchanged':closed['protected_ACTIVO_unchanged'],'shared_sources_unchanged':closed['shared_sources_unchanged']},
            'pair_locator':None if closed.get('paired')is None else{
                'directory':closed['paired']['directory'],'manifest_sha256':closed['paired']['manifest_sha256'],
                'complete_native_snapshot_sha256':snap.encoded_sha256,
                'scope':'Complete local operational pair, not duplicated in this essential archive.'}})
    write(out/'INDICE.json',index)
    shutil.copy2(Path(__file__),out/Path(__file__).name)
    r=recalc(out);write(out/'RECALCULO.json',r)
    flat=[]
    for arm in r['branches']:
        for w in arm['works']:
            flat.append({'sources':arm['sources'],'life':arm['life'],'episode':w['episode'],'source_id':w['public']['source_id'],
                'tag':w['public']['tag'],'goal_tag':w['public']['goal_tag'],'query_tick':w['query_tick'],'RAW_selector':w['RAW_selector_sign'],
                'action':w['action'],'old_gain':w['recalculated_old_gain'],'RAW_numeric':w['RAW_numeric_sign'],
                'feedback':w['feedback']['category'],'source_locator':w['locator']})
    with(out/'OPORTUNIDADES.csv').open('x',encoding='utf8',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)
    write(out/'MANIFIESTO.json',{'self_hash_excluded':True,'members':[{'file':p.relative_to(out).as_posix(),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size}for p in sorted(out.rglob('*'))if p.is_file()]})
    return r


def main():
    a=argparse.ArgumentParser(description=__doc__);g=a.add_mutually_exclusive_group(required=True)
    g.add_argument('--export',type=Path);g.add_argument('--recalc',type=Path);a.add_argument('--output',type=Path);a=a.parse_args()
    r=export(a.export)if a.export else recalc(a.recalc)
    if a.output:write(a.output,r)
    print(json.dumps({'branches':[{'sources':x['sources'],'work':len(x['works']),'old_gain':x['old_gain'],'actions':x['actions'],
        'lexical':[(v['form'],v['RAW_sign'])for v in x['lexical']],'receipts':x['terminal_native_statuses'],'physical':x['physical']}for x in r['branches']],
        'checks':len(r['checks']),'issues':r['issues'],'new_Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
