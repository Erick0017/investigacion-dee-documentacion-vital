"""Retrieve identified I01/I02 runners, never run them on import."""
import hashlib,json,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from supervise import atomic_json
def sha(b):return hashlib.sha256(b).hexdigest()
def main(root):
    root=Path(root).resolve();vital=root.parents[3];index=[]
    selected={
      'INGENIERIA_01_DEE_V27_MEMORIA_APRENDIZAJE_PLASTICIDAD_Y_PROCESAMIENTO_RESULTADOS.zip':[
       'REWRITE_WORK/RUNNERS/reset_apparatus_v1.py','REWRITE_WORK/RUNNERS/feedback_apparatus_v1.py','REWRITE_WORK/RUNNERS/rewrite_common.py','REWRITE_WORK/RUNNERS/clock_decoder_apparatus_v1.py','REWRITE_WORK/RUNNERS/run_r04_reset_corrected_holdout.py','REWRITE_WORK/RUNNERS/freeze_r04_reset_corrected.py','REWRITE_WORK/RUNNERS/run_r14_feedback_holdout.py','REWRITE_WORK/RUNNERS/freeze_r14_feedback.py'],
      'INGENIERIA_02_DEE_V27_PROCESAMIENTO_INTEGRADO_ADAPTACION_Y_AUTONOMIA_RESULTADOS.zip':[
       'RUNNERS/paired_relative_apparatus_v2.py','RUNNERS/temporal_order_apparatus_v1.py','RUNNERS/run_d14_persistent_native_reader.py','RUNNERS/run_d15_recurrent_feedback_phase_search.py','RUNNERS/ing02_common.py','RUNNERS/integrated_scaffold_apparatus_v2.py','RUNNERS/run_d09_relative_readout_longevity.py','RUNNERS/run_d16_temporal_order_discovery.py']}
    for archive,members in selected.items():
        path=vital/'ingenieria'/archive
        with zipfile.ZipFile(path) as z:
            hashes={}
            if 'HASHES.sha256' in z.namelist():
                for row in z.read('HASHES.sha256').decode('utf-8-sig').splitlines():
                    if not row.strip():continue
                    h,name=row.split(maxsplit=1);hashes[name.strip().lstrip('*')]=h
            folder='I01' if '_01_' in archive else 'I02'
            for member in members:
                data=z.read(member)
                if member in hashes:assert sha(data)==hashes[member]
                out=root/'fuentes_pertinentes'/folder/member;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
                index.append({'archive':str(path),'archive_sha256':sha(path.read_bytes()),'member':member,'sha256':sha(data),'manifest_checked':member in hashes,'destination':out.relative_to(root).as_posix(),'status':'source recovered, historical campaign not rerun'})
    product=vital/'DEE thinking/archivo/DEE_thinking_3_5_0_ENTREGA_FINAL_RESULTADOS.zip'
    assert sha(product.read_bytes())=='4cae52462e39ebc0443c14b4f07fe0a944cf6e1acb28f92a3657c80da2bb81ac'
    with zipfile.ZipFile(product) as z:
        for rel in ['source/src/runtime.cpp','source/include/dee_thinking/runtime.hpp','source/include/dee_thinking/organizational.hpp','source/bindings/organizational_pybind.cpp']:
            matches=[n for n in z.namelist() if n==rel or n.endswith('/'+rel)]
            assert len(matches)==1,(rel,matches);data=z.read(matches[0]);out=root/'fuentes_pertinentes/producto'/rel;out.parent.mkdir(parents=True,exist_ok=True)
            if out.exists():assert out.read_bytes()==data
            else:out.write_bytes(data)
            index.append({'archive':str(product),'member':matches[0],'sha256':sha(data),'destination':out.relative_to(root).as_posix(),'role':'exact implementation decision map, frozen source'})
    atomic_json(root/'fuentes_pertinentes/MECHANISM_INDEX.json',index);print(json.dumps({'retrieved':len(index),'historical_runs':0}))
if __name__=='__main__':main(sys.argv[1])
