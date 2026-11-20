"""The fixed generic P0 procedure on a held-out noisy-history access failure."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import recurso_fase_mi02 as phase
from capacidades import integracion_distribuida_mi02_r6 as shared

atomic_json(E/'RESERVA38_FIJADA.json',{'source':Store().record('MI02_ESTRES37R2_nominal'),'procedure':'Same generic symmetric1000+1000 and19ticks as33; no reference, word or sign supplied','modes':['none','sham','treatment'],'new_context':'Six missed opportunities after a previously unseen nominal-noise history, lower acquired magnitudes thanMAIN33','future_availability':[-1]*3+[1]*3,'not_claimed':'Native self-selection or unlimited recovery','sources':archive()})
for mode in('none','sham','treatment'):
    life='MI02_RESERVA38_'+mode;fork('MI02_ESTRES37R2_nominal',life)
    run(life,'RESERVA38_'+mode+'_RESOURCE',lambda a,mode=mode:phase.pulse(a,mode=mode))
    run(life,'RESERVA38_'+mode+'_USE',lambda a:shared.live(a,availability=[-1]*3+[1]*3))
atomic_json(E/'RESERVA38_CORTES.json',{mode:Store().record('MI02_RESERVA38_'+mode)for mode in('none','sham','treatment')})
