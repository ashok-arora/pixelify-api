import numpy as np
import random


class Transposition:
    def __init__(self, shape, key=None):
        self.key = key
        if self.key is None:
            temp = list(map(str, range(0, shape[1])))
            random.shuffle(temp)
            self.key = temp

    def encrypt(self, matrix):
        assert self.key is not None, 'Key is not set'

        key = np.array(self.key).astype('int')
        sort_order = np.argsort(key)
        np.copyto(matrix, matrix[:, sort_order])

    def decrypt(self, matrix):
        assert self.key is not None, 'Key is not set'

        key = np.array(self.key).astype('int')
        np.copyto(matrix, matrix[:, key])
