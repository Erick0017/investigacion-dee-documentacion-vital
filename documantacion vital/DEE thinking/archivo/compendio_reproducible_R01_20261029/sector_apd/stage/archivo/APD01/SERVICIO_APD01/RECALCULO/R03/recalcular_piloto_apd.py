"""Portable reinspection of the short APD pilot, not a repeated experiment."""
import argparse,gzip,hashlib,importlib.util,json
from pathlib import Path

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
audit=module('APD_pilot_posthoc_auditor',Path(__file__).with_name('auditar_apd_resultados_r04.py'))
service=module('APD_pilot_memory_decoder',Path(__file__).with_name('recalcular_servicio_apd.py'))
def calculate(root):
    primary=root/'PILOTO_APD.json.gz';value=json.loads(gzip.decompress(primary.read_bytes()));records=value['records'];checks={};issues=[];raw=0;numeric=[];memory=[]
    def check(label,ok):
        checks[label]=bool(ok)
        if not ok:issues.append(label)
    for identifier in('apdpilot_apd','apdpilot_count','apdpilot_old6','apdpilot_queued_gamma'):
        r=records.get(identifier,records.get('queued_gamma_executed_once')if identifier=='apdpilot_queued_gamma'else None)
        check(identifier+'_completed_transport',r is not None and r.get('status','completed')=='completed')
        if not r:continue
        answer=json.loads(r['result'])if isinstance(r.get('result'),str)else r;top=answer.get('result',{})
        if identifier in('apdpilot_apd','apdpilot_count'):
            result=audit.audit(top['rows'][0],root/'artefactos');numeric.append({'id':identifier,'audit':result});check(identifier+'_physical_decoder_and_real_bytes',not result['issues'])
        for path,node in service.walk(top):
            if all(k in node for k in('raw','state','s_reg','semantic','direction')):
                decoded=service.fields(node['raw']);raw+=1;check(identifier+'_'+path+'_RAW',all(node[k]==v for k,v in decoded.items()))
            if 'context_signal'in node and isinstance(node.get('reader'),dict)and'panel'in node['reader']:
                command=service.memory(node['reader']);check(identifier+'_'+path+'_fixed_memory_decoder',command==node['reader']['formed_native_command']);memory.append({'id':identifier,'context':node['context_signal'],'tick':node['read_tick'],'sign':command})
        fence=top.get('INSTRUMENTO_FENCE')
        if fence:check(identifier+'_observed_guard_denials_empty',not fence['denied'])
    first=records['saved_pending']['committed_snapshot'];second=records['reloaded']['committed_snapshot'];check('same_native_fields_after_process_change',first['physical']==second['physical']);check('same_APD_environment_and_external_protocol_after_process_change',first['operational_dependencies']==second['operational_dependencies'])
    check('genuine_queued_request_executed_once',records['literal_pending_admission']['admission']=='queued'and records['queued_gamma_executed_once']['id']=='apdpilot_queued_gamma')
    history=value['protocol']['auditor_only_prior_signs_not_actor_input'];old=[r for r in memory if r['id']=='apdpilot_old6'];check('old_panel_exact_six_unique_contexts',len(old)==6 and len({r['context']for r in old})==6);check('old_panel_matches_explicit_preceding_history',{r['context']:r['sign']for r in old}==history)
    check('finalize_zero_ticks_and_fields',records['after_stop']['physical']==records['final']['physical']);check('same_identity_and_native_continuation',all(value['protocol']['initial'][k]==records['final'][k]for k in('life_id','world_id','parent'))and records['final']['physical']['tick']>value['protocol']['initial']['physical']['tick'])
    for name,expected in value['protected_before'].items():check('original_'+name,value['protected_after'].get(name)==expected)
    for identity in value['protocol']['source']:
        f=root/'PILOTO_CODIGO'/identity['file'];check('executed_pilot_source_'+identity['file'],f.stat().st_size==identity['bytes']and hashlib.sha256(f.read_bytes()).hexdigest()==identity['sha256'])
    check('no_recorded_pilot_harness_error',not records.get('harness_error'));check('original_operational_checks_all_true',all(value['checks'].values()))
    return {'schema':'DEE.APD01.portable_short_pilot_recalculation.v1','sources':[{'file':'PILOTO_APD.json.gz','sha256':hashlib.sha256(primary.read_bytes()).hexdigest()}],'checks':checks,'issues':issues,'RAW_observations_checked':raw,'numeric_and_count':numeric,'memory_uses':memory,'initial':value['protocol']['initial'],'final':records['final'],'host_seconds_recorded':value['host_seconds'],'original_functional_issues':value['functional_issues'],'scope':'Archived field/receipt/byte and process-witness verification, not native reproduction. Legacy guard boolean is not treated as a complete history-read ACL or OS sandbox. The pilot is operational and belongs to the same later reserve life, not a separate learner or sixty-minute trial.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open('x',encoding='utf8')as f:json.dump(r,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':r['issues'],'RAW':r['RAW_observations_checked']}));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
