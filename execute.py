# main.py
import os
import time
from scraper import load_cookies, scrape_catalog
from detector import hybrid_analysis
from utils import ensure_dir
import requests

def send(payload):
    checkpoint1 = "https://roscapeoutboundcheckpointhunt.onrender.com/send_message"
    checkpoint2 = "https://roscapeoutboundcheckpointhunt.onrender.com/send_message"

    headers = {"Content-Type": "application/json"}

    try:
        r1 = requests.post(checkpoint1, json=payload, headers=headers)
        if r1.status_code == 200:
            print("Sent successfully to checkpoint1")
        else:
            print(f"Failed sending to checkpoint1: {r1.status_code} {r1.text}")
    except Exception as e:
        print(f"Error sending to checkpoint1: {e}")

    try:
        r2 = requests.post(checkpoint2, json=payload, headers=headers)
        if r2.status_code == 200:
            print("Sent successfully to checkpoint2")
        else:
            print(f"Failed sending to checkpoint2: {r2.status_code} {r2.text}")
    except Exception as e:
        print(f"Error sending to checkpoint2: {e}")

def download_image(url, path):
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"Download error: {e}")
    return False

def main():
    ensure_dir("images")
    cookies = load_cookies()

    while True:
        items = scrape_catalog(cookies, max_items=5)
        for i, item in enumerate(items):
            url = item["image_url"]
            username = item["username"]
            user_id = item["user_id"]

            image_path = f"images/{user_id or 'unknown'}_{i}.png"
            print(f"\nDownloading: {url} (User: {username}, ID: {user_id})")

            if not download_image(url, image_path):
                print("Download failed.")
                continue

            print("Analyzing image...")
            result = hybrid_analysis(image_path, unsafe_threshold=60, username=username, user_id=user_id)
            print(result["summary"])

            # Your custom logic here with result
            if result["unsafe_score"] >= 40:
                send(result)
            elif result["unsafe_score"] <= 39:
                if result["nsfw_score"] >= 21:
                    send(result)
                else:
                    continue
            else:
                continue

        print("Batch done. Restarting scrape...")
        time.sleep(10)  # wait 10 seconds before next batch to be polite


if __name__ == "__main__":
    main()
