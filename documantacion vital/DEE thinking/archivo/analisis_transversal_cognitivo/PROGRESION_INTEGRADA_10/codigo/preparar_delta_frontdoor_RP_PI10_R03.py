"""Stage the R02 family12 variant of the standard-RP extension, no deploy."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;source=H/'preparar_delta_frontdoor_RP_PI10_R02.py';text=source.read_text('utf8')
for old,new in(('RP_PI10_DELTA_R02_PREPARADO','RP_PI10_DELTA_R03_PREPARADO'),('DEE.PI10.diagnostic_family.identity_binding.R01','DEE.PI10.diagnostic_family.identity_binding.R02'),('pi10_vinculo_reproduccion_R01.py','pi10_vinculo_reproduccion_R02.py'),('pi10_guardia_reproduccion_R01.py','pi10_guardia_reproduccion_R02.py'),('DEE.PI10.staged_standard_RP_owned_family_delta.R02','DEE.PI10.staged_standard_RP_owned_family_delta.R03'),('finite18guard','finite12guard'),('Real18','Real12')):
 assert old in text,old;text=text.replace(old,new)
ast.parse(text);namespace={'__file__':str(source),'__name__':'PI10_RP_family12_stage_only'};exec(compile(text,str(source)+':R02_family12_staging_only','exec'),namespace)
