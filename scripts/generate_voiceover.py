#!/usr/bin/env python3
"""
Generates American English neural voiceover tracks and subtitle timings for the
Ternary CNFET Educational Video using edge-tts and ffprobe.
"""

import os
import json
import subprocess

VIDEO_DIR = "/home/robson/coding/ternary-cnfet-3d/video"
AUDIO_DIR = os.path.join(VIDEO_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

VOICE = "en-US-ChristopherNeural"

SCENES = [
    {
        "id": "scene_01_anatomy",
        "title": "1. Gate-All-Around CNFET Architecture",
        "formula": "Si / SiO2 Substrate  |  Pd/Au Contacts  |  HfO2 High-k (IOR 1.90)",
        "narration": (
            "In a Carbon Nanotube Field-Effect Transistor, semiconducting single-walled carbon nanotubes "
            "bridge Palladium and Gold source and drain contacts over a silicon dioxide substrate. "
            "A coaxial Gate-All-Around stack of hafnium oxide and metal surrounds each nanotube channel."
        ),
    },
    {
        "id": "scene_02_chirality",
        "title": "2. Chiral Diameter & Threshold Voltage Modulation",
        "formula": "d_CNT = 0.0783 * n (nm)   |   Eg = 0.84 eV / d_CNT   |   Vth = 0.43 V / d_CNT",
        "narration": (
            "The threshold voltage is inversely proportional to the nanotube diameter. "
            "The front wide thirteen-zero nanotube measures one point zero two nanometers across, yielding a low threshold of zero point four two volts. "
            "The rear narrow seven-zero nanotube measures zero point five five nanometers, producing a high threshold of zero point seven eight volts."
        ),
    },
    {
        "id": "scene_03_state_minus1",
        "title": "3. Balanced Ternary State -1 (Vgs < 0.42 V)",
        "formula": "STATE -1:  Vgs < Vth1 < Vth2   |   CH1 (13,0): OFF   |   CH2 (7,0): OFF",
        "narration": (
            "In balanced ternary state minus one, the gate voltage remains below zero point four two volts. "
            "Both conduction band barriers, E C one and E C two, stay elevated, blocking electron injection into both channels."
        ),
    },
    {
        "id": "scene_04_state_0",
        "title": "4. Balanced Ternary State 0 (0.42 V <= Vgs < 0.78 V)",
        "formula": "STATE 0:  Vth1 <= Vgs < Vth2   |   CH1 (13,0): BALLISTIC ON   |   CH2 (7,0): OFF",
        "narration": (
            "In balanced ternary state zero, the gate voltage reaches the intermediate window between zero point four two and zero point seven eight volts. "
            "The cyan barrier E C one drops, triggering ballistic electron transport through the wide nanotube, while the high pink barrier E C two keeps the narrow nanotube switched off."
        ),
    },
    {
        "id": "scene_05_state_plus1",
        "title": "5. Balanced Ternary State +1 (Vgs >= 0.78 V)",
        "formula": "STATE +1:  Vgs >= Vth2 > Vth1   |   CH1 (13,0): ON   |   CH2 (7,0): BALLISTIC ON",
        "narration": (
            "In balanced ternary state plus one, the gate voltage exceeds zero point seven eight volts. "
            "Both potential barriers drop below the source Fermi level, enabling simultaneous ballistic conduction across both carbon nanotubes."
        ),
    },
]


def get_duration(filepath):
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filepath,
        ],
        text=True,
    ).strip()
    return float(out)


def main():
    manifest = []
    for sc in SCENES:
        mp3_path = os.path.join(AUDIO_DIR, f"{sc['id']}.mp3")
        vtt_path = os.path.join(AUDIO_DIR, f"{sc['id']}.vtt")
        subprocess.run(
            [
                "/home/robson/.local/bin/edge-tts",
                "--voice",
                VOICE,
                "--text",
                sc["narration"],
                "--write-media",
                mp3_path,
                "--write-subtitles",
                vtt_path,
            ],
            check=True,
        )
        dur = get_duration(mp3_path)
        sc_info = dict(sc)
        sc_info["audio_path"] = mp3_path
        sc_info["vtt_path"] = vtt_path
        sc_info["duration_sec"] = round(dur, 3)
        manifest.append(sc_info)
        print(f"Generated {sc['id']}: {dur:.2f}s")

    manifest_path = os.path.join(VIDEO_DIR, "scenes_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved manifest to {manifest_path}")


if __name__ == "__main__":
    main()
