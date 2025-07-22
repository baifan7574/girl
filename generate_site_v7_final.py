import os
import json
from datetime import datetime

# === 配置读取 ===
with open("config.json", "r", encoding="utf-8") as f_conf:
    config = json.load(f_conf)

domain = config.get("domain").rstrip("/")
base_dir = os.getcwd()
keywords_dir = os.path.join(base_dir, "keywords")
output_dir = base_dir

sitemap_entries = set()
latest_images = {}

# === 遍历所有分类 ===
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
        nav_links += "<a href='index.html'>⬅️ Back to Home</a>"
        if prev_link:
            nav_links += f" | <a href='{prev_link}'>⬅️ Previous</a>"
        if next_link:
            nav_links += f" | <a href='{next_link}'>Next ➡️</a>"
        nav_links += "</div>"

        if not os.path.exists(html_path):
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

    if images:
        latest_img = images[-1]
        latest_img_path = f"{category}/{images[-1]}"
        latest_images[category] = latest_img_path

    cat_page = f"{category}.html"
    if os.path.exists(os.path.join(output_dir, cat_page)):
        sitemap_entries.add(f"{domain}/{cat_page}")

# === 强制纳入所有 image_ 页面 ===
for f_item in os.listdir(output_dir):
    if f_item.startswith("image_") and f_item.endswith(".html"):
        sitemap_entries.add(f"{domain}/{f_item}")

# === 写 sitemap.xml ===
now = datetime.today().strftime("%Y-%m-%d")
with open("sitemap.xml", "w", encoding="utf-8") as f_map:
    f_map.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f_map.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for url in sorted(sitemap_entries):
        f_map.write(f"  <url><loc>{url}</loc><lastmod>{now}</lastmod></url>\n")
    f_map.write('</urlset>')

print(f"✅ sitemap.xml 写入完成，共 {len(sitemap_entries)} 个页面")

# === 写 index.html，保持原结构，更新封面图 ===
with open("index.html", "w", encoding="utf-8") as f_index:
    f_index.write("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>GentleGallery</title>
  <meta name="description" content="Gallery of sensual and aesthetic photography in multiple styles.">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>GentleGallery</h1>
    <p class="tagline">For Men Who Appreciate More Than Beauty.</p>
  </header>
<main>
  <section class="grid">
""")
    for cat in sorted(latest_images.keys()):
        img_src = latest_images[cat]
        f_index.write(f"    <a class='category' href='{cat}/index.html'>\n")
        f_index.write(f"      <img src='{img_src}' alt='{cat.title()} Collection'>\n")
        f_index.write(f"      <span>{cat.title()}</span>\n")
        f_index.write("    </a>\n")
    f_index.write("""
  </section>
</main>
  <footer><p>&copy; 2025 GentleGallery. All rights reserved.</p></footer>
  <script src="ads.js"></script>
</body>
</html>
""")

print("✅ index.html 已更新（封面图已替换为每类最新图片）")