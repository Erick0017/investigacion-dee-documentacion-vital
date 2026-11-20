"""Extract locators for explicit manual NSM review; never award a level."""
import hashlib,json
from pathlib import Path
FRONT=Path(__file__).resolve().parent;ROOT=FRONT.parent
HIST=ROOT.parents[2]/'CPC4'
CPC8=ROOT.parents[2]/'CPC8/runs/RECONSTRUCCION_20261019_002104'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def compact(o):return {k:o[k] for k in ('tick','site','raw','clock','state','s_reg','direction','semantic','active') if k in o}
def main():
    cat=read(FRONT/'referencias/NSM65_CATALOGO_4_5.json');old=read(CPC8/'revision/NSM65_EVIDENCIAS.json');hist=[]
    for name in ('MAIN_MINUS','FULL_PLUS','LEX_SIGNAL_OMITTED','LEX_UNPAIRED','LEX_MEMORY_CUT','LEX_SHAM','RESERVED_TRANSLATION_PLUS','RESERVED_TRANSLATION_MINUS_SWAPPED'):
        path=HIST/'resultados/confirmacion'/name/'MEASUREMENTS.json';m=read(path);lang=m['language']
        hist.append({'case':name,'original_path':str(path),'sha256':sha(path),
                     'source_hashes_at_entry':lang['source_sha256_at_entry'],
                     'lessons':[{'form_id':e['form_id'],'text_form':e['text_form'],'sensor':e['current_sensor'],'mode':e['mode']} for e in lang['lessons']],
                     'queries':[{'form_id':q['form_id'],'physical_output':q['physical_output'],'available':q['available'],
                                 'resource_class':q['resource_class'],'receipt':q['receipt'],'input_tick':q['input_tick'],'emission_tick':q['emission_tick']} for q in lang['queries']],
                     'diagnostics':lang['diagnostics']})
    source_references=[]
    for path in (FRONT/'referencias/NSM65_CATALOGO_4_5.json',CPC8/'revision/NSM65_EVIDENCIAS.json',CPC8/'revision/GENERALIZACION_RESERVADA.json',
                 HIST/'src/channel.py',HIST/'src/phase_language.py',ROOT/'revision/CALCULOS.json'):
        source_references.append({'path':str(path),'sha256':sha(path),'bytes':path.stat().st_size})
    old_positives=[]
    for e in old['entries']:
        if e['id'] in ('NSM65.ONE','NSM65.TWO','NSM65.BEFORE','NSM65.TOUCH','NSM65.MORE','NSM65.LIKE_AS'):
            old_positives.append({'id':e['id'],'historical_summary_NOT_current_E1':e['nivel_resumen_conservador'],
                                  'historical_additional_dimensions':e['dimensiones_adicionales_medidas'],'scope':e['alcance'],
                                  'dimensions':{k:e[k] for k in ('D','E','F','G','H','I')},'limit':e['limite']})
    continuations=[]
    for folder in ('E1_MAIN_1220_1371','E1_MAIN_1371_1639','E1_MAIN_1639_1907'):
        path=ROOT/'front_relations/resultados'/folder/'MEDICIONES.json';m=read(path)
        if m['status']!='MEASURED':raise AssertionError('Only sealed measured primary accepted')
        row={'case':m['case_id'],'member':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path),
             'continuity_type':m.get('continuity_type'),'last_complete_tick':m['last_complete_tick'],'parent':m['parent'],
             'RAW_clock_edits':m['MAIN_RAW_clock_edits'],'initial_physical':m.get('initial_physical'),'final_physical':m.get('final_physical'),
             'new_order_observations':[{'tick':v['tick'],'stage':v['stage'],'banks':[{'id':b['id'],'physical':compact(b['physical'])} for b in v['banks']]} for v in m.get('new_order_observations',[])],
             'late_E2_observations':[{'tick':v['tick'],'stage':v['stage'],'banks':[{'id':b['id'],'physical':compact(b['physical'])} for b in v['banks']]} for v in m.get('late_E2_observations',[])]}
        continuations.append(row)
    manual=[]
    for entry in cat['entries']:
        item={'id':entry['id'],'forma_es':entry['forma_es'],'group':entry['grupo_documental'],
              'operational_question_member':'front_semantics/revision/NSM65_PLAN_CPC9.json#'+entry['id'],
              'scope_rule':'A source-level association or prepared native prerequisite is preserved separately; no automatic E1 or semantic promotion.',
              'historical_candidate_available':entry['id'] in ('NSM65.THERE_IS','NSM65.NOT','NSM65.ONE','NSM65.TWO','NSM65.BEFORE','NSM65.TOUCH','NSM65.MORE','NSM65.LIKE_AS')}
        manual.append(item)
    out={'schema':'CPC9.NSM65.manual_review_support.v1','catalogue_count':len(manual),'source_references':source_references,
         'CPC4_assisted_current_sensor_historical_positive':hist,'CPC8_positive_scopes_not_automatically_CPC9_E1':old_positives,
         'CPC9_sealed_main_continuations_read':continuations,'entries_for_manual_review':manual,
         'no_level_assigned_by_this_script':True,'no_engine_imports':True}
    path=ROOT/'notes/NSM65_APOYO_EVIDENCIAL.json';path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'path':str(path),'sha256':sha(path),'catalogue':len(manual),'historical_lexical_cases':len(hist),'main_continuations':len(continuations)}))
if __name__=='__main__':main()
