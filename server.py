# app.py

from flask import Flask, render_template, request
from model import find_similar_images

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Kullanıcı tarafından yüklenen dosya
        input_image = request.files["input_image"]
        
        # Kullanıcı tarafından yüklenen dosyanın benzerlerini bul
        similar_images = find_similar_images(input_image, dataset_path='C:\\Users\\emiry\\melspectograms')

        return render_template("result.html", input_image=input_image, similar_images=similar_images)
    
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
