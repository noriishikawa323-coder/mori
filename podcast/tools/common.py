"""共通ユーティリティ: メタ読み込み / タイムライン読み込み / 音声デコード。"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "podcast" / "script"
AUDIO_DIR = ROOT / "podcast" / "audio"
LINES_DIR = AUDIO_DIR / "lines"


def load_meta(path: Path | None = None) -> dict:
    return json.loads((path or SCRIPT_DIR / "ep001_meta.json").read_text(encoding="utf-8"))


def load_timeline(path: Path | None = None) -> list[dict]:
    src = path or SCRIPT_DIR / "ep001_timeline.jsonl"
    items = []
    for lineno, raw in enumerate(src.read_text(encoding="utf-8").splitlines(), 1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            items.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{src}:{lineno}: 不正なJSON: {exc}") from exc
    return items


def ffmpeg_bin() -> str:
    """静的ffmpegバイナリのパス。imageio-ffmpeg が無ければ PATH 上の ffmpeg。"""
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def decode_audio(path: Path, sample_rate: int, channels: int = 2) -> np.ndarray:
    """任意の音声ファイル(wav/mp3/m4a...)を float32 の (n, channels) 配列で読む。"""
    cmd = [
        ffmpeg_bin(), "-v", "error", "-i", str(path),
        "-f", "f32le", "-acodec", "pcm_f32le",
        "-ar", str(sample_rate), "-ac", str(channels), "-",
    ]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"デコード失敗 {path}: {proc.stderr.decode(errors='replace')[:400]}")
    return np.frombuffer(proc.stdout, dtype="<f4").reshape(-1, channels).copy()


def silence(seconds: float, sample_rate: int, channels: int = 2) -> np.ndarray:
    return np.zeros((max(0, int(round(seconds * sample_rate))), channels), dtype=np.float32)


def line_wav_path(item: dict) -> Path:
    return LINES_DIR / f"{item['id']}_{item['speaker']}.wav"
