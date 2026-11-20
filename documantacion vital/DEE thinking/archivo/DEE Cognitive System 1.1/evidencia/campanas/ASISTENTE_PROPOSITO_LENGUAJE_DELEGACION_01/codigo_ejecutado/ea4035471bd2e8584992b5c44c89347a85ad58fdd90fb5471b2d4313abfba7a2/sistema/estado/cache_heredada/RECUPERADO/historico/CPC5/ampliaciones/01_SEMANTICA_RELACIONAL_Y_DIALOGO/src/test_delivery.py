"""Small synthetic transport/manifest checks. Not a DEE scientific trial."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_extension import BASE, EXT, NAME, PARENT_SHA, parent_inventory, put, safe_name, sha, split_transport


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(); started=time.monotonic(); checks=[]
    inherited=parent_inventory()
    assert len(inherited)==1379
    checks.append({'id':'parent_inventory','member_count':len(inherited),'parent_sha256':PARENT_SHA,'status':'PASS'})
    for bad in ('../outside','CPC5/../../outside','/CPC5/a','CPC5\\bad'):
        try: safe_name(bad)
        except ValueError: pass
        else: raise AssertionError('Unsafe name accepted: '+bad)
    checks.append({'id':'unsafe_names_rejected','status':'PASS'})
    temp_parent=EXT/'jobs'; temp_parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='delivery_synthetic_',dir=temp_parent) as folder:
        folder=Path(folder); small=folder/'small.bin'; small.write_bytes(b'CPC5 finite synthetic transport check')
        assert split_transport(small,folder/'unused')['split_required'] is False
        assert not (folder/'unused').exists()
        target=folder/'synthetic.bin'; count=21*1024*1024+3
        chunk=(b'CPC5-TRANSPORT-TEST-'*65536)
        with target.open('xb') as out:
            left=count
            while left:
                block=chunk[:min(left,len(chunk))];out.write(block);left-=len(block)
        destination=folder/'parts';destination.mkdir()
        result=split_transport(target,destination)
        assert result['reconstruction_tested'] and len(result['parts'])==2
        assert abs(result['parts'][0]['bytes']-result['parts'][1]['bytes'])<=1
        assert result['zip_sha256']==sha(target)
        output=folder/'actually_rejoined.zip'
        run=subprocess.run([sys.executable,'-I','-B',str(destination/'REUNIR_CPC5.py'),
                            '--salida',str(output)],capture_output=True,text=True,timeout=45)
        assert run.returncode==0,(run.stdout,run.stderr)
        assert sha(output)==sha(target) and output.stat().st_size==count
        blocked=subprocess.run([sys.executable,'-I','-B',str(destination/'REUNIR_CPC5.py'),
                                '--salida',str(output)],capture_output=True,text=True,timeout=45)
        assert blocked.returncode!=0 and sha(output)==sha(target)
        checks.append({'id':'two_binary_parts_actual_reunion','status':'PASS','synthetic_bytes':count,
                       'parts':[{'bytes':r['bytes'],'sha256':r['sha256']} for r in result['parts']],
                       'rejoined_sha256':sha(output),'existing_output_protected':True,
                       'temporary_test_payload_removed_after_test':True})
    result={'schema':'CPC5.extension.delivery-tools-test.v1','status':'VERIFIED',
            'scope':'Synthetic transport and format tests, not scientific observations or archive validation',
            'checks':checks,'elapsed_seconds':time.monotonic()-started}
    put(args.output,result);print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
