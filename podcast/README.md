# ポッドキャスト音声ビルド

台本(JSONL)を VOICEVOX で1行ずつ合成し、間・SE・BGM・ラウドネスを整えて
1本のエピソードWAVに仕上げるパイプラインです。

```
podcast/
├── script/
│   ├── ep001_meta.json              話者割り当て・感情プリセット・マスタリング設定
│   ├── ep001_timeline.jsonl         台本本体（1行=1発話 / SE / 無音 / チャプター）
│   └── ep001_production_notes.md    SE仕様・演出メモ・裏取りリスト
├── tools/
│   ├── common.py                    共通ユーティリティ
│   ├── make_se.py                   実演コーナーのSEを生成
│   ├── synthesize.py                VOICEVOX 合成（1行1ファイル）
│   └── build_episode.py             結合・無音付加・BGM合成・LUFS正規化
└── audio/
    ├── lines/                       行ごとのWAV（生成物・gitignore）
    └── podcast_ep001.wav            最終成果物
```

## いちばん簡単な手順

1. **VOICEVOX** を https://voicevox.hiroshiba.jp からダウンロードして起動する
   （起動しておくだけでよく、アプリ側の操作は要りません）
2. リポジトリのフォルダで:
   - Windows → `make_audio.bat` をダブルクリック
   - Mac / Linux → ターミナルで `bash make_audio.sh`

これで `podcast/audio/podcast_ep001.wav` が出来ます。
ライブラリのインストールも中でやるので、事前準備は Python が入っていることだけです。

キャスティングを変えて作り直したいときは引数をそのまま渡せます。

```bash
bash make_audio.sh --force --casting as_specified
```

---

## 必要なもの（手動でやる場合）

```bash
pip install -r podcast/requirements.txt
```

VOICEVOX エンジンを起動し、`http://127.0.0.1:50021` で待ち受けさせてください
(VOICEVOX アプリを起動しておくだけでも可)。

## 使い方

```bash
# 0. 実演コーナーのSEを生成（初回のみ。assets/se/ に3点出ます）
python3 podcast/tools/make_se.py

# 1. 全162行を合成（2回目以降は差分のみ。--force で全再合成）
python3 podcast/tools/synthesize.py

# 2. 結合してマスタリング
python3 podcast/tools/build_episode.py

# BGMを重ねる場合
python3 podcast/tools/build_episode.py --bgm assets/bgm/calm_jazz.mp3
```

出力: `podcast/audio/podcast_ep001.wav` （44.1kHz / 16bit / ステレオ / -16 LUFS）
同時に `podcast_ep001_cues.txt` にチャプター表が出ます。

### エンジンが無い環境での確認

```bash
python3 podcast/tools/synthesize.py --mock
python3 podcast/tools/build_episode.py --out /tmp/preview.wav
```

`--mock` は VOICEVOX を呼ばず、話速から尺を推定した**テンポ確認用のプレビュー音**
（話者ごとに高さの違うパルス音）を生成します。本合成の前に、間の取り方と
全体の尺だけを耳でチェックできます。

## 台本フォーマット

`ep001_timeline.jsonl` は1行1レコードのJSONです。

```jsonc
{"type":"line","id":"0043","speaker":"SAKAI","emotion":"surprise","text":"あ。","pause":0.8}
{"type":"se","id":"SE02","file":"assets/se/se02_nakikawashi.wav","fallback_sec":7.0,"pause":1.0}
{"type":"silence","sec":0.8,"note":"まとめ直前の完全無音"}
{"type":"marker","label":"04_雑学2_鳴き交わし"}
```

- `pause` … その発話の**後ろ**に入れる無音（秒）。台本上は 0.5〜1.0 で運用。
- `se` … 実ファイルがあれば挿入、無ければ `fallback_sec` の無音で尺を維持。
- `marker` … 音には出ず、チャプター表の見出しになる。

### キャスティングの切り替え

`ep001_meta.json` の `casting_presets` に定義してあります。

```bash
python3 podcast/tools/synthesize.py --force                        # 既定 (玄野武宏 / 青山龍星)
python3 podcast/tools/synthesize.py --force --casting as_specified # ずんだもん / 四国めたん
```

| プリセット | ハヤシ(解説) | サカイ(リアクション) |
|---|---|---|
| `izakaya`（既定） | 玄野武宏(11) | 青山龍星(13) |
| `as_specified` | ずんだもん(3) | 四国めたん(2) |

台本が居酒屋トークの文体なので、既定は男性2人にしてあります。
別のキャラで試すときは `ep001_meta.json` の `casting_presets` に追記するか、
`voicevox_speaker_id` を直接書き換えてください。
作り直すときは `--force` を付けて上書きします。

