"""Exact passive metadata diff of the two closed PI10 source exports.

Reads snapshots using the preserved stdlib parser. No Native import, world,
database or process. Classification labels are descriptive, not permission
to ignore changes or a claim of full physical equality over three ticks.
"""
from pathlib import Path
import hashlib, importlib.util, json

P=Path(__file__).resolve().parents[1]
C=P.parents[2]/'DEE Cognitive 2.0'
OUT=P/'control/COMPARACION_METADATA_D_A_P0_PI10_R01.json'
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(data):return hashlib.sha256(data).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def leaves(a,b,path=''):
    if a==b:return []
    if isinstance(a,dict)and isinstance(b,dict):
        result=[]
        for k in sorted(set(a)|set(b)):
            child=path+'/'+str(k).replace('~','~0').replace('/','~1')
            if k not in a or k not in b:result.append({'path':child,'before_present':k in a,'after_present':k in b})
            else:result.extend(leaves(a[k],b[k],child))
        return result
    return [{'path':path or '/', 'before':a,'after':b}]
def load_pair(folder,parser):
    mf=folder/'EXPORTACION_SERVICIO.json';v=read(mf);snap=folder/v['native_snapshot'];need(sha(snap.read_bytes())==v['snapshot_sha256'],'Export snapshot identity')
    view=parser.snapshot_view(snap);need(view['physical']=={k:v['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')},'Export physical identity')
    return {'manifest':str(mf),'manifest_sha256':sha(mf.read_bytes()),'snapshot':str(snap),'snapshot_sha256':sha(snap.read_bytes()),'physical':view['physical']},view
def main():
    need(not OUT.exists(),'Preserve prior comparison')
    pp=C/'reproducibilidad/observador_pasivo.py';sp=importlib.util.spec_from_file_location('PI10_exact_frozen_metadata_parser',pp);parser=importlib.util.module_from_spec(sp);sp.loader.exec_module(parser)
    source,a=load_pair(P/'pares/PRINCIPAL_D_T922371',parser);target,b=load_pair(P/'pares/P0_COMUN_T922374',parser)
    need(source['physical']['tick']==922371 and target['physical']['tick']==922374,'Exact before and lawful P0 cuts')
    before=a['metadata'];after=b['metadata'];same=[];changed=[]
    for key in sorted(set(before)|set(after)):
        if before.get(key)==after.get(key):same.append(key);continue
        classification='scientific_or_unclassified_requires_review'
        if key=='DEE.Cognitive.System.1.1.life.v1'or key.startswith('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'):classification='administrative_transport_candidate'
        elif key=='DEE.Cognitive.PI10.adaptive_query.two_native_traces.R01':classification='new_unlearned_PI10_preparation'
        elif key=='DEE.Cognitive.PI04.C2C.coordination.R01':classification='possible_C2C_identity_only_requires_exact_leaf_check'
        elif key.startswith('DEE.Cognitive.PI02'):classification='PI02_progress_or_segmentation_requires_review'
        row={'key':key,'before_present':key in before,'after_present':key in after,'before_sha256':sha(before[key].encode('utf8'))if key in before else None,'after_sha256':sha(after[key].encode('utf8'))if key in after else None,'classification':classification}
        if key in before and key in after:
            try:row['JSON_leaf_changes']=leaves(json.loads(before[key]),json.loads(after[key]))
            except (ValueError,TypeError):row['JSON_leaf_changes']=None
        changed.append(row)
    out={'schema':'DEE.PI10.frozen_D_to_lawful_P0_metadata_diff.R01','Native_imported':False,'new_ticks_in_recalculation':0,'source':source,'target':target,
      'parser_sha256':sha(pp.read_bytes()),'elapsed_recorded_Native_ticks':3,'literal_equal_metadata_keys':same,'changed_metadata_keys':changed,
      'scope':'Exact metadata bytes of closed original exports. Three Native evolution ticks and legal new anatomy intentionally differ physically; this is not a migration0 equality test or a claim of learned capacity.'}
    with OUT.open('x',encoding='utf8')as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'file':str(OUT),'sha256':sha(OUT.read_bytes()),'same_count':len(same),'changed':[{'key':v['key'],'classification':v['classification'],'paths':[p['path']for p in v.get('JSON_leaf_changes',[])or[]]}for v in changed],'Native_imported':False},ensure_ascii=False))
if __name__=='__main__':main()
