import os
from pathlib import Path
from datetime import datetime
import random
import json
import requests

# === 读取配置 ===
base_dir = Path(".")
config_file = base_dir / "config.json"
if not config_file.exists():
    print("❌ 缺少 config.json 文件，终止执行")
    exit(1)

with open(config_file, "r", encoding="utf-8") as f:
    config = json.load(f)

domain = config.get("domain", "").rstrip("/")
category_css = config.get("category_css", "style.css")
keywords_dir = base_dir / "keywords"
sitemap_entries = []
exclude_dirs = {"generator", "keywords", "pages", "static"}

# === HTML模板 ===
image_page_template = """<html>
<head>
  <meta charset='utf-8'>
  <title>{title}</title>
  <meta name='description' content='{description}'>
  <meta name='keywords' content='{keywords}'>
  <link rel='stylesheet' href='{css}'>
</head>
<body>
  <div class='image-block'>
    <img src='{img_src}' alt='{alt}'>
    <p>{alt}</p>
  </div>
  <div>{ad_block}</div>
</body>
</html>"""

category_page_template = """<html>
<head>
  <meta charset='utf-8'>
  <title>{title}</title>
  <meta name='description' content='{description}'>
  <meta name='keywords' content='{keywords}'>
  <link rel='stylesheet' href='{css}'>
</head>
<body>
  <h1>{category}</h1>
  {image_blocks}
  <div>{ad_block}</div>
</body>
</html>"""

image_block_template = """<div class='image-block'>
  <a href='{image_page}'><img src='{img_src}' alt='{alt}'></a>
  <p>{alt}</p>
</div>"""

ad_block_script = "<script src='https://example-adnetwork.com/script.js'></script>"

def load_keywords(category):
    path = keywords_dir / f"{category}.txt"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def generate_meta_keywords(words, count=6):
    return ", ".join(random.sample(words, min(len(words), count))) if words else ""

# === 主逻辑 ===
for folder in sorted(base_dir.iterdir()):
    if not folder.is_dir() or folder.name in exclude_dirs or folder.name.startswith("."):
        continue

    category = folder.name
    print(f"👉 正在处理分类：{category}")
    keywords = load_keywords(category)
    if not keywords:
        print(f"⚠️ 无关键词，跳过：{category}")
        continue

    image_files = sorted([f for f in folder.iterdir() if f.suffix.lower() in {".jpg", ".jpeg", ".png"}])
    if not image_files:
        print(f"⚠️ 无图片，跳过：{category}")
        continue

    image_blocks = ""
    for i, img in enumerate(image_files):
        img_src = f"{category}/{img.name}"
        alt_text = random.choice(keywords) if keywords else img.stem
        image_page = f"image_{category}_{i+1:04}.html"

        html_img = image_page_template.format(
            title=f"{alt_text} - {category.capitalize()}",
            description=f"High quality image in {category}",
            keywords=generate_meta_keywords(keywords),
            css=category_css,
            img_src=img_src,
            alt=alt_text,
            ad_block=ad_block_script
        )
        with open(base_dir / image_page, "w", encoding="utf-8") as f:
            f.write(html_img)

        image_blocks += image_block_template.format(image_page=image_page, img_src=img_src, alt=alt_text)
        sitemap_entries.append(f"{domain}/{image_page}")

    cat_html = category_page_template.format(
        title=f"{category.capitalize()} - Gallery",
        description=f"Explore {category} image collection",
        keywords=generate_meta_keywords(keywords),
        css=category_css,
        category=category.capitalize(),
        image_blocks=image_blocks,
        ad_block=ad_block_script
    )
    page_name = f"{category}.html"
    with open(base_dir / page_name, "w", encoding="utf-8") as f:
        f.write(cat_html)
    sitemap_entries.append(f"{domain}/{page_name}")

# === 写 sitemap.xml ===
now = datetime.utcnow().strftime("%Y-%m-%d")
with open(base_dir / "sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for url in sitemap_entries:
        f.write(f"  <url><loc>{url}</loc><lastmod>{now}</lastmod></url>\n")
    f.write("</urlset>")

try:
    ping_url = f"https://www.google.com/ping?sitemap={domain}/sitemap.xml"
    requests.get(ping_url)
    print("✅ 已通知 Google 爬虫更新 sitemap.xml")
except Exception as e:
    print("❌ Google Ping 失败：", e)
