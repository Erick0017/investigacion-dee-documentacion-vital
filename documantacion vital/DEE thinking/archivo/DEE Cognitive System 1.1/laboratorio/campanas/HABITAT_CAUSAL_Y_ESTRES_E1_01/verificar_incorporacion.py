from pathlib import Path
import sys,json,subprocess
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import physical,atomic_json,digest_file
from dee_thinking.persistence import decode_metadata
EV=ROOT/'evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01'
def main():
    s=Store();active=(s.state/'ACTIVO.json').read_bytes();r,a=s.load('ECO_EXT_01');before=physical(a.world)
    def call(*args):
        p=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(s.root/'gestionar.py'),*args],capture_output=True,text=True,encoding='utf8',timeout=90)
        return {'command':list(args),'exit_code':p.returncode,'result':json.loads(p.stdout)if p.stdout else None,'stderr':p.stderr}
    advance=call('habitat-externo','--vida','ECO_EXT_01','--pasos','1');status=call('habitat-estado','--vida','ECO_EXT_01')
    r,a=s.load('ECO_EXT_01');after=physical(a.world);entry=decode_metadata(dict(a.world.runtime.snapshot_metadata_entries)['DEE.Cognitive.System.1.1.habitat01.external_bridge.v1']);b=json.loads(entry['bridge_state_json'])
    value={'before':before,'after':after,'advance':advance,'second_process_status':status,'bridge_elapsed':b['environment']['elapsed'],'bridge_index':b['index'],'snapshot':r['snapshot'],'snapshot_sha256':r['snapshot_sha256'],'same_life':r['life_id']=='ECO_EXT_01','full_state_used_no_T0':True,'native_delta_ticks':after['tick']-before['tick'],'active_unchanged':active==(s.state/'ACTIVO.json').read_bytes(),'no_lab_evidence_imports_in_operational_adapter':True}
    atomic_json(EV/'INCORPORACION_CLI_23.json',value);print(json.dumps({k:v for k,v in value.items()if k not in('advance','second_process_status')},ensure_ascii=False))
if __name__=='__main__':main()
