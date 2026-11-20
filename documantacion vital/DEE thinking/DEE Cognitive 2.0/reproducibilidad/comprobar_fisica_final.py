"""Compare a closed diagnostic snapshot with its predetermined physical result.

Read-only by default. Explicit --salida writes only a new documentary proof;
there are no DEE imports, readers, probes, owner calls or phase adjustments.
"""
from pathlib import Path
import argparse,hashlib,json,sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
from observador_pasivo import snapshot_view
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--resultado',type=Path,required=True);p.add_argument('--salida',type=Path);a=p.parse_args()
 summary=a.resultado.resolve(strict=True);root=summary.parent;r=read(summary);c=read(root/'CONTEXTO_EJECUCION.json')
 if r.get('status')!='COMPLETED'or r.get('owner_closed_coherently')is not True:raise ValueError('Completed full recipe and coherent owner closure required')
 variant=c['fixed_recipe']['variants'][c['variant']];expected=variant.get('expected_final_physical')
 if expected is None:raise ValueError('No expected physical result was fixed before this reproduction')
 if set(expected)!={'N','tick','RAW_sha256','clocks_sha256'}:raise ValueError('Only the predetermined four physical fields')
 cardpath=root/'sistema/estado/vidas'/r['life']/'VIDA.json';card_before=sha(cardpath);card=read(cardpath)
 snapshot=(root/'sistema'/card['snapshot']).resolve(strict=True)
 if not snapshot.is_relative_to((root/'sistema/estado').resolve()):raise ValueError('Snapshot outside diagnostic state')
 encoded_before=sha(snapshot);view=snapshot_view(snapshot)
 if encoded_before!=card['snapshot_sha256']or view['encoded_sha256']!=encoded_before:raise ValueError('Closed checkpoint hash differs from its life record')
 if card_before!=sha(cardpath)or encoded_before!=sha(snapshot):raise ValueError('Diagnostic source changed during passive inspection')
 differences={k:{'expected':expected[k],'actual':view['physical'][k]}for k in expected if expected[k]!=view['physical'][k]}
 result={'schema':'DEE.reproduction.predetermined_final_physics.v1','life':r['life'],'recipe':r['recipe'],'variant':r['variant'],
  'predetermined_expected':expected,'expected_source':variant.get('expected_final_physical_source'),'actual':view['physical'],
  'differences':differences,'exact_physical_match':not differences,'summary_sha256':sha(summary),'context_sha256':sha(root/'CONTEXTO_EJECUCION.json'),
  'snapshot':str(snapshot),'snapshot_sha256':encoded_before,'new_native_ticks':0,'DEE_imports':0,
  'scope':'Exact physical N/tick/RAW/clocks after actual reproduction. Administrative metadata/transport identities can legitimately differ; this is not global causal-state equality or general cognitive PASS.'}
 if a.salida:
  with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if not differences else 2
if __name__=='__main__':raise SystemExit(main())
