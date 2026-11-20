"""Pure clean-extraction verification for the PI04 analysis package.
Stdlib only. Does not import DEE, advance worlds, reproduce Native or read
absolute source/path locators recorded by scientific evidence.
"""
from pathlib import Path,PurePosixPath
import argparse,csv,hashlib,io,json,subprocess,sys,zipfile,xml.etree.ElementTree as ET
VERSION='DEE.PI04.analysis_clean_recalculation.v1'
def need(x,s):
 if not x:raise ValueError(s)
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def safe(root,name):
 need(isinstance(name,str)and'\\'not in name and'\x00'not in name,'Invalid manifest path')
 p=PurePosixPath(name);need(not p.is_absolute()and'..'not in p.parts and':'not in name,'Unsafe manifest path')
 q=(root/Path(*p.parts)).resolve(strict=True);need(q.is_relative_to(root),'Manifest escape');return q
def digest(b):return hashlib.sha256(b).hexdigest()
CHILD_FENCE = r"""
import sys,os,json,runpy
cfg=json.loads(sys.argv[1]);argv=cfg['argv'];sys.argv=argv
allowed=[os.path.normcase(os.path.realpath(p))for p in(cfg['root'],cfg['destination'],sys.base_prefix)]
root,destination,stdlib=allowed
audit={'schema':'DEE.PI04.recalculation.child_access_fence.v1','root':cfg['root'],'destination':cfg['destination'],'Native_ticks':0,'DEE_or_app_imports':0,'denied':[],'opens_inside_extraction':0,'opens_inside_destination':0,'opens_inside_stdlib':0,'external_source_locator_opened':False}
def inside(path,base):
 try:return os.path.commonpath([path,base])==base
 except ValueError:return False
def refuse(kind,value):
 audit['denied'].append({'kind':kind,'value':str(value)[:500]});raise PermissionError('PI04 pure-child access fence: '+kind)
def hook(event,args):
 if event=='import':
  name=str(args[0]).lower()
  if name=='app'or name.startswith('app.')or name.startswith('dee_'):
   audit['DEE_or_app_imports']+=1;refuse('DEE/app import',name)
 if event=='open'and args and not isinstance(args[0],int):
  name=os.path.normcase(os.path.realpath(os.fspath(args[0])));mode=args[1]if len(args)>1 else None;flags=args[2]if len(args)>2 else 0
  write=(isinstance(mode,str)and any(x in mode for x in('w','a','x','+')))or(isinstance(flags,int)and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
  if inside(name,destination):audit['opens_inside_destination']+=1
  elif inside(name,root):
   if write:refuse('write to extraction',name)
   audit['opens_inside_extraction']+=1
  elif inside(name,stdlib):
   if write:refuse('write to runtime',name)
   audit['opens_inside_stdlib']+=1
  else:
   audit['external_source_locator_opened']=True;refuse('open outside extraction/destination/runtime',name)
 if event.startswith('socket.')or event in('subprocess.Popen','os.system','os.exec','os.spawn','ctypes.dlopen'):refuse('network/process/native-loader event',event)
sys.addaudithook(hook)
try:runpy.run_path(argv[0],run_name='__main__')
finally:
 with open(cfg['audit'],'x',encoding='utf8')as h:json.dump(audit,h,ensure_ascii=False,indent=2)
"""
def run(root,argv,target):
 config={'root':str(root),'destination':str(target.parent.resolve()),'argv':list(map(str,argv)),'audit':str(target.with_suffix('.AUDIT.json'))}
 r=subprocess.run([sys.executable,'-I','-B','-X','utf8','-c',CHILD_FENCE,json.dumps(config,ensure_ascii=False)],cwd=root,capture_output=True,encoding='utf8',errors='strict',timeout=120)
 target.with_suffix('.stdout.txt').write_text(r.stdout,encoding='utf8');target.with_suffix('.stderr.txt').write_text(r.stderr,encoding='utf8')
 need(r.returncode==0,'Pure recalculation failed: '+str(argv[0])+' '+r.stderr[-1800:])
 audit=load(target.with_suffix('.AUDIT.json'));need(not audit['denied']and audit['DEE_or_app_imports']==0 and audit['external_source_locator_opened']is False,'Child accessed undeclared source or imported DEE/app')
 return r

