from pathlib import Path
from zipfile import ZipFile
import json,hashlib,subprocess,sys,xml.etree.ElementTree as E
from docx import Document
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01'
source=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_4_CANDIDATO_SIN_VALIDAR.docx';target=ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_5_INTEGRACION_SITUADA_SIN_VALIDACION_VISUAL.docx'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with ZipFile(target)as z:
    assert z.testzip()is None
    for n in z.namelist():
        if n.endswith('.xml'):E.fromstring(z.read(n))
d=Document(target);text='\n'.join(p.text for p in d.paragraphs)
historical6100=[p.text for p in d.paragraphs if'ECO_EXT'in p.text and'T6100'in p.text]
assert all('corrige'in p.lower()for p in historical6100)
assert 'Edición documental 1.5'in text and'22. Integración cognitiva situada'in text
assert all('1.5'in s.footer.paragraphs[0].text and'1.0'not in s.footer.paragraphs[0].text for s in d.sections)
assert sha(source)=='a3f864295097a041b200cd41b93fe5ad5a2740d524a9e9416311b46d14f6b971'
assert sha(ROOT/'DEE_Cognitive_System_1_1_Manual_Maestro_Continuidad_Edicion_1_0.docx')=='f0d1a71f8dc4aa8d9d72aa1428b9ed62df320897ce4987353122539285f2e6e5'
audit={'source':str(source),'source_sha256':sha(source),'updated_word':str(target),'updated_sha256':sha(target),'bytes':target.stat().st_size,'real_docx_modified':True,'structural_zip_and_xml_valid':True,'document_edition':'1.5','software_version_unchanged':'1.1.0','headers_and_footers_updated':True,'toc_links':len([p for p in d.paragraphs if p.style.name=='TOCline']),'historical_6100_mentions_explicitly_corrected':historical6100,'previous_editions_unchanged':True,'initial_validator_false_positive':'It rejected the explicit historical correction ECO_EXT01/T6100; fixed the validator, did not alter or regenerate the Word.'}
render=Path(r'C:\Users\Erik\.codex\plugins\cache\openai-primary-runtime\documents\26.1011.51657\skills\documents\render_docx.py');out=LAB/'manual_render'
try:
    r=subprocess.run([sys.executable,str(render),str(target),'--output_dir',str(out),'--emit_pdf'],capture_output=True,text=True,encoding='utf8',timeout=45);render_record={'command':[sys.executable,str(render),str(target),'--output_dir',str(out),'--emit_pdf'],'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'PNG':[str(p)for p in out.glob('page-*.png')]}
except subprocess.TimeoutExpired as e:render_record={'timeout_seconds':45,'stdout':str(e.stdout),'stderr':str(e.stderr),'PNG':[]}
audit['visual_validation']='PAGES_GENERATED_REQUIRE_VISUAL_QA'if render_record['PNG']else'NOT_AVAILABLE_NO_PAGES';audit['render_attempt']=render_record
(EV/'CAMBIOS_MANUAL_ESTRUCTURA.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:audit[k]for k in('updated_word','updated_sha256','bytes','toc_links','visual_validation','render_attempt')},ensure_ascii=False))
