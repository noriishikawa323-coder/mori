# 業種別 HACCP 記録様式ジェネレータ（A4横・4ページ／業種）
import base64, os, re, ssl, subprocess, sys, urllib.parse, urllib.request

OUT = os.path.dirname(os.path.abspath(__file__))
DAYS = 31

# ---------- 共通の一般衛生管理（どの業種でも入れる8項目） ----------
BASE_GEN = [
    ("原材料の受入の確認", "配送温度・期限・包装の破れ・においを確認した"),
    ("冷蔵庫の温度（10℃以下）", "庫内の温度計を見る"),
    ("冷凍庫の温度（−15℃以下）", "庫内の温度計を見る"),
    ("交差汚染・二次汚染の防止", "生のものとそれ以外で、まな板と包丁を分けた"),
    ("器具等の洗浄・消毒・殺菌", "まな板・包丁・ふきん・スポンジ"),
    ("トイレの洗浄・消毒", "ドアノブ・水栓も含む"),
    ("従業員の健康管理", "下痢・嘔吐・発熱・手の傷の有無を確認した"),
    ("手洗いの実施", "作業前・トイレ後・生の食材を触った後"),
]

LAW_COMMON = [
    "<b>牛のレバーを生食用として提供することは禁止されています</b>（2012年7月〜）。",
    "<b>豚の肉・内臓（レバーを含む）を生食用として提供することも禁止されています</b>（2015年6月〜）。",
    "加熱の目安は<b>中心部まで75℃で1分以上</b>（レバーは63℃で30分以上、または75℃1分以上）。",
]
LAW_RAWBEEF = ("牛肉のユッケ・タルタルなどの<b>生食用食肉は、規格基準を満たす場合のみ</b>提供できます。"
               "加工の設備・方法・表示・届出の要件があるので、扱うなら保健所に確認してください。")

