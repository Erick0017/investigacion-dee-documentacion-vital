"""Lossless storage optimization only; never modifies a physical Runtime."""
from pathlib import Path
import argparse,base64,json,zlib,struct,hashlib,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from campos_guardados import array_bytes,values
sys.stdout.reconfigure(encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError('Existing optimized field view protected')
    a.out.mkdir(parents=True);previous=[];summary=[]
    for f in sorted(a.source.glob('S*.json')):
        d=json.loads(f.read_bytes());fields={k:array_bytes(d,k,a.source)for k in('RAW','CLOCKS')};dd=dict(d);used={}
        for key,raw in fields.items():
            full=dd[key+'_ZLIB_BASE64'];best=None;cost=len(full)
            # Initial, immediately previous, and last main2353 are a bounded,
            # data-compression choice, never a policy choice by the participant.
            candidates=[]
            for i in sorted(set([0,len(previous)-1]+[i for i,v in enumerate(previous)if v['name']=='S09_T2353.json'])):
                if 0<=i<len(previous):candidates.append(previous[i])
            for base in candidates:
                old=base['fields'][key];res=bytearray(len(raw));offset=(d['physical']['tick']-base['tick'])if key=='CLOCKS'else 0
                for i,(v,pv)in enumerate(zip(values(raw),values(old))):
                    value=(v-pv-offset)&((1<<64)-1)if key=='CLOCKS'else v^pv;struct.pack_into('<Q',res,i*8,value)
                enc=base64.b64encode(zlib.compress(res,9)).decode('ascii');candidate={'base_file':base['name'],'operation':'ADD_OFFSET_MOD2_64'if key=='CLOCKS'else'XOR','offset':offset,'residual_ZLIB_BASE64':enc}
                trial=len(json.dumps(candidate,separators=(',',':')))
                if trial<cost:best=candidate;cost=trial
            if best:
                dd.pop(key+'_ZLIB_BASE64');dd[key+'_DELTA']=best;used[key]={'base':best['base_file'],'operation':best['operation']}
            else:used[key]={'operation':'FULL_ZLIB_BASE64'}
        dd['array_encoding']='Lossless fulluint64LE or declared base+XOR/add-offset residual; every reconstructed array must match its originalSHA.'
        out=a.out/f.name;out.write_text(json.dumps(dd,ensure_ascii=False,separators=(',',':'),sort_keys=True)+'\n',encoding='utf8')
        for key,b in fields.items():
            if array_bytes(dd,key,a.out)!=b:raise ValueError('Optimized field did not reproduce original bytes')
        previous.append({'name':f.name,'tick':d['physical']['tick'],'fields':fields});summary.append({'file':f.name,'encoding':used,'physical':d['physical'],'all_original_uint64_bytes_equal':True})
    (a.out/'EXTRACCION_CAMPOS.json').write_text(json.dumps({'status':'PASS','scope':'Storage transform, not new experience, regulator or clock manipulation','records':summary},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':'PASS','records':len(summary),'bytes':sum(f.stat().st_size for f in a.out.iterdir()),'all_original_fields_equal':True}))
if __name__=='__main__':main()
