"""Prospective post-reserve literal protocol/typed checks; no owner or ticks."""
import argparse,ast,hashlib,importlib.util,json
from pathlib import Path
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main(system,novelty_path,out):
    source=Path(__file__).with_name('post_reserva_apd_r01.py');ast.parse(source.read_text(encoding='utf8'));post=module('post_prospective_data_only',source);queue=module('post_typed_validation_only',system/'app/cola_local.py');novelty=json.loads(novelty_path.read_bytes());excluded={tuple(v)for v in novelty['excluded_pairs']+novelty['selected_pairs']};checks={};pairs=[]
    for request in post.REQUESTS:queue.validate_request(request['payload']);checks['typed_'+request['id']]=True
    checks['exactly_two_requests']=len(post.REQUESTS)==2;checks['six_memory_seven_functions']=list(map(lambda r:len(r['payload']['situaciones']),post.REQUESTS))==[6,7];checks['no_teaching_or_route_teaching']=all(r['modo']not in('apd-docencia','apd-ruta-docencia')and r.get('operacion_memoria')not in('enseñar','revisar')for q in post.REQUESTS for r in q['payload']['situaciones']);checks['cost_returns_explicitly_omitted']=all(q['payload']['retorno']=='omit'for q in post.REQUESTS)
    for pair in post.PAIRS:pairs.append({'pair':list(pair),'absent_from_indexed_P01_P26_and_all_R01_R02_R03_planned_pairs':pair not in excluded})
    checks['six_literal_pairs_new_against_indexed_prior_set']=all(p['absent_from_indexed_P01_P26_and_all_R01_R02_R03_planned_pairs']for p in pairs)
    result={'schema':'DEE.APD01.prospective_post_reserve_candidate.N0.v1','status':'WAIT_ACTUAL_R03_CUT_NOT_EXECUTABLE','requests':post.REQUESTS,'literal_pairs':pairs,'new_pair_exclusion_witness':{'file':str(novelty_path),'sha256':sha(novelty_path)},'checks':checks,'all_true':all(checks.values()),'harness':{'file':source.name,'sha256':sha(source)},'same_life_required':'ASISTENTE_MAIN reached after R03; no snapshot rollback, diagnostic fork or new identity','maximum_owner_seconds':900,'hard_RAM_bytes':536870912,'new_ticks':0,'no_Runtime_imports':True,'owner_processes':0,'scope':'Source/payload freeze is prospective. Actual initial snapshot/hash and source26 are bound only after real R03 STOP and Root GO; current ASISTENTE_MAIN is not queried by this preparation.'}
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'file':str(out),'sha256':sha(out),'checks':checks,'new_ticks':0}));return not result['all_true']
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--exclusion',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();raise SystemExit(main(a.sistema,a.exclusion,a.salida))
