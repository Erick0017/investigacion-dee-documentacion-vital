"""Create local Studio connection data without printing its bearer token.

The .rbxmx is PRIVATE transport configuration, excluded from every public ZIP
and Agent/World snapshot. No DEE/Studio APIs are called by this helper.
"""
from pathlib import Path
import argparse
import sys
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sdk_common import RUNTIME, INSTANCE, canonical, read, sha

def create(instance_id):
    if INSTANCE.fullmatch(instance_id) is None: raise ValueError('Explicit SDK instance ID')
    connection = read(RUNTIME / 'configuracion/CONEXION_PRIVADA.json')
    if connection['bind'] != '127.0.0.1' or len(connection['token']) < 32: raise ValueError('Private loopback connection only')
    root = ET.Element('roblox', {'version': '4'})
    folder = ET.SubElement(root, 'Item', {'class': 'Folder', 'referent': 'RBX_DEE_PRIVATE_CONNECTION'})
    properties = ET.SubElement(folder, 'Properties'); ET.SubElement(properties, 'string', {'name': 'Name'}).text = 'DEE_SDK_PrivateConnection'
    for name, value in (('BaseUrl', 'http://127.0.0.1:' + str(connection['port'])), ('InstanceId', instance_id), ('Token', connection['token'])):
        node = ET.SubElement(folder, 'Item', {'class': 'StringValue', 'referent': 'RBX_PRIVATE_' + name})
        props = ET.SubElement(node, 'Properties'); ET.SubElement(props, 'string', {'name': 'Name'}).text = name
        ET.SubElement(props, 'string', {'name': 'Value'}).text = value
    path = RUNTIME / 'configuracion' / ('INYECCION_LOCAL_' + instance_id + '.rbxmx')
    with path.open('xb') as out: out.write(ET.tostring(root, encoding='utf-8', xml_declaration=True))
    return {'privateFile': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path),
            'tokenPrinted': False, 'publicDistribution': False, 'NativeOpened': False}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--instance', required=True)
    print(canonical(create(p.parse_args().instance)))
