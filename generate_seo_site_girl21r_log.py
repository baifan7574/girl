
import os
from pathlib import Path
from datetime import datetime
import random

# === 配置 ===
base_dir = Path(".")
output_dir = base_dir
keywords_dir = base_dir / "keywords"
domain = "https://girl-21r.pages.dev"

exclude_dirs = {"generator", "keywords", "pages"}

# === 模板内容（简略示例） ===
image_block_template = '<div><img src="{img_src}" alt="{alt}"><p>{alt}</p></div>\n'
category_template = """
<html>
<head><title>{category}</title><meta charset="utf-8"></head>
<body>
<h1>{category}</h1>
{image_blocks}
<div>{pagination}</div>
<p>{keywords}</p>
</body>
</html>
"""

# === 工具函数 ===
def load_keywords(category):
    filepath = keywords_dir / f"{category}.txt"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def generate_seo_text(words, count=5):
    return ", ".join(random.sample(words, min(len(words), count))) if words else ""

# === 主逻辑 ===
sitemap_entries = []

for folder in sorted(base_dir.iterdir()):
    if not folder.is_dir() or folder.name in exclude_dirs or folder.name.startswith("."):
        continue

    print("👉 正在处理分类：", folder.name)

    category = folder.name
    keywords = load_keywords(category)
    if not keywords:
        print(f"⚠️ 没有关键词，跳过：{category}")
        continue

    image_files = sorted([f for f in folder.iterdir() if f.suffix.lower() in {".jpg", ".jpeg", ".png"}])
    if not image_files:
        print(f"⚠️ 没有图片，跳过：{category}")
        continue

    image_blocks = ""
    for i, img in enumerate(image_files):
        img_src = f"{category}/{img.name}"
        title = img.stem.replace("_", " ")
        image_page_name = f"image_{category}_{i+1:03}.html"
        image_blocks += image_block_template.format(image_page=image_page_name, img_src=img_src, alt=title)
        sitemap_entries.append(f"{domain}/{image_page_name}")

    page_name = f"{category}.html"
    with open(base_dir / page_name, "w", encoding="utf-8") as f:
        f.write(category_template.format(
            category=category.capitalize(),
            image_blocks=image_blocks,
            pagination="",
            keywords=generate_seo_text(keywords, 6)
        ))
    sitemap_entries.append(f"{domain}/{page_name}")

# === 写 sitemap ===
now = datetime.utcnow().strftime("%Y-%m-%d")
with open(base_dir / "sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for url in sitemap_entries:
        f.write(f"  <url><loc>{url}</loc><lastmod>{now}</lastmod></url>\n")
    f.write("</urlset>")
