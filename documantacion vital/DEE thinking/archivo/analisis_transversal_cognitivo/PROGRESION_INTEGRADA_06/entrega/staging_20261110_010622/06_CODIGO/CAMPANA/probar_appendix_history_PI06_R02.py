"""Test the editorial selector, with in-memory XML and literal real DOCX reads.

Never authors/publishes a DOCX and never imports or executes DEE.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';D=P/'documentos';tests=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def test(name,ok):
 if not ok:raise AssertionError(name)
 tests.append({'name':name,'passed':True})
oldfile=H/'publicar_documentos_PI06_literal_R01.py';newfile=H/'publicar_documentos_PI06_literal_R02.py'
old=load(oldfile,'PI06_publisher_R01_readonly_test');new=load(newfile,'PI06_publisher_R02_readonly_test')
def function_asts(file):return {x.name:ast.dump(x,include_attributes=False)for x in ast.parse(file.read_bytes()).body if isinstance(x,ast.FunctionDef)}
oldf=function_asts(oldfile);newf=function_asts(newfile)
test('only_appendix_history_function_changed',set(oldf)==set(newf)and[n for n in oldf if oldf[n]!=newf[n]]==['appendix_history'])
stage=json.loads((D/'ACTUALIZACION_DOCUMENTAL_PI06_1_33.json').read_text('utf8'));original=Path(stage['prior_literal_backups']['Manual']['path']);staged=Path(stage['Manual']['output'])
critical=[original,staged,Path(stage['Manual']['source']),Path(stage['Compendium']['source']),Path(stage['Compendium']['output']),oldfile]
before={str(p):sha(p)for p in critical}
old_wrong=old.appendix_history(original);new_wrong=old.appendix_history(staged)
test('R01_reproduces_wrong_index_range',len(old_wrong)==1436 and len(new_wrong)==1476 and old_wrong!=new_wrong)
previous=new.appendix_history(original);current=new.appendix_history(staged)
test('real_appendix_nonempty',len(previous)>1)
test('real_appendix_complete_literal_elements_equal',previous==current)
test('historical_chapters1_48_still_literal_equal',new.history1_48(original)==new.history1_48(staged))
W=new.W;E=new.E
def paragraph(text,style=None):
 p=E.Element(W+'p')
 if style is not None:E.SubElement(E.SubElement(p,W+'pPr'),W+'pStyle').set(W+'val',style)
 E.SubElement(E.SubElement(p,W+'r'),W+'t').text=text
 return p
title='Apéndice A. Inventario histórico de las 73 entradas'
def xml(elements):
 root=E.Element(W+'document',nsmap={'w':W[1:-1]});body=E.SubElement(root,W+'body')
 for e in elements:body.append(e)
 return E.tostring(root)
class FakeZip:
 data=b''
 def __init__(self,*args,**kw):pass
 def __enter__(self):return self
 def __exit__(self,*args):return False
 def read(self,name):
  if name!='word/document.xml':raise AssertionError('Only document XML read')
  return self.data
real_zip=new.zipfile.ZipFile
try:
 new.zipfile.ZipFile=FakeZip
 FakeZip.data=xml([paragraph(title),paragraph('49 PI06','Heading1'),paragraph('New chapter'),paragraph(title,'Heading1'),paragraph('Old appendix'),E.Element(W+'sectPr')])
 selected=new.appendix_history('IN_MEMORY_ONLY')
 test('index_duplicate_not_selected',len(selected)==3 and E.fromstring(selected[1]).find('.//'+W+'t').text=='Old appendix')
 for style in('Heading1','heading1','Ttulo1','Titulo1','Title1'):
  FakeZip.data=xml([paragraph(title),paragraph(title,style),paragraph('body')]);test('recognized_heading_style_'+style,len(new.appendix_history('IN_MEMORY_ONLY'))==2)
 for name,elements in(('TOC_only',[paragraph(title)]),('no_exact_heading',[paragraph(title+' other','Heading1')]),('duplicate_H1',[paragraph(title,'Heading1'),paragraph(title,'Heading1')])):
  FakeZip.data=xml(elements)
  try:new.appendix_history('IN_MEMORY_ONLY')
  except ValueError:test('fail_closed_'+name,True)
  else:raise AssertionError('Ambiguous or absent real Appendix heading accepted')
finally:new.zipfile.ZipFile=real_zip
after={str(p):sha(p)for p in critical};test('all_original_staged_DOCX_and_R01_unchanged',before==after)
out=P/'control/APPENDIX_HISTORY_EDITORIAL_PI06_R02_VERIFICADO.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI06.editorial_appendix_selector_fix.R02','cause':'R01 chose the first matching Appendix A text in the table of contents, so its range incorrectly included the new chapter49. R02 requires exactly one actual Heading1 Appendix A and compares every element from that heading through the body end literally.',
 'tests':tests,'passed':len(tests),'R01_source_sha256':sha(oldfile),'R02_source_sha256':sha(newfile),'old_wrong_range_counts':[len(old_wrong),len(new_wrong)],'actual_appendix_elements':len(previous),
 'actual_appendix_literal_equal':True,'chapters1_48_literal_equal':True,'original_and_staged_before':before,'original_and_staged_after':after,'Native_executed':False,'DOCX_authored_or_modified':False,'product_modified':False,
 'equality_requirement_not_weakened':True,'visual_QA':False},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':sha(out),'passed':len(tests),'actual_appendix_elements':len(previous),'R02_sha256':sha(newfile)}))
