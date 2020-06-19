
from datetime import datetime
import cv2
import numpy as np

from models.deepface.deepface import get_detector, get_recognizer
from models.deepface.deepface.utils.visualization import draw_bboxs

detector = get_detector(name='dlib')
recognizer = get_recognizer(name='vgg2')


def show_with_face(npimg, faces):
    img = draw_bboxs(np.copy(npimg), faces)
    cv2.imshow('DeepFace', img)
    cv2.waitKey(0)


def extract_embeddings(img_path):

    npimg = cv2.imread(img_path, cv2.IMREAD_COLOR)

    #start_time = datetime.now()
    faces = detector.detect(npimg)
    #print(faces)
    #print('[1 Time taken: {!s}]'.format(datetime.now() - start_time))

    #start_time = datetime.now()
    _, feats = recognizer.extract_features(npimg=npimg, faces=faces)
    #print('[2 Time taken: {!s}]'.format(datetime.now() - start_time))

    #features[name] = feats[0]

    #show_with_face(npimg, faces)

    feats = [i / np.linalg.norm(i, 2) for i in feats]

    return feats, faces


if __name__ == '__main__':
    e, f = extract_embeddings('samples/blackpink/faces/jennie.jpg')

    print(e)
    print(f)
