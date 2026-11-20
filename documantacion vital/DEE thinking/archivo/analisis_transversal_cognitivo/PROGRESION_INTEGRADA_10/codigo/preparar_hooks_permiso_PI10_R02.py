"""Prospective R02 public hook staging; no product/world mutation."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;src=H/'preparar_hooks_permiso_PI10_R01.py';text=src.read_text('utf8')
for old,new in(("SOURCE=P/'estados/REAL/sistema'","SOURCE=P/'estados/P02/sistema'"),('PERMISO_PI10_R01_PREPARADO','PERMISO_PI10_R02_PREPARADO'),('pi10_permiso_operativo_R01','pi10_permiso_operativo_R02'),('DEE.PI10.public_permission.staged_owner_delta.R01','DEE.PI10.public_permission.staged_owner_delta.R02'),('DEE.PI10.exact_operational_permission.v1','DEE.PI10.exact_operational_permission.v2'),('REAL18','REAL12')):
 assert old in text,old;text=text.replace(old,new)
ast.parse(text);namespace={'__file__':str(src),'__name__':'PI10_hook_R02_stage_only'};exec(compile(text,str(src)+':R02_public_host_hooks_only','exec'),namespace)
