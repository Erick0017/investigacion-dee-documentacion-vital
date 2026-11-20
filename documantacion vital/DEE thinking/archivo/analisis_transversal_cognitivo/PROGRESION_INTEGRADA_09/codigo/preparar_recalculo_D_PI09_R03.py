"""Prepare STATE-only documentary identity correction; no evidence modified."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'RECALCULAR_D_PI09_R02.py';dst=H/'RECALCULAR_D_PI09_R03.py'
data=src.read_bytes();assert hashlib.sha256(data).hexdigest()=='e3a023340c20f209e5f20b52f6e67e9c8d94c2894534067fe2f39b8209a23dc3'
text=data.decode('utf-8-sig')
changes=[
 ("                for rid,r in direct.items():require(r['site']==[52,48,48]and r['direction']==[0,0,0]and r['payload']==0 and r['requested_tick']==row['before_tick']+2,'Fixed support position/calendar')", "                for r in row['requests']:require(r['id']in direct and r['site']==[52,48,48]and r['direction']==[0,0,0]and r['payload']==0 and r['requested_tick']==row['before_tick']+2,'Fixed support position/calendar; receipt normalized separately')"),
('return_plans={};closures=[]','return_plans={};closures=[];closure_primary_identities={}'),
("        require(closed['new_Native_ticks']==closed['final_tick']-closed['initial_tick'],'Closure tick denominator')", """        require(closed['new_Native_ticks']==closed['final_tick']-closed['initial_tick'],'Closure tick denominator')
        for record in closed['records']:
            key=(item['arm'],record['sha256'])
            require(key not in closure_primary_identities or closure_primary_identities[key]==closed['life_id'],'Conflicting hashed closure identity')
            closure_primary_identities[key]=closed['life_id']"""),
("            life=row.get('life_id');group=(life,arm);require(life,'D row requires actual life identity')", """            closure_life=closure_primary_identities.get((arm,item['sha256']))
            require(closure_life is not None,'Each literal primary must belong to its actual hashed closed phase')
            if 'first_stage'not in row and not('P0_guard'in row and 'ready'in row):
                require({'present','progress','physical','new_native_ticks'}<=set(row)and row['new_native_ticks']==0,'Only a fixed zero-tick STATE may derive its outer identity from the actual closure')
                progress=row['progress'];life=row.get('life_id')or(progress.get('life_id')if progress else None)or closure_life
                require(life==closure_life,'STATE progress/closure identity differs')
                aux.append({'arm':arm,'life_id':life,'file':item['file'],'present':row['present'],'ordinal':progress.get('ordinal')if progress else None,'pending':progress.get('pending')if progress else None,'identity_scope':'Zero-tick STATE bound to the exact hashed primary member of its actual closed phase; never an invented episode identity'})
                continue
            life=row.get('life_id');require(life is not None and life==closure_life,'Material preparation/episode must carry its explicit actual life identity; no fallback')
            group=(life,arm)"""),
("            if 'first_stage'not in row:\n                progress=row.get('progress');aux.append({'arm':arm,'file':item['file'],'present':row.get('present'),'ordinal':progress.get('ordinal')if progress else None,'pending':progress.get('pending')if progress else None});continue\n",''),
("'schema':'DEE.PI09.D.recalculated_persistent_environment.R02'", "'schema':'DEE.PI09.D.recalculated_persistent_environment.R03','scientific_family':'DEE.PI09.persistent_environment.D.R02','technical_revision':'Only zero-tick STATE identity from its exact hashed closure; material rows still require explicit life_id'"),
]
for old,new in changes:
    assert text.count(old)==1,old[:100]
    text=text.replace(old,new)
ast.parse(text)
with dst.open('x',encoding='utf8',newline='\n')as f:f.write(text)
print(json.dumps({'file':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'Native_executed':False,'source_R02_preserved':True,'primary_or_index_modified':False}))
