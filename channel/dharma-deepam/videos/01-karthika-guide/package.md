# Video 01 – upload package

**Publish:** Sunday 8 Nov 2026, 18:30 IST (Premiere optional) · Channel: ధర్మ దీపం · Playlist: కార్తీక మాసం 2026

## Title (yt-package: 98/100, 48 chars, fits desktop; mobile shows "కార్తీక మాసం 2026: 29 రోజుల్లో ఏ రోజు…", subject survives)

కార్తీక మాసం 2026: 29 రోజుల్లో ఏ రోజు ఏం చేయాలి?

Runner-up (A/B with YouTube "Test & compare"): కార్తీక మాసం 2026 | ఇంట్లోనే 5 ఆచారాలు, 8 తేదీలు

## Thumbnail (pairing score 100/100 — does not repeat the title)

`out/thumbnail.jpg` — ghat painting, right side: **రోజూ / ఒక దీపం**, small line కార్తీకం 2026.

## Description

కార్తీక మాసం 2026 మంగళవారం, నవంబర్ 10 నుండి మంగళవారం, డిసెంబర్ 8 వరకు (హైదరాబాద్ పంచాంగం).
ఇంట్లోనే, అపార్ట్‌మెంట్‌లో ఉన్నా, విదేశాల్లో ఉన్నా పాటించగల 5 ఆచారాలు, 8 ముఖ్యమైన తేదీలు.

📅 కార్తీకం 2026 తేదీలు
• మంగళ 10 నవం – కార్తీక మాసం ప్రారంభం
• శుక్ర 13 నవం – నాగుల చవితి
• సోమ 16, 23, 30 నవం, 7 డిసెం – కార్తీక సోమవారాలు
• 20 / 21 నవం – ఉత్థాన ఏకాదశి (మీ పంచాంగం చూడండి)
• శని 21 నవం – క్షీరాబ్ది ద్వాదశి
• మంగళ 24 నవం – కార్తీక పౌర్ణమి, జ్వాలా తోరణం
• మంగళ 8 డిసెం – కార్తీక అమావాస్య

{CHAPTERS — paste out/chapters.txt here}

తేదీలు హైదరాబాద్ (IST) పంచాంగం ప్రకారం. మీ ఊరిలో లేదా కుటుంబ సంప్రదాయంలో తేడా ఉంటే మీ పురోహితులు చెప్పినట్లే చేయండి.
చిత్రాలు: ఈ ఛానల్ కోసం రూపొందించిన చిత్రకళ.

🪔 ఈ రోజు దీపం వెలిగించారా? కామెంట్‌లో మీ ఊరి పేరు రాయండి.

#కార్తీకమాసం #KarthikaMasam2026 #ధర్మదీపం

## The three searches this should win (yt-seo)

1. కార్తీక మాసం 2026 తేదీలు / karthika masam 2026 dates
2. karthika masam 2026 start date telugu
3. కార్తీక సోమవారాలు 2026

Tags barely matter; add only: కార్తీక మాసం 2026, karthika masam 2026, karthika masam telugu, కార్తీక సోమవారం, కార్తీక పౌర్ణమి 2026.

## Upload settings

- Audience: **No, not made for kids**
- Altered or synthetic content: the paintings are clearly non-realistic art (no disclosure needed). **If the draft synthetic voice is ever kept, answer Yes** — but replace it with a human voiceover (see below).
- Subtitles: upload `out/01-karthika-guide.srt` (Telugu)
- Category: Education (or Nonprofits & Activism), language Telugu, location India
- End screen: video 02 / Karthika Somavaram anchor + subscribe element (no spoken subscribe ask)
- Pinned comment: "🪔 ఈ రోజు మీ ఇంట్లో దీపం వెలిగించారా? మీ ఊరి పేరు రాయండి — 24 నవంబర్ కార్తీక పౌర్ణమి వీడియో త్వరలో."

## Replacing the draft voice (must do before upload)

1. Read each scene's `say` line from `script.json` into your phone, one file per scene, named `<scene id>.wav`
   (hook.wav, turn.wav, why.wav, p1.wav … close.wav). A quiet room with soft furnishings is enough.
2. Put them in a folder, e.g. `Videos/DharmaDeepam/01-karthika-guide/voice/`.
3. Re-render: `python3 channel/tools/render.py channel/dharma-deepam/videos/01-karthika-guide <img folder> --voice <voice folder> --shorts pournami,p2,p1`
   The text timing, subtitles and chapters re-time to your voice automatically, and the "draft voice" label disappears.

**Ship it, or change it?**
