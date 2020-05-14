# -*- coding: utf-8 -*-

import os, sys
from datetime import datetime
import knn


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

    persons = os.listdir(test_path)
    total_acc = 0

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

            # Find all people in the image using a trained classifier model
            # Note: You can pass in either a classifier file name or a classifier model instance
            predictions = knn.predict(image_file, model_path=model_name)

            # Print results on the console
            if len(predictions)==0:
                fail += 1
            else:
                for name, (top, right, bottom, left) in predictions:
                    #print("- Found {} at ({}, {})".format(name, left, top))
                    if name==p:
                        correct += 1
                    else:
                        wrong += 1

        print('%10s\t%d\t%d\t%d\t%d\t%.3f\t%.3f\t%s'%\
            (p, total, correct, wrong, fail, correct/total, correct/(total-fail), datetime.now() - start_time))

        total_acc += correct/total

    print('total_acc: %.3f'%(total_acc/len(persons)))