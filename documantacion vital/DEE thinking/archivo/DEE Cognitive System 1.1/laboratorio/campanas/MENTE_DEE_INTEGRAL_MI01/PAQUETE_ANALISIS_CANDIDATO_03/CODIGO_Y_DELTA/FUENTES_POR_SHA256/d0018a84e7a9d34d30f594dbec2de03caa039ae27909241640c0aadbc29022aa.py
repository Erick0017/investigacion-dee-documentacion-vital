"""Frozen small same-life Spanish teaching trial, not target-based translation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun import *
from capacidades import espanol_funcional_01 as ef

# No native execution on import. Run after the current single writer ends.
def run_cases():
    configs=[(150,True,True,1),(151,False,True,1),(152,True,False,1),(153,True,True,3)]
    atomic_json(E/'ESPANOL_CONTACTO_PROTOCOLO_150.json',{'parent':'E1_MI01_MAIN23453','cases':configs,'geometry':'Existing EF01 contact frame at28,34,54; no trained records imported','comparison':'Actor actual contact/offroute, cue omitted and unseen medium magnitude. All class banks get identical cues. Decoder is pre-existing EF01; raw primary and positive load must support it.','not_claimed':'General negation, deictic roles or novel NSM level from a bank name.'})
    for number,present,cue,medium in configs:
        life='MI01_ESPANOL_'+str(number);fork('E1_MI01_MAIN',life)
        def fn(a,number=number,present=present,cue=cue,medium=medium):
            initial=physical(a.world,occupation=True);plan=ef.contact_prepare(a,frame='MI01_CONTACTO',base=(28,34,54))
            teaching=ef.contact_teach(a,frame='MI01_CONTACTO',present=present,medium=medium,signal=cue)
            query=ef.contact_query(a,frame='MI01_CONTACTO',use=False);use=ef.contact_query(a,frame='MI01_CONTACTO',use=True)
            return{'initial':initial,'plan':plan,'experience':teaching,'query':query,'use':use,'final':physical(a.world,occupation=True)}
        v=run(life,life,fn)['result'];print(json.dumps({'case':number,'labels_query':v['query']['SPANISH_DECODED'],'labels_use':v['use']['SPANISH_DECODED'],'outputs':v['use']['ENTE']['output']},ensure_ascii=False),flush=True)
if __name__=='__main__':run_cases()
