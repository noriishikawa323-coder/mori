#!/usr/bin/env bash
# ポッドキャスト音声を一発で作る (Mac / Linux)
#   1. VOICEVOX を起動しておく
#   2. ターミナルでこのファイルのあるフォルダに移動して:  bash make_audio.sh
set -u

cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python) || {
  echo "エラー: Python が見つかりません。https://www.python.org からインストールしてください。"
  exit 1
}

echo "[1/4] 必要なライブラリを確認しています..."
"$PY" -m pip install --quiet --disable-pip-version-check -r podcast/requirements.txt || {
  echo "エラー: ライブラリのインストールに失敗しました。"
  exit 1
}

echo "[2/4] VOICEVOX が起動しているか確認しています..."
if ! curl -s -m 5 http://127.0.0.1:50021/version > /dev/null 2>&1; then
  echo
  echo "  VOICEVOX に接続できません。"
  echo "  VOICEVOX アプリを起動して、画面が出きってから、もう一度このファイルを実行してください。"
  echo "  （アプリを起動しておくだけで大丈夫です。操作は要りません）"
  exit 1
fi
echo "      OK"

echo "[3/4] セリフを合成しています（162行。数分かかります）..."
"$PY" podcast/tools/synthesize.py "$@" || exit 1

echo "[4/4] 1本につないで音量を整えています..."
"$PY" podcast/tools/build_episode.py || exit 1

echo
echo "完成しました: podcast/audio/podcast_ep001.wav"
