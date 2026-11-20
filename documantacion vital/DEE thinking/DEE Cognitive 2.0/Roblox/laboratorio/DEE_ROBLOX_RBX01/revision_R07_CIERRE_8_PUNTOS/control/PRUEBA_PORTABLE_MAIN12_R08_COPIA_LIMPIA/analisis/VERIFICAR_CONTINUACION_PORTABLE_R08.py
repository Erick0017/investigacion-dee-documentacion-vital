"""Finite passive check of the delivered MAIN35-46 recipe; no Native/SDK/DB."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

def load(p): return json.loads(p.read_text('utf-8-sig'))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):
    root=a.package_root.resolve(); out=a.output.resolve()
    if out.exists() or not out.parent.is_dir(): raise ValueError('Fresh output with existing parent required')
    out.mkdir()
    script=root/'analisis/RECALCULO_CONTINUACION_35_46_R07_R01.py'
    inp=root/'analisis/INPUTS_CONTINUACION_35_46_R07_R01.json'
    resource_script=root/'analisis/RECURSOS_RECALCULO_R07.py'
    resource_root=root/'analisis/RECURSOS_MAIN12_CERRADO_R08_R01'
    commands=[
      [sys.executable,'-I','-B',str(script),'--inputs',str(inp),'--package-root',str(root),'--output',str(out/'science')],
      [sys.executable,'-I','-B',str(resource_script),'--owner-journal','MAIN35_46='+str(resource_root/'PRIMARIOS/01_owner.jsonl'),'--phase-events','LIVE_NATIVE='+str(resource_root/'PRIMARIOS/02_phases.jsonl'),'--output',str(out/'resources')]]
    calls=[]
    for i,cmd in enumerate(commands,1):
        r=subprocess.run(cmd,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',timeout=120)
        (out/f'command_{i}.stdout.txt').write_text(r.stdout,encoding='utf-8')
        (out/f'command_{i}.stderr.txt').write_text(r.stderr,encoding='utf-8')
        calls.append({'returncode':r.returncode,'script_sha256':digest(Path(cmd[3]))})
        if r.returncode: raise ValueError('Passive recipe failed: '+str(i))
    before=load(root/'analisis/MAIN12_CONTINUACION_RECALCULO_R08_R01/HECHOS_CIERRE8_R07.json')
    after=load(out/'science/HECHOS_CIERRE8_R07.json')
    for doc in (before,after):
        for src in doc['sources']: src.pop('resolved',None)
    science_equal=before==after
    rb=load(resource_root/'RECURSOS_RECALCULADOS.json'); ra=load(out/'resources/RECURSOS_RECALCULADOS.json')
    resource_fields=('status','owner_runs','closed_owner_aggregate','phase_times','phase_aliases_deduplicated','issues')
    resource_equal=all(rb[k]==ra[k] for k in resource_fields)
    proof={'schema':'DEE.R07.MAIN12.portable_verification.R08.v1','science_equal_except_resolved_local_paths':science_equal,
      'resource_measurements_equal':resource_equal,'resource_compared_fields':resource_fields,'calls':calls,
      'science_issues':after['issues_total'],'resource_issues':ra['issues'],
      'source_resolution':'Package manifest aliases only; no original filesystem source paths read by the science recipe',
      'Native_executed':False,'MCP_Studio_model_SQLite_executed':False,
      'scope':'Only continuation35-46 and its one resource run. Earlier MAIN6/CTRL/P07 never recalculated. Clean selected-file copy proof; final ZIP extraction remains separate.'}
    (out/'VERIFICACION_PORTABLE_MAIN12_R08.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(proof,ensure_ascii=False))
    return 0 if science_equal and resource_equal and after['issues_total']==0 and not ra['issues'] else 1
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    raise SystemExit(run(p.parse_args()))
