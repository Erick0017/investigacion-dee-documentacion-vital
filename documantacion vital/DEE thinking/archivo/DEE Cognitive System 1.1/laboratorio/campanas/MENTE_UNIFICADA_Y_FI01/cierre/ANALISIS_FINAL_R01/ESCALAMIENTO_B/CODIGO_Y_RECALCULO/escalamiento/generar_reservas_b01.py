"""Freeze externally designed raw cases, never imported by the DEE codec.

This is an examiner data generator, not a native input compressor or policy.
Every output list must still be sent scalar-by-scalar through the physical tree.
"""
import argparse,hashlib,json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    records=[]
    for n in(8,16,32,64,128):
        q,r=divmod(63,n);base=[q+int(i<r)for i in range(n)]
        cases=[{'id':'BASE','raw':base}]
        for i in range(n):
            value=list(base);value[i]+=2
            cases.append({'id':'COMPONENT_'+str(i),'component_changed':i,'delta':2,'raw':value})
        assert max(max(x['raw'])for x in cases)<=32
        records.append({'joint_level':n,'raw_cases':cases,'base_examinee_command_hypothesis':1,'perturbed_examinee_command_hypothesis':-1,'criterion':'If learned/native threshold64 is confirmed prospectively, each component changes one physical action. Otherwise preserve failed hypothesis; do not relabel this reserve as valid after tuning.'})
    data={'schema':'FI01.B01.prospective_component_cases.v1','generated_by_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'native_ticks':0,'not_runtime_actor_input':'Expected commands, IDs, changed indices and teaching labels are auditor-only; frame() receives raw lists only.',
          'teaching_histories':{'T':[74,12],'U':[42,12],'H':[12,74]},'rows':records,'dependent_copies':'All component contrasts may share one learned prefix/base reference. Not independent learners or teaching replications.'}
    a.out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'output':str(a.out),'bytes':a.out.stat().st_size,'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'native_ticks':0}))
if __name__=='__main__':main()
