"""Version-only passive adapter. No Native, SDK, model or state access."""
from pathlib import Path
import hashlib

ROOT=Path(__file__).resolve().parent
old=ROOT/'RECALCULO_CIERRE8_R07.py'
new=ROOT/'RECALCULO_CIERRE8_R07_R02.py'
raw=old.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='62211e67641e0daee3b9612e0909f98813a9bf31310df78b833fea921f157b7d'
text=raw.decode('utf-8-sig')
def replace(before,after):
    global text
    assert text.count(before)==1,before
    text=text.replace(before,after)
replace("VERSION='DEE.R07.passive_recalculation.R01'","VERSION='DEE.R07.passive_recalculation.R02'")
replace("    events=source.jsonl(block['events'])\n    return result,world,events", """    # A resumed closed block may preserve its phases in several original logs.
    # These are source fragments, not extra worlds, opportunities or Native runs.
    if 'event_fragments' in block:
        ensure('events' not in block,'Use events OR event_fragments, never both')
        keys=block['event_fragments']
        ensure(isinstance(keys,list) and keys and all(isinstance(k,str) for k in keys),
               'Explicit nonempty event fragment paths required')
        ensure(len(keys)==len(set(keys)),'Repeated event fragment path')
    else:
        keys=[block['events']]
    events=[]
    for key in keys:
        for line,event in source.jsonl(key):
            events.append(({'source':key,'line':line},event))
    return result,world,events""")
replace("            locator={'source':block['events'],'line':line}","            locator=line  # Exact original fragment path and line, not a merged pseudo-source.")
replace("        blocks.append({'block':bidx,'result':block['result'],'world':block['world'],", "        blocks.append({'block':bidx,'result':block['result'],'world':block['world'],\n            'event_fragments':block.get('event_fragments',[block.get('events')]),")
assert not new.exists(),str(new)
new.write_text(text,encoding='utf-8',newline='\n')
assert old.read_bytes()==raw
print(new.name,hashlib.sha256(new.read_bytes()).hexdigest())
