"""Offline scene packaging. Never opens Studio, DEE or a participant policy.

--build refuses an existing output. --refresh-existing-R05 requires the exact
current SHA and is restricted to this R05 mundo directory, preserving old bytes.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[1] / "revision_R04" / "continuacion_01" / "mundo" / "DEE_RBX01_R04_L4.rbxlx"
SOURCE_FILES = {"Config": "Config_C02.luau", "Body_C02": "Body_C02.luau",
                "Controller": "Controller_C02.server.luau", "EstadoPareja_C02": "EstadoPareja_C02.luau",
                "Bridge": "Bridge_mailbox_C02.luau", "ExportarRegistros_C02":"ExportarRegistros_C02.luau"}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def name(item): return item.findtext("Properties/string[@name='Name']")
def prop(item, tag, key, value=None):
    p = item.find("Properties")
    if p is None: p = ET.SubElement(item, "Properties")
    e = p.find(f"{tag}[@name='{key}']")
    if e is None: e = ET.SubElement(p, tag, {"name": key})
    if value is not None: e.text = str(value)
    return e

def set_xyz(item, tag, key, values):
    e=prop(item,tag,key)
    for axis,value in zip(("X","Y","Z"),values):
        ch=e.find(axis)
        if ch is None: ch=ET.SubElement(e,axis)
        ch.text=format(float(value),".12g")

def set_cf(item, position, direction=None):
    # Roblox CFrame.lookAt with world-up, serialized as row-major rotation.
    if direction is None: matrix=[1,0,0,0,1,0,0,0,1]
    else:
        dx,dy,dz=direction; mag=math.sqrt(dx*dx+dy*dy+dz*dz)
        look=(dx/mag,dy/mag,dz/mag); back=tuple(-v for v in look)
        right=(back[2],0,-back[0]); rm=math.sqrt(sum(v*v for v in right))
        right=tuple(v/rm for v in right)
        up=(back[1]*right[2]-back[2]*right[1],back[2]*right[0]-back[0]*right[2],back[0]*right[1]-back[1]*right[0])
        matrix=[right[0],up[0],back[0],right[1],up[1],back[1],right[2],up[2],back[2]]
    set_xyz(item,"CoordinateFrame","CFrame",position)
    e=prop(item,"CoordinateFrame","CFrame")
    for key,value in zip(("R00","R01","R02","R10","R11","R12","R20","R21","R22"),matrix):
        ch=e.find(key)
        if ch is None: ch=ET.SubElement(e,key)
        ch.text=format(value,".12g")

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def scale(a,s): return tuple(x*s for x in a)
def norm(a): return scale(a,1/math.sqrt(sum(v*v for v in a)))

def parse_config(source):
    positions={int(n):tuple(map(float,(x,y,z))) for n,x,y,z in re.findall(
        r"\[(\d+)\]\s*=\s*Vector3\.new\(\s*([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\)",source)}
    block=source.split("C.Edges={",1)[1].split("}\n",1)[0]
    edges={int(s):{0:int(a),1:int(b)} for s,a,b in re.findall(
        r"\[(\d+)\]\s*=\s*\{\s*\[0\]\s*=\s*(\d+)\s*,\s*\[1\]\s*=\s*(\d+)\s*\}",block)}
    labels={int(s):text for s,text in re.findall(r'\[(\d+)\]="([^"\n]+)"',source.split("C.ZoneNames=",1)[1].split("C.FreePorts=",1)[0])}
    assert set(positions)==set(edges)==set(labels)==set(range(6)),"CONFIG_GEOMETRY_INCOMPLETE"
    return positions,edges,labels

def make_part(template_part, label, pos, direction, size):
    obj=copy.deepcopy(template_part)
    for child in list(obj.findall("Item")): obj.remove(child)
    obj.set("referent","RBX_C02_"+hashlib.sha256(label.encode()).hexdigest()[:28])
    p=obj.find("Properties")
    for e in list(p):
        if e.tag=="UniqueId": p.remove(e)
    prop(obj,"string","Name",label);prop(obj,"bool","Anchored","true")
    prop(obj,"bool","CanCollide","true");prop(obj,"bool","CanQuery","true")
    prop(obj,"bool","CanTouch","false")
    prop(obj,"token","shape",1)
    prop(obj,"Color3uint8","Color3uint8",str(0xFF334B5C))
    set_xyz(obj,"Vector3","size",size);set_cf(obj,pos,direction)
    return obj

def install(root, sources):
    folder=next(x for x in root.findall(".//Item") if name(x)=="RBX01Server")
    existing={name(x):x for x in folder.findall("Item")}
    existing["Body_C02"]=existing.pop("Body_R04",existing.get("Body_C02"))
    assert all(k in existing for k in ("Config","Body_C02","Bridge","Controller"))
    for module in ("EstadoPareja_C02","ExportarRegistros_C02"):
        if module not in existing:
            state=copy.deepcopy(existing["Body_C02"])
            state.set("referent","RBX_C02_"+hashlib.sha256(module.encode()).hexdigest()[:28])
            for e in list(state.find("Properties")):
                if e.tag=="UniqueId":state.find("Properties").remove(e)
            folder.append(state);existing[module]=state
    for label,text in sources.items():
        obj=existing[label];prop(obj,"string","Name",label)
        prop(obj,"ProtectedString","Source",text)
        if obj.get("class")=="Script":prop(obj,"bool","Disabled","false")
    return folder

def geometry(root,positions,edges,labels):
    world=next(x for x in root.findall(".//Item") if name(x)=="RBX01")
    children={name(x):x for x in world.findall("Item")}
    assert all(k in children for k in ("DEE_Body","Gates","Pickups","Bridges"))
    body=children["DEE_Body"]; primary=body.findtext("Properties/Ref[@name='PrimaryPart']")
    assert any(x.get("referent")==primary for x in body.findall("Item")),"PRIMARY_PART_REF_INVALID"
    bridges=children["Bridges"]; template_part=next(x for x in bridges.findall("Item") if x.get("class")=="Part")
    for x in list(bridges.findall("Item")): bridges.remove(x)
    prop(bridges,"string","Name","Roads_C02")
    routes=[]
    for station,ports in sorted(edges.items()):
        for port,destination in sorted(ports.items()):
            start=positions[station];end=positions[destination];direction=norm(sub(end,start))
            lateral=scale((-direction[2],0,direction[0]),5)
            points=[start,add(start,lateral),add(end,lateral),end]
            routes.append({"station":station,"port":port,"destination":destination,"centerline_points":points,
                "basis":"Body_C02.execute points={start,start+lateral,finish+lateral,finish}"})
            for i,(a,b) in enumerate(zip(points,points[1:])):
                delta=sub(b,a);length=math.sqrt(sum(v*v for v in delta));center=scale(add(a,b),.5)
                center=(center[0],5.25,center[2])
                bridges.append(make_part(template_part,f"Road_C02_{station}_{port}_{i}",center,delta,(6,1.5,length+.2)))
            gate=next(x for x in children["Gates"].findall("Item") if name(x)==f"Gate_{station}_{port}")
            for label,value in (("Station",station),("Port",port)):
                item=next(x for x in gate.findall("Item")if name(x)==label)
                assert item.findtext("Properties/int64[@name='Value']")==str(value)
            point=add(add(start,scale(direction,26)),add(lateral,(0,1.1,0)))
            set_cf(gate,point,direction)
            # Phase 0 is free at every port, matching Body.new/updateGates.
            prop(gate,"bool","CanCollide","false");prop(gate,"float","Transparency",.8)
            prop(gate,"Color3uint8","Color3uint8",str(0xFF41E6B4))
            label=next((x for x in children.get("Labels",[]).findall("Item")if name(x)==f"ExitLabel_{station}_{port}"),None)
            if label is not None:set_cf(label,add(point,(0,4.2,0)))
    for part in children["Pickups"].findall("Item"):
        kind=next((x for x in part.findall("Item")if name(x)=="Kind"),None)
        if kind is not None:
            kind_value=kind.findtext("Properties/string[@name='Value']")
            assert kind_value in ("KEY","RESOURCE","DELIVERY")
            set_cf(part,positions[{"KEY":1,"RESOURCE":5,"DELIVERY":0}[kind_value]])
    if "Labels" in children:
        for item in children["Labels"].findall("Item"):
            m=re.fullmatch(r"Station_(\d)",name(item) or "")
            if m:
                station=int(m[1]);set_cf(item,add(positions[station],(0,7,0)))
                text=next((x for x in item.findall(".//Item")if x.get("class")=="TextLabel"),None)
                if text is not None:prop(text,"string","Text",f"{station:02d}  {labels[station]}")
    return world,routes,primary

def export_geometry(world):
    parts=[]
    for item in world.findall(".//Item"):
        if item.get("class") not in ("Part","MeshPart","UnionOperation","WedgePart"):continue
        cf=item.find("Properties/CoordinateFrame[@name='CFrame']");size=item.find("Properties/Vector3[@name='size']")
        if cf is None or size is None:continue
        pose=[float(cf.findtext(k,"0")) for k in ("X","Y","Z","R00","R01","R02","R10","R11","R12","R20","R21","R22")]
        color=int(item.findtext("Properties/Color3uint8[@name='Color3uint8']","4294967295"))
        parts.append({"name":name(item),"referent":item.get("referent"),"position":pose[:3],"pose12":pose,
            "size":[float(size.findtext(k))for k in ("X","Y","Z")],"color":[(color>>16)&255,(color>>8)&255,color&255],
            "transparency":float(item.findtext("Properties/float[@name='Transparency']","0")),
            "part_class":item.get("class"),"shape":int(item.findtext("Properties/token[@name='shape']","1"))})
    return parts

def local_cframe(parent,child):
    """Exact rigid transform P^-1 C, using XML row-major CFrames."""
    pr=[parent[3+i*3:6+i*3]for i in range(3)];cr=[child[3+i*3:6+i*3]for i in range(3)]
    delta=[child[i]-parent[i]for i in range(3)]
    xyz=[sum(pr[k][i]*delta[k]for k in range(3))for i in range(3)]
    rot=[sum(pr[k][i]*cr[k][j]for k in range(3))for i in range(3)for j in range(3)]
    return xyz+rot

def main():
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--build",action="store_true");g.add_argument("--refresh-existing-R05",action="store_true")
    p.add_argument("--expected-sha256");p.add_argument("--output",default="DEE_RBX01_C02.rbxlx")
    p.add_argument("--fingerprint","--scenario-fingerprint",dest="fingerprint")
    p.add_argument("--max-cycles",type=int,choices=(4,6,42,48));p.add_argument("--suspend-after",type=int,choices=(2,3,14,16))
    p.add_argument("--dev-signs-reversed",action="store_true")
    p.add_argument("--dev-operands",type=int,nargs=3,metavar=("A_LEFT","A_RIGHT","B_RIGHT"))
    p.add_argument("--control-signs-reversed",action="store_true")
    p.add_argument("--control-operands",type=int,nargs=3,metavar=("A_LEFT","A_RIGHT","B_RIGHT"))
    p.add_argument("--participant",choices=("LIVE_NATIVE","PROGRAMMED","CONVENTIONAL_AI"));a=p.parse_args()
    target=(HERE/a.output).resolve()
    assert target.parent==HERE and target.suffix==".rbxlx" and target.name.startswith("DEE_RBX01_C02"),"OUTPUT_OUTSIDE_R05_DENIED"
    if a.build:assert not target.exists(),"BUILD_TARGET_EXISTS"
    else:
        assert target.is_file() and a.expected_sha256 and sha(target)==a.expected_sha256,"REFRESH_SHA_MISMATCH"
        preserved=HERE/(target.stem+"_pre_refresh_"+a.expected_sha256[:12]+".rbxlx")
        if preserved.exists():assert sha(preserved)==a.expected_sha256
        else:preserved.write_bytes(target.read_bytes())
    template_hash=sha(TEMPLATE);tree=ET.parse(TEMPLATE);root=tree.getroot()
    sources={key:(HERE/filename).read_text(encoding="utf-8-sig")for key,filename in SOURCE_FILES.items()}
    config=sources["Config"]
    assert 'C.AutoStart="NONE"' in config
    if a.fingerprint:
        assert re.fullmatch(r"[0-9a-f]{64}",a.fingerprint)
        config=re.sub(r'C.ScenarioFingerprint=[^\n]+',f'C.ScenarioFingerprint="{a.fingerprint}" -- Explicit packaging override.',config)
    if a.max_cycles:config=re.sub(r"C.MaxCycles=\d+",f"C.MaxCycles={a.max_cycles}",config)
    if a.suspend_after:config=re.sub(r"C.SuspendAfter=\d+",f"C.SuspendAfter={a.suspend_after}",config)
    if a.max_cycles==42:assert a.suspend_after==14,"MAIN42_REQUIRES_PROSPECTIVE_SUSPEND14"
    if a.participant:config=re.sub(r'C.Participant="[^"]+"',f'C.Participant="{a.participant}"',config)
    if a.max_cycles==6:
        assert a.suspend_after==3 and "CTRL6"in target.stem,"CONTROL6_REQUIRES_EXPLICIT_OUTPUT_AND_BOUNDARY"
        config='-- SIX-CYCLE PAIRED CONTROL ONLY. Not the 48-cycle evaluation.\n'+config
        config=config.replace('C.WorldId="RBX01_R05_C02_V1"','C.WorldId="RBX01_R05_C02_CTRL6"')
    if a.dev_signs_reversed or a.dev_operands:
        assert a.max_cycles==4 and a.suspend_after==2 and "DEV" in target.stem,"DEV_OVERRIDE_REQUIRES_EXPLICIT_DEV4_OUTPUT_AND_BOUNDARY"
        config='-- DEVELOPMENT INTERFACE CHECK ONLY. Not a reserved evaluation.\n'+config
        config=config.replace('C.WorldId="RBX01_R05_C02_V1"','C.WorldId="RBX01_R05_C02_DEV4"')
    if a.control_signs_reversed or a.control_operands:
        assert a.max_cycles==6 and a.suspend_after==3 and "CTRL6"in target.stem,"CONTROL_OVERRIDE_REQUIRES_EXPLICIT_CTRL6_OUTPUT_AND_BOUNDARY"
    if a.dev_signs_reversed or a.control_signs_reversed:
        config,count=re.subn(r"function C.SignsAtCycle\(cycle\).*?\nend",'function C.SignsAtCycle(cycle)\n    return {luma=-1,nara=1}\nend',config,count=1,flags=re.S)
        assert count==1
    operands=a.dev_operands or a.control_operands
    if operands:
        x,y,z=operands;assert all(0<=v<=32 for v in (x,y,z))
        variant="PAIRED_CONTROL6"if a.control_operands else"DEVELOPMENT_INTERFACE"
        config,count=re.subn(r"function C.OperandsAtCycle\(cycle\).*?\nend",f'function C.OperandsAtCycle(cycle)\n    return {{aLeft={x},aRight={y},bRight={z},variant="{variant}"}}\nend',config,count=1,flags=re.S)
        assert count==1
    sources["Config"]=config
    positions,edges,labels=parse_config(config);install(root,sources)
    world,routes,primary=geometry(root,positions,edges,labels)
    refs=[x.get("referent")for x in root.findall(".//Item")];assert len(refs)==len(set(refs)),"DUPLICATE_REFERENT"
    missing=[e.text for e in root.findall(".//Ref")if e.text not in (None,"null") and e.text not in refs]
    assert not missing,("UNRESOLVED_REF",missing)
    payload=ET.tostring(root,encoding="utf-8",xml_declaration=True)
    ET.fromstring(payload);assert sha(TEMPLATE)==template_hash,"ORIGINAL_CHANGED"
    target.write_bytes(payload)
    all_parts=export_geometry(world)
    body=next(x for x in world.findall("Item")if name(x)=="DEE_Body")
    body_refs={x.get("referent")for x in body.findall(".//Item")}
    reference=next(x for x in all_parts if x["referent"]==primary)
    body_parts=[dict(x,local_pose12=local_cframe(reference["pose12"],x["pose12"]))for x in all_parts if x["referent"]in body_refs]
    geometry_parts=[x for x in all_parts if x["referent"]not in body_refs]
    body_size=reference["size"]
    metadata={"mode":"OFFLINE_XML_PACKAGING_NOT_AN_EXECUTION","template":str(TEMPLATE),"template_sha256":template_hash,
        "output":str(target),"bytes":target.stat().st_size,"sha256":sha(target),"auto_start":"NONE","primary_part_referent":primary,
        "source_files":{key:{"path":str(HERE/filename),"sha256":sha(HERE/filename),"embedded_sha256":hashlib.sha256(sources[key].encode()).hexdigest()}for key,filename in SOURCE_FILES.items()},
        "overrides":{"fingerprint":a.fingerprint,"max_cycles":a.max_cycles,"suspend_after":a.suspend_after,"participant":a.participant,
            "dev_signs_reversed":a.dev_signs_reversed,"dev_operands":a.dev_operands,
            "control_signs_reversed":a.control_signs_reversed,"control_operands":a.control_operands},
        "source_reference":"Sources captured now; refresh required after any later source edit.",
        "geometry_scope":"EDIT initial parts only, excludes runtime-created devices/panels/contact markers. Root must export runtime geometry after Body.new.",
        "positions":positions,"edges":edges,"routes":routes,"parts":geometry_parts,"body_parts":body_parts,
        "body_reference_pose12":reference["pose12"],"framing_points":list(positions.values()),"body_size":body_size,
        "validation":{"xml_reparsed":True,"referents_unique":True,"references_resolved":True,"template_preserved":True,"roads":36}}
    report=target.with_suffix(".geometry.json");report.write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:metadata[k]for k in ("output","bytes","sha256","template_sha256","validation")},ensure_ascii=False))

if __name__=="__main__":main()
