"""Preregister finite refinements/reserves; instrumental recalc from real receipts."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as dt
from observations import dump,sha
from run_multibranch import append_ledger,utc

def main():
    root=Path(sys.argv[1]);p=root/'CAMPAIGN_CONFIG.json';cfg=json.loads(p.read_text(encoding='utf-8'))
    if cfg.get('followup_frozen_utc'):print('FOLLOWUP_ALREADY_FROZEN');return
    original_hash=sha(p)
    # Correct a case-sensitive enum accounting defect. Evolution/data arrays unaffected.
    for file in (root/'BRANCHES').glob('*/*/MEASUREMENTS.json'):
        m=json.loads(file.read_text(encoding='utf-8'));changed=False
        for key in ('host_writes_after_t0','host_writes_after_t0_main'):
            old=m.get(key)
            if not isinstance(old,dict):continue
            cp=next((x for x in reversed(m['checkpoints']) if x['label']=='FINAL'),None)
            if cp is None:continue
            rt=dt.Runtime.load_snapshot(str(root/cp['path']));rs=rt.receipts
            new={'scheduled_calls_recorded_separately':True,
                 'applied_event_batches':sum(r.status==dt.EventStatus.APPLIED for r in rs),
                 'applied_physical_sites':sum(len(r.channels) for r in rs if r.status==dt.EventStatus.APPLIED),
                 'rejected_events':sum(str(r.status).lower().startswith('rejected') for r in rs)}
            if new!=old:
                m.setdefault('instrumental_corrections',[]).append({'field':key,'previous':old,'reason':'native EventStatus string is lowercase; recount uses enum equality and checkpoint receipts','new':new})
                m[key]=new;changed=True
        if changed:
            before=sha(file);dump(file,m);append_ledger(root,{'case':m['branch']+'/'+m['case_id'],'status':'MEASURED',
                          'instrumental_correction':'receipt count only; no rerun','previous_result_sha256':before,'result_sha256':sha(file)})
    for s in cfg['cases']:
        if s['case']=='unpaired' and s['branch'] in ('L01','L04'):
            s['skip_reason']='catalog boundary-0 contract rejected at_tick=1; original error preserved; explicit Runtime research-timing replacement follows'
    extra=[]
    def case(b,name,kind,spec,role='control',level=0,configuration=1):
        extra.append({'branch':b,'case':name,'kind':kind,'spec':spec,'role':role,'level':level,
                      'configuration':configuration,'preregistered_utc':utc()})
    for b in ('L01','L04'):
        case(b,'unpaired_runtime_contract','association',{'arm':'unpaired','research_timing':True,'events':[7,11] if b=='L01' else [7,15]},'control')
    # A second signal encoding removes an incidental load difference between S0/S1.
    for arm in ('paired','none','signal_only','event_only','unpaired','inverted'):
        spec={'arm':'paired' if arm=='inverted' else arm,'cues':[5,5],'events':[11,7] if arm=='inverted' else [7,11],
              'query':[5,5],'research_timing':arm=='unpaired'}
        case('L01','balanced_'+arm,'association',spec,'treatment' if arm=='paired' else 'control')
    cfg['cases']+=extra;cfg['followup_frozen_utc']=utc();cfg['followup_parent_config_sha256']=original_hash
    cfg['technical_hotfixes']=[{'utc':utc(),'issue':'README extraction ambiguity','fix':'prefer exact ZIP member'},
                              {'utc':utc(),'issue':'catalog unpaired temporal rejection','fix':'new case using explicit Runtime research timing; preserved rejected case'},
                              {'utc':utc(),'issue':'lowercase EventStatus accounting','fix':'enum equality; counts recalculated from saved receipts, physical arrays untouched'}]
    dump(p,cfg);print('FROZEN',len(extra),'additional discovery cases')

if __name__=='__main__':main()
