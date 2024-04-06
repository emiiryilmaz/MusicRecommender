import json
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
import numpy as np

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Güçlü bir gizli anahtarla değiştirin
client = MongoClient('localhost', 27017)
db = client['MusicRecommender']  # MongoDB veritabanı adınızı değiştirin
users_collection = db['users']
songs_collection = db['songs']

json_file = "song_info.json"  
with open(json_file, 'r') as file:
    json_data = json.load(file)
@app.route('/get_similar_songs', methods=['POST'])
def get_similar_songs():
    selected_file = request.json.get('file')
    data_dict = np.load('most_similar_arrays.npy', allow_pickle=True).item()
    similar_song_info = []

    for similar_song in data_dict[selected_file]:
        similar_filename = similar_song[0]
        similar_title = None
        similar_artist = None

        for item in json_data:
            if item["file"] == similar_filename:
                similar_title = item["title"]
                similar_artist = item["artist"]
                break

        if similar_title is not None and similar_artist is not None:
            similar_song_info.append({"title": similar_title, "artist": similar_artist})

    return jsonify(similar_song_info)

@app.route('/get_songs', methods=['GET'])
def get_songs():
    songs = list(songs_collection.find({}, {'_id': 0, 'title': 1, 'artist': 1, 'file': 1}))
    return jsonify(songs)

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    else:
        return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if users_collection.find_one({'username': username}):
            flash('Username already exists. Choose a different one.', 'danger')
        else:
            users_collection.insert_one({'name': name,'email': email,'username': username, 'password': password})
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

from flask import request, render_template  # render_template import edilmeli

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            flash('Login successful.', 'success')
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error_message = 'Invalid username or password. Please try again.'

    return render_template('login.html', error_message=error_message)  # render_template ile error_message değişkeni template'e gönderilmeli

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/success')
def success():
    if 'username' in session:
        return "Başarıyla giriş yaptınız!"
    else:
        return redirect(url_for('login'))
    
    
@app.route('/about', methods=['GET', 'POST'])
def about():
 return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
