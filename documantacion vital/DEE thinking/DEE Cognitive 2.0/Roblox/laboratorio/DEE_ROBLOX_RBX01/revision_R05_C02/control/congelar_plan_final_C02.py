"""Root-authorized final explicit analysis plan; never builds ZIP or runs engines."""
from pathlib import Path
import datetime, hashlib, importlib.util, json, sys

ROOT=Path(__file__).resolve().parents[1]
VIDEO_SHA='bf96c566a2293dd3caf449463a5cac3ce89b58f417b93eda001fc14de7d91c66'
VIDEO_BYTES=14938957

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write_new(path,value):
    with path.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def run():
    dest=ROOT/'control/finalexport.json'
    if dest.exists():raise ValueError('Preserve existing final plan; Root must choose a new explicit revision')
    source=ROOT/'control/finalexport_PLANTILLA_C02_POST_CURACION_R02.json'
    plan=read(source);rows=plan['files'];seen={x['source']for x in rows}
    video=ROOT/'video/DEE_RBX01_C02_COMPARATIVA_1080p.mp4'
    if video.stat().st_size!=VIDEO_BYTES or sha(video)!=VIDEO_SHA:raise ValueError('Final separate video differs')
    omissions_path=ROOT/'control/OMISIONES_LOCALIZADAS_C02.json'
    omissions=read(omissions_path)
    if any(x.get('category')=='Final video delivered separately'for x in omissions['exclusions']):raise ValueError('Separate video already registered; no duplicate source')
    omissions['exclusions'].append(dict(category='Final video delivered separately',path=str(video),
        bytes=VIDEO_BYTES,sha256=VIDEO_SHA,reason='One complete MP4 is delivered separately, not duplicated inside the bounded analysis ZIP.',
        technical='Native1920x1080,30fps CFR,SAR1:1,9240frames,308seconds; see selected actual container/visual QA records.',
        next_material='The separate original MP4 matched by the stated bytes/SHA; JSON derived rendering sources are selected in the analysis ZIP.'))
    omissions['video_added_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    omissions_path.write_text(json.dumps(omissions,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    spec=importlib.util.spec_from_file_location('_C02_final_pack_rules',ROOT/'control/empacar_evidencia_C02_R02.py')
    pack=importlib.util.module_from_spec(spec);sys.modules[spec.name]=pack;spec.loader.exec_module(pack)
    def add(name,role,why):
        if name in seen:return
        path=ROOT/name
        if not path.is_file():raise ValueError('Required final source absent: '+name)
        pack.source_allowed(path,role);pack.validate_text(name,path.read_bytes())
        rows.append(dict(source=name,archive=name,sha256=sha(path),role=role,selection_reason=why));seen.add(name)
    for name in ('finalizar_video_C02.py','renderizar_comparativa_C02.py','materializar_manifiesto_C02.py',
                 'transformar_exports_video_C02_R02.py','verificar_contenedor_C02.py','extraer_QA_MP4_C02.py'):
        add('video/'+name,'code','Exact final derived renderer/materializer/container QA source; no new Native/Roblox/model execution')
    for name in ('SELECCION_PROSPECTIVA_C02_R04.json','TEXTOS_REVISADOS_C02.json','MANIFIESTO_FINAL_C02_R04.json',
                 'INDICE_VIDEO.csv','DEE_RBX01_C02_COMPARATIVA_1080p.verificacion.json',
                 'QA/REVISION_VISUAL_ENTREGABLE_C02.json','QA/VERIFICACION_CONTENEDOR_C02.json',
                 'QA/FFMPEG_METADATOS_REALES_C02.txt','QA/MP4_ENTREGABLE_R15/INDICE_QA_MP4.json',
                 'QA/MP4_ENTREGABLE_R15/DECISIVOS_REALES.json'):
        add('video/'+name,'verification','Actual final video selection, words, index, bytes/hash and complete-container/visual QA; sampled images remain local')
    indices=[]
    for folder in ('MAIN_R02_FINAL','PROGRAMMED_FINAL','CONVENTIONAL_AI_FINAL','DEV_FORMAT_WITNESS_2SEG'):
        base='video/datos/'+folder
        for name in ('SOURCE_INDEX_C02.json','poses.jsonl','events.jsonl','geometry.json'):
            add(base+'/'+name,'map','Derived display data from captured whole Worlds; not a new capture, trajectory, Native decision or experimental replicate')
        indices.append((base,read(ROOT/base/'SOURCE_INDEX_C02.json')))
    # Refresh ALL sources after Root declares report/readme/continuity stable.
    aliases=plan.get('content_aliases_not_duplicated',[]);unique=[];byhash={}
    for row in rows:
        path=ROOT/row['source'];pack.source_allowed(path,row['role']);pack.validate_text(row['archive'],path.read_bytes())
        row['sha256']=sha(path)
        if row['sha256']in byhash:
            aliases.append(dict(omitted_source=row['source'],same_bytes_as=byhash[row['sha256']]['source'],sha256=row['sha256'],reason='Exact content alias; one full content copy selected, never counted as another event.'))
        else:byhash[row['sha256']]=row;unique.append(row)
    rows[:]=unique
    localizers=[]
    for base,index in indices:
        checkpoints=[];command=['python','-I','-B','video/transformar_exports_video_C02_R02.py','--root','.']
        for item in index['source_checkpoints']:
            selected=byhash.get(item['sha256'])
            if not selected:raise ValueError('Derived video lacks packaged original checkpoint: '+item['path'])
            checkpoints.append(dict(original_absolute_provenance=item['path'],relative_provenance=item.get('relative_path'),
                archive=selected['archive'],bytes=item['bytes'],sha256=item['sha256']))
            command+=['--checkpoint',selected['archive']]
        command+=['--output-directory',base+'_REGENERADO','--role',index['role'],'--run-id',index['run_id'],
            '--purpose',index['purpose'],'--expected-world-id',index['world_id'],'--expected-scenario-sha256',index['scenario_sha256'],
            '--expected-opportunities',str(index['prospective_opportunities'])]
        localizers.append(dict(derived_directory=base,source_index_sha256=sha(ROOT/base/'SOURCE_INDEX_C02.json'),
            original_checkpoints=checkpoints,passive_regeneration_command=' '.join(command)))
    localizer_path=ROOT/'control/LOCALIZADORES_VIDEO_C02.json'
    write_new(localizer_path,dict(schema='DEE.RBX01.C02.video_provenance_localizers.R01',
        explanation='Absolute paths inside original source indices are historical provenance, not promised portable locations. Use archive members matched by SHA. If root moves, regenerate Derived using the converter and new relative checkpoint paths; never open or advance DEE.',
        rendering_scope='Derived reconstruction from frozen poses/events/geometry; no actual new Studio capture, Native or model execution. Existing final render remains identified by its independent hash.',
        rows=localizers,separate_video=dict(path=str(video),bytes=VIDEO_BYTES,sha256=VIDEO_SHA),
        Native_ticks=0,MCP_calls=0,model_calls=0))
    add('control/LOCALIZADORES_VIDEO_C02.json','map','Historical absolute video provenance remapped to exact packaged checkpoint members; passive converter commands for a moved root')
    add('control/congelar_plan_final_C02.py','code','Exact Root-authorized explicit final plan generation; no automatic ZIP build')
    plan.update(finalized=True,frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=rows,
        prior_template=dict(path=str(source),sha256=sha(source)),content_aliases_not_duplicated=aliases,
        separate_video=dict(path=str(video),bytes=VIDEO_BYTES,sha256=VIDEO_SHA,included_in_zip=False),
        projected_content_files=len(rows),projected_uncompressed_bytes=sum((ROOT/x['source']).stat().st_size for x in rows),
        pending_before_finalization=[],missing_at_template_cut=[],
        finalization_scope='Root declared final scientific report/readme/continuity and real final video metadata stable. All selected content hashes refreshed; no ZIP build performed.',
        actual_source_rows=13,full_Manual_reading_claimed=False)
    write_new(dest,plan)
    return dict(plan=str(dest),sha256=sha(dest),files=len(rows),uncompressed_bytes=plan['projected_uncompressed_bytes'],finalized=True,missing=0,zip_built=False)

if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
