"""Execute the existing twelve witnesses consecutively, never select a world.

Expected values are checked only after each physical use. The arithmetic
binding transports the actual prior integer, with no expected fallback.
"""
from pathlib import Path
import argparse,hashlib,json,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
sys.path.insert(0,str(P/'codigo'))
from servicio_ensayo_PI05 import Owner
def get(value,path):
    for key in path:value=value[key]
    return value
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--vida',required=True);ap.add_argument('--tag',required=True);a=ap.parse_args()
    if not a.vida.startswith('ECI02_PI03_REPRO_PI04_') or not a.tag.startswith('PI04_'):raise ValueError('Explicit PI04 candidate/diagnostic only')
    out=P/'control'/(a.tag+'.json')
    if out.exists():raise ValueError('Closed panel is preserved; do not repeat')
    file=C/'reproducibilidad/recetas/panel_12.json';recipe=json.loads(file.read_text(encoding='utf8'));v=recipe['variants']['principal'];rows=[];numbers={};ids={};begin=None
    with Owner(a.vida,a.tag)as owner:
        for batch in v['batches']:
            for spec in batch:
                literal=dict(spec['literal'])
                if 'actual_integer_binding'in spec:
                    b=spec['actual_integer_binding'];actual=numbers[b['from_step']]
                    if type(actual)is not int:raise ValueError('Actual integer absent; never substitute expected')
                    literal[b['field']]=actual
                actual=owner.material(a.tag+'_'+spec['label'],literal,feedback='omit')
                if begin is None:begin=actual['before_tick']
                if spec.get('require_zero_ticks')and actual['after_tick']!=actual['before_tick']:raise ValueError('Administrative pause changed time')
                observed=get(actual,spec['read_path'])if 'read_path'in spec else None
                if 'read_path'in spec:numbers[spec['label']]=observed
                row={'label':spec['label'],'literal':literal,'before_tick':actual['before_tick'],'after_tick':actual['after_tick'],'observed':observed,'expected_evaluator_only':spec.get('expected'),'correct':None if 'expected'not in spec else observed==spec['expected'],'primary':str(P/'ensayos'/(a.tag+'_'+spec['label']+'.json'))}
                for path in spec.get('receipt_paths',[]):
                    for req in get(actual,path):
                        identifier=int(req['id']);status=req.get('receipt',req).get('status')
                        if identifier in ids and ids[identifier]!=status:raise ValueError('Receipt aliases disagree')
                        ids[identifier]=status
                rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
                if row['correct']is False:raise ValueError('Material regression preserved; panel stopped, no remedial teaching')
        owner.control('guardar')
    proof={'schema':'DEE.PI04.existing_panel12.actual.R01','life':a.vida,'recipe':str(file),'recipe_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'rows':rows,'correct':sum(r['correct']is True for r in rows),'tested':sum(r['correct']is not None for r in rows),'inputs':{'unique_requested':len(ids),'applied':sum(s=='applied'for s in ids.values()),'other':sum(s!='applied'for s in ids.values())},'before_tick':begin,'after_tick':rows[-1]['after_tick'],'new_native_ticks':rows[-1]['after_tick']-begin,'owner_closed':True,'single_consecutive_life':True,'not_acquisition':True}
    expected=v['native_receipt_expectations']
    if proof['correct']!=12 or len(ids)!=expected['unique_requested']or proof['inputs']['applied']!=expected['applied']:raise ValueError('Panel denominator or response mismatch; primaries preserved')
    with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
    print(json.dumps({'proof':str(out),'responses':proof['correct'],'inputs':proof['inputs'],'Native_ticks':proof['new_native_ticks']}),flush=True)
if __name__=='__main__':main()
