from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import recalcular as rc
LAB=Path(__file__).resolve().parent;ROOT=LAB.parents[2];EV=ROOT/'evidencia/campanas/INTEGRACION_COGNITIVA_SITUADA_E1_01';OUT=LAB/'entrega_analisis';s=rc.read(EV/'LECTURA_CIENTIFICA.json')['stress_comparable_endpoints']
labels=['Sin ruido','Nominal: 2/intervalo','Severo: 24/intervalo'];keys=['no_noise','nominal','severe'];matrix=[];sources=[]
for key in keys:
    rr=[x for f in s[key]['sources']for x in rc.extrows(rc.read(EV/f))];matrix.append([int(x['qualified_in_declared_domain'])for x in rr]);sources.append({'condition':key,'files':s[key]['sources'],'ticks':[x['tick']for x in rr],'accepted_codes':matrix[-1]})
occupation=[rc.read(EV/'STRESS_MATCHED_144_WITHDRAW6.json')['physical']['occupied'],rc.read(EV/'TRUE_WITHDRAWAL_NOMINAL_173.json')['physical']['occupied'],rc.read(EV/'TRUE_WITHDRAWAL_SEVERE_173.json')['physical']['occupied']]
fig,(a,b)=plt.subplots(2,1,figsize=(9,5.7),gridspec_kw={'height_ratios':[1.45,1]},layout='constrained')
a.imshow(matrix,aspect='auto',cmap=ListedColormap(['#d8dee9','#276b65']),vmin=0,vmax=1,interpolation='nearest');a.set_yticks(range(3),labels);a.set_xticks([0,5,11,12,17],[6301,6636,7038,7105,7440]);a.set_xlabel('Tick DEE de cada oportunidad externa');a.axvline(11.5,color='#ad4b31',linestyle='--',linewidth=1.5);a.set_title('Código motor admitido (oscuro), no prueba de función recuperada',loc='left',fontweight='bold',fontsize=11);a.text(12,-.8,'6 intervalos sin cola de ruido',color='#ad4b31',fontsize=9)
b.barh(range(3),occupation,color=['#64748b','#b75e49','#64748b']);b.set_yticks(range(3),labels);b.invert_yaxis();b.set_xscale('log');b.set_xlim(100,1_000_000);b.set_xlabel('Sitios con state distinto de0 en T7440 (escala logarítmica)');b.set_title('Ocupación no equivale a capacidad ni a energía',loc='left',fontweight='bold',fontsize=11)
for y,v in enumerate(occupation):b.text(v*1.12,y,str(v),va='center',fontsize=9)
fig.suptitle('Tres futuros de E1 desde T6237; mismo horizonte de18 oportunidades',fontsize=12,fontweight='bold');fig.text(.02,-.035,'Severo: volvió el código9, pero no distinguió objetos1 y400; no se acredita comparación recuperada.\nRamas con prefijo compartido, no18réplicas independientes. N67,300763sitios.',fontsize=9)
fig.savefig(OUT/'ESTRES_CODIGO_Y_OCUPACION.png',dpi=150,bbox_inches='tight');fig.savefig(OUT/'ESTRES_CODIGO_Y_OCUPACION.svg',bbox_inches='tight');plt.close(fig)
(OUT/'DATOS_FIGURA_ESTRES.json').write_text(json.dumps({'sources':sources,'occupied_T7440':occupation,'dimension':67,'scope':'All values come from primary responses/endpoints. A valid code is not relabeled as restored magnitude comparison.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'figure':str(OUT/'ESTRES_CODIGO_Y_OCUPACION.png'),'occupied':occupation}))
