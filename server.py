from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
import numpy as np

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Güçlü bir gizli anahtarla değiştirin
client = MongoClient('localhost', 27017)
db = client['MusicRecommender']  # MongoDB veritabanı adınızı değiştirin
users_collection = db['users']
songs_collection = db['songs']

@app.route('/get_similar_songs', methods=['POST'])
def get_similar_songs():
    selected_file = request.json.get('filename')

    # most_similar_Arrays.npy dosyasından en benzer 5 şarkıyı bul
    most_similar_data = np.load('most_similar_arrays.npy', allow_pickle=True).item()
    similar_songs = most_similar_data[selected_file]

    # Benzer şarkıların başlık ve sanatçı bilgilerini alma ve kullanıcıya gösterme
    similar_song_info = []
    for similar_song in similar_songs:
        for song in songs_collection.find():
            if song['file'] == similar_song:
                title = song['title']
                artist = song['artist']
                similarity_score = similar_songs[similar_song]
                similar_song_info.append({"title": title, "artist": artist, "similarity_score": similarity_score})
                break
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
