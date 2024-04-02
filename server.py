from flask import Flask, render_template, redirect, request, session, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)
app.secret_key = "sizin_gizli_anahtarınız"  # Oturum güvenliği için gizli anahtar belirleyin
app.config['MONGO_URI'] = 'mongodb://localhost:27017/MusicRecommender'

mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('home_page.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = mongo.db.users.find_one({'username': username})
    
    if user and user['password'] == password:
        session['username'] = username
        return redirect('/')
    else:
        return jsonify({'error': 'Kullanıcı adı veya şifre hatalı!'})

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    newusername = request.form['newusername']
    newpassword = request.form['newpassword']
    confirm_password = request.form['confirm_password']

    if mongo.db.users.find_one({'username': newusername}):
        return jsonify({'error': 'Bu kullanıcı adı zaten alınmış!'})

    if newpassword != confirm_password:
        return jsonify({'error': 'Şifreler eşleşmiyor!'})

    mongo.db.users.insert_one({
        'username': newusername,
        'password': newpassword,
        'email': email,
    })

    return redirect('/')

@app.route('/logout')
def logout():
    # Oturumu sonlandır
    session.pop('username', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
