"""AST-selected PI06 dispatch bodies with explicit FAKE imports, never Native."""
from pathlib import Path
import ast, hashlib, json
from types import SimpleNamespace

P=Path(__file__).resolve().parents[1]
CODE=P/'codigo/pi06_organizacion_R01.py'


def main():
    source=CODE.read_bytes(); tree=ast.parse(source.decode('utf8'))
    wanted={'_fiplus','_evolve','_counts','evolution_ticks'}
    selected=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in wanted]
    # The scientific bodies remain literal; replace only import statements by
    # explicit fake objects. This does NOT test the Native binary or admission.
    for n in selected:
        n.body=[x for x in n.body if not isinstance(x,(ast.Import,ast.ImportFrom))]
    class FakeWorld:
        def __init__(self):self.requests={};self.runtime=self;self.clock=1000
        def submit(self,name,payload,tick):
            assert tick>self.clock
            rid=len(self.requests)+800
            self.requests[rid]={'id':rid,'port':name,'payload':payload,'tick':tick,
                                'receipt':{'status':'scheduled'}}
            return SimpleNamespace(id=rid)
        def receipt(self,rid):return self.requests[rid]['receipt']
    class FakeAdapter:
        def __init__(self):self.world=FakeWorld();self.run_calls=[]
        @property
        def tick(self):return self.world.clock
        def run_until(self,target):
            assert target>=self.tick
            self.run_calls.append([self.tick,target]);self.world.clock=target
            for r in self.world.requests.values():
                if r['tick']<target:r['receipt']={'status':'applied'}
    def physical(w):return {'tick':w.clock,'N':67,'RAW_sha256':'fakeRAW','clocks_sha256':'fakeCLOCK'}
    def observe(w,site):return {'raw':0,'site':list(site),'state':0}
    def calendar(a):
        q=a.tick+56
        return {'before_tick':a.tick,'input_tick':q-54,'query_tick':q,
                'early_reader_tick':q+4,'old_reader_tick':q+6,'horizon_tick':q+142}
    old_calls=[]
    def old_fiplus(a,row,directory):
        old_calls.append(dict(row));cal=calendar(a);requests=[]
        for i in range(176):
            r=a.world.submit('old.'+str(i),0,a.tick+2)
            requests.append({'id':r.id,'port':'old.'+str(i),'tick':a.tick+2,
                             'payload':0,'receipt':{'status':'applied'}})
        a.run_until(cal['horizon_tick'])
        return {'calendar':cal,'requests':requests,'early_physical_choice':None,
                'old_q6_choice':0,'before_tick':cal['before_tick'],'after_tick':a.tick}
    declared=[]
    env={'VERSION':'FAKE_TEST_ONLY','CONDITIONS':{'intacto':None,'izq0':('izq',0),
          'izq7':('izq',7),'izq32':('izq',32),'der0':('der',0),'sham0':('sham',0)},
         'SITES':{'izq':[52,48,56],'der':[19,53,23],'sham':[60,48,56]},
         'baseline':SimpleNamespace(_calendar=calendar,_fiplus=old_fiplus,FIPLUS='old_fixed_FI'),
         'physical':physical,'observe':observe,'exact_receipt':lambda x:dict(x),
         '_declare':lambda a,n,s:declared.append((n,list(s)))or True}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(CODE),'exec'),env)
    checks=[]
    for condition in env['CONDITIONS']:
        a=FakeAdapter();row={'condicion':condition,'izquierda':14,'derecha':3,'captura':'normal'}
        result=env['_fiplus'](a,row,Path('FAKE_OWNED_DIAGNOSTIC'),{'life_id':'FAKE_PI06'},'fake_proof')
        extra=int(condition!='intacto')
        assert result['Native_inputs']['unique_requested']==176+extra
        assert result['Native_inputs']['applied']==176+extra
        assert result['early_physical_choice']is None and result['old_q6_choice']==0
        assert a.tick==1198 and len(a.run_calls)==1
        assert old_calls[-1]=={'modo':'old_fixed_FI','izquierda':14,'derecha':3,'captura':'normal'}
        if extra:
            r=result['transient']['request']
            assert r['tick']==1006==result['calendar']['query_tick']-50
            assert r['declared_state']==1 and r['declared_semantic']==1 and r['direction']==[0,0,1]
            assert result['transient']['physical_before_scheduling']==result['transient']['physical_after_scheduling']
        checks.append({'condition':condition,'requested':176+extra,'after_tick':1198,
                       'q4_NULL_and_q6_zero_preserved':True,'passed':True})
    a=FakeAdapter();before=dict(a.world.requests)
    result=env['_evolve'](a,{'ticks':2000,'captura':'normal'},{'life_id':'FAKE_PI06'},'fake_proof')
    assert a.tick==3000 and a.world.requests==before and result['new_inputs_scheduled']==0
    checks.append({'check':'normal evolution contains no new input/repair','passed':True})
    # No reference answer is accepted in row parsing; actual early NULL remains
    # NULL even though a distinct q+6 zero exists in this intentionally FAKE case.
    out={'schema':'DEE.PI06.organization.fake_flow_tests.R01','module_sha256':hashlib.sha256(source).hexdigest(),
         'Native_executed':False,'DEE_imports':False,'Native_ticks':0,
         'test_modality':'AST body with imports replaced by explicit mocks; not an integration or physical-admission proof',
         'checks':checks,'checks_passed':len(checks)}
    path=P/'control/ORGANIZACION_PI06_FLUJO_FAKE_R01.json'
    with path.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'checks_passed':len(checks),'Native_executed':False,'proof_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
