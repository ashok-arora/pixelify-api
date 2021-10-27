class Caesar:
    def __init__(self, key):
        self.key = key % 256

    def encrypt(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                for k in range(len(matrix[i][j])):
                    matrix[i][j][k] = (matrix[i][j][k] + self.key) % 256

    def decrypt(self, matrix):
        for i in range(len(matrix)):
            for j in range(len(matrix[i])):
                for k in range(len(matrix[i][j])):
                    matrix[i][j][k] = (matrix[i][j][k] - self.key) % 256
