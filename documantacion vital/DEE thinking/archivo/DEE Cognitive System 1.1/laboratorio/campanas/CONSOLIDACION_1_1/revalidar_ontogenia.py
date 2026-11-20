from pathlib import Path
import argparse,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store,legacy_class
from app.native_tools import physical,observe,moore27,atomic_json,digest_file,exact_receipt
from app.process_control import protect_current,current_resources
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();protect_current();a.out.mkdir(parents=True,exist_ok=False);planfile=Path(__file__).with_name('ONTOGENIA_REVALIDACION_PLAN_R1.json');plan=json.loads(planfile.read_bytes());store=Store();reference=store.record('E1_CPC9_884');summaries=[]
    for case in plan['cases']:
        folder=a.out/case['id'];folder.mkdir();started=time.perf_counter();life='DCS11_'+case['id'];record=store.create(life,'cpc9_integral_n67',case['preparation']);record,s=store.load(life);initial=physical(s.world,occupation=True);s.curriculum(**case['experience']);result={'schema':'DCS1.1.fresh_integral_controls.r1','case':case,'life_id':life,'initial':initial,'plan_sha256':digest_file(planfile),'geometry':s.geometry,'frames':[],'snapshots':[],'external_protocol':case['experience'],'RAW_clock_edits':[],'status':'SCHEDULED'}
        for tick in plan['frames']:
            s.run_until(tick);before=physical(s.world);view=s.view()
            if physical(s.world)!=before:raise AssertionError('View calledpassive modifiednativeworld')
            frame={'tick':tick,'physical':physical(s.world,occupation=True),'view':view}
            if tick in(5,15,19,31,76,82,206,210,214,216,221):
                c=s.geometry['body']['emission'];frame['Moore27_order_emission']=moore27(s.world,c)
            result['frames'].append(frame)
            if tick in(0,31,214,884):
                file=folder/('T'+str(tick)+'.deetsnap.gz');result['snapshots'].append({'file':file.name,'storage':s.save(file),'sha256':digest_file(file),'physical':frame['physical']})
        result['receipts']=[exact_receipt(r)for r in s.world.runtime.receipts];result['final']=physical(s.world,occupation=True);result['status']='MEASURED';result['seconds']=time.perf_counter()-started;result['resources']=current_resources()
        if case['id']=='ONTO_R1_BASE_REPLAY':result['full_884_reference_equal']=all(result['final'][k]==reference['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256'))
        record=store.commit(record,s,{'kind':'FRESH_INTEGRAL_CONTROLS','plan_sha256':digest_file(planfile),'case':case});result['operative_snapshot']=record['snapshot'];atomic_json(folder/'MEDICIONES.json',result);summaries.append({'case':case['id'],'seconds':result['seconds'],'final':result['final'],'reference_equal':result.get('full_884_reference_equal')});atomic_json(a.out/'RESUMEN.json',{'cases':summaries,'plan_sha256':digest_file(planfile)});print(json.dumps(summaries[-1]),flush=True)
if __name__=='__main__':main()
