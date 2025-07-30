
import os
import json
import random
from datetime import datetime

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

domain = config.get("domain").rstrip("/")
base_dir = os.getcwd()
keywords_dir = os.path.join(base_dir, "keywords")
output_dir = base_dir

sitemap_entries = set()
all_generated_files = []
report_lines = []

# === 英文描述模板 ===
def generate_paragraph(keyword):
    return (
        f"This image explores the theme of {keyword}. "
        f"Featuring distinct visual composition and styled aesthetics, it captures the subtle emotion and depth of {keyword}. "
        f"Perfect for those who appreciate fine visual storytelling."
    )

def generate_internal_links(category, current_img, all_imgs, count=3):
    others = [img for img in all_imgs if img != current_img]
    random.shuffle(others)
    selected = others[:count]
    links = "<div style='margin-top:20px; text-align:center;'>More from this category:<br>"
    for img in selected:
        page = f"image_{category}_{all_imgs.index(img)+1:04}.html"
        links += f"<a href='{page}'>{img}</a> &nbsp; "
    links += "</div>"
    return links

# === 遍历分类目录 ===
for category in sorted(os.listdir(base_dir)):
    cat_path = os.path.join(base_dir, category)
    if not os.path.isdir(cat_path): continue
    if category in ["keywords", "generator", "static", "__pycache__"]: continue

    images = sorted([f for f in os.listdir(cat_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))])
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
        nav_links += "<a href='index.html'>🏠 Home</a>"
        if prev_link:
            nav_links += f" | <a href='{prev_link}'>⬅️ Prev</a>"
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

        body = (
            f"{nav_links}\n"
            f"<h1 style='text-align:center;'>{alt}</h1>\n"
            f"<div style='text-align:center;'><img src='{img_path}' alt='{alt}' style='max-width:100%;height:auto;'></div>\n"
            f"<p style='max-width:800px;margin:auto;text-align:center;padding:10px;'>{generate_paragraph(alt)}</p>\n"
            f"{generate_internal_links(category, img, images)}\n"
            f"{nav_links}\n"
            '<script src="ads.js"></script>\n'
        )

        full_html = (
            "<html><head>\n"
            "<meta charset='utf-8'>\n"
            f"<title>{alt}</title>\n"
            f"<meta name='description' content='{alt} gallery photo'>\n"
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
            f"{json_ld}\n"
            "</head><body>\n"
            f"{body}</body></html>"
        )

        with open(html_path, "w", encoding="utf-8") as f_html:
            f_html.write(full_html)

        sitemap_entries.add(f"{domain}/{page_name}")
        all_generated_files.append((page_name, full_html))

# === sitemap.xml ===
now = datetime.today().strftime("%Y-%m-%d")
with open("sitemap.xml", "w", encoding="utf-8") as f_map:
    f_map.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f_map.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for url in sorted(sitemap_entries):
        f_map.write(f"  <url><loc>{url}</loc><lastmod>{now}</lastmod></url>\n")
    f_map.write('</urlset>')

# === robots.txt ===
robots_txt = (
    "User-agent: *\n"
    "Allow: /\n"
    f"Sitemap: {domain}/sitemap.xml\n"
)
with open("robots.txt", "w", encoding="utf-8") as f:
    f.write(robots_txt)

# === 强索引 HTML页（前50图） ===
boost_file = os.path.join(base_dir, "index_boost.html")
with open(boost_file, "w", encoding="utf-8") as bf:
    bf.write("<html><head><title>Quick Indexing Page</title></head><body>\n")
    bf.write("<h2>Submit these to Google Search Console for faster indexing:</h2>\n<ul>\n")
    for fname, _ in all_generated_files[:50]:
        full_url = f"{domain}/{fname}"
        bf.write(f"<li><a href='{full_url}' target='_blank'>{full_url}</a></li>\n")
    bf.write("</ul></body></html>")

# === 报告页（检查 ads.js、内链） ===
with open("check_report.txt", "w", encoding="utf-8") as report:
    for fname, content in all_generated_files:
        issues = []
        if "ads.js" not in content:
            issues.append("❌ Missing ads.js")
        if "More from this category" not in content:
            issues.append("❌ No internal links")
        if len(content) < 1000:
            issues.append("⚠️ Page too short")
        line = f"{fname}: {' | '.join(issues) if issues else '✅ OK'}"
        report_lines.append(line)
        report.write(line + "\n")

print("✅ Enhanced V10 脚本执行完毕！已生成：图片页 + sitemap + robots + 内链推荐 + 收录推荐页 + 检查报告 ✅")
