"""Prepare the eval seal only after an explicit, hashed Root calibration decision.

No selection or Native execution. The script checks preservation and exact
source identity; it does not infer scientific acceptance from a PASS label.
Root must provide the separate causal calibration decision and all proofs.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent
CALSHA='7d38997fab6b36bf6c6ea64694f49435312f7cafb8fadea76533e530270069c0'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,why):
    if not ok:raise ValueError(why)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--decision-root',type=Path,required=True);a=parser.parse_args()
    decisionbytes=a.decision_root.read_bytes();d=json.loads(decisionbytes)
    need(d.get('schema')=='DEE.PI10.Root_calibration_decision.R01'and d.get('calibration_accepted')is True and d.get('evaluation_authorized')is True,'Explicit Root causal acceptance and evaluation authorization required')
    need(d.get('protocol_calibration_sha256')==CALSHA,'Exact previously frozen calibration protocol')
    out=H/'PROTOCOLO_PI10_R01.json';b=out.read_bytes();need(sha(b)==CALSHA,'Unexpected current protocol: no silent new version or overwrite')
    p=json.loads(b);need(p['status']=='SEALED_FOR_CALIBRATION','Calibration protocol must remain current and preserved')
    proofs=d.get('calibration_proofs');need(isinstance(proofs,list)and len(proofs)>=2,'Both original closed calibration proofs required')
    for proof in proofs:
        source=Path(proof['file']);data=source.read_bytes();need(source.is_file()and sha(data)==proof['sha256'],'Exact original calibration proof bytes')
    for name,digest in p['sources_sha256'].items():need(sha((H/name).read_bytes())==digest,'Pinned source changed: '+name)
    need(d.get('scientific_schedule_and_criteria_unchanged')is True,'Changing scientific choices requires a new declared variant/reserve, not this seal')
    saved=P/'fuentes'/'PROTOCOLO_PI10_R01_SELLADO_CALIBRACION.json';need(not saved.exists(),'Do not overwrite the calibration seal')
    saved.write_bytes(b)
    p['status']='SEALED_FOR_EVALUATION';p['evaluation_sealed_utc']=datetime.now(timezone.utc).isoformat()
    p['evaluation_root_decision']={'file':str(a.decision_root.absolute()),'sha256':sha(decisionbytes),'calibration_protocol_sha256':CALSHA}
    p['not_a_seal']='Evaluation authorized prospectively after separately preserved Root calibration decision. No evaluation result, useful learning or adoption is claimed.'
    out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({'protocol':str(out),'sha256':sha(out.read_bytes()),'status':p['status'],'calibration_preserved':str(saved),'Native_executed':False}))
if __name__=='__main__':main()
