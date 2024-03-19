# model.py

import os
import numpy as np 
from PIL import Image
from tensorflow.keras.preprocessing import image
from keras.applications.vgg16 import VGG16
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained VGG16 model
vgg16 = VGG16(weights='imagenet', include_top=False, pooling='max', input_shape=(224, 224, 3))

for model_layer in vgg16.layers:
  model_layer.trainable = False

def load_image(image_path):
    input_image = Image.open(image_path)
    # Convert image to RGB mode
    input_image = input_image.convert("RGB")
    resized_image = input_image.resize((224, 224))
    return resized_image

# Function to get image embeddings using VGG16
def get_image_embeddings(image):
    image_array = np.expand_dims(np.asarray(image), axis=0)
    image_embedding = vgg16.predict(image_array)
    return image_embedding

# Function to compute similarity score between two images
def get_similarity_score(image1, image2):
    image1_vector = get_image_embeddings(image1)
    image2_vector = get_image_embeddings(image2)
    similarity_score = cosine_similarity(image1_vector, image2_vector).reshape(1,)
    return similarity_score[0]

# Function to find top 5 similar images to the given input image
def find_similar_images(input_image_path, dataset_path):
    input_image = load_image(input_image_path)
    input_image_embedding = get_image_embeddings(input_image)

    similarity_scores = {}
    for image_file in os.listdir(dataset_path):
        image_path = os.path.join(dataset_path, image_file)
        if os.path.isfile(image_path):
            image_to_compare = load_image(image_path)
            similarity_score = get_similarity_score(input_image, image_to_compare)
            similarity_scores[image_path] = similarity_score

    # Sort similarity scores in descending order
    sorted_similarity_scores = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

    # Get top 5 similar images
    top_similar_images = sorted_similarity_scores[:5]

    return top_similar_images
