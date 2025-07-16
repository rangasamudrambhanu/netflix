from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

movies = {
    "action": ["Mad Max: Fury Road", "John Wick", "Die Hard"],
    "drama": ["The Godfather", "Forrest Gump", "Shawshank Redemption"],
    "comedy": ["The Hangover", "Superbad", "Step Brothers"]
}

@app.route('/')
def home():
    return render_template('index.html', movies=movies)

@app.route('/movies')
def get_movies():
    return jsonify(movies)

@app.route('/recommend')
def recommend():
    genre = request.args.get('genre', 'action')
    return jsonify({genre: movies.get(genre, [])})

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
