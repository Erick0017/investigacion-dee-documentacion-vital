"""Seal the scientific handoff before testing the exact ZIP; no simulator work."""
import json
import platform
import sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,identity
from supervisor import remaining

def main():
    registry=json.loads((ROOT/'revision/INDICE_EVIDENCIA.json').read_text(encoding='utf-8'))
    budget=json.loads((ROOT/'BUDGET.json').read_text(encoding='utf-8-sig'))
    jobs=[]
    for path in sorted((ROOT/'jobs').glob('*/COMMAND.json')):
        m=json.loads(path.read_text(encoding='utf-8'));jobs.append({'job':path.parent.name,'status':m['status'],'exit_code':m['exit_code'],'elapsed_seconds':m['elapsed_seconds']})
    assert all(j['status']!='RUNNING' for j in jobs)
    selected=['src/selective_native.py','src/residue_regulation.py','src/integrated_revision.py','src/integrated_public.py',
              'src/run_integrated_revision.py','app/console.py','ejecutar.py','configuraciones/integrated_revision.json','configuraciones/CLEAN_PLAN.json']
    preserved=json.loads((ROOT/'genealogia/BASE_SOURCE_IDENTITY.json').read_text(encoding='utf-8'))
    provenance={'schema':'CPC7.scientific-handoff.v1','project':'DEE Universe / INVESTIGACION DEE',
        'project_author':'Ivan Erick Tlaltecatl Morales','sealed_utc':datetime.now(timezone.utc).isoformat(),
        'instrument':identity(),'kernel_source_sha256':sha(ROOT/'genealogia/kernel_v27.cpp'),
        'kernel_source_matches_frozen':sha(ROOT/'genealogia/kernel_v27.cpp')=='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31',
        'budget':budget,'remaining_seconds_original_at_seal':remaining(),'budget_restarted':False,
        'platform':{'system':platform.system(),'machine':platform.machine(),'python':platform.python_version()},
        'selected_final_sources':{p:sha(ROOT/p) for p in selected},
        'historical_source_copy_record':{'path':'genealogia/BASE_SOURCE_IDENTITY.json','sha256':sha(ROOT/'genealogia/BASE_SOURCE_IDENTITY.json'),'record':preserved},
        'scientific_registry':{'path':'revision/INDICE_EVIDENCIA.json','sha256':sha(ROOT/'revision/INDICE_EVIDENCIA.json'),'counts':registry['counts']},
        'native_law_modified':False,'new_wheel_compiled':False,'new_product_version_published':False,
        'new_external_redacted_export_created':False,'synthetic_model_data':True,'external_physical_measurements':False,
        'identity_vs_function':'Hashes establish identity. Native replay, controls and held-out histories establish the finite functions, separately.',
        'reproduction_protocol':'The exact candidate is extracted and its included wheel installed offline. The internal clean plan runs real native trajectories before auditor comparisons. Its report stays outside the immutable ZIP.',
        'supervision':'Windows JobObjects for owned workers, finite task deadlines and a single original UTC/QPC budget. No foreign process is terminated.',
        'limitations_document':'revision/LECTURA_PROVISIONAL.md','supervised_job_records':jobs}
    put(ROOT/'PROVENANCE.json',provenance)
    put(ROOT/'REANUDACION.json',{'schema':'CPC7.scientific-closure.resume.v1','updated_utc':provenance['sealed_utc'],
        'budget_file_sha256':sha(ROOT/'BUDGET.json'),'budget_restarted':False,'remaining_seconds_original':remaining(),
        'scientific_work_status':'CLOSED_AT_MEASURED_FINITE_SCOPE','last_completed_frontier':'U0 integrated revision T472, pilot/control/reserve and live restore+continuation',
        'primary_registry':'revision/INDICE_EVIDENCIA.json','primary_registry_counts':registry['counts'],
        'checkpoints':['resultados/integrated_revision/IR_P01_GUARDED_M1/T472.deetsnap','resultados/integrated_revision/IR_R607_GUARDED_M1/T472.deetsnap','resultados/demo_live_u0_integrated_03/sesion_continuada.deetsnap'],
        'code_configuration':'PROVENANCE.json records selected hashes; final MANIFEST covers all payload members.',
        'next_delivery_task':'Test the exact sealed ZIP and publish atomically; external verification report is the authority for that container.',
        'pending_scientific_questions':['General experience-learned source/need/regulation policy','Learned selective access beyond two own banks','Cooperating complete compounds and new social learning','New-referent semantic composition and functional NSM65 integration','Continued access beyond measured472 and further updates'],
        'continuation_authority':'A future scientific extension requires new user authorization; no background work is scheduled.',
        'global_deadline':budget['deadline_utc']})
    print(json.dumps({'science_sealed':True,'remaining_original_seconds':remaining(),'counts':registry['counts']}))

if __name__=='__main__':main()
