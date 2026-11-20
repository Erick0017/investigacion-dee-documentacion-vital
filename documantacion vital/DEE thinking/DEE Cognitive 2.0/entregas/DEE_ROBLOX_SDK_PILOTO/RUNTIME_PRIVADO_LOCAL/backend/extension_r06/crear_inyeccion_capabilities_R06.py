"""Private EXT connection data only. No Native/Studio and no token in stdout."""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r06'))
from sdk_common import RUNTIME,canonical,instance_home,read,sha

def create(instance,port=8899):
    home,cfg=instance_home(instance)
    if not(home/'sistema/capacidades/SDK_CAPABILITIES_SCOPE_R06.json').is_file():
        raise ValueError('Install the closed post-K4 capabilities scope first')
    if type(port) is not int or not 1024<=port<=65535:raise ValueError('Unprivileged loopback port')
    connection=read(RUNTIME/'configuracion/CONEXION_PRIVADA.json')
    if connection['bind']!='127.0.0.1' or len(connection['token'])<32:raise ValueError('Private loopback only')
    root=ET.Element('roblox',{'version':'4'})
    folder=ET.SubElement(root,'Item',{'class':'Folder','referent':'RBX_CAP_PRIVATE'})
    props=ET.SubElement(folder,'Properties');ET.SubElement(props,'string',{'name':'Name'}).text='DEE_SDK_CAPABILITIES_PrivateConnection_R06'
    for name,value in (('BaseUrl','http://127.0.0.1:'+str(port)),('InstanceId',instance),('Token',connection['token'])):
        node=ET.SubElement(folder,'Item',{'class':'StringValue','referent':'RBX_CAP_PRIVATE_'+name})
        fields=ET.SubElement(node,'Properties');ET.SubElement(fields,'string',{'name':'Name'}).text=name
        ET.SubElement(fields,'string',{'name':'Value'}).text=value
    path=RUNTIME/'configuracion'/('INYECCION_CAPABILITIES_R06_'+instance+'.rbxmx')
    with path.open('xb') as f:f.write(ET.tostring(root,encoding='utf8',xml_declaration=True))
    return {'privateFile':str(path),'sha256':sha(path),'bytes':path.stat().st_size,
            'tokenPrinted':False,'NativeOpened':False,'publicDistribution':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--instance',required=True);p.add_argument('--port',type=int,default=8899)
    a=p.parse_args();print(canonical(create(a.instance,a.port)))
