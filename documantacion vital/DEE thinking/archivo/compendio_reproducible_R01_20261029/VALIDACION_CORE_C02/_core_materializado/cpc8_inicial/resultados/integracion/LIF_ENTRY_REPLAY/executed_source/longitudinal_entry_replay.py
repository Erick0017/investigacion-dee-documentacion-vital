"""Technical replay only: exact P11 inputs, added passive admission views.

No new sample, hypothesis, port, rescue, state edit or current consequence.
The original measurements are read only after the805 trajectory finishes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    config_path=ROOT/'configuraciones/integracion/LONGITUDINAL_690_FROZEN.json';config=json.loads(config_path.read_text(encoding='utf8'))
    parent=ROOT/config['parent_snapshot']
    if sha(parent)!=config['parent_sha256']:raise AssertionError('Parent identity changed')
    a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic();source=a.out/'executed_source'
    shutil.copytree(ROOT/config['parent_source'],source/'src');shutil.copyfile(__file__,source/'longitudinal_entry_replay.py')
    sys.path.insert(0,str(source/'src'))
    from dee_thinking import _native as native
    from dee_thinking.consolidated import exact_observation
    from comunicacion.social_channel import SocialSession
    from integracion.shared_world import physical,move
    s=SocialSession.load(parent);entry=physical(s.world)
    entries=[{'port':'event.A','payload':3,'tick':786,'origin':'NEW_CURRENT_ORDER_EVENT'},
        {'port':'event.B','payload':3,'tick':787,'origin':'NEW_CURRENT_ORDER_EVENT'},
        {'port':'order.read','payload':7,'tick':788,'kind':'probe','origin':'EXPLICIT_EXTERNAL_ORDER_QUERY'},
        {'port':'U.right.signal','payload':5,'tick':786,'origin':'NEW_OPAQUE_RIGHT_CUE'},
        {'port':'U.right.event.minus','payload':11,'tick':786,'origin':'NEW_CURRENT_RIGHT_DIRECTIONAL_EVENT'},
        {'port':'need.actual.left.-1','payload':17,'tick':797,'origin':'CURRENT_SENSOR_REPORT_FIXED_CODEC'},
        {'port':'need.actual.right.-1','payload':17,'tick':797,'origin':'CURRENT_SENSOR_REPORT_FIXED_CODEC'}]
    request_start=len(s.receipts());s.stimulate(entries);s.query_lower(range(65),1048,9)
    channels={p.name:p.channel for p in s.world.interfaces};frames=[]
    def at(q):return exact_observation(s.world.runtime.observe(native.Coordinate(*q)))
    for tick in(785,786,787,788,789,790,791,800,801,804,805):
        s.run_until(tick);ports=[]
        for name in('event.A','event.B','order.read'):
            c=channels[name];q=c.injection_site;center=[q.x,q.y,q.z];gate=native.inspect_write_gate(s.world.runtime,q,False)
            ports.append({'port':name,'center':at(center),'Moore27':[at(move(center,(dx,dy,dz),1,131))for dx in(-1,0,1)for dy in(-1,0,1)for dz in(-1,0,1)],
                'kernel_gate_passive':{'absolute_tick':int(gate.absolute_tick),'local_clock':str(gate.local_clock),'center_available':gate.center_available,
                    'n_active':gate.n_active,'direction_sum':[gate.direction_sum.dx,gate.direction_sum.dy,gate.direction_sum.dz],
                    'tetra_pattern':gate.tetra_pattern,'hadron':gate.hadron,'rule_value':gate.rule_value,'survives_material_rule':gate.survives_material_rule,
                    'semantic_protected':gate.semantic_protected,'write_protected':gate.write_protected,'k':gate.k,'period':gate.period,
                    'phase_remainder':None if gate.phase_remainder is None else str(gate.phase_remainder),'ordinary_increment_condition':gate.ordinary_increment_condition,
                    'branch':gate.branch,'demux_status':gate.demux_status,
                    'scope':'Passive kernel write-gate state, not an instruction to open a gate. Host interface RAW-empty admission is a separate contract.'}})
        frames.append({'tick':tick,'entry_ports':ports,'observation':s.observe()})
    # Evaluation after the complete trajectory, never injected into it.
    pilot_path=ROOT/'resultados/integracion/LIF_P11_NEW_AB/MEASUREMENTS.json';pilot=json.loads(pilot_path.read_text(encoding='utf8'))
    target=next(x['physical']for x in pilot['snapshots']if x['tick']==805)
    def past(rows):return[x for x in rows if x['receipt']['requested_tick']<=805]
    comparison={'initial_RAW_clocks_tick_equal':entry==pilot['parent']['physical'],'final805_RAW_clocks_tick_equal':physical(s.world)==target,
        'past_receipts_and_call_ticks_equal':past(s.receipts())==past(pilot['requests'])}
    if not all(comparison.values()):raise AssertionError('Passive replay differs: '+json.dumps(comparison))
    result={'schema':'CPC8.integration.longitudinal_entry_replay.v1','technical_status':'PASS','preparations':0,'scientific_replicates_added':0,
        'technical_replays':1,'parent_snapshot':config['parent_snapshot'],'parent_sha256':sha(parent),'reference':str(pilot_path.relative_to(ROOT)),
        'reference_sha256':sha(pilot_path),'configuration_sha256':sha(config_path),'executed_source':{p.relative_to(source).as_posix():sha(p)for p in source.rglob('*.py')},
        'frames':frames,'new_requests':s.receipts()[request_start:],'comparisons':comparison,'elapsed_seconds':time.monotonic()-started,
        'scope':'Extra passive observables of an identical pilot trajectory. No new independent preparation or positive scientific reserve.'}
    target=a.out/'MEASUREMENTS.json';temporary=target.with_name(target.name+'.pending.'+str(os.getpid()));temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temporary,target)
    print(json.dumps({'technical_status':'PASS','comparisons':comparison,'elapsed_seconds':result['elapsed_seconds']}),flush=True)


if __name__=='__main__':main()
