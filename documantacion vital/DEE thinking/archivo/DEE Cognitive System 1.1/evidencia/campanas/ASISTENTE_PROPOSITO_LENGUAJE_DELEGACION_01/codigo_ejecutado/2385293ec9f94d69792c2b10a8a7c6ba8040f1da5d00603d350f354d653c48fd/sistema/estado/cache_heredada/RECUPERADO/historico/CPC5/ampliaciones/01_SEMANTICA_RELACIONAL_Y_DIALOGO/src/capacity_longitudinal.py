"""Two-block native capacity curriculum; persistence stores phase, not answers."""
import argparse,json
from collections import Counter
from pathlib import Path
import sys,time
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from capacity import CapacitySession,memory,normalized_op
from common import sha,put,identity,record,receipt,digest,operational,until,local_context
ROOT=HERE.parent


def decode(w,f,identifier,payload):
    p=record(w,f['hub']);r=receipt(w,identifier)
    valid=r['status']=='applied' and p['active'] and p['semantic']==1 and p['s_reg']>payload and p['direction']in([-1,1,0],[-1,-1,0])
    return {'form':f['name'],'tick':int(w.runtime.current_tick),'input_payload':payload,'physical':p,'receipt':r,
            'decoder_valid':valid,'decoded_y':p['direction'][1] if valid else None,'origin':'ENTE'}


def run_case(case,out):
    out=Path(out)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);start=time.monotonic();engine=identity();s=CapacitySession.create(case);w=s.world;forms=s.spec['forms'];n=s.spec['N'];split=case['first_block']
    if not 1<=split<len(forms):raise ValueError('Two nonempty acquired blocks')
    signs=case.get('directions',[1 if i%3 else -1 for i in range(len(forms))])
    if len(signs)!=len(forms) or any(x not in(-1,1) for x in signs):raise ValueError('Physical environmental directions')
    # Port phase is merely protocol timing, never an acquired class lookup.
    s.state['port_phase_residues']={f['name']:0 if i<split else 8 for i,f in enumerate(forms)}
    snapshots=[];lessons=[];readouts=[];windows=[]
    def save(name):snapshots.append(s.save(out/(name+'.deetsnap')))
    def teach(subset,tick,block):
        until(w,tick);rows=[]
        for i,f in subset:
            sign=signs[i];ids=[s.submit(f['name'],'event.'+('plus' if sign==1 else 'minus'),11,tick),s.submit(f['name'],'signal',5,tick)]
            rows.append({'form':f['name'],'block':block,'experience_tick':tick,'physical_event_y':sign,'receipt_ids':ids})
        until(w,tick+3)
        for r in rows:
            f=next(f for f in forms if f['name']==r['form']);r['physical_after']=record(w,f['hub']);r['receipts']=[receipt(w,x) for x in r['receipt_ids']]
        lessons.extend(rows);save(f'ACQUIRED_BLOCK{block}_T{tick+3}')
    def query(subset,tick,block):
        until(w,tick);ids=[s.submit(f['name'],'signal',5,tick,True) for _,f in subset];until(w,tick+2)
        windows.append({'block':block,'tick':tick+2,'form':subset[0][1]['name'],'before':local_context(w,subset[0][1]['hub'])})
        until(w,tick+3)
        for (_,f),i in zip(subset,ids):readouts.append({'panel':block,'input_tick':tick,**decode(w,f,i,5)})
    put(out/'CONFIG.json',{'case':case,'engine':engine,'source_sha256':sha(__file__),'dependency_capacity_sha256':sha(HERE/'capacity.py'),
          'criterion_frozen':{'old_first_use_before_new':'query first block atN unless load-control cohort explicitly omits it',
            'new_exposure':'atN+8, no oldrelation re-teaching','retention':'same MAIN oldqueries2N,3N and newqueries2N+8,3N+8',
            'decoder':'Applied/active/semantic1/load>query/y direction read directly; no target access',
            'scope':'65 opaque acquired correspondences /2directional content classes; not65NSMmeanings'}})
    save('INITIAL_T0');old=list(enumerate(forms[:split]));new=list(enumerate(forms[split:],split))
    teach(old,0,1)
    if not case.get('omit_early_query',False):query(old,n,'OLD_BEFORE_NEW')
    else:until(w,n+3)
    save('BEFORE_NEW_BLOCK_T'+str(w.runtime.current_tick));teach(new,n+8,2)
    for cycle in(2,3):query(old,n*cycle,f'OLD_AFTER_NEW_{cycle}');query(new,n*cycle+8,f'NEW_{cycle}')
    save('FINAL_T'+str(w.runtime.current_tick));final=digest(w);loaded=CapacitySession.load(out/snapshots[-1]['file'])
    technical={'save_load_physical_equal':digest(loaded.world)==final,'save_load_operative_equal':normalized_op(loaded.world)==normalized_op(w)}
    learned={r['form']:r['physical_after']['direction'][1] for r in lessons if r['physical_after']['active']};metrics={}
    for panel in dict.fromkeys(x['panel'] for x in readouts):
        rs=[x for x in readouts if x['panel']==panel]
        metrics[panel]={'queries':len(rs),'applied':sum(x['receipt']['status']=='applied' for x in rs),
             'valid':sum(x['decoder_valid'] for x in rs),'matches_acquired':sum(x['decoder_valid'] and x['decoded_y']==learned.get(x['form']) for x in rs),
             'rejected':sum(x['receipt']['status']=='rejected' for x in rs)}
    result={'case':case,'status':'MEASURED','source_sha256':sha(__file__),'dependency_capacity_sha256':sha(HERE/'capacity.py'),
            'engine':engine,'geometry':s.spec,'preparations':1,'forks':0,'same_RUNTIME':True,'calls':s.state['calls'],
            'receipts':[receipt(w,c['id']) for c in s.state['calls']],'lessons':lessons,'readouts':readouts,'local_windows':windows,
            'calculations':metrics,'checkpoints':snapshots,'final':final,'operative_final':operational(w),'technical':technical,
            'direct_RAW_writes_after_T0':0,'direct_clock_writes_after_T0':0,'resources':{'basic_buffers_bytes':32*n**3,**memory()},
            'elapsed_seconds':time.monotonic()-start,'scope':'First block acquired and optionally used before second, retained without re-teaching. K forms are not K distinct NSM meanings.'}
    put(out/'MEASUREMENTS.json',result);assert all(technical.values());print(json.dumps({'id':case['id'],'metrics':metrics,'seconds':result['elapsed_seconds']}),flush=True);return result


