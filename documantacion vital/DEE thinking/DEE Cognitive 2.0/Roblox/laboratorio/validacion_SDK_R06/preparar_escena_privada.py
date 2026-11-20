"""Prepare one owned local Place copy. Never print credentials or open DEE."""
from pathlib import Path
import argparse, hashlib, json, xml.etree.ElementTree as E

def name(item):
    p=item.find("Properties")
    return None if p is None else next((x.text for x in p if x.get("name")=="Name"),None)

def make(source, connection, target):
    source=Path(source).resolve(strict=True); connection=Path(connection).resolve(strict=True)
    target=Path(target).resolve()
    if target.exists(): raise FileExistsError(target)
    if target.parent != source.parents[2]: raise ValueError("Explicit relocated validation root only")
    tree=E.parse(source); root=tree.getroot()
    cfg=[x for x in root.iter("Item") if name(x)=="SDKConfig"]
    if len(cfg)!=1: raise ValueError("One config")
    code=next(x for x in cfg[0].find("Properties") if x.get("name")=="Source")
    if code.text.count('"Mode": "PREVIEW"')!=1: raise ValueError("Exact public preview config")
    code.text=code.text.replace('"Mode": "PREVIEW"','"Mode": "NATIVE"')
    ss=next((x for x in root.findall("Item") if x.get("class")=="ServerStorage"),None)
    if ss is None:
        ss=E.SubElement(root,"Item",{"class":"ServerStorage","referent":"RBX_SDK_PRIVATE_SS"})
        p=E.SubElement(ss,"Properties"); E.SubElement(p,"string",{"name":"Name"}).text="ServerStorage"
    if any(name(x)=="DEE_SDK_PrivateConnection" for x in ss.findall("Item")): raise ValueError("Existing private connection")
    folder=E.parse(connection).getroot().find("Item")
    if folder is None or name(folder)!="DEE_SDK_PrivateConnection": raise ValueError("Private connection file")
    ss.append(folder)
    hs=next((x for x in root.findall("Item") if x.get("class")=="HttpService"),None)
    if hs is None:
        hs=E.SubElement(root,"Item",{"class":"HttpService","referent":"RBX_SDK_LOCAL_HTTP"})
        p=E.SubElement(hs,"Properties"); E.SubElement(p,"string",{"name":"Name"}).text="HttpService"
    p=hs.find("Properties"); enabled=next((x for x in p if x.get("name")=="HttpEnabled"),None)
    if enabled is None: enabled=E.SubElement(p,"bool",{"name":"HttpEnabled"})
    enabled.text="true"
    with target.open("xb") as out: tree.write(out,encoding="utf-8",xml_declaration=True)
    return {"privateScene":str(target),"bytes":target.stat().st_size,"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"publicSourceChanged":False,"NativeOpened":False,"credentialPrinted":False,"changes":["Mode NATIVE","private ServerStorage connection","owned local Place HttpEnabled"]}

if __name__=="__main__":
    a=argparse.ArgumentParser(); a.add_argument("--source",required=True); a.add_argument("--connection",required=True); a.add_argument("--target",required=True); v=a.parse_args()
    print(json.dumps(make(v.source,v.connection,v.target),ensure_ascii=False))
