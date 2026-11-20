"""Pure F1 control-flow Fakes + actual frozen Native-v2 file parsing. No DEE."""
from pathlib import Path
import argparse
import ast
import copy
import gzip
import hashlib
import json
import struct

HERE=Path(__file__).resolve().parent;P8=HERE.parent;SITE=(52,48,56)


def digest(b):return hashlib.sha256(b).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()


class FakeWorld:
    def __init__(self,target=True):self.tick=10;self.values={SITE:1229201223295434753 if target else 0};self.calls=0
    def diagnostic_fork(self,edits,authorize):
        assert authorize is True and len(edits)==1 and edits[0]['clock']is None
        self.calls+=1;b=copy.deepcopy(self);b.values[edits[0]['site']]=edits[0]['raw'];return b
    def run_until(self,tick):assert tick>=self.tick;self.tick=tick


def fake_observe(world,site):
    raw=world.values.get(tuple(site),0);v=[(raw>>s)&15 for s in(48,52,56)]
    return {'raw':str(raw),'clock':'123','tick':world.tick,'site':list(site),'state':raw&0xffffffff,
            'semantic':raw>>60,'s_reg':(raw>>32)&65535,'direction':[x-16 if x&8 else x for x in v]}


def fake_checkpoint(world,path,keep):
    raw=bytearray(67**3*8)
    for site,value in world.values.items():struct.pack_into('<Q',raw,((site[0]*67+site[1])*67+site[2])*8,value)
    fields={'N':67,'tick':world.tick,'RAW_sha256':digest(raw),'clocks_sha256':digest(b'fixed_Fake_clocks'),
            'paused':False,'next_event_id':12,'next_sequence':17,'phase':'same_fake_phase',
            'interfaces_count':4,'interfaces_sha256':digest(b'fake_interfaces'),'pending_count':1,
            'pending_sha256':digest(b'fake_pending'),'receipts_count':11,
            'receipts_sha256':digest(b'fake_receipts'),'backend':0,'threads':1}
    fields['Native_causal_prefix_sha256']=digest(canon(fields));fields['snapshot']={'path':str(path),'FAKE_NOT_A_NATIVE_SNAPSHOT':True}
    return fields,bytes(raw)if keep else None


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destino',type=Path,required=True);a=ap.parse_args()
    dest=a.destino.resolve()
    if dest.exists()or not dest.is_relative_to(HERE):raise ValueError('Fresh P8/codigo destination required')
    source=HERE/'pi08_diagnostico_cola_diagonal_R01.py';tree=ast.parse(source.read_text('utf-8'))
    names={'_Reader','_snapshot_fields','PostFormationAdapter','_world_holder'}
    selected=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))and n.name in names]
    assert len(selected)==4
    ns={'Path':Path,'SITE':SITE,'sha':digest,'gzip':gzip,'struct':struct}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(source)+'#pure_definitions_only','exec'),ns)
    checks=[];summaries={}
    def init(self,world):self.world=world
    def tick(self):return self.world.tick
    def run(self,target):return self.world.run_until(target)
    WorldAdapter=type('WorldAdapter',(),{'__module__':'app.lives','__init__':init,'tick':property(tick),'run_until':run})
    def hi(self,base):self.base=base
    HabitatAdapter=type('HabitatAdapter',(),{'__module__':'capacidades.adapter_habitat_R04','__init__':hi,
        'world':property(lambda s:s.base.world),'tick':property(lambda s:s.base.tick),'run_until':lambda s,t:s.base.run_until(t)})
    for arm in('raw_cut','identity_sham'):
        parent=FakeWorld();holder=WorldAdapter(parent);wrapped=HabitatAdapter(holder)
        assert ns['_world_holder'](wrapped)is holder
        observed=[]
        class Recorder:
            def capture(self,base):observed.append((base.tick,base.world.values[SITE]))
        hook=ns['PostFormationAdapter'](wrapped,holder=holder,q=10,arm=arm,ticks=[17,18,19,20],
            recorder=Recorder(),directory=Path('fake_output_not_written'),enable_fork=True,
            observe=fake_observe,checkpoint=fake_checkpoint,
            make_edit=lambda site,raw,label:{'site':site,'raw':raw,'clock':None,'label':label})
        hook.run_until(20);hook.run_until(22)
        assert hook.fork_count==1 and parent.calls==1 and parent.tick==18 and holder.world is not parent
        assert parent.values[SITE]==1229201223295434753
        assert holder.world.values[SITE]==(0 if arm=='raw_cut' else 1229201223295434753)
        assert hook.intervention['diagnostic_edit_applied']and all(hook.intervention['preserved_Native_fields'].values())
        assert observed[1]==(18,1229201223295434753)
        summaries[arm]={'Fake_fork_count':hook.fork_count,'parent_stopped_tick':parent.tick,
                        'branch_final_tick':holder.tick,'pre_edit_frame_preserved':True,
                        'parent_untouched_and_clock_None':True}
    checks.append({'name':'raw_cut_and_identity_sham_on_readonly_Habitat_wrapper','passed':True})
    checks.append({'name':'one_fork_only_and_no_parent_advance_after_fork','passed':True})
    missing=FakeWorld(False);base=WorldAdapter(missing)
    h=ns['PostFormationAdapter'](base,holder=base,q=10,arm='raw_cut',ticks=[18,19],recorder=None,
        directory=Path('not_written'),enable_fork=True,observe=fake_observe,
        checkpoint=fake_checkpoint,make_edit=lambda *args:None)
    h.run_until(20)
    assert h.fork_count==0 and base.world is missing and h.intervention['status']=='NO_FIXED_TARGET_NO_SEARCH_NO_EDIT'
    checks.append({'name':'absent_fixed_target_does_not_trigger_search_or_edit','passed':True})
    try:ns['_world_holder'](object())
    except ValueError:checks.append({'name':'unknown_adapter_rejected','passed':True})
    else:raise AssertionError('Unknown world setter accepted')
    # This format check reads one actually frozen snapshot, never a Native loader.
    reference=json.loads((P8/'fuentes/F1_PRECONTROL_A1_PI08_RECALCULADO_R01.json').read_text('utf-8'))
    old=reference['snapshots_public_views'][0];path=Path(old['snapshot']['path']);encoded=path.read_bytes()
    assert digest(encoded)==old['snapshot']['sha256']
    actual,raw=ns['_snapshot_fields'](path,True)
    mapping={'interfaces_sha256':'interface_specs_sha256','receipts_sha256':'receipts_block_sha256',
             'Native_causal_prefix_sha256':'causal_prefix_sha256','backend':'backend_enum'}
    exact=[]
    for key in('N','tick','RAW_sha256','clocks_sha256'):
        assert actual[key]==old['physical'][key];exact.append(key)
    for key in('phase','paused','next_event_id','next_sequence','threads','interfaces_count','interfaces_sha256',
               'pending_count','pending_sha256','receipts_count','receipts_sha256','Native_causal_prefix_sha256','backend'):
        assert actual[key]==old[mapping.get(key,key)];exact.append(key)
    assert len(raw)==67**3*8 and path.read_bytes()==encoded
    checks.append({'name':'actual_frozen_Native_v2_parser_matches_prior_complete_passive_reader','passed':True,'fields':exact})
    dest.mkdir(parents=True)
    result={'schema':'DEE.PI08.F1.pure_preparation_tests.v1','all_tests_passed':True,'checks':checks,
            'wrapper_source':str(source),'wrapper_sha256':digest(source.read_bytes()),'Fake_summaries':summaries,
            'actual_frozen_snapshot_parser_source':str(path),'actual_frozen_snapshot_sha256':digest(encoded),
            'new_Native_ticks':0,'actual_Native_Runtime_forks':0,'DEE_imports':0,'product_modified':False,
            'Native_intervention_physically_validated':False,
            'scope':'AST-selected pure control-flow Fakes plus one frozen-file binary-format check. '
                    'The Native fork API was not imported or executed; Root still must seal and run any actual F1.'}
    out=dest/'PRUEBA.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'proof':str(out),'sha256':digest(out.read_bytes()),'checks':len(checks),'new_Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
