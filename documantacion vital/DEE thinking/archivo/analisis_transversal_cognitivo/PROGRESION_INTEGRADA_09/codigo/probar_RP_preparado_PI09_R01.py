"""Actual prepared capsule/analysis interface verification, stdlib only."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';STAGE=H/'RP_INCORPORACION_PI09_R01_PREPARADA';OUT=H/'PRUEBA_RP_PREPARADO_PI09_R01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 if OUT.exists():raise FileExistsError('Prueba anterior preservada')
 OUT.mkdir();file=C/'reproducibilidad/reproducir.py';spec=importlib.util.spec_from_file_location('RP_actual_stdlib_validation',file);rp=importlib.util.module_from_spec(spec);spec.loader.exec_module(rp)
 recipe=json.loads((STAGE/'receta.json').read_text('utf8'));rp.resource=lambda entry:STAGE/('capsule'if '/codigo_preservado/'in entry['product_relative']else'analysis')
 cap=rp.capsule_check({'product_relative':'reproducibilidad/codigo_preservado/X','manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(STAGE/'capsule/SISTEMA_CODIGO.json')})
 analysis=rp.recipe_analysis_check(recipe)
 process=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(STAGE/'analysis/RECALCULAR_RP_PI09_R01.py'),'--root',str(STAGE/'analysis'),'--out-dir',str(OUT/'recalculo')],capture_output=True,text=True,encoding='utf8',errors='strict',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 (OUT/'stdout.txt').write_text(process.stdout,'utf8');(OUT/'stderr.txt').write_text(process.stderr,'utf8')
 if process.returncode:raise RuntimeError('Falló el adaptador real de recálculo preparado')
 actual=json.loads((OUT/'recalculo/RESULTADO_RECALCULO.json').read_text('utf8'));prior=json.loads((STAGE/'analysis/RESULTADO_RECALCULO.json').read_text('utf8'))
 if actual!=prior:raise ValueError('El adaptador RP cambió el resultado documental original')
 if any(name=='app'or name.startswith(('app.','dee_thinking'))for name in sys.modules):raise ValueError('Una prueba stdlib importó DEE/app')
 steps=recipe['variants']['native12']['batches'][0];episodes=[s for s in steps if s['label'].startswith('EP_')]
 if len(episodes)!=12 or [s['literal']for s in episodes]!=[{'modo':'eci01-pi09-episodio'}]*12:raise ValueError('Cambió la entrada literal del actor')
 result={'schema':'DEE.PI09.RP.actual_prepared_interfaces.stdlib_test.R01','passed':True,'capsule':cap,'analysis':analysis,'recalculation_byte_semantics_equal':True,'completed_opportunities':actual['completed_opportunities'],'expected_values_only_after_response':True,'Native_executed':False,'DEE_imports':0,'source_state_read':False,'new_material_replay_claimed':False}
 proof=OUT/'RESULTADO.json';proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':True,'proof':str(proof),'sha256':sha(proof),'Native_executed':False}))
if __name__=='__main__':main()
