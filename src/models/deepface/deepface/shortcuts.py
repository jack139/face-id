import os
from glob import glob
from datetime import datetime

import cv2
from tqdm import tqdm

from .confs.conf import DeepFaceConfs
from .detectors.detector_dlib import FaceDetectorDlib
from .detectors.detector_ssd import FaceDetectorSSDInceptionV2, FaceDetectorSSDMobilenetV2
from .recognizers.recognizer_vgg import FaceRecognizerVGG
from .recognizers.recognizer_resnet import FaceRecognizerResnet


def get_detector(name='ssd_mobilenet_v2'):
    """

    :type name: str
    :param name: 
    :return:
    """

    if name == 'dlib':
        return FaceDetectorDlib()
    elif name == 'ssd_inception_v2':
        return FaceDetectorSSDInceptionV2()
    elif name == 'ssd_mobilenet_v2':
        return FaceDetectorSSDMobilenetV2()

    return None


def get_recognizer(name='vgg', db=None):
    """

    :param db:
    :param name:
    :return:
    """
    if name == 'vgg':
        return FaceRecognizerVGG(custom_db=db)
    elif name == 'vgg2':
        return FaceRecognizerResnet(custom_db=db)

    return None


def save_features(img_folder_path, output_path=None, method="vgg"):
    """

    :param path: folder contain images("./samples/faces/")
    :return:
    """
    name_paths = [(os.path.basename(img_path)[:-4], img_path)
                  for img_path in glob(os.path.join(img_folder_path, "*.jpg"))]

    detector = get_detector()
    recognizer = get_recognizer(name=method)

    features = {}
    for name, path in tqdm(name_paths):
        npimg = cv2.imread(path, cv2.IMREAD_COLOR)
        start_time = datetime.now()
        faces = detector.detect(npimg)
        print(faces)
        print('[1 Time taken: {!s}]'.format(datetime.now() - start_time))
        _, feats = recognizer.extract_features(npimg=npimg, faces=faces)
        print('[2 Time taken: {!s}]'.format(datetime.now() - start_time))
        features[name] = feats[0]

    import pickle
    if not output_path:
        output_path = os.path.join("recognizers/vggface", os.path.basename(img_folder_path) + ".pkl")
    with open(output_path, 'wb') as f:
        pickle.dump(features, f, pickle.HIGHEST_PROTOCOL)
