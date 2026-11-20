from pathlib import Path
import json,importlib.util
L=Path(__file__).resolve().parent;R=L.parents[2];S=R/'sistema';E=R/'evidencia/campanas/CONSOLIDACION_EVOLUCION_E1_CICLO_02'
sp=importlib.util.spec_from_file_location('snapshot_only',S/'capacidades/observador_causal_retrospectivo_01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
rows=[]
for t in range(21109,21119):
 p=E/'C02_LATDIAG_315_PASIVO_VENTANA'/('PRE_T'+str(t)+'.deetsnap.gz');x=m.Snapshot(p);reads=[]
 for ix in range(67):
  for z in range(20,27):
   v=x.observation([ix,59,z])
   if v['s_reg']==7 and v['direction'][0]<0:reads.append(v)
 rows.append({'tick':x.tick,'path':str(p.relative_to(R)),'sha256':x.encoded_sha256,'negative_7_in_plane_slice':reads})
(E/'TUBO_NEGATIVO_21118_ZERO_TICKS.json').write_text(json.dumps({'rows':rows,'scope':'Observed local candidate tube, not a unique particle ID or resolved genealogy before21108.'},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(rows,ensure_ascii=False))
