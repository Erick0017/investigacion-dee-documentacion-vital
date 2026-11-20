"""Mechanical release metadata/stub integration; no physics modifications."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
    stub=ROOT/'source/python/dee_thinking/_native.pyi'
    text=stub.read_text(encoding='utf-8').split('# DEE4 public cognitive additions')[0].rstrip()
    text+='\n\n# DEE4 public cognitive additions\n'
    for name in ('cognitive4.pyi.inc','informative4.pyi.inc'):
        text+=(stub.parent/name).read_text(encoding='utf-8')+'\n'
    stub.write_text(text,encoding='utf-8')
    contract=json.loads((ROOT/'PRODUCT_CONTRACT.json').read_text(encoding='utf-8'))
    contract['version']='4.0.0'
    contract['heritage']={'version':'3.5.0','product_sha256':'4cae52462e39ebc0443c14b4f07fe0a944cf6e1acb28f92a3657c80da2bb81ac','wheel_sha256':'721d4ad1610d6efc7e7101b49b9d68c6925efdcf596361aca09aabd0e315bcaa','preserved_nine_families':True,'source_changes':'native cognitive/informative layers, bindings, version metadata and tests; kernel untouched'}
    contract['primary_evidence']={'archive':'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip','sha256':'75ab357f41f6214c1798efbf69bd0708ab891038d30d770fdfe4a379208f793e','selected_members':'evidence/CPC3','selection_provenance':'PARENTS.json','inherited_multibranch_counts':'source experimental counts are provenance, not the number of tests run for 4.0'}
    contract['cpc3_public_capabilities']=[
      {'api':'CognitiveSession','profile':'continuity','N':47,'mode':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION','PASSIVE_OBSERVATION'],'realization':'current MAIN, local A/B relation and renewed zero-load sensing; external barrier observation is coded, not a future/error answer','domain':'T32 seed, declared origins and phase slots; consumption and rejection remain observable'},
      {'api':'CognitiveSession','profile':'comparison','N':47,'mode':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION'],'realization':'signed physical expectation/consequence comparison at84','domain':'one singleton directional class episode, not a general scalar equality oracle'},
      {'api':'NativeInformationSession','N':47,'mode':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION'],'realization':'expectation, comparison, route, information, later native use','domain':'finite prepared routes/resources; keep separate from other MAIN instances'},
      {'api':'FinitePolicySession','N':67,'mode':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION'],'realization':'R14 finite keep/switch organization, received report and later action','domain':'one prepared finite revision; not arbitrary learned utility'},
      {'api':'NativeAssociationSession','N':34,'mode':['EXPERIENCE_PROTOCOL','PHYSICAL_PROBE'],'realization':'online cue/teacher acquisition, common and sequential consuming queries','domain':'bounded additive relational family; form/word aliases external'},
      {'api':'create_learnable_cascade / experience_composition / query_composition','N':127,'mode':['EXPERIENCE_PROTOCOL','NATIVE_EVOLUTION','PHYSICAL_PROBE'],'realization':'empty coexisting native cascade, acquired relationships and physical routes','domain':'checked depths, timing, geometry; no output callbacks'},
      {'api':'dee_thinking.cognition / dialogue','mode':['PASSIVE_OBSERVATION','EXPERIENCE_PROTOCOL'],'realization':'Spanish grammar, lifecycle and fixed measurement renderer over native sessions','domain':'finite explicit grammar; unsupported questions never replaced by cached answers'}]
    contract['persistence_4']={'cognitive':'versioned physical world plus full protocol, predictions, external barrier law, interface aliases and audit journal','informative':'world snapshot metadata with bounded chunked session data, queues and receipts','legacy':'Runtime v1/v2 and OrganizationalWorld3.5 physical continuation; CPC3 Python session metadata is not silently migrated','no_pickle':True,'uint64_exact':True}
    contract['claims']={'single_universal_main':False,'language_model':False,'host_future_or_expected_answer_used_for_native_output':False,'external_environment':'explicit prepared barrier law; actual observed classes coded, evaluator never feeds errors back'}
    (ROOT/'PRODUCT_CONTRACT.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
