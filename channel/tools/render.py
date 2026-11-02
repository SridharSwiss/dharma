#!/usr/bin/env python3
"""Faceless devotional video renderer for Dharma Deepam.

    python3 render.py <video_dir> <img_dir> [--voice draft|<folder of per-scene wavs>] [--shorts p1,p2,pournami]

Reads <video_dir>/script.json (scenes: img, title, sub, bullets|list, say, chapter) and renders:
  out/<id>.mp4          1920x1080 long video (slow Ken Burns on each painting, Telugu text, narration, tanpura-like drone)
  out/<id>.srt          Telugu subtitles timed to the narration
  out/chapters.txt      YouTube chapters from scene timings
  out/short-<scene>.mp4 1080x1920 Shorts for the listed scenes
Voice: 'draft' uses espeak-ng Telugu (robotic, for timing only - replace before upload).
A folder of human recordings named <scene_id>.wav replaces it scene by scene.
"""
import json, os, re, subprocess, sys, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_DIR = "/usr/share/fonts/truetype/noto/"
_FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")
SERIF_B = os.path.join(_FD, "Ramabhadra-Regular.ttf")   # heavy display face for titles (benchmark: Bhakthi TV-style)
SANS = os.path.join(_FD, "Mandali-Regular.ttf")          # clean body face for subtitles and lists
SANS_B = FONT_DIR + "NotoSansTelugu-Bold.ttf" if os.path.exists(FONT_DIR + "NotoSansTelugu-Bold.ttf") else SERIF_B
FPS = 25
GOLD = (245, 196, 110)
CREAM = (255, 246, 230)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: sys.exit("FAILED: " + " ".join(cmd[:6]) + "\n" + r.stderr[-1500:])
    return r

def dur(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout)

def font(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)

def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def overlay(scene, W, H, vertical=False, draft=True):
    """Transparent PNG with the scene's text."""
    fix = lambda x: x.replace(" · ", " – ").replace("·", "–")
    scene = {k: (fix(v) if isinstance(v, str) else [fix(i) for i in v] if isinstance(v, list) else v) for k, v in scene.items()}
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pad = int(W * 0.06)
    has_list = bool(scene.get("list"))
    # shade: bottom gradient (or left panel for lists)
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shade)
    if has_list and not vertical:
        sd.rectangle([0, 0, int(W * 0.58), H], fill=(12, 8, 4, 190))
    else:
        top = int(H * (0.50 if vertical else 0.55))
        for y in range(top, H):
            a = int(215 * ((y - top) / (H - top)) ** 0.9)
            sd.line([(0, y), (W, y)], fill=(10, 6, 2, a))
        if vertical:
            for y in range(0, int(H * 0.22)):
                a = int(170 * (1 - y / (H * 0.22)))
                sd.line([(0, y), (W, y)], fill=(10, 6, 2, a))
    im = Image.alpha_composite(im, shade); d = ImageDraw.Draw(im)
    # brand
    fb = font(SANS_B, int(H * (0.022 if vertical else 0.03)))
    d.text((pad, int(H * 0.04)), "🪔 ధర్మ దీపం" if False else "ధర్మ దీపం", font=fb, fill=GOLD)
    if draft:
        fd = font(SANS, int(H * (0.016 if vertical else 0.022)))
        t = "డ్రాఫ్ట్ స్వరం – అప్‌లోడ్ ముందు మార్చండి"
        d.text((W - pad - d.textlength(t, font=fd), int(H * 0.045)), t, font=fd, fill=(255, 120, 90))
    ft = font(SERIF_B, int(H * (0.042 if vertical else 0.072)))
    fs = font(SANS, int(H * (0.026 if vertical else 0.040)))
    fl = font(SANS, int(H * (0.024 if vertical else 0.038)))
    maxw = W - 2 * pad
    if has_list and not vertical:
        y = int(H * 0.13)
        for line in wrap(d, scene["title"], ft, int(W * 0.5)):
            d.text((pad, y), line, font=ft, fill=GOLD, stroke_width=3, stroke_fill=(20, 8, 0)); y += int(ft.size * 1.35)
        y += int(H * 0.02)
        for item in scene["list"]:
            d.ellipse([pad, y + fl.size * 0.45, pad + 12, y + fl.size * 0.45 + 12], fill=GOLD)
            d.text((pad + 30, y), item, font=fl, fill=CREAM); y += int(fl.size * 1.55)
        return im
    lines_t = wrap(d, scene["title"], ft, maxw)
    sub = scene.get("sub")
    bullets = scene.get("bullets") or []
    block = len(lines_t) * ft.size * 1.3 + (fs.size * 1.6 if sub else 0) + len(bullets) * fs.size * 1.5
    y = (int(H * 0.62) if vertical else int(H * 0.92 - block))
    # soft backdrop so text stays readable over bright art (flames, sky)
    bw = max([d.textlength(l, font=ft) for l in lines_t] + [d.textlength(sub or "", font=fs)] + [d.textlength(b, font=fs) + fs.size for b in bullets])
    bk = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bk)
    bd.rounded_rectangle([pad - 24, y - 18, min(W - pad + 24, pad + bw + 28), y + block + 22], radius=18, fill=(8, 5, 2, 150))
    im = Image.alpha_composite(im, bk); d = ImageDraw.Draw(im)
    for line in lines_t:
        d.text((pad, y), line, font=ft, fill=GOLD, stroke_width=3, stroke_fill=(20, 8, 0)); y += int(ft.size * 1.3)
    if sub:
        for line in wrap(d, sub, fs, maxw):
            d.text((pad, y + 6), line, font=fs, fill=CREAM); y += int(fs.size * 1.5)
    for b in bullets:
        r_ = fs.size * 0.16
        d.ellipse([pad, y + 8 + fs.size * 0.55, pad + 2 * r_, y + 8 + fs.size * 0.55 + 2 * r_], fill=GOLD)
        d.text((pad + fs.size * 0.8, y + 8), b, font=fs, fill=CREAM); y += int(fs.size * 1.5)
    return im

