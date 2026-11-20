"""Targeted passive source/provenance index; never imports historical runners."""
from datetime import datetime,timezone
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CPC4=ROOT.parents[1]
CPC3=CPC4.parent/'CPC3'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    sources=[
      ('I02_BODY',CPC3/'fuentes_pertinentes/I02/RUNNERS/paired_relative_apparatus_v2.py',
       'Real constructor: A/B at midpoint+-X; semantic4 tetra supports; local clocks; finite/persistent reader choice.'),
      ('I02_PATTERNS',CPC3/'fuentes_pertinentes/I02/RUNNERS/run_d09_relative_readout_longevity.py',
       'Actual topologically valid support patterns and finite longitudinal observers.'),
      ('I02_RENEWED_READER',CPC3/'fuentes_pertinentes/I02/RUNNERS/run_d14_persistent_native_reader.py',
       'semantic4 source two cells upstream renews read interaction; contrasts finite semantic1 and no_reader. Source RAW fixed does not mean clock fixed.'),
      ('R04_RECURRENCE',CPC3/'fuentes_pertinentes/I01/REWRITE_WORK/RUNNERS/reset_apparatus_v1.py',
       'Actual prepared recurrent/reset mechanism; not inferred from its name.'),
      ('R14_FEEDBACK',CPC3/'fuentes_pertinentes/I01/REWRITE_WORK/RUNNERS/feedback_apparatus_v1.py',
       'Finite prepared action/consequence/policy/action; no_action/no_penalty/wrong_consequence alternatives.'),
      ('PRODUCT4_INFORMATION',CPC4/'referencias/fuentes/fuentes/producto4/source/src/informative.cpp',
       'NativeInformationSession N47 finite offaxis comparison/access/later-use; FinitePolicySession N67 one prepared retainP/switchQ revision. Not a renewable learned utility controller.'),
      ('PRODUCT4_API',CPC4/'referencias/instrumento_minimo/include/dee_thinking/cognitive.hpp',
       'CognitiveSession full continuing operative state; NativeAssociationSession finite online collision relations; no arbitrary external-error writing.')]
    destination=ROOT/'resultados/auditor/source_references';destination.mkdir(parents=True,exist_ok=True)
    rows=[]
    for key,path,scope in sources:
        row={'id':key,'source':str(path),'exists':path.exists(),'scope':scope,'historical_runner_executed':False}
        if path.exists():
            payload=path.read_bytes();copy=destination/(key+'_'+path.name+'.txt')
            if copy.exists():assert copy.read_bytes()==payload
            else:copy.write_bytes(payload)
            row.update(sha256=sha(path),bytes=len(payload),passive_copy=str(copy.relative_to(ROOT)))
        rows.append(row)
    report={'utc':datetime.now(timezone.utc).isoformat(),'mode':'DIRECTED_SOURCE_READING_NOT_NATIVE_EXECUTION',
        'sources':rows,'after_T0_policy':'Only declared experience inputs/native evolution. Never copy an expected output, delta, phase or error from evaluator to memory.',
        'observer_plan':{'N':67,'H':[26,36,16],'D':[26,44,24],
          'windows':[[85,86],[93,94],[160,161],[227,228]],
          'fields':['RAW_uint64','clock_uint64','state','semantic','s_reg','dx','dy','dz','activity','26neighbor_presence_and_absence'],
          'limits':'Port/field/kinematic compatibility is not unique genealogy. Frozen domains and actual guard branches required for causal claims.'},
        'dependencies':'No GUDHI requested; no historical suites rerun; public product4 used for new technical windows only.'}
    out=ROOT/'resultados/auditor/SOURCE_REVIEW.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'sources':len(rows),'recovered':sum(x['exists'] for x in rows),'output':str(out)}))

if __name__=='__main__':main()
