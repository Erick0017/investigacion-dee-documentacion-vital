"""Engineering provenance and progress, not a participant or science verdict."""
import argparse,ctypes,json,time,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,sha,put

def elapsed(budget):
    now=ctypes.c_longlong();freq=ctypes.c_longlong()
    ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(now));ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
    assert freq.value==budget['qpc_frequency']
    return (now.value-int(budget['start_qpc']))/freq.value

def main():
    p=argparse.ArgumentParser();p.add_argument('--development',action='store_true');p.add_argument('--closed',action='store_true');a=p.parse_args()
    budget=json.loads((ROOT/'BUDGET.json').read_text(encoding='utf-8-sig'));sources=json.loads((ROOT/'genealogia/SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
    code=[]
    for q in sorted(list((ROOT/'src').glob('*.py'))+[ROOT/'app.py',ROOT/'ejecutar.py',ROOT/'iniciar_cpc6.ps1']):
        code.append({'path':q.relative_to(ROOT).as_posix(),'sha256':sha(q),'bytes':q.stat().st_size})
    originals=[]
    if a.development:
        from package_cpc6 import protected_sources
        originals=protected_sources(ROOT)
    documents=json.loads((ROOT/'genealogia/DIRECTED_PRODUCT_READINGS.json').read_text(encoding='utf-8'))
    report={'schema':'CPC6.provenance.v1','project':'DEE Universe / INVESTIGACION DEE','project_author':'Ivan Erick Tlaltecatl Morales',
      'campaign':'CPC6 MENTE DEE INTEGRADA','instrument':identity(),'frozen_kernel_source_sha256':sha(ROOT/'genealogia/kernel_v27.cpp'),
      'product_recompiled_or_modified':False,'historical_sources':sources['identities'],'original_protected_artifacts':originals,
      'directed_document_references':[{'file':r['file'],'sha256':r['sha256'],'document_xml_sha256':r['document_xml_sha256']} for r in documents if 'file' in r],
      'selected_genealogy_manifest':{'path':'genealogia/SOURCE_MANIFEST.json','sha256':sha(ROOT/'genealogia/SOURCE_MANIFEST.json')},
      'code_at_report':code,'N_main':67,'basic_four_buffer_estimate_bytes':32*67**3,
      'resource_scope':'9,624,416 basic-buffer bytes per N67 Runtime; excludes scratch, Python, clones, queues and telemetry. Not a measured industrial performance claim.',
      'decision_boundaries':{'participant':'Native v27 evolution of admitted fields; never reads targets, logs or audit summaries to answer.',
       'host':'Preparation, current sensors, fixed finite query schedules, rendering, persistence and evaluation.',
       'auditor':'Controls on independent forks, arrays/hashes, interpretation and resource comparisons; no corrected state returned to MAIN.'},
      'source_storage':'Historical scientific archives remain outside; only selected exact source/fixtures plus directed excerpts included. No full corpus claim.',
      'execution_generated_data':'Synthetic sandbox worlds, not measurements of an external machine, brain or universe.',
      'budget':budget,'elapsed_monotonic_seconds_at_report':elapsed(budget),'report_utc':datetime.now(timezone.utc).isoformat()}
    put(ROOT/'PROVENANCE.json',report)
    progress={'schema':'CPC6.resume.v1','state':'CLOSED' if a.closed else 'SCIENCE_CLOSED_VALIDATION_AND_PACKAGING',
      'original_budget':budget,'consumed_monotonic_seconds':elapsed(budget),'updated_utc':datetime.now(timezone.utc).isoformat(),
      'completed':['Historical identity and selected reference reproduction','Fresh U0 longitudinal lives, controls and reserves',
       'Single/two/four architecture screen and native two-compound bridge','Two sequential opaque forms and renewed first-form use after second learning',
       'Exact source/configuration and primary telemetry preserved'],
      'next_tasks':[] if a.closed else ['Finish final-profile backend and app technical checks','Exact-candidate clean reproduction','Verified atomic ZIP and transport publication'],
      'scientific_open_goals':['General NSM65 meanings and productive linguistic composition','Utility-learned autonomous regulation and information-request timing','Unlimited access and arbitrary geometry/phase transfer'],
      'original_budget_reset':False,'future_resume_requires_new_authorization':True,'background_science_after_close':False}
    put(ROOT/'REANUDACION.json',progress);print(json.dumps({'state':progress['state'],'elapsed_seconds':progress['consumed_monotonic_seconds'],'code_files':len(code)}))
if __name__=='__main__':main()
