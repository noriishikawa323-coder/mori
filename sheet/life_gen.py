# 生活まわりのシート群（単発バイト／ポイント失効／年払いカレンダー ほか）
import base64, os, re, ssl, subprocess, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))

STYLE = """<style>
:root{ --navy:#2B3A55; --accent:#F0A202; --line:#2B3A55; }
@page{ size:A4; margin:0; }
*{ box-sizing:border-box; margin:0; padding:0; }
html,body{ background:#fff; }
body{ font-family:"Noto Sans JP","IPAGothic",sans-serif; color:var(--navy);
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.page{ width:210mm; height:297mm; padding:15mm; page-break-after:always;
  position:relative; display:flex; flex-direction:column; }
.page.land{ width:297mm; height:210mm; padding:10mm 12mm; }
.page:last-child{ page-break-after:auto; }
h1{ font-size:23pt; font-weight:700; line-height:1.18; letter-spacing:.02em; }
h1 small{ display:block; font-size:9.5pt; font-weight:400; opacity:.7; margin-top:1.5mm; }
.sub{ font-size:11pt; margin-top:2mm; opacity:.78; }
.note{ font-size:9pt; opacity:.7; }
.head{ display:flex; align-items:flex-end; justify-content:space-between; gap:8mm; }
.fields{ font-size:10pt; text-align:right; line-height:2; white-space:nowrap; }
.fld{ display:inline-block; border-bottom:1.2pt solid var(--line); height:6mm; }
.band{ margin-top:5mm; border-left:2.6pt solid var(--accent); padding-left:4mm;
  font-size:11.5pt; line-height:1.65; }
.band b{ font-weight:700; }
.box{ border:1.2pt solid var(--line); padding:3mm 4.5mm; font-size:9.6pt;
  line-height:1.7; margin-top:3.5mm; }
.box h3{ font-size:11pt; font-weight:700; margin-bottom:1.5mm; }
.box .grp{ margin-top:2.5mm; }
.accentbox{ border:1.8pt solid var(--accent); }
ol.steps{ list-style:none; counter-reset:s; margin-top:2mm; }
ol.steps li{ counter-increment:s; position:relative; padding-left:10mm;
  margin-bottom:3mm; font-size:11pt; line-height:1.6; }
ol.steps li::before{ content:counter(s); position:absolute; left:0; top:.3mm;
  width:7mm; height:7mm; border-radius:50%; background:var(--navy); color:#fff;
  font-size:9.5pt; display:flex; align-items:center; justify-content:center; }
table{ width:100%; border-collapse:collapse; table-layout:fixed; }
th,td{ border:1pt solid var(--line); }
th{ background:rgba(43,58,85,.08); font-weight:700; font-size:8.8pt;
  padding:1.6mm .8mm; text-align:center; line-height:1.35; }
td{ font-size:10pt; padding:1mm 2mm; }
.hl th{ background:rgba(240,162,2,.2); }
.sum td{ background:rgba(240,162,2,.16); font-weight:700; height:9mm; }
.cb{ display:inline-block; width:5mm; height:5mm; border:1.2pt solid var(--line);
  vertical-align:-.8mm; margin-right:1.5mm; }
.award{ margin-top:auto; border:1.8pt solid var(--accent); padding:4.5mm 5mm; }
.award .big{ font-size:14pt; display:flex; align-items:flex-end; gap:3mm; }
.award .big .money{ flex:1; border-bottom:1.6pt solid var(--accent); height:10mm; }
.award .small{ font-size:10pt; margin-top:2.5mm; opacity:.85; }
.mini{ display:inline-block; width:22mm; border-bottom:1pt solid var(--line); }
pre{ font-family:"Noto Sans JP","IPAGothic",monospace; font-size:10pt;
  line-height:1.9; white-space:pre-wrap; border:1.2pt solid var(--line);
  padding:4mm 5mm; margin-top:3mm; }
.foot{ position:absolute; left:15mm; right:15mm; bottom:7mm; font-size:8pt;
  opacity:.5; display:flex; justify-content:space-between; }
.page.land .foot{ left:12mm; right:12mm; bottom:5mm; }
</style>"""


