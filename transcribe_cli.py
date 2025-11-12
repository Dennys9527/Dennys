"""Command-line utility for transcribing meeting recordings into timestamped captions.

This script uses the `faster-whisper` implementation of OpenAI's Whisper ASR model,
which provides strong accuracy with zero per-minute API cost (open-source weights,
local compute required). Segment text can optionally be machine-translated to
Simplified Chinese, Traditional Chinese, or English via `googletrans`.

Usage example:
    python transcribe_cli.py path/to/audio.mp3 --format srt --output-language zh-cn
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Dict, Optional

from faster_whisper import WhisperModel
from googletrans import Translator


OUTPUT_LANGUAGE_CHOICES = {
    "auto": None,
    "zh-cn": "zh-cn",
    "zh-tw": "zh-tw",
    "en": "en",
}

LANGUAGE_ALIASES = {
    "zh": "zh-cn",
    "zh-cn": "zh-cn",
    "zh-tw": "zh-tw",
    "en": "en",
}


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe meeting recordings and export SRT/VTT subtitles."
    )
    parser.add_argument("audio", type=Path, help="Path to the audio file (mp3, wav, etc.)")
    parser.add_argument(
        "--model",
        default="medium",
        help="Whisper model size to load (tiny, base, small, medium, large-v2, etc.).",
    )
    parser.add_argument(
        "--language",
        default="auto",
        help="Language code for transcription (e.g. en, zh). Use 'auto' to detect automatically.",
    )
    parser.add_argument(
        "--output-language",
        choices=OUTPUT_LANGUAGE_CHOICES.keys(),
        default="auto",
        help="Target language for subtitles (auto keeps original, zh-cn, zh-tw, en).",
    )
    parser.add_argument(
        "--format",
        choices=("srt", "vtt"),
        default="srt",
        help="Subtitle export format.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Destination path for the subtitle file. Defaults to audio filename with .srt/.vtt",
    )
    parser.add_argument(
        "--device",
        choices=("cpu", "cuda"),
        default="cpu",
        help="Device for running Whisper (cpu or cuda).",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5,
        help="Beam size for decoding (larger improves accuracy at higher compute cost).",
    )
    parser.add_argument(
        "--compute-type",
        default="int8_float16",
        help="Computation type for faster-whisper (e.g. int8, int8_float16, float16).",
    )
    return parser.parse_args(argv)


def format_timestamp(seconds: float, separator: str) -> str:
    total_milliseconds = int(round(seconds * 1000))
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{milliseconds:03d}"


def segments_to_srt(segments: Iterable[Dict[str, str]]) -> str:
    lines: List[str] = []
    for idx, seg in enumerate(segments, start=1):
        lines.append(str(idx))
        start = format_timestamp(seg["start"], ",")
        end = format_timestamp(seg["end"], ",")
        lines.append(f"{start} --> {end}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines)


def segments_to_vtt(segments: Iterable[Dict[str, str]]) -> str:
    lines: List[str] = ["WEBVTT", ""]
    for seg in segments:
        start = format_timestamp(seg["start"], ".")
        end = format_timestamp(seg["end"], ".")
        lines.append(f"{start} --> {end}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines)


def normalize_language_code(code: Optional[str]) -> Optional[str]:
    if code is None:
        return None
    code = code.lower()
    return LANGUAGE_ALIASES.get(code, code)


def maybe_translate_segments(
    segments: List[Dict[str, str]],
    detected_language: Optional[str],
    target_language: Optional[str],
) -> None:
    if not target_language:
        return

    detected_language = normalize_language_code(detected_language)
    if detected_language == target_language:
        return

    translator = Translator()
    for seg in segments:
        translated = translator.translate(
            seg["text"],
            dest=target_language,
            src=detected_language or "auto",
        )
        seg["text"] = translated.text


def build_segments(
    model: WhisperModel,
    audio_path: Path,
    language: Optional[str],
    beam_size: int,
) -> (List[Dict[str, str]], str):
    segments_iter, info = model.transcribe(
        str(audio_path),
        beam_size=beam_size,
        language=language,
        vad_filter=True,
    )

    collected: List[Dict[str, str]] = []
    for segment in segments_iter:
        collected.append(
            {
                "id": segment.id,
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
            }
        )
    return collected, info.language


def export_subtitles(segments: List[Dict[str, str]], fmt: str) -> str:
    if fmt == "srt":
        return segments_to_srt(segments)
    if fmt == "vtt":
        return segments_to_vtt(segments)
    raise ValueError(f"Unsupported subtitle format: {fmt}")


def resolve_output_path(audio_path: Path, output: Optional[Path], fmt: str) -> Path:
    if output is not None:
        return output
    suffix = f".{fmt}"
    return audio_path.with_suffix(suffix)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    audio_path: Path = args.audio
    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}", file=sys.stderr)
        return 1

    target_language = OUTPUT_LANGUAGE_CHOICES[args.output_language]
    language = None if args.language.lower() == "auto" else args.language

    print("Loading Whisper model ...", file=sys.stderr)
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)

    print("Transcribing audio ...", file=sys.stderr)
    segments, detected_language = build_segments(
        model=model,
        audio_path=audio_path,
        language=language,
        beam_size=args.beam_size,
    )

    print(f"Detected language: {detected_language}", file=sys.stderr)

    maybe_translate_segments(segments, detected_language, target_language)

    subtitle_text = export_subtitles(segments, args.format)

    output_path = resolve_output_path(audio_path, args.output, args.format)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(subtitle_text, encoding="utf-8")

    print(f"Subtitles written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
