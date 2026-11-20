import hashlib,json,sys,zipfile
from pathlib import Path
root=Path(__file__).resolve().parent;product=root.parents[1];cases=product/'casos practicos'
parents=[(product/'archivo/DEE_thinking_3_5_0_ENTREGA_FINAL_RESULTADOS.zip','4cae52462e39ebc0443c14b4f07fe0a944cf6e1acb28f92a3657c80da2bb81ac'),(cases/'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip','75ab357f41f6214c1798efbf69bd0708ab891038d30d770fdfe4a379208f793e')]
provenance=[]
for index,(path,expected) in enumerate(parents):
    h=hashlib.sha256(path.read_bytes()).hexdigest();assert h==expected,(path,h)
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None;names=z.namelist();rows=[]
        for n in names:
            parts=Path(n).parts
            if index==0:
                # Exact product source, build recipe and scope, not scientific
                # nested ZIPs or a copied virtual environment.
                rel=n.split('/',1)[1] if n.startswith('DEE_thinking_3_5_0/') else n
                if not (rel.startswith(('source/','docs/')) or rel in ('PRODUCT_CONTRACT.json','README.md','THIRD_PARTY_NOTICES.md')):continue
                dest=root/rel
            else:
                rel=n[5:] if n.startswith('CPC3/') else n
                selected=rel.startswith(('src/core/','src/habitat/','src/lenguaje/','fuentes_pertinentes/documentos/')) or rel in ('INFORME_CIENTIFICO.md','CAPACIDADES.json','MIGRACION_Y_LIMPIEZA.json','experimentos/continuidad/RESULTADOS.json','experimentos/seleccion_revisable/RESULTADOS.json') or (rel.startswith('experimentos/') and (rel.endswith('EXPERIMENT_CONFIG.json') or rel.endswith('MEASUREMENTS.json'))) or rel.startswith('checkpoints/continuidad/BA_FULL/') or rel in ('experimentos/seleccion_revisable/casos/D_P_BAD_POS/FINAL_T15.deetsnap','experimentos/seleccion_revisable/casos/D_P_GOOD_POS/FINAL_T15.deetsnap')
                if not selected:continue
                dest=root/'evidence/CPC3'/rel
            if n.endswith('/'):continue
            dest.parent.mkdir(parents=True,exist_ok=True);data=z.read(n);dest.write_bytes(data);rows.append({'member':n,'destination':str(dest.relative_to(root)),'sha256':hashlib.sha256(data).hexdigest()})
    provenance.append({'path':str(path),'sha256':h,'selected_members':rows})
(root/'PARENTS.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8');print(json.dumps({'verified_parents':len(provenance),'source_exists':(root/'source/CMakeLists.txt').exists(),'members':[len(x['selected_members']) for x in provenance]}))
