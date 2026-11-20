"""Generic material phase perturbation, matched positive/negative content cases."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from comun_mi02 import *
from capacidades import recurso_fase_mi02 as phase
from capacidades import integracion_distribuida_mi02_r6 as shared
from capacidades.observador_causal_retrospectivo_01 import Snapshot,compare
late=json.loads((E/'MAIN29_CORTE_ALCANZADO.json').read_bytes());early=json.loads((E/'MAIN29_PREFIJO_A.json').read_bytes())
atomic_json(E/'PROTOCOLO_FASE33_FIJADO.json',{'late_source':late['snapshot_sha256'],'early_source':early['snapshot_sha256'],'groups':['none','same-load away-from-body sham','symmetric inward resource'],'load_each':1000,'content_blind':'Same two packets for both positive and negative learned motor states. No original sample, word or desired sign is supplied.','questions':['Does a generic material event change a missed contact phase without reteaching stored content?','Does the same event harm an already matched phase?'],'not_claimed':'Autonomous access selection, policy learning by the phase procedure, or universal regulation.'})
records=[]
for label,source,available in[('late',late,1),('early',early,-1)]:
    for mode in('none','sham','treatment'):
        life='MI02_FASE33_'+label+'_'+mode;fork('D1_MI02_MAIN',life,source['snapshot']);r=run(life,'FASE33_'+label+'_'+mode,lambda a,mode=mode:phase.pulse(a,mode=mode));phase_cut=Store().record(life)
        z=run(life,'FASE33_USO_'+label+'_'+mode,lambda a,available=available:shared.live(a,availability=[available]))
        row=z['rows'][0];records.append({'label':label,'mode':mode,'phase_snapshot':phase_cut,'available':available,'useful':row['useful_material_actions'],'failed':row['failed_material_actions'],'conflict':row['conflict'],'pulse_admission':[x['receipt']['status']for x in r['requests']]})
        print(json.dumps(records[-1]|{'phase_snapshot':phase_cut['snapshot_sha256']},ensure_ascii=False),flush=True)
comparisons=[]
for label in('late','early'):
    base=next(x for x in records if x['label']==label and x['mode']=='none')
    for mode in('sham','treatment'):
        other=next(x for x in records if x['label']==label and x['mode']==mode);comparisons.append({'label':label,'mode':mode,'fields':compare(Snapshot(S/base['phase_snapshot']['snapshot']),Snapshot(S/other['phase_snapshot']['snapshot']),sample_limit=20)})
atomic_json(E/'FASE33_RESUMEN_Y_CAMPOS.json',{'records':records,'comparisons_after_same19ticks':comparisons,'no_new_main_ticks':True})
