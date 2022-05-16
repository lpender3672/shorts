import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import tensorflow as tf

#W1 = tf.Variable(np.random.randn(15,6))
#b1 = tf.Variable(np.zeros((W1.shape[0],1)))
#W2 = tf.Variable(np.random.randn(15,W1.shape[0]))
#b2 = tf.Variable(np.zeros((W2.shape[0],1)))
#W3 = tf.Variable(np.random.randn(1,W2.shape[0]))
#b3 = tf.Variable(np.zeros((W3.shape[0],1)))

def initialize(layers_dims):
    parameters = {}
    for layer in range(len(layers_dims)-1):
        parameters["W" + str(layer + 1)] = tf.Variable(np.random.randn(layers_dims[layer + 1],layers_dims[layer])) 
        parameters["b" + str(layer + 1)] = tf.Variable(np.zeros((layers_dims[layer + 1],1)))
    return (parameters)
parameters = initialize([6,15,15,1])

X_data = np.array([[1,1,1,0,0,0], [0,0,0,1,1,1], [1,1,0,0,0,0], [0,1,0,0,0,0], [0,0,1,0,0,0]])
Y_data = np.array([1,0,1,0,1])
m = X_data.shape[0]
X_data = (X_data.T).reshape(6,m)
X = tf.placeholder(tf.float64, shape=(6, m))
Y_data = Y_data.reshape(1, m)
Y = tf.placeholder(tf.float64, shape=(1, m))

#layer1 = tf.nn.relu(tf.matmul(W1, X) + b1)
#layer2 = tf.nn.relu(tf.matmul(W2, layer1) + b2)
#layer3 = tf.nn.softmax(tf.matmul(W3, layer2) + b3) 

def forward_propagate(X, parameters):
    pred = X
    for i in range(int(len(parameters)/2) - 1 ):
        pred = tf.nn.relu(tf.matmul(parameters['W'+ str(i+1)], pred) + parameters['b' + str(i+1)])
    pred = tf.nn.softmax(tf.matmul(parameters['W' + str(i+2)], pred) + parameters['b'+ str(i+2)])
    return (pred)

pred = forward_propagate(X, parameters)

LW1 = np.array([])
Lb1 = np.array([])
LW2 = np.array([])
Lb2 = np.array([])


training_epoch = 2000
learning_rate = 0.1

                              
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = pred,labels = Y))
optimizer = tf.train.AdamOptimizer(learning_rate = 0.01).minimize(cost)
init = tf.global_variables_initializer()

with tf.Session() as session:
    session.run(init)
    for epoch in range(training_epoch):
        minibatch_cost = 0
        _ , minibatch_cost= session.run([optimizer, cost], feed_dict={X: X_data, Y: Y_data})
        print(minibatch_cost)
    #LW1,Lb1, LW2, Lb2 = session.run([W1, b1,W2, b2])
    #print(LW1 +Lb1+  LW2+  Lb2)