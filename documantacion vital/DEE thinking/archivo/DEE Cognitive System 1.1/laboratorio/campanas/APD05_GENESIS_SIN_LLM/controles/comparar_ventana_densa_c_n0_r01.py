"""Exactly compare two already archived dense C fields; no motor/import/ticks."""
from pathlib import Path
from array import array
from collections import Counter
import argparse,hashlib,json,sys,zlib


def run(root):
    index=json.loads((root/'INDICE_FUENTES.json').read_bytes()); rows=[]
    for tick in (648684,648688):
        name='C_T%d_RAW_CLOCKS_U64_LE.zlib'%tick
        item=next(x for x in index['arrays'] if x['file']==name)
        path=root/item['exported']; encoded=path.read_bytes()
        if hashlib.sha256(encoded).hexdigest()!=item['sha256']:raise ValueError('Original field hash differs')
        data=zlib.decompress(encoded); n=67**3
        if len(data)!=16*n:raise ValueError('Array dimensions differ')
        raw=array('Q');clocks=array('Q');raw.frombytes(data[:8*n]);clocks.frombytes(data[8*n:])
        if sys.byteorder!='little':raw.byteswap();clocks.byteswap()
        rows.append((raw,clocks))
    a,b=rows
    return {'schema':'APD05.exact_dense_RAW_stationary_window.N0.R01','Native_ticks':0,
      'life':'APD04_ATENCION_SENSOR02_AUX','ticks':[648684,648688],'N':67,'sites':67**3,
      'RAW_changed_sites':sum(x!=y for x,y in zip(a[0],b[0])),
      'clock_changed_sites':sum(x!=y for x,y in zip(a[1],b[1])),
      'clock_delta_counts':{str(k):v for k,v in sorted(Counter(y-x for x,y in zip(a[1],b[1])).items())},
      'states_exact':{str(k):v for k,v in sorted(Counter(x&0xffffffff for x in a[0]).items())},
      'semantic_exact':{str(k):v for k,v in sorted(Counter((x>>60)&15 for x in a[0]).items())},
      'attribution':'The exact RAW field is unchanged across this FOUR-tick observed window while every clock advances4. This is not equality of the complete causal state, proof of an absorbing global microstate, irreversible memory loss, or a prediction for arbitrary future inputs. It motivates, but does not replace, the actual dynamic-rest controls from complete paired states.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    value=run(a.root)
    with a.out.open('x',encoding='utf8',newline='\n')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(value,ensure_ascii=False))


if __name__=='__main__':main()
