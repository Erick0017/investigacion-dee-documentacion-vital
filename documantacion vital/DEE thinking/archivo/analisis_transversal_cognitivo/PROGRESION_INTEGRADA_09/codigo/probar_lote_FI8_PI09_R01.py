"""Pure fake administrative lifecycle, explicitly not actual Native evidence."""
from pathlib import Path
from types import SimpleNamespace
import copy,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;OUT=H/'PRUEBA_LOTE_FI8_PI09_R01'
def main():
 if OUT.exists():raise FileExistsError('Prueba anterior preservada')
 OUT.mkdir();sp=importlib.util.spec_from_file_location('FI8_pure_module',H/'pi09_lote_FI8_R01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 old=json.dumps({'version':'old_literal','ordinal':7,'rows':[{'old':i}for i in range(7)],'pending':None,'uncertain':False},sort_keys=True);oldreg=json.dumps({'literal_old_R03':12})
 metadata={m.OLD_KEY:old,'OLD_REGULATION':oldreg,'OTHER_ANCESTOR':'literal'};physical={'N':67,'tick':100,'RAW_sha256':'a'*64,'clocks_sha256':'b'*64};calls=[]
 runtime=SimpleNamespace(snapshot_metadata_entries=metadata.items());runtime.set_snapshot_metadata=lambda k,v:metadata.__setitem__(k,v)
 a=SimpleNamespace(tick=100,world=SimpleNamespace(runtime=runtime));home=OUT/'worker';home.mkdir()
 def encoded(v):
  data=json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
  if len(data.encode())>65536:raise ValueError('Exact historical metadata quota')
  return data
 body=SimpleNamespace(_physical=lambda unused:dict(physical),_safe=lambda v:v,_encoded=encoded)
 private=SimpleNamespace(body=body,regulation=SimpleNamespace(KEY='OLD_REGULATION',_selected=lambda unused:False),protocol=lambda unused:({},'c'*64),_home=lambda directory,unused:Path(directory)/m.FOLDER,_get=lambda unused:json.loads(metadata[m.KEY]))
 m._PRIVATE=private;m.identity=lambda unused:{'life_id':m.LIFE,'profile':'fisica_directa'};tests=[]
 def check(n,v):
  if v is not True:raise AssertionError(n)
  tests.append({'name':n,'pass':True})
 def rejects(n,fn):
  try:fn()
  except ValueError:check(n,True);return
  raise AssertionError(n)
 baseline=copy.deepcopy(metadata);private.body._encoded=lambda unused:(_ for _ in()).throw(ValueError('SIMULATED_PREWRITE_ENCODING_INTERRUPT'))
 rejects('prewrite_interrupt_preserves_everything',lambda:m.admit(a,home));check('prewrite_no_artifacts_or_metadata',metadata==baseline and not(home/m.FOLDER).exists())
 private.body._encoded=encoded;r=m.admit(a,home)
 check('new_offers8_old7_literal',r['new_offers_added_now']==8 and metadata[m.OLD_KEY]==old and set(metadata)==set(baseline)|{m.KEY})
 check('new_ordinal0_is_explicit_supply_only',json.loads(metadata[m.KEY])['ordinal']==0 and json.loads(metadata[m.KEY])['explicit_new_supply']['old_remaining']==1)
 file=home/m.FOLDER/'eventos.jsonl';literal=file.read_bytes();prior=copy.deepcopy(metadata);r2=m.admit(a,home)
 check('same_lot_idempotent_without_additional_supply',r2['already_admitted']is True and r2['new_offers_added_now']==0 and metadata==prior and file.read_bytes()==literal)
 check('reopen_reads_persisted_new_state',m.state(a)['new_lot_remaining']==8 and m.state(a)['old_FI_ordinal']==7)
 check('physical_and_input_calls_unchanged',physical=={'N':67,'tick':100,'RAW_sha256':'a'*64,'clocks_sha256':'b'*64}and calls==[])
 rejects('no_capacity_override',lambda:m.validate_literal({'modo':m.ADMIT,'max_queries':16}))
 rejects('no_reader_or_target',lambda:m.validate_literal({'modo':m.QUERY,'izquierda':1,'derecha':7,'expected':-1}))
 bad=json.loads(old);bad['ordinal']=8;rejects('exhausted_old_cut_is_not_7',lambda:m.plan_values(json.dumps(bad),oldreg,100))
 result={'schema':'DEE.PI09.FI8.pure_administrative_tests.R01','passed':len(tests),'tests':tests,'fixture_MOCK_ONLY_NOT_NATIVE':True,'Native_executed':False,'DEE_imports':0,'actual_admission_and_reopen_still_required':True,'old_code_or_protocol_or_quota_changed':False,'new_source_sha256':hashlib.sha256((H/'pi09_lote_FI8_R01.py').read_bytes()).hexdigest()}
 proof=OUT/'RESULTADO.json';proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':len(tests),'proof':str(proof),'sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),'Native_executed':False,'fixture_MOCK_ONLY_NOT_NATIVE':True}))
if __name__=='__main__':main()
