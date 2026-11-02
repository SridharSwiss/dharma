"""Telugu narration in the channel owner's cloned voice with IndicF5 (AI4Bharat, MIT).

    python clone_tts.py bridge                       # pass 1: English ref -> Telugu bridge reference
    python clone_tts.py scenes <script.json> <outdir> [scene_id ...]   # pass 2: one wav per scene

Pass 1 turns the English reference into a Telugu reference in the same voice, so pass 2 copies the
voice with Telugu rhythm and vowel lengths instead of English prosody.
"""
import json, os, re, sys, numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = r"C:\Users\SRIDH\Videos\DharmaDeepam\voice"
REF_EN = os.path.join(VOICE, "voice_owner-ref.wav")
REF_EN_TEXT = ("Traditional firewalls and reactive defenses are no longer enough to handle the massive surge of digital "
               "asset flows and sophisticated exploits.")
REF_EN_CLIP = os.path.join(VOICE, "voice_owner-ref_0-8.8s.wav")
BRIDGE_TEXT = ("నమస్కారం. కార్తీక మాసం శివుడికీ, విష్ణువుకీ ప్రీతికరమైన మాసం. "
               "ఈ నెలలో రోజూ తెల్లవారుజామున ఒక చిన్న దీపం వెలిగిస్తే, ఇల్లంతా ప్రశాంతంగా ఉంటుంది.")
BRIDGE = os.path.join(VOICE, "bridge_te_v2.wav")
SR = 24000
# Telugu reference cut from the clean second sentence of the bridge (14.70-21.05 s): voice from the owner,
# rhythm and vowel lengths from Telugu. Used for every scene.
TE_REF = os.path.join(VOICE, "voice_te_ref.wav")
TE_REF_TEXT = "ఈ నెలలో రోజూ తెల్లవారుజామున ఒక చిన్న దీపం వెలిగిస్తే, ఇల్లంతా ప్రశాంతంగా ఉంటుంది."

MODELS = r"C:\Users\SRIDH\dharma-tts\models"

def _local(repo_id):
    # plain-folder downloads: Windows without Developer Mode cannot create the HF cache symlinks
    from huggingface_hub import snapshot_download
    d = os.path.join(MODELS, repo_id.replace("/", "__"))
    if not os.path.isdir(d) or not any(f.endswith((".bin", ".safetensors", ".yaml")) for f in os.listdir(d)):
        snapshot_download(repo_id, local_dir=d)
    return d

class Model:
    """IndicF5 assembled directly from its weights (same parts and settings as the model card's INF5Model)."""
    def __init__(self):
        import imageio_ffmpeg
        from pydub import AudioSegment
        AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()
        from safetensors.torch import load_file
        from f5_tts.infer.utils_infer import load_vocoder, load_model
        from f5_tts.model import DiT
        d = _local("ai4bharat/IndicF5")
        self.vocoder = load_vocoder("vocos", is_local=True, local_path=_local("charactr/vocos-mel-24khz"), device="cpu")
        self.ema = load_model(DiT, dict(dim=1024, depth=22, heads=16, ff_mult=2, text_dim=512, conv_layers=4),
                              mel_spec_type="vocos", vocab_file=os.path.join(d, "checkpoints", "vocab.txt"), device="cpu")
        sd = load_file(os.path.join(d, "model.safetensors"))
        pick = lambda pre: {k[len(pre):]: v for k, v in sd.items() if k.startswith(pre)}
        print("ema", self.ema.load_state_dict(pick("ema_model._orig_mod."), strict=False))
        print("voc", self.vocoder.load_state_dict(pick("vocoder._orig_mod."), strict=False))
        self.ema.eval(); self.vocoder.eval()

    def __call__(self, text, ref_audio_path, ref_text, speed=0.92, cps=13.0):
        # F5 sizes the output from UTF-8 byte ratios; Telugu letters are 3 bytes vs 1 for English, so with an
        # English reference it allots ~3x too much time and fills it with babble. Size it from Telugu
        # speaking rate instead (cps = Unicode characters per second, measured ~13-14 for calm narration).
        from f5_tts.infer.utils_infer import preprocess_ref_audio_text, infer_process
        ra, rt = preprocess_ref_audio_text(ref_audio_path, ref_text)
        ref_sec = sf.info(ra).duration
        chars = len(re.sub(r"\s+", "", text))
        fix = ref_sec + chars / cps / speed + 0.3
        audio, sr, _ = infer_process(ra, rt, text, self.ema, self.vocoder, mel_spec_type="vocos",
                                     speed=speed, nfe_step=32, fix_duration=fix, device="cpu")
        return audio

def load():
    return Model()

def gen(model, text, ref, ref_text):
    a = model(text, ref_audio_path=ref, ref_text=ref_text)
    a = np.asarray(a, dtype=np.float32)
    if a.dtype != np.float32 or np.abs(a).max() > 1.5: a = a / 32768.0
    return a

def sentences(t):
    parts = [p.strip() for p in re.split(r"(?<=[.?!])\s+", t) if p.strip()]
    out, cur = [], ""
    for p in parts:  # keep chunks 60-180 chars: long enough for natural prosody, short enough to stay stable
        if len(cur) + len(p) < 180: cur = (cur + " " + p).strip()
        else:
            if cur: out.append(cur)
            cur = p
    if cur: out.append(cur)
    return out

def main():
    mode = sys.argv[1]
    model = load()
    if mode == "bridge":
        if not os.path.exists(REF_EN_CLIP):
            x, r = sf.read(REF_EN); sf.write(REF_EN_CLIP, x[: int(r * 8.8)], r)
        a = gen(model, BRIDGE_TEXT, REF_EN_CLIP, REF_EN_TEXT)
        sf.write(BRIDGE, a, SR); print("bridge", BRIDGE, round(len(a) / SR, 1), "s")
        return
    script, outdir = sys.argv[2], sys.argv[3]
    only = set(sys.argv[4:])
    os.makedirs(outdir, exist_ok=True)
    S = json.load(open(script, encoding="utf-8"))
    gap = np.zeros(int(SR * 0.28), dtype=np.float32)
    for sc in S["scenes"]:
        if only and sc["id"] not in only: continue
        if os.path.exists(os.path.join(outdir, sc["id"] + ".wav")): print("skip", sc["id"]); continue  # resume
        chunks = []
        for s in sentences(sc["say"]):
            chunks += [gen(model, s, TE_REF, TE_REF_TEXT), gap]
        a = np.concatenate(chunks)
        sf.write(os.path.join(outdir, sc["id"] + ".wav"), a, SR)
        print("scene", sc["id"], round(len(a) / SR, 1), "s", flush=True)

if __name__ == "__main__":
    main()
