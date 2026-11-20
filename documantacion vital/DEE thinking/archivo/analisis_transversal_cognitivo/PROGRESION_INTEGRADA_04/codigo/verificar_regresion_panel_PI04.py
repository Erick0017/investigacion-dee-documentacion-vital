"""Passive PI04 gate witness, six executed primaries; does not run DEE."""
from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def info(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def walk(x):
 if isinstance(x,dict):
  if 'id'in x and 'status'in x and 'kind'in x:yield x
  for v in x.values():yield from walk(v)
 elif isinstance(x,list):
  for v in x:yield from walk(v)
def main():
 rows=[];allids={};last=817583
 for name,expected in [('luma',1),('nara',-1),('clasifica',-1),('suma',1),('alfa',-1),('FIplus',1)]:
  p=P/'ensayos'/('PI04_MAIN_PANEL12_OP2_'+name+'.json');j=read(p)
  assert j['status']=='completed';r=json.loads(j['result']);assert r['before_tick']==last;last=r['after_tick']
  row=r['result']['rows'][0]
  if name=='alfa':row=row['result']['rows'][0]
  actual=row['early_physical_choice']if name=='FIplus'else row['reader']['formed_native_command']
  rs={}
  for q in walk(r['result']):
   key=int(q['id']);assert key not in rs or rs[key]==q;rs[key]=q
  assert all(q['status']=='applied'for q in rs.values())
  assert not(set(rs)&set(allids));allids.update(rs)
  rows.append({'name':name,'expected':expected,'actual':actual,'correct':actual==expected,'before_tick':r['before_tick'],'after_tick':r['after_tick'],'unique_Native_inputs':len(rs),'primary':info(p)})
 assert last==818074 and sum(x['correct']for x in rows)==5 and len(rows)==6 and rows[-1]['actual']==-1 and rows[-1]['unique_Native_inputs']==176
 export=P/'control/EXPORTACION_ESTABLE_PI03_PI04_C2C_CONSERVACION_FALLIDA_T818074.json';e=read(export)
 assert e['tick']==818074 and e['manifest_sha256']=='38f038262fd00bbae49033b645202bc81f77a6a0ab309603fcfc3c5076a509d2'
 out={'schema':'DEE.PI04.conservation_regression.passive_verified.v1','Native_execution_by_this_verifier':False,'new_Native_ticks':0,'life_id':'ECI02_PI03_REPRO_PI04_MAIN_02','before_tick':817583,'after_tick':818074,'planned_panel':12,'executed':6,'correct':5,'unexecuted':6,'complete_panel':False,'gate':'BLOCKED_MATERIAL_REGRESSION','rows':rows,'unique_Native_inputs':len(allids),'all_applied':True,'stable_full_pair':info(export),'interpretation':'FIplus comparison changed to -1 rather than expected +1. No unique cause or erasure established. Six unexecuted witnesses are not failures. No adoption.'}
 target=P/'control/CONSERVACION_REGRESION_PI04_VERIFICADA.json'
 if target.exists():assert read(target)==out
 else:target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'output':info(target),'executed':6,'correct':5,'inputs':len(allids)},ensure_ascii=False))
if __name__=='__main__':main()
