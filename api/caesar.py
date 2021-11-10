import random


class Caesar:
    def __init__(self, size, key=None):
        self.key = random.randint(0, 255) if key is None else key

    def encrypt(self, matrix):
        assert self.key is not None, 'Key is not set'

        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                for k in range(len(matrix[i][j])):
                    matrix[i][j][k] = (matrix[i][j][k] + self.key) % 256

    def decrypt(self, matrix):
        assert self.key is not None, 'Key is not set'

        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                for k in range(len(matrix[i][j])):
                    matrix[i][j][k] = (matrix[i][j][k] - self.key) % 256
