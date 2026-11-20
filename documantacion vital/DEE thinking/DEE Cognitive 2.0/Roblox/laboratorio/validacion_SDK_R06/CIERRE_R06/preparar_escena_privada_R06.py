"""FS-only privateR06 Place. Reads a privateconnectionXML; never prints token or opensNative."""
from pathlib import Path
import argparse,copy,hashlib,json,re,xml.etree.ElementTree as E

def name(i):
 p=i.find('Properties');return None if p is None else next((x.text for x in p if x.get('name')=='Name'),None)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def make(source,connection,target,auto_end=False):
 source=Path(source).resolve(strict=True);connection=Path(connection).resolve(strict=True);target=Path(target).resolve()
 if target.exists():raise FileExistsError(target)
 if target==source or target.is_relative_to(source.parents[1]):raise ValueError('Private target must be outside publicKIT')
 tree=E.parse(source);root=tree.getroot();configs=[x for x in root.iter('Item')if name(x)=='SDKConfig']
 if len(configs)!=1:raise ValueError('Oneconfig')
 s=next(x for x in configs[0].find('Properties')if x.get('name')=='Source');m=re.search(r'\[=\[(.*?)\]=\]',s.text,re.S)
 if m is None:raise ValueError('Configenvelope')
 c=json.loads(m.group(1))
 if c['Version']!='0.1.1'or c['Mode']!='PREVIEW'or c['PrivateConnectionFolder']!='DEE_SDK_PrivateConnection_R06':raise ValueError('ExactR06source')
 c['Mode']='NATIVE';c['AutoEndStudioTest']=bool(auto_end);s.text=s.text[:m.start(1)]+'\n'+json.dumps(c,ensure_ascii=False,indent=2)+'\n'+s.text[m.end(1):]
 ss=next((x for x in root.findall('Item')if x.get('class')=='ServerStorage'),None)
 if ss is None:
  ss=E.SubElement(root,'Item',{'class':'ServerStorage','referent':'R06_PRIVATE_SS'});p=E.SubElement(ss,'Properties');E.SubElement(p,'string',{'name':'Name'}).text='ServerStorage'
 if any(name(x)==c['PrivateConnectionFolder']for x in ss.findall('Item')):raise ValueError('Existingprivatefolder')
 folder=E.parse(connection).getroot().find('Item')
 if folder is None or name(folder)!=c['PrivateConnectionFolder']:raise ValueError('ExactprivatefolderR06')
 values={name(x):next((v.text for v in x.find('Properties')if v.get('name')=='Value'),None)for x in folder.findall('Item')}
 if set(values)!={'BaseUrl','InstanceId','Token'}or not isinstance(values['Token'],str)or len(values['Token'])<32:raise ValueError('Privateconnectionfields')
 if re.fullmatch(r'http://127\.0\.0\.1:[0-9]+',values['BaseUrl']or'')is None:raise ValueError('Privateloopbackonly')
 ss.append(copy.deepcopy(folder));hs=next((x for x in root.findall('Item')if x.get('class')=='HttpService'),None)
 if hs is None:
  hs=E.SubElement(root,'Item',{'class':'HttpService','referent':'R06_PRIVATE_HTTP'});p=E.SubElement(hs,'Properties');E.SubElement(p,'string',{'name':'Name'}).text='HttpService'
 p=hs.find('Properties');v=next((x for x in p if x.get('name')=='HttpEnabled'),None)
 if v is None:v=E.SubElement(p,'bool',{'name':'HttpEnabled'})
 v.text='true';original=sha(source)
 with target.open('xb')as out:tree.write(out,encoding='utf-8',xml_declaration=True)
 if sha(source)!=original:raise RuntimeError('Publicsourcechanged')
 return{'schema':'DEE.SDK.PrivateScene.R06','sourceSha256':original,'privateScene':str(target),'privateSceneSha256':sha(target),'bytes':target.stat().st_size,'mode':'NATIVE','AutoEndStudioTest':bool(auto_end),'httpEnabledLocalPlace':True,'NativeExecuted':False,'credentialPrinted':False}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--connection',required=True);p.add_argument('--target',required=True);p.add_argument('--auto-end-studio-test',action='store_true');a=p.parse_args()
 print(json.dumps(make(a.source,a.connection,a.target,a.auto_end_studio_test),ensure_ascii=False))
