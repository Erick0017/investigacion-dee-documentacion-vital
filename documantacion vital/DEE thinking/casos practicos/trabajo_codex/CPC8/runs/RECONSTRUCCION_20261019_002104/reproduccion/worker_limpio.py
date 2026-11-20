"""Bounded technical worker; installed engine, candidate app, external outputs.

Native trajectories receive no expected state or target. Historical primaries
are opened only by the separate audit mode after trajectories have completed.
"""
import argparse,gc,hashlib,json,os,platform,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WHEEL='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
KERNEL='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def put(path,value):
 path=Path(path)
 if path.exists():raise FileExistsError('Protected existing report: '+str(path))
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def identity():
 import dee_thinking as dee
 from dee_thinking import _native as d
 wheel=ROOT/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl';kernel=ROOT/'genealogia/product45/kernel_v27.cpp'
 value={'python':sys.executable,'CPython':platform.python_implementation(),'python_version':platform.python_version(),'pointer_bits':struct.calcsize('P')*8,'isolated':bool(sys.flags.isolated),'ignore_environment':bool(sys.flags.ignore_environment),'no_bytecode':bool(sys.dont_write_bytecode),'PYTHONPATH_env_present':bool(os.environ.get('PYTHONPATH')),'PYTHONPATH_ignored':bool(sys.flags.isolated and sys.flags.ignore_environment),'product':dee.__version__,'module':dee.__file__,'native':d.__file__,'site_packages_only':Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())and Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()),'wheel_sha256':sha(wheel),'pyd_sha256':sha(d.__file__),'kernel_source_sha256':sha(kernel),'build_info':dee.build_info(),'sys_path':sys.path}
 r=d.Runtime(8);value['direct_empty_Runtime']={'N':8,'tick':int(r.current_tick),'raw_all_zero':all(x==0 for x in r.raw_copy()),'clocks_all_zero':all(x==0 for x in r.clock_copy()),'channels_empty':not r.channel_names};del r
 value['passed']=all((value['CPython']=='CPython',sys.version_info[:2]==(3,13),value['pointer_bits']==64,value['isolated'],value['ignore_environment'],value['no_bytecode'],value['site_packages_only'],value['product']=='4.5.0',value['wheel_sha256']==WHEEL,value['pyd_sha256']==PYD,value['kernel_source_sha256']==KERNEL,value['direct_empty_Runtime']['raw_all_zero'],value['direct_empty_Runtime']['clocks_all_zero'],value['direct_empty_Runtime']['channels_empty']))
 return value
def restore(snapshot,out,profile='integrada'):
 sys.path.insert(0,str(ROOT));from app.experimento import Experiment
 app=Experiment(out)
 try:
  if profile=='magnitud_social':
   events=({'op':'cargar','archivo':str(snapshot),'perfil':profile},{'op':'guardar','archivo':'RESTORED_MAGNITUD_T73.deetsnap.gz'},{'op':'avanzar','t':80},{'op':'avanzar','t':147},{'op':'avanzar','t':214},{'op':'avanzar','t':281},{'op':'avanzar','t':549},{'op':'guardar','archivo':'RESTORED_MAGNITUD_T549.deetsnap.gz'},{'op':'avanzar','t':554},{'op':'avanzar','t':559},{'op':'avanzar','t':563},{'op':'avanzar','t':616},{'op':'guardar','archivo':'RESTORED_MAGNITUD_T616.deetsnap.gz'})
  elif profile=='contacto_social':
   events=({'op':'cargar','archivo':str(snapshot),'perfil':profile},{'op':'guardar','archivo':'RESTORED_CONTACTO_T549.deetsnap.gz'},{'op':'avanzar','t':554},{'op':'avanzar','t':559},{'op':'avanzar','t':563},{'op':'avanzar','t':616},{'op':'guardar','archivo':'RESTORED_CONTACTO_T616.deetsnap.gz'})
  else:events=({'op':'cargar','archivo':str(snapshot),'perfil':'integrada'},{'op':'avanzar','t':549},{'op':'guardar','archivo':'RESTORED_T549.deetsnap.gz'},{'op':'consultar','relacion':'compuesta','carga':13,'t':613},{'op':'avanzar','t':616},{'op':'guardar','archivo':'RESTORED_T616.deetsnap.gz'})
  for e in events:app.execute(e)
 finally:app.close()