# ---------- 業種ごとの定義 ----------
SHOPS = [
    dict(
        slug="ippan", name="一般飲食店", note="居酒屋・定食屋・食堂など",
        extra=[("開店前の店内・厨房の点検", "ねずみや虫の形跡、水漏れ、においを見た"),
               ("ダスター・ふきんの交換", "使い回さず、汚れたら交換した")],
        imp=[("分類1　加熱しないで出すもの（刺身・冷奴・サラダ・漬物など）",
              [("冷蔵庫から出したら、すぐ提供した", "常温に置きっぱなしにしていない")]),
             ("分類2　加熱して熱いまま出すもの（焼き物・揚げ物・炒め物・汁物など）",
              [("中心部まで火が通ったことを確認した", "目安 中心温度75℃で1分以上")]),
             ("分類3　加熱してから冷ますもの・作りおき（煮物・仕込み品など）",
              [("加熱後、すばやく冷やして冷蔵した", ""),
               ("提供前に、しっかり再加熱した", "再加熱しないものは「／」"),
               ("仕込み品に日付を書いた", "つくった日が分かるようにした")]),
             ("毎日かならず確認すること（法令）",
              [("牛レバー・豚肉・豚の内臓を、生では出していない", "加熱用として提供した")])],
        law=LAW_COMMON + [LAW_RAWBEEF],
        point=("いちばん止まりやすいのは「冷蔵庫の温度」です",
               "温度計を庫内に入れて、見る場所を決めてしまってください。"
               "毎日おなじ場所を見るだけにすると、確認が習慣になります。"),
    ),
    dict(
        slug="yakiniku", name="焼肉店", note="焼肉・ホルモンなど、客席で焼く店",
        extra=[("スライサー・ミンサーの分解洗浄・消毒", "刃・受け皿まで外して洗い、消毒した"),
               ("トング・取り箸の準備と洗浄消毒", "生肉用トングを客数分そろえた"),
               ("ロースター・網・受け皿・排気の清掃", "網は使い回さず、汚れたら交換")],
        imp=[("分類1　加熱しないで出すもの（キムチ・ナムル・サラダ・冷麺など）",
              [("冷蔵庫から出したら、すぐ提供した", "常温に置きっぱなしにしていない")]),
             ("分類2　厨房で加熱して出すもの（スープ・クッパ・石焼など）",
              [("中心部まで火が通ったことを確認した", "目安 中心温度75℃で1分以上")]),
             ("分類3　お客様が客席で焼くもの（この店の主力。ここが一番大事）",
              [("生肉をつかむ専用のトング・取り箸を一緒に出した", "食べる箸で生肉を触らせない"),
               ("「よく焼いてから食べる」ことをお客様に伝えた", "口頭またはテーブルの案内で"),
               ("網・鉄板が汚れていないか見て、必要なら交換した", "")]),
             ("分類4　加熱してから冷ますもの・作りおき（タレ・スープ・ナムル）",
              [("加熱後、すばやく冷やして冷蔵した", ""),
               ("仕込み品に日付を書いた", "つくった日が分かるようにした")]),
             ("毎日かならず確認すること（法令）",
              [("牛レバー・豚肉・豚の内臓を、生では出していない", "加熱用として提供した")])],
        law=LAW_COMMON + [LAW_RAWBEEF],
        point=("焼肉店の食中毒は、焼き方では起きません",
               "生肉を触った箸やトングで、焼けた肉やサラダを触ることで起きます。"
               "だから分類3の1行目を「生肉用トングを出したか」にしています。<b>ここだけは毎日○がつく状態にしてください。</b>"),
    ),
    dict(
        slug="sushi", name="寿司・刺身の店", note="寿司店・海鮮居酒屋など",
        extra=[("ネタケース・冷蔵ショーケースの温度", "生食用のネタは特に低い温度を保つ"),
               ("魚専用のまな板・包丁の使い分け", "野菜・加熱済みのものとは分ける"),
               ("酢飯の温度と時間の管理", "作ってから長く常温に置いていない")],
        imp=[("分類1　生で出すもの（刺身・寿司・カルパッチョなど）※この店の主力",
              [("生食用の表示があるものを使った", "解凍品は解凍方法と時間を守った"),
               ("さばいてから提供までを短くした", "冷蔵から出しっぱなしにしていない"),
               ("アニサキスを目視で確認した", "内臓は早く取り除いた。冷凍品は表示どおり")]),
             ("分類2　加熱して出すもの（焼き物・揚げ物・汁物など）",
              [("中心部まで火が通ったことを確認した", "目安 中心温度75℃で1分以上"),
               ("二枚貝は十分に加熱した", "ノロウイルス対策 85〜90℃で90秒以上")]),
             ("分類3　加熱してから冷ますもの・作りおき（煮物・煮ツメ・仕込み）",
              [("加熱後、すばやく冷やして冷蔵した", ""),
               ("仕込み品に日付を書いた", "つくった日が分かるようにした")]),
             ("毎日かならず確認すること（法令）",
              [("牛レバー・豚肉・豚の内臓を、生では出していない", "扱わない日は「／」")])],
        law=LAW_COMMON + [LAW_RAWBEEF,
            "生食用の鮮魚介類は<b>生食用として仕入れたもの</b>を使ってください。加熱用は生で出せません。",
            "アニサキスは<b>冷凍（−20℃で24時間以上）または加熱</b>で死にます。目視での除去も合わせて行ってください。"],
        point=("この店は分類1が主力です",
               "生で出すものが多いぶん、温度と時間の記録がそのまま store の説明材料になります。"
               "「冷蔵から出して何分で出したか」を意識するだけで、記録の質が変わります。"),
    ),
    dict(
        slug="ramen", name="ラーメン店", note="ラーメン・つけ麺・中華そば",
        extra=[("スープの保温温度の確認", "寸胴を温かいまま保つ。ぬるいまま置かない"),
               ("チャーシュー・煮玉子など仕込み品の冷却", "加熱後すばやく冷やして冷蔵した"),
               ("寸胴・ゆで麺機・ラーメンダレ容器の洗浄", "こびりつきを落として消毒した")],
        imp=[("分類1　加熱しないで出すもの（メンマ・ネギ・薬味・冷やし系）",
              [("冷蔵庫から出したら、すぐ使った", "常温に置きっぱなしにしていない")]),
             ("分類2　加熱して熱いまま出すもの（スープ・麺・餃子・炒飯）※主力",
              [("スープを十分に熱い状態で提供した", "ぬるいまま出していない"),
               ("餃子・唐揚げなどの中心部まで火が通った", "目安 中心温度75℃で1分以上")]),
             ("分類3　加熱してから冷ますもの・作りおき（チャーシュー・煮玉子・タレ）",
              [("加熱後、すばやく冷やして冷蔵した", "常温で放置していない"),
               ("提供前に、しっかり再加熱した", "再加熱しないものは「／」"),
               ("仕込み品に日付を書いた", "つくった日が分かるようにした")]),
             ("毎日かならず確認すること（法令）",
              [("牛レバー・豚肉・豚の内臓を、生では出していない", "レアチャーシューは中心まで加熱した")])],
        law=LAW_COMMON + [
            "いわゆる<b>レアチャーシューも、豚肉である以上は中心まで加熱</b>が必要です。生食用として出すことはできません。"],
        point=("危ないのは、営業中ではなく仕込みです",
               "加熱したものを常温でゆっくり冷ますと、いちばん菌が増える温度帯を長く通ります。"
               "<b>加熱後は小分けにして早く冷やす</b>。ここを分類3の1行目に置いています。"),
    ),
    dict(
        slug="yakitori", name="焼鳥・鶏料理の店", note="焼鳥・鶏専門店",
        extra=[("鶏専用のまな板・包丁・トングの使い分け", "野菜・加熱済みのものとは必ず分ける"),
               ("串打ち場の温度と作業時間", "常温に長く出しっぱなしにしていない"),
               ("焼き台・網・受け皿の清掃", "こげ・脂を落とした")],
        imp=[("分類1　加熱しないで出すもの（お通し・サラダ・冷奴など）",
              [("冷蔵庫から出したら、すぐ提供した", "常温に置きっぱなしにしていない")]),
             ("分類2　加熱して出すもの（焼鳥・唐揚げ・鍋）※この店の主力",
              [("串の中心部まで火が通ったことを確認した", "目安 中心温度75℃で1分以上。太い部位は特に"),
               ("肉汁が透明であることを確認した", "赤い肉汁が出るものは焼き直した"),
               ("焼き上がりを、生の串と別のトングで扱った", "生を触った器具で焼き上がりを触らない")]),
             ("分類3　加熱してから冷ますもの・作りおき（タレ・スープ・仕込み）",
              [("加熱後、すばやく冷やして冷蔵した", ""),
               ("仕込み品に日付を書いた", "つくった日が分かるようにした")]),
             ("毎日かならず確認すること（法令・食中毒対策）",
              [("鶏を生や半生で出していない", "鶏刺し・タタキを出さない日は○"),
               ("牛レバー・豚肉・豚の内臓を、生では出していない", "扱わない日は「／」")])],
        law=LAW_COMMON + [
            "鶏肉の生食は法律で一律に禁止されているわけではありませんが、"
            "<b>カンピロバクター食中毒の主な原因</b>で、自治体によっては提供の自粛を求めています。"
            "<b>中心部まで加熱して出すことを強くおすすめします。</b>"],
        point=("鶏はカンピロバクターです",
               "少ない菌数でも発症し、まれに重い後遺症につながります。"
               "太い部位ほど中心が生で残るので、<b>肉汁が透明か</b>を毎回見る癖をつけてください。"),
    ),
    dict(
        slug="cafe", name="カフェ・喫茶店", note="カフェ・喫茶・軽食の店",
        extra=[("製氷機の清掃・点検", "内部のぬめり、氷の色とにおいを見た"),
               ("牛乳・生クリームの温度と期限", "開封日を書いて、期限内のものを使った"),
               ("ミルクピッチャー・抽出器具の洗浄", "分解して洗い、乾かした")],
        imp=[("分類1　加熱しないで出すもの（サンドイッチ・サラダ・ケーキ・アイス）※主力",
              [("冷蔵庫から出したら、すぐ提供した", "常温に置きっぱなしにしていない"),
               ("盛り付けは手袋または専用の器具で行った", "素手で直接触っていない")]),
             ("分類2　加熱して出すもの（ホットサンド・パスタ・スープ・グラタン）",
              [("中心部まで火が通ったことを確認した", "目安 中心温度75℃で1分以上")]),
             ("分類3　作りおき（仕込みのソース・カット野菜・カットフルーツ）",
              [("加熱したものは、すばやく冷やして冷蔵した", ""),
               ("カットしたものに日付を書いた", "つくった日が分かるようにした")]),
             ("毎日かならず確認すること",
              [("氷・水まわりに異常がなかった", "におい・色・ぬめり")])],
        law=LAW_COMMON + [
            "生クリーム・カスタード・卵を使ったものは<b>傷みやすい</b>ので、"
            "つくった日を管理し、冷蔵のまま提供してください。"],
        point=("見落としやすいのは製氷機です",
               "毎日使うのに、中を見る機会がほとんどありません。"
               "<b>氷は加熱せずに口に入る</b>ものなので、確認項目に入れてあります。"),
    ),
    dict(
        slug="bento", name="弁当・惣菜・テイクアウト", note="弁当店・惣菜店・持ち帰りのある店",
        extra=[("盛り付け時の手袋・専用器具の使用", "素手で直接触っていない"),
               ("できあがりから渡すまでの時間", "長く置いたものは出していない"),
               ("消費期限・保存方法の表示", "貼り忘れがないか確認した")],
        imp=[("分類1　加熱しないで詰めるもの（サラダ・漬物・生野菜の飾り）",
              [("冷蔵のまま扱い、すぐ詰めた", "常温に置きっぱなしにしていない")]),
             ("分類2　加熱して詰めるもの（揚げ物・焼き物・煮物）※主力",
              [("中心部まで火が通ったことを確認した", "目安 中心温度75℃で1分以上")]),
             ("分類3　加熱後に冷ましてから詰めるもの ※ここが一番大事",
              [("加熱後、すばやく冷やしてから詰めた", "温かいまま蓋をしていない"),
               ("詰めた後は冷蔵で保管した", "常温で並べていない場合は「／」"),
               ("つくった日・消費期限を書いた", "")]),
             ("毎日かならず確認すること（法令）",
              [("表示（消費期限・保存方法）をつけた", ""),
               ("牛レバー・豚肉・豚の内臓を、生では出していない", "扱わない日は「／」")])],
        law=LAW_COMMON + [
            "持ち帰りのものは、<b>お客様が食べるまでの時間</b>が読めません。"
            "消費期限と保存方法（要冷蔵など）の表示をつけ、早めに食べるよう伝えてください。",
            "テイクアウトを新しく始める場合は、<b>営業許可の範囲に入るか保健所に確認</b>してください。"],
        point=("温かいまま蓋をしないでください",
               "湯気がこもって水滴になり、菌が増えます。"
               "<b>加熱→急冷→詰める</b>の順番を守るだけで、事故はかなり減ります。"),
    ),
    dict(
        slug="bar", name="バー・スナック", note="バー・スナック・ショットバー",
        extra=[("製氷機・アイスペールの清掃", "内部のぬめり、氷のにおいを見た"),
               ("グラス・シェーカー・マドラーの洗浄消毒", "口が触れる部分を特に"),
               ("カットフルーツ・ガーニッシュの管理", "つくり置きは冷蔵。当日中に使い切った")],
        imp=[("分類1　加熱しないで出すもの（カットフルーツ・チーズ・生ハム・乾き物）※主力",
              [("冷蔵から出したら、すぐ提供した", "常温に出しっぱなしにしていない"),
               ("盛り付けは手袋または専用の器具で行った", "素手で直接触っていない")]),
             ("分類2　加熱して出すもの（温かいフード・揚げ物）",
              [("中心部まで火が通ったことを確認した", "目安 中心温度75℃で1分以上。出さない日は「／」")]),
             ("分類3　作りおき（自家製シロップ・インフュージョン・仕込み）",
              [("冷蔵で保管し、つくった日を書いた", "")]),
             ("毎日かならず確認すること",
              [("氷と水まわりに異常がなかった", "におい・色・ぬめり")])],
        law=LAW_COMMON + [
            "自家製のシロップや果実酒などを提供する場合、<b>酒類の製造にあたらないか</b>注意してください。"
            "判断に迷うときは、税務署と保健所に確認してください。"],
        point=("氷とグラスが、この業態の急所です",
               "どちらも加熱せずに直接口に触れます。"
               "製氷機の中は毎日見るものではないので、あえて確認項目に入れてあります。"),
    ),
]

