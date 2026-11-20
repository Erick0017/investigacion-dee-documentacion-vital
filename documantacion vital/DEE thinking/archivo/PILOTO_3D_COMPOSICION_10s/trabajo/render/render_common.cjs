/* Deterministic local WebGL2 image exporter. No DEE imports, physics or network.
 * Stdin: one {op:'render',model:{...}} JSON line per image; stdout: PNG <bytes>\n + bytes.
 * Geometry is supplied by evidence adapters. Only editorial camera/labels are projected.
 */
'use strict';
const {chromium}=require('C:/Users/Erik/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const readline=require('readline');

function installRenderer(){
 const W=1920,H=1080,c=document.getElementById('world'),o=document.getElementById('editorial'),g=c.getContext('webgl2',{alpha:false,antialias:true,preserveDrawingBuffer:true,depth:true});
 if(!g)throw Error('WebGL2 unavailable');
 const ctx=o.getContext('2d'),out=document.createElement('canvas');out.width=W;out.height=H;const ox=out.getContext('2d');
 const V=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],norm=a=>{let n=Math.hypot(...a);if(!n)throw Error('Zero vector');return a.map(v=>v/n);};
 function rgb(s){if(Array.isArray(s))return s.slice(0,3).map(v=>v>1?v/255:v);s=(s||'#46C7EB').replace('#','');return [0,2,4].map(i=>parseInt(s.slice(i,i+2),16)/255);}
 function shader(type,source){const s=g.createShader(type);g.shaderSource(s,source);g.compileShader(s);if(!g.getShaderParameter(s,g.COMPILE_STATUS))throw Error(g.getShaderInfoLog(s));return s;}
 function program(vs,fs){const p=g.createProgram();g.attachShader(p,shader(g.VERTEX_SHADER,vs));g.attachShader(p,shader(g.FRAGMENT_SHADER,fs));g.linkProgram(p);if(!g.getProgramParameter(p,g.LINK_STATUS))throw Error(g.getProgramInfoLog(p));return p;}
 const pr=program(`#version 300 es
 precision highp float;
 layout(location=0)in vec3 a_pos;layout(location=1)in vec3 a_norm;
 layout(location=2)in mat4 i_matrix;layout(location=6)in vec4 i_color;
 uniform mat4 vp;uniform vec2 lens_shift;out vec3 wn;out vec3 wp;out vec4 col;
 void main(){vec4 w=i_matrix*vec4(a_pos,1.);wp=w.xyz;wn=mat3(i_matrix)*a_norm;col=i_color;gl_Position=vp*w;gl_Position.xy+=lens_shift*gl_Position.w;}`,`#version 300 es
 precision highp float;in vec3 wn;in vec3 wp;in vec4 col;uniform vec3 eye;out vec4 color;
 void main(){vec3 n=normalize(wn),l=normalize(vec3(-.5,-.65,1.)),v=normalize(eye-wp);float key=max(dot(n,l),0.);float fill=max(dot(n,normalize(vec3(.8,.3,.4))),0.);float spec=pow(max(dot(n,normalize(l+v)),0.),42.);float rim=pow(1.-max(dot(n,v),0.),3.);vec3 lit=col.rgb*(.31+.68*key+.19*fill)+vec3(.65,.80,.91)*spec*.22+col.rgb*rim*.10;color=vec4(pow(max(lit,vec3(0.)),vec3(.90)),col.a);}`);
 const linePr=program(`#version 300 es
 precision highp float;layout(location=0)in vec3 p;layout(location=1)in vec4 c;uniform mat4 vp;uniform vec2 lens_shift;out vec4 col;void main(){gl_Position=vp*vec4(p,1.);gl_Position.xy+=lens_shift*gl_Position.w;col=c;}`,`#version 300 es
 precision highp float;in vec4 col;out vec4 color;void main(){color=col;}`);
 function tri(out,a,b,c,na,nb,nc){out.push(...a,...na,...b,...nb,...c,...nc);}
 function sphere(){const a=[],U=48,VV=32,p=(i,j)=>{let t=i*Math.PI/VV,f=j*2*Math.PI/U;return [Math.sin(t)*Math.cos(f),Math.sin(t)*Math.sin(f),Math.cos(t)];};for(let i=0;i<VV;i++)for(let j=0;j<U;j++){let x=p(i,j),y=p(i+1,j),z=p(i+1,j+1),w=p(i,j+1);tri(a,x,y,z,x,y,z);tri(a,x,z,w,x,z,w);}return a;}
 function cube(){const a=[];for(const [n,u,v] of [[[1,0,0],[0,1,0],[0,0,1]],[[-1,0,0],[0,-1,0],[0,0,1]],[[0,1,0],[-1,0,0],[0,0,1]],[[0,-1,0],[1,0,0],[0,0,1]],[[0,0,1],[1,0,0],[0,1,0]],[[0,0,-1],[1,0,0],[0,-1,0]]]){let pp=[[-1,-1],[1,-1],[1,1],[-1,1]].map(([x,y])=>n.map((q,k)=>q+u[k]*x+v[k]*y));tri(a,pp[0],pp[1],pp[2],n,n,n);tri(a,pp[0],pp[2],pp[3],n,n,n);}return a;}
 function cylinder(cone=false){const a=[],U=16;for(let i=0;i<U;i++){let t=i*2*Math.PI/U,s=(i+1)*2*Math.PI/U,x=[Math.cos(t),Math.sin(t)],y=[Math.cos(s),Math.sin(s)],n1=[x[0],x[1],cone?1:0],n2=[y[0],y[1],cone?1:0],p=[...x,-.5],q=[...y,-.5],r=cone?[0,0,.5]:[...y,.5],w=cone?[0,0,.5]:[...x,.5];tri(a,p,q,r,n1,n2,n2);if(!cone)tri(a,p,r,w,n1,n2,n1);tri(a,[0,0,-.5],q,p,[0,0,-1],[0,0,-1],[0,0,-1]);if(!cone)tri(a,[0,0,.5],w,r,[0,0,1],[0,0,1],[0,0,1]);}return a;}
 function mesh(vertices){const vao=g.createVertexArray();g.bindVertexArray(vao);const vb=g.createBuffer();g.bindBuffer(g.ARRAY_BUFFER,vb);g.bufferData(g.ARRAY_BUFFER,new Float32Array(vertices),g.STATIC_DRAW);for(let i=0;i<2;i++){g.enableVertexAttribArray(i);g.vertexAttribPointer(i,3,g.FLOAT,false,24,i*12);}const ib=g.createBuffer();g.bindBuffer(g.ARRAY_BUFFER,ib);for(let i=0;i<4;i++){g.enableVertexAttribArray(2+i);g.vertexAttribPointer(2+i,4,g.FLOAT,false,80,i*16);g.vertexAttribDivisor(2+i,1);}g.enableVertexAttribArray(6);g.vertexAttribPointer(6,4,g.FLOAT,false,80,64);g.vertexAttribDivisor(6,1);return {vao,ib,count:vertices.length/6};}
 const meshes={sphere:mesh(sphere()),cube:mesh(cube()),cylinder:mesh(cylinder()),cone:mesh(cylinder(true))};
 const lineVao=g.createVertexArray(),lineBuf=g.createBuffer();g.bindVertexArray(lineVao);g.bindBuffer(g.ARRAY_BUFFER,lineBuf);g.enableVertexAttribArray(0);g.vertexAttribPointer(0,3,g.FLOAT,false,28,0);g.enableVertexAttribArray(1);g.vertexAttribPointer(1,4,g.FLOAT,false,28,12);
 function mul(a,b){const o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)o[c*4+r]+=a[k*4+r]*b[c*4+k];return o;}
 function cam(m){const eye=m.eye,target=m.target,z=norm(V(eye,target));let up=[0,0,1];if(Math.abs(dot(z,up))>.98)up=[0,1,0];let x=norm(cross(up,z)),y=cross(z,x),v=new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,eye),-dot(y,eye),-dot(z,eye),1]);let f=1/Math.tan((m.fov||42)*Math.PI/360),near=.05,far=2000,p=new Float32Array([f/(W/H),0,0,0,0,f,0,0,0,0,(far+near)/(near-far),-1,0,0,2*far*near/(near-far),0]);return mul(p,v);}
 function matrix(pos,scale,rotation=0){let c=Math.cos(rotation),s=Math.sin(rotation);return [scale[0]*c,scale[0]*s,0,0,-scale[1]*s,scale[1]*c,0,0,0,0,scale[2],0,...pos,1];}
 function between(a,b,r){let z=norm(V(b,a)),u=Math.abs(z[2])>.98?[0,1,0]:[0,0,1],x=norm(cross(u,z)),y=cross(z,x),L=Math.hypot(...V(b,a)),mid=a.map((v,i)=>(v+b[i])/2);return [...x.map(v=>v*r),0,...y.map(v=>v*r),0,...z.map(v=>v*L),0,...mid,1];}
 function project(pos,vp,shift){let v=[...pos,1],q=[0,0,0,0];for(let r=0;r<4;r++)for(let k=0;k<4;k++)q[r]+=vp[k*4+r]*v[k];if(q[3]<=0)return null;return [(q[0]/q[3]+shift[0]+1)*W/2,(1-q[1]/q[3]-shift[1])*H/2,q[2]/q[3]];}
 function label(text,x,y,size,color,align='center',bold=true){if(/^[\d\s+\-−=→/.,]+$/.test(String(text)))size=Math.max(64,size);ctx.font=`${bold?600:400} ${size}px "Segoe UI",Arial,sans-serif`;ctx.textAlign=align;ctx.textBaseline='middle';ctx.lineJoin='round';ctx.lineWidth=Math.max(2,size*.06);ctx.strokeStyle='rgba(4,12,18,.92)';ctx.strokeText(String(text),x,y);ctx.fillStyle=color||'#E8F4F3';ctx.fillText(String(text),x,y);}
 function draw(m){
  if(!m.camera||!Array.isArray(m.camera.eye)||!Array.isArray(m.camera.target))throw Error('Explicit camera eye/target required');
  const vp=cam(m.camera),shift=m.camera.lens_shift||[.04,.14],eye=m.camera.eye,lo=m.bounds?.[0]||[-10,-10,-5],hi=m.bounds?.[1]||[10,10,10],batches={sphere:[],cube:[],cylinder:[],cone:[]},transparent=[];
  function add(shape,mat,color,alpha=1){let item=[...mat,...rgb(color),alpha];if(alpha<.999)transparent.push({shape,item,distance:Math.hypot(mat[12]-eye[0],mat[13]-eye[1],mat[14]-eye[2])});else(batches[shape]||batches.sphere).push(item);}
  const lines=[],line=(a,b,color,alpha=.5)=>{let c=[...rgb(color),alpha];lines.push(...a,...c,...b,...c);};
  if(m.grid){for(let x of [lo[0],hi[0]])for(let y of [lo[1],hi[1]])line([x,y,lo[2]],[x,y,hi[2]],'#345061',.45);for(let z of [lo[2],hi[2]]){line([lo[0],lo[1],z],[hi[0],lo[1],z],'#345061',.45);line([lo[0],hi[1],z],[hi[0],hi[1],z],'#345061',.45);line([lo[0],lo[1],z],[lo[0],hi[1],z],'#345061',.45);line([hi[0],lo[1],z],[hi[0],hi[1],z],'#345061',.45);}}
  // A declared editorial coordinate reference, never particles, links or paths.
  if(m.spatial_grid){const sg=m.spatial_grid,baseStep=Math.max(.25,Number(sg.step||1)),span=Math.max(hi[0]-lo[0],hi[1]-lo[1]),step=Math.max(baseStep,span/24),z=Number.isFinite(sg.plane_z)?sg.plane_z:lo[2],alpha=sg.opacity===undefined?.12:sg.opacity,color=sg.color||'#567080';for(let x=Math.ceil(lo[0]/step)*step;x<=hi[0]+1e-6;x+=step)line([x,lo[1],z],[x,hi[1],z],color,alpha);for(let y=Math.ceil(lo[1]/step)*step;y<=hi[1]+1e-6;y+=step)line([lo[0],y,z],[hi[0],y,z],color,alpha);if(sg.verticals){for(const x of [lo[0],hi[0]])for(const y of [lo[1],hi[1]])line([x,y,z],[x,y,hi[2]],color,alpha*.8);}}
  if(m.ground){const z=typeof m.ground.z==='number'?m.ground.z:lo[2]-.4;add('cube',matrix([(lo[0]+hi[0])/2,(lo[1]+hi[1])/2,z],[(hi[0]-lo[0])*.62,(hi[1]-lo[1])*.62,.025]),m.ground.color||'#102531',m.ground.opacity||.60);for(const p of m.particles||[]){const r=p.radius||.6;for(let s of [1,1.5,2])add('sphere',matrix([p.position[0]+.12*(p.position[2]-z),p.position[1]+.16*(p.position[2]-z),z+.04],[(r*1.35)*s,(r*.7)*s,.007]),'#000000',(.11/s)*(p.opacity===undefined?1:p.opacity));}}
  for(const p of m.particles||[]){let r=p.radius===undefined?.6:p.radius;if(r<=0)continue;add(p.shape==='cube'?'cube':'sphere',matrix(p.position,p.scale||[r,r,r],p.rotation_z||0),p.color||'#46C7EB',p.opacity===undefined?1:p.opacity);}
  for(const b of m.boxes||[])add('cube',matrix(b.position,b.scale,b.rotation_z||0),b.color||'#B89BE8',b.opacity===undefined?1:b.opacity);
  for(const b of m.planes||[])add('cube',matrix(b.position||b.center,b.scale,b.rotation_z||0),b.color||'#46C7EB',b.opacity===undefined?.18:b.opacity);
  for(const path of m.paths||[]){let pts=path.points||[];for(let j=1;j<pts.length;j++)if(Math.hypot(...V(pts[j],pts[j-1]))>1e-7)add('cylinder',between(pts[j-1],pts[j],path.radius||.035),path.color||'#46C7EB',path.opacity===undefined?.62:path.opacity);}
  for(const a of m.arrows||[]){let z=norm(a.direction),L=a.length||2,p=a.origin,q=p.map((v,i)=>v+z[i]*L),neck=p.map((v,i)=>v+z[i]*L*.77);add('cylinder',between(p,neck,a.radius||.065),a.color||'#E8F4F3');add('cone',between(neck,q,(a.radius||.065)*2.7),a.color||'#E8F4F3');}
  for(const h of m.highlights||[]){let p=h.position,r=h.radius||1.2;for(const plane of [[0,1],[0,2],[1,2]]){let old;for(let j=0;j<=48;j++){let a=j*Math.PI/24,q=p.slice();q[plane[0]]+=r*Math.cos(a);q[plane[1]]+=r*Math.sin(a);if(old)line(old,q,h.color||'#E8F4F3',h.opacity===undefined?.54:h.opacity);old=q;}}}
  g.viewport(0,0,W,H);g.clearColor(7/255,19/255,29/255,1);g.clear(g.COLOR_BUFFER_BIT|g.DEPTH_BUFFER_BIT);g.enable(g.DEPTH_TEST);g.depthFunc(g.LEQUAL);g.disable(g.BLEND);g.depthMask(true);g.useProgram(pr);g.uniformMatrix4fv(g.getUniformLocation(pr,'vp'),false,vp);g.uniform2fv(g.getUniformLocation(pr,'lens_shift'),shift);g.uniform3fv(g.getUniformLocation(pr,'eye'),eye);
  function batch(shape,items){if(!items.length)return;let mesh=meshes[shape];g.bindVertexArray(mesh.vao);g.bindBuffer(g.ARRAY_BUFFER,mesh.ib);g.bufferData(g.ARRAY_BUFFER,new Float32Array(items.flat()),g.DYNAMIC_DRAW);g.drawArraysInstanced(g.TRIANGLES,0,mesh.count,items.length);}
  for(const shape of Object.keys(batches))batch(shape,batches[shape]);
  g.enable(g.BLEND);g.blendFunc(g.SRC_ALPHA,g.ONE_MINUS_SRC_ALPHA);g.depthMask(false);transparent.sort((a,b)=>b.distance-a.distance);for(const x of transparent)batch(x.shape,[x.item]);
  if(lines.length){g.useProgram(linePr);g.uniformMatrix4fv(g.getUniformLocation(linePr,'vp'),false,vp);g.uniform2fv(g.getUniformLocation(linePr,'lens_shift'),shift);g.bindVertexArray(lineVao);g.bindBuffer(g.ARRAY_BUFFER,lineBuf);g.bufferData(g.ARRAY_BUFFER,new Float32Array(lines),g.DYNAMIC_DRAW);g.drawArrays(g.LINES,0,lines.length/7);}g.depthMask(true);g.finish();
  ctx.clearRect(0,0,W,H);
  for(const l of m.labels||[]){const q=project(l.position,vp,shift);if(!q)continue;let off=l.offset||[0,-55],x=q[0]+off[0],y=q[1]+off[1],size=l.size||54;ctx.font=`600 ${size}px "Segoe UI",Arial,sans-serif`;let half=ctx.measureText(String(l.text)).width/2;x=Math.max(96+half,Math.min(W-96-half,x));y=Math.max(90+size/2,Math.min(820-size/2,y));if(l.leader!==false&&(Math.abs(off[0])+Math.abs(off[1])>20)){ctx.beginPath();ctx.moveTo(q[0],q[1]);ctx.lineTo(x,y+size*.35);ctx.strokeStyle=l.color||'#B4D2DE';ctx.lineWidth=2;ctx.stroke();}label(l.text,x,y,size,l.color);}
  for(const l of m.screen_labels||[])label(l.text,l.xy[0],l.xy[1],l.size||60,l.color,l.align||'center',l.bold!==false);
  if(m.provenance){label('Etapas',76,62,30,'#B7CBD5','left',false);}
  ox.drawImage(c,0,0);ox.drawImage(o,0,0);return out.toDataURL('image/png').split(',')[1];
 }
 const d=g.getExtension('WEBGL_debug_renderer_info');
 window.PILOTO={draw,info:{implementation:'WebGL2 deterministic explicit-frame rendering; direct canvas export; no captured application UI',width:W,height:H,renderer:d?g.getParameter(d.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER),vendor:d?g.getParameter(d.UNMASKED_VENDOR_WEBGL):g.getParameter(g.VENDOR),antialias:g.getContextAttributes().antialias,version:g.getParameter(g.VERSION),physical_interpolation:'none; caller supplies every recorded or declared illustrative state'}};
 return window.PILOTO.info;
}

(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--no-first-run','--disable-background-networking','--disable-component-update','--disable-sync']});
 try{
  const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
  await page.route('**/*',r=>r.abort());
  await page.setContent('<html><style>html,body{margin:0;overflow:hidden;background:#07131D}canvas{position:absolute;inset:0;width:1920px;height:1080px}</style><canvas id="world" width="1920" height="1080"></canvas><canvas id="editorial" width="1920" height="1080"></canvas></html>');
  const info=await page.evaluate(installRenderer);info.browser=await browser.version();process.stdout.write('INFO '+JSON.stringify(info)+'\n');
  const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});
  for await(const line of rl){if(!line.trim())continue;const req=JSON.parse(line);if(req.op==='close')break;if(req.op!=='render')throw Error('Only render/close are admitted');try{const data=await page.evaluate(m=>window.PILOTO.draw(m),req.model);const png=Buffer.from(data,'base64');process.stdout.write('PNG '+png.length+'\n');if(!process.stdout.write(png))await new Promise(resolve=>process.stdout.once('drain',resolve));}catch(e){process.stdout.write('ERROR '+JSON.stringify({message:e.message})+'\n');}}
 }finally{await browser.close();}
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1;});
