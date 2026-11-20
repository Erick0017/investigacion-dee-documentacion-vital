#!/usr/bin/env python3
"""Comprueba sólo el parche de guarda focalR03. Sin ejecutar Studio/Native/HTTP ni enumerartrayectorias."""
import argparse,hashlib,json,pathlib,xml.etree.ElementTree as ET

def src(root):
    out={}
    for i in root.iter('Item'):
        p=i.find('Properties')
        if p is None:continue
        n=p.find("string[@name='Name']");s=p.find("ProtectedString[@name='Source']")
        if n is not None and s is not None:
            assert n.text not in out
            out[n.text]=(i.attrib['class'],s.text or '')
    return out

def run(h):
    checks=[]
    def check(n,v):assert v,n;checks.append({'name':n,'passed':True})
    for arm in ('CONSUME_RECHARGE','NONCONSUMING_CONTROL'):
        old=src(ET.parse(h/('DEE_FOCAL_'+arm+'_R02.rbxlx')).getroot())
        new=src(ET.parse(h/('DEE_FOCAL_'+arm+'_R03.rbxlx')).getroot())
        check('only_guard_and_startup_changed_'+arm,all(new[k]==v for k,v in old.items() if k!='SDK_Arranque') and set(new)==set(old)|{'FocalHttpLoop'})
        check('guard_source_exact_'+arm,new['FocalHttpLoop'][1]==(h/'FocalHttpLoop_R03.luau').read_text(encoding='utf-8'))
        check('startup_native_requires_guard_'+arm,new['SDK_Arranque'][1]==(h/'SDK_Arranque_FOCAL_R03.server.luau').read_text(encoding='utf-8') and 'package.FocalHttpLoop' in new['SDK_Arranque'][1])
        guard=new['FocalHttpLoop'][1]
        check('profile_and_condition_before_original_loop_'+arm,guard.index('contract.profile=="FOCAL"')<guard.index('return OriginalLoop.start(cfg)') and 'contract.focalCondition==condition' in guard)
    package=ET.parse(h/'DEEConnector_FOCAL_R03.rbxmx').getroot()
    check('export_is_single_model',len(package.findall('Item'))==1 and package.find('Item').attrib['class']=='Model')
    check('export_matches_treatment_scene',src(package)==src(ET.parse(h/'DEE_FOCAL_CONSUME_RECHARGE_R03.rbxlx').getroot()))
    return {'schema':'DEE.Focal.GuardCheck.R03','nativeExecuted':False,'studioExecuted':False,'httpRequested':False,'repeatedEnvironmentTraceEnumeration':False,'LuauCompilation':'PENDING_ROOT','checks':checks,'passed':True}

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
r=run(pathlib.Path(__file__).resolve().parent)
with a.output.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2,ensure_ascii=False);f.write('\n')
print(json.dumps({'passed':True,'checks':len(r['checks']),'nativeExecuted':False},ensure_ascii=False))
