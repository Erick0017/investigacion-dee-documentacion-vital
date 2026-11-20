"""Held-out raw values, passive retention, late genuine learning, probe control."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from app.lives import WorldAdapter
from capacidades import comparacion_efimera_mi02 as b

atomic_json(E/'RESERVA_EFIMERA35_FIJADA.json',{'reference':'Existing210 retained32/10; existing212 initiallyuntrained; new213 learns65/11','program':['210 passive845ticks then novel24/26/22/33/1/None with newspacings','210 matched exact-fork no-probe control','212 late explicit acquisition32/10 then same queries','213 new raw reference and55/56/57/70/80'],'not_claimed':['Integration intoMAIN','Unbiased equality','Autonomous query initiation','NSM MORE/LESS acquisition'],'sources':archive()})
run('MI02_EFIMERO_210','EFIMERO35_PASSIVE',lambda a:(a.run_until(a.tick+845),b.state(a))[1])
fork('MI02_EFIMERO_210','MI02_EFIMERO35_SIN_SONDA')
run('MI02_EFIMERO_210','EFIMERO35_RESERVED210',lambda a:b.read(a,objects=[24,26,22,33,1,None],spacings=(29,31,37)))
run('MI02_EFIMERO35_SIN_SONDA','EFIMERO35_NO_PROBE',lambda a:b.read(a,objects=[24,26,22,33,1,None],spacings=(29,31,37),probe=False))
run('MI02_EFIMERO_212','EFIMERO35_LATE_TEACH212',lambda a:b.teach_empty(a,values=(32,10)))
run('MI02_EFIMERO_212','EFIMERO35_LATE_USE212',lambda a:b.read(a,objects=[24,26,22,33,1,None],spacings=(29,31,37)))
life='MI02_EFIMERO_213';recipe,g=b.recipe();a=WorldAdapter(d.OrganizationalWorld.create(recipe));p=E/(life+'.PREPARACION_T0.deetsnap.gz');a.save(p);Store().import_state(p,life,'fisica_directa',expected=sha(p))
run(life,'EFIMERO35_ACQUIRE213',lambda a:b.acquire(a,geometry=g,values=(65,11)))
run(life,'EFIMERO35_RESERVED213',lambda a:b.read(a,objects=[55,56,57,70,80,0],spacings=(29,31,37)))
atomic_json(E/'EFIMERO35_CORTES.json',{x:Store().record(x)for x in['MI02_EFIMERO_210','MI02_EFIMERO_212','MI02_EFIMERO_213','MI02_EFIMERO35_SIN_SONDA']})
