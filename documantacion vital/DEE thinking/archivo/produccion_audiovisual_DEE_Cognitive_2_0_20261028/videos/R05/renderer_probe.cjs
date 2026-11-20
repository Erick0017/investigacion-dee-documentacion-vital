// Local graphics availability/throughput probe only. No DEE, browser session or network.
const {chromium}=require('C:/Users/Erik/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{
  const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--no-first-run','--disable-background-networking','--disable-component-update','--disable-sync']});
  try{
    const p=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
    await p.setContent('<html><style>html,body{margin:0;background:#07131D}canvas{display:block}</style><canvas id="c" width="1920" height="1080"></canvas></html>');
    const info=await p.evaluate(()=>{
      const c=document.getElementById('c'),g=c.getContext('webgl2',{antialias:true,preserveDrawingBuffer:true});
      if(!g)return {available:false};
      window.g=g;const d=g.getExtension('WEBGL_debug_renderer_info');
      const vs=g.createShader(g.VERTEX_SHADER);g.shaderSource(vs,'#version 300 es\nin vec3 a;uniform float t;void main(){float s=sin(t),c=cos(t);vec3 p=vec3(c*a.x+s*a.z,a.y,-s*a.x+c*a.z);gl_Position=vec4(p.xy,p.z*.1,1.5+p.z*.2);}');g.compileShader(vs);
      const fs=g.createShader(g.FRAGMENT_SHADER);g.shaderSource(fs,'#version 300 es\nprecision highp float;out vec4 color;void main(){color=vec4(.27,.78,.92,1);}');g.compileShader(fs);
      const pr=g.createProgram();g.attachShader(pr,vs);g.attachShader(pr,fs);g.linkProgram(pr);g.useProgram(pr);
      const buf=g.createBuffer();g.bindBuffer(g.ARRAY_BUFFER,buf);g.bufferData(g.ARRAY_BUFFER,new Float32Array([-.7,-.4,.3,.7,-.4,-.3,0,.6,.2]),g.STATIC_DRAW);
      const a=g.getAttribLocation(pr,'a');g.enableVertexAttribArray(a);g.vertexAttribPointer(a,3,g.FLOAT,false,0,0);window.t=g.getUniformLocation(pr,'t');
      window.draw=i=>{g.clearColor(7/255,19/255,29/255,1);g.clear(g.COLOR_BUFFER_BIT|g.DEPTH_BUFFER_BIT);g.uniform1f(window.t,i*.02);g.drawArrays(g.TRIANGLES,0,3);g.finish();};
      return {available:true,version:g.getParameter(g.VERSION),renderer:d?g.getParameter(d.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER),vendor:d?g.getParameter(d.UNMASKED_VENDOR_WEBGL):g.getParameter(g.VENDOR),antialias:g.getContextAttributes().antialias,three_local:undefined};
    });
    if(!info.available)throw Error('WebGL2 unavailable in existing Chrome');
    const start=performance.now();let total=0;
    for(let i=0;i<30;i++){await p.evaluate(i=>window.draw(i),i);const png=await p.screenshot({type:'png'});total+=png.length;if(i===29){const out=path.join(__dirname,'previas');fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'probe_webgl.png'),png);}}
    const seconds=(performance.now()-start)/1000;
    console.log(JSON.stringify({...info,browser:await b.version(),frames:30,host_seconds:seconds,fps:30/seconds,estimated_10800_seconds:10800*seconds/30,png_bytes:total,scope:'Graphics probe, not DEE evolution. Sparse triangle is only a lower bound on final scene complexity.'}));
  }finally{await b.close();}
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1;});
