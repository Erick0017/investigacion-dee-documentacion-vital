"""Faithful EN units tied to actual ES model phonemes, never proportional timing."""
from pathlib import Path
import datetime as dt
import hashlib
import importlib.util
import json
import re
import sys
import tempfile

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
A=ROOT/"trabajo/audio"
sys.path.insert(0,str(ROOT.parent/"AUDIOVISUAL_R12/codigo"))
import audio_r12 as reuse
sys.path.insert(0,str(reuse.alias_readonly()/"pydeps"))
from PIL import ImageFont
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from kokoro_onnx.tokenizer import Tokenizer

PLANS={
 (1,3):[("Ya demostró aprendizaje, memoria,","It has already demonstrated learning, memory,"),("composición y comunicación en ensayos concretos.","composition and communication in specific trials.")],
 (3,4):[("Persistir significa utilizar lo conservado y recibir nuevas experiencias,","Persistence means using what is retained and receiving new experiences,"),("no aprender sin parar.","not learning without end.")],
 (4,4):[("También existen repertorios de asociaciones,","Association repertoires also exist,"),("aunque conservar un estado no garantiza siempre su acceso.","although retaining a state does not always guarantee access.")],
 (5,4):[("Es revisión selectiva en ese ensayo,","This is selective revision in that trial,"),("no conservación garantizada de todo conocimiento.","not a guarantee that all knowledge will be preserved.")],
 (7,1):[("En comunicación, información adquirida por un participante llegó a otro","In communication, information acquired by one participant reached another"),("y afectó una respuesta posterior del receptor.","and affected the receiver's later response.")],
 (7,3):[("Se demuestra transmitir y utilizar información","This demonstrates transmitting and using information"),("entre participantes definidos,","between defined participants,"),("sin afirmar conversación humana.","without claiming human conversation.")],
 (9,4):[("En otro ensayo, una salida actuó sobre un servicio externo","In another trial, an output acted on an external service,"),("y su efecto regresó como experiencia.","and its effect returned as experience.")],
 (10,2):[("Experiencias distintas cambiaron la dirección de un pulso","Different experiences changed the direction of a pulse"),("que intervino sobre una interferencia,","that acted on an interference,"),("cambiando una consecuencia funcional.","changing a functional consequence.")],
 (11,4):[("El logro consiste en adquirir y utilizar relaciones concretas,","The achievement is to acquire and use specific relations,"),("no en conversar libremente.","not to hold a free conversation.")],
 (12,1):[("En transferencia, la experiencia previa cambió una primera actuación en otro contexto,","In transfer, prior experience changed the first action in another context,"),("antes de recibir allí una nueva consecuencia.","before receiving a new consequence there.")],
 (13,2):[("Cognitive ya permite utilizar asociaciones, memoria y comparación","Cognitive already allows associations, memory and comparison"),("en una instancia con continuidad propia.","to be used in one instance with its own continuity.")],
 (13,3):[("Universe aporta la dinámica;","Universe provides the dynamics;"),("Thinking, la ejecución;","Thinking, the execution;"),("Cognitive, los accesos y la continuidad.","and Cognitive, access and continuity.")],
 (14,1):[("El interés de DEE está en reunir capacidades","DEE's interest lies in bringing capabilities together"),("dentro de una dinámica computacional propia:","within its own computational dynamics:"),("conservar experiencia, revisarla,","retaining experience, revising it,"),("combinarla y utilizar información.","combining it and using information.")],
 (14,2):[("Esa base permite explorar agentes adaptativos","This basis enables exploration of adaptive agents"),("y nuevas formas de memoria y procesamiento.","and new forms of memory and processing.")]
}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def stamp(t):
    ms=round(t*1000);return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}"
def save(p,x):
    with p.open("x",encoding="utf-8",newline="\n") as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write("\n")