def tts(text, out):
    run(["espeak-ng", "-v", "te", "-s", "138", "-p", "38", "-w", out, text])

def scene_clip(img_path, ov_path, audio, out, W, H, seconds, idx, vertical=False):
    frames = int(seconds * FPS) + 1
    src = Image.open(img_path).convert("RGB")
    sw, sh = src.size
    # trim generated borders slightly, then cover-crop to the target ratio
    src = src.crop((int(sw * 0.015), int(sh * 0.02), int(sw * 0.985), int(sh * 0.98)))
    sw, sh = src.size
    tr = W / H
    if sw / sh > tr:
        nw = int(sh * tr); x0 = (sw - nw) // 2; src = src.crop((x0, 0, x0 + nw, sh))
    else:
        nh = int(sw / tr); y0 = (sh - nh) // 2; src = src.crop((0, y0, sw, y0 + nh))
    big = os.path.splitext(out)[0] + "_src.jpg"
    src.resize((int(W * 1.25), int(H * 1.25)), Image.LANCZOS).save(big, quality=92)
    zin = idx % 2 == 0
    z = "min(1+0.10*on/%d,1.10)" % frames if zin else "max(1.10-0.10*on/%d,1.0)" % frames
    vf = (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
          f"format=yuv420p")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", big, "-i", ov_path, "-i", audio,
         "-filter_complex", f"[0:v]{vf}[bg];[bg][1:v]overlay=0:0,fade=t=in:st=0:d=0.5,fade=t=out:st={seconds-0.5:.2f}:d=0.5[v];"
                            f"[2:a]apad,atrim=0:{seconds:.2f},afade=t=in:d=0.2[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{seconds:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", out])
    os.remove(big)

