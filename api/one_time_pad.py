import random


class OneTimePad:
    def __init__(self, size, key=None):
        self.key = self.key = ';'.join(
            [str(random.randint(0, 255)) for _ in range(size)]) if key is None else key

    def encrypt(self, matrix):
        assert self.key is not None, 'Key is not set'

        counter = 0
        key = list(map(int, self.key.split(';')))
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                for k in range(len(matrix[i][j])):
                    matrix[i][j][k] = (matrix[i][j][k] + key[counter]) % 256
                    counter += 1

    def decrypt(self, matrix):
        assert self.key is not None, 'Key is not set'

        counter = 0
        key = list(map(int, self.key.split(';')))
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                for k in range(len(matrix[i][j])):
                    matrix[i][j][k] = (matrix[i][j][k] - key[counter]) % 256
                    counter += 1
