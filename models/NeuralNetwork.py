# coding: utf-8

import numpy as np
from models.InitialWeights import InitialWeights
from models.NeuralNetworkMath import NeuralNetworkMath


class NeuralNetwork:
    def __init__(self, hyper_parameters, training_set, debug=False):
        layers_n_neurons = hyper_parameters["layers_structure"]
        self.training_set = training_set
        self.debug = debug
        self.layer_neurons = layers_n_neurons
        self.n_layers = len(layers_n_neurons)
        self.weight_matrices = []
        self.bias_weights_matrices = []
        self._lambda = hyper_parameters["lambda"] or 0.1
        self.last_activations = [None] * self.n_layers
        self.deltas = [None] * self.n_layers
        self.build_neurons()
        self.train(training_set)

    def predict(self, features=[]):
        """
        :param features:
        :return:
        """
        return self.outputs(features)

    def outputs(self, inputs=[]):
        features_matrix = self.array_to_matrix(inputs)
        accumulator = features_matrix
        # Multiplica todas as matrizes, (entrada x pesos) + bias.
        # Forward propagation
        for layer_i in range(len(self.weight_matrices)):
            accumulator = self.hidden_activation(accumulator, layer_i)
        return accumulator.tolist()

    def hidden_activation(self, acc_matrix=[], layer=0):
        weights = self.weight_matrices[layer]
        bias = self.bias_weights_matrices[layer]
        print(weights, acc_matrix, bias)
        zs = np.add(weights.dot(acc_matrix), bias)
        print(zs)
        activations = NeuralNetworkMath.sigmoid(zs)
        self.last_activations[layer] = activations
        return activations

    def back_propagate(self, expected_outputs=[]):
        for layer in reversed(range(self.n_layers)):
            if layer == self.last_layer_index():
                deltas = self.outputs(expected_outputs)
            else:
                activations = self.last_activations[layer]
                weights = self.weight_matrices[layer]
                next_layer_deltas = self.deltas[layer+1]
                deltas = NeuralNetworkMath.delta(activations,
                                                 weights,
                                                 next_layer_deltas)
            self.deltas[layer] = deltas

    def output_deltas(self, output_matrix=[[]]):
        outputs = self.last_activations[self.last_layer_index()]
        return np.subtract(outputs, output_matrix)

    def train(self, training_dataset):
        loss = 0
        for example in training_dataset.get_examples():
            # Isso tá incompleto. Ver a função NeuralNetworkMath.loss
            inputs = example.get_body()
            outputs = self.outputs(inputs)
            loss += NeuralNetworkMath.loss(outputs, [[1]])
        n_examples = len(training_dataset.examples)
        loss = loss / n_examples
        regularization = NeuralNetworkMath.loss_regularization(self.weight_matrices,
                                                               _lambda=self._lambda,
                                                               n_examples=n_examples)
        return loss + regularization

    def build_neurons(self):
        for layer in range(self.n_layers):
            if layer == 0:
                continue
            previous_n_neurons = self.layer_neurons[layer - 1]
            n_neurons = self.layer_neurons[layer]
            weights = InitialWeights.generate(n_neurons,
                                              previous_n_neurons,
                                              debug=self.debug)
            bias_weights = InitialWeights.generate(n_neurons, 1, debug=self.debug)
            self.weight_matrices.append(np.array(weights))
            self.bias_weights_matrices.append(bias_weights)

    def last_layer_index(self):
        return self.n_layers-1

    def array_to_matrix(self, array=[]):
        return list(map(lambda inp: [inp], array))

