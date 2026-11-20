"""External functional accounting of all reserved APD opportunities.

Transport admission, unique physical response, content, real artifact and modeled
cost are separate. Rejections and silences remain in their original denominator.
"""
import argparse,gzip,hashlib,json
from collections import Counter
from pathlib import Path

def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def calculate(root):
    pro=load(root/'PROTOCOLO.json');config=load(root/'CONFIG_READY.json');calc=load(root/'RECALCULO_SERVICIO_APD.json');rows=load(root/'REGISTROS_APD.json.gz');events={e['id']:e for e in pro['events']};transport={r['id']:r for r in rows};teaching=calc['explicit_teaching'];initial=config['audit_only_prior_memory_signs_not_actor_input'];memory=[];oldforms={k:v for k,v in calc['baseline_history']['last_physically_decoded_signs'].items()if k not in initial}
    canonical=json.dumps(config,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf8')
    if hashlib.sha256(canonical).hexdigest()!=pro['configuration_sha256']:raise ValueError('The source of auditor-only history and literal fixed curriculum differs from the frozen configuration')
    if any(calc['baseline_history']['last_physically_decoded_signs'].get(k)!=v for k,v in initial.items()):raise ValueError('Declared initial memory history disagrees with its actual preceding physical panel')
    def expected_sign(context,tick,initials):
        applicable=[r for r in teaching if r['context']==context and r['after_tick']<tick and r['signal']in(-1,1)and r['admissions']['by_status'].get('applied',0)==r['admissions']['requested_unique']and r['admissions']['requested_unique']>0]
        return applicable[-1]['signal']if applicable else initials.get(context)
    for row in calc['memory_uses']:
        wanted=expected_sign(row['context'],row['tick'],initial);payload=json.loads(transport[row['id']]['payload']);mode=payload.get('situaciones',[{}])[0].get('modo')
        memory.append({**row,'regime':events.get(row['id'],{}).get('regime'),'request_mode':mode,'expected_from_declared_history':wanted,'matches_expected':wanted is not None and row['choice']==wanted})
    primitive=[]
    def add_primitive(audited,item,index=None):
        if audited.get('kind')!='integrated_APD':return
        tick=item['before_tick']or 0;wanted=expected_sign(audited['literal_form'],tick,oldforms);actual=(audited.get('word')or{}).get('command');route=(audited.get('route')or{}).get('choice');numeric=audited.get('numeric_result');completed=audited.get('completed',False)
        price=audited.get('modeled_price')
        primitive.append({'id':item['id'],'composition_stage':index,'regime':events.get(item['id'],{}).get('regime'),'before_tick':tick,'after_tick':item['after_tick'],'form':audited['literal_form'],'word_command':actual,'expected_from_explicit_history':wanted,'word_matches_history':wanted is not None and actual==wanted,'route':route,'procedure':'native'if route==-1 else'external'if route==1 else'material_help_external'if route==0 else None,'numeric_result':numeric,'correct_given_actual_operator':audited.get('correct_when_responded'),'abstention':audited.get('abstention',True),'real_artifact_completed':completed,'modeled_price':price,'completed_within_prepared_modeled_budget2':completed and price is not None and price<=2,'audit_issues':audited.get('issues',[])})
    for item in calc['APD_requests']:add_primitive(item['audit'],item)
    for item in calc['assisted_compositions']:
        for i,part in enumerate(item['audit'].get('parts',[])):add_primitive(part,item,i)
    primitive.sort(key=lambda r:(r['before_tick'],r['id'],r['composition_stage']if r['composition_stage']is not None else-1))
    raw=[];datum=[]
    for e in pro['events']:
        row=e['payload']['situaciones'][0];mode=row['modo']
        if mode not in('crudos','dato'):continue
        readers=[r for r in calc['native_readers']if r['id']==e['id']and r['origin']==[15,15,15]];reader=readers[0]if len(readers)==1 else None
        item={'id':e['id'],'regime':e['regime'],'transport_status':transport.get(e['id'],{}).get('status'),'choice':reader['choice']if reader else None,'native_read_tick':reader['tick']if reader else None}
        if mode=='crudos':
            nz=[{'index':i,'value':v}for i,v in enumerate(row['componentes'])if v];extra=[r['index']for r in nz if r['index']!=0];expected=1 if extra else-1
            raw.append({**item,'component_count':len(row['componentes']),'nonzero':nz,'frozen_test_relation':expected,'matches_expected':bool(reader)and reader['choice']==expected})
        else:datum.append({**item,'value':row['valor']})
    regimes=[]
    for i in(1,2,3):
        scheduled=[e for e in pro['events']if e['regime']==i];identifiers={e['id']for e in scheduled};m=[r for r in memory if r['id']in identifiers];p=[r for r in primitive if r['id']in identifiers];a=[r for r in raw if r['id']in identifiers];last={}
        for r in m:last[r['context']]=r
        regimes.append({'regime':i,'nominal_scheduled':len(scheduled),'nominal_transport':dict(Counter(transport.get(e['id'],{}).get('status','not_queued')for e in scheduled)),'memory_uses':len(m),'memory_matches_history':sum(r['matches_expected']for r in m),'last_observation_per_context':last,'APD_primitive_executions':len(p),'APD_word_matches_history':sum(r['word_matches_history']for r in p),'APD_responded':sum(not r['abstention']for r in p),'APD_numeric_correct_given_actual_operator':sum(r['correct_given_actual_operator']is True for r in p),'APD_completed_real_artifacts':sum(r['real_artifact_completed']for r in p),'APD_routes':dict(Counter(str(r['route'])for r in p)),'raw128_nominal':len(a),'raw128_matches_frozen_relation':sum(r['matches_expected']for r in a)})
    def scheduled_kind(mode):return[e for e in pro['events']if e['payload']['situaciones'][0]['modo']==mode]
    def opportunity_counts(mode,actual,success):
        scheduled=scheduled_kind(mode);new=[r for r in actual if r['id'].startswith(pro['request_prefix'])];return {'scheduled':len(scheduled),'queued_rows':sum(e['id']in transport for e in scheduled),'completed_transport':sum(transport.get(e['id'],{}).get('status')=='completed'for e in scheduled),'archived_complete_execution_results':len(new),'partial_or_uncertain_transport_rows':sum(transport.get(e['id'],{}).get('status')in('uncertain','failed_preserved','processing')for e in scheduled),'numeric_correct_given_actual_operator':sum(success(r)for r in new),'scope':'New reserve opportunities only; seven inherited queued actions remain separate. Complete archived results are not all possible partial physical executions. Numeric correctness only; lexical-history agreement, artifact completion and route usefulness remain separate.'}
    apd_single=calc['APD_requests'];counts=calc['native_counts'];compositions=calc['assisted_compositions'];workers=calc['workers'];prepare=[r for r in workers if r['operation']=='prepare'];verify=[r for r in workers if r['operation']=='verify_commit'];ordinary=[r for r in workers if r['operation']=='execute_service'];last={}
    for row in memory:last[row['context']]=row
    return {'schema':'DEE.APD01.service_functional_tables.v1','sources':[{'file':f,'sha256':sha(root/f)}for f in('PROTOCOLO.json','CONFIG_READY.json','RECALCULO_SERVICIO_APD.json','REGISTROS_APD.json.gz')],'underlying_recalculation_issues':calc['issues'],'regimes':regimes,'memory_uses':memory,'last_memory_observations':last,'explicit_teaching':teaching,'APD_primitive_uses_including_composition_stages':primitive,'APD_direct':opportunity_counts('apd',apd_single,lambda r:r['audit'].get('correct_when_responded')is True),'native_count':opportunity_counts('apd-conteo',counts,lambda r:r['audit'].get('correct_when_responded')is True),'composition':opportunity_counts('apd-componer',compositions,lambda r:r.get('result')is not None and not r.get('out_of_domain')and all(p.get('correct_when_responded')is True for p in r['audit'].get('parts',[]))),'raw128':raw,'scalar':datum,'environment_changes':calc['environment_changes'],'chains':{'nominal_begin':len(scheduled_kind('cadena-iniciar')),'nominal_finish':len(scheduled_kind('cadena-finalizar')),'actual_preparations':len(prepare),'accepted_preparations':sum(r['accepted']for r in prepare),'actual_verifications':len(verify),'transaction_commits':sum(r['transaction_completed']for r in verify),'all_stages':prepare+verify},'individual_work':{'executions':len(ordinary),'useful_under_declared_law':sum(r['accepted']for r in ordinary),'not_useful':sum(not r['accepted']for r in ordinary)},'new_form_histories':{form:{'explicit_teaching':[r for r in teaching if r['context']==form],'uses':[r for r in primitive if r['form']==form]}for form in('total','quita')},'scope':'All denominators retained. Six Spanish forms address two already prepared operator classes, not six new concepts or NSM meanings. New-form and beta lessons are explicit operator events. The final observed panel precedes subsequent idle ticks; it is not proof of unlimited later access. Three regimes and repeated requests belong to one life, not independent learners.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open('x',encoding='utf8')as f:json.dump(r,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'regimes':r['regimes'],'APD_direct':r['APD_direct'],'count':r['native_count'],'composition':r['composition']}));return bool(r['underlying_recalculation_issues'])
if __name__=='__main__':raise SystemExit(main())