def continuation(snapshot,out,payload=9):
    identity();out=Path(out)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);s=CapacitySession.load(snapshot);w=s.world;before=digest(w);before_op=operational(w);n=s.spec['N'];forms=s.spec['forms'];phases=s.state.get('port_phase_residues')
    if phases is None:raise ValueError('Longitudinal phase protocol required')
    base=(int(w.runtime.current_tick)//n+1)*n;rs=[]
    for phase in sorted(set(phases.values())):
        until(w,base+phase);subset=[f for f in forms if phases[f['name']]==phase];ids=[s.submit(f['name'],'signal',payload,base+phase,True) for f in subset];until(w,base+phase+3)
        rs.extend([decode(w,f,i,payload) for f,i in zip(subset,ids)])
    cp=s.save(out/'CONTINUED.deetsnap');result={'status':'MEASURED','source_sha256':sha(__file__),'parent_sha256':sha(snapshot),
        'parent':str(snapshot),'before':before,'before_operative':before_op,'readouts':rs,'after':digest(w),'checkpoint':cp,
        'scope':'Other-process continuation after quiet interval, novel querypayload. Only physical/operative snapshot; no teachingfiles or targetmap loaded.'}
    put(out/'CONTINUATION.json',result);print(json.dumps({'queries':len(rs),'applied':sum(r['receipt']['status']=='applied' for r in rs),'valid':sum(r['decoder_valid'] for r in rs),'tick':result['after']['tick']}),flush=True)


def summarize():
    """External post-trajectory recalculation, never consulted by a participant."""
    rows=[]
    for pattern in('capacity_discovery/*/MEASUREMENTS.json','capacity_confirmation/*/MEASUREMENTS.json','capacity_longitudinal/*/MEASUREMENTS.json'):
        for path in sorted((ROOT/'resultados').glob(pattern)):
            m=json.loads(path.read_text(encoding='utf-8'));panels={}
            for r in m['readouts']:
                key=str(r.get('panel',r.get('round')));p=panels.setdefault(key,{'queries':0,'receipt_status_counts':Counter(),'decoder_valid':0,'observed_y_counts':Counter()})
                p['queries']+=1;p['receipt_status_counts'][r['receipt']['status']]+=1;p['decoder_valid']+=bool(r['decoder_valid']);p['observed_y_counts'][str(r['decoded_y'])]+=1
            rows.append({'case_id':m['case']['id'],'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'N':m['geometry']['N'],'forms':m['geometry']['K'],
                         'physical_content_classes':2,'same_RUNTIME':m['same_RUNTIME'],'source_sha256':m['source_sha256'],'panels':panels,'scope':m['scope']})
    put(ROOT/'resultados/capacity_RECALCULATION.json',{'schema':'CPC5.extension.capacity.recalculation.v1','source_sha256':sha(__file__),
        'cases':rows,'calculation_correction':'v2capacity calculations.rejected tested exact string rejected; native receipt statuses are rejected_occupied etc. Use receipt_status_counts here, not that incomplete aggregation. Primary receipts retained unmodified.',
        'counting_scope':'K entries are opaque forms representing2directional content classes, never K NSM meanings; repeatedqueries are not independent worlds.'})
    arch=[];byid={}
    for pattern in('architectures_screen/*/MEASUREMENTS.json','architectures_confirmation/*/MEASUREMENTS.json'):
        for path in sorted((ROOT/'resultados').glob(pattern)):
            m=json.loads(path.read_text(encoding='utf-8'));byid[m['case']['id']]=m
            arch.append({'case_id':m['case']['id'],'file':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'groups':m['geometry']['groups'],
                 'components':12,'resources':m['resources'],'rounds':m['calculations'],'receipt_status_counts':dict(Counter(r['status']for r in m['receipts'])),
                 'contact':m.get('consequence_at_contact'),'final':m['final'],'interventions':m['interventions']})
    base=byid.get('ARCH_D_A3_THREE_CLUSTERS');reverse=byid.get('ARCH_C_A3_REVERSE_RELATION_ORDER');collapse=None
    if base and reverse:
        collapse={'base_case':base['case']['id'],'permuted_case':reverse['case']['id'],'same_initial_inventory':True,'same_final_physical_state':base['final']==reverse['final'],
          'base_final':base['final'],'permuted_final':reverse['final'],'base_intermediate_stage3':base['readouts'][3],'permuted_intermediate_stage3':reverse['readouts'][3],
          'scope':'If fullRAW/clocks/tick converge, order of these load-contributions is inaccessible in that final physical state. Early intermediate/readout differences remain recorded only by the auditor; no general bound on v27 relation representation.'}
    put(ROOT/'resultados/architectures_RECALCULATION.json',{'schema':'CPC5.extension.architectures.recalculation.v1','source_sha256':sha(__file__),
        'cases':arch,'order_collapse_contrast':collapse,'interpretation_domain':'Matched finite native memory-transformation chains with actual cluster gaps; does not establish renewable autonomous compound bodies or semantic-role preservation.'})
    print(json.dumps({'capacity_cases':len(rows),'architecture_cases':len(arch),'order_collapse':None if collapse is None else collapse['same_final_physical_state']}),flush=True)


def architecture_continuation(snapshot,out):
    """Continue actual pending physical events; expected outputs are not read."""
    import dee_thinking as d
    identity();out=Path(out)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);w=d.OrganizationalWorld.load_snapshot(str(snapshot));key='cpc5.extension.architectures.v1';state=json.loads(w.runtime.snapshot_metadata(key))
    before=digest(w);op=operational(w)
    if state['schema']!=1 or state['tick']!=w.runtime.current_tick:raise ValueError('Foreign or stale operative snapshot')
    final_tick=max(x['requested_tick']for x in state['calls'])+6
    if not before['tick']<=final_tick<=512:raise ValueError('Finite prepared horizon0..512')
    until(w,final_tick);state['tick']=int(w.runtime.current_tick);w.runtime.set_snapshot_metadata(key,json.dumps(state,separators=(',',':')))
    after=digest(w);path=out/'CONTINUED.deetsnap';w.save_snapshot(str(path))
    result={'status':'MEASURED','modality':'TECHNICAL_CONTINUATION_IN_OTHER_PROCESS','source_sha256':sha(__file__),
      'parent':str(snapshot),'parent_sha256':sha(snapshot),'before':before,'before_operative':op,'after':after,
      'operative_after':operational(w),'checkpoint':{'file':path.name,'sha256':sha(path)},
      'scope':'No expected terminal data or teachingmap loaded; original pending queue evolves to declared finite environment horizon. Physical equivalence checked externally after execution.'}
    put(out/'CONTINUATION.json',result);print(json.dumps({'before':before['tick'],'after':after['tick']}),flush=True)


