"""Versioned declarative contract; does not manufacture validation outcomes."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    inherited=json.loads((ROOT/'evidence/product40/PRODUCT_CONTRACT.json').read_text(encoding='utf-8'))
    contract={
      'schema':'DEE.thinking.product-contract.4.5.v1','product':'DEE thinking','version':'4.5.0',
      'author':'Ivan Erick Tlaltecatl Morales','project':'DEE Universe / INVESTIGACION DEE',
      'distribution':'PRIVATE_RECONSTRUCTIVE; no external publication authorized',
      'kernel':'DEE v27 frozen','kernel_source_sha256':inherited['kernel_source_sha256'],
      'platform':'Windows x64','python':'CPython 3.13 cp313','cpp':'C++20',
      'normal_execution':inherited['normal_execution'],
      'direct_physics':{'runtime_requires_cognitive_session':False,'import_prepares_world':False,
        'empty_runtime_injects_cognitive_material':False,'cognitive_recipes_optional':True,
        'passive_attach_edits_physics':False,'automatic_cleanup_or_clock_repair':False,
        'catalog_required_for_research':False,'recipe_domains_are_kernel_limits':False},
      'inherited_4_0_contract':{'status':'PRESERVED_CONTRACT; test coverage in VALIDATION_REPORT.json',
        'source':'evidence/product40/PRODUCT_CONTRACT.json','content':inherited},
      'new_contracts':{
        'repertoire':{'recipe_id':'repertoire.cpc5.v1','cpp_namespace':'dee::thinking::consolidated',
          'python':'dee_thinking.RepertoireSession','factory':'prepare_repertoire',
          'mechanical_domain':{'N':[31,151],'K':[1,65],'plane_gap_min':2,'condition':'gap*K <= N'},
          'witnesses':'N31/K8, N67/K16, N131/K65; other combinations are research preparations',
          'representation':'opaque acquired correspondences to two physical direction classes, not K NSM meanings',
          'training':'fixed cue and current observed-consequence carriers; no map initially in participant',
          'queries':'physical probes; consumes/modifies state; read window input_tick+3, finite tested cadences',
          'absence':'missing/unapplied/occupied/outside-window/observed-zero are not a common negative value'},
        'revision':{'methods':['double_teacher','symmetric_counterflow'],
          'interface_preflight':'all declared batch interfaces/codecs validated before the first submission; physical occupancy/phase still produces normal receipts, never automatic clearing',
          'modality':'EXTERNAL_DECLARED_PROTOCOL_WITH_NATIVE_TRANSFORMATION',
          'resources':'M1 adds an additional current-consequence teacher; M2 adds two fixed counterflows before lesson',
          'cadence':'repertoire revision at4N, next query5N; U0 L03 lesson402, next panel469..472',
          'controls':'offpath_sham keeps doses; no adaptive utility-policy claim',
          'offpath_scope':'repertoire z+10 sham validated for K2; populated K16/K65 can overlap another memory plane'},
        'integrated':{'recipe_id':'integrated_u0.cpc7.v1','python':'dee_thinking.IntegratedSession',
          'factory':'prepare_integrated_u0','N':67,'default_center':[33,25,42],
          'initial_source_load':0,'forms':16,'initial_learned_map':False,
          'mechanism':'order experience -> comparison -> discrepancy-conditioned native request -> one own acquired bank -> action interaction -> later arbitrary-form association -> more acquisition -> L03 revision',
          'horizon':472,'tested_backend':'LAZY','custom_geometries':'research preparation requiring new measurements',
          'selection':'prepared comparison and paths; content/route usage depends on acquired state, not general learned question policy',
          'guards':'six fixed physical interceptors; treatment/none/sham optional atT0; not learned attention',
          'complements':'absence-driven V2 and CPC6 remote reader remain distinct experimental profiles unless independently validated',
          'identity':'new T0 body; no trained historical snapshot is imported to claim new acquisition'},
        'observability':{'api':['DirectionalReadout','read_directional_response','read_form_response'],
          'passive':True,'integers':'RAW/clock uint64 in native state, decimal strings in JSON observations',
          'status':'Applied receipt required for a covered directional response; preserve receipt, reason and exact vector',
          'scope':'local physical reading, not a unique particle genealogy or general semantic decoder'},
        'experimental_absence':{'python':'dee_thinking.experimental_absence','status':'EXPERIMENTAL_BUNDLED',
          'N':67,'initial_source_load':7,'initial_placements':17,'interfaces':31,
          'scope':'CPC7 absence V2, prepared opportunity/absence-mediated request; separate from discrepancy U0/source0',
          'horizon':35,'read_boundaries':[19,24,29],'control':'match, unpaired source, request cut/sham, opposite-order reserve'},
        'experimental_remote_reader':{'python':'dee_thinking.RemoteReaderSession','status':'EXPERIMENTAL_BUNDLED',
          'N':67,'horizon':170,'read_boundaries':[53,90,162],
          'scope':'CPC6 word bus, first association, second acquisition, remote renewed access; not merged into CPC7U0',
          'supply':'44 declared ticks with finite opportunities','admission':'physical pattern coverage and query admission reported independently',
          'metadata_load_domain':'valid self-produced snapshots; bounded JSON/tick/channels checked, operational reads/requests/geometry less exhaustive than ConsolidatedSession; no general tampered-metadata robustness claim'},
        'experimental_acquired_regulation':{'python':'dee_thinking.experimental_regulation.CPC5RegulationSession','status':'EXPERIMENTAL_BUNDLED',
          'N':67,'horizon':437,'initial_conditions':'zero-load cue/report physically paired; learned directional product, no copied trained memory',
          'scope':'CPC5 learned-pulse routing and finite useful occupancy/contact; no consequence-selected general regulation policy',
          'controls':['unpaired','opposite','absent','translated reserve','diagnostic remove/sham where tested']},
        'persistence':{'native_runtime_formats':[1,2],'organizational_snapshot':'inherited format and operational queue',
          'native_string_path_encoding':'UTF-8 converted to native filesystem paths; ASCII C++4.0 consumers preserved, locale-encoded C++ paths must explicitly convert to UTF-8',
          'metadata_key':'dee_thinking.consolidated.session.v1','compression':'optional bounded gzip; CRC, encoded/logical size and optional SHA-256',
          'arbitrary_deserialization':False,'migration':'explicit selected CPC legacy metadata adapters on copies; no automatic reinterpretation',
          'restoration':'load native physical+operational snapshot; attach inert descriptor only; never rebuild or re-teach'},
        'language':{'interface':'structured Spanish commands, not free conversation or LLM',
          'NSM':'65-entry sourced evidence catalogue; registration is not acquisition',
          'provenance':['ENTE','INSTRUMENTO','INTERPRETACION']}
      },
      'compatibility':{'python_import':'dee_thinking','public_4_0_names':'preserved; API_DIFF.json compares installed exports',
        'cpp_target':'DEE::thinking','cmake_find_package':'dee_thinking 4.5 CONFIG',
        'source_compatibility':'tested declared 4.0 C++ domain; no universal binary ABI guarantee',
        'microscopic_law':'kernel byte-identical; inherited transition sections, branch order, packing, clocks and constants unchanged. Four literal filesystem conversions in snapshot/trace I/O audited separately by exact reversal'},
      'validation':'Declared contracts are checked by separate primary observations; RELEASE_VERIFIED is decided only by VALIDATION_REPORT.json and exact-ZIP external proof.'
    }
    text=json.dumps(contract,ensure_ascii=False,indent=2)
    for path in (ROOT/'PRODUCT_CONTRACT.json',ROOT/'source/PRODUCT_CONTRACT.json',ROOT/'source/python/dee_thinking/data/PRODUCT_CONTRACT.json'):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
    print('Contract written; no test status changed.')
if __name__=='__main__':main()
