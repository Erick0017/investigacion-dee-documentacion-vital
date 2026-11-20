"""Read-only identity bridge: original exact paired manifest versus updater bundle."""
import argparse,hashlib,json,zipfile
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--zip',type=Path,required=True);ap.add_argument('--source-manifest',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    raw=a.source_manifest.read_bytes();source=json.loads(raw);source_sha=hashlib.sha256(raw).hexdigest()
    assert source_sha=='9610905c1c3879fd4de3062894c2978c8cb5187e068185cfe889b7b2ee80a085'
    with zipfile.ZipFile(a.zip)as z:
        prefix='cognitive sistem/'
        catalog=json.loads(z.read(prefix+'entes/CATALOGO.json'))
        selected=[r for r in catalog['cuts']if r['alias']=='APD03_ASISTENTE'];assert len(selected)==1
        row=selected[0];assert row['source_life']=='APD03_MAIN'and row['tick']==604825
        bundle=json.loads(z.read(prefix+row['persistent_service']['bundle']));paired=bundle['paired_export_manifest']
        assert bundle['snapshot_package_member']==row['snapshot']
        for key in('life_id','profile','backend','snapshot_sha256','physical'):
            assert source[key]==paired[key],key
        def index(data):
            result={r['file']:(r['bytes'],r['sha256'])for r in data['members']}
            assert len(result)==len(data['members']);return result
        expected=index(source);offered=index(paired)
        assert expected==offered,{'omitted':sorted(expected.keys()-offered.keys()),'extra':sorted(offered.keys()-expected.keys()),'different':[n for n in expected.keys()&offered.keys()if expected[n]!=offered[n]]}
        assert row['snapshot_sha256']=='c7cf2e78837ed5f99c950016314bfe5f8fbfa868f72a67af36a94a78261a24ba'
        value={'schema':'APD03.paired_distribution_identity.N0.R01','new_native_ticks':0,'zip':str(a.zip),'source_manifest_sha256':source_sha,
            'paired_members_identical_by_relative_name_size_sha256':True,'members':len(expected),'expanded_member_bytes':sum(v[0]for v in expected.values()),
            'same_physical_fields':True,'snapshot_sha256':row['snapshot_sha256'],'selected_alias':row['alias'],
            'serialized_manifest_bytes_not_claimed_identical':True,'reason':'Existing updater emits a deduplicated bundle descriptor; the original member bytes and causal state are unchanged.',
            'scope':'Read-only selected bundle identity, not the subsequent exact archive extraction or new functional proof.'}
    with a.out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps(value,ensure_ascii=False))
if __name__=='__main__':main()
