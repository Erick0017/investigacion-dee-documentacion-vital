"""Extracción audiovisual R03. Sólo bytes históricos; nunca importa DEE."""
from pathlib import Path
import json,gzip,hashlib,importlib.util,datetime
W=Path(__file__).resolve().parent
ROOT=next(p for p in W.parents if p.name=='DEE thinking')
OLD=ROOT/'archivo/DEE Cognitive System 1.1'
sources=[]
def load(p,id,pointer):
 p=Path(p);b=p.read_bytes();sha=hashlib.sha256(b).hexdigest()
 sources.append(dict(id=id,path=str(p),sha256=sha,bytes=len(b),pointer=pointer))
 if p.suffix=='.gz':b=gzip.decompress(b)
 return json.loads(b.decode('utf-8-sig'))
def obs(v):return {k:v[k]for k in('tick','site','raw','clock','state','s_reg','semantic','direction')if k in v}
def aa_extract():
 base=OLD/'evidencia/campanas/ACCESO_ADAPTATIVO_01'
 paired={}; controls={}
 for sign in('plus','minus'):
  d=load(base/'USO_INMEDIATO_RECUPERADO_46'/sign/'PRIMARIOS.json.gz','AA46_'+sign,'/stages;/historical_source_read;/later_content_teacher_inputs')
  assert d['later_content_teacher_inputs']==[] and d['old_code_reintroduced_after_first_block'] is False
  stages=[]
  for s in d['stages']:
   a=s['answer'];stages.append(dict(block=s['block'],stage=s['stage'],tick=a['INSTRUMENTO']['tick'],content_codes=a['CONTENT_CODES'],recipient_mode=a['INSTRUMENTO']['recipient_mode'],fields={k:{kk:obs(vv)for kk,vv in v.items()}if k in('B','memories')else obs(v)for k,v in a['ENTE'].items()}))
  paired[sign]=dict(life=d['life'],N=d['pre']['N'],pre=d['pre'],post=d['post'],initial_external_content=d['initial_external_content'],prepared_redundancy=d['prepared_redundancy'],historical_source_read=d['historical_source_read'],design=d['design_before'],later_content_teacher_inputs=[],old_code_reintroduced=False,stages=stages,access_curriculum=dict(epoch=d['second_preparation']['INSTRUMENTO']['epoch'],end_tick=d['second_preparation']['INSTRUMENTO']['end_tick']))
  for suffix in('no_access_teaching','no_backup','cut_backup','sham_backup'):
   name=sign+'_'+suffix;dd=load(base/'CONTROLES_USO_INMEDIATO_47'/name/'PRIMARIOS.json.gz','AA47_'+name,'/stages;/later_content_teacher_inputs')
   controls[name]=dict(life=dd['life'],late_content_teacher_inputs=dd['later_content_teacher_inputs'],stages=[dict(stage=s['stage'],tick=s['answer']['INSTRUMENTO']['tick'],codes=s['answer']['CONTENT_CODES'])for s in dd['stages']if s['block']=='access_without_content_reteaching'])
 return dict(paired=paired,controls=controls,scope='Dos soportes adquiridos inicialmente; nuevo acceso enseñado, no reconstrucción del mismo soporte perdido ni reparación iniciada autónomamente. Vista parcial de registros, no trayectoria microscópica íntegra.')
def u0_extract():
 base=ROOT/'4.5/DEE_thinking_4_5_0/validation/cpc_ports_4_5_final6'
 out={}
 for name in('IR_P01_GUARDED_M1','IR_MATCH_CURRENT'):
  config=load(base/name/'CONFIG.json','U0_'+name+'_config','/geometry/ticks;/geometry/sites;/case')
  d=load(base/name/'RESULT.json','U0_'+name+'_result','/frames;/calls')
  out[name]=dict(identity=name,N=67,case=config['case'],geometry=config['geometry'],frames=[dict(tick=f['tick'],body=f['body'],questions=f['questions'],own_banks=f['own_banks'],actions=f['actions'])for f in d['frames']if f['tick']in('3','5','11','15','19','70','72')],calls=[c for c in d['calls']if c['port'].startswith(('event.','need.actual.','own.use.'))])
 return dict(cases=out,scope='Previsión condicionada por historia AB, comparación y solicitud con oportunidades preparadas; otra realización distinta de DEE20 y APD03. Se observan fronteras discretas; no se inventa el trayecto entre ellas.')
