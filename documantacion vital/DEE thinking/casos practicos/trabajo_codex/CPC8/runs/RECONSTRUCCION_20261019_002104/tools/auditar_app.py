"""Audit current native demo, not a replacement semantic evaluator."""
import argparse,gc,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from integracion.longitudinal_e1 import LongitudinalE1Session
from integracion.relational_pair import physical
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def frames(folder):
 return[x['contenido']for x in(read_line for read_line in(map(json.loads,(folder/'OBSERVACIONES.jsonl').read_text(encoding='utf-8').splitlines())))if x['origen']=='ENTE']
def run(out):
 p=ROOT/'resultados/app/DEMO_P01';c=ROOT/'resultados/app/DEMO_C01';primary=ROOT/'resultados/integracion/LCE_P01_FRESH_LONGITUDINAL'
 a=LongitudinalE1Session.load(p/'E1_T549.deetsnap.gz');ap=physical(a.world);ar=a.receipts();av=a.view();del a;gc.collect()
 b=LongitudinalE1Session.load(primary/'T549.deetsnap.gz');bp=physical(b.world);br=b.receipts();bv=b.view();del b;gc.collect()
 pf={x['tick']:x for x in frames(p)};cf={x['tick']:x for x in frames(c)}
 same_receipts={x['id']:x['receipt']for x in ar}=={x['id']:x['receipt']for x in br}
 result={'schema':'CPC8R.app.actual_execution.audit.v1','demo_directory':p.relative_to(ROOT).as_posix(),'reference_directory':primary.relative_to(ROOT).as_posix(),
 'exact_full_physical549_equal':ap==bp,'native_receipts_by_id_equal':same_receipts,'view549_equal':av==bv,'app_physical549':ap,'reference_physical549':bp,
 'actual_common206':pf[206]['encuentro_comun'],'actual_old_words549':pf[549]['bancos_senal_compuesta'],'modal_receiver227':pf[227]['emisiones_receptor_en_tick_actual'],
 'new_quantity338_vs_noaddition_control':{'with':pf[338]['cantidad']['center'],'without':cf[338]['cantidad']['center']},
 'all_reported_views_passive':all(x['observacion_pasiva_comprobada']for x in pf.values())and all(x['observacion_pasiva_comprobada']for x in cf.values()),
 'sample_provenance':{'engine':'Official installed4.5, identity in jobstdout','new_world':'Each demo createsfreshT0; saved/loaded206 in positive, no re-teaching at load.','interpretation':'Structured parser routes user requests to fixed declared ports; not autonomous routing or free language.'},
 'source_hashes':{str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest()for x in(ROOT/'app/experimento.py',ROOT/'ejecutar.py',ROOT/'configuraciones/demo_e1.jsonl',ROOT/'configuraciones/demo_control.jsonl')},
 'primary_source_change_warning':'If executable or eventfiles change, repeat affected demos; these hashes identify the exact tested app.'}
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:result[k]for k in('exact_full_physical549_equal','native_receipts_by_id_equal','view549_equal','all_reported_views_passive')}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.out)
