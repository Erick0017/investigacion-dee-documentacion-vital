"""Preserve reviewed draft; make narrow current-catalog correction in R02."""
from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent
def main():
 source=H/'incorporar_PI07_misma_identidad.py';text=source.read_text('utf8');needle=" # Existing Supervisor protocol prevents the launcher from trying import_new."
 if text.count(needle)!=1:raise ValueError('Exact synchronization point required')
 extra=" catalog.setdefault('PI07_prior_current_principal',catalog.get('current_principal'))\n catalog['current_principal']={'life_id':LIFE,'profile':card['profile'],'N':card['physical']['N'],'tick':card['physical']['tick'],'snapshot_sha256':card['snapshot_sha256'],'selection':'COMMITTED','world_id':card['world_id'],'prior_principal':{'life_id':PARENT,'tick':PARENT_T,'snapshot_sha256':PARENT_SHA},'actual_persistence_parent':card['parent'],'adoption_witness':str(ADOPTED),'unselected_zero_reopening_witness':str(reopening),'updated_utc':now(),'scope':'One selected same-identity successor. Old principal descriptors are historical; no branch memory fusion.'}\n"
 target=H/'incorporar_PI07_misma_identidad_R02.py'
 if target.exists():raise FileExistsError('Preserve prior R02')
 new=text.replace(needle,extra+needle);ast.parse(new);target.write_text(new,encoding='utf8');print(target,hashlib.sha256(target.read_bytes()).hexdigest())
if __name__=='__main__':main()
