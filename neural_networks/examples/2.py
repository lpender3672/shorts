import numpy as np
from scipy import optimize

class NeuralNet(object):
  def __init__(self):
    self.InputLayerSize=1
    self.OutputLayerSize=1
    self.HiddenLayerSize=3

    self.w1 = np.random.randn(self.InputLayerSize,self.HiddenLayerSize)
    print(self.w1)
    self.w2 = np.random.randn(self.HiddenLayerSize,self.OutputLayerSize)
    print(self.w2)
######forward propergation###########
  def forward(self, x):
    self.z2 = np.dot(x,self.w1)
    self.a2 = self.sigmoid(self.z2)
    self.z3 = np.dot(self.a2,self.w2)
    self.YHat = self.sigmoid(self.z3)
    return(self.YHat)


  def sigmoid(self, z):
    return(1/(1+np.exp(-z)))

###################Backpropergating######################
  def sigmoidPrime(self,z):
    return(np.exp(-z)/((1+np.exp(-z))**2))

  def costFunction(self, x, y):
    #Compute cost for given x,y, use weights already stored in class.
    self.yHat = self.forward(x)
    J = 0.5*sum((y-self.YHat)**2)
    return J
  
  def CostFunctionPrime(self, x, y):
    YHat = self.forward(x)

    delta3 = np.multiply(-(y-YHat) , self.sigmoidPrime(self.z3))
    DjDw2 = np.dot(self.a2.T, delta3)

    delta2 = np.dot(delta3, self.w2.T) * self.sigmoidPrime(self.z2)
    DjDw1 = np.dot(x.T, delta2)

    return DjDw1, DjDw2
  
  def getParams(self):
    #Get W1 and W2 unrolled into vector:
    params = np.concatenate((self.w1.ravel(), self.w2.ravel()))
    return params
    
  def setParams(self, params):
      #Set W1 and W2 using single paramater vector.
      w1_start = 0
      w1_end = self.HiddenLayerSize * self.InputLayerSize
      self.w1 = np.reshape(params[w1_start:w1_end], (self.InputLayerSize , self.HiddenLayerSize))
      w2_end = w1_end + self.HiddenLayerSize*self.OutputLayerSize
      self.w2 = np.reshape(params[w1_end:w2_end], (self.HiddenLayerSize, self.OutputLayerSize))
      
  def computeGradients(self, x, y):
      DjDw1, DjDw2 = self.CostFunctionPrime(x,y)
      return np.concatenate((DjDw1.ravel(), DjDw2.ravel()))


def computeNumericalGradient(N, x, y):
      paramsInitial = N.getParams()
      numgrad = np.zeros(paramsInitial.shape)
      perturb = np.zeros(paramsInitial.shape)
      e = 1e-4

      for p in range(len(paramsInitial)):
          #Set perturbation vector
          perturb[p] = e
          N.setParams(paramsInitial + perturb)
          loss2 = N.costFunction(x, y)
          
          N.setParams(paramsInitial - perturb)
          loss1 = N.costFunction(x, y)

          #Compute Numerical Gradient
          numgrad[p] = (loss2 - loss1) / (2*e)

          #Return the value we changed to zero:
          perturb[p] = 0
          
      #Return Params to original value:
      N.setParams(paramsInitial)

      return numgrad
##################optimization########################

class trainer(object):
    def __init__(self, N):
        #Make Local reference to network:
        self.N = N
        
    def callbackF(self, params):
        self.N.setParams(params)
        self.J.append(self.N.costFunction(self.x, self.y))   
        
    def costFunctionWrapper(self, params, x, y):
        self.N.setParams(params)
        cost = self.N.costFunction(x, y)
        grad = self.N.computeGradients(x,y)
        
        return cost, grad
        
    def train(self, x, y):
        #Make an internal variable for the callback function:
        self.x = x
        self.y = y

        #Make empty list to store costs:
        self.J = []
        
        params0 = self.N.getParams()

        options = {'maxiter': 200, 'disp' : True}
        _res = optimize.minimize(self.costFunctionWrapper, params0, jac=True, method='BFGS', \
                                 args=(x, y), options=options, callback=self.callbackF)

        self.N.setParams(_res.x)
        self.optimizationResults = _res

#####################variables and outputs###############################
NN = NeuralNet()
#x=np.array(([0,0],[0,1],[1,0],[1,1]))
#y=np.array(([0],[1],[1],[0]))
x=np.array(([0.01],[0.02],[0.03],[0.04]))
y=np.array(([0.03],[0.05],[0.07],[0.09]))


#numgrad = computeNumericalGradient(NN, x, y)
grad = np.linalg.norm(NN.computeGradients(x,y))
#print(np.linalg.norm(grad-numgrad)/np.linalg.norm(grad+numgrad))





T = trainer(NN)
T.train(x,y)
#NN.CostFunctionPrime(x,y)
#YHat = NN.forward(x) 


##DjDw1, DjDw2 = NN.CostFunctionPrime(x,y)
print(NN.CostFunctionPrime(x,y))

"""
while grad >=0.0001:
  NN.w1 = NN.w1 - 3*DjDw1
  NN.w2 = NN.w2 - 3*DjDw2
  grad = np.linalg.norm(NN.computeGradients(x,y))
  print(grad)
"""
YHat=NN.forward(x)


print(x[0],np.round(YHat[0],2),y[0])
print(x[1],np.round(YHat[1],2),y[1])
print(x[2],np.round(YHat[2],2),y[2])
print(x[3],np.round(YHat[3],2),y[3])

print(np.round(NN.forward([0.05]),2))

