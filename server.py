import json
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from flask import request, render_template
from pymongo import MongoClient
import numpy as np

app = Flask(__name__)
app.secret_key = "your_secret_key"  
client = MongoClient('localhost', 27017)
db = client['MusicRecommender']  
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
            similar_song_info.append({"title": similar_title, "artist": similar_artist,"file":similar_filename})
    return jsonify(similar_song_info)

@app.route('/get_songs', methods=['GET'])
def get_songs():
    songs = list(songs_collection.find({}, {'_id': 0, 'title': 1, 'artist': 1, 'file': 1}))
    return jsonify(songs)

@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    if 'username' not in session:
        return jsonify({"error": "User not logged in"}), 401  # 401 Unauthorized
    
    username = session['username']
    song_data = request.json  # Frontend'den gelen JSON verilerini al
    print("Received POST data:", song_data)  # Verileri konsola yazdır
    song_title = song_data["title"]
    song_artist = song_data["artist"]
    song_file = song_data["file"]
    print(song_file)
    if not song_title or not song_artist or not song_file:
        return jsonify({"error": "Incomplete song data"}), 400  # 400 Bad Request
    
    user = users_collection.find_one({'username': username})
    playlist = user.get("playlist", [])

    if any(song["file"] == song_file for song in playlist):
        return jsonify({"error": "Song already in playlist"}), 409  # 409 Conflict

    playlist.append({"title": song_title, "artist": song_artist,"file":song_file})
    users_collection.update_one(
        {'username': username},
        {'$set': {'playlist': playlist}}  # Çalma listesi alanını güncelle
    )
    print(song_artist)
    return jsonify({"message": "Song added to playlist successfully"}), 200

@app.route('/remove_from_playlist', methods=['POST'])
def remove_from_playlist():
    if 'username' not in session:
        return jsonify({"error": "User not logged in"}), 401  # 401 Unauthorized

    username = session['username']
    song_data = request.json  # Frontend'den gelen JSON verilerini al
    song_file = song_data.get("file")  # Şarkıyı belirlemek için 'file' anahtarını kullanıyoruz

    if not song_file:
        return jsonify({"error": "Song file not specified"}), 400  # 400 Bad Request
    
    user = users_collection.find_one({'username': username})
    if not user:
        return jsonify({"error": "User not found"}), 404  # 404 Not Found
    
    playlist = user.get("playlist", [])
    new_playlist = [song for song in playlist if song["file"] != song_file]

    if len(new_playlist) == len(playlist):  # Hiçbir değişiklik yoksa, şarkı çalma listesinde değil
        return jsonify({"error": "Song not found in playlist"}), 404  # 404 Not Found

    # Çalma listesini güncelle
    users_collection.update_one(
        {'username': username},
        {'$set': {'playlist': new_playlist}}
    )

    return jsonify({"message": "Song removed from playlist successfully"}), 200  # 200 OK

@app.route('/play_song', methods=['POST'])
def play_song():
    song_data = request.json  
    song_file = song_data.get("file")
    if not song_file:
        return jsonify({"error": "Song file not specified"}), 400  # 400 Bad Request
    song = songs_collection.find_one({"file": song_file})
    if not song:
        return jsonify({"error": "Song not found"}), 404  # 404 Not Found
    return jsonify({"file_path": song_file}), 200  # 200 OK

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

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/is_logged_in', methods=['GET'])
def is_logged_in():
    if 'username' in session:
        return jsonify({"is_logged_in": True})
    else:
        return jsonify({"is_logged_in": False})


@app.route('/success')
def success():
    if 'username' in session:
        return "Başarıyla giriş yaptınız!"
    else:
        return redirect(url_for('login'))
    
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

@app.route('/playlist', methods=['GET'])
def playlist():
    if 'username' not in session:
        return redirect(url_for('login'))  # Giriş yapmamışsa yönlendir

    username = session['username']
    user = users_collection.find_one({'username': username})
    playlist = user.get("playlist", [])  # Çalma listesi olup olmadığını kontrol et

    return render_template('playlist.html', playlist=playlist, username=username)   
@app.route('/about', methods=['GET', 'POST'])
def about():
 return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
