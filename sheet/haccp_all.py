# 全8業種をまとめた1ファイル版（A4横・33ページ）
import importlib.util, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("hg", os.path.join(HERE, "haccp_gen.py"))
hg = importlib.util.module_from_spec(spec); spec.loader.exec_module(hg)

TOTAL = 1 + len(hg.SHOPS) * 4

toc = "".join(
    f'<tr><td style="padding:1.2mm 3mm;font-size:9.5pt;"><b>{s["name"]}</b>'
    f'<span style="opacity:.65;font-size:8pt;">　{s["note"]}</span></td>'
    f'<td style="padding:1.2mm 3mm;font-size:9.5pt;text-align:right;width:32mm;'
    f'white-space:nowrap;">{2 + i*4} 〜 {5 + i*4} ページ</td></tr>'
    for i, s in enumerate(hg.SHOPS))

cover = f'''<div class="page">
  <div style="font-size:10.5pt;letter-spacing:.3em;color:#F0A202;font-weight:700;margin-top:3mm;">HACCP 記録様式　全8業種</div>
  <h1 style="font-size:27pt;margin-top:3mm;line-height:1.25;">飲食店の衛生管理記録表</h1>
  <p style="font-size:11pt;margin-top:2.5mm;opacity:.85;line-height:1.6;">
    1ヶ月1枚。閉店後に○を書くだけ。A4横・印刷してそのまま使えます。<br>
    <b>自分の業種のページだけ印刷してください。</b>1業種につき4ページです。</p>

  <table style="margin-top:4mm;">{toc}</table>

  <div style="display:flex;gap:7mm;margin-top:4mm;">
    <div class="guide" style="flex:1;margin:0;padding:2.5mm 4mm;font-size:8.6pt;">
      <h3 style="font-size:10pt;">1業種に入っているもの（4ページ）</h3>
      1. 使い方と、その業種で守るべき法令　／　2. 記入例（○×／の書き方、特記事項の実例）<br>
      3. 一般衛生管理の記録（10〜11項目 × 31日）　／　4. 重要管理の記録（メニュー分類 × 31日）
    </div>
    <div class="law" style="flex:1;margin:0;padding:2.5mm 4mm;font-size:8.6pt;">
      <h3 style="font-size:10pt;">先に読んでください</h3>
      この様式は<b>例示</b>です。業種別手引書に指定の様式がある場合は、項目名をそちらに合わせてください。
      保存期間は手引書に従ってください（1年程度が目安）。提出の義務はなく、店に置いておけば足ります。
    </div>
  </div>

  <div class="foot"><span>飲食店の衛生管理記録表　全8業種</span><span>1 / {TOTAL}</span></div>
</div>'''

pages = [cover]
for s in hg.SHOPS:
    gen_rows = "".join(hg.row(t, x) for t, x in hg.BASE_GEN + s["extra"])
    imp_rows = ""
    for st, rows in s["imp"]:
        imp_rows += hg.sec(st) + "".join(hg.row(t, x) for t, x in rows)
    pages += [
        hg.howto_page(s),
        hg.rei_page(s),
        hg.record_page("一般衛生管理の記録", s["name"], gen_rows,
            "<span><b>○</b>＝問題なし　<b>×</b>＝問題あり（下の特記事項に書く）　<b>／</b>＝休業日</span>"
            "<span>記入は<b>1日1回</b>、閉店後にまとめてで構いません。</span>",
            "問題があったこと／どう対応したか", f'{s["name"]}｜一般衛生管理', ""),
        hg.record_page("重要管理の記録", f'{s["name"]}／その日出したものだけ確認します', imp_rows,
            "<span><b>○</b>＝問題なし　<b>×</b>＝問題あり　<b>／</b>＝その日出していない／休業日</span>"
            "<span>温度を測った日は、数字を書いておくとより確実です。</span>",
            "問題があったこと／どう対応したか（出さずに廃棄した・加熱し直した など）",
            f'{s["name"]}｜重要管理', ""),
    ]

out = []
for n, p in enumerate(pages, 1):
    p = re.sub(r'(<div class="foot"><span>.*?</span><span>).*?(</span></div>)',
               lambda m: m.group(1) + f"{n} / {TOTAL}" + m.group(2), p, flags=re.S)
    out.append(p)

html = ('<meta charset="utf-8">\n'
        '<title>飲食店の衛生管理記録表 全8業種（HACCPの考え方を取り入れた衛生管理）</title>\n'
        + hg.STYLE + "\n" + "\n".join(out))
chars = set(html) | set("0123456789○×／℃−")
html = html.replace("<style>", "<style>\n" + hg.font_faces(
    "".join(sorted(c for c in chars if c.strip()))) + "\n", 1)

tmp = "/tmp/_haccp_all.html"
pdf = os.path.join(HERE, "haccp-all.pdf")
open(tmp, "w", encoding="utf-8").write(html)
subprocess.run(["/opt/pw-browsers/chromium", "--headless", "--no-sandbox", "--disable-gpu",
                "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
                "--virtual-time-budget=15000", f"--print-to-pdf={pdf}", "file://" + tmp],
               check=True, capture_output=True)
print("pages(expected):", TOTAL, "size:", os.path.getsize(pdf))
