"""Prospective setup scheduling revision after measured RAM preflight failure.

R01 started no child. Its5GiB preflight remains unchanged. The now-closed own
capture editor frees RAM. Only the administrative latest-start becomes19UTC;
Native last-new20UTC, finish21:07UTC,512MiB limits and reserve do not change.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'control/importar_copias_pre_native_R07_R01.py'
text=source.read_text('utf8')
for before,after in (
    ('LATEST_START=1794852000','LATEST_START=1794855600'),
    ("'control/IMPORTACIONES_PRE_NATIVE_R01'","'control/IMPORTACIONES_PRE_NATIVE_R02'"),
):
    if text.count(before)!=1:raise ValueError('Exact scheduling anchor required')
    text=text.replace(before,after)
exec(compile(text,str(source),'exec'),{'__file__':str(source),'__name__':'__main__'})
