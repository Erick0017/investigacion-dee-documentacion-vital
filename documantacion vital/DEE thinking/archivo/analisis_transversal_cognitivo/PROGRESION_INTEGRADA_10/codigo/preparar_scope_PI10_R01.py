"""Pure finite-experiment scope from an actually sealed protocol/full pair.

No DEE imports or Native execution. Canonical working config is replaced only
after preserving each exact generated scope under its unique slug filename;
already installed per-world copies are never changed by this tool.
"""
from pathlib import Path
import argparse,hashlib,json,re
P=Path(__file__).resolve().parents[1];H=P/'codigo'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--slug',required=True);ap.add_argument('--vida',required=True);ap.add_argument('--rol',choices=('p0','calibration','evaluation'),required=True);ap.add_argument('--brazo',choices=('real','nonfailure','yoked'),default='real');ap.add_argument('--force-query',choices=('null','true','false'),default='null');ap.add_argument('--traza',choices=('none','cut','sham'),default='none');ap.add_argument('--prefijo',type=Path,required=True);ap.add_argument('--manifest-sha256',required=True);ap.add_argument('--escribir',action='store_true');a=ap.parse_args()
 need(re.fullmatch('[A-Z][A-Z0-9_]{0,24}',a.slug)and re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9_]{1,25}',a.vida),'Exact unused PI10 scope identity')
 protocol=H/'PROTOCOLO_PI10_R01.json';p=read(protocol);need(p.get('status')in('SEALED_FOR_CALIBRATION','SEALED_FOR_EVALUATION'),'Root must seal protocol before preparing a material scope; no fabricated seal')
 for name,digest in p['sources_sha256'].items():need(Path(name).name==name and sha(H/name)==digest,'Sealed source mismatch: '+name)
 need({'pi10_consulta_adaptativa_R01.py','pi10_dos_trazas_legales_R01.py','pi10_entorno_dos_puertas_R01.py'}<=set(p['sources_sha256']),'All three actual scientific sources must be sealed')
 pair=a.prefijo.resolve(strict=True);need(pair.parent==(P/'pares').resolve()and sha(pair/'EXPORTACION_SERVICIO.json')==a.manifest_sha256,'Explicit actual full paired prefix/hash')
 m=read(pair/'EXPORTACION_SERVICIO.json');need(m['physical']['N']==67 and m['physical']['tick']>=922371,'Actual current-D continuation N67')
 force={'null':None,'true':True,'false':False}[a.force_query];need(force is None or a.rol=='calibration','Forcing only in declared separate calibration')
 need(a.brazo!='yoked','Yoked scope requires the actual Real source plan, separately prepared after Real; no invented feedback')
 value={'schema':'DEE.PI10.fixed_experiment_scope.R01','life_id':a.vida,'role':a.rol,'arm':a.brazo,'trace_control':a.traza,'force_query':force,'protocol_sha256':sha(protocol),'source_physical':{k:m['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')},'source_full_pair_manifest_sha256':a.manifest_sha256,'calibration_authorized':a.rol=='calibration','evaluation_authorized':a.rol=='evaluation','environment_and_instrumentation_not_Native_policy':True}
 target=H/('PI10_EXPERIMENTO_'+a.slug+'_R01.json');canonical=H/'PI10_EXPERIMENTO_R01.json';data=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
 if a.escribir:
  if target.exists():need(target.read_text('utf-8-sig')==data,'Different prior exact scope, preserve and use new revision')
  else:
   with target.open('x',encoding='utf8')as f:f.write(data)
  temporary=canonical.with_name(canonical.name+'.WRITING');need(not temporary.exists(),'Unresolved prior canonical config write');temporary.write_text(data,'utf8');temporary.replace(canonical)
 print(json.dumps({'mode':'SCOPE_WRITTEN_NO_NATIVE'if a.escribir else'PLAN_ONLY_NO_NATIVE','scope':str(target),'canonical':str(canonical),'scope_sha256':sha(target)if target.exists()else hashlib.sha256(data.encode()).hexdigest(),'protocol_sha256':sha(protocol),'source_physical':value['source_physical'],'Native':0}))
if __name__=='__main__':main()
