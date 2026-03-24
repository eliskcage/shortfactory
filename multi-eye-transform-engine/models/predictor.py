# models/predictor.py

class Predictor:
    def __init__(self, memory):
        self.memory = memory

    def predict(self, node_field, context):
        scores = {}

        for label, data in self.memory.items():
            shape_score = self.compare(node_field, data["nodes"])
            context_score = context.get(label, 0.5)

            scores[label] = shape_score * context_score

        return sorted(scores.items(), key=lambda x: -x[1])

    def compare(self, a, b):
        overlap = len(set(a.keys()) & set(b.keys()))
        return overlap / (len(a) + 1)