"""Documentary omission map from named existing metadata; no recursive scan/runtime."""
from pathlib import Path
import argparse, datetime, hashlib, json

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def anchor(path):
    path = Path(path)
    return dict(path=str(path), exists=path.is_file(), bytes=path.stat().st_size if path.is_file() else None,
                sha256=sha(path) if path.is_file() else None,
                hash_scope='Current bytes of this named small metadata file only; not a directory hash.')

def run(output):
    output = output if output.is_absolute() else ROOT / output
    if output.exists() or not output.resolve().is_relative_to(ROOT):
        raise ValueError('Fresh C02 output only')
    mapping_path = ROOT / 'evidencia/MAPA_ESTADO_FINAL_NATIVE_C02_R01.json'
    mapping = read(mapping_path)
    native = mapping['Native_root_manifest']
    model_path = ROOT / 'comparadores/MODELO_LOCAL_PREPARADO_C02.json'
    model = read(model_path)
    critical_path = ROOT / 'control/CRITICOS_DESPUES_CIENCIA_C02.json'
    critical = read(critical_path)
    coverage_path = ROOT / 'fuentes/LOCALIZADORES_REPERTORIO_BASE.json'
    coverage = read(coverage_path)
    rows = []
    rows.append(dict(category='Complete final experimental Native root',
        path=mapping['Native_root_locator'], bytes=sum(x['bytes'] for x in native['files']),
        files=len(native['files']), sha256=None, manifest=anchor(mapping_path),
        component_hashes_locator='Native_root_manifest.files[*].sha256',
        byte_count_basis='Existing complete file map, not a second scan; excludes unlisted later changes.',
        reason='Full coherent Native state remains local; selected primaries and its whole hash map travel. The ZIP is not an executable backup.',
        next_material='Use the full root together with final World, closed bridge and shared-runtime anchors under the published continuation contract; never RAW/clocks alone.'))
    model_files=[]
    for item in model['files']:
        path=Path(model['target'])/item['relative_path']
        model_files.append(dict(path=str(path), bytes=item['bytes'], sha256=item['sha256'],
            hash_basis='Reported source/copy equality in MODELO_LOCAL_PREPARADO_C02.json at its recorded cut; large blob not reread now.',
            exists_now=path.is_file(), current_size_matches_metadata=path.is_file() and path.stat().st_size==item['bytes']))
    manifest_path=Path(model['target'])/'manifests/registry.ollama.ai/library/llama3.2/latest'
    model_files.append({**anchor(manifest_path), 'hash_basis':'Named small model manifest read now; no inference.'})
    rows.append(dict(category='Local conventional-model weights',path=model['target'],
        bytes=sum(x['bytes'] or 0 for x in model_files),files=len(model_files),sha256=None,
        metadata=anchor(model_path),components=model_files,
        reason='About2GB of preexisting external comparator weights; metadata, own history and model lifecycle are selected, not its binary weights.',
        next_material='The exact local model manifest and its six content-addressed blobs for material comparator reproduction; passive calculations need none.'))
    for name in ('DEV_SELLADO_R02/PAREJA_C02/PAREJA_C02.json',
                 'MAIN_R02_SELLADO_R01/PAREJA_C02/PAREJA_C02.json',
                 'AI02_SELLADO_FRONTERA5_R02/PAIR_COMPARATOR_C02/PAIR_COMPARATOR_C02.json',
                 'AI02_SELLADO_FRONTERA6_R01/PAIR_COMPARATOR_C02/PAIR_COMPARATOR_C02.json',
                 'AI02_SELLADO_FRONTERA12_R01/PAIR_COMPARATOR_C02/PAIR_COMPARATOR_C02.json'):
        path=ROOT/'evidencia'/name
        if not path.is_file():
            rows.append(dict(category='Historical full paired checkpoint',path=str(path.parent),manifest=anchor(path),bytes=None,sha256=None,reason='Named pair manifest unavailable at this documentary cut; not invented.'))
            continue
        value=read(path);members=value.get('members',[])
        member_rows=list(members.values()) if isinstance(members,dict) else members
        rows.append(dict(category='Historical full paired checkpoint',path=str(path.parent),
            files=len(members),bytes=sum(x.get('bytes',0) for x in member_rows),sha256=None,
            manifest=anchor(path),component_hashes_locator='members[*]; recorded pair member set, not whole-directory inventory',
            native_tick=value.get('native_tick'), completed=value.get('completed_opportunities'),
            reason='Full Native copies and/or closed SQLite stay local. Small pair metadata, policy and World are selected where decisive; no incompatible futures merged.',
            next_material='Whole coherent pair with all declared members and shared dependencies for material restore; analysis ZIP alone cannot do it.'))
    for name in ('DEV','MAIN','MEMPAIR','MEMCTRL'):
        path=ROOT/'native'/name
        rows.append(dict(category='Other experimental Native life / control',path=str(path),exists=path.is_dir(),
            bytes=None,sha256=None,measurement='No new recursive count or directory hash; exact complete current size not measured for this omission map.',
            reason='Original experimental roots remain local. Selected whole functions/journals/negative controls travel; a prepared or absent arm is not called executed.',
            next_material='CONTEXTO_EJECUCION.json, complete state/queue/interfaces/artifacts and matching branch contract; do not reconstruct from a favorable output.'))
    rows.append(dict(category='Official runtime and protected operational documents',
        path=str(ROOT.parents[2]),bytes=None,sha256=None,
        named_preservation_control=anchor(critical_path),named_anchors=critical['files'],
        shared_runtime_anchors=mapping['shared_runtime_anchors'],
        reason='C02 is a bounded experimental comparison, not a distribution or a Manual update. Official motor/WHL/kernel, principal and Manual remain local and unchanged within the11 named-file check.',
        Manual_internal_edition=coverage.get('Manual_internal_edition'),
        Manual_content_reading=coverage.get('coverage_statement'),
        next_material='Exact shared runtime + original Manual when operational or full-document review is required; no claim of complete Manual reading in C02.'))
    for category,path,reason,next_material in (
        ('Deep SDK / per-call transport traces',ROOT/'evidencia','Repeated tool response chunks and SDK inventories do not become independent science. Decisive failures, literal Worlds and Root provenance are selected.','Named original period directory if transport forensics beyond the selected failure/capture record is needed.'),
        ('Regenerable checkpoint hex staging',ROOT/'evidencia/CONVENTIONAL_AI_R06_02_PERIODO_05','Hex/response chunks duplicate a verified complete JSON checkpoint; keep original locally, do not copy every transport chunk.','Use complete WORLD_CHECKPOINT.json and the exact captured transport/decoder scripts; request raw chunks only if rechecking transport.'),
        ('Synthetic tests and clean-copy staging',ROOT/'pruebas','Synthetic fixtures and extraction working copies are not additional Native experiments; final verification proofs may travel without every regenerated copy.','Source scripts and a new temporary destination recreate ordinary fixtures; no scientific originals removed.'),
        ('Packaging working copies / full videos',ROOT/'entrega','Packaging stages duplicate selected sources. Video binaries are delivered separately; final metadata/provenance will be added by Root.','Final standard ZIP or separate video with metadata; staging is not the only copy of a scientific state.'),
        ('Private transport configuration / closed bridge DBs',ROOT/'configuracion_privada','Credential-bearing configurations and SQLite remain local; no secrets copied. Selected closure and pair manifests preserve scientific identities.','A locally authorized secure configuration plus the coherent closed paired database; do not extract bearer values into this report.')):
        rows.append(dict(category=category,path=str(path),exists=path.exists(),bytes=None,sha256=None,
            measurement='Not recursively inventoried at closure; no folder hash asserted.',reason=reason,next_material=next_material))
    value=dict(schema='DEE.RBX01.C02.localized_omissions.R01',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        scope='Targeted omission map from named closed records; no census, new Native execution, model call, MCP, HTTP or SQLite connection.',
        source_coverage=dict(metadata=anchor(coverage_path),source_count=len(coverage.get('sources',[])),
            statement=coverage.get('coverage_statement'),claim=str(len(coverage.get('sources',[])))+' source rows have the coverage stated individually; this is not integral Manual/Compendium reading.'),
        exclusions=rows,folder_hash_policy='sha256:null for folders. File/member hashes and reported cut are identified explicitly; no aggregate hash invented.',
        Native_imports=0,Native_ticks=0,model_calls=0,MCP_calls=0,HTTP_calls=0,SQLite_connections=0,recursive_scans=0)
    with output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    return dict(path=str(output),bytes=output.stat().st_size,sha256=sha(output),groups=len(rows),source_count=value['source_coverage']['source_count'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    print(json.dumps(run(p.parse_args().output),ensure_ascii=False,indent=2))
