"""Portable launcher; resolves only the two included frozen local calculators.

Explicitly adds this file's directory because the bundled interpreter may use
safe-path mode. No historical paths, native engine, target feedback or actor.
"""
from pathlib import Path
import runpy,sys
HERE=Path(__file__).resolve().parent
SCRIPTS={'B05':'recalcular_escalamiento_b_R3_B05_FINAL.py',
         'B06_B07':'recalcular_b06_b07_R2_FINAL.py'}
if len(sys.argv)<2 or sys.argv[1]not in SCRIPTS:raise SystemExit('Usage: RUN_RECALCULO_B.py B05|B06_B07 --evidence DIRECTORY --out NEW_FILE.json')
script=HERE/SCRIPTS[sys.argv[1]];sys.path.insert(0,str(HERE));sys.argv=[str(script),*sys.argv[2:]]
runpy.run_path(str(script),run_name='__main__')
