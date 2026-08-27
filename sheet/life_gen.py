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


# =================== 8. 期限のあるもの一覧 ===================
def kigen():
    p1 = '''<h1>期限のあるもの、全部ここに<small>年に1回だけ書けば、切らしません</small></h1>

  <div class="band">
    <b>1年に1回、この1枚に「次いつ切れるか」だけを書く。</b><br>
    あとは、家計を見るついでに横目で見るだけです。
  </div>

  <div class="box accentbox">
    <h3>「忘れていた」は、理由として認められません</h3>
    運転免許の更新について、警視庁のページにはこう書かれています。<br>
    <b>「仕事で忙しかった、更新のハガキが届かなかった、気づかなかった」などは、やむを得ない理由に該当しません。</b><br>
    つまり、通知が来なかったことを理由に救済されることは基本的にありません。<b>期限を管理する責任は、こちら側にあります。</b>
  </div>

  <div class="box">
    <h3>書き出すもの</h3>
    <div><b>身分証</b>　運転免許／マイナンバーカード（カード本体と電子証明書は期限が別）／パスポート／在留カード</div>
    <div class="grp"><b>車</b>　車検／自賠責／任意保険／点検</div>
    <div class="grp"><b>住まい</b>　賃貸の更新／火災保険／地震保険</div>
    <div class="grp"><b>仕事</b>　資格の更新／講習／健康診断</div>
    <div class="grp"><b>その他</b>　クレジットカードの有効期限／定期券／保証期間／ポイントの期限</div>
  </div>

  <div class="box">
    <h3>マイナンバーカードは、期限が2つあります</h3>
    カード本体の有効期限と、<b>電子証明書の有効期限（発行から5年）</b>は別です。<br>
    電子証明書が切れると、コンビニでの証明書発行や、確定申告のオンライン手続きができなくなります。
    カードは使えるのに手続きだけ通らない、という状態になるので、<b>2行に分けて書いてください。</b>
  </div>

  <div class="box">
    <h3>書いたあとに1つだけ</h3>
    <b>いちばん近い期限を、スマホのカレンダーに1件だけ登録してください。</b>1か月前の通知つきで。<br>
    全部登録する必要はありません。1件やっておけば、その日にこの紙をまた開くことになります。
  </div>'''

    hdr = ('<tr class="hl"><th style="width:52mm;">何の期限か</th>'
           '<th style="width:32mm;">次に切れる日</th>'
           '<th style="width:30mm;">いつ手続きする</th>'
           '<th style="width:26mm;">済</th>'
           '<th>どこで・持ち物・メモ</th></tr>')
    body = ""
    for _ in range(19):
        body += ('<tr><td style="height:8.2mm;"></td><td></td><td></td>'
                 '<td style="text-align:center;"><span class="cb"></span></td><td></td></tr>')
    p2 = f'''<div class="head">
    <h1 style="font-size:20pt;">期限一覧<small>「次に切れる日」だけ埋めれば機能します</small></h1>
    <div class="fields">書いた日 <span class="fld" style="width:14mm;"></span> 年
      <span class="fld" style="width:10mm;"></span> 月</div>
  </div>
  <table style="margin-top:4mm;">{hdr}{body}</table>

  <div class="box accentbox">
    <h3>いちばん近い期限は</h3>
    <span class="fld" style="width:40mm;"></span> が　<span class="fld" style="width:20mm;"></span> 月
    <span class="fld" style="width:20mm;"></span> 日<br>
    <b>この日をカレンダーに入れましたか　<span class="cb"></span> 入れた</b>
  </div>'''
    return [page(p1, "期限のあるもの一覧", "1 / 2　使い方"),
            page(p2, "期限のあるもの一覧", "2 / 2　期限一覧")]


