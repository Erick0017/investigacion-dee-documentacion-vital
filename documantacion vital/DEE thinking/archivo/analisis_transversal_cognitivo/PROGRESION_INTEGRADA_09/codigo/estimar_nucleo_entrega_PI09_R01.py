"""Estimate compressed evidence size from closed, known files only. No DEE."""
from pathlib import Path
import json,zlib
P=Path(__file__).resolve().parents[1]
rows=[]
for folder in ('control/CUATRO_CONSULTA_PORTABLE_R03','control/AR_PORTABLE_CUATRO_R01'):
 root=P/folder
 files=[p for p in root.rglob('*')if p.is_file()]
 rows.append({'folder':folder,'files':len(files),'bytes':sum(p.stat().st_size for p in files),'deflate_payload_bytes':sum(len(zlib.compress(p.read_bytes(),9))for p in files)})
print(json.dumps({'closed_evidence_estimate':rows,'Native_executed':False,'ZIP_created':False},indent=2))
