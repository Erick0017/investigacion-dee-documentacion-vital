"""Native-resolution OpenGL scientific visualization. No DEE engine imports.

Particles, paths and highlights are supplied by the editor from recorded evidence.
The renderer never evolves the universe or invents trajectories.
"""
from pathlib import Path
import sys,math,json,time
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'python_deps'))
import moderngl

def rgb(color):
    if isinstance(color,str):
        color=color.lstrip('#');return tuple(int(color[i:i+2],16)/255 for i in (0,2,4))
    a=tuple(float(x) for x in color[:3]);return tuple(x/255 for x in a) if max(a)>1 else a

def matrices(eye,target,aspect,fov=42,near=.1,far=500):
    eye=np.asarray(eye,dtype=np.float32);target=np.asarray(target,dtype=np.float32)
    z=eye-target;z/=np.linalg.norm(z);up=np.array([0,0,1.],dtype=np.float32)
    if abs(np.dot(z,up))>.98:up=np.array([0,1.,0],dtype=np.float32)
    x=np.cross(up,z);x/=np.linalg.norm(x);y=np.cross(z,x)
    view=np.eye(4,dtype=np.float32);view[:3,:3]=np.stack([x,y,z]);view[:3,3]=-view[:3,:3]@eye
    f=1/math.tan(math.radians(fov)/2)
    p=np.zeros((4,4),dtype=np.float32);p[0,0]=f/aspect;p[1,1]=f;p[2,2]=(far+near)/(near-far);p[2,3]=2*far*near/(near-far);p[3,2]=-1
    return view,p

def sphere_mesh(u=32,v=20):
    rows=[]
    def p(i,j):
        a=math.pi*i/v;b=2*math.pi*j/u
        return [math.sin(a)*math.cos(b),math.sin(a)*math.sin(b),math.cos(a)]
    for i in range(v):
        for j in range(u):
            for ii,jj in [(i,j),(i+1,j),(i+1,j+1),(i,j),(i+1,j+1),(i,j+1)]:
                a=p(ii,jj);rows.append(a+a)
    return np.asarray(rows,dtype='f4')

