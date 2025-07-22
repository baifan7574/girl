import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

# === 配置读取 ===
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

domain = config.get("domain").rstrip("/")
base_dir = os.getcwd()
keywords_dir = os.path.join(base_dir, "keywords")
output_dir = base_dir

sitemap_entries = set()
latest_images_per_cat = {}

# === 扫描分类，提取最新4张图 ===
for category in sorted(os.listdir(base_dir)):
    cat_path = os.path.join(base_dir, category)
    if not os.path.isdir(cat_path): continue
    if category in ["keywords", "generator", "static", "__pycache__"]: continue

    images = sorted(
        [f for f in os.listdir(cat_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))],
        reverse=True
    )
    if not images:
        continue

    latest_images_per_cat[category] = images[:4]

    # === 单图页生成 ===
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

# === sitemap.xml 生成 ===
now = datetime.today().strftime("%Y-%m-%d")
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for url in sorted(sitemap_entries):
        f.write(f"  <url><loc>{url}</loc><lastmod>{now}</lastmod></url>\n")
    f.write('</urlset>')

print(f"✅ sitemap.xml 写入完成，共 {len(sitemap_entries)} 个页面")

# === 修改主页 index.html，只换图片，不改结构 ===
index_path = os.path.join(base_dir, "index.html")
if os.path.exists(index_path):
    with open(index_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for section in soup.find_all("div", class_="section"):
        h2 = section.find("h2")
        if not h2: continue
        cat = h2.text.strip().lower()
        if cat in latest_images_per_cat:
            gallery = section.find("div", class_="gallery")
            if gallery:
                gallery.clear()
                for img in latest_images_per_cat[cat]:
                    img_path = f"{cat}/{img}"
                    tag = soup.new_tag("a", href=img_path, **{"data-lightbox": cat})
                    img_tag = soup.new_tag("img", src=img_path)
                    tag.append(img_tag)
                    gallery.append(tag)

    # 插入 ads.js 引用
    if not soup.find("script", {"src": "ads.js"}):
        script_tag = soup.new_tag("script", src="ads.js")
        soup.body.append(script_tag)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print("✅ index.html 已更新（图片替换、结构保持、广告插入）")
else:
    print("⚠️ 未找到 index.html，无法修改主页。")