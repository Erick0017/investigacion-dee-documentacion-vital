"""Estilo audiovisual R03. Sólo dibujo editorial, sin importar DEE."""
from functools import lru_cache
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math
BG='#09131F'; DARK='#050D17'; WHITE='#F5F7FA'; GRAY='#B9C4D0'; CYAN='#44D8E8'; AMBER='#FFBE66'; VIOLET='#AC8BFA'; MUTED='#456174'
SIZE=(1920,1080)
@lru_cache(None)
def font(size,bold=False):
 return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf'if bold else'C:/Windows/Fonts/segoeui.ttf',round(size))
def text(im,xy,value,size=44,color=WHITE,bold=False,anchor=None,width=None):
 value=str(value);d=ImageDraw.Draw(im)
 if width:
  while size>24 and d.textlength(value,font=font(size,bold))>width:size-=1
 box=d.textbbox(xy,value,font=font(size,bold),anchor=anchor)
 if not(box[0]>=70 and box[2]<=1850 and box[1]>=0 and box[3]<=1020):raise ValueError((value,box))
 d.text(xy,value,font=font(size,bold),fill=color,anchor=anchor,stroke_width=0)
 return box
def center(im,y,value,size=48,color=WHITE,bold=False,width=1710):
 return text(im,(960,y),value,size,color,bold,'mm',width)
def lines(value,size=44,width=1710):
 d=ImageDraw.Draw(Image.new('RGB',(1,1)));rows=[];row=[]
 for word in str(value).split():
  if row and d.textlength(' '.join(row+[word]),font=font(size))>width:rows.append(' '.join(row));row=[]
  row.append(word)
 if row:rows.append(' '.join(row))
 return rows
def bi(im,xy,es,en,size=44,color=WHITE,anchor=None,width=800):
 text(im,xy,es,size,color,True,anchor,width)
 x,y=xy;text(im,(x,y+size*1.08),en,max(26,round(size*.60)),GRAY,False,anchor,width)
def panel(im,box,color=MUTED,fill=BG,radius=18):
 ImageDraw.Draw(im).rounded_rectangle(box,radius=radius,outline=color,width=2,fill=fill)
def finish(im,es,en,category,source,detail=None):
 im=im.convert('RGB');d=ImageDraw.Draw(im)
 d.rectangle((0,0,1920,194),fill=DARK);d.rectangle((0,798,1920,1080),fill=DARK)
 text(im,(90,32),es,56,WHITE,True,width=1740)
 text(im,(90,107),en,31,GRAY,width=1740)
 if detail:text(im,(90,151),detail,25,CYAN,width=1740)
 text(im,(90,808),category,25,GRAY,width=1740)
 text(im,(90,846),source,24,GRAY,width=1740)
 return im
def plain():
 return Image.new('RGB',SIZE,BG)
def caption(im,rows):
 ys=[963]if len(rows)==1 else[908,963]
 for y,row in zip(ys,rows):center(im,y,row,46,WHITE)
def phase_between(t,a,b):return max(0,min(1,(t-a)/max(.001,b-a)))
def lerp(a,b,p):
 p=max(0,min(1,p));p=p*p*(3-2*p)
 return [x*(1-p)+y*p for x,y in zip(a,b)]