def page(inner, footl, footr, land=False):
    cls = "page land" if land else "page"
    return (f'<div class="{cls}">{inner}'
            f'<div class="foot"><span>{footl}</span><span>{footr}</span></div></div>')


def rows(n, cells, h="7.4mm"):
    return "".join(f'<tr><td style="height:{h};"></td>' + "<td></td>" * (cells - 1) + "</tr>"
                   for _ in range(n))


# =================== 1. 単発バイトの稼働記録＋確定申告 ===================
def baito():
    p1 = '''<h1>単発バイトの稼働記録<small>確定申告のために、あとから思い出せる形で残しておく1枚です</small></h1>

  <div class="band">
    <b>働いた日の帰り道、電車の中で1行だけ書く。</b><br>
    アプリを開けば履歴は見られますが、<b>複数のアプリを使っていると合計が出せません。</b>
  </div>

  <div class="box accentbox">
    <h3>なぜ記録が要るのか</h3>
    単発バイトは、給与として払われるものと、報酬（業務委託）として払われるものが混ざります。
    さらにアプリを複数使っていると、<b>年間でいくら稼いだのかが誰にも分からなくなります。</b><br>
    分からないまま年を越すと、確定申告が要るのかどうかも判断できません。
    このシートは、その判断ができる状態にしておくためのものです。
  </div>

  <div class="box">
    <h3>「20万円の壁」の数え方</h3>
    よく言われる20万円は、<b>会社員などで給与を1か所からもらっている人</b>が、
    それ以外の所得（給与以外の副業の所得など）が20万円以下なら
    <b>所得税の確定申告を省略できる</b>という話です。<br>
    ここで数えるのは「売上」ではなく<b>所得（＝売上−経費）</b>です。交通費や道具代を引いた後の金額。<br>
    <div class="grp"><b>ただし、次の点に注意してください。</b><br>
    ・単発バイトが<b>給与</b>として払われている場合は、この20万円の話とは扱いが変わります（2か所以上から給与をもらう場合など）<br>
    ・所得税の申告が不要でも、<b>住民税の申告は必要</b>な場合があります<br>
    ・払われ方（給与か報酬か）は、アプリの明細や源泉徴収票で確認できます</div>
    <div class="grp">迷ったら、この記録を持って市区町村の窓口か税務署に聞くのが早いです。
    <b>「いくら稼いだか分からない」状態で相談に行くと、そこで詰みます。</b>だから記録します。</div>
  </div>

  <div class="box">
    <h3>経費になりうるもの（レシートは捨てないでください）</h3>
    交通費／作業に使う道具・服・靴／現場で必要な備品／通信費の一部　など。<br>
    仕事のために使ったと説明できるものが対象です。<b>家事と共用のものは、使った割合の分だけ</b>になります。
    判断に迷うものは「迷った」とメモして残しておけば、あとで聞けます。
  </div>'''

    hdr = ('<tr class="hl"><th style="width:16mm;">日付</th><th style="width:38mm;">アプリ・会社名</th>'
           '<th style="width:32mm;">仕事の内容</th><th style="width:18mm;">時間</th>'
           '<th style="width:24mm;">もらった額</th><th style="width:22mm;">交通費</th>'
           '<th>メモ（給与／報酬・立替など）</th></tr>')
    p2 = f'''<div class="head">
    <h1 style="font-size:20pt;">稼働の記録<small>働いた日に1行。1枚で24日分</small></h1>
    <div class="fields"><span class="fld" style="width:16mm;"></span> 年
      <span class="fld" style="width:12mm;"></span> 月</div>
  </div>
  <table style="margin-top:4mm;">{hdr}{rows(24, 7, "7.6mm")}
    <tr class="sum"><td colspan="4" style="text-align:right;">この月の合計</td>
      <td></td><td></td><td></td></tr>
  </table>
  <div class="box" style="margin-top:3mm;">
    <h3>メモ欄に書いておくと後で助かること</h3>
    <b>給与</b>として振り込まれたか、<b>報酬</b>として振り込まれたか。明細に「源泉徴収」と書いてあれば報酬の可能性が高いです。<br>
    立て替えたお金、キャンセルされた案件、現地までの経路（あとで交通費を思い出せます）。
  </div>'''

    mh = ('<tr class="hl"><th style="width:20mm;">月</th><th>もらった額の合計</th>'
          '<th>経費の合計</th><th>差し引き（所得）</th><th style="width:34mm;">メモ</th></tr>')
    mrows = "".join(f'<tr><td style="height:8.6mm;text-align:center;">{m}月</td>'
                    "<td></td><td></td><td></td><td></td></tr>" for m in range(1, 13))
    p3 = f'''<h1 style="font-size:20pt;">1年のまとめ<small>毎月の合計を、ここに書き写すだけ</small></h1>
  <p class="sub">12月まで埋まったら、いちばん下が「1年でいくら稼いだか」です。</p>
  <table style="margin-top:4mm;">{mh}{mrows}
    <tr class="sum"><td style="text-align:center;">年計</td><td></td><td></td><td></td><td></td></tr>
  </table>

  <div class="box accentbox">
    <h3>年が明けたら、この紙を持って</h3>
    ・<b>源泉徴収票</b>（本業がある人）<br>
    ・<b>各アプリの支払調書・支払明細</b>（アプリ内でダウンロードできることが多いです）<br>
    ・<b>経費のレシート</b><br>
    この3つとこのシートを揃えれば、申告が要るかどうかの判断も、実際の申告も進みます。
    <b>この記事のシートは税務の判断そのものを代わりにするものではありません。</b>最終的な扱いは税務署・税理士に確認してください。
  </div>'''

    return [page(p1, "単発バイトの稼働記録", "1 / 3　使い方"),
            page(p2, "単発バイトの稼働記録", "2 / 3　稼働の記録"),
            page(p3, "単発バイトの稼働記録", "3 / 3　1年のまとめ")]


