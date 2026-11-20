"""Only prospective Max2->Max3 configuration/binding delta. No Native/Studio/HTTP."""
from pathlib import Path
import argparse,copy,json,re,xml.etree.ElementTree as E

def scripts(p):
 out={}
 for i in E.parse(p).getroot().iter('Item'):
  props=i.find('Properties')
  if props is None:continue
  n=props.find("string[@name='Name']");s=props.find("ProtectedString[@name='Source']")
  if n is not None and s is not None:out[n.text]=s.text or ''
 return out

def run(stage):
 kit=stage/'PAQUETE_CANDIDATO/KIT_DESARROLLADOR';archive=stage/'ANTES_HORIZONTE_MAX2';checks=[]
 def check(n,v):assert v,n;checks.append({'name':n,'passed':True})
 old=json.loads((archive/'CONFIGURACION_PUBLICA.json').read_text(encoding='utf8'));new=json.loads((kit/'configuracion/CONFIGURACION_PUBLICA.json').read_text(encoding='utf8'))
 check('prospective3_6_runs1',new['MaxOpportunities']==3 and new['MaxActions']==6 and new['RunCycles']==1 and new['PersistenceBinding']['maxOpportunities']==3 and new['PersistenceBinding']['maxActions']==6)
 reverted=copy.deepcopy(new)
 for k in ('MaxOpportunities','MaxActions','ScenarioFingerprint'):reverted[k]=old[k]
 for k in ('maxOpportunities','maxActions'):reverted['PersistenceBinding'][k]=old['PersistenceBinding'][k]
 check('no_other_configuration_change',reverted==old and new['ScenarioFingerprint']!=old['ScenarioFingerprint'])
 source=(kit/'configuracion/SDKConfig.luau').read_text(encoding='utf8')
 check('lua_config_matches_json',json.loads(re.search(r'\[=\[(.*?)\]=\]',source,re.S).group(1))==new)
 for rel in ('conector/DEEConnector_SDK_0_1_1.rbxmx','ejemplos/DEE_SDK_PILOTO_0_1_1.rbxlx'):
  before=scripts(archive/Path(rel).name);after=scripts(kit/rel)
  check('only_Config_module_changed_'+Path(rel).name,set(before)==set(after)and all(after[k]==v for k,v in before.items()if k!='SDKConfig')and after['SDKConfig']==source)
 c0=json.loads((archive/'CONTRATO_K4_R06.json').read_text(encoding='utf8'));c1=json.loads((kit/'guias/CONTRATO_K4_R06.json').read_text(encoding='utf8'))
 c1.pop('prospectiveHorizon');c1['bindings']=[x.replace('MaxOpportunities3','MaxOpportunities2').replace('MaxActions6','MaxActions4')for x in c1['bindings']]
 check('K4_criterion_unchanged_except_horizon',c0==c1)
 return{'schema':'DEE.SDK.Max3Delta.R06','NativeExecuted':False,'StudioExecuted':False,'HttpRequested':False,'base22ChecksNotRepeated':True,'checks':checks,'passed':True}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=run(Path(__file__).resolve().parent)
 with a.output.open('x',encoding='utf8')as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'passed':True,'checks':len(r['checks']),'NativeExecuted':False}))
