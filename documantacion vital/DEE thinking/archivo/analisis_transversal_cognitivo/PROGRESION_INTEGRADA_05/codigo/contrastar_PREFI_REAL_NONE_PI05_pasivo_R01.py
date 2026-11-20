"""Frozen T817876 RAW/clocks/interfaces/agenda comparison; no SQLite/DEE."""
from pathlib import Path
import hashlib,json,runpy
P5=Path(__file__).resolve().parent.parent
OUT=P5/'control'/'CONTRASTE_PREFI_REAL_NONE_GLOBAL_R01.json'

def info(p):
    b=Path(p).read_bytes();return {'path':str(Path(p).resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def main():
    if OUT.exists():raise FileExistsError('Preserve existing proof')
    parser=P5/'codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    m=runpy.run_path(str(parser),run_name='pure_closed_snapshot_parser')
    S5=P5/'estados/candidato/sistema';values={};views={};sources={};preservation={}
    for arm,name in [('real','PI05_REAL_PREFI_R01.json'),('none','PI05_NONE_PREFI_R01.json')]:
        source=P5/'control'/name;d=json.loads(source.read_text(encoding='utf-8'))
        if not d['owner_closed_coherently']or d['after_tick']!=817876:raise ValueError('Exact closed preFI proof required')
        cut=d['final']['committed_snapshot'];snapshot=S5/cut['snapshot'];before=info(snapshot)
        v=m['parse'](snapshot,cut['snapshot_sha256']);after=info(snapshot)
        if before!=after:raise ValueError('Frozen snapshot changed during inspection')
        if v[0]['physical']!={k:cut['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')}:raise ValueError('Physical primary mismatch')
        values[arm]=v;views[arm]=v[0];sources[arm]=info(source);preservation[arm]={'before':before,'after':after,'equal':True}
    a=values['real'];b=values['none'];rd=[];cd=[]
    for i,(x,y)in enumerate(zip(a[1],b[1])):
        p=[i//4489,(i//67)%67,i%67]
        if x!=y:rd.append({'site':p,'real':m['decode'](x),'none':m['decode'](y)})
        if a[2][i]!=b[2][i]:cd.append(p)
    differing_meta=[{'key':k,'real_sha256':None if k not in a[6]else hashlib.sha256(a[6][k].encode()).hexdigest(),'none_sha256':None if k not in b[6]else hashlib.sha256(b[6][k].encode()).hexdigest()}for k in sorted(set(a[6])|set(b[6]))if a[6].get(k)!=b[6].get(k)]
    ra={v['id']:v for v in a[5]};rb={v['id']:v for v in b[5]};rc=[i for i in sorted(set(ra)|set(rb))if ra.get(i)!=rb.get(i)]
    special={}
    for name,p in [('future_collision_parent',[19,53,25]),('predicted_old_zeroZ_at_preFI',[19,53,17]),('MU_A',[14,14,15]),('MU_B',[16,14,15])]:
        i=(p[0]*67+p[1])*67+p[2];special[name]={'site':p,'real':m['decode'](a[1][i]),'none':m['decode'](b[1][i]),'clock_real':str(a[2][i]),'clock_none':str(b[2][i])}
    result={'schema':'DEE.PI05.frozen_preFI_REAL_NONE_global_comparison.R01','mode':'PASSIVE_COMPLETE_FROZEN_SNAPSHOTS_ONLY','Native_ticks':0,'DEE_imports':0,'SQLite_opened':False,'VIDA_current_not_read':True,'parser':info(parser),'sources':sources,'frozen_snapshot_before_after_preservation':preservation,'views':views,
      'comparison':{'GLOBAL_RAW_bytes_exact':a[7]==b[7],'GLOBAL_clocks_bytes_exact':a[8]==b[8],'RAW_difference_sites':len(rd),'RAW_differences':rd,'clock_difference_sites':len(cd),'clock_difference_positions':cd,'interfaces_exact':a[3]==b[3],'agenda_exact':a[4]==b[4],'agenda_real':a[4],'agenda_none':b[4],'Native_receipt_history_exact':a[5]==b[5],'Native_receipt_difference_count':len(rc),'Native_receipt_difference_IDs':rc,'metadata_exact':a[6]==b[6],'metadata_different_keys':differing_meta,'causal_prefix_bytes_exact':a[0]['causal_prefix_sha256']==b[0]['causal_prefix_sha256']},'specific_observations':special,
      'scope':'Same absolute age and declared FI geometry do not imply complete causal identity. Every RAW/clocks site was compared; no absence in the future nominal route is used as global erasure evidence. Immutable snapshot SHA was checked before/after; no live SQLite or future current VIDA was read. Counterfactual history metadata/receipts and environments remain distinct, even if physical buffers converge.'}
    with OUT.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(OUT),'bytes':OUT.stat().st_size,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'RAW_differences':rd,'clocks_exact':a[8]==b[8],'interfaces_exact':a[3]==b[3],'agenda_exact':a[4]==b[4],'receipt_difference_count':len(rc),'metadata_different_keys':len(differing_meta),'Native_ticks':0}))

if __name__=='__main__':main()
