#!/usr/bin/env python3
"""台本タイムラインを1行ずつ VOICEVOX で音声合成する。

  python3 podcast/tools/synthesize.py                    # 差分のみ合成
  python3 podcast/tools/synthesize.py --force            # 全行を再合成
  python3 podcast/tools/synthesize.py --only 0043,0044   # 指定IDだけ
  python3 podcast/tools/synthesize.py --mock             # エンジン無しの疎通確認(無音生成)

VOICEVOX エンジンを先に起動しておくこと (既定 http://127.0.0.1:50021)。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import LINES_DIR, load_meta, load_timeline, line_wav_path  # noqa: E402

# 感情プリセットで上書きしない audio_query のキーは VOICEVOX の既定値をそのまま使う
PRESET_KEYS = ("speedScale", "pitchScale", "intonationScale", "volumeScale")


def _post(url: str, payload: bytes | None, timeout: float) -> bytes:
    req = urllib.request.Request(url, data=payload, method="POST")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read()


def check_engine(base: str, timeout: float = 5.0) -> str:
    try:
        with urllib.request.urlopen(f"{base}/version", timeout=timeout) as res:
            return res.read().decode().strip().strip('"')
    except (urllib.error.URLError, OSError) as exc:
        raise SystemExit(
            f"VOICEVOX エンジンに接続できません ({base}): {exc}\n"
            "エンジンを起動してから再実行するか、--mock で疎通確認のみ行ってください。"
        ) from exc


def synth_line(base: str, text: str, speaker_id: int, preset: dict,
               sample_rate: int, timeout: float, retries: int = 3) -> bytes:
    """audio_query -> パラメータ上書き -> synthesis。WAVバイト列を返す。"""
    qs = urllib.parse.urlencode({"text": text, "speaker": speaker_id})
    last: Exception | None = None
    for attempt in range(retries):
        try:
            query = json.loads(_post(f"{base}/audio_query?{qs}", None, timeout))
            for key in PRESET_KEYS:
                if key in preset:
                    query[key] = preset[key]
            # 行間の無音は結合側で管理するので、エンジン側の前後無音は最小にする
            query["prePhonemeLength"] = 0.0
            query["postPhonemeLength"] = 0.0
            query["outputSamplingRate"] = sample_rate
            query["outputStereo"] = False
            body = json.dumps(query, ensure_ascii=False).encode("utf-8")
            return _post(f"{base}/synthesis?speaker={speaker_id}", body, timeout)
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
            last = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"合成に失敗しました: {last}")


def mock_wav(text: str, preset: dict, sample_rate: int, speaker_key: str) -> bytes:
    """エンジン非依存のプレビュー音。

    話速から尺を推定し、話者ごとに高さの違うモールス信号のような音を返す。
    本合成の前に、間の取り方とテンポだけを耳で確認するために使う。
    """
    import io

    # 日本語のおおよその発話速度 ~7.5 モーラ/秒 を基準に、speedScale で割る
    speed = preset.get("speedScale", 1.0)
    seconds = max(0.35, len(text) / 7.5 / speed)
    n = int(seconds * sample_rate)
    t = np.arange(n, dtype=np.float32) / sample_rate

    freq = 220.0 if speaker_key == "HAYASHI" else 330.0
    freq *= 1.0 + preset.get("pitchScale", 0.0) * 4.0
    # モーラのリズムを模した振幅変調で、テンポが耳で分かるようにする
    mora = 7.5 * speed
    env = (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * mora * t))).astype(np.float32)
    env *= np.minimum(1.0, np.minimum(t, seconds - t) * 40.0).astype(np.float32)
    wave = (0.12 * env * np.sin(2 * np.pi * freq * t)).astype(np.float32)

    buf = io.BytesIO()
    sf.write(buf, wave, sample_rate, subtype="PCM_16", format="WAV")
    return buf.getvalue()


def resolve_casting(meta: dict, name: str) -> dict:
    """キャスティングプリセットを話者割り当てに解決する。"""
    presets = meta.get("casting_presets", {})
    key = name or meta.get("default_casting", "")
    if not key:
        return meta["speakers"]
    if key not in presets:
        raise SystemExit(
            f"未定義のキャスティング '{key}'。選べるのは: {', '.join(presets) or '(なし)'}"
        )
    preset = presets[key]
    print(f"キャスティング: {preset.get('label', key)}")
    merged = {}
    for role, base in meta["speakers"].items():
        merged[role] = {**base, **{k: v for k, v in preset.get(role, {}).items()}}
        print(f"  {role:8s} -> speaker_id={merged[role]['voicevox_speaker_id']} "
              f"({merged[role]['voicevox_name']})")
    return merged


def main() -> int:
    ap = argparse.ArgumentParser(description="VOICEVOX で台本を1行ずつ合成する")
    ap.add_argument("--engine", default="http://127.0.0.1:50021", help="VOICEVOX エンジンのURL")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--force", action="store_true", help="既存の行WAVも作り直す")
    ap.add_argument("--only", default="", help="合成する行IDをカンマ区切りで指定")
    ap.add_argument("--casting", default="",
                    help="キャスティングプリセット名 (未指定なら meta の default_casting)")
    ap.add_argument("--mock", action="store_true",
                    help="エンジンを使わず、尺とテンポだけのプレビュー音を生成する")
    args = ap.parse_args()

    meta = load_meta()
    timeline = load_timeline()
    sample_rate = meta["master"]["sample_rate"]
    speakers = resolve_casting(meta, args.casting)
    presets = meta["emotion_presets"]
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    base = args.engine.rstrip("/")
    if args.mock:
        print("[mock] VOICEVOX を呼ばず、テンポ確認用のプレビュー音を書き出します")
    else:
        print(f"VOICEVOX エンジン接続OK (version {check_engine(base, args.timeout)})")

    LINES_DIR.mkdir(parents=True, exist_ok=True)
    lines = [it for it in timeline if it["type"] == "line"]
    done = skipped = 0

    for idx, item in enumerate(lines, 1):
        if only and item["id"] not in only:
            continue
        out = line_wav_path(item)
        if out.exists() and not args.force:
            skipped += 1
            continue

        speaker = speakers.get(item["speaker"])
        if speaker is None:
            raise SystemExit(f"{item['id']}: 未定義の話者 {item['speaker']}")
        preset = presets.get(item["emotion"])
        if preset is None:
            raise SystemExit(f"{item['id']}: 未定義の感情プリセット {item['emotion']}")

        sid = speaker["voicevox_speaker_id"]
        if args.mock:
            wav = mock_wav(item["text"], preset, sample_rate, item["speaker"])
        else:
            wav = synth_line(base, item["text"], sid, preset, sample_rate, args.timeout)
        out.write_bytes(wav)
        done += 1
        print(f"  [{idx:3d}/{len(lines)}] {item['id']} {item['speaker']:8s} "
              f"{item['emotion']:10s} speaker={sid} {item['text'][:26]}")

    print(f"\n合成完了: 新規 {done} 行 / スキップ {skipped} 行 -> {LINES_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
