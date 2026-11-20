#!/usr/bin/env python3
"""Create two private focal Place copies from publicR03. Files only; never prints credentials."""
from pathlib import Path
import argparse,hashlib,json,re,xml.etree.ElementTree as E

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def name(item):
    p=item.find('Properties')
    return None if p is None else next((x.text for x in p if x.get('name')=='Name'),None)
def service(root,cls,ref):
    found=[x for x in root.findall('Item')if x.get('class')==cls]
    if len(found)>1:raise ValueError('Duplicate service')
    if found:return found[0]
    x=E.SubElement(root,'Item',{'class':cls,'referent':ref});p=E.SubElement(x,'Properties');E.SubElement(p,'string',{'name':'Name'}).text=cls;return x

def make(registry,relocated_root):
    registry=Path(registry).resolve(strict=True);base=Path(relocated_root).resolve(strict=True)
    if base.name!='_sdk_val_20261118_01':raise ValueError('Exact relocated validation root required')
    for p in (base,*base.parents):
        if p.is_symlink()or getattr(p.lstat(),'st_file_attributes',0)&1024:raise ValueError('Linked private target prohibited')
    runtime=base/'RUNTIME_PRIVADO_LOCAL';r=json.loads(registry.read_text(encoding='utf-8'))
    if Path(r['relocatedRuntime']).resolve()!=runtime:raise ValueError('Registry runtime mismatch')
    if len(r['participants'])!=2:raise ValueError('Exactly two reserved focal participants')
    plans=[]
    for row in r['participants']:
        condition=row['condition'];expected={'OSCILANTE':('CONSUME_RECHARGE',8897,'DEE_FOCAL_OSC_VALIDACION_01.rbxlx'),'CONTROL':('NONCONSUMING_CONTROL',8898,'DEE_FOCAL_CONTROL_VALIDACION_01.rbxlx')}
        if condition not in expected:raise ValueError('Condition')
        arm,port,filename=expected[condition];instance=row['instanceId']
        if re.fullmatch(r'SDK_DEMO_[0-9A-F]{16}',instance)is None:raise ValueError('Instance format')
        target=Path(row['privateScene']).resolve()
        if target.parent!=base or target.name!=filename or target.exists():raise ValueError('Private target exists or escapes explicit root')
        source=Path(row['sourceScene']).resolve(strict=True)
        if source.name!='DEE_FOCAL_'+arm+'_R03.rbxlx':raise ValueError('Exact publicR03 source')
        proofpath=runtime/'estado_demo/instancias'/instance/'PREPARACION_FOCAL.json'
        proof=json.loads(proofpath.read_text(encoding='utf-8'))
        ctx=proofpath.parent/'CONTEXTO_EJECUCION.json'
        if proof['profile']!='FOCAL'or proof['condition']!=condition or proof['instanceId']!=instance or proof['NativeImported']is not False or proof['newNativeTicks']!=0 or proof['contextSha256']!=sha(ctx):raise ValueError('FS-only prepared context required')
        tree=E.parse(source);root=tree.getroot();cfg=[x for x in root.iter('Item')if name(x)=='SDKConfig']
        if len(cfg)!=1:raise ValueError('One SDKConfig')
        code=next(x for x in cfg[0].find('Properties')if x.get('name')=='Source')
        found=re.search(r'\[=\[(.*?)\]=\]',code.text,re.S)
        if found is None:raise ValueError('Public config envelope')
        c=json.loads(found.group(1))
        if c['Version']!='0.1.0'or c['Mode']!='PREVIEW'or c['Focal']['Arm']!=arm or(c['MaxOpportunities'],c['RunCycles'],c['MaxActions'])!=(6,6,12)or c['PrivateConnectionFolder']!='DEE_FOCAL_PrivateConnection':raise ValueError('Exact safe focal source config')
        c['Mode']='NATIVE';code.text=code.text[:found.start(1)]+'\n'+json.dumps(c,ensure_ascii=False,indent=2)+'\n'+code.text[found.end(1):]
        ss=service(root,'ServerStorage','RBX_FOCAL_PRIVATE_SS')
        if any(name(x)=='DEE_FOCAL_PrivateConnection'for x in ss.findall('Item')):raise ValueError('Source already contains private connection')
        hs=service(root,'HttpService','RBX_FOCAL_PRIVATE_HTTP');props=hs.find('Properties')
        enabled=next((x for x in props if x.get('name')=='HttpEnabled'),None)
        if enabled is None:enabled=E.SubElement(props,'bool',{'name':'HttpEnabled'})
        enabled.text='true'
        plans.append((row,tree,ss,proof,sha(source),target,'http://127.0.0.1:'+str(port)))
    # Read only the existing demo token; never put it in a DTO, log, filename or print.
    connection=json.loads((runtime/'configuracion/CONEXION_PRIVADA.json').read_text(encoding='utf-8-sig'))
    token=connection.get('token')
    if not isinstance(token,str)or len(token)<32:raise ValueError('Private token unavailable or invalid')
    results=[]
    for row,tree,ss,proof,sourcehash,target,url in plans:
        folder=E.SubElement(ss,'Item',{'class':'Folder','referent':'RBX_FOCAL_PRIVATE_CONNECTION'});p=E.SubElement(folder,'Properties');E.SubElement(p,'string',{'name':'Name'}).text='DEE_FOCAL_PrivateConnection'
        for key,value in [('BaseUrl',url),('InstanceId',row['instanceId']),('Token',token)]:
            item=E.SubElement(folder,'Item',{'class':'StringValue','referent':'RBX_FOCAL_PRIVATE_'+key});props=E.SubElement(item,'Properties');E.SubElement(props,'string',{'name':'Name'}).text=key;E.SubElement(props,'string',{'name':'Value'}).text=value
        with target.open('xb')as out:tree.write(out,encoding='utf-8',xml_declaration=True)
        if sha(row['sourceScene'])!=sourcehash:raise RuntimeError('Public source changed; preserve private file')
        results.append({'condition':row['condition'],'instanceId':row['instanceId'],'lifeId':proof['lifeId'],'sessionId':proof['sessionId'],'contextSha256':proof['contextSha256'],'privateScene':str(target),'privateSceneBytes':target.stat().st_size,'privateSceneSha256':sha(target),'publicSourceSha256':sourcehash,'baseUrl':url,'httpEnabled':True,'mode':'NATIVE','privateFolder':'DEE_FOCAL_PrivateConnection','credentialPrinted':False,'NativeImported':False,'nativeExecutedByAgent':False,'leasesAppliedByAgent':False})
    return{'schema':'DEE.Focal.PrivateScenes.FS.01','nativeExecutedByAgent':False,'NativeImported':False,'leasesAppliedByAgent':False,'credentialPrinted':False,'participants':results}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--registry',type=Path,required=True);p.add_argument('--relocated-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    result=make(a.registry,a.relocated_root)
    with a.output.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result,ensure_ascii=False))
