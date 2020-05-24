# Train multiple images per person
# Find and recognize faces in an image using a SVC with scikit-learn

"""
Structure:
        <test_image>.jpg
        <train_dir>/
            <person_1>/
                <person_1_face-1>.jpg
                <person_1_face-2>.jpg
                .
                .
                <person_1_face-n>.jpg
           <person_2>/
                <person_2_face-1>.jpg
                <person_2_face-2>.jpg
                .
                .
                <person_2_face-n>.jpg
            .
            .
            <person_n>/
                <person_n_face-1>.jpg
                <person_n_face-2>.jpg
                .
                .
                <person_n_face-n>.jpg
"""

import face_recognition
from sklearn import svm
import os, sys
import pickle

# Training the SVC classifier

# The training data would be all the face encodings from all the known images and the labels are their names
encodings = []
names = []

if __name__ == "__main__":
    if len(sys.argv)<2:
        print("usage: python3 %s <train_data_dir> [model_name]" % sys.argv[0])
        sys.exit(2)

    train_data_dir = sys.argv[1]

    if len(sys.argv)>2:
        model_name = sys.argv[2]
    else:
        model_name = 'trained_knn_model'


    # Training directory
    train_dir = os.listdir(train_data_dir)

    # Loop through each person in the training directory
    for person in train_dir:
        print('encoding: ', person)
        pix = os.listdir(os.path.join(train_data_dir, person))

        # Loop through each training image for the current person
        for person_img in pix:
            # Get the face encodings for the face in each image file
            face = face_recognition.load_image_file(os.path.join(train_data_dir, person, person_img))
            face_bounding_boxes = face_recognition.face_locations(face)

            #If training image contains exactly one face
            if len(face_bounding_boxes) == 1:
                face_enc = face_recognition.face_encodings(face)[0]
                # Add face encoding for current image with corresponding label (name) to the training data
                encodings.append(face_enc)
                names.append(person)
            else:
                print(person + "/" + person_img + " was skipped and can't be used for training")

    # Create and train the SVC classifier
    print('training...')
    clf = svm.SVC(gamma='scale')
    clf.fit(encodings,names)

    with open(model_name+'.svm.clf', 'wb') as f:
        pickle.dump(clf, f)

    print('done.')
