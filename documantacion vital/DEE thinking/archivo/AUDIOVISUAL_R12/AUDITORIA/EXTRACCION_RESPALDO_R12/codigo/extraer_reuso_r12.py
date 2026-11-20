"""Reuse only existing R08 extracts/models and the archived ECI02 closure.

No DEE imports, new worlds, ticks, experiments or changes to the old production.
"""
from pathlib import Path
from copy import deepcopy
import gzip,hashlib,importlib,json,shutil,sys

ROOT=Path(__file__).resolve().parents[1]
R08=ROOT.parent/'AUDIOVISUAL_R08'
THINK=ROOT.parent.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)

def main():
    out=ROOT/'evidencia_reutilizada';out.mkdir(exist_ok=True)
    sources=[]
    for rel in ['infraestructura/FUENTES_MECANISMOS_S06_S11_R08.json',
                'evidencia_principal/PRINCIPAL_R08_DATOS_EXACTOS.json.gz',
                'verificaciones/DISCREPANCIA_CONTROL_Z_R08.json']:
        src=R08/rel;dst=out/src.name
        if dst.exists():assert dst.read_bytes()==src.read_bytes()
        else:shutil.copy2(src,dst)
        sources.append({'original':str(src),'included':str(dst.relative_to(ROOT)),'sha256':sha(src)})
    sys.path.insert(0,str(R08/'codigo'))
    mech=importlib.import_module('escenas_mecanismos_r08')
    principal=importlib.import_module('escenas_principal_r08')
    plan={
       'CPC9_composition':('S07',['S07_P01','S07_P02','S07_P03','S07_P04']),
       'IC01_communication':('S08',['S08_P01','S08_P02','S08_P03']),
       'CYCLE02_consequence':('S09',['S09_P01']),
       'ENTE01_external':('S09',['S09_P03','S09_P04']),
       'ENTE02_transfer':('S10',['S10_P01','S10_P02','S10_P03','S10_P04']),
       'FI01_many_contributions':('S11',['S11_P01']),
       'ECI02_principal':('S11',['S11_P03','S11_P04'])}
    cases={}
    for key,(scene,shots) in plan.items():
        variations={}
        for shot in shots:
            rows=[];seen=set()
            for i in range(101):
                progress=min(.999999,i/100)
                fn=principal.model if key=='ECI02_principal' else mech.model
                m=fn(scene,shot,progress)
                payload={'panels':m.get('panels',[]),'bounds':m.get('bounds'),
                         'source':m.get('source'),'source_refs':m.get('source_refs'),
                         'scheme':m.get('scheme'),'evidence_type':m.get('evidence_type'),
                         'stage_jump':m.get('stage_jump'),'crop_notice':m.get('crop_notice')}
                # An editorial progress field is not a new physical state.
                for x in (payload,payload.get('scheme') or {}):x.pop('progress',None)
                code=hashlib.sha256(canonical(payload).encode()).hexdigest()
                if code in seen:continue
                seen.add(code)
                rows.append({'origin_shot':shot,'origin_progress_first':progress,
                             'extraction_sha256':code,**payload})
            variations[shot]=rows
        cases[key]=variations
    # Exact bytes and provenance of the extra archived clean-app proof.
    src=THINK/'archivo/analisis_transversal_cognitivo/ECI02/CONSOLIDACION_OPERATIVA/datos/PRUEBA_CARPETA_ESENCIAL_R01.json'
    dst=out/src.name
    if dst.exists():assert dst.read_bytes()==src.read_bytes()
    else:shutil.copy2(src,dst)
    sources.append({'original':str(src),'included':str(dst.relative_to(ROOT)),'sha256':sha(src)})
    proof=json.loads(src.read_text(encoding='utf8'))
    assert proof['zero_tick_reopen_physical_equal'] and all(proof['zero_tick_reopen_Native_protocol_equal'].values())
    # This proof reopens the final state but does not establish a NEW query
    # after that reopen. Keep that distinction explicit in scene S03.
    summary={k:proof[k] for k in ['life','role','initial_record','last_saved_before_reopen',
        'second_owner_started_from_exact_latest_snapshot','zero_tick_reopen_physical_equal',
        'zero_tick_reopen_Native_protocol_equal','responses','all_two_fixed_contracts_correct',
        'final_record','native_ticks_total']}
    summary['no_new_post_reopen_query_claim']=True
    save(out/'REUSO_R12_DATOS.json',{'schema':'DEE.R12.readonly.reused_sources.v1',
        'new_DEE_ticks':0,'sources':sources,'cases':cases,'clean_reopen':summary,
        'method':'Existing recorded panel observations only. Editorial original labels are not new physical events.',
        'limitations':['No source artifact is modified. No scientific replay.',
                      'No additional native query after the archived final reopen is inferred.']})
    print(json.dumps({'new_DEE_ticks':0,'source_count':len(sources),
        'variants':{k:{s:len(v)for s,v in d.items()}for k,d in cases.items()},
        'file':str(out/'REUSO_R12_DATOS.json')},ensure_ascii=False))
if __name__=='__main__':main()
