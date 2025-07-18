import os
import glob
import random
import datetime
from pathlib import Path

base_dir = Path(__file__).resolve().parent
keywords_dir = base_dir / "keywords"
images_per_page = 20
exclude_dirs = {"generator", "pages", "single", "assets", "__pycache__"}

# 加载关键词
def load_keywords(category):
    file_path = keywords_dir / f"{category}.txt"
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# 生成 SEO 字段
def generate_seo_text(keywords, count=6):
    return ", ".join(random.sample(keywords, min(count, len(keywords))))

category_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{category} Gallery</title>
    <meta name="description" content="Gallery of {category}">
    <meta name="keywords" content="{keywords}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>{category} Gallery</h1>
    <div class="gallery">
        {image_blocks}
    </div>
    {pagination}
    <div class="back-home"><a href="index.html">← Back to Home</a></div>
</body>
</html>"""

image_block_template = """<div class="thumb">
    <a href="{image_page}">
        <img src="{img_src}" alt="{alt}" title="{alt}">
    </a>
</div>"""

image_page_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h2>{title}</h2>
    <div class="full-image">
        <img src="{img_src}" alt="{description}">
    </div>
    <div class="nav">
        {prev_link}
        {next_link}
    </div>
    <div class="back-home">
        <a href="index.html">← Back to Home</a>
    </div>
</body>
</html>"""

sitemap_entries = []

for folder in sorted(base_dir.iterdir()):
    if not folder.is_dir() or folder.name in exclude_dirs or folder.name.startswith("."):
        continue

    category = folder.name
    keywords = load_keywords(category)
    if not keywords:
        print(f"⚠️ 没有关键词，跳过：{category}")
        continue

    images = sorted(glob.glob(str(folder / "*.jpg")))
    total_pages = (len(images) + images_per_page - 1) // images_per_page

    for page_num in range(total_pages):
        image_blocks = ""
        start = page_num * images_per_page
        end = min(start + images_per_page, len(images))
        for idx in range(start, end):
            img_name = os.path.basename(images[idx])
            img_src = f"{category}/{img_name}"
            base_title = f"{category.capitalize()} Image {idx+1}"
            title = f"{base_title} - {generate_seo_text(keywords, 2)}"
            description = f"{generate_seo_text(keywords, 3)}"
            keyword_str = generate_seo_text(keywords, 8)

            image_page_name = f"image_{category}_{idx+1:03d}.html"
            prev_link = f'<a href="image_{category}_{idx:03d}.html">← Previous</a>' if idx > 0 else ""
            next_link = f'<a href="image_{category}_{idx+2:03d}.html">Next →</a>' if idx + 1 < len(images) else ""

            with open(base_dir / image_page_name, "w", encoding="utf-8") as f:
                f.write(image_page_template.format(
                    img_src=img_src,
                    title=title,
                    description=description,
                    keywords=keyword_str,
                    prev_link=prev_link,
                    next_link=next_link
                ))

            sitemap_entries.append(f"https://yourdomain.com/{image_page_name}")
            image_blocks += image_block_template.format(image_page=image_page_name, img_src=img_src, alt=title)

        page_name = f"{category}.html" if page_num == 0 else f"{category}_page{page_num+1}.html"
        pagination = ""
        if total_pages > 1:
            for i in range(total_pages):
                pg = f"{category}.html" if i == 0 else f"{category}_page{i+1}.html"
                pagination += f'<a href="{pg}">Page {i+1}</a> '

        with open(base_dir / page_name, "w", encoding="utf-8") as f:
            f.write(category_template.format(
                category=category.capitalize(),
                image_blocks=image_blocks,
                pagination=pagination,
                keywords=generate_seo_text(keywords, 6)
            ))

        sitemap_entries.append(f"https://yourdomain.com/{page_name}")

# sitemap.xml
now = datetime.datetime.utcnow().strftime("%Y-%m-%d")
with open(base_dir / "sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for url in sitemap_entries:
        f.write(f"  <url><loc>{url}</loc><lastmod>{now}</lastmod></url>\n")
    f.write('</urlset>')