### 感情プリセット

`ep001_meta.json` の `emotion_presets` で定義。VOICEVOX の audio_query を上書きします。

| preset | speedScale | pitchScale | intonationScale | 用途 |
|---|---|---|---|---|
| `normal` | 1.0 | 0.0 | 1.0 | 通常解説 |
| `surprise` | 1.1 | 0.03 | 1.1 | 驚きのシーン |
| `tsukkomi` | 1.15 | 0.0 | 1.3 | ツッコミ |
| `conclusion` | 0.95 | 0.0 | 1.0 | 結論・噛み締めるトーン |

行間の無音はビルド側で管理するため、合成時に `prePhonemeLength` /
`postPhonemeLength` は 0 にしています。プリセットを増やす場合は
`ep001_meta.json` にキーを足すだけで `synthesize.py` が拾います。

## マスタリング

`ep001_meta.json` の `master` セクションで制御します。

| キー | 既定 | 内容 |
|---|---|---|
| `lead_in_sec` | 3.0 | 冒頭の無音 |
| `tail_sec` | 5.0 | 末尾の余韻 |
| `target_lufs` | -16.0 | 目標ラウドネス（`--lufs` で上書き可） |
| `true_peak_ceiling_db` | -1.0 | ピーク上限。リミッターで超過分だけ抑える |
| `se_level_ratio` | 0.9 | セリフの実効音量に対するSEの比率（`--se-ratio`） |
| `bgm_level_ratio` | 0.15 | ナレーションの実効音量に対するBGMの比率 |
| `bgm_fade_in_sec` / `bgm_fade_out_sec` | 3.0 / 5.0 | BGMのフェード |

BGMとSEはどちらもナレーションの**有声区間のRMS**を基準に音量を合わせます
（全体RMSだと無音区間に引っ張られて大きくなりすぎるため）。SEの音量は
素材ファイルの絶対レベルに依存しないので、SEを差し替えてもバランスは崩れません。
エピソードより短いBGMは自動でループします。

ピーク処理は**ルックアヘッド・リミッター**です。全体を一律に下げると
ラウドネス正規化の結果が崩れる（SEや語気の強い行のピークに引きずられて
最終値が目標を大きく下回る）ため、超過している箇所のゲインだけを下げ、
その後もう一度目標ラウドネスに合わせ直しています。BGM有り/無しの両方で
**-16.00 LUFS かつピーク -1.00 dBFS** になることを実測確認済みです。

## クレジット表記

VOICEVOX で生成した音声を公開する場合、各キャラクターの利用規約に従った
クレジット表記が必要です。配信ページと音声内の双方を確認してください。

## PCが無い場合（Google Colab）

`podcast/colab/ep001_make_audio.ipynb` を Google Colab で開くと、
クラウド上のLinuxで VOICEVOX エンジンごと動かせます。スマホのブラウザからでも
セルの ▶ を上から順に押すだけで、Googleドライブに音声が出ます。

Colab で開くURL:
https://colab.research.google.com/github/noriishikawa323-coder/mori/blob/claude/podcast-planning-daily-insights-2mbv5m/podcast/colab/ep001_make_audio.ipynb

開けない場合は colab.research.google.com → GitHub タブ →
`noriishikawa323-coder/mori` を検索 → ブランチを選択 → ノートブックを選択。

注意: iOSではブラウザを裏に回すとColabの接続が切れます。実行中は
Safariを前面に置き、設定→画面表示と明るさ→自動ロックを「なし」にしてください。

## コマンドを使わない手順

1. https://github.com/noriishikawa323-coder/mori/tree/claude/podcast-planning-daily-insights-2mbv5m
   を開き、緑の **Code** ボタン → **Download ZIP**
2. ダウンロードしたZIPを展開する
   （Windows: 右クリック → すべて展開 / Mac: ダブルクリック）
3. VOICEVOX を起動しておく
4. 展開したフォルダの中の
   - Windows → `make_audio.bat` をダブルクリック
   - Mac → `make_audio.command` をダブルクリック

`podcast/audio/podcast_ep001.wav` ができます。

### 予備手段: VOICEVOXアプリだけで作る

上がどうしても動かない場合、`podcast/script/ep001_voicevox_import.txt` を
VOICEVOX の「テキスト読み込み」で開くと、162行が音声ブロックとして並びます。
そのまま「音声を繋げて書き出し」で1本のwavになります。

ただしこの方法では、感情プリセット（話速・抑揚）、行間の間、SE、BGM、
ラウドネス正規化がすべて反映されません。仕上がりは粗くなります。