# =================== 9. 申請しないともらえないお金 ===================
def shinsei():
    p1 = '''<h1>申請しないと、もらえません<small>心当たりを確認して、時効までに動くための1枚</small></h1>

  <div class="band">
    <b>日本の公的な給付は「申請主義」です。</b><br>
    条件を満たしていても、自分から申請しない限り、自動では1円も入ってきません。
  </div>

  <div class="box accentbox">
    <h3>しかも、時効があります</h3>
    健康保険の現金給付（高額療養費・傷病手当金・埋葬料など）は、<b>時効が2年</b>です。<br>
    2年を過ぎると、条件を満たしていた分も<b>受け取る権利そのものが消えます。</b><br>
    逆に言えば、<b>過去2年以内なら、まだ間に合う</b>ということです。ここが大事です。
  </div>

  <div class="box">
    <h3>時効の起算日（いつから数えるか）</h3>
    ・<b>高額療養費</b>　診療を受けた月の翌月1日から2年<br>
    ・<b>傷病手当金</b>　労務不能だった日ごとに、その翌日から2年<br>
    ・<b>埋葬料</b>　亡くなった日の翌日から2年<br>
    <div class="grp">雇用保険にも期限があります。<b>再就職手当</b>は、再就職した日から2年以内に申請すれば受けられる場合があります。</div>
  </div>

  <div class="box">
    <h3>ふるさと納税は5年さかのぼれます</h3>
    ワンストップ特例の書類を出し忘れても、<b>確定申告（還付申告）に切り替えれば控除を受けられます。</b><br>
    還付申告は、その年の翌年1月1日から<b>5年以内</b>なら可能です。<b>「出し忘れたからもう無理」ではありません。</b>
  </div>

  <div class="box">
    <h3>このシートの使い方</h3>
    次のページのリストを<b>上から読んで、心当たりのあるものに印をつけるだけ</b>です。<br>
    金額の計算も、条件の判定もしません。<b>「これ、自分かも」を見つけるための紙</b>です。<br>
    印がついたものだけ、窓口に電話して聞いてください。それで終わります。
  </div>

  <div class="box accentbox">
    <h3>先に断っておきます</h3>
    制度の条件・金額・期限は、<b>加入している保険や自治体、その時々の制度改正によって変わります。</b>
    このシートは判定をするものではなく、<b>確認しにいくきっかけを作るためのもの</b>です。<br>
    最終的な可否は、健康保険組合・協会けんぽ・年金事務所・ハローワーク・市区町村・税務署に確認してください。
  </div>'''

    def sec(t):
        return (f'<tr><td colspan="4" style="background:rgba(240,162,2,.18);'
                f'font-weight:700;font-size:9.6pt;height:6.6mm;">{t}</td></tr>')

    def item(name, when, note):
        return (f'<tr><td style="width:14mm;text-align:center;height:8.6mm;">'
                f'<span class="cb"></span></td>'
                f'<td style="width:56mm;font-size:9.6pt;"><b>{name}</b></td>'
                f'<td style="width:40mm;font-size:9pt;">{when}</td>'
                f'<td style="font-size:9pt;">{note}</td></tr>')

    hdr = ('<tr class="hl"><th style="width:14mm;">心当たり</th><th>制度</th>'
           '<th style="width:40mm;">時効・期限の目安</th><th>どんなときか／聞く先</th></tr>')

    rows_html = (
        sec("医療費が高かった・入院した")
        + item("高額療養費", "診療を受けた月の翌月1日から2年",
               "1か月の自己負担が上限を超えたとき／健保・協会けんぽ・市区町村")
        + item("医療費控除", "翌年1月1日から5年（還付申告）",
               "1年の医療費が一定額を超えたとき／税務署")
        + sec("病気やケガで働けなかった")
        + item("傷病手当金", "労務不能だった日ごとに翌日から2年",
               "病気やケガで仕事を休み、給与が出なかったとき／健保・協会けんぽ")
        + item("障害年金", "受給権発生から5年分までさかのぼれる場合あり",
               "病気やケガで生活や仕事に制限があるとき／年金事務所")
        + sec("仕事を辞めた・変わった")
        + item("失業給付（基本手当）", "原則、離職の翌日から1年の受給期間",
               "退職して求職しているとき／ハローワーク")
        + item("再就職手当", "再就職した日から2年以内",
               "失業給付の受給中に早く再就職したとき／ハローワーク")
        + item("国民健康保険料・年金の減免", "自治体により異なる",
               "退職・収入減で払うのが厳しいとき／市区町村・年金事務所")
        + sec("家族に関すること")
        + item("出産育児一時金・出産手当金", "2年",
               "出産したとき／健保・協会けんぽ")
        + item("育児休業給付金", "期限あり。早めに",
               "育児休業を取ったとき／ハローワーク・勤務先")
        + item("児童手当", "さかのぼり支給は原則なし。申請月の翌月分から",
               "子どもが生まれた・引っ越したとき／市区町村")
        + item("埋葬料・葬祭費", "亡くなった日の翌日から2年",
               "家族が亡くなったとき／健保・市区町村")
        + sec("ふるさと納税")
        + item("ワンストップを出し忘れた", "翌年1月1日から5年（還付申告）",
               "確定申告に切り替えれば控除を受けられます／税務署")
    )

    p2 = f'''<h1 style="font-size:20pt;">心当たりチェック<small>読んで、当てはまりそうなものに印をつけるだけ</small></h1>
  <table style="margin-top:4mm;">{hdr}{rows_html}</table>

  <div class="box" style="margin-top:3mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">印がついたら、次にやること</h3>
    <div style="margin-top:1.5mm;">
      <b>1.</b> 右の「聞く先」に電話する。<b>「◯◯に当てはまるか知りたい」</b>だけでいいです。<br>
      <b>2.</b> 該当しそうなら、必要書類を聞いてメモする。<br>
      <b>3.</b> 時効の日を、カレンダーに入れる。
    </div>
    <div class="grp"><b>この3つで終わります。</b>金額の計算も、制度の勉強も要りません。</div>
  </div>

  <div class="box accentbox" style="margin-top:2.5mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">電話するのは、面倒ではあります</h3>
    ただ、ここに並んでいるのは<b>数万円から数十万円</b>の話です。1本の電話で確認できるなら、時給としては相当いい。<br>
    そして<b>2年経つと、確認する権利ごと消えます。</b>
  </div>'''
    return [page(p1, "申請しないともらえないお金", "1 / 2　使い方"),
            page(p2, "申請しないともらえないお金", "2 / 2　心当たりチェック")]


PRODUCTS.update({
    "kigen":   ("期限のあるもの一覧", kigen),
    "shinsei": ("申請しないともらえないお金 チェックシート", shinsei),
})


