"""Select byte-exact historical sources; never invoke historical campaigns."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVES = ROOT.parents[1]
SOURCES = {
    'CPC3': ('CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip', '1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6'),
    'CPC4': ('CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip', '4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723'),
    'CPC5': ('CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip', 'd31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05'),
}


def sha_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    selections = []
    def choose(archive, prefix, names, destination):
        for name in names:
            selections.append((archive, prefix + name, destination + name))

    choose('CPC3', 'CPC3/genealogia/CP01_C08/src/', ['sesion.py', 'laboratorio.py', 'fronts.py'], 'CP01_C08/src/')
    choose('CPC3', 'CPC3/genealogia/CP02_B/src/', ['predictor.py', 'baseline.py', 'worker.py'], 'CP02_B/src/')
    choose('CPC3', 'CPC3/genealogia/CP02_B/', ['EXPERIMENT_CONFIG.json', 'INFORME.md', 'resultados/PAIRED_gate0.json', 'resultados/PAIRED_gate1.json', 'checkpoints/PAIRED_gate1_FINAL.deetsnap'], 'CP02_B/')
    choose('CPC3', 'CPC3/src/core/', ['entity.py', 'comparison.py', 'central_comparison.py', 'comparison_entity.py', 'revisable_selection.py', 'policy_session.py'], 'CPC3/core/')
    choose('CPC3', 'CPC3/experimentos/comparacion_seleccion/', ['run_central_comparison.py', 'central_discovery/open_changed/MEASUREMENTS.json', 'central_discovery/open_changed/FINAL.deetsnap'], 'CPC3/comparacion/')
    sem = 'CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/'
    choose('CPC3', sem + 'src/', ['common.py', 'memory.py', 'habitat.py', 'participant.py', 'experiment.py'], 'SEM01/src/')
    choose('CPC3', sem, ['configuraciones/casos/A_future_UV.json', 'configuraciones/EXPERIMENT_CONFIG.json', 'resultados/confirmacion/A_future_UV/MEASUREMENTS.json', 'resultados/confirmacion/A_future_UV/MAIN_FINAL.deetsnap'], 'SEM01/')
    choose('CPC4', 'CPC4/ampliaciones/02_APRENDIZAJE_CONTINUO_RED_ABCD/src/red/', ['common_helpers.py', 'recipe_v3.py', 'session_v3.py', 'regulated_session.py', 'regulated_habitat.py', 'regulated_experiment.py', 'regulated_curriculum.py'], 'CPC4_red/')
    choose('CPC5', 'CPC5/src/', ['common.py', 'compound.py', 'network.py', 'linguistic.py', 'relative_compound.py', 'references.py'], 'CPC5/src/')
    choose('CPC5', 'CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/src/', ['order_stream.py', 'semantic_relations.py', 'ordered_composition.py', 'dialogue.py', 'network_dialogue.py', 'network_session.py', 'capacity_longitudinal.py'], 'CPC5/ampliacion01/src/')
    identity = []
    manifests = []
    missing = []
    for label, (name, expected) in SOURCES.items():
        path = ARCHIVES / name
        actual = sha_file(path)
        if actual != expected:
            raise RuntimeError(f'Historical identity mismatch: {name}: {actual}')
        with zipfile.ZipFile(path) as z:
            identity.append({'source_id': label, 'archive': name, 'sha256': actual, 'size_bytes': path.stat().st_size, 'members': len(z.infolist()), 'original_not_modified': True})
            for archive, member, relative in selections:
                if archive != label:
                    continue
                if member not in z.namelist():
                    missing.append({'archive': name, 'member': member})
                    continue
                data = z.read(member)
                dest = ROOT / 'genealogia' / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists() and dest.read_bytes() != data:
                    raise RuntimeError(f'Refusing to replace differing selected source: {dest}')
                dest.write_bytes(data)
                info = z.getinfo(member)
                manifests.append({'file': dest.relative_to(ROOT).as_posix(), 'source_archive': name, 'source_archive_sha256': actual, 'source_member': member, 'size_bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'source_crc32': format(info.CRC, '08x'), 'operation': 'BYTE_EXACT_SELECTIVE_EXTRACTION'})
    manifest = {'schema': 'CPC6.selected_genealogy.v1', 'identities': identity, 'files': manifests, 'missing_requested_members': missing, 'original_archives_modified': False, 'historical_mains_executed': False}
    (ROOT / 'genealogia' / 'SOURCE_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    rows = [
        {'id': 'CP01_C01_C08', 'source': 'CP01_C08/src/fronts.py', 'mechanism': 'C01 first-event phase latch; C02 mobile collision calibration; C03 passive-plus-probe diagnosis; C04 native encounter; C05 mobile transfer; C06 action late cut; C07 external causal signature; C08 persistent mobile session', 'domain': 'N34 mobile; N47 relative; N127 transfer/distributed according to individual recipe. No combination assumed.', 'controls': 'history opposite, unpaired, path cut, no return/yoked/offpath, explicit diagnostic forks', 'published_limit': 'C08 external mod31 habitat; fixed signal loads; online physical history rather than arbitrary language', 'status': 'REFERENCE_SELECTED_NOT_ALL_REEXECUTED'},
        {'id': 'CP02_B', 'source': 'CP02_B/src/predictor.py', 'mechanism': 'Native relative memory from actual past outcomes; zero-load sensory events at32/33; live direction forecast', 'domain': 'N47 H0 atT32; targets60/100/150 known, finite phase and interface domain', 'controls': 'none, unpaired, memory equalized, route blocked, independent barrier change80', 'published_limit': 'External barrier law and persistence forecast; not arbitrary learned world model', 'status': 'REFERENCE_SELECTED_FOR_BRIEF_REPLAY'},
        {'id': 'CPC3_MAIN', 'source': 'CPC3/core/entity.py', 'mechanism': 'MAIN current physical output, finite phase input opportunities, pending forecast audit; continuation32->1032', 'domain': 'N47 relative T32; no operational forks, finite slots163/292/554/812/945', 'controls': 'H0, actual histories, fixed reader zero-probe, passive current observation', 'published_limit': 'Native history and current readout; external packet-world law', 'status': 'REFERENCE_SELECTED_FOR_INTEGRATION'},
        {'id': 'CPC3_CENTRAL_COMPARISON', 'source': 'CPC3/core/comparison_entity.py', 'mechanism': 'Physical expectation encounters independently encoded actual present outcome at target83, native marker84', 'domain': 'N47, one pending expectation; one comparison episode with one-tick readout', 'controls': 'opposite history, barrier changed, H0 actual, report omitted; independent actual encoder never receives forecast error', 'published_limit': 'Directional finite comparator; marker is not reusable fresh forecast', 'status': 'REFERENCE_SELECTED_FOR_BRIEF_REPLAY'},
        {'id': 'SEM01', 'source': 'SEM01/src/experiment.py', 'mechanism': 'Fixed opaque signal paired with physically sensed current supply; later signal alone emits learned direction and acts', 'domain': 'N67; S1/S2 acquired at17/45; queried84/112; final129', 'controls': 'opposite assignments, unpaired, signal-only, outcomes-only, explicit memory intervention, action cut', 'published_limit': 'Outcome sensor external and fixed; action geometry prepared; not two learners communicating', 'status': 'REFERENCE_SELECTED_FOR_BRIEF_REPLAY'},
        {'id': 'CPC4_ABCD_REGULATION', 'source': 'CPC4_red/regulated_session.py', 'mechanism': 'Same-Runtime participants, acquired relations, finite communication and programmed external counterflow realized byv27', 'domain': 'CPC4 red geometry and fixed windows; no arbitrary renewable port promise', 'controls': 'virgin/opposite/unpaired, selective relay cut, sham, actuator preserved', 'published_limit': 'Counterflow externally scheduled; W1 andW2 distinct interference; no experience-selected policy claimed', 'status': 'REFERENCE_SELECTED_NOT_REEXECUTED'},
        {'id': 'CPC5_COMPOUND', 'source': 'CPC5/src/compound.py', 'mechanism': 'Physically coupled acquired mobile stages, separately taught backups, context/relative bridge and learned directional regulation', 'domain': 'Four stages yield73; eight grouped4+4 yield165; limited timing domain', 'controls': 'stage omission, route cut, backup omission, same-dose opposite direction and cadence variation', 'published_limit': 'Grouping is circuit partition, not autonomous renewable bodies; responses do not count semantic depth', 'status': 'REFERENCE_SELECTED_NOT_REEXECUTED'},
        {'id': 'CPC5_AMPLIACION01', 'source': 'CPC5/ampliacion01/src/network_session.py', 'mechanism': '65 opaque associations over two direction classes; temporal stream/order representation; finite question->relay->answer->use network', 'domain': 'Published local worlds/horizons, 1..4 groups with growing resources; MAIN retention/cadence bounded', 'controls': 'none/unpaired/opposite, learned memory cut, ordered omission, request/reply cut, stream order reversal', 'published_limit': '65 codes are not65 NSM meanings; prepared order encoding versus acquired association distinct; finite dialogue not unbounded reusable network', 'status': 'REFERENCE_SELECTED_FOR_INTEGRATION'}
    ]
    out = {'schema': 'CPC6.genealogy_map.v1', 'archive_identities': identity, 'source_root': 'genealogia/', 'rows': rows, 'layer_separation': ['native evolution and acquired state', 'declared external sensors/environment', 'passive instruments and diagnostic forks', 'auditor references never fed to participant'], 'replay_results': []}
    (ROOT / 'revision' / 'MAPA_CPC1_A_5.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'files': len(manifests), 'selected_bytes': sum(x['size_bytes'] for x in manifests), 'missing': missing, 'map': 'revision/MAPA_CPC1_A_5.json'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
