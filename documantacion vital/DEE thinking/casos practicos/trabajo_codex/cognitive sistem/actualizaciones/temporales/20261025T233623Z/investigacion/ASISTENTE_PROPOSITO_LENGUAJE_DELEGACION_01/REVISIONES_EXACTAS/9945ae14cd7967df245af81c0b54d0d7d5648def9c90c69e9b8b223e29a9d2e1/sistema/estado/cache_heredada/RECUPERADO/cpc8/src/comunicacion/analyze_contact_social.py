"""Reconcile strict native contact communication and independent inherited functions."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src/relaciones'))
from analyze_full_spatial_e1 import functional_windows,receipt
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def snapshots(m):return[{k:x.get(k)for k in('path','tick','sha256','physical')}for x in m.get('snapshots',[])]
def source_parent(root,m):
    name=m['parent']['snapshot'].replace('\\','/').split('/')[-2];path=root/'resultados/semantica'/name/'MEASUREMENTS.json';return json.loads(path.read_text(encoding='utf8'))
def analyze(root):
    rows=[]
    for path in sorted((root/'resultados/semantica').glob('CTS_*/MEASUREMENTS.json')):
        m=json.loads(path.read_text(encoding='utf8'));schema=m['schema'];technical=schema.endswith('restore.v1');base=m if m.get('geometry')else source_parent(root,m);g=base['geometry'];case=base['case'];rcv={r['id']:r for r in g['contact_social']['receivers']};captures=m.get('contact_social_observations',m.get('contact_social_observations_after_fork',m.get('contact_social_observations_after_restore',[])));q=[x for x in captures if x['phase']=='QUERY'];uses=[]
        for p in captures:
            if p['phase']not in('USE','DELIVERY'):continue
            r=rcv[p['receiver']];expected=[0,1,r['expected_content_z']+1];physical=p['physical'];valid=bool(physical['active']and physical['semantic']==1 and physical['direction']==expected and physical['s_reg']>case.get('communication_use_load',13));uses.append({'receiver':p['receiver'],'phase':p['phase'],'tick':p['tick'],'expected':expected,'physical':physical,'valid_native_use_or_delivery':valid})
        fs=functional_windows(m)if m.get('frames')and m.get('status')=='MEASURED'else []
        frames={f['tick']:f for f in m.get('frames',[])};late=[];z=0 if case.get('late_actor_mode','offpath')=='onpath'else-1;kind='right.'+('changed'if z==0 else'free')
        for tick,field,vector,payload in((411,'query_site',[-1,1,z],5),(417,'effect_site',[0,1,z],7),(478,'renewed_site',[-1,1,z],5),(484,'renewed_effect',[0,1,z],7)):
            if tick not in frames:continue
            p=frames[tick]['contact'][kind][field];late.append({'tick':tick,'physical':p,'expected_direction':vector,'valid':bool(p['active']and p['semantic']==1 and p['direction']==vector and p['s_reg']>payload)})
        axis=1 if case.get('order','AB')=='AB'else-1;bank=('plus'if axis==1 else'minus')+'.'+('changed'if case.get('actor_mode','contact')=='contact'else'free');word616=frames.get(616,{}).get('joint',{}).get(bank,{}).get('delivery_site')
        if word616 is None:word616=m.get('final_word',{}).get(bank,{}).get('delivery_site')
        word616valid=bool(word616 and word616['active']and word616['semantic']==1 and word616['direction']==[0,1,1]and word616['s_reg']>13)
        social=m.get('social_captures',[]);mode428=[x for x in social if x['phase']=='FORM_QUERY'and x['tick']==428];use89=[]
        for f in m.get('return_use_observations',[]):
            if f['tick']==89:
                for r in f['receivers']:
                    p=r['contact'];use89.append({'source_candidate':r['source_candidate'],'physical':p,'valid':bool(p['active']and p['semantic']==1 and p['direction']==[0,0,-1]and p['s_reg']>13)})
        initiative_sequence=[]
        for record in m.get('initiative_captures',[]):
            t=record['tick']
            if t not in(72,77,86):continue
            for branch in record['branches']:
                source_value=case.get('initiative_source',1);point=branch['question']if t==72 else branch['source']if t==77 else branch['return'][str(source_value)]
                vector=[0,1,1]if t==72 else[source_value,0,0]if t==77 else[source_value,-1,-1];load=7 if t==72 else 23 if t==77 else 30
                initiative_sequence.append({'tick':t,'physical':point,'expected_direction':vector,'expected_load':load,'valid':bool(point['active']and point['semantic']==1 and point['direction']==vector and point['s_reg']==load)})
        rows.append({'case_id':m['case']['id'],'schema':schema,'primary':path.relative_to(root).as_posix(),'sha256':sha(path),'status':m['status'],'preparations':m.get('preparations',0),'diagnostic_forks':m.get('diagnostic_forks',0),'technical_continuations':m.get('continuations',0)if technical else 0,'source_sha256':m.get('source_sha256'),'configuration_sha256':m.get('configuration_sha256'),'resources':g['resources'],'added_contact_social_ports':g['contact_social']['new_interfaces'],'added_counterflow_ports':len(g.get('contact_regulation',{}).get('items',[])),'added_initial_material':0,'parent':m.get('parent'),'parent_unchanged':m.get('parent_unchanged'),'physical_checks':m.get('checks'),'requests_all_including_inherited':len(m.get('requests',[])),'query554':[{'receiver':x['receiver'],'covered':x['covered'],'content':x['content'],'physical':x['physical'],'request_applied':x['request_applied']}for x in q],'valid_query554':sum(x['covered']for x in q),'native_uses_and_deliveries':uses,'old_functional_windows':fs,'old_functional_summary':{f:{'valid':sum(x['valid_functional_readout']for x in fs if x['family']==f),'windows':sum(x['family']==f for x in fs)}for f in sorted({x['family']for x in fs})},'late_contact_query_and_use':late,'MODE_B428_valid':sum(x['covered']for x in mode428)if mode428 else None,'IUE_use89':use89,'IUE_use89_valid':sum(x['valid']for x in use89),'IUE_sequence72_77_86':initiative_sequence,'word616':{'physical':word616,'valid':word616valid}if word616 else None,'snapshots':snapshots(m),'new_source_contact_experience_after484':[],'interpretation_scope':'Strict local native reader; components and old functions reported separately. No global semantic verdict.'})
    return{'schema':'CPC8R.contact_socialE1.analysis.v1','counts':{'primary_records':len(rows),'preparations':sum(x['preparations']for x in rows),'diagnostic_forks':sum(x['diagnostic_forks']for x in rows),'technical_continuations':sum(x['technical_continuations']for x in rows)},'prepared':'Geometry/format, complementary read and recording directions, all candidate cues and use resources, fixed counterflow. No learned regulation policy.','acquired':'Contact consequenceZ from native actor/medium interaction is expressed by acquired source relation, then physically paired with recipient recordingcue. Both cohorts have equal source/message doses but distinctZ.','cases':rows}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,default=ROOT/'resultados/semantica/CONTACT_SOCIAL_E1_ANALYSIS.json');a=p.parse_args();m=analyze(a.root);a.out.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'counts':m['counts'],'cases':[{'id':x['case_id'],'q':x['valid_query554'],'functions':x['old_functional_summary'],'late':[y['valid']for y in x['late_contact_query_and_use']],'MODE':x['MODE_B428_valid'],'word616':x['word616']['valid']if x['word616']else None}for x in m['cases']]}))