# =================== 10. 補助金もらい忘れリスト ===================
def hojo():
    p1 = '''<h1>補助金、もらい忘れていませんか<small>自分の市区町村にあるのに、誰も教えてくれない制度を洗い出す1枚</small></h1>

  <div class="band">
    <b>補助金は、申請しないと1円ももらえません。</b><br>
    そして、住んでいる自治体に何があるかは、自分で調べに行かない限り分かりません。
  </div>

  <div class="box accentbox">
    <h3>先に、このシートの限界を書いておきます</h3>
    全国には1,700を超える市区町村があり、<b>制度の名前・金額・条件・期限は毎年変わります。</b>
    予算が尽きた時点で受付終了になる制度も多くあります。<br>
    そのため、このシートは<b>「どこにいくらある」という一覧ではありません。</b><br>
    <b>「こういう種類の補助金がある」という型を知り、自分の自治体にあるかを自分で確認するための紙</b>です。
    金額や条件は、必ず自治体の最新情報で確認してください。
  </div>

  <div class="box">
    <h3>調べ方は3つだけ</h3>
    <ol class="steps" style="margin-top:1.5mm;">
      <li><b>自治体サイトで検索する。</b><br>
        <span class="note">検索窓に「補助」「助成」と入れるだけ。制度名で探そうとすると出てきません。</span></li>
      <li><b>Googleで「市区町村名＋補助金」「市区町村名＋助成金」。</b><br>
        <span class="note">広報誌のPDFが引っかかることが多く、そこに一覧が載っています。</span></li>
      <li><b>住宅まわりは、専用の検索サイトがあります。</b><br>
        <span class="note">住宅リフォーム推進協議会「地方公共団体における住宅リフォーム支援制度検索サイト」<br>
        j-reform.com/reform-support ／ 都道府県 → 市区町村の順に絞れます。終了済みの制度も載っているので要確認。</span></li>
    </ol>
  </div>

  <div class="box">
    <h3>電話が、いちばん早いです</h3>
    市役所の代表番号にかけて<b>「個人向けの補助金の一覧はありますか」</b>と聞いてください。<br>
    担当課につないでくれます。窓口で「何かもらえるものはありますか」と聞くのも有効です。
    <b>職員は制度を知っていますが、こちらから聞かないと案内しません。</b>
  </div>

  <div class="box">
    <h3>3つだけ、注意点</h3>
    <b>1. 予算切れで終わります。</b>年度初め（4〜6月）に確認するのがいちばん取りやすい。<br>
    <b>2. 着工前・購入前の申請が必要な制度が多いです。</b>買ってから気づくと、もう対象外になります。<br>
    <b>3. 国・都道府県・市区町村で別々にあります。</b>併用できるものもあれば、できないものもあります。
  </div>'''

    def sec(t):
        return (f'<tr><td colspan="4" style="background:rgba(240,162,2,.18);'
                f'font-weight:700;font-size:9.4pt;height:5.6mm;">{t}</td></tr>')

    def item(name, hint, where):
        return (f'<tr><td style="width:13mm;text-align:center;height:7.4mm;">'
                f'<span class="cb"></span></td>'
                f'<td style="width:58mm;font-size:9.4pt;"><b>{name}</b></td>'
                f'<td style="font-size:8.8pt;">{hint}</td>'
                f'<td style="width:34mm;font-size:8.8pt;">{where}</td></tr>')

    hdr = ('<tr class="hl"><th style="width:13mm;">心当たり</th><th>よくある補助金の型</th>'
           '<th>どんなときか</th><th style="width:34mm;">よくある窓口</th></tr>')

    rows_html = (
        sec("住まい（金額が大きい。まずここから）")
        + item("断熱窓・内窓・ドアの交換", "冬寒い・結露する家。国と都道府県で別々にあることが多い", "環境課・住宅課")
        + item("給湯器の買い替え", "エコキュート・エコジョーズなど省エネ型に替えるとき", "環境課")
        + item("太陽光・蓄電池", "設置するとき。都道府県の制度が大きい", "環境課")
        + item("耐震診断・耐震改修", "1981年以前の建物は対象になりやすい", "建築指導課")
        + item("バリアフリー改修", "手すり・段差解消。介護保険の住宅改修とは別枠のことも", "高齢福祉課")
        + item("一般の住宅リフォーム", "市内業者に頼むことが条件の制度が多い", "住宅課")
        + item("空き家の活用・解体", "相続した家がある人。解体費の補助がある自治体も", "住宅課・都市計画課")
        + sec("子ども・家族")
        + item("出産・子育ての祝い金／給付", "自治体独自の上乗せがある場合", "子育て支援課")
        + item("不妊治療・不育症の助成", "国の保険適用とは別に、独自の上乗せがある自治体も", "健康課")
        + item("チャイルドシート購入補助", "自治体によってはレンタル制度も", "交通・子育て担当")
        + item("入学・入園の準備金", "就学援助と合わせて確認", "教育委員会")
        + item("紙おむつ・ミルクの支給", "乳児のいる世帯向け", "子育て支援課")
        + sec("健康・医療")
        + item("健康診断・がん検診の無料化", "年齢で対象になる年がある。受けないと消えます", "健康課")
        + item("予防接種の助成", "高齢者の肺炎球菌・帯状疱疹など", "健康課")
        + item("人間ドックの補助", "健康保険組合・国保のどちらにもある場合", "保険年金課・健保")
        + sec("暮らし・その他")
        + item("自転車ヘルメットの購入補助", "上限2,000〜3,000円程度の自治体が多い", "交通安全担当")
        + item("生ごみ処理機・コンポスト", "購入費の一部を補助", "清掃・環境課")
        + item("雨水タンクの設置", "設置費の補助がある自治体も", "下水道・環境課")
        + item("生け垣・緑化の助成", "ブロック塀から生け垣にするときなど", "みどり・公園課")
        + item("ブロック塀の撤去", "地震対策として補助がある自治体が多い", "建築指導課")
        + item("犬猫の不妊・去勢手術", "飼い主のいない猫も対象になることがある", "生活衛生課")
        + item("移住・定住の支援金", "引っ越し先で使えることがある。転入前の相談が必要な場合も", "企画・定住促進課")
        + item("商店・事業の開業支援", "個人事業の開業でも対象になる制度がある", "産業振興課")
    )

    p2 = f'''<h1 style="font-size:20pt;">よくある補助金の型<small>心当たりのあるものに印をつけて、自分の自治体にあるか調べます</small></h1>
  <table style="margin-top:3.5mm;">{hdr}{rows_html}</table>

  <div class="box" style="margin-top:3mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">窓口の名前は自治体で違います</h3>
    右の欄はあくまで目安です。分からなければ<b>代表番号にかけて、この表の名前をそのまま言えば</b>つないでくれます。
  </div>'''

    hdr3 = ('<tr class="hl"><th style="width:52mm;">制度の名前</th>'
            '<th style="width:26mm;">いくら</th>'
            '<th style="width:30mm;">申請の期限</th>'
            '<th style="width:24mm;">申請した</th>'
            '<th>条件・持ち物・電話した日</th></tr>')
    body3 = ""
    for _ in range(14):
        body3 += ('<tr><td style="height:9.4mm;"></td><td></td><td></td>'
                  '<td style="text-align:center;"><span class="cb"></span></td><td></td></tr>')

    p3 = f'''<div class="head">
    <h1 style="font-size:20pt;">調べた結果を書く<small>該当したものだけ、ここに書き写します</small></h1>
    <div class="fields">
      市区町村 <span class="fld" style="width:36mm;"></span><br>
      調べた日 <span class="fld" style="width:14mm;"></span> 年
      <span class="fld" style="width:10mm;"></span> 月</div>
  </div>
  <table style="margin-top:4mm;">{hdr3}{body3}</table>

  <div class="box accentbox" style="margin-top:3mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">「申請の期限」の欄を、必ず埋めてください</h3>
    <b>予算がなくなり次第終了する制度が多く、期限より先に締め切られることがあります。</b>
    そして<b>買う前・工事の前に申請が必要な制度</b>が多い。ここを外すと、条件を満たしていても対象外になります。<br>
    調べたその日に、期限をスマホのカレンダーへ入れてください。
  </div>

  <div class="box" style="margin-top:2.5mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">来年またやること</h3>
    制度は<b>毎年入れ替わります。</b>新しくできるものもあれば、なくなるものもある。<br>
    <b>年度初め（4〜6月）にもう一度この紙を開く。</b>それだけで、取りこぼしはかなり減ります。
  </div>'''

    # 実例（受付が続いているものだけ／2026年8月時点で各自治体サイトを確認）
    ex_helmet = [
        ("江戸川区", "自転車用ヘルメット購入補助",
         "1個あたり最大2,000円（2,000円未満の商品はその価格まで）。1人1回",
         "令和8年度の<b>予算額に達するまで</b>受付"),
        ("練馬区", "自転車用ヘルメット購入費助成",
         "1個につき2,000円（販売価格が2,000円未満ならその額）",
         "令和8年度も実施中。<b>協力店で購入するその場で申請</b>"),
        ("足立区", "自転車用ヘルメットの割引",
         "対象ヘルメットを3,000円引きで購入できる方式",
         "令和8年度も実施中。<b>指定店で購入するその場で申請</b>"),
    ]
    ex_env = [
        ("葛飾区", "生ごみ処理機等購入費補助金",
         "購入価格の1/2、上限20,000円",
         "令和8年度も実施中。<b>予算がなくなり次第終了</b>"),
        ("品川区", "家庭用生ごみ処理機購入費助成",
         "申請件数に上限あり",
         "<b>上限に達した時点で終了</b>。区が「上限が迫っている」と告知中"),
        ("大田区", "雨水タンク設置助成",
         "小型タンクは費用の2/3・1基上限40,000円、2基まで（個人）",
         "<b>設置前の申請が必要</b>"),
        ("世田谷区", "雨水タンク設置助成",
         "1基あたり上限35,000円（設置費は上限5,000円）",
         "前期は<b>令和8年8月31日まで</b>に交付申請／後期の事前登録は<b>令和8年10月1日から</b>"),
        ("練馬区", "雨水タンク設置助成",
         "雨水浸透施設とあわせて設置する場合などが対象（条件あり）",
         "<b>設置前の申請が必要</b>"),
    ]

    def exrow(a, b, c, d):
        return (f'<tr><td style="width:19mm;height:8.4mm;font-size:8.8pt;text-align:center;">'
                f'<b>{a}</b></td><td style="width:40mm;font-size:8.4pt;">{b}</td>'
                f'<td style="font-size:8.4pt;">{c}</td>'
                f'<td style="width:52mm;font-size:8.4pt;">{d}</td></tr>')

    t_helmet = "".join(exrow(*r) for r in ex_helmet)
    t_env = "".join(exrow(*r) for r in ex_env)

    p4 = f'''<h1 style="font-size:20pt;">実際にある補助金の例<small>2026年8月時点で受付が続いているものだけ。金額は変わるので必ず区に確認してください</small></h1>

  <div class="box accentbox" style="padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">終了した制度は載せていません。ただし「今日ある」保証にはなりません</h3>
    <b>多くが「予算がなくなり次第終了」です。</b>同じ生ごみ処理機の補助でも、
    杉並区は令和8年度分が予算上限に達して受付を終えました。
    <b>期限の日付より先に締め切られる</b>ということです。見つけたら、その週に動いてください。
  </div>

  <table style="margin-top:3mm;">
    <tr class="hl"><th style="width:19mm;">自治体</th><th style="width:40mm;">制度</th>
      <th>金額（確認時点）</th><th style="width:52mm;">受付期間・期限</th></tr>
    <tr><td colspan="4" style="background:rgba(240,162,2,.18);font-weight:700;
      font-size:9pt;height:5.2mm;">自転車ヘルメット</td></tr>
    {t_helmet}
    <tr><td colspan="4" style="background:rgba(240,162,2,.18);font-weight:700;
      font-size:9pt;height:5.2mm;">生ごみ処理機・雨水タンク</td></tr>
    {t_env}
  </table>

  <div class="box" style="margin-top:2.5mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">この表から分かること</h3>
    <b>1. 期限が日付で決まっていない制度が多い。</b>「予算がなくなり次第終了」＝早い者勝ちです。<br>
    <b>2. 同じ制度でも、区によって金額が違います。</b>雨水タンクは35,000円〜40,000円と幅があります。<br>
    <b>3. 隣の区にあって、自分の区にないこともあります。</b>だから自分で確認するしかありません。<br>
    <b>4. どれも購入前・設置前の申請が必要です。</b>買ってからでは間に合いません。
  </div>

  <div class="box accentbox" style="margin-top:2.5mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">全国どこでも使える入口（住宅まわり）</h3>
    <b>住宅リフォーム推進協議会「地方公共団体における住宅リフォーム支援制度検索サイト」</b><br>
    j-reform.com/reform-support　都道府県 → 市区町村の順に絞り込めます。
    耐震化・バリアフリー・省エネ・環境・防災などの分類で探せます。
    <b>終了した制度も掲載されていることがあるため、最新情報は必ず自治体に確認してください。</b>
  </div>

  <div class="box" style="margin-top:2.5mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">住宅以外は、この2手で拾えます</h3>
    <b>1.</b> 自治体サイトの検索窓に「補助」「助成」と入れる（制度名で探さない）<br>
    <b>2.</b> Googleで「市区町村名 補助金」「市区町村名 助成金」。広報誌のPDFに一覧が載っていることが多いです<br>
    それでも分からなければ、<b>代表番号に電話して「個人向けの補助金の一覧はありますか」</b>と聞いてください。
  </div>'''

    return [page(p1, "補助金もらい忘れリスト", "1 / 4　使い方と調べ方"),
            page(p2, "補助金もらい忘れリスト", "2 / 4　よくある補助金の型"),
            page(p3, "補助金もらい忘れリスト", "3 / 4　調べた結果を書く"),
            page(p4, "補助金もらい忘れリスト", "4 / 4　実例と探し方")]


