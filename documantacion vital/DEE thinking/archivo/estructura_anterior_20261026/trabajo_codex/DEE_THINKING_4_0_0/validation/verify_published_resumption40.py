"""Verify the published container and its exact tested executable payload.

Does not repeat scientific cases or modify the package. The external receipt
contains the ZIP hash so that no circular self-identity is introduced.
"""
import argparse, hashlib, json, zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

PREFIX = 'DEE_thinking_4_0_0/'
KERNEL = 'fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'

def digest(data): return hashlib.sha256(data).hexdigest()
def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);p.add_argument('--tested-candidate',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
    with zipfile.ZipFile(a.archive) as z,zipfile.ZipFile(a.tested_candidate) as tested:
        names=z.namelist();assert len(names)==len(set(names));assert z.testzip() is None
        assert all(n.startswith(PREFIX) and '..' not in PurePosixPath(n).parts for n in names)
        data=json.loads(z.read(PREFIX+'MANIFEST.json'));expected={}
        for row in data['files']:
            name=row['path'];assert not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts
            assert name not in expected;expected[name]=row['sha256'];body=z.read(PREFIX+name)
            assert len(body)==row['size'] and digest(body)==row['sha256'],name
        assert set(names)=={PREFIX+x for x in expected}|{PREFIX+'MANIFEST.json',PREFIX+'HASHES.sha256'}
        hashes={}
        for line in z.read(PREFIX+'HASHES.sha256').decode('utf-8').splitlines():
            sha,name=line.split('  ',1);assert name not in hashes;hashes[name]=sha
        assert hashes=={**expected,'MANIFEST.json':digest(z.read(PREFIX+'MANIFEST.json'))}
        report=json.loads(z.read(PREFIX+'VALIDATION_REPORT.json'));checks=json.loads(z.read(PREFIX+'validation/FINAL_EXTRACTION_CHECK.json'))
        assert report['status']=='RELEASE_VERIFIED' and checks['all_commands_succeeded']
        assert checks['archive_tested_sha256']==file_sha(a.tested_candidate)
        assert report['block_I']['cpp_unique_tests']==22 and report['block_I']['python_unique_methods']==61
        assert report['block_II']['scientific_case_records_total']==30
        assert digest(z.read(PREFIX+'source/src/kernel_v27.cpp'))==KERNEL
        wheel='wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
        assert expected[wheel]==checks['installed_wheel_sha256']==report['wheel_sha256']
        # Every file in the execution payload is unchanged since the actual
        # clean-extraction installation and trajectory. New records are only
        # closure reports/documentation and retained diagnostic evidence.
        fixed=('source/','install_cpp/','wheel/','app/')
        singles={'supervise40.py','iniciar_mente.ps1','tools/reproduce40.py','tools/verify40.py','tools/build40.ps1','experiments/run_block_ii.py','experiments/run_signal_prediction40.py','validation/release_smoke40.py'}
        old=set(tested.namelist());covered=[]
        for name in expected:
            if name.startswith(fixed) or name in singles:
                assert PREFIX+name in old and z.read(PREFIX+name)==tested.read(PREFIX+name),name
                covered.append(name)
        assert len(covered)>100
        changes=[n[len(PREFIX):] for n in names if n not in old or z.read(n)!=tested.read(n)]
    value={'product':'DEE thinking4.0.0','status':'RELEASE_VERIFIED','path':str(a.archive.resolve()),'size_bytes':a.archive.stat().st_size,'sha256':file_sha(a.archive),'wheel_sha256':report['wheel_sha256'],'kernel_source_sha256':KERNEL,'CRC':True,'manifest_and_hashes':True,'tested_payload_byte_identical':covered,'differences_from_tested_candidate':changes,'member_count':len(names),'validation':'fresh extraction, noneditable installation, public CPC3 function, newly generated trajectory, shipped Spanish launcher, pending-input restoration in another process, external C++ consumer','generated_utc':datetime.now(timezone.utc).isoformat(),'scientific_scope':'30 finite case records, not 30 independent capacities or population replicates'}
    a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:value[k] for k in ('path','size_bytes','sha256','wheel_sha256','CRC','manifest_and_hashes','member_count')},indent=2))

if __name__=='__main__':main()
