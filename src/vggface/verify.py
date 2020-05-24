# -*- coding: utf-8 -*-

import sys

# face verification with the VGGFace2 model
from matplotlib import pyplot
from PIL import Image
import numpy as np
#from numpy import asarray
from scipy.spatial.distance import cosine
#from mtcnn.mtcnn import MTCNN
from keras.preprocessing import image
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input

import face_recognition

'''
# extract a single face from a given photograph
def extract_face(filename, required_size=(224, 224)):
    # load image from file
    pixels = pyplot.imread(filename)
    # create the detector, using default weights
    detector = MTCNN()
    # detect faces in the image
    results = detector.detect_faces(pixels)
    # extract the bounding box from the first face
    x1, y1, width, height = results[0]['box']
    x2, y2 = x1 + width, y1 + height
    # extract the face
    face = pixels[y1:y2, x1:x2]
    # resize pixels to the model size
    image = Image.fromarray(face)
    image = image.resize(required_size)
    face_array = asarray(image)
    return face_array
'''

def extract_face(filename, required_size=(224, 224)):
    # load image from file
    pixels = face_recognition.load_image_file(filename)
    # extract the bounding box from the first face
    face_bounding_boxes = face_recognition.face_locations(pixels)

    # 可能返回 >0, 多个人脸
    if len(face_bounding_boxes) == 0:
        return None

    top, right, bottom, left = face_bounding_boxes[0]
    x1, y1, width, height = left, top, right-left, bottom-top
    x2, y2 = x1 + width, y1 + height
    # extract the face
    face = pixels[y1:y2, x1:x2]
    # resize pixels to the model size
    image = Image.fromarray(face)
    image = image.resize(required_size)
    face_array = np.asarray(image, 'float32')

    # show face
    #from PIL import ImageDraw
    #draw = ImageDraw.Draw(image)
    #del draw
    #image.show()
    return face_array

model = VGGFace(model='senet50', include_top=False, input_shape=(224, 224, 3), pooling='avg') # pooling: None, avg or max
#model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')

def load_face(filename, required_size=(224, 224)):
    img = image.load_img(filename, target_size=required_size)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    return x


def get_features(filename):
    # extract faces
    face = extract_face(filename)
    # prepare the face for the model, e.g. center pixels
    sample = preprocess_input(face, version=2)
    # create a vggface model
    #model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')
    # perform prediction
    yhat = model.predict(sample)
    return yhat


# extract faces and calculate face embeddings for a list of photo files
def get_embeddings(filenames):
    # extract faces
    faces = [load_face(f) for f in filenames]
    # convert into an array of samples
    samples = np.asarray(faces, 'float32')
    # prepare the face for the model, e.g. center pixels
    samples = preprocess_input(samples, version=2)
    # create a vggface model

    # perform prediction
    yhat = model.predict(samples)
    return yhat

# determine if a candidate face is a match for a known face
def is_match(known_embedding, candidate_embedding, thresh=0.5):
    # calculate distance between embeddings
    score = cosine(known_embedding, candidate_embedding)
    if score <= thresh:
        print('>face is a Match (%.3f <= %.3f)' % (score, thresh))
    else:
        print('>face is NOT a Match (%.3f > %.3f)' % (score, thresh))

if __name__ == '__main__':
    if len(sys.argv)<3:
        print("usage: python3 %s <img1> <img2>" % sys.argv[0])
        sys.exit(2)

    filename1 = sys.argv[1]
    filename2 = sys.argv[2]

    feature1 = get_features(filename1)
    feature2 = get_features(filename2)

    is_match(feature1, feature2)
