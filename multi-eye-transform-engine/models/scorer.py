# models/scorer.py

class Scorer:
    def evaluate(self, node_field, absence_field, steps):
        coverage = len(node_field.nodes)
        efficiency = coverage / (steps + 1)

        return {
            "coverage": coverage,
            "efficiency": efficiency
        }