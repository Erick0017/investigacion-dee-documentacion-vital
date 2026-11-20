"""Pure fake-world tests only; no DEE/Native import or original-file writes."""
from pathlib import Path
from types import SimpleNamespace,ModuleType
import ast,hashlib,importlib.util,json,sys,uuid

HERE=Path(__file__).resolve().parent
def load(n):
    p=HERE/(n+'.py');s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    out=HERE.parent/'control'/('PRUEBAS_INSTRUMENTO_FAKE_'+uuid.uuid4().hex[:8]);out.mkdir()
    c=load('observador_global_PI05_R01');plugin=load('pi05_transito_causal_R01');future=load('pi05_yoke_futuros_R01')
    class Runtime:
        dimension=2;current_tick=0;snapshot_metadata_entries=[]
        def raw_copy(self):return [0,3+self.current_tick,0,0,0,0,0,0]
        def clock_copy(self):return [self.current_tick]*8
    class Adapter:
        def __init__(self):self.world=SimpleNamespace(runtime=Runtime());self.calls=[]
        @property
        def tick(self):return self.world.runtime.current_tick
        def run_until(self,t):self.calls.append(t);self.world.runtime.current_tick=t;return {'fake':t}
    a=Adapter();rec=c.GlobalRecorder(out/'frames',N=2,ticks=[0,1,2,7],anchor_ticks={0,7},provenance={'scope':'FAKE ONLY'})
    w=c.CapturingAdapter(a,ticks=[0,1,2,7],recorder=rec);w.run_until(2);w.run_until(7);rec.close()
    v=c.verify_recording(out/'frames');frames=list(c.iter_frames(out/'frames'))
    assert v['frames_reconstructed']==4 and [x['tick']for x in frames]==[0,1,2,7]
    assert frames[-1]['raw_bytes']==c.uint64_bytes(a.world.runtime.raw_copy())
    assert len(frames[0]['raw_bytes'])==64 and a.calls==[1,2,7]
    b=Adapter();b.run_until(7)
    assert b.world.runtime.raw_copy()==a.world.runtime.raw_copy()and b.world.runtime.clock_copy()==a.world.runtime.clock_copy()
    rejected=0
    for row in({'modo':plugin.FIPLUS,'izquierda':14,'derecha':3,'captura':'global','expected':1},
                {'modo':plugin.FIPLUS,'izquierda':21,'derecha':3,'captura':'global'},
                {'modo':plugin.WAIT,'ticks':20001},{'modo':plugin.EXTEND,'failed':False}):
        try:plugin.validate_literal(row)
        except ValueError:rejected+=1
    assert rejected==4
    try:c.GlobalRecorder(out/'invalid',N=2,ticks=[0,1],anchor_ticks={1},provenance={})
    except ValueError:pass
    else:raise AssertionError('Implicit first anchor allowed')
    # Test the extension guard using a stub JSON codec, NOT dee_thinking.
    fake=ModuleType('dee_thinking.persistence');fake.decode_metadata=json.loads;fake.encode_metadata=json.dumps
    parent=ModuleType('dee_thinking');parent.persistence=fake
    assert 'dee_thinking'not in sys.modules
    sys.modules['dee_thinking']=parent;sys.modules['dee_thinking.persistence']=fake
    try:
        x={'slots':[{'ordinal':20,'source_ordinal':20,'failed':False,'calendar':{'q':1}},
                    {'ordinal':21,'source_ordinal':21,'failed':False,'calendar':{'q':2}}]}
        future._load_protocol=lambda:(x,'fixed_prospective_hash')
        m={'arm':'yoked','ordinal':20,'plan':{'plan':{'slots':list(range(20))}}}
        e={'version':future.VERSION,'protocol_sha256':'fixed_prospective_hash','slots':x['slots'],
           'old_plan_sha256':future._sha(future._canonical(m['plan'])),'prepared_ordinal':20}
        f=Adapter();f.world.runtime.snapshot_metadata_entries=[(future.KEY,json.dumps(e))]
        old=future._canonical(m['plan'])
        assert future.replay_signal(f,m,{'q':1})is False and future._canonical(m['plan'])==old
        try:future.replay_signal(f,m,{'q':2})
        except ValueError:pass
        else:raise AssertionError('Retimed future permitted')
        m['ordinal']=22
        try:future.validate_future(f,m)
        except ValueError:pass
        else:raise AssertionError('Exhausted future permitted')
    finally:del sys.modules['dee_thinking.persistence'];del sys.modules['dee_thinking']
    for p in HERE.glob('*PI05*.py'):ast.parse(p.read_text('utf8'),filename=str(p))
    result={'schema':'DEE.PI05.pure_instrument_tests.v1','scope':'Fake2^3 arrays/JSON stubs only, NOT Native passivity or scientific result',
            'Native_executed':False,'Native_ticks':0,'fake_frames_losslessly_reconstructed':4,'all_zero_sites_retained':True,
            'readonly_modes_import_real_DEE':False,'request_guards_rejected':rejected,
            'first_anchor_explicit':True,'old20_plan_unchanged_in_fake_future_test':True,'future_calendar_and_exhaustion_guards':True,
            'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in HERE.glob('*PI05*.py')},'output':str(out)}
    (out/'RESULTADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
