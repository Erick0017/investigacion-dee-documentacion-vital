"""No engine: distinguish useful multi-function continuation from a new loss."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).parent))
from instrumentos_pc01 import packed,idx,sha
p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);a=p.parse_args();out={}
for path in sorted((a.evidence/'CONTINUIDAD_CARGA_28').glob('*/PRIMARIOS.json')):
    prim=json.loads(path.read_bytes());points=[]
    for row in prim['blocks']:
        t=row['global_sample']['tick'];q=[(22-(t-32501))%67,(38+t-32501)%67,(50-(t-32501))%67];raw={i:int(v)for i,v,c in row['global_sample']['rows']};r=packed(raw.get(idx(q,67),0));points.append({'tick':t,'nominal_free_position':q,'record':r,'valid_free_signature':r['state']==1 and r['semantic']==1 and r['direction']==[-1,1,-1],'magnitude_word':row['magnitude']['TRADUCCION']['SPANISH_DECODED'],'spatial_word':row['spatial']['SPANISH_DECODED'],'probe_free_word':row.get('free',{}).get('SPANISH_DECODED')})
    out[prim['case']]={'source':str(path),'sha256':sha(path),'points':points,'first_sample_missing':next((r['tick']for r in points if not r['valid_free_signature']),None),'final':prim['commit']['result']['final'],'scope':'Onepredictedcarrieratfixedcadenceisnota completeknowledgeinventory. Preciselossrequiresfurthercausaltrace. No forgettingclaimfromthissampler.'}
(a.evidence/'CONTINUIDAD_Y_NUEVO_LIMITE_28.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(out,ensure_ascii=False))