# =================== 2. ポイントの失効管理 ===================
def point():
    p1 = '''<h1>ポイントの失効管理シート<small>貯めることより、失わないことのほうが効きます</small></h1>

  <div class="band">
    <b>毎月〈1日〉に、この1枚を見る。</b><br>
    期限が今月のものがあれば、その場で使う。なければ閉じる。それだけです。
  </div>

  <div class="box accentbox">
    <h3>失効に気づけない理由</h3>
    ポイントの期限は<b>アプリの中にしか書いていません。</b>そして通知は、他の通知に埋もれます。<br>
    しかも失効しても、誰も教えてくれません。<b>減ったことに気づかない損は、いちばん取り返しにくい</b>です。
  </div>

  <div class="box">
    <h3>最初に1回だけやること</h3>
    <ol class="steps" style="margin-top:1.5mm;">
      <li><b>使っているポイントを、次のページに書き出す。</b><br>
        <span class="note">全部でなくて構いません。よく使う上位5つだけでも効果があります。</span></li>
      <li><b>それぞれの「期限のルール」を書く。</b><br>
        <span class="note">期間限定なのか、最終利用日から◯ヶ月なのか。アプリのヘルプに必ず書いてあります。</span></li>
      <li><b>期間限定のものは、期限の日付をそのまま書く。</b><br>
        <span class="note">ここが埋まれば、あとは毎月見るだけです。</span></li>
    </ol>
  </div>

  <div class="box">
    <h3>いちばん効くのは「最終利用日で延びるもの」を知っておくこと</h3>
    ポイントには、<b>使うたびに期限が先に延びるタイプ</b>があります。
    このタイプは、少額でも定期的に使っていれば実質失効しません。<br>
    逆に<b>期間限定ポイント</b>は延びません。ここだけ日付を管理すれば、大きな失効はほぼ防げます。
  </div>

  <div class="box">
    <h3>貯め方は増やさないでください</h3>
    種類を増やすほど、管理できなくなって失効します。<b>寄せたほうが得</b>です。
    このシートに書いてみて、使っていないものが見つかったら、そこはもう追いかけないと決めてしまってください。
  </div>'''

    hdr = ('<tr class="hl"><th style="width:34mm;">ポイント名</th>'
           '<th style="width:26mm;">いまの残高</th>'
           '<th style="width:44mm;">期限のルール</th>'
           '<th style="width:26mm;">次の期限</th>'
           '<th style="width:34mm;">何に使うか決めておく</th>'
           '<th>確認した日</th></tr>')
    p2 = f'''<h1 style="font-size:20pt;">ポイント一覧<small>毎月1日に、残高と期限だけ見直します</small></h1>
  <table style="margin-top:4mm;">{hdr}{rows(16, 6, "9mm")}</table>

  <div class="box">
    <h3>「何に使うか決めておく」欄について</h3>
    期限が近いのに使えない理由の多くは、<b>その場で使い道を考えるから</b>です。<br>
    「コンビニのコーヒー」「ドラッグストアの日用品」など、<b>いつでも使える先を1つ決めて書いておく</b>と、期限前に確実に消化できます。
  </div>

  <div class="award">
    <div class="big">今年、失効させずに使えた額 <span class="money"></span> 円</div>
    <div class="small">見直した月を塗る　○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○</div>
  </div>'''
    return [page(p1, "ポイントの失効管理", "1 / 2　使い方"),
            page(p2, "ポイントの失効管理", "2 / 2　ポイント一覧")]


