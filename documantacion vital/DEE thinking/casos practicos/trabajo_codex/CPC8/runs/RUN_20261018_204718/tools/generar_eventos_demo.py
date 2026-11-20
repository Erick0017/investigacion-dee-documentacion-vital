"""Declared environmental curriculum, not a participant memory or decoder."""
import json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'configuraciones/demo';OUT.mkdir(parents=True,exist_ok=True)
for mode in('reservada','desacoplada'):
 rng=random.Random(8675309);values=[rng.choice((-1,1)) for _ in range(65)];values[16]=1
 commands=['crear reubicada','orden BA','extra -1']
 for k in range(32):
  if k==16 and mode=='desacoplada':commands+=['acontecimiento L17 1 0','señal L17 1']
  else:commands.append(f'experiencia L{k+1:02d} {values[k]} 0')
 commands+=['consecuencia 1','oportunidades','asociar',
  'consultar '+','.join(f'L{k+1:02d}' for k in range(32) if k!=16)+' 131',
  'consultar forma 267','avanzar 260']
 commands +=[f'experiencia L{k+1:02d} {values[k]} 262' for k in range(32,65)]
 commands+=['consultar '+','.join(f'L{k+1:02d}' for k in range(65))+' 393',
  'consultar forma 398','avanzar 401',
  'consultar '+','.join(f'L{k+1:02d}' for k in range(65))+' 655',
  'consultar forma 660','avanzar 663']
 path=OUT/(mode+'.json')
 if path.exists():raise FileExistsError(path)
 path.write_text(json.dumps({'schema':'CPC8.console.events.v1','description':'Nueva realización del mismo dominio; no nueva primitivaNSM',
  'environment_seed_not_sent_to_participant':8675309,'condition':mode,'commands':commands},ensure_ascii=False,indent=2),encoding='utf-8')
print('Created two equal-dose event streams before running the visitor reserve.')
