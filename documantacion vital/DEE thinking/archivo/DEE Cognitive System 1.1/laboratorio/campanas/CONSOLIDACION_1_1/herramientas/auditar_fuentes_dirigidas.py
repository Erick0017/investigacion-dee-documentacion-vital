"""Actual source access and limited methodological extracts, never participant input."""
from pathlib import Path
import hashlib,json,re,sys,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[4]
VITAL=ROOT.parents[3]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    out=ROOT/'evidencia/genealogia/LECTURA_DIRIGIDA';out.mkdir(parents=True,exist_ok=True);rows=[]
    selectors=[('FISICA DEE Y PROCESAMIENTO NATIVO','Procesamiento_Nativo_DEE_Libro_Manual_v1.docx'),('mente basal','ORGANIZACION_BASAL_PERSISTENTE_DOCUMENTO_MAESTRO_V2_1.docx'),('entrelazamiento cuantico explicacion y kernel completo/por separado','DEE ENTRELAZAMIENTO'),('entrelazamiento cuantico explicacion y kernel completo/por separado','Fundamentos operacionales DEE.docx')]
    for folder,stem in selectors:
        matches=[p for p in (VITAL/folder).glob('*.docx')if p.name.startswith(stem)]
        if not matches:rows.append({'selection':stem,'status':'NOT_FOUND'});continue
        for p in matches:
            b=p.read_bytes()
            with zipfile.ZipFile(p)as z:xml=z.read('word/document.xml');root=ET.fromstring(xml)
            paragraphs=[''.join(n.itertext())for n in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')]
            # The XML text-node list is preserved with exact source locators;
            # adjacent nodes can form one paragraph, hence no claim of full prose layout.
            keys=r'observador|memoria|acceso|persist|relativ|causal|reorganiz|interferencia|reduc|fase|distribu|entrelaz'
            picked=[{'text_node_index':i,'text':t}for i,t in enumerate(paragraphs)if re.search(keys,t,re.I)][:100]
            row={'path':str(p),'sha256':sha(b),'bytes':len(b),'effective_access':'OPENED_DOCX_XML_DIRECTED_TEXT_NODES','document_xml_sha256':sha(xml),'total_text_nodes':len(paragraphs),'selected_nodes':picked,'scope':'Directed methodological reading only; not native experimental proof.'};rows.append(row)
    base=VITAL/'DEE thinking/casos practicos'
    archives=[base/'CPC7_MENTE_DEE_ACCESO_SELECTIVO_Y_APRENDIZAJE_CONTINUO_RESULTADOS.zip',base/'trabajo_codex/CPC8/runs/resultados/CPC8_ORGANIZACION_COGNITIVA_NATIVA_APRENDIZAJE65_RESULTADOS.zip']
    archives+=list((base/'trabajo_codex/CPC8/runs/historico').glob('*65164*.zip'))
    for p in archives:
        if not p.is_file():rows.append({'path':str(p),'status':'NOT_FOUND'});continue
        selected=[]
        with zipfile.ZipFile(p)as z:
            candidates=[n for n in z.namelist()if n.endswith(('.md','.json','.py'))and any(k in n for k in('LECTURA_PROVISIONAL','MATRIZ_CAPACIDADES','RETENCION','REGULACION','DIAGNOSTICOS','SOC_I21','MAPA_CPC','ARQUITECTURA'))and z.getinfo(n).file_size<600000]
            # Member bytes are actually opened, hash checked and indexed. Select
            # a bounded directed set, never claim the whole archive was read.
            for n in candidates[:14]:
                b=z.read(n);selected.append({'member':n,'sha256':sha(b),'bytes':len(b),'excerpt':b.decode('utf8',errors='replace')[:4500]})
        rows.append({'path':str(p),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size,'effective_access':'OPENED_ZIP_AND_LISTED_SELECTED_MEMBERS','selected_members':selected})
    result={'schema':'DCS1.1.directed_sources.v1','root':str(VITAL),'sources':rows,'conversations':'No private ChatGPT conversation access used. Prompts in current user request are accessible instructions; corpus references do not establish transcript access.','limits':'Directed text excerpts are not a claim of full reading. Missing4.5books remain absent; installed executable contracts and technical4.5files are the instrument authority.'}
    target=out/'FUENTES_ABIERTAS.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'sources':len(rows),'file':str(target)}))
if __name__=='__main__':main()
