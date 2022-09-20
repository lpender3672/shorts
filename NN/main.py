
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation

class layer(object):

    def sigmoid(self, x):
        return 1/(1+np.exp(-x))

    def __init__(self, n_inputs, n_outputs):
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs

        self.weights = np.random.rand(n_inputs, n_outputs)
        self.biases = np.zeros((1, n_outputs))

        self.cost_gradient_weights = np.zeros((n_inputs, n_outputs))
        self.cost_gradient_biases = np.zeros((1, n_outputs))
    
    def forward(self, inputs):
        self.output = np.dot(inputs, self.weights) + self.biases
        return self.sigmoid(self.output)
    
    def backward(self, d_output):
        self.d_weights = np.dot(d_output, self.output.T)
        self.d_biases = np.sum(d_output, axis=0, keepdims=True)
        self.d_inputs = np.dot(self.weights.T, d_output)
        return self.d_inputs
    
    def apply_gradients(self, learning_rate):
        self.weights -= learning_rate * self.cost_gradient_weights
        self.biases -= learning_rate * self.cost_gradient_biases

class network(object):
    def __init__(self, layer_sizes):
        self.layer_sizes = layer_sizes

        self.in_size = layer_sizes[0]
        self.out_size = layer_sizes[-1]

        self.layers = []
        for i in range(len(layer_sizes) - 1):
            self.layers.append(layer(layer_sizes[i], layer_sizes[i+1]))
        self.layers.append(layer(layer_sizes[-1], layer_sizes[-1]))
    
    def outputs(self, inputs):
        for layer in self.layers:
            inputs = layer.forward(inputs)
        return inputs
    
    def classify(self, inputs):
        return np.argmax(self.outputs(inputs), axis=2)

    def loss(self, inputs, target):
        square_error = np.square(self.outputs(inputs) - target)
        return np.sum(square_error)

    def learn(self, inputs, target, learning_rate):
        
        h = 0.0001
        initial_loss = self.loss(inputs, target)

        for layer in self.layers:

            for  i in range(layer.n_inputs):
                for j in range(layer.n_outputs):
                    layer.weights[i, j] += h
                    d_loss = self.loss(inputs, target) - initial_loss
                    layer.cost_gradient_weights[i, j] = d_loss / h
                    layer.weights[i, j] -= h

            for j in range(layer.n_outputs):
                layer.biases[0, j] += h
                d_loss = self.loss(inputs, target) - initial_loss
                layer.cost_gradient_biases[0, j] = d_loss / h
                layer.biases[0, j] -= h
        
        for layer in self.layers:
            layer.apply_gradients(learning_rate)
    
    def train(self, inputs, target, learning_rate, epochs, update_func = None):

        self.error_history = []
        self.epoch_history = [self.outputs(inputs)]

        self.history = []

        for i in range(epochs):
            
            if (i % 10) == 0:
                self.history.append(self.outputs(inputs))
                if update_func:
                    update_func()

            if (i % 100) == 0:
                print(f"Epoch {i}/{epochs}, Loss: {self.loss(inputs, target)}")

            self.learn(inputs, target, learning_rate)
            self.error_history.append(self.loss(inputs, target))
            self.epoch_history.append(i)
        
        print("Final Error: ", self.error_history[-1])
        #plt.plot(np.linspace(1,epochs,epochs), np.array(error))
    
    

def f(x):
    return 0.2*x**4 + 0.1*x**3 - x**2 + 2

net = network([2, 3, 3, 1])

x,y = np.meshgrid(np.linspace(-1,1,20), np.linspace(0,1,10))

inputs = np.array([x.ravel(), y.ravel()]).T
outputs = np.less(x**2 + y**2, 0.5).reshape(200, 1).astype(int)

firstoutput = net.outputs(inputs)


def get_boundary(x, net):
    ## returns y values at given x values at the class boundary
    samples = 100
    ypos = np.linspace(0, 1, samples)
    xgrid, ygrid = np.meshgrid(x, ypos)
    sample_input = np.array([xgrid.ravel(), ygrid.ravel()]).T
    sample_output = net.outputs(sample_input).reshape(samples, x.size)
    y = ypos[np.argmin(abs(sample_output - 0.5), axis = 0)]
    #print(y)
    return y

x_boundary_line = np.linspace(-1, 1, 100)
y_boundary_lines = []

def epoch_update():
    y_boundary_lines.append(get_boundary(x_boundary_line, net))


net.train(inputs, outputs, 0.1, 5000, epoch_update)
out = net.outputs(inputs)

fig, ax = plt.subplots()

scatter = ax.scatter(x, y)
color = np.less(firstoutput, 0.5).reshape(200, 1).astype(int)
color = np.array([[0, 0, 1] if c == 1 else [1, 0, 0] for c in color])
scatter.set_color(color)
boundary_line = ax.plot(x_boundary_line, y_boundary_lines[0], color="black")[0]
plt.axis('scaled')

def animate(i):
    data = net.history[i % len(net.history)]
    color = np.less(data, 0.5).reshape(200, 1).astype(int)
    color = np.array([[0, 0, 1] if c == 1 else [1, 0, 0] for c in color])
    scatter.set_color(color)
    boundary_line.set_ydata(y_boundary_lines[i % len(y_boundary_lines)])
    return scatter

ani = animation.FuncAnimation(fig, animate, interval=50)

# To save the animation, use e.g.
#
# ani.save("movie.mp4")

plt.show()