# ---------- HTML 組み立て ----------
STYLE = """<style>
:root{ --navy:#2B3A55; --accent:#F0A202; --line:#2B3A55; }
@page{ size:A4 landscape; margin:0; }
*{ box-sizing:border-box; margin:0; padding:0; }
html,body{ background:#fff; }
body{ font-family:"Noto Sans JP","IPAGothic",sans-serif; color:var(--navy);
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.page{ width:297mm; height:210mm; padding:10mm 12mm; page-break-after:always;
  position:relative; display:flex; flex-direction:column; }
.page:last-child{ page-break-after:auto; }
.head{ display:flex; align-items:flex-end; justify-content:space-between; gap:8mm; }
h1{ font-size:17pt; font-weight:700; line-height:1.2; }
h1 small{ display:block; font-size:9pt; font-weight:400; opacity:.7; margin-top:1mm; }
.fields{ font-size:10pt; text-align:right; line-height:2.1; white-space:nowrap; }
.fld{ display:inline-block; border-bottom:1.2pt solid var(--line); height:6mm; }
table{ width:100%; border-collapse:collapse; }
th,td{ border:1pt solid var(--line); }
th{ background:rgba(43,58,85,.08); font-weight:700; }
.cal{ margin-top:4mm; table-layout:fixed; }
.cal th.item{ width:64mm; font-size:9pt; padding:1.5mm 2mm; text-align:left; }
.cal th.day{ font-size:6.6pt; padding:1.2mm 0; text-align:center; }
.cal td.item{ font-size:8.2pt; padding:1mm 2mm; line-height:1.3; }
.cal td.item b{ font-weight:700; font-size:9pt; }
.cal td.item span{ opacity:.7; font-size:7pt; display:block; }
.cal td.d{ padding:0; }
.cal tr{ height:8.8mm; }
.cal .sec td{ background:rgba(240,162,2,.18); font-size:8.2pt; font-weight:700;
  padding:.8mm 2mm; height:5.4mm; }
.legend{ margin-top:2mm; font-size:8.6pt; opacity:.85; display:flex; gap:8mm; }
.legend b{ font-weight:700; }
.memo{ margin-top:2mm; }
.memo th{ font-size:8.6pt; padding:1.2mm; }
.memo td{ height:7.6mm; }
.memo .w-date{ width:22mm; }
.memo .w-sign{ width:26mm; }
.foot{ position:absolute; left:12mm; right:12mm; bottom:4mm; font-size:7.5pt;
  opacity:.5; display:flex; justify-content:space-between; }
.guide{ margin-top:3mm; border:1.2pt solid var(--line); padding:3mm 4.5mm;
  font-size:9pt; line-height:1.6; }
.guide h3{ font-size:10.5pt; font-weight:700; margin-bottom:1.5mm; }
.law{ margin-top:3.5mm; border:1.8pt solid var(--accent); padding:3mm 4.5mm;
  font-size:9pt; line-height:1.6; }
.law h3{ font-size:10.5pt; font-weight:700; margin-bottom:1.5mm; }
.law ul{ margin-left:5mm; }
.law li{ margin-top:1mm; }
</style>"""

