"""Thin opt-in adapter over the existing complete-world owner; no T0 or policy.

Importing this file imports only pathlib. The habitat capability is resolved
lazily on the first advance, so this instrumentation is inert at module import.
PI02 habitat.advance must evolve the unwrapped base passed here, never call this
wrapper recursively, and must preserve its progress in the complete snapshot.
If its declared enabled flag is false, that capability must allow passive base
advancement; the adapter does not reinterpret an action, target or useful route.
"""
from pathlib import Path

VERSION='PI02.owner_habitat_adapter.R04'

class HabitatAdapter:
    def __init__(self,base,directory):
        if isinstance(base,HabitatAdapter):raise ValueError('Do not nest habitat adapters; use wrap() to reuse the existing wrapper')
        self.base=base
        self.directory=Path(directory)
    @property
    def world(self):return self.base.world
    @property
    def tick(self):return self.base.tick
    def save(self,path):return self.base.save(path)
    def run_until(self,target):
        if type(target)is not int or target<int(self.tick):raise ValueError('Exact nondecreasing target tick required; no rewind')
        from capacidades import pi02_habitat_R04 as habitat
        if habitat.KEY in dict(self.world.runtime.snapshot_metadata_entries):
            return habitat.advance(self.base,target,self.directory)
        return self.base.run_until(target)

def wrap(base,directory):
    """Wrap the same lived world once; never load/create/import another world."""
    if isinstance(base,HabitatAdapter):
        if base.directory.resolve()!=Path(directory).resolve():raise ValueError('An existing habitat wrapper has a different operational directory')
        return base
    return HabitatAdapter(base,directory)
