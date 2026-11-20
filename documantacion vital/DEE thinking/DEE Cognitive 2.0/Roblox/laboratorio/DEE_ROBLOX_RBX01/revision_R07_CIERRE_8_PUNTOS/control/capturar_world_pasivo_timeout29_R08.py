"""One passive, nonretrying World checkpoint after known LLM timeout. No Native."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidencia/LLM_TIMEOUT29_MUNDO_PRESERVADO_R08'
STUDIO='55088438-427a-4b14-b6d1-3af85bad9dca'
def record(kind,**fields):
    with(OUT/'EVENTS.jsonl').open('a',encoding='utf8')as f:
        f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':kind,**fields},ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
def run():
    if OUT.exists():raise FileExistsError('No checkpoint retry or reused destination')
    OUT.mkdir();path=ROOT/'control/world_comprimido_v3_R07_REFERENCIAS.py'
    spec=importlib.util.spec_from_file_location('_passive_timeout29_world',path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    world=None
    try:
        world=m.CompressedWorld(STUDIO,OUT,record,expected_place='DEE_RBX01_R07_NATIVE.rbxlx')
        saved=world.checkpoint('R07_LLM_TIMEOUT29_POST_BEGIN_READ_ONLY',OUT/'WORLD_CHECKPOINT.json')
        raw=(OUT/'WORLD_CHECKPOINT.json').read_bytes()
        result={'status':'PASSIVE_WORLD_CHECKPOINT_SAVED_AFTER_LLM_TIMEOUT','studio':STUDIO,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
          'boundary':saved['boundary'],'S':saved['S'],'Native_calls':0,'model_calls':0,'initialize_calls':0,'begin_calls':0,'action_calls':0,'automatic_retry':False,
          'scope':'Preserved actual post-BEGIN29 World. No claim that a pending reference episode is a restorable quiescent boundary.'}
    except BaseException as error:
        result={'status':'PASSIVE_CHECKPOINT_REJECTED_PRESERVED','error':type(error).__name__+': '+str(error),'Native_calls':0,'model_calls':0,
          'initialize_calls':0,'begin_calls':0,'action_calls':0,'automatic_retry':False}
        record('FAILED_PRESERVED',error=result['error'])
    finally:
        if world is not None:world.close()
    with(OUT/'RESULTADO_CAPTURA.json').open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':run()
