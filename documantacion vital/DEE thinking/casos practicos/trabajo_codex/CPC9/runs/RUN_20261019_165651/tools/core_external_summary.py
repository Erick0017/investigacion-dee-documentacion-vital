"""Derived summaries copied outside immutable Core ZIP for CPC9's final report."""
from pathlib import Path
from collections import Counter
import hashlib, json, zipfile
RUN=Path(__file__).resolve().parents[1]
artifact=RUN/'core/final/DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip'
with artifact.open('rb')as stream:identity=hashlib.file_digest(stream,'sha256').hexdigest()
assert identity=='412a6819e36203a0086790003301a13722bd14fd3a3213b03681d827f7cca1a2'
with zipfile.ZipFile(artifact)as archive:
    m=json.loads(archive.read('DEE_COGNITIVE_CORE/documentacion/MATRIZ_CAPACIDADES.json'))
    c=json.loads(archive.read('DEE_COGNITIVE_CORE/documentacion/COMPRESION.json'))
    expanded=sum(row.file_size for row in archive.infolist())
pending=[{key:r.get(key)for key in('id','CPC_origin','mechanism','domain','controls','limits','current_status_explanation','source_count','source_bytes_recovered')}for r in m['rows']if r['current_recovery_status']=='D']
out=artifact.parent
data={'schema':'DEE_CORE.external_summary.v1','artifact_sha256':identity,
      'compressed_bytes':artifact.stat().st_size,'expanded_bytes':expanded,
      'outer_members':103,'logical_members':c['content_paths'],'unique_blobs':c['unique_blobs'],
      'logical_selected_bytes':c['selected_logical_unpacked_bytes'],
      'unique_selected_bytes':c['unique_unpacked_bytes'],
      'historical_archive_copies_compressed_bytes':c['all_historical_archive_copies_compressed_bytes'],
      'historical_archive_copies_expanded_bytes':c['all_historical_archive_copies_expanded_bytes'],
      'historical_corpus_scope':'Only the identified CPC3–CPC8 archive copies, with CP01/CP02 genealogies inside CPC3. Not the whole DEE document corpus; not unique information.',
      'compressed_size_reduction_fraction':1-artifact.stat().st_size/c['all_historical_archive_copies_compressed_bytes'],
      'expanded_size_reduction_fraction':1-expanded/c['all_historical_archive_copies_expanded_bytes'],
      'compression_caveat':'These reductions include explicit coverage loss of unselected dense snapshots and documentary domains not reproduced. They are not an information-equivalence assertion.',
      'capability_rows':len(m['rows']),'classification_counts':m['counts'],
      'no_automatic_E1_promotions':True,
      'pending_broad_domains':pending,
      'raw_snapshot_essential_names':c['exact_seed_snapshots_retained'],
      'public_recovery_families':32,'optional_direct_array_families':2,
      'optional_dependency':'NumPy2.2.6 for CORE06/07, explicit external --numpy-root; default32need only CPython3.13x64 and OS C++ runtime.',
      'status':'SEALED_WAITING_EXACT_ZIP_FULL34_RECOVERY'}
(out/'CORE_RESUMEN_Y_PENDIENTES.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({key:data[key]for key in('artifact_sha256','classification_counts','logical_members','unique_blobs','compressed_size_reduction_fraction','status')}))
