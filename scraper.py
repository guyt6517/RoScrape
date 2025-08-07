import os
import requests
from bs4 import BeautifulSoup
import random

KEYWORDS = [
    "erp", "hug me", "snowbunny", "daddy", "femboy", "add me", "condo", "roleplay",
    "toy", "furry", "fishnet", "fvta", "domme", "naked", "strip", "18+", "17+", "fembxy",
    "fmby", "fxmboy", "fxmby", "fxbxy", "studio"
]

def parse_netscape_cookies(cookie_str):
    """
    Parse Netscape formatted cookies from a string into a dict suitable for requests.
    """
    cookies = {}
    lines = cookie_str.strip().splitlines()
    for line in lines:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.strip().split("\t")
        if len(parts) == 7:
            domain, flag, path, secure, expiration, name, value = parts
            cookies[name] = value
    return cookies

def load_cookies():
    """
    Load cookies from the environment variable ROBLOX_COOKIES.
    """
    cookie_data = os.getenv("ROBLOX_COOKIES")
    if not cookie_data:
        raise ValueError("Environment variable ROBLOX_COOKIES not set or empty.")
    return parse_netscape_cookies(cookie_data)

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
    url = "https://www.roblox.com/users/search?keyword=avatar"
    r = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    for user_link in soup.select("a[href^='/users/']"):
        href = user_link.get("href")
        username = user_link.text.strip()
        user_id = None
        parts = href.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "users":
            try:
                user_id = int(parts[1])
            except:
                user_id = None

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
    target = random.choice(["Clothing", "Users"])

    if target == "Clothing":
        print("Scraping clothing items...")
        return scrape_clothing(cookies, max_items)
    else:
        print("Scraping users...")
        return scrape_users(cookies, max_items)
