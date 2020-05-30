# -*- coding: utf-8 -*-

import os, sys
from settings import ALGORITHM
from models import knn_db
from facelib import dbport


if __name__ == "__main__":
    if len(sys.argv)<2:
        print("usage: python3 %s <group_id>" % sys.argv[0])
        sys.exit(2)

    group_id = sys.argv[1]


    face_algorithm = ['vgg', 'evo']

    for algorithm in face_algorithm:
        # Train the KNN classifier and save it to disk
        print("Training KNN classifier...")
        classifier = knn_db.train(group_id, 
            encodings_index=ALGORITHM[algorithm]['index'],
            model_save_path=group_id + ALGORITHM[algorithm]['ext'], 
            n_neighbors=2,
            face_algorithm=algorithm)
        print("Training complete!")
