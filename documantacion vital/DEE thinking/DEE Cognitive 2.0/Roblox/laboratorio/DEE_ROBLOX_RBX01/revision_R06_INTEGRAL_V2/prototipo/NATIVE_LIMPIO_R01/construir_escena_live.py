"""Append only an injected adapter to the real clean package scene. No runtime."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
PROTOTYPE=HERE.parent
DEFINITION=dict(schema='DEE.NativeCleanSceneDefinition.R01',actor=[0,3,0],panel=dict(price0=0,price1=0,signal=1,queryCost=1),
    ports={'0':[6,0,0],'1':[-6,0,0]},resource=[6,3,0],base=[0,3,0],permissionStock=200,maxNewNativeEpisodes=1,
    nativeSequenceOffset=8,productsInitiallyAbsent=True,goalDelivery=True,teacherMode='omitted')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def modules(tree):
    return {x.find("Properties/string[@name='Name']").text:hashlib.sha256(x.find("Properties/ProtectedString[@name='Source']").text.encode()).hexdigest()for x in tree.iter('Item')if x.get('class')=='ModuleScript'}
def run():
    source=PROTOTYPE/'exportado/DEEConnector_ESCENA_MINIMA_R06.rbxlx';tree=ET.parse(source);before=modules(tree)
    package=next(x for x in tree.iter('Item')if x.get('class')=='Model'and x.find("Properties/string[@name='Name']")is not None and x.find("Properties/string[@name='Name']").text=='DEEConnector_R06')
    item=ET.SubElement(package,'Item',{'class':'ModuleScript','referent':'RBX_NATIVE_CLEAN_ADAPTER_R01'});props=ET.SubElement(item,'Properties')
    ET.SubElement(props,'string',{'name':'Name'}).text='LiveAdapters_R01'
    ET.SubElement(props,'ProtectedString',{'name':'Source'}).text=(HERE/'LiveAdapters_R01.luau').read_text(encoding='utf8')
    output=HERE/'DEEConnector_NATIVE_LIMPIO_R01.rbxlx'
    if output.exists():raise ValueError('Fresh live scene only')
    tree.write(output,encoding='utf-8',xml_declaration=True);actual=modules(ET.parse(output))
    if any(actual.get(k)!=v for k,v in before.items()):raise ValueError('Existing exported Main/Binding/adapter source changed')
    fingerprint=hashlib.sha256(json.dumps(DEFINITION,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    installer=HERE/'INSTALAR_LIVE_SELLADO_R01.luau'
    with installer.open('x',encoding='utf8')as f:f.write((HERE/'INSTALAR_LIVE_R01.luau').read_text(encoding='utf8').replace('SCENARIO_SHA_PLACEHOLDER',fingerprint))
    record=dict(schema='DEE.NativeCleanSceneExport.R01',scene=dict(path=str(output),bytes=output.stat().st_size,sha256=sha(output)),
        source_clean_scene_sha256=sha(source),original_exported_modules_unchanged=True,modules_sha256=actual,
        scenario=DEFINITION,scenario_sha256=fingerprint,installer_sha256=sha(installer),Native_ticks=0,MCP_calls=0,
        status='PREPARED_NOT_OPENED_NOT_NATIVE_EXECUTED')
    with(HERE/'MANIFIESTO_LIVE_ESCENA_R01.json').open('x',encoding='utf8')as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(record,ensure_ascii=False,indent=2))
if __name__=='__main__':run()
