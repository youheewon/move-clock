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
import wave

import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "voices"
PHRASES = BASE / "phrases.json"
MANIFEST = BASE / "manifest.json"
PROFILES = {"female": "F1", "male": "M1"}
VOICE_REVISION = "energetic-2"
MALE_REVISION = "m1-clarity-1"
ANNOUNCEMENTS = {
    "휴식 시작": "휴식!",
    "운동 시작": "운동 시작!",
    "운동 완료": "운동 완료!",
}


def spoken_text(phrase: str) -> str:
    if phrase in SPOKEN_NUMBERS:
        return SPOKEN_NUMBERS[phrase]
    if phrase in ANNOUNCEMENTS:
        return ANNOUNCEMENTS[phrase]
    if phrase.endswith(" 시작"):
        return f"{phrase[:-3]}! 시작!"
    return phrase
SPOKEN_NUMBERS = {"5": "다섯", "4": "넷", "3": "셋", "2": "둘", "1": "하나"}


def filename(text: str, profile: str) -> str:
    revision = VOICE_REVISION + (":" + MALE_REVISION if profile == "male" else "")
    return hashlib.sha256((revision + ":" + text).encode("utf-8")).hexdigest()[:14] + ".wav"


def signal_stats(path: Path) -> tuple[float, float]:
    """Catch Supertonic outputs that have a WAV header but silent PCM."""
    if not path.is_file() or path.stat().st_size < 1024:
        return 0.0, 0.0
    try:
        with wave.open(str(path), "rb") as src:
            if src.getsampwidth() != 2:
                return 0.0, 0.0
            channels = src.getnchannels()
            pcm = np.frombuffer(src.readframes(src.getnframes()), dtype="<i2").astype(np.float32) / 32768.0
        if channels > 1:
            pcm = pcm.reshape(-1, channels).mean(axis=1)
        return float(np.max(np.abs(pcm))), float(np.sqrt(np.mean(np.square(pcm))))
    except (OSError, EOFError, ValueError):
        return 0.0, 0.0


def audible(path: Path) -> bool:
    peak, rms = signal_stats(path)
    return peak >= 0.02 and rms >= 0.002



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
        "voice_revision": VOICE_REVISION,
        "male_revision": MALE_REVISION,
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
            wav_path = output_dir / filename(phrase, profile)
            if not audible(wav_path):
                spoken = spoken_text(phrase)
                # The M1 voice sometimes produces an almost entirely silent
                # WAV for a short Korean word, despite a normal file size.
                # Retry with independent samples, and reject invalid audio.
                variants = [spoken] * 4
                if phrase == "1":
                    variants = ["하나!", "하나.", "하나!", "하나."]
                for attempt, wording in enumerate(variants, start=1):
                    wav, _ = tts.synthesize(
                        text=wording,
                        voice_style=style,
                        lang="ko",
                        total_steps=12,
                        speed=1.12 if profile == "male" else 1.24,
                        silence_duration=0.3,
                        verbose=False,
                    )
                    tts.save_audio(wav, str(wav_path))
                    if audible(wav_path):
                        if attempt > 1:
                            print(f"  [retry] {profile} {phrase}: usable take on attempt {attempt}", flush=True)
                        break
                    print(f"  [rejected silent clip] {profile} {phrase} (attempt {attempt})", flush=True)
                else:
                    raise RuntimeError(f"Could not generate audible {profile} voice: {phrase}")
            mapping[phrase] = f"./voices/{profile}/{wav_path.name}"
            peak, rms = signal_stats(wav_path)
            print(f"  {pos:02}/{len(phrases)} {phrase} peak={peak:.3f} rms={rms:.3f}", flush=True)
        valid_names = {filename(phrase, profile) for phrase in phrases}
        for outdated in output_dir.glob("*.wav"):
            if outdated.name not in valid_names:
                outdated.unlink()
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
