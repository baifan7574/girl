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

# === 遍历所有分类 ===
for category in sorted(os.listdir(base_dir)):
    cat_path = os.path.join(base_dir, category)
    if not os.path.isdir(cat_path): continue
    if category in ["keywords", "generator", "static", "__pycache__"]: continue

    images = [f for f in os.listdir(cat_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not images: continue

    keyword_file = os.path.join(keywords_dir, f"{category}.txt")
    keywords = []
    if os.path.exists(keyword_file):
        with open(keyword_file, "r", encoding="utf-8") as kf:
            keywords = [line.strip() for line in kf if line.strip()]

    print(f"📂 分类：{category}（共 {len(images)} 张图）")

    for i, img in enumerate(images):
        page_name = f"image_{category}_{i+1:04}.html"
        img_path = f"{category}/{img}"
        alt = keywords[i % len(keywords)] if keywords else f"{category} image {i+1}"
        html_path = os.path.join(output_dir, page_name)

        # 如果页面文件不存在，则新建
        if not os.path.exists(html_path):
            html = f"""<html><head>
<meta charset='utf-8'>
<title>{alt}</title>
<meta name='description' content='{alt} gallery photo'>
<meta name='viewport' content='width=device-width, initial-scale=1.0'>
</head><body>
<h1>{alt}</h1>
<img src='{img_path}' alt='{alt}' style='max-width:100%;height:auto;'>
</body></html>"""
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)

        # ✅ 将 image 页面加入 sitemap
        sitemap_entries.add(f"{domain}/{page_name}")

    # ✅ 分类页也加入 sitemap
    cat_page = f"{category}.html"
    if os.path.exists(os.path.join(output_dir, cat_page)):
        sitemap_entries.add(f"{domain}/{cat_page}")

# ✅ 强行扫描所有 image_*.html 页纳入 sitemap（防遗漏）
for f in os.listdir(output_dir):
    if f.startswith("image_") and f.endswith(".html"):
        sitemap_entries.add(f"{domain}/{f}")

# === 写 sitemap.xml ===
now = datetime.today().strftime("%Y-%m-%d")
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for url in sorted(sitemap_entries):
        f.write(f"  <url><loc>{url}</loc><lastmod>{now}</lastmod></url>\n")
    f.write('</urlset>')

print(f"✅ sitemap.xml 写入完成，共 {len(sitemap_entries)} 个页面")
