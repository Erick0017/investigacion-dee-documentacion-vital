"""Declared external port extension, not native growth or semantic65 claims.

The unchanged living E1 continues in its existing N67 world. New empty input
interfaces add no RAW/clocks/material and provide actual later experiences.
No trained state is imported. No host response selection occurs.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'base_validada/cpc8/src'),str(ROOT/'front_semantics/src'),str(ROOT/'front_relations/src')]
from main_social_life import MainSocialSession
from repertorio_n67 import N67RepertoireSession,prepare
from integracion.relational_pair import physical
class MainWithRepertoire(MainSocialSession):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.repertoire=N67RepertoireSession(self.world,self.geometry['cpc9_repertoire_extension']['geometry'],self.state.get('cpc9_repertoire_state'))if'cpc9_repertoire_extension'in self.geometry else None
    def attach_instruments(self,k=65):
        if self.repertoire is not None:raise ValueError('Repertoire already present')
        recipe,g=prepare(k);before=physical(self.world);count=len(self.world.runtime.channel_names)
        for spec in recipe.interfaces:self.world.declare_interface(spec)
        after=physical(self.world)
        if before!=after:raise AssertionError('Inert registration changed physical state')
        entry={'geometry':g,'introduced_at':self.tick,'attribution':'EXTERNAL_INSTRUMENTAL_INTERFACE_EXTENSION; NOT acquired architecture or native growth',
          'new_material':0,'new_interfaces':len(recipe.interfaces),'before':before,'after':after,'channels_before':count,'channels_after':len(self.world.runtime.channel_names)}
        self.geometry['cpc9_repertoire_extension']=entry;self.repertoire=N67RepertoireSession(self.world,g)
        return entry
    def receipts(self):return super().receipts()+(self.repertoire.receipts()if self.repertoire else[])
    def save(self,path):
        if self.repertoire:self.state['cpc9_repertoire_state']=self.repertoire.state
        return super().save(path)
