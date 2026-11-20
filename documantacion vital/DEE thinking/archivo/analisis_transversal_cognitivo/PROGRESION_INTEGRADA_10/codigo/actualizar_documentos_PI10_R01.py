"""Root-only surgical staging/publication of the same two existing DOCX.

Default/check-facts are read-only. No DEE/Word import and no inferred result.
Requires external real closed facts; marker acknowledgement is necessary for
the first authoring command. Preserve chapters1..54 and every appendix as
literal XML. Do not execute --author/--publish before Root's documents marker.
"""
from pathlib import Path
from datetime import datetime,timezone
from xml.sax.saxutils import escape
import argparse,copy,hashlib,importlib.util,json,os,re,shutil,zipfile
import xml.etree.ElementTree as ET

P=Path(__file__).resolve().parents[1];R=P.parents[2];C=R/'DEE Cognitive 2.0';D=P/'documentos'
MAN=C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'
COMP=R/'CPC - Experimentos y mecanismos/COMPENDIO_MAESTRO_DE_MECANISMOS_Y_RESULTADOS_DEE.docx'
BASE=D/'base_1_38';BASE_MANIFEST=BASE/'FUENTES_ORIGINALES_1_38_PI10_R01.json'
PINS={MAN.name:'d1da770ece0a5c2e1c830d2501c0b6a203def32664bbb9dd35bb2663ba73cd6f',COMP.name:'465da0044a20287fe8dec8ca6084e98da6890e6ab03cbb0d8c3fff0810aa4d5d'}
HELPER=P/'codigo/OOXML_HELPERS_PI08_B_LITERAL.py';HELPER_SHA='ef5a23de5875c8ccd352f961417adfe068a190bdf46c131aeaf2d183f2790358'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
TITLE='55 PI10 Consulta adaptativa y dos trazas nativas';ANCHOR='DEE_PI10_CAP55'
COMP_TITLE='PI10 Consulta adaptativa y dos trazas nativas';COMP_ANCHOR='DEE_PI10_COMPENDIO'
STAGE=D/'edicion_1_39';STRUCTURE=D/'ESTRUCTURA_EDICION_1_39_PI10_R01.json';PUBLICATION=D/'PUBLICACION_EDICION_1_39_PI10_R01.json'
CONTROL_LABELS={'Documento','Corte de liberación registrado','Base principal','Estado de esta edición'}
def require(ok,msg):
    if not ok:raise ValueError(msg)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text('utf-8-sig'))
def info(path):
    p=Path(path);return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def regular(path):
    p=Path(path).resolve(strict=True)
    for node in(Path(path),*Path(path).parents):require(not node.is_symlink()and not(getattr(node.lstat(),'st_file_attributes',0)&1024),'No linked document/evidence path')
    require(p.is_file(),'Existing regular file required');return p
