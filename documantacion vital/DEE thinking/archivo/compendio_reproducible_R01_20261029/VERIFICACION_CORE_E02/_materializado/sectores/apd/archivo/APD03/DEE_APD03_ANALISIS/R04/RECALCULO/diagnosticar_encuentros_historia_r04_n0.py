"""Extract fixed hub/source windows from already recorded R04 ROI, no ticks."""
import argparse,gzip,hashlib,json
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fields(raw):
    def signed(shift):
        value=(raw>>shift)&15;return value-16 if value&8 else value
    return {'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,'semantic':(raw>>60)&15,
        'direction':[signed(x)for x in(48,52,56)]}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);args=parser.parse_args()
    result=json.loads((args.evidence/'RESULTADOS.json').read_bytes());rows=[]
    for branch in result['results']:
        if 'failure'in branch or not branch['arm']['recording']:continue
        folder=args.evidence/Path(branch['primary']).parent
        primary=json.loads(gzip.decompress((folder/'PRIMARIO.json.gz').read_bytes()))
        requested={primary['A_lesson']['input_tick']+3,primary['A_lesson']['teacher_tick']+3,
            primary['B_lesson']['input_tick']+3};windows=[];occupied=[]
        with gzip.open(folder/'ROI_TICK_A_TICK.jsonl.gz','rb')as stream:
            for line in stream:
                frame=json.loads(line);tick=frame['tick'];sites={tuple(r['site']):r for r in frame['sites']}
                if int(sites[(47,7,47)]['raw']):occupied.append({'tick':tick,**sites[(47,7,47)],
                    'fields':fields(int(sites[(47,7,47)]['raw']))})
                if tick in requested:
                    for site,label in(((47,7,47),'shared_K'),((44,7,47),'hub_A'),((47,4,47),'hub_B')):
                        item=sites[site];windows.append({'tick':tick,'label':label,**item,'fields':fields(int(item['raw']))})
        hubchecks=[]
        for name in('A_lesson','B_lesson'):
            episode=primary[name];hub=episode['hub'];matching=[r for r in windows if r['tick']==episode['end_tick']and r['site']==hub['site']]
            same=len(matching)==1 and matching[0]['raw']==str(hub['raw'])and matching[0]['clock']==str(hub['clock'])
            if not same:raise ValueError('Passive/source hub differs')
            hubchecks.append({'episode':name,'tick':episode['end_tick'],'hub':hub,'passive_equals_primary':same})
        rows.append({'index':branch['index'],'arm':branch['arm'],'primary_sha256':sha(folder/'PRIMARIO.json.gz'),
            'trace_sha256':sha(folder/'ROI_TICK_A_TICK.jsonl.gz'),'fixed_windows':windows,'hub_checks':hubchecks,
            'all_nonzero_K_frames':occupied,'K_nonzero_count':len(occupied),
            'K_gaps_between_nonzero_frames':[b['tick']-a['tick']for a,b in zip(occupied,occupied[1:])]})
    body={'schema':'DEE.APD03.history_R04.fixed_source_hub_extraction.N0','arms':rows,'new_native_ticks':0,
        'scope':'Fixed known K/hub positions in recorded ROI. No reconstruction of unobserved trajectory or single-parent lineage.',
        'not_a_return_proof':'Repeated source class at67tick spacing is not by itself proof that the same carrier crossed periodic boundaries and returned.'}
    with args.out.open('x',encoding='utf8')as stream:
        json.dump(body,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'out':str(args.out),'sha256':sha(args.out),'arms':[{'index':r['index'],'K_nonzero':r['K_nonzero_count'],
        'gaps':r['K_gaps_between_nonzero_frames'],'hubs':r['hub_checks']}for r in rows]}))


if __name__=='__main__':main()
