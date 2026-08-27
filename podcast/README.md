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

## 必要なもの

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
python3 podcast/tools/synthesize.py --force                   # 既定 (ずんだもん / 四国めたん)
python3 podcast/tools/synthesize.py --force --casting izakaya # 玄野武宏 / 青山龍星
```

| プリセット | ハヤシ(解説) | サカイ(リアクション) |
|---|---|---|
| `as_specified`（既定） | ずんだもん(3) | 四国めたん(2) |
| `izakaya` | 玄野武宏(11) | 青山龍星(13) |

台本は居酒屋トークの文体なので、`izakaya` のほうが噛み合います。
両方合成して聴き比べる場合は `--force` を付けて上書きしてください。

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
