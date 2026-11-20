"""Execute selected untouched SEM01 sources; compress generated states exactly."""
import argparse,gzip,hashlib,importlib.util,json,sys,tempfile,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'base_validada'))
from reproducir_cp01_cp02 import exact
FILES={'common':'71938e3f9c836c3e08ac.py','memory':'565f132df6ccde21d211.py','habitat':'264ca10b7baa599a8427.py',
 'participant':'3c71f9254300a3ea9ed1.py','experiment':'34f72ebef28ccea4a89a.py'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=False)
 package=types.ModuleType('sem01_original');package.__path__=[];sys.modules[package.__name__]=package
 for name,filename in FILES.items():
  spec=importlib.util.spec_from_file_location('sem01_original.'+name,ROOT/'genealogia/fuentes'/filename)
  module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;setattr(package,name,module);spec.loader.exec_module(module)
 specs=[{'id':'SEM8_PAIRED','pairing':{'S1':'U','S2':'V'},'future_events':{'S1':'U','S2':'V'}},
  {'id':'SEM8_OPPOSITE','pairing':{'S1':'V','S2':'U'},'future_events':{'S1':'U','S2':'V'}},
  {'id':'SEM8_UNPAIRED','mode':'unpaired','pairing':{'S1':'U','S2':'V'},'future_events':{'S1':'U','S2':'V'}},
  {'id':'SEM8_SIGNALS_ONLY','mode':'signals_only','pairing':{'S1':'U','S2':'V'},'future_events':{'S1':'U','S2':'V'}},
  {'id':'SEM8_RESERVE','pairing':{'S1':'U','S2':'V'},'future_events':{'S1':'U','S2':'V'},'translation':[3,7,5],'signal_payload':7}]
 (out/'FROZEN.json').write_text(json.dumps({'cases':specs,'sources':FILES,'source_changes':'NONE',
  'instrumentation':'Generated snapshots gzip-compressed and decode-hash checked; new generated JSON RAW/clocks converted from exact integers to exact strings. Original source untouched.',
  'criterion':'Original fixed anticipation and physical supply criterion; all two-signal results kept, including temporal residues/adverse outcomes.'},indent=2),encoding='utf-8')
 summaries=[]
 for spec in specs:
  dest=out/spec['id'];dest.mkdir();proof=[]
  with tempfile.TemporaryDirectory(prefix='cpc8_sem_') as temporary:
   short=Path(temporary);r=package.experiment.run_case(spec,short)
   for source in sorted(short.iterdir()):
    data=source.read_bytes();identity={'source_file':source.name,'original_bytes':len(data),'original_sha256':hashlib.sha256(data).hexdigest()}
    if source.suffix=='.deetsnap':
     encoded=gzip.compress(data,compresslevel=6,mtime=0);target=dest/(source.name+'.gz');target.write_bytes(encoded)
     assert gzip.decompress(encoded)==data
     identity.update({'storage':target.name,'encoding':'gzip','encoded_bytes':len(encoded),'reconstruction_byte_exact':True})
    elif source.suffix in('.json','.jsonl'):
     if source.suffix=='.json':text=json.dumps(exact(json.loads(data)),ensure_ascii=False,indent=2)
     else:text=''.join(json.dumps(exact(json.loads(line)),ensure_ascii=False)+'\n' for line in data.decode('utf-8').splitlines() if line)
     (dest/source.name).write_text(text,encoding='utf-8');identity['storage']=source.name;identity['encoding']='exact_uint64_JSON_strings'
    else:(dest/source.name).write_bytes(data);identity['storage']=source.name
    proof.append(identity)
  (dest/'STORAGE_PROOF.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
  summaries.append({'case_id':spec['id'],'initial':r['initial'],'final':r['final'],
   'uses':[{'signal':u['signal'],'emission':u['anticipation']['emission'],'evaluation':u['evaluation'],'prediction_correct':u['prediction_correct']} for u in r['uses']]})
  (out/'SUMMARY.json').write_text(json.dumps(exact(summaries),ensure_ascii=False,indent=2),encoding='utf-8')
  print(spec['id'],flush=True)
 old=json.loads((ROOT/'genealogia/fuentes/ab015efbf0f15579fe14.json').read_text(encoding='utf-8'))
 parity={'reference_member':'CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/resultados/confirmacion/A_future_UV/MEASUREMENTS.json',
  'initial_physical_equal':old['initial']==summaries[0]['initial'],'final_physical_equal':old['final']==summaries[0]['final'],
  'reference':old['final'],'reexecuted':summaries[0]['final'],'scope':'Physical hashes only; generated metadata/version/timestamps may differ. No new independent scientific replica claimed.'}
 (out/'HISTORICAL_PARITY.json').write_text(json.dumps(parity,indent=2),encoding='utf-8');print(json.dumps(parity))
if __name__=='__main__':main()
