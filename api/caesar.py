import random


class Caesar:
    def __init__(self, shape, key=None):
        self.key = random.randint(0, 255) if key is None else key
        self.key = str(self.key)

    def encrypt(self, matrix):
        assert self.key is not None, "Key is not set"

        key = int(self.key)
        matrix += key
        matrix %= 256

    def decrypt(self, matrix):
        assert self.key is not None, "Key is not set"

        key = int(self.key)
        matrix -= key
        matrix %= 256
