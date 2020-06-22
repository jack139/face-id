
from datetime import datetime
import cv2
import numpy as np

import face_recognition

from models.deepface.deepface import get_detector, get_recognizer

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


#######################################################3

def detect2(npimg):
    from .deepface.utils.bbox import BoundingBox

    #dets, scores, idx = self.detector.run(npimg, self.upsample_scale, -1)
    dets = face_recognition.face_locations(npimg)
    faces = []
    #for det, score in zip(dets, scores):
    for det in dets:
        #if score < DeepFaceConfs.get()['detector']['dlib']['score_th']:
        #    continue

        top, right, bottom, left = det

        x = max(left, 0)
        y = max(top, 0)
        w = min(right - left, npimg.shape[1] - x)
        h = min(bottom - top, npimg.shape[0] - y)

        if w <= 1 or h <= 1:
            continue

        bbox = BoundingBox(x, y, w, h, 0)

        # find landmark
        bbox.face_landmark = np.zeros((68, 2), dtype=np.int)

        faces.append(bbox)

    #faces = sorted(faces, key=lambda x: x.score, reverse=True)
    print(faces)
    return faces


def extract_embeddings2(img_path):

    #npimg = cv2.imread(img_path, cv2.IMREAD_COLOR)
    pixels = face_recognition.load_image_file(img_path)

    #start_time = datetime.now()
    #faces = detector.detect(npimg)
    faces = detect2(pixels)
    #print(faces)
    #print('[1 Time taken: {!s}]'.format(datetime.now() - start_time))

    npimg = cv2.cvtColor(np.asarray(pixels),cv2.COLOR_RGB2BGR)

    #start_time = datetime.now()
    _, feats = recognizer.extract_features(npimg=npimg, faces=faces)
    #print('[2 Time taken: {!s}]'.format(datetime.now() - start_time))

    #features[name] = feats[0]

    #show_with_face(npimg, faces)

    feats = [i / np.linalg.norm(i, 2) for i in feats]

    return feats, faces



if __name__ == '__main__':
    e, f = extract_embeddings('../data/test2/chenzhipeng/1_0_chenzhipeng_0083.jpg')

    print(e)
    print(f)

    #e, f = extract_embeddings2('../data/test2/chenzhipeng/1_0_chenzhipeng_0083.jpg')

    #print(e)
    #print(f)
