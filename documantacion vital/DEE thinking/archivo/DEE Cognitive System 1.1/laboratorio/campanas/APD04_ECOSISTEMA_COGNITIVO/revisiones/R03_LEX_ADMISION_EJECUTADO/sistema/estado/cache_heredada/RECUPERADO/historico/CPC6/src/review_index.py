"""Explicit CPC6 primary-evidence registry and auditor-only compact views.

Never imported by participants. No recursive all-JSON experiment discovery:
only named campaign indices, named aggregates and explicit extra-index arguments.
Reproductions, continuations, diagnostic forks and preparations remain separate.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha

REGISTRY=(
 ('D01','D01_INTEGRATED_DISCOVERY','PREPARATION'),('D02','D02_LANGUAGE_DISCOVERY','PREPARATION'),
 ('D03','D03_NATIVE_CONSOLIDATION','PREPARATION'),('D04','D04_OPEN_LANDING','PREPARATION'),
 ('D05','D05_LONGITUDINAL','PREPARATION'),('D06','D06_BILATERAL','PREPARATION'),('D07','D07_TWO_FORMS','PREPARATION'),
 ('R01','R01_RESERVED_INTEGRATION','PREPARATION'),('R02','R02_CROSS_AND_REUSE','PREPARATION'),
 ('B01BUS','B01_WORD_BUS','PREPARATION'),('R03','R03_WORD_BUS_V2','PREPARATION'),
 ('AF_DISC','action_feedback_component_discovery','COMPONENT_PREPARATION'),
 ('AF_CTRL','action_feedback_component_controls_reserved','COMPONENT_PREPARATION'),
 ('IC01','INTEGRATION_CONTROLS_01','CASE_DEPENDENT'),
 ('CC01','CONSOLIDATION_CONTROLS_01','DIAGNOSTIC_FORK'),
 ('WBCTRL','WORD_BUS_CONTROLS_01','DIAGNOSTIC_FORK'),
 ('LA01','LATE_ACCESS_01','CONTROLLED_CONTINUATION'),
 ('RET_D01','RETENTION_D01','PREPARATION'),('RET_D02','RETENTION_D02_ALTERNATE_ACCESS','PREPARATION'),
 ('RET_C01','RETENTION_C01_CAUSAL','DIAGNOSTIC_FORK'),('RET_C02','RETENTION_C02_FIELD','DIAGNOSTIC_FORK'),
 ('AS01','ARCHITECTURE_SCREEN_01','PREPARATION'),('AB01','ARCHITECTURE_BRIDGE_01','PREPARATION'),
 ('BD02','ARCHITECTURE_BRIDGE_DELAYED_02','PREPARATION'),('BD04','ARCHITECTURE_BRIDGE_DELAYED_04','PREPARATION'),
 ('BC05','ARCHITECTURE_BRIDGE_CONFIRM_05','PREPARATION'))

KNOWN_SCHEMAS={'CPC6.U0.life.v1','CPC6.action_feedback.component.v1','CPC6.U0.diagnostic.v1',
 'CPC6.consolidation.causal_control.v1','CPC6.late_access.continuation.v1','CPC6.retention.case.v1',
 'CPC6.retention.alternate_access.v1','CPC6.retention.causal.v1','CPC6.retention.field_localization.v1',
 'CPC6.architecture_screen.case.v1','CPC6.architecture_bridge.case.v1','CPC6.architecture_bridge_delayed.case.v1',
 'CPC6.word_bus.causal_control.v1'}
CRITICAL={0,5,15,19,20,23,30,33,53,65,69,70,75,79,80,83,88,89,90,93,94,97,100,105,110,116,117,120,136,160,161,162,164,170}


def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def relative(p):return str(Path(p).relative_to(ROOT)).replace('\\','/')
def rows(m):return m.get('rows',[])
def end_tick(m):return m.get('final_physical',{}).get('tick',max((int(r.get('tick',0)) for r in rows(m)),default=None))
def start_tick(m):
    value=min((int(r.get('tick',0)) for r in rows(m)),default=None)
    if value is not None:return value
    for key in ('pre_MAIN','MAIN_before','MAIN_physical_before','pre_parent','physical_before'):
        if isinstance(m.get(key),dict) and m[key].get('tick') is not None:return m[key]['tick']
    if m.get('query_receipt',{}).get('requested_tick') is not None:return m['query_receipt']['requested_tick']
    return None


def physical_records(value,path=''):
    if isinstance(value,dict):
        if {'raw','clock','site','state','s_reg','direction'}<=value.keys():
            # Exact uint64 values, never cast to float.
            r={k:value.get(k) for k in ('tick','site','raw','clock','state','s_reg','semantic','direction','active')}
            r['raw']=str(r['raw']);r['clock']=str(r['clock']);r['tick']=str(r['tick']) if r['tick'] is not None else None
            yield path,r
        else:
            for k,v in value.items():yield from physical_records(v,path+'/'+str(k))
    elif isinstance(value,list):
        for i,v in enumerate(value):yield from physical_records(v,path+'/'+str(i))


def normalize_requests(m):
    result=[]
    for q in m.get('requests',m.get('calls',m.get('all_parent_requests',[]))):
        r=q.get('receipt',{})
        if not r:continue
        result.append({'port':q.get('port'), 'payload':q.get('payload'),'requested_tick':str(q.get('tick',r.get('requested_tick'))),
            'call_tick':str(q['call_tick']) if 'call_tick' in q else None,'kind':q.get('kind',r.get('kind')),
            'status':r.get('status'),'effective_tick':str(r['effective_tick']) if r.get('effective_tick') is not None else None,'reason':r.get('reason','')})
    return result


def compact_observations(m,case_key,primary):
    # Prefer direct recorded trajectories/panels. Local-window duplication stays
    # in the primary artifact and is not expanded into another pseudo-sample.
    source={'rows':m['rows']} if 'rows' in m else {k:m[k] for k in ('post_query_panel','panel','reader','response97','intervention','before_old_query','retention_emission') if k in m}
    bucket=defaultdict(list)
    for path,r in physical_records(source):
        if r['tick'] is not None:bucket[int(r['tick'])].append((path,r))
    ticks=sorted(bucket)
    requested_frontiers=set(m.get('case',{}).get('checkpoints',[]))
    selected=set(ticks) if len(ticks)<=12 else (set(ticks)&(CRITICAL|requested_frontiers))|{ticks[0],ticks[-1]}
    def rank(item):
        path,r=item;importance=0 if any(t in path for t in ('emission','reader','queries','response')) else 1 if 'information' in path else 2 if any(t in path for t in ('comparison','policies','actions')) else 3
        return (not bool(r['active']),importance,path)
    result=[]
    for tick in sorted(selected):
        unique={}
        for path,r in sorted(bucket[tick],key=rank):
            key=(tuple(r['site']),r['raw'],r['clock'])
            if key not in unique:unique[key]={'source_path':path,'physical':r,'aliases':[]}
            unique[key]['aliases'].append(path)
        mandatory=[x for x in unique.values() if any(('/word_bus/' in p and p.endswith('/target')) or '/targets/' in p for p in x['aliases'])]
        chosen=mandatory[:4]+[x for x in unique.values() if x not in mandatory][:max(0,6-len(mandatory[:4]))]
        result.append({'case_key':case_key,'primary':primary,'kind':'SELECTED_EXACT_PHYSICAL_FRAME','tick':str(tick),
            'physical_records_in_recorded_frame':len(unique),'selected_count':len(chosen),'records':chosen,
            'coverage':'At most6 exact records perselectedtick; fullfixedcandidates andlocalwindows remaininprimary. Selectionis auditdisplay,notanentityobserver.'})
    return result


def primary_entry(family,path,kind,item=None,subcase=None):
    m=read(path);case=m.get('case') or {};cid=case.get('id',Path(path).parent.name)
    if kind=='CASE_DEPENDENT':kind='DIAGNOSTIC_FORK' if case.get('mode')=='diagnostic' else 'PREPARATION'
    if m.get('schema') not in KNOWN_SCHEMAS:raise ValueError('Unregistered primary schema '+str((path,m.get('schema'))))
    prep=int(kind in ('PREPARATION','COMPONENT_PREPARATION'));fork=int(kind=='DIAGNOSTIC_FORK');continuation=int(kind=='CONTROLLED_CONTINUATION' or fork)
    parent=m.get('parent') or m.get('parent_case') or m.get('base') or case.get('parent_case') or case.get('parent')
    config_path=Path(path).with_name('CONFIG.json');config=read(config_path) if config_path.exists() else {}
    snapshots=[]
    candidates=list(m.get('snapshots',[]))+[m[k] for k in ('snapshot_before','snapshot_after') if isinstance(m.get(k),dict)]
    for s in candidates:
        name=s.get('file',s.get('path',''))
        if name:
            member=Path(path).parent/Path(name).name
            snapshots.append({'path':relative(member),'sha256_recorded':s.get('sha256'),'tick':s.get('physical',{}).get('tick')})
    entry={'case_key':family+'/'+cid,'family':family,'case_id':cid,'schema':m.get('schema'),'primary':relative(path),'sha256':sha(path),
       'record_kind':kind,'case_fields':case,'parent':parent,'parent_snapshot':m.get('parent_snapshot',m.get('base_snapshot',m.get('parent_checkpoint'))),
       'tick_start':start_tick(m),'tick_end':end_tick(m),'preparations':prep,'component_preparations':int(kind=='COMPONENT_PREPARATION'),
       'diagnostic_forks':fork,'controlled_continuations':int(kind=='CONTROLLED_CONTINUATION'),'all_continuation_runs':continuation,
       'owner_runtimes':m.get('owner_runtimes',1),'candidate_bodies':m.get('individual_candidates',2 if family.startswith(('AB','BD','BC')) else 1),
       'status':m.get('status','MEASURED'),'elapsed_seconds':m.get('elapsed_seconds'),
       'receipt_counts':dict(Counter(q['status'] for q in normalize_requests(m))),
       'source_sha256':m.get('source_sha256',config.get('source_sha256')),'configuration_sha256':m.get('configuration_sha256',m.get('config_sha256')),
       'configuration_file':relative(config_path) if config_path.exists() else None,'configuration_file_sha256':sha(config_path) if config_path.exists() else None,
       'checkpoints':snapshots}
    return entry,m


def retention_row(entry,m):
    panel=[]
    for row in rows(m):
        t=int(row.get('tick',0))
        if t not in CRITICAL and t!=end_tick(m):continue
        body=row.get('body',{});second=row.get('consolidation',{})
        if body or second:panel.append({'tick':t,'R1_delta':body.get('delta'),'R2_delta':second.get('delta'),
          'R2_left_delta':second.get('left',{}).get('delta'),'R1_emission':body.get('emission'),
          'R2_emission':second.get('emission'),'renewed_observation':row.get('renewed'),
          'F1_emissions':row.get('decoded_language',[]),'F2_emissions':row.get('decoded_order_language',[]),
          'word_bus_fields':row.get('word_bus'),'word_bus_decoded':row.get('decoded_word_bus',[])})
    causal_panel=[]
    if m.get('schema')=='CPC6.word_bus.causal_control.v1':
        for row in rows(m):
            causal_panel.append({'tick':row['tick'],'R1_delta':row.get('R1',{}).get('delta'),
              'right_R2_delta':row.get('right_R2',{}).get('delta'),'left_R2_delta':row.get('left_R2',{}).get('delta'),
              'targets':row.get('targets'),'bus_approach':row.get('bus_approach')})
    return {'case_key':entry['case_key'],'primary':entry['primary'],'record_kind':entry['record_kind'],
      'query_requests':[q for q in normalize_requests(m) if q['kind']=='probe'],
      'panel':panel,'delta_before':m.get('delta_before'),'delta_after':m.get('delta_after'),
      'query_receipt':m.get('retention_receipt',m.get('query_receipt')),
      'recorded_retention_readout':m.get('retention_decode'),
      'late_bus_causal_panel':causal_panel,'comparison162':m.get('comparison162'),
      'intervention':m.get('intervention') if causal_panel else None,
      'new_participant_inputs_after_fork':m.get('new_participant_inputs_after_fork') if causal_panel else None,
      'scope':'Delta alone is state distinction,notavailablefunctionalaccess; emittedprobes andreceipts areseparatelypreserved. A reader97 and latebus162 may depend on differentdistributedcontext, so causalresultsareindexedbyreader/window.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--extra-index',action='append',default=[],help='FAMILY=path/to/INDEX.json; explicitnewprimaryregistryentry')
    a=p.parse_args();registry=[(family,ROOT/'resultados'/folder/'INDEX.json',kind) for family,folder,kind in REGISTRY]
    extra_file=ROOT/'configuraciones/review_registry_additions.json'
    extra=read(extra_file).get('indices',[]) if extra_file.exists() else []
    extra += [{'family':x.split('=',1)[0],'index':x.split('=',1)[1],'kind':'PREPARATION'} for x in a.extra_index]
    registry += [(x['family'],ROOT/x['index'],x.get('kind','PREPARATION')) for x in extra]
    revision=ROOT/'revision';revision.mkdir(parents=True,exist_ok=True);entries=[];observations=[];retention=[];initiative=[];seen=set();missing=[];families=[]
    for family,index_path,kind in registry:
        if not index_path.exists():missing.append({'family':family,'index':relative(index_path),'state':'NOT_FINAL_INDEX_PRESENT'});continue
        content=read(index_path);items=content.get('cases',[]) if isinstance(content,dict) else content
        n=0
        for item in items:
            rel=item.get('evidence',item.get('source'))
            if not rel or not rel.replace('\\','/').endswith(('MEASUREMENTS.json','CASE_RESULT.json')):raise ValueError('Registry index has noprimary result '+str((family,item.keys())))
            path=ROOT/rel
            if not path.exists():missing.append({'family':family,'primary':rel,'state':'PRIMARY_NOT_FINAL'});continue
            resolved=str(path.resolve())
            if resolved in seen:raise ValueError('Sameprimaryregisteredtwice '+resolved)
            seen.add(resolved);entry,m=primary_entry(family,path,kind,item);entries.append(entry);n+=1
            observations += compact_observations(m,entry['case_key'],entry['primary'])
            if family.startswith(('D','R','RET','LA','CC','B01BUS','WBCTRL')):retention.append(retention_row(entry,m))
            if m.get('predictions') or family.startswith(('AB','BD','BC','AS')):
                initiative.append({'case_key':entry['case_key'],'primary':entry['primary'],'record_kind':entry['record_kind'],
                   'predictions_written_before_target':m.get('predictions',[]),'requests':normalize_requests(m),
                   'summary':m.get('summary'),'host_RAW_clock_edits':m.get('host_RAW_clock_edits_after_T0',m.get('host_RAW_clock_writes_after_T0',[])),
                   'native_query_initiation_evidence':None,'query_origin_scope':'Thisrecordcontainsprogrammedoruserinducedqueries. Nativeinitiatedquestionselection requiresseparateevidence.'})
        families.append({'family':family,'index':relative(index_path),'index_sha256':sha(index_path),'registered_records':n})
    # One aggregate contains two diagnostic forks, not a third newpreparation.
    rescue_path=ROOT/'resultados/ARCHITECTURE_U4_RESCUE_01/MEASUREMENTS.json'
    if rescue_path.exists():
        m=read(rescue_path)
        for i,sub in enumerate(m['results']):
            entries.append({'case_key':'ARCH_RESCUE/'+sub['label'],'family':'ARCH_RESCUE','case_id':sub['label'],'schema':m['schema'],
                'primary':relative(rescue_path),'primary_subcase':'results/'+str(i),'sha256':sha(rescue_path),'record_kind':'DIAGNOSTIC_FORK',
                'case_fields':{'raw_written':sub['raw_written'],'clock_written':sub['clock_written']},'parent':'AS03_FOUR_COMPOUNDS',
                'tick_start':30,'tick_end':33,'preparations':0,'component_preparations':0,'diagnostic_forks':1,'controlled_continuations':0,'all_continuation_runs':1,
                'owner_runtimes':1,'candidate_bodies':4,'status':'MEASURED','receipt_counts':{}})
            observations += compact_observations({'rows':sub['frames']},entries[-1]['case_key'],relative(rescue_path))
    reference_files=('referencias/sem01/MEASUREMENTS.json','referencias/sem01_normalized01/MEASUREMENTS.json','referencias/central_normalized01/MEASUREMENTS.json')
    references=[{'primary':'resultados/'+x,'sha256':sha(ROOT/'resultados'/x),'record_kind':'REFERENCE_ATTEMPT_OR_REPRODUCTION','new_scientific_preparations_counted':0} for x in reference_files if (ROOT/'resultados'/x).exists()]
    tech_path=ROOT/'resultados/ARCHITECTURE_U4_INSPECTION_01.json'
    technical_reproductions=[{'primary':relative(tech_path),'sha256':sha(tech_path),'record_kind':'TECHNICAL_REPRODUCTION','new_scientific_preparations_counted':0}] if tech_path.exists() else []
    errors=[]
    for folder in sorted((ROOT/'jobs').iterdir()):
        command=folder/'COMMAND.json'
        if not command.exists():continue
        value=read(command)
        if value.get('exit_code') not in (None,0) or value.get('status') in ('TIMEOUT','FAILED','ERROR'):
            errors.append({'job':folder.name,'command':relative(command),'sha256':sha(command),'status':value.get('status'),
               'exit_code':value.get('exit_code'),'stderr':relative(folder/'stderr.log') if (folder/'stderr.log').exists() else None})
    counts={'measured_primary_records':len(entries),'new_preparations':sum(x['preparations'] for x in entries),
       'component_preparations_subset':sum(x['component_preparations'] for x in entries),'diagnostic_forks':sum(x['diagnostic_forks'] for x in entries),
       'controlled_continuations_not_new_preparations':sum(x['controlled_continuations'] for x in entries),'technical_reproductions_separate':len(technical_reproductions),
       'reference_primary_files_separate':len(references),'failed_or_timeout_jobs_separate':len(errors),
       'independent_statistical_replicates_claimed':0}
    by_family={f:dict(Counter(x['record_kind'] for x in entries if x['family']==f)) for f in sorted({x['family'] for x in entries})}
    index={'schema':'CPC6.review.primary_index.v1','generator_sha256':sha(__file__),'registry':families,'counts':counts,'by_family':by_family,
       'cases':entries,'reference_attempts_or_reproductions':references,'technical_reproductions':technical_reproductions,'technical_errors_and_timeouts':errors,'pending_indices':missing,
       'counting_contract':'Primaryresultsonly. Analysissummaries,sourcecopies,indexrows,snapshots,ticks,checksumsandCOMBINATIONmembership arenotadditionalcases.22RETrecords=14preparations+8forks,not30individuals. ARCHhistories19 countedseparatelyfrom2rescueforksand1technicalreproduction.'}
    put(revision/'INDICE_EVIDENCIA.json',index)
    with (revision/'OBSERVACIONES.jsonl').open('w',encoding='utf-8',newline='\n') as f:
        for row in observations:f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
    calculations={'schema':'CPC6.review.calculations.v1','counts':counts,'by_family':by_family,'formulae':{
      'primary_records':'Oneentryperregisteredprimarycase; aggregateforksseparatedbysubcasepath.',
      'preparations':'1forfreshRuntimephysicalpreparation,0fordiagnosticforkandloadcontinuation.',
      'receipt_counts':'Status countsamongrecordedrequests; mayincludeoriginalqueuedrequestsintheparentofacontinuation. Notcountedagainasnewexperienceevents.',
      'observations':'Up to6 exactphysicalrecordsperselectedtick; fullprimaryevidenceunchanged; noRAW/clockconversiontofloat.',
      'interpretation':'Noautomaticscientificsuccess,intelligenceorsemanticmasteryverdictgenerated.'},
      'observation_frames':len(observations),'primary_bytes':sum((ROOT/x['primary']).stat().st_size for x in entries if 'primary_subcase' not in x),
      'architecture_calculations':'resultados/ARCHITECTURES_AND_DIALOGUE.json','retention_calculations':'resultados/RETENTION_SYNTHESIS.json'}
    put(revision/'CALCULOS.json',calculations)
    put(revision/'INICIATIVA_Y_TRANSFERENCIA.json',{'schema':'CPC6.review.initiative_transfer.v1','cases':initiative,
       'architecture_message_evidence':read(ROOT/'resultados/ARCHITECTURES_AND_DIALOGUE.json'),
       'attribution':'Nativepredictionsandnativeportadores areseparatefromexternallyscheduledrequests. ThepreparedfiniteR14controllerand24fixedsupportexposures arenotaregulatorychoicelearnedfromutility.'})
    put(revision/'COMPARACION_ARQUITECTURAS.json',read(ROOT/'resultados/ARCHITECTURES_AND_DIALOGUE.json'))
    put(revision/'RETENCION.json',{'schema':'CPC6.review.retention.v1','old_access_summary':read(ROOT/'resultados/RETENTION_SYNTHESIS.json'),
        'longitudinal_and_access_cases':retention,'scope':'Perindividualandpercontinuationpanels; donotaddrepertoriesofdifferentworldsasoneindividual. State,access,emissionanduseareseparate.'})
    print(json.dumps({'counts':counts,'by_family':by_family,'observation_frames':len(observations),'pending':missing}),flush=True)


if __name__=='__main__':main()
