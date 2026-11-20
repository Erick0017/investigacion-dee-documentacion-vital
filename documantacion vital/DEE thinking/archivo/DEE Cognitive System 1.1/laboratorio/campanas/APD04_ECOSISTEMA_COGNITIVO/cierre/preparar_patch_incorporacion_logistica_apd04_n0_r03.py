"""Produce un patch documental/logístico; nunca aplica nada a la fuente S."""
import argparse
import copy
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return (json.dumps(x,ensure_ascii=False,sort_keys=False,indent=2)+'\n').encode('utf8')
def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(canonical(x))
def insert_entry(text,key,row):
    marker='"'+key+'": [';start=text.index(marker)+len(marker)
    nl='\r\n' if '\r\n' in text else '\n'
    assert text[start:start+len(nl)]==nl
    encoded=nl.join('    '+line for line in json.dumps(row,ensure_ascii=False,indent=2).splitlines())
    return text[:start]+nl+encoded+','+text[start:]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();r=a.root.resolve();out=a.out.resolve();assert not out.exists()
    assert out.is_relative_to(r/'laboratorio')
    proposal=r/'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/cierre/operacion_final/APD04_TALLER_SITUADO.json'
    contract=json.loads(proposal.read_bytes());cut=contract['current_local_operational_cut'];parent=contract['parent']
    assert cut['life']=='APD04_SEMILLA_COLABORADOR_R01' and cut['tick']==654959
    assert cut['snapshot_sha256']=='52a35b4062bc843a74a115679ba7c6f76c9db1eab145926ac9d01d22390723fc'
    assert cut['paired_manifest_sha256']=='0658ca4404f1d676cb9d496f2c1d4f5fbdfee98188a5c717db68e760088f9b2c'
    names=['sistema/capacidades/CATALOGO_CAPACIDADES.json','sistema/documentacion/ESTADO_ACTUAL_DE_VIDAS.json',
           'sistema/documentacion/RAMAS_Y_GENEALOGIA.json','LEER_PRIMERO.md']
    originals={n:(r/n).read_bytes() for n in names};before={n:sha(b) for n,b in originals.items()}
    assert all('APD04_TALLER_SITUADO' not in b.decode('utf8') for n,b in originals.items() if n.endswith('.json'))
    entry={'id':contract['id'],'version':contract['version'],'origin':'APD04 continuous MAIN prefix plus explicitly selected complete R03REAL post10 clone; not T0 or fused auxiliary memories',
        'implementation':', '.join(contract['implementation']),'contract':'contratos/APD04_TALLER_SITUADO.json',
        'availability':contract['availability'],'integration':contract['integration'],
        'knowledge':'Two finite form associations taught in MAIN: clasifica+ and equilibra-. Selected seed is exact whole-state post10 clone; its current panel must be taken from the final measured record, not historical maxima.',
        'limits':'Prepared body, sensor, codecs, readers, source calendar and external cache. R03 historical localWAIT is P1, not an available-current-seed policy promise. No generalR2/freeSpanish/NSM upgrades or20simultaneous sources.',
        'execution_command':'INICIAR.bat usar --nueva MI_APD04; later INICIAR.bat usar --vida MI_APD04',
        'life_id':cut['life'],'tick':cut['tick'],'N':67,'snapshot_sha256':cut['snapshot_sha256'],'paired_manifest_sha256':cut['paired_manifest_sha256'],
        'current_access_panel':'PENDING_ROOT_FINAL_PANEL_RECORD_NOT_INFERRED',
        'full_exact_zip_proof':'PENDING_ROOT_EXACT_ARCHIVE_VERIFICATION',
        'protected_default_unchanged':True,'not_a_response_lookup_table':True,'publication_status':'BOUNDED_EXPERIMENTAL_ALTERNATIVE_NO_GLOBAL_PROMOTION'}
    selected={'life_id':cut['life'],'profile':'fisica_directa','branch':'EXPLICIT_COMPLETE_PAIRED_FORK','N':67,'tick':cut['tick'],
        'snapshot':cut['snapshot'],'snapshot_sha256':cut['snapshot_sha256'],'paired_service_manifest_sha256':cut['paired_manifest_sha256'],
        'paired_service_required':True,'paired_export':cut['paired_export'],
        'parent':{'life_id':parent['life'],'tick':parent['tick'],'snapshot_sha256':parent['snapshot_sha256'],'paired_manifest_sha256':parent['paired_manifest_sha256']},
        'owner_stopped':True,'native_pending':0,'global_default':False,'knowledge_is_not_the_whole_library':True,
        'selection':'Prospective before final diagnostics, late views and early reserve. Exact post10 clone; no favourable historic WAIT/maxima merged.',
        'historical_acquisitions':{'source_life':'APD04_MAIN','source_tick':639374,'additional_finite_forms':['clasifica','equilibra'],'NSM_upgrades':[]},
        'current_access_panel':'PENDING_ROOT_FINAL_PANEL_RECORD_NOT_INFERRED','full_exact_zip_proof':'PENDING_ROOT',
        'limits':['Material queries can destroy or change access.','Environmental cache is not Native numeric memory.','No current WAITpolicy or general attention claim.'],
        'continuity':'CONTINUIDAD_APD04_ECOSISTEMA_COGNITIVO.json','continuity_pointer_status':'Root final closed record must be linked before release.'}
    genealogy={'life_id':cut['life'],'parent_life_id':parent['life'],'parent_tick':parent['tick'],'parent_snapshot_sha256':parent['snapshot_sha256'],
        'parent_import':'Complete postSTOP paired state/SQLite/interfaces/queues/artifacts, not T0 or selected regions',
        'tick':cut['tick'],'snapshot_sha256':cut['snapshot_sha256'],'paired_service_manifest_sha256':cut['paired_manifest_sha256'],
        'adverse_future_preserved':True,'auxiliary_memories_merged':False,'global_promotion':False,
        'continuity':selected['continuity'],'scope':'Selected complete operational seed only. The later early-reserve branch has its own unfinished record; no final tick invented.'}
    proposed={}
    key=names[0];proposed[key]=insert_entry(originals[key].decode('utf8'),'entries',entry).encode('utf8')
    key=names[1];old=json.loads(originals[key]);txt=originals[key].decode('utf8')
    prev=old.get('preferred_research_life');needle='"preferred_research_life": '+json.dumps(prev)
    replacement='"preferred_research_life": '+json.dumps(cut['life'])+',\n  "previous_preferred_research_life_pre_APD04": '+json.dumps(prev)
    assert txt.count(needle)==1;txt=txt.replace(needle,replacement,1)
    proposed[key]=insert_entry(txt,'lives',selected).encode('utf8')
    key=names[2];txt=originals[key].decode('utf8');needle='"latest_research_branch": '
    assert txt.count(needle)==1;txt=txt.replace(needle,'"historical_latest_research_branch_pre_APD04": ',1)
    nl='\r\n' if '\r\n' in txt else '\n';head='  "latest_research_branch": '+json.dumps(genealogy,ensure_ascii=False,indent=2).replace('\n','\n  ')+','+nl
    txt=txt.replace('  "selected": [',head+'  "selected": [',1)
    proposed[key]=insert_entry(txt,'selected',selected).encode('utf8')
    overlay={'schema':'DCS1.1.NSM65.affected_overlay.v1','campaign':'APD04_ECOSISTEMA_COGNITIVO','original_catalog_unchanged':True,
        'automatic_semantic_level_promotions':0,'nsm_upgrades':[],'affected':[],
        'additional_spanish_forms':[{'form':w,'origin':'Explicit teaching in APD04_MAIN T639374','scope':'Finite acquired signal association, not NSM primitive or free-language concept','currently_selected_life':cut['life'],'current_access':'Final measured panel required; historic maximum not imputed'} for w in ('clasifica','equilibra')],
        'selected_complete_state':{'life':cut['life'],'tick':cut['tick'],'snapshot_sha256':cut['snapshot_sha256']},
        'scope':'2/5/10/20 external source counts are sequential P0 opportunities, not20simultaneous full channels,20Native learned concepts or a universal memory bound.',
        'unchanged_pending':'All65 entries and prior levels/pending research remain unchanged. No newYO/TU, generalNO, equality/HOLD, language orR2 claimed.'}
    proposed['sistema/capacidades/NSM65_ACTUALIZACIONES_APD04.json']=canonical(overlay)
    manual='DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_18_APD04_ECOSISTEMA_SIN_VALIDACION_VISUAL.docx'
    readme=originals['LEER_PRIMERO.md'].decode('utf8');paragraph_sep='\r\n\r\n' if '\r\n' in readme else '\n\n';oldpara=readme.split(paragraph_sep)[2]
    newpara=oldpara.replace('MI_COPIA','MI_APD04').replace('APD03_MAIN T604825','APD04_SEMILLA_COLABORADOR_R01 T654959')
    readme=readme.replace(oldpara,newpara,1).replace('## Corte vigente APD03 — autonomía práctica y desarrollo acotado','## Corte histórico APD03 — autonomía práctica y desarrollo acotado',1)
    marker='## Corte histórico APD03 — autonomía práctica y desarrollo acotado'
    intro='## Corte APD04 — taller situado y aprendizaje finito\n\nLa entrada común selecciona una copia completa de `APD04_SEMILLA_COLABORADOR_R01`, N67,T654959, del REAL R03post10. No modifica ACTIVO ni combina memorias. `clasifica` y `equilibra` son dos asociaciones adicionales enseñadas en el prefijo MAIN, no dos nuevas primitivas NSM o18significados nuevos. El panel actual yla prueba Full se consultan en el cierre real; el WAIT histórico de una oportunidad no se promete como política accesible desde la semilla.\n\nConsulte [la guía APD04](sistema/documentacion/GUIA_USO_APD04.md), [el contrato](sistema/contratos/APD04_TALLER_SITUADO.json) y[la continuidad cerrada](CONTINUIDAD_APD04_ECOSISTEMA_COGNITIVO.json). El [Manual Maestro APD04, edición1.18]('+manual+') debe existir con su comprobación real antes de liberar esta actualización; este patch no crea ni certifica el Word. Los futuros adversos, originales yediciones anteriores permanecen preservados.\n\n'
    assert readme.count(marker)==1;proposed['LEER_PRIMERO.md']=readme.replace(marker,intro+marker,1).encode('utf8')
    # Every pre-existing row remains value-exact; the text insertion also retains its bytes.
    for name,listkey in [(names[0],'entries'),(names[1],'lives'),(names[2],'selected')]:
        assert json.loads(proposed[name])[listkey][1:]==json.loads(originals[name])[listkey]
    assert json.loads(proposed[names[1]])['preferred_life']==json.loads(originals[names[1]])['preferred_life']
    for n,b in proposed.items():
        if n.endswith('.json'):json.loads(b)
    out.mkdir(parents=True)
    for n,b in originals.items():p=out/'BASELINES'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    for n,b in proposed.items():p=out/'PROPUESTOS'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    patch=[]
    for n,b in proposed.items():
        old=originals.get(n,b'').decode('utf8').splitlines(keepends=True);new=b.decode('utf8').splitlines(keepends=True)
        patch.extend(difflib.unified_diff(old,new,fromfile='a/'+n if old else '/dev/null',tofile='b/'+n,n=3))
    patchbytes=''.join(patch).encode('utf8');(out/'INCORPORACION_LOGISTICA_APD04_R01.patch').write_bytes(patchbytes)
    stage=Path(tempfile.mkdtemp(prefix='apd04_patch_N0_'))/'prueba';shutil.copytree(out/'BASELINES',stage)
    (stage/'patch.diff').write_bytes(patchbytes)
    check=subprocess.run(['git','apply','--check','patch.diff'],cwd=stage,capture_output=True,text=True)
    apply=None
    if check.returncode==0:
        apply=subprocess.run(['git','apply','patch.diff'],cwd=stage,capture_output=True,text=True)
    tested=apply is not None and apply.returncode==0 and all((stage/n).read_bytes()==b for n,b in proposed.items())
    unchanged=all((r/n).read_bytes()==b for n,b in originals.items());assert unchanged
    dump(out/'MANIFIESTO_Y_GUARDAS.json',{'schema':'APD04.logistics_patch.N0.R01','status':'NOT_APPLIED_TO_SOURCE',
        'root_sources_before_sha256':before,'source_still_unchanged':unchanged,'proposal_contract_sha256':sha(proposal.read_bytes()),
        'proposed_members':[{'file':n,'before_sha256':before.get(n),'after_sha256':sha(b),'bytes':len(b)} for n,b in proposed.items()],
        'patch_sha256':sha(patchbytes),'git_check':{'returncode':check.returncode,'stdout':check.stdout,'stderr':check.stderr},
        'test_copy_directory':str(stage),
        'prior_tool_failures_preserved':['R01:CRLFparagraphIndexError before output, no Native or S edits.','R02:WinError267 while launching git from long staging CWD; proposed bytes preserved, no Native or S edits.'],
        'applied_only_to_disposable_copy':None if apply is None else {'returncode':apply.returncode,'stdout':apply.stdout,'stderr':apply.stderr,'byte_exact_all_targets':tested},
        'unchanged_all_preexisting_entries':True,'protected_default_changed':False,'nsm_upgrades':[],
        'Root_before_release':['Fill final measured seed panel/Full proof in contract and index; do not inherit historical maxima.',
            'Install Root approved contract/guide separately. This patch does not copy them over frozen S.',
            'Require exact current source hashes or regenerate a new patch from revised documentary baselines.',
            'Require existing Word1.18 target and closed continuity JSON before releasing README.',
            'Only Root applies after all Native owners STOP; do not apply while source freeze is active.'],
        'new_Native_ticks':0,'Word_changed':False,'Full_changed':False,'ZIP_created':False})
    print(json.dumps({'source_unchanged':unchanged,'patch_tested_on_copy':tested,'members':len(proposed),'new_Native_ticks':0}))


if __name__=='__main__':main()
