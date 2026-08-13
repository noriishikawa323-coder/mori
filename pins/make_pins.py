import base64, os, re, ssl, subprocess, sys, urllib.parse, urllib.request

SCR = "/tmp/claude-0/-home-user-mori/5e5d14c7-11a7-55e8-b81e-a8f9cee12367/scratchpad"
OUT = "/home/user/mori/pins"
os.makedirs(OUT, exist_ok=True)

PINS = [
    dict(slug="kakeibo", title="つけない家計簿", lead="書くのは数字5つだけ",
         bullets=["費目分けなし", "月1回・5分", "スマホで書ける"],
         img=f"{SCR}/pg3.png", accent="#F0A202"),
    dict(slug="subsc", title="サブスク棚おろし", lead="年1回15分で全部出す",
         bullets=["一覧の開き方つき", "今日は解約しなくていい", "年間いくらか分かる"],
         img=f"{SCR}/s2.png", accent="#F0A202"),
    dict(slug="souji", title="順番を決めない掃除", lead="週1回・1つだけ",
         bullets=["やる場所を選ばない", "日付を書くだけ", "抜けても戻れる"],
         img=f"{SCR}/c2.png", accent="#F0A202"),
]

# ---- フォント（必要な字だけ取得して埋め込む） ----
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, context=ctx, timeout=90) as r:
        d = r.read()
    return d if binary else d.decode()

chars = set("テンプレートPDF・")
for p in PINS:
    chars |= set(p["title"] + p["lead"] + "".join(p["bullets"]))
text = "".join(sorted(c for c in chars if c.strip()))
css = get("https://fonts.googleapis.com/css2?family="
          + urllib.parse.quote("Noto Sans JP:wght@400;700")
          + "&text=" + urllib.parse.quote(text))
faces = []
for block in re.findall(r"@font-face\s*\{[^}]*\}", css):
    w = re.search(r"font-weight:\s*(\d+)", block).group(1)
    u = re.search(r"url\((https://[^)]+)\)", block).group(1)
    b64 = base64.b64encode(get(u, binary=True)).decode()
    faces.append("@font-face{font-family:'NS';font-style:normal;font-weight:%s;"
                 "src:url(data:font/woff2;base64,%s) format('woff2');}" % (w, b64))
FONT = "\n".join(faces)

TPL = """<meta charset="utf-8"><style>
%(font)s
*{margin:0;padding:0;box-sizing:border-box}
body{width:1000px;height:1500px;font-family:'NS',sans-serif;color:#2B3A55;
  background:#FAF7F2;display:flex;flex-direction:column;align-items:center;
  padding:60px 56px 90px;overflow:hidden}
.kicker{font-size:26px;font-weight:700;letter-spacing:.24em;color:%(accent)s}
h1{font-size:94px;font-weight:700;line-height:1.16;text-align:center;margin-top:22px}
.lead{font-size:40px;margin-top:22px;opacity:.8}
.rule{width:120px;height:8px;background:%(accent)s;margin-top:34px;border-radius:4px}
.shot{margin-top:40px;width:620px;height:700px;overflow:hidden;
  box-shadow:0 26px 60px rgba(43,58,85,.28);
  border:1px solid rgba(43,58,85,.16);background:#fff}
.shot img{display:block;width:100%%}
ul{margin-top:auto;padding-top:30px;display:flex;gap:14px;list-style:none;flex-wrap:wrap;justify-content:center}
li{font-size:25px;font-weight:700;background:#fff;border:3px solid #2B3A55;
  border-radius:999px;padding:13px 22px;white-space:nowrap}
</style>
<div class="kicker">%(kicker)s</div>
<h1>%(title)s</h1>
<div class="lead">%(lead)s</div>
<div class="rule"></div>
<div class="shot"><img src="data:image/png;base64,%(img)s"></div>
<ul>%(bullets)s</ul>"""

for p in PINS:
    img = base64.b64encode(open(p["img"], "rb").read()).decode()
    html = TPL % dict(font=FONT, accent=p["accent"], kicker="PDF テンプレート",
                      title=p["title"], lead=p["lead"], img=img,
                      bullets="".join(f"<li>{b}</li>" for b in p["bullets"]))
    hp = f"{SCR}/pin_{p['slug']}.html"
    open(hp, "w", encoding="utf-8").write(html)
    subprocess.run([
        "/opt/pw-browsers/chromium", "--headless", "--no-sandbox", "--disable-gpu",
        "--hide-scrollbars", "--force-device-scale-factor=1",
        "--window-size=1000,1500", "--virtual-time-budget=6000",
        f"--screenshot={OUT}/pin-{p['slug']}.png", "file://" + hp,
    ], check=True, capture_output=True)
    print("pin:", f"{OUT}/pin-{p['slug']}.png", os.path.getsize(f"{OUT}/pin-{p['slug']}.png"))
