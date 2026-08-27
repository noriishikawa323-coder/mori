#!/usr/bin/env python3
"""行ごとのWAVを1本のエピソードに結合し、間・無音・BGM・ラウドネスを仕上げる。

  python3 podcast/tools/build_episode.py
  python3 podcast/tools/build_episode.py --bgm assets/bgm/calm_jazz.mp3
  python3 podcast/tools/build_episode.py --out podcast/audio/podcast_ep001.wav

処理順:
  1. 行WAVを順に連結し、行間に台本指定の間(0.5〜1.0秒)を挿入
  2. SEキューは実ファイルがあれば挿入、無ければ指定尺の無音でタイムラインを維持
  3. 冒頭3秒・末尾5秒の無音を付加
  4. BGMをナレーション音量の15%で重ね、冒頭3秒フェードイン / 末尾5秒フェードアウト
  5. 全体を -16 LUFS に正規化し、トゥルーピーク上限でクリップを防止
  6. 44.1kHz / 16bit の WAV として書き出し、チャプター表も出力
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (AUDIO_DIR, ROOT, decode_audio, line_wav_path,  # noqa: E402
                    load_meta, load_timeline, silence)


def to_stereo(x: np.ndarray) -> np.ndarray:
    if x.ndim == 1:
        return np.repeat(x[:, None], 2, axis=1)
    if x.shape[1] == 1:
        return np.repeat(x, 2, axis=1)
    return x[:, :2]


def voiced_rms(x: np.ndarray, floor_ratio: float = 0.02) -> float:
    """無音区間を除いた実効音量。BGM比率の基準にする。"""
    mono = x.mean(axis=1)
    peak = float(np.max(np.abs(mono))) or 1.0
    voiced = mono[np.abs(mono) > peak * floor_ratio]
    if voiced.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(voiced ** 2)))


def fade(x: np.ndarray, sr: int, fade_in_sec: float, fade_out_sec: float) -> np.ndarray:
    n = len(x)
    y = x.copy()
    n_in = min(int(fade_in_sec * sr), n)
    if n_in > 0:
        y[:n_in] *= np.linspace(0.0, 1.0, n_in, dtype=np.float32)[:, None]
    n_out = min(int(fade_out_sec * sr), n)
    if n_out > 0:
        y[n - n_out:] *= np.linspace(1.0, 0.0, n_out, dtype=np.float32)[:, None]
    return y


def tile_to(x: np.ndarray, n: int) -> np.ndarray:
    if len(x) == 0:
        raise ValueError("BGMが空です")
    reps = int(np.ceil(n / len(x)))
    return np.tile(x, (reps, 1))[:n] if reps > 1 else x[:n]


def build_narration(timeline: list[dict], sr: int, verbose: bool) -> tuple[np.ndarray, list[tuple[float, str]], dict]:
    chunks: list[np.ndarray] = []
    cues: list[tuple[float, str]] = []
    stats = {"lines": 0, "se_real": 0, "se_missing": 0, "missing_lines": []}
    pos = 0  # サンプル数

    def emit(block: np.ndarray) -> None:
        nonlocal pos
        chunks.append(block)
        pos += len(block)

    for item in timeline:
        kind = item["type"]
        if kind == "marker":
            cues.append((pos / sr, item["label"]))
            continue
        if kind == "silence":
            emit(silence(item["sec"], sr))
            continue
        if kind == "se":
            path = ROOT / item["file"]
            if path.exists():
                emit(to_stereo(decode_audio(path, sr)))
                stats["se_real"] += 1
                if verbose:
                    print(f"  SE  {item['id']} <- {item['file']}")
            else:
                emit(silence(item["fallback_sec"], sr))
                stats["se_missing"] += 1
                print(f"  SE  {item['id']} 未配置のため {item['fallback_sec']}秒の無音で代替 "
                      f"({item['file']})")
            emit(silence(item.get("pause", 0.0), sr))
            continue
        if kind == "line":
            path = line_wav_path(item)
            if not path.exists():
                stats["missing_lines"].append(item["id"])
                emit(silence(item.get("pause", 0.0), sr))
                continue
            audio, file_sr = sf.read(path, dtype="float32", always_2d=True)
            if file_sr != sr:
                audio = to_stereo(decode_audio(path, sr))
            else:
                audio = to_stereo(audio)
            emit(audio)
            emit(silence(item.get("pause", 0.0), sr))
            stats["lines"] += 1

    return np.concatenate(chunks) if chunks else silence(0, sr), cues, stats


def main() -> int:
    ap = argparse.ArgumentParser(description="エピソード音声をビルドする")
    ap.add_argument("--out", default="podcast/audio/podcast_ep001.wav")
    ap.add_argument("--bgm", default="", help="BGMファイル。省略するとBGM無しで書き出す")
    ap.add_argument("--bgm-ratio", type=float, default=None, help="ナレーション音量に対するBGM比率")
    ap.add_argument("--lufs", type=float, default=None, help="目標ラウドネス (既定 -16)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    meta = load_meta()
    m = meta["master"]
    sr = m["sample_rate"]
    target_lufs = args.lufs if args.lufs is not None else m["target_lufs"]
    bgm_ratio = args.bgm_ratio if args.bgm_ratio is not None else m["bgm_level_ratio"]

    print("== 1. 行WAVを連結し、行間の間を挿入 ==")
    narration, cues, stats = build_narration(load_timeline(), sr, args.verbose)
    if stats["missing_lines"]:
        miss = stats["missing_lines"]
        print(f"\n!! 行WAVが {len(miss)} 本ありません (先頭: {', '.join(miss[:8])})")
        print("   先に synthesize.py を実行してください。中断します。")
        return 1
    print(f"   セリフ {stats['lines']} 行 / SE 実ファイル {stats['se_real']} ・無音代替 {stats['se_missing']}")

    print("== 2. 冒頭3秒・末尾5秒の無音を付加 ==")
    lead_in, tail = m["lead_in_sec"], m["tail_sec"]
    master = np.concatenate([silence(lead_in, sr), narration, silence(tail, sr)])
    cues = [(0.0, "00_リードイン")] + [(t + lead_in, label) for t, label in cues]

    if args.bgm:
        bgm_path = Path(args.bgm)
        if not bgm_path.is_absolute():
            bgm_path = ROOT / bgm_path
        if not bgm_path.exists():
            print(f"!! BGMが見つかりません: {bgm_path} — BGM無しで続行します")
        else:
            print(f"== 3. BGMを合成 ({bgm_path.name}, ナレーション比 {bgm_ratio:.0%}) ==")
            bgm = tile_to(to_stereo(decode_audio(bgm_path, sr)), len(master))
            base = voiced_rms(master)
            bgm_rms = float(np.sqrt(np.mean(bgm ** 2))) or 1.0
            bgm *= (base * bgm_ratio) / bgm_rms
            master = master + fade(bgm, sr, m["bgm_fade_in_sec"], m["bgm_fade_out_sec"])
    else:
        print("== 3. BGM指定なし — ナレーションのみで書き出します ==")

    print(f"== 4. ラウドネスを {target_lufs} LUFS に正規化 ==")
    meter = pyln.Meter(sr)
    before = meter.integrated_loudness(master)
    master = pyln.normalize.loudness(master, before, target_lufs)

    ceiling = 10 ** (m["true_peak_ceiling_db"] / 20.0)
    peak = float(np.max(np.abs(master)))
    if peak > ceiling:
        master *= ceiling / peak
        print(f"   ピーク {20*np.log10(peak):.2f} dBFS -> {m['true_peak_ceiling_db']:.1f} dBFS に抑制")
    after = meter.integrated_loudness(master)

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"== 5. 書き出し: {out} ==")
    sf.write(out, master, sr, subtype="PCM_16")

    cue_path = out.with_name(out.stem + "_cues.txt")
    with cue_path.open("w", encoding="utf-8") as fh:
        for t, label in cues:
            fh.write(f"{int(t)//60:02d}:{int(t)%60:02d}\t{label}\n")

    dur = len(master) / sr
    print(f"\n   尺        : {int(dur)//60}分{dur % 60:04.1f}秒")
    print(f"   形式      : {sr} Hz / 16bit / {master.shape[1]}ch")
    print(f"   ラウドネス: {before:.2f} -> {after:.2f} LUFS (目標 {target_lufs})")
    print(f"   ピーク    : {20*np.log10(max(float(np.max(np.abs(master))), 1e-9)):.2f} dBFS")
    print(f"   チャプター: {cue_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
