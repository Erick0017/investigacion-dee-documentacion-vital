"""MA02 service04/05 final wording correction; historical references remain intact."""
import argparse
import gzip
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('archived_service',Path(__file__).with_name('recalcular_servicio_01.py'))
service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fase',choices=('04','05'),required=True)
    p.add_argument('--evidencia',type=Path,required=True)
    p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args(); x=service.calculate(a.evidencia,phase=a.fase)
    sizes=set()
    for item in x['sources']:
        name=item['file'] if 'file'in item else item['path']
        value=json.loads(gzip.decompress((a.evidencia/name).read_bytes()))
        for row in value.get('result',{}).get('result',{}).get('rows',[]):
            if 'reader'in row:sizes.add(len(row['reader']['panel']))
    x['fixed_gate_panel_sizes_observed']=sorted(sizes)
    if sizes!={10}:raise ValueError('Expected all ten fixed gate panels in these five-context stages.')
    x['scope_and_limits'][0]='Decode uses all ten fixed RAW gates after the five-context extension. Earlier four-context service01/02 protocols used eight. Context and historical signs are used later for external scoring only.'
    x['editorial_correction_only']='Corrected the eight-gate wording inherited from service01. No primary bytes, geometry, decoding, metric or historical reference changed.'
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'phase':a.fase,'issues':len(x['issues']),'fixed_gate_panel_sizes_observed':sorted(sizes)}))
    return 1 if x['issues']else 0


if __name__=='__main__':raise SystemExit(main())
