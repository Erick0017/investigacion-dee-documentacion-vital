"""Post-trajectory reconciliation only; never imported by a participant."""
import hashlib,json,os,sys
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src/relaciones'))
from analyze_full_spatial_e1 import functional_windows
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def put(p,m):
 p=Path(p);t=p.with_name(p.name+'.pending');t.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');os.replace(t,p)
def valid(o,v,load=None):return bool(o['active']and o['semantic']==1 and o['direction']==v and(load is None or o['s_reg']==load))
def rows():
 out=[];snapchecks=[]
 folders=['count_sign','count_sign_layout2','count_sign_branch','count_sign_final_fixed','count_mcts','count_sign_diagnostics','count_sign_Bonly_confirm','count_sign_original_diagnostics']
 for folder in folders:
  for p in sorted((ROOT/'resultados/semantica'/folder).glob('*/MEASUREMENTS.json')):
   m=load(p);r={'case_id':m['case']['id'],'schema':m['schema'],'primary':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'preparations':m.get('preparations',0),'diagnostic_forks':m.get('diagnostic_forks',0),'continuations':m.get('continuations',0),'status':m.get('status'),'source_sha256':m.get('source_sha256'),'configuration_sha256':m.get('configuration_sha256'),'parent':m.get('parent')}
   for s in m.get('snapshots',[]):
    if not s.get('sha256'):continue
    sp=p.parent/s['path'];snapchecks.append({'case_id':r['case_id'],'path':sp.relative_to(ROOT).as_posix(),'valid_sha256':sha(sp)==s['sha256']})
   if'snapshot'in m and m['snapshot'].get('sha256'):
    s=m['snapshot'];sp=p.parent/s['path'];snapchecks.append({'case_id':r['case_id'],'path':sp.relative_to(ROOT).as_posix(),'valid_sha256':sha(sp)==s['sha256']})
   if m['schema']=='CPC8R.count_sign.alternative_diagnostic.v1':
    r.update(parent_unchanged=m['parent_unchanged'],assisted_alternative114=m['qualified_alternative114'],new_added_requests=sum(not x.get('inherited_identical_request_alias',False)for x in m['new_requests']),aliased_inherited_requests=sum(x.get('inherited_identical_request_alias',False)for x in m['new_requests']),receipt_statuses=dict(Counter(x['receipt']['status']for x in m['new_requests'])),scope='DIAGNOSTIC_FORK_ONLY; original MAIN decoder/window is unchanged')
   elif m['schema']=='CPC8R.magnitudeCTS_countF3.measurements.v1':
    fs=functional_windows(m);f={x['tick']:x for x in m['frames']};case=m['case'];cq=[]
    for index,t in enumerate((70,137,204,338,405,472,539)):
     pre=f[t-1]['quantity'];ref=case.get('quantity_reference',31)+(case.get('addition_value',11)if index>=3 else 0)+5;values=list(case.get('quantity_objects',(16,45,31)))+list(case.get('later_quantity_objects',(36,42,31,50)));obj=values[index]+5;operands=pre['reference_site']['active']and pre['reference_site']['s_reg']==ref and pre['object_site']['active']and pre['object_site']['s_reg']==obj
     match=next(x for x in fs if x['family']=='QUANTITY'and x['tick']==t);cq.append({'tick':t,'pre_reference':pre['reference_site'],'pre_object':pre['object_site'],'operands_preserved':operands,'output':match['physical'],'valid_with_operands':bool(operands and match['valid_functional_readout'])})
    mag=[]
    for index,t in enumerate((147,214,281)):
     pre=f[t-1]['magnitude_transfer'];post=f[t]['magnitude_transfer'];ref=case.get('magnitude_value',31)+5;obj=list(case.get('magnitude_objects',(18,45,31)))[index]+5;dx=(ref>obj)-(ref<obj);operands=pre['reference_site']['active']and pre['reference_site']['s_reg']==ref and pre['object_site']['active']and pre['object_site']['s_reg']==obj
     mag.append({'tick':t,'pre_reference':pre['reference_site'],'pre_object':pre['object_site'],'output':post['center'],'operands_preserved':operands,'valid':bool(operands and valid(post['center'],[dx,0,0],7))})
    counter=[]
    for t,offset in((10,5),(77,12),(144,19)):
     o=f[t]['count_current']['collector'];counter.append({'tick':t,'physical':o,'fixed_offset':offset,'affine_units':o['s_reg']-offset if o['active']and o['semantic']==1 else None,'query_receipts':[x for x in m['requests']if x['port']=='counter.'+('cue'if t==10 else'query1'if t==77 else'query2')]})
    social=[x for x in m['contact_social_observations']if x['phase']=='QUERY'];source=case.get('initiative_source',1);useq=[]
    for rec in m['return_use_observations']:
     if rec['tick']==89:
      useq=[dict(x,valid=valid(x['contact'],[0,0,-1])and x['contact']['s_reg']>13)for x in rec['receivers']]
    word=f[616]['joint']['plus.changed']['delivery_site']
    late=[]
    for t,field,vec,minimum in((411,'query_site',[-1,1,0],5),(417,'effect_site',[0,1,0],7),(478,'renewed_site',[-1,1,0],5),(484,'renewed_effect',[0,1,0],7)):
     o=f[t]['contact']['right.changed'][field];late.append({'tick':t,'physical':o,'valid':valid(o,vec)and o['s_reg']>minimum})
    r.update(resources=m['geometry']['resources'],count_geometry=m['geometry']['count_coexistence'],count_readings=counter,old_functional_windows=fs,old_functional_summary={kind:{'valid':sum(x['valid_functional_readout']for x in fs if x['family']==kind),'windows':sum(x['family']==kind for x in fs)}for kind in sorted({x['family']for x in fs})},quantity_with_operands=cq,magnitude_transfer=mag,contact_social_query554=social,late_contact=late,MODE_B428=[x for x in m['social_captures']if x['phase']=='FORM_QUERY'and x['tick']==428],IUE_use89=useq,word616={'physical':word,'valid':valid(word,[0,1,1])and word['s_reg']>13},receipt_statuses=dict(Counter(x['receipt']['status']for x in m['requests'])))
   else:
    g=m['geometry'];f={x['tick']:x for x in m['frames']};case=m['case'];final=g.get('readout')=='transient_gap';parallel='branches'in g;comparison=g['ticks'].get('comparison',87);form=g['ticks'].get('form',90);queries=g['ticks'].get('queries',[157,224]);r.update(resources=g['resources'],readout=g.get('readout','layout'+str(g.get('layout',1))),prepared_scope=g['scope'])
    if parallel:
     r['native_references24']=f.get(24,{}).get('branches',[]);r['operands90']=f.get(90,{}).get('branches',[]);r['comparison91']=f.get(91,{}).get('branches',[]);r['form94']=f[94]['names'];r['queries']=[]
     r['additional_acquisition100']={'physical103':f.get(103,{}).get('extra'),'physical170':f.get(170,{}).get('extra'),'receipts':[x for x in m['requests']if x['port'].startswith('extra.')],'scope':'Separate paired experience100 and later170probe; additional support is not a second count meaning.'}
     for k,t in enumerate(queries):
      key='query1'if k==0 else'query2';z=1 if k==0 else 0;observed=f[t]['names'];qualified=[]
      for o in observed:
       physical=o[key];v=[0,1,z]if final else[o['candidate_comparator_x']-1,1,z]
       if valid(physical,v)and physical['s_reg']>7:qualified.append({'route_axis_candidate':o['route_axis_candidate'],'candidate_comparator_x':o['candidate_comparator_x'],'physical':physical})
      r['queries'].append({'tick':t,'qualified_by_ORIGINAL_frozen_reader':qualified,'all_exact':observed,'scope':'No alternate-diagnostic decoder applied to this MAIN reading.'})
    else:
     r.update(reference_pre=f[comparison-1]['quantity'],comparison=f[comparison]['quantity'],form=f[form]['names'],queries=[{'tick':t,'all_exact':f[t]['names']}for t in queries])
    r['receipt_statuses']=dict(Counter(x['receipt']['status']for x in m['requests']))
   expected=m.get('source_sha256',{})
   if not expected and 'parent'in m and 'snapshot'in m['parent']:
    parent_primary=(ROOT/m['parent']['snapshot']).parent/'MEASUREMENTS.json'
    if parent_primary.exists():expected=load(parent_primary).get('source_sha256',{})
   r['executed_source_checks']=[{'path':rel,'expected_sha256':value,'actual_sha256':sha(p.parent/'executed_source'/rel),'equal':sha(p.parent/'executed_source'/rel)==value}for rel,value in expected.items()]
   if m['schema']=='CPC8R.count_sign.original_reader_diagnostic.v1':
    r.update(parent_unchanged=m['parent_unchanged'],interventions=m['interventions'],new_added_requests=0,scope='Diagnostic all-bank cut/sham; ORIGINAL queued reader only, no new channel, no modified decoder.')
   diagnostic_source=p.parent/'executed_source/diagnostic_reader.py'
   if diagnostic_source.exists():r['diagnostic_reader_source_sha256']=sha(diagnostic_source)
   original_diag=p.parent/'executed_source/original_reader_diagnostic.py'
   if original_diag.exists():r['original_reader_diagnostic_source_sha256']=sha(original_diag)
   out.append(r)
 return out,snapchecks

