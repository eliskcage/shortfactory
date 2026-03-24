# field/node_field.py

class NodeField:
    def __init__(self):
        self.nodes = {}

    def update(self, samples):
        for s in samples:
            if s["hit"]:
                key = tuple(round(v, 2) for v in s["pos"])
                self.nodes[key] = self.nodes.get(key, 0) + 1