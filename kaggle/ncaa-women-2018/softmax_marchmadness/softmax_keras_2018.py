#!/usr/local/bin/python
#
# Trains a softmax classifier to output the probability of one team beating another 
# - Wesley Chavez 03-05-2018 
#

import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.datasets import mnist
from keras.utils import np_utils
from keras.utils.np_utils import to_categorical

def build_logistic_model(input_dim, output_dim):
    model = Sequential()
    model.add(Dense(output_dim, input_dim=input_dim, activation='softmax'))

    return model

def main():

    train_nonorm = np.load('x.npy')
    test_nonorm = np.load('testdata_2018.npy')  # Data from 2018

    labels = np.load('labels.npy')
    trainlabels = labels.astype(int)

    # feature scaling
    n=np.amin(train_nonorm, axis=0)
    m=np.amax(train_nonorm, axis=0)
    m[m == 0] = 1
    n[n == m] = 0
    train = (train_nonorm-n)/(m-n)
    test = (test_nonorm-n)/(m-n)

    trainlabels = to_categorical(trainlabels,nb_classes=2)

    model = build_logistic_model(37, 2)
    
    model.summary()
    
    # compile the model
    model.compile(optimizer='adagrad', loss='categorical_crossentropy', metrics=['accuracy'])
    history = model.fit(train, trainlabels,
                        batch_size=50, nb_epoch=10000,
                        verbose=1)
    
    s=[]    
    for i in range (test.shape[0]):
        s.append(model.predict(test[i].reshape((1,37)))[0][0])
    print [ '{:0.6f}'.format(x) for x in s]
    # save model as json and yaml
    json_string = model.to_json()
    open('Logistic_model.json', 'w').write(json_string)
    yaml_string = model.to_yaml()
    open('Logistic_model.yaml', 'w').write(yaml_string)
    
    # save the weights in h5 format
    # model.save_weights('Logistic_wts.h5')
    
    # to read a saved model and weights
    # model = model_from_json(open('my_model_architecture.json').read())
    # model = model_from_yaml(open('my_model_architecture.yaml').read())
    # model.load_weights('my_model_weights.h5')



if __name__ == '__main__':
    main()

