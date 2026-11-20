"""Post-trajectory catalogue and evidence indexes; never imported by actors."""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from campaign import put,sha

def ref(path):
    p=ROOT/path
    return {'path':str(path).replace('\\','/'),'sha256':sha(p)} if p.is_file() else {'path':str(path).replace('\\','/'),'status':'NOT_PRESENT_AT_ASSEMBLY'}

def main():
    capabilities=[
      {'id':'HERITED_RENEWED_ACCESS','function':'Acceso físico renovado a dos formas heredadas','domain':'One historical CPC4 genealogy, fixed temporal protocol, three cycles',
       'measured':'26/36/46 in239/306/373 and267/334/401; controls phase/context/report',
       'modalities':['EXPERIENCE_PROTOCOL','PHYSICAL_PROBE','NATIVE_EVOLUTION'],
       'evidence':ref('resultados/lenguaje/FINAL_EVIDENCE_INDEX.json')},
      {'id':'TWO_RELATIONS_RETAINED','function':'Conservación de una memoria relativa al adquirir otra','domain':'N47, two cells, eight frozen cases through520',
       'measured':'First delta +/-1 retained while second acquires +/-1; H0=0; query400 rejectedOccupied separately',
       'modalities':['EXPERIENCE_PROTOCOL','PASSIVE_OBSERVATION','PHYSICAL_PROBE'],
       'evidence':ref('resultados/auditor/REGULATION_RETENTION_REVIEW.json')},
      {'id':'ABCD_SOCIAL_AND_ROLE_EXCHANGE','function':'Comunicación física y utilización social porD, retorno deD aB',
       'domain':'N67, finite mobile functional cores, v3 reference0..431',
       'measured':'21->37->58->74; D79/84; native relay89 reachesB350; B94@417',
       'modalities':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION','PHYSICAL_PROBE','DIAGNOSTIC_FORK'],
       'evidence':ref('resultados/red/NETWORK_MEASUREMENTS_SUMMARY.json')},
      {'id':'CONTEXTUAL_TASK_AND_NATIVE_FILTER','function':'Dos bancos y neutralización física de interferencia toroidal',
       'domain':'Separate frozen dual_habitat and fixed_counterflow preparations, not retroactive alteration of v3',
       'measured':'Baseline Flat utility4; exact RAW-only diagnostic rescue5; fixed neutralizer0 givesFlat5 versus NO/SHAM4, N5, benign6, reservedFlat5',
       'modalities':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION','DIAGNOSTIC_FORK'],
       'limit':'Neutralizer is a designed fixed circuit, not an attention policy acquired from consequences',
       'evidence':ref('resultados/red/NETWORK_MEASUREMENTS_SUMMARY.json')},
      {'id':'HISTORY_DEPENDENT_EXPRESSION','function':'Misma experiencia aplicada, expresión diferente por contexto adquirido',
       'domain':'Two I02 historical preparations with fixed upstream event',
       'measured':'Both Applied; occupied material inAB vs void delivery inBA; delta persists, expression changes',
       'modalities':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION','PASSIVE_OBSERVATION'],
       'evidence':ref('resultados/auditor/NATIVE_PREEMPTION_RECONSTRUCTION.json')},
      {'id':'CONTINUOUS_NATIVE_TO_LANGUAGE','function':'Misma red hasta1431, enseñanza posterior y consultas en1501/1529',
       'domain':'Finite GroundedSession; same world, current F7/R3 sensor',
       'measured':'Two forms with swapped/unpaired/omitted controls and two complete translated worlds',
       'modalities':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION','PHYSICAL_PROBE'],
       'evidence':ref('resultados/lenguaje/LANGUAGE_SUMMARY.json')},
      {'id':'NEW_DIRECTION_FORMS','function':'Adquisición posterior de dos formas relativas al signoZ',
       'domain':'Same MAIN1529..1634; separate reserved source/payload variations',
       'measured':'New21 readouts1606/1634; old26 readout absent1568/1596',
       'limit':'Four sequentially acquired forms are not four simultaneously retained available meanings',
       'modalities':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION','PHYSICAL_PROBE'],
       'evidence':ref('resultados/lenguaje/NSM65_EVOLUCION.json')},
      {'id':'PERSISTENT_PORTABLE_DEMO','function':'Interacción por eventos, sesión física y operativa restaurable',
       'domain':'WindowsCPython3.13x64 official4.0.0; finite validated protocols',
       'measured':'Native0..1501, other process new query1529, new direction experiences1634, later input1637; pending input1640 continuation equal1643',
       'modalities':['PASSIVE_OBSERVATION','EXPERIENCE_PROTOCOL','PHYSICAL_PROBE'],
       'evidence':ref('resultados/technical/PUBLIC_UI_FINAL05/PUBLIC_UI_CHECKS.json')}
    ]
    put(ROOT/'CAPACIDADES.json',{'schema':'CPC4.A02.capabilities.v1','author':'Ivan Erick Tlaltecatl Morales',
      'instrument':'DEE thinking4.0.0','kernel':'v27','capabilities':capabilities,
      'scientific_scope':'Scoped physical mechanisms and observations; no automatic global cognitive verdict',
      'open_objectives':[
        {'objective':'Attention/relevance revised by experience in the ABCD task','status':'INCONCLUSIVE','local_limit':'Fixed physical neutralizer and history-dependent expression established; consequence-to-policy learning not implemented as an evidenced chain'},
        {'objective':'All65meanings accumulated in one participant','status':'NOT_MEASURED','local_limit':'Catalog documented; inherited2 and new4 local associations are distinct cohorts/finite windows'},
        {'objective':'YO/TU, BEFORE/AFTER, general NSM composition','status':'NOT_MEASURED','local_limit':'Physical role exchange and numeric/vector integration do not establish deictic or linguistic composition'},
        {'objective':'Autonomous convention adaptation by both emitters and receivers','status':'INCONCLUSIVE','local_limit':'Each acquired native directional relations; jointly negotiated convention not isolated'}]})
    put(ROOT/'NSM65_EVOLUCION.json',{'schema':'CPC4.A02.NSM.pointer.v1','registered_catalog_entries':65,
      'full_entry_matrix':ref('resultados/lenguaje/NSM65_EVOLUCION.json'),
      'case_and_65_entry_index':ref('resultados/lenguaje/FINAL_EVIDENCE_INDEX.json'),
      'scoped_inherited_associations_renewed':2,'new_scoped_associations_acquired_sequentially':4,
      'new_words':['BUENO','MALO','ARRIBA','DEBAJO'],'simultaneous_retention_of_all_four':'Not observed under the tested later probes',
      'new_NSM_composition_tested':False,'universal_prime_mastery_count':0,
      'rule':'Do not add counts across individuals or equate a registered expression with acquired meaning.'})
    rows=[]
    for p in sorted((ROOT/'resultados/regulacion/DUAL_CONFIRMATION').glob('*/MEASUREMENTS.json')):
        d=json.loads(p.read_text(encoding='utf-8'));panel=[]
        for x in d['rows']:
            if x['tick'] in (2,250,259,262,270,399,400,403,520):
                panel.append({'tick':x['tick'],'deltas':{k:v['delta'] for k,v in x['memories'].items()},
                    'comparator_directions':{k:v['physical']['comparator']['direction'] for k,v in x['memories'].items()}})
        rows.append({'case':d['case'],'evidence':ref(p.relative_to(ROOT)),'panel':panel,
          'final_deltas':{k:v['delta'] for k,v in d['final']['memories'].items()},'receipts':d['receipts']})
    put(ROOT/'RETENCION.json',{'schema':'CPC4.A02.retention.v1','independent_worlds':len(rows),'physical_trajectories':rows,
       'inherited_access':ref('resultados/lenguaje/FINAL_EVIDENCE_INDEX.json'),
       'language_retention_and_failed_old_access':ref('resultados/lenguaje/LANGUAGE_SUMMARY.json'),
       'scope':'Rows across different worlds are not one individual. Delta, reader availability, expression and task use are recorded independently.'})
    trace_path=ROOT/'resultados/auditor/V3_MESSAGE_RECONSTRUCTION/MESSAGE_RECONSTRUCTION.json'
    trace=json.loads(trace_path.read_text(encoding='utf-8'))
    with (ROOT/'MENSAJES.jsonl').open('w',encoding='utf-8') as f:
        for seg in trace['segments']:
            c=seg['configuration'];samples=seg['samples']
            f.write(json.dumps({'genealogy':'V3_FULL_U','segment':c,'coverage_certified':seg['prefix_certified'],
              'observed_samples':len(samples),'first':samples[0],'last':samples[-1],
              'evidence':ref(trace_path.relative_to(ROOT)),
              'branch_evidence':ref('resultados/auditor/V3_MESSAGE_RECONSTRUCTION/MESSAGE_BRANCH_RECONSTRUCTION.json'),
              'attribution':'Field-and-branch forward reconstruction. Functional necessity is tested in separate intervention cohorts, not inferred from this label.'},ensure_ascii=False)+'\n')
    with (ROOT/'DIALOGOS.jsonl').open('w',encoding='utf-8') as f:
        for p in sorted((ROOT/'resultados/demo').rglob('DIALOGOS.jsonl')):
            for i,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
                if line.strip():f.write(json.dumps({'session':str(p.parent.relative_to(ROOT)),'line':i,'source':ref(p.relative_to(ROOT)),'dialogue':json.loads(line)},ensure_ascii=False)+'\n')
    checkpoints=[]
    for p in sorted((ROOT/'resultados').rglob('*.deetsnap')):
        checkpoints.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
    put(ROOT/'checkpoints/INDEX.json',{'schema':'CPC4.A02.checkpoint_index.v1','copies_made':0,'files':checkpoints,
      'scope':'Full bytes exist at the referenced result paths; this index does not duplicate them or infer episode identity from filenames.'})
    put(ROOT/'REANUDACION.json',{'schema':'CPC4.A02.resume.v1','generated_utc':datetime.now(timezone.utc).isoformat(),
       'budget_identity':ref('BUDGET.json'),'work_requires_new_authorized_execution':True,
       'no_automatic_background_continuation':True,
       'completed':['Inherited renewed access','Two relative memories and acquisition/retention controls','ABCD native roles and context contrasts','Native-to-language continuation','Directional second vocabulary and old-retention panel','Causal residual trace/rescue and fixed counterflow'],
       'state_choices':[
         {'path':'resultados/demo/CENTRAL_V3_01/RED_LENGUAJE_T1501.deetsnap','tick':1501,'next':'cargar then consultar MALO; one finite word query remains'},
         {'path':'resultados/demo/CONTINUAR_V3_02/RED_LENGUAJE_T1529.deetsnap','tick':1529,'next':'direcciones begins a distinct new experience/probe block in the same world'},
         {'path':'resultados/demo/DIRECTION_CONTINUE04/RED_T1637.deetsnap','tick':1637,'next':'Passive observe or declared physical input; completed linguistic protocol is historical, not automatically reset'},
         {'path':'resultados/regulacion/DUAL_CONFIRMATION/AB_AB/T520.deetsnap','tick':520,'next':'Two acquired deltas; reader/query availability must be checked rather than clearing sites'}],
       'pending':['Acquired consequence-to-relevance policy in the same ABCD network',
                  'Accumulated linguistic accessibility after consumptive queries and further teaching',
                  'Deictic and relational NSM composition beyond the measured local classes'],
       'regulated_checkpoint':ref('resultados/red/fixed_counterflow_continuation01/T937.deetsnap'),
       'validation_state':'CLEAN_REPRODUCTION_COMPLETE' if (ROOT/'resultados/reproduccion_limpia/CLEAN_REPRODUCTION.json').exists() else 'SCIENTIFIC_CUT_CLOSED_CLEAN_REPRODUCTION_PENDING'})
    print(json.dumps({'capabilities':len(capabilities),'retention_worlds':len(rows),'checkpoint_files':len(checkpoints)}))

if __name__=='__main__':main()