def collect(snapshot):
 sys.path.insert(0,str(ROOT/'src'))
 from integracion.initiative_use_e1 import InitiativeUseE1Session
 from integracion.relational_pair import physical
 from dee_thinking.consolidated import exact_observation
 s=InitiativeUseE1Session.load(snapshot)
 if s.geometry.get('finite_protocol')=='CPC8R.contactSocialE1.counterflow1.0_to616.v1':
  from comunicacion.contact_social_regulated import RegulatedContactSocialE1Session
  s=RegulatedContactSocialE1Session(s.world,s.geometry,s.state,s.identifier)
 elif s.geometry.get('finite_protocol')=='CPC8R.magnitudeCTS.0_to616.v1':
  from transferencia_magnitud.cts_integrado import MagnitudeCTSSession
  s=MagnitudeCTSSession(s.world,s.geometry,s.state,s.identifier)
 requests=sorted(s.receipts(),key=lambda r:r['id']);rt=s.world.runtime
 protocols=[{'id':p.id,'kind':p.kind,'modality':str(p.modality),'next_capture':p.next_capture,'steps':[{'input_tick':x.input_tick,'read_tick':x.read_tick,'input':x.input,'receipt_ids':x.receipt_ids,'targets':[[q.x,q.y,q.z]for q in x.targets],'captured':[exact_observation(o)for o in x.captured]}for x in p.steps]}for p in s.world.protocols]
 inputs=[{'id':r['id'],'port':r['port'],'payload':r.get('payload',r.get('load')),'requested_tick':r['receipt']['requested_tick'],'kind':r['receipt']['kind']}for r in requests]
 value={'physical':physical(s.world),'operative':{'channels':sorted(rt.channel_names),'protocol_phase':rt.protocol_phase,'paused':rt.paused,'organization_ids':s.world.organization_ids,'protocols':protocols,'native_receipts':[r['receipt']for r in requests],'submitted_inputs':inputs},'current_view':s.view()};del s;gc.collect();return value