# =================== 3. 年払いカレンダー ===================
def nenbarai():
    p1 = '''<h1>年払いカレンダー<small>忘れた頃に大きい金額が引き落ちる、を防ぐための1枚</small></h1>

  <div class="band">
    <b>1年に1回だけ書く。あとは毎月の家計を見るときに、横目で見るだけ。</b><br>
    毎月の支出は把握できていても、<b>年1回の支出だけは毎回きれいに忘れます。</b>
  </div>

  <div class="box accentbox">
    <h3>これは「節約」の紙ではありません</h3>
    年払いのものを減らそう、という話ではありません。<br>
    <b>いつ、いくら出ていくかを、事前に知っている状態にするだけ</b>の紙です。<br>
    残高不足も、慌てての分割払いも、たいてい「知らなかった」から起きます。
  </div>

  <div class="box">
    <h3>書き出すもの（心当たりのあるものだけで構いません）</h3>
    <div><b>車</b>　車検／自動車税／任意保険／タイヤ交換</div>
    <div class="grp"><b>住まい</b>　火災保険／更新料／固定資産税／町内会費</div>
    <div class="grp"><b>お金</b>　カードの年会費／サブスクの年払い／NHK／各種保険</div>
    <div class="grp"><b>暮らし</b>　健康診断／予防接種／帰省／お中元お歳暮／誕生日</div>
    <div class="grp"><b>仕事</b>　資格の更新／組合費／確定申告での納税</div>
  </div>

  <div class="box">
    <h3>金額が分からないものは「去年いくらだったか」でいい</h3>
    正確でなくて構いません。<b>ゼロと書いてあるより、だいたいの数字が書いてあるほうが100倍役に立ちます。</b><br>
    分からないものは空欄にせず「？」と書いて、来年その欄を埋めてください。
  </div>

  <div class="box">
    <h3>いちばん下の「毎月いくら貯めておけばいいか」欄</h3>
    年間の合計を12で割った数字です。これが<b>毎月よけておくべき額</b>になります。<br>
    この金額を普段の生活費と分けておくだけで、年1回の出費が「事件」ではなくなります。
  </div>'''

    mh = ('<tr class="hl"><th style="width:16mm;">月</th>'
          '<th>何が来るか</th><th style="width:28mm;">いくら</th>'
          '<th style="width:22mm;">払った</th></tr>')
    body = ""
    for m in range(1, 13):
        body += (f'<tr><td style="height:12.6mm;text-align:center;font-weight:700;">{m}月</td>'
                 '<td></td><td></td><td style="text-align:center;">'
                 '<span class="cb"></span></td></tr>')
    p2 = f'''<div class="head">
    <h1 style="font-size:20pt;">1年に来るお金<small>金額が分からないものは「？」でOK</small></h1>
    <div class="fields"><span class="fld" style="width:18mm;"></span> 年</div>
  </div>
  <table style="margin-top:4mm;">{mh}{body}
    <tr class="sum"><td style="text-align:center;">合計</td>
      <td style="text-align:right;">1年でこれだけ出ていきます　→</td><td></td><td></td></tr>
  </table>

  <div class="award">
    <div class="big">毎月よけておく額（合計 ÷ 12） <span class="money"></span> 円</div>
    <div class="small">この額を生活費と分けておけば、年1回の出費で慌てることがなくなります。</div>
  </div>'''
    return [page(p1, "年払いカレンダー", "1 / 2　使い方"),
            page(p2, "年払いカレンダー", "2 / 2　1年に来るお金")]


