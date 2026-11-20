"""Sólo pruebas de encuadre, sin audio ni ticks del motor."""
import pelicula as p
from PIL import Image,ImageDraw
r=p.get_renderer()
out=p.W/'encuadres';out.mkdir(exist_ok=True)
scenes=[]
for source in p.G['scenes']:
    at=0;bounds=[]
    for sentence in p.sentences(source['es']):
        duration=len(sentence.split())*.45;bounds.append([at,at+duration]);at+=duration+.6
    scenes.append({'scene':source['scene'],'duration':at,'sentences':bounds})
for s in scenes:
    for j,ratio in enumerate([.15,.40,.65,.90]):
        im=p.image_at(r,s,ratio*s['duration']);im.save(out/f'{s["scene"]:02}_{j}.png')
sheet=Image.new('RGB',(1920,2304),p.BG)
for i in range(32):
    name=f'{i//4+1:02}_{i%4}.png';im=Image.open(out/name).resize((480,270));sheet.paste(im,((i%4)*480,(i//4)*288));ImageDraw.Draw(sheet).text(((i%4)*480+8,(i//4)*288+270),name,fill=p.WHITE,font=p.font(14))
sheet.save(out/'encuadres.jpg',quality=95)
print('ENCUADRES',flush=True)