PRODUCTS.update({"hojo": ("補助金もらい忘れリスト", hojo)})


# =================== 10. 入居時チェック表 ===================
def nyukyo():
    p1 = '''<h1>入居時チェック表<small>退去のときに「これは元からありました」と言えるようにしておく1枚です</small></h1>

  <div class="band">退去費用でもめる理由は、ひとつだけです。<br>
    <b>入居したときの状態を、誰も記録していないからです。</b><br>
    傷がいつからあったのか分からなければ、<b>あなたがつけたことになります。</b></div>

  <div class="box accentbox">
    <h3>今日やることは3つです</h3>
    <ol class="steps" style="margin-top:1mm;">
      <li><b>荷物を入れる前に、部屋を撮る。</b>家具を置いたら、その裏はもう撮れません。</li>
      <li><b>この表に、傷・汚れの場所を書く。</b>見る場所は印刷してあります。順番に見るだけです。</li>
      <li><b>管理会社にメールで送る。</b>送った日時が、そのまま記録になります。</li>
    </ol>
  </div>

  <div class="box">
    <h3>法律は、借りている側にあります</h3>
    <b>民法621条</b>（2020年4月施行）は、<b>通常の使用でついた損耗と経年変化は、借主の原状回復義務に含まれない</b>と定めています。
    国土交通省の「原状回復をめぐるトラブルとガイドライン」も同じ考え方です。<br>
    もめるのは、そこではありません。<b>「その傷が、通常の使用によるものか、あなたがつけたものか」</b>で争いになります。
    だから、入居した日の状態を残しておく必要があります。
  </div>

  <div class="box">
    <h3>撮り方は、この4つだけ守ってください</h3>
    <b>1. 全体 → 寄り、の順にセットで撮る。</b>寄りだけだと、どこの傷か分からなくなります。<br>
    <b>2. 傷の横に、定規かスマホを置く。</b>大きさが分かります。<br>
    <b>3. 日付を写し込む必要はありません。</b>写真の日時と、送信メールの日付が残ります。<br>
    <b>4. 最後に、部屋を一周する動画を1本撮る。</b>撮り忘れた場所を、あとから拾えます。
  </div>

  <div class="box accentbox">
    <h3>期限があります。契約書を今すぐ見てください</h3>
    多くの契約で、<b>入居後2週間以内</b>に「入居時確認書」を提出することになっています。
    ここを過ぎると、<b>「入居時には無かった傷」として扱われやすくなります。</b><br>
    <div style="margin-top:2mm;font-size:10.5pt;">
      提出期限　<span class="fld" style="width:14mm;"></span> 年
      <span class="fld" style="width:10mm;"></span> 月
      <span class="fld" style="width:10mm;"></span> 日まで　／　
      提出先（担当者名）<span class="fld" style="width:44mm;"></span></div>
  </div>

  <div class="box" style="margin-top:auto;">
    <h3>この表を書くのは、一生に一度、入居日だけです</h3>
    毎月も、毎週も、書きません。<b>今日30分かけるかどうかで、退去のときに数万円変わります。</b>
  </div>'''

    secs = [
        ("玄関・廊下", ["玄関ドアの内側（へこみ・キズ）", "たたき・シューズボックスの中",
                    "廊下の壁と床（家具を運んだ跡）"]),
        ("居室（洋室・和室）", ["壁 4面（画びょう跡・下地のへこみ・日焼け）", "床のキズ・へこみ・きしみ",
                        "天井のシミ・雨漏りの跡", "窓ガラス・サッシ・網戸の破れ",
                        "エアコン（動くか・カビ臭くないか）", "押入れ・クローゼットの中"]),
        ("キッチン", ["シンク・コンロまわりの焦げと汚れ", "換気扇の油汚れ",
                   "床の油じみ", "扉・取っ手のガタつき"]),
        ("浴室・洗面所", ["浴槽と床のカビ・ひび", "鏡・棚のくもりとサビ",
                    "洗面台の下（水漏れの跡）", "浴室の換気扇（動くか）"]),
        ("トイレ", ["便器と床のよごれ・ひび", "ペーパーホルダー・タオル掛けのぐらつき"]),
        ("その他", ["ベランダの床・手すり・排水口", "建具のガタつき・鍵のかかり具合"]),
    ]
    body = ""
    for name, items in secs:
        body += (f'<tr><td colspan="4" style="background:rgba(240,162,2,.18);font-weight:700;'
                 f'font-size:9.4pt;height:5.4mm;padding-left:2mm;">{name}</td></tr>')
        for it in items:
            body += (f'<tr><td style="height:7mm;font-size:9pt;padding-left:2mm;">{it}</td>'
                     f'<td style="text-align:center;font-size:9pt;">有 ・ 無</td>'
                     f'<td></td><td style="text-align:center;"><span class="cb"></span></td></tr>')

    p2 = f'''<div class="head">
    <div><h1 style="font-size:21pt;">見る場所チェック<small>上から順に見るだけです。「無」でも、写真は撮ってください</small></h1></div>
    <div class="fields">物件名 <span class="fld" style="width:40mm;"></span><br>
      入居日 <span class="fld" style="width:14mm;"></span> 年
      <span class="fld" style="width:10mm;"></span> 月
      <span class="fld" style="width:10mm;"></span> 日</div>
  </div>

  <table style="margin-top:4mm;">
    <tr class="hl"><th>見る場所</th><th style="width:22mm;">傷・汚れ</th>
      <th style="width:62mm;">あった場合、その内容</th><th style="width:16mm;">写真</th></tr>
    {body}
  </table>

  <div class="box" style="margin-top:3mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">「無」の場所こそ、写真が要ります</h3>
    退去時にもめるのは、<b>入居時に何も無かった場所に、傷ができていたとき</b>ではありません。
    <b>元からあった傷を、無かったことにされるとき</b>です。
    だから「有」だけ撮っても足りません。<b>全部の場所を1枚ずつ撮ってください。</b>
  </div>'''

    tai = [("壁のクロス（壁紙）", "6年", "6年住めば、借主の負担は原則1円まで下がります"),
           ("カーペット・クッションフロア", "6年", "同上"),
           ("流し台", "5年", ""),
           ("エアコン・ガスレンジなどの設備", "6年", ""),
           ("便器・洗面台などの給排水設備", "15年", ""),
           ("ふすま紙・障子紙・畳表", "考慮しない", "消耗品の扱い。破れば張替費用の負担が生じます"),
           ("フローリング", "考慮しない", "部分補修の場合。全面張替えは建物の年数で見ます"),
           ("木製建具・柱", "考慮しない", "")]
    trow = "".join(f'<tr><td style="height:7.2mm;font-size:9.4pt;padding-left:2mm;">{a}</td>'
                   f'<td style="text-align:center;font-size:9.4pt;"><b>{b}</b></td>'
                   f'<td style="font-size:8.8pt;">{c}</td></tr>' for a, b, c in tai)

    p3 = f'''<h1 style="font-size:21pt;">退去のときに、この紙を出します<small>請求書が来てからでは遅い。出す順番と、言い方を決めておきます</small></h1>

  <div class="box accentbox">
    <h3>立会いの日に、その場でサインしないでください</h3>
    立会いで見積書や確認書を出され、その場で署名を求められることがあります。
    <b>「持ち帰って確認します」と言って構いません。</b>署名すると、金額に同意したと扱われることがあります。
  </div>

  <div class="box">
    <h3>言い方は、これだけ覚えておけば足ります</h3>
    <div style="margin-top:1.5mm;font-size:10.5pt;line-height:1.8;border-left:2.6pt solid var(--accent);padding-left:4mm;">
      「この傷は<b>入居時からありました。</b><br>
      入居日に撮った写真と、<b>◯月◯日に御社へ送ったメール</b>が手元にあります。」</div>
    <div style="margin-top:2mm;">写真があると分かった時点で、話が終わることがほとんどです。争う必要はありません。</div>
  </div>

  <div style="margin-top:3.5mm;font-size:10.5pt;font-weight:700;">経過年数の考え方（国土交通省ガイドライン）</div>
  <div class="note" style="margin-top:1mm;">借主の過失で傷つけた場合でも、<b>年数が経つほど負担は下がります。</b>「新品に戻す費用の全額」を払う必要はありません。</div>
  <table style="margin-top:2mm;">
    <tr class="hl"><th>部位</th><th style="width:24mm;">耐用年数</th><th style="width:72mm;">備考</th></tr>
    {trow}
  </table>

  <div class="box" style="margin-top:3mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">それでも折り合わないとき</h3>
    <b>1.</b> 契約書の「特約」を読む。通常損耗まで借主負担とする特約は、内容によっては無効と判断されることがあります<br>
    <b>2.</b> 自治体の消費生活センター（局番なし <b>188</b>）に相談する。無料です<br>
    <b>3.</b> <b>敷金の返還を求める権利の時効は5年です。</b>退去した直後に決着しなくても、すぐに諦める必要はありません
  </div>

  <div class="box" style="margin-top:auto;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">保存場所を、今日決めてください</h3>
    写真とこの紙は、<b>退去する日まで（数年後）</b>必要になります。
    スマホの中だけに置くと、機種変更で消えます。<br>
    <div style="margin-top:1.5mm;">写真の保存先（クラウド名など）<span class="fld" style="width:60mm;"></span></div>
  </div>'''

    return [page(p1, "入居時チェック表", "1 / 3　使い方と撮り方"),
            page(p2, "入居時チェック表", "2 / 3　見る場所チェック"),
            page(p3, "入居時チェック表", "3 / 3　退去のときに使う")]


