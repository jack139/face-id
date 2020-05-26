# -*- coding: utf-8 -*-

from importlib import import_module

ALGORITHM = {
    'rec' : { 'distance_threshold' : 0.6, 'ext' : '.rec.clf', 'module' : 'face_rec.verify' },
    'vgg'  : { 'distance_threshold' : 0.8, 'ext' : '.vgg.clf', 'module' : 'vggface.verify' },
    'evo'  : { 'distance_threshold' : 1.25, 'ext' : '.evo.clf', 'module' : 'face_evoLVe.verify' },
}


def import_verify(face_algorithm):
    return import_module(ALGORITHM[face_algorithm]['module'])
