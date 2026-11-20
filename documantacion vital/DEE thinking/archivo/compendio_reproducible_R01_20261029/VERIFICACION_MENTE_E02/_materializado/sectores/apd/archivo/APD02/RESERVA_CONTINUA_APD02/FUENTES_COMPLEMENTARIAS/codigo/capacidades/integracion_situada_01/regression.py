"""Small existing material panel; no legacy family suite or audit targets.

Same physical panel as HABITAT01.inherited_panel. Its probes affect the life.
"""
from app.native_tools import physical,observe,moore27
from capacidades import puente_adquirible as bridge

def inherited_panel(a,*,social=True,quantity=82,old=True):
    def emit(port,payload,tick):return a.input(port,payload,tick,'probe','MATERIAL_DIAGNOSTIC_EXISTING_PANEL')
    start=physical(a.world,occupation=True);requests=[];frames=[]
    if social:
        at=45+67*((a.tick-45)//67+1);g=bridge.geometry(a.world)
        for f in g['forms']:
            for b in f['branches']:requests.append(emit('DCS11.mobile.'+f['id']+'.'+b['id']+'.readminus',7,at-3))
        a.run_until(at);frames.append({'kind':'social','tick':a.tick,'forms':[{'id':f['id'],'branches':[{'id':b['id'],'read':observe(a.world,b['use_site'])}for b in f['branches']]}for f in g['forms']]})
    k=max(0,(a.tick-65)//67+1);t=65+67*k;read=70+67*k
    if quantity is not None:
        a.quantity.present_object(quantity,round_index=k);requests.append(emit('quantity.reader',7,read-1));a.run_until(read);o=observe(a.world,a.quantity.geometry['center']);frames.append({'kind':'quantity','tick':a.tick,'object':quantity,'read':o,'context':moore27(a.world,a.quantity.geometry['center'])})
    if old:
        requests.append(emit('TM.quantity.reader',7,read+1));a.run_until(read+2);frames.append({'kind':'two_memory','tick':a.tick,'read':observe(a.world,a.two_memory.geometry['center'])})
    return{'initial':start,'frames':frames,'requests':requests,'final':physical(a.world,occupation=True),'probe_is_material':True,'scope':'Pre-existing panel reused. Current quantity sign need not equal the historical sign after reference updates. A probe is not passive observation or a new independent individual.'}
