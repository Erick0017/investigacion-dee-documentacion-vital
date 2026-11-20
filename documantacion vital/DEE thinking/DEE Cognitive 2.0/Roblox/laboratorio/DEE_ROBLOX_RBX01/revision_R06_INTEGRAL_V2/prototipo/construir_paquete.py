"""Export source-only .rbxmx + bounded MCP install steps. No Studio/Native run."""
from pathlib import Path
import argparse,hashlib,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
MODULES=('Main','BackendBinding','MinimalAdapters','ExampleConfig')
DEFINITION={'schema':'DEE.MinimalSceneDefinition.R01','experience':'R06_CLEAN','scene':'scene_01',
            'port_offsets':{'0':[6,0,0],'1':[-6,0,0]},'actor_start':[0,3,0],
            'technical_fixture':True,'Native_ticks':0,'max_opportunities':2,'shared_runtime':'NONE_IN_PACKAGE'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):
    with path.open('x',encoding='utf8')as f:f.write(data)
def run(output_directory):
    destination=Path(output_directory)
    if not destination.is_absolute():destination=ROOT/destination
    if not destination.resolve().is_relative_to(ROOT):raise ValueError('Fresh prototype export directory only')
    destination.mkdir(exist_ok=False)
    steps=destination/'instalacion_MCP';steps.mkdir()
    sources={name:(ROOT/'fuentes'/f'{name}.luau').read_bytes()for name in MODULES}
    model=ET.Element('roblox',{'version':'4'});ET.SubElement(model,'External').text='null';ET.SubElement(model,'External').text='nil'
    container=ET.SubElement(model,'Item',{'class':'Model','referent':'RBX_DEE_PACKAGE'})
    props=ET.SubElement(container,'Properties');ET.SubElement(props,'string',{'name':'Name'}).text='DEEConnector_R06'
    for name,raw in sources.items():
        item=ET.SubElement(container,'Item',{'class':'ModuleScript','referent':'RBX_'+name})
        prop=ET.SubElement(item,'Properties');ET.SubElement(prop,'string',{'name':'Name'}).text=name
        ET.SubElement(prop,'ProtectedString',{'name':'Source'}).text=raw.decode('utf8')
    xml=destination/'DEEConnector_R06.rbxmx';ET.ElementTree(model).write(xml,encoding='utf-8',xml_declaration=True)
    restored=ET.parse(xml)
    actual={x.find("Properties/string[@name='Name']").text:x.find("Properties/ProtectedString[@name='Source']").text.encode('utf8')for x in restored.findall('./Item/Item')}
    if actual!=sources:raise ValueError('XML source roundtrip differs')
    first='''assert(game:GetService("RunService"):IsStudio()and game:GetService("RunService"):IsRunning(),"STUDIO_PLAY_ONLY")
local ss=game:GetService("ServerStorage");assert(not ss:FindFirstChild("DEE_Install_R06_V1"),"INSTALL_ALREADY_PRESENT_PRESERVED")
assert(not game:GetService("ServerScriptService"):FindFirstChild("DEEConnector_R06"),"PACKAGE_ALREADY_PRESENT_PRESERVED")
local f=Instance.new("Folder");f.Name="DEE_Install_R06_V1";f:SetAttribute("Protocol","DEE.SourceInstall.R01");f.Parent=ss
'''
    for name in MODULES:first+='local c=Instance.new("Folder");c.Name='+json.dumps(name)+';c.Parent=f\n'
    first+='return{prepared=true,NativeTicks=0,packageNotYetInstalled=true}'
    files=[]
    def step(label,code):
        if len(code.encode('utf8'))>8192:raise ValueError('MCP code exceeds bounded8192B')
        path=steps/f'{len(files):03d}_{label}.luau';write(path,code+'\n')
        files.append(dict(path=path.relative_to(ROOT).as_posix(),bytes=path.stat().st_size,sha256=sha(path)))
    step('preparar',first)
    counts={}
    for name,raw in sources.items():
        chunks=[raw[i:i+3000].hex()for i in range(0,len(raw),3000)];counts[name]=len(chunks)
        for index,chunk in enumerate(chunks):
            code='local f=assert(game:GetService("ServerStorage"):FindFirstChild("DEE_Install_R06_V1"));assert(f:GetAttribute("Protocol")=="DEE.SourceInstall.R01");local c=f['+json.dumps(name)+'];local name='+json.dumps(f'{index:04d}')+';assert(not c:FindFirstChild(name),"CHUNK_ALREADY_PRESENT_PRESERVED");local v=Instance.new("StringValue");v.Name=name;v.Value='+json.dumps(chunk)+';v.Parent=c;return{stored=name,module='+json.dumps(name)+',hexBytes=#v.Value,NativeTicks=0}'
            step(name+'_'+str(index),code)
    final='''local ss=game:GetService("ServerStorage");local f=assert(ss:FindFirstChild("DEE_Install_R06_V1"));assert(not f:GetAttribute("Assembled"),"INSTALL_ALREADY_ASSEMBLED")
local parent=game:GetService("ServerScriptService");assert(not parent:FindFirstChild("DEEConnector_R06"),"PACKAGE_ALREADY_PRESENT")
local model=Instance.new("Model");model.Name="DEEConnector_R06"
local function decode(hex)return(hex:gsub("..",function(v)return string.char(tonumber(v,16))end))end
'''
    for name,count in counts.items():
        final+='do local chunks={};local c=f['+json.dumps(name)+'];assert(#c:GetChildren()=='+str(count)+',"CHUNK_COUNT");for i=0,'+str(count-1)+' do chunks[#chunks+1]=c[string.format("%04d",i)].Value end;local source=decode(table.concat(chunks));assert(#source=='+str(len(sources[name]))+',"SOURCE_LENGTH");local m=Instance.new("ModuleScript");m.Name='+json.dumps(name)+';m.Source=source;m.Parent=model end\n'
    final+='model.Parent=parent;f:SetAttribute("Assembled",true);local api=require(model.Main);return{installed=true,schema=api.Schema,NativeTicks=0,backendStarted=false,XMLFileNotImportedByThisMethod=true}'
    step('ensamblar',final)
    fingerprint=hashlib.sha256(json.dumps(DEFINITION,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    scene='''assert(game:GetService("RunService"):IsStudio()and game:GetService("RunService"):IsRunning(),"STUDIO_PLAY_ONLY")
local package=assert(game:GetService("ServerScriptService"):FindFirstChild("DEEConnector_R06"));local API=require(package.Main);local adapters=require(package.MinimalAdapters)
assert(not workspace:FindFirstChild("DEE_Minimal_R06"),"EXISTING_TEST_SCENE_PRESERVED")
local world=Instance.new("Folder");world.Name="DEE_Minimal_R06";world.Parent=workspace
local actor=Instance.new("Model");actor.Name="Agent_01";local part=Instance.new("Part");part.Name="Core";part.Size=Vector3.new(2,2,2);part.Anchored=true;part.CanCollide=false;part.Position=Vector3.new(0,3,0);part.Parent=actor;actor.PrimaryPart=part;actor.Parent=world
actor:SetAttribute("DEE_AgentId","agent_01");game:GetService("CollectionService"):AddTag(actor,"DEE_Agent")
local runtime=API.mount({ExperienceId="R06_CLEAN",SceneId="scene_01",ScenarioFingerprint="FINGERPRINT",RegistryRoot=world,
Agents={agent_01={Participant="DEE",MaxOpportunities=2,MaxActions=4,AllowTechnicalTest=true}},
MakeAdapters=function(model)return adapters.new(model,{worldRoot=world})end})
runtime:scanTagged();local a=runtime:get("agent_01")
a:bindSession({sessionId="MCP_TECH_SESSION",lifeId="MCP_TECHNICAL_CONTROL",nativeTick=0})
return{observation=a:observe("ROUTE_CHOICE"),scope="TECHNICAL_CONNECTOR_INSTALL_NOT_NATIVE",NativeTicks=0}
'''.replace('FINGERPRINT',fingerprint)
    write(destination/'INSTALAR_ESCENA_MINIMA.luau',scene)
    test='''local package=game:GetService("ServerScriptService").DEEConnector_R06;local API=require(package.Main);local H=game:GetService("HttpService");local a=API.lookupRuntime("R06_CLEAN","scene_01"):get("agent_01");local s=a:status();assert(s.phase=="AWAIT_ACTION","TEST_EXPECTS_ORIGINAL_FRESH_OBSERVATION")
local raw=H:JSONEncode({protocol=API.Schema,namespace=a.namespace,sessionId=s.sessionId,seq=s.sequence,observationId=s.observation.observationId,actionId="MCP_TEST_ACTION_01",operationId="MCP_TEST_OPERATION_01",action={name="EXIT_0"},sourceKind="MCP_TECHNICAL_CONTROL"})
local ack=a:deliverAction(raw);local beforeDuplicate=a.adapters.body:capture();local duplicate=a:deliverAction(raw);local afterDuplicate=a.adapters.body:capture();assert(beforeDuplicate.schema==afterDuplicate.schema and #beforeDuplicate.pose==12 and #afterDuplicate.pose==12,"DUPLICATE_POSE_SHAPE");for i=1,12 do assert(beforeDuplicate.pose[i]==afterDuplicate.pose[i],"DUPLICATE_ACTION_REPLAYED_COMPONENT_"..i)end
a:confirmActionAck(ack.actionId,ack.operationId);local closed=a:completeFeedback({actionId=ack.actionId,feedbackOperationId="MCP_TEST_FEEDBACK_01",nativeTick=0})
local checkpoint=a:capture({backendWriterClosed=true,bridgeQuiescent=true,sessionId=s.sessionId,lifeId=s.lifeId,nativeTick=0,proofKind="NO_BACKEND_CREATED_TECHNICAL_ONLY"})
return{ack=ack,duplicateWasSameAction=duplicate.actionId==ack.actionId,cursor=closed.actionCursor,completedOpportunities=closed.completedOpportunities,folderCursor=a.node.ActionCursor.Value,checkpoint=checkpoint,NativeTicks=0,scope="MCP_TECHNICAL_CONTROL_NOT_DEE_DECISION"}
'''
    technical=destination/'PRUEBA_TECNICA_ACCION_Y_ACK_R02.luau';write(technical,test)
    manifest=dict(schema='DEE.RBX.ReusableModuleExport.R01',package=dict(path=xml.relative_to(ROOT).as_posix(),bytes=xml.stat().st_size,sha256=sha(xml)),
        modules={name:dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())for name,raw in sources.items()},
        XML_roundtrip_sources_equal=True,install_steps=files,scene_definition=DEFINITION,scene_fingerprint=fingerprint,
        technical_test=dict(path=technical.relative_to(ROOT).as_posix(),bytes=technical.stat().st_size,sha256=sha(technical),executed=False,revision='R02 numeric pose comparison, no JSON key-order assumption'),
        clean_Studio_install_status='NOT_EXECUTED_ROOT_MCP_REQUIRED',Native_ticks=0,model_calls=0,MCP_calls=0,
        claims='Source export and installer prepared, not yet a verified Studio-imported package or scientific Native demonstration.')
    write(destination/'MANIFIESTO_PROTO_MODULO_R01.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(package=str(xml),bytes=xml.stat().st_size,sha256=sha(xml),steps=len(files),XML_roundtrip=True,Native_executed=False),indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-directory',default='exportado')
    run(p.parse_args().output_directory)
