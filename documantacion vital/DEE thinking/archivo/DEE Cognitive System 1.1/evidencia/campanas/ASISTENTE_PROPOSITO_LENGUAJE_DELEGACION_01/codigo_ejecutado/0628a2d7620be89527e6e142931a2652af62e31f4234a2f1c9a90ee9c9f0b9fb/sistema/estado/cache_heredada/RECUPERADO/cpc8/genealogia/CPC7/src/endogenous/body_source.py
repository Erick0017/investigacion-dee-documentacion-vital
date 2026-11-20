"""One declared scalar-source preparation change; original body stays frozen.

The source remains semantic4, state6100, direction0, clock19 and present. Only
s_reg of this one INITIAL placement changes. Nothing resets an ongoing MAIN.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import order_memory


def prepare_geometry(n=67,center=(33,25,42),phase=260,source_load=0):
    import dee_thinking as d
    if type(source_load) is not int or not 0<=source_load<=65535:raise ValueError('Representable initial source load')
    prep=order_memory.prepare_geometry(n=n,center=center,phase=phase)
    source=order_memory.add(center,(0,0,1),n);indices=[]
    for i,p in enumerate(prep['placements']):
        if (p.site.x,p.site.y,p.site.z)==source:indices.append(i)
    if len(indices)!=1:raise ValueError('The declared original body source was not unique')
    index=indices[0];old=prep['placements'][index]
    expected=d.pack_record(6100,7,0,0,0,4)
    if old.raw!=expected or old.clock!=19:raise ValueError('Unexpected frozen original source fields')
    new=d.InitialPlacement();new.site=d.Coordinate(*source)
    new.raw=d.pack_record(6100,source_load,0,0,0,4);new.clock=old.clock;new.role=old.role+'; explicit initial source-load calibration'
    prep['placements'][index]=new
    prep['geometry']['prepared_scalar_source']={'site':source,'state':6100,'semantic':4,'direction':[0,0,0],'clock':'19',
        'initial_load':source_load,'original_load':7,'RAW_before':str(old.raw),'RAW_after':str(new.raw),
        'RAW_xor_hex':format(old.raw^new.raw,'016x'),'changed_fields':['s_reg'] if source_load!=7 else [],
        'modality':'INITIAL_PREPARATION; never a RAW edit afterT0',
        'scope':'Fixed designer-supplied supply parameter. Functional continuity and emissions require their own comparison; no acquired homeostasis is implied.'}
    return prep