def audit(out):
 base=ROOT/'resultados/integracion';positive=json.loads((base/'IUE_P01_RETURN_USED_PLUS/MEASUREMENTS.json').read_text(encoding='utf8'));control=json.loads((base/'IUE_C01_NO_QUALIFIED_QUESTION/MEASUREMENTS.json').read_text(encoding='utf8'));continued=json.loads((base/'IUE_T11_RESTORE_PLUS_NEW_QUERY/MEASUREMENTS.json').read_text(encoding='utf8'));rows=[]
 def native_case(label,path,primary):
  result=collect(path);expected={'physical':primary['final_physical'],'native_receipts':[r['receipt']for r in sorted(primary['requests'],key=lambda r:r['id'])]};row={'name':label,'actual':result['physical'],'expected':expected['physical'],'full_RAW_clocks_tick_equal':result['physical']==expected['physical'],'native_receipts_equal':result['operative']['native_receipts']==expected['native_receipts']};rows.append(row);return result
 p549=native_case('public_app549_vs_frozen_science',out/'demo_integrada/E1_T549.deetsnap.gz',positive)
 p616=native_case('public_app616_vs_frozen_science',out/'demo_integrada/E1_T616.deetsnap.gz',continued)
 c549=native_case('public_negative_history_control549_vs_frozen_science',out/'demo_control/E1_T549.deetsnap.gz',control)
 r549=collect(out/'restore_process/RESTORED_T549.deetsnap.gz');r616=collect(out/'restore_process/RESTORED_T616.deetsnap.gz')
 for label,a,b in(('separate_process549',r549,p549),('separate_process_new_query616',r616,p616),('public86_vs_scientific86',collect(out/'demo_integrada/E1_T86.deetsnap.gz'),collect(base/'IUE_P01_RETURN_USED_PLUS/EXTRA_T86.deetsnap.gz'))):rows.append({'name':label,'actual':a['physical'],'expected':b['physical'],'full_RAW_clocks_tick_equal':a['physical']==b['physical'],'operative_equal':a['operative']==b['operative']})
 def qualified(physical):return physical['active']and physical['semantic']==1 and physical['direction']==[0,0,-1]and physical['s_reg']>13
 def metric_app(directory):
  records=[json.loads(x)for x in(directory/'OBSERVACIONES.jsonl').read_text(encoding='utf8').splitlines()];frames=[x['contenido']for x in records if x['origen']=='ENTE'];frame=next(x for x in frames if x['tick']==89);return{'count':sum(qualified(x['contact'])for x in frame['uso_fisico_del_retorno_actual']),'passive_views':all(x['observacion_pasiva_comprobada']for x in frames),'explicit_errors':[x for x in records if x['contenido'].get('estado')in('ERROR_EXPLICITO','RECHAZO_EXPLICITO')]}
 def metric_primary(m):return sum(qualified(x['contact'])for x in next(r for r in m['return_use_observations']if r['tick']==89)['receivers'])
 metric={'formula':'count active semantic1, direction(0,0,-1), s_reg>13 over the two fixed recipients at89; wrong-vector56 and resources13 do not qualify','positive_app':metric_app(out/'demo_integrada'),'positive_primary_count':metric_primary(positive),'control_app':metric_app(out/'demo_control'),'control_primary_count':metric_primary(control)}
 metric['recalculated_matches']=metric['positive_app']['count']==metric['positive_primary_count']and metric['control_app']['count']==metric['control_primary_count']
 result={'schema':'CPC8R.clean.audit.v1','comparison_mode':'Historical physical references and current observations opened only AFTER all trajectories completed; never passed to participants. Metadata origins/identifiers can differ; native operational fields and exact submitted payloads compared separately.','comparisons':rows,'metric':metric,'primary_hashes':{str(p.relative_to(ROOT)):sha(p)for p in(base/'IUE_P01_RETURN_USED_PLUS/MEASUREMENTS.json',base/'IUE_C01_NO_QUALIFIED_QUESTION/MEASUREMENTS.json',base/'IUE_T11_RESTORE_PLUS_NEW_QUERY/MEASUREMENTS.json')},'passed':all(r['full_RAW_clocks_tick_equal']and r.get('native_receipts_equal',True)and r.get('operative_equal',True)for r in rows)and metric['recalculated_matches']and metric['positive_app']['passive_views']and metric['control_app']['passive_views']and not metric['positive_app']['explicit_errors']and not metric['control_app']['explicit_errors']}
 return result
def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='mode',required=True);i=sub.add_parser('identidad');i.add_argument('--report',type=Path,required=True);r=sub.add_parser('restaurar');r.add_argument('--snapshot',type=Path,required=True);r.add_argument('--out',type=Path,required=True);r.add_argument('--profile',choices=('integrada','contacto_social','magnitud_social'),default='integrada');a=sub.add_parser('auditar');a.add_argument('--out',type=Path,required=True);a.add_argument('--report',type=Path,required=True);args=p.parse_args()
 if args.mode=='restaurar':restore(args.snapshot.resolve(),args.out.resolve(),args.profile);return
 result=identity()if args.mode=='identidad'else audit(args.out.resolve());put(args.report,result);print(json.dumps({'mode':args.mode,'passed':result['passed']}))
 if not result['passed']:raise SystemExit(1)
if __name__=='__main__':main()
