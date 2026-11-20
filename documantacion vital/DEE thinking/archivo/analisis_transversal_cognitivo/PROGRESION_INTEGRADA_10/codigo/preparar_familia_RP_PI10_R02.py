"""Stage prospective R02 family12 tools only, no registration/material copy.

Neutral P02 manifest/tick must come from the actual later recipe binding;
there is no guessed future snapshot or current-principal selection dependency.
"""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;outputs=[]
def put(name,text):
 ast.parse(text);p=H/name
 if p.exists():assert p.read_text('utf8')==text
 else:
  with p.open('x',encoding='utf8')as f:f.write(text)
 outputs.append({'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
t=(H/'pi10_vinculo_reproduccion_R01.py').read_text('utf8')
for old,new in(('DEE.PI10.diagnostic_family.identity_binding.R01','DEE.PI10.diagnostic_family.identity_binding.R02'),('pi10_consulta18_familia_desde_P0_T922374_R01','pi10_consulta12_familia_desde_P02_R02'),('PI10_CONSULTA18_FAMILIA_R01','PI10_CONSULTA12_FAMILIA_R02'),('PI10_RPF_','PI10_RPF2_'),('PI10_P0_01','PI10_P02_01'),('PI10_EXPERIMENTO_R01.json','PI10_EXPERIMENTO_R02.json'),('DEE.PI10.fixed_experiment_scope.R01','DEE.PI10.fixed_experiment_scope.R02'),('real18','real12'),('VINCULO_FAMILIA_PI10_R01','VINCULO_FAMILIA_PI10_R02'),('full_P0_manifest_sha256','full_P02_manifest_sha256')):t=t.replace(old,new)
old="context['prefix_manifest_sha256']==P0_SHA";new="context['prefix_manifest_sha256']==binding['neutral_P02_manifest_sha256']";assert old in t;t=t.replace(old,new)
old="'full_P02_manifest_sha256':P0_SHA";new="'full_P02_manifest_sha256':context['prefix_manifest_sha256']";assert old in t;t=t.replace(old,new)
put('pi10_vinculo_reproduccion_R02.py',t)
t=(H/'pi10_guardia_reproduccion_R01.py').read_text('utf8')
for old,new in(('pi10_consulta18_familia_desde_P0_T922374_R01','pi10_consulta12_familia_desde_P02_R02'),('PI10_RPF_','PI10_RPF2_'),('BOUND=36288','BOUND=24192'),('real18','real12'),('DEE.PI10.RP.owned_finite18.v1','DEE.PI10.RP.owned_finite12.v2'),('FAMILIA_PI10_R01','FAMILIA_PI10_R02'),('DEE.PI10.RP.fixed18_driver_guard.v1','DEE.PI10.RP.fixed12_driver_guard.v2'),('DIRECTORIOS_FAMILIA_PI10_R01','DIRECTORIOS_FAMILIA_PI10_R02')):t=t.replace(old,new)
old="steps=[s for batch in batches for s in batch];modes=[s['literal']['modo']for s in steps];need(modes==['eci01-pi10-admitir']+['eci01-pi10-episodio']*7+['eci01-pi10-estado']+['eci01-pi10-episodio']*11+['eci01-pi10-estado'],'Fixed eighteen actual episodes only')"
new="splits=recipe['material_supervisor']['episode_batches'];need(len(splits)==2 and all(type(n)is int and n>0 for n in splits)and sum(splits)==12,'Two frozen batches totalling twelve');steps=[s for batch in batches for s in batch];modes=[s['literal']['modo']for s in steps];need(modes==['eci01-pi10-admitir']+['eci01-pi10-episodio']*splits[0]+['eci01-pi10-estado']+['eci01-pi10-episodio']*splits[1]+['eci01-pi10-estado'],'Fixed twelve actual episodes only')"
assert old in t;t=t.replace(old,new)
old="need([len(b)for b in batches]==[9,12],'Exact ADMIT+7EP+STATE /11EP+STATE batches');";new="need(len(batches)==2,'Exact two prepared batches');";assert old in t;t=t.replace(old,new)
t=t.replace('index==21','index==15')
anchor="context_file=Path(context_file).resolve(strict=True);dest=context_file.parent;c=read(context_file);recipe=c['fixed_recipe'];";new=anchor+"global INITIAL;INITIAL=recipe['sources']['neutral_P02']['tick'];need(type(INITIAL)is int and INITIAL>=922377,'Actual neutral P02 start required');";assert anchor in t;t=t.replace(anchor,new)
put('pi10_guardia_reproduccion_R02.py',t)
print(json.dumps({'prepared_tools':outputs,'Native':0,'product_modified':False,'recipe_registered':False,'actual_Real12_and_neutral_P02_bindings_still_required':True}))