def main(a):
 root=a.raiz.resolve(strict=True);dest=a.destino.resolve();need(not dest.exists(),'Fresh non-existent output directory required');need(not dest.is_relative_to(root),'Output must be separate from the extracted evidence')
 m=load(root/'05_CONTROL/MANIFIESTO_SHA256.json');entries=m.get('content');need(isinstance(entries,list)and entries,'Global content manifest required; source locators are never opened')
 checked=[];seen=set()
 for row in entries:
  n=row['file'];need(n not in seen,'Duplicate manifest path');seen.add(n);p=safe(root,n);b=p.read_bytes();need(len(b)==row['bytes']and digest(b)==row['sha256'],'Content mismatch: '+n)
  ext=p.suffix.lower()
  if ext=='.json':json.loads(b.decode('utf-8-sig'))
  elif ext in('.csv','.tsv'):list(csv.reader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t'if ext=='.tsv'else','))
  elif ext in('.md','.txt','.py','.srt','.jsonl'):b.decode('utf-8-sig')
  checked.append(n)
 manuals=[safe(root,n)for n in seen if n.startswith('02_MANUAL/')and n.endswith('.docx')and'DCS11_MM_001'in n];need(len(manuals)==1,'Exactly one complete Cognitive Manual required')
 with zipfile.ZipFile(manuals[0])as z:
  need(z.testzip()is None,'Manual CRC failed');core=ET.fromstring(z.read('docProps/core.xml'));values=[x.text for x in core if x.tag.endswith('}version')];need('1.31'in values,'Manual actual internal edition must be1.31')
  for n in z.namelist():
   if n.endswith('.xml')or n.endswith('.rels'):ET.fromstring(z.read(n))
 # Every child program is a preserved pure recalculator; never execute actor/protocol code.
 dest.mkdir(parents=True)
 f1=root/'04_EVIDENCIAS/F1';r=run(root,[f1/'RECALCULAR_F1.py'],dest/'F1');f1result=json.loads(r.stdout);need(f1result==load(f1/'RESULTADO_CONTRASTADO.json'),'F1 recorded contrast differs')
 e3=root/'04_EVIDENCIAS/E3';run(root,[e3/'RECALCULAR_E3.py','--evidence',e3,'--out',dest/'E3'],dest/'E3_run');e3result=load(dest/'E3/RECALCULO_E3.json');co=e3result['comparison'];need(co['real_products']==14 and co['permuted_products']==18 and co['actual_control_effect_return_mismatches']==4,'E3 decisive actual values differ')
 c2=root/'04_EVIDENCIAS/C2C';run(root,[c2/'RECALCULAR_C2C_R01.py','recalculate','--evidence',c2,'--out',dest/'C2C'],dest/'C2C_run');c2result=load(dest/'C2C/RECALCULO_C2C.json');need((dest/'C2C/RECALCULO_C2C.json').read_bytes()==(c2/'RECALCULO_C2C.json').read_bytes(),'C2C archived and recalculated report differ')
 arms=c2result['arms'];need({k:(v['included'],v['products'],v['Native_inputs_unique'])for k,v in arms.items()}=={'real':(20,19,3720),'none':(20,12,3720),'yoked':(20,20,3720)},'C2C actual histories differ')
 closure=root/'04_EVIDENCIAS/CIERRE';decision=load(closure/'DECISION_NO_ADOPCION_PI04.json');need(decision['adoption_performed']is False and decision['principal']['life_id']=='ECI02_PI03_MAIN'and decision['principal']['tick']==775355,'Protected main/no-adoption differs')
 panel=load(closure/'CONSERVACION_REGRESION_PI04_VERIFICADA.json');need(panel['executed']==6 and panel['correct']==5 and panel['planned_panel']==12 and panel['gate']=='BLOCKED_MATERIAL_REGRESSION'and panel['after_tick']==818074,'Panel regression gate differs')
 cold=load(closure/'C2C_COLD20_NATIVE_VERIFICADA_R01.json');need(cold['status']=='NATIVE_REPLAY_VERIFIED'and cold['Native_executed']is True and cold['closed']is True and cold['products']==19 and cold['reserved_products']==8 and cold['Native_inputs_applied']==3720,'Recorded actual cold replay differs')
 facts=load(closure/'CIERRE_CIENTIFICO_PI04.json');need(facts['closed_for_authoring']is True and facts['principal']['adoption_performed']is False and facts['principal']['tick']==775355,'Authoring facts contradict no-adoption')
 result={'schema':VERSION,'status':'DOCUMENTARY_RECALCULATION_VERIFIED','Native_ticks_executed':0,'DEE_modules_imported':0,'recorded_absolute_source_paths_opened':False,'child_access_fences':[p.name for p in sorted(dest.glob('*.AUDIT.json'))],'content_members_verified':len(checked),'manual_internal_edition':'1.31','manual_sha256':digest(manuals[0].read_bytes()),'F1':f1result['checks'],'E3':co,'C2C':{k:{n:v[n]for n in('included','products','Native_inputs_unique','reserve8')}for k,v in arms.items()},'selected_main':{'life_id':'ECI02_PI03_MAIN','N':67,'T':775355},'candidate_not_adopted_T':818074,'regression_panel':{'correct':5,'executed':6,'planned':12},'limits':['Manual XML/CRC and text structure are not visual rendering QA.','Recorded Native replay proof is checked, not executed again.','Full operative snapshots/interfaces/SQLite/environment stay outside this analysis ZIP.','F1 retrospective and prepared P0 sensor are not autonomous retrieval.']}
 (dest/'VERIFICACION_EXPEDIENTE_PI04.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'status':result['status'],'members':len(checked),'Native_ticks':0,'output':str(dest/'VERIFICACION_EXPEDIENTE_PI04.json')},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raiz',type=Path,required=True);p.add_argument('--destino',type=Path,required=True);main(p.parse_args())
