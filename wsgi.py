import threading
from flask import Flask
import execute  # your main.py with main()

app = Flask(__name__)

@app.route("/")
def index():
    return "Roblox scraper running..."

def run_scraper():
    main.main()

# Start scraper thread on module load
threading.Thread(target=run_scraper, daemon=True).start()