class SceneRenderer:
    def __init__(self,width=1920,height=1080,samples=4):
        self.width=int(width);self.height=int(height)
        self.ctx=moderngl.create_standalone_context(require=330)
        self.samples=min(samples,self.ctx.max_samples)
        self.ms=self.ctx.framebuffer(color_attachments=[self.ctx.renderbuffer((self.width,self.height),components=4,samples=self.samples)],depth_attachment=self.ctx.depth_renderbuffer((self.width,self.height),samples=self.samples))
        self.color=self.ctx.texture((self.width,self.height),4)
        self.resolved=self.ctx.framebuffer([self.color])
        self.bg=self.ctx.program(vertex_shader='''#version 330
        in vec2 pos;out vec2 uv;void main(){uv=pos*.5+.5;gl_Position=vec4(pos,0,1);}''',fragment_shader='''#version 330
        in vec2 uv;out vec4 frag;void main(){float d=length((uv-vec2(.5,.55))*vec2(1.1,.8));vec3 a=vec3(.018,.038,.065);vec3 b=vec3(.045,.079,.116);frag=vec4(mix(b,a,smoothstep(.05,.75,d)),1);}''')
        self.bg_vbo=self.ctx.buffer(np.array([-1,-1,1,-1,-1,1,1,1],dtype='f4').tobytes())
        self.bg_vao=self.ctx.vertex_array(self.bg,[(self.bg_vbo,'2f','pos')])
        self.program=self.ctx.program(vertex_shader='''#version 330
        uniform mat4 mvp;uniform vec3 eye;
        in vec3 in_pos;in vec3 in_normal;in vec3 center;in float radius;in vec3 color;
        out vec3 normal;out vec3 world;out vec3 col;
        void main(){world=center+radius*in_pos;normal=in_normal;col=color;gl_Position=mvp*vec4(world,1);}''',fragment_shader='''#version 330
        uniform vec3 eye;in vec3 normal;in vec3 world;in vec3 col;out vec4 frag;
        void main(){vec3 n=normalize(normal);vec3 l=normalize(vec3(-.4,-.6,1.0));vec3 v=normalize(eye-world);
        float key=max(0.,dot(n,l));float fill=max(0.,dot(n,normalize(vec3(.8,.4,.25))));
        float spec=pow(max(0.,dot(n,normalize(l+v))),45.);float rim=pow(1.-max(0.,dot(n,v)),3.);
        vec3 c=col*(.30+.72*key+.22*fill)+vec3(.60,.76,.90)*spec*.36+col*rim*.16;
        c=pow(c,vec3(.82));frag=vec4(c,1.);}''')
        self.mesh=sphere_mesh();self.mesh_vbo=self.ctx.buffer(self.mesh.tobytes());self.instance=self.ctx.buffer(reserve=8192*7*4)
        self.vao=self.ctx.vertex_array(self.program,[(self.mesh_vbo,'3f 3f','in_pos','in_normal'),(self.instance,'3f 1f 3f /i','center','radius','color')])
        self.line_prog=self.ctx.program(vertex_shader='''#version 330
        uniform mat4 mvp;in vec3 pos;in vec4 color;out vec4 col;void main(){gl_Position=mvp*vec4(pos,1);col=color;}''',fragment_shader='''#version 330
        in vec4 col;out vec4 frag;void main(){frag=col;}''')
        self.line_buffer=self.ctx.buffer(reserve=2*1024*1024)
        self.line_vao=self.ctx.vertex_array(self.line_prog,[(self.line_buffer,'3f 4f','pos','color')])
        self.last_eye=None;self.last_target=None;self.last_fov=42
        self.info={'renderer':self.ctx.info.get('GL_RENDERER'),'vendor':self.ctx.info.get('GL_VENDOR'),'version':self.ctx.version_code,'samples':self.samples,'width':self.width,'height':self.height,'implementation':'ModernGL standalone WGL; GPU depth-tested shaded meshes, perspective projection, MSAA'}

    def project(self,position,eye=None,target=None,fov=None):
        eye=self.last_eye if eye is None else eye;target=self.last_target if target is None else target
        if eye is None or target is None:raise ValueError('Supply eye and target before first render.')
        view,p=matrices(eye,target,self.width/self.height,self.last_fov if fov is None else fov)
        q=p@view@np.array([*position,1.],dtype=np.float32)
        if q[3]<=0:return None
        a=q[:3]/q[3]
        return (float((a[0]+1)*self.width/2),float((1-a[1])*self.height/2),float(a[2]))

    def _lines(self,segments,mvp,width=1):
        if not segments:return
        data=np.asarray(segments,dtype='f4')
        if data.nbytes>self.line_buffer.size:self.line_buffer.orphan(data.nbytes)
        self.line_buffer.write(data.tobytes());self.line_prog['mvp'].write(mvp.T.astype('f4').tobytes())
        self.ctx.line_width=width;self.line_vao.render(moderngl.LINES,vertices=len(data))

    def render(self,particles,*,eye=(62,-45,67),target=(23,23,25),bounds=(0,66),paths=None,highlights=None,fov=42,grid=True,**kwargs):
        self.last_eye=eye;self.last_target=target;self.last_fov=fov
        view,p=matrices(eye,target,self.width/self.height,fov);mvp=p@view
        self.ms.use();self.ctx.viewport=(0,0,self.width,self.height);self.ms.clear(0,0,0,1,depth=1)
        self.ctx.disable(moderngl.DEPTH_TEST);self.ctx.disable(moderngl.BLEND);self.bg_vao.render(moderngl.TRIANGLE_STRIP)
        self.ctx.enable(moderngl.DEPTH_TEST);self.ctx.enable(moderngl.BLEND);self.ctx.blend_func=(moderngl.SRC_ALPHA,moderngl.ONE_MINUS_SRC_ALPHA)
        seg=[]
        def edge(a,b,c):seg.extend([list(a)+list(c),list(b)+list(c)])
        if isinstance(bounds[0],(list,tuple,np.ndarray)):lo=np.array(bounds[0],float);hi=np.array(bounds[1],float)
        else:lo=np.repeat(float(bounds[0]),3);hi=np.repeat(float(bounds[1]),3)
        if grid:
            corners=[(x,y,z) for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]
            for i,a in enumerate(corners):
                for b in corners[i+1:]:
                    if sum(x!=y for x,y in zip(a,b))==1:edge(a,b,(.38,.49,.59,.56))
            step=max(2,(hi[0]-lo[0])/8)
            for x in np.arange(lo[0],hi[0]+.001,step):
                edge((x,lo[1],lo[2]),(x,hi[1],lo[2]),(.27,.37,.47,.48))
                edge((x,hi[1],lo[2]),(x,hi[1],hi[2]),(.27,.37,.47,.32))
            for y in np.arange(lo[1],hi[1]+.001,step):
                edge((lo[0],y,lo[2]),(hi[0],y,lo[2]),(.27,.37,.47,.48))
            for z in np.arange(lo[2],hi[2]+.001,step):
                edge((lo[0],hi[1],z),(hi[0],hi[1],z),(.27,.37,.47,.32))
        self._lines(seg,mvp,1)
        for path in paths or []:
            pts=path.get('points',[]);color=rgb(path.get('color','#3B6678'));a=float(path.get('alpha',.5));line=[]
            for x,y in zip(pts,pts[1:]):line.extend([list(x)+[*color,a],list(y)+[*color,a]])
            self._lines(line,mvp,float(path.get('width',1.5)))
        self.ctx.disable(moderngl.BLEND)
        items=[]
        for d in particles:
            pos=d.get('position',d.get('xyz'));color=rgb(d.get('color','#44D8C1'));radius=float(d.get('radius',.65))
            if radius>0:items.append([*pos,radius,*color])
        if items:
            data=np.asarray(items,dtype='f4');self.instance.write(data.tobytes());self.program['mvp'].write(mvp.T.astype('f4').tobytes());self.program['eye'].value=tuple(float(x) for x in eye)
            self.vao.render(instances=len(items))
        self.ctx.enable(moderngl.BLEND)
        for h in highlights or []:
            pos=np.asarray(h['position'],float);radius=h.get('radius',1.2);color=rgb(h.get('color','#FFFFFF'));line=[]
            for plane in [(0,1),(0,2),(1,2)]:
                pts=[]
                for a in np.linspace(0,2*math.pi,65):
                    v=pos.copy();v[plane[0]]+=radius*math.cos(a);v[plane[1]]+=radius*math.sin(a);pts.append(v)
                for x,y in zip(pts,pts[1:]):line.extend([list(x)+[*color,.52],list(y)+[*color,.52]])
            self._lines(line,mvp,1.5)
        self.ctx.copy_framebuffer(self.resolved,self.ms)
        data=self.resolved.read(components=3,alignment=1)
        return Image.frombytes('RGB',(self.width,self.height),data).transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    def close(self):self.ctx.release()

