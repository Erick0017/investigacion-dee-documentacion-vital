"""Prepare source only for bounded closed S6 full-pair exports; no execution."""
from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent;source=H/'exportar_main_cerrado_PI06.py';target=H/'exportar_corte_aislado_PI06_R02.py'
text=source.read_text('utf-8-sig')
def replace(old,new):
 global text
 if text.count(old)!=1:raise ValueError('Exact edit no longer unique: '+old)
 text=text.replace(old,new)
replace('import argparse,ctypes,hashlib,importlib.util,json,os,shutil,sqlite3','import argparse,ctypes,hashlib,importlib.util,json,os,re,shutil,sqlite3')
replace("parent=(CAMPAIGN/'pares').resolve(strict=True);expected=parent/('BASE_MAIN_T'+str(ar.tick));dest=(expected if ar.destino is None else ar.destino).resolve(strict=False);regular(s);regular(dest)",
 "parent=(CAMPAIGN/'pares').resolve(strict=True)\n    if ar.destino is None:raise ValueError('Explicit new bounded PI06/pares destination required')\n    dest=ar.destino.resolve(strict=False);expected=parent/dest.name;regular(s);regular(dest)\n    if not re.fullmatch(r'[A-Za-z0-9_]{1,48}_T'+str(ar.tick),dest.name):raise ValueError('Short exact new export name must end in its declared Native tick')")
replace("s5=(PRODUCT/'sistema').resolve(strict=True)","s5=(CAMPAIGN/'estados/candidato/sistema').resolve(strict=True)")
replace("if s!=s5 or ar.vida!=SOURCE_LIFE:raise ValueError('Exact actual closed product Main source only')", "if s!=s5 or not re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI06_[A-Za-z0-9_]{1,24}',ar.vida):raise ValueError('Only exact isolated S6 PI06 diagnostic source; never current product Main')")
replace('DEE.PI06.actual_product_closed_paired_preservation.R01','DEE.PI06.isolated_closed_paired_preservation.R02')
replace('PI06_R01_exact_product_Main_only','PI06_R02_exact_S6_diagnostic_only')
replace('direct_current_product_baseline_export','direct_closed_S6_export')
text=text.replace('Closed exact actual product Main pair into PI06 baseline','Closed declared isolated S6 cut to one new bounded PI06 pair')
ast.parse(text)
with target.open('x',encoding='utf8')as f:f.write(text)
print(target.name,len(target.read_bytes()),hashlib.sha256(target.read_bytes()).hexdigest())
