"""Prepare the reused connector on another map; no SDK, Native or model calls."""
from pathlib import Path
import copy
import hashlib
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
HERE=ROOT/'prototipo/NATIVE_LIMPIO_R07'
OLD=ROOT.parent/'revision_R06_INTEGRAL_V2/prototipo'
WORLD=ROOT.parent/'revision_R06_INTEGRAL_V2/evidencia/NATIVE_CONTINUACION_C16_R01/WORLD_CHECKPOINT.json'
WORLD_SHA='48544f655382bdf97b4930200158e35371d878c29d17c1ce918077aa27cf6930'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text(p):return Path(p).read_text(encoding='utf-8-sig')
def name(e):
 p=e.find("Properties/string[@name='Name']");return p.text if p is not None else None
def sources(root):
 return{name(e):e.find("Properties/ProtectedString[@name='Source']").text for e in root.iter('Item')if e.get('class')=='ModuleScript'}
def exact(s,a,b):
 if s.count(a)!=1:raise ValueError('EXPECTED_SOURCE_ONCE:'+repr(a[:70])+':'+str(s.count(a)))
 return s.replace(a,b,1)
def write(p,data):
 if p.exists():raise ValueError('NO_OVERWRITE:'+str(p))
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(data if isinstance(data,bytes)else data.encode('utf-8'))
def main():
 scene=OLD/'NATIVE_LIMPIO_R01/DEEConnector_NATIVE_LIMPIO_R01.rbxlx'
 preserved={str(p):sha(p)for p in[scene,OLD/'exportado/DEEConnector_R06.rbxmx',OLD/'NATIVE_LIMPIO_R01/ejecutar_native_limpio_R03_preparado.py',WORLD]}
 if sha(WORLD)!=WORLD_SHA:raise ValueError('EXACT_CLOSED_PAR28_WORLD_REQUIRED')
 state=json.loads(text(WORLD));s=state['S']
 if state['native_tick']!=991187 or s['completedCycles']!=28:raise ValueError('EXACT_PAR28_CUT')
 inherited={k:s[k]for k in('permissionStock','inventoryKey','inventoryResource','numberAPresent','codeBPresent','numberAVersion')}
 inherited['codeBCurrent']=bool(s['codeBPresent'] and s.get('codeBFromAVersion')==s['numberAVersion'])
 definition={'schema':'DEE.R07.PilotOtherMap.v1','parent_native_tick':991187,'parent_world_sha256':WORLD_SHA,
  'source_sequence_offset':56,'positions':{'start':[20,3,20],'port0':[-12,3,48],'port1':[55,3,-12]},
  'obstacles':[[34,3,4,8,6,12],[0,3,35,6,6,8]],'local_panels':'both free, price1 encoding, querycost1',
  'motor':'Humanoid Pathfinding to only the chosen fixed endpoint',
  'actuator':'arrival at port0/1 sets fixed device value0/1; no resource/learning claim',
  'max_opportunities':3,'fresh_driver_opportunities':1,'inherited_public_state':inherited}
 adapter=text(ROOT/'prototipo/fuentes/LiveAdapters_R07.luau')
 motor=text(ROOT/'mundo/MotorPathfinding_R07.luau')
 definition['adapter_sha256']=hashlib.sha256(adapter.encode()).hexdigest();definition['motor_sha256']=hashlib.sha256(motor.encode()).hexdigest()
 fp=hashlib.sha256(json.dumps(definition,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 tree=ET.parse(scene);root=tree.getroot();before=sources(root)
 package=next(e for e in root.iter('Item')if name(e)=='DEEConnector_R06')
 package.find("Properties/string[@name='Name']").text='DEEConnector_R07'
 for e in list(package):
  if e.tag=='Item'and name(e)=='LiveAdapters_R01':package.remove(e)
 for module,source in [('LiveAdapters_R07',adapter),('MotorPathfinding_R07',motor)]:
  item=ET.SubElement(package,'Item',{'class':'ModuleScript','referent':'RBX_R07_PILOT_'+module})
  props=ET.SubElement(item,'Properties');ET.SubElement(props,'string',{'name':'Name'}).text=module
  ET.SubElement(props,'ProtectedString',{'name':'Source'}).text=source
 for e in root.iter('Item'):
  if e.get('class')=='Script':
   props=e.find('Properties');disabled=props.find("bool[@name='Disabled']")
   if disabled is None:disabled=ET.SubElement(props,'bool',{'name':'Disabled'})
   disabled.text='true'
 data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
 exported=ET.Element('roblox',{'version':'4'});exported.append(copy.deepcopy(package))
 exported_data=ET.tostring(exported,encoding='utf-8',xml_declaration=True)
 after=sources(ET.fromstring(data))
 for n in('Main','BackendBinding'):
  if before[n]!=after[n]:raise ValueError('PROVEN_CONNECTOR_CORE_CHANGED:'+n)
 installer=text(ROOT/'prototipo/fuentes/INSTALAR_PILOTO_R07_BASE.luau')
 installer=installer.replace('INHERITED_JSON_LITERAL',json.dumps(json.dumps(inherited,separators=(',',':'))))
 installer=installer.replace('SCENARIO_SHA_PLACEHOLDER',fp).replace('PAR28_WORLD_SHA_PLACEHOLDER',WORLD_SHA)
 # The only executable driver is an adaptation of the preserved raw-string ABI fix.
 driver=text(OLD/'NATIVE_LIMPIO_R01/ejecutar_native_limpio_R03_preparado.py')
 driver=driver.replace('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V2_CTRL1','ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_PILOT')
 driver=driver.replace('CUTOFF=1794802380;LAST_NEW=1794798600','CUTOFF=1794863220;LAST_NEW=1794859200')
 driver=driver.replace('953651','991187').replace('CTRL1','PILOT').replace('DEEConnector_R06','DEEConnector_R07').replace('R06_NATIVE_CLEAN','R07_NATIVE_PILOT').replace('scene_01','map_b')
 driver=driver.replace("observation['seq']+8","observation['seq']+56").replace('seq+8','seq+56').replace('ancestral8','ancestral56')
 driver=driver.replace('MANIFIESTO_LIVE_ESCENA_R01.json','MANIFIESTO_PILOTO_R07.json').replace('DEEConnector_NATIVE_LIMPIO_R01.rbxlx','DEEConnector_PILOTO_OTRO_MAPA_R07.rbxlx')
 driver=driver.replace('RBX06_NATIVE_SCOPE_INTEGRAL_V2.json','RBX07_NATIVE_SCOPE_INTEGRAL_V3.json').replace('RBX06_NATIVE_INTEGRAL_V2/events.jsonl','RBX07_NATIVE_INTEGRAL_V3/events.jsonl')
 driver=driver.replace("scope['teacher_mode']=='omitted'","scope['teacher_mode']=='paired'")
 driver=driver.replace("ledger['limit']==100000","ledger['limit']==160000").replace('<=100000','<=160000')
 driver=driver.replace("ROOT/'control/mcp_persistente_R06.py'","ROOT/'control/mcp_persistente_v3.py'")
 driver=driver.replace("ROOT/'native/owner_support_integral_v2.py'","ROOT/'native/owner_support_v3.py'").replace("ROOT/'native/adapter_integral_v2.py'","ROOT/'native/adapter_v3.py'")
 driver=driver.replace('LiveAdapters_R01','LiveAdapters_R07').replace('INSTALAR_LIVE_SELLADO_R01.luau','INSTALAR_PILOTO_R07.luau')
 driver=driver.replace("if not first['null']:","if first['action']in('ASK_STATION','SKIP_STATION'):")
 driver=driver.replace('No new Native clean episode after03:10UTC','No new Native pilot episode after20:00UTC')
 driver=driver.replace('public panel1/bothfree','public panel1/bothfree with fixed local tags')
 driver=driver.replace('Prepared port anatomy±6','Prepared absolute ports on a different map')
 driver=driver.replace('prepared minimal body','prepared Humanoid body on another map').replace('injected minimal body','injected Humanoid body on another map')
 driver=driver.replace('R02 plus the preserved R03 continuation proved the actual original episode.','R06 proved its own original episode; this R07 adaptation is PREPARED until actually executed.')
 driver=driver.replace('historical safety/cutoff guards','new R07 safety/cutoff guards')
 driver=driver.replace('on advanced PILOT T955215','on any advanced PILOT after991187').replace('no teacher','no new teacher').replace('teacherMode','teacherMode')
 compile(driver,'ejecutar_piloto_R07_preparado.py','exec')
 write(HERE/'DEEConnector_PILOTO_OTRO_MAPA_R07.rbxlx',data)
 write(ROOT/'prototipo/exportado/DEEConnector_R07.rbxmx',exported_data)
 write(HERE/'INSTALAR_PILOTO_R07.luau',installer)
 write(HERE/'ejecutar_piloto_R07_preparado.py',driver)
 # Store sources inside the kit for inspection and reinstallation.
 write(HERE/'LiveAdapters_R07.luau',adapter);write(HERE/'MotorPathfinding_R07.luau',motor)
 for p,h in preserved.items():
  if sha(p)!=h:raise ValueError('PRESERVED_SOURCE_CHANGED:'+p)
 record={'schema':'DEE.R07.PilotPrepared.v1','status':'PILOTO_PREPARADO_NO_EXTERNAMENTE_VALIDADO',
  'scene':{'path':str(HERE/'DEEConnector_PILOTO_OTRO_MAPA_R07.rbxlx'),'sha256':sha(HERE/'DEEConnector_PILOTO_OTRO_MAPA_R07.rbxlx')},
  'modules_sha256':{n:hashlib.sha256(v.encode()).hexdigest()for n,v in after.items()},
  'definition':definition,'scenario_sha256':fp,'preserved_sources':preserved,
  'original_Main_Binding_unchanged':True,'Native_ticks':0,'MCP_calls':0,'model_calls':0,
  'driver_sha256':sha(HERE/'ejecutar_piloto_R07_preparado.py'),
  'fresh_driver_not_materially_reproduced':True,'external_developers_consulted':0}
 write(HERE/'MANIFIESTO_PILOTO_R07.json',json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(record,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
