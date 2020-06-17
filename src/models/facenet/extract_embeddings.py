# -*- coding: utf-8 -*-

import tensorflow.compat.v1 as tf
import numpy as np
from . import facenet
import math

batch_size = 90

def extract_embeddings(G, images):
    assert(len(images)<batch_size), 'images should less than batch_size'
    
    seed = 666

    with G.as_default():
      
        with tf.Session() as sess:
            
            np.random.seed(seed=seed)            

            # Load the model
            #print('Loading feature extraction model')
            #facenet.load_model(model)
            
            # Get input and output tensors
            images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
            embedding_size = embeddings.get_shape()[1]
            
            # Run forward pass to calculate embeddings
            print('Calculating features for images')
            nrof_images = len(images)
            #nrof_batches_per_epoch = int(math.ceil(1.0*nrof_images / batch_size))
            emb_array = np.zeros((nrof_images, embedding_size))
            #for i in range(nrof_batches_per_epoch):
            #    start_index = i*batch_size
            #    end_index = min((i+1)*batch_size, nrof_images)
            #    paths_batch = paths[start_index:end_index]
            #    images = facenet.load_data(paths_batch, False, False, image_size)
            feed_dict = { images_placeholder:images, phase_train_placeholder:False }
            emb_array[0:nrof_images,:] = sess.run(embeddings, feed_dict=feed_dict)

    return emb_array


if __name__ == '__main__':
    image_size = 160
    model = '/home/gt/Codes/yhtech/face_model/20180402-114759/20180402-114759.pb'
    image_list = [
        '../../../data/aligned/alex_lacamoire/img1.png',
        '../../../data/aligned/biden/biden.png'
    ]
    images = facenet.load_data(image_list, False, False, image_size)
    r = extract_embeddings(images, model)
    print(r)
