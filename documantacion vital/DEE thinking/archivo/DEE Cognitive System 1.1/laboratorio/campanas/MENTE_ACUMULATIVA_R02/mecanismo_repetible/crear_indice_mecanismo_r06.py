"""Final extended index after the one bounded R06; no native import or tick."""
import json,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('index_base',HERE/'crear_indice_mecanismo.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b)
def main():
    target=b.EV/'INDICE_MECANISMO_MA02_R06_FINAL.json'
    if target.exists():raise FileExistsError(target)
    old=json.loads((b.EV/'INDICE_MECANISMO_MA02_FINAL.json').read_text(encoding='utf8'));entries=[]
    for p in sorted(b.EV.rglob('*')):
        if not p.is_file()or p.name.startswith('INDICE_MECANISMO_'):continue
        if '.deetsnap.gz'in p.name:kind='COMPLETE_LOCAL_WORLD_SNAPSHOT';inc=False
        elif '.worker'in p.parent.name:kind='ACTUAL_LOCAL_SERVICE_FILE';inc=True
        elif p.name.startswith('RECALCULO_'):kind='ARCHIVED_RECALCULATION_REFERENCE';inc=p.name=='RECALCULO_MECANISMO_MA02_R06_FINAL.json'
        elif p.name.endswith('.jsonl'):kind='OPERATIONAL_ATTEMPT_JOURNAL';inc=False
        elif p.name.startswith('PROTOCOLO_'):kind='PROSPECTIVE_PROTOCOL';inc=True
        else:kind='PRIMARY_RESULT_OR_OPERATIONAL_CHECK';inc=True
        entries.append(b.item(p,kind,inc))
    for p in sorted(HERE.rglob('*')):
        if p.is_file()and p.suffix in('.py','.md'):entries.append(b.item(p,'EXECUTED_CODE_OR_REPORT',True))
    for p in[b.ROOT/'sistema/capacidades/selector_p1_ma02.py',b.ROOT/'sistema/contratos/SELECTOR_P1_MA02.json']:entries.append(b.item(p,'INCORPORATED_OPERATIONAL_COMPONENT',True))
    value={**old,'entries':entries,'final_extension':'R06 fixed late four-support supply, six existing-parent branches, no MAIN or protected P1 state advanced','source_self_hash_excluded_to_avoid_autoreference':True}
    target.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps({'entries':len(entries),'local_snapshots':sum(x['kind']=='COMPLETE_LOCAL_WORLD_SNAPSHOT'for x in entries),'recommended_analysis_bytes':sum(x['bytes']for x in entries if x['recommended_in_analysis'])}))
if __name__=='__main__':main()
