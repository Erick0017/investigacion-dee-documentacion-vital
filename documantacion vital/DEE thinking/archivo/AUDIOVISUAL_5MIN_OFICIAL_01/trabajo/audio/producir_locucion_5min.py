"""Literal14-block local narration; frozen natural speed, no time stretch/cuts."""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import importlib.abc
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/"trabajo"
AUDIO=WORK/"audio"
DOC=Path("C:/Users/Erik/.codex/codex-remote-attachments/01a0921e-4727-7f93-8ad0-0b605c9afe96/9165C4B3-2EC7-4437-A31F-F66A3B9B5FA4/3-DEE_Cognitive_Narrativa_5_Minutos_ES.docx")
DOC_SHA="d7dc3b8a861b3da96d547e7bada1eb4220c9b504d75b2005b69dec7b65a3299a"
BOUNDARIES=[0,24,48,67,90,110,130,150,170,191,211,230,251,271,300]
INDEX=AUDIO/"PROVENIENCIA_TOMAS_14.json"
GUION=AUDIO/"guion.json"
sys.path.insert(0,str(ROOT.parent/"AUDIOVISUAL_R12/codigo"))
import audio_r12 as reuse


class NoNative(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split(".")[0] in {"dee_thinking","sqlite3","_sqlite3"}:raise RuntimeError("No Native/SQLite in audiovisual voice production")
        return None


def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def save_new(p,x):
    with p.open("x",encoding="utf-8",newline="\n") as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write("\n")
def atomic(p,x):
    t=p.with_name(p.name+".pending");assert not t.exists()
    save_new(t,x);t.replace(p)


def extract():
    assert sha(DOC)==DOC_SHA
    ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(DOC) as z:tree=ET.fromstring(z.read("word/document.xml"))
    paragraphs=["".join(t.text or "" for t in p.findall(".//w:t",ns)) for p in tree.findall(".//w:body/w:p",ns)]
    blocks=[]
    for i,text in enumerate(paragraphs):
        m=re.match(r"^(\d{2})\s{2,}(.+?)\s{2,}(\d\d:\d\d).(\d\d:\d\d)$",text)
        if not m:continue
        idx=int(m[1]);assert idx==len(blocks)+1
        def seconds(v):a,b=map(int,v.split(":"));return a*60+b
        a,b=seconds(m[3]),seconds(m[4]);assert (a,b)==(BOUNDARIES[idx-1],BOUNDARIES[idx])
        voice=paragraphs[i+1];assert voice and not re.match(r"^\d{2}\s{2,}",voice)
        assert voice==" ".join(voice.split()),"Do not normalize the literal silently"
        blocks.append({"id":f"B{idx:02}","block":idx,"title_documentary_not_spoken":m[2],"start_s":a,"end_s":b,"duration_s":b-a,
            "literal_ES":voice,"literal_UTF8_sha256":hashlib.sha256(voice.encode("utf-8")).hexdigest(),"Word_paragraph_1based":i+2,
            "word_count_split":len(voice.split())})
    assert len(blocks)==14 and sum(b["word_count_split"] for b in blocks)==616
    body="\n\n".join(b["literal_ES"] for b in blocks)
    return {"schema":"DEE.5MIN.official_literal_voice_script.R01","source":{"path":str(DOC),"sha256":DOC_SHA,"body_paragraphs_read":len(paragraphs),"tables_read":1,
        "table_documentary_values":["05:00 duración objetivo","14 BLOQUES secuencia original R12","616 PALABRAS locución sin títulos"]},
        "duration_s":300,"boundaries_s":BOUNDARIES,"blocks":blocks,"block_count":14,"word_count_split":616,
        "literal_voice_only_UTF8_sha256":hashlib.sha256(body.encode("utf-8")).hexdigest(),"titles_spoken":False,
        "extraction_scope":"Exactly the14voice paragraphs following numbered headings; banners, headings and table are documentary only.","new_Native_ticks":0}


def boundary():
    def guard(event,args):
        if event=="socket.connect":raise PermissionError("Offline voice production")
        if event=="open":
            p,mode,flags=args
            if not isinstance(p,(str,bytes,os.PathLike)):return
            if os.fsdecode(p) in {os.devnull,"NUL","nul"}:return
            write=isinstance(mode,str) and any(c in mode for c in "wax+")
            write=write or bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if write and not Path(os.fsdecode(p)).resolve().is_relative_to(ROOT):raise PermissionError("Write outside5MINproduction scope")
    sys.addaudithook(guard)


def align_sentences(module,synth,row):
    phonemes=row["phoneme_timings"];all_ph="";indices=[]
    for i,p in enumerate(phonemes):
        txt=reuse.norm_phonemes(p["phoneme"]);all_ph+=txt;indices.extend([i]*len(txt))
    words=list(re.finditer(r"\S+",row["es"]))
    def align(fragments,kind):
        result=[];cursor=0;text_cursor=0
        for number,fragment in enumerate(fragments,1):
            char_start=row["es"].find(fragment,text_cursor);assert char_start>=0
            char_end=char_start+len(fragment);text_cursor=char_end
            item={"fragment_id":row["id"]+f"_{kind}{number:02}","literal_ES":fragment,"character_range_0based_exclusive":[char_start,char_end],
                "word_range_0based_exclusive":[next(i for i,w in enumerate(words) if w.end()>char_start),sum(w.start()<char_end for w in words)]}
            expected=reuse.norm_phonemes(synth.tokenizer.known(synth.tokenizer.phonemize(module.synthesis_text(fragment),lang=module.PARAMS["language"])))
            at=all_ph.find(expected,cursor)
            if at<0 or not expected:
                item.update(start_s_in_take=None,end_s_in_take=None,alignment="UNRESOLVED; no invented word-count timing")
            else:
                first,last=indices[at],indices[at+len(expected)-1]
                item.update(start_s_in_take=phonemes[first]["start"],end_s_in_take=phonemes[last]["end"],
                    phoneme_first_index=first,phoneme_last_index=last,alignment="exact_full_fragment_canonical_model_phonemes")
                cursor=at+len(expected)
            result.append(item)
        return result
    sentences=module.split_sentences(row["es"])
    result=align(sentences,"S")
    clauses=[x.strip() for sentence in sentences for x in re.findall(r"[^,;:]+(?:[,;:]|$)",sentence) if x.strip()]
    row["clauses_exact_model"]=align(clauses,"C")
    return result


def synthesize():
    script=load(GUION);assert canonical(script)==canonical(extract()),"Guion differs from complete original extraction"
    reuse.ROOT=WORK
    module,np,sf,synth,assets,runner=reuse.setup();module.PARAMS.update(speed=1.0)
    existing=load(INDEX) if INDEX.exists() else {"schema":"DEE.5MIN.local_voice_takes.R01","guion_sha256":sha(GUION),"takes":[],"new_Native_ticks":0,
        "voice":"em_alex","language":"es-419","speed":1.0,"source_runner":{"path":str(reuse.TTS),"sha256":sha(reuse.TTS)},"assets":assets,"runner_files":runner}
    assert existing["guion_sha256"]==sha(GUION)
    cache={t["id"]:t for t in existing["takes"]}
    for block in script["blocks"]:
        rid=block["id"]+"_R01"
        row=module.synthesize({"id":rid,"es":block["literal_ES"]},np,sf,synth,assets,runner,cache)
        row.update(block_id=block["id"],start_s=block["start_s"],end_s=block["end_s"],window_s=block["duration_s"],
            selected_lead_s=.2,model_fit_margin_s=block["duration_s"]-.2-row["speech_block_seconds"],sentences_exact_model=align_sentences(module,synth,row))
        cache[rid]=row;existing.update(takes=list(cache.values()),updated_utc=dt.datetime.now(dt.timezone.utc).isoformat(),code_sha256=sha(__file__))
        atomic(INDEX,existing)
        print(json.dumps({"block":block["id"],"window_s":block["duration_s"],"complete_take_s":row["duration"],"full_model_s":row["speech_block_seconds"],
            "fit_margin_s":row["model_fit_margin_s"],"sentences":len(row["sentences_exact_model"]),"unresolved_sentences":sum(p["start_s_in_take"] is None for p in row["sentences_exact_model"])}),flush=True)
    assert len(existing["takes"])==14
    for name,expected in module.EXPECTED_ASSETS.items():assert sha(reuse.VOICE_SOURCE/name)==expected
    oversized=[t["block_id"] for t in existing["takes"] if t["model_fit_margin_s"]<0]
    print(json.dumps({"takes_complete":14,"oversized_blocks":oversized,"titles_spoken":False,"new_Native_ticks":0}),flush=True)
    if oversized:return 2
    return 0


def assemble():
    script=load(GUION);assert canonical(script)==canonical(extract())
    source=load(INDEX);assert len(source["takes"])==14 and source["guion_sha256"]==sha(GUION)
    sys.path.insert(0,str(reuse.alias_readonly()/"pydeps"))
    import numpy as np
    import soundfile as sf
    frames=300*24000;master=np.zeros(frames,dtype=np.int32);proofs=[];phrases=[];clauses=[]
    for block in script["blocks"]:
        take=next(t for t in source["takes"] if t["block_id"]==block["id"])
        assert take["model_fit_margin_s"]>=0
        file=WORK/take["file"];assert sha(file)==take["wav_sha256"]
        with file.open("rb") as f:waveform,sr=sf.read(f,dtype="int32")
        assert sr==24000 and len(waveform)==take["total_samples"]
        a=take["leading_margin_samples"];n=take["model_samples"];model=waveform[a:a+n]
        start=round((block["start_s"]+.2)*sr);end=start+n;assert end<=round(block["end_s"]*sr)
        assert np.count_nonzero(waveform[:a])==0 and np.count_nonzero(waveform[a+n:])==0
        master[start:end]=model
        proofs.append({"block_id":block["id"],"source_path":str(file.relative_to(ROOT)),"source_sha256":sha(file),"source_model_samples":[a,a+n],
            "master_model_samples":[start,end],"model_PCM_int32_sha256":hashlib.sha256(model.tobytes()).hexdigest(),"entire_model_waveform_retained":True,
            "only_external_zero_silence_replaced":True,"window_s":[block["start_s"],block["end_s"]],"model_s":[start/sr,end/sr]})
        shift=start/sr-a/sr
        for p in take["sentences_exact_model"]:
            row={**p,"block_id":block["id"]}
            row["start_s_in_master"]=None if p["start_s_in_take"] is None else p["start_s_in_take"]+shift
            row["end_s_in_master"]=None if p["end_s_in_take"] is None else p["end_s_in_take"]+shift
            phrases.append(row)
        for p in take["clauses_exact_model"]:
            row={**p,"block_id":block["id"]}
            row["start_s_in_master"]=None if p["start_s_in_take"] is None else p["start_s_in_take"]+shift
            row["end_s_in_master"]=None if p["end_s_in_take"] is None else p["end_s_in_take"]+shift
            clauses.append(row)
    raw=AUDIO/"locucion_5min_24k.wav"
    with raw.open("xb") as f:sf.write(f,master,24000,subtype="PCM_24",format="WAV")
    with raw.open("rb") as f:readback,sr=sf.read(f,dtype="int32")
    assert np.array_equal(readback,master) and len(readback)==7200000
    for p in proofs:
        a,b=p["master_model_samples"];assert hashlib.sha256(readback[a:b].tobytes()).hexdigest()==p["model_PCM_int32_sha256"]
    tests=next(p for p in ROOT.parents if p.name=="tests")
    ff=tests/"_dee20_trabajo/presentacion_clara/herramientas/ffmpeg.exe";out=AUDIO/"locucion_5min_48k.wav"
    command=[str(ff),"-nostdin","-hide_banner","-v","error","-n","-i",str(raw),"-ar","48000","-ac","2","-c:a","pcm_s24le",str(out)]
    process=subprocess.run(command,stdin=subprocess.DEVNULL,capture_output=True,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    assert process.returncode==0,process.stderr.decode(errors="replace")
    with out.open("rb") as f:final,fs=sf.read(f,dtype="int32",always_2d=True)
    assert fs==48000 and final.shape==(14400000,2) and np.array_equal(final[:,0],final[:,1])
    assert all(sha(WORK/t["file"])==t["wav_sha256"] for t in source["takes"])
    report={"schema":"DEE.5MIN.continuous_literal_narration.R01","created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"duration_seconds":300,"sample_rate":48000,"channels":2,
        "sample_frames":14400000,"voice":"em_alex","speed":1.0,"blocks":14,"literal_words":616,"titles_spoken":False,"new_Native_ticks":0,
        "guion_sha256":sha(GUION),"take_index_sha256":sha(INDEX),"block_waveform_proofs":proofs,"phrase_model_timings":phrases,"clause_model_timings":clauses,
        "phrases_resolved":sum(p["start_s_in_master"] is not None for p in phrases),"phrases_unresolved":sum(p["start_s_in_master"] is None for p in phrases),
        "assembly":"Every original complete model waveform preserved. Only verified external zero silence replaced by each declared window's padding. No atempo, phoneme cut or internal splice.",
        "final_files":[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":sha(p)} for p in (raw,out)],"FFmpeg":{"command":command,"sha256":sha(ff),"stderr":process.stderr.decode(errors="replace")},
        "code_sha256":sha(__file__),"timing_scope":"Actual emitted model phoneme durations, not word-count timestamps or independent ASR.","listening_or_ASR":"NO EVALUADO: not performed; no human audibility/naturalness claim from these metrics."}
    save_new(AUDIO/"CONTINUIDAD_AUDIO_300s_R01.json",report)
    print(json.dumps({"audio":str(out),"duration_seconds":300,"sample_frames":14400000,"sha256":sha(out),"blocks":14,"phrases_resolved":report["phrases_resolved"],"phrases_unresolved":report["phrases_unresolved"]}),flush=True)


def main():
    sys.meta_path.insert(0,NoNative());boundary()
    parser=argparse.ArgumentParser();parser.add_argument("mode",choices=["extract","synthesize","assemble"]);args=parser.parse_args()
    if args.mode=="extract":
        x=extract();save_new(GUION,x);print(json.dumps({"guion":str(GUION),"sha256":sha(GUION),"blocks":14,"words":616,"source_sha256":DOC_SHA}));return 0
    if args.mode=="synthesize":return synthesize()
    assemble();return 0


if __name__=="__main__":raise SystemExit(main())
