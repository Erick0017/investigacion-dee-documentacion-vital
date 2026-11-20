"""FS-only private focal scenes. No Native, leases, Studio or token output."""
from pathlib import Path
import argparse,json,re,xml.etree.ElementTree as E
from sdk_common import RUNTIME,atomic,canonical,read,sha,safe,verify_focal_sources
from serial_guard import REGISTRY
HERE=Path(__file__).resolve().parent

def name(item):
    props=item.find('Properties')
    return next((x.text for x in props or [] if x.get('name')=='Name'),None)

def service(root,class_name,referent):
    found=[x for x in root.findall('Item') if x.get('class')==class_name]
    if len(found)>1:raise ValueError('AMBIGUOUS_SERVICE')
    if found:return found[0]
    node=E.SubElement(root,'Item',{'class':class_name,'referent':referent})
    p=E.SubElement(node,'Properties');E.SubElement(p,'string',{'name':'Name'}).text=class_name
    return node

def make(private_root,runtime=RUNTIME):
    runtime=Path(runtime).resolve(strict=True);verify_focal_sources(runtime)
    base=Path(private_root).resolve(strict=True)
    if base!=runtime.parent:raise ValueError('EXACT_PRIVATE_SHORT_DEPLOYMENT_PARENT')
    for p in (base,*base.parents):
        if p.is_symlink() or getattr(p.lstat(),'st_file_attributes',0)&1024:raise ValueError('LINKED_TARGET')
    rows=read(runtime/REGISTRY)['participants']
    if [r['condition'] for r in rows]!=['OSCILANTE','CONTROL']:raise ValueError('EXACT_TWO_PREPARED_PARTICIPANTS')
    plans=[]
    for row in rows:
        condition=row['condition'];arm='CONSUME_RECHARGE' if condition=='OSCILANTE' else 'NONCONSUMING_CONTROL'
        short='OSC' if condition=='OSCILANTE' else 'CONTROL';port=8897 if condition=='OSCILANTE' else 8898
        source=HERE/'escenas'/('DEE_FOCAL_'+arm+'_R06.rbxlx')
        target=base/('DEE_FOCAL_'+short+'_R06_01.rbxlx')
        if target.exists():raise FileExistsError('PRIVATE_SCENE_NEVER_OVERWRITTEN')
        home=runtime/'estado_demo/instancias'/row['instanceId'];cfg=read(home/'INSTANCE.json')
        proof=read(home/'PREPARACION_FOCAL.json')
        if (cfg.get('profile')!='FOCAL' or cfg.get('validationRevision')!='FOCAL_R06'
                or cfg.get('focalCondition')!=condition or cfg['nativeTick']!=991187
                or cfg['localSequence']!=0 or cfg['completedCycles']!=0
                or proof['contextSha256']!=sha(home/'CONTEXTO_EJECUCION.json')):
            raise ValueError('EXACT_FRESH_PREPARED_FOCAL_CONTEXT')
        tree=E.parse(source);root=tree.getroot()
        modules=[x for x in root.iter('Item') if name(x)=='SDKConfig']
        if len(modules)!=1:raise ValueError('ONE_CONFIG')
        text=next(x for x in modules[0].find('Properties') if x.get('name')=='Source')
        m=re.search(r'\[=\[(.*?)\]=\]',text.text,re.S)
        if not m:raise ValueError('CONFIG_ENVELOPE')
        c=json.loads(m.group(1))
        if (c['Mode']!='PREVIEW' or c['Focal']['Arm']!=arm
                or (c['MaxOpportunities'],c['RunCycles'],c['MaxActions'])!=(6,6,12)):
            raise ValueError('FROZEN_SAFE_SOURCE_CONFIG')
        c['Mode']='NATIVE'
        text.text=text.text[:m.start(1)]+'\n'+json.dumps(c,ensure_ascii=False,indent=2)+'\n'+text.text[m.end(1):]
        folder_name=c['PrivateConnectionFolder']
        ss=service(root,'ServerStorage','RBX_FOCAL_R06_PRIVATE')
        if any(name(x)==folder_name for x in ss.findall('Item')):raise ValueError('NO_PRIVATE_SOURCE_CONNECTION')
        http=service(root,'HttpService','RBX_FOCAL_R06_HTTP');props=http.find('Properties')
        enabled=next((x for x in props if x.get('name')=='HttpEnabled'),None)
        if enabled is None:enabled=E.SubElement(props,'bool',{'name':'HttpEnabled'})
        enabled.text='true'
        plans.append((row,tree,ss,folder_name,target,source,port))
    token=read(runtime/'configuracion/CONEXION_PRIVADA.json')['token']
    if not isinstance(token,str) or len(token)<32:raise ValueError('PRIVATE_TOKEN_REQUIRED')
    out=[]
    for row,tree,ss,folder_name,target,source,port in plans:
        folder=E.SubElement(ss,'Item',{'class':'Folder','referent':'FOCAL_PRIVATE_CONNECTION'})
        props=E.SubElement(folder,'Properties');E.SubElement(props,'string',{'name':'Name'}).text=folder_name
        for key,value in [('BaseUrl','http://127.0.0.1:'+str(port)),('InstanceId',row['instanceId']),('Token',token)]:
            item=E.SubElement(folder,'Item',{'class':'StringValue','referent':'FOCAL_PRIVATE_'+key})
            props=E.SubElement(item,'Properties');E.SubElement(props,'string',{'name':'Name'}).text=key
            E.SubElement(props,'string',{'name':'Value'}).text=value
        with target.open('xb') as f:tree.write(f,encoding='utf-8',xml_declaration=True)
        out.append({'condition':row['condition'],'instanceId':row['instanceId'],'file':str(target),
                    'sha256':sha(target),'publicSourceSha256':sha(source),'mode':'NATIVE',
                    'HttpEnabled':True,'credentialPrinted':False,'NativeExecuted':False})
    return {'schema':'DEE.SDK.FocalPrivateScenes.R06','participants':out,'NativeExecuted':False}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--private-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    value=make(a.private_root);atomic(a.output,value,new=True);print(canonical(value))
