"""Prepare exact mature Discovery source public reopening0; no Native."""
from pathlib import Path
import ast,hashlib
H=Path(__file__).resolve().parent
def once(t,a,b):
 if t.count(a)!=1:raise ValueError('Exact source-zero anchor changed '+a[:80])
 return t.replace(a,b)
def main():
 old=H/'reabrir_producto_D_PI09_0_R01.py';out=H/'reabrir_SOURCE_D_PI09_0_R01.py'
 if out.exists():raise FileExistsError('Prior source-zero revision preserved')
 t=old.read_text('utf-8-sig').replace("S=C/'sistema';RP=","S=P/'estados/DISCOVERY/sistema';RP=")
 t=once(t,"output=P/'control'/('REAPERTURA_SELECCIONADA_D_PRODUCTO_PI09.json'if a.seleccionado else'REAPERTURA_D_PRODUCTO_PI09.json')","output=P/'control/REAPERTURA_SOURCE_D_PI09_R01.json'")
 t=once(t,"need((read(S/'estado/ACTIVO.json')['life_id']==LIFE)==a.seleccionado,'Selected/unselected phase differs')","need(not a.seleccionado and not(S/'estado/ACTIVO.json').exists(),'Only isolated mature Discovery, never a selected world')")
 t=t.replace("nativecard=S/'estado/vidas'/PARENT/'VIDA.json';parent=read(nativecard);protected={str(p):sha(p)for p in(nativecard,S/parent['snapshot'])}","nativecard=C/'sistema/estado/vidas'/PARENT/'VIDA.json';parent=read(nativecard);protected={str(p):sha(p)for p in(nativecard,C/'sistema'/parent['snapshot'])}")
 start=t.index(" profile=load('PI09_D_public_profile_probe'");end=t.index(' # Reuse the already used public client',start)
 t=t[:start]+" codefile=S.parent/'SISTEMA_CODIGO_PI09.json';code=read(codefile);sourcefiles=[codefile,*[S/r['file']for r in code['files']]];codebefore={str(p):sha(p)for p in sourcefiles};probes=[]\n"+t[end:]
 t=t.replace('client.LIFE=LIFE','client.LIFE=LIFE;client.S=S')
 t=t.replace("tag='PI09_D_PRODUCT0_SELECTED_R01'if a.seleccionado else'PI09_D_PRODUCT0_UNSELECTED_R01'","tag='PI09_D_SOURCE0_R01'")
 t=t.replace("'DEE.PI09.D.product_public0.reopening.R01'","'DEE.PI09.D.mature_source.public_reopening0.R01'")
 t=t.replace("'material_public_use_executed':False}","'material_public_use_executed':False,'source_code_unchanged':codebefore=={p:sha(Path(p))for p in codebefore},'all_scientific_metadata_literal_unchanged':valid,'current_principal_unchanged':unchanged,'causal_prefix_equal':fields['causal_prefix_sha256']}")
 t=once(t,"with output.open('x',encoding='utf8')as f:","need(result['source_code_unchanged'],'Frozen source code changed during zero reopening')\n with output.open('x',encoding='utf8')as f:")
 ast.parse(t);out.write_text(t,'utf8');print(out.name,hashlib.sha256(out.read_bytes()).hexdigest())
if __name__=='__main__':main()
