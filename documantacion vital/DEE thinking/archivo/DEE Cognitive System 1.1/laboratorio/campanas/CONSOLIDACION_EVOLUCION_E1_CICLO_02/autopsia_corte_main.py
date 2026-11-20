"""Zero-tick full-state inspection around the newly observed access loss."""
from pathlib import Path
import json,hashlib,importlib.util
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
sp=importlib.util.spec_from_file_location('read_only_snapshot',S/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
rows=[]
for id in('C02_ACCESS_120_USO4','C02_MAIN_124_ANTERIORES','C02_MAIN_125_PUERTA','C02_MAIN_171_CONTINUAR','C02_MAIN_171_USO','C02_MAIN_172_CONTINUAR','C02_MAIN_172_USO','C02_MAIN_175_EXTERNO'):
 p=E/(id+'.json')
 if not p.exists():continue
 d=json.loads(p.read_text(encoding='utf8'))['result']
 if 'INSTRUMENTO'not in d:continue
 i=d['INSTRUMENTO'];t=i['tick'];h=i['snapshot_sha256']
 candidates=list((S/'estado/checkpoints').glob('E1_CICLO02_MAIN.T'+str(t)+'.*'))
 path=next(q for q in candidates if hashlib.sha256(q.read_bytes()).hexdigest()==h)
 x=m.Snapshot(path);site=[(11+t-20572)%67,59,23]
 fields=x.observation(site)
 nonzero=[x.observation([ix,59,23])for ix in range(67)if x.raw[m.index([ix,59,23],67)]!=0]
 rows.append({'experiment':id,'snapshot':str(path.relative_to(S)),'snapshot_sha256':h,'tick':t,'old_positive_expected_ballistic_site':site,'read':fields,
    'same_y_z_raw_nonzero':nonzero,'pending_count':len(x.pending),'checksum_valid':x.checksum_valid,
    'scope':'Expected tube, not a unique lineage inferred from matching load. A failed port does not establish global erasure.'})
out={'native_ticks':0,'reference_read_tick':20572,'reference_site':[11,59,23],'rows':rows}
(E/'AUTOPSIA_CORTE_MAIN_219.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{'experiment':r['experiment'],'tick':r['tick'],'old_expected':{k:r['read'][k]for k in('state','s_reg','direction')},'slice_nonzero':len(r['same_y_z_raw_nonzero'])}for r in rows],ensure_ascii=False))
