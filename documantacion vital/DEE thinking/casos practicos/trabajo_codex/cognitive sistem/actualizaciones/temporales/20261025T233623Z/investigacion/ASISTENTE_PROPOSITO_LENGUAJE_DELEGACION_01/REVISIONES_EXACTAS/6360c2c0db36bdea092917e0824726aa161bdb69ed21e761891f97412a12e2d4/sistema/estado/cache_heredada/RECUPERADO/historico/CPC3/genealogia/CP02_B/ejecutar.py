"""Portable bounded launcher. Default is a new prospective session demonstration."""
import argparse,subprocess,sys
from pathlib import Path


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['demo','reproduce'],default='demo');p.add_argument('--output',default='ejecucion_nueva');a=p.parse_args();root=Path(__file__).resolve().parent
    command=[sys.executable,'-I','-B',str(root/'conversar.py'),'--events',str(root/'SESION_REPRODUCIBLE.txt'),'--output',a.output] if a.mode=='demo' else [sys.executable,'-I','-B',str(root/'src'/'reproduce.py'),'--package',str(root),'--output',a.output]
    pchild=subprocess.Popen(command)
    try:code=pchild.wait(timeout=180)
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill.exe','/PID',str(pchild.pid),'/T','/F'],capture_output=True,timeout=15);code=124
    raise SystemExit(code)
