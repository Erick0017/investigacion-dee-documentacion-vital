"""Bounded paired raw-context sensitivity in pinned complete AUX worlds; no task solver."""
import argparse,gc,gzip,hashlib,importlib.util,json,shutil,sys,time
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def emit(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
 with p.open('xb')as f:f.write(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
 if args.out.exists():raise FileExistsError('Fresh experiment only')
 args.out.mkdir(parents=True);sys.path.insert(0,str(args.system.resolve()))
 from app.lives import load_adapter
 from app.native_tools import physical
 from app.process_control import protect_current,current_resources
 from capacidades import selector_acrecion_nativo as sel
 protect_current(output=args.out/'RECURSOS.json',memory_limit=512*1024*1024)
 here=Path(__file__).parent;source=here.parent/'traza_retorno_demorado_r04.py';protocol=here/'PROTOCOLO_SENSIBILIDAD_R01.json';proto=json.loads(protocol.read_bytes());snapshot=args.system/proto['snapshot']
 if sha(source)!=proto['route_module_sha256']or sha(snapshot)!=proto['snapshot_sha256']:raise ValueError('Pinned full parent or mechanism source changed')
 spec=importlib.util.spec_from_file_location('APD02_CONTEXT_PARENT_R04',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 sources=[]
 for i,file in enumerate((Path(__file__),protocol,source,Path(sel.__file__),args.system/'app/lives.py',args.system/'app/process_control.py')):
  dst=args.out/'CODIGO_EJECUTADO'/(str(i).zfill(2)+'_'+file.name);dst.parent.mkdir(exist_ok=True);shutil.copyfile(file,dst);sources.append({'source':str(file),'file':dst.relative_to(args.out).as_posix(),'bytes':dst.stat().st_size,'sha256':sha(dst)})
 emit(args.out/'ANTES_DEL_PRIMER_TICK.json',{'protocol':proto,'sources':sources,'source_snapshot_sha256':sha(snapshot),'native_not_yet_started':True,'resources':current_resources()})
 def read(a,family):
  rows=[];candidates=[]
  for x in(-1,0,1):
   for z in((0,)if family['id']=='plane'else(0,-1)):
    o=m.obs(a,m.at((2*x,2,2*z)));rows.append(o)
    if o['state']>0 and o['semantic']==1 and o['direction']==[x,1,z]:candidates.append({'choice':x,'z_class':z,'observation':o})
  return{'observations':rows,'candidates':candidates,'choice':candidates[0]['choice']if len(candidates)==1 else None,'z_class':candidates[0]['z_class']if len(candidates)==1 else None,'reader_uses_context_or_target':False,'reader_gate_count':len(rows)}
 began=time.monotonic();queries=0;families=[];plane_link_failed=False
 for family in proto['families']:
  if family['id']=='above'and not plane_link_failed:break
  outcomes=[]
  for arm,sequence in enumerate(proto['arm_context_sequences']):
   if queries>=proto['maximum_material_queries']or time.monotonic()-began>=proto['budget_seconds']:outcomes.append({'arm':arm,'not_executed':'Frozen query/time budget'});break
   folder=args.out/family['id']/('ARM'+str(arm));folder.mkdir(parents=True)
   a=load_adapter('fisica_directa',snapshot)
   try:
    if a.tick!=proto['tick']:raise ValueError('No alternate parent, reset or clock edit')
    pre=m.obs(a,family['sensor_site']);a.save(folder/'ANTES_COMPLETO.deetsnap.gz')
    if int(pre['raw']):
     emit(folder/'PREFLIGHT_RECHAZADO.json',{'sensor_pre':pre,'actual_parent':physical(a.world),'reason':'Nonzero RAW is causal matter, not an available sensor slot','sensor_not_installed':True});outcomes.append({'arm':arm,'not_performed':'Initial sensor RAW nonzero','sensor_pre':pre});plane_link_failed=True;continue
    channel=proto['one_logical_context_channel'];m.declare(a,channel,family['sensor_site'],(0,0,0),1,1)
    events=[]
    for index,flag in enumerate(sequence):
     if queries>=proto['maximum_material_queries']or time.monotonic()-began>=proto['budget_seconds']:events.append({'not_executed':'Frozen query/time budget'});break
     before=physical(a.world);sensor_before=m.obs(a,family['sensor_site']);pending=m.get(a)
     if pending['pending_window']is not None:raise ValueError('Do not erase a pending native trace')
     k=(a.tick+m.DELAY+5+390)//391;k=k if k%2 else k+1;boundary=k*391;q=boundary-m.DELAY
     sensory=m.submit(a,channel,flag,q+3);resources=sel.query(a.world,q,5,m.P)
     for x in(-1,0,1):
      label=str(x);resources += [m.submit(a,m.P+'.divert.'+label,0,q+7),m.submit(a,m.P+'.flatten.'+label,0,q+9),m.submit(a,m.P+'.clear.'+label,0,boundary+10)]
     a.run_until(q-1);pre_reader=read(a,family);a.run_until(q+3);sensor_at_input=m.obs(a,family['sensor_site']);a.run_until(q+6);answer=read(a,family)
     pending['pending_window']={'query_tick':q,'boundary':boundary,'deadline':boundary-3,'generic_resource_requests':resources};pending['uses']+=1;m.save(a,pending);queries+=1
     a.save(folder/('LECTURA_'+str(index)+'_COMPLETO.deetsnap.gz'));requests=m.receipts(a,[sensory]);status=requests[0]['receipt']['status'];trace_compatible=answer['z_class']==0 and answer['choice']is not None
     cleanup=m.consequence(a,'SUCCESS',mode='omit');a.save(folder/('TRAS_LIMPIEZA_'+str(index)+'_COMPLETO.deetsnap.gz'))
     event={'index':index,'raw_missing_bit':flag,'before':before,'sensor_before':sensor_before,'query_tick':q,'boundary':boundary,'sensor_at_input':sensor_at_input,'sensory_requests':requests,'pre_reader':pre_reader,'reader':answer,'original_R04_trace_compatible':trace_compatible,'diagnostic_cleanup_no_environmental_feedback':cleanup,'sensor_after_cleanup':m.obs(a,family['sensor_site']),'after':physical(a.world)};events.append(event)
     emit(folder/('EVENTO_'+str(index)+'.json.gz'),event);print(json.dumps({'family':family['id'],'arm':arm,'index':index,'bit':flag,'sensor_status':status,'choice':answer['choice'],'z':answer['z_class'],'sensor_raw_after':event['sensor_after_cleanup']['raw'],'tick':a.tick}),flush=True)
     if status!='applied'or int(sensor_before['raw'])or int(event['sensor_after_cleanup']['raw'])or answer['choice']is None:plane_link_failed=True
    row={'arm':arm,'sequence':sequence,'events':events,'final':physical(a.world)};emit(folder/'RESULTADOS.json.gz',row);outcomes.append(row)
   finally:del a;gc.collect()
  if family['id']=='plane':
   first=[o['events'][0]['reader']['choice']for o in outcomes if o.get('events')and'reader'in o['events'][0]]
   if len(first)!=2 or first[0]==first[1]:plane_link_failed=True
  families.append({'family':family,'arms':outcomes})
 emit(args.out/'RESULTADOS.json',{'schema':'APD02.native_context_sensitivity.R01','protocol':proto,'sources':sources,'families':families,'material_queries':queries,'elapsed_seconds':time.monotonic()-began,'resources':current_resources(),'scope':proto['scope']});return 0
if __name__=='__main__':raise SystemExit(main())
