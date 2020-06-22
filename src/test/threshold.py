# -*- coding: utf-8 -*-

import sys
import pickle
from models import knn



if __name__ == "__main__":
    if len(sys.argv)<2:
        print("usage: python3 %s <Xy_file>" % sys.argv[0])
        sys.exit(2)

    Xy_file = sys.argv[1]

    with open(Xy_file, 'rb') as f:
        X, y = pickle.load(f)

    knn.score_acc_f1(X, y)
