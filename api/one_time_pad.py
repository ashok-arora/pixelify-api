import numpy as np
import random


class OneTimePad:
    def __init__(self, shape, key=None):
        self.key = self.key = (
            ";".join([str(random.randint(0, 255)) for _ in range(np.prod(shape))])
            if key is None
            else key
        )

    def encrypt(self, matrix):
        assert self.key is not None, "Key is not set"

        key = np.array(self.key.split(";")).astype(matrix.dtype)
        key = key.reshape(matrix.shape)
        matrix += key
        matrix %= 256

    def decrypt(self, matrix):
        assert self.key is not None, "Key is not set"

        key = np.array(self.key.split(";")).astype(matrix.dtype)
        key = key.reshape(matrix.shape)
        matrix -= key
        matrix %= 256
