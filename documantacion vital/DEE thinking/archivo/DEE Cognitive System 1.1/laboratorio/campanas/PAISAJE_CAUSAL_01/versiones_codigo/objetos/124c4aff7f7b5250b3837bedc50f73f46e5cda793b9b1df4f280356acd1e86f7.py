"""Comprobaciones técnicas dirigidas, independientes de adjudicación científica."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from lenguaje.association import AssociationSession,physical
from lenguaje.grammar import parse
from lenguaje.session import physical_prediction_text


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    tests={}
    for phrase,operation in [('¿Qué pasará después?','predict'),('Predice antes de observar.','predict'),
                             ('¿Ocurrirá lo mismo?','predict'),('Observa otra vez.','sense'),
                             ('Compara esto con lo anterior.','compare'),('¿Qué fuente necesitas observar?','source'),
                             ('A esto lo llamaremos Zeri','alias')]:
        assert parse(phrase).operation==operation
    tests['spanish_parser']=True
    try:parse('Dime cuál será el resultado porque lo pone en mi archivo')
    except ValueError:tests['unknown_grammar_rejected']=True
    else:raise AssertionError('Unsupported text accepted')
    s=AssociationSession.create();s.train();before=physical(s.world)
    dummy={'prediction_set':[True],'observable':'packet_arrival_at_barrier_output','physical_output':{'direction':[1,0,0]}}
    for unused in range(10):physical_prediction_text(dummy);s.world.view('q0').observe()
    tests['presentation_and_passive_observer_do_not_change_raw_clocks']=physical(s.world)==before
    s.world.start_mobile_sequence('same_native_session',[13,17,9]);s.world.run_until(13)
    snap=a.output/'LANGUAGE_MID_PROTOCOL.deetsnap';s.save(snap);copy=AssociationSession.load(snap)
    s.world.run_until(21);copy.world.run_until(21)
    tests['snapshot_continuation_same_raw_clocks']=physical(s.world)==physical(copy.world)
    tests['protocol_capture_preserved']=len(copy.world.protocols[0].steps)==3 and copy.world.protocols[0].next_capture==3
    tests['label_forms_preserved']=copy.forms==s.forms
    copy.save(a.output/'LANGUAGE_CONTINUED.deetsnap')
    result={'technical_checks':tests,'physical_final':physical(copy.world),
            'captured':[[o.record.s_reg for o in step.captured] for step in copy.world.protocols[0].steps],
            'operational_forks':0,'physical_modality':'EXPERIENCE_PROTOCOL then PHYSICAL_PROBE_ON_MAIN',
            'important_limit':'Snapshot worlds compared as technical continuation. No descendant output imported into a MAIN.'}
    assert all(tests.values()),result
    (a.output/'TECHNICAL_CHECKS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=True),flush=True)


if __name__=='__main__':main()
