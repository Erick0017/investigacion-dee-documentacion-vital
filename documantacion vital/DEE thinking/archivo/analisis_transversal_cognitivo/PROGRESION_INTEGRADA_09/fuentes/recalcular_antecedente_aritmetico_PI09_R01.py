"""Six frozen PI08 arithmetic records and nominal geometry; stdlib only."""
from pathlib import Path
import ast, hashlib, json, sys

P = Path(__file__).resolve().parents[1]
P8 = P.with_name('PROGRESION_INTEGRADA_08')
C = P.parents[2]/'DEE Cognitive 2.0'


def read(path): return json.loads(path.read_text('utf-8-sig'))


def item(path):
    return {'path':str(path),'bytes':path.stat().st_size,
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def row(path):
    doc = read(path)
    result = doc['result']
    if isinstance(result,str): result = json.loads(result)
    return result['result']['rows'][0]


def decode(raw):
    n = int(raw)
    def signed(shift):
        value=(n>>shift)&15
        return value-16 if value>=8 else value
    return {'RAW':str(n),'state':n&0xffffffff,'s_reg':(n>>32)&65535,
            'semantic':(n>>60)&15,'direction':[signed(s)for s in(48,52,56)]}


def geometry(source):
    tree=ast.parse(source.read_text('utf8'))
    selected=[]
    for node in tree.body:
        if isinstance(node,ast.Assign) and all(isinstance(x,ast.Name) and x.id in {'VERSION','N','E','S','FACTORS'}for x in node.targets): selected.append(node)
        elif isinstance(node,ast.FunctionDef) and node.name=='geometry': selected.append(node)
    scope={}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(source),'exec'),scope)
    return scope['geometry'](128)


def main():
    forbidden=[]
    def audit(event,args):
        if event=='import'and str(args[0]).split('.')[0]in {'dee_thinking','app','capacidades','_native'}:
            forbidden.append(str(args[0]));raise RuntimeError('Native/app imports forbidden')
    sys.addaudithook(audit)
    sources = [(name,P8/relative)for name,relative in (
        ('B_REAL_SUM','ensayos/PI08_B_CONSERVACION_R02_number13.json'),
        ('B_REAL_DIF','ensayos/PI08_B_CONSERVACION_R02_number8.json'),
        ('B_NONE_SUM','ensayos/PI08_B_NONE_AUTOPSIA_PANEL_R02_number13.json'),
        ('B_NONE_DIF','ensayos/PI08_B_NONE_AUTOPSIA_PANEL_R02_number8.json'),
        ('A_RP_SUM','estados/RP_A_PANEL12_R01/ensayos/ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_ARP_PANEL12_01_number13.json'),
        ('A_RP_DIF','estados/RP_A_PANEL12_R01/ensayos/ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_ARP_PANEL12_01_number8.json'))]
    code=C/'sistema/capacidades/percepcion_cruda_fi01.py'
    g=geometry(code)
    first={q['component_index']:q for q in g['raw_sources'] if q['component_index']in(0,1)}
    selected_nodes=[q for q in g['nodes'] if q['id']in('left.root.0.0','left.root.0','left.root','right.root.0.0','right.root.0','right.root')]
    rows=[]
    for name,path in sources:
        r=row(path);op=r['native_operation'];t=op['native_trial'];q=t['query_tick'];root=q-35
        gate=next(f for f in t['frames']if f['tick']==t['datum_tick']-2)['fields']['C']
        decoded=decode(gate['raw'])
        assert gate['site']==[12,17,18] and decoded['state']>0 and decoded['semantic']==1 and decoded['direction']==[1,-1,-1]
        requests=t['requests'];unique={x['id']:x for x in requests}
        assert len(unique)==176 and all(x['receipt']['status']=='applied'for x in unique.values())
        components=[]
        for index,s in first.items():
            port='MU.raw.L128.'+s['id'];matches=[x for x in requests if x['port']==port]
            assert len(matches)==1
            components.append({'component_index':index,'nominal_geometry':s,'actual_request':matches[0]})
        rows.append({'case':name,'primary':item(path),'operation':op['operation'],'operands':op['operands'],
                     'before_tick':t['before']['tick'],'after_tick':t['after']['tick'],
                     'input_tick':t['input_tick'],'root_tick_derived_from_fixed_calendar':root,
                     'query_tick':q,'query_moduli':{str(m):q%m for m in(67,391,782)},
                     'numeric_gate_tick':t['datum_tick']-2,'gate_observation':gate,'gate_decoded':decoded,
                     'actual_numeric_result':r['numeric_result'],'direct_requests':len(unique),'all_applied':True,
                     'normalizer_shift':t['timing']['wait_ticks'],
                     'first_independent_components':components,
                     'nominal_node_calendar':[dict(n,absolute_nominal_tick=root+n['join_tick_relative'])for n in selected_nodes],
                     'observed_frame_ticks':[f['tick']for f in t['frames']],
                     'earlier_nodes_materially_observed_in_this_primary':any(any(k.startswith('left.')or k.startswith('right.')for k in f['fields'])for f in t['frames'])})
    assert [r['actual_numeric_result']for r in rows]==[7,2,7,2,13,8]
    assert rows[0]['query_moduli']['391']==rows[4]['query_moduli']['391'] and rows[0]['query_moduli']['782']==rows[4]['query_moduli']['782']
    result={'schema':'DEE.PI09.F1.frozen_arithmetic_recalculation.R01','rows':rows,
            'geometry_code':item(code),'geometry_scope':'AST constants+geometry only. Nominal path is apparatus, not observed carrier lineage.',
            'counts':{'actual_frozen_primaries_read':6,'Native_executions':0,'DEE_imports':forbidden},
            'findings':{'actual_results':[7,2,7,2,13,8],'all_six_C_signatures_valid':True,
                        'all_six_176_direct_inputs_applied':True,'A_B_equal_391_and_782_SUM_phases':True,
                        'A_SUM_query_mod67':58,'B_SUM_query_mod67':19,
                        'current_primaries_do_not_locate_first_tree_divergence':True,
                        'NONE_same_failure_excludes_contingent_negative_return_as_necessary_condition':True}}
    out=P/'fuentes/ANTECEDENTE_ARITMETICO_RECALCULADO_PI09_R01.json'
    with out.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'output':item(out),'actual_results':result['findings']['actual_results'],'Native':0,'DEE_imports':forbidden},ensure_ascii=False))


if __name__=='__main__': main()
