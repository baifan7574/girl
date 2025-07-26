
import os
import json
from datetime import datetime

# === 配置读取 ===
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

domain = config.get("domain").rstrip("/")
base_dir = os.getcwd()
keywords_dir = os.path.join(base_dir, "keywords")
output_dir = base_dir

sitemap_entries = set()

# === 遍历分类目录 ===
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

        json_ld = (
            '<script type="application/ld+json">\n'
            '{\n'
            '  "@context": "https://schema.org",\n'
            '  "@type": "ImageObject",\n'
            f'  "contentUrl": "{domain}/{img_path}",\n'
            f'  "name": "{alt}",\n'
            f'  "description": "{alt}",\n'
            '  "author": {\n'
            '    "@type": "Organization",\n'
            '    "name": "Gentleman\'s Frame"\n'
            '  }\n'
            '}\n'
            '</script>'
        )

        html = (
            "<html><head>\n"
            "<meta charset='utf-8'>\n"
            f"<title>{alt}</title>\n"
            f"<meta name='description' content='{alt} gallery photo'>\n"
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
            f"{json_ld}\n"
            "</head><body>\n"
            f"{nav_links}\n"
            f"<h1 style='text-align:center;'>{alt}</h1>\n"
            f"<div style='text-align:center;'><img src='{img_path}' alt='{alt}' style='max-width:100%;height:auto;'></div>\n"
            f"{nav_links}\n"
            '<script src="ads.js"></script>\n'
            "</body></html>"
        )

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

# === 生成 robots.txt ===
robots_txt = (
    "User-agent: *\n"
    "Allow: /\n"
    f"Sitemap: {domain}/sitemap.xml\n"
)
with open("robots.txt", "w", encoding="utf-8") as f:
    f.write(robots_txt)

print("✅ V10脚本完成：保留V9所有功能 + Schema.org结构化数据 + 自动robots.txt")
