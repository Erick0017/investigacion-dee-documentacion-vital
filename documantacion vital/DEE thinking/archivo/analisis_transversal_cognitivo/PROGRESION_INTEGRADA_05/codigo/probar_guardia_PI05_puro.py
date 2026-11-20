"""Pure stubs only: check age/input/namespace contracts, not Native effects."""
from pathlib import Path
from types import ModuleType,SimpleNamespace as NS
import importlib.util,json,sys,hashlib
H=Path(__file__).resolve().parent;PATCH=H/'FUENTES_GUARDIA_PI05_R01_SELLADAS';P=H.parent
def module(n,path):
    s=importlib.util.spec_from_file_location(n,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
    guard=module('PI05_guard_fake',PATCH/'capacidades/pi05_guardia_transito_R01.py')
    data=json.loads((PATCH/'capacidades/PROTOCOLO_PI05_GUARDIA_R01.json').read_text('utf8'))
    guard.protocol=lambda:(data,'fake-protocol-sha')
    def adapter(tick=817876):
        rt=NS(current_tick=tick,dimension=67,channel_names=[],receipts={},fields={})
        class World:
            runtime=rt
            def declare_interface(self,iface):rt.channel_names.append(iface.name);rt.site=iface.channel.injection_site
            def submit(self,ch,payload,tick):
                rt.receipts[1]={'id':1,'status':'scheduled'};rt.submission=(ch,payload,tick);return NS(id=1)
        rt.receipt=lambda i:rt.receipts[i]
        class Adapter:
            world=World()
            @property
            def tick(self):return rt.current_tick
        return Adapter()
    baseline=ModuleType('capacidades.pi05_transito_causal_R01');baseline.FIPLUS='eci01-pi05-fiplus'
    baseline._identity=lambda a:{'life_id':'ECI02_PI03_REPRO_PI04_PI05_FAKE'}
    baseline._calendar=lambda a:{'input_tick':a.tick+2}
    calls=[]
    def fake_balance(a,row,directory):
        calls.append({'before':a.tick,'row':row,'scheduled':a.world.runtime.submission})
        rt=a.world.runtime;rt.current_tick+=198;rt.receipts[1]['status']='applied';rt.fields[rt.site]=4<<60
        return {'requests':[{'id':1000+i,'receipt':{'id':1000+i,'status':'applied'}}for i in range(176)],
                'before_tick':a.tick-198,'after_tick':a.tick,'old_q6_choice':None,'early_physical_choice':None}
    baseline._fiplus=fake_balance
    native=ModuleType('dee_thinking._native');native.ChannelSpec=NS;native.InterfaceSpec=NS
    native.Coordinate=lambda *a:tuple(a);native.Direction=lambda *a:tuple(a)
    native_parent=ModuleType('dee_thinking');native_parent._native=native
    consolidated=ModuleType('dee_thinking.consolidated');consolidated.exact_receipt=lambda r:r.copy()
    tools=ModuleType('app.native_tools')
    tools.physical=lambda world:{**data['source'],'tick':world.runtime.current_tick}
    tools.observe=lambda world,site:{'raw':str(world.runtime.fields.get(tuple(site),0)),'clock':str(world.runtime.current_tick)}
    caps=ModuleType('capacidades');caps.pi05_transito_causal_R01=baseline;app=ModuleType('app');app.native_tools=tools
    stubs={'capacidades':caps,'capacidades.pi05_transito_causal_R01':baseline,'dee_thinking':native_parent,
           'dee_thinking._native':native,'dee_thinking.consolidated':consolidated,'app':app,'app.native_tools':tools}
    assert not any(n in sys.modules for n in stubs)
    sys.modules.update(stubs)
    try:
        a=adapter();r=guard.dispatch(a,{'modo':guard.GUARD,'izquierda':14,'derecha':3,'captura':'global'},directory='FAKE')
        assert calls[0]['before']==817876 and calls[0]['scheduled'][2]==817878 and a.tick==818074
        assert r['Native_inputs']['unique_requested']==177 and r['Native_inputs']['applied']==177
        assert r['old_q6_choice']is None and r['early_physical_choice']is None # no invented favourable fallback
        b=adapter(818074);r2=guard.dispatch(b,{'modo':guard.PREPARE_GUARD},directory='FAKE')
        assert b.tick==818074 and r2['new_native_ticks']==0 and b.world.runtime.submission[2]==818076
        assert r2['support']['request']['receipt']['status']=='scheduled'
        try:guard.dispatch(b,{'modo':guard.PREPARE_GUARD},directory='FAKE')
        except ValueError:pass
        else:raise AssertionError('Reinstallation permitted')
        c=adapter();c.world.runtime.fields[(19,53,20)]=1
        try:guard.validate(c,{'modo':guard.GUARD,'izquierda':14,'derecha':3,'captura':'global'})
        except ValueError:pass
        else:raise AssertionError('Occupied support overwritten')
        for bad in({'modo':guard.PREPARE_GUARD,'site':[1,1,1]}, {'modo':guard.GUARD,'izquierda':14,'derecha':3,'captura':'global','expected':1}):
            try:guard.validate_literal(bad)
            except ValueError:pass
            else:raise AssertionError('Hidden input permitted')
    finally:
        for n in stubs:del sys.modules[n]
    proof={'schema':'DEE.PI05.P0_guard.fake_contract_tests.R01','Native_executed':False,'Native_ticks':0,
           'scope':'Python stubs only. No legal-admission, passivity, scientific efficacy or collateral-safety result.',
           'checks':{'same_start_age':True,'old_horizon198':True,'old176_plus1':True,'fixed_birth_plus2':True,
                     'NULL_not_replaced':True,'separate_installation0ticks_pending':True,'no_reinstallation':True,'no_occupied_rewrite':True,'no_hidden_arguments':True},
           'module_sha256':hashlib.sha256((PATCH/'capacidades/pi05_guardia_transito_R01.py').read_bytes()).hexdigest()}
    out=P/'control/PRUEBAS_GUARDIA_FAKE_R01.json';assert not out.exists();out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(proof))
if __name__=='__main__':main()
