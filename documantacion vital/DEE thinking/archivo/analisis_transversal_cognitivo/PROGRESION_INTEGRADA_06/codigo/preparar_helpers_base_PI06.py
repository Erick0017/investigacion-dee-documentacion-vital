"""Prepare reviewed helper source only; no source-system/world/engine import."""
from pathlib import Path
import ast,hashlib
P=Path(__file__).resolve().parents[1];H=P/'codigo';PREV=P.with_name('PROGRESION_INTEGRADA_05')/'codigo'
def write(name,source):
 ast.parse(source);dest=H/name
 with dest.open('x',encoding='utf8')as f:f.write(source)
 print(name,len(dest.read_bytes()),hashlib.sha256(dest.read_bytes()).hexdigest())
def once(text,old,new):
 if text.count(old)!=1:raise ValueError('Exact source edit not unique: '+old)
 return text.replace(old,new)

export=(PREV/'exportar_final_directo_RP_PI05_R03.py').read_text('utf-8-sig')
export=once(export,"SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_GUARD_01'","SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'")
export=once(export,"parent=(RP/'materiales').resolve(strict=True);expected=parent/('PI03_PI05_FINAL_GUARD_T'+str(ar.tick))","parent=(CAMPAIGN/'pares').resolve(strict=True);expected=parent/('BASE_MAIN_T'+str(ar.tick))")
export=once(export,"s5=(CAMPAIGN/'estados/candidato/sistema').resolve(strict=True)","s5=(PRODUCT/'sistema').resolve(strict=True)")
export=export.replace('Only one new canonical stable PI05 final-guard RP alias','Only one new exact PI06 baseline export from the actual closed product Main')
export=export.replace('Exact closed continuing S5 GUARD source only','Exact actual closed product Main source only')
export=export.replace('Closed exact final S5 GUARD pair directly in stable RP R03','Closed exact actual product Main pair into PI06 baseline')
export=export.replace('DEE.PI05.direct_stable_closed_paired_preservation.R03','DEE.PI06.actual_product_closed_paired_preservation.R01')
export=export.replace('R03_direct_stable_RP_exact_final_GUARD_only','PI06_R01_exact_product_Main_only')
export=export.replace('direct_stable_RP_export','direct_current_product_baseline_export')
write('exportar_main_cerrado_PI06.py',export)

owner=(PREV/'servicio_ensayo_PI05.py').read_text('utf-8-sig').replace('supervised for PI05','supervised for PI06')
write('servicio_ensayo_PI06.py',owner)

clone=(PREV/'clonar_PI05.py').read_text('utf-8-sig')
clone=clone.replace('isolated PI05 system','isolated PI06 system').replace('DEE.PI05.full_pair_diagnostic_import.v1','DEE.PI06.full_pair_diagnostic_import.v1')
clone=once(clone,"r'ECI02_PI03_REPRO_PI04_PI05_[A-Za-z0-9_]{1,32}'","r'ECI02_PI03_REPRO_PI04_PI05_PI06_[A-Za-z0-9_]{1,24}'")
write('clonar_PI06.py',clone)
print('Prepared source only; no Native/owner/export/clone executed.')
