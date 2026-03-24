# spiders/spider.py

import random

class Spider:
    def __init__(self, id):
        self.id = id

    def sample(self, space):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        z = random.uniform(-1, 1)

        hit = space.query(x, y, z)

        return {
            "pos": (x, y, z),
            "hit": hit
        }