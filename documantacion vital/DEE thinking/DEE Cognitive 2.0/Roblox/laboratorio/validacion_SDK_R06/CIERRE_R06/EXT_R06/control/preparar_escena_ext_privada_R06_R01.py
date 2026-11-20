"""Prepare a NEW private EXT scene. FS/XML only; never starts Native or HTTP."""
from pathlib import Path
import argparse,copy,hashlib,json,re,xml.etree.ElementTree as E
MODEL_SHA256='aa6807c530f662ce11e21f107008978f9bf9ee003f28416c0f85a22fd3b107bb'
SOURCE_SHA256='28a5bd308b07abfed1696b2e4e0bf4bf702858616ac76f75ff38e34edab5fb7e'
FOLDER='DEE_SDK_CAPABILITIES_PrivateConnection_R06'
VERSION='DEE.Roblox.SDK.assisted_capabilities.R06'

SCOPE_SCRIPT='''-- Static disclosure only: no HTTP, Native, Main or avatar control.
local p=workspace:WaitForChild("DEE_SDK_EXT_R06_PANEL",10)
if p then
 local sign=Instance.new("Part");sign.Name="EXT_R06_ALCANCE_PREPARACION"
 sign.Anchored=true;sign.CanCollide=false;sign.CanTouch=false;sign.CanQuery=false
 sign.Size=Vector3.new(28,3,1);sign.Position=Vector3.new(20,20,20)
 sign.Color=Color3.fromRGB(43,33,12);sign.Parent=workspace
 local gui=Instance.new("SurfaceGui");gui.Face=Enum.NormalId.Front;gui.CanvasSize=Vector2.new(1120,120);gui.Parent=sign
 local text=Instance.new("TextLabel");text.Size=UDim2.fromScale(1,1);text.BackgroundTransparency=1
 text.Font=Enum.Font.Code;text.TextSize=24;text.TextColor3=Color3.fromRGB(255,220,135)
 text.TextWrapped=true;text.RichText=false
 text.Text="EXT ASISTIDA | Core desactivado. Escena de archivo: NO es el World físico actual K4. Pareja previa PRE_CAP tras avance Native. Sin actuación del avatar."
 text.Parent=gui
end
'''

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def name(item):
    props=item.find('Properties')
    if props is None:return None
    return next((x.text for x in props if x.get('name')=='Name'),None)
def props(item):
    value=item.find('Properties')
    if value is None:value=E.SubElement(item,'Properties')
    return value
def boolean(item,key,value):
    p=props(item);nodes=[x for x in p if x.get('name')==key]
    if len(nodes)>1:raise ValueError('AMBIGUOUS_BOOLEAN_PROPERTY')
    node=nodes[0] if nodes else E.SubElement(p,'bool',{'name':key})
    if node.tag!='bool':raise ValueError('BOOLEAN_PROPERTY_REQUIRED')
    node.text='true' if value else 'false'
def named_source(item):
    found=[x for x in props(item) if x.get('name')=='Source']
    if len(found)!=1:raise ValueError('EXACT_ONE_SCRIPT_SOURCE')
    return found[0]
def service(root,klass,referent):
    found=[x for x in root.findall('Item') if x.get('class')==klass]
    if len(found)>1:raise ValueError('AMBIGUOUS_SERVICE')
    if found:return found[0]
    item=E.SubElement(root,'Item',{'class':klass,'referent':referent})
    E.SubElement(props(item),'string',{'name':'Name'}).text=klass
    return item
def no_links(path):
    for p in (path,*path.parents):
        if p.exists() and (p.is_symlink() or getattr(p.lstat(),'st_file_attributes',0)&1024):
            raise ValueError('LINKED_PRIVATE_PATH_NOT_ACCEPTED')
def value(item,key):
    found=[x for x in item.findall('Item') if name(x)==key and x.get('class')=='StringValue']
    if len(found)!=1:raise ValueError('EXACT_PRIVATE_CONNECTION_FIELD')
    return next(x.text or '' for x in props(found[0]) if x.get('name')=='Value')

