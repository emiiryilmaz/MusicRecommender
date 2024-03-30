from flask import Flask, render_template, redirect, request



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home_page.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Giriş işlemleri burada yapılacak
        return redirect('/')  # Başarılı giriş durumunda ana sayfaya yönlendir
    return render_template('login.html')  # login.html dosyasını render et


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Kayıt işlemleri burada yapılacak
        return redirect('/')  # Başarılı kayıt durumunda ana sayfaya yönlendir
    return render_template('register.html')  # register.html dosyasını render et


if __name__ == "__main__":
    app.run(debug=True)
