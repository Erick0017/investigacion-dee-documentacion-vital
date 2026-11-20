"""Editorial phrase assignment aligned to stored emitted phoneme timestamps.

No waveform, schedule, adapter or renderer is changed. Text cut choices are
editorial; timestamps are measured model events, not word-count interpolation.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"codigo"))
import audio_r12 as audio

# Each pair specifies the exact terminal literal text of the first and second
# contiguous fragments. No words or punctuation are rewritten.
CUTS={
"S01.1":["sistema experimental","a la inteligencia."],
"S01.2":["aprendizaje, memoria,","ensayos concretos."],
"S01.3":["conservar experiencia","nuevas situaciones."],
"S02.1":["un lugar.","información."],
"S02.2":["organización existente.","un resultado,"],
"S02.3":["Aquí, físico significa","estados e interacciones del modelo."],
"S03.1":["su historia.","su estado anterior,"],
"S03.2":["y reabrirse.","también las colas"],
"S03.3":["aprender sin parar.","utilizar lo conservado"],
"S04.1":["una experiencia","relaciones dentro del mundo."],
"S04.2":["estados y relaciones del sistema.","Para comprobar su uso,"],
"S04.3":["repertorios de varias asociaciones.","se comprueba en cada prueba:"],
"S05.1":["una asociación ya aprendida.","cambiaron su respuesta"],
"S05.2":["las otras asociaciones del panel:","siguieron disponibles."],
"S05.3":["controles de revisión.","adquirir, corregir y volver a utilizar una relación,"],
"S06.1":["dos contribuciones","en un producto común."],
"S06.2":["una historia de orden y contacto.","cambia la consecuencia,"],
"S06.3":["procesamiento compuesto:","para producir consecuencias nuevas."],
"S07.1":["en un participante","llegó a otro."],
"S07.2":["o contenido distinto","separar el efecto de comunicar"],
"S07.3":["La capacidad observada","transmitir y utilizar información entre participantes definidos,"],
"S08.1":["anticipación y consulta.","información actual."],
"S08.2":["La pregunta accede","en un banco propio,"],
"S08.3":["el aparato nativo.","sus oportunidades y tiempos."],
"S09.1":["la consecuencia de una acción","modificó una referencia."],
"S09.2":["el comportamiento fue distinto.","qué aporta experimentar la consecuencia,"],
"S09.3":["una salida activó","mediante un puente preparado,"],
"S10.1":["en un perfil experimental:","la dirección de un pulso"],
"S10.2":["una consecuencia funcional.","el efecto de esa historia"],
"S10.3":["Es regulación local.","Geometría y oportunidades siguen preparadas;"],
"S11.1":["mediante experiencia con un uso.","Más adelante,"],
"S11.2":["como entradas.","adquirir y utilizar una relación,"],
"S11.3":["Son asociaciones funcionales delimitadas.","todos los conceptos universales"],
"S12.1":["La experiencia previa","primera actuación en otro contexto,"],
"S12.2":["esa experiencia podía perjudicar.","Transferir no significa acertar siempre:"],
"S12.3":["muchas contribuciones.","ampliar esas funciones,"],
"S13.1":["ensayos identificados.","asociaciones, memoria y comparación"],
"S13.2":["Universe aporta la dinámica;","Thinking, la ejecución;"],
"S13.3":["La integración existe,","sigue siendo más amplio"],
"S14.1":["dinámica computacional propia:","conservar experiencia, revisarla,"],
"S14.2":["y nuevas formas de memoria y procesamiento.","Las aplicaciones y ventajas concretas"],
"S14.3":["DEE Cognitive: capacidades demostradas,","un sistema inteligente en desarrollo."]}


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def split_literal(text,cuts):
    fragments=[];cursor=0
    for cut in cuts:
        i=text.find(cut,cursor)
        if i<cursor:raise ValueError("Literal cut absent: "+cut)
        end=i+len(cut);fragments.append(text[cursor:end].strip());cursor=end
    fragments.append(text[cursor:].strip())
    assert all(fragments) and " ".join(fragments)==text
    return fragments


def align_fragments(module,synth,take,fragments):
    phonemes=take["phoneme_timings"]
    stream="";indices=[]
    for i,value in enumerate(phonemes):
        chars=audio.norm_phonemes(value["phoneme"])
        stream+=chars;indices.extend([i]*len(chars))
    result=[];cursor=0
    for text in fragments:
        expected=audio.norm_phonemes(synth.tokenizer.known(synth.tokenizer.phonemize(module.synthesis_text(text),lang=module.PARAMS["language"])))
        found=stream.find(expected,cursor);matched=len(expected);method="exact_fragment_canonical_emitted_phonemes"
        if found<0:
            for size in (64,48,40,32,24,20,16,12):
                prefix=expected[:size]
                if len(prefix)>=12 and stream.count(prefix,cursor)==1:
                    found=stream.find(prefix,cursor);matched=len(prefix);method="unique_emitted_phoneme_prefix_"+str(len(prefix));break
        if found<0:
            result.append({"fragment_literal":text,"status":"UNRESOLVED_NO_INVENTED_WORD_TIME"})
            continue
        first,last=indices[found],indices[found+matched-1]
        result.append({"fragment_literal":text,"status":"ALIGNED_TO_EMITTED_MODEL_EVENTS","method":method,
            "phoneme_first_index":first,"matched_phoneme_last_index":last,"matched_canonical_characters":matched,
            "phoneme_onset_take_s":float(phonemes[first]["start"]),
            "last_matched_phoneme_end_take_s":float(phonemes[last]["end"]),
            "exact_full_fragment_matched":method.startswith("exact_fragment")})
        cursor=found+matched
    return result


def main():
    source_path=ROOT/"guion_fuente/SHOTLIST_R12_DERIVADO_DEL_DOCX.json"
    schedule_path=ROOT/"audio/TIEMPOS_ANCLAS_R12.json"
    index_path=ROOT/"audio/PROVENIENCIA_AUDIO_R12.json"
    pcm_path=ROOT/"audio/PRUEBA_PCM_R12.json"
    subtitle_path=ROOT/"audio/SUBTITULOS_ALINEADOS_R12.json"
    inputs=[source_path,schedule_path,index_path,pcm_path,subtitle_path,ROOT/"audio/R12_ES.srt"]
    before={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    source,schedule,index,pcm,subtitles=[load(p) for p in inputs[:5]]
    literal={s["original_shot_id"]:s for c in source["scenes"] for s in c["shots"]}
    takes={r["id"]:r for r in index["takes"]};placement={r["shot_id"]:r for r in pcm["model_blocks"]}
    assert set(CUTS)==set(literal) and len(subtitles["cues"])==97
    audio.write_boundary()
    module,np,sf,synth,assets,runner=audio.setup()  #Tokenizer only; never create/create_timed.
    rows=[];unresolved=[]
    old_files=list((ROOT/"qa").glob("KEYFRAMES_*/KEYFRAMES.json"))
    old=load(sorted(old_files)[-1])["records"] if old_files else []
    for timing in schedule["rows"]:
        sid=timing["shot_id"];internal=timing["shot_id_internal"]
        take=takes[index["selected"][internal]]
        assert sha(ROOT/take["file"])==take["wav_sha256"]
        fragments=split_literal(timing["anchor_exact"],CUTS[sid])
        aligned=align_fragments(module,synth,take,fragments)
        delta=timing["actual_start_s"]+(placement[internal]["new_external_lead_samples"]-take["leading_margin_samples"])/24000
        for phase,item in zip(("Orientar","Mostrar","Leer"),aligned):
            item["phase"]=phase;item["phase_instruction_exact"]=literal[sid]["phases_exact"][phase.lower()]
            if item["status"].startswith("UNRESOLVED"):
                unresolved.append({"shot_id":sid,"phase":phase,"fragment":item["fragment_literal"]});continue
            item["voice_fragment_start_s"]=delta+item["phoneme_onset_take_s"]
            item["matched_phoneme_end_s"]=delta+item["last_matched_phoneme_end_take_s"]
            item["first_video_frame_at_or_after_voice_onset"]=math.ceil(item["voice_fragment_start_s"]*30-1e-9)
            item["stored_emitted_phoneme_source"]={"path":"audio/PROVENIENCIA_AUDIO_R12.json","take_id":take["id"],
                "phoneme_first_index":item["phoneme_first_index"],"phoneme_last_matched_index":item["matched_phoneme_last_index"]}
        complete=all(x["status"]=="ALIGNED_TO_EMITTED_MODEL_EVENTS" for x in aligned)
        kframes=None;bounds=None
        if complete:
            bounds=[aligned[1]["first_video_frame_at_or_after_voice_onset"],aligned[2]["first_video_frame_at_or_after_voice_onset"]]
            a,b=timing["first_visual_frame_30fps"],timing["end_visual_frame_exclusive_30fps"]
            if not a<bounds[0]<bounds[1]<b:raise ValueError("Nonordered phase onsets "+sid)
            ks=[a,*bounds,b-1]
            kframes=[{"keyframe":k,"frame":v,"time_s":v/30,"basis":basis} for k,v,basis in zip(
                ("K0","K1","K2","K3"),ks,("Actual shot boundary before first voice, including prepared leading silence",
                "First frame at or after measured onset of Mostrar fragment","First frame at or after measured onset of Leer fragment",
                "Last existing frame of this actual shot; includes final reading reserve when applicable"))]
            ends=[aligned[1]["voice_fragment_start_s"],aligned[2]["voice_fragment_start_s"],timing["actual_end_s"]]
            starts=[timing["actual_start_s"],aligned[1]["voice_fragment_start_s"],aligned[2]["voice_fragment_start_s"]]
            for phase,start,end in zip(aligned,starts,ends):
                phase["editorial_phase_start_s"]=start;phase["editorial_phase_end_s"]=end
                phase["interval_basis"]="Measured next-fragment onset; final phase extends to fixed shot end. Not a guessed word-ending timestamp."
        oldshot=[{"keyframe":x["keyframe"],"frame":x["frame"],"time_s":x["seconds"]} for x in old if x["shot_id"]==sid]
        rows.append({"scene_id":timing["scene_id"],"shot_id":sid,"shot_id_internal":internal,"literal_anchor":timing["anchor_exact"],
            "take_id":take["id"],"take_WAV_sha256":take["wav_sha256"],"actual_start_s":timing["actual_start_s"],"actual_end_s":timing["actual_end_s"],
            "first_visual_frame_30fps":timing["first_visual_frame_30fps"],"end_visual_frame_exclusive_30fps":timing["end_visual_frame_exclusive_30fps"],
            "phases":aligned,"phase_boundaries_frames":bounds,"keyframes_voice_bound":kframes,
            "previous_sampling_keyframes_NOT_voice_bindings":oldshot,
            "alignment_status":"RESOLVED" if complete else "UNRESOLVED",
            "assignment_status":"COMPROBACIÓN EDITORIAL; not a listening/ASR or factual-keyframe certification",
            "SRT_cue_indices_0based":[i for i,c in enumerate(subtitles["cues"]) if c["shot_id"]==sid]})
    after={str(p.relative_to(ROOT)):sha(p) for p in inputs};assert before==after
    report={"schema":"DEE.R12.editorial_phases_real_voice.R01","status":"COMPROBACIÓN EDITORIAL",
        "scene_count":14,"shot_count":42,"phase_count":126,"all_fragments_literal":True,
        "all_boundaries_resolved":not unresolved,"unresolved":unresolved,"rows":rows,
        "inputs_sha256":before,"script_sha256":sha(__file__),
        "method":"Three manually chosen contiguous literal fragments per anchor, phonemized with the original tokenizer and matched against already emitted model phoneme events. Time offsets use exact stored placement and the new external zero margins. No word-count timing, audio inference, ASR, stretching or waveform change.",
        "K0_K3_scope":"Editorial voice-bound keyframes recommended to renderer. They are NOT new physical states or evidence that the visual K0/K1/K2/K3 are factually correct; primary bindings remain separately required.",
        "unchanged_audio_schedule_and_sources":True,"model_synthesis_calls":0,"new_Native_ticks":0,"human_listening":False,"independent_ASR":False}
    out=ROOT/"AUDITORIA/FASES_Y_VOZ_R12.json";assert not out.exists()
    out.write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
    print(json.dumps({"path":str(out),"bytes":out.stat().st_size,"sha256":sha(out),"phases":126,
        "resolved_shots":sum(r["alignment_status"]=="RESOLVED" for r in rows),"unresolved":unresolved,"model_synthesis_calls":0},ensure_ascii=False))


if __name__=="__main__":main()