PRODUCTS.update({"nyukyo": ("入居時チェック表", nyukyo)})


# =================== 11. 診察前の3分シート ===================
def shinsatsu():
    p1 = '''<h1>診察前の3分シート<small>診察室に入ってから思い出しても、もう遅い。待合室で埋める1枚です</small></h1>

  <div class="band">診察室で、言おうと思っていたことを言えずに出てきたことはありませんか。<br>
    <b>本人の記憶力の問題ではありません。</b>診察が短いからです。<br>
    厚生労働省の受療行動調査では、<b>診察時間が3分未満だった外来患者が1割以上</b>います。</div>

  <div class="box accentbox">
    <h3>いつ書くか、決めてあります</h3>
    <b>受付を済ませて、待合室に座った直後です。</b><br>
    家で書こうとすると、書きません。順番が来るまでの時間は、どうせ空いています。
    <b>埋めるのは5項目だけです。3分で終わります。</b>
  </div>

  <div class="box">
    <h3>この5つを書きます</h3>
    <b>① いつから</b>　日付で書いてください。「最近」「しばらく前」では、医師は判断できません<br>
    <b>② どんなふうに</b>　痛み方・出方。表現の例は次のページに載せてあります<br>
    <b>③ 何をすると悪くなるか／楽になるか</b>　ここが診断で一番効きます<br>
    <b>④ 前回の薬はどうだったか</b>　効いた・効かない・飲むのをやめた。<b>やめたことは言っていい</b>です<br>
    <b>⑤ 今日いちばん聞きたいこと（1つだけ）</b>　複数書くと、全部聞けずに終わります
  </div>

  <div class="box">
    <h3>「④ 薬をやめた」を言えない人が多い</h3>
    飲んでいないのに「飲んでいます」と答えると、<b>効かない薬だと判断されて、より強い薬が出ます。</b>
    合わなかった、飲み忘れた、高かった。理由は何でも構いません。
    <b>事実だけ言えば、そこから選び直してくれます。</b>
  </div>

  <div class="box">
    <h3>聞き忘れたときの受け皿を、2つ用意してあります</h3>
    <b>1. 薬のことは、薬局で聞けます。</b>飲み合わせ、副作用、飲む時間。薬剤師は答える立場の人です<br>
    <b>2. それ以外は、3ページ目の「次回聞くこと」に書いて持ち越します。</b>
    次の診察で最初に出せば、それで足ります
  </div>

  <div class="box" style="margin-top:auto;">
    <h3>持ち物（出る前に、ここだけ見てください）</h3>
    <span class="cb"></span>保険証・マイナ保険証　　<span class="cb"></span>診察券　　
    <span class="cb"></span>お薬手帳　　<span class="cb"></span>今飲んでいる薬そのもの（袋ごと）<br>
    <span class="note">薬の名前は覚えなくて構いません。<b>袋ごと持っていけば、それが一番正確です。</b></span>
  </div>'''

    def blank(h):
        return f'<div style="border-bottom:1pt solid var(--line);height:{h};"></div>'

    q = ""
    for n, (t, sub, lines, h) in enumerate([
            ("① いつから", "日付で。思い出せなければ「◯月ごろ」でも構いません", 1, "10mm"),
            ("② どんなふうに", "下の言葉から選んで丸をつけても構いません", 3, "10mm"),
            ("③ 何をすると悪くなる／楽になる", "動いたとき・食後・朝だけ・横になると楽 など", 3, "10mm"),
            ("④ 前回の薬はどうだったか", "効いた／効かない／やめた／副作用が出た", 2, "10mm"),
            ("⑤ 今日いちばん聞きたいこと", "1つだけ書いてください", 2, "10mm")], 1):
        q += (f'<div style="margin-top:{"2.5mm" if n > 1 else "3mm"};">'
              f'<div style="font-size:11pt;font-weight:700;">{t}'
              f'<span style="font-size:8.6pt;font-weight:400;opacity:.65;">　{sub}</span></div>'
              + "".join(blank(h) for _ in range(lines)) + '</div>')

    p2 = f'''<div class="head">
    <div><h1 style="font-size:21pt;">診察前に書く<small>この面をコピーして、通院のたびに1枚使ってください</small></h1></div>
    <div class="fields">受診日 <span class="fld" style="width:12mm;"></span> 年
      <span class="fld" style="width:9mm;"></span> 月
      <span class="fld" style="width:9mm;"></span> 日<br>
      病院・科 <span class="fld" style="width:38mm;"></span></div>
  </div>

  {q}

  <div class="box" style="margin-top:3.5mm;padding:2.5mm 4.5mm;">
    <h3 style="font-size:10.5pt;">② が書けないときは、この中から選んでください</h3>
    <div style="line-height:1.9;">
      <b>痛み方</b>　ズキズキ ／ ガンガン ／ チクチク ／ 締めつけられる ／ 焼けるよう ／ 重い ／ しびれる<br>
      <b>出方</b>　ずっと続く ／ 波がある ／ 急に来て急に治まる ／ 決まった時間だけ ／ だんだん強くなる<br>
      <b>強さ</b>　10段階で（10＝これまでで一番痛い）　今日は<span class="fld" style="width:12mm;"></span>くらい
    </div>
  </div>

  <div class="box accentbox" style="margin-top:2.5mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">診察室では、この紙を見せて構いません</h3>
    読み上げようとすると、緊張して飛びます。<b>「これ、書いてきました」と渡すのが一番早いです。</b>
    嫌がる医師はまずいません。短い時間で要点が分かるからです。
  </div>

  <div class="box" style="margin-top:auto;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">診察のあと、忘れないうちに1行だけ</h3>
    言われた病名・次にすること・次回の予約日を、次のページに1行で書き写してください。
    <b>会計を待っている間で構いません。</b>家に着くころには、半分忘れています。
  </div>'''

    rec = "".join('<tr><td style="height:8.6mm;"></td><td></td><td></td><td></td><td></td></tr>'
                  for _ in range(16))

    p3 = f'''<h1 style="font-size:21pt;">受診の記録<small>1回1行。次に別の病院にかかるとき、この紙がそのまま説明になります</small></h1>

  <table style="margin-top:4mm;">
    <tr class="hl"><th style="width:22mm;">受診日</th><th style="width:34mm;">病院・科</th>
      <th>言われたこと（病名・検査結果）</th>
      <th style="width:42mm;">出た薬</th><th style="width:22mm;">次回</th></tr>
    {rec}
  </table>

  <div class="box accentbox" style="margin-top:3.5mm;padding:2.5mm 4.5mm;">
    <h3 style="font-size:10.5pt;">次回、聞くこと</h3>
    <span class="note">今日聞けなかったこと、あとから気になったことを、思い出したときに書いてください。</span>
    <div style="border-bottom:1pt solid var(--line);height:8mm;"></div>
    <div style="border-bottom:1pt solid var(--line);height:8mm;"></div>
    <div style="border-bottom:1pt solid var(--line);height:8mm;"></div>
  </div>

  <div class="box" style="margin-top:2.5mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">この記録が、いちばん効く場面</h3>
    <b>1. 別の病院・救急にかかるとき。</b>「いつ・どこで・何と言われて・何を飲んでいるか」を一度に渡せます<br>
    <b>2. 家族が代わりに説明するとき。</b>付き添いの人が持っていれば、本人が答えられなくても済みます<br>
    <b>3. 医療費控除を出すとき。</b>受診日が並んでいると、領収書の抜けに気づけます
  </div>

  <div class="box" style="margin-top:auto;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">書く回数</h3>
    <b>通院した日だけです。</b>通院がない月は、何も書きません。
  </div>'''

    return [page(p1, "診察前の3分シート", "1 / 3　使い方"),
            page(p2, "診察前の3分シート", "2 / 3　診察前に書く（コピーして使う面）"),
            page(p3, "診察前の3分シート", "3 / 3　受診の記録")]


