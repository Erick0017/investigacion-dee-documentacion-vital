using System;
using System.Collections.Generic;
using System.Speech.Synthesis;
public class MarcaVozDEE {
    public double seconds;
    public int start;
    public int count;
    public string text;
}
public class VozDEE {
    public static MarcaVozDEE[] Generar(string text,string output) {
        List<MarcaVozDEE> marks=new List<MarcaVozDEE>();
        using(SpeechSynthesizer voice=new SpeechSynthesizer()) {
            voice.SelectVoice("Microsoft Sabina Desktop");voice.Rate=0;voice.Volume=100;
            voice.SpeakProgress += delegate(object sender,SpeakProgressEventArgs e) {
                lock(marks) { marks.Add(new MarcaVozDEE {seconds=e.AudioPosition.TotalSeconds,start=e.CharacterPosition,count=e.CharacterCount,text=e.Text}); }
            };
            voice.SetOutputToWaveFile(output);voice.Speak(text);voice.SetOutputToNull();
        }
        lock(marks) { return marks.ToArray(); }
    }
}
