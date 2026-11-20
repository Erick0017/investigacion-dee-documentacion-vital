"""Index only explicitly selected closed APD02 stages and current CAS helper bytes."""
import argparse,hashlib,json
from pathlib import Path
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve preparation index revisions')
    config=json.loads(a.config.read_bytes());root=Path(config['source_root']);here=Path(__file__).parent;stages=[]
    for row in config['stages']:
        stage=root/row['source'];manifest=stage/row.get('manifest','MANIFIESTO.json');plan=stage/row.get('plan','PLAN_RECALCULO.json')
        if sha(manifest)!=row['manifest_sha256']:raise ValueError('Closed manifest changed')
        m=json.loads(manifest.read_bytes());members=m.get('files',m.get('members'));indexes=[]
        for item in members:
            name=item.get('file',item.get('path'));base=Path(name).name.upper()
            if any(word in base for word in('OMISION','INDICE','SNAPSHOT','FUENTES')):
                indexes.append({'logical_member_in_namespace':name,'bytes':item['bytes'],'sha256':item['sha256']})
        stages.append({'namespace':row['namespace'],'source_relative_to_research_root':row['source'],'local_locator':str(stage),'manifest_sha256':sha(manifest),'plan_sha256':sha(plan),'omission_or_source_index_members_already_archived':indexes})
    previous=root/'laboratorio/campanas/ASISTENTE_PROPOSITO_LENGUAJE_DELEGACION_01/cierre'
    reused=[{'source_relative_to_research_root':f.relative_to(root).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f),'unchanged_APD01_source':True}for f in(previous/'ensamblar_analisis_apd_cas_R03.py',previous/'repetir_todo_apd_cas.py',previous/'sellar_probar_zip_analisis_apd.py')]
    current=[{'file':f.name,'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(here.glob('*.py'))]
    result={'schema':'APD02.CAS.selected_source_and_omission_preparation.v1','status':'PREPARACION_NO_FINAL','native_ticks':0,'ZIP_generated':False,'config_file':a.config.name,'config_sha256':sha(a.config),'source_stages':stages,'reused_APD01_instrument_sources':reused,'new_APD02_helper_sources':current,'pending_components':config['pending_components'],'no_current_SQLite_or_live_Runtime_read':True,'not_in_analysis_by_design':[{'kind':'Native engine, WHL, binary dependencies and environment installation','reason':'Analysis package is not the operational collaborator Full ZIP; copied motor binaries are explicitly blocked'},{'kind':'Complete dense worlds and deep telemetry excluded by each closed stage','reason':'Retained at their private exact locators and hashes in the included stage-specific indices; no snapshots are reconstructed from incomplete arrays'},{'kind':'Superseded closed packaging or auditor-stage folders','reason':'Latest preferred closed stage preserves its actual physical primaries and source revisions; duplicate predecessor trees are not counted as new scientific cases. Local omission/source indices retain provenance.'},{'kind':'Future service, goal-main, Full proof, manual, report, continuity and operational delta','reason':'Still pending in this preparation; must be supplied and pinned by Root before final approval, not counted as tested here'}],'scope':'Every byte of the selected closed-stage logical members will be retained through CAS aliases, including positive, negative, instrumental-error and code-revision files. This proposal is neither campaign closure nor proof of a future ZIP. Final Root metadata/documents must be captured only after their true close; no placeholder may silently become a result.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps({'output':str(a.output),'sha256':sha(a.output),'closed_stages_indexed':len(stages),'pending_components':len(config['pending_components']),'native_ticks':0}));return 0
if __name__=='__main__':raise SystemExit(main())
