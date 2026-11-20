"""Pure binding test against actual frozen EVALUATION capsule; no state."""
from pathlib import Path
import copy,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;P=H.parent
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 file=H/'pi10_vinculo_reproduccion_R02.py';sp=importlib.util.spec_from_file_location('PI10_pure_R02_binder',file);binder=importlib.util.module_from_spec(sp);sp.loader.exec_module(binder);cap=H/'CAPSULA_EVALUACION_REAL2_R02';manifest=read(cap/'SISTEMA_CODIGO.json');frozen=read(cap/'CONGELACION_CAPSULA_REAL2_R02.json');assert frozen['capsule_manifest_sha256']==sha(cap/'SISTEMA_CODIGO.json')
 for r in manifest['files']:assert sha(cap/r['file'])==r['sha256']
 docs={n:read(cap/n)for n in binder.FILES};prior=copy.deepcopy(docs);life=binder.PREFIX+'PURE202611';after=binder.rebound_documents(docs,life,frozen['template_life_id']);assert docs==prior
 allowed={binder.FILES[0]:{'life_id','role'},binder.FILES[1]:{'life_id'},binder.FILES[2]:{'files_sha256'}};changes={}
 for n in binder.FILES:
  keys={k for k in set(prior[n])|set(after[n])if prior[n].get(k)!=after[n].get(k)};assert keys==allowed[n];changes[n]=sorted(keys)
 oldpins=prior[binder.FILES[2]]['files_sha256'];newpins=after[binder.FILES[2]]['files_sha256'];assert {k for k in set(oldpins)|set(newpins)if oldpins.get(k)!=newpins.get(k)}=={'PI10_TRANSPORTE_ANCESTRAL_R01.json','PI10_EXPERIMENTO_R02.json'}
 for mode in('real','nonfailure','yoked'):
  d=copy.deepcopy(prior);d[binder.FILES[1]]['arm']=mode
  if mode=='real':assert binder.rebound_documents(d,life,frozen['template_life_id'])[binder.FILES[1]]['arm']=='real'
  else:
   try:binder.rebound_documents(d,life,frozen['template_life_id'])
   except ValueError:pass
   else:raise AssertionError('Control allowed as actual-real recipe')
 report={'schema':'DEE.PI10.pure_actual_capsule_family_binding.R02','Native_imports':0,'Native_ticks':0,'state_created':False,'fictitious_life_id_used_only_as_JSON_test':life,'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'binder_sha256':sha(file),'capsule_files_verified':len(manifest['files']),'exact_changed_top_level_fields':changes,'non_real_controls_rejected':True,'scientific_bodies_or_protocols_changed':False,'not_a_Native_reproduction':True};out=P/'control/PRUEBA_PURA_VINCULO_RP_PI10_R02.json';data=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
 if out.exists():assert out.read_text('utf8')==data
 else:
  with out.open('x',encoding='utf8')as f:f.write(data)
 print(json.dumps({'proof':str(out),'sha256':sha(out),'Native':0}))
if __name__=='__main__':main()
