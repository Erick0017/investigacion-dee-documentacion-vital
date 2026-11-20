"""Select the explicitly authorized CLOSED cut for the existing updater.

This edits distribution configuration only, never snapshots or a live service.
No performance-based branch selection is performed by this program.
"""
import argparse,hashlib,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
COLLAB=ROOT.parent/'cognitive sistem'

def load(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sello',type=Path,required=True);p.add_argument('--manual',required=True)
    p.add_argument('--principal',choices=('MU_MAIN_FASE_R3',),required=True,help='Explicit maintainer choice, never inferred from results.')
    p.add_argument('--salida',type=Path,required=True);a=p.parse_args();seal=load(a.sello)
    if seal.get('campaign')!='MENTE_UNIFICADA_Y_FI01'or seal.get('authorization','').find('CLOSED')<0:raise ValueError('Explicit closed-source seal required')
    manual=ROOT/a.manual
    if not manual.is_file()or sha(manual)!=seal['manual']['sha256']:raise ValueError('Selected Word differs from the sealed authority')
    selected=load(COLLAB/'actualizaciones/SELECCION.json');cut=load(ROOT/'evidencia/campanas/MENTE_UNIFICADA_Y_FI01/servicio/SERVICIO_60MIN_FASE_R17/CORTE_PARA_MANUAL.json')
    if cut['main']['life_id']!=a.principal or cut['persistent_service']['pending_or_uncertain']or not cut['persistent_service']['owner_stopped']:raise ValueError('Selected life is not the declared stopped cut')
    if cut['issues']:raise ValueError('Unresolved archived integrity discrepancy, not a functional score: inspect before distribution')
    lives=[a.principal,'MU_MAIN','MUFI_ACCESO_BASAL_T_READY','MUFI_ACCESO_BASAL_H_READY','MUFI_ACCESO_BASAL_T_GAMMA_MINUS_READY']
    admitted={r['life_id']:r for r in seal['lives']}
    for life in lives:
        card=load(ROOT/'sistema/estado/vidas'/life/'VIDA.json')
        if life not in admitted or card['snapshot_sha256']!=admitted[life]['snapshot_sha256']:raise ValueError('Life is not part of the exact closed source selection: '+life)
        if life not in selected['lives']:selected['lives'].append(life)
    selected['campaign']='MENTE_UNIFICADA_Y_FI01';selected['manual']=a.manual;selected['verification']=a.sello.resolve().relative_to(ROOT).as_posix()
    descriptions=selected.setdefault('descriptions',{})
    descriptions[a.principal]={'alias':'MENTE_UNIFICADA','scope':cut['persistent_service']['manual_results_text'],
      'limits':'Explicit imported continuation from R11, B0 re-teaching and prepared R3P0 sensor calendar. Six opaque acquired sign associations, finite raw128 input and two-request assisted chains; not six meanings, learned planner, autonomous recovery, general regulation or competent general control. Full paired journal/outbox/artifacts are mandatory; ordinary snapshot-only forks are incomplete.'}
    descriptions['MU_MAIN']={'alias':'MENTE_UNIFICADA_R11','scope':'Preserved original unified R11 trajectory, final T68924. Real persistent service with 485 completed material requests, actual worker files, six context associations and explicit beta revision; ten of twelve frozen raw128 tasks had the expected response.',
      'limits':'Adverse late sensor cases had no output candidate after D−20→−21. The later R3 preparation and its explicit re-teaching are not memories of this source life. Current post-STOP cut, complete transport and exact lineage preserved; no global promotion or reconstruction from T0.'}
    for life in lives[2:]:
        descriptions[life]={'alias':life,'scope':'Separate finite auxiliary participant at an actual complete pre-use READY checkpoint. Prepared basal query and history-conditioned P1 access can emit a native memory command once.',
          'limits':'One destructive use within its admitted domain; not MAIN knowledge, an autonomous initiative to recover, persistent general selector or P2/R2. History and snapshot stay separate.'}
    packages=selected.setdefault('research_packages',[]);base='laboratorio/campanas/MENTE_UNIFICADA_Y_FI01';ev='evidencia/campanas/MENTE_UNIFICADA_Y_FI01';target='investigacion/MENTE_UNIFICADA_Y_FI01'
    additions=[
      {'source':base,'target':target+'/A_B_CODIGO_Y_RESULTADOS','root_files_only':True,'include_patterns':['*.py','INFORME_RESULTADOS.md','CAPACIDADES_POR_VIDA.json','COBERTURA.json','DECISIONES_E_INCORPORACIONES.md','CONTINUIDAD_MENTE_UNIFICADA_Y_FI01.json','CONTINUIDAD_R11_PRESERVADA.json','CIERRE_INTERNO_A.json','PRESUPUESTO.json']},
      {'source':ev,'target':target+'/A_B_PRIMARIOS','root_files_only':True,'include_patterns':['*.json.gz','RECALCULO*.json']},
      {'source':ev+'/codigo_ejecutado','target':target+'/REVISIONES_EXACTAS','exclude_patterns':['*.docx']},
      {'source':base+'/escalamiento/ANALISIS_B_CERRADO_R2','target':target+'/ESCALAMIENTO','exclude_patterns':['*.docx']},
      {'source':base+'/escalamiento/ANALISIS_AUTOPSIA_R15','target':target+'/AUTOPSIA_R15','exclude_patterns':['*.docx']},
      {'source':base+'/escalamiento/ANALISIS_PROTECCION_FASE_R16','target':target+'/PROTECCION_FASE_R16','exclude_patterns':['*.docx']}]
    for name in('MECANISMO','SERVICIO','AUXILIAR','ADAPTACION','PREFLIGHT_R3','SERVICIO_FASE_R3'):
        additions.append({'source':base+'/cierre/'+name,'target':target+'/'+name,'exclude_patterns':['*.docx']})
    for row in additions:
        if not(ROOT/row['source']).is_dir():raise ValueError('Closed scientific contribution absent: '+row['source'])
        packages[:]=[old for old in packages if old.get('target')!=row['target']];packages.append(row)
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'selection':str(a.salida),'sha256':sha(a.salida),'selected_principal':a.principal,'total_lives':len(selected['lives']),'scientific_packages_added':len(additions),'originals_modified':False,'distribution_config_only':True}))

if __name__=='__main__':main()
