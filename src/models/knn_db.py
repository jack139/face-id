"""
Algorithm Description:
The knn classifier is first trained on a set of labeled (known) faces and can then predict the person
in an unknown image by finding the k most similar faces (images with closet face-features under eucledian distance)
in its training set, and performing a majority vote (possibly weighted) on their label.

For example, if k=3, and the three closest face images to the given image in the training set are one image of Biden
and two images of Obama, The result would be 'Obama'.

"""

import math, operator
from datetime import datetime
from sklearn import neighbors
import pickle
from facelib import dbport

# 训练
def train(group_id, encodings_index=0, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False, face_algorithm='rec'):
    """
    Trains a k-nearest neighbors classifier for face recognition.

    :param model_save_path: (optional) path to save model on disk
    :param n_neighbors: (optional) number of neighbors to weigh in classification. Chosen automatically if not specified
    :param knn_algo: (optional) underlying data structure to support knn.default is ball_tree
    :param verbose: verbosity of training
    :return: returns knn classifier that was trained on the given data.
    """
    X = []
    y = []

    # 按用户分组从db装入特征数据
    user_list = dbport.user_list_by_group(group_id)
    for i in range(len(user_list)):
        faces = dbport.user_face_list(group_id, user_list[i])
        for f in faces:
            r = dbport.face_info(f)
            if r:
                X.append(r['encodings'][encodings_index])
                y.append(user_list[i])

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    start_time = datetime.now()
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)
    print('[Time taken: {!s}]'.format(datetime.now() - start_time))

    # Save the trained KNN classifier
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf


# 识别
def predict(faces_encodings, knn_clf=None, model_path=None, distance_threshold=0.6, face_algorithm='rec'):
    """
    Recognizes faces in given image using a trained KNN classifier

    :param knn_clf: (optional) a knn classifier object. if not specified, model_save_path must be specified.
    :param model_path: (optional) path to a pickled knn classifier. if not specified, model_save_path must be knn_clf.
    :param distance_threshold: (optional) distance threshold for face classification. the larger it is, the more chance
           of mis-classifying an unknown person as a known one.
    :return: a list of names and face locations for the recognized faces in the image: [(name, bounding box), ...].
        For faces of unrecognized persons, the name 'unknown' will be returned.
    """

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    # Load a trained KNN model (if one was passed in)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    #print(faces_encodings)

    # Use the KNN model to find the first 5 best matches for the test face
    # 返回5个最佳结果
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=5)
    #are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Predict classes and remove classifications that aren't within the threshold
    #return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

    #print(closest_distances)

    # return multi results
    results = []
    for i in range(len(X_face_locations)):
        # 第一个超过阈值，说明未匹配到
        if closest_distances[0][i][0]>distance_threshold:
            results.append(['unknown', X_face_locations[i], round(closest_distances[0][i][0], 6), 0])
            continue
        # 将阈值范围内的结果均返回
        labels = {}
        temp_result = []
        for j in range(len(closest_distances[0][i])):
            if closest_distances[0][i][j]<=distance_threshold:
                # labels are in classes_
                l = knn_clf.classes_[knn_clf._y[closest_distances[1][i][j]]]
                #results.append( (l, X_face_locations[i], round(closest_distances[0][i][j], 6)) )
                if l not in labels.keys():
                    temp_result.append([
                        l, 
                        X_face_locations[i], 
                        round(closest_distances[0][i][j], 6)
                    ])
                    labels[l] = 1
                else:
                    labels[l] += 1

        # 找到labels里count最大值
        max_count = max(labels.items(), key=operator.itemgetter(1))[1]
        # 相同人脸位置，labels 里 count最大的认为就是结果，如果count相同才返回多结果
        results.extend([i+[labels[i[0]]] for i in temp_result if labels[i[0]]==max_count])
        # 当count最大的不是距离最短的结果时，同时返回距离最短的结果
        #results.extend( [result+[labels[result[0]]] for i,result in enumerate(temp_result) \
        #    if labels[result[0]]==max_count or (i==0 and labels[result[0]]!=max_count)] )

    return results
