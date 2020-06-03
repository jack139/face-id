# coding:utf-8
from datetime import datetime
import urllib3, json, base64

#from models.vggface import verify
#from models.face_evoLVe import verify
from facelib import api_func

from facelib import utils 
import face_recognition

urllib3.disable_warnings()

with open('../data/me/2s.jpg', 'rb') as f:
    img_data = f.read()
    img_data = base64.b64encode(img_data).decode('utf-8')

with open('../data/me/2.jpg', 'rb') as f:
    img_data2 = f.read()
    img_data2 = base64.b64encode(img_data2).decode('utf-8')


if __name__ == '__main__':

    start_time = datetime.now()
    encoding_list, face_boxes = api_func.face_features(img_data2)
    print('[Time taken: {!s}]'.format(datetime.now() - start_time))

    print(face_boxes)

    print('*'*20)

    start_time = datetime.now()
    encoding_list, face_boxes = api_func.face_features(img_data)
    print('[Time taken: {!s}]'.format(datetime.now() - start_time))

    print(face_boxes)


    #pixels = utils.load_image_b64(img_data)
    #start_time = datetime.now()
    #face_bounding_boxes = face_recognition.face_locations(pixels)
    #print('[Time taken: {!s}]'.format(datetime.now() - start_time))
    #print(face_bounding_boxes)

'''
VGG 

[1 Time taken: 0:00:00.083070]
[2 Time taken: 0:00:01.539855]
[3 Time taken: 0:00:01.546304]
[4 Time taken: 0:00:00.000195]
[4 Time taken: 0:00:00.840806]
[Time taken: 0:00:02.387366]
[(576, 1093, 1242, 428)]
********************
[1 Time taken: 0:00:00.044739]
[2 Time taken: 0:00:01.458869]
[3 Time taken: 0:00:01.465369]
[4 Time taken: 0:00:00.000224]
[4 Time taken: 0:00:00.066552]
[Time taken: 0:00:01.535262]
[(576, 1093, 1242, 428)]

EVO

[1 Time taken: 0:00:00.084194]
[2 Time taken: 0:00:01.539117]
[3 Time taken: 0:00:01.545524]
[4 Time taken: 0:00:00.813897]
[Time taken: 0:00:02.359666]
[(576, 1093, 1242, 428)]
********************
[1 Time taken: 0:00:00.043905]
[2 Time taken: 0:00:01.431460]
[3 Time taken: 0:00:01.437975]
[4 Time taken: 0:00:00.543777]
[Time taken: 0:00:01.981951]
[(576, 1093, 1242, 428)]

'''
