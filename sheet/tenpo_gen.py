# 店舗運営の書式3種（シフト表／発注表／新人教育チェック表）
import base64, os, re, ssl, subprocess, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

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
h1{ font-size:18pt; font-weight:700; line-height:1.2; }
h1 small{ display:block; font-size:9pt; font-weight:400; opacity:.7; margin-top:1mm; }
.fields{ font-size:10pt; text-align:right; line-height:2.1; white-space:nowrap; }
.fld{ display:inline-block; border-bottom:1.2pt solid var(--line); height:6mm; }
table{ width:100%; border-collapse:collapse; table-layout:fixed; }
th,td{ border:1pt solid var(--line); }
th{ background:rgba(43,58,85,.08); font-weight:700; font-size:8.4pt; padding:1.4mm .5mm;
  text-align:center; }
td{ font-size:9.5pt; padding:.8mm 2mm; }
.band{ margin-top:4mm; border-left:2.6pt solid var(--accent); padding-left:4mm;
  font-size:11.5pt; line-height:1.6; }
.band b{ font-weight:700; }
.guide{ margin-top:3.5mm; border:1.2pt solid var(--line); padding:3mm 4.5mm;
  font-size:9.5pt; line-height:1.7; }
.guide h3{ font-size:11pt; font-weight:700; margin-bottom:1.5mm; }
.accentbox{ border:1.8pt solid var(--accent); }
.legend{ margin-top:2.5mm; font-size:9pt; opacity:.85; }
.legend b{ font-weight:700; }
.foot{ position:absolute; left:12mm; right:12mm; bottom:5mm; font-size:8pt;
  opacity:.5; display:flex; justify-content:space-between; }
