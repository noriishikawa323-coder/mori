#!/usr/bin/env python3
"""実演コーナーのSE(擬音・オルゴール)を生成する。

  python3 podcast/tools/make_se.py

assets/se/ に SE01〜SE03 を書き出す。定位・間隔は ep001_production_notes.md の
仕様に合わせてある。数値を触って詰め直せるように、全パラメータを定数にしてある。
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT  # noqa: E402

SR = 44100
SE_DIR = ROOT / "assets" / "se"

PAN_RATIO = 0.35   # 遠い側のゲイン。1.0で中央、0.0で振り切り。0.35 ≒ パン65%
ITD_MS = 0.4       # 遠い側を遅らせる時間差。振り切らずに方向感を出す
CHIRP_SEC = 0.20   # 「ピヨ」1回の長さ


def _env(n: int, attack: float = 0.012, release: float = 0.10) -> np.ndarray:
    """立ち上がりの速い包絡。方向定位は音の立ち上がりで決まるので鋭くする。"""
    t = np.arange(n) / SR
    a = np.minimum(1.0, t / attack)
    r = np.exp(-np.maximum(0.0, t - attack) / release)
    return (a * r).astype(np.float32)


def chirp(f_start: float, f_end: float, seconds: float = CHIRP_SEC) -> np.ndarray:
    """「ピヨ」1回。周波数が下がる短い笛音に、2倍音を薄く足す。"""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    freq = f_start + (f_end - f_start) * (t / seconds) ** 0.7
    phase = 2 * np.pi * np.cumsum(freq) / SR
    tone = np.sin(phase) + 0.28 * np.sin(2 * phase) + 0.08 * np.sin(3 * phase)
    return (tone * _env(n) * 0.55).astype(np.float32)


def piyo() -> np.ndarray:
    return chirp(2650, 1850)


def piyo_piyo() -> np.ndarray:
    """「ピヨピヨ」。0.25秒間隔で2回。子鳥側なのでわずかに高く。"""
    gap = np.zeros(int(0.25 * SR), dtype=np.float32)
    one = chirp(2800, 1980)
    return np.concatenate([one, gap, one])


def reverb(mono: np.ndarray, decay: float = 0.22, mix: float = 0.22,
           seed: int = 0) -> np.ndarray:
    """屋外の遠さを作る浅いリバーブ。指数減衰ノイズとの畳み込み。"""
    rng = np.random.default_rng(seed)
    n = int(decay * SR)
    ir = (rng.standard_normal(n) * np.exp(-np.arange(n) / (decay * SR / 4))).astype(np.float32)
    ir[0] = 1.0
    ir /= np.abs(ir).sum()
    wet = np.convolve(mono, ir)[: len(mono)]
    return ((1 - mix) * mono + mix * wet * 3.0).astype(np.float32)


def place(mono: np.ndarray, side: str, total_sec: float, at_sec: float,
          seed: int = 0) -> np.ndarray:
    """モノラル素材を、指定時刻・指定の左右位置でステレオ上に置く。"""
    out = np.zeros((int(total_sec * SR), 2), dtype=np.float32)
    wet = reverb(mono, seed=seed)
    start = int(at_sec * SR)
    itd = int(ITD_MS / 1000 * SR)

    near_gain, far_gain = 1.0, PAN_RATIO
    near, far = (0, 1) if side == "L" else (1, 0)

    end = min(len(out), start + len(wet))
    out[start:end, near] += wet[: end - start] * near_gain
    s2, e2 = start + itd, min(len(out), start + itd + len(wet))
    out[s2:e2, far] += wet[: e2 - s2] * far_gain
    return out


def build_se01() -> np.ndarray:
    """ピヨ×3 / 左chのみ / 間隔1.2秒 / 5秒。"""
    total = 5.0
    out = np.zeros((int(total * SR), 2), dtype=np.float32)
    for i, at in enumerate((0.45, 1.65, 2.85)):
        out += place(piyo(), "L", total, at, seed=i)
    return out


def build_se02() -> np.ndarray:
    """ピヨ(左) →0.8秒→ ピヨピヨ(右) を2往復 / 7秒。この0.8秒が命。"""
    total, out = 7.0, np.zeros((int(7.0 * SR), 2), dtype=np.float32)
    t = 0.5
    for cycle in range(2):
        out += place(piyo(), "L", total, t, seed=cycle * 2)
        out += place(piyo_piyo(), "R", total, t + 0.8, seed=cycle * 2 + 1)
        t += 0.8 + 1.9   # 次の往復まで
    return out


def build_se03() -> np.ndarray:
    """オルゴール風メロディ / 左右ほぼ均等・ステレオ幅広め / 8秒。

    「どっちから鳴っているか分からない」を体験させるパートなので、
    定位を作らず、左右を薄くずらして広がりだけを出す。
    """
    total = 8.0
    n = int(total * SR)
    mono = np.zeros(n, dtype=np.float32)
    # 通りゃんせを流用せず、同じ気配のヨナ抜き音階で書いた自作フレーズ
    scale = {"D4": 293.66, "E4": 329.63, "G4": 392.00, "A4": 440.00,
             "B4": 493.88, "D5": 587.33, "E5": 659.25}
    phrase = [("A4", 0.0), ("A4", 0.55), ("B4", 1.1), ("D5", 1.65), ("B4", 2.2),
              ("A4", 2.75), ("G4", 3.4), ("E4", 3.95), ("G4", 4.5), ("A4", 5.05),
              ("B4", 5.6), ("A4", 6.15), ("E4", 6.8)]
    for name, at in phrase:
        f = scale[name]
        ln = int(1.1 * SR)
        t = np.arange(ln) / SR
        # オルゴールの倍音構成: 基音 + 高次倍音が速く減衰する
        note = (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.45)
                + 0.35 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / 0.20)
                + 0.18 * np.sin(2 * np.pi * f * 4.2 * t) * np.exp(-t / 0.08))
        start = int(at * SR)
        end = min(n, start + ln)
        mono[start:end] += (note[: end - start] * 0.30).astype(np.float32)

    # 左右で違うリバーブをかけ、片側をわずかに遅らせて定位を溶かす
    left = reverb(mono, decay=0.45, mix=0.40, seed=11)
    right = reverb(mono, decay=0.45, mix=0.40, seed=22)
    shift = int(0.011 * SR)
    right = np.concatenate([np.zeros(shift, dtype=np.float32), right])[:n]
    return np.stack([left, right], axis=1)


def main() -> int:
    SE_DIR.mkdir(parents=True, exist_ok=True)
    targets = {
        "se01_piyo_left.wav": build_se01(),
        "se02_nakikawashi.wav": build_se02(),
        "se03_melody.wav": build_se03(),
    }
    for name, audio in targets.items():
        peak = float(np.max(np.abs(audio)))
        if peak > 0:
            audio = audio / peak * 0.85   # ヘッドルームを残す
        path = SE_DIR / name
        sf.write(path, audio, SR, subtype="PCM_16")
        rms_l = float(np.sqrt(np.mean(audio[:, 0] ** 2)))
        rms_r = float(np.sqrt(np.mean(audio[:, 1] ** 2)))
        print(f"  {name:24s} {len(audio)/SR:4.1f}秒  L/R比 {rms_l/(rms_r or 1e-9):5.2f}")
    print(f"\n書き出し先: {SE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
