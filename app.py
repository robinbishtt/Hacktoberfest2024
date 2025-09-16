from flask import Flask, render_template, request
import requests
import pandas as pd
from transformers import pipeline
from datetime import datetime

app = Flask(__name__)

# Initialize sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def fetch_social_media_data(endpoint="posts", limit=10):
    """Fetch data from JSONPlaceholder API."""
    try:
        url = f"https://jsonplaceholder.typicode.com/{endpoint}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()[:limit]
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def analyze_sentiment(texts):
    """Perform sentiment analysis on a list of texts."""
    try:
        # Truncate texts to 512 tokens (max for DistilBERT)
        results = sentiment_analyzer([text[:512] for text in texts])
        return [{
            "label": res["label"],
            "score": round(res["score"], 4),
            "sentiment": "Positive" if res["label"] == "POSITIVE" else "Negative"
        } for res in results]
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return [{"label": "ERROR", "score": 0.0, "sentiment": "Unknown"} for _ in texts]

def save_results(data, sentiments, filename_prefix="sentiment_results"):
    """Save fetched data and sentiment results to a JSON file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        results = [
            {"id": post["id"], "title": post["title"], "body": post["body"], **sent}
            for post, sent in zip(data, sentiments)
        ]
        pd.DataFrame(results).to_json(filename, orient="records", indent=4)
        print(f"Results saved to {filename}")
        return filename
    except Exception as e:
        print(f"Error saving results: {e}")
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    """Main route for the web interface."""
    posts = []
    sentiments = []
    saved_file = None
    error = None
    
    if request.method == "POST":
        try:
            limit = int(request.form.get("limit", 10))
            if limit < 1 or limit > 100:
                error = "Please enter a number between 1 and 100."
            else:
                # Fetch social media data
                posts = fetch_social_media_data(limit=limit)
                if not posts:
                    error = "Failed to fetch data from API."
                else:
                    # Extract text (title + body for JSONPlaceholder)
                    texts = [f"{post['title']} {post['body']}" for post in posts]
                    # Analyze sentiment
                    sentiments = analyze_sentiment(texts)
                    # Save results if requested
                    if request.form.get("save") == "yes":
                        saved_file = save_results(posts, sentiments)
        except ValueError:
            error = "Invalid input! Please enter a valid number."
    
    return render_template("index.html", 
                         posts=posts, 
                         sentiments=sentiments, 
                         saved_file=saved_file, 
                         error=error)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
