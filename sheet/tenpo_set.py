# シフト・発注・新人教育を1ファイルにまとめた版（A4横・9ページ）
import importlib.util, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("tg", os.path.join(HERE, "tenpo_gen.py"))
tg = importlib.util.module_from_spec(spec); spec.loader.exec_module(tg)

parts = [("シフト表", tg.shift_pages()),
         ("発注表", tg.order_pages()),
         ("新人教育チェック表", tg.train_pages())]
TOTAL = 1 + sum(len(p) for _, p in parts)

rows, n = "", 2
for name, pgs in parts:
    rows += (f'<tr><td style="padding:1.6mm 3mm;font-size:10pt;"><b>{name}</b></td>'
             f'<td style="padding:1.6mm 3mm;font-size:10pt;text-align:right;width:34mm;'
             f'white-space:nowrap;">{n} 〜 {n+len(pgs)-1} ページ</td></tr>')
    n += len(pgs)

cover = f'''<div class="page">
  <div style="font-size:10.5pt;letter-spacing:.3em;color:#F0A202;font-weight:700;margin-top:5mm;">飲食店の書式セット</div>
  <h1 style="font-size:28pt;margin-top:4mm;line-height:1.25;">シフト・発注・新人教育</h1>
  <p style="font-size:11pt;margin-top:3mm;opacity:.85;line-height:1.6;">
    毎月・毎週・人が入るたび。<b>必ず発生するのに、毎回ゼロから考えている作業</b>を3つ集めました。<br>
    A4横・印刷してそのまま使えます。</p>

  <table style="margin-top:5mm;">{rows}</table>

  <div style="display:flex;gap:7mm;margin-top:5mm;">
    <div class="guide" style="flex:1;margin:0;padding:3mm 4.5mm;">
      <h3 style="font-size:10.5pt;">3つに共通していること</h3>
      どれも<b>「その場で判断させない」</b>ための紙です。<br>
      シフトは先に人数を決める。発注は先に発注点を決める。教育は先に順番を決める。<br>
      決めてしまえば、あとは紙を見るだけになり、<b>人に任せられるようになります。</b>
    </div>
    <div class="guide accentbox" style="flex:1;margin:0;padding:3mm 4.5mm;">
      <h3 style="font-size:10.5pt;">最初にやること</h3>
      3つとも、<b>最初の1回だけ書き込む欄</b>があります。<br>
      ・発注表の「定番品リスト」<br>
      ・新人教育の「覚えることリスト」<br>
      ここさえ埋めれば、次の月からはコピーして使うだけです。<b>今日はここだけで構いません。</b>
    </div>
  </div>

  <div class="foot"><span>飲食店の書式セット</span><span>1 / {TOTAL}</span></div>
</div>'''

pages = [cover] + [p for _, pgs in parts for p in pgs]
out = []
for i, p in enumerate(pages, 1):
    p = re.sub(r'(<div class="foot"><span>.*?</span><span>).*?(</span></div>)',
               lambda m: m.group(1) + f"{i} / {TOTAL}" + m.group(2), p, flags=re.S)
    out.append(p)

html = ('<meta charset="utf-8">\n<title>飲食店の書式セット（シフト・発注・新人教育）</title>\n'
        + tg.STYLE + "\n" + "\n".join(out))
chars = set(html) | set("0123456789○×／−")
html = html.replace("<style>", "<style>\n" + tg.font_faces(
    "".join(sorted(c for c in chars if c.strip()))) + "\n", 1)

tmp, pdf = "/tmp/_tenpo_set.html", os.path.join(HERE, "tenpo-set.pdf")
open(tmp, "w", encoding="utf-8").write(html)
subprocess.run(["/opt/pw-browsers/chromium", "--headless", "--no-sandbox", "--disable-gpu",
                "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
                "--virtual-time-budget=12000", f"--print-to-pdf={pdf}", "file://" + tmp],
               check=True, capture_output=True)
print("expected:", TOTAL, "size:", os.path.getsize(pdf))
