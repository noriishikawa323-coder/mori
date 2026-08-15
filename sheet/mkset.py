import re

SH = "/home/user/mori/sheet/"

def extract_pages(src):
    """トップレベルの <div class="page"> ... </div> を深さを数えて切り出す"""
    out, i = [], 0
    while True:
        m = re.compile(r'<div class="page"[^>]*>').search(src, i)
        if not m:
            return out
        start, depth, j = m.start(), 1, m.end()
        tag = re.compile(r'<div\b[^>]*>|</div>')
        while depth:
            t = tag.search(src, j)
            depth += 1 if t.group(0) != "</div>" else -1
            j = t.end()
        out.append(src[start:j])
        i = j

gen = open(SH + "haccp.html", encoding="utf-8").read()
yak = open(SH + "haccp-yakiniku.html", encoding="utf-8").read()
head = yak[:yak.index('<div class="page"')]
head = head.replace("焼肉屋の衛生管理記録表（HACCPの考え方を取り入れた衛生管理）",
                    "飲食店の衛生管理記録表セット（HACCPの考え方を取り入れた衛生管理）")

gp, yp = extract_pages(gen), extract_pages(yak)
assert len(gp) == 3 and len(yp) == 3, (len(gp), len(yp))

def refoot(html, left, right):
    return re.sub(r'<div class="foot">.*?</div>',
                  f'<div class="foot"><span>{left}</span><span>{right}</span></div>',
                  html, flags=re.S)

def retitle(html, sub):
    return re.sub(r'<small>.*?</small>', f'<small>{sub}</small>', html, count=1, flags=re.S)

cover = '''<div class="page">
  <div style="font-size:11pt;letter-spacing:.3em;color:#F0A202;font-weight:700;margin-top:6mm;">HACCP 記録様式セット</div>
  <h1 style="font-size:31pt;margin-top:4mm;line-height:1.25;">飲食店の衛生管理記録表<br>一般飲食店版＋焼肉店版</h1>
  <p style="font-size:11.5pt;margin-top:4mm;opacity:.8;">1ヶ月1枚。閉店後に○を書くだけ。A4横・印刷してそのまま使えます。</p>

  <div style="display:flex;gap:8mm;margin-top:7mm;">
    <div class="guide" style="flex:1;margin:0;">
      <h3>入っているもの</h3>
      ・使い方と、守るべき法令<br>
      ・記入例<br>
      ・一般衛生管理の記録（一般飲食店版）<br>
      ・重要管理の記録（一般飲食店版）<br>
      ・一般衛生管理の記録（焼肉店版）<br>
      ・重要管理の記録（焼肉店版）
    </div>
    <div class="guide" style="flex:1;margin:0;">
      <h3>どちらの版を使うか</h3>
      <b>焼肉・ホルモンなど、客席で焼く店</b><br>　→ 焼肉店版<br>
      <b>それ以外の飲食店</b><br>　→ 一般飲食店版<br><br>
      両方使っても構いません。要らない項目は線で消し、足りない項目は書き足してください。
    </div>
  </div>

  <div class="law" style="margin-top:7mm;">
    <h3>先に読んでください</h3>
    この様式は<b>例示</b>です。業種別手引書に指定の様式がある場合は、項目名をそちらに合わせてください。記録すべき内容が同じであれば、書式が違っても差し支えありません。<br>
    保存期間は手引書に従ってください（1年程度としているものが多いです）。提出の義務はなく、店に置いておけば足ります。
  </div>

  <div class="foot"><span>HACCP 記録様式セット</span><span>1 / 7</span></div>
</div>'''

def cell(v, mark=False):
    st = "text-align:center;font-size:11pt;"
    if mark:
        st += "color:#F0A202;font-weight:700;"
    return f'<td class="d" style="{st}">{v}</td>'

def sample(vals):
    s = ""
    for v in vals:
        s += cell(v, v == "×") if v else '<td class="d"></td>'
    return s

rei = '''<div class="page">
  <div class="head"><h1>記入例<small>迷うのは最初の1週間だけです</small></h1></div>

  <table class="cal" style="margin-top:5mm;">
    <tr><th class="item" style="width:64mm;">確認すること</th>''' + \
    "".join(f'<th class="day">{d}</th>' for d in range(1, 11)) + '''</tr>
    <tr><td class="item"><b>冷蔵庫の温度（10℃以下）</b><span>庫内の温度計を見る</span></td>''' + \
    sample(["○","○","／","○","×","○","○","","",""]) + '''</tr>
    <tr><td class="item"><b>手洗いの実施</b><span>作業前・トイレ後・生肉を触った後</span></td>''' + \
    sample(["○","○","／","○","○","○","○","","",""]) + '''</tr>
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

  <div class="foot"><span>記入例</span><span>3 / 7</span></div>
</div>'''

body = "\n".join([
    cover,
    refoot(yp[2], "使い方", "2 / 7"),
    rei,
    refoot(retitle(gp[0], "一般飲食店版"), "一般飲食店版｜一般衛生管理", "4 / 7"),
    refoot(retitle(gp[1], "一般飲食店版／メニューを3つに分けて、その日つくったものだけ確認します"),
           "一般飲食店版｜重要管理", "5 / 7"),
    refoot(retitle(yp[0], "焼肉店版"), "焼肉店版｜一般衛生管理", "6 / 7"),
    refoot(retitle(yp[1], "焼肉店版／メニューを4つに分けて、その日出したものだけ確認します"),
           "焼肉店版｜重要管理", "7 / 7"),
])

open(SH + "haccp-set.html", "w", encoding="utf-8").write(head + body)
print("pages:", body.count('class="page"'))
