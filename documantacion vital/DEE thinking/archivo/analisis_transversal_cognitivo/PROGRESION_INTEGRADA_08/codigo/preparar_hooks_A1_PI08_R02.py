"""Versioned correction of an unexecuted hook-builder whitespace anchor.
Preserve the R01 source and partial stage; no Native or target-source change.
"""
from pathlib import Path
import hashlib
H=Path(__file__).resolve().parent;original=H/'preparar_hooks_A1_PI08_R01.py';target=H/'instalar_hooks_A1_PI08_R02.py'
if target.exists():raise FileExistsError('Prepared Root applier revision preserved')
s=original.read_text('utf8')
s=s.replace('PI08_A1_INSTALACION_R01','PI08_A1_INSTALACION_R02').replace('PI08_A1_HOOKS_PREPARADOS_R01.json','PI08_A1_HOOKS_PREPARADOS_R02.json').replace('PI08_A1_HOOKS_APLICADOS_R01.json','PI08_A1_HOOKS_APLICADOS_R02.json').replace('ORIGINALES_HOOKS_A1_PI08_R01','ORIGINALES_HOOKS_A1_PI08_R02')
old='dispatcher=replace_once(dispatcher,"    return result\\n\\ndef uncertain(a):", "    result[\'PI08_integration32\']=_load(\'pi08_integracion_c2c_R01\').operational_dependencies(a,directory)\\n    return result\\n\\ndef uncertain(a):")'
new='dispatcher=replace_once(dispatcher,"    result[\'PI05_explicit_environment30\']=_load(\'pi05_c2c_ofertas_R01\').operational_dependencies(a,directory)\\n", "    result[\'PI05_explicit_environment30\']=_load(\'pi05_c2c_ofertas_R01\').operational_dependencies(a,directory)\\n    result[\'PI08_integration32\']=_load(\'pi08_integracion_c2c_R01\').operational_dependencies(a,directory)\\n")'
if old not in s:raise ValueError('Exact prior failed-builder line must be preserved')
s=s.replace(old,new);compile(s,str(target),'exec');target.write_text(s,encoding='utf8');print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
