"""Seal local source/state locators after physics, without importing DEE."""
import gzip,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];EV=ROOT/'evidencia/campanas/MENTE_ACUMULATIVA_R02/mecanismo_repetible'
def item(p,kind,include):
    b=p.read_bytes();r={'path':p.relative_to(ROOT).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'kind':kind,'recommended_in_analysis':include}
    if p.suffix=='.gz':r['gzip_uncompressed_bytes_modulo_2p32']=int.from_bytes(b[-4:],'little')
    return r
def main():
    dest=EV/'INDICE_MECANISMO_MA02_FINAL.json'
    if dest.exists():raise FileExistsError(dest)
    entries=[]
    for p in sorted(EV.rglob('*')):
        if not p.is_file():continue
        if '.deetsnap.gz' in p.name:kind='COMPLETE_LOCAL_WORLD_SNAPSHOT';inc=False
        elif '.worker' in p.parent.name:kind='ACTUAL_LOCAL_SERVICE_FILE';inc=True
        elif p.name.startswith('RECALCULO_'):kind='ARCHIVED_RECALCULATION_REFERENCE';inc=p.name.endswith('_FINAL.json')
        elif p.name.endswith('.jsonl'):kind='OPERATIONAL_ATTEMPT_JOURNAL';inc=False
        elif p.name.startswith('PROTOCOLO_'):kind='PROSPECTIVE_PROTOCOL';inc=True
        else:kind='PRIMARY_RESULT_OR_OPERATIONAL_CHECK';inc=True
        entries.append(item(p,kind,inc))
    for p in sorted(HERE.rglob('*')):
        if p.is_file()and p.suffix in('.py','.md'):entries.append(item(p,'EXECUTED_CODE_OR_REPORT',True))
    for p in[ROOT/'sistema/capacidades/selector_p1_ma02.py',ROOT/'sistema/contratos/SELECTOR_P1_MA02.json']:
        entries.append(item(p,'INCORPORATED_OPERATIONAL_COMPONENT',True))
    lives=[]
    for name in('MA02_SELECTOR_P1_H1','MA02_SELECTOR_P1_H0','MA02_SELECTOR_P1_H1_EVALUACION_01','MA02_SELECTOR_P1_H0_EVALUACION_01','MA02_SELECTOR_P1_H1_CLI_01','MA02_SELECTOR_P1_H0_CLI_01'):
        p=ROOT/'sistema/estado/vidas'/name/'VIDA.json';v=json.loads(p.read_text(encoding='utf8'));lives.append({'life_id':name,'profile':v['profile'],'tick':v['physical']['tick'],'snapshot':v['snapshot'],'snapshot_sha256':v['snapshot_sha256'],'branch':v['branch'],'parent':v['parent']})
    r={'scope':'Local exact source/state index for MA02 mechanism complement, not a replacement backup and not a claim of integration into MAIN','entries':entries,'system_lives':lives,'omission_policy':'All complete operational and diagnostic snapshots remain local. The compact analysis includes all primary result/control records, actual small service outputs, prospective protocols, exact code and final recalculation; no motor/WHL or full historical corpus. A primary result contains local snapshot locators and exact SHA. Prior recalculation and duplicate attempt journal are excluded as regenerable/redundant but retained locally.','source_self_hash_excluded_to_avoid_autoreference':True}
    dest.write_text(json.dumps(r,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8');print(json.dumps({'entries':len(entries),'snapshots_local':sum(x['kind']=='COMPLETE_LOCAL_WORLD_SNAPSHOT'for x in entries),'local_bytes':sum(x['bytes']for x in entries),'analysis_recommended_bytes':sum(x['bytes']for x in entries if x['recommended_in_analysis'])}))
if __name__=='__main__':main()
