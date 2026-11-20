"""Compact functional tables from the independently recalculated R17 archive.

No decisions, learning or reconstruction are fed to the participant. The frozen
test layout is compared with every result, including absent or incorrect outputs.
"""
import argparse,gzip,hashlib,json
from collections import Counter
from pathlib import Path

def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def calculate(root):
    pro=load(root/'PROTOCOLO.json');calc=load(root/'RECALCULO_FASE_R3.json');rows=load(root/'REGISTROS_TRANSPORTE.json.gz');events={e['id']:e for e in pro['events']};transport={r['id']:r for r in rows};byregime=[];raw=[];teaching=[]
    initial=pro['initial_memory_signs']
    for row in rows:
        p=json.loads(row['payload']);situations=p.get('situaciones',[])
        if any(s.get('operacion_memoria')=='revisar'for s in situations):
            answer=json.loads(row['result']);native=answer['result']['rows'][0]['result']['rows'][0]
            teaching.append({'id':row['id'],'status':row['status'],'before_tick':answer['before_tick'],'after_tick':answer['after_tick'],'context':native['context_signal'],'signal':native['teaching_signal'],'requests':len(native['requests']),'admitted':sum(x['receipt']['status']=='applied'for x in native['requests']),'hub':native['hub'],'scope':'Explicit operator teaching; not autonomous consequence-policy learning.'})
    revision_tick=teaching[0]['after_tick']if len(teaching)==1 else None
    memory=[]
    for r in calc['memory_uses']:
        expected=teaching[0]['signal']if r['context']=='beta'and revision_tick is not None and r['tick']>revision_tick else initial[r['context']]
        payload=json.loads(transport[r['id']]['payload']);mode=payload.get('situaciones',[{}])[0].get('modo')
        memory.append({**r,'regime':events.get(r['id'],{}).get('regime'),'request_mode':mode,'expected_from_declared_teaching_history':expected,'matches_expected':r['choice']==expected})
    for e in pro['events']:
        item=e['payload']['situaciones'][0]
        if item['modo']!='crudos':continue
        responses=[r for r in calc['native_readers']if r['id']==e['id']];read=responses[0]if len(responses)==1 else None
        nonzero=[{'index':i,'value':v}for i,v in enumerate(item['componentes'])if v]
        extra=[v['index']for v in nonzero if v['index']!=0];expected=-1 if not extra else 1
        raw.append({'id':e['id'],'regime':e['regime'],'actual_transport_status':transport.get(e['id'],{}).get('status'),'component_count':len(item['componentes']),'nonzero':nonzero,'choice':read['choice']if read else None,'native_read_tick':read['tick']if read else None,'frozen_expected_test_relation':expected,'matches_expected':bool(read)and read['choice']==expected,'R3_reserved_index':extra[0]if len(extra)==1 and extra[0]in(3,64,126)else None})
    for i in(1,2,3):
        m=[r for r in memory if r['regime']==i];a=[r for r in raw if r['regime']==i];last={}
        for r in m:last[r['context']]=r
        byregime.append({'regime':i,'scheduled_opportunities':sum(e['regime']==i for e in pro['events']),'memory_uses_including_chain_starts':len(m),'memory_unique_signs':sum(r['choice']in(-1,1)for r in m),'memory_matches_declared_history':sum(r['matches_expected']for r in m),'last_observation_per_context':last,'raw128_requests':len(a),'raw128_unique_signs':sum(r['choice']in(-1,1)for r in a),'raw128_matches_frozen_test':sum(r['matches_expected']for r in a)})
    workers=calc['workers'];work=[r for r in workers if r['operation']=='execute_service'];prepare=[r for r in workers if r['operation']=='prepare'];finish=[r for r in workers if r['operation']=='verify_commit'];nominal=Counter(e['payload']['situaciones'][0]['modo']for e in pro['events']);scalar=[]
    for e in pro['events']:
        s=e['payload']['situaciones'][0]
        if s['modo']=='dato':
            rs=[r for r in calc['native_readers']if r['id']==e['id']]
            scalar.append({'id':e['id'],'regime':e['regime'],'value':s['valor'],'choice':rs[0]['choice']if len(rs)==1 else None,'transport_status':transport.get(e['id'],{}).get('status')})
    return {'schema':'DEE.unified.service_functional_tables.v1',
      'sources':[{'file':f,'sha256':hashlib.sha256((root/f).read_bytes()).hexdigest()}for f in('PROTOCOLO.json','RECALCULO_FASE_R3.json','REGISTROS_TRANSPORTE.json.gz')],
      'underlying_recalculation_issues':calc['issues'],'regimes':byregime,'memory_uses':memory,
      'memory_reading_components':{'direct_queries':sum(r['request_mode']=='memoria'for r in memory),'chain_start_reads':sum(r['request_mode']=='cadena-iniciar'for r in memory),'explicit_revision_without_query':len(teaching)},
      'explicit_teaching':teaching,'raw128':raw,'scalar':scalar,
      'chains':{'nominal_begin':nominal['cadena-iniciar'],'nominal_finish':nominal['cadena-finalizar'],'actual_preparations':len(prepare),'accepted_preparations':sum(r['accepted']for r in prepare),'actual_verifications':len(finish),'transaction_commits':sum(r['transaction_completed']for r in finish),'all_actual_stages':prepare+finish},
      'individual_work':{'nominal_opportunities':nominal['trabajo'],'actual_executions':len(work),'useful_under_declared_environmental_law':sum(r['accepted']for r in work),'not_useful_under_declared_environmental_law':sum(not r['accepted']for r in work),'native_choices':dict(Counter(str(r['worker'])for r in work))},
      'scope':'Retrospective functional accounting from frozen evaluation protocol and RAW-verified responses. Six sign associations are not six NSM meanings. All repeated queries share one life. The last observed panel precedes the final idle interval; it is not a measurement of accessibility after that interval. Raw128 successes and failures remain in full. Explicit beta revision is operator teaching, not autonomous policy learning.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'regimes':[{k:v for k,v in q.items()if k!='last_observation_per_context'}for q in r['regimes']],'teaching':r['explicit_teaching'],'individual_work':r['individual_work']}));return bool(r['underlying_recalculation_issues'])
if __name__=='__main__':raise SystemExit(main())
