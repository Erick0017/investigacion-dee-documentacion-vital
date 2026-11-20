#!/usr/bin/env python3
"""Preflight de modelo ambiental y fuentes. Sin imports Native, Roblox, HTTP o SQLite."""
import argparse,copy,hashlib,itertools,json,pathlib

def begin(ports,epoch):
    for row in ports.values():
        for v in row.values():
            if not v['available'] and epoch>=v['ready']:
                v.update(available=True,ready=None)
def signal(ports,station):
    a,b=ports[station][0]['available'],ports[station][1]['available']
    if a and b:return 1
    if a:return 0
    if b:return 2
    raise ValueError('both local ports unavailable before query')
def simulate(cfg,arm,choices):
    ports={s:{p:{'available':True,'ready':None}for p in (0,1)}for s in range(6)}
    station=cfg['startStation'];rows=[]
    for epoch,choice in enumerate(choices,1):
        begin(ports,epoch);sig=signal(ports,station)
        row={'epoch':epoch,'station':station,'signal':sig,'hypotheticalPaidDatum':sig+3*station,'choiceForStaticTraceOnly':choice}
        if choice!='WAIT':
            p=int(choice);token=ports[station][p];row['toll']=0 if token['available'] else 2
            if token['available'] and arm=='CONSUME_RECHARGE':token.update(available=False,ready=epoch+3)
            station=cfg['edges'][str(station)][str(p)]
        else:row['toll']=0
        row['nextStation']=station;rows.append(row)
    return rows

def run(directory,actor_source=None):
    cfg=json.loads((directory/'CONFIG_CANDIDATA_FOCAL.json').read_text(encoding='utf-8'))
    protocol=json.loads((directory/'PROTOCOLO_FOCAL.json').read_text(encoding='utf-8'))
    assert cfg['maxCyclesPerArm']==6 and cfg['rechargeEpochs']==3 and cfg['minimumPermissionStock']==18
    assert all(cfg['edges'][str(s)][str(p)]!=s for s in range(6)for p in (0,1))
    n=0
    for actions in itertools.product(('0','1','WAIT'),repeat=6):
        for arm in cfg['arms']:simulate(cfg,arm,actions)
        n+=1
    constant=simulate(cfg,'NONCONSUMING_CONTROL',('1',)*6)
    candidate=simulate(cfg,'CONSUME_RECHARGE',('1',)*6)
    differences=[a['epoch']for a,b in zip(candidate,constant)if a['hypotheticalPaidDatum']!=b['hypotheticalPaidDatum']]
    assert differences==[4,5]
    actual_source_verified=False
    if actor_source:
        raw=actor_source.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==protocol['sources']['effectiveActor']['sha256']
        text=raw.decode('utf-8')
        assert "return signal + 3*submitted_tag" in text and "if queried:" in text and "role_limits = {'main': 24, 'control': 6, 'load': 3, 'pilot': 3}" in text
        actual_source_verified=True
    return {'schema':'DEE.Focal.StaticPreflight.R01','kind':'STATIC_ENVIRONMENT_AND_ABI_ONLY_NOT_NATIVE_ADMISSION','nativeExecuted':False,'studioExecuted':False,'hypothetical':True,'allChoiceTracesChecked':n,'armsPerTrace':2,'bothPaidAtCurrentSample':False,'sourceVerified':actual_source_verified,'sameAll1StaticTrace':{'candidate':candidate,'control':constant,'differentHypotheticalPaidDatumEpochs':differences},'nativeExposure':'NOT_PROVED_NO_NATIVE_REQUESTS','materialReadiness':protocol['preflight']['materialReadiness'],'passedStaticChecks':True}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--actor-source',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path)
    a=p.parse_args();result=run(pathlib.Path(__file__).resolve().parent,a.actor_source);text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if a.output:
        with a.output.open('x',encoding='utf-8') as f:f.write(text)
    print(text)
if __name__=='__main__':main()
