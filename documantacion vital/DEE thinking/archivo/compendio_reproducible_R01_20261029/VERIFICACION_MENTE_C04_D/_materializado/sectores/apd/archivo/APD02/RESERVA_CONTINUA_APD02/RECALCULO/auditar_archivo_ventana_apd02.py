"""Reusable archived FIFO/RAW scanner, with fixed readers and deduplicated receipts."""
import collections,hashlib,importlib.util,json
from pathlib import Path
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
u=load('pure_archive_raw_util',Path(__file__).with_name('recalcular_cadena_main_apd02.py'))
r4=load('pure_fixed_route04_util',Path(__file__).with_name('recalcular_ruta04_main_apd02.py'))
def scan(root,origin):
    x=u.read(root/'REGISTROS_VENTANA.json.gz');proto=u.read(root/'PROTOCOLO.json');logs=[json.loads(v)for v in(root/'ADMISIONES.jsonl').read_text(encoding='utf8').splitlines()if v];issues=[];checks=0;raw_count=0;seen={};receipts={};statuses=collections.defaultdict(set);readers=[];numbers=[];parsed={};unparsed=[]
    def check(name,ok):
        nonlocal checks
        checks+=1
        if not ok:issues.append(name)
    terminal=lambda v:v not in('scheduled','pending')
    transports={k:v for k,v in x['records'].items()if not k.endswith('_parsed')}
    for identifier,t in transports.items():
        check(identifier+':transport_ID',t['id']==identifier);check(identifier+':payload_SHA',hashlib.sha256(t['payload'].encode()).hexdigest()==t['payload_sha'])
        if not t.get('result'):unparsed.append({'id':identifier,'status':t['status']});continue
        body=json.loads(t['result']);parsed[identifier]=body;check(identifier+':result_ID',body['id']==identifier)
        if identifier+'_parsed'in x['records']:check(identifier+':result_mirror',body==x['records'][identifier+'_parsed'])
        guard=body.get('result',{}).get('INSTRUMENTO_FENCE')
        if guard:check(identifier+':truthful_guard_scope',not guard['denied']and guard.get('operational_history_reads_universally_blocked')is False)
        for path,node in u.walk(body):
            if not isinstance(node,dict):continue
            label=identifier+path
            if'raw'in node and'site'in node and'tick'in node:
                raw_count+=1;d=u.decoded(node)
                for k,v in d.items():
                    if k in node:check(label+':'+k,node[k]==v)
                key=(tuple(node['site']),int(node['tick']));stamp=(str(node['raw']),str(node.get('clock')))
                if key in seen:check(label+':consistent_site_tick',seen[key]==stamp)
                else:seen[key]=stamp
            if isinstance(node.get('receipt'),dict)and'id'in node['receipt']:
                rc=node['receipt'];rid=str(rc['id']);entry={k:rc.get(k)for k in('id','kind','channels','requested_tick','status','effective_tick','reason')};statuses[rid].add(rc['status'])
                if rid in receipts:
                    old=receipts[rid];check(label+':same_receipt_identity',all(old[k]==entry[k]for k in('id','kind','channels','requested_tick')))
                    if terminal(old['status'])and terminal(entry['status']):check(label+':same_terminal_receipt',old==entry)
                    elif terminal(entry['status']):receipts[rid]=entry
                else:receipts[rid]=entry
            if'formed_native_command'in node and'panel'in node:
                codec={f:(u.I,v)for f,v in u.CONTEXTS.items()}if len(node['panel'])==12 else u.FORM_CODEC;answer,cs=u.pure_z(node,codec);check(label+':fixed_pureZ_reader',answer==node['formed_native_command']and cs==node['candidates']);readers.append({'id':identifier,'path':path,'gates':len(node['panel']),'choice':answer})
            if'choice'in node and'observations'in node:
                answer,cs=r4.choice3(node,origin)if len(node['observations'])==3 else u.selector(node,(15,15,15));check(label+':fixed_route_or_current_reader',answer==node['choice']and cs==[v.get('choice')if isinstance(v,dict)else v for v in node['candidates']]);readers.append({'id':identifier,'path':path,'gates':len(node['observations']),'choice':answer})
            if node.get('kind')=='APD01_candidate_numeric_operation':
                value=u.numeric(node);check(label+':numeric_C_RAW',value==node['numeric_reader']['numeric_result']);numbers.append({'id':identifier,'path':path,'operation':node['operation'],'value':value})
    check('unique_admission_IDs',len(logs)==len({l['id']for l in logs}))
    admitted={l['id']for l in logs if l['admission'].get('admission')=='queued'};check('every_archived_transport_was_admitted',set(transports)<=admitted)
    for l in logs:
        if l['id']in transports:check(l['id']+':unchanged_literal_payload',l['payload']==json.loads(transports[l['id']]['payload']))
    sequential=[l for l in logs if l['id']in transports]
    for a,b in zip(sequential,sequential[1:]):
        x1=transports[a['id']];x2=transports[b['id']]
        if x1.get('finished_utc')and x2.get('started_utc'):check(a['id']+':FIFO_terminal_before_next',x1['finished_utc']<=x2['started_utc'])
    return{'x':x,'proto':proto,'logs':logs,'transports':transports,'parsed':parsed,'issues':issues,'checks':checks,'RAW_serialized_observations':raw_count,'unique_observed_site_ticks':len(seen),'fixed_readers':readers,'native_numeric_readers':numbers,'native_inputs':{'unique_requested':len(receipts),'terminal_status_counts':dict(collections.Counter(r['status']for r in receipts.values())),'serialized_status_sets':dict(collections.Counter(','.join(sorted(v))for v in statuses.values())),'receipts':sorted(receipts.values(),key=lambda r:r['id'])},'transport_summary':{'requested':len(logs),'admitted':len(admitted),'status_counts':dict(collections.Counter(t['status']for t in transports.values())),'archived_parseable_result_count':len(parsed),'unparsed_or_incomplete_results':unparsed,'material_archived':sum(not t['is_control']for t in transports.values()),'controls_archived':sum(bool(t['is_control'])for t in transports.values())}}
