"""Decode one-second inspection samples from existing encoded R05 scenes."""
from pathlib import Path
import argparse,json,subprocess,sys
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from pipeline_r05 import FF,SCENE_SECONDS,sha

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--scenes',required=True)
    parser.add_argument('--group',default='actuales')
    args=parser.parse_args()
    rows=[]
    for scene in args.scenes.split(','):
        scene=scene.strip().upper()
        assert scene in {f'S{x:02d}' for x in range(1,16)}
        source=HERE/'escenas'/f'{scene}.mp4'
        assert source.is_file(),source
        n=SCENE_SECONDS[int(scene[1:])-1]*30
        folder=HERE/'previas/QA_CODIFICADO'/args.group/scene
        folder.mkdir(parents=True,exist_ok=False)
        subprocess.run([str(FF),'-hide_banner','-v','error','-xerror','-i',str(source),
                        '-vf',f'select=not(mod(n\\,30))+eq(n\\,{n-1})','-fps_mode','vfr',
                        '-threads','2',str(folder/'%03d.png')],check=True,timeout=180)
        frames=list(range(0,n,30))+[n-1]
        images=sorted(folder.glob('*.png'))
        assert len(images)==len(frames),(scene,len(images),len(frames))
        rows.append({'scene':scene,'source_sha256':sha(source),'samples':[
            {'local_frame':f,'local_seconds':round(f/30,3),'path':str(p.relative_to(HERE)),'sha256':sha(p)}
            for f,p in zip(frames,images)]})
    print(json.dumps({'scope':'Encoded frame inspection samples, not a claim of continuous human playback.','rows':rows},ensure_ascii=False))

if __name__=='__main__':main()
