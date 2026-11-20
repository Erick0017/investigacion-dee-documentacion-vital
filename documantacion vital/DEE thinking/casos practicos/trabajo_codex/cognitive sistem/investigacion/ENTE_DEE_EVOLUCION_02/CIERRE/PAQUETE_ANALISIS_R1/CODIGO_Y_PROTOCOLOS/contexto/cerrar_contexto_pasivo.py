"""Zero-tick support inspection and source/checkpoint preservation, not science replay."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'sistema'))
from app.lives import Store
from app.native_tools import physical
from capacidades import cierre_funcional_cf01 as cf
from capacidades import arquitectura_distribuida_mi02_r8 as body
EV=ROOT/'evidencia/campanas/ENTE_DEE_EVOLUCION_02/contexto'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    output=EV/'ESTADO_SOPORTES_PASIVO.json'
    if output.exists():raise FileExistsError('Original passive inspection protected')
    store=Store(ROOT/'sistema');rec,a=store.load('EO01_MAIN');before=physical(a.world);fields=[]
    for name,p in [('ctx_left',[5,15,13]),('ctx_right',[7,15,13]),('own_left',[5,15,15]),('own_right',[7,15,15]),('B_current_left',[18,13,15]),('B_current_right',[20,13,15])]:
        near=[body.obs(a,body.xyz(a,p,(x,y,z)))for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)if(x,y,z)!=(0,0,0)]
        fields.append({'name':name,'record':body.obs(a,p),'moore26':near,'alive_moore26':sum(q['state']>0 for q in near),'RAW_empty_neighbours':[q for q in near if q['raw']=='0']})
    after=physical(a.world)
    if before!=after:raise ValueError('Passive inspection changed physics')
    index=[]
    for p in sorted((ROOT/'sistema/estado/vidas').glob('AUX_EO02_CTX_*/VIDA.json')):
        r=json.loads(p.read_bytes());snapshot=ROOT/'sistema'/r['snapshot']
        index.append({'life':r['life_id'],'parent':r['parent'],'physical':r['physical'],'snapshot':str(snapshot),'snapshot_sha256':digest(snapshot),'snapshot_bytes':snapshot.stat().st_size,'life_record':str(p)})
    sources=[]
    for name in ['app/lives.py','app/native_tools.py','capacidades/cierre_funcional_cf01.py','capacidades/ente_operativo_01_core.py','capacidades/arquitectura_distribuida_mi02_r8.py','capacidades/integracion_distribuida_mi02_r6.py','capacidades/distribucion_social_mi02_r2.py']:
        source=ROOT/'sistema'/name;target=HERE/'codigo_ejecutado'/name
        if target.exists():raise FileExistsError(target)
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());sources.append({'path':name,'sha256':digest(source),'bytes':source.stat().st_size,'capture':'Exact existing source bytes, copied after pilots; no shared-source modification was made by this context work.'})
    row={'schema':'EO02.context.passive_support.v1','life':'EO01_MAIN','snapshot':rec['snapshot'],'snapshot_sha256':rec['snapshot_sha256'],'physical_before':before,'physical_after':after,'new_native_ticks':0,'witness':cf.witness(a),'fields':fields,'auxiliary_checkpoint_index':index,'shared_sources':sources,'scope':'Neighbour counts are exact descriptions, not proof that an eight-neighbour count alone caused the failed revision. No support was removed or altered.'}
    output.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'output':str(output),'tick':a.tick,'support_counts':{x['name']:x['alive_moore26']for x in fields},'auxiliary_lives':len(index),'new_ticks':0},ensure_ascii=False))
if __name__=='__main__':main()