def prepare(source_scene,connection_xml,extension_model,output,instance_id,*,
            source_sha256=SOURCE_SHA256):
    source=Path(source_scene).resolve(strict=True);connection=Path(connection_xml).resolve(strict=True)
    model=Path(extension_model).resolve(strict=True);target=Path(output).absolute()
    if not re.fullmatch(r'SDK_DEMO_[0-9A-F]{16}',instance_id):raise ValueError('EXACT_SDK_INSTANCE_REQUIRED')
    if target.parent.resolve(strict=True)!=source.parent or target.suffix.lower()!='.rbxlx':
        raise ValueError('NEW_SCENE_IN_SAME_PRIVATE_SHORT_DIRECTORY_REQUIRED')
    if target.exists():raise FileExistsError('PRIVATE_TARGET_NEVER_OVERWRITTEN')
    for p in (source,connection,model,target.parent):no_links(p)
    if sha(source)!=source_sha256:raise ValueError('EXACT_CLOSED_SOURCE_SCENE_SHA_REQUIRED')
    if sha(model)!=MODEL_SHA256:raise ValueError('FROZEN_EXTENSION_MODEL_SHA_REQUIRED')
    source_before=sha(source);connection_before=sha(connection);model_before=sha(model)
    tree=E.parse(source);root=tree.getroot()
    if root.tag!='roblox':raise ValueError('ROBLOX_XML_REQUIRED')
    existing=[x for x in root.iter('Item') if x.get('class') in ('Script','LocalScript')]
    core=[x for x in existing if x.get('class')=='Script' and name(x)=='SDK_Arranque']
    if len(core)!=1 or len(existing)!=1:raise ValueError('ONLY_KNOWN_CORE_BOOTSTRAP_EXPECTED')
    core_ids=[next((v.text for v in props(x) if v.get('name')=='Value'),None) for x in root.iter('Item') if x.get('class')=='StringValue' and name(x)=='InstanceId']
    if core_ids != [instance_id]:raise ValueError('SOURCE_CORE_AND_EXT_MUST_BE_SAME_INSTANCE')
    core_source=named_source(core[0]).text
    boolean(core[0],'Disabled',True);boolean(core[0],'Enabled',False)
    # Disable only the bootstrap's execution; its Source and all core modules remain literal.
    xml=E.parse(connection).getroot()
    folders=[x for x in xml.findall('Item') if x.get('class')=='Folder' and name(x)==FOLDER]
    if len(folders)!=1 or len(xml.findall('Item'))!=1:raise ValueError('ONE_EXACT_PRIVATE_EXT_FOLDER')
    folder=folders[0]
    if {name(x) for x in folder.findall('Item')}!={'BaseUrl','InstanceId','Token'}:
        raise ValueError('PRIVATE_CONNECTION_EXACT_FIELDS')
    if value(folder,'BaseUrl')!='http://127.0.0.1:8899' or value(folder,'InstanceId')!=instance_id:
        raise ValueError('EXACT_PRIVATE_EXT_ENDPOINT_AND_INSTANCE')
    if not 32<=len(value(folder,'Token'))<=1024:raise ValueError('PRIVATE_TOKEN_REQUIRED')
    ext=E.parse(model).getroot()
    items=ext.findall('Item')
    if len(items)!=1 or items[0].get('class')!='Model' or name(items[0])!='DEE_SDK_Capabilities_EXT_R06':
        raise ValueError('EXACT_FROZEN_EXTENSION_PACKAGE')
    package=copy.deepcopy(items[0])
    configs=[x for x in package.iter('Item') if name(x)=='Config_EXT_R06']
    if len(configs)!=1:raise ValueError('ONE_EXTENSION_CONFIG')
    node=named_source(configs[0]);match=re.search(r'\[=\[(.*?)\]=\]',node.text or '',re.S)
    if not match:raise ValueError('EXT_CONFIG_JSON_ENVELOPE')
    cfg=json.loads(match.group(1))
    if cfg['ExtensionVersion']!=VERSION or cfg['Enabled'] is not False or cfg['NoAutomaticMaterial'] is not True:
        raise ValueError('SAFE_PUBLIC_EXTENSION_DEFAULT_EXPECTED')
    if cfg['PrivateConnectionFolder']!=FOLDER:raise ValueError('EXT_PRIVATE_FOLDER_CONTRACT')
    cfg['Enabled']=True
    node.text=node.text[:match.start(1)]+'\n'+json.dumps(cfg,ensure_ascii=False,indent=2)+'\n'+node.text[match.end(1):]
    sss=service(root,'ServerScriptService','RBX_EXT_PRIVATE_SSS')
    if any(name(x)=='DEE_SDK_Capabilities_EXT_R06' for x in sss.findall('Item')):
        raise ValueError('EXT_PACKAGE_ALREADY_PRESENT')
    sss.append(package)
    ss=service(root,'ServerStorage','RBX_EXT_PRIVATE_SS')
    if any(name(x)==FOLDER for x in ss.findall('Item')):raise ValueError('EXT_PRIVATE_FOLDER_ALREADY_PRESENT')
    private_folder=copy.deepcopy(folder)
    for n,item in enumerate(private_folder.iter('Item'),1):item.set('referent','RBX_EXT_PRIVATE_CONNECTION_'+str(n))
    ss.append(private_folder)
    notice=E.SubElement(ss,'Item',{'class':'StringValue','referent':'RBX_EXT_PRIVATE_SCOPE'})
    E.SubElement(props(notice),'string',{'name':'Name'}).text='DEE_SDK_EXT_ALCANCE_R06'
    E.SubElement(props(notice),'string',{'name':'Value'}).text='ASSISTED; Core bootstrap disabled. File scene is not current physical K4 World. Previous SDK_PAIR is PRE_CAP after Native advance. No avatar actuation.'
    note=E.SubElement(package,'Item',{'class':'Script','referent':'RBX_EXT_PRIVATE_LABEL'})
    E.SubElement(props(note),'string',{'name':'Name'}).text='EXT_R06_ALCANCE_ASISTIDO'
    E.SubElement(props(note),'ProtectedString',{'name':'Source'}).text=SCOPE_SCRIPT
    http=service(root,'HttpService','RBX_EXT_PRIVATE_HTTP');boolean(http,'HttpEnabled',True)
    # Added objects get fresh XML referents; do not touch original core references.
    used={x.get('referent') for x in root.iter('Item') if x not in list(package.iter('Item'))}
    mapping={}
    for n,item in enumerate(package.iter('Item'),1):
        old=item.get('referent');new='RBX_EXT_PRIVATE_PACKAGE_'+str(n)
        if new in used:raise ValueError('REFERENT_COLLISION')
        if old:mapping[old]=new
        item.set('referent',new)
    for ref in package.iter('Ref'):
        if ref.text in mapping:ref.text=mapping[ref.text]
    if named_source(core[0]).text!=core_source:raise RuntimeError('CORE_SOURCE_CHANGED')
    if (sha(source),sha(connection),sha(model))!=(source_before,connection_before,model_before):
        raise RuntimeError('SOURCE_CHANGED_DURING_PREPARATION')
    with target.open('xb') as out:tree.write(out,encoding='utf-8',xml_declaration=True)
    return {'schema':'DEE.SDK.PrivateExtensionScene.R06.R01','status':'PREPARED_NOT_EXECUTED',
        'sourceSceneSha256':source_before,'extensionModelSha256':model_before,
        'privateConnectionFileSha256':connection_before,'output':str(target),'outputBytes':target.stat().st_size,
        'outputSha256':sha(target),'instanceId':instance_id,'coreBootstrapDisabled':True,
        'coreSourceChanged':False,'extensionEnabled':True,'HttpEnabled':True,'credentialPrinted':False,
        'NativeExecutedByHelper':False,'HTTPRequestedByHelper':False,'avatarActuatedByHelper':False,
        'currentWorldPairClaimed':False,'worldBinding':'PRE_CAP_SDK_PAIR_NOT_CURRENT_AFTER_NATIVE_ADVANCE',
        'mapDisclosure':'File preparation only; not actual K4 physical World.',
        'nextStep':'Root starts the prepared scene and checks GetCapabilitiesRO before any explicit assisted SubmitCapability.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-scene',required=True,type=Path);p.add_argument('--private-connection-xml',required=True,type=Path)
    p.add_argument('--extension-model',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    p.add_argument('--instance',required=True);p.add_argument('--source-sha256',default=SOURCE_SHA256)
    a=p.parse_args()
    result=prepare(a.source_scene,a.private_connection_xml,a.extension_model,a.output,a.instance,source_sha256=a.source_sha256)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
