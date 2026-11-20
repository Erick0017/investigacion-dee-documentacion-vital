"""Portable stdlib analysis of exact PI05 global frames, never Native.

Inventories and all global difference sites are external observations. A charge,
position, direction or overlapping difference is never a Native lineage label
or proof of a causal encounter. No report is produced before input data exist.
"""
from pathlib import Path
from array import array
import argparse,collections,contextlib,csv,gzip,hashlib,io,json,runpy,struct,sys

HERE=Path(__file__).resolve().parent;N=67;COUNT=N**3;SIZE=COUNT*8
CODEC=HERE/'observador_global_PI05_R01.py'
NOMINAL_NODES=[{'id': 'left.root', 'site': [62, 36, 1], 'join_tick_relative': 0, 'arity': 4}, {'id': 'left.root.0', 'site': [52, 48, 58], 'join_tick_relative': -12, 'arity': 4}, {'id': 'left.root.0.0', 'site': [48, 54, 54], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.0.1', 'site': [56, 54, 54], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.0.2', 'site': [48, 54, 62], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.0.3', 'site': [56, 54, 62], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.1', 'site': [5, 48, 58], 'join_tick_relative': -12, 'arity': 4}, {'id': 'left.root.1.0', 'site': [1, 54, 54], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.1.1', 'site': [9, 54, 54], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.1.2', 'site': [1, 54, 62], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.1.3', 'site': [9, 54, 62], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.2', 'site': [52, 48, 11], 'join_tick_relative': -12, 'arity': 4}, {'id': 'left.root.2.0', 'site': [48, 54, 7], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.2.1', 'site': [56, 54, 7], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.2.2', 'site': [48, 54, 15], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.2.3', 'site': [56, 54, 15], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.3', 'site': [5, 48, 11], 'join_tick_relative': -12, 'arity': 4}, {'id': 'left.root.3.0', 'site': [1, 54, 7], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.3.1', 'site': [9, 54, 7], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.3.2', 'site': [1, 54, 15], 'join_tick_relative': -18, 'arity': 4}, {'id': 'left.root.3.3', 'site': [9, 54, 15], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root', 'site': [29, 65, 35], 'join_tick_relative': 0, 'arity': 4}, {'id': 'right.root.0', 'site': [19, 53, 25], 'join_tick_relative': -12, 'arity': 4}, {'id': 'right.root.0.0', 'site': [15, 47, 21], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.0.1', 'site': [23, 47, 21], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.0.2', 'site': [15, 47, 29], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.0.3', 'site': [23, 47, 29], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.1', 'site': [39, 53, 25], 'join_tick_relative': -12, 'arity': 4}, {'id': 'right.root.1.0', 'site': [35, 47, 21], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.1.1', 'site': [43, 47, 21], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.1.2', 'site': [35, 47, 29], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.1.3', 'site': [43, 47, 29], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.2', 'site': [19, 53, 45], 'join_tick_relative': -12, 'arity': 4}, {'id': 'right.root.2.0', 'site': [15, 47, 41], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.2.1', 'site': [23, 47, 41], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.2.2', 'site': [15, 47, 49], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.2.3', 'site': [23, 47, 49], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.3', 'site': [39, 53, 45], 'join_tick_relative': -12, 'arity': 4}, {'id': 'right.root.3.0', 'site': [35, 47, 41], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.3.1', 'site': [43, 47, 41], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.3.2', 'site': [35, 47, 49], 'join_tick_relative': -18, 'arity': 4}, {'id': 'right.root.3.3', 'site': [43, 47, 49], 'join_tick_relative': -18, 'arity': 4}] # Exact static FI128 geometry; not observed lineage.
NOMINAL_SHARED={'C':[12,17,18],'S':[14,15,16],'E':[15,15,15],'A':[14,14,15],'B':[16,14,15],
    'reader_minus_z0':[13,17,15],'reader_minus_zminus':[13,17,13],
    'reader_zero_z0':[15,17,15],'reader_zero_zminus':[15,17,13],
    'reader_plus_z0':[17,17,15],'reader_plus_zminus':[17,17,13]}

def digest(value):return hashlib.sha256(value).hexdigest()
def file_digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for value in iter(lambda:f.read(1048576),b''):h.update(value)
    return h.hexdigest()
def info(path):
    # Stable leaf locator for portable recalculation; original absolute
    # provenance remains in the capture/primary, never used to open originals.
    path=Path(path);return {'file':path.name,'bytes':path.stat().st_size,'sha256':file_digest(path)}
def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def output_root(path):
    path=Path(path).absolute()
    if path.exists():raise FileExistsError('Analysis requires a new unused destination')
    for p in(path,*path.parents):
        if p.is_symlink()or(p.exists()and getattr(p.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked output directory')
    path.mkdir(parents=True);return path
def u64(data):
    if not isinstance(data,bytes)or len(data)!=SIZE:raise ValueError('Exact complete N67 uint64LE buffer required')
    a=array('Q');a.frombytes(data)
    if a.itemsize!=8:raise ValueError('Host uint64 width differs')
    if sys.byteorder!='little':a.byteswap()
    return a
def record(value):
    v=int(value);directions=[(v>>s)&15 for s in(48,52,56)]
    return {'raw':str(v),'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':(v>>60)&15,
      'direction':[d-16 if d&8 else d for d in directions]}
def site(index):return [index//4489,(index//67)%67,index%67]
def index(point):return(point[0]*67+point[1])*67+point[2]
def normalize(frame):
    raw=frame['raw_bytes'];clocks=frame['clocks_bytes'];row=frame['row'];cfg=frame['config'];tick=frame['tick']
    if cfg.get('N')!=67 or row['tick']!=tick or cfg.get('byte_order')!='little':raise ValueError('Expected fixed N67 coherent tick/codec')
    if digest(raw)!=row['RAW_sha256']or digest(clocks)!=row['clocks_sha256']:raise ValueError('Reconstructed RAW/clocks hashes differ')
    return {'tick':tick,'raw_bytes':raw,'clocks_bytes':clocks,'raw':u64(raw),'clocks':u64(clocks),'row':row,'config':cfg}
def frame_iterator(directory):
    module=runpy.run_path(str(CODEC),run_name='pure_PI05_global_frame_codec')
    previous=None
    for value in module['iter_frames'](directory):
        frame=normalize(value)
        if previous is not None and frame['tick']<=previous:raise ValueError('Frame ticks must be strictly increasing')
        previous=frame['tick'];yield frame
def nominal_points():
    rows=[(n['id'],n['site'],n['join_tick_relative'])for n in NOMINAL_NODES]
    rows.extend((name,p,None)for name,p in NOMINAL_SHARED.items())
    return rows
def at_json(value,pointer):
    if not pointer.startswith('/'):raise ValueError('Explicit JSON pointer required')
    for part in pointer[1:].split('/'):
        while isinstance(value,str):value=json.loads(value)
        part=part.replace('~1','/').replace('~0','~');value=value[int(part)]if isinstance(value,list)else value[part]
    return value
def event_evidence(primary,pointer):
    if primary is None:return None
    requests=at_json(read_json(primary),pointer)
    if not isinstance(requests,list):raise ValueError('Direct actual request list required; no recursive history scan')
    events=[];ids={}
    for req in requests:
        receipt=req['receipt'];identifier=int(req['id'])
        if identifier!=receipt['id']:raise ValueError('Receipt identifier differs')
        value={'channel':req.get('port',req.get('channel')),'tick':req.get('tick',req.get('requested_tick')),
            'payload':req['payload'],'site':req.get('site'),'direction':req.get('direction')}
        if not isinstance(value['channel'],str)or type(value['tick'])is not int:raise ValueError('Actual channel/tick missing')
        if identifier in ids:
            if ids[identifier]!=(value,receipt):raise ValueError('Conflicting aliases')
            continue
        ids[identifier]=(value,receipt);events.append({**value,'Native_id':identifier,'receipt':receipt})
    source_complete=lambda event:all(isinstance(event[k],list)and len(event[k])==3 and all(type(v)is int for v in event[k])for k in('site','direction'))
    return {'primary':info(primary),'pointer':pointer,'unique_requests':len(ids),'statuses':dict(collections.Counter(x['receipt']['status']for x in events)),
      'requests_with_explicit_physical_source':sum(source_complete(x)for x in events),'missing_physical_sources_not_invented':[{'Native_id':x['Native_id'],'channel':x['channel']}for x in events if not source_complete(x)],
      'events':sorted(events,key=lambda x:(x['tick'],x['channel']))}
@contextlib.contextmanager
def gz_text(path):
    # A streaming, deterministic gzip payload; never enters snapshot metadata.
    with Path(path).open('xb')as binary:
        with gzip.GzipFile(fileobj=binary,mode='wb',mtime=0,filename='')as compressed:
            with io.TextIOWrapper(compressed,encoding='utf-8',newline='')as text:yield text
def dump_json(path,value):
    with Path(path).open('x',encoding='utf-8')as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def manifest(root):
    files=[{'file':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':file_digest(p)}for p in sorted(root.iterdir())if p.is_file()and p.name!='MANIFIESTO_SHA256.json']
    dump_json(root/'MANIFIESTO_SHA256.json',{'schema':'DEE.PI05.global_analysis.member_manifest.v1','files':files,'self_hash_intentionally_excluded':True})
def inventory(directory,destination,primary=None,pointer='/result/result/rows/0/requests'):
    root=output_root(destination);summaries=[];previous_raw=None;previous_clock=None;first_cfg=None
    with gz_text(root/'RAW_NO_NULO_GLOBAL.jsonl.gz')as records,gz_text(root/'NODOS_NOMINALES.csv.gz')as cells:
        writer=csv.writer(cells);writer.writerow(['tick','role','x','y','z','raw','clock','state','s_reg','semantic','dx','dy','dz','nominal_join_relative_not_measured_arrival'])
        for f in frame_iterator(directory):
            raw=f['raw'];clocks=f['clocks'];first_cfg=first_cfg or f['config'];present=[];semantics=collections.Counter();directions=collections.Counter();active=inactive=charge=maximum=0
            for i,v in enumerate(raw):
                if not v:continue
                r=record(v);present.append({'index':i,'site':site(i),'clock':str(clocks[i]),**r});semantics[r['semantic']]+=1;directions[str(r['direction'])]+=1
                active+=r['state']>0;inactive+=r['state']==0;charge+=r['s_reg'];maximum=max(maximum,r['s_reg'])
            records.write(json.dumps({'tick':f['tick'],'RAW_sha256':f['row']['RAW_sha256'],'clocks_sha256':f['row']['clocks_sha256'],'nonzero_RAW_records':present},ensure_ascii=False,separators=(',',':'))+'\n')
            for role,p,relative in nominal_points():
                i=index(p);r=record(raw[i]);writer.writerow([f['tick'],role,*p,r['raw'],str(clocks[i]),r['state'],r['s_reg'],r['semantic'],*r['direction'],relative])
            changed_raw=None if previous_raw is None else sum(a!=b for a,b in zip(previous_raw,raw))
            changed_clocks=None if previous_clock is None else sum(a!=b for a,b in zip(previous_clock,clocks))
            summaries.append({'tick':f['tick'],'RAW_sha256':f['row']['RAW_sha256'],'clocks_sha256':f['row']['clocks_sha256'],'raw_nonzero':len(present),'active_state':active,'state0_raw_nonzero':inactive,'s_reg_sum_all_fields_not_energy':charge,'max_s_reg':maximum,'semantic_counts_present':dict(semantics),'direction_counts_present':dict(directions),'changed_RAW_sites_since_previous_frame':changed_raw,'changed_clocks_sites_since_previous_frame':changed_clocks,'all_clocks_min':str(min(clocks)),'all_clocks_max':str(max(clocks)),
              'fusion_branch_excluded_for_following_step_by_max_only':maximum<=19663,'following_step_dependency_radius_bound_if_excluded':1,'otherwise_conservative_raw_dependency_radius_bound':3})
            previous_raw=raw;previous_clock=clocks
    if not summaries:raise ValueError('No observed frames')
    result={'schema':'DEE.PI05.global_inventory.external_observer.R01','recalculation':'DETERMINISTIC_FROM_FROZEN_CAPTURE_NO_HOST_TIMESTAMP','capture':Path(directory).name,'capture_config':first_cfg,'capture_config_file':info(Path(directory)/'CAPTURA.json'),'frame_count':len(summaries),'first_tick':summaries[0]['tick'],'last_tick':summaries[-1]['tick'],'complete_N67_each_frame':True,'all_reconstructed_frame_hashes_verified':True,'frames':summaries,'actual_requests':event_evidence(primary,pointer),
      'scope':'All RAW!=0 records, including inactive nonzeroRAW, plus fixed nominal-node observations. No path/lineage is inferred by a matching value; no Native access or new capability is claimed.','new_Native_ticks':0,'actor_receives_inventory':False}
    dump_json(root/'RESUMEN_GLOBAL.json',result);manifest(root);return root/'RESUMEN_GLOBAL.json'
def compare_event_streams(a,b):
    if a is None or b is None:return {'actual_event_lists_available':False,'single_payload_intervention_verified':False,'differences':[]}
    ea=a['events'];eb=b['events'];different=[];structure=True
    if len(ea)!=len(eb):structure=False
    for x,y in zip(ea,eb):
        keys=('channel','tick','site','direction')
        if any(x[k]!=y[k]for k in keys):structure=False
        if any(x[k]!=y[k]for k in(*keys,'payload')):different.append({'a':{k:x[k]for k in(*keys,'payload')},'b':{k:y[k]for k in(*keys,'payload')}})
    only_payload=structure and len(different)==1 and all(different[0]['a'][k]==different[0]['b'][k]for k in('channel','tick','site','direction'))
    geometry_complete=a['requests_with_explicit_physical_source']==len(ea)and b['requests_with_explicit_physical_source']==len(eb)
    return {'actual_event_lists_available':True,'same_event_count':len(ea)==len(eb),'same_reported_sources_timing_directions':structure,'all_physical_sources_explicit_in_requests':geometry_complete,'same_sources_timing_directions_verified_from_requests':structure and geometry_complete,'single_payload_intervention_verified':only_payload,'interface_contract_identity_not_checked_by_event_list':True,'differences':different,'missing_physical_sources_a':a['missing_physical_sources_not_invented'],'missing_physical_sources_b':b['missing_physical_sources_not_invented'],'admission_status_counts_a':a['statuses'],'admission_status_counts_b':b['statuses'],'scope':'The direct event list proves reported timing/channel/payload changes. Missing source coordinates are never treated as verified geometry; complete prefix/interface contracts require their separate proof. Admission differences are outcomes to retain; they are not silently removed to match dose.'}
def onset_witness(directory_a,directory_b,root,onset,onset_indices):
    if onset is None:return {'observed_difference':False}
    if len(onset_indices)>1000:return {'observed_difference':True,'onset':onset,'onset_site_count':len(onset_indices),'expanded_local_witness':'Not expanded above1000onset sites; complete global differences remain in the main CSV and all original frames remain reconstructable.'}
    wanted={onset-1,onset,onset+1};a={f['tick']:f for f in frame_iterator(directory_a)if f['tick']in wanted};b={f['tick']:f for f in frame_iterator(directory_b)if f['tick']in wanted};available=sorted(set(a)&set(b))
    max_before=None
    if onset-1 in a and onset-1 in b:max_before=max(max((v>>32)&65535 for v in a[onset-1]['raw']),max((v>>32)&65535 for v in b[onset-1]['raw']))
    radius=1 if max_before is not None and max_before<=19663 else 3
    region=set()
    for i in onset_indices:
        p=site(i)
        for x in range(-radius,radius+1):
            for y in range(-radius,radius+1):
                for z in range(-radius,radius+1):region.add(index([(p[0]+x)%67,(p[1]+y)%67,(p[2]+z)%67]))
    with gz_text(root/'PRIMERA_DIFERENCIA_VECINDAD.csv.gz')as f:
        w=csv.writer(f);w.writerow(['tick','index','x','y','z','RAW_a','RAW_b','clock_a','clock_b','state_a','sreg_a','semantic_a','direction_a','state_b','sreg_b','semantic_b','direction_b'])
        for tick in available:
            for i in sorted(region):
                x=record(a[tick]['raw'][i]);y=record(b[tick]['raw'][i]);w.writerow([tick,i,*site(i),x['raw'],y['raw'],str(a[tick]['clocks'][i]),str(b[tick]['clocks'][i]),x['state'],x['s_reg'],x['semantic'],str(x['direction']),y['state'],y['s_reg'],y['semantic'],str(y['direction'])])
    return {'observed_difference':True,'onset':onset,'onset_site_count':len(onset_indices),'requested_ticks':sorted(wanted),'available_ticks':available,'missing_ticks':sorted(wanted-set(available)),'global_max_sreg_previous_boundary':max_before,'conservative_causal_neighbourhood_radius':radius,'toroidal_region_sites':len(region),'scope':'This is the first observed difference, not automatically the first failing encounter or a lineage. Full global differences are exported separately; local enlargement is derived from the frozen kernel bound.'}
def compare(directory_a,directory_b,destination,primary_a=None,primary_b=None,pointer='/result/result/rows/0/requests',prefix_proof=None):
    root=output_root(destination);it_a=iter(frame_iterator(directory_a));it_b=iter(frame_iterator(directory_b));summaries=[];initial=None;first_difference=None;first_indices=[];last_difference=None;cfg={};sentinel=object()
    with gz_text(root/'DIFERENCIAS_GLOBALES_COMPLETAS.csv.gz')as differences:
        writer=csv.writer(differences);writer.writerow(['tick','index','x','y','z','RAW_a','RAW_b','RAW_xor','clock_a','clock_b','clock_xor','state_a','sreg_a','semantic_a','direction_a','state_b','sreg_b','semantic_b','direction_b'])
        while True:
            a=next(it_a,sentinel);b=next(it_b,sentinel)
            if a is sentinel and b is sentinel:break
            if a is sentinel or b is sentinel:raise ValueError('Different capture lengths; no time-alignment by selecting favourable frames')
            if a['tick']!=b['tick']:raise ValueError('Exact absolute Native tick matching required')
            if initial is None:initial={'tick':a['tick'],'RAW_bytes_exact':a['raw_bytes']==b['raw_bytes'],'clocks_bytes_exact':a['clocks_bytes']==b['clocks_bytes']};cfg={'a':a['config'],'b':b['config']}
            raw_indices=[];clock_indices=[];union=[];ha=hashlib.sha256();hc=hashlib.sha256()
            for i,(ra,rb,ca,cb)in enumerate(zip(a['raw'],b['raw'],a['clocks'],b['clocks'])):
                if ra!=rb:raw_indices.append(i);ha.update(struct.pack('<I',i))
                if ca!=cb:clock_indices.append(i);hc.update(struct.pack('<I',i))
                if ra!=rb or ca!=cb:
                    union.append(i);x=record(ra);y=record(rb);writer.writerow([a['tick'],i,*site(i),str(ra),str(rb),str(ra^rb),str(ca),str(cb),str(ca^cb),x['state'],x['s_reg'],x['semantic'],str(x['direction']),y['state'],y['s_reg'],y['semantic'],str(y['direction'])])
            if union:
                if first_difference is None:first_difference=a['tick'];first_indices=union
                last_difference=a['tick']
            nominal=[]
            for role,p,_ in nominal_points():
                i=index(p)
                if a['raw'][i]!=b['raw'][i]or a['clocks'][i]!=b['clocks'][i]:nominal.append({'role':role,'site':p,'a':record(a['raw'][i]),'b':record(b['raw'][i]),'clock_a':str(a['clocks'][i]),'clock_b':str(b['clocks'][i])})
            summaries.append({'tick':a['tick'],'RAW_difference_sites':len(raw_indices),'clocks_difference_sites':len(clock_indices),'union_difference_sites':len(union),'RAW_difference_index_uint32LE_sha256':ha.hexdigest(),'clocks_difference_index_uint32LE_sha256':hc.hexdigest(),'nominal_node_differences':nominal,'RAW_a_sha256':a['row']['RAW_sha256'],'RAW_b_sha256':b['row']['RAW_sha256'],'clocks_a_sha256':a['row']['clocks_sha256'],'clocks_b_sha256':b['row']['clocks_sha256']})
    if initial is None:raise ValueError('No matching observed frames')
    events=compare_event_streams(event_evidence(primary_a,pointer),event_evidence(primary_b,pointer));same_physics=initial['RAW_bytes_exact']and initial['clocks_bytes_exact']
    witness=onset_witness(directory_a,directory_b,root,first_difference,first_indices)
    result={'schema':'DEE.PI05.global_difference.external_influence_observer.R01','recalculation':'DETERMINISTIC_FROM_FROZEN_CAPTURES_NO_HOST_TIMESTAMP','capture_a':Path(directory_a).name,'capture_b':Path(directory_b).name,'capture_configs':cfg,'initial_physical_comparison':initial,'actual_event_comparison':events,'complete_prefix_proof_descriptor':None if prefix_proof is None else info(prefix_proof),'frame_count':len(summaries),'first_observed_difference_tick':first_difference,'last_observed_difference_tick':last_difference,'first_difference_is_already_initial_history_difference':first_difference==initial['tick'],'first_difference_window':witness,'frames':summaries,'all_global_difference_sites_exported':True,
      'interpretation':{'same_initial_RAW_clocks_and_single_payload_change':same_physics and events['single_payload_intervention_verified'],'complete_operational_prefix_identity_not_inferred_from_two_buffers':True,'causal_encounter_automatically_certified':False,'Native_lineage_labels_assigned':False,'functional_recovery_certified':False,'all_RAW_clocks_convergence_means_only_buffer_convergence':True,
        'scope':'D(T) is the complete observed RAW/clocks difference support at matched ticks. Initial history differences preclude attributing all D to the current input. A controlled payload contrast also needs comparable complete prefixes/interfaces/agenda and a causal intervention to identify a specific encounter. Value/direction/position coincidence never establishes lineage.'},'new_Native_ticks':0,'actor_receives_differences':False}
    dump_json(root/'RESUMEN_INFLUENCIA.json',result);manifest(root);return root/'RESUMEN_INFLUENCIA.json'
def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='mode',required=True)
    inv=sub.add_parser('inventario');inv.add_argument('--captura',required=True,type=Path);inv.add_argument('--destino',required=True,type=Path);inv.add_argument('--primario',type=Path)
    cmp=sub.add_parser('comparar');cmp.add_argument('--captura-a',required=True,type=Path);cmp.add_argument('--captura-b',required=True,type=Path);cmp.add_argument('--destino',required=True,type=Path);cmp.add_argument('--primario-a',type=Path);cmp.add_argument('--primario-b',type=Path);cmp.add_argument('--prueba-prefijo',type=Path)
    for parser in(inv,cmp):parser.add_argument('--ruta-recibos',default='/result/result/rows/0/requests',help='Explicit direct-list JSON pointer, transparently parsing serialized transport result; never recursive history scan')
    a=ap.parse_args()
    result=inventory(a.captura,a.destino,a.primario,a.ruta_recibos)if a.mode=='inventario'else compare(a.captura_a,a.captura_b,a.destino,a.primario_a,a.primario_b,a.ruta_recibos,a.prueba_prefijo)
    print(json.dumps({'result_path':str(result.resolve()),'result':info(result),'Native_ticks':0,'observer_only':True},ensure_ascii=False))
if __name__=='__main__':main()
