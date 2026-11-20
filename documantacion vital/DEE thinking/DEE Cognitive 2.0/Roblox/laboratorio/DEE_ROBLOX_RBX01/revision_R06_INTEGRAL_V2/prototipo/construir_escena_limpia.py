"""Embed the exact exported .rbxmx Item in a clean local .rbxlx; no Studio run."""
from pathlib import Path
import copy,hashlib,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def string(parent,name,text):ET.SubElement(parent,'string',{'name':name}).text=text
def source_map(tree):
    result={}
    for item in tree.iter('Item'):
        if item.get('class')=='ModuleScript':
            name=item.find("Properties/string[@name='Name']").text
            raw=item.find("Properties/ProtectedString[@name='Source']").text.encode('utf8')
            if name in result:raise ValueError('Duplicate module name')
            result[name]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    return result
def run():
    package=ROOT/'exportado/DEEConnector_R06.rbxmx'
    manifest=json.loads((ROOT/'exportado/MANIFIESTO_PROTO_MODULO_R02.json').read_text(encoding='utf8'))
    if sha(package)!=manifest['package']['sha256']:raise ValueError('Exported package changed')
    package_tree=ET.parse(package);modules=source_map(package_tree)
    if modules!=manifest['modules']:raise ValueError('Package source fingerprint differs')
    root=ET.Element('roblox',{'version':'4'})
    ET.SubElement(root,'External').text='null';ET.SubElement(root,'External').text='nil'
    def service(class_name,ref):
        item=ET.SubElement(root,'Item',{'class':class_name,'referent':ref})
        properties=ET.SubElement(item,'Properties');string(properties,'Name',class_name)
        return item,properties
    workspace,properties=service('Workspace','RBX_CLEAN_WORKSPACE')
    ET.SubElement(properties,'Ref',{'name':'CurrentCamera'}).text='RBX_CLEAN_CAMERA'
    camera=ET.SubElement(workspace,'Item',{'class':'Camera','referent':'RBX_CLEAN_CAMERA'})
    camera_props=ET.SubElement(camera,'Properties');string(camera_props,'Name','Camera')
    frame=ET.SubElement(camera_props,'CoordinateFrame',{'name':'CFrame'})
    # Prepared default view only; no recorded scene or cognitive trajectory.
    for name,val in zip(('X','Y','Z','R00','R01','R02','R10','R11','R12','R20','R21','R22'),(12,12,24,1,0,0,0,1,0,0,0,1)):
        ET.SubElement(frame,name).text=str(val)
    scripts,_=service('ServerScriptService','RBX_CLEAN_SCRIPTS')
    scripts.append(copy.deepcopy(package_tree.getroot().find('Item')))
    service('ServerStorage','RBX_CLEAN_STORAGE');service('ReplicatedStorage','RBX_CLEAN_REPLICATED')
    output=ROOT/'exportado/DEEConnector_ESCENA_MINIMA_R06.rbxlx'
    if output.exists():raise ValueError('Preserve existing clean scene')
    ET.ElementTree(root).write(output,encoding='utf-8',xml_declaration=True)
    parsed=ET.parse(output)
    if source_map(parsed)!=modules:raise ValueError('Embedded package Sources differ')
    items=list(parsed.iter('Item'));refs=[i.get('referent')for i in items]
    if len(refs)!=len(set(refs)):raise ValueError('Duplicate XML referent')
    for element in parsed.iter('Ref'):
        if element.text not in ('null','nil')and element.text not in refs:raise ValueError('Unresolved XML reference')
    if any(i.get('class')in ('Script','LocalScript')for i in items):raise ValueError('Clean scene must not autorun scripts')
    record=dict(schema='DEE.RBX.CleanModuleScene.R01',path=str(output),bytes=output.stat().st_size,
        sha256=sha(output),package_rbxmx_sha256=sha(package),module_sources=modules,
        exact_exported_Item_embedded=True,unique_referents=True,references_resolved=True,
        contains_no_auto_scripts=True,contains_C02_world=False,
        Root_required_next='Open this actual rbxlx in Studio, Play, run INSTALAR_ESCENA_MINIMA then PRUEBA_TECNICA_ACCION_Y_ACK_R02. No Source-install step needed.',
        Studio_opened_by_builder=False,Native_ticks=0,MCP_calls=0,model_calls=0)
    proof=ROOT/'exportado/ESCENA_MINIMA_MANIFIESTO_R01.json'
    with proof.open('x',encoding='utf8')as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(record,ensure_ascii=False,indent=2))
if __name__=='__main__':run()
