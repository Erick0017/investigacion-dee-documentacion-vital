"""Bounded static checks plus explicit reviewed dataflow; not a formal proof."""
import argparse
import ast
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    files=['app/console.py','src/integrated_public.py','src/selective_native.py','src/residue_regulation.py','src/update_methods.py',
           'src/integrated.py','src/order_memory.py','src/endogenous/comparison_need.py','src/comparadores/models.py']
    found=[]
    for name in files:
        path=ROOT/name;text=path.read_text(encoding='utf-8');tree=ast.parse(text)
        strings=[(n.lineno,n.value) for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
        forbidden=[{'line':line,'value':value} for line,value in strings if 'EVALUATOR.json' in value or ('fixtures_v1' in value and 'RESERVED' in value)]
        assert not forbidden,(name,forbidden)
        writes=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('diagnostic_fork','set_raw','set_clock')]
        found.append({'file':name,'sha256':sha(path),'no_literal_evaluator_or_reserved_answer_path':True,'state_intervention_call_lines':writes})
    models=(ROOT/'src/comparadores/models.py').read_text(encoding='utf-8')
    assert 'open(' not in models and 'read_text(' not in models
    result={'schema':'CPC7.information_boundary.review.v1','status':'BOUNDED_CHECKS_PASSED','files':found,
        'reviewed_dataflow':[
            {'layer':'GENERATOR','input':'bank_values / history / actual','operation':'Encodes present experiences and fixed pedagogical opportunities through declared interfaces; never consulted to decode a reserved response.'},
            {'layer':'PARTICIPANT','input':'World state plus declared channel events','operation':'Native v27 evolves; request source and information direction are not selected by a host readout callback.'},
            {'layer':'INTERFACE','input':'Structured visitor command','operation':'Names an explicit operation or physical port. Spanish alias is not an acquired semantic relation.'},
            {'layer':'AUDITOR','input':'Sealed trajectory and EVALUATOR separately','operation':'Scores after simulation, does not write outcome or chosen policy back to MAIN.'},
            {'layer':'PERSISTENCE','input':'Native snapshot and geometry/request metadata','operation':'Session restoration preserves provenance/queue. Session methods do not reconstruct an answer from requests or teaching maps.'}],
        'reviewed_interventions':'ResearchStateEdit/diagnostic_fork operate on explicit copies; initial placements and empty interfaces are experimental preparation beforeT0.',
        'limitations':['Literal/AST checks are bounded, not a formal noninterference proof. Primary data and executed source are included for independent review.',
                      'Generator and auditor code share a language/process in some experiments; their information boundaries are architectural and reviewed, not an operating-system security sandbox.',
                      'Historical external absolute paths in provenance/logs describe development. The clean extraction validates operational independence, not the absence of provenance strings.'],
        'models_no_file_reading':True,'engine_code_changed':False}
    put(a.out/'INFORMATION_BOUNDARY.json',result);print(json.dumps({'status':result['status'],'files':len(files)}))

if __name__=='__main__':main()