DAYHDR = "".join(f'<th class="day">{d}</th>' for d in range(1, DAYS + 1))
BLANKS = '<td class="d"></td>' * DAYS

def fields():
    return ('<div class="fields">店名 <span class="fld" style="width:52mm;"></span> '
            '<span class="fld" style="width:16mm;"></span> 年 '
            '<span class="fld" style="width:12mm;"></span> 月<br>'
            '衛生管理者 <span class="fld" style="width:38mm;"></span></div>')

def row(title, sub):
    s = f'<span>{sub}</span>' if sub else ""
    return f'<tr><td class="item"><b>{title}</b>{s}</td>{BLANKS}</tr>'

def sec(t):
    return f'<tr class="sec"><td colspan="{DAYS+1}">{t}</td></tr>'

def record_page(title, small, rows_html, legend, memo_head, footl, footr):
    return f'''<div class="page">
  <div class="head"><h1>{title}<small>{small}</small></h1>{fields()}</div>
  <table class="cal"><tr><th class="item">確認すること</th>{DAYHDR}</tr>{rows_html}</table>
  <div class="legend">{legend}</div>
  <table class="memo">
    <tr><th class="w-date">日付</th><th>{memo_head}</th><th class="w-sign">記入者</th></tr>
    <tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr>
  </table>
  <div class="foot"><span>{footl}</span><span>{footr}</span></div>
</div>'''

