"""Small bounded integrity tests; synthetic bytes are not DEE measurements."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
from package_delivery import ROOT, NAME, split_transport, sha, put


def main():
    with tempfile.TemporaryDirectory(prefix='delivery_tool_test_',dir=ROOT/'jobs') as directory:
        folder=Path(directory)
        small=folder/'small.bin';small.write_bytes(b'CPC5 threshold test')
        no_parts=split_transport(small,folder)
        assert no_parts['split_required'] is False
        assert not list(folder.glob('*.001'))
        source=folder/NAME
        block=bytes(range(256))*4096
        with source.open('wb') as stream:
            for _ in range(21):stream.write(block)
            stream.write(b'odd-final-byte')
        original_hash=sha(source)
        parts=split_transport(source,folder)
        assert parts['reconstruction_tested'] and parts['zip_sha256']==original_hash
        assert len(parts['parts'])==2
        assert abs(parts['parts'][0]['bytes']-parts['parts'][1]['bytes'])<=1
        command=[sys.executable,'-I','-X','utf8',str(ROOT/'REUNIR_CPC5.py'),'--carpeta',str(folder)]
        joined=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=30)
        assert joined.returncode==0,joined.stderr
        reunited=folder/(NAME.removesuffix('.zip')+'_REUNIDO.zip')
        assert sha(reunited)==sha(source)==original_hash
        refused=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=30)
        assert refused.returncode!=0 and sha(reunited)==original_hash
        # Changing one part must be detected before producing an output.
        modified=folder/parts['parts'][0]['name']
        with modified.open('r+b') as stream:stream.write(b'BAD')
        wrong=subprocess.run(command+['--salida',str(folder/'must_not_exist.zip')],
                             capture_output=True,text=True,encoding='utf-8',timeout=30)
        assert wrong.returncode!=0 and not (folder/'must_not_exist.zip').exists()
        result={'schema':'CPC5.delivery-tools-test.v1','synthetic_bytes_not_scientific':True,
                'threshold_20MiB_uses_compressed_zip_size':True,
                'exactly_two_sequential_parts':True,'approximately_equal_sizes':True,
                'actual_reunion_sha256':original_hash,'existing_file_protected':True,
                'damaged_part_rejected':True,'canonical_preserved':sha(source)==original_hash}
    put(ROOT/'resultados'/'DELIVERY_TOOLS_TEST.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
