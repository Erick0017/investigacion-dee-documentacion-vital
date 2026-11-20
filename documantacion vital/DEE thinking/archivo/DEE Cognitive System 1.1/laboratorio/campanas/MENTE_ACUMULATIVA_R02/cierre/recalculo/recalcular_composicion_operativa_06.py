"""Archived import/use/save/reopen of the acquired R10++ alternate life."""
import argparse
import importlib.util
import json
from pathlib import Path

sp=importlib.util.spec_from_file_location('service_archived',Path(__file__).with_name('recalcular_servicio_01.py'))
s=importlib.util.module_from_spec(sp);sp.loader.exec_module(s)
c=s.common


def calculate(root):
    audit=c.Audit(root);checks=[];sessions=[];fences=[]
    def check(name,value):
        checks.append({'check':name,'observed':bool(value)})
        if not value:audit.issues.append({'check':name,'issue':'not established'})
    names=['55_IMPORTAR_COMPOSICION_PLUS','56_ESTADO_COMPOSICION_PLUS','57_FORK_COMPOSICION_PLUS',
           '58_COMPOSICION_PLUS_GESTOR','59_ANTERIORES_TRAS_PLUS','60_GUARDAR_PLUS_USO','61_REABRIR_PLUS_USO']
    raw={name:audit.load(name+'.json.gz')for name in names};r={name:x['result']for name,x in raw.items()}
    reservation=audit.load('entrada_comun/MA02_R10_PLUS.R10.json.gz')
    history=next(row for row in reservation['rows']if row['kind']=='joint')['history_snapshot']
    check('import references exact complete acquired++history',r[names[0]]['parent']['encoded_sha256']==history['sha256'])
    check('ready import is T2616, not reconstructionT0',r[names[0]]['physical']['tick']==2616)
    fp=lambda q:s.fingerprint(q.get('physical',q.get('INSTRUMENTO',{}).get('physical')))
    check('ready status/fork preserve same native fields',fp(r[names[0]])==fp(r[names[1]])==fp(r[names[2]]))
    check('evaluation fork names its acquired source',r[names[2]]['parent']['life_id']=='MA02_COMPOSICION_PLUS_LISTA')
    for name,x in raw.items():
        check(name+': archived process successful',x['returncode']==0 and not x['timed_out'])
        check(name+': stdout exact result',json.loads(x['stdout'])==x['result'])
        value=x['result'];fence=value.get('INSTRUMENTO_FENCE')
        if fence:
            check(name+': no denied fence operation',fence['denied']==[])
            check(name+': no environment process during pure composition',fence['exact_environment_processes']==[])
            fences.append({'case':name,'denied':fence['denied'],'exact_environment_processes':fence['exact_environment_processes']})
        content=value.get('result',{})
        if 'rows'not in content:continue
        rows=[];requests=[]
        for row in content['rows']:
            for o in row['reader']['panel']:audit.check_observation(o,name+':panel')
            for frame in row['frames']:
                for o in frame['sites']:audit.check_observation(o,name+':frame')
            joint=row['kind']=='joint'
            vectors={**s.V,'epsilon':(1,-1,0)}
            gates=[s.position(v,4,z)for v in vectors.values()for z in(-1,1)]
            decoded=c.decode(row['reader']['panel'],[(33,33,27),(33,33,39)])if joint else c.decode(row['reader']['panel'],gates,{s.position(v,4,z):z for v in vectors.values()for z in(-1,1)})
            check(name+': fixed RAW decoder',decoded['decoded_sign']==row['reader']['formed_native_command'])
            check(name+': fixed read window',row['read_tick']==(row['second_tick']+9 if joint else row['input_tick']+4))
            check(name+': exact parent cut used',row['before']['tick']<row['after']['tick'])
            if joint:
                check(name+': native positive joint output',decoded['decoded_sign']==1)
                check(name+': same physical output as reserved R10PLUS',row['reader']['panel']==next(q for q in reservation['rows']if q['kind']=='joint')['fixed_panel'])
            expected=1 if joint or row['context_signal']=='gamma'else -1
            rows.append({'kind':row['kind'],'context_for_auditor':row['context_signal'],'input_tick':row['input_tick'],
                'read_tick':row['read_tick'],**decoded,'expected_for_external_scoring_only':expected,
                'correct':decoded['decoded_sign']==expected,'receipts':c.receipt_summary(row['requests'])})
            requests.extend(row['requests'])
        sessions.append({'case':name,'life':value['INSTRUMENTO']['life_id'],'rows':rows,'requested':len(rows),
            'responded':sum(q['decoded_sign']is not None for q in rows),'correct':sum(q['correct']for q in rows),
            'receipts':c.receipt_summary(requests),'final_physical':fp(value)})
    check('composition uses copied ready prefix',s.fingerprint(r[names[3]]['result']['rows'][0]['before'])==fp(r[names[2]]))
    check('gamma/delta use follows composition without reset',s.fingerprint(r[names[4]]['result']['rows'][0]['before'])==fp(r[names[3]]))
    check('save and another-process passive status keep native fields',fp(r[names[4]])==fp(r[names[5]])==fp(r[names[6]]))
    return {'schema':'DEE.MA02.archived_composition_service06.v1','new_dee_ticks':0,'sources':audit.sources,
        'sessions':sessions,'fences':fences,'checks':checks,'observations_checked':audit.observations,'issues':audit.issues,
        'scope_and_limits':['Ready++is an imported full acquired R10 branch at2616, not MAIN5, not a new T0 and not merged knowledge.',
            'One native composition and then two retained gamma/delta accesses were used consecutively in the evaluation copy; the ready original was not consumed.',
            'Gate decoding does not receive historical signs; expected fields above are auditor scoring only.',
            'Composition consumes alpha/beta accesses. This operational check is not proof of retention for all four contents after composition.',
            'Save/reopen physical fingerprints compare N,tick,RAW,clocks, not equality of all whole-snapshot metadata.',
            'Archived process/fence records are recalculated, not re-executed by this script.']}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args();x=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'issues':len(x['issues']),'observations_checked':x['observations_checked'],'sessions':[{k:q[k]for k in('case','requested','responded','correct','receipts')}for q in x['sessions']],'issue_sample':x['issues'][:5]}))
    return 1 if x['issues']else 0


if __name__=='__main__':raise SystemExit(main())
