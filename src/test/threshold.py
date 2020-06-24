# -*- coding: utf-8 -*-

import sys
import pickle
from models.knn import score_acc_f1
from facelib import dbport
from config.settings import ALGORITHM


if __name__ == "__main__":
    if len(sys.argv)<3:
        print("usage: python3 %s <db_vgg|db_evo|db_rec|file> <group_id|Xy_file>" % sys.argv[0])
        sys.exit(2)

    method = sys.argv[1]
    Xy_file = group_id = sys.argv[2]

    if method=='file':
        with open(Xy_file, 'rb') as f:
            X, y = pickle.load(f)
        print('Calculating...')
        score_acc_f1(X, y)

    elif method in ('db_vgg', 'db_evo', 'db_rec'):
        X = []
        y = []
        user_list = dbport.user_list_by_group(group_id)
        for i in range(len(user_list)):
            faces_list = dbport.user_face_list(group_id, user_list[i])

            for face in faces_list:
                r = dbport.face_info(face)

                X.append(r['encodings'][ALGORITHM[method[-3:]]['index']])
                y.append(user_list[i])
        print('Calculating...')
        score_acc_f1(X, y, title=method[-3:])

    else:
        print('Unknown method.')
        sys.exit(1)

    
