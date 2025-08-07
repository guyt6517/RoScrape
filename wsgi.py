from flask import Flask
import threading
import execute  # your main.py file with the main() function

app = Flask(__name__)

@app.route("/")
def index():
    return "Roblox scraper running..."

def run_scraper():
    main.main()

if __name__ == "__main__":
    # Start scraper in background thread
    threading.Thread(target=run_scraper, daemon=True).start()
    app.run(host="0.0.0.0", port=8000)
