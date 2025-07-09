
import os
import shutil
import random
import xml.etree.ElementTree as ET
from xml.dom import minidom

base_dir = "."
site_url = "https://gentlemansframe.com"
images_per_page = 20

keywords = {
    "dark": ["dark lighting", "leather outfit", "gothic girl", "AI generated portrait", "moody background", "black latex"],
    "office": ["office woman", "tight white shirt", "business attire", "desk model", "AI fashion look", "elegant pose"],
    "shower": ["wet body", "shower scene", "AI girl in bathroom", "water dripping", "realistic lighting", "sensual photo"],
    "soft": ["soft skin", "innocent beauty", "natural light", "clean towel hair", "minimal makeup", "calm mood"],
    "uniform": ["school uniform", "AI cosplay", "tight outfit", "pleated skirt", "roleplay girl", "seductive look"]
}

def generate_keywords(category, name):
    base = keywords.get(category.lower(), ["AI model", "realistic photo", "woman portrait"])
    return random.sample(base, 3)

def write_html(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def create_category_pages(category, image_files):
    cat_folder = os.path.join(base_dir, category)
    single_folder = os.path.join(cat_folder, "single")
    pages_folder = os.path.join(cat_folder, "pages")
    os.makedirs(single_folder, exist_ok=True)
    os.makedirs(pages_folder, exist_ok=True)

    single_urls = []

    for img in image_files:
        name = os.path.splitext(img)[0]
        kw = generate_keywords(category, name)
        alt_text = f"{name.replace('_', ' ').title()} - {' '.join(kw)}"
        meta_desc = f"Explore a {kw[0]}, featuring {kw[1]} and {kw[2]}."
        html = f"""<html>
<head>
  <title>{alt_text}</title>
  <meta name="description" content="{meta_desc}">
  <meta name="keywords" content="{', '.join(kw)}">
  <style>
    body {{ font-family: Arial, sans-serif; text-align: center; background: #f5f5f5; }}
    img {{ max-width: 90%; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
    a {{ text-decoration: none; color: #555; }}
  </style>
</head>
<body>
  <h2>{alt_text}</h2>
  <img src="../{img}" alt="{alt_text}"><br><br>
  <a href="../index.html">← Back to Home</a>
</body>
</html>"""
        write_html(os.path.join(single_folder, f"{name}.html"), html)
        single_urls.append(f"{site_url}/{category}/single/{name}.html")

    for i in range(0, len(image_files), images_per_page):
        page_num = i // images_per_page + 1
        imgs = image_files[i:i+images_per_page]
        gallery_html = ""
        for img in imgs:
            name = os.path.splitext(img)[0]
            gallery_html += f'<a href="../single/{name}.html"><img src="../{img}" style="width:150px;margin:8px;border-radius:10px;"></a>\n'
        page_html = f"""<html>
<head><title>{category.title()} - Page {page_num}</title>
<style>body{{font-family:Arial;text-align:center;background:#fff}}</style>
</head>
<body>
  <h1>{category.title()} - Page {page_num}</h1>
  {gallery_html}
  <br><a href="../index.html">← Back to Home</a>
</body>
</html>"""
        write_html(os.path.join(pages_folder, f"page{page_num}.html"), page_html)

    return single_urls

exclude = {"single", "pages", "generator", "__MACOSX"}
categories = [d for d in os.listdir(base_dir) if os.path.isdir(d) and d.lower() not in exclude]

all_sitemap_urls = []
homepage_thumbs = ""

for cat in categories:
    cat_path = os.path.join(base_dir, cat)
    image_files = sorted([
        f for f in os.listdir(cat_path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ], key=lambda x: os.path.getmtime(os.path.join(cat_path, x)), reverse=True)

    if not image_files:
        continue

    urls = create_category_pages(cat, image_files)
    all_sitemap_urls.extend(urls)

    homepage_thumbs += f"<h3 style='font-size:20px;'>{cat.title()}</h3>\n"
    for img in image_files[:4]:
        name = os.path.splitext(img)[0]
        homepage_thumbs += f'<a href="{cat}/single/{name}.html"><img src="{cat}/{img}" style="width:120px;margin:8px;border-radius:10px;box-shadow:0 4px 8px rgba(0,0,0,0.2);"></a>\n'

nav_links = " · ".join([f'<a href="{cat}/pages/page1.html">{cat.title()}</a>' for cat in categories])

index_html = f"""<html>
<head>
  <title>Gentleman's Frame</title>
  <style>
    body {{ font-family: 'Playfair Display', serif; text-align: center; background-color: #fdfdfd; color: #222; }}
    h1 {{ font-size: 42px; margin-top: 20px; font-weight: 600; }}
    h2 {{ font-size: 28px; }}
    a {{ text-decoration: none; color: #333; font-size: 18px; margin: 0 10px; }}
    img {{ border-radius: 10px; }}
  </style>
</head>
<body>
  <h1>Gentleman’s Frame</h1>
  <p style="font-size:16px;margin-bottom:20px;">For Men Who Appreciate More Than Beauty.</p>
  <div style="margin-bottom: 20px;">{nav_links}</div>
  <hr>
  <h2>Latest Uploads</h2>
  {homepage_thumbs}
  {''' + homepage_footer + '''}
</body>
</html>"""

write_html(os.path.join(base_dir, "index.html"), index_html)

urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
for url in all_sitemap_urls:
    url_tag = ET.SubElement(urlset, "url")
    loc = ET.SubElement(url_tag, "loc")
    loc.text = url
rough_string = ET.tostring(urlset, 'utf-8')
reparsed = minidom.parseString(rough_string)
sitemap_content = reparsed.toprettyxml(indent="  ")
with open(os.path.join(base_dir, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sitemap_content)

print("✅ 全站结构 + 美化首页 + 页脚 + SEO 自动完成！")
