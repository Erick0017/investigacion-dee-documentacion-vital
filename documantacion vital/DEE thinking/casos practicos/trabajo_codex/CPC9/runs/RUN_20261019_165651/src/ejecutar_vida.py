"""Fresh CPC9 life; writes exact local/native outputs, never reads targets."""
from pathlib import Path
import argparse,hashlib,json,sys,time,traceback
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from vida_e1 import LifeSession
from ejecutar_retorno import write
from integracion.relational_pair import physical,move

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--source',type=int,default=31);p.add_argument('--first-object',type=int,default=18)
    p.add_argument('--count',choices=['both','A','B','none'],default='both');p.add_argument('--count-form',default='paired')
    p.add_argument('--regulation',choices=['plus','minus','offpath'],default='plus')
    p.add_argument('--two-reference',type=int,default=31);p.add_argument('--two-object',type=int,default=11)
    p.add_argument('--two-omit',choices=['R','O']);p.add_argument('--two-order',default='O_first')
    p.add_argument('--contact-medium',type=int,default=3);p.add_argument('--remote',choices=['onpath','offpath','omitted'],default='onpath')
    p.add_argument('--remote-name',default='paired');p.add_argument('--back-form',default='paired')
    p.add_argument('--until',type=int,default=884);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    r={'schema':'CPC9.life.measurements.v1','case_id':a.case,'configuration':vars(a)|{'out':str(a.out)},
       'preparations':0,'frames':[],'local_neighborhoods':[],'snapshots':[],'MAIN_RAW_clock_edits':[],
       'source_hashes':{},'status':'RUNNING','independence':'Fresh prepared life; not a continuation of another candidate'}
    for folder in ('src','base_validada/cpc8/src','front_semantics/src','front_relations/src'):
        for path in sorted((ROOT/folder).rglob('*.py')):
            data=path.read_bytes();h=hashlib.sha256(data).hexdigest();r['source_hashes'][str(path.relative_to(ROOT))]=h
            # Preserve one exact source per hash, even if an auditor/runner is corrected later.
            copy=ROOT/'genealogia/code_by_hash'/(h+'.py')
            if not copy.exists():copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(data)
    try:
        contacts=('A','B')if a.count=='both'else()if a.count=='none'else(a.count,)
        s=LifeSession.create(identifier=a.case,medium_load=a.contact_medium,
             regulation_medium=-1 if a.regulation=='minus'else 1,regulation_route='offpath'if a.regulation=='offpath'else'onpath',
             count_contacts=contacts,remote_regulation=a.remote)
        r.update(preparations=1,geometry=s.geometry)
        s.curriculum(magnitude_value=a.source,magnitude_objects=(a.first_object,45,31),count_form=a.count_form,
             two_reference=a.two_reference,two_object=a.two_object,two_omit=a.two_omit,two_order=a.two_order,
             remote_name=a.remote_name,back_form=a.back_form)
        ticks={0,1,2,3,4,5,9,10,11,24,31,53,54,69,70,71,72,73,76,77,78,79,80,86,89,91,94,100,114,136,137,138,139,142,143,146,147,148,149,165,170,171,177,180,203,204,205,206,210,213,214,215,216,220,221,225,268,270,271,280,281,282,337,338,339,340,342,343,344,348,349,350,404,405,409,410,411,415,416,417,428,471,472,476,477,478,482,483,484,486,487,499,500,538,539,549,550,553,554,558,559,563,601,603,605,606,616,617,668,672,673,683,684,735,739,740,750,751,802,806,807,817,818,884}
        for tick in sorted(t for t in ticks if t<=a.until):
            s.run_until(tick);v=s.view();r['frames'].append({'tick':tick,'physical':physical(s.world),'view':v})
            if tick in (71,72,138,139,205,206,342,343,348,349,350,409,410,415,416,605,606,672,673):
                centers={'two_memory':s.two_memory.geometry['center'],'main_quantity':s.geometry['quantity']['center']}
                if 342<=tick<=416:
                    centers.update({x['id']:x['hub']if tick<415 else x['effect']for x in s.geometry['remote_contact']['surfaces']})
                r['local_neighborhoods'].append({'tick':tick,'windows':{name:[s.observe(move(site,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)]for name,site in centers.items()}})
            if tick in (0,94,148,216,549,616,606,673,884):
                path=a.out/f'T{tick}.deetsnap.gz';storage=s.save(path)
                r['snapshots'].append({'path':path.name,'storage':storage,'physical':physical(s.world)})
            r.update(last_complete_tick=tick,requests=s.receipts(),elapsed_seconds=time.monotonic()-started)
            write(a.out/'MEDICIONES.json',r)
        r.update(status='MEASURED',final_physical=physical(s.world),receipt_statuses=dict(Counter(x['receipt']['status']for x in s.receipts())))
    except BaseException as error:
        r.update(status='TECHNICAL_ERROR',error=repr(error),traceback=traceback.format_exc());raise
    finally:write(a.out/'MEDICIONES.json',r)
    print(json.dumps({'case':a.case,'status':r['status'],'tick':s.tick,'resources':s.geometry['resources'],'requests':len(s.receipts()),'seconds':time.monotonic()-started},ensure_ascii=False))
if __name__=='__main__':main()
