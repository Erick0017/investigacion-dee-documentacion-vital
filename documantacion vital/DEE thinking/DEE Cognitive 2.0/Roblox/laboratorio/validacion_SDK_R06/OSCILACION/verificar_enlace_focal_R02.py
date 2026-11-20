#!/usr/bin/env python3
"""Comprobación de enlace XML/fuentes focales. Cero Native/Studio/HTTP; no repite trazas ambientales."""
import argparse,hashlib,json,pathlib,xml.etree.ElementTree as ET

def sources(root):
    found={}
    for item in root.iter('Item'):
        p=item.find('Properties')
        if p is None:continue
        n=p.find("string[@name='Name']");s=p.find("ProtectedString[@name='Source']")
        if n is not None and s is not None:
            assert n.text not in found
            found[n.text]=(item.attrib['class'],s.text or '')
    return found

def run(home):
    kit=home.parents[1]/'KIT_DESARROLLADOR'
    kit_sources=sources(ET.parse(kit/'conector/DEEConnector_SDK_0_1_0.rbxmx').getroot())
    configs={};trees={};checks=[]
    def check(name,v):
        assert v,name
        checks.append({'name':name,'passed':True})
    for arm in ('CONSUME_RECHARGE','NONCONSUMING_CONTROL'):
        cfg=json.loads((home/('CONFIG_SDK_FOCAL_'+arm+'.json')).read_text(encoding='utf-8'));configs[arm]=cfg
        tree=ET.parse(home/('DEE_FOCAL_'+arm+'_R02.rbxlx')).getroot();src=sources(tree);trees[arm]=src
        check('original_and_HTTP_sources_unchanged_'+arm,all(src[k]==v for k,v in kit_sources.items() if k!='SDKConfig'))
        check('fixed_scope_and_safe_default_'+arm,cfg['Mode']=='PREVIEW' and cfg['MaxOpportunities']==6 and cfg['RunCycles']==6 and cfg['MaxActions']==12 and cfg['PrivateConnectionFolder']=='DEE_FOCAL_PrivateConnection')
        check('separate_map_adapter_and_rule_'+arm,cfg['MapModule']=='MapaFocal' and cfg['AdapterModule']=='FocalAdapters' and cfg['Focal']['Arm']==arm and cfg['Focal']['rechargeEpochs']==3)
        for name,file in [('MapaFocal','MapaFocal_R02.luau'),('FocalAdapters','FocalAdapters_R02.luau'),('DisponibilidadLocal','DisponibilidadLocal_R02.luau')]:
            check('embedded_source_'+name+'_'+arm,src[name][1]==(home/file).read_text(encoding='utf-8'))
        check('actual_server_bootstrap_'+arm,src['SDK_Arranque'][0]=='Script')
        check('no_secret_connection_or_HTTP_enable_embedded_'+arm,not any(n.text=='DEE_FOCAL_PrivateConnection' for n in tree.findall(".//Item/Properties/string[@name='Name']")) and not any(i.attrib.get('class')=='HttpService' for i in tree.iter('Item')))
    a,b=configs.values()
    check('same_geometry_and_mechanism',a['Map']==b['Map'] and {k:v for k,v in a['Focal'].items() if k!='Arm'}=={k:v for k,v in b['Focal'].items() if k!='Arm'})
    check('no_anatomical_self_edges',all(a['Focal']['edges'][str(s)][str(p)]!=s for s in range(6)for p in (0,1)))
    adapter=trees['CONSUME_RECHARGE']['FocalAdapters'][1]
    check('existing_local_sensor_path',all(v in adapter for v in ['law:quoteLocal(station,motor.root)','state.signal=sample.signal','stationSignal=state.signal','publicContactCode=station','contactCode(true)==target']))
    check('version_unchanged',(kit.parent/'VERSION.txt').read_text(encoding='utf-8').strip()=='0.1.0')
    pins=json.loads((kit/'pruebas/PINES_PUBLICOS_0_1_0.json').read_text(encoding='utf-8'))['files']
    check('closed_KIT_code_unchanged',all(hashlib.sha256((kit/n).read_bytes()).hexdigest()==p['sha256']for n,p in pins.items()))
    return {'schema':'DEE.Focal.LinkPreflight.R02','nativeExecuted':False,'studioExecuted':False,'httpRequested':False,'environmentTraceEnumerationRepeated':False,'LuauCompilation':'PENDING_ROOT_STUDIO','actualNativeExposure':'NOT_EXECUTED','checks':checks,'passed':True}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
    r=run(pathlib.Path(__file__).resolve().parent)
    with a.output.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'passed':r['passed'],'checks':len(r['checks']),'nativeExecuted':False,'output':str(a.output)},ensure_ascii=False))
if __name__=='__main__':main()
