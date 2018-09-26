# -*- coding:utf-8 -*-
from util.MathUtils import *
from util.util import interval
import matplotlib.pyplot as plt
from random import random


class BPNeuralNetwork:
    def __init__(self):
        self.input_n = 0
        self.hidden_n = 0
        self.output_n = 0
        self.input_cells = []
        self.hidden_cells = []
        self.output_cells = []
        self.input_weights = []
        self.output_weights = []
        self.input_correction = []
        self.output_correction = []

    def setup(self, ni, nh, no, learn, correct):
        self.input_n = ni + 1
        self.hidden_n = nh
        self.output_n = no
        # init cells
        self.input_cells = [1.0] * self.input_n
        self.hidden_cells = [1.0] * self.hidden_n
        self.output_cells = [1.0] * self.output_n
        # init weights
        self.input_weights = make_matrix(self.input_n, self.hidden_n)
        self.output_weights = make_matrix(self.hidden_n, self.output_n)
        # random activate
        for i in range(self.input_n):
            for h in range(self.hidden_n):
                self.input_weights[i][h] = rand(-0.2, 0.2)
        for h in range(self.hidden_n):
            for o in range(self.output_n):
                self.output_weights[h][o] = rand(-2.0, 2.0)
        # init correction matrix
        self.input_correction = make_matrix(self.input_n, self.hidden_n)
        self.output_correction = make_matrix(self.hidden_n, self.output_n)

        self.learn = learn
        self.correct = correct

    def predict(self, inputs):
        # activate input layer
        if isinstance(inputs, list):
            for i in range(self.input_n - 1):
                self.input_cells[i] = inputs[i]  # 输入层输出值
        else:
            self.input_cells[0] = inputs

        # activate hidden layer
        for j in range(self.hidden_n):
            total = 0.0
            for i in range(self.input_n):
                total += self.input_cells[i] * \
                    self.input_weights[i][j]  # 隐藏层输入值
            self.hidden_cells[j] = sigmoid(total)  # 隐藏层的输出值
        # activate output layer
        for k in range(self.output_n):
            total = 0.0
            for j in range(self.hidden_n):
                total += self.hidden_cells[j] * self.output_weights[j][k]
                #-----------------------------------------------
            # self.output_cells[k] = sigmoid(total)
            self.output_cells[k] = total  # 输出层的激励函数是f(x)=x
 #-----------------------------------------------
        return self.output_cells[:]

    # x,y,修改最大迭代次数， 学习率λ， 矫正率μ三个参数.
    def back_propagate(self, case, label):
        # feed forward
        self.predict(case)
        # get output layer error
        output_deltas = [0.0] * self.output_n
        if self.output_n == 1:
            output_deltas[0] = label - self.output_cells[0]
        else:
            for o in range(self.output_n):
                output_deltas[o] = label[o] - self.output_cells[o]
#-----------------------------------------------
        # get hidden layer error
        hidden_deltas = [0.0] * self.hidden_n
        for h in range(self.hidden_n):
            error = 0.0
            for o in range(self.output_n):
                error += output_deltas[o] * self.output_weights[h][o]
            hidden_deltas[h] = sigmoid_derivative(self.hidden_cells[h]) * error

        # update output weights
        for h in range(self.hidden_n):
            for o in range(self.output_n):
                change = output_deltas[o] * self.hidden_cells[h]
                self.output_weights[h][o] += self.learn * change + \
                    self.correct * self.output_correction[h][o]
                self.output_correction[h][o] = change

        # update input weights
        for i in range(self.input_n):
            for h in range(self.hidden_n):
                change = hidden_deltas[h] * self.input_cells[i]
                self.input_weights[i][h] += self.learn * change + \
                    self.correct * self.input_correction[i][h]
                self.input_correction[i][h] = change
        # get global error
        error = 0.0
        if self.output_n == 1:
            error = 0.5 * (label - self.output_cells[0])**2
        else:
            for o in range(len(label)):
                error += 0.5 * (label[o] - self.output_cells[o]) ** 2
        return error

    def train(self, cases, labels, limit=10000):
        for j in range(limit):
            error = 0.0
            for i in range(len(cases)):
                label = labels[i]
                case = cases[i]
                error += self.back_propagate(case, label)

    def test(self):
        cases = interval(-pi, pi, 0.1)
        errors = [random() / 10 * [-1 ,1][random() > 0.5] for _ in cases]
        labels = [cos(x) + error for x, error in zip(cases, errors)]
        self.setup(1, 5, 1, 0.05, 0.1)
        self.train(cases, labels, 10000)
        test_cases = interval(-pi, pi, 0.01)
        test_labels = [cos(x) for x in test_cases]
        predict_labels = [self.predict(test_case) for test_case in test_cases]
        plt.xlabel("x")
        plt.ylabel("true value")
        plt.plot(test_cases, test_labels, label="true value")
        plt.plot(test_cases, predict_labels, label="predict value")
        plt.legend()
        plt.show()


if __name__ == '__main__':
    nn = BPNeuralNetwork()
    nn.test()
