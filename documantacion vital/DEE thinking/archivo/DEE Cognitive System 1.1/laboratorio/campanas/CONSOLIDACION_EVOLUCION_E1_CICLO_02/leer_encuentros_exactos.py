"""Read-only full-checkpoint geometry; no lineage from load equality alone."""
from pathlib import Path
import json,hashlib,importlib.util
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
sp=importlib.util.spec_from_file_location('snapshot_only',S/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
out=[]
for name,id,coord in(('C02_DIAG_221_CONTINUACION','first_departure',[5,59,23]),('C02_LATDIAG_315_PASIVO','first_departure',[21,59,23])):
 d=json.loads((E/(name+'.json')).read_bytes())['data']['result'][id]
 pre_info=d['pre'];pre_path=R/(pre_info['path']if isinstance(pre_info,dict)else pre_info)
 post_info=d['post'];post_path=R/(post_info['path']if isinstance(post_info,dict)else post_info)
 a=m.Snapshot(pre_path);b=m.Snapshot(post_path);roi=[]
 for t,snapshot in(('pre',a),('post',b)):
  q=[]
  for dx in range(-3,4):
   for dy in range(-3,4):
    for dz in range(-3,4):
     p=[(coord[0]+dx)%67,(coord[1]+dy)%67,(coord[2]+dz)%67];v=snapshot.observation(p)
     if v['raw']!='0':q.append(v)
  roi.append({'stage':t,'tick':snapshot.tick,'nonzero_RAW_in_ROI':q,'pending':snapshot.pending,'checksum_valid':snapshot.checksum_valid})
 out.append({'case':name,'center':coord,'pre_original':{'path':str(pre_path.relative_to(R)),'sha256':a.encoded_sha256},'post_original':{'path':str(post_path.relative_to(R)),'sha256':b.encoded_sha256},'region':roi,
  'coverage':'ROI radius3, partial. Full native pre/post bytes available; future pending protocol explicit. No assumption that Moore26 alone spans the tick.'})
path=E/'ENCUENTROS_EXACTOS_ZERO_TICKS.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{'case':r['case'],'regions':[{'stage':x['stage'],'tick':x['tick'],'nonzero':x['nonzero_RAW_in_ROI'],'pending_boundaries':[q['boundary']for q in x['pending']]}for x in r['region']]}for r in out],ensure_ascii=False))
