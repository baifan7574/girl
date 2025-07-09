
import json
import os
import time
from PIL import Image
from io import BytesIO
import base64
import requests

def generate_images(config_file):
    print(f"📁 正在处理配置文件：{config_file}")
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    output_dir = config.get("output_dir", "./output")
    os.makedirs(output_dir, exist_ok=True)

    total = config.get("total_images", 50)
    batch = config.get("batch_size", 6)
    generated = 0

    while generated < total:
        current_batch = min(batch, total - generated)
        payload = {
            "prompt": config["prompt"],
            "negative_prompt": config["negative_prompt"],
            "steps": config["steps"],
            "width": config["width"],
            "height": config["height"],
            "cfg_scale": config["cfg_scale"],
            "sampler_name": config["sampler_name"],
            "batch_size": current_batch,
            "n_iter": 1,
            "seed": config["seed"],
            "alwayson_scripts": {}
        }

        if config.get("hires_fix"):
            payload["enable_hr"] = True
            payload["denoising_strength"] = config.get("hires_denoising_strength", 0.55)
            payload["hr_scale"] = config.get("hires_scale", 1.5)
            payload["hr_upscaler"] = config.get("hires_upscaler", "Latent")

        if config.get("refiner"):
            payload["alwayson_scripts"]["refiner"] = {"args": [True]}

        res = requests.post(url="http://127.0.0.1:7860/sdapi/v1/txt2img", json=payload)
        res.raise_for_status()
        images = res.json()["images"]

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        for i, img_data in enumerate(images):
            image = Image.open(BytesIO(base64.b64decode(img_data)))
            index = generated + i + 1
            save_path = os.path.join(output_dir, f"{timestamp}_{index:02d}.jpg")
            image.save(save_path)
            print(f"✅ 已保存：{save_path}")

        generated += current_batch

# 多配置循环
config_files = [f for f in os.listdir() if f.startswith("config_") and f.endswith(".json")]
for file in config_files:
    generate_images(file)

input("请按任意键继续...")
