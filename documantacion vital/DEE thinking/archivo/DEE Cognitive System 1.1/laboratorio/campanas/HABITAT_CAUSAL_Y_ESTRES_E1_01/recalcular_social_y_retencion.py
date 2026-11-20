"""Recalculate existing habitat/social/control records without engine or ticks."""
from pathlib import Path
from collections import Counter
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
EV = ROOT/'evidencia/campanas/HABITAT_CAUSAL_Y_ESTRES_E1_01'


def read(name):
    p=EV/name
    return json.loads(p.read_text(encoding='utf8'))


def sha(name):
    return hashlib.sha256((EV/name).read_bytes()).hexdigest()


def valid(x, vector):
    return x['state']==1 and x['semantic']==1 and x['direction']==list(vector)


def qualify_axis(x):
    return x['state']==1 and x['semantic']==1 and x['direction'] in([1,0,0],[-1,0,0],[0,0,0])


def summarize():
    result={'schema':'DCS1.1.HABITAT.social_retention.static_recalculation.v1',
            'native_ticks_executed':0,'source_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'criteria':{'required_state':1,'required_semantic':1,
                        'social_form':'(0,signY,1) at admitted minus-X mobile reader; one matching form, not generic active material',
                        'B_source':'(+X or -X), not an active neutral preparation counted as a private contrast',
                        'E1_read':'(bank.sign,0,1) at hub',
                        'E1_use_and_delivery':'(bank.sign,1,1), derived from existing return geometry',
                        'state2_or3':'Not a qualified response under this contract even when active=true'},
            'social':[],'panels':[],'early':[],'sources':[]}
    for name in('MAIN_SOCIAL_18','SOCIAL_ABSENT_18','SOCIAL_CUT_20','SOCIAL_SHAM_21'):
        j=read(name+'.json');o=j['result']['operation'];entry={'case':name,'source':name+'.json',
            'initial':j['result']['initial'],'final':j['result']['final'],'mode':o['plan']['mode'],
            'trials':[],'interceptions':o['interceptions']}
        for trial in o['plan']['trials'][:2]:
            cs={c['stage']:c for c in o['captures']if c['trial']==trial['index']}
            b=cs['B_source_formed_before_cut']['B_center'];row={'trial':trial['index'],
                'private_value':trial['private_object_value'],'B_source':b,
                'B_qualified_polarity':valid(b,(1,0,0))or valid(b,(-1,0,0)),
                'E1':[]}
            for bank in o['plan']['E1_banks']:
                sign=bank['sign'];br={'bank':bank['id']}
                for stage,site,vector in(('E1_later_read','hub',(sign,0,1)),
                                          ('E1_current_use','use_site',(sign,1,1)),
                                          ('E1_delivery','delivery_site',(sign,1,1))):
                    c=cs[stage];x=next(x for x in c['E1']if x['bank']==bank['id'])[site]
                    br[stage]={'tick':c['tick'],'read':x,'qualified':valid(x,vector)}
                row['E1'].append(br)
            row['qualified_delivery_any_bank']=any(b['E1_delivery']['qualified']for b in row['E1'])
            entry['trials'].append(row)
        entry['counts']={'trials':len(entry['trials']),
                         'B_qualified_polarities':sum(t['B_qualified_polarity']for t in entry['trials']),
                         'E1_qualified_delivery':sum(t['qualified_delivery_any_bank']for t in entry['trials']),
                         'interceptor_receipt_statuses':dict(Counter(r['receipt']['status']for i in entry['interceptions']for r in i['requests'])),
                         'unsupported_interventions':sum(i['status'].startswith('UNSUPPORTED')for i in entry['interceptions'])}
        result['social'].append(entry);result['sources'].append({'path':name+'.json','sha256':sha(name+'.json')})
    for name in('BASELINE_01','MAIN_FINAL_PANEL_19'):
        j=read(name+'.json');r=j['result'];entry={'case':name,'initial':r['initial'],'final':r['final'],'frames':[]}
        for frame in r['frames']:
            if frame['kind']=='social':
                fs=[]
                for f in frame['forms']:
                    branches=[{'bank':b['id'],'read':b['read'],'qualified_form':valid(b['read'],(0,-1 if b['id']=='minus'else 1,1))}for b in f['branches']]
                    fs.append({'form':f['id'],'branches':branches,'qualified':any(b['qualified_form']for b in branches)})
                entry['frames'].append({'kind':'social','tick':frame['tick'],'forms':fs,'qualified':sum(x['qualified']for x in fs),'denominator':len(fs)})
            else:
                entry['frames'].append({'kind':frame['kind'],'tick':frame['tick'],'read':frame['read'],'qualified_axis':qualify_axis(frame['read'])})
        result['panels'].append(entry);result['sources'].append({'path':name+'.json','sha256':sha(name+'.json')})
    for name in('EARLY_SHOCK_REPRO_PRIMARY_05','EARLY_RECOVERY_22'):
        j=read(name+'.json');r=j['result'];rows=r['rows'];initial_tick=r['initial']['tick']
        result['early'].append({'case':name,'initial':r['initial'],'final':r['final'],
            'rows':[{'index':x['index'],'tick':x['read_tick'],'read':x['native_read'],'qualified':qualify_axis(x['native_read']),
                     'noise_requested':len(x['noise']),'stress_stopped':x['stress_stopped']}for x in rows],
            'qualified':sum(qualify_axis(x['native_read'])for x in rows),'denominator':len(rows),
            'new_receipts':dict(Counter(x['status']for x in j['receipts']if x['requested_tick']>initial_tick))})
        result['sources'].append({'path':name+'.json','sha256':sha(name+'.json')})
    omit=read('ORIGIN_OMIT_16/MEDICIONES.json');replay=read('ORIGIN_REPLAY_11/MEDICIONES.json')
    a=omit['result']['rows'];b=replay['result']['rows'];c=next(x for x in a[-1]['context']if x['site']==[49,36,35])
    result['origin_control']={'omitted_native_inputs':len(omit['omitted_inputs']),
                             'exogenous_deltas_equal_every_step':[x['exogenous_delta']==y['exogenous_delta']for x,y in zip(a,b)],
                             'omit_qualified':sum(qualify_axis(x['native_read'])for x in a),'replay_qualified':sum(qualify_axis(x['native_read'])for x in b),
                             'denominator_each':len(a),'reference_site_T5296_omit':c,
                             'reference_site_T5296_replay':next(x for x in b[-1]['context']if x['site']==[49,36,35]),
                             'scope':'All12 noise submissions omitted with identical RNG draws; actions and later environmental states may diverge. Does not isolate which individual noise input caused the late change.'}
    for p in('ORIGIN_OMIT_16/MEDICIONES.json','ORIGIN_REPLAY_11/MEDICIONES.json'):
        result['sources'].append({'path':p,'sha256':sha(p)})
    result['limitations']=['Four social arms share T7172 prefix, not four independent ontogenies.',
        'No_partner withholds current private-B inputs/readers; existing B body/history remains.',
        'First cut/sham both applied2/2 barriers. Second injection unsupported because first barriers persist; not an independent second cut.',
        'Full/sham second B polarity is valid before later deterioration, but E1 states2/3 do not establish second learned delivery.',
        'Early recovery after investigator stops new stress is not learned self-regulation.',
        'Baseline and final panel are material diagnostic continuations, not simultaneous passive surveys.',
        'No global erasure, consciousness, negotiation or autonomous P2/R2 conclusion follows.']
    return result


if __name__=='__main__':
    value=summarize();target=EV/'RESUMEN_SOCIAL_Y_RETENCION.json'
    if target.exists():raise FileExistsError('Keep previous static recalc intact')
    target.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'path':str(target),'sha256':sha(target.name),
                      'social':[(x['case'],x['counts'])for x in value['social']],
                      'panels':[(x['case'],[(f['kind'],f.get('qualified',f.get('qualified_axis')))for f in x['frames']])for x in value['panels']],
                      'early':[(x['case'],x['qualified'],x['denominator'])for x in value['early']],
                      'origin':value['origin_control']},ensure_ascii=False))
