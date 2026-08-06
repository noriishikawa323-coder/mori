# 和柄ネイル：ChatGPT画像生成プロンプト集

## 前提

- ChatGPTが出せる縦長サイズは **1024×1536px**。ちょうど2:3で、Pinterest推奨の
  1000×1500と同じ比率なので**リサイズ不要でそのまま投稿できる**。
- プロンプトには「1024x1536」と**数字で明記**する。「vertical」だけだと
  正方形で返ってくることがある。
- Canvaは使わず、**文字も画像に焼き込む**方針。

---

## 案A：まとめ型（一番おすすめ）

```
Create a Pinterest pin image, exactly 1024x1536 pixels (2:3 vertical portrait).

LAYOUT:
- Top 18% of the image: a solid white horizontal band containing text.
- Bottom 82%: a 2x2 grid of four square close-up photos of manicured
  fingernails, separated by thin 4px white gaps.

THE FOUR PHOTOS (all real-photo style, soft natural daylight from the left,
shot from above, shallow depth of field):
1. Pale pink gel nails with delicate painted cherry blossom petals
2. Milky nude nails with scattered gold leaf flakes
3. Glossy red and white checkered pattern nails (Japanese ichimatsu)
4. Dusty pink solid nails with one small gold accent nail
Each hand rests on a natural beige linen cloth.

TEXT IN THE WHITE BAND — render this exact text, spelled exactly as written:
Line 1 (large, bold sans-serif, near-black, all caps):
"JAPANESE NAIL ART IDEAS"
Line 2 (small, regular weight, warm gray, sentence case):
"12 designs to try at home"
Center the text. Line 1 should be about 3x the size of line 2.

STYLE: clean, minimal, editorial. Warm neutral color palette.
No other text anywhere. No watermark, no logo, no signature, no extra words.
```

---

## 案B：シンプル1枚型

```
Create a Pinterest pin image, exactly 1024x1536 pixels (2:3 vertical portrait).

MAIN PHOTO (fills the whole frame):
Realistic close-up photograph of a woman's hand with Japanese cherry blossom
nail art. Pastel pink base with delicate white and pink sakura petals and a
few tiny gold foil flecks. The hand is tilted at about 45 degrees, fingers
relaxed. Blurred warm wooden table in the background. Soft natural window
light. Clean minimal aesthetic, no clutter.

TEXT OVERLAY:
Place a solid white rectangle across the bottom 24% of the image.
Inside it, render this exact text, spelled exactly as written:
Line 1 (large, bold sans-serif, near-black, all caps):
"CHERRY BLOSSOM NAILS"
Line 2 (small, regular weight, warm gray):
"You can do at home - no salon"
Center both lines.

No other text anywhere. No watermark, no logo, no extra words.
```

---

## 案C：Before/After型（クリック率が一番高い）

```
Create a Pinterest pin image, exactly 1024x1536 pixels (2:3 vertical portrait).

LAYOUT: two stacked photos of equal height, split by a thin 4px white line.

TOP HALF: flat lay photograph, shot straight down, of Japanese nail art
sticker sheets with sakura petal and gold leaf designs, arranged neatly on a
white marble surface. Soft even lighting.

BOTTOM HALF: realistic close-up photograph of a hand with the finished
manicure using those same sakura designs - pale pink gel nails with delicate
petals and gold flecks, resting on the same white marble surface.

TEXT OVERLAY:
Place a solid white rectangle across the bottom 20% of the image, on top of
the bottom photo. Inside it, render this exact text, spelled exactly as
written:
Line 1 (large, bold sans-serif, near-black, all caps):
"KAWAII NAIL STICKERS"
Line 2 (small, regular weight, warm gray):
"Salon look in 5 minutes"
Center both lines.

No other text anywhere. No watermark, no logo, no extra words.
```

---

## 案Aの右下コマを差し替える（ピンク一色を避ける）

4枚すべてがピンク系だと画面が単調になり、サムネイルでの視認性が落ちる。
生成後にこう返して、1コマだけ青に差し替える。

```
Keep the image exactly the same, but replace ONLY the bottom-right photo.
Replace it with a close-up of nails in the same style and lighting, showing a
deep indigo blue base with a white seigaiha wave pattern (traditional Japanese
wave motif) on two nails, and solid indigo on the others.
Do not change the other three photos, the layout, the white band, or the text.
```

---

## 文字が崩れたときの直し方

2〜3回に1回はスペルが崩れる。生成画像をよく見て、崩れていたらこう返す。

```
Keep the image exactly the same, but fix the text.
Line 1 must read exactly: JAPANESE NAIL ART IDEAS
Line 2 must read exactly: 12 designs to try at home
Do not change the photos, layout, or colors.
```

**どうしても直らない場合**：プロンプトの `TEXT` 部分を丸ごと削除して
「文字なしの画像」を作り、文字はPinterest投稿時の**タイトル欄**に書く。
写真がきれいなら文字なしでも十分戦える。最初はこの方が失敗しない。

---

## 量産用テンプレート

季節違い・色違いは、案Aの以下2か所だけ差し替える。

| 変えるもの | 差し替え例 |
|---|---|
| 4枚の柄の指定 | 桜 → `summer festival fireworks pattern` / `autumn maple leaf` / `blue and white asanoha geometric` |
| 1行目のテキスト | `JAPANESE NAIL ART IDEAS` → `SUMMER JAPANESE NAILS` / `FALL JAPANESE NAIL IDEAS` |
| 2行目のテキスト | 数字を変えるだけ（`10 designs` / `15 designs`）でも別ピンとして機能する |

**1行目には必ず英語キーワードを残す。**
`Japanese nail art` / `cherry blossom nails` / `kawaii nail stickers` の3つが
検索の入り口なので、ここを削ると流入が止まる。

---

## 保存・アップロード時の注意

- ダウンロードした画像は**PNGのままでOK**（Pinterestが自動変換する）
- **ファイル名を英語にする**：`japanese-nail-art-ideas-01.png` のように。
  日本語ファイル名は文字化けすることがあり、ファイル名も弱いながら検索の材料になる
- 同じ画像を何度も投稿しない。**1枚1ピン**が原則
