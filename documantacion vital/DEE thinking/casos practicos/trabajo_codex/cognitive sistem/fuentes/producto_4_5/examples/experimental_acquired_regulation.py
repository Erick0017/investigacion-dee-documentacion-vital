"""Installed experimental recipe: real trajectories, no archived response table."""
import argparse,json
from dee_thinking.experimental_regulation import CPC5RegulationSession

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['paired','unpaired','opposite'],default='paired');p.add_argument('--save');a=p.parse_args()
    s=CPC5RegulationSession.create(mode=a.mode)
    s.run_until(3);print(json.dumps({'stage':'acquisition','provenance':'INSTRUMENTO','state':s.observe()},ensure_ascii=False))
    s.run_until(292);print(json.dumps({'stage':'native_contact','provenance':'INSTRUMENTO','state':s.observe()},ensure_ascii=False))
    if a.save:s.save_snapshot(a.save)
    for tick,bank,field in ((424,'N','resource'),(430,'Flat','resource'),(431,'N','function'),(437,'Flat','function')):
        s.run_until(tick);print(json.dumps({'tick':tick,'bank':bank,'field':field,'provenance':'ENTE_PHYSICAL_RECORD','observation':s.observe()['banks'][bank][field]},ensure_ascii=False))
if __name__=='__main__':main()
