"""Read-only numeric-gate autopsy; no Native/app imports or query execution."""
from pathlib import Path
from collections import Counter
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];S=P/'estados/B_REAL_R01/sistema'
OUT=P/'control/AUTOPSIA_ARITMETICA_PANEL_B_PI08_R01.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,why):
 if not ok:raise ValueError(why)
def ref(p):return{'path':str(p),'sha256':sha(p)}
source=S/'capacidades/aritmetica_apd_01.py';tree=ast.parse(source.read_text('utf-8-sig'))
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='read_numeric')
namespace={'VERSION':'APD01.native_numeric_tree.candidate.R1','LEVEL':128,'BIAS':32,'AGGREGATE_SITE':[12,17,18],'AGGREGATE_DIRECTION':[1,-1,-1]}
exec(compile(ast.Module(body=[function],type_ignores=[]),str(source)+'::pure_decoder_only','exec'),namespace)
rows=[]
for label in('number13','number8','C2C31'):
 file=P/'ensayos'/('PI08_B_CONSERVACION_R02_'+label+'.json');data=json.loads(file.read_text('utf-8-sig'))
 value=data['result'];value=json.loads(value)if isinstance(value,str)else value
 row=value['result']['rows'][0];arithmetic=row['native_arithmetic']if label=='C2C31'else row
 native=arithmetic['native_operation'];trial=native['native_trial'];numeric=arithmetic['numeric_reader']
 recomputed=namespace['read_numeric'](trial,native['operation']);require(recomputed==numeric,'Literal decoder differs from recorded result')
 observation=numeric['observation'];raw=int(observation['raw']);payload=(raw>>32)&65535
 direction=[((raw>>s)&15)-(16 if(raw>>s)&8 else 0)for s in(48,52,56)]
 valid=bool(raw&0xffffffff)and((raw>>60)&15)==1 and direction==[1,-1,-1]and observation['site']==[12,17,18]
 manual=(payload-(32 if native['operation']=='diferencia'else 0))if valid else None
 require(manual==numeric['numeric_result']==arithmetic['numeric_result'],'Independent uint64 decoding differs')
 requests={r['id']:r for r in trial['requests']};counts=Counter(r['receipt']['status']for r in requests.values())
 require(len(requests)==176 and counts=={'applied':176},'Explicit176 complete current direct inputs required')
 require(all(r['id']==r['receipt']['id']and r['tick']==r['receipt']['effective_tick']for r in requests.values()),'ID/effective-time admission mismatch')
 nonzero=[{k:r[k]for k in('id','port','site','direction','tick','payload')}for r in requests.values()if r['payload']and str(r['port']).startswith('MU.raw.')]
 encoded=trial['raw_components'];require(encoded[:2]==[native['operands'][0],native['operands'][1]if native['operation']=='suma'else 32-native['operands'][1]],'Input codec differs from actual operands')
 rows.append({'label':label,'primary':ref(file),'operation':native['operation'],'actual_operands':native['operands'],
  'independent_encoded_operands':encoded[:2],'input_tick':trial['input_tick'],'query_tick':trial['query_tick'],
  'numeric_read_tick':numeric['tick'],'numeric_gate_is_query_plus1':numeric['tick']==trial['query_tick']+1,
  'numeric_gate_is_datum_minus2':numeric['tick']==trial['datum_tick']-2,
  'query_mod67':trial['query_tick']%67,'query_mod782':trial['query_tick']%782,'calendar':trial['timing'],
  'numeric_observation':observation,'manual_bit_decoder':{'valid':valid,'semantic':(raw>>60)&15,'direction':direction,'payload':payload,'representation_bias':numeric['representation_bias'],'numeric_result':manual},
  'literal_decoder_matches_record':True,'Native_inputs':{'unique_requested':176,'status_counts':dict(counts)},
  'nonzero_raw_input_requests':nonzero,'recorded_C_frames':[{ 'tick':f['tick'],'raw':f['fields']['C']['raw'],'s_reg':f['fields']['C']['s_reg']}for f in trial['frames']],
  'before':trial['before'],'after':trial['after'],'direct_numeric_layer_same_lived_adapter':arithmetic['same_lived_adapter'],
  'provider_called':arithmetic['provider_called'],'R04_route_consulted':arithmetic['R04_route_consulted']})
result={'schema':'DEE.PI08.B.numeric_panel_passive_autopsy.R01','Native_executed':False,'DEE_imported':False,'source_modified':False,
 'sources':[ref(S/x)for x in('capacidades/aritmetica_directa_eci02.py','capacidades/aritmetica_apd_01.py','capacidades/percepcion_cruda_fi01.py','capacidades/pi04_coordinacion_central_C2C.py','app/mundo_genesis_apd05.py')],
 'observed':rows,'findings':[
 'The direct external API and internal C2C both call the identical arithmetic_api.execute/native_pair/raw.frame on the same lived adapter; no alternative numeric provider or reader is selected.',
 'Numeric decoding uses C=(12,17,18), direction(1,-1,-1), SEM1 at q+1/datum-2. This is distinct from regulated FI q4 and the downstream q6 six-class motor reader.',
 'SUM6+7 physically emits valid payload7 at this numeric gate. Both the unchanged literal decoder and independent uint64 bit extraction return7; this is not a report/word/parser substitution.',
 'DIF uses the actual returned7 as its left input and independently encodes(7,27); Native Cpayload34 minus fixed bias32 yields2. It is the correct subtraction of the actual transported upstream7, while failing the inherited13-to8 functional chain criterion.',
 'Internal C2C31 independently encodes(8,7) and the same Cgate emits valid15. The different operands and different query phases prevent treating it as a matched arithmetic trial.',
 'All176 events were Applied in each arithmetic call; admission alone does not certify subsequent aggregation/transport. The earliest preserved failing physical witness is C(q+1).',
 'All three calendar waits are0, but absolute phases differ. The regulated outer FI access does not redirect the explicit arithmetic API or the internal C2C arithmetic call.'],
 'unresolved':['No complete global trajectory was captured inside this failing numeric call. Loss or interference before C is not isolated; the fact that7 equals the right operand does not prove lineage or uniquely locate a lost left carrier.','The existing None continuation can supply a prospective matched nominal panel after complete paired preservation. No result of that future control is assumed.'],
 'B_conservation_gate_remains_false':True,'parent_A_unchanged_by_this_analysis':True}
with OUT.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(OUT),'sha256':sha(OUT),'manual_and_literal_decoders_match':True,'Native_executed':False}))
