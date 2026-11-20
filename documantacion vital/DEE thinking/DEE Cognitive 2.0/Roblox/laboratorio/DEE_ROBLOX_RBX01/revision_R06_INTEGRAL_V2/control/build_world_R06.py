"""Offline XML packaging of the preserved DEV scene. Never launches a world."""
from pathlib import Path
import json,hashlib,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
C02=ROOT.parent/'revision_R05_C02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'mundo/DEE_RBX01_INTEGRAL_V2_NATIVE.rbxlx'
 assert not out.exists(),'No overwrite'
 source=C02/'mundo/DEE_RBX01_C02_DEV4.rbxlx';before=sha(source)
 tree=ET.parse(source);root=tree.getroot()
 def name(x):return x.findtext("Properties/string[@name='Name']")
 package=next(x for x in root.findall('.//Item') if name(x)=='RBX01Server')
 modules={name(x):x for x in package.findall('Item')}
 config=modules['Config'].find("Properties/ProtectedString[@name='Source']").text
 config=re.sub(r'C.WorldId=[^\n]+','C.WorldId="RBX01_INTEGRAL_V2_R06"',config)
 config=re.sub(r'C.MaxCycles=\d+','C.MaxCycles=28',config)
 config=re.sub(r'C.SuspendAfter=\d+','C.SuspendAfter=10',config)
 config=re.sub(r'C.ReserveStartsAtCycle=\d+','C.ReserveStartsAtCycle=11',config)
 config=re.sub(r'function C.PhaseAtCycle\(cycle\).*?\nend',
 'function C.PhaseAtCycle(cycle)\n if cycle>=23 then return 2 end\n if cycle>=17 then return 1 end\n return 0\nend',config,flags=re.S)
 config=re.sub(r'function C.SignsAtCycle\(cycle\).*?\nend',
 'function C.SignsAtCycle(cycle)\n if cycle>=17 then return {luma=1,nara=-1} end\n return {luma=-1,nara=1}\nend',config,flags=re.S)
 config=re.sub(r'function C.OperandsAtCycle\(cycle\).*?\nend',
 '''function C.OperandsAtCycle(cycle)
 if cycle>=26 then return {aLeft=9,aRight=2,bRight=1,variant="RESERVE_D"} end
 if cycle>=21 then return {aLeft=11,aRight=4,bRight=7,variant="RESERVE_C"} end
 if cycle>=16 then return {aLeft=8,aRight=3,bRight=2,variant="RESERVE_B"} end
 if cycle>=11 then return {aLeft=7,aRight=3,bRight=2,variant="RESERVE_A"} end
 return {aLeft=6,aRight=2,bRight=1,variant="FAMILIAR"}
end''',config,flags=re.S)
 body=(C02/'mundo/Body_C02_R02.luau').read_text('utf-8-sig')
 old='self.pendingTool={kind="LESSON",items={{form="luma",observedSign=signs.luma},{form="nara",observedSign=signs.nara}}}'
 assert body.count(old)==1
 body=body.replace(old,'if self.S.cycle>=16 then '+old+' else self:emit("LESSON_OMITTED_BY_FROZEN_RETENTION_PROTOCOL",{cycle=self.S.cycle}) end')
 sources={'Config':config,'Body_C02':body,'EstadoPareja_C02':(C02/'mundo/EstadoPareja_C02.luau').read_text('utf-8-sig'),
 'Controller':'-- R06 explicit MCP API only. No auto-start and no second controller.\n'}
 for key,text in sources.items():
  modules[key].find("Properties/ProtectedString[@name='Source']").text=text
 for item in root.findall('.//Item'):
  if item.get('class') in ('Script','LocalScript'):
   # Local HUD can remain; no automatic Native or main controller.
   if name(item)=='Controller':item.find("Properties/bool[@name='Disabled']").text='true'
 api=ET.SubElement(package,'Item',{'class':'ModuleScript','referent':'R06_API_WORLD'})
 props=ET.SubElement(api,'Properties');ET.SubElement(props,'string',{'name':'Name'}).text='WorldAPI_R06'
 ET.SubElement(props,'ProtectedString',{'name':'Source'}).text=(ROOT/'mundo/WorldAPI_R06.luau').read_text('utf8')
 protocol=ROOT/'protocolo/PROTOCOLO_INTEGRAL_V2_R01.json'
 fp=hashlib.sha256((config+body+sources['EstadoPareja_C02']+(ROOT/'mundo/WorldAPI_R06.luau').read_text('utf8')+sha(protocol)).encode()).hexdigest()
 config=re.sub(r'C.ScenarioFingerprint=[^\n]+',f'C.ScenarioFingerprint="{fp}"',config)
 modules['Config'].find("Properties/ProtectedString[@name='Source']").text=config
 (ROOT/'mundo/Config_R06.luau').write_text(config,encoding='utf8')
 (ROOT/'mundo/Body_R06.luau').write_text(body,encoding='utf8')
 payload=ET.tostring(root,encoding='utf-8',xml_declaration=True);ET.fromstring(payload)
 out.write_bytes(payload);assert sha(source)==before
 result={'schema':'DEE.RBX01.R06.world_package.R01','source':str(source),'source_sha256':before,
 'output':str(out),'bytes':len(payload),'sha256':sha(out),'scenario_sha256':fp,'Native_executed':False,
 'source_world_preserved':True,'auto_start':'NONE','host_prepared_order_through_cycle':22,'native_order_from_cycle':23,
 'sources':{str(p.relative_to(ROOT)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in (ROOT/'mundo').glob('*.luau')}}
 (ROOT/'mundo/BUILD_WORLD_R06.json').write_text(json.dumps(result,indent=2),encoding='utf8')
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
