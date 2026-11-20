"""Passive paired-history comparison at the first configured post-training Wslot.

Reads only supplied frozen JSON/JSONL, never DEE. No best-case search.
"""
from pathlib import Path
import argparse,datetime,gzip,hashlib,json,sys
def sha(b):return hashlib.sha256(b).hexdigest()
def data(path):
    b=Path(path).read_bytes();return gzip.decompress(b)if Path(path).suffix=='.gz'else b
def read(summary,journal):
    s=json.loads(data(summary).decode('utf-8-sig'));n=s['requests'][-1]['result']['result']['rows'][0]['habitat']['log_count'];b=b''.join(data(journal).splitlines(keepends=True)[:n])
    if sha(b)!=s['journal_sha256']:raise ValueError('Historical journal prefix identity')
    return s,[json.loads(x)for x in b.decode('utf-8').splitlines()]
def find(events,kind,episode):return next(x for x in events if x['kind']==kind and x.get('episode')==episode)
def run(main_summary,main_journal,control_summary,control_journal):
    ms,m=read(main_summary,main_journal);cs,c=read(control_summary,control_journal);errors=[]
    prefixes=[]
    for episode in (0,2,3,5):
        a=find(m,'FI_FRAME_FINISHED',episode)['trial'];b=find(c,'FI_FRAME_FINISHED',episode)['trial']
        prefixes.append({'episode':episode,'requests_176_exact_equal':a['requests']==b['requests'],'recorded_FI_frames_exact_equal':a['frames']==b['frames'],'early_RAW_clock_observation_exact_equal':a['early_observation']==b['early_observation']})
    paired=find(m,'OPPORTUNITY_COMPLETED',5);control=find(c,'OPPORTUNITY_COMPLETED',5)
    W=next(x for x in paired['warning_receipts']if x['channel']=='PI02.R03.warning');q=W['nominal_arrival_tick']
    hmain=next(x['H']for x in m if x['kind']=='FIXED_PORT_OBSERVATIONS'and x['tick']==q)
    hcontrol=next(x['H']for x in c if x['kind']=='FIXED_PORT_OBSERVATIONS'and x['tick']==q)
    close5=next(x for x in m if x['kind']=='DEVICE_COMMAND'and x['origin']=='learned_warning'and x['tick']==q)
    prior_main=[x for x in m if x['kind']=='DEVICE_COMMAND'and x['tick']<q][-1]
    prior_control=[x for x in c if x['kind']=='DEVICE_COMMAND'and x['tick']<q][-1]
    wm=find(m,'FI_FRAME_FINISHED',6);wc=find(c,'FI_FRAME_FINISHED',6)
    next_source=wm['gate']['source_tick']
    refreshes_before_next_gate=[x for x in m if x['kind']=='DEVICE_COMMAND'and x['origin']=='learned_warning'and q<=x['tick']<=wm['gate']['at_tick']]
    same_warning=paired['warning_receipts']==control['warning_receipts']
    if not same_warning:errors.append('First common W/G admission differed')
    if not all(all(x[k]for k in x if k!='episode')for x in prefixes):errors.append('Observed FI prefix differs before first W response')
    return {'schema':'PI02.R04.first_common_warning.paired_control.v1','calculated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_ticks':0,'DEE_imports':0,
            'main':ms['life'],'control':cs['life'],'fixed_question':'First configured post-training warning slot episode5, not a selected successful case',
            'source_files':[{'role':role,'file':Path(p).name,'decoded_sha256':sha(data(p))}for role,p in zip(('main_summary','main_journal','control_summary','control_journal'),(main_summary,main_journal,control_summary,control_journal))],
            'prior_observed_FI_prefix':prefixes,
            'first_warning':{'episode':5,'q':q,'W_G_receipts_exact_equal':same_warning,'admitted_input_receipts':paired['warning_receipts'],'main_H':hmain,'control_H':hcontrol,'main_close_device':close5,
                             'control_CLOSE_at_q_recorded':any(x['kind']=='LEARNED_WARNING_SIGNATURE'and x['tick']==q for x in c),
                             'control_close_device_at_q':[x for x in c if x['kind']=='DEVICE_COMMAND'and x['origin']=='learned_warning'and x['tick']==q],
                             'prior_device_main':prior_main,'prior_device_control':prior_control,
                             'same_useful_current_work_and_gate':paired['effect']==control['effect'],
                             'scope':('Same paired training; formed warning-device actuation cut in control. Same current W/G admissions, phase and recorded FI prefix. Compare the formed signal separately from its applied effect.'if cs['arm']=='warning_cut'else'Different learned physical histories; same current W/G admissions, phase and recorded FI prefix. Not identical global worlds.')},
            'next_work':{'episode':6,'source_tick':next_source,'main_gate':wm['gate'],'control_gate':wc['gate'],'main_raw0_receipt':wm['trial']['requests'][0]['receipt'],'control_raw0_receipt':wc['trial']['requests'][0]['receipt'],
                         'main_early_observation':wm['trial']['early_observation'],'control_early_observation':wc['trial']['early_observation'],
                         'main_effect':find(m,'OPPORTUNITY_COMPLETED',6)['effect'],'control_effect':find(c,'OPPORTUNITY_COMPLETED',6)['effect'],
                         'old_device_TTL_before_next_input':prior_main['guard_until']<next_source,
                         'warning_device_refreshes_before_gate':refreshes_before_next_gate,
                         'causal_limit':'Both CLOSE5 and CLOSE6 precede this input. These records do not establish necessity of CLOSE5 alone. A cut of all formed warning actuations tests the sequence/channel, not a single necessary refresh.'},
            'inconsistencies':errors,
            'interpretation_scope':'Observed history->signature->device-state/TTL->input-admission->FI-action chain. This is the first predefined common warning comparison; aggregate outcomes are analyzed separately, including negative reversed-device and valence-omission results.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--main-summary',type=Path,required=True);p.add_argument('--main-journal',type=Path,required=True);p.add_argument('--control-summary',type=Path,required=True);p.add_argument('--control-journal',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--strict',action='store_true');a=p.parse_args();r=run(a.main_summary,a.main_journal,a.control_summary,a.control_journal);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'first_warning_q':r['first_warning']['q'],'W_G_receipts_equal':r['first_warning']['W_G_receipts_exact_equal'],'prior_FI_prefix':r['prior_observed_FI_prefix'],'inconsistencies':r['inconsistencies']},ensure_ascii=False,indent=2));return 2 if a.strict and r['inconsistencies']else 0
if __name__=='__main__':sys.exit(main())
