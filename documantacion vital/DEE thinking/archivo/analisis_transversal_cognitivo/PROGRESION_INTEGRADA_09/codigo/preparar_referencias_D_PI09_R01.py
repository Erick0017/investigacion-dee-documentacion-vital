"""Root-only referencias cerradas para la decisión D; no autoriza ni mueve."""
from pathlib import Path
import argparse,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):
 p=Path(p).resolve(strict=True)
 if not p.is_relative_to(P.resolve()):raise ValueError('Referencia fuera de P9')
 json.loads(p.read_text('utf-8-sig'));return {'path':str(p),'sha256':sha(p)}
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for name in('conservacion','ultima-funcion','source-zero'):ap.add_argument('--'+name,type=Path,required=True)
 ap.add_argument('--real',type=Path,default=P/'control/PI09_D_REAL6_R03.json');ap.add_argument('--none',type=Path,default=P/'control/PI09_D_NONE6_R03.json');ap.add_argument('--yoke',type=Path,default=P/'control/PI09_D_YOKE6_R03.json')
 ap.add_argument('--rp-result',type=Path,default=P/'estados/RP_D_FAMILIA_R01/RESULTADO_REPRODUCCION.json');ap.add_argument('--comparacion',type=Path,default=P/'control/COMPARACION_RP_D6_FAMILIA_PI09_R01.json');ap.add_argument('--rp-registro',type=Path,default=P/'control/RP_D6_FAMILIA_REGISTRADA_PI09_R01.json');ap.add_argument('--salida',type=Path,required=True);a=ap.parse_args()
 out=a.salida.resolve()
 if not out.is_relative_to((P/'control').resolve())or out.exists():raise ValueError('Salida nueva dentro de control')
 registered=json.loads(a.rp_registro.read_text('utf-8-sig'))
 if registered.get('registered')is not True:raise ValueError('El registro RP real todavía no está cerrado')
 data={'first_milestone_adoption':ref(P/'control/ADOPCION_PRODUCTO_PI09.json'),'D_actual_closed_arms':{'real':ref(a.real),'none':ref(a.none),'yoked':ref(a.yoke)},'D_conservation_proof':ref(a.conservacion),'D_source_reopening_function_proof':ref(a.ultima_funcion),'D_source_zero_reopening_proof':ref(a.source_zero),'D_reproduction_result':ref(a.rp_result),'D_reproduction_comparison':ref(a.comparacion),'D_new_frontdoor_CLI_replay_verified':True,'D_generic_family_registration':ref(a.rp_registro),
 'scope':'Sucesor único Discovery D: readaptación local en entorno persistente fijo mediante los mismos bancos Native y retorno genérico compartido. Mantener el principal NATIVE quieto hasta decidir; movimiento de identidad completa sin fusión ni reinicio.',
 'gains':['En el estudio D fijo de seis oportunidades, Real5/6, None3/6 y Yoke1/6; el retorno contingente permite revisión Native útil local.','Disponibilidad de la adquisición D6 por familia diagnóstica reutilizable, sólo si su frente CLI y comparación completa están registrados.'],
 'losses':['No se demuestra crédito específico de la primera consulta ni bancos nuevos: ambos selectores comparten historia y consecuencia genérica.','Aritmética pública conserva legacy_partial: la mejora pareada de la guardia temporal fue0; no se habilita esa política experimental.'],
 'uncertainties':['Dominio acotado y entorno P0 preparado; no afirmar regulación general ni superioridad universal.','Una reproducción de seis incluye el primer fallo y dos conflictos terminales reales; igualdad no significa seis éxitos.'],
 'assistance':['Ingeniería P0 de suministro ambiental y lote FI8 nuevo explícito; no energía ni aprendizaje instalado.','Transporte y permisos administrativos exactos separados de cuerpos científicos literales; sin selección de respuestas por Python.'],
 'regression_coverage':{'actual_same_life_conservation':ref(a.conservacion),'actual_last_function_after_reopen':ref(a.ultima_funcion),'source0':ref(a.source_zero),'scope':'Doce funciones declaradas, última función D útil y reapertura0; resultados y dosis reales conservados.'},
 'catalog_entry':{'id':'PI09_D_ENTORNO_PERSISTENTE_NATIVE_R02','type':'integracion_native_adquirida_acotada','status':'ACTUAL_GATES_PENDING_ROOT_DECISION','scope':'Readaptación local D y uso finito en una continuación completa; no crédito específico de consulta ni guardia aritmética nueva.','historical_R02_material_calendar':'readonly','reproduction_recipe':'pi09_d6_familia_desde_DISCOVERY_T907543_R01'}}
 with out.open('x',encoding='utf8')as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'referencias':str(out),'sha256':sha(out),'approved_for_adoption':False,'Native_executed':False,'product_writes':False}))
if __name__=='__main__':main()
