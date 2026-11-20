"""Continue the actually lived normalized reader through other native uses.

Each operation is a new manager process, not response replay. The failed
main35future is preserved; this is a separately identified exact branch.
"""
from pathlib import Path
import argparse,sys,json,subprocess
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from instrumentos_pc01 import sha,receipts
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_API43_recall';life='PC01_NORMALIZADO45';data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'commands':[],'criteria_before':'Exactfullbranchfromrealnew-processnormalizedreadercurrent40313. Interleaveoldmagnitude/spatial/contact/freefunctionswithnewnormalizedformqueries; saveandqueryagaininanotherprocess. No newwordteaching,sourcecopy,labtargetsorautonomousrouteselection. A failedreaderremainsfailed; normalizerisnotreapplied.'}
def cli(*args):
    i=len(data['commands'])+1;argv=[sys.executable,'-I','-B','-X','utf8',str(a.system/'gestionar.py'),'--system-root',str(a.system),*args];r=subprocess.run(argv,cwd=a.system,text=True,encoding='utf8',capture_output=True,timeout=300);(a.out/('CLI_'+str(i)+'.stdout.json')).write_text(r.stdout,encoding='utf8');(a.out/('CLI_'+str(i)+'.stderr.log')).write_text(r.stderr,encoding='utf8');data['commands'].append({'argv':argv,'returncode':r.returncode,'stdout_sha256':sha(a.out/('CLI_'+str(i)+'.stdout.json')),'stderr_sha256':sha(a.out/('CLI_'+str(i)+'.stderr.log'))})
    if r.returncode:raise RuntimeError('Manageroperationfailed '+r.stderr)
    return json.loads(r.stdout)
data['fork']=cli('bifurcar',parent,life,'--modalidad','CANDIDATE');_,start=s.load(life);data['pre']=physical(start.world,occupation=True);data['operations']=[]
schedule=[('espanol-contexto',{'value':64,'method':'B'}),('paisaje-contexto-dosis',{'parameter':3,'load':4}),('espanol-contacto-consultar',{'frame':'contactoA'}),('espanol-contacto-consultar',{'frame':'freeRepair5'}),('paisaje-forma-transformada',{}),('espanol-contexto',{'value':117,'method':'B'}),('paisaje-contexto-dosis',{'parameter':-3,'load':6}),('paisaje-forma-transformada',{})]
for name,options in schedule:data['operations'].append({'name':name,'parameters':options,'response':cli('experiencia','--vida',life,name,'--parametros',json.dumps(options))})
data['save']=cli('guardar','--vida',life);data['new_process_after_save']=cli('experiencia','--vida',life,'paisaje-forma-transformada','--parametros','{}');rec,end=s.load(life);data['post']=physical(end.world,occupation=True);data['receipts']=receipts(end.world.runtime);data['complete_state']=rec;data['stable_default_not_changed']=s.record('E1_SOCIAL_11')['snapshot_sha256']=='51e2ec6a41f906607848c003c6a22e3e33690f57d20dcae90c8dbbc7ab9ad396';(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'life':life,'tick':data['post']['tick'],'sequence':[r['response']['result'].get('SPANISH_DECODED',r['response']['result'].get('TRADUCCION',{}).get('SPANISH_DECODED'))for r in data['operations']],'after_save':data['new_process_after_save']['result']['SPANISH_DECODED'],'stable_protected':data['stable_default_not_changed']},ensure_ascii=False))
