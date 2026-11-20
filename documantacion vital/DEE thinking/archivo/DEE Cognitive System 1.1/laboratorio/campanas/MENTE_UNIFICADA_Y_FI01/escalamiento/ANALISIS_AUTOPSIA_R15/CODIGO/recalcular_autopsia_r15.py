"""Portable stdlib-only recalc; no DEE import or new ticks.

Evidence folder contains four exact records, agenda extracts and deduplicated
complete u64le physical fields. Full operational snapshots remain local.
"""
from pathlib import Path
from array import array
import argparse,gzip,hashlib,json,sys

def read(p):
    b=Path(p).read_bytes();return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)

def signed(v,k):
    x=(v>>k)&15;return x-16 if x&8 else x

def decoded(v):return {'state':v&0xffffffff,'s_reg':(v>>32)&65535,'semantic':v>>60,'direction':[signed(v,k)for k in(48,52,56)]}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('folder',type=Path);ap.add_argument('--out',type=Path);args=ap.parse_args();p=args.folder
    labels=['real','no_datum','sham_datum','no_query'];tags=['62525_COMMON','62564_POST','62698_PASSIVE','62896_COMMON_RAW128']
    checks=[];frames=0;arrays={};agendas={};summaries=[]
    def ck(ok,label):
        checks.append({'check':label,'ok':bool(ok)})
        if not ok:raise AssertionError(label)
    def fields(h):
        if h not in arrays:
            data=gzip.decompress((p/'fields'/(h+'.u64le.gz')).read_bytes());ck(hashlib.sha256(data).hexdigest()==h,'exact physical field SHA '+h)
            a=array('Q');a.frombytes(data)
            if sys.byteorder!='little':a.byteswap()
            ck(len(a)==67**3,'complete u64le field size '+h);arrays[h]=a
        return arrays[h]
    for arm in labels:
        r=read(p/(arm+'.json.gz'));rs=r['requests'];ck(len(rs)=={'real':4,'no_datum':3,'sham_datum':4,'no_query':1}[arm],'initial dose '+arm)
        ck(all(x['receipt']['status']=='applied'for x in rs),'initial admission '+arm)
        for f in r['phase_frames']:
            for o in f['fields'].values():
                frames+=1;d=decoded(int(o['raw']));ck(all(d[k]==o[k]for k in d),'exact RAW decoding '+arm+' '+str(f['tick'])+' '+str(o['site']))
        phase={f['tick']:f for f in r['phase_frames']}
        ck(phase[62560]['fields']['A']['s_reg']==104 and phase[62560]['fields']['B']['s_reg']==124,'prewrite refs '+arm)
        a=104 if arm=='real'else 105
        ck(phase[62561]['fields']['A']['s_reg']==a and phase[62561]['fields']['B']['s_reg']==125,'postwrite refs '+arm)
        common=r['common_raw128'];v=[0]*128;v[0]=19;v[2]=2
        ck(common['raw_components']==v,'identical common raw vector '+arm)
        ck(len(common['requests'])==176 and all(x['receipt']['status']=='applied'for x in common['requests']),'common176/176 admission '+arm)
        reader=common['reader'];cs=[]
        for o in reader['observations']:
            d=decoded(int(o['raw']));x=(o['site'][0]-15)//2;z=(o['site'][2]-15)//2
            ck(all(d[k]==o[k]for k in d),'common reader RAW decoding '+arm+' '+str(o['site']))
            if d['state']>0 and d['semantic']==1 and d['direction']==[x,1,z]:cs.append(x)
        choice=cs[0]if len(cs)==1 else None
        ck(reader['choice']==choice and choice==(None if arm=='real'else 1),'frozen common reader '+arm)
        ff={f['tick']:f['fields']for f in common['frames']}
        ck(ff[62757]['S']['s_reg']==21,'common S21 '+arm)
        ck(ff[62758]['E']['direction']==([0,1,-1]if arm=='real'else[1,1,-1]),'native common output direction '+arm)
        summaries.append({'arm':arm,'requested':len(rs),'admitted':len(rs),'post_A':a,'post_B':125,'post_difference':a-125,'scalar_reader':r['fixed_scalar_reader']['choice'],'common_requests':176,'common_admitted':176,'common_choice':choice})
        for tag in tags:
            q=read(p/'agendas'/(arm+'_'+tag+'.json.gz'));agendas[(arm,tag)]=q
            ck(not q['pending']and not q['owner_protocols'],'empty owner/native agenda '+arm+' '+tag)
            fields(q['summary']['RAW_sha256']);fields(q['summary']['clocks_sha256'])
    comparisons=[]
    for tag in tags:
        a=agendas[('real',tag)];ar=fields(a['summary']['RAW_sha256']);ac=fields(a['summary']['clocks_sha256'])
        for arm in labels[1:]:
            b=agendas[(arm,tag)];br=fields(b['summary']['RAW_sha256']);bc=fields(b['summary']['clocks_sha256'])
            dd=[i for i,(x,y)in enumerate(zip(ar,br))if x!=y];cc=[i for i,(x,y)in enumerate(zip(ac,bc))if x!=y]
            ck(dd==([]if tag=='62525_COMMON'else[(14*67+14)*67+15]),'full RAW difference confined to A '+tag+' '+arm)
            ck(cc==[],'full clocks identical '+tag+' '+arm)
            ck(a['channels']==b['channels']and a['owner_interfaces']==b['owner_interfaces'],'same physical interfaces '+tag+' '+arm)
            comparisons.append({'tag':tag,'other':arm,'RAW_different':len(dd),'clocks_different':len(cc),'pending_equal':a['pending']==b['pending'],'receipts_equal':a['receipts']==b['receipts']})
    original=read(p/'COMPARACIONES_COMPLETAS.json.gz')['62564_POST']['original_vs_real']
    ck(original['RAW_different_sites']==0 and original['clock_different_sites']==0 and original['receipts_equal'],'real technical reproduction matches original physical fields and receipts')
    result={'classification':'Archived exact recalc, no native physics','new_ticks':0,'arms':summaries,'comparisons':comparisons,'decoded_phase_observations':frames,
      'checks':len(checks),'failures':sum(not x['ok']for x in checks),'scope':'One retrospective prefix, four new diagnostic forks. Not independent learners, new capacity, general threshold stability, content erasure or a unique proof of the downstream support collision.'}
    b=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2).encode()
    if args.out:args.out.write_bytes(b)
    else:print(b.decode())

if __name__=='__main__':main()
