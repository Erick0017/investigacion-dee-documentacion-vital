from pathlib import Path
import sys,argparse,json,time


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--stage',default='discovery')
    a=p.parse_args();root=Path(a.root);sys.path.insert(0,str(root/'src'))
    from habitat.native_loop import run_native_loop
    cases=[('AB_same',dict(history='AB',consequence=1,context=0)),
           ('AB_changed',dict(history='AB',consequence=-1,context=1)),
           ('BA_same',dict(history='BA',consequence=-1,context=1)),
           ('BA_changed',dict(history='BA',consequence=1,context=0))]
    if a.stage=='confirmation':
        cases += [('H0_changed',dict(history='H0',consequence=-1,context=1)),
                  ('query_omitted',dict(history='AB',consequence=-1,context=1,query=False)),
                  ('consequence_omitted',dict(history='AB',consequence=-1,context=1,consequence_enabled=False)),
                  ('selected_Q_cut',dict(history='AB',consequence=-1,context=1,selected_cut='Q')),
                  ('unselected_P_cut',dict(history='AB',consequence=-1,context=1,selected_cut='P')),
                  ('roles_reversed_AB',dict(history='AB',consequence=-1,context=0)),
                  ('roles_reversed_BA',dict(history='BA',consequence=1,context=1)),
                  ('reserved_AB',dict(history='AB',consequence=-1,context=1,origin=(22,20,24),report=31)),
                  ('reserved_BA',dict(history='BA',consequence=1,context=0,origin=(28,26,18),report=41))]
    out=root/'experimentos/comparacion_seleccion'/('native_'+a.stage);out.mkdir(parents=True,exist_ok=True)
    (out/'EXPERIMENT_CONFIG.json').write_text(json.dumps({'cases':[{'id':n,'spec':s} for n,s in cases],
          'stage':a.stage,'freeze_before_execution':True,'decoder':'No native comparison product is inferred from external delta'},indent=2),encoding='utf-8')
    rows=[];start=time.monotonic()
    for name,spec in cases:
        try:
            x=run_native_loop(spec,out/name)
            em=next(t for t in x['trace'] if t['tick']==37)
            meet=next(t for t in x['trace'] if t['tick']==x['metadata']['arrival_tick'])
            info=next(t for t in x['trace'] if t['tick']==x['metadata']['arrival_tick']+9)
            row={'id':name,'emission':em,'meetings':{k:v for k,v in meet['ports'].items() if k.endswith('meeting')},
                 'access':{k:v for k,v in info['ports'].items() if k.endswith('access')},'receipts':x['receipts']}
        except Exception as e:row={'id':name,'technical_error':repr(e)}
        rows.append(row);print(json.dumps(row),flush=True)
        (out/'SUMMARY.json').write_text(json.dumps({'cases':rows,'elapsed_seconds':time.monotonic()-start},indent=2),encoding='utf-8')


if __name__=='__main__':main()
