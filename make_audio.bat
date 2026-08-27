@echo off
chcp 65001 > nul
rem ポッドキャスト音声を一発で作る (Windows)
rem   1. VOICEVOX を起動しておく
rem   2. このファイルをダブルクリック

cd /d "%~dp0"

where python > nul 2>&1
if errorlevel 1 (
  echo エラー: Python が見つかりません。https://www.python.org からインストールしてください。
  echo インストール時に "Add Python to PATH" にチェックを入れてください。
  pause
  exit /b 1
)

echo [1/4] 必要なライブラリを確認しています...
python -m pip install --quiet --disable-pip-version-check -r podcast\requirements.txt
if errorlevel 1 ( echo エラー: ライブラリのインストールに失敗しました。& pause & exit /b 1 )

echo [2/4] VOICEVOX が起動しているか確認しています...
curl -s -m 5 http://127.0.0.1:50021/version > nul 2>&1
if errorlevel 1 (
  echo.
  echo   VOICEVOX に接続できません。
  echo   VOICEVOX アプリを起動して、画面が出きってから、もう一度このファイルを実行してください。
  echo   ^(アプリを起動しておくだけで大丈夫です。操作は要りません^)
  pause
  exit /b 1
)
echo       OK

echo [3/4] セリフを合成しています（162行。数分かかります）...
python podcast\tools\synthesize.py %*
if errorlevel 1 ( pause & exit /b 1 )

echo [4/4] 1本につないで音量を整えています...
python podcast\tools\build_episode.py
if errorlevel 1 ( pause & exit /b 1 )

echo.
echo 完成しました: podcast\audio\podcast_ep001.wav
pause