def put(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with Path(path).open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def helper(anchor):
    require(sha(HELPER)==HELPER_SHA,'Literal OOXML helper changed')
    spec=importlib.util.spec_from_file_location('PI10_literal_OOXML_helper',HELPER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ANCHOR=anchor;return m
def source_check():
    manifest=read(BASE_MANIFEST);require(manifest.get('authoring_executed')is False and manifest.get('published')is False,'Literal source backups, not a prior publication')
    for source in(MAN,COMP):
        regular(source);regular(BASE/source.name)
        require(sha(source)==PINS[source.name]==sha(BASE/source.name),'Current/source backup CAS differs; preserve and inspect')
        with zipfile.ZipFile(source)as z:require(z.testzip()is None,'Source DOCX member CRC failure')
def nonempty(value):return isinstance(value,str)and bool(value.strip())
def validate_facts(f):
    require(f.get('schema')=='DEE.PI10.final_document_facts.R01'and f.get('internal_edition')=='1.39'and f.get('closed_for_authoring')is True,'Real final facts, edition1.39 and explicit closure required')
    require(datetime.fromisoformat(f['cut_utc'].replace('Z','+00:00')).tzinfo is not None,'Timezone-aware actual cut required')
    for k in('description',):require(nonempty(f.get(k)),'Actual nonempty description')
    front=f['front']
    for k in('edition_summary','principal_summary','functional_summary','conservation_summary','resume_summary','coverage_summary'):require(nonempty(front.get(k)),'Real explained front field required: '+k)
    require(set(front.get('control_table',{}))==CONTROL_LABELS and all(nonempty(v)for v in front['control_table'].values()),'Exactly four current documentary-control values required')
    for key in('manual_sections','compendium_sections'):
        sections=f.get(key);require(isinstance(sections,list)and 1<=len(sections)<=10,'Actual1..10 explained sections required: '+key)
        for section in sections:
            require(nonempty(section.get('heading'))and isinstance(section.get('paragraphs'),list)and section['paragraphs']and all(nonempty(v)for v in section['paragraphs']),'Empty scientific sections rejected')
            require(all(nonempty(v)for v in section.get('sources',[])),'No empty source labels')
    def unresolved(v):
        if isinstance(v,str):require('{{'not in v and not re.search(r'\bROOT:',v),'Editorial placeholders prohibited')
        elif isinstance(v,dict):
            for x in v.values():unresolved(x)
        elif isinstance(v,list):
            for x in v:unresolved(x)
    unresolved({k:f[k]for k in('front','manual_sections','compendium_sections')})
    selected=f['selected_life'];require(selected.get('N')==67 and type(selected.get('T'))is int and selected['T']>=922371 and nonempty(selected.get('life_id')),'Actual selected cut required; no assumed PI10 adoption')
    require(re.fullmatch('[0-9a-f]{64}',selected.get('snapshot_sha256',''))is not None,'Actual selected snapshot hash required')
    active=read(C/'sistema/estado/ACTIVO.json');require(active['life_id']==selected['life_id'],'Facts must describe actual current selection')
    card=read(C/'sistema/estado/vidas'/selected['life_id']/'VIDA.json')
    require(card['physical']['N']==selected['N']and card['physical']['tick']==selected['T']and card['snapshot_sha256']==selected['snapshot_sha256'],'Facts/current stable life card differ')
    require(sha(C/'sistema'/card['snapshot'])==selected['snapshot_sha256'],'Current complete native snapshot locator/hash differs')
    require(isinstance(f.get('evidence'),list)and f['evidence'],'Real decisive evidence references required')
    for ref in f['evidence']:
        path=regular(Path(ref['path']));require(path.is_relative_to(R.resolve())and sha(path)==ref['sha256'],'Actual DEE evidence reference changed')
    source_check()
def edit_body(raw,f,manual):
    h=helper(ANCHOR if manual else COMP_ANCHOR);pre,parts,post,_=h.body_parts(raw);infos=[h.info(x,pre)for x in parts]
    bookmark_ids=[int(x)for x in re.findall(rb'<w:bookmarkStart\b[^>]*w:id="(\d+)"',raw)];new_id=max(bookmark_ids,default=0)+1
    if manual:
        first=next(i for i,(_,t,s)in enumerate(infos)if s=='Ttulo1'and re.match(r'^1(?:\.\s|\s)',t))
        appendix=next(i for i,(_,t,s)in enumerate(infos)if s=='Ttulo1'and t.startswith('Apéndice A'))
        require(any(s=='Ttulo1'and t.startswith('54 PI09 ')for _,t,s in infos),'Complete prior chapter54 required')
        require(not any(s=='Ttulo1'and t.startswith('55 ')for _,t,s in infos),'PI10 chapter already present; no duplicate authoring')
        old_history=b''.join(parts[first:]);front=f['front']
        mapping={8:'DEE thinking 4.5.0 | DEE Cognitive 2.0 | Edición documental 1.39 | DCS11-MM-001',9:front['edition_summary'],13:front['principal_summary'],14:front['functional_summary'],15:front['conservation_summary'],16:front['resume_summary'],18:'Funciones heredadas: evidencia histórica por vida y corte; continuidad actual en el capítulo 55',26:front['coverage_summary']}
        require('Edición documental 1.38'in infos[8][1]and'DCS11-MM-001'in infos[8][1],'Exact old front anchor required')
        for index,text in mapping.items():require(index<first,'Front edit escaped history');parts[index]=h.whole_paragraph(parts[index],pre,text)
        replacements={}
        for row in infos[23][0].findall('.//{'+W+'}tr'):
            cells=row.findall('{'+W+'}tc')
            if len(cells)!=2:continue
            label=''.join(t.text or ''for t in cells[0].iter('{'+W+'}t'))
            if label in CONTROL_LABELS:
                texts=list(cells[1].iter('{'+W+'}t'));require(len(texts)==1,'Split control cell; inspect before editing');replacements[texts[0].text or '']=front['control_table'][label]
        require(len(replacements)==4,'All four actual control-cell anchors required');parts[23],count=h.replace_texts(parts[23],replacements);require(count==4,'Control table anchor counts differ')
        toc=next(i for i,(_,t,s)in enumerate(infos[:first])if t=='54 PI09 Regulación integrada, reproducción y límites')
        additions={toc+1:h.paragraph(TITLE,'TOCline',link=ANCHOR),appendix:h.render_sections(f['manual_sections'],'55',TITLE,new_id)}
        out=pre+b''.join(additions.get(i,b'')+x for i,x in enumerate(parts))+post
        require(b''.join(parts[first:])==old_history,'Old chapters1..54 or appendices were changed')
        proof={'old_history_XML_sha256':hashlib.sha256(old_history).hexdigest(),'old_chapters1_to54_and_appendices_literal':True,'front_modified_children':list(mapping)+[23],'new_bookmark':ANCHOR}
    else:
        require(not any(s=='Ttulo1'and t==COMP_TITLE for _,t,s in infos),'PI10 compendium section already present')
        old=b''.join(parts);index=next((i for i,(node,_,_)in enumerate(infos)if node.tag=='{'+W+'}sectPr'),len(parts))
        toc=next(i for i,(_,t,s)in enumerate(infos)if s=='Ttulo1'and t=='Índice navegable')
        first_after_toc=next(i for i,(_,_,s)in enumerate(infos)if i>toc and s=='Ttulo1')
        # Compendium has no TOCline/Source style: use its existing default
        # instead of adding unresolved style references or changing old styles.
        chapter=h.render_sections(f['compendium_sections'],'PI10',COMP_TITLE,new_id).replace(b'<w:pStyle w:val="Source"/>',b'<w:pStyle w:val="Normal"/>')
        additions={first_after_toc:h.paragraph(COMP_TITLE,None,link=COMP_ANCHOR),index:chapter}
        out=pre+b''.join(additions.get(i,b'')+x for i,x in enumerate(parts))+additions.get(len(parts),b'')+post
        require(b''.join(parts)==old,'Old compendium body changed')
        proof={'old_body_XML_sha256':hashlib.sha256(old).hexdigest(),'old_body_literal':True,'index_entry_added':True,'new_bookmark':COMP_ANCHOR}
    ET.fromstring(out);return out,proof
def build(source,target,f,manual):
    with zipfile.ZipFile(source)as zin:
        require(zin.testzip()is None,'Source CRC failure');members=zin.infolist();old={i.filename:zin.read(i)for i in members}
    document,body_proof=edit_body(old['word/document.xml'],f,manual);changes={'word/document.xml':document};core=old['docProps/core.xml'].decode('utf8')
    values={'cp:version':'1.39','cp:revision':'39','dcterms:modified':f['cut_utc'],'dc:description':f['description']}
    if manual:values['dc:title']='DEE Cognitive 2.0 Manual Maestro Edición 1.39 PI10'
    for tag,value in values.items():
        core,count=re.subn(r'(<'+re.escape(tag)+r'(?:\s[^>]*)?>).*?(</'+re.escape(tag)+r'>)',lambda m:m[1]+escape(value)+m[2],core,flags=re.S);require(count==1,'Missing/duplicate document property '+tag)
    changes['docProps/core.xml']=core.encode('utf8')
    if 'word/settings.xml'in old:changes['word/settings.xml']=helper(ANCHOR).settings_edit(old['word/settings.xml'])
    if manual:
        for name,data in old.items():
            if re.fullmatch(r'word/(?:header|footer)\d+\.xml',name):
                value=data.replace(b'1.38',b'1.39')
                if value!=data:changes[name]=value
    for name,data in changes.items():ET.fromstring(data)
    with zipfile.ZipFile(target,'x')as zout:
        for member in members:zout.writestr(copy.copy(member),changes.get(member.filename,old[member.filename]))
    with zipfile.ZipFile(target)as z:
        require(z.testzip()is None,'Output CRC failure')
        for name,value in old.items():
            if name.endswith('.xml'):ET.fromstring(z.read(name))
            if name not in changes:require(z.read(name)==value,'Unapproved package member changed')
    return {'source':info(source),'backup':info(BASE/source.name),'output':info(target),'modified_members':list(changes),'unchanged_members':[name for name in old if name not in changes],'structure_valid':True,'visual_QA_not_implied':True,**body_proof}
def main(args):
    if not(args.author or args.publish or args.check_facts):
        print(json.dumps({'mode':'READ_ONLY_PLAN','edition':'1.39','sources':[info(s)for s in(MAN,COMP)],'backup_manifest':info(BASE_MANIFEST),'chapter':'55','Native_imported':False,'authoring_executed':False},ensure_ascii=False));return
    require(args.facts is not None,'External real closed facts required');facts=read(args.facts);validate_facts(facts)
    if args.check_facts:print(json.dumps({'facts_valid':True,'edition':'1.39','read_only':True,'Native_imported':False}));return
    if args.author:
        require(args.marker_confirmed and facts.get('actual_authoring_marker_registered_by_root')is True,'Root must first execute the documents edit marker for these same two outputs; this builder never repeats it')
        require(not STAGE.exists()and not STRUCTURE.exists(),'Prior/partial staging preserved; no overwrite');STAGE.mkdir(parents=True)
        rows=[build(s,STAGE/s.name,facts,is_manual)for s,is_manual in((MAN,True),(COMP,False))]
        put(STRUCTURE,{'schema':'DEE.PI10.complete_DOCX_structural_staging.R01','facts':info(args.facts),'source_backup_manifest':info(BASE_MANIFEST),'rows':rows,'internal_edition':'1.39','published':False,'Native_imported':False,'visual_review_required':True});print(json.dumps({'staged':str(STAGE),'documents':2,'old_history_preserved':True,'published':False}));return
    proof=read(STRUCTURE);require(proof['facts']['sha256']==sha(args.facts),'Facts changed after authoring')
    require(args.visual_proof is not None,'Actual render/review proof or explicitly documented renderer limitation required before publication')
    visual=read(args.visual_proof);require(visual.get('status')in('rendered_and_reviewed','render_blocked_explicit_limitation')and visual.get('documents'),'Explicit actual visual-review status required')
    hashes={row['sha256']for row in visual['documents']};require({r['output']['sha256']for r in proof['rows']}<=hashes,'Visual proof must bind both staged DOCX hashes')
    if visual['status']=='render_blocked_explicit_limitation':require(args.accept_visual_limitation and nonempty(visual.get('limitation')),'Root must explicitly acknowledge the actual renderer limitation')
    require(not PUBLICATION.exists(),'Existing publication is preserved')
    for row in proof['rows']:
        require(sha(row['source']['path'])==row['source']['sha256']and sha(row['output']['path'])==row['output']['sha256'],'Document CAS changed before publication')
        pending=Path(row['source']['path']+'.PI10.pending');require(not pending.exists(),'Unresolved pending publication preserved');shutil.copyfile(row['output']['path'],pending);require(sha(pending)==row['output']['sha256'],'Pending publication bytes differ')
    put(D/'PUBLICACION_PI10_EN_CURSO_R01.json',{'schema':'DEE.PI10.two_document_publication_intent.R01','facts':info(args.facts),'structure':info(STRUCTURE),'visual':info(args.visual_proof),'source_files':[r['source']for r in proof['rows']],'target_files':[r['output']for r in proof['rows']]})
    for row in proof['rows']:
        source=Path(row['source']['path']);require(sha(source)==row['source']['sha256'],'Concurrent source edit during publication');os.replace(Path(str(source)+'.PI10.pending'),source);require(sha(source)==row['output']['sha256'],'Published file identity differs')
    put(PUBLICATION,{'schema':'DEE.PI10.actual_complete_DOCX_publication.R01','at':datetime.now(timezone.utc).isoformat(),'internal_edition':'1.39','facts':info(args.facts),'source_backup_manifest':info(BASE_MANIFEST),'structural_proof':info(STRUCTURE),'visual_proof':info(args.visual_proof),'visual_status':visual['status'],'rows':[{**row,'published':info(row['source']['path'])}for row in proof['rows']],'Native_imported':False})
    print(json.dumps({'published':True,'documents':2,'internal_edition':'1.39','manifest':str(PUBLICATION),'visual_status':visual['status']}))
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);group=ap.add_mutually_exclusive_group();group.add_argument('--author',action='store_true');group.add_argument('--publish',action='store_true');group.add_argument('--check-facts',action='store_true');ap.add_argument('--facts',type=Path);ap.add_argument('--marker-confirmed',action='store_true');ap.add_argument('--visual-proof',type=Path);ap.add_argument('--accept-visual-limitation',action='store_true');main(ap.parse_args())
