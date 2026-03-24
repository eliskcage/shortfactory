# spiders/swarm.py

from spiders.spider import Spider

class Swarm:
    def __init__(self, size):
        self.spiders = [Spider(i) for i in range(size)]

    def explore(self, space):
        results = []
        for spider in self.spiders:
            results.append(spider.sample(space))
        return results