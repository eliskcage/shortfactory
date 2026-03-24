# main.py

from spiders.swarm import Swarm
from field.node_field import NodeField
from field.absence_field import AbsenceField
from models.predictor import Predictor
from models.scorer import Scorer
from context.context_engine import ContextEngine
from storage.memory import memory

class DummySpace:
    def query(self, x, y, z):
        # fake shape (sphere)
        return x*x + y*y + z*z < 0.5

swarm = Swarm(50)
node_field = NodeField()
absence_field = AbsenceField()

space = DummySpace()

# run exploration
for step in range(100):
    samples = swarm.explore(space)
    node_field.update(samples)
    absence_field.update(samples)

# context
context_engine = ContextEngine()
context = context_engine.get_context("shoe_shop")

# prediction
predictor = Predictor(memory)
prediction = predictor.predict(node_field.nodes, context)

# scoring
scorer = Scorer()
score = scorer.evaluate(node_field, absence_field, 100)

print("Prediction:", prediction[:3])
print("Score:", score)