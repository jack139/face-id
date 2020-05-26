# -*- coding: utf-8 -*-

import os, sys
import face_recognition
from sklearn import svm
import pickle
from datetime import datetime

if __name__ == "__main__":
    if len(sys.argv)<3:
        print("usage: python3 %s <model_name> <test dir>" % sys.argv[0])
        sys.exit(2)

    test_path = sys.argv[2]
    model_name = sys.argv[1]

    if not model_name.endswith('.clf'):
        model_name += '.clf'

    if not os.path.isdir(test_path):
        print('test need directory.')
        sys.exit(0)

    # load model
    with open(model_name, 'rb') as f:
        clf = pickle.load(f)

    persons = os.listdir(test_path)

    print('name\t\ttotal\tcorrect\twrong\tfail\tacc\tpreci\telapsed time')
    for p in persons:
        images = os.listdir(os.path.join(test_path, p))
        images = [os.path.join(test_path, p, i) for i in images]

        # Using the trained classifier, make predictions for unknown images
        total = len(images)
        correct = 0
        wrong = 0
        fail = 0
        start_time = datetime.now()
        for image_file in images:
            #print("Looking for faces in {}".format(image_file))

            # Load the test image with unknown faces into a numpy array
            test_image = face_recognition.load_image_file(image_file)

            # Find all the faces in the test image using the default HOG-based model
            face_locations = face_recognition.face_locations(test_image)
            no = len(face_locations)
            #print("Number of faces detected: ", no)
            if no==0:
                fail += 1
            else:
                # Predict all the faces in the test image using the trained classifier
                #print("Found:")
                for i in range(no):
                    test_image_enc = face_recognition.face_encodings(test_image)[i]
                    name = clf.predict([test_image_enc])
                    #print(*name)
                    if name[0]==p:
                        correct += 1
                    else:
                        wrong += 1

        print('%10s\t%d\t%d\t%d\t%d\t%.3f\t%.3f\t%s'%\
            (p, total, correct, wrong, fail, correct/total, correct/(total-fail), datetime.now() - start_time))
