"""Prepare ONLY isolated PI08 B code/context; optional Root import command.

Default is a read-only plan. --preparar copies a bounded existing capsule list
plus the actual adopted A deltas, adds mode-only B hooks in the COPIES and four
empty diagnostic systems. Never changes Cognitive, source states or selectors.
This script never imports DEE or starts a Native child. Root receives exact
contexts for the existing bounded import supervisor, separately from owners.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, ast, hashlib, json, os, shutil

P = Path(__file__).resolve().parents[1]
H = P/'codigo'
C = P.parents[2]/'DEE Cognitive 2.0'
S = C/'sistema'
RP = C/'reproducibilidad'
BASE = RP/'codigo_preservado/PI07_R03_LOCAL_FI_PRE34_R03/SISTEMA_CODIGO.json'
STAGE = H/'FUENTES_B_PI08_R01_PREPARADAS'
OUT = P/'control/SISTEMAS_B_PI08_R01_PREPARADOS.json'


def read(path): return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def require(ok, message):
    if not ok: raise ValueError(message)
def once(text, before, after):
    require(text.count(before) == 1, 'Actual source hook anchor changed: '+before[:100])
    return text.replace(before, after)
def safe_relative(value):
    rel = PurePosixPath(value)
    require(not rel.is_absolute() and ':' not in value and '\\' not in value and all(v not in ('.', '..') for v in rel.parts), 'Unsafe source member')
    require(not value.startswith(('estado/', 'runtime/')) and not value.endswith('.sqlite3'), 'Code capsule cannot insert world state')
    return rel
def regular(path):
    for node in (path, *path.parents):
        if node.exists(): require(not node.is_symlink() and not(getattr(node.lstat(), 'st_file_attributes', 0)&1024), 'No reparse path')
    return path
def put(path, value):
    regular(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8') as out: json.dump(value, out, ensure_ascii=False, indent=2); out.write('\n')


def main(args):
    sealfile = H/'SELLO_PI08_B_R01.json'; seal = read(sealfile)
    require(seal['A_adopted'] and seal['protocol_sha256'] == sha(H/'PROTOCOLO_PI08_B_R01.json'), 'Actual post-A prospective B seal required')
    adoption = read(P/'control/ADOPCION_PRODUCTO_PI08.json')
    require(adoption['phase'] == 'COMMITTED' and sha(P/'control/ADOPCION_PRODUCTO_PI08.json') == seal['A_adoption_proof_sha256'], 'Protected A adoption changed')
    delta = read(P/'control/DELTA_OPERATIVO_PRODUCTO_PROPUESTO_PI08_R02.json')
    names = {row['file'] for row in read(BASE)['files']} | {row['file'] for row in delta['proposed_code_files']} | {'gestionar.py'}
    sources = []
    for relative in sorted(names):
        rel = safe_relative(relative); source = regular(S.joinpath(*rel.parts))
        require(source.is_file(), 'Actual adopted code dependency missing: '+relative)
        sources.append({'file': relative, 'source': str(source), 'bytes': source.stat().st_size, 'source_sha256': sha(source)})
    newnames = ['pi08_revision_flexible_B_R01.py', 'pi08_revision_flexible_B_episodio_R01.py', 'PROTOCOLO_PI08_B_R01.json', 'SELLO_PI08_B_R01.json']
    for name in newnames:
        source = regular(H/name)
        require(source.is_file(), 'New B source unavailable: '+name)
        sources.append({'file': 'capacidades/'+name, 'source': str(source), 'bytes': source.stat().st_size, 'source_sha256': sha(source)})
    roles = ('real', 'none', 'yoked', 'reference')
    destinations = {role: P/'estados'/('B_'+role.upper()+'_R01') for role in roles}
    if not args.preparar:
        print(json.dumps({'mode': 'READ_ONLY_NO_NATIVE', 'source_code_files': len(sources), 'stage': str(STAGE),
            'destinations': {k: str(v) for k,v in destinations.items()}, 'Native_executed': False,
            'note': 'Code/context only. Importing four complete worlds is a separate explicit Root phase.'}, ensure_ascii=False, indent=2))
        return
    require(not STAGE.exists() and not OUT.exists(), 'Preserve existing prepared B source')
    require(not any(path.exists() for path in destinations.values()), 'Unused explicit diagnostic destinations only')
    require(not (RP/'EJECUCION_MATERIAL.lock').exists() and not (P/'PI08_ROOT_NATIVE_WRITER.lock').exists(), 'A Root material writer remains active')
    source_before = {row['source']: row['source_sha256'] for row in sources}
    STAGE.mkdir()
    for row in sources:
        target = STAGE.joinpath(*PurePosixPath(row['file']).parts); target.parent.mkdir(parents=True, exist_ok=True)
        with Path(row['source']).open('rb') as src, target.open('xb') as dst: shutil.copyfileobj(src, dst)
        require(sha(target) == row['source_sha256'], 'Copied source differs')
    worldfile = STAGE/'app/mundo_genesis_apd05.py'; world = worldfile.read_text('utf-8-sig')
    world = once(world, '        pi08.operational_dependencies(self.a,self.work_directory)\n',
                 "        pi08.operational_dependencies(self.a,self.work_directory)\n        from capacidades import pi08_revision_flexible_B_R01 as pi08b\n        pi08b.operational_dependencies(self.a,self.work_directory)\n        for path in pi08b.code_files():\n            self.code_sha256['PI08B/'+path.name]=hashlib.sha256(path.read_bytes()).hexdigest()\n")
    anchor = "        if row is not None and str(row.get('modo','')).startswith('eci01-pi08-c2c-'):"
    require(world.count(anchor) == 2, 'Actual two A1 mode routers required')
    index = world.index(anchor)
    world = world[:index]+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi08-b-'):\n            from capacidades import pi08_revision_flexible_B_R01 as pi08b\n            pi08b.validate(self.a,row)\n            return\n"+world[index:]
    index = world.index(anchor, world.index('    def execute(self,payload):'))
    world = world[:index]+"        if row is not None and str(row.get('modo','')).startswith('eci01-pi08-b-'):\n            from capacidades import pi08_revision_flexible_B_R01 as pi08b\n            pi08b.validate(self.a,row)\n            self.before_mutation('PI08_B_RESEARCH_NATIVE_SELECTION_OR_EXPLICIT_CONTROL')\n            value=pi08b.dispatch(self.a,row,actuator=payload.get('actuador','closed'),directory=self.work_directory)\n            return {'version':pi08b.VERSION,'rows':[value]}\n"+world[index:]
    world = once(world, "        result['PI08_integration']=pi08.operational_dependencies(self.a,self.work_directory)\n",
                 "        result['PI08_integration']=pi08.operational_dependencies(self.a,self.work_directory)\n        from capacidades import pi08_revision_flexible_B_R01 as pi08b\n        result['PI08_B']=pi08b.operational_dependencies(self.a,self.work_directory)\n")
    world = once(world, '    def external_uncertainty(self):\n',
                 '    def external_uncertainty(self):\n        from capacidades import pi08_revision_flexible_B_R01 as pi08b\n        if pi08b.uncertain(self.a):return True\n')
    ast.parse(world); worldfile.write_text(world, encoding='utf8', newline='\n')
    queuefile = STAGE/'app/cola_local.py'; queue = queuefile.read_text('utf-8-sig')
    anchor = "            if str(row.get('modo','')).startswith('eci01-pi08-c2c-'):"
    queue = once(queue, anchor, "            if str(row.get('modo','')).startswith('eci01-pi08-b-'):\n                from capacidades.pi08_revision_flexible_B_R01 import validate_literal\n                validate_literal(row)\n                continue\n"+anchor)
    ast.parse(queue); queuefile.write_text(queue, encoding='utf8', newline='\n')
    rows = []
    for row in sources:
        target = STAGE/row['file']
        if target.suffix == '.py': ast.parse(target.read_text('utf-8-sig'))
        rows.append({**row, 'bytes': target.stat().st_size, 'sha256': sha(target),
                     'B_mode_hook_only': row['file'] in ('app/cola_local.py', 'app/mundo_genesis_apd05.py')})
    manifest = {'schema': 'DEE.PI08.B.isolated_code_capsule.R01', 'source_actual_adopted_product': str(S),
                'protocol_sha256': seal['protocol_sha256'], 'seal_sha256': sha(sealfile), 'files': rows,
                'source_state_never_copied': True, 'original_R03_unchanged': True, 'Native_executed': False}
    put(STAGE/'SISTEMA_CODIGO.json', manifest)
    contexts = {}
    wheel = 'dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
    for role, destination in destinations.items():
        system = destination/'sistema'; system.mkdir(parents=True)
        for row in rows:
            target = system/row['file']; target.parent.mkdir(parents=True, exist_ok=True)
            with (STAGE/row['file']).open('rb') as src, target.open('xb') as dst: shutil.copyfileobj(src, dst)
            require(sha(target) == row['sha256'], 'Isolated system source differs')
        (system/'estado/checkpoints').mkdir(parents=True)
        (system/'runtime').mkdir()
        os.link(S/'runtime'/wheel, system/'runtime'/wheel)
        life = seal['research_life_ids'][role]
        context = {'schema': 'DEE.PI08.B.explicit_complete_pair_import.v1', 'life': life, 'system': str(system),
                   'prefix': seal['source_prefix']['path'], 'prefix_manifest_sha256': seal['source_prefix']['manifest_sha256'],
                   'source_code_manifest_sha256': sha(STAGE/'SISTEMA_CODIGO.json'), 'role_auditor_only': role,
                   'tool_sources': [{'file': name, 'sha256': sha(RP/name)} for name in ('importar_diagnostico.py', 'observador_pasivo.py')],
                   'never_select_or_promote': True, 'Native_executed_by_preparation': False}
        contextfile = destination/'CONTEXTO_EJECUCION.json'; put(contextfile, context)
        contexts[role] = {'directory': str(destination), 'system': str(system), 'life': life,
                          'context': str(contextfile), 'context_sha256': sha(contextfile)}
    require(all(sha(Path(path)) == digest for path, digest in source_before.items()), 'Actual source changed during isolated preparation')
    put(OUT, {'schema': 'DEE.PI08.B.isolated_systems.prepared.v1', 'recorded_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'PREPARED_CODE_ONLY_NO_WORLD_IMPORTED', 'source_manifest': str(STAGE/'SISTEMA_CODIGO.json'),
              'source_manifest_sha256': sha(STAGE/'SISTEMA_CODIGO.json'), 'code_files': len(rows), 'contexts': contexts,
              'Native_executed': False, 'principal_or_source_state_changed': False,
              'next': 'Root explicitly invokes existing import_pair importer under512MiB job for each context, then runner B. No automatic import or owner here.'})
    print(json.dumps({'proof': str(OUT), 'sha256': sha(OUT), 'code_files': len(rows), 'contexts': contexts, 'Native_executed': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--preparar', action='store_true')
    main(parser.parse_args())
