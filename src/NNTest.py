# -*- coding:utf-8 -*-
import NN
import mnist_loader


def main():
    training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
    network = NN.NN([784, 30, 10])
    network.SGD(training_data, 30, 10, 3.0, test_data=test_data)

if __name__ == '__main__':
    main()


