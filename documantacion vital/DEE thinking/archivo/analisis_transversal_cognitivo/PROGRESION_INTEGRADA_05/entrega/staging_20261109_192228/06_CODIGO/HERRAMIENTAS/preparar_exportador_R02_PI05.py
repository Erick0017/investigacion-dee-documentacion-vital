from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
p=H/'exportar_prefijo_cerrado_PI05.py';t=p.read_text('utf8')
t=t.replace('Closed PI04 NONE/YOKE paired export','Closed exact S5 PI05 or original PI04 NONE/YOKE paired export R02')
t=t.replace("ap.add_argument('--vida',choices=sorted(ALLOWED),required=True)","ap.add_argument('--vida',required=True);ap.add_argument('--tick',type=int,required=True)")
marker="if not dest.is_relative_to(CAMPAIGN.resolve())or dest.exists():raise ValueError('New unused PI05 campaign destination only')"
extra="""
    s5=(CAMPAIGN/'estados/candidato/sistema').resolve();s2=(CAMPAIGN.parent/'PROGRESION_INTEGRADA_04/estados/candidato_R02/sistema').resolve()
    if not ((s==s5 and ar.vida.startswith('ECI02_PI03_REPRO_PI04_PI05_')and len(ar.vida)>len('ECI02_PI03_REPRO_PI04_PI05_'))or(s==s2 and ar.vida in ALLOWED and ar.tick==816019)):
        raise ValueError('Exact S5 PI05 diagnostic or two original historical controls only')
    if not 0<ar.tick<1000000000:raise ValueError('Explicit exact expected current tick required')"""
assert t.count(marker)==1;t=t.replace(marker,marker+extra)
t=t.replace('!=816019','!=ar.tick').replace("'source_tick':816019","'source_tick':ar.tick")
t=t.replace('Only exact coherent post20 T816019 complete prefix','Only exact coherent expected full prefix')
t=t.replace("'schema':'DEE.PI05.closed_paired_preservation.v1'","'schema':'DEE.PI05.closed_paired_preservation.R02'")
t=t.replace("'source_sha256':critical","'source_exporter_version':'R02_expected_tick_and_exact_S5_scope','source_sha256':critical")
ast.parse(t);o=H/'exportar_corte_PI05_R02.py'
assert not o.exists();o.write_text(t,encoding='utf8')
print(json.dumps({'created':str(o),'original_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'R02_sha256':hashlib.sha256(o.read_bytes()).hexdigest(),'Native_executed':False}))
