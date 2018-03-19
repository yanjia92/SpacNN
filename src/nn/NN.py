# -*- coding: utf-8 -*-
import numpy as np
from util.util import sigmond, sigmond_prime
import random

# NN class referenced from 神经网络与深度学习.pdf
class NN(object):
    # sizes 表示各层包含的神经元个数
    # 这里假设第一层是输入层,最后一层是输出层,中间均为hidden layer
    def __init__(self, sizes):
        self.num_layers = len(sizes)
        self.sizes = sizes
        self.bias = [np.random.randn(x, 1) for x in sizes[1:]]
        # 这里将x1和x2交换顺序是为了方便利用前一层的激活向量计算后一层的激活向量
        self.weights = [np.random.randn(x2, x1) for (x1, x2) in zip(sizes[:-1], sizes[1:])]

    # 随机梯度下降
    # 算法思想:将整个训练集分为多个batches,一次epoch之中,利用多个batches进行多次梯度下降
    # training_data: list of (x, y)
    # epochs: 训练的次数
    # min_batch_size: 每次随机梯度下降的小样本的大小
    # eta: 学习速率
    # test_data: 如果提供test_data,则after each epoch,就测试NN的准确率
    def SGD(self, training_data, epochs, min_batch_size, eta, test_data=None):
        if test_data: n_test = len(test_data)
        n = len(training_data)
        for i in xrange(epochs):
            random.shuffle(training_data)
            batches = [training_data[j:j+min_batch_size] for j in range(0, n, min_batch_size)]
            for batch in batches:
                self.update_min_batch(batch, eta)
            if test_data:
                print "Epoch {0}: {1} / {2}".format(i, self.evaluate(test_data), n_test)
            else:
                print "Epoch {0} finished".format(i)

    # 利用batch中的样本使用反向传播进行训练,更新weights和biases
    # batch: 小样本训练集
    # eta: 学习速率
    def update_min_batch(self, batch, eta):
        nabla_b = [np.zeros(b.shape) for b in self.bias]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x,y)
            # 对所有样本对应的梯度进行求和
            nabla_b = [nb + dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw + dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]

        self.bias = [b - eta/len(batch)*nb for b, nb in zip(self.bias, nabla_b)]
        self.weights = [w - eta/len(batch)*nw for w, nw in zip(self.weights, nabla_w)]

    # 验证test_data中有多少个样本测试是正确的
    def evaluate(self, test_data):
        test_results = [(np.argmax(self.feedforward(x)), y) for x,y in test_data]
        return sum(int(x==y) for x,y in test_results)

    # return the output of the NN if a is the input
    def feedforward(self, a):
        for (b,w) in zip(self.bias, self.weights):
            a = sigmond(np.dot(w, a) + b)
        return a


    # 根据训练集x,y对权重和偏置计算误差关于权重和偏置的梯度
    # x: 训练样本的输入
    # y: 训练样本的输出
    def backprop(self, x, y):
        nabla_b = [np.zeros(b.shape) for b in self.bias]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        # feedforward
        activation = x
        activations = [x] # 存储每一层的激活值, e.g. sigmond(z)
        zs = [] # 存储每一层的z值,e.g. z = wx+b
        for w, b in zip(self.weights, self.bias):
            z = np.dot(w, activation) + b
            zs.append(z)
            activation = sigmond(z)
            activations.append(activation)
        # backward pass
        # 计算出代价函数对于输出层误差的变化率
        delta = self.cost_derivative(activations[-1], y) * sigmond_prime(zs[-1])
        # 计算代价函数关于输出层神经元偏置的变化率
        nabla_b[-1] = delta
        # 计算代价函数关于输出层神经元权重的变化率
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        for l in xrange(2, self.num_layers):
            z = zs[-l] # 得到倒数第l层神经元的z值
            # 计算代价函数关于倒数第l层神经元的误差
            sp = sigmond_prime(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)


    # 计算输出层每个神经元代价函数关于其输出的变化率
    def cost_derivative(self, output_activations, y):
        return (output_activations - y)





