"""Single public entry point. New science is explicit, never silently repeated."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    demo=sub.add_parser('demostracion');demo.add_argument('--eventos',type=Path);demo.add_argument('--salida',type=Path,default=Path('sesion_CPC5'))
    net=sub.add_parser('red');net.add_argument('--caso',type=Path,required=True);net.add_argument('--salida',type=Path,required=True)
    lang=sub.add_parser('lenguaje');lang.add_argument('--caso',type=Path,required=True);lang.add_argument('--salida',type=Path,required=True)
    comp=sub.add_parser('compuesto');comp.add_argument('--caso',type=Path,required=True);comp.add_argument('--salida',type=Path,required=True)
    for name in ('heterogeneo','puente'):
        item=sub.add_parser(name);item.add_argument('--config',type=Path,required=True);item.add_argument('--salida',type=Path,required=True)
    ref=sub.add_parser('referencia');ref.add_argument('--caso',choices=['ABCD_FILTER_FLAT','SEM01_A_future_UV','RELATIVE_AB_BA'],required=True);ref.add_argument('--salida',type=Path,required=True)
    check=sub.add_parser('verificar');check.add_argument('--manifest',type=Path,default=ROOT/'MANIFEST.json')
    args=p.parse_args()
    if args.command=='verificar':
        import hashlib
        value=json.loads(args.manifest.read_text(encoding='utf-8-sig'))
        items=value.get('files',value.get('entries',[]));fail=[];count=0
        if isinstance(items,dict):items=[{'path':k,**v} if isinstance(v,dict) else {'path':k,'sha256':v} for k,v in items.items()]
        for row in items:
            name=row.get('path',row.get('file'));expected=row.get('sha256')
            if not name or not expected:continue
            path=ROOT/name
            if not path.is_file():fail.append({'path':name,'reason':'missing'});continue
            h=hashlib.sha256()
            with path.open('rb') as f:
                for block in iter(lambda:f.read(1048576),b''):h.update(block)
            count+=1
            if h.hexdigest()!=expected:fail.append({'path':name,'reason':'hash'})
        print(json.dumps({'verified':count,'errors':fail}));raise SystemExit(bool(fail))
    if args.command=='demostracion':
        command=[sys.executable,'-B',str(ROOT/'demostracion.py'),'--salida',str(args.salida)]
        if args.eventos:command+=['--eventos',str(args.eventos)]
    elif args.command=='red':command=[sys.executable,'-B',str(ROOT/'src/network.py'),'worker','--case',str(args.caso),'--out',str(args.salida)]
    elif args.command=='compuesto':command=[sys.executable,'-B',str(ROOT/'src/compound.py'),'--case',str(args.caso),'--output',str(args.salida)]
    elif args.command in ('heterogeneo','puente'):
        script='heterogeneous.py' if args.command=='heterogeneo' else 'heterobridge.py'
        command=[sys.executable,'-B',str(ROOT/'src'/script),'--config',str(args.config),'--output',str(args.salida)]
    elif args.command=='referencia':command=[sys.executable,'-B',str(ROOT/'src/references.py'),'--case',args.caso,'--output',str(args.salida)]
    else:command=[sys.executable,'-B',str(ROOT/'src/linguistic.py'),'--case',str(args.caso),'--output',str(args.salida)]
    completed=subprocess.run(command,timeout=1800)
    raise SystemExit(completed.returncode)

if __name__=='__main__':main()
