"""Pure audit of one explicitly named immutable completed episode witness.

Reading a completed witness during a still-open owner's subsequent episodes
does not certify closure of the world or a coherent DB copy. Only the named
file is read and checked for unchanged bytes. No Native/Owner import.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--testigo',type=Path,required=True);p.add_argument('--protocolo',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    if a.salida.exists():raise ValueError('No overwrite of a previous primary audit')
    code=H/'recalcular_primarios_PI10_R02.py';s=importlib.util.spec_from_file_location('primary_audit',code);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    before=a.testigo.read_bytes();protocol=a.protocolo.read_bytes();v=json.loads(before);actual=m.project_episode(v,json.loads(protocol))
    if a.testigo.read_bytes()!=before or a.protocolo.read_bytes()!=protocol:raise ValueError('Observed concurrent change; no stable witness conclusion')
    result={'schema':'DEE.PI10.one_immutable_witness_recalc.R01','at_utc':datetime.now(timezone.utc).isoformat(),
      'testigo':{'file':str(a.testigo.absolute()),'bytes':len(before),'sha256':hashlib.sha256(before).hexdigest()},
      'protocol_sha256':hashlib.sha256(protocol).hexdigest(),'independent_reader_sha256':hashlib.sha256(code.read_bytes()).hexdigest(),
      'projection_checked':True,'row':actual,'Native_executed':False,'DEE_imported':False,'world_closure_not_certified':True,
      'scope':'A named immutable completed record only; current world, later operations and file-transfer payload bytes are not reread here. Use the closed compact-bundle audit for the latter.'}
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
