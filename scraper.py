import requests
from bs4 import BeautifulSoup
import random
import time

KEYWORDS = [
    "erp", "hug me", "snowbunny", "daddy", "femboy", "add me", "condo", "roleplay",
    "toy", "furry", "fishnet", "fvta", "domme", "naked", "strip", "18+", "17+", "fembxy",
    "fmby", "fxmboy", "fxmby", "fxbxy", "studio"
]

def load_cookies(file_path="cookies.txt"):
    cookies = {}
    with open(file_path, "r") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) == 7:
                domain, flag, path, secure, expiration, name, value = parts
                cookies[name] = value
    return cookies

def scrape_clothing(cookies, max_items=5):
    url = "https://www.roblox.com/catalog"
    r = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    for img in soup.find_all("img"):
        alt_text = img.get("alt", "").lower()
        src = img.get("src", "")
        if any(k in alt_text for k in KEYWORDS) and src.startswith("http"):
            results.append({
                "image_url": src,
                "username": "N/A",
                "user_id": None
            })
        if len(results) >= max_items:
            break
    return results

def scrape_users(cookies, max_items=5):
    # Scrapes user avatars from Roblox users search page (simplified)
    url = "https://www.roblox.com/users/search?keyword=avatar"
    r = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    # This example assumes user entries in page contain profile links and avatar images:
    # The exact selectors may require updates if Roblox changes page structure
    for user_link in soup.select("a[href^='/users/']"):
        href = user_link.get("href")
        username = user_link.text.strip()
        # Extract userID from href, e.g. /users/12345678/profile
        user_id = None
        parts = href.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "users":
            try:
                user_id = int(parts[1])
            except:
                user_id = None

        # Find avatar img inside user link
        img = user_link.find("img")
        img_url = img.get("src") if img else None

        if img_url and img_url.startswith("http"):
            results.append({
                "image_url": img_url,
                "username": username,
                "user_id": user_id
            })

        if len(results) >= max_items:
            break

    return results

def scrape_catalog(cookies, max_items=5):
    # Randomly pick clothing or user scraping each call
    target = random.choice(["Clothing", "Users"])

    if target == "Clothing":
        print("Scraping clothing items...")
        return scrape_clothing(cookies, max_items)
    else:
        print("Scraping users...")
        return scrape_users(cookies, max_items)
