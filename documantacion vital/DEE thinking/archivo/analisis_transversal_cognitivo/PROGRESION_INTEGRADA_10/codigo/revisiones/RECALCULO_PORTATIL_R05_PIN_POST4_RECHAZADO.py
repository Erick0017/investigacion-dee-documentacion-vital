"""Portable envelope/metric recalculation using a checked relative bundle.

Preserves and delegates literal R04 scoring. Original absolute paths in the
proof are provenance only: they must map through INDEX, never be opened.
--indice-portatil PANEL_INDEX --fuentes-dir FOUR_RECALC_JSON_DIR
--salida NEW. The data directory must contain the four exact named closed
recalc/contrast files. No Native, SQLite, original world or approval.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;BASE=H/'recalcular_metricas_adopcion_PI10_R04.py';PIN='db3581559e55f7428c63ae20e77d9e1e5021bc1385310cfc74f545478f664f27'
DATA={'COMPARISON':('CONTRASTE_REAL_NONE12_PI10_R02.json','9c03f0386d279cd691e9e9a48456e045b81b7bad88c3c7e509514f733d3637d3'),'REAL':('RECALCULO_REAL2_12_PI10_R03.json','13c5961bb3497eff35fa164c971987e83663221f57f0b1d3457e44247e0f234e'),'YOKE':('CONTRASTE_TRES_BRAZOS12_PI10_R02.json','2f2ce821b69de61f78246798bc6afd2df28510118de8bbb6b4d1da08c4d8a095'),'CUT':('CONTRASTE_CUT_SHAM_PI10_R02.json','5eb75aaf8a6ff946501d132f44c726a19e1476fc3d53804d454978a24004e135')}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):p=Path(p).resolve(strict=True);return {'path':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def run(index,data):
 index=Path(index).resolve(strict=True);folder=index.parent;v=read(index);need(v.get('schema')=='DEE.PI10.closed_panel_bundle.R01'and v.get('closed')is True,'Exact closed portable panel index')
 mapped={};roles={}
 for row in v['files']:
  rel=PurePosixPath(row['file']);need(not rel.is_absolute()and not any(x in('.','..')for x in rel.parts)and ':'not in str(rel)and '\\'not in str(rel),'Safe bundle member')
  p=(folder/Path(*rel.parts)).resolve(strict=True);need(p.is_relative_to(folder)and p.is_file()and p.stat().st_size==row['bytes']and sha(p)==row['sha256'],'Bundle member/hash differs')
  need(row['original_source_path']not in mapped,'Ambiguous historical source mapping');mapped[row['original_source_path']]=p
  if row['role']!='exact_primary':need(row['role']not in roles,'Ambiguous fixed/proof/plan role');roles[row['role']]=p
 need({'closed_owner_proof','actual_driver_plan','prospective_fixed_steps'}<=set(roles),'Complete closed proof/plan/fixed-step set')
 need(sha(BASE)==PIN,'Literal R04 scorer changed');sp=importlib.util.spec_from_file_location('portable_literal_R04_scorer',BASE);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 data=Path(data).resolve(strict=True)
 for name,(filename,digest)in DATA.items():
  p=data/filename;need(p.is_file()and sha(p)==digest,'Exact closed data file required: '+filename);setattr(m,name,p)
 def bounded(p):
  # Historical Windows strings are matched BEFORE any platform path resolve.
  if str(p)in mapped:return mapped[str(p)]
  local=Path(p).resolve(strict=True);need(local.is_relative_to(folder)and local.is_file(),'Unmapped original path is never opened');return local
 m.bounded=bounded;m.FIXED=roles['prospective_fixed_steps'];out=m.score(roles['closed_owner_proof'])
 out['schema']='DEE.PI10.actual_adoption_science_metrics.PORTABLE_R05';out['portable_recalculation']={'index':info(index),'mapped_original_paths':len(mapped),'original_absolute_input_paths_opened':False,'literal_R04_scoring_source':info(BASE),'fixed_reader_paths_and_expected_values_unchanged':True,'data':[info(data/f)for f,_ in DATA.values()],'Native':0}
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--indice-portatil',type=Path,required=True);ap.add_argument('--fuentes-dir',type=Path,required=True);ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args();need(not a.salida.exists(),'Existing output preserved');v=run(a.indice_portatil,a.fuentes_dir);a.salida.parent.mkdir(parents=True,exist_ok=True)
 with a.salida.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':info(a.salida),'measured_adoption_metrics':v['measured_adoption_metrics'],'Native':0},ensure_ascii=False))
