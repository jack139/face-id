
import tensorflow as tf
import numpy as np
from .nets.L_Resnet_E_IR_fix_issue9 import get_resnet
import tensorlayer as tl
import cv2
from PIL import Image
#from datetime import datetime

from .initializer import xavier_initializer


def load_image(filename, image_size=[112,112]):
    img = Image.open(filename)
    img = img.convert('RGB')
    img = img.resize(image_size)
    np_img = np.array(img)
    np_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
    return np.array(np_img, dtype=np.float32)

def data_iter(datasets, batch_size):
    data_num = datasets.shape[0]
    for i in range(0, data_num, batch_size):
        yield datasets[i:min(i+batch_size, data_num), ...]


def extract_embeddings(sess, datas, embedding_tensor, batch_size=32, feed_dict=None, input_placeholder=None):
    embeddings = None
    feed_dict.setdefault(input_placeholder, None)
    for idx, data in enumerate(data_iter(datas, batch_size)):
        data_tmp = data.copy()    # fix issues #4
        data_tmp -= 127.5
        data_tmp *= 0.0078125
        feed_dict[input_placeholder] = data_tmp

        #start_time = datetime.now()
        _embeddings = sess.run(embedding_tensor, feed_dict)
        #print('[Time taken: {!s}]'.format(datetime.now() - start_time))

        if embeddings is None:
            embeddings = np.zeros((datas.shape[0], _embeddings.shape[1]))
        try:
            embeddings[idx*batch_size:min((idx+1)*batch_size, datas.shape[0]), ...] = _embeddings
        except ValueError:
            print('idx*batch_size value is %d min((idx+1)*batch_size, datas.shape[0]) %d, batch_size %d, data.shape[0] %d' %
                  (idx*batch_size, min((idx+1)*batch_size, datas.shape[0]), batch_size, datas.shape[0]))
            print('embedding shape is ', _embeddings.shape)

    feats = [i / np.linalg.norm(i, 2) for i in embeddings]
    return feats


def main(image_path):
    image_size = [112, 112]
    net_depth = 50
    num_output = 85164
    ckpt_index_list = ['710000.ckpt']
    ckpt_file = '/home/gt/Codes/yhtech/face_model/ckpt_model_d/InsightFace_iter_best_'

    images = tf.placeholder(name='img_inputs', shape=[None, *image_size, 3], dtype=tf.float32)
    labels = tf.placeholder(name='img_labels', shape=[None, ], dtype=tf.int64)
    dropout_rate = tf.placeholder(name='dropout_rate', dtype=tf.float32)

    w_init_method = xavier_initializer(uniform=False)
    net = get_resnet(images, net_depth, type='ir', w_init=w_init_method, trainable=False, keep_rate=dropout_rate)
    embedding_tensor = net.outputs
    # mv_mean = tl.layers.get_variables_with_name('resnet_v1_50/bn0/moving_mean', False, True)[0]
    # 3.2 get arcface loss
    #logit = arcface_loss(embedding=net.outputs, labels=labels, w_init=w_init_method, out_num=num_output)

    sess = tf.Session()
    saver = tf.train.Saver()

    result_index = []
    file_index = ckpt_index_list[0]
    feed_dict_test = {}
    path = ckpt_file + file_index
    saver.restore(sess, path)
    print('ckpt file %s restored!' % file_index)
    feed_dict_test.update(tl.utils.dict_to_one(net.all_drop))
    feed_dict_test[dropout_rate] = 1.0

    data = load_image(image_path)

    results = extract_embeddings(sess, np.array(data), embedding_tensor, feed_dict=feed_dict_test, input_placeholder=images)

    result_index.append(results)

    return result_index

if __name__ == '__main__':
    r = main('../data/aligned112/biden/biden.png')
    print(r)