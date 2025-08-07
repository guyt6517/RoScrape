# Generated with CHATGPT
# main.py
import os
from scraper import download_image
from detector import hybrid_analysis
from utils import ensure_dir

def main():
    ensure_dir("images")

    # Replace this with the actual Roblox image URL you want to analyze
    url = "https://cdn.roblox.com/avatar-image.png"
    image_path = "images/avatar.png"

    print(f"Downloading image from {url}...")
    if not download_image(url, image_path):
        print("Failed to download image")
        return

    print("Analyzing image...")
    result = hybrid_analysis(image_path)
    print(result["summary"])

if __name__ == "__main__":
    main()
