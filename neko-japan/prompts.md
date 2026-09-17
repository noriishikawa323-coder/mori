# 招き猫：ChatGPT画像生成プロンプト集

## 前提

- ChatGPTが出せる縦長サイズは **1024×1536px**。2:3でPinterest推奨の
  1000×1500と同じ比率なので**リサイズ不要でそのまま投稿できる**。
- プロンプトには「1024x1536」と**数字で明記**する。「vertical」だけだと
  正方形で返ってくることがある。
- 文字も画像に焼き込む方針（Canvaは使わない）。
- **Amazonの商品画像は絶対に使わない。** 規約違反でアカウント停止の対象。
  AI生成画像かフリー素材のみ。

---

## 案A：まとめ型（一番おすすめ / ピン1・4・9用）

```
Create a Pinterest pin image, exactly 1024x1536 pixels (2:3 vertical portrait).

LAYOUT:
- Top 18% of the image: a solid cream-white horizontal band containing text.
- Bottom 82%: a 2x2 grid of four square photos, separated by thin 4px white gaps.

THE FOUR PHOTOS (all real-photo style, soft natural daylight from the left,
shallow depth of field, shot straight on):
1. A small matte black Japanese maneki neko figurine with gold and red
   details, sitting on a pale oak shelf
2. A glossy gold ceramic beckoning cat with a raised left paw, on a white
   kitchen counter
3. A small antique-brass maneki neko charm on a dark cord with red beads,
   hanging from a cream canvas tote bag
4. A white ceramic maneki neko beside a small stack of books on a linen cloth
Warm neutral background tones throughout.

TEXT IN THE CREAM BAND — render this exact text, spelled exactly as written:
Line 1 (large, bold serif, near-black, title case):
"Maneki Neko"
Line 2 (small, regular weight, warm gray, sentence case):
"4 lucky cat pieces for your home"
Center the text. Line 1 should be about 2.5x the size of line 2.

STYLE: clean, minimal, editorial. Warm neutral palette, cream and terracotta.
No other text anywhere. No watermark, no logo, no signature, no extra words.
```

---

## 案B：黒猫の厄除け（ピン2用）

```
Create a Pinterest pin image, exactly 1024x1536 pixels (2:3 vertical portrait).

A single matte black Japanese maneki neko figurine with small gold and red
painted details, sitting on a pale oak windowsill. Soft morning daylight from
the right, long gentle shadow. Plain warm white wall behind, slightly out of
focus. Real-photo style, shot slightly above eye level, shallow depth of field.
The cat occupies the middle third of the frame.

TEXT overlaid in the lower third, on a semi-transparent cream panel:
Line 1 (large, bold serif, near-black, title case):
"The Black Lucky Cat"
Line 2 (small, regular weight, warm gray, sentence case):
"Not for money - for warding off bad luck"

STYLE: quiet, editorial, minimal. Warm neutral palette.
No other text anywhere. No watermark, no logo, no extra words.
```

---

## 案C：手振り猫（ピン3・7用）

```
Create a Pinterest pin image, exactly 1024x1536 pixels (2:3 vertical portrait).

A glossy gold ceramic Japanese beckoning cat (maneki neko) with a raised left
paw, sitting on a light wood counter beside a small ceramic cup. Warm
late-afternoon light from the left. Softly blurred background suggesting a
small cafe interior. Real-photo style, shot straight on at counter height,
shallow depth of field.

TEXT overlaid across the top 20%, on a solid cream band:
Line 1 (large, bold serif, near-black, title case):
"The Waving Cat"
Line 2 (small, regular weight, warm gray, sentence case):
"From every Japanese restaurant window"

STYLE: warm, inviting, editorial. Cream, gold and soft brown palette.
No other text anywhere. No watermark, no logo, no extra words.
```

---

## 案D：キーホルダー（ピン5用）

```
Create a Pinterest pin image, exactly 1024x1536 pixels (2:3 vertical portrait).

Close-up of a small antique-brass Japanese maneki neko charm hanging from a
dark braided cord, strung with round red and black beads and a single old
Chinese coin, clipped to the handle of a cream canvas tote bag. Soft diffused
daylight. Real-photo style, shot close, very shallow depth of field so the bag
fabric texture is soft behind the charm.

TEXT overlaid in the lower quarter, on a semi-transparent cream panel:
Line 1 (large, bold serif, near-black, title case):
"Lucky Cat Keychain"
Line 2 (small, regular weight, warm gray, sentence case):
"Brass charm with feng shui coins"

STYLE: tactile, warm, editorial. Brass, cream and deep red palette.
No other text anywhere. No watermark, no logo, no extra words.
```

---

## 案E：意味の解説型（ピン1・9用 / 保存されやすい）

```
Create a Pinterest pin image, exactly 1024x1536 pixels (2:3 vertical portrait).

LAYOUT:
- Top 16%: solid cream band with a title.
- Middle 60%: two white ceramic maneki neko figurines side by side on a pale
  oak surface against a plain warm white wall. The LEFT cat raises its LEFT
  paw. The RIGHT cat raises its RIGHT paw. Soft even daylight, real-photo
  style, shot straight on.
- Bottom 24%: solid cream band with two short lines of text.

TEXT IN THE TOP BAND (large, bold serif, near-black, title case):
"What the Raised Paw Means"

TEXT IN THE BOTTOM BAND — two lines, small, warm gray, sentence case,
left-aligned with generous margins:
"Left paw - invites people and customers"
"Right paw - invites money and fortune"

STYLE: clean, informative, minimal. Warm neutral palette.
No other text anywhere. No watermark, no logo, no extra words.
```

---

## 案F：棚のスタイリング（ピン6・10用）

```
Create a Pinterest pin image, exactly 1024x1536 pixels (2:3 vertical portrait).

A narrow pale oak shelf against a warm white wall, styled minimally: a small
white ceramic maneki neko with a raised paw, a short stack of two books, a
small dried branch in a slim ceramic vase. Lots of empty wall space above.
Soft natural daylight from the left, gentle shadows. Real-photo style, shot
straight on, shallow depth of field.

TEXT overlaid in the upper third, on the empty wall space, no panel:
Line 1 (large, bold serif, warm dark brown, title case):
"Small Japanese Decor"
Line 2 (small, regular weight, warm gray, sentence case):
"For a small apartment"

STYLE: airy, minimal, Japandi. Cream, pale wood and soft white palette.
No other text anywhere. No watermark, no logo, no extra words.
```

---

## 使い方

1. ChatGPTに上のプロンプトを1つ貼る
2. 出てきた画像を保存
3. Pinterestで新規ピン作成 → 画像アップロード
4. タイトル・説明文は別途用意したものを貼る
5. リンク先: `https://playful-bubblegum-75d73e.netlify.app`

同じプロンプトを再実行すると毎回違う絵が出るので、1つのプロンプトから
2〜3枚作って別々のピンにしてもいい。Pinterestは同じリンクに複数ピンを
貼るのが普通の運用。
