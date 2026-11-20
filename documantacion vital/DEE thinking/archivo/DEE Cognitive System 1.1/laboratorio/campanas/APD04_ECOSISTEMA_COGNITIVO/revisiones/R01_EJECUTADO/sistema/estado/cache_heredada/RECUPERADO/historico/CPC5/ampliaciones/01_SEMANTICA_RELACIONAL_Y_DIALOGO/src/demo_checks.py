"""Auditor only: compare newly generated demos after native trajectories."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,put,sha,digest,operational,identity

def verify(generated,reference,out):
    a=json.loads(Path(generated).read_text(encoding='utf-8'));b=json.loads(Path(reference).read_text(encoding='utf-8'))
    fields={k:a[k]==b[k] for k in ('rejected_commands','final_physical','final_operative')}
    fields['no_command_rejected']=a['rejected_commands']==0
    result={'schema':'CPC5.extension.demo_comparison.v1','verified':all(fields.values()),'fields':fields,
            'generated':str(generated),'reference':str(reference),'reference_sha256':sha(reference),
            'comparisons_after_native_trajectory_only':True}
    put(out,result);assert result['verified'];print(json.dumps(result))

def inspect(path,out):
    import dee_thinking as d
    identity();w=d.OrganizationalWorld.load_snapshot(str(path))
    op=operational(w);op['metadata']={k:v for k,v in op['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    put(out,{'physical':digest(w),'operative':op,'snapshot_sha256':sha(path)})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['verify','inspect']);p.add_argument('--generated',type=Path);p.add_argument('--reference',type=Path);p.add_argument('--snapshot',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    verify(a.generated,a.reference,a.output) if a.mode=='verify' else inspect(a.snapshot,a.output)
