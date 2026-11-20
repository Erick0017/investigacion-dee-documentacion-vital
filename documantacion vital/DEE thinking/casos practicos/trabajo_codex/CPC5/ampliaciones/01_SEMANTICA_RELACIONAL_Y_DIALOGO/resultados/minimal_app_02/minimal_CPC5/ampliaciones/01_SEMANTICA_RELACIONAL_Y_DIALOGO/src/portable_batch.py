"""Portable finite batch wrapper around existing native scientific functions.

Output paths are relative to the user's output directory, never a private lab
root. Case IDs name files only. No expected result or history table is read.
"""
from pathlib import Path
import argparse
import importlib
import json
import re
import sys
import time

HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from common import put,sha

MODES={'dialogo':'dialogue','orden':'order_stream','capacidad':'capacity','arquitectura':'architectures'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=tuple(MODES),required=True)
    p.add_argument('--config',type=Path);p.add_argument('--case',type=Path)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if bool(args.config)==bool(args.case):raise ValueError('Choose exactly one --config or --case')
    source=args.config or args.case;configuration=json.loads(source.read_text(encoding='utf-8'))
    cases=configuration['cases']if args.config else[configuration.get('case',configuration)]
    if not isinstance(cases,list)or not 1<=len(cases)<=256:raise ValueError('Finite1..256case list required')
    ids=[]
    for case in cases:
        if not isinstance(case,dict)or not isinstance(case.get('id'),str)or case.get('id')in('.','..')or not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}',case['id']):
            raise ValueError('Each case requires a safe explicit ID; IDs name outputs, not native answers')
        ids.append(case['id'])
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate case IDs')
    if args.output.exists():raise FileExistsError('Preserve existing results; choose a new output directory')
    args.output.mkdir(parents=True)
    module=importlib.import_module(MODES[args.mode]);started=time.monotonic();rows=[]
    run_case=module.run_case
    try:
        for case in cases:
            target=args.output/case['id'];result=run_case(case,target)
            primary=target/'MEASUREMENTS.json'
            rows.append({'id':case['id'],'file':primary.relative_to(args.output).as_posix(),
                'sha256':sha(primary),'native_source_sha256':sha(Path(module.__file__)),
                'elapsed_seconds':result.get('elapsed_seconds'),'status':'COMPLETED'})
            put(args.output/'INDEX.json',{'schema':'CPC5.extension.portable-batch.v1','mode':args.mode,
                'configuration_sha256':sha(source),'cases':rows,'paths_relative_to':'This output directory',
                'scope':'Calls unchanged native research preparation/evolution. No external answer calculation or result replay.'})
    except BaseException as exc:
        put(args.output/'BATCH_ERROR.json',{'error':repr(exc),'mode':args.mode,'completed_cases':rows,
            'elapsed_seconds':time.monotonic()-started,'partial_case_preserved':True})
        raise
    print(json.dumps({'mode':args.mode,'cases':len(rows),'elapsed_seconds':time.monotonic()-started},ensure_ascii=False))


if __name__=='__main__':main()
