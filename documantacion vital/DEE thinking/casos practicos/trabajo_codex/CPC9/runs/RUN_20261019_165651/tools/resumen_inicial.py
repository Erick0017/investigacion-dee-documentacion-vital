"""Read-only calculations from primary observations; no DEE import."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def obs(o):return {'active':o.get('active'),'load':o.get('s_reg'),'direction':o.get('direction'),'raw':o.get('raw'),'clock':o.get('clock')}
def main():
    out=[]
    for folder in ('retorno','integracion','vida','vida_integral'):
        for path in sorted((ROOT/'resultados'/folder).glob('*/MEDICIONES.json')):
            d=json.loads(path.read_text(encoding='utf-8'))
            if 'frames'not in d:continue
            frames={x['tick']:x.get('view',x)for x in d['frames']}
            cfg=d.get('config',d.get('configuration',{}))
            row={'case':d.get('case_id'),'folder':folder,'status':d['status'],'last':d.get('last_complete_tick'),'primary':str(path.relative_to(ROOT)),
                 'quantity':[],'two_memory':[],'returns':[],'old_forms':[],'count':[],'regulator':[],'remote':[]}
            for t,f in frames.items():
                if t in(216,221,225):row['returns'].append({'tick':t,'banks':[{'bank':b['bank'],**obs(b['hub']if t==216 else b['use_site']if t==221 else b['delivery_site'])}for b in f.get('return',[])]})
                if t in(281,348,415,549,616,683,750,817,884):row['old_forms'].append({'tick':t,'values':{k:obs(v['delivery_site'])for k,v in f.get('joint',{}).items()}})
                if t in(70,137,204,338,405,472,539,606,673,740,807)and'quantity'in f:row['quantity'].append({'tick':t,'output':obs(f['quantity']['center'])})
                if t in(72,139,206)and'two_memory'in f:row['two_memory'].append({'tick':t,'output':obs(f['two_memory']['center'])})
                if t in(71,138,205)and'two_memory'in f:row['two_memory'].append({'tick':t,'R':obs(f['two_memory']['reference_site']),'O':obs(f['two_memory']['object_site'])})
                if t in(69,70,77,78,136,137)and'cpc9_regulator'in f:row['regulator'].append({'tick':t,'quantity':{k:obs(v)for k,v in f['cpc9_regulator']['quantity'].items()}})
                if t in(114,148)and'cpc9_count'in f:
                    field='reading1'if t==114 else'reading2'
                    row['count'].append({'tick':t,'qualified':[{'route':v['route_axis_candidate'],'heading':v['heading'],**obs(v[field])}for v in f['cpc9_count']['readers']
                        if v[field]['active']and v[field]['semantic']==1 and v[field]['s_reg']>7 and v[field]['direction']==[v['heading'],1,1 if t==114 else 0]]})
                if t in(215,282,349,416,483,550,617,684,751,818)and'count_repeated'in f:
                    z=1 if ((t-215)//67)%2==0 else 0
                    row['count'].append({'tick':t,'qualified':[{'route':v['route'],'heading':v['heading'],**obs(v['physical'])}for v in f['count_repeated']
                        if v['physical']['active']and v['physical']['semantic']==1 and v['physical']['s_reg']>7 and v['physical']['direction']==[v['heading'],1,z]]})
                if t in(343,410,416,477,483)and'remote_contact'in f:row['remote'].append({'tick':t,'values':{v['id']:obs(v['hub']if t in(343,410)else v['effect']if t==416 else v['renewed']if t==477 else v['renewed_effect'])for v in f['remote_contact']}})
            out.append(row)
    target=ROOT/'revision/RESUMEN_INICIAL_CALCULADO.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps({'scope':'Calculations only. No global cognitive verdict. Full primary exact values remain available.','cases':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in out:
        print(json.dumps({'case':r['case'],'status':r['status'],'last':r['last'],
             'returns':r['returns'],'count_qualified':[(x['tick'],len(x['qualified']))for x in r['count']],
             'TM':r['two_memory'],'old884':r['old_forms'][-1]if r['old_forms']else None},ensure_ascii=False))
if __name__=='__main__':main()
