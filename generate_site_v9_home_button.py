import os
import json
from datetime import datetime

# === 读取配置 ===
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

domain = config.get("domain").rstrip("/")
base_dir = os.getcwd()
keywords_dir = os.path.join(base_dir, "keywords")
output_dir = base_dir

sitemap_entries = set()

# === 遍历每个分类，生成图页 ===
for category in sorted(os.listdir(base_dir)):
    cat_path = os.path.join(base_dir, category)
    if not os.path.isdir(cat_path): continue
    if category in ["keywords", "generator", "static", "__pycache__"]: continue

    images = sorted(
        [f for f in os.listdir(cat_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    )
    if not images: continue

    keyword_file = os.path.join(keywords_dir, f"{category}.txt")
    keywords = []
    if os.path.exists(keyword_file):
        with open(keyword_file, "r", encoding="utf-8") as kf:
            keywords = [line.strip() for line in kf if line.strip()]

    for i, img in enumerate(images):
        page_name = f"image_{category}_{i+1:04}.html"
        img_path = f"{category}/{img}"
        alt = keywords[i % len(keywords)] if keywords else f"{category} image {i+1}"
        html_path = os.path.join(output_dir, page_name)

        prev_link = f"image_{category}_{i:04}.html" if i > 0 else ""
        next_link = f"image_{category}_{i+2:04}.html" if i + 1 < len(images) else ""

        nav_links = "<div style='text-align:center;margin-top:20px;'>"
        nav_links += "<a href='index.html'>🏠 Back to Home</a>"
        if prev_link:
            nav_links += f" | <a href='{prev_link}'>⬅️ Previous</a>"
        if next_link:
            nav_links += f" | <a href='{next_link}'>Next ➡️</a>"
        nav_links += "</div>"

        html = f"""<html><head>
<meta charset='utf-8'>
<title>{alt}</title>
<meta name='description' content='{alt} gallery photo'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
</head><body>
{nav_links}
<h1 style='text-align:center;'>{alt}</h1>
<div style='text-align:center;'><img src='{img_path}' alt='{alt}' style='max-width:100%;height:auto;'></div>
{nav_links}
<script src="ads.js"></script>
</body></html>"""

        with open(html_path, "w", encoding="utf-8") as f_html:
            f_html.write(html)

        sitemap_entries.add(f"{domain}/{page_name}")

# === 写 sitemap.xml ===
now = datetime.today().strftime("%Y-%m-%d")
with open("sitemap.xml", "w", encoding="utf-8") as f_map:
    f_map.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f_map.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for url in sorted(sitemap_entries):
        f_map.write(f"  <url><loc>{url}</loc><lastmod>{now}</lastmod></url>\n")
    f_map.write('</urlset>')

print(f"✅ V9脚本执行完毕，所有单图页已添加“返回主页 + 上下页”导航，sitemap 也生成完毕。")