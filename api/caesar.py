import random


class Caesar:
    def __init__(self, size, key=None):
        self.key = random.randint(0, 255) if key is None else key

    def encrypt(self, matrix):
        assert self.key is not None, 'Key is not set'

        matrix += self.key
        matrix %= 256

    def decrypt(self, matrix):
        assert self.key is not None, 'Key is not set'

        matrix -= self.key
        matrix %= 256
