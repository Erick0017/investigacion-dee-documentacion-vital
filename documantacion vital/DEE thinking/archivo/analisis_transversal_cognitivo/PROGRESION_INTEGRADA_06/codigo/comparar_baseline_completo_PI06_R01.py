"""Compare closed baseline snapshots passively; no engine or actor imports."""
from pathlib import Path
import array,ast,gzip,hashlib,json,struct,sys

P=Path(__file__).resolve().parents[1]
S=P/'estados/candidato/sistema'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def small(v):
    data=json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
    return v if len(data)<240 else {'bytes':len(data),'sha256':sha(data)}
def differences(a,b,path='',result=None):
    if result is None:result=[]
    if type(a)!=type(b):result.append({'pointer':path,'normal':small(a),'global':small(b)})
    elif isinstance(a,dict):
        for k in sorted(set(a)|set(b)):
            if k not in a or k not in b:result.append({'pointer':path+'/'+k,'normal':small(a.get(k)),'global':small(b.get(k))})
            else:differences(a[k],b[k],path+'/'+k,result)
    elif isinstance(a,list):
        if len(a)!=len(b):result.append({'pointer':path+'/length','normal':len(a),'global':len(b)})
        for i,(x,y)in enumerate(zip(a,b)):differences(x,y,path+'/'+str(i),result)
    elif a!=b:result.append({'pointer':path,'normal':small(a),'global':small(b)})
    return result
def main():
    parser=P.parent/'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    tree=ast.parse(parser.read_text(encoding='utf-8-sig'))
    body=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))and x.name in ('Reader','parse','decode')]
    env={'array':array,'gzip':gzip,'struct':struct,'sys':sys,'sha':sha,'json':json}
    exec(compile(ast.Module(body=body,type_ignores=[]),str(parser),'exec'),env)
    values={};sources={}
    for arm in ('normal','global'):
        path=P/'control'/('BASELINE_'+arm+'_PI06_R01.json');proof=read(path)
        if proof['status']!='COMPLETED'or not proof['owner_closed_coherently']:raise ValueError('Both matched arms must be closed coherently')
        card=proof['closed_card'];snapshot=S/card['snapshot'];hashed=card['snapshot_sha256']
        values[arm]=env['parse'](snapshot,hashed)
        if sha(snapshot.read_bytes())!=hashed:raise ValueError('Concurrent snapshot change')
        if values[arm][0]['physical']['tick']!=825849 or proof['actual_new_ticks']!=938:raise ValueError('Finite matching source age required')
        sources[arm]={'proof':str(path),'proof_sha256':sha(path.read_bytes()),'snapshot':str(snapshot),'snapshot_sha256':hashed}
    a=values['normal'];b=values['global'];an=a[0];bn=b[0]
    keys=('physical','paused','phase','next_event_id','next_sequence','backend_enum','threads',
          'interfaces_count','interface_specs_sha256','pending_count','pending_sha256',
          'receipts_count','receipts_block_sha256','causal_prefix_sha256')
    native={k:{'normal':an[k],'global':bn[k],'equal':an[k]==bn[k]}for k in keys}
    metadata=[]
    for key in sorted(set(a[6])|set(b[6])):
        if a[6].get(key)==b[6].get(key):continue
        x=a[6].get(key);y=b[6].get(key)
        try:diff=differences(json.loads(x),json.loads(y))
        except (ValueError,TypeError):diff=None
        metadata.append({'key':key,'normal_bytes':len(x.encode())if x is not None else None,
            'global_bytes':len(y.encode())if y is not None else None,
            'normal_sha256':sha(x.encode())if x is not None else None,
            'global_sha256':sha(y.encode())if y is not None else None,
            'all_changed_json_leaves':diff,'only_documentary_identity_not_assumed':True})
    all_native_equal=all(x['equal']for x in native.values())
    value={'schema':'DEE.PI06.baseline.complete_snapshot.passivity_contrast.R01',
        'sources':sources,'native_fields':native,'all_pre_metadata_Native_fields_equal':all_native_equal,
        'RAW_arrays_exact_equal':a[7]==b[7],'clocks_arrays_exact_equal':a[8]==b[8],
        'interface_specs_exact_equal':a[3]==b[3],'pending_agenda_exact_equal':a[4]==b[4],
        'all_Native_receipts_exact_equal':a[5]==b[5],'metadata_keys_normal':len(a[6]),
        'metadata_keys_global':len(b[6]),'changed_metadata':metadata,
        'changed_metadata_keys':[x['key']for x in metadata],
        'Native_executed':False,'new_Native_ticks':0,
        'passivity_scope':'Equal-age938tick baseline with no new material input. The finite descriptor capture/segmentation is compared here; this does not validate all future observations or material queries.',
        'full_operational_state_not_compared':'This check covers the complete native snapshot including all metadata, not SQLite/outbox/external environments. Their whole-pair preservation remains separate.'}
    output=P/'control/CONTRASTE_BASELINE_COMPLETO_PI06_R01.json'
    with output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(output),'sha256':sha(output.read_bytes()),'native_equal':all_native_equal,
        'changed_metadata_keys':value['changed_metadata_keys'],'Native_executed':False}))

if __name__=='__main__':main()