PRODUCTS.update({"shinsatsu": ("診察前の3分シート", shinsatsu)})


# =================== 12. 家電の買い替え年表 ===================
def kaden():
    p1 = '''<h1>家電の買い替え年表<small>壊れてから買うと高い。先に「いつ買い替えるか」を書いておく1枚です</small></h1>

  <div class="band">冷蔵庫が止まった日に、冷蔵庫は選べません。<br>
    <b>中身が傷むので、その日に買える物を買うことになります。</b><br>
    高い物を買わされるのではなく、<b>選ぶ時間がないから高くつきます。</b></div>

  <div class="box accentbox">
    <h3>寿命より先に「修理できない日」が来ます</h3>
    メーカーは、修理用の部品をいつまでも持っていません。
    <b>補修用性能部品の保有期間</b>といって、目安はこうなっています。<br>
    <div style="margin-top:1.5mm;line-height:1.9;">
      <b>エアコン・冷蔵庫 … 9年</b>　／　<b>テレビ・電子レンジ … 8年</b>　／　
      <b>洗濯機・炊飯器・掃除機 … 6年</b></div>
    <div style="margin-top:1.5mm;">これを過ぎると、<b>直せる故障でも「部品がありません」で終わります。</b>
    メーカーによって年数は違うので、正確な年数は取扱説明書の最後のページに書いてあります。</div>
  </div>

  <div class="box">
    <h3>しかも、この年数は「買った年から」ではありません</h3>
    保有期間は<b>「その製品の製造を打ち切ったときから」</b>数えます。<br>
    型落ちを安く買った場合、<b>買った時点ですでに何年か過ぎています。</b>
    安く買えた分、修理できる期間は短い。そう思っておいてください。
  </div>

  <div class="box">
    <h3>この紙でやることは、2つだけです</h3>
    <ol class="steps" style="margin-top:1mm;">
      <li><b>今ある家電の「買った年」を書く。</b>思い出せなければ「引っ越した年」で構いません</li>
      <li><b>買った年 ＋ 目安の年数 ＝ 買い替えの年</b>を書く。これで、慌てる年が先に分かります</li>
    </ol>
  </div>

  <div class="box">
    <h3>買った年が分からないときの調べ方</h3>
    <b>1.</b> 本体の側面か背面のシールに<b>製造年</b>が書いてあります（冷蔵庫は内側の壁面）<br>
    <b>2.</b> ネット通販で買ったなら、注文履歴に残っています<br>
    <b>3.</b> どうしても分からなければ<b>「たぶん◯年ごろ」で構いません。</b>1年ずれても使えます
  </div>

  <div class="box" style="margin-top:auto;">
    <h3>開く回数</h3>
    <b>年に1回。</b>年末か、年度の初めに一度開いて、買い替えの年が近いものを確認するだけです。
  </div>'''

    guide = [("エアコン", "9年"), ("冷蔵庫", "9年"), ("テレビ", "8年"),
             ("電子レンジ", "8年"), ("洗濯機", "6年"), ("炊飯器", "6年"), ("掃除機", "6年")]
    g = "　／　".join(f'<b>{a}</b> {b}' for a, b in guide)

    body = rows(18, 6, "8.6mm")
    p2 = f'''<div class="head">
    <div><h1 style="font-size:21pt;">家電の一覧<small>1台1行。全部埋めなくて構いません。大きい物から書いてください</small></h1></div>
    <div class="fields">書いた日 <span class="fld" style="width:14mm;"></span> 年
      <span class="fld" style="width:10mm;"></span> 月</div>
  </div>

  <div class="note" style="margin-top:3mm;line-height:1.9;">部品保有期間の目安　{g}</div>

  <table style="margin-top:2mm;">
    <tr class="hl"><th style="width:30mm;">品目</th><th style="width:38mm;">メーカー・型番</th>
      <th style="width:20mm;">買った年</th><th style="width:26mm;">保証の期限</th>
      <th style="width:24mm;">買い替えの年</th><th>気になっていること（音・冷え・水漏れ）</th></tr>
    {body}
  </table>

  <div class="box accentbox" style="margin-top:3mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">「保証の期限」の欄について</h3>
    <b>保証は2つあります。</b>メーカー保証（ふつう1年）と、店で付けた延長保証（5年・10年など）。<br>
    <b>延長保証は、加入したこと自体を忘れる人がほとんどです。</b>
    有償で直した後に「保証に入っていた」と気づいても、戻りません。
    <b>今日ここに書いて、保証書の場所も決めてください。</b>
  </div>

  <div class="box" style="margin-top:2.5mm;padding:2.5mm 4.5mm;line-height:1.6;">
    <h3 style="font-size:10.5pt;">いちばん右の欄が、予告になります</h3>
    「最近うるさい」「氷ができるのが遅い」「脱水で止まる」。
    <b>家電は、いきなり壊れる前に必ず変な音や動きが出ます。</b>
    ここに書いておくと、次に開いたときに「そういえば去年から言っていた」と分かります。
  </div>'''

    p3 = f'''<h1 style="font-size:21pt;">買い替えの前に決めておくこと<small>金額と、捨て方。この2つで慌てます</small></h1>

  <div class="box accentbox">
    <h3>まず、いくら用意しておくか</h3>
    2ページ目を見て、<b>これから3年以内に買い替えの年が来るもの</b>を書き出してください。
    <table style="margin-top:2mm;">
      <tr class="hl"><th style="width:52mm;">品目</th><th style="width:34mm;">買い替えの年</th><th>だいたいの金額</th></tr>
      {rows(4, 3, "8.4mm")}
      <tr class="sum"><td>合計</td><td></td><td></td></tr>
    </table>
    <div style="margin-top:2.5mm;font-size:11pt;line-height:1.9;">
      合計　<span class="fld" style="width:26mm;"></span> 円　÷　36ヶ月　＝　
      <b>毎月よけておく額　<span class="fld" style="width:24mm;"></span> 円</b></div>
    <div class="note" style="margin-top:1mm;">この額を毎月別にしておけば、その年が来ても、選ぶ時間があります。</div>
  </div>

  <div class="box">
    <h3>捨てるのに、お金と手間がかかります</h3>
    <b>エアコン・テレビ・冷蔵庫・洗濯機の4品目</b>は、家電リサイクル法の対象です。
    ゴミには出せません。<b>リサイクル料金と、運ぶための費用がかかります。</b><br>
    買い替えなら、<b>買う店に引き取りを頼むのが一番早い</b>です（購入時に伝える必要があります）。
    処分だけなら、自治体の案内する方法か、指定の引取場所に持ち込みます。
  </div>

  <div class="box">
    <h3>直すか、買い替えるか。この3つで決めてください</h3>
    <b>1. 部品保有期間を過ぎている</b>　→　買い替え。次に別の場所が壊れても、もう直せません<br>
    <b>2. 修理の見積が、新品の半額を超えた</b>　→　買い替え。同じ金額で保証が新しく付きます<br>
    <b>3. 出張費と診断料は、直さなくてもかかることがあります</b>　→　電話の時点で
    <b>「見るだけでいくらかかりますか」</b>と先に聞いてください
  </div>

  <div class="box">
    <h3>買う時期を、少しずらすだけで変わります</h3>
    <b>エアコンを7月に買うのが、いちばん高くつきます。</b>本体も高く、工事も1〜2週間待ちます。<br>
    暑くなる前、寒くなる前。<b>「まだ動いているうち」に動くのが唯一の方法</b>です。
    2ページ目に買い替えの年を書いておくのは、そのためです。
  </div>

  <div class="box" style="margin-top:auto;">
    <h3>今日、ここだけ決めてください</h3>
    <div style="line-height:2;">
      保証書・取扱説明書の保管場所　<span class="fld" style="width:64mm;"></span><br>
      次にこの紙を開く月　<span class="fld" style="width:20mm;"></span> 月
      <span class="note">（年末か、年度初めをおすすめします）</span></div>
  </div>'''

    return [page(p1, "家電の買い替え年表", "1 / 3　使い方と部品の期限"),
            page(p2, "家電の買い替え年表", "2 / 3　家電の一覧"),
            page(p3, "家電の買い替え年表", "3 / 3　お金と捨て方")]


PRODUCTS.update({"kaden": ("家電の買い替え年表", kaden)})