if __name__=='__main__':
 data,snaps=rows();attempts=[]
 for folder in('count_sign_final','count_sign_final_repaired'):
  for p in sorted((ROOT/'resultados/semantica'/folder).glob('*/executed_source/src/count_sign/branch_session.py')):
   attempts.append({'case_id':p.parents[3].name,'source':p.relative_to(ROOT).as_posix(),'source_sha256':sha(p),'status':'IMPORT_SYNTAX_FAILURE_BEFORE_RUNTIME','preparations':0})
 out={'schema':'CPC8R.count_sign_and_coexistence.analysis.v1','counts':{'primary_records':len(data),'preparations':sum(r['preparations']for r in data),'diagnostic_forks':sum(r['diagnostic_forks']for r in data),'continuations':sum(r['continuations']for r in data),'technical_import_failures':len(attempts),'snapshots_verified':len(snaps),'snapshot_hash_failures':sum(not s['valid_sha256']for s in snaps)},'cases':data,'snapshot_checks':snaps,'technical_import_failures':attempts,
  'data_calculation_interpretation_separated':True,'original_failures_retained':True,
  'scope':'Post-trajectory auditor computation; no import of this module by a session, no result writes into MAIN. Parallel comparator threshold and unit2calibration are prepared, not a learned counting rule. Alternate diagnostic114 does not replace original failed A-only/TWO114/148 readers. B-only G13/G31 do have original qualified114/148 readings, separately reported.'}
 out['final_access_by_history']=[]
 for r in data:
  if r.get('readout')!='transient_gap':continue
  out['final_access_by_history'].append({'case_id':r['case_id'],
   'reference24_loads':[x['reference_hub24']['s_reg']for x in r['native_references24']if x['reference_hub24']['active']],
   'comparison91_active_vectors':[x['quantity']['center']['direction']for x in r['comparison91']if x['quantity']['center']['active']],
   'formed12_at94':[{'route_axis_candidate':x['route_axis_candidate'],'candidate_comparator_x':x['candidate_comparator_x'],'physical':x['memory']}for x in r['form94']if x['memory']['active']and x['memory']['s_reg']==12],
   'original_qualified_counts':[{'tick':x['tick'],'n':len(x['qualified_by_ORIGINAL_frozen_reader'])}for x in r['queries']]})
 out['final_access_scope']='B-only G13/G31 yields zero-X formed memory and original qualified114/148 readings, whereas A-only G11 and TWO G12/G32 retain X and fail those readers. Same reference7 is not invariant later expression across A-only/B-only histories. B-specific form controls and ORIGINAL-reader cut/sham are reported separately. All successes are auxiliary worlds, not the selected MAIN;114 can affect148.'
 out['geometry_narrative_erratum']='Frozen branch geometry prepared prose says material6, inherited from the permanent layout. In the actual transient_gap protocol object resource3 plus cue5 produces threshold8, with exact operands90 retained. No recipe, payload, decoder or primary is changed to correct this prose.'
 out['interpretation_erratum']={'previous_statement':'The original114/148 readers failed, without a history qualifier.','corrected_statement':'They fail in A-only G11 and TWO G12/G32, not B-only G13/G31. The earlier blanket statement was an analysis overgeneralization, not a decoder or physical change.','corrected_after_review_of':['CNS_G13_ONE_B','CNS_G31_RESERVE_ONE_B'],'physics_or_primary_modified':False}
 parent=load(ROOT/'resultados/semantica/count_sign_final_fixed/CNS_G13_ONE_B/MEASUREMENTS.json');sham=load(ROOT/'resultados/semantica/count_sign_original_diagnostics/CNS_D31_B_ORIGINAL_SHAM/MEASUREMENTS.json')
 pf={f['tick']:f for f in parent['frames']};sf={f['tick']:f for f in sham['frames']}
 out['Bonly_confirmation']={'no_form':'CNS_G51_B_NO_FORM','unpaired':'CNS_G52_B_UNPAIRED','sham':'CNS_D31_B_ORIGINAL_SHAM','cut':'CNS_D32_B_ORIGINAL_CUT','reader':'Original fixed all-candidate reader. Candidate bank identifies the prepared comparison branch; zero-X alone is not an ONE category.','sham_parent_physical_equality':[{'tick':t,'RAW_equal':pf[t]['physical']['RAW_sha256']==sf[t]['physical']['RAW_sha256'],'clocks_equal':pf[t]['physical']['clocks_sha256']==sf[t]['physical']['clocks_sha256']}for t in(94,114,148,171)],'interpretation':'Auxiliary B-only availability after experience100 and successive114/148 queries, not E2 MAIN or two jointly learned lexical meanings; first query may affect second.'}
 out['counts']['executed_source_hash_checks']=sum(len(r['executed_source_checks'])for r in data)
 out['counts']['executed_source_hash_failures']=sum(not c['equal']for r in data for c in r['executed_source_checks'])
 out['invalid_duplicate_diagnostic_ids']=['CNS_D11_ONE_SHAM','CNS_D12_ONE_CUT']
 out['diagnostic_scope']='D11/D12 introduced duplicate probes at already queued input cells and changed state1vs77: conflicts make them unsuitable negatives. Preserved. D21-D27 deduplicate literal public interface/request identity, never RAW; they are assisted diagnostic forks only.'
 out['supervised_jobs']=[]
 for job in sorted((ROOT/'jobs').glob('*/COMMAND.json')):
  if job.parent.name.startswith(('count_sign_','count_mcts_','count_diag_')):
   j=load(job);out['supervised_jobs'].append({'name':job.parent.name,'source':job.relative_to(ROOT).as_posix(),'sha256':sha(job),**{k:j.get(k)for k in('status','exit_code','elapsed_seconds','peak_job_memory_bytes','owned_job_closed','owned_worker_waited')}})
 put(ROOT/'resultados/semantica/COUNT_SIGN_AND_COEXISTENCE_ANALYSIS.json',out)
 put(ROOT/'revision/COUNT_SIGN_Y_COEXISTENCIA.json',{'schema':'CPC8R.count_sign.review.v1','analysis':'resultados/semantica/COUNT_SIGN_AND_COEXISTENCE_ANALYSIS.json','analysis_sha256':sha(ROOT/'resultados/semantica/COUNT_SIGN_AND_COEXISTENCE_ANALYSIS.json'),'counts':out['counts'],'primary_cases':[{'case_id':r['case_id'],'primary':r['primary'],'sha256':r['sha256'],'schema':r['schema'],'preparations':r['preparations'],'diagnostic_forks':r['diagnostic_forks']}for r in data]})
 print(json.dumps(out['counts']))
 for r in data:
  if r['schema']=='CPC8R.magnitudeCTS_countF3.measurements.v1':print(json.dumps({'id':r['case_id'],'counter':[(x['tick'],x['affine_units'])for x in r['count_readings']],'old':r['old_functional_summary'],'quantity_operands':[x['valid_with_operands']for x in r['quantity_with_operands']],'transfer':[x['valid']for x in r['magnitude_transfer']],'late':[x['valid']for x in r['late_contact']],'MODE':sum(x['covered']for x in r['MODE_B428']),'IUE':sum(x['valid']for x in r['IUE_use89']),'word616':r['word616']['valid']}))
