from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
import recalcular as rc
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';OUT=LAB/'entrega_analisis';s=rc.read(EV/'LECTURA_CIENTIFICA.json')['stress_comparable_endpoints'];labels=['Sin ruido','Nominal: 2/intervalo','Severo: 24/intervalo'];keys=['no_noise','nominal','severe'];matrix=[];sources=[]
for key in keys:
    rr=[x for f in s[key]['sources']for x in rc.extrows(rc.read(EV/f))];matrix.append([int(x['qualified_in_declared_domain'])for x in rr]);sources.append({'condition':key,'files':s[key]['sources'],'ticks':[x['tick']for x in rr],'accepted_codes':matrix[-1]})
occupation=[rc.read(EV/'STRESS_MATCHED_144_WITHDRAW6.json')['physical']['occupied'],rc.read(EV/'TRUE_WITHDRAWAL_NOMINAL_173.json')['physical']['occupied'],rc.read(EV/'TRUE_WITHDRAWAL_SEVERE_173.json')['physical']['occupied']]
im=Image.new('RGB',(1500,850),'white');d=ImageDraw.Draw(im)
def text(x,y,t,n=22,color='#243243'):d.text((x,y),t,font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n),fill=color)
text(35,25,'Estrés: códigos, ocupación y función son resultados distintos',30);text(35,72,'Tres futuros desde T6237; mismo horizonte de 18 oportunidades',22);text(350,117,'Oscuro: código motor admitido. No equivale a comparación recuperada.',20)
for r,label in enumerate(labels):
    y=160+70*r;text(35,y+22,label)
    for c,v in enumerate(matrix[r]):d.rectangle((350+60*c,y,408+60*c,y+56),fill='#276b65'if v else'#d8dee9')
for c,t in[(0,6301),(5,6636),(11,7038),(12,7105),(17,7440)]:text(350+c*60,382,str(t),18)
for y in range(145,374,13):d.line((1069,y,1069,y+7),fill='#ad4b31',width=3)
text(1080,140,'6 intervalos limpios',17,'#ad4b31');text(660,420,'Tick DEE de la oportunidad',20);text(35,468,'Ocupación final en T7440 (logaritmo de sitios, no energía)',25)
for r,(label,v)in enumerate(zip(labels,occupation)):
    y=520+60*r;text(35,y+7,label);end=350+(math.log10(v)-2)/4*1080;d.rectangle((350,y,end,y+33),fill='#b75e49'if r==1 else'#64748b');text(end+12,y+5,str(v),20)
for power in range(2,7):
    x=350+(power-2)*270;d.line((x,710,x,720),fill='#64748b',width=1);text(x-20,727,str(10**power),17)
text(35,777,'Severo: volvió el código 9, pero no distinguió objetos 1 y 400. Sin objeto no hubo salida.',20);text(35,811,'No se acredita comparación recuperada. N67: 300763 sitios. Prefijo compartido, no réplicas independientes.',18)
im.save(OUT/'ESTRES_CODIGO_Y_OCUPACION.png');(OUT/'DATOS_FIGURA_ESTRES.json').write_text(json.dumps({'sources':sources,'occupied_T7440':occupation,'dimension':67,'scope':'Primary codes and occupancy, not a cognitive score'},ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(str(OUT/'ESTRES_CODIGO_Y_OCUPACION.png'))
