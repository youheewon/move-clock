#!/usr/bin/env python3
"""Generate both Supertonic 3 Korean voice packs for MOVE CLOCK.

Run from repository root:
  python -m pip install supertonic
  python generate_supertonic.py

This downloads the Supertonic 3 model temporarily (around 400 MB). Only
short generated WAV files and their manifest are committed/deployed.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "voices"
PHRASES = BASE / "phrases.json"
MANIFEST = BASE / "manifest.json"
PROFILES = {"female": "F1", "male": "M1"}
SPOKEN_NUMBERS = {"5": "다섯", "4": "넷", "3": "셋", "2": "둘", "1": "하나"}


def filename(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:14] + ".wav"


def main() -> int:
    try:
        from supertonic import TTS
    except ImportError:
        print("Install the Supertonic package first: pip install supertonic", file=sys.stderr)
        return 1

    catalog = json.loads(PHRASES.read_text(encoding="utf-8"))
    phrases = list(dict.fromkeys(
        catalog["shared"] + [name + " 시작" for name in catalog["exercise_names"]]
    ))
    print(f"Preparing {len(phrases)} phrases per voice, {len(phrases) * 2} clips total.", flush=True)
    tts = TTS(model="supertonic-3", auto_download=True)
    result = {
        "generated": True,
        "engine": "Supertonic 3",
        "profiles": PROFILES,
        "voices": {},
    }

    for profile, style_name in PROFILES.items():
        print(f"Generating {profile} / {style_name}...", flush=True)
        style = tts.get_voice_style(voice_name=style_name)
        output_dir = BASE / profile
        output_dir.mkdir(parents=True, exist_ok=True)
        mapping = {}
        for pos, phrase in enumerate(phrases, start=1):
            wav_path = output_dir / filename(phrase)
            if not wav_path.is_file() or wav_path.stat().st_size < 100:
                wav, _ = tts.synthesize(
                    text=SPOKEN_NUMBERS.get(phrase, phrase),
                    voice_style=style,
                    lang="ko",
                    total_steps=8,
                    speed=1.18,
                    silence_duration=0.02,
                    verbose=False,
                )
                tts.save_audio(wav, str(wav_path))
            if not wav_path.is_file() or wav_path.stat().st_size <= 100:
                raise RuntimeError(f"Missing or empty clip: {wav_path}")
            mapping[phrase] = f"./voices/{profile}/{wav_path.name}"
            print(f"  {pos:02}/{len(phrases)} {phrase}", flush=True)
        result["voices"][profile] = mapping

    if any(len(result["voices"][p]) != len(phrases) for p in PROFILES):
        raise RuntimeError("Both profiles must be complete.")
    MANIFEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Both voice packs are complete.", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"Voice generation failed: {e}", file=sys.stderr)
        raise
