"""Read one committed complete life cut with the stdlib observer;0ticks."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--sistema',type=Path,required=True);p.add_argument('--vida',required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();record_path=a.sistema/'estado/vidas'/a.vida/'VIDA.json';before=record_path.read_bytes();rec=json.loads(before)
    snapshot=a.sistema/rec['snapshot'];sp=importlib.util.spec_from_file_location('obs0',a.sistema/'capacidades/observador_causal_retrospectivo_01.py')
    obs=importlib.util.module_from_spec(sp);sp.loader.exec_module(obs);s=obs.Snapshot(snapshot)
    if s.encoded_sha256!=rec['snapshot_sha256']:raise ValueError('Committed snapshot SHA mismatch')
    av=s.observation([14,14,15]);bv=s.observation([16,14,15]);after=record_path.read_bytes()
    z={'life_id':rec['life_id'],'tick':s.tick,'N':s.N,'snapshot':str(snapshot),'snapshot_sha256':s.encoded_sha256,
       'checksum_valid':s.checksum_valid,'VIDA_sha256_at_selection':sha(before),'VIDA_sha256_after_decode':sha(after),
       'same_committed_pointer_during_decode':before==after,'A':av,'B':bv,'D_A_minus_B':av['s_reg']-bv['s_reg'],
       'clock_aligned':int(av['clock'])==s.tick and int(bv['clock'])==s.tick,'native_pending':len(s.pending),
       'native_ticks_executed':0,'scope':'One committed complete cut, not an advancing life or a private Runtime. A concurrent later commit does not invalidate the immutable measured snapshot.'}
    with a.salida.open('xb')as f:f.write((json.dumps(z,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8'))
    print(json.dumps(z,ensure_ascii=False))
if __name__=='__main__':main()
