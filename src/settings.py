# -*- coding: utf-8 -*-

from importlib import import_module

ALGORITHM = {
    'rec' : { 'distance_threshold' : 0.6, 'ext' : '.rec.clf', 'module' : 'face-recognition.knn' },
    'vgg'  : { 'distance_threshold' : 0.8, 'ext' : '.vgg.clf', 'module' : 'vggface.knn' },
}

def import_knn(face_algorithm):
    return import_module(ALGORITHM[face_algorithm]['module'])
