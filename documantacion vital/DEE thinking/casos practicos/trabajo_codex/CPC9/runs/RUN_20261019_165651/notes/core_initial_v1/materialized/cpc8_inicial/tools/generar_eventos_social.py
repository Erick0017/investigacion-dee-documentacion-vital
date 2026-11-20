"""Public events for the integrated I21 contract and a matched source control."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'configuraciones/demo';folder.mkdir(parents=True,exist_ok=True)
values=[-1 if k%3==0 else 1 for k in range(65)];values[16]=1
for mode in('integrada','control'):
 commands=['crear social','orden BA']
 for k in range(32):
  if mode=='control' and k==16:commands+=['acontecimiento L17 1 0','señal L17 1']
  else:commands.append(f'experiencia L{k+1:02d} {values[k]} 0')
 commands+=['consultar '+','.join(f'L{k+1:02d}' for k in range(32) if k!=16)+' 131',
  'oportunidades','social enseñar','social consultar 1','social renovar -1','avanzar 5','consecuencia 1','avanzar 260']
 commands +=[f'experiencia L{k+1:02d} {values[k]} 262' for k in range(32,65)]
 commands +=['consultar '+','.join(f'L{k+1:02d}' for k in range(65))+' 393','avanzar 396','revisar 1 treatment',
  'consultar '+','.join(f'L{k+1:02d}' for k in range(65))+' 655','social consultar 1 678 11 7','avanzar 690']
 path=folder/('vida_'+mode+'.json')
 if path.exists():raise FileExistsError(path)
 path.write_text(json.dumps({'schema':'CPC8.console.events.v1','source_contract':'SOCIAL_F3_L01_UPDATE_FROZEN/I21',
  'condition':mode,'scope':'Explicit environmental experiences and pedagogy. Participant query/response never reads this event file.',
  'commands':commands},ensure_ascii=False,indent=2),encoding='utf-8')
print('Frozen two public integrated event files before executing the interface.')