def howto_page(shop):
    laws = "".join(f"<li>{x}</li>" for x in shop["law"])
    pt, pb = shop["point"]
    return f'''<div class="page">
  <div class="head"><h1>{shop["name"]}の衛生管理記録表
    <small>{shop["note"]}／HACCPの考え方を取り入れた衛生管理　最初に1回だけ読めば、あとは毎日○を書くだけです</small></h1></div>

  <div class="law">
    <h3>守ること（食品衛生法・食中毒対策）</h3>
    <ul>{laws}</ul>
  </div>

  <div class="guide">
    <h3>1. 毎日やること</h3>
    閉店後に、3ページ目のその日の列に<b>上から○を入れていくだけ</b>です。1分かかりません。<br>
    「問題なし」なら○。何かあったときだけ×にして、下の特記事項に1行書きます。<br>
    4ページ目は、<b>その日に出した分類だけ</b>○を入れます。出していない分類は「／」で構いません。
  </div>

  <div class="guide">
    <h3>2. {pt}</h3>
    {pb}
  </div>

  <div class="guide">
    <h3>3. 保存と、保健所に聞かれたとき</h3>
    書いた紙は<b>ファイルに綴じて店に置いておく</b>だけで構いません。提出の義務はありません。保存期間は手引書に従ってください（1年程度が目安）。<br>
    <b>×がついた記録が残っていること自体は、問題になりません。</b>気づいて対応した記録が残っているほうが評価されます。<br>
    <b>この様式は例示です。</b>業種別手引書に指定の様式がある場合は、項目名をそちらに合わせてください。記録すべき内容が同じであれば、書式が違っても差し支えありません。
  </div>

  <div class="foot"><span>{shop["name"]}｜使い方</span><span>1 / 4</span></div>
</div>'''

