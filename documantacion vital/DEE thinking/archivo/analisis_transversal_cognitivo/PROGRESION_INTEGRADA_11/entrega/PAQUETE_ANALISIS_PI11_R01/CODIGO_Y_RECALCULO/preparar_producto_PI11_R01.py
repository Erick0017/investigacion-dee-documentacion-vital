"""Pure creation of product-only PI11 adapters, never touches the product.

Source diagnostic R01 code remains literal. Generated code is prepared under
this codigo directory for an explicit isolated interface test and later CAS
deployment only if Root's scientific gates are met.
"""
from pathlib import Path
import argparse,ast,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema'
OLD=P.with_name('PROGRESION_INTEGRADA_10')/'codigo'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def emit(root,relative,text):
    ast.parse(text);out=root/relative;out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():need(out.read_text('utf-8-sig')==text,'Existing different prepared product source preserved')
    else:out.write_text(text,'utf8')
    return {'file':relative,'source':str(out),'bytes':out.stat().st_size,'sha256':sha(out)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-system',type=Path,required=True);ap.add_argument('--revision',choices=('R01','R02'),default='R02');a=ap.parse_args();source=a.source_system.resolve(strict=True)
    need(source.parent.parent==(P/'estados').resolve()and source.name=='sistema'and not(source/'estado/ACTIVO.json').exists(),'Explicit PI11 diagnostic source code only')
    for p in(source,*source.parents):need(not p.is_symlink()and not(getattr(p.lstat(),'st_file_attributes',0)&1024),'No reparse source')
    out=H/('PRODUCTO_PREPARADO_'+a.revision);rows=[]
    file=source/'app/mundo_genesis_apd05.py';text=file.read_text('utf-8-sig')
    old='        pi10_transport.install(self.a)\n        from capacidades import pi11_identidad_heredada_R01 as pi11_identity\n        pi11_identity.install(self.a)\n'
    new='        from capacidades import pi11_identidad_heredada_R02 as pi11_identity\n        pi11_identity.install(self.a)\n        pi10_transport.install(self.a)\n'
    need(text.count(old)==1,'Exact scientific R01 install ordering anchor');text=text.replace(old,new)
    for method in('validate','execute'):
        anchor='    def '+method+'(self,payload):\n        row=self._eci01_row(payload)\n'
        need(text.count(anchor)==1,'Exact owner public validation anchor')
        extra='        from capacidades import pi11_identidad_heredada_R02 as pi11_identity\n        pi11_identity.validate_external(self.a,row,payload=payload)\n'
        text=text.replace(anchor,anchor+extra)
    rows.append(emit(out,'app/mundo_genesis_apd05.py',text))
    rows.append(emit(out,'capacidades/pi11_identidad_heredada_R02.py',(H/'pi11_identidad_heredada_R02.py').read_text('utf-8-sig')))
    source_c2c=S/'app/pi10_identidad_c2c_R02.py';text=source_c2c.read_text('utf-8-sig')
    old="LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'"
    new="LIFE=json.loads((Path(__file__).resolve().parents[1]/'contratos/PI11_USO_OPERATIVO_R01.json').read_text('utf-8-sig'))['life_id']"
    need(text.count(old)==1,'Exact C2C current identity anchor');text=text.replace(old,new).replace('pi10_permiso_operativo_R02','pi11_identidad_heredada_R02').replace('DEE.PI10.C2C.','DEE.PI11.C2C.')
    rows.append(emit(out,'app/pi11_identidad_c2c_R01.py',text))
    launcher=(source/'gestionar.py').read_text('utf-8-sig')
    anchor="if len(sys.argv)>1 and sys.argv[1]in('pi10-estado','pi10-usar'):"
    need(launcher.count(anchor)==1,'Existing manager public command anchor')
    block="if len(sys.argv)>1 and sys.argv[1]in('pi11-estado','pi11-usar'):\n    helper=Path(__file__).resolve().parent/'app/pi11_gestor_publico_R01.py'\n    import runpy\n    runpy.run_path(str(helper),run_name='__main__')\n    raise SystemExit(0)\n\n"
    rows.append(emit(out,'gestionar.py',launcher.replace(anchor,block+anchor)))
    rows.append(emit(out,'app/pi11_gestor_publico_R01.py',(H/'pi11_gestor_publico_R01.py').read_text('utf-8-sig')))
    manifest={'schema':'DEE.PI11.prepared_product_code.'+a.revision,'source_system':str(source),'Native_imported':False,'Native_ticks':0,'product_written':False,'files':rows,'diagnostic_R01_sources_literal_unchanged':True,'must_test_before_deployment':True}
    mf=out/'CODIGO_PREPARADO.json'
    if mf.exists():need(json.loads(mf.read_text('utf8'))==manifest,'Existing prepared product manifest changed')
    else:mf.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
