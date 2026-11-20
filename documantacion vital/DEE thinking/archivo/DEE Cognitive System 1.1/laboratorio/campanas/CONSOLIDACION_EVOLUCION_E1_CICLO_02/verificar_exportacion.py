"""Portable, non-simulating validation of the exact analysis package.
Standard library only. No native engine, external environment, life commit,
historical directories or network are used. Outputs must be outside the ZIP.
"""
from pathlib import Path
import argparse,ast,csv,gzip,hashlib,importlib.util,json,subprocess,sys,xml.etree.ElementTree as ET
from zipfile import ZipFile
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def module(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify(root):
    root=Path(root).resolve();manifest=read(root/'MANIFIESTO_HASHES.json');members=manifest['members']
    for v in members:
        p=root/v['path'];assert p.is_file()and p.stat().st_size==v['bytes']and sha(p)==v['sha256'],('Member integrity',v['path'])
    calc=module('c02_offline_recalc',root/'RECALCULO/recalcular.py')
    m=calc.calculate(root/'EVIDENCIA_CAUSAL/PRIMARIOS');m['exact_input_ledger']=calc.input_ledger(root/'EVIDENCIA_CAUSAL/RECIBOS_OPERACIONES_EXACTOS.json.gz')
    expected=read(root/'RECALCULO/CALCULOS_ESPERADOS.json');assert m==expected,'Recalculated results differ from sealed expected values'
    assert m['main_gate']['opportunities']==21 and m['main_gate']['useful']==21 and m['main_gate']['utility']==10
    assert len(m['case_inventory'])==239 and m['exact_raw_observations_verified']==7178
    assert not m['exact_input_ledger']['unresolved']
    tables=read(root/'RECALCULO/TABLAS_DATOS.json');table_rows={}
    for t in tables['tables']:
        with(root/t['file']).open(encoding='utf-8-sig',newline='')as f:actual=list(csv.reader(f))
        assert actual==[t['columns'],*t['rows']],('CSV exact text equality',t['file'])
        table_rows[t['file']]=len(t['rows'])
    reader=module('c02_snapshot_only',root/'RECALCULO/snapshot_reader.py');witnesses=read(root/'EVIDENCIA_CAUSAL/INDICE_SNAPSHOTS_COMPLETOS.json');summaries={}
    cache={}
    for v in witnesses['files']:
        p=root/v['exported_path'];x=reader.Snapshot(p)
        assert x.checksum_valid and x.encoded_sha256==v['sha256']and x.tick==v['tick']
        assert reader.sha(reader.pbytes(x.raw))==v['RAW_sha256']and reader.sha(reader.pbytes(x.clocks))==v['clocks_sha256']
        summaries[v['role']]={'tick':x.tick,'N':x.N,'pending_count':len(x.pending),'sha256':x.encoded_sha256,'checksum_valid':True}
        # Keep only the few pairs required for explicit physical assertions.
        if v['role']in('source_pre_arm','source_committed','pre21035','post21035','pre21118','post21118','current_triple','current_main'):cache[v['role']]=x
    a,b=cache['source_pre_arm'],cache['source_committed'];assert a.raw==b.raw and a.clocks==b.clocks and len(a.pending)==0 and len(b.pending)==191
    a,b=cache['pre21035'],cache['post21035'];assert a.tick==21034 and b.tick==21035
    assert a.observation([4,59,23])['direction']==[1,0,0]and a.observation([4,59,23])['s_reg']==7
    assert a.observation([4,59,22])['direction']==[1,0,1]and a.observation([4,59,22])['s_reg']==7
    assert b.observation([5,59,23])['direction']==[1,0,1]and b.observation([5,59,23])['s_reg']==14
    a,b=cache['pre21118'],cache['post21118'];assert a.tick==21117 and b.tick==21118
    assert a.observation([20,59,23])['direction']==[1,0,0]and a.observation([22,59,23])['direction']==[-1,0,0]
    assert b.observation([21,59,23])['direction']==[0,0,0]and b.observation([21,59,23])['s_reg']==14
    x=cache['current_triple'];assert x.tick==21711
    for site,sign in(([11,59,23],1),([31,59,26],-1),([11,48,29],1)):
        f=x.observation(site);assert f['state']==1 and f['semantic']==1 and f['s_reg']==7 and f['direction']==[sign,0,0]
    site=[49,(35+(x.tick-22)%67)%67,35];assert x.observation(site)['s_reg']==93
    x=cache['current_main'];assert x.tick==21711 and x.observation([49,(35+(x.tick-22)%67)%67,35])['s_reg']==97
    p=root/'MANUAL/Manual_Maestro_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx'
    with ZipFile(p)as z:
        assert z.testzip()is None
        for n in z.namelist():
            if n.endswith('.xml'):ET.fromstring(z.read(n))
        doc=z.read('word/document.xml').decode('utf8');assert 'DCS11_CICLO02'in doc and 'E1_CICLO02_SEPARACION_TRIPLE_01'in doc
        assert sum(z.read(n).count(b'PAGE')for n in z.namelist()if n.startswith('word/footer')and n.endswith('.xml'))==2
    source_count=0
    for p in root.rglob('*.py'):
        compile(p.read_bytes(),str(p),'exec',dont_inherit=True);source_count+=1
    with __import__('tempfile').TemporaryDirectory(prefix='c02_reference_',dir=root.parent)as temp:
        out=Path(temp)/'references.json'
        command=[sys.executable,'-I','-B',str(root/'RECALCULO/referencias_entorno.py'),'--calculos',str(root/'RECALCULO/CALCULOS_ESPERADOS.json'),'--salida',str(out)]
        p=subprocess.run(command,capture_output=True,text=True,encoding='utf8',timeout=30);assert p.returncode==0,p.stderr
        assert read(out)==read(root/'EVIDENCIA_CAUSAL/REFERENCIAS_ENTORNO.json')
    visual=read(root/'MANUAL/VALIDACION_VISUAL_WORD.json');assert visual['sha256']==sha(root/'MANUAL/Manual_Maestro_1_6_CICLO02_SIN_VALIDACION_VISUAL.docx')
    return {'verified_members':len(members),'CSV_rows':table_rows,'primaries':m['exported_primaries'],'raw_integer_observations_checked':m['exact_raw_observations_verified'],
       'main_gate':{k:m['main_gate'][k]for k in('opportunities','valid','useful','utility')},'receipt_operations':len(m['exact_input_ledger']['operations']),
       'complete_snapshot_witnesses':summaries,'python_sources_syntax_checked':source_count,
       'reference_environment_recalculated':True,'word_xml_and_fields':True,'word_visual_validation':visual['visual_validation'],
       'native_ticks':0,'DEE_or_Gymnasium_imported':False,'classification':'Archived recalculation/integrity, NOT a new native reproduction, policy test or standalone continuation package',
       'limits':['Original complete campaign telemetry and all operational snapshots remain local.','Python syntax and field integrity do not prove every mechanism. Causal scope is stated per contrast.','Word render blocked: LibreOffice soffice.exe unavailable.','CSV values are exact strings, including uint64. No conversion to floating point.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
    out=verify(a.root);a.salida.parent.mkdir(parents=True,exist_ok=True);a.salida.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in out.items()if k!='complete_snapshot_witnesses'},ensure_ascii=False))