PRODUCTS = {
    "baito":    ("単発バイトの稼働記録＋確定申告シート", baito),
    "point":    ("ポイントの失効管理シート", point),
    "nenbarai": ("年払いカレンダー", nenbarai),
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


def build(products=None):
    products = products or PRODUCTS
    htmls = {s: (f'<meta charset="utf-8">\n<title>{t}</title>\n' + STYLE + "\n"
                 + "\n".join(fn()))
             for s, (t, fn) in products.items()}
    chars = set("".join(htmls.values())) | set("0123456789○×／−？")
    faces = font_faces("".join(sorted(c for c in chars if c.strip())))
    for slug, html in htmls.items():
        html = html.replace("<style>", "<style>\n" + faces + "\n", 1)
        tmp = f"/tmp/_life_{slug}.html"
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
    build()


# =================== 4. 親の情報シート ===================
def oya():
    p1 = '''<h1>親のことを、1枚に<small>倒れてからでは、誰も答えられません</small></h1>

  <div class="band">
    <b>次に実家に帰ったとき、親と一緒に座って、この1枚を埋める。</b><br>
    30分あれば終わります。今日でなくていいので、<b>次に会う日には持っていってください。</b>
  </div>

  <div class="box accentbox">
    <h3>これが要る場面は、ある日いきなり来ます</h3>
    親が救急で運ばれたとき、病院で最初に聞かれるのは、<b>保険証・かかりつけ・飲んでいる薬</b>です。<br>
    そのあと、入院の手続き、支払い、家の鍵、ペット、契約の停止と続きます。<br>
    どれも本人しか知らないことばかりで、<b>本人が答えられない状態で必要になります。</b>
  </div>

  <div class="box">
    <h3>聞き方に困ったら</h3>
    お金の話から入ると、たいてい嫌がられます。<b>健康の話から入ってください。</b><br>
    「かかりつけどこだっけ」「薬なに飲んでる」なら、普通の会話として聞けます。
    その流れで保険証の場所を聞き、最後に「何かあったときのために」で残りを埋める。<br>
    <div class="grp"><b>全部埋まらなくて構いません。</b>2ページ目の上半分（健康のこと）だけでも、あるのと無いのとでは全然違います。</div>
  </div>

  <div class="box">
    <h3>書いたあと</h3>
    ・<b>兄弟がいるなら、写真を撮って共有してください。</b>1人だけが持っていても意味がありません<br>
    ・原本は自分の家に置く。実家に置くと、実家に入れないときに詰みます<br>
    ・<b>暗証番号やパスワードは書かないでください。</b>「どこに書いてあるか」までにとどめます<br>
    ・1年に1回、正月にでも見直す。薬とかかりつけは変わります
  </div>

  <div class="box">
    <h3>この紙を、親に見せるとき</h3>
    「終活」という言葉は使わないほうがうまくいきます。<br>
    <b>「自分が困るから書いてほしい」</b>と言うと、たいてい通ります。実際そのとおりなので。
  </div>'''

    def sec(t):
        return (f'<tr><td colspan="2" style="background:rgba(240,162,2,.18);'
                f'font-weight:700;font-size:10pt;height:7mm;">{t}</td></tr>')

    def item(label, hint="", h="10mm"):
        sub = f'<span class="note" style="display:block;">{hint}</span>' if hint else ""
        return (f'<tr><td style="width:52mm;font-size:9.6pt;height:{h};">'
                f'<b>{label}</b>{sub}</td><td></td></tr>')

    t1 = (sec("本人のこと")
          + item("名前・生年月日")
          + item("住所・電話")
          + item("マイナンバーカード／保険証", "どこにしまってあるか（番号は書かない）")
          + sec("健康のこと　※ここだけでも埋めてください")
          + item("かかりつけの病院", "病院名・診療科・電話")
          + item("持病・手術歴")
          + item("飲んでいる薬", "お薬手帳の場所でも可")
          + item("アレルギー・輸血の可否")
          + item("介護保険の認定", "あり／なし・担当ケアマネの連絡先")
          + sec("連絡先")
          + item("兄弟・親族", "名前と電話")
          + item("近所で頼れる人", "名前と電話")
          + item("かかりつけ以外の連絡先", "施設・ヘルパーなど"))

    t2 = (sec("お金のこと　※場所だけ。番号や暗証番号は書かない")
          + item("使っている銀行", "銀行名・支店。通帳の場所")
          + item("年金", "受け取り口座・基礎年金番号の書類の場所")
          + item("保険", "生命保険・医療保険の会社名と証券の場所")
          + item("クレジットカード", "会社名だけ")
          + sec("家のこと")
          + item("持ち家／賃貸", "賃貸なら管理会社と連絡先")
          + item("鍵の場所・預け先")
          + item("契約しているもの", "電気・ガス・水道・通信・新聞・宅配など")
          + sec("本人の希望　※話せる範囲で")
          + item("延命治療について", "希望を聞けていれば", "12mm")
          + item("入院・施設について", "", "12mm")
          + item("その他、伝えておきたいこと", "", "14mm"))

    p2 = f'''<div class="head">
    <h1 style="font-size:20pt;">親の情報シート ①<small>健康と連絡先。ここが最優先です</small></h1>
    <div class="fields">書いた日 <span class="fld" style="width:14mm;"></span> 年
      <span class="fld" style="width:10mm;"></span> 月</div>
  </div>
  <table style="margin-top:4mm;">{t1}</table>
  <div class="box" style="margin-top:3mm;">
    <b>この紙は、写真に撮って兄弟と共有してください。</b>
    1人だけが持っていると、その1人がいないときに使えません。
  </div>'''

    p3 = f'''<h1 style="font-size:20pt;">親の情報シート ②<small>お金・家・希望。場所が分かればそれで十分です</small></h1>
  <table style="margin-top:4mm;">{t2}</table>
  <div class="box accentbox" style="margin-top:3mm;">
    <b>暗証番号・パスワード・口座番号は書かないでください。</b>
    この紙は持ち歩くことがあります。「どこを見れば分かるか」までで止めておくのが安全です。
  </div>'''
    return [page(p1, "親のことを1枚に", "1 / 3　使い方"),
            page(p2, "親のことを1枚に", "2 / 3　健康と連絡先"),
            page(p3, "親のことを1枚に", "3 / 3　お金・家・希望")]


# =================== 5. 引っ越し手続きチェックリスト ===================
def hikkoshi():
    def block(title, items, h="8.2mm"):
        rs = ""
        for label, when, memo in items:
            rs += (f'<tr><td style="height:{h};text-align:center;width:14mm;">'
                   f'<span class="cb"></span></td>'
                   f'<td style="width:64mm;font-size:9.6pt;"><b>{label}</b></td>'
                   f'<td style="width:34mm;font-size:9pt;">{when}</td>'
                   f'<td style="font-size:9pt;">{memo}</td></tr>')
        return (f'<tr><td colspan="4" style="background:rgba(240,162,2,.18);'
                f'font-weight:700;font-size:10pt;height:7mm;">{title}</td></tr>' + rs)

    hdr = ('<tr class="hl"><th style="width:14mm;">済</th><th>やること</th>'
           '<th style="width:34mm;">いつ</th><th>メモ・持ち物</th></tr>')

    b1 = block("引っ越しが決まったら", [
        ("いまの家の解約を連絡する", "決まってすぐ", "契約書を見る。1〜2か月前の通知が多い"),
        ("引っ越し業者を決める", "1か月前まで", "土日と月末は高い"),
        ("駐車場・駐輪場の解約", "1か月前", ""),
        ("子どもの転校の連絡", "決まってすぐ", "学校に在学証明などを頼む"),
        ("粗大ごみの申し込み", "2週間前", "自治体は予約制。直前は埋まります"),
    ])
    b2 = block("いまの市区町村でやること", [
        ("転出届を出す", "引っ越し前後2週間", "マイナンバーカードがあれば手続きが変わることも"),
        ("国民健康保険の手続き", "同上", "加入している人だけ"),
        ("児童手当・医療費助成などの手続き", "同上", "受けている制度があれば"),
        ("印鑑登録の廃止", "同上", "自動で消える自治体もある"),
    ])
    p1 = f'''<h1>引っ越し手続きチェックリスト<small>やることは多いのに、順番が決まっていないから漏れます</small></h1>

  <div class="band">
    <b>上から順にやれば、それで終わります。</b>考える必要はありません。<br>
    自治体によって細かい違いがあるので、<b>役所に行く前に1回だけ電話</b>して確認すると確実です。
  </div>

  <table style="margin-top:4mm;">{hdr}{b1}{b2}</table>'''

    b3 = block("ライフライン（引っ越し1〜2週間前）", [
        ("電気　停止と開始", "1〜2週間前", "ネットで両方できる会社が多い"),
        ("ガス　停止と開始", "1〜2週間前", "開栓は立ち会いが要る。予約が要ります"),
        ("水道　停止と開始", "1〜2週間前", ""),
        ("インターネット・回線", "1か月前", "工事が要る場合は早めに。ここが一番遅れます"),
    ])
    b4 = block("住所変更（引っ越し後）", [
        ("転入届を出す", "引っ越しから14日以内", "期限があるのはここ"),
        ("マイナンバーカードの住所変更", "同上", "転入届と同時に"),
        ("運転免許証の住所変更", "早めに", "警察署か免許センター"),
        ("車庫証明・車検証", "住所変更後", "車がある人"),
        ("銀行・クレジットカード", "早めに", "アプリでできることが多い"),
        ("携帯・保険・証券", "早めに", ""),
        ("勤務先への届け出", "早めに", "通勤手当が変わります"),
        ("郵便の転送届", "引っ越し前でも可", "1年間、旧住所あての郵便が届きます"),
        ("通販サイトの住所", "気づいたとき", "うっかり旧住所に送りがち"),
    ])
    p2 = f'''<h1 style="font-size:20pt;">続き<small>期限があるのは「転入届（14日以内）」だけです</small></h1>
  <table style="margin-top:4mm;">{hdr}{b3}{b4}</table>

  <div class="box accentbox" style="margin-top:3mm;">
    <h3>とくに遅れやすい3つ</h3>
    <b>ネット回線</b>（工事に1か月かかることがある）／<b>ガスの開栓</b>（立ち会いの予約が埋まる）／
    <b>粗大ごみ</b>（自治体の予約が直前は取れない）。この3つだけは、決まった日に即申し込んでください。
  </div>'''
    return [page(p1, "引っ越し手続きチェックリスト", "1 / 2　決まったら／役所"),
            page(p2, "引っ越し手続きチェックリスト", "2 / 2　ライフライン／住所変更")]


# =================== 6. あと何日もつか ===================
def nannichi():
    p1 = '''<h1>あと何日もつか<small>週に1回、1分。使えるお金を「1日あたり」に直すだけのシート</small></h1>

  <div class="band">
    <b>毎週〈決めた曜日〉の朝、銀行アプリを開いて、残高を1つ書く。</b><br>
    あとは引き算と割り算だけです。
  </div>

  <div class="box accentbox">
    <h3>やることは3行</h3>
    <div style="font-size:12.5pt;font-weight:700;margin:2.5mm 0;line-height:1.9;">
      ① いまの残高　－　② 給料日までに必ず出ていくお金　＝　③ 使えるお金<br>
      ③ ÷ 給料日までの残り日数　＝　<span style="color:#C97F00;">1日あたり使える額</span>
    </div>
    「あといくらある」ではなく「<b>1日あたりいくら</b>」に直すのがこのシートの全部です。
  </div>

  <div class="box">
    <h3>なぜ1日あたりに直すのか</h3>
    残高が3万円あると、多いのか少ないのか分かりません。<br>
    でも「給料日まであと15日、1日2,000円」と出れば、<b>今日の判断がその場でできます。</b><br>
    節約しようと思わなくても、数字を見た時点で行動が変わります。<b>我慢を要求しない設計です。</b>
  </div>

  <div class="box">
    <h3>②に入れるもの（必ず出ていくお金だけ）</h3>
    家賃／カードの引き落とし／サブスク／定期券／すでに決まっている予定の費用。<br>
    <b>「たぶん使う」は入れないでください。</b>入れると数字が信用できなくなって、見なくなります。
  </div>

  <div class="box">
    <h3>マイナスが出た週について</h3>
    それが分かっただけで、この週の記入は成功です。<br>
    <b>気づくのが今日か、引き落とし当日かで、できることの数がまったく違います。</b>
    足りないと分かった週は、いちばん下の欄に「どうするか」を1つだけ書いてください。
  </div>'''

    hdr = ('<tr class="hl"><th style="width:20mm;">日付</th>'
           '<th style="width:30mm;">① いまの残高</th>'
           '<th style="width:34mm;">② 必ず出ていくお金</th>'
           '<th style="width:30mm;">③ 使えるお金</th>'
           '<th style="width:22mm;">残り日数</th>'
           '<th style="background:rgba(240,162,2,.28);">1日あたり</th></tr>')
    body = ""
    for _ in range(14):
        body += ('<tr><td style="height:11.4mm;"></td><td></td><td></td>'
                 '<td></td><td></td><td></td></tr>')
    p2 = f'''<div class="head">
    <h1 style="font-size:20pt;">記入表<small>週に1行。14週分（約3か月）</small></h1>
    <div class="fields">毎週 <span class="fld" style="width:14mm;"></span> 曜日の朝<br>
      給料日 毎月 <span class="fld" style="width:14mm;"></span> 日</div>
  </div>
  <table style="margin-top:4mm;">{hdr}{body}</table>

  <div class="box">
    <h3>足りないと分かった週に、やること（1つだけ書く）</h3>
    <div style="height:8mm;border-bottom:1.2pt solid rgba(43,58,85,.4);margin-top:2mm;"></div>
    <div style="height:8mm;border-bottom:1.2pt solid rgba(43,58,85,.4);"></div>
  </div>'''
    return [page(p1, "あと何日もつか", "1 / 2　使い方"),
            page(p2, "あと何日もつか", "2 / 2　記入表")]


PRODUCTS.update({
    "oya":      ("親のことを1枚に（親の情報シート）", oya),
    "hikkoshi": ("引っ越し手続きチェックリスト", hikkoshi),
    "nannichi": ("あと何日もつかシート", nannichi),
})