def architecture_query(case,out):
    """Same new request after the contact; no previous response table is read."""
    import dee_thinking as d
    identity();out=Path(out)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);snapshot=ROOT/case['snapshot'];w=d.OrganizationalWorld.load_snapshot(str(snapshot));key='cpc5.extension.architectures.v1';state=json.loads(w.runtime.snapshot_metadata(key));spec=state['geometry'];n=spec['N']
    before=digest(w);before_op=operational(w);at=((int(w.runtime.current_tick)-6)//n+1)*n+6;cycle=(at-6)//n;query=case.get('query',9)
    r=w.submit('request',query,at);call={'id':int(r.id),'port':'request','payload':query,'requested_tick':at,'call_tick':int(w.runtime.current_tick),'origin':'COMMON_NEW_QUERY_AFTER_CONSEQUENCE','modality':'EXPERIENCE_PROTOCOL'};state['calls'].append(call)
    stages=spec['stages'];last=stages[-1]['meeting_tick']+cycle*n;end=last+6
    boundaries={at,last-1,last,last+2,last+3,end};windows=[]
    for tick in sorted(boundaries):
        until(w,tick);site=stages[-1]['meeting'] if tick<=last else spec['consequence_site_round1']
        if tick==end:site=tuple((site[i]+(-1,1,0)[i]*3)%n for i in range(3))
        windows.append({'tick':tick,'site':site,'physical':record(w,site),'local_context':local_context(w,site)})
    state['tick']=int(w.runtime.current_tick);w.runtime.set_snapshot_metadata(key,json.dumps(state,separators=(',',':')));path=out/'CONTINUED.deetsnap';w.save_snapshot(str(path))
    result={'case':case,'status':'MEASURED','modality':'NEW_PHYSICAL_QUERY_ON_RESTORED_CONTINUATION','source_sha256':sha(__file__),
       'parent_sha256':sha(snapshot),'before':before,'before_operative':before_op,'input':call,'receipt':receipt(w,r.id),
       'windows':windows,'after':digest(w),'operative_after':operational(w),'checkpoint':{'file':path.name,'sha256':sha(path)},
       'scope':'Joint aggregate is queried after previous environmental contact. Spatial reader shift is an explicit second observable, not a repaired answer or semantic-role recovery.'}
    put(out/'CONTINUATION.json',result);print(json.dumps({'id':case['id'],'tick':end,'windows':[{ 'tick':x['tick'],'s_reg':x['physical']['s_reg'],'direction':x['physical']['direction'],'active':x['physical']['active']} for x in windows]}),flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['worker','screen','continue','architecture-continue','architecture-query-screen','summarize']);p.add_argument('--case',type=Path);p.add_argument('--config',type=Path);p.add_argument('--snapshot',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
    if a.command=='summarize':summarize()
    elif a.command=='architecture-continue':architecture_continuation(a.snapshot,a.out)
    elif a.command=='architecture-query-screen':
        cfg=json.loads(a.config.read_text(encoding='utf-8'));a.out.mkdir(parents=True,exist_ok=True);rows=[]
        for c in cfg['cases']:
            m=architecture_query(c,a.out/c['id']);rows.append({'id':c['id'],'after':m['after'],'file':str((a.out/c['id']/'CONTINUATION.json').relative_to(ROOT))})
            put(a.out/'INDEX.json',{'configuration':cfg,'cases':rows,'same_final_physical_state':len(rows)==2 and rows[0]['after']==rows[1]['after']})
    elif a.command=='continue':continuation(a.snapshot,a.out)
    elif a.command=='worker':run_case(json.loads(a.case.read_text(encoding='utf-8')),a.out)
    else:
        cfg=json.loads(a.config.read_text(encoding='utf-8'));a.out.mkdir(parents=True,exist_ok=True);rows=[]
        for c in cfg['cases']:
            target=a.out/c['id'];m=json.loads((target/'MEASUREMENTS.json').read_text(encoding='utf-8')) if(target/'MEASUREMENTS.json').exists()else run_case(c,target)
            rows.append({'id':c['id'],'calculations':m['calculations'],'file':str((target/'MEASUREMENTS.json').relative_to(ROOT)),'sha256':sha(target/'MEASUREMENTS.json')});put(a.out/'INDEX.json',{'configuration':cfg,'cases':rows})
