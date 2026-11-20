"""Root-requested explicit control/holdout limits; preserve the R01 proposal."""
from pathlib import Path
import ast
import hashlib

H = Path(__file__).resolve().parent


def once(s, old, new):
    if s.count(old) != 1: raise ValueError('Exact prepared-source locator changed')
    return s.replace(old, new, 1)


def main():
    source = H/'incorporar_mecanismos_producto_PI04_JSON_R01.py'
    target = H/'incorporar_mecanismos_producto_PI04_JSON_R02.py'
    if target.exists(): raise ValueError('Preserve prior R02')
    s = source.read_text(encoding='utf8')
    s = s.replace('INCORPORACION_MECANISMOS_PI04_JSON_R01','INCORPORACION_MECANISMOS_PI04_JSON_R02')
    s = s.replace('INCORPORACION_MECANISMOS_PRODUCTO_PI04_JSON_R01','INCORPORACION_MECANISMOS_PRODUCTO_PI04_JSON_R02')
    s = s.replace('CATALOGO_ANTES_MECANISMOS_PI04_JSON_R01','CATALOGO_ANTES_MECANISMOS_PI04_JSON_R02')
    s = once(s, "    reg = regression()\n", """    reg = regression()
    controls = {}
    for arm,name,count in [('none','PI04_C2C_NONE20_R01.json',12),('yoked','PI04_C2C_YOKE20_R01.json',20)]:
        f = P/'control'/name; v = read(f)
        if v.get('owner_closed') is not True or v.get('completed') != 20 or v.get('products') != count or v.get('arm') != arm:
            raise ValueError('Actual closed control counts differ; preserve the discrepancy')
        controls[arm] = {'opportunities':20,'products':count,'proof':desc(f)}
    noadoptfile = P/'control/DECISION_NO_ADOPCION_PI04.json'; noadopt = read(noadoptfile)
    if noadopt.get('approved_for_adoption') is not False or noadopt.get('adoption_performed') is not False or noadopt['principal']['life_id'] != 'ECI02_PI03_MAIN':
        raise ValueError('The actual reasoned nonadoption decision must be preserved')
""")
    s = once(s, "        'limits':['Es observación/recálculo sobre evidencia, no nueva simulación, recuperación cognitiva ni habilidad adquirida por PI03_MAIN.'],",
        "        'limits':['Es observación/recálculo sobre evidencia, no nueva simulación, recuperación cognitiva ni habilidad adquirida por PI03_MAIN.',\n            'Rasgos y criterio seleccionados por el auditor sobre este corpus; sin reserva ciega. No es un clasificador aprendido por el ente.'],")
    s = once(s, "        'attributed_to_main':False,'current_principal_possesses_this_acquisition':False,'principal_adoption':False,",
        "        'attributed_to_main':False,'current_principal_possesses_this_acquisition':False,'principal_adoption':False,\n        'comparisons':{'real':{'opportunities':20,'products':19},**controls,'shared_prefix_not_independent_organisms':True,'advantage_over_yoked_return':False},")
    s = once(s, "        'limits':['No planificación o iniciativa general. Los controles con prefijo compartido no son organismos independientes.',",
        "        'limits':['No planificación o iniciativa general. Los controles con prefijo compartido no son organismos independientes.',\n            'Real19/20, retorno genérico constante de no fallo12/20 y retorno desacoplado20/20. No hay ventaja de contingencia verdadera ni crédito temporal exclusivo demostrado.',\n            'La secuencia consulta→función aritmética→segunda selección→dispositivo sigue preparada; no fue iniciada o descubierta autónomamente por Native.',")
    s = once(s, "            'regression_and_nonadoption':reg,'principal_adoption':False},",
        "            'regression_and_nonadoption':reg,'reasoned_noadoption':desc(noadoptfile),'principal_adoption':False,\n            'controls':{'real':{'opportunities':20,'products':19},**controls,'shared_prefix_not_independent_organisms':True,'true_contingency_advantage':False,\n                'none_is_not_physical_return_omission':'Constant nonfailure generic return, same input dose; the yoked plan is frozen and permutes real-history returns.'}},")
    ast.parse(s)
    target.write_text(s,encoding='utf8',newline='')
    print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())


if __name__=='__main__':main()