def main():
    translation_path=ROOT/"trabajo/TRADUCCION_EN.json";translation=load(translation_path)
    guion=load(A/"guion.json");index=load(A/"PROVENIENCIA_TOMAS_14.json");continuity=load(A/"CONTINUIDAD_AUDIO_300s_R01.json")
    before={str(p.relative_to(ROOT)):sha(p) for p in (translation_path,A/"guion.json",A/"PROVENIENCIA_TOMAS_14.json",A/"CONTINUIDAD_AUDIO_300s_R01.json",A/"locucion_5min_48k.wav")}
    font_path=Path("C:/Windows/Fonts/segoeui.ttf");font=ImageFont.truetype(str(font_path),84)
    spec=importlib.util.spec_from_file_location("_approved_pronunciation_only",reuse.TTS);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    short_data=reuse.alias_readonly()/"pydeps/espeakng_loader/espeak-ng-data"
    EspeakWrapper.data_path=property(lambda self:short_data)
    tokenizer=Tokenizer()  # G2P only: no ONNX Session or create_timed call.
    rows=[];problems=[]
    for block in translation["blocks"]:
        bnum=block["block"];bid=f"B{bnum:02}"
        original=next(b for b in guion["blocks"] if b["id"]==bid)
        assert original["literal_ES"]==block["literal_ES"]
        take=next(t for t in index["takes"] if t["block_id"]==bid)
        sentence_rows=[p for p in continuity["phrase_model_timings"] if p["block_id"]==bid]
        assert len(sentence_rows)==len(block["sentences"])
        emitted="";char_to_phone=[]
        for j,p in enumerate(take["phoneme_timings"]):
            token=reuse.norm_phonemes(p["phoneme"]);emitted+=token;char_to_phone.extend([j]*len(token))
        for snum,(sentence,aligned) in enumerate(zip(block["sentences"],sentence_rows),1):
            assert sentence["ES"]==aligned["literal_ES"]
            units=PLANS.get((bnum,snum),[(sentence["ES"],sentence["EN"])])
            assert " ".join(es for es,en in units)==sentence["ES"],"ES split must cover the exact complete sentence"
            source_char_cursor=aligned["character_range_0based_exclusive"][0]
            phone_cursor=aligned["phoneme_first_index"]
            for part,(es,en) in enumerate(units,1):
                ca=block["literal_ES"].find(es,source_char_cursor);assert ca>=source_char_cursor
                cb=ca+len(es);source_char_cursor=cb
                words=list(re.finditer(r"\S+",block["literal_ES"]))
                wa=next(i for i,w in enumerate(words) if w.end()>ca);wb=sum(w.start()<cb for w in words)
                if len(units)==1:
                    first,last=aligned["phoneme_first_index"],aligned["phoneme_last_index"]
                else:
                    expected=reuse.norm_phonemes(tokenizer.known(tokenizer.phonemize(module.synthesis_text(es),lang="es-419")))
                    norm_cursor=next(i for i,p in enumerate(char_to_phone) if p>=phone_cursor)
                    at=emitted.find(expected,norm_cursor)
                    if at<0:
                        problems.append({"block":bid,"sentence":snum,"unit":part,"ES":es,"cause":"Exact complete emitted phoneme sequence not found; no linear timestamp fallback"});continue
                    first,last=char_to_phone[at],char_to_phone[at+len(expected)-1]
                    assert aligned["phoneme_first_index"]<=first<=last<=aligned["phoneme_last_index"]
                    phone_cursor=last+1
                start=take["phoneme_timings"][first]["start"]+block["start_s"]+.2-take["leading_margin_samples"]/24000
                end=take["phoneme_timings"][last]["end"]+block["start_s"]+.2-take["leading_margin_samples"]/24000
                ew=en.split();choices=[]
                if font.getlength(en)<=1674:choices.append(([en],float(font.getlength(en)),0))
                for split in range(1,len(ew)):
                    lines=[" ".join(ew[:split])," ".join(ew[split:])];widths=[float(font.getlength(line)) for line in lines]
                    choices.append((lines,max(widths),abs(widths[0]-widths[1])))
                good=[c for c in choices if c[1]<=1674]
                if not good:
                    problems.append({"block":bid,"sentence":snum,"unit":part,"EN":en,"cause":"Cannot fit two84pxSegoeUI lines within1680px"});continue
                chosen=min(good,key=lambda c:(len(c[0])>1,c[1]+c[2]*.05)) if any(len(c[0])==1 for c in good) else min(good,key=lambda c:c[1]+c[2]*.05)
                rows.append({"block_id":bid,"sentence_1based":snum,"unit_1based":part,"source_full_ES_sentence":sentence["ES"],"source_full_EN_sentence":sentence["EN"],
                    "ES_phrase":es,"EN_cue":en,"EN_lines":chosen[0],"line_widths_px":[float(font.getlength(line)) for line in chosen[0]],
                    "ES_character_range_0based_exclusive":[ca,cb],"ES_word_range_0based_exclusive":[wa,wb],"phoneme_first_index":first,"phoneme_last_index":last,
                    "voice_start_global_s":start,"voice_end_global_s":end,"source_take_path":take["file"],"source_take_sha256":take["wav_sha256"],
                    "alignment":"exact_complete_span_of_emitted_model_phonemes; G2P only for new subphrases","new_G2P_needed":len(units)>1,
                    "translation_adjustment":"Semantic segmentation; English words unchanged in order except documented faithful compact rendering" if (bnum,snum) in PLANS else "Root-authored complete sentence unchanged"})
    report={"schema":"DEE.5MIN.EN_subtitles_model_alignment.R01","created_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"new_Native_ticks":0,"new_TTS_inference":False,
        "translation_source_sha256":sha(translation_path),"rows":rows,"unresolved":problems,"font":{"path":str(font_path),"sha256":sha(font_path),"size_px":84,"safe_width_px":1674,"maximum_width_px":1680,"maximum_lines":2},
        "source_hashes_before":before,"perceptual_scope":"Model-time editorial alignment, not independent ASR, listening or comprehension; no proportional text-length timing used."}
    if problems:
        save(A/"INDICE_SUBTITULOS_EN_PENDIENTES_R01.json",report);print(json.dumps({"unresolved":problems},ensure_ascii=False));return 2
    rows.sort(key=lambda r:r["voice_start_global_s"])
    for i,row in enumerate(rows):
        end=row["voice_end_global_s"]+.08
        if i+1<len(rows):end=min(end,max(row["voice_end_global_s"],rows[i+1]["voice_start_global_s"]-.01))
        row.update(cue_index=i+1,SRT_start_global_s=row["voice_start_global_s"],SRT_end_global_s=end,
            start_error_vs_model_s=0,end_hold_after_model_s=end-row["voice_end_global_s"])
        assert 0<=row["SRT_start_global_s"]<end<=300 and row["end_hold_after_model_s"]<=.1+1e-9
        if i:assert row["SRT_start_global_s"]>=rows[i-1]["SRT_end_global_s"]-1e-9
    # The two exact English pilot phrases remain untouched.
    b6=[r for r in rows if r["block_id"]=="B06"]
    assert b6[0]["EN_cue"]=="In composition, two contributions formed a common product."
    assert b6[1]["EN_cue"]=="That product was used in another interaction within the same world."
    output=ROOT/"DEE_Cognitive_5min_EN.srt"
    with output.open("x",encoding="utf-8",newline="\n") as f:
        for row in rows:f.write(f"{row['cue_index']}\n{stamp(row['SRT_start_global_s'])} --> {stamp(row['SRT_end_global_s'])}\n"+"\n".join(row["EN_lines"])+"\n\n")
    after={name:sha(ROOT/name) for name in before};assert before==after
    report.update(cue_count=len(rows),all64_sentences_covered=True,all84px_lines_fit=True,pilot_two_EN_phrases_literal=True,source_hashes_after=after,
        output={"path":str(output.relative_to(ROOT)),"bytes":output.stat().st_size,"sha256":sha(output)},code_sha256=sha(__file__))
    save(A/"INDICE_SUBTITULOS_EN_R01.json",report)
    print(json.dumps({"SRT":str(output),"sha256":sha(output),"cues":len(rows),"source_sentences":64,"unresolved":0,"maximum_line_width_px":max(w for r in rows for w in r["line_widths_px"])},ensure_ascii=False))
    return 0


if __name__=="__main__":raise SystemExit(main())
