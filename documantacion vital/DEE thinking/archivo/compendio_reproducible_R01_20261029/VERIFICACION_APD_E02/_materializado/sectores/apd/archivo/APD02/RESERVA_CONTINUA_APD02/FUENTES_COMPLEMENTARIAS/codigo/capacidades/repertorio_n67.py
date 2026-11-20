"""System adapter for the newly revalidated bare N67 directional repertoire.

Explicit form requests choose ports. Probe parity is an instrument protocol,
not a learned endogenous selector. No target map is retained by this adapter.
"""
from pathlib import Path
import sys
SYSTEM_ROOT=Path(__file__).resolve().parents[1]
SOURCE=SYSTEM_ROOT/'organizaciones/cpc9/src'
if str(SOURCE)not in sys.path:sys.path.insert(0,str(SOURCE))
# The recovered primitive has the same historical filename as this adapter;
# load by a distinct explicit module identity, never from a working-directory path.
import importlib.util
_spec=importlib.util.spec_from_file_location('_dcs11_native_n67_primitive',SOURCE/'repertorio_n67.py')
_primitive=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_primitive)
from dee_thinking.consolidated import exact_observation,exact_receipt
from dee_thinking import _native as d

class SystemRepertoire67:
    def __init__(self,session):
        self.session=session;self.world=session.world;self.state=session.state
        if 'DCS_query_counts'not in self.state:
            counts={f['id']:0 for f in session.geometry['forms']}
            for row in self.state.get('requests',[]):
                if row.get('probe'):
                    for f in session.geometry['forms']:
                        if row['port']in(f['ports']['read.plus'],f['ports']['read.minus']):counts[f['id']]+=1
            self.state['DCS_query_counts']=counts
    @property
    def tick(self):return self.session.tick
    @property
    def forms(self):return tuple(f['id']for f in self.session.geometry['forms'])
    @classmethod
    def create(cls,identifier='N67',count=65):return cls(_primitive.N67RepertoireSession.create(count))
    @classmethod
    def load(cls,path):return cls(_primitive.N67RepertoireSession.load(path))
    def run_until(self,tick):return self.session.run_until(tick)
    def save(self,path):return self.session.save(path)
    def receipts(self):return self.session.receipts()
    def _form(self,value):
        if type(value)is int:
            if not 0<=value<len(self.session.geometry['forms']):raise ValueError('Form index outside admitted range')
            return self.session.geometry['forms'][value]
        return next(f for f in self.session.geometry['forms']if f['id']==value)
    def acquire(self,form,consequence,tick,*,cue=5,teacher=11,mode='paired'):
        if consequence not in(-1,1)or mode not in('paired','unpaired','omitted'):raise ValueError('Explicit actual event+/-1 and paired/unpaired/omitted mode required')
        f=self._form(form);rows=[self.session.input(f['ports']['cue'],cue,tick+int(mode=='unpaired'))]
        if mode!='omitted':rows.append(self.session.input(f['ports']['event.plus'if consequence==1 else'event.minus'],teacher,tick))
        return rows
    def query(self,forms,tick,*,payload=7):
        forms=[forms]if isinstance(forms,(str,int))else list(forms);requests=[]
        for value in forms:
            f=self._form(value);n=self.state['DCS_query_counts'][f['id']];port=f['ports']['read.plus'if n%2==0 else'read.minus'];rr=self.session.input(port,payload,tick,True);self.state['DCS_query_counts'][f['id']]=n+1;requests.append({'form':f['id'],'query_index':n,'receipt':rr,'hub':f['hub']})
        self.run_until(tick+3)
        return{'read_tick':self.tick,'modality':'EXPLICIT_USER_MATERIAL_QUERY','responses':[{'form':r['form'],'query_index':r['query_index'],'receipt':exact_receipt(self.world.runtime.receipt(r['receipt']['id'])),'physical':exact_observation(self.world.runtime.observe(d.Coordinate(*r['hub'])))}for r in requests],'limits':'Cadence/phase and interference remain physical. No expected sign is used for routing or response completion.'}
