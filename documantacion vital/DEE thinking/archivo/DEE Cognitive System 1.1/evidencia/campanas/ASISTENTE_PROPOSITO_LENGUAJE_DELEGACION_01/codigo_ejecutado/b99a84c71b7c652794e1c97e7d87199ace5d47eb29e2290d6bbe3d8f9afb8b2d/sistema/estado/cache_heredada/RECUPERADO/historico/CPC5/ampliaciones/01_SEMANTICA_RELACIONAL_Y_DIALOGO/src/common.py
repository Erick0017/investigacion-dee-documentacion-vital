"""Exact passive records and declared inputs, reused from CPC5; no response oracle."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('cpc5_frozen_common',BASE/'src/common.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
for name in ('sha','put','identity','record','interface','receipt','digest','operational','until','local_context','gate'):
    globals()[name]=getattr(module,name)
