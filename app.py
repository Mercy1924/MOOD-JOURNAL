from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "mood_secret"

# Database (SQLite for demo, switch to MySQL if needed)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mood.db'
db = SQLAlchemy(app)

# Hugging Face API setup (replace with your token if needed)
HF_API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_API_KEY', '')}"}

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(50))
    score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

db.create_all()

def analyze_sentiment(text):
    """Send text to Hugging Face sentiment API."""
    try:
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json={"inputs": text})
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            label = result[0]['label']
            score = result[0]['score']
            return label, score
        else:
            return "Neutral", 0.0
    except Exception as e:
        print("Error calling Hugging Face:", e)
        return "Error", 0.0

@app.route("/")
def index():
    entries = Entry.query.order_by(Entry.created_at.desc()).all()
    return render_template("index.html", entries=entries)

@app.route("/add", methods=["POST"])
def add():
    text = request.form.get("text")
    if text:
        mood, score = analyze_sentiment(text)
        entry = Entry(text=text, mood=mood, score=score)
        db.session.add(entry)
        db.session.commit()
        flash("Entry added successfully!")
    return redirect(url_for("index"))

@app.route("/edit/<int:entry_id>")
def edit(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    return render_template("edit.html", entry=entry)

@app.route("/update/<int:entry_id>", methods=["POST"])
def update_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    entry.text = request.form.get("content")
    mood, score = analyze_sentiment(entry.text)
    entry.mood = mood
    entry.score = score
    db.session.commit()
    flash("Entry updated successfully!")
    return redirect(url_for("index"))

@app.route("/delete/<int:entry_id>", methods=["POST"])
def delete(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted.")
    return redirect(url_for("index"))

@app.route("/chart-data")
def chart_data():
    entries = Entry.query.order_by(Entry.created_at).all()
    labels = [e.created_at.strftime("%Y-%m-%d %H:%M") for e in entries]
    scores = [e.score for e in entries]
    return jsonify({"labels": labels, "scores": scores})

if __name__ == "__main__":
    app.run(debug=True)
