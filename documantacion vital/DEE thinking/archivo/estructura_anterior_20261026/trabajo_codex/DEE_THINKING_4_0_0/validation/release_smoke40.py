"""Run from a clean extraction against its noneditable installed WHL."""
import argparse,hashlib,json,sys,tempfile,zipfile
from pathlib import Path
import dee_thinking as d

LAB_PREFIXES=('core','habitat','lenguaje','src.core','src.habitat','src.lenguaje','dee_universe_v27')

def no_laboratory_modules():
    found=[name for name in sys.modules if any(name==prefix or name.startswith(prefix+'.') for prefix in LAB_PREFIXES)]
    assert not found, 'Laboratory/alternate engine imported: '+repr(found)
    return True

def installed_identity(wheel):
    module=Path(d.__file__).resolve();prefix=Path(sys.prefix).resolve();package=module.parent
    assert module.is_relative_to(prefix) and 'site-packages' in module.parts, 'Noneditable installation in the current interpreter is required'
    native=Path(d._native.__file__).resolve()
    assert native.is_relative_to(package) and native.is_relative_to(prefix)
    members={}
    with zipfile.ZipFile(wheel) as archive:
        names=archive.namelist();assert len(names)==len(set(names)), 'Duplicate wheel members'
        assert archive.testzip() is None
        assert 'Version: 4.0.0' in archive.read('dee_thinking-4.0.0.dist-info/METADATA').decode('utf-8')
        assert 'Tag: cp313-cp313-win_amd64' in archive.read('dee_thinking-4.0.0.dist-info/WHEEL').decode('utf-8')
        for name in names:
            if not name.startswith('dee_thinking/') or name.endswith('/'):continue
            relative=Path(name).relative_to('dee_thinking')
            assert '..' not in relative.parts
            path=package/relative;data=archive.read(name)
            expected=hashlib.sha256(data).hexdigest()
            assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==expected, 'Installed payload differs from the supplied wheel: '+name
            members[name]=expected
    installed_code={path.relative_to(package).as_posix() for path in package.rglob('*') if path.is_file() and path.suffix in ('.py','.pyi','.pyd') and '__pycache__' not in path.parts}
    expected_code={str(Path(name).relative_to('dee_thinking')).replace('\\','/') for name in members if Path(name).suffix in ('.py','.pyi','.pyd')}
    assert installed_code==expected_code, 'Unaccounted installed Python/native modules'
    assert any(name.endswith('.pyd') for name in members)
    return {'wheel':str(wheel),'wheel_sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),
            'native':str(native),'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
            'installed_payload_members':members,'no_unaccounted_code_members':True}

def receipt_panel(runtime):
    return [{'id':r.id,'kind':str(r.kind),'status':str(r.status),'requested_tick':r.requested_tick,
             'effective_tick':r.effective_tick,'channels':list(r.channels),'reason':r.reason} for r in runtime.receipts]
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    p.add_argument('--wheel',type=Path,default=Path(__file__).resolve().parents[1]/'wheel/dee_thinking-4.0.0-cp313-cp313-win_amd64.whl')
    a=p.parse_args();identity=installed_identity(a.wheel.resolve())
    assert d.__version__=='4.0.0' and sys.version_info[:2]==(3,13)
    assert d.build_info()['kernel_version']==27
    no_laboratory_modules()
    seed=d.reference_seed_path();params=d.CognitiveParameters();params.seed_path=seed;params.profile='comparison'
    c=d.CognitiveSession.create(params);history=c.sense();emission=c.predict()
    assert [r['status'] for r in history['receipts']]==['applied','applied']
    assert emission['prediction_set']==[False] and emission['emission_tick']==37 and emission['target_tick']==83
    with tempfile.TemporaryDirectory(prefix='dt4-release-') as td:
        save=str(Path(td)/'pending.deetsnap');c.save_snapshot(save);r=d.CognitiveSession.load_snapshot(save)
        left=c.compare();right=r.compare()
        assert isinstance(left,dict) and isinstance(right,dict), 'Binding result contract changed'
        assert c.tick==84 and r.tick==84
        assert left['status']==right['status']=='CURRENT_NATIVE_COMPARISON_MEASURED'
        assert left['comparison_decoder']==right['comparison_decoder']
        marker=left['comparison_decoder'];assert marker['presentation']=='discrepancia_direccional'
        assert marker['signed_comparison_marker_present'] and marker['represented_expectation_before_report'] and marker['report_applied'] and marker['within_window']
        actual=marker['physical_output']
        # Frozen physical regression witness from the preserved CPC3 parity
        # state. This is asserted AFTER evolution and never passed to DEE.
        expected={'tick':84,'site':(15,15,15),'raw':2238007539826425857,'clock':84,'state':1,'s_reg':0,'semantic':1,'direction':(-1,0,-1),'active':True}
        for key,value in expected.items():
            assert (tuple(actual[key]) if key in ('site','direction') else actual[key])==value,(key,actual[key],value)
        assert left['physical_output']==actual
        assert left['source_actual']['tick']==83 and left['source_actual']['arrived'] is True
        assert left['input_receipt']['status']=='applied' and left['input_receipt']['effective_tick']==83
        assert c.world.runtime.raw_copy()==r.world.runtime.raw_copy();assert c.world.runtime.clock_copy()==r.world.runtime.clock_copy()
        assert receipt_panel(c.world.runtime)==receipt_panel(r.world.runtime)
        assert c.predict()['status']==r.predict()['status']=='OUTSIDE_FORECAST_DOMAIN'
        w=d.create_learnable_cascade(2);receipts=d.experience_composition(w,[(3,9),(3,11)]);w.save_snapshot(str(Path(td)/'learned.deetsnap'));v=d.OrganizationalWorld.load_snapshot(str(Path(td)/'learned.deetsnap'));q=d.query_composition(v,23)
        assert len(receipts)==4 and all(receipt['status']=='applied' for receipt in receipts)
        assert q['decoded']['stage0']==35 and q['decoded']['stage1']==49
        assert q['receipts'][0]['status']=='applied'
        assert v.observe('stage1','response').raw==q['outputs']['stage1']['raw']
    row={'version':d.__version__,'module':d.__file__,'identity':identity,'build_info':d.build_info(),'cpc3_function':'physical comparison at84','cpc3_result':left,'new_reserved_question':{'query':23,'response':q},'save_restore_continue':True,'no_hidden_lab_imports':no_laboratory_modules(),
         'scope':'directed installation smoke; not a replacement for the complete release validation matrix'}
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');print('CLEAN_EXTRACTION_RELEASE_SMOKE_OK')
if __name__=='__main__':main()
