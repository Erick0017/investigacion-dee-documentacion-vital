"""Read primary artifact identities; copy only selected inputs to the new system."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import argparse,hashlib,json,os,platform,sys,time,zipfile,xml.etree.ElementTree as ET,shutil
sys.stdout.reconfigure(encoding='utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
def filehash(f):
    h=hashlib.sha256()
    with f.open('rb')as s:
        for b in iter(lambda:s.read(1048576),b''):h.update(b)
    return h.hexdigest()
def put(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True);p.add_argument('--root',type=Path,required=True);a=p.parse_args();w=a.workspace.resolve();r=a.root.resolve();proj=json.loads((r/'PROYECTO.json').read_bytes());b=proj['budget'];elapsed=time.perf_counter()-b['start_monotonic']/b['monotonic_frequency']
    if elapsed<0 or elapsed>b['budget_seconds']:raise RuntimeError('Invalid or exhausted monotonic campaign budget')
    for folder in ['sistema/runtime','sistema/app','sistema/capacidades','sistema/organizaciones','sistema/contratos','sistema/estado/vidas','sistema/estado/checkpoints','sistema/pruebas_minimas','sistema/documentacion','laboratorio/candidatos','laboratorio/pruebas_integracion','laboratorio/diagnosticos','evidencia/informes','evidencia/telemetria','evidencia/controles','evidencia/reservas','evidencia/checkpoints_diagnosticos','evidencia/genealogia','evidencia/verificaciones','entregas']:(r/folder).mkdir(parents=True,exist_ok=True)
    source=w/'documantacion vital/DEE thinking';c=source/'casos practicos/trabajo_codex';out=c/'CPC9/runs/resultados';files=[out/'DEE_COGNITIVE_CORE_CPC01_A_CPC08.zip',out/'CPC9_ONTOGENIA_SEMANTICA_NATIVA65_RESULTADOS.zip',out/'CPC9_AUDITORIA_CIENTIFICA_ESENCIAL.zip',source/'4.5/DEE_THINKING_4_5_0_COMPILACION_Y_VALIDACION_RESULTADOS.zip'];entries=[];member_index=[];docs=[]
    for f in files:
        rec={'path':str(f),'bytes':f.stat().st_size,'sha256':filehash(f),'effective_access':'OPENED_ZIP'}
        with zipfile.ZipFile(f)as z:
            rec.update(members=len(z.infolist()),expanded_bytes=sum(i.file_size for i in z.infolist()));members=[{'name':i.filename,'bytes':i.file_size,'compressed_bytes':i.compress_size}for i in z.infolist()];member_index.append({'archive':f.name,'sha256':rec['sha256'],'members':members})
            for i in z.infolist():
                if i.filename.lower().endswith('.docx')and('4_5'in i.filename.lower()or'4.5'in i.filename.lower()):docs.append({'archive':str(f),'member':i.filename,'sha256':sha(z.read(i))})
            if f.name.startswith('DEE_THINKING_4_5_0'):
                matches=[i for i in z.infolist()if i.filename.endswith('/wheel/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl')]
                if len(matches)!=1:raise ValueError('Official wheel member is ambiguous')
                data=z.read(matches[0]);expected='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
                if sha(data)!=expected:raise ValueError('Official product wheel identity mismatch')
                target=r/'sistema/runtime'/Path(matches[0].filename).name
                if target.exists()and target.read_bytes()!=data:raise FileExistsError('Different system wheel already present')
                target.write_bytes(data);rec['copied_wheel']={'member':matches[0].filename,'sha256':expected,'destination':str(target.relative_to(r))}
                for name in ['LEEME.md','PRODUCT_CONTRACT.json','VALIDATION_REPORT.json','API_DIFF.json','MIGRATION_NOTES.md','BUILD_INFO.json','MATRIZ_CAPACIDADES_CPC.json']:
                    candidates=[i for i in z.infolist()if Path(i.filename).name==name and i.filename.count('/')<=2]
                    for i in candidates:
                        d=z.read(i);t=r/'evidencia/genealogia/producto45'/name;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(d)
        entries.append(rec)
    for f in source.rglob('*.docx'):
        if '4_5'in f.name or'4.5'in f.name:docs.append({'path':str(f),'sha256':filehash(f),'bytes':f.stat().st_size})
    references=['DEE_thinking_4_5_0_Libro_Blanco_y_Manual_Tecnico.docx','DEE_thinking_4_5_0_Maestro_Arquitectura_Reconstruccion.docx'];status=[]
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for name in references:
        rows=[x for x in docs if Path(x.get('path',x.get('member',''))).name==name]
        if not rows:status.append({'name':name,'status':'NO_ENCONTRADO_EN_RAIZ_Y_PAQUETES_INSPECCIONADOS','fallback':'Executable installed contract and product technical files'});continue
        for x in rows:
            if'path'in x:data=Path(x['path']).read_bytes()
            else:
                with zipfile.ZipFile(x['archive'])as z:data=z.read(x['member'])
            import io
            with zipfile.ZipFile(io.BytesIO(data))as z:tree=ET.fromstring(z.read('word/document.xml'))
            paragraphs=[''.join(p.itertext())for p in tree.findall('.//w:p',ns)]
            text='\n'.join(paragraphs);dest=r/'evidencia/genealogia/documentos'/name.replace('.docx','.texto.txt');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding='utf8');status.append({**x,'name':name,'status':'TEXTO_INTEGRO_EXTRAIDO_PENDIENTE_LECTURA','text_file':str(dest.relative_to(r)),'characters':len(text)})
    put(r/'evidencia/genealogia/INVENTARIO_INICIAL.json',{'timestamp':datetime.now(timezone.utc).isoformat(),'sources':entries,'manuals':status,'elapsed_seconds':elapsed,'python_for_inventory':sys.version,'platform':platform.platform(),'conversations':'Only files/exports actually opened may be counted; none opened yet.'});put(r/'laboratorio/campanas/CONSOLIDACION_1_1/INDICE_MIEMBROS_ORIGINALES.json',member_index)
    put(r/'REANUDACION.json',{'status':'ACTIVA','budget':b,'elapsed_seconds':elapsed,'completed':'Artifact inventory and identity of official copied wheel','next':'Verify isolated CPython, recover complete learned checkpoint, implement the minimal life manager','no_background_authorization':True})
    print(json.dumps({'status':'PASS','sources':entries,'manuals':status,'elapsed_seconds':elapsed},ensure_ascii=False))
if __name__=='__main__':main()
