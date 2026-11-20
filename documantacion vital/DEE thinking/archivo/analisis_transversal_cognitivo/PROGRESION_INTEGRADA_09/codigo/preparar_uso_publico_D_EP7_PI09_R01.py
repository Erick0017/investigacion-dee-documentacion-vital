"""Deriva el cliente público D opcional; no ejecuta operaciones."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;source=H/'usar_principal_NATIVE_EP12_PI09_R01.py';target=H/'usar_principal_D_EP7_PI09_R01.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(text,a,b):
 if text.count(a)!=1:raise ValueError('Ancla pública cambió: '+a)
 return text.replace(a,b)
if target.exists():raise FileExistsError('Cliente D anterior preservado')
t=source.read_text('utf8');t=t.replace('NATIVE_EP12','D_EP7').replace('NATIVE_EP12','D_EP7').replace('NATIVE12','D7').replace('EP12','EP7').replace('No se adopta','Se adopta')
t=t.replace('PI09_NATIVE_01','PI09_DISCOVERY_01').replace('DEE.Cognitive.PI09.selective_registered_consultation.R02','DEE.Cognitive.PI09.persistent_environment.D.R02').replace('eci01-pi09-episodio','eci01-pi09-d-episodio').replace('eci01-pi09-estado','eci01-pi09-d-estado').replace('BOUND=2280','BOUND=2110')
t=t.replace('confirmar_no_adopcion_D','confirmar_adopcion_D').replace('--confirmar-no-adopcion-D','--confirmar-adopcion-D')
t=once(t,"need(not adopted.exists()or read(adopted).get('phase')!='COMMITTED','D ya adoptada: esta alternativa queda prohibida')","need(adopted.exists()and read(adopted).get('phase')=='COMMITTED'and read(adopted).get('life_id')==LIFE,'D debe estar realmente COMMITTED antes del uso público')")
t=once(t,"need(card['physical']['tick']==903603 and progress['ordinal']==12 and len(progress['rows'])==12,'Se exige el principal quieto y la oferta12 sin consumir')","initial=card['physical']['tick'];need(initial>917679 and progress['ordinal']==7 and len(progress['rows'])==7,'Se exige Discovery adoptada con la oferta7 disponible')")
t=t.replace("'initial_tick':903603","'initial_tick':initial").replace("'Root_explicit_no_D_adoption':True,'D_adopted':False","'Root_explicit_D_adoption':True,'D_adopted':True").replace("material_card['physical']['tick']-903603","material_card['physical']['tick']-initial").replace("final['physical']['tick']-903603","final['physical']['tick']-initial")
t=t.replace("m['ordinal']==13 and len(m['rows'])==13","m['ordinal']==8 and len(m['rows'])==8").replace("['progress']['ordinal']==13","['progress']['ordinal']==8").replace("'ordinal_before':12,'ordinal_after':13,'remaining':5","'ordinal_before':7,'ordinal_after':8,'remaining':4").replace("'before':12,'after':13,'total':18","'before':7,'after':8,'total':12")
t=t.replace("'NO_ADOPTAR_D'","'D_COMMITTED'").replace('una oportunidad pública NATIVE12, sólo si D no se adopta','una oportunidad pública D7, sólo después de D COMMITTED').replace('consume la oferta R02 ordinal12 ya existente','consume la oferta D ordinal7 ya existente').replace('Sólo tras decisión explícita de Root de no adoptar D','Sólo tras decisión explícita y COMMITTED real de D').replace('NATIVE seleccionado','Discovery seleccionada')
ast.parse(t);target.write_text(t,'utf8');print(json.dumps({'source':source.name,'source_sha256':sha(source),'target':str(target),'sha256':sha(target),'Native_executed':False,'ordinal_before':7,'ordinal_after':8,'max_ticks':2110}))
