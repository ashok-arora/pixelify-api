import numpy as np
import random


class ModifiedCaesar:
    def __init__(self, shape, key=None):
        self.key = [random.randint(0, 255), random.randint(1, shape[1]-1), random.randint(1, shape[1]-1)] if key is None else key

    def encrypt(self, matrix):
        assert self.key is not None, 'Key is not set'

        key, rotation, shift = self.key
        matrix += key
        matrix %= 256

        for i in range(matrix.shape[0]):
            matrix[i] = np.roll(matrix[i], rotation, axis=0)
            rotation += shift

    def decrypt(self, matrix):
        assert self.key is not None, 'Key is not set'

        key, rotation, shift = self.key
        matrix -= key
        matrix %= 256

        for i in range(matrix.shape[0]):
            matrix[i] = np.roll(matrix[i], -rotation, axis=0)
            rotation += shift
