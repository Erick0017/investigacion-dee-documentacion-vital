"""Pure transport serialization. Caller supplies the ACTUAL backend decision.

No policy, arithmetic, DEE import, network or process. Does not authenticate that
a supplied decision is Native; the backend receipt and outer root ledger do.
"""
import argparse, json, re
from pathlib import Path
PROTOCOL='DEE.RBX.Connector.R01'
SOURCES={'DEE_NATIVE','PROGRAMMED','CONVENTIONAL_AI','MCP_TECHNICAL_CONTROL'}
ACTIONS={'ASK_STATION','SKIP_STATION','SAFE_WAIT','EXIT_0','EXIT_1'}
def identifier(value):
    if not isinstance(value,str)or not re.fullmatch(r'[A-Za-z0-9_-]{1,96}',value):raise ValueError('Bounded identity required')
    return value
def observation(value):
    if not isinstance(value,dict)or value.get('protocol')!=PROTOCOL:raise ValueError('Observation protocol')
    for key in('sessionId','observationId'):identifier(value[key])
    parts=value['namespace'].split('/')
    if len(parts)!=3:raise ValueError('Experience/scene/entity namespace required')
    for part in parts:identifier(part)
    if type(value.get('seq'))is not int or value['seq']<1:raise ValueError('Actual observation seq')
    if value.get('phase')not in('QUERY_CHOICE','ROUTE_CHOICE'):raise ValueError('Phase')
    if not isinstance(value.get('sensors'),dict):raise ValueError('Local sensors required')
    return value
def action_envelope(observed,decision,source_kind):
    observation(observed)
    if source_kind not in SOURCES:raise ValueError('Declared actual backend source')
    if not isinstance(decision,dict)or not isinstance(decision.get('action'),dict):raise ValueError('Actual completed decision required')
    if decision['action'].get('name')not in ACTIONS:raise ValueError('Unsupported actual action; no fallback')
    return dict(protocol=PROTOCOL,namespace=observed['namespace'],sessionId=observed['sessionId'],
        observationId=observed['observationId'],seq=observed['seq'],actionId=identifier(decision['actionId']),
        operationId=identifier(decision['operationId']),action=decision['action'],sourceKind=source_kind)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--observation',type=Path,required=True)
    p.add_argument('--decision',type=Path);p.add_argument('--source-kind',choices=sorted(SOURCES));p.add_argument('--output',type=Path)
    a=p.parse_args();v=observation(read(a.observation))
    if a.decision:
        if not a.source_kind or not a.output:raise ValueError('Explicit source-kind and fresh output required')
        v=action_envelope(v,read(a.decision),a.source_kind)
        with a.output.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(v,ensure_ascii=False,indent=2))