if __name__=='__main__':
    r=SceneRenderer();particles=[{'position':(20,23,30),'radius':.8,'color':'#FFBE66'},{'position':(27,30,30),'radius':.8,'color':'#B99CFF'},{'position':(18,23,30),'radius':.55,'color':'#44D8C1'},{'position':(27,30,24),'radius':.7,'color':'#B99CFF'}]
    paths=[{'points':[(20,15,30),(20,23,30)],'color':'#FFBE66'},{'points':[(27,30,15),(27,30,30)],'color':'#B99CFF'},{'points':[(17,23,30),(20,23,30),(27,30,30)],'color':'#44D8C1'}]
    im=r.render(particles,eye=(46,-12,52),target=(23,23,26),bounds=((12,10,10),(36,38,38)),paths=paths,highlights=[{'position':(20,23,30),'radius':1.2}]);im.save(HERE/'piloto_1080.png')
    start=time.monotonic()
    for i in range(30):r.render(particles,eye=(46-i*.05,-12,52),target=(23,23,26),bounds=((12,10,10),(36,38,38)),paths=paths)
    report={**r.info,'benchmark_frames':30,'benchmark_host_seconds':time.monotonic()-start,'fps':30/(time.monotonic()-start),'scope':'Editorial visualization of supplied coordinates, not a DEE simulation. All role colors assigned by visualizer.'}
    (HERE/'renderer_report.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report));r.close()
