"""Preserve and correct the documentary candidate, never a physical life."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EV=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_11_R1_ENTE02_SIN_VALIDACION_VISUAL.docx'
    if sha(m)!='c85d33bc3c637e4e8f804f2d9332f1078f11ed9f5f4085479a3e0a7548ea9d33':raise ValueError('Corrected R1 exact identity')
    p=ROOT/'CONTINUIDAD_ENTE_DEE_EVOLUCION_02.json';backup=EV/'CONTINUIDAD_DOCUMENTAL_R00_CONSERVADA.json'
    if backup.exists():raise FileExistsError('Documentary revision already applied')
    shutil.copyfile(p,backup);cut=json.loads(p.read_bytes());prior=cut['manual']
    cut['manual'].update(path=m.name,bytes=m.stat().st_size,sha256=sha(m),document_revision='1.11R1',previous_editorial_candidate_preserved=True)
    cut['documentary_correction']={'at_utc':datetime.now(timezone.utc).isoformat(),'previous_manual':prior,'meaning':'R10 serial16 was executed; serial32 was attempted in R9 with reuse failures, not in R10. No native state, tick, acquired field or metric changed.','previous_continuity_sha256':sha(backup)}
    # Evidence records and snapshots are not rewritten.
    for dest in [p,EV/p.name]:dest.write_text(json.dumps(cut,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'corrected_manual':m.name,'sha256':sha(m),'same_native_cut':True,'no_new_ticks':True}))
if __name__=='__main__':main()
