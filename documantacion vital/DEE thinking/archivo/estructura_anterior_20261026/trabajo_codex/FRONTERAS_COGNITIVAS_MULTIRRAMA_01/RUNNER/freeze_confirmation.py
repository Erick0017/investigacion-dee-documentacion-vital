"""Numeric queue selection, fixed reserves, and measurement-only coverage."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from observations import dump,sha,signature
from run_multibranch import utc

def main():
    root=Path(sys.argv[1]);p=root/'CAMPAIGN_CONFIG.json';cfg=json.loads(p.read_text(encoding='utf-8'))
    if cfg.get('confirmation_frozen_utc'):print('CONFIRMATION_ALREADY_FROZEN');return
    def load(b,n):return json.loads((root/'BRANCHES'/b/n/'MEASUREMENTS.json').read_text(encoding='utf-8'))
    paired=load('L01','balanced_paired');none=load('L01','balanced_none');unpaired=load('L01','balanced_unpaired')
    comp=load('L05','full');om1=load('L05','omit1');om2=load('L05','omit2');cut=load('L05','link_cut')
    signal=load('L08','full');sig0=load('L08','naive1');sig1=load('L08','naive2')
    eligible={'L01':paired['phi']!=none['phi'] and paired['phi']!=unpaired['phi'],
              'L02':load('L02','paired_1')['phi']!=load('L02','unpaired_1')['phi'],
              'L04':load('L04','paired')['phi']!=load('L04','none')['phi'],
              'L05':all(signature(comp['second_response'])!=signature(x['second_response']) for x in (om1,om2,cut)),
              'L08':all(signal['second_response']['direction']!=x['second_response']['direction'] for x in (sig0,sig1))}
    queue=[]
    def case(b,name,kind,spec,role='treatment',level=1,configuration=1):
        queue.append({'branch':b,'case':name,'kind':kind,'spec':spec,'role':role,'level':level,
                      'configuration':configuration,'frozen_utc':utc()})
    translations=[(2,3,1),(4,2,3)]
    for j,tr in enumerate(translations):
        anchors=[[10+tr[0],10+tr[1],8+tr[2]],[10+tr[0],10+tr[1],24+tr[2]]]
        if eligible['L01']:
            for arm in ('paired','unpaired'):
                case('L01',f'reserve{j}_{arm}','association',{'arm':arm,'cues':[5,5],'events':[7,11],'query':[5,5],
                      'anchors':anchors,'research_timing':arm=='unpaired'},'treatment' if arm=='paired' else 'control')
        if eligible['L02']:
            for paired in (True,False):
                case('L02',f'reserve{j}_{"paired" if paired else "unpaired"}','anticipation',
                     {'sign':1 if j==0 else -1,'paired':paired,'translation':tr,'query':17 if j==0 else 19},
                     'treatment' if paired else 'control')
        if eligible['L04']:
            for arm in ('paired','none'):
                case('L04',f'reserve{j}_{arm}','association',{'arm':arm,'events':[7,15],'query':17 if j==0 else 19,'anchors':anchors},
                     'treatment' if arm=='paired' else 'control')
        if eligible['L05']:
            for arm in ('full','link_cut'):
                case('L05',f'reserve{j}_{arm}','composition',{'arm':arm,'translation':tr,'query':17 if j==0 else 19,'horizon':20},
                     'treatment' if arm=='full' else 'control')
        if eligible['L08']:
            for arm in ('full','naive2'):
                case('L08',f'reserve{j}_{arm}','composition',{'arm':arm,'translation':tr,'query':17 if j==0 else 19,
                     'receiver_axis':'z','horizon':22},'treatment' if arm=='full' else 'control')
    if eligible['L01']:
        case('L01','retention_one_toroidal_lap','association',{'cues':[5,5],'events':[7,11],'query':[5,5],'extra_age':34},level=2)
    if eligible['L02']:
        case('L02','reserved_longer_consequence','anticipation',{'consequence_tick':22,'query':17},level=2)
        case('L02','naive_age_matched','anticipation',{'naive':True},role='control',level=1)
    if eligible['L04']:
        case('L04','new_payload_context','association',{'events':[7,15],'query':29,'anchors':[[14,16,12],[14,16,28]]},level=2)
    if eligible['L05']:
        case('L05','lineage_reuse_query','composition',{'horizon':20,'extra_query':17},level=2)
    if eligible['L08']:
        case('L08','reserved_inverted_receiver','composition',{'receiver_axis':'z','receiver_sign':-1,'translation':(4,2,3),'query':23,'horizon':22},level=2)
    # Second architecture for L06, no-input quiescent prepared context; original attempts retained.
    for hist in ('AB','BA','H0'):
        case('L06','quiescent_'+hist,'rest_or_damage',{'history':hist,'remove_environment':True,'reference_control':True},
             'treatment' if hist=='AB' else 'control',level=0)
    for j,origin in enumerate(((22,20,24),(28,26,18))):
        for hist in ('AB','H0'):
            case('L06',f'reserve{j}_{hist}','rest_or_damage',{'history':hist,'origin':origin,'remove_environment':True,'reference_control':True},
                 'treatment' if hist=='AB' else 'control',level=1)
    # A single new joint apparatus from unlearned native preparation, no snapshot grafting.
    # It tests query payload equivalence (L04) through the physically sequential transform (L05).
    combination={'id':'L04_PLUS_L05','kind':'composition','frozen_utc':utc(),
                 'N':34,'components':{'first_relation':[5,7],'second_relation':[9,15]},
                 'query_reserved_payload':23,'horizon':20,
                 'controls':['omit1','omit2','link_cut','receiver_offpath_sham'],
                 'resources':'full and route sham same initial native carriers; omissions separately record dose differences',
                 'origin':'all relations acquired at tick 3 in the new joint Runtime; never combined learned snapshots',
                 'no_nonadditivity_requirement':True}
    cfg['cases']+=queue;cfg['confirmation_frozen_utc']=utc();cfg['confirmation_parent_config_sha256']=sha(p)
    cfg['numeric_queue_eligibility']=eligible;cfg['combinations']=[combination]
    cfg['coverage_pending']={
      'L01':'Signal identity is a fixed physical route/direction; no symbolic association decoder.',
      'L02':'Early acquired routing is measured. Learned temporal expectation vs transport timing is not separated by this first apparatus.',
      'L03':'Post-emission causal effects are measured; learned contingency distinction and matched open replay are not implemented.',
      'L04':'Reserved finite query transforms are measured; broader acquisition of categories beyond fixed physical interfaces is untested.',
      'L05':'Transformations are additive/mobile and queries transform the same carriers.',
      'L06':'Early probes valid; some original late probes rejected occupied. New quiescent context is a distinct declared preparation.',
      'L07':'H3 is calibration only. Native damaged basal states are measured without host repair; whole acquired signature restoration must be read from data.',
      'L08':'Finite emitter/receiver relational histories, not independently renewed complete material bodies. Acquired symbolic code untested.',
      'L09':'Hidden source condition also reaches uninformative route backgrounds; acquired choice of informative intervention not isolated.'}
    dump(p,cfg);print('FROZEN',len(queue),'cases; eligibility',eligible)

if __name__=='__main__':main()
