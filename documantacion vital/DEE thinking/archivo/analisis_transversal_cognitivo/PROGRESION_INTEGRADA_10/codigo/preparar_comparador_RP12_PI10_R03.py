"""Prepare conservative R02-family12 comparison, no Native/product writes."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
def put(p,t):
 ast.parse(t)
 if p.exists():assert p.read_text('utf8')==t
 else:
  with p.open('x',encoding='utf8')as f:f.write(t)
base=(H/'comparar_reproduccion_PI10_R01.py').read_text('utf8')
for old,new in(('DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01','DEE.Cognitive.PI10.adaptive_query.two_native_traces.R02'),('PI10_CONSULTA_ADAPTATIVA_R01','PI10_CONSULTA_ADAPTATIVA_R02'),('PI10_RPF_','PI10_RPF2_'),('==18','==12'),('Real18','Real12'),('RPF18','RPF12'),('real18','real12')):base=base.replace(old,new)
bp=H/'comparar_reproduccion_PI10_R03_base.py';put(bp,base);pin=hashlib.sha256(bp.read_bytes()).hexdigest();text=(H/'comparar_reproduccion_PI10_R02.py').read_text('utf8')
for old,new in(("BASE=HERE/'comparar_reproduccion_PI10_R01.py'","BASE=HERE/'comparar_reproduccion_PI10_R03_base.py'"),('b134d62214c6052fde992d6b5e65b12af621011f639feab77c863501115b360b',pin),('pi10_vinculo_reproduccion_R01.py','pi10_vinculo_reproduccion_R02.py'),('VINCULO_FAMILIA_PI10_R01.json','VINCULO_FAMILIA_PI10_R02.json'),('full_P0_manifest_sha256','full_P02_manifest_sha256'),("==binder.P0_SHA","==contract['neutral_P02_manifest_sha256']"),('Real18','Real12'),('RPF18','RPF12'),('real18','real12'),('full_passive_comparison.R02','full_passive_comparison.R03')):
 text=text.replace(old,new)
out=H/'comparar_reproduccion_PI10_R03.py';put(out,text);print(json.dumps({'base':str(bp),'base_sha256':pin,'comparison':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'Native':0,'product_modified':False}))
