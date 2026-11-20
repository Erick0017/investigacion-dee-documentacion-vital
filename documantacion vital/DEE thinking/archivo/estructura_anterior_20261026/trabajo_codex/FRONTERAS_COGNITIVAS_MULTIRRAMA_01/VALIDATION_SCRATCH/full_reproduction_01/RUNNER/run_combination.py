"""The one frozen L04/L05 crossing; all relations created by native exposure."""
import json
from pathlib import Path
import sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from observations import dump,sha
from run_multibranch import Case,append_ledger,utc
from branches import composition

def main():
    root=Path(sys.argv[1]);cfg=json.loads((root/'CAMPAIGN_CONFIG.json').read_text(encoding='utf-8'))
    for arm in ('full','omit1','omit2','link_cut','receiver_offpath_sham'):
        name='L04_PLUS_L05_'+arm;directory=root/'COMBINATIONS'/name
        if (directory/'MEASUREMENTS.json').exists():
            m=json.loads((directory/'MEASUREMENTS.json').read_text(encoding='utf-8'))
            assert all(sha(root/p['path'])==p['sha256'] for p in m['checkpoints'])
            print('SKIP_VERIFIED',name);continue
        s={'branch':'C_L04_L05','case':name,'kind':'composition','combination':True,
           'role':'treatment' if arm=='full' else 'control','level':1,'configuration':0,
           'spec':{'arm':'full' if arm=='receiver_offpath_sham' else arm,'query':23,'horizon':20}}
        if arm=='receiver_offpath_sham':s['spec']['receiver_shift']=(0,0,5)
        append_ledger(root,{'case':name,'status':'RUNNING','spec':s,'frozen_combination':cfg['combinations'][0]})
        ctx=Case(root,s);timer=time.perf_counter();r=ctx.finish(composition(ctx,s['spec']))
        append_ledger(root,{'case':name,'status':'MEASURED','elapsed_seconds':time.perf_counter()-timer,
                            'result_sha256':sha(directory/'MEASUREMENTS.json')})
        print('MEASURED',name,'response',r['second_response']['s_reg'],r['second_response']['direction'],flush=True)

if __name__=='__main__':main()
