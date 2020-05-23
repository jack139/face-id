# -*- coding: utf-8 -*-

import os, sys
from datetime import datetime
import knn

if __name__ == "__main__":
    if len(sys.argv)<3:
        print("usage: python3 %s <model_name> <test dir or file>" % sys.argv[0])
        sys.exit(2)

    test_thing = sys.argv[2]
    model_name = sys.argv[1]

    if not model_name.endswith('.clf'):
        model_name += '.clf'

    if os.path.isdir(test_thing):
        images = os.listdir(test_thing)
        images = [os.path.join(test_thing, i) for i in images]
    else:
        images = [ test_thing ]

    # Using the trained classifier, make predictions for unknown images
    for image_file in images:
        print("Looking for faces in {}".format(image_file))

        # Find all people in the image using a trained classifier model
        # Note: You can pass in either a classifier file name or a classifier model instance
        start_time = datetime.now()
        predictions = knn.predict(image_file, model_path=model_name, distance_threshold=0.5)
        print('[Time taken: {!s}]'.format(datetime.now() - start_time))

        # Print results on the console
        for name, (top, right, bottom, left), distance in predictions:
            print("- Found {} at ({}, {}), distance={}".format(name, left, top, distance))

        # Display results overlaid on an image
        knn.show_prediction_labels_on_image(image_file, predictions)
