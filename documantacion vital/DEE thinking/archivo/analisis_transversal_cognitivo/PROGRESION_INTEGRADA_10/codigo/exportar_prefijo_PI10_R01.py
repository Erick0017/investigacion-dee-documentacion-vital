"""Closed PI10 paired-export adaptation; Root only, no Native import/steps.

Uses the reviewed current-D exporter literally except its explicit source and
destination identity guards. Exact common P0/fork preservation, not a reset.
"""
from pathlib import Path
import argparse,ast,hashlib,json,re,types
P=Path(__file__).resolve().parents[1]
SOURCE=P/'codigo/exportar_principal_cerrado_PI10_R01.py'
SOURCE_SHA='8250c77947687afa6cd97a7eb3e53f8feb5f08e13fb44124f3610e802331cbad'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def adapt(a):
 need(hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA,'Reviewed source exporter changed')
 system=a.sistema.resolve(strict=True);need(system.name=='sistema'and system.parent.parent==(P/'estados').resolve()and not(system/'estado/ACTIVO.json').exists(),'Exact isolated unselected PI10 source only')
 need(re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9_]{1,25}',a.vida)and re.fullmatch(r'[A-Z][A-Z0-9_]{0,60}',a.nombre),'Exact PI10 life and fresh pair name required')
 text=SOURCE.read_text('utf-8-sig')
 old="dest=(P/'pares'/('PRINCIPAL_D_T'+str(a.tick))).resolve()"
 need(text.count(old)==1,'Reviewed export destination anchor changed');text=text.replace(old,"dest=(P/'pares'/a.nombre).resolve()")
 old="activefile=S/'estado/ACTIVO.json';active=read(activefile);need(active['life_id']==LIFE,'Changed main: reconcile genealogy, never take highest tick')"
 new="activefile=C/'sistema/estado/ACTIVO.json';active=read(activefile);need(active['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'and active['tick']==922371 and active['snapshot_sha256']=='72743ad2fc708e41c2529af8f7192fe1087184562e4cd094f469384faedcd331','Protected original main advanced: reconcile before copying old futures')"
 need(text.count(old)==1,'Reviewed selector guard anchor changed');text=text.replace(old,new)
 old="and active['tick']==a.tick and card['snapshot_sha256']==active['snapshot_sha256']==sha(snapshot)==a.snapshot_sha256"
 new="and card['snapshot_sha256']==sha(snapshot)==a.snapshot_sha256"
 need(text.count(old)==1,'Reviewed current-card guard changed');text=text.replace(old,new)
 ast.parse(text);m=types.ModuleType('PI10_closed_full_pair_export_identity_adaptation');m.__file__=str(SOURCE);exec(compile(text,str(SOURCE)+':PI10_closed_source_identity_only','exec'),m.__dict__)
 m.S=system;m.LIFE=a.vida
 return m
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--sistema',type=Path,required=True);ap.add_argument('--vida',required=True);ap.add_argument('--nombre',required=True);ap.add_argument('--tick',type=int,required=True);ap.add_argument('--snapshot-sha256',required=True);ap.add_argument('--exportar',action='store_true');a=ap.parse_args()
 m=adapt(a)
 if a.exportar:m.export(a)
 else:print(json.dumps({'mode':'PLAN_ONLY','source':str(a.sistema),'life_id':a.vida,'destination':str(P/'pares'/a.nombre),'new_Native_ticks':0}))
if __name__=='__main__':main()