def cellv(v):
    st = "text-align:center;font-size:11pt;"
    if v == "×":
        st += "color:#F0A202;font-weight:700;"
    return f'<td class="d" style="{st}">{v}</td>' if v else '<td class="d"></td>'

def rei_page(shop):
    hdr = "".join(f'<th class="day">{d}</th>' for d in range(1, 11))
    r1 = "".join(cellv(v) for v in ["○", "○", "／", "○", "×", "○", "○", "", "", ""])
    r2 = "".join(cellv(v) for v in ["○", "○", "／", "○", "○", "○", "○", "", "", ""])
    return f'''<div class="page">
  <div class="head"><h1>記入例<small>迷うのは最初の1週間だけです</small></h1></div>
  <table class="cal" style="margin-top:5mm;">
    <tr><th class="item">確認すること</th>{hdr}</tr>
    <tr><td class="item"><b>冷蔵庫の温度（10℃以下）</b><span>庫内の温度計を見る</span></td>{r1}</tr>
    <tr><td class="item"><b>手洗いの実施</b><span>作業前・トイレ後・生の食材を触った後</span></td>{r2}</tr>
  </table>
  <table class="memo" style="margin-top:3mm;">
    <tr><th class="w-date">日付</th><th>問題があったこと／どう対応したか</th><th class="w-sign">記入者</th></tr>
    <tr><td style="text-align:center;">5</td>
      <td style="font-size:10pt;">朝の時点で冷蔵庫が14℃。扉が半開きだった。閉めて2時間後に8℃を確認。中の食材は見た目とにおいを確認して使用。</td>
      <td style="text-align:center;">山田</td></tr>
    <tr><td></td><td></td><td></td></tr>
  </table>
  <div class="guide">
    <h3>使う記号は3つだけ</h3>
    <b>○</b> 確認した、問題なし　　<b>×</b> 問題があった（下の特記事項に1行書く）　　<b>／</b> 休業日、その日は該当なし
  </div>
  <div class="law">
    <h3>×は、書いたほうがいい</h3>
    <b>×がついた記録が残っていること自体は、問題になりません。</b>ずっと○だけが並んでいる記録のほうが「本当に見ているのか」と思われます。<br>
    大事なのは<b>気づいたこと</b>と<b>どう対応したか</b>が残っていることです。上の例のように1行で足ります。
  </div>
  <div class="foot"><span>{shop["name"]}｜記入例</span><span>2 / 4</span></div>
</div>'''

