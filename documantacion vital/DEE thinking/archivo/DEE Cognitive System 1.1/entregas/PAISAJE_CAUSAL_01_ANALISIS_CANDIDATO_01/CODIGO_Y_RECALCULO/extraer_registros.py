"""Safe data-only verification/extraction of the indexed PC01 measured records.

Python standard library only. Does not import the engine or execute archive
members. Default verifies all hashes without expanding to disk.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,tarfile
def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--out',type=Path);p.add_argument('--prefix',default='');p.add_argument('--report',type=Path);a=p.parse_args();folder=a.root/'EVIDENCIA_ESENCIAL';index=json.loads((folder/'INDICE_REGISTROS.json').read_bytes());archive=folder/'REGISTROS_COMPLETOS.tar.xz';expected={r['member']:r for r in index['members']}
    if len(expected)!=len(index['members'])or index['payload_expanded_bytes']>2*1024**3:raise ValueError('Invalid/oversized data index')
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=index['archive_sha256']:raise ValueError('Data archive hash mismatch')
    verified=[];written=[];total=0
    with tarfile.open(archive,'r|xz')as tf:
        for member in tf:
            rel=PurePosixPath(member.name)
            if not member.isfile()or rel.is_absolute()or'..'in rel.parts or'\\'in member.name or':'in member.name or member.name not in expected:raise ValueError('Unexpected data member')
            row=expected[member.name]
            if member.size!=row['payload_bytes']or member.size>128*1024**2:raise ValueError('Unexpected data size')
            data=tf.extractfile(member).read();total+=len(data)
            if total>2*1024**3 or hashlib.sha256(data).hexdigest()!=row['payload_sha256']:raise ValueError('Data reconstruction mismatch')
            verified.append(member.name)
            if a.out and member.name.startswith(a.prefix):
                base=a.out.resolve();dest=base.joinpath(*rel.parts).resolve()
                if not dest.is_relative_to(base):raise ValueError('Output outside requested extraction directory')
                dest.parent.mkdir(parents=True,exist_ok=True)
                if dest.exists()and dest.read_bytes()!=data:raise FileExistsError('Different existing extraction is preserved: '+str(dest))
                if not dest.exists():dest.write_bytes(data)
                written.append(member.name)
    if len(verified)!=len(expected):raise ValueError('Missing indexed records')
    result={'schema':'PC01.data_reconstruction.verification.v1','archive_sha256':index['archive_sha256'],'verified_members':len(verified),'expanded_payload_bytes':total,'written_members':len(written),'all_indexed_payloads_exact':True,'no_native_simulation_or_code_execution':True,'not_an_operational_world_backup':True}
    if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result));return 0
if __name__=='__main__':raise SystemExit(main())
