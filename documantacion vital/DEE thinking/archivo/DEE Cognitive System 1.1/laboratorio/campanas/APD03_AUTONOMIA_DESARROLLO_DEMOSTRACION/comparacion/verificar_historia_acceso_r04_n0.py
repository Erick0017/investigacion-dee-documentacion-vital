"""Syntax, static ROI, finite curriculum and identical-dose protocol fixtures."""
import argparse,ast,hashlib,importlib.util,json,types
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True,type=Path);args=parser.parse_args()
    here=Path(__file__).resolve().parent;paths=[here/'protocolo_historia_acceso_lexico_apd03_r04.py',here/'ejecutar_historia_acceso_lexico_apd03_r04.py']
    sources=[]
    for path in paths:
        data=path.read_bytes();ast.parse(data);sources.append({'file':path.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    spec=importlib.util.spec_from_file_location('history_n0',paths[0]);p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
    plan=p.plan();coords=[tuple(r['site'])for r in plan['ROI']]
    assert len(coords)==len(set(coords))and all(all(0<=c<67 for c in point)for point in coords)
    assert len([r for r in plan['ROI']if any(k.startswith('fixed32')for k in r['roles'])])==32
    class Fake:
        def __init__(self):self.tick=549343
    events=[]
    def query(a,form,detailed=False):
        a.tick+=67;return {'form':form,'mock_only':True,'reader':{'formed_native_command':None}}
    def teach(a,form,sign,mode):
        a.tick+=67;return {'form':form,'sign':sign,'mode':mode,'mock_only':True,
            'requests':[{'value':5},{'value':11}]}
    original=p.lexical_module;p.lexical_module=lambda:types.SimpleNamespace(get=lambda a:{},query=query,teach=teach)
    for arm in plan['arms']:
        rows=[];fake=Fake();result=p.run_arm(fake,a_mode=arm['A_mode'],b_sign=arm['B_sign'],
            identity={'kind':'N0_fake'},on_event=lambda kind,value:rows.append({'kind':kind,'value':value}))
        assert len(rows)==15 and result['end_tick']-result['start_tick']==1005
        assert [r['value']for r in result['A_lesson']['requests']]==[5,11]
        assert [r['value']for r in result['B_lesson']['requests']]==[5,11]
        events.append({'arm':arm,'mock_events':len(rows),'mock_ticks':1005,
            'A_mode':result['A_lesson']['mode'],'A_nominal_dose':[5,11],'B_nominal_dose':[5,11]})
    p.lexical_module=original
    result={'schema':'DEE.APD03.history_R04.N0_fixture','sources':sources,'arms':events,
        'roi_sites':len(coords),'fixed_reader_sites':32,'new_native_ticks':0,
        'scope':'Syntax/static geometry/fake curriculum only; not proof of actual admission, passivity or learning',
        'issues':0}
    with args.out.open('x',encoding='utf8')as stream:json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(result))


if __name__=='__main__':main()