def build_html(shop):
    gen_rows = "".join(row(t, s) for t, s in BASE_GEN + shop["extra"])
    imp_rows = ""
    for stitle, rows in shop["imp"]:
        imp_rows += sec(stitle) + "".join(row(t, s) for t, s in rows)
    p3 = record_page("一般衛生管理の記録", shop["name"], gen_rows,
                     "<span><b>○</b>＝問題なし　<b>×</b>＝問題あり（下の特記事項に書く）　<b>／</b>＝休業日</span>"
                     "<span>記入は<b>1日1回</b>、閉店後にまとめてで構いません。</span>",
                     "問題があったこと／どう対応したか",
                     f'{shop["name"]}｜一般衛生管理', "3 / 4")
    p4 = record_page("重要管理の記録", f'{shop["name"]}／その日出したものだけ確認します', imp_rows,
                     "<span><b>○</b>＝問題なし　<b>×</b>＝問題あり　<b>／</b>＝その日出していない／休業日</span>"
                     "<span>温度を測った日は、数字を書いておくとより確実です。</span>",
                     "問題があったこと／どう対応したか（出さずに廃棄した・加熱し直した など）",
                     f'{shop["name"]}｜重要管理', "4 / 4")
    title = f'{shop["name"]}の衛生管理記録表（HACCPの考え方を取り入れた衛生管理）'
    return (f'<meta charset="utf-8">\n<title>{title}</title>\n{STYLE}\n'
            + howto_page(shop) + rei_page(shop) + p3 + p4)

# ---------- フォント埋め込み & PDF 化 ----------
def font_faces(text):
    ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
    ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    def get(u, b=False):
        r = urllib.request.Request(u, headers={"User-Agent": ua})
        with urllib.request.urlopen(r, context=ctx, timeout=120) as f:
            d = f.read()
        return d if b else d.decode()
    css = get("https://fonts.googleapis.com/css2?family="
              + urllib.parse.quote("Noto Sans JP:wght@400;700")
              + "&text=" + urllib.parse.quote(text))
    out = []
    for blk in re.findall(r"@font-face\s*\{[^}]*\}", css):
        w = re.search(r"font-weight:\s*(\d+)", blk).group(1)
        u = re.search(r"url\((https://[^)]+)\)", blk).group(1)
        b64 = base64.b64encode(get(u, True)).decode()
        out.append("@font-face{font-family:'Noto Sans JP';font-style:normal;"
                   f"font-weight:{w};src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    return "\n".join(out)

def main():
    htmls = {s["slug"]: build_html(s) for s in SHOPS}
    chars = set("".join(htmls.values()))
    chars |= set("0123456789○×／℃−")
    faces = font_faces("".join(sorted(c for c in chars if c.strip())))
    for slug, html in htmls.items():
        html = html.replace("<style>", "<style>\n" + faces + "\n", 1)
        tmp = f"/tmp/_haccp_{slug}.html"
        open(tmp, "w", encoding="utf-8").write(html)
        pdf = f"{OUT}/haccp-{slug}.pdf"
        subprocess.run(["/opt/pw-browsers/chromium", "--headless", "--no-sandbox",
                        "--disable-gpu", "--no-pdf-header-footer",
                        "--run-all-compositor-stages-before-draw",
                        "--virtual-time-budget=8000",
                        f"--print-to-pdf={pdf}", "file://" + tmp],
                       check=True, capture_output=True)
        print(slug, os.path.getsize(pdf))

if __name__ == "__main__":
    main()
