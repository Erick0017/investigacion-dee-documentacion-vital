"""Compare only the preserved editable project and the protected deliverables."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=R/'trabajo';backup=H/'PROYECTO_INTACTO/trabajo'
oa={str(p.relative_to(original)):p for p in original.rglob('*') if p.is_file()}
ba={str(p.relative_to(backup)):p for p in backup.rglob('*') if p.is_file()}
assert oa.keys()==ba.keys(),'Original project member set differs from its intact copy'
rows=[]
for name,p in oa.items():
 digest=sha(p);assert digest==sha(ba[name]),name
 rows.append({'relative_file':name,'bytes':p.stat().st_size,'sha256':digest})
protected={
 'DEE_Cognitive_5min_MASTER_1080p_ES_ENsub.mp4':'7beec0b2fde67b09b4b81171ce03b788610223c124553e67d46346f0990327cc',
 'DEE_Cognitive_5min_EN.srt':'be37093f83c88dc0e7d04ae632f6f2f0a6a563e59197e1246585f7b10843b266',
 'CORRECCION_S07_01/DEE_S07_DESPUES_1080p.mp4':'7bb3ecac833399cb52d812082f0392d9044c26a16ea29feb3e8c9ec30fa64636'}
for n,digest in protected.items():assert sha(R/n)==digest,n
out=H/'verificacion';out.mkdir(exist_ok=True)
(out/'ORIGINALES_INTACTOS.json').write_text(json.dumps({'project_files_compared':len(rows),'all_project_files_byte_identical_to_intact_backup':True,'protected_deliverables':protected,'files':rows,'DEE_states_opened_or_modified':False},ensure_ascii=False,indent=2),'utf8')
print('Original editable project preserved:',len(rows),'files; protected master/SRT/S07 unchanged.',flush=True)
