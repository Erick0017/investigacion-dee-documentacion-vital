"""Passive complete Native terminal comparison for a prospective counter-input."""
from pathlib import Path
import array,ast,gzip,hashlib,json,struct,sys
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato/sistema'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def xyz(i):return [i//(67*67),(i//67)%67,i%67]
def main():
    parser=P.parent/'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    tree=ast.parse(parser.read_text(encoding='utf-8-sig'))
    nodes=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))and x.name in('Reader','parse','decode')]
    env={'array':array,'gzip':gzip,'struct':struct,'sys':sys,'sha':sha,'json':json}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(parser),'exec'),env)
    views={};sources={}
    for arm,name in [('izq','PI06_DISC_IZQ0_R01.json'),('intact','PI06_DISC_NONE_R01.json')]:
        proofpath=P/'control'/name;proof=read(proofpath)
        if not proof['closed']or proof['status']!='CLOSED'or proof['final_tick']!=826449:raise ValueError('Both fixed phases must be closed at the same age')
        cardpath=S/'estado/vidas'/proof['life_id']/'VIDA.json';card=read(cardpath)
        if card['physical']['tick']!=proof['final_tick']or card['snapshot_sha256']!=proof['final_snapshot_sha256']:raise ValueError('Do not replace the exact reached source with another continuation')
        views[arm]=env['parse'](S/card['snapshot'],card['snapshot_sha256'])
        sources[arm]={'proof':str(proofpath),'proof_sha256':sha(proofpath.read_bytes()),
            'life_id':proof['life_id'],'snapshot':card['snapshot'],'snapshot_sha256':card['snapshot_sha256']}
    a=views['izq'];b=views['intact'];rawdiff=[];clockdiff=[]
    for i,(x,y)in enumerate(zip(a[1],b[1])):
        if x!=y:rawdiff.append({'site':xyz(i),'izq':env['decode'](x),'intact':env['decode'](y),
                              'clock_izq':int(a[2][i]),'clock_intact':int(b[2][i])})
    for i,(x,y)in enumerate(zip(a[2],b[2])):
        if x!=y:clockdiff.append({'site':xyz(i),'izq':int(x),'intact':int(y)})
    sites={}
    for label,site in [('counter_source',[52,48,51]),('sham_source',[60,48,51]),
                       ('predicted_contact',[52,48,50]),('old_zero',[52,48,47])]:
        i=(site[0]*67+site[1])*67+site[2]
        sites[label]={'site':site,'izq':env['decode'](a[1][i]),'intact':env['decode'](b[1][i]),
                      'clock_izq':int(a[2][i]),'clock_intact':int(b[2][i])}
    output=P/'control/DIFERENCIA_TERMINAL_IZQ_NONE_PI06_R01.json'
    value={'schema':'DEE.PI06.terminal_spatial_difference.passive.R01','sources':sources,'N':67,'tick':826449,
        'RAW_difference_count':len(rawdiff),'RAW_differences':rawdiff,
        'clock_difference_count':len(clockdiff),'clock_differences':clockdiff,
        'prospective_sites':sites,'same_native_age':True,'Native_executed':False,'new_Native_ticks':0,
        'scope':'The full arrays are compared. A matching zero signature is not a unique lineage tag, and physical arrays alone are not full operational identity.',
        'prospective_counter_prediction':'If the old+Zzero is at47 atT, it reaches49 before eventsT+2. A legal−Zzero born at51 atT+2 can meet it at50 by frameT+3. No RAW/clocks edit or newSEM4. Exact encounter/absence and later FI remain empirical.'}
    with output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(output),'sha256':sha(output.read_bytes()),'RAW_differences':rawdiff,
        'clock_difference_count':len(clockdiff),'prospective_sites':sites},ensure_ascii=False))
if __name__=='__main__':main()