def drone(seconds, out):
    # Sa (C3) + Pa (G3) + upper Sa, slow tremolo: a quiet tanpura-like bed
    run(["ffmpeg", "-y", "-loglevel", "error",
         "-f", "lavfi", "-i", f"sine=f=130.81:d={seconds}", "-f", "lavfi", "-i", f"sine=f=196.0:d={seconds}",
         "-f", "lavfi", "-i", f"sine=f=261.63:d={seconds}",
         "-filter_complex", "[0]volume=0.6[a];[1]volume=0.35[b];[2]volume=0.25[c];[a][b][c]amix=3,tremolo=f=0.25:d=0.35,"
                            "lowpass=f=1200,volume=0.05,afade=t=in:d=3,afade=t=out:st=%.1f:d=3" % (seconds - 3),
         "-ar", "48000", out])

def srt_time(t):
    h, m = int(t // 3600), int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"

def main():
    vdir, idir = sys.argv[1], sys.argv[2]
    args = sys.argv[3:]
    voice = args[args.index("--voice") + 1] if "--voice" in args else "draft"
    shorts = args[args.index("--shorts") + 1].split(",") if "--shorts" in args else []
    S = json.load(open(os.path.join(vdir, "script.json"), encoding="utf-8"))
    out = os.path.join(vdir, "out"); work = os.path.join(out, "work"); os.makedirs(work, exist_ok=True)
    draft = voice == "draft"
    clips, t, srt, chapters, n = [], 0.0, [], [], 1
    timing = {}
    for i, sc in enumerate(S["scenes"]):
        wav = os.path.join(work, sc["id"] + ".wav")
        if draft: tts(sc["say"], wav)
        else: shutil.copy(os.path.join(voice, sc["id"] + ".wav"), wav)
        secs = dur(wav) + 0.9
        ov = os.path.join(work, sc["id"] + "_ov.png"); overlay(sc, 1920, 1080, draft=draft).save(ov)
        clip = os.path.join(work, f"{i:02d}_{sc['id']}.mp4")
        scene_clip(os.path.join(idir, sc["img"] + ".jpg"), ov, wav, clip, 1920, 1080, secs, i)
        clips.append(clip); timing[sc["id"]] = (t, secs, wav)
        if sc.get("chapter"): chapters.append(f"{int(t // 60)}:{int(t % 60):02d} {sc['chapter']}")
        sents = [x.strip() for x in re.split(r"(?<=[.?!])\s+", sc["say"]) if x.strip()]
        total = sum(len(x) for x in sents); st = t + 0.1
        for x in sents:
            d_ = (secs - 0.9) * len(x) / total
            srt.append(f"{n}\n{srt_time(st)} --> {srt_time(st + d_)}\n{x}\n"); n += 1; st += d_
        t += secs
        print(f"scene {sc['id']:10s} {secs:5.1f}s")
    lst = os.path.join(work, "list.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(c)}'\n" for c in clips))
    joined = os.path.join(work, "joined.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    bed = os.path.join(work, "drone.wav"); drone(t, bed)
    final = os.path.join(out, S["id"] + ".mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined, "-i", bed, "-filter_complex",
         "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-13:TP=-1.5:LRA=11[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", final])
    open(os.path.join(out, S["id"] + ".srt"), "w", encoding="utf-8").write("\n".join(srt))
    open(os.path.join(out, "chapters.txt"), "w", encoding="utf-8").write("\n".join(chapters) + "\n")
    print(f"long video: {final}  {t/60:.1f} min")
    # Shorts
    for sid in shorts:
        sc = next(s for s in S["scenes"] if s["id"] == sid)
        _, secs, wav = timing[sid]
        vs = dict(sc); vs.pop("list", None)
        ov = os.path.join(work, f"short_{sid}_ov.png"); overlay(vs, 1080, 1920, vertical=True, draft=draft).save(ov)
        clip = os.path.join(work, f"short_{sid}_raw.mp4")
        scene_clip(os.path.join(idir, sc["img"] + ".jpg"), ov, wav, clip, 1080, 1920, min(secs, 58), 0, vertical=True)
        bed = os.path.join(work, f"short_{sid}_bed.wav"); drone(min(secs, 58), bed)
        so = os.path.join(out, f"short-{sid}.mp4")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", clip, "-i", bed, "-filter_complex",
             "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-13:TP=-1.5[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", so])
        print(f"short: {so}  {min(secs,58):.1f}s")

if __name__ == "__main__":
    main()
