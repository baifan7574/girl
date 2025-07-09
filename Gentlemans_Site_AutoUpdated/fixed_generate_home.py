import os
from pathlib import Path
from math import ceil

base_path = Path(__file__).parent
image_base = base_path
output_path = base_path
categories = ["dark", "office", "shower", "soft", "uniform"]
images_per_index = 8
images_per_page = 20

def make_img_tag(category, img_file):
    rel_path = f"{category}/{img_file}"
    return f'<a href="{rel_path}" data-lightbox="{category}"><img src="{rel_path}" alt="{img_file}" class="thumb"></a>'

def generate_index_html():
    index_file = output_path / "index.html"
    with open(index_file, "r", encoding="utf-8") as f:
        content = f.read()

    start_tag = "<!-- AUTO_INSERT_START -->"
    end_tag = "<!-- AUTO_INSERT_END -->"
    if start_tag not in content or end_tag not in content:
        print("⚠️ 页面中缺少插入标记，无法更新 index.html")
        return

    before, _, after = content.partition(start_tag)
    _, _, remaining = after.partition(end_tag)

    new_sections = ""
    for category in categories:
        category_path = image_base / category
        if not category_path.exists():
            continue
        images = sorted([f for f in os.listdir(category_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])[:images_per_index]
        img_tags = "\n".join([make_img_tag(category, img) for img in images])
        section = (
            f"<section>\n"
            f"<h2>{category.capitalize()}</h2>\n"
            f"<div class=\"gallery\">{img_tags}</div>\n"
            f"<a href=\"{category}.html\">→ View More</a>\n"
            f"</section>\n"
        )
        new_sections += section

    updated_content = before + start_tag + "\n" + new_sections + end_tag + remaining
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(updated_content)

def generate_category_pages():
    for category in categories:
        category_path = image_base / category
        if not category_path.exists():
            continue
        images = sorted([f for f in os.listdir(category_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        total_pages = ceil(len(images) / images_per_page)

        for page in range(1, total_pages + 1):
            page_images = images[(page-1)*images_per_page:page*images_per_page]
            img_tags = "\n".join([make_img_tag(category, img) for img in page_images])
            pagination = ""

            if total_pages > 1:
                if page > 1:
                    pagination += f'<a href="{category}_page{page-1}.html">← Previous</a> '
                if page < total_pages:
                    pagination += f'<a href="{category}_page{page+1}.html">Next →</a>'

            filename = f"{category}.html" if page == 1 else f"{category}_page{page}.html"
            with open(output_path / filename, "w", encoding="utf-8") as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset='UTF-8'>
    <title>{category.capitalize()} Gallery</title>
    <link rel='stylesheet' href='styles.css'>
    <link rel='stylesheet' href='lightbox.css'>
</head>
<body>
    <h1>{category.capitalize()}</h1>
    <div class='gallery'>{img_tags}</div>
    <div class='pagination'>{pagination}</div>
    <div><a href='index.html'>← Back to Home</a></div>
    <script src='lightbox-plus-jquery.js'></script>
</body>
</html>""")

generate_index_html()
generate_category_pages()
print("✅ 网站页面已成功生成，请刷新 index.html 查看效果。")
