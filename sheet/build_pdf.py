import base64, os, re, subprocess, urllib.parse, urllib.request, ssl, sys

SRC = "/home/user/mori/sheet/tsukenai-kakeibo.html"
OUT_HTML = "/tmp/claude-0/-home-user-mori/5e5d14c7-11a7-55e8-b81e-a8f9cee12367/scratchpad/embedded.html"
OUT_PDF = "/home/user/mori/sheet/tsukenai-kakeibo.pdf"

html = open(SRC, encoding="utf-8").read()

# characters that actually need rendering: everything in the file + a safety set
chars = set(html)
chars |= set("0123456789０１２３４５６７８９円月日年％%,.、。ー－")
text = "".join(sorted(c for c in chars if c.strip()))

ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, context=ctx, timeout=90) as r:
        data = r.read()
    return data if binary else data.decode("utf-8")

css_url = ("https://fonts.googleapis.com/css2?family="
           + urllib.parse.quote("Noto Sans JP:wght@400;700")
           + "&text=" + urllib.parse.quote(text))
css = get(css_url)

faces = []
for block in re.findall(r"@font-face\s*\{[^}]*\}", css):
    weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
    url = re.search(r"url\((https://[^)]+)\)", block).group(1)
    fmt = "woff2" if url.endswith(".woff2") else "truetype"
    b64 = base64.b64encode(get(url, binary=True)).decode()
    faces.append(
        "@font-face{font-family:'Noto Sans JP';font-style:normal;"
        f"font-weight:{weight};"
        f"src:url(data:font/{fmt};base64,{b64}) format('{fmt}');}}"
    )
    print(f"  weight {weight}: {len(b64)//1024} KB", file=sys.stderr)

if not faces:
    sys.exit("no @font-face blocks returned")

html = html.replace("<style>", "<style>\n" + "\n".join(faces) + "\n", 1)
open(OUT_HTML, "w", encoding="utf-8").write(html)

subprocess.run([
    "/opt/pw-browsers/chromium", "--headless", "--no-sandbox", "--disable-gpu",
    "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=8000",
    f"--print-to-pdf={OUT_PDF}", "file://" + OUT_HTML,
], check=True, capture_output=True)

print("PDF:", OUT_PDF, os.path.getsize(OUT_PDF), "bytes")