def ciclo_extract():
 base=OLD/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
 out={}
 for name in('C02_GATE_050_RETORNO','C02_GATE_051_SIN_RETORNO','C02_GATE_052_ACCION_ANULADA','C02_GATE_053_SHAM'):
  d=load(base/(name+'.json'),name,'/data/result/rows')
  result=d['data']['result']
  out[name]=dict(life=d['life'],mode=result['mode'],rows=[{k:x[k]for k in('index','tick','force_sensor','wear_available','native_pre','native_response','valid','native_action','executed_action','environment','utility_auditor_only','useful_auditor_only','return_input_tick','host_does_not_return_utility_or_resistance')}for x in result['rows']])
 return dict(cases=out,actuator='Native -X7=attempt/+1; +X7=retreat/-1; otros=neutral. +1 abre sólo si fuerza supera resistencia actual; intento causa desgaste, retirada no. Codec fijo devuelve desgaste, no utilidad/acción correcta.',scope='Referencia escalar adquirida utilizada por comparador y actuador preparados; no política general de control.')
def aggregate_extract():
 base=OLD/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/escalamiento'
 pair={}
 for name in('ref_sham_zero','ref_sham_two'):
  d=load(base/'B05_CONTROLS_R3_N128'/(name+'.json.gz'),'B05_'+name,'/result/geometry;/result/raw_components;/result/frames;/result/reader')
  z=d['result'];pair[name]=dict(life=d['INSTRUMENTO']['life_id'],initial=z['initial'],raw_components=z['raw_components'],geometry=z['geometry'],frames=z['frames'],reader=z['reader'],leaf_tick=z['leaf_tick'],native_datum_tick=z['native_datum_tick'],fixed_reader_tick=z['fixed_reader_tick'])
 a,b=pair.values()
 assert a['initial']==b['initial']
 assert a['raw_components']==[0]*128 and b['raw_components']==[2]+[0]*127
 assert a['reader']['choice']==-1 and b['reader']['choice']==1
 rv=base/'B05_RELEVANCE_R2_N128_0_128'
 summary=load(rv/'RESUMEN.json','B05_relevance_summary','/arms')
 arms=[]
 for i in range(128):
  name='component_%03d.json.gz'%i;p=rv/name;raw=p.read_bytes();d=json.loads(gzip.decompress(raw));z=d['result']
  listed=next(a for a in summary['arms']if a['label']=='component_%03d'%i)
  sh=hashlib.sha256(raw).hexdigest();assert sh==listed['output_sha256']
  vec=z['raw_components'];assert len(vec)==128 and vec[i]==2 and sum(v!=0 for v in vec)==1
  datum=next(f['fields']['D']for f in z['frames']if f['tick']==z['native_datum_tick'])
  assert datum['s_reg']==2 and z['reader']['choice']==1
  arms.append(dict(component_index=i,original=str(p),sha256=sh,life=d['INSTRUMENTO']['life_id'],native_datum_tick=z['native_datum_tick'],datum=obs(datum),reader_tick=z['reader']['tick'],reader_choice=z['reader']['choice'],requested=listed['requested'],applied=listed['applied']))
 return dict(pair=pair,relevance=arms,counts=dict(input_components=128,prepared_zero_resources=45,merger_nodes=42,component_cases=128,held_out=126,technical_repetitions=2),scope='Preparación física de agregación y lector. 128 componentes no son 128 conocimientos. Estados de sitios muestreados con clocks exactos; sin identidad única de portador interpolada entre encuentros. Geometría en metadatos conserva la etiqueta del constructor OFFLINE_PLAN, pero los resultados son ejecuciones históricas ya registradas. Integridad del RESUMEN: parent_record_unchanged=false, parent_snapshot_unchanged=true, active_unchanged=true; no declarar prueba global de integridad del corpus.')
def apd03_extract():
 p=W.parent/'R02_memoria_plasticidad/evidencia_apd03.py'
 spec=importlib.util.spec_from_file_location('evidencia_apd03_lectura',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 d=m.extract();sources.extend(d['sources'])
 return d
def main():
 out=dict(schema='DEE.R03.visual_sources.amplitud.v1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_native_ticks=0,native_imported=False,aa46=aa_extract(),u0=u0_extract(),ciclo02=ciclo_extract(),aggregate128=aggregate_extract(),apd03=apd03_extract(),sources=sources)
 p=W/'fuentes_extraidas/amplitud.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(dict(output=str(p),bytes=p.stat().st_size,sources=len(sources),new_native_ticks=0),ensure_ascii=False))
if __name__=='__main__':main()