.sun{ background:rgba(240,162,2,.13); }
</style>"""


def page(inner, footl, footr):
    return f'<div class="page">{inner}<div class="foot"><span>{footl}</span>' \
           f'<span>{footr}</span></div></div>'


def head(title, small, fields=""):
    f = f'<div class="fields">{fields}</div>' if fields else ""
    return f'<div class="head"><h1>{title}<small>{small}</small></h1>{f}</div>'


MONTH_FIELDS = ('店名 <span class="fld" style="width:44mm;"></span> '
                '<span class="fld" style="width:14mm;"></span> 年 '
                '<span class="fld" style="width:12mm;"></span> 月分')


# ============================ シフト表 ============================
def shift_pages():
    STAFF = 13

    # P1 希望の回収
    hdr = "".join(f'<th style="width:7.2mm;">{d}</th>' for d in range(1, 32))
    body = ""
    for _ in range(STAFF):
        body += ('<tr><td style="height:8.6mm;"></td>'
                 + '<td></td>' * 31 + '<td></td></tr>')
    p1 = head("希望休の回収表",
              "配るのはこの1枚だけ。提出されたものを見ながら、次のページで組みます",
              MONTH_FIELDS) + f'''
  <div class="band">
    <b>毎月〈締切日〉までに、この紙をスタッフに回す。</b>
    出せる日に○、休みたい日に×、どちらでもいい日は空欄。
  </div>
  <table style="margin-top:4mm;">
    <tr><th style="width:30mm;">名前</th>{hdr}<th style="width:34mm;">希望・連絡事項</th></tr>
    {body}
  </table>
  <div class="legend">
    <b>○</b>＝出られる　　<b>×</b>＝休みたい　　<b>空欄</b>＝どちらでもいい
    提出締切　<span class="fld" style="width:16mm;"></span> 日まで
  </div>
  <div class="guide" style="margin-top:3mm;padding:2.5mm 4.5mm;">
    <h3 style="font-size:10.5pt;">締切を過ぎた人の扱いを、先に決めておいてください</h3>
    「出していない人は、こちらで入れる」と最初に言っておくだけで、催促がほぼ要らなくなります。
    毎月おなじ日に配って、おなじ日に締める。日付を動かさないことがいちばん効きます。
  </div>'''

    # P2/P3 確定シフト
    def fixed(days, no, label):
        h = "".join(f'<th style="width:{224/len(days):.2f}mm;">{d}</th>' for d in days)
        b = ""
        for _ in range(STAFF):
            b += '<tr><td style="height:9.4mm;"></td>' + '<td></td>' * len(days) + '</tr>'
        return head(f"確定シフト表（{label}）",
                    "セルには時間を書きます（例：17-23）。休みは斜線で消してください",
                    MONTH_FIELDS) + f'''
  <table style="margin-top:4mm;">
    <tr><th style="width:32mm;">名前</th>{h}</tr>
    {b}
    <tr><th style="background:rgba(240,162,2,.16);">出勤人数</th>{"<td></td>" * len(days)}</tr>
  </table>
  <div class="guide" style="margin-top:3.5mm;">
    <h3>先に「人数」を決めてから、名前を入れてください</h3>
    名前から埋めると、忙しい日に人が足りない組み方になります。<br>
    <b>曜日ごとの必要人数を先に決めて</b>、いちばん下の行に書いてから、上に名前を入れる。この順番だけで、組む時間がかなり短くなります。
  </div>'''

    return [
        page(p1, "シフト表", "1 / 3　希望休の回収"),
        page(fixed(range(1, 17), 2, "1日〜16日"), "シフト表", "2 / 3　確定シフト 前半"),
        page(fixed(range(17, 32), 3, "17日〜31日"), "シフト表", "3 / 3　確定シフト 後半"),
    ]


# ============================ 発注表 ============================
def order_pages():
    ROWS = 19
    master_rows = ""
    for _ in range(ROWS):
        master_rows += ('<tr><td style="height:6.6mm;"></td><td></td><td></td>'
                        '<td></td><td></td></tr>')
    p1 = head("発注リスト（お店の定番品）",
              "最初に1回だけ書けば、あとは毎週これを見るだけになります") + f'''
  <div class="band">
    <b>発注で時間がかかるのは、注文することではなく「何を頼むか思い出すこと」です。</b><br>
    一度この紙に書き出してしまえば、次からは上から見ていくだけになります。
  </div>
  <table style="margin-top:4mm;">
    <tr><th style="width:62mm;">品名</th><th style="width:44mm;">業者</th>
        <th style="width:26mm;">単位</th>
        <th style="width:44mm;">これを切ったら頼む（発注点）</th>
        <th>届く曜日・締切</th></tr>
    {master_rows}
  </table>
  <div class="guide" style="margin-top:3mm;padding:2.5mm 4.5mm;">
    <h3 style="font-size:10.5pt;">「発注点」だけは、必ず埋めてください</h3>
    残りいくつになったら頼むか、という数字です。ここが決まっていないと、毎回その場で判断することになります。
    <b>判断が要らなくなると、発注は誰にでも任せられます。</b>
  </div>'''

    week_rows = ""
    for _ in range(ROWS):
        week_rows += ('<tr><td style="height:6.6mm;"></td>' + '<td></td>' * 7
                      + '<td></td></tr>')
    days = ["月", "火", "水", "木", "金", "土", "日"]
    dh = "".join(f'<th style="width:17mm;">{d}</th>' for d in days)
    p2 = head("週の発注チェック表",
              "頼んだ日に○。届いたら○に一本線を入れて消します",
              '<span class="fld" style="width:14mm;"></span> 月 '
              '<span class="fld" style="width:14mm;"></span> 日の週') + f'''
  <table style="margin-top:4mm;">
    <tr><th style="width:74mm;">品名</th>{dh}<th>メモ（欠品・値上がりなど）</th></tr>
    {week_rows}
  </table>
  <div class="guide" style="margin-top:3mm;padding:2.5mm 4.5mm;">
    <h3 style="font-size:10.5pt;">メモ欄は、来月の自分のためにあります</h3>
    「欠品した」「値上がりした」「多すぎた」を一言だけ残しておくと、
    次の棚卸で原価率が動いたときに、理由がすぐ分かります。
  </div>'''
    return [page(p1, "発注表", "1 / 2　定番品リスト"),
            page(p2, "発注表", "2 / 2　週の発注チェック")]


# ============================ 新人教育 ============================
def train_pages():
    p1 = head("新人が入ったら、この1枚",
              "教える人が変わっても、同じ順番で教えられるようにするための表です") + '''
  <div class="band">
    <b>新人が辞める理由の多くは、仕事がきついことではありません。</b><br>
    「何を覚えたら一人前なのか分からない」まま、毎回ちがう人にちがうことを言われることです。
  </div>

  <div class="guide accentbox" style="padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">この表の使い方は3つだけ</h3>
    1. 次のページに、<b>自分の店で教えることを上から順に書く</b>（最初の1回だけ）<br>
    2. 教えたら「説明した」に日付。やらせてみたら「やってみた」に日付。<br>
    3. <b>一人でできた日に、3つめの欄に日付を入れる。ここが埋まったら、その項目は終わりです。</b>
  </div>

  <div class="guide" style="margin-top:3mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">順番のつけ方</h3>
    上から<b>「その日いちばん使うもの」</b>の順に並べてください。きれいな分類は要りません。<br>
    ・初日に必要なこと（入り方、着替え、手洗い、休憩、あいさつ）<br>
    ・1週目に必要なこと（その人が実際にやる持ち場のことだけ）<br>
    ・慣れてからでいいこと（レジ締め、発注、クレーム対応）<br>
    <b>初日に全部教えないでください。</b>覚えられる量を超えると、本人は「向いていない」と思い込みます。
  </div>

  <div class="guide" style="margin-top:3mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">教える側が変わるときは、この紙を渡す</h3>
    日付が入っている項目は、もう教えなくていい項目です。<br>
    これがあるだけで「前も同じこと言われた」「誰も教えてくれなかった」が両方なくなります。
  </div>'''

    rows = ""
    for _ in range(17):
        rows += ('<tr><td style="height:7.4mm;"></td><td></td><td></td>'
                 '<td></td><td></td></tr>')
    p2 = head("覚えることリスト",
              "上から順に。日付を入れるだけです",
              '名前 <span class="fld" style="width:40mm;"></span><br>'
              '入った日 <span class="fld" style="width:14mm;"></span> 月 '
              '<span class="fld" style="width:14mm;"></span> 日') + f'''
  <table style="margin-top:4mm;">
    <tr><th style="width:104mm;">覚えること</th>
        <th style="width:32mm;">説明した</th>
        <th style="width:32mm;">やってみた</th>
        <th style="width:36mm;background:rgba(240,162,2,.16);">一人でできた</th>
        <th>教えた人</th></tr>
    {rows}
  </table>
  <div class="guide" style="margin-top:3mm;padding:2.5mm 4.5mm;">
    <h3 style="font-size:10.5pt;">全部埋まらなくていい</h3>
    上から3分の1が埋まれば、その人はもう戦力です。残りは働きながらで構いません。
    <b>埋まっていない欄を責める道具にはしないでください。</b>そうなった瞬間、この紙は使われなくなります。
  </div>'''
    return [page(p1, "新人教育チェック表", "1 / 2　使い方"),
            page(p2, "新人教育チェック表", "2 / 2　覚えることリスト")]


# ============================ 出力 ============================
PRODUCTS = {
    "shift":  ("シフト表（希望休の回収＋確定シフト）", shift_pages),
    "hacchu": ("発注表（定番品リスト＋週の発注チェック）", order_pages),
    "kyoiku": ("新人教育チェック表", train_pages),
}


def font_faces(text):
    ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
    ua = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120 Safari/537.36")
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
    htmls = {}
    for slug, (title, fn) in PRODUCTS.items():
        htmls[slug] = (f'<meta charset="utf-8">\n<title>{title}</title>\n'
                       + STYLE + "\n" + "\n".join(fn()))
    chars = set("".join(htmls.values())) | set("0123456789○×／−")
    faces = font_faces("".join(sorted(c for c in chars if c.strip())))
    for slug, html in htmls.items():
        html = html.replace("<style>", "<style>\n" + faces + "\n", 1)
        tmp = f"/tmp/_{slug}.html"
        open(tmp, "w", encoding="utf-8").write(html)
        pdf = os.path.join(HERE, f"{slug}.pdf")
        subprocess.run(["/opt/pw-browsers/chromium", "--headless", "--no-sandbox",
                        "--disable-gpu", "--no-pdf-header-footer",
                        "--run-all-compositor-stages-before-draw",
                        "--virtual-time-budget=10000",
                        f"--print-to-pdf={pdf}", "file://" + tmp],
                       check=True, capture_output=True)
        print(slug, os.path.getsize(pdf))


if __name__ == "__main__":
    main